"""Views for the payments app.

The flow:

1. Employer hits ``feature_gig_checkout`` — we create a Stripe Checkout
   Session and persist a ``Payment`` in the ``pending`` state.
2. Stripe redirects them to ``payment_success`` (which is JUST a UX
   confirmation page — it does NOT mark the payment complete).
3. The actual source of truth is the Stripe webhook
   ``checkout.session.completed``, handled in ``stripe_webhook``.

This keeps the success page replay-safe and ensures customers can't fake
a featured gig by hitting the success URL directly.
"""

from __future__ import annotations

import logging

import stripe
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from gigs.models import Gig

from .models import Payment, PaymentEvent

logger = logging.getLogger("quickgigs.payments")

if settings.STRIPE_SECRET_KEY:
    stripe.api_key = settings.STRIPE_SECRET_KEY


# ---------------------------------------------------------------------------
# Checkout
# ---------------------------------------------------------------------------


@login_required
def feature_gig_checkout(request, gig_id: int):
    gig = get_object_or_404(Gig, id=gig_id, employer=request.user)

    if not settings.PAYMENTS_ENABLED:
        messages.error(
            request,
            "Payments aren't configured on this deployment.",
        )
        return redirect("gigs:gig_detail", pk=gig.id)

    if gig.is_featured:
        messages.warning(request, "This gig is already featured.")
        return redirect("gigs:gig_detail", pk=gig.id)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "price_data": {
                        "currency": settings.STRIPE_CURRENCY,
                        "product_data": {
                            "name": f"Feature gig: {gig.title}",
                            "description": "Top placement & featured badge for 30 days.",
                        },
                        "unit_amount": int(settings.FEATURED_GIG_PRICE * 100),
                    },
                    "quantity": 1,
                },
            ],
            success_url=request.build_absolute_uri(
                reverse("payments:payment_success", kwargs={"gig_id": gig.id})
            ),
            cancel_url=request.build_absolute_uri(
                reverse("payments:payment_cancel", kwargs={"gig_id": gig.id})
            ),
            client_reference_id=str(gig.id),
            metadata={
                "gig_id": str(gig.id),
                "user_id": str(request.user.id),
                "payment_type": Payment.Type.FEATURED_GIG,
            },
        )

        Payment.objects.create(
            user=request.user,
            gig=gig,
            amount=settings.FEATURED_GIG_PRICE,
            currency=settings.STRIPE_CURRENCY,
            payment_type=Payment.Type.FEATURED_GIG,
            status=Payment.Status.PENDING,
            stripe_session_id=session.id,
            description=f"Feature gig: {gig.title}",
        )

        return redirect(session.url, code=303)

    except stripe.error.StripeError:
        logger.exception("Stripe checkout creation failed for gig %s", gig.id)
        messages.error(
            request,
            "Sorry — we couldn't start the checkout. Please try again.",
        )
        return redirect("gigs:gig_detail", pk=gig.id)


def payment_success(request, gig_id: int):
    """Shown after Stripe redirects the customer back.

    This page is purely informational — the webhook is the source of truth.
    """
    gig = get_object_or_404(Gig, id=gig_id)
    return render(request, "payments/success.html", {"gig": gig})


def payment_cancel(request, gig_id: int):
    gig = get_object_or_404(Gig, id=gig_id)
    return render(request, "payments/cancel.html", {"gig": gig})


@login_required
def payment_history(request):
    payments = (
        Payment.objects.filter(user=request.user).select_related("gig").order_by("-created_at")
    )
    return render(request, "payments/history.html", {"payments": payments})


# ---------------------------------------------------------------------------
# Webhook — Stripe → us
# ---------------------------------------------------------------------------


@csrf_exempt
@require_POST
def stripe_webhook(request):
    """Receive checkout.session.completed and mark the payment complete."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
    webhook_secret = settings.STRIPE_WEBHOOK_SECRET

    if not webhook_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not configured; refusing webhook.")
        return HttpResponse(status=500)

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
    except (ValueError, stripe.error.SignatureVerificationError):
        logger.warning("Invalid Stripe webhook signature")
        return HttpResponse(status=400)

    event_id = event["id"]
    event_type = event["type"]

    # Idempotency: skip if we've already processed this event.
    if PaymentEvent.objects.filter(stripe_event_id=event_id).exists():
        return JsonResponse({"status": "duplicate"})

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event)
    else:
        logger.info("Ignoring Stripe event %s", event_type)

    return JsonResponse({"status": "ok"})


def _handle_checkout_completed(event: dict) -> None:
    session = event["data"]["object"]
    session_id = session.get("id")
    payment_intent_id = session.get("payment_intent") or ""

    try:
        payment = Payment.objects.select_related("gig").get(stripe_session_id=session_id)
    except Payment.DoesNotExist:
        logger.warning("Stripe webhook for unknown session_id=%s", session_id)
        return

    with transaction.atomic():
        if payment.status != Payment.Status.COMPLETED:
            payment.status = Payment.Status.COMPLETED
            payment.stripe_payment_intent = payment_intent_id
            payment.save(update_fields=["status", "stripe_payment_intent", "updated_at"])

            if (
                payment.payment_type == Payment.Type.FEATURED_GIG
                and payment.gig
                and not payment.gig.is_featured
            ):
                payment.gig.is_featured = True
                payment.gig.save(update_fields=["is_featured", "updated_at"])

        PaymentEvent.objects.create(
            payment=payment,
            event_type=event["type"],
            stripe_event_id=event["id"],
            raw=event,
        )

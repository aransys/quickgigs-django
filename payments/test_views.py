"""View-level tests for the payments app.

These tests focus on permissions, idempotency, and the webhook flow —
not on hitting real Stripe.
"""

from __future__ import annotations

import json
from decimal import Decimal
from unittest.mock import patch

import pytest
from django.urls import reverse

from payments.models import Payment, PaymentEvent


@pytest.mark.django_db
class TestPaymentHistory:
    def test_login_required(self, client):
        resp = client.get(reverse("payments:payment_history"))
        assert resp.status_code == 302

    def test_only_shows_users_own_payments(self, client, employer, freelancer, gig):
        Payment.objects.create(
            user=employer, gig=gig, amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
            description="My payment",
        )
        Payment.objects.create(
            user=freelancer, amount=Decimal("4.99"),
            payment_type=Payment.Type.APPLICATION_BOOST,
            description="Other person's payment",
        )
        client.force_login(employer)
        resp = client.get(reverse("payments:payment_history"))
        assert resp.status_code == 200
        assert b"My payment" in resp.content
        assert b"Other person" not in resp.content


@pytest.mark.django_db
class TestFeatureGigCheckout:
    def test_only_owner_can_checkout(self, client, gig, freelancer):
        client.force_login(freelancer)
        resp = client.get(
            reverse("payments:feature_gig_checkout", kwargs={"gig_id": gig.pk})
        )
        # get_object_or_404 with employer filter → 404
        assert resp.status_code == 404


@pytest.mark.django_db
class TestStripeWebhook:
    def test_no_secret_returns_500(self, client, settings):
        settings.STRIPE_WEBHOOK_SECRET = ""
        resp = client.post(
            reverse("payments:stripe_webhook"), data=b"{}",
            content_type="application/json",
        )
        assert resp.status_code == 500

    @patch("stripe.Webhook.construct_event")
    def test_invalid_signature_returns_400(self, mock_construct, client, settings):
        from stripe.error import SignatureVerificationError

        settings.STRIPE_WEBHOOK_SECRET = "whsec_test"
        mock_construct.side_effect = SignatureVerificationError("bad", "sig")
        resp = client.post(
            reverse("payments:stripe_webhook"),
            data=b"{}", content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        assert resp.status_code == 400

    @patch("stripe.Webhook.construct_event")
    def test_checkout_completed_marks_payment_and_features_gig(
        self, mock_construct, client, settings, employer, gig
    ):
        settings.STRIPE_WEBHOOK_SECRET = "whsec_test"
        payment = Payment.objects.create(
            user=employer, gig=gig, amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
            stripe_session_id="cs_test_123",
        )
        mock_construct.return_value = {
            "id": "evt_test_1",
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_test_123", "payment_intent": "pi_xyz"}},
        }
        resp = client.post(
            reverse("payments:stripe_webhook"),
            data=b"{}", content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        assert resp.status_code == 200
        payment.refresh_from_db()
        gig.refresh_from_db()
        assert payment.status == Payment.Status.COMPLETED
        assert payment.stripe_payment_intent == "pi_xyz"
        assert gig.is_featured is True
        assert PaymentEvent.objects.filter(stripe_event_id="evt_test_1").count() == 1

    @patch("stripe.Webhook.construct_event")
    def test_duplicate_event_is_idempotent(
        self, mock_construct, client, settings, employer, gig
    ):
        settings.STRIPE_WEBHOOK_SECRET = "whsec_test"
        payment = Payment.objects.create(
            user=employer, gig=gig, amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
            stripe_session_id="cs_test_999",
        )
        PaymentEvent.objects.create(
            payment=payment,
            event_type="checkout.session.completed",
            stripe_event_id="evt_dup",
            raw={},
        )
        mock_construct.return_value = {
            "id": "evt_dup",
            "type": "checkout.session.completed",
            "data": {"object": {"id": "cs_test_999"}},
        }
        resp = client.post(
            reverse("payments:stripe_webhook"),
            data=b"{}", content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        assert resp.status_code == 200
        assert json.loads(resp.content)["status"] == "duplicate"

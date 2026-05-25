"""Models for the payments app."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models

from gigs.models import Gig


class Payment(models.Model):
    """A Stripe-backed payment record."""

    class Type(models.TextChoices):
        FEATURED_GIG = "featured_gig", "Featured gig upgrade"
        GIG_POSTING = "gig_posting", "Gig posting fee"
        APPLICATION_BOOST = "application_boost", "Application boost"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        FAILED = "failed", "Failed"
        REFUNDED = "refunded", "Refunded"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="payments",
    )
    gig = models.ForeignKey(
        Gig,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="payments",
        help_text="Associated gig (if applicable).",
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
    )
    currency = models.CharField(max_length=3, default="gbp")
    stripe_session_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    stripe_payment_intent = models.CharField(max_length=255, blank=True)
    payment_type = models.CharField(max_length=32, choices=Type.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self) -> str:
        return f"{self.user.username} · £{self.amount} · {self.get_payment_type_display()}"

    @property
    def is_successful(self) -> bool:
        return self.status == self.Status.COMPLETED


class PaymentEvent(models.Model):
    """Audit trail of Stripe events processed against a payment."""

    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name="events")
    event_type = models.CharField(max_length=80)
    stripe_event_id = models.CharField(max_length=255, unique=True)
    raw = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.event_type} ({self.stripe_event_id})"

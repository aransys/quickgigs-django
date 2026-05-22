"""Model-level tests for the payments app."""

from __future__ import annotations

from decimal import Decimal

import pytest

from payments.models import Payment, PaymentEvent


@pytest.mark.django_db
class TestPayment:
    def test_str(self, employer, gig):
        p = Payment.objects.create(
            user=employer,
            gig=gig,
            amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
        )
        assert "9.99" in str(p)
        assert employer.username in str(p)

    def test_is_successful(self, employer):
        p = Payment.objects.create(
            user=employer,
            amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
        )
        assert p.is_successful is False
        p.status = Payment.Status.COMPLETED
        assert p.is_successful is True

    def test_currency_default(self, employer):
        p = Payment.objects.create(
            user=employer,
            amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
        )
        assert p.currency == "gbp"


@pytest.mark.django_db
class TestPaymentEvent:
    def test_unique_event_id(self, employer):
        payment = Payment.objects.create(
            user=employer,
            amount=Decimal("9.99"),
            payment_type=Payment.Type.FEATURED_GIG,
        )
        PaymentEvent.objects.create(
            payment=payment,
            event_type="checkout.session.completed",
            stripe_event_id="evt_unique_1",
            raw={"id": "evt_unique_1"},
        )
        # Second event with the same ID should not be insertable.
        from django.db import IntegrityError

        with pytest.raises(IntegrityError):
            PaymentEvent.objects.create(
                payment=payment,
                event_type="checkout.session.completed",
                stripe_event_id="evt_unique_1",
                raw={},
            )

"""Model-level tests for the gigs app."""

from __future__ import annotations

import datetime as dt
from decimal import Decimal

import pytest
from django.db import IntegrityError
from django.utils import timezone

from gigs.models import Application, Gig


@pytest.mark.django_db
class TestGigModel:
    def test_str_is_title(self, gig):
        assert str(gig) == "Build a landing page"

    def test_get_absolute_url_uses_pk(self, gig):
        assert gig.get_absolute_url() == f"/gigs/{gig.pk}/"

    def test_is_available_true_for_active_undated(self, gig):
        assert gig.is_available is True

    def test_is_available_false_for_inactive(self, gig):
        gig.is_active = False
        assert gig.is_available is False

    def test_is_overdue_when_deadline_past(self, gig):
        gig.deadline = timezone.now().date() - dt.timedelta(days=1)
        assert gig.is_overdue is True
        assert gig.is_available is False

    def test_days_remaining(self, gig):
        gig.deadline = timezone.now().date() + dt.timedelta(days=7)
        assert gig.days_remaining == 7

    def test_days_remaining_none_when_no_deadline(self, gig):
        assert gig.days_remaining is None


@pytest.mark.django_db
class TestApplicationModel:
    def test_str(self, application):
        assert str(application) == f"{application.applicant.username} → {application.gig.title}"

    def test_default_status_is_pending(self, application):
        assert application.status == Application.Status.PENDING

    def test_is_withdrawable_for_pending(self, application):
        assert application.is_withdrawable is True

    def test_is_withdrawable_false_after_accept(self, application):
        application.status = Application.Status.ACCEPTED
        assert application.is_withdrawable is False

    def test_unique_constraint_per_gig_per_applicant(self, gig, freelancer):
        Application.objects.create(
            gig=gig, applicant=freelancer, cover_letter="x" * 60,
        )
        with pytest.raises(IntegrityError):
            Application.objects.create(
                gig=gig, applicant=freelancer, cover_letter="y" * 60,
            )

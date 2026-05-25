"""Form-level tests for the gigs app."""

from __future__ import annotations

import pytest

from gigs.forms import ApplicationForm, GigForm
from gigs.models import Gig


@pytest.mark.django_db
class TestGigForm:
    def test_valid_form(self):
        form = GigForm(
            data={
                "title": "A new gig",
                "description": "Detailed description of the gig.",
                "budget": "150.00",
                "location": "Remote",
                "category": Gig.Category.WEB_DEV,
                "deadline": "",
            }
        )
        assert form.is_valid(), form.errors

    def test_zero_budget_rejected(self):
        form = GigForm(
            data={
                "title": "Zero gig",
                "description": "Detailed description of the gig.",
                "budget": "0",
                "location": "Remote",
                "category": Gig.Category.WEB_DEV,
                "deadline": "",
            }
        )
        assert not form.is_valid()
        assert "budget" in form.errors

    def test_required_fields(self):
        form = GigForm(data={})
        assert not form.is_valid()
        for field in ("title", "description", "budget", "location", "category"):
            assert field in form.errors


@pytest.mark.django_db
class TestApplicationForm:
    def test_valid_form(self):
        form = ApplicationForm(
            data={
                "cover_letter": (
                    "I have plenty of relevant experience and would love to chat about this."
                ),
                "proposed_rate": "100.00",
            }
        )
        assert form.is_valid(), form.errors

    def test_short_cover_letter_rejected(self):
        form = ApplicationForm(data={"cover_letter": "too short"})
        assert not form.is_valid()
        assert "cover_letter" in form.errors

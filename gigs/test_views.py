"""View-level tests for the gigs app."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.urls import reverse

from gigs.models import Application, Gig


@pytest.mark.django_db
class TestGigList:
    def test_anonymous_can_view_list(self, client, gig):
        resp = client.get(reverse("gigs:gig_list"))
        assert resp.status_code == 200
        assert gig.title.encode() in resp.content

    def test_search_filters_results(self, client, gig, employer):
        Gig.objects.create(
            title="Design a logo",
            description="Brand kit",
            employer=employer,
            budget=Decimal("100"),
            location="Remote",
            category=Gig.Category.DESIGN,
        )
        resp = client.get(reverse("gigs:gig_list"), {"search": "logo"})
        assert resp.status_code == 200
        assert b"logo" in resp.content.lower()
        assert b"landing page" not in resp.content.lower()

    def test_category_filter(self, client, gig):
        resp = client.get(
            reverse("gigs:gig_list"), {"category": Gig.Category.DESIGN}
        )
        assert resp.status_code == 200
        assert gig.title.encode() not in resp.content


@pytest.mark.django_db
class TestGigDetail:
    def test_renders(self, client, gig):
        resp = client.get(reverse("gigs:gig_detail", kwargs={"pk": gig.pk}))
        assert resp.status_code == 200
        assert gig.title.encode() in resp.content

    def test_application_context_for_owner(self, client, gig):
        client.force_login(gig.employer)
        resp = client.get(reverse("gigs:gig_detail", kwargs={"pk": gig.pk}))
        assert resp.context["application_count"] == 0


@pytest.mark.django_db
class TestGigCreate:
    def test_login_required(self, client):
        resp = client.get(reverse("gigs:gig_create"))
        assert resp.status_code == 302  # redirected to login

    def test_creates_gig(self, client, user):
        client.force_login(user)
        resp = client.post(
            reverse("gigs:gig_create"),
            {
                "title": "New gig",
                "description": "Lorem ipsum dolor sit amet, doing things.",
                "budget": "200.00",
                "location": "London",
                "category": Gig.Category.WRITING,
                "deadline": "",
            },
        )
        assert resp.status_code == 302
        assert Gig.objects.filter(title="New gig", employer=user).exists()


@pytest.mark.django_db
class TestGigPermissions:
    def test_non_owner_cannot_edit(self, client, gig, freelancer):
        client.force_login(freelancer)
        resp = client.get(reverse("gigs:gig_update", kwargs={"pk": gig.pk}))
        # UserPassesTestMixin returns 302 (login redirect) or 403.
        assert resp.status_code in (302, 403)

    def test_owner_can_toggle_status(self, client, gig):
        client.force_login(gig.employer)
        resp = client.post(reverse("gigs:toggle_gig_status", kwargs={"pk": gig.pk}))
        gig.refresh_from_db()
        assert resp.status_code == 302
        assert gig.is_active is False

    def test_toggle_status_requires_POST(self, client, gig):
        client.force_login(gig.employer)
        resp = client.get(reverse("gigs:toggle_gig_status", kwargs={"pk": gig.pk}))
        assert resp.status_code == 405


@pytest.mark.django_db
class TestApplyFlow:
    def test_cannot_apply_to_own_gig(self, client, gig):
        client.force_login(gig.employer)
        resp = client.post(
            reverse("gigs:apply_to_gig", kwargs={"pk": gig.pk}),
            {"cover_letter": "x" * 60, "proposed_rate": "100"},
        )
        assert resp.status_code == 302
        assert Application.objects.count() == 0

    def test_freelancer_can_apply(self, client, gig, freelancer):
        client.force_login(freelancer)
        resp = client.post(
            reverse("gigs:apply_to_gig", kwargs={"pk": gig.pk}),
            {
                "cover_letter": (
                    "I have built dozens of landing pages and would love to do this one."
                ),
                "proposed_rate": "700",
            },
        )
        assert resp.status_code == 302
        assert Application.objects.filter(gig=gig, applicant=freelancer).exists()

    def test_double_apply_redirects_to_existing(self, client, application):
        client.force_login(application.applicant)
        resp = client.get(
            reverse("gigs:apply_to_gig", kwargs={"pk": application.gig.pk})
        )
        assert resp.status_code == 302

    def test_withdraw_only_by_applicant(self, client, application, employer):
        client.force_login(employer)
        resp = client.post(
            reverse("gigs:withdraw_application", kwargs={"pk": application.pk})
        )
        assert resp.status_code == 403


@pytest.mark.django_db
class TestApplicationDetail:
    def test_unrelated_user_404s(self, client, application, user):
        client.force_login(user)
        resp = client.get(
            reverse("gigs:application_detail", kwargs={"pk": application.pk})
        )
        assert resp.status_code == 404

    def test_applicant_can_view(self, client, application):
        client.force_login(application.applicant)
        resp = client.get(
            reverse("gigs:application_detail", kwargs={"pk": application.pk})
        )
        assert resp.status_code == 200

    def test_employer_can_view(self, client, application):
        client.force_login(application.gig.employer)
        resp = client.get(
            reverse("gigs:application_detail", kwargs={"pk": application.pk})
        )
        assert resp.status_code == 200

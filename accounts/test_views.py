"""View-level tests for the accounts app."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from accounts.models import UserProfile


@pytest.mark.django_db
class TestSignUpFlow:
    def test_get_page_renders(self, client):
        resp = client.get(reverse("accounts:signup"))
        assert resp.status_code == 200

    def test_signup_creates_user_and_profile(self, client):
        resp = client.post(
            reverse("accounts:signup"),
            {
                "username": "newcomer",
                "email": "newcomer@example.com",
                "password1": "T3st-pass!42",
                "password2": "T3st-pass!42",
            },
        )
        assert resp.status_code == 302
        user = get_user_model().objects.get(username="newcomer")
        assert UserProfile.objects.filter(user=user).exists()


@pytest.mark.django_db
class TestChooseRole:
    def test_login_required(self, client):
        resp = client.get(reverse("accounts:choose_role"))
        assert resp.status_code == 302

    def test_set_employer(self, client, user):
        client.force_login(user)
        resp = client.post(reverse("accounts:choose_role"), {"role": "employer"})
        assert resp.status_code == 302
        user.userprofile.refresh_from_db()
        assert user.userprofile.is_employer

    def test_invalid_role_rejected(self, client, user):
        client.force_login(user)
        resp = client.post(reverse("accounts:choose_role"), {"role": "hacker"})
        assert resp.status_code == 400


@pytest.mark.django_db
class TestProfile:
    def test_profile_view_requires_login(self, client):
        resp = client.get(reverse("accounts:profile"))
        assert resp.status_code == 302

    def test_logged_in_user_can_see_profile(self, client, user):
        client.force_login(user)
        resp = client.get(reverse("accounts:profile"))
        assert resp.status_code == 200
        assert user.username.encode() in resp.content

    def test_can_update_profile(self, client, user):
        client.force_login(user)
        resp = client.post(
            reverse("accounts:profile_edit"),
            {
                "bio": "I build things.",
                "skills": "Python, Django",
                "hourly_rate": "50.00",
                "company_name": "",
                "phone": "",
            },
        )
        assert resp.status_code == 302
        user.userprofile.refresh_from_db()
        assert user.userprofile.bio == "I build things."

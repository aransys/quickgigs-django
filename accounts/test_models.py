"""Model-level tests for the accounts app."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from accounts.models import UserProfile


@pytest.mark.django_db
class TestUserProfile:
    def test_profile_auto_created(self):
        u = get_user_model().objects.create_user(username="zoe", password="x")
        assert UserProfile.objects.filter(user=u).exists()

    def test_default_role_is_unset(self):
        u = get_user_model().objects.create_user(username="ana", password="x")
        assert u.userprofile.user_type == UserProfile.Role.UNSET
        assert u.userprofile.has_chosen_role is False

    def test_role_helpers(self, employer, freelancer):
        assert employer.userprofile.is_employer
        assert not employer.userprofile.is_freelancer
        assert freelancer.userprofile.is_freelancer
        assert not freelancer.userprofile.is_employer

    def test_skill_list_parsing(self, user):
        user.userprofile.skills = "Python, Django, ,JavaScript"
        assert user.userprofile.skill_list == ["Python", "Django", "JavaScript"]

    def test_display_name_falls_back_to_username(self, user):
        assert user.userprofile.display_name == user.username
        user.first_name = "Alice"
        user.last_name = "Wonderland"
        assert user.userprofile.display_name == "Alice Wonderland"

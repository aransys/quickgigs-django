"""Form-level tests for the accounts app."""

from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model

from accounts.forms import SignUpForm


@pytest.mark.django_db
class TestSignUpForm:
    def test_valid(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password1": "S3cure-pass!42",
                "password2": "S3cure-pass!42",
            }
        )
        assert form.is_valid(), form.errors

    def test_password_mismatch(self):
        form = SignUpForm(
            data={
                "username": "newuser",
                "email": "new@example.com",
                "password1": "S3cure-pass!42",
                "password2": "different",
            }
        )
        assert not form.is_valid()
        assert "password2" in form.errors

    def test_duplicate_email_rejected(self):
        get_user_model().objects.create_user(
            username="someone", email="taken@example.com", password="x"
        )
        form = SignUpForm(
            data={
                "username": "newuser",
                "email": "taken@example.com",
                "password1": "S3cure-pass!42",
                "password2": "S3cure-pass!42",
            }
        )
        assert not form.is_valid()
        assert "email" in form.errors

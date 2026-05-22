"""Shared pytest fixtures for QuickGigs."""

from __future__ import annotations

from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from accounts.models import UserProfile
from gigs.models import Application, Gig


User = get_user_model()


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="alice", email="alice@example.com", password="testpass123"
    )


@pytest.fixture
def employer(db):
    u = User.objects.create_user(
        username="bob_employer", email="bob@example.com", password="testpass123"
    )
    u.userprofile.user_type = UserProfile.Role.EMPLOYER
    u.userprofile.save()
    return u


@pytest.fixture
def freelancer(db):
    u = User.objects.create_user(
        username="carol_freelancer", email="carol@example.com", password="testpass123"
    )
    u.userprofile.user_type = UserProfile.Role.FREELANCER
    u.userprofile.save()
    return u


@pytest.fixture
def gig(db, employer):
    return Gig.objects.create(
        title="Build a landing page",
        description="A clean, fast landing page in Next.js.",
        employer=employer,
        budget=Decimal("800.00"),
        location="Remote",
        category=Gig.Category.WEB_DEV,
    )


@pytest.fixture
def application(db, gig, freelancer):
    return Application.objects.create(
        gig=gig,
        applicant=freelancer,
        cover_letter=(
            "I've shipped many Next.js landing pages and would love to take this on. "
            "Happy to discuss approach and timeline."
        ),
        proposed_rate=Decimal("750.00"),
    )

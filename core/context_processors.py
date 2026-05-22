"""Template context processors for QuickGigs."""

from __future__ import annotations

from django.conf import settings


def site_meta(request):
    """Inject brand & feature flags into every template.

    Keeps templates free of hard-coded brand strings and lets the navbar /
    payments UI know whether Stripe is configured.
    """

    return {
        "SITE_NAME": "QuickGigs",
        "SITE_TAGLINE": "Find your next gig.",
        "PAYMENTS_ENABLED": getattr(settings, "PAYMENTS_ENABLED", False),
        "FEATURED_GIG_PRICE": getattr(settings, "FEATURED_GIG_PRICE", 0),
        "STRIPE_PUBLISHABLE_KEY": getattr(settings, "STRIPE_PUBLISHABLE_KEY", ""),
    }

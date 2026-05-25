"""View-level tests for the core app."""

from __future__ import annotations

import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestStaticPages:
    @pytest.mark.parametrize("view_name", ["core:home", "core:about", "core:contact"])
    def test_pages_render(self, client, view_name):
        resp = client.get(reverse(view_name))
        assert resp.status_code == 200

    def test_home_shows_recent_gigs(self, client, gig):
        resp = client.get(reverse("core:home"))
        assert resp.status_code == 200
        assert gig.title.encode() in resp.content

    def test_home_includes_site_meta_context(self, client):
        resp = client.get(reverse("core:home"))
        assert b"QuickGigs" in resp.content

"""Top-level URL configuration for QuickGigs."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("core.urls")),
    path("accounts/", include("accounts.urls")),
    path("gigs/", include("gigs.urls")),
    path("payments/", include("payments.urls")),
]

if settings.DEBUG:
    try:
        import debug_toolbar  # noqa: F401

        urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    except ImportError:
        # debug_toolbar only ships in requirements-dev.txt; safe to skip
        # if it isn't installed.
        pass

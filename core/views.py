"""Site-wide views: home, about, contact."""

from __future__ import annotations

from django.db.models import Count, Q
from django.views.generic import TemplateView

from accounts.models import UserProfile
from gigs.models import Gig


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        active = Gig.objects.filter(is_active=True).select_related("employer")
        ctx["featured_gigs"] = list(
            active.filter(is_featured=True).order_by("-created_at")[:3]
        )
        ctx["recent_gigs"] = list(active.order_by("-created_at")[:6])

        profile_counts = UserProfile.objects.aggregate(
            employers=Count("pk", filter=Q(user_type="employer")),
            freelancers=Count("pk", filter=Q(user_type="freelancer")),
        )
        ctx["total_gigs"] = active.count()
        ctx["total_employers"] = profile_counts["employers"] or 0
        ctx["total_freelancers"] = profile_counts["freelancers"] or 0
        return ctx


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"

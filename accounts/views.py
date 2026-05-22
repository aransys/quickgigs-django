"""Views for the accounts app."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_http_methods
from django.views.generic import CreateView, UpdateView

from .forms import SignUpForm, UserProfileForm
from .models import UserProfile


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("accounts:choose_role")
    template_name = "accounts/signup.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        # Profile is created by the post_save signal; sign the user in.
        login(self.request, self.object)
        messages.success(
            self.request,
            f"Welcome to QuickGigs, {self.object.username}.",
        )
        return response


@login_required
@require_http_methods(["GET", "POST"])
def choose_role(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        role = request.POST.get("role")
        if role not in {UserProfile.Role.EMPLOYER, UserProfile.Role.FREELANCER}:
            return HttpResponseBadRequest("Invalid role.")
        profile.user_type = role
        profile.save(update_fields=["user_type", "updated_at"])

        if profile.is_employer:
            messages.success(request, "You're set up as an employer — let's post a gig.")
            return redirect("gigs:gig_create")
        messages.success(request, "You're set up as a freelancer — browse gigs and apply.")
        return redirect("gigs:gig_list")

    return render(request, "accounts/choose_role.html", {"profile": profile})


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    return render(
        request,
        "accounts/profile.html",
        {"profile": profile, "skills_list": profile.skill_list},
    )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = "accounts/profile_edit.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        messages.success(self.request, "Profile updated.")
        return super().form_valid(form)

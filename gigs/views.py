"""Views for the gigs app."""

from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import ApplicationForm, ApplicationStatusForm, GigForm
from .models import Application, Gig

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class EmployerOwnsGigMixin(UserPassesTestMixin):
    """Only the gig's employer may proceed."""

    def test_func(self) -> bool:
        gig = self.get_object()
        return self.request.user.is_authenticated and self.request.user == gig.employer

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only manage your own gigs.")
        return redirect("gigs:gig_list")


# ---------------------------------------------------------------------------
# Gig CRUD
# ---------------------------------------------------------------------------


class GigListView(ListView):
    model = Gig
    template_name = "gigs/gig_list.html"
    context_object_name = "gigs"
    paginate_by = 12

    def get_queryset(self):
        qs = Gig.objects.filter(is_active=True).select_related("employer")

        q = self.request.GET.get("search", "").strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        category = self.request.GET.get("category", "").strip()
        if category:
            qs = qs.filter(category=category)

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Gig.Category.choices
        ctx["current_category"] = self.request.GET.get("category", "")
        ctx["search_query"] = self.request.GET.get("search", "")
        return ctx


class GigDetailView(DetailView):
    model = Gig
    template_name = "gigs/gig_detail.html"
    context_object_name = "gig"

    def get_queryset(self):
        return Gig.objects.select_related("employer", "employer__userprofile")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            ctx["user_application"] = Application.objects.filter(
                gig=self.object, applicant=user
            ).first()
            if user == self.object.employer:
                ctx["application_count"] = self.object.applications.count()
        return ctx


class GigCreateView(LoginRequiredMixin, CreateView):
    model = Gig
    form_class = GigForm
    template_name = "gigs/gig_form.html"

    def form_valid(self, form):
        form.instance.employer = self.request.user
        messages.success(
            self.request,
            "Gig posted. Manage it from “My gigs”.",
        )
        return super().form_valid(form)


class GigUpdateView(LoginRequiredMixin, EmployerOwnsGigMixin, UpdateView):
    model = Gig
    form_class = GigForm
    template_name = "gigs/gig_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Gig updated.")
        return super().form_valid(form)


class GigDeleteView(LoginRequiredMixin, EmployerOwnsGigMixin, DeleteView):
    model = Gig
    template_name = "gigs/gig_confirm_delete.html"
    success_url = reverse_lazy("gigs:my_gigs")

    def form_valid(self, form):
        messages.success(self.request, "Gig deleted.")
        return super().form_valid(form)


@login_required
@require_POST
def toggle_gig_status(request, pk: int):
    gig = get_object_or_404(Gig, pk=pk)
    if request.user != gig.employer:
        return HttpResponseForbidden("You can only manage your own gigs.")

    gig.is_active = not gig.is_active
    gig.save(update_fields=["is_active", "updated_at"])
    messages.success(
        request,
        f"Gig {'activated' if gig.is_active else 'deactivated'}.",
    )
    return redirect("gigs:gig_detail", pk=pk)


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------


@login_required
def apply_to_gig(request, pk: int):
    gig = get_object_or_404(Gig, pk=pk)

    if request.user == gig.employer:
        messages.error(request, "You can't apply to your own gig.")
        return redirect("gigs:gig_detail", pk=pk)

    if not gig.is_active:
        messages.error(request, "This gig is no longer accepting applications.")
        return redirect("gigs:gig_detail", pk=pk)

    existing = Application.objects.filter(gig=gig, applicant=request.user).first()
    if existing:
        messages.info(request, "You've already applied to this gig.")
        return redirect("gigs:application_detail", pk=existing.pk)

    if request.method == "POST":
        form = ApplicationForm(request.POST)
        if form.is_valid():
            application = form.save(commit=False)
            application.gig = gig
            application.applicant = request.user
            application.save()
            messages.success(request, "Your application has been submitted.")
            return redirect("gigs:gig_detail", pk=pk)
    else:
        form = ApplicationForm()

    return render(request, "gigs/apply_to_gig.html", {"form": form, "gig": gig})


class ApplicationDetailView(LoginRequiredMixin, DetailView):
    model = Application
    template_name = "gigs/application_detail.html"
    context_object_name = "application"

    def get_object(self, queryset=None):
        application = get_object_or_404(
            Application.objects.select_related("gig", "gig__employer", "applicant"),
            pk=self.kwargs["pk"],
        )
        if self.request.user not in (application.applicant, application.gig.employer):
            raise Http404
        return application


@login_required
def my_applications(request):
    applications = (
        Application.objects.filter(applicant=request.user)
        .select_related("gig", "gig__employer")
        .order_by("-created_at")
    )
    return render(request, "gigs/my_applications.html", {"applications": applications})


@login_required
def my_gigs(request):
    """Dashboard for employers — own gigs plus application counts."""
    gigs = (
        Gig.objects.filter(employer=request.user)
        .annotate(
            application_count=Count("applications"),
            pending_count=Count(
                "applications",
                filter=Q(applications__status=Application.Status.PENDING),
            ),
        )
        .order_by("-created_at")
    )

    summary = gigs.aggregate(
        total_gigs=Count("id"),
        active_gigs=Count("id", filter=Q(is_active=True)),
        total_applications=Count("applications"),
        pending_applications=Count(
            "applications", filter=Q(applications__status=Application.Status.PENDING)
        ),
    )

    return render(
        request,
        "gigs/my_gigs.html",
        {"gigs": gigs, **summary},
    )


@login_required
def gig_applications(request, pk: int):
    gig = get_object_or_404(Gig, pk=pk)
    if request.user != gig.employer:
        return HttpResponseForbidden("You can only view applications for your own gigs.")
    applications = gig.applications.select_related("applicant").order_by("-created_at")
    return render(
        request,
        "gigs/gig_applications.html",
        {"gig": gig, "applications": applications},
    )


@login_required
def update_application_status(request, pk: int):
    application = get_object_or_404(Application.objects.select_related("gig"), pk=pk)
    if request.user != application.gig.employer:
        return HttpResponseForbidden(
            "You can only manage applications for your own gigs.",
        )

    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, "Application status updated.")
            return redirect("gigs:gig_applications", pk=application.gig.pk)
    else:
        form = ApplicationStatusForm(instance=application)

    return render(
        request,
        "gigs/update_application_status.html",
        {"form": form, "application": application},
    )


@login_required
def withdraw_application(request, pk: int):
    application = get_object_or_404(Application, pk=pk)
    if request.user != application.applicant:
        return HttpResponseForbidden("You can only withdraw your own applications.")
    if not application.is_withdrawable:
        messages.error(request, "Only pending applications can be withdrawn.")
        return redirect("gigs:my_applications")

    if request.method == "POST":
        application.status = Application.Status.WITHDRAWN
        application.save(update_fields=["status", "updated_at"])
        messages.success(request, "Application withdrawn.")
        return redirect("gigs:my_applications")

    return render(request, "gigs/withdraw_application.html", {"application": application})

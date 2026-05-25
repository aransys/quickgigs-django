"""Admin registrations for the gigs app."""

from django.contrib import admin

from .models import Application, Gig


@admin.register(Gig)
class GigAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "employer",
        "budget",
        "category",
        "is_active",
        "is_featured",
        "created_at",
    )
    list_filter = ("category", "is_active", "is_featured", "created_at")
    search_fields = ("title", "description", "employer__username")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("is_active", "is_featured")
    ordering = ("-created_at",)
    autocomplete_fields = ("employer",)


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = (
        "gig",
        "applicant",
        "status",
        "proposed_rate",
        "created_at",
    )
    list_filter = ("status", "created_at", "gig__category")
    search_fields = ("gig__title", "applicant__username", "cover_letter")
    readonly_fields = ("created_at", "updated_at")
    list_editable = ("status",)
    ordering = ("-created_at",)
    autocomplete_fields = ("gig", "applicant")
    fieldsets = (
        ("Application", {"fields": ("gig", "applicant", "status")}),
        ("Submission", {"fields": ("cover_letter", "proposed_rate")}),
        ("Employer notes", {"fields": ("employer_notes",)}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("gig", "applicant")

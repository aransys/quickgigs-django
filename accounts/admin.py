"""Admin registrations for the accounts app."""

from django.contrib import admin

from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "user_type", "company_name", "hourly_rate", "created_at")
    list_filter = ("user_type", "created_at")
    search_fields = ("user__username", "user__email", "company_name", "skills")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)
    fieldsets = (
        ("User", {"fields": ("user", "user_type")}),
        ("Profile", {"fields": ("bio", "skills", "phone")}),
        ("Work", {"fields": ("hourly_rate", "company_name")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

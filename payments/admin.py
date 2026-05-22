"""Admin registrations for the payments app."""

from django.contrib import admin

from .models import Payment, PaymentEvent


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "currency",
        "payment_type",
        "status",
        "created_at",
    )
    list_filter = ("payment_type", "status", "created_at")
    search_fields = (
        "user__username",
        "user__email",
        "stripe_session_id",
        "stripe_payment_intent",
        "description",
    )
    date_hierarchy = "created_at"
    readonly_fields = (
        "stripe_session_id",
        "stripe_payment_intent",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("user", "gig")
    fieldsets = (
        ("Payment", {"fields": ("user", "amount", "currency", "payment_type", "status")}),
        ("Linked", {"fields": ("gig", "description")}),
        ("Stripe", {"fields": ("stripe_session_id", "stripe_payment_intent")}),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(PaymentEvent)
class PaymentEventAdmin(admin.ModelAdmin):
    list_display = ("payment", "event_type", "stripe_event_id", "created_at")
    list_filter = ("event_type", "created_at")
    search_fields = ("stripe_event_id", "payment__user__username")
    readonly_fields = ("payment", "event_type", "stripe_event_id", "raw", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        # Events come from Stripe — never create them by hand.
        return False

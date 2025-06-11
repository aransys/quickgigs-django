from django.contrib import admin
from .models import Payment, PaymentHistory

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'payment_type', 'status', 'created_at']
    list_filter = ['payment_type', 'status', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_payment_id', 'description']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'amount', 'payment_type', 'status')
        }),
        ('Associated Content', {
            'fields': ('gig', 'description')
        }),
        ('Payment Processing', {
            'fields': ('stripe_payment_id',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )

@admin.register(PaymentHistory)
class PaymentHistoryAdmin(admin.ModelAdmin):
    list_display = ['payment', 'old_status', 'new_status', 'changed_by', 'created_at']
    list_filter = ['old_status', 'new_status', 'created_at']
    search_fields = ['payment__user__username', 'notes']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
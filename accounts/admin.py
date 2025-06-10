from django.contrib import admin
from .models import UserProfile

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'company_name', 'hourly_rate', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email', 'company_name', 'skills']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'user_type')
        }),
        ('Profile Details', {
            'fields': ('bio', 'skills', 'phone')
        }),
        ('Work Information', {
            'fields': ('hourly_rate', 'company_name')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )
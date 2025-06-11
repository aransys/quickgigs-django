from django.db import models
from django.contrib.auth.models import User
from gigs.models import Gig

class Payment(models.Model):
    PAYMENT_TYPE_CHOICES = [
        ('gig_posting', 'Gig Posting Fee'),
        ('featured_gig', 'Featured Gig Upgrade'),
        ('premium_profile', 'Premium Profile'),
        ('application_boost', 'Application Boost'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    gig = models.ForeignKey(Gig, on_delete=models.SET_NULL, null=True, blank=True, 
                           help_text="Associated gig (if applicable)")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True, help_text="Payment description or notes")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - ${self.amount} - {self.get_payment_type_display()}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment"
        verbose_name_plural = "Payments"

class PaymentHistory(models.Model):
    """Track payment history and changes"""
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='history')
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Payment {self.payment.id}: {self.old_status} → {self.new_status}"
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Payment History"
        verbose_name_plural = "Payment Histories"
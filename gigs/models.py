from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.urls import reverse
from decimal import Decimal

class Gig(models.Model):
    """Simple gig/job posting model"""
    
    CATEGORY_CHOICES = [
        ('web_dev', 'Web Development'),
        ('design', 'Graphic Design'),
        ('writing', 'Content Writing'),
        ('marketing', 'Digital Marketing'),
        ('data_entry', 'Data Entry'),
        ('translation', 'Translation'),
        ('video_editing', 'Video Editing'),
        ('other', 'Other'),
    ]
    
    # Essential fields only
    title = models.CharField(max_length=200)
    description = models.TextField()
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_gigs')
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    deadline = models.DateField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-created_at']
        verbose_name = "Gig"
        verbose_name_plural = "Gigs"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('gigs:gig_detail', kwargs={'pk': self.pk})
    
    @property
    def is_available(self):
        """Check if gig is available"""
        if not self.is_active:
            return False
        if self.deadline and self.deadline < timezone.now().date():
            return False
        return True
    
    @property
    def days_remaining(self):
        """Days until deadline"""
        if self.deadline:
            delta = self.deadline - timezone.now().date()
            return max(0, delta.days)
        return None
    
    @property
    def is_overdue(self):
        """Check if gig is overdue"""
        if self.deadline and self.deadline < timezone.now().date():
            return True
        return False

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('withdrawn', 'Withdrawn'),
    ]
    
    gig = models.ForeignKey(Gig, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    cover_letter = models.TextField(help_text="Explain why you're the right fit for this gig")
    proposed_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Your proposed rate for this project (optional)"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    employer_notes = models.TextField(blank=True, help_text="Internal notes from employer")
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ['gig', 'applicant']  # Prevent duplicate applications
    
    def __str__(self):
        return f"{self.applicant.username} -> {self.gig.title}"
    
    def get_absolute_url(self):
        return reverse('gigs:application_detail', kwargs={'pk': self.pk})
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.urls import reverse

class Gig(models.Model):
    """Simple gig/job posting model"""
    
    CATEGORY_CHOICES = [
        ('web_dev', 'Web Development'),
        ('design', 'Design & Graphics'),
        ('writing', 'Writing & Content'),
        ('marketing', 'Marketing & Social Media'),
        ('data_entry', 'Data Entry'),
        ('admin', 'Administrative'),
        ('tech_support', 'Tech Support'),
        ('other', 'Other'),
    ]
    
    # Essential fields only
    title = models.CharField(max_length=200)
    description = models.TextField()
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_gigs')
    budget = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        validators=[MinValueValidator(0.01)],
        help_text="Budget in USD"
    )
    location = models.CharField(max_length=100, default='Remote')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
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
        return reverse('gig_detail', kwargs={'pk': self.pk})
    
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
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Keep your existing Task model (unchanged)
class Task(models.Model):
    # Field definitions
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True, blank=True)
    
    # Methods
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """
        Check if task is past its due date and not completed.
        Returns:
            bool: True if task is overdue, False otherwise
        """
        if self.due_date and not self.completed:
            return self.due_date < timezone.now().date()
        return False
    
    # Meta class
    class Meta:
        ordering = ["completed", "due_date", "created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

# NEW: Add the Gig model (transformed from Task)
class Gig(models.Model):
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
    
    # Fields transformed from Task model
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline = models.DateField(null=True, blank=True)  # was: due_date
    is_active = models.BooleanField(default=True)       # was: completed (inverted logic)
    
    # New fields for job board functionality
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_gigs')
    budget = models.DecimalField(max_digits=8, decimal_places=2, help_text="Budget in USD")
    location = models.CharField(max_length=100, default='Remote')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    is_featured = models.BooleanField(default=False, help_text="Featured gigs appear at the top")
    
    # Methods
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """
        Check if gig is past its deadline and still active.
        Returns:
            bool: True if gig is overdue, False otherwise
        """
        if self.deadline and self.is_active:
            return self.deadline < timezone.now().date()
        return False
    
    def is_available(self):
        """
        Check if gig is available for applications.
        Returns:
            bool: True if gig is active and not overdue
        """
        return self.is_active and not self.is_overdue()
    
    # Meta class
    class Meta:
        ordering = ['-is_featured', '-created_at']  # Featured first, then newest
        verbose_name = "Gig"
        verbose_name_plural = "Gigs"
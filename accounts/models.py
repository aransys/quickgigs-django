from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class UserProfile(models.Model):
    """Simple user profile"""
    
    USER_TYPE_CHOICES = [
        ('employer', 'Employer'),
        ('freelancer', 'Freelancer'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='freelancer')
    bio = models.TextField(blank=True, help_text="Tell us about yourself")
    skills = models.TextField(
        blank=True, 
        help_text="Your skills (e.g., Python, Django, JavaScript)"
    )
    hourly_rate = models.DecimalField(
        max_digits=6, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Your hourly rate in USD"
    )
    company_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"
    
    @property
    def is_employer(self):
        return self.user_type == 'employer'
    
    @property
    def is_freelancer(self):
        return self.user_type == 'freelancer'
    
    @property
    def display_name(self):
        if self.user.first_name and self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}"
        return self.user.username


# Auto-create profile when user registers
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()
"""Signals for the accounts app.

We create a ``UserProfile`` immediately when a ``User`` row is created.
The previous implementation also re-saved the profile on every User save,
which was wasteful and could cause recursion under some edge cases.
"""

from __future__ import annotations

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

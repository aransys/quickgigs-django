"""Models for the accounts app."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models


class UserProfile(models.Model):
    """Extra profile fields hanging off the built-in User."""

    class Role(models.TextChoices):
        EMPLOYER = "employer", "Employer"
        FREELANCER = "freelancer", "Freelancer"
        UNSET = "unset", "Not chosen yet"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="userprofile",
    )
    user_type = models.CharField(max_length=20, choices=Role.choices, default=Role.UNSET)
    bio = models.TextField(blank=True, help_text="A short introduction.")
    skills = models.TextField(
        blank=True,
        help_text="Comma-separated, e.g. Python, Django, JavaScript",
    )
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Hourly rate in GBP.",
    )
    company_name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=32, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User profile"
        verbose_name_plural = "User profiles"

    def __str__(self) -> str:
        return f"{self.user.username} ({self.get_user_type_display()})"

    # -- Convenience accessors ---------------------------------------------

    @property
    def is_employer(self) -> bool:
        return self.user_type == self.Role.EMPLOYER

    @property
    def is_freelancer(self) -> bool:
        return self.user_type == self.Role.FREELANCER

    @property
    def has_chosen_role(self) -> bool:
        return self.user_type in (self.Role.EMPLOYER, self.Role.FREELANCER)

    @property
    def display_name(self) -> str:
        if self.user.first_name or self.user.last_name:
            return f"{self.user.first_name} {self.user.last_name}".strip()
        return self.user.username

    @property
    def skill_list(self) -> list[str]:
        return [s.strip() for s in self.skills.split(",") if s.strip()]

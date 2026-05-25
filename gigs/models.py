"""Models for the gigs app: Gig postings and Applications."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Gig(models.Model):
    """A job posting created by an employer."""

    class Category(models.TextChoices):
        WEB_DEV = "web_dev", "Web Development"
        DESIGN = "design", "Graphic Design"
        WRITING = "writing", "Content Writing"
        MARKETING = "marketing", "Digital Marketing"
        DATA_ENTRY = "data_entry", "Data Entry"
        TRANSLATION = "translation", "Translation"
        VIDEO_EDITING = "video_editing", "Video Editing"
        OTHER = "other", "Other"

    title = models.CharField(max_length=200)
    description = models.TextField()
    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posted_gigs",
    )
    budget = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Total project budget in GBP.",
    )
    location = models.CharField(
        max_length=100,
        help_text="Where the work happens — 'Remote', a city, or a country.",
    )
    category = models.CharField(max_length=50, choices=Category.choices)
    deadline = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    featured_until = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-created_at"]
        indexes = [
            models.Index(fields=["employer", "-created_at"]),
            models.Index(fields=["is_active", "is_featured"]),
            models.Index(fields=["category"]),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self) -> str:
        return reverse("gigs:gig_detail", kwargs={"pk": self.pk})

    @property
    def is_available(self) -> bool:
        if not self.is_active:
            return False
        return not (self.deadline and self.deadline < timezone.now().date())

    @property
    def is_overdue(self) -> bool:
        return bool(
            self.is_active
            and self.deadline
            and self.deadline < timezone.now().date()
        )

    @property
    def days_remaining(self) -> int | None:
        if not self.deadline:
            return None
        delta = self.deadline - timezone.now().date()
        return max(0, delta.days)


class Application(models.Model):
    """A freelancer's application to a gig."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        REVIEWED = "reviewed", "Reviewed"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"
        WITHDRAWN = "withdrawn", "Withdrawn"

    gig = models.ForeignKey(
        Gig, on_delete=models.CASCADE, related_name="applications"
    )
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
    )
    cover_letter = models.TextField(
        help_text="Explain why you're the right fit for this gig.",
    )
    proposed_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Your proposed rate for this project (optional).",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    employer_notes = models.TextField(
        blank=True,
        help_text="Private notes visible only to the employer.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["gig", "applicant"],
                name="unique_application_per_gig",
            ),
        ]
        indexes = [
            models.Index(fields=["applicant", "-created_at"]),
            models.Index(fields=["gig", "status"]),
        ]

    def __str__(self) -> str:
        return f"{self.applicant.username} → {self.gig.title}"

    def get_absolute_url(self) -> str:
        return reverse("gigs:application_detail", kwargs={"pk": self.pk})

    @property
    def is_withdrawable(self) -> bool:
        return self.status == self.Status.PENDING

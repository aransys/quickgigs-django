"""Forms for the gigs app."""

from __future__ import annotations

from decimal import Decimal

from django import forms

from .models import Application, Gig

# Shared Tailwind class set for all inputs.
INPUT_CLASSES = (
    "block w-full rounded-lg border-gray-300 bg-white px-4 py-2.5 text-gray-900 "
    "shadow-sm transition placeholder:text-gray-400 "
    "focus:border-brand-500 focus:outline-none focus:ring-2 focus:ring-brand-200"
)


class GigForm(forms.ModelForm):
    """Create or edit a gig posting."""

    class Meta:
        model = Gig
        fields = ["title", "description", "budget", "location", "category", "deadline"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "e.g. Build a landing page in Next.js",
                    "autofocus": "autofocus",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 6,
                    "placeholder": (
                        "Describe the project, requirements, " "and what success looks like."
                    ),
                }
            ),
            "budget": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "e.g. Remote, London, New York",
                }
            ),
            "category": forms.Select(attrs={"class": INPUT_CLASSES}),
            "deadline": forms.DateInput(attrs={"class": INPUT_CLASSES, "type": "date"}),
        }

    def clean_budget(self):
        budget = self.cleaned_data.get("budget")
        if budget is not None and budget <= Decimal("0"):
            raise forms.ValidationError("Budget must be greater than 0.")
        return budget


class ApplicationForm(forms.ModelForm):
    """Freelancer cover letter and optional rate."""

    class Meta:
        model = Application
        fields = ["cover_letter", "proposed_rate"]
        widgets = {
            "cover_letter": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 8,
                    "placeholder": (
                        "Why are you the right fit? Mention relevant experience, "
                        "similar projects you've shipped, and how you'd approach this."
                    ),
                }
            ),
            "proposed_rate": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "0.00",
                    "step": "0.01",
                    "min": "0.01",
                    "inputmode": "decimal",
                }
            ),
        }
        labels = {
            "cover_letter": "Cover letter",
            "proposed_rate": "Your proposed rate (optional, GBP)",
        }

    def clean_cover_letter(self):
        value = (self.cleaned_data.get("cover_letter") or "").strip()
        if len(value) < 50:
            raise forms.ValidationError(
                "Please write at least 50 characters — give the employer something to react to."
            )
        return value


class ApplicationStatusForm(forms.ModelForm):
    """Employer-facing form to triage applications."""

    class Meta:
        model = Application
        fields = ["status", "employer_notes"]
        widgets = {
            "status": forms.Select(attrs={"class": INPUT_CLASSES}),
            "employer_notes": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 3,
                    "placeholder": "Private notes — only you will see these.",
                }
            ),
        }

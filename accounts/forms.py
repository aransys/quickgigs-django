"""Forms for the accounts app."""

from __future__ import annotations

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from gigs.forms import INPUT_CLASSES

from .models import UserProfile


class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={"class": INPUT_CLASSES, "placeholder": "you@example.com"}),
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "Pick a username"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update(
            {"class": INPUT_CLASSES, "placeholder": "Create a strong password"}
        )
        self.fields["password2"].widget.attrs.update(
            {"class": INPUT_CLASSES, "placeholder": "Repeat the password"}
        )

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["bio", "skills", "hourly_rate", "company_name", "phone"]
        widgets = {
            "bio": forms.Textarea(
                attrs={
                    "class": INPUT_CLASSES,
                    "rows": 4,
                    "placeholder": "Tell employers about yourself.",
                }
            ),
            "skills": forms.TextInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "Python, Django, JavaScript, Figma…",
                }
            ),
            "hourly_rate": forms.NumberInput(
                attrs={
                    "class": INPUT_CLASSES,
                    "placeholder": "25.00",
                    "step": "0.01",
                    "min": "0.01",
                    "inputmode": "decimal",
                }
            ),
            "company_name": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "Your company name"},
            ),
            "phone": forms.TextInput(
                attrs={"class": INPUT_CLASSES, "placeholder": "+44 7…"},
            ),
        }

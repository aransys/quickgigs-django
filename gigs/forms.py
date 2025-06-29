from django import forms
from .models import Gig, Application
from decimal import Decimal

# from .models import Task

# class TaskForm(forms.ModelForm):
#     class Meta:
#         model = Task
#         fields = ["title", "description", "due_date", "completed"]
#         widgets = {
#             "due_date": forms.DateInput(attrs={"type": "date"}),
#             "description": forms.Textarea(attrs={"rows": 4}),
#         }

class GigForm(forms.ModelForm):
    class Meta:
        model = Gig
        fields = ['title', 'description', 'budget', 'location', 'category', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter a clear, descriptive title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Describe the project, requirements, and expectations'
            }),
            'budget': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Remote, London, New York'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
            'deadline': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }

    def clean_budget(self):
        budget = self.cleaned_data.get('budget')
        if budget and budget <= 0:
            raise forms.ValidationError("Budget must be greater than 0")
        return budget


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'proposed_rate']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Tell the employer why you\'re the perfect fit for this project. Highlight your relevant experience, skills, and approach to completing this work.',
                'required': True
            }),
            'proposed_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
        }
        labels = {
            'cover_letter': 'Cover Letter',
            'proposed_rate': 'Your Proposed Rate (Optional)',
        }

    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter and len(cover_letter.strip()) < 50:
            raise forms.ValidationError("Please provide a more detailed cover letter (at least 50 characters)")
        return cover_letter

    def clean_proposed_rate(self):
        proposed_rate = self.cleaned_data.get('proposed_rate')
        if proposed_rate and proposed_rate <= 0:
            raise forms.ValidationError("Proposed rate must be greater than 0")
        return proposed_rate


class ApplicationStatusForm(forms.ModelForm):
    """Form for employers to update application status"""
    class Meta:
        model = Application
        fields = ['status', 'employer_notes']
        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'employer_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add any notes about this application (optional)'
            }),
        }

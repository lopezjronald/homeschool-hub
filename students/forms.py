from django import forms
from django.utils import timezone

from .models import Student


class StudentForm(forms.ModelForm):
    """Form for creating and editing student profiles."""

    class Meta:
        model = Student
        fields = ["first_name", "last_name", "date_of_birth", "grade_level"]
        widgets = {
            "date_of_birth": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def clean_date_of_birth(self):
        """Ensure date of birth is not in the future."""
        dob = self.cleaned_data.get("date_of_birth")
        if dob and dob > timezone.now().date():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob

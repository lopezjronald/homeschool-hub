from django import forms

from .models import Curriculum


class CurriculumForm(forms.ModelForm):
    """Form for creating and editing curricula."""

    class Meta:
        model = Curriculum
        fields = ["name", "subject", "grade_level"]

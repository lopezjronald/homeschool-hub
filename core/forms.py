from django import forms

from core.models import Invitation


class TeacherInviteForm(forms.Form):
    """Form for inviting a teacher by email."""

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "placeholder": "teacher@example.com",
            "class": "form-control",
        }),
    )

    def __init__(self, *args, family=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.family = family

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if self.family and Invitation.objects.filter(
            email=email, family=self.family, status=Invitation.PENDING,
        ).exists():
            raise forms.ValidationError(
                "A pending invitation already exists for this email."
            )
        return email

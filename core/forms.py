from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from core.models import Family, Invitation

User = get_user_model()


class FamilyForm(forms.ModelForm):
    """Rename the household / family."""

    class Meta:
        model = Family
        fields = ("name",)
        widgets = {"name": forms.TextInput(attrs={"class": "form-control", "autocomplete": "off"})}


class TeacherInviteForm(forms.Form):
    """Invite someone to a family by email, choosing the access role."""

    # UI label -> stored FamilyMembership role. Co-parent stores as "parent".
    ROLE_CHOICES = [
        ("parent", "Co-parent — full access"),
        ("guardian", "Guardian — full access"),
        ("grandparent", "Grandparent — view only"),
        ("teacher", "Teacher — view only"),
    ]

    email = forms.EmailField(
        label="Their email",
        widget=forms.EmailInput(attrs={
            "placeholder": "name@example.com",
            "class": "form-control",
            "autocomplete": "off",
        }),
    )
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        initial="parent",
        required=False,
        label="Invite as",
        widget=forms.Select(attrs={"class": "form-select"}),
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

    def clean_role(self):
        role = self.cleaned_data.get("role") or "teacher"
        valid = {value for value, _ in self.ROLE_CHOICES}
        return role if role in valid else "teacher"


class InviteSignupForm(forms.ModelForm):
    """Registration for a new user joining a family via an invitation link.

    The invitation is the trust signal, so the account is created active (no
    separate email verification step).
    """

    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
    )
    password2 = forms.CharField(
        label="Confirm password",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", "class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control", "autocomplete": "username"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "autocomplete": "email"}),
        }

    def clean_email(self):
        return self.cleaned_data["email"].strip().lower()

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get("password1")
        p2 = cleaned.get("password2")
        if p1 and p2 and p1 != p2:
            self.add_error("password2", "Passwords do not match.")
        if p1:
            try:
                validate_password(p1)
            except ValidationError as exc:
                self.add_error("password1", exc)
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = True  # the invitation link verifies them
        if commit:
            user.save()
        return user

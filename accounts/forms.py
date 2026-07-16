from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.contrib.auth import get_user_model

from .models import UserProfile

User = get_user_model()


class EmailOrUsernameAuthenticationForm(AuthenticationForm):
    """Authentication form with field labeled 'Email or Username'."""

    username = UsernameField(label="Email or Username")


class RegisterForm(forms.ModelForm):
    """User registration form with password confirmation.

    Creates the user as inactive; a verification email is required to activate.
    """

    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Enter a strong password.",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
        help_text="Enter the same password for confirmation.",
    )

    class Meta:
        model = User
        fields = ("email", "username")

    def clean(self):
        """Ensure password fields match."""
        cleaned = super().clean()
        if cleaned.get("password1") != cleaned.get("password2"):
            self.add_error("password2", "Passwords do not match.")
        return cleaned

    def save(self, commit: bool = True):
        """Persist the user with `is_active=False` until verified."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        user.is_active = False
        if commit:
            user.save()
        return user


class AccountNameForm(forms.ModelForm):
    """Edit the user's display name."""

    class Meta:
        model = User
        fields = ("first_name", "last_name")
        widgets = {
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
        }


class ContactForm(forms.ModelForm):
    """Optional contact info (kept for charter/ES communication)."""

    class Meta:
        model = UserProfile
        fields = ("phone", "address_line1", "city", "state", "postal_code")
        widgets = {
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "address_line1": forms.TextInput(attrs={"autocomplete": "address-line1"}),
            "city": forms.TextInput(attrs={"autocomplete": "address-level2"}),
            "state": forms.TextInput(attrs={"autocomplete": "address-level1"}),
            "postal_code": forms.TextInput(attrs={"autocomplete": "postal-code"}),
        }


class NotificationsForm(forms.ModelForm):
    """Per-user notification preferences."""

    class Meta:
        model = UserProfile
        fields = ("notify_on_submission",)
        labels = {"notify_on_submission": "Email me when a child submits work to finalize"}


class PreferencesForm(forms.ModelForm):
    """Per-user preferences: display timezone + default landing page."""

    class Meta:
        model = UserProfile
        fields = ("timezone", "landing")


class ChangeEmailForm(forms.Form):
    """Request an email change — requires the current password (verify-then-commit)."""

    new_email = forms.EmailField(
        label="New email address",
        widget=forms.EmailInput(attrs={"autocomplete": "email"}),
    )
    current_password = forms.CharField(
        label="Confirm your current password",
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        pw = self.cleaned_data["current_password"]
        if not self.user or not self.user.check_password(pw):
            raise forms.ValidationError("That password doesn't match.")
        return pw

    def clean_new_email(self):
        email = (self.cleaned_data["new_email"] or "").strip().lower()
        if self.user and email == (self.user.email or "").lower():
            raise forms.ValidationError("That's already your email address.")
        qs = User.objects.filter(email__iexact=email)
        if self.user:
            qs = qs.exclude(pk=self.user.pk)
        if qs.exists():
            raise forms.ValidationError("That email is already in use by another account.")
        return email

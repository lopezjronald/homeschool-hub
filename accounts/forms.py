from django.contrib.auth.forms import AuthenticationForm, UsernameField
from django import forms
from django.contrib.auth import get_user_model

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
        fields = ("email", "username", "role")

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

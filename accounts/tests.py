from django.test import TestCase
from django.urls import reverse
from django.core import mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

User = get_user_model()


class RegistrationTests(TestCase):
    """Tests for user registration and email verification."""

    @classmethod
    def setUpTestData(cls):
        cls.existing_user = User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="testpass123",
            is_active=True,
        )

    def test_register_page_renders(self):
        """GET /accounts/register/ returns 200 and uses correct template."""
        response = self.client.get(reverse("accounts:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/register.html")

    def test_register_valid_user(self):
        """POST with valid data creates inactive user and redirects to login."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "securepass123",
            "password2": "securepass123",
            "role": "parent",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertRedirects(response, reverse("accounts:login"))

        user = User.objects.get(username="newuser")
        self.assertFalse(user.is_active)
        self.assertEqual(user.email, "newuser@example.com")

    def test_register_sends_verification_email(self):
        """Verification email is sent on registration."""
        data = {
            "username": "emailtest",
            "email": "emailtest@example.com",
            "password1": "securepass123",
            "password2": "securepass123",
            "role": "parent",
        }
        self.client.post(reverse("accounts:register"), data)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("emailtest@example.com", mail.outbox[0].to)

    def test_register_password_mismatch(self):
        """Form error when password1 != password2."""
        data = {
            "username": "mismatch",
            "email": "mismatch@example.com",
            "password1": "securepass123",
            "password2": "differentpass",
            "role": "parent",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "password2", "Passwords do not match.")

    def test_register_duplicate_email(self):
        """Form error when email already exists."""
        data = {
            "username": "newname",
            "email": "existing@example.com",
            "password1": "securepass123",
            "password2": "securepass123",
            "role": "parent",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "email", "User with this Email address already exists."
        )

    def test_register_duplicate_username(self):
        """Form error when username already exists."""
        data = {
            "username": "existing",
            "email": "different@example.com",
            "password1": "securepass123",
            "password2": "securepass123",
            "role": "parent",
        }
        response = self.client.post(reverse("accounts:register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"], "username", "A user with that username already exists."
        )

    def test_verify_valid_token_activates_user(self):
        """User becomes active after clicking valid verification link."""
        user = User.objects.create_user(
            username="toverify",
            email="toverify@example.com",
            password="testpass123",
            is_active=False,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(reverse("accounts:verify", kwargs={"uidb64": uidb64, "token": token}))
        self.assertRedirects(response, reverse("accounts:login"))

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_verify_invalid_token_rejected(self):
        """Invalid token shows error and user stays inactive."""
        user = User.objects.create_user(
            username="badtoken",
            email="badtoken@example.com",
            password="testpass123",
            is_active=False,
        )
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        response = self.client.get(reverse("accounts:verify", kwargs={"uidb64": uidb64, "token": "invalid-token"}))
        self.assertRedirects(response, reverse("accounts:login"))

        user.refresh_from_db()
        self.assertFalse(user.is_active)


class LoginTests(TestCase):
    """Tests for user login."""

    @classmethod
    def setUpTestData(cls):
        cls.active_user = User.objects.create_user(
            username="activeuser",
            email="active@example.com",
            password="testpass123",
            is_active=True,
        )
        cls.inactive_user = User.objects.create_user(
            username="inactiveuser",
            email="inactive@example.com",
            password="testpass123",
            is_active=False,
        )

    def test_login_page_renders(self):
        """GET /accounts/login/ returns 200 and uses correct template."""
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_login_with_username(self):
        """Can log in using username + password."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "activeuser", "password": "testpass123"},
        )
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_email(self):
        """Can log in using email + password."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "active@example.com", "password": "testpass123"},
        )
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_email_case_insensitive(self):
        """Email comparison ignores case."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "ACTIVE@EXAMPLE.COM", "password": "testpass123"},
        )
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_wrong_password_rejected(self):
        """Invalid password fails authentication."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "activeuser", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_inactive_user_rejected(self):
        """Unverified (inactive) user cannot log in."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "inactiveuser", "password": "testpass123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_redirects_to_home(self):
        """Successful login redirects to /."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "activeuser", "password": "testpass123"},
        )
        self.assertRedirects(response, "/")


class LogoutTests(TestCase):
    """Tests for user logout."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="logoutuser",
            email="logout@example.com",
            password="testpass123",
            is_active=True,
        )

    def test_logout_post_succeeds(self):
        """POST to /accounts/logout/ logs user out and redirects to home."""
        self.client.login(username="logoutuser", password="testpass123")
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("home"))

    def test_logout_get_forbidden(self):
        """GET to /accounts/logout/ returns 403."""
        self.client.login(username="logoutuser", password="testpass123")
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 403)

    def test_logout_clears_session(self):
        """After logout, user is anonymous."""
        self.client.login(username="logoutuser", password="testpass123")
        self.client.post(reverse("accounts:logout"))
        response = self.client.get(reverse("home"))
        self.assertFalse(response.wsgi_request.user.is_authenticated)


class PasswordResetTests(TestCase):
    """Tests for password reset flow."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="resetuser",
            email="reset@example.com",
            password="oldpassword123",
            is_active=True,
        )

    def test_password_reset_page_renders(self):
        """GET /accounts/password-reset/ returns 200."""
        response = self.client.get(reverse("accounts:password_reset"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/password_reset.html")

    def test_password_reset_sends_email(self):
        """POST with valid email sends reset email."""
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "reset@example.com"},
        )
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("reset@example.com", mail.outbox[0].to)

    def test_password_reset_invalid_email_no_error(self):
        """POST with unknown email still shows done page (security)."""
        response = self.client.post(
            reverse("accounts:password_reset"),
            {"email": "nonexistent@example.com"},
        )
        self.assertRedirects(response, reverse("accounts:password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_password_reset_confirm_page_renders(self):
        """Valid token shows password form."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        response = self.client.get(
            reverse("accounts:password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
        )
        # Django redirects to set-password URL with token replaced by 'set-password'
        self.assertEqual(response.status_code, 302)

    def test_password_reset_confirm_changes_password(self):
        """Submitting new password updates user."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)

        # First GET to set session token
        reset_url = reverse("accounts:password_reset_confirm", kwargs={"uidb64": uidb64, "token": token})
        response = self.client.get(reset_url, follow=True)

        # POST new password to the redirected URL
        final_url = response.redirect_chain[-1][0]
        response = self.client.post(
            final_url,
            {"new_password1": "newpassword456", "new_password2": "newpassword456"},
        )
        self.assertRedirects(response, reverse("accounts:password_reset_complete"))

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("newpassword456"))

    def test_password_reset_invalid_token_rejected(self):
        """Invalid token shows error page."""
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        response = self.client.get(
            reverse("accounts:password_reset_confirm", kwargs={"uidb64": uidb64, "token": "invalid-token"})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "invalid")

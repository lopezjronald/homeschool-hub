from django.test import TestCase, override_settings
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
        self.assertRedirects(response, reverse("accounts:post_login"), fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_with_email(self):
        """Can log in using email + password."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "active@example.com", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("accounts:post_login"), fetch_redirect_response=False)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_email_case_insensitive(self):
        """Email comparison ignores case."""
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "ACTIVE@EXAMPLE.COM", "password": "testpass123"},
        )
        self.assertRedirects(response, reverse("accounts:post_login"), fetch_redirect_response=False)
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
        self.assertRedirects(response, reverse("accounts:post_login"), fetch_redirect_response=False)


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


class OnboardingWelcomeTests(TestCase):
    """Welcome page + post-login routing + UserProfile (HH-104, onboarding Phase 2)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="p2", email="p2@example.com", password="pw", is_active=True,
        )

    def test_post_login_new_user_routes_to_welcome(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:post_login"))
        self.assertRedirects(resp, reverse("accounts:welcome"), fetch_redirect_response=False)

    def test_welcome_renders_for_new_user(self):
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:welcome"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "What brings you here")

    def test_welcome_post_records_goal_and_marks_seen(self):
        from accounts.models import UserProfile

        self.client.force_login(self.user)
        resp = self.client.post(reverse("accounts:welcome"), {"goal": "charter"})
        self.assertRedirects(resp, reverse("home"), fetch_redirect_response=False)
        p = UserProfile.objects.get(user=self.user)
        self.assertTrue(p.has_seen_welcome)
        self.assertEqual(p.onboarding_goal, "charter")

    def test_skip_marks_seen_without_recording_goal(self):
        from accounts.models import UserProfile

        self.client.force_login(self.user)
        resp = self.client.post(reverse("accounts:welcome"), {"goal": "charter", "skip": "1"})
        self.assertRedirects(resp, reverse("home"), fetch_redirect_response=False)
        p = UserProfile.objects.get(user=self.user)
        self.assertTrue(p.has_seen_welcome)
        self.assertEqual(p.onboarding_goal, "")

    def test_review_goal_routes_to_progress(self):
        self.client.force_login(self.user)
        resp = self.client.post(reverse("accounts:welcome"), {"goal": "review"})
        self.assertRedirects(resp, reverse("dashboard:dashboard"), fetch_redirect_response=False)

    def test_seen_editor_routes_home(self):
        from accounts.models import UserProfile

        UserProfile.objects.create(user=self.user, has_seen_welcome=True)
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:post_login"))
        self.assertRedirects(resp, reverse("home"), fetch_redirect_response=False)

    def test_seen_reviewer_routes_to_progress(self):
        from accounts.models import UserProfile
        from core.models import Family, FamilyMembership

        fam = Family.objects.create(name="Rev Fam")
        FamilyMembership.objects.create(user=self.user, family=fam, role="grandparent")
        UserProfile.objects.create(user=self.user, has_seen_welcome=True)
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:post_login"))
        self.assertRedirects(resp, reverse("dashboard:dashboard"), fetch_redirect_response=False)

    def test_already_seen_welcome_redirects_away(self):
        from accounts.models import UserProfile

        UserProfile.objects.create(user=self.user, has_seen_welcome=True)
        self.client.force_login(self.user)
        resp = self.client.get(reverse("accounts:welcome"))
        self.assertRedirects(resp, reverse("home"), fetch_redirect_response=False)


class HintDismissTests(TestCase):
    """Dismissible just-in-time hints (HH-105, onboarding Phase 3)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="hinter", email="h@example.com", password="pw", is_active=True,
        )

    def test_hint_shows_then_hides_after_dismiss(self):
        self.client.force_login(self.user)
        curricula = reverse("curricula:curriculum_list")

        resp = self.client.get(curricula)
        self.assertContains(resp, "Got it")  # hint present for a new user

        redirect = self.client.post(
            reverse("accounts:dismiss_hint"),
            {"key": "curricula_online", "next": curricula},
        )
        self.assertRedirects(redirect, curricula, fetch_redirect_response=False)

        from accounts.models import UserProfile
        self.assertIn("curricula_online", UserProfile.objects.get(user=self.user).dismissed_hints)

        resp2 = self.client.get(curricula)
        self.assertNotContains(resp2, "Got it")  # stays dismissed

    def test_dismiss_rejects_offsite_redirect(self):
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse("accounts:dismiss_hint"),
            {"key": "curricula_online", "next": "https://evil.example.com/"},
        )
        self.assertRedirects(resp, reverse("home"), fetch_redirect_response=False)


class SettingsTests(TestCase):
    """The logged-in settings hub: name, contact, notifications, email, password."""

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username="su", email="su@e.com", password="pw-orig-123", is_active=True, first_name="Sam",
        )

    def setUp(self):
        self.client.login(username="su", password="pw-orig-123")

    def test_settings_requires_login(self):
        self.client.logout()
        resp = self.client.get(reverse("accounts:settings"))
        self.assertEqual(resp.status_code, 302)
        self.assertIn("login", resp.url)

    def test_settings_renders(self):
        resp = self.client.get(reverse("accounts:settings"))
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Settings")
        self.assertContains(resp, "su@e.com")

    def test_update_name(self):
        self.client.post(reverse("accounts:account_update"), {"first_name": "Samuel", "last_name": "Jones"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Samuel")
        self.assertEqual(self.user.last_name, "Jones")

    def test_update_contact_and_notifications(self):
        from accounts.models import UserProfile

        self.client.post(reverse("accounts:contact_update"), {
            "phone": "555-1234", "address_line1": "1 Main St", "city": "Town", "state": "CA", "postal_code": "90000",
        })
        self.client.post(reverse("accounts:notifications_update"), {})   # checkbox omitted -> False
        prof = UserProfile.get_for(self.user)
        self.assertEqual(prof.phone, "555-1234")
        self.assertEqual(prof.city, "Town")
        self.assertFalse(prof.notify_on_submission)

    def test_change_password_keeps_session(self):
        resp = self.client.post(reverse("accounts:password_change"), {
            "old_password": "pw-orig-123", "new_password1": "brand-new-456", "new_password2": "brand-new-456",
        })
        self.assertRedirects(resp, reverse("accounts:password_change_done"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("brand-new-456"))
        self.assertEqual(self.client.get(reverse("accounts:settings")).status_code, 200)   # still signed in

    def test_change_email_requires_correct_password(self):
        self.client.post(reverse("accounts:change_email"), {"new_email": "new@e.com", "current_password": "wrong"})
        self.user.refresh_from_db()
        self.assertIsNone(self.user.pending_email)
        self.assertEqual(len(mail.outbox), 0)

    def test_change_email_sends_link_and_defers_commit(self):
        self.client.post(reverse("accounts:change_email"), {"new_email": "New@e.com", "current_password": "pw-orig-123"})
        self.user.refresh_from_db()
        self.assertEqual(self.user.pending_email, "new@e.com")   # normalized/lowercased
        self.assertEqual(self.user.email, "su@e.com")            # not committed yet
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["new@e.com"])       # link goes to the NEW address

    def test_change_email_confirm_commits(self):
        self.client.post(reverse("accounts:change_email"), {"new_email": "new@e.com", "current_password": "pw-orig-123"})
        self.user.refresh_from_db()
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        resp = self.client.get(reverse("accounts:change_email_confirm", kwargs={"uidb64": uid, "token": token}))
        self.assertRedirects(resp, reverse("accounts:settings"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "new@e.com")
        self.assertIsNone(self.user.pending_email)

    def test_change_email_confirm_bad_token_does_nothing(self):
        self.client.post(reverse("accounts:change_email"), {"new_email": "new@e.com", "current_password": "pw-orig-123"})
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        self.client.get(reverse("accounts:change_email_confirm", kwargs={"uidb64": uid, "token": "bad-token"}))
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, "su@e.com")            # unchanged

    def test_change_email_rejects_taken_address(self):
        User.objects.create_user(username="taken", email="taken@e.com", password="pw", is_active=True)
        self.client.post(reverse("accounts:change_email"), {"new_email": "taken@e.com", "current_password": "pw-orig-123"})
        self.user.refresh_from_db()
        self.assertIsNone(self.user.pending_email)
        self.assertEqual(len(mail.outbox), 0)


_GOOGLE_CONFIGURED = {
    "google": {"APP": {"client_id": "test-id", "secret": "test-secret", "key": ""}},
}


class SocialAuthTests(TestCase):
    """django-allauth social login is additive and gated on configuration."""

    def test_existing_password_login_still_works(self):
        User.objects.create_user(username="pw", email="pw@e.com", password="secret123", is_active=True)
        resp = self.client.post(reverse("accounts:login"), {"username": "pw", "password": "secret123"})
        self.assertEqual(resp.status_code, 302)
        self.assertIn("_auth_user_id", self.client.session)

    def test_no_social_button_when_unconfigured(self):
        resp = self.client.get(reverse("accounts:login"))
        self.assertEqual(resp.status_code, 200)
        self.assertNotContains(resp, "Sign in with")

    @override_settings(SOCIALACCOUNT_PROVIDERS=_GOOGLE_CONFIGURED)
    def test_social_button_shows_when_configured(self):
        resp = self.client.get(reverse("accounts:login"))
        self.assertContains(resp, "Sign in with Google")
        self.assertContains(resp, "/auth/google/login/")   # provider login mounted at /auth/

    def test_allauth_urls_mounted_under_auth(self):
        self.assertTrue(reverse("socialaccount_connections").startswith("/auth/"))

    def test_allauth_local_signup_is_closed(self):
        # allauth's own /auth/signup/ must NOT create accounts — the app owns
        # registration (with email verification). This is the security gate that
        # keeps allauth from minting active, unverified accounts.
        before = User.objects.count()
        self.client.post("/auth/signup/", {
            "email": "sneaky@e.com", "username": "sneaky",
            "password1": "xyzpass12345", "password2": "xyzpass12345",
        })
        self.assertEqual(User.objects.count(), before)
        self.assertFalse(User.objects.filter(email="sneaky@e.com").exists())

    def test_social_signup_stays_open(self):
        # Closing LOCAL signup must not close social signup (new Google users).
        from accounts.adapters import SocialSignupAdapter
        self.assertTrue(SocialSignupAdapter().is_open_for_signup(None, None))

    def test_social_login_links_existing_account_by_verified_email(self):
        # A Google login whose verified email matches an existing account is
        # linked via connect() (password preserved), not dead-ended or duplicated.
        from unittest.mock import MagicMock
        from allauth.account.models import EmailAddress
        from accounts.adapters import SocialSignupAdapter

        user = User.objects.create_user(username="ex", email="ex@e.com", password="keepme123", is_active=True)
        sl = MagicMock(is_existing=False)
        sl.user = MagicMock(email="ex@e.com")
        sl.email_addresses = [EmailAddress(email="ex@e.com", verified=True)]
        SocialSignupAdapter().pre_social_login(MagicMock(), sl)
        sl.connect.assert_called_once()
        self.assertEqual(sl.connect.call_args.args[1], user)
        user.refresh_from_db()
        self.assertTrue(user.has_usable_password())   # connect never wipes the password

    def test_social_login_ignores_unverified_email(self):
        from unittest.mock import MagicMock
        from allauth.account.models import EmailAddress
        from accounts.adapters import SocialSignupAdapter

        User.objects.create_user(username="ex2", email="ex2@e.com", password="p", is_active=True)
        sl = MagicMock(is_existing=False)
        sl.user = MagicMock(email="ex2@e.com")
        sl.email_addresses = [EmailAddress(email="ex2@e.com", verified=False)]
        SocialSignupAdapter().pre_social_login(MagicMock(), sl)
        sl.connect.assert_not_called()   # unverified provider email must not auto-link

    @override_settings(SOCIALACCOUNT_PROVIDERS=_GOOGLE_CONFIGURED)
    def test_settings_shows_connected_accounts_card_when_configured(self):
        User.objects.create_user(username="s", email="s@e.com", password="pw", is_active=True)
        self.client.login(username="s", password="pw")
        resp = self.client.get(reverse("accounts:settings"))
        self.assertContains(resp, "Connected accounts")
        self.assertContains(resp, "Connect Google")

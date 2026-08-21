from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter


class NoLocalSignupAdapter(DefaultAccountAdapter):
    """Disable allauth's OWN local email/password signup.

    The app runs its own registration + email-verification flow at
    ``/accounts/register/``; allauth is mounted only to provide *social* login.
    Without this, allauth's ``/auth/signup/`` would create active, unverified,
    auto-logged-in accounts, bypassing our verification gate.

    NOTE: social signup is governed by ``SocialSignupAdapter`` below — the default
    social adapter delegates its ``is_open_for_signup`` to *this* account adapter,
    which would (wrongly) close social signup too, so we override it there.
    """

    def is_open_for_signup(self, request):
        return False


class SocialSignupAdapter(DefaultSocialAccountAdapter):
    """Policy for social (Google) logins, kept separate from the local-signup gate.

    - Social signup stays OPEN so new users can join via Google even though local
      email/password signup is closed.
    - If a social login's PROVIDER-VERIFIED email matches an existing account, we
      link it to that account with ``sociallogin.connect`` (which preserves the
      local password) instead of creating a duplicate or dead-ending at the
      "signup closed" page. Only verified emails are trusted (Google sets this
      from its ``email_verified`` claim), so this can't hijack an account whose
      email the requester doesn't control. This deliberately avoids allauth's
      ``SOCIALACCOUNT_EMAIL_AUTHENTICATION`` path, which wipes the local password.
    """

    def is_open_for_signup(self, request, sociallogin):
        # Closed unless the deploy says otherwise. This returned a flat True,
        # which meant anybody with a Google account could create one here — the
        # register page was closed and this door was standing open beside it.
        #
        # Note what this does NOT block: an existing user signing in. allauth
        # only consults this when the social identity is unknown AND cannot be
        # connected to an account, so the button on the login page keeps working
        # for the people who are already here. `pre_social_login` below runs
        # first and links a provider-verified email to its existing account.
        from django.conf import settings

        return bool(getattr(settings, "PUBLIC_SIGNUP_ENABLED", False))

    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return  # this Google account is already linked — just log in
        email = (getattr(sociallogin.user, "email", "") or "").lower()
        verified = {e.email.lower() for e in sociallogin.email_addresses if e.verified}
        if not email or email not in verified:
            return
        from django.contrib.auth import get_user_model

        user = get_user_model().objects.filter(email__iexact=email).first()
        if user is not None:
            sociallogin.connect(request, user)

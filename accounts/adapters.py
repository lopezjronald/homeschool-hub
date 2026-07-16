from allauth.account.adapter import DefaultAccountAdapter


class NoLocalSignupAdapter(DefaultAccountAdapter):
    """Disable allauth's OWN local email/password signup.

    The app runs its own registration + email-verification flow at
    ``/accounts/register/``; allauth is mounted only to provide *social* login.
    Without this, allauth's ``/auth/signup/`` would create active, unverified,
    auto-logged-in accounts, bypassing our verification gate. Social signup for
    new Google users is governed by the separate social-account adapter and is
    unaffected.
    """

    def is_open_for_signup(self, request):
        return False

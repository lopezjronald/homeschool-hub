from core.models import FamilyMembership
from core.utils import get_selected_family, get_user_families


def signup_open(request):
    """Whether anyone may create an account, for the templates that offer it.

    A "Register" link that leads to "invitation only" is a small lie the nav
    tells every visitor. The flag is the single source of truth for both, so
    the link and the page can never disagree.
    """
    from django.conf import settings

    return {"public_signup_enabled":
            bool(getattr(settings, "PUBLIC_SIGNUP_ENABLED", False))}


def family_context(request):
    """Provide family data to all templates for the navbar switcher."""
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {}

    selected = get_selected_family(request)
    can_invite = False
    if selected:
        can_invite = FamilyMembership.objects.filter(
            user=request.user, family=selected, role="parent",
        ).exists()

    # Action-inbox nav badge. Only editors have actionable items, and the count is
    # kept to a few COUNTs (it runs on every authenticated page — see inbox_count).
    from core.permissions import user_can_edit
    from core.services import inbox_count

    can_edit = user_can_edit(request.user)
    badge = inbox_count(request, selected) if can_edit else 0

    return {
        "user_families": get_user_families(request.user),
        "selected_family": selected,
        "can_invite_teacher": can_invite,
        "inbox_visible": can_edit,
        "inbox_badge_count": badge,
    }


def onboarding_hints(request):
    """Expose the set of just-in-time hints the user has already dismissed."""
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {"dismissed_hints": []}
    from accounts.models import UserProfile

    return {"dismissed_hints": UserProfile.get_for(request.user).dismissed_hints}

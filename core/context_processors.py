from core.models import FamilyMembership
from core.utils import get_selected_family, get_user_families


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

    return {
        "user_families": get_user_families(request.user),
        "selected_family": selected,
        "can_invite_teacher": can_invite,
    }

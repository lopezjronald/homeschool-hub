from core.utils import get_selected_family, get_user_families


def family_context(request):
    """Provide family data to all templates for the navbar switcher."""
    if not hasattr(request, "user") or not request.user.is_authenticated:
        return {}

    return {
        "user_families": get_user_families(request.user),
        "selected_family": get_selected_family(request),
    }

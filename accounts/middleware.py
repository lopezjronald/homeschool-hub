from zoneinfo import ZoneInfo

from django.utils import timezone

from .models import UserProfile


class TimezoneMiddleware:
    """Render dates/times in the signed-in user's preferred timezone.

    Activates ``UserProfile.timezone`` for the request (falling back to the
    project default ``settings.TIME_ZONE`` when unset or invalid). Anonymous
    requests use the default.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        tzname = ""
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            tzname = UserProfile.get_for(user).timezone

        if tzname:
            try:
                timezone.activate(ZoneInfo(tzname))
            except Exception:  # noqa: BLE001 — bad/removed zone → fall back to default
                timezone.deactivate()
        else:
            timezone.deactivate()

        return self.get_response(request)

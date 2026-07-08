from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    """Landing page. For a signed-in parent it's a hub of tiles with live counts."""
    context = {}
    if request.user.is_authenticated:
        from activities.models import ExternalActivity
        from core.permissions import scoped_queryset
        from core.utils import get_selected_family
        from curricula.models import Curriculum
        from students.models import Student

        family = get_selected_family(request)
        context["children_count"] = scoped_queryset(
            Student.objects.all(), request.user, family,
        ).count()
        context["curricula_count"] = scoped_queryset(
            Curriculum.objects.all(), request.user, family,
        ).count()
        activities = scoped_queryset(
            ExternalActivity.objects.all(), request.user, family,
        ).select_related("student")
        context["activities_count"] = activities.count()
        # `is_due` is a Python property (cadence + last-logged + snooze/mute),
        # so evaluate in-process rather than in the DB.
        context["due_activities"] = [a for a in activities if a.is_due]
    return render(request, "home.html", context)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("students/", include(("students.urls", "students"), namespace="students")),
    path("curricula/", include(("curricula.urls", "curricula"), namespace="curricula")),
    path("assignments/", include(("assignments.urls", "assignments"), namespace="assignments")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
    path("worklog/", include(("worklog.urls", "worklog"), namespace="worklog")),
    path("tutor/", include(("tutor.urls", "tutor"), namespace="tutor")),
    path("portal/", include(("portal.urls", "portal"), namespace="portal")),
    path("activities/", include(("activities.urls", "activities"), namespace="activities")),
    path("core/", include(("core.urls", "core"), namespace="core")),
]

# Serve static files in DEBUG mode (fallback if WhiteNoise isn't handling them)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files locally in DEBUG mode when not using R2
if settings.DEBUG and not getattr(settings, "USE_R2", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render  # <-- THIS LINE IS THE FIX
from django.conf import settings
from django.conf.urls.static import static


def home(request):
    # Now that 'render' is imported, this line will work correctly.
    return render(request, "home.html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
    path("students/", include(("students.urls", "students"), namespace="students")),
    path("curricula/", include(("curricula.urls", "curricula"), namespace="curricula")),
    path("assignments/", include(("assignments.urls", "assignments"), namespace="assignments")),
    path("dashboard/", include(("dashboard.urls", "dashboard"), namespace="dashboard")),
]

# Serve static files in DEBUG mode (fallback if WhiteNoise isn't handling them)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Serve media files locally in DEBUG mode when not using R2
if settings.DEBUG and not getattr(settings, "USE_R2", False):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
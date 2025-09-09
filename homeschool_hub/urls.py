# homeschool_hub/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse          # ← add this import
from django.conf import settings
from django.conf.urls.static import static

def home(_request):
    return HttpResponse("<h1>Welcome</h1>")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("accounts/", include(("accounts.urls", "accounts"), namespace="accounts")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.urls import path

from . import views

app_name = "tutor"

urlpatterns = [
    path("worklog/<int:entry_pk>/assess/", views.assess_create, name="assess_create"),
    path("assessments/<int:pk>/", views.assess_detail, name="assess_detail"),
    path("assessments/<int:pk>/finalize/", views.assess_finalize, name="assess_finalize"),
]

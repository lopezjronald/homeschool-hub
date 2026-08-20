from django.urls import path

from . import views

app_name = "tutor"

urlpatterns = [
    path("worklog/<int:entry_pk>/assess/", views.assess_create, name="assess_create"),
    path("worklog/<int:entry_pk>/assess/pending/", views.assess_pending, name="assess_pending"),
    path("worklog/<int:entry_pk>/assess/status/", views.assess_status, name="assess_status"),
    path("assessments/", views.assessment_list, name="assessment_list"),
    path("assessments/<int:pk>/", views.assess_detail, name="assess_detail"),
    path("assessments/<int:pk>/finalize/", views.assess_finalize, name="assess_finalize"),
    path("materials/<int:pk>/", views.material_detail, name="material_detail"),
    path("materials/<int:pk>/approve/", views.material_approve, name="material_approve"),
    path("curricula/<int:curriculum_pk>/discussion/", views.discussion_guide, name="discussion_guide"),
    path("curricula/<int:curriculum_pk>/lexicon-guide/", views.lexicon_guide, name="lexicon_guide"),
    path("curricula/<int:curriculum_pk>/dickinson-guide/", views.dickinson_guide, name="dickinson_guide"),
    path("curricula/<int:curriculum_pk>/onetrue-guide/", views.onetrue_guide, name="onetrue_guide"),
    path("curricula/<int:curriculum_pk>/poetry-guide/", views.poetry_guide, name="poetry_guide"),
]

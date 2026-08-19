from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.student_list, name="student_list"),
    path("add/", views.student_create, name="student_create"),
    path("<int:pk>/enter-portal/", views.enter_portal, name="enter_portal"),
    path("<int:pk>/", views.student_detail, name="student_detail"),
    path("<int:pk>/work/<int:curriculum_id>/", views.student_work, name="student_work"),
    path("<int:pk>/work/set/<int:set_pk>/", views.student_work_set, name="student_work_set"),
    path("<int:pk>/work/set/<int:set_pk>/approve/", views.student_work_set_approve,
         name="student_work_set_approve"),
    # Per-child lesson complete/skip tracking (HH-141)
    path("<int:pk>/lessons/<int:curriculum_id>/", views.student_lessons, name="student_lessons"),
    path("<int:pk>/lessons/<int:curriculum_id>/mark/", views.lesson_mark, name="lesson_mark"),
    path("<int:pk>/lessons/<int:curriculum_id>/save/", views.lessons_save, name="lessons_save"),
    path("<int:pk>/lessons/<int:curriculum_id>/skip-practice/", views.lessons_skip_practice, name="lessons_skip_practice"),
    path("<int:pk>/edit/", views.student_update, name="student_update"),
    path("<int:pk>/delete/", views.student_delete, name="student_delete"),
]

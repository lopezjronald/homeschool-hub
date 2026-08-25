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
    # Finished work filed against ONE lesson — maths is done on paper (HH-167)
    path("<int:pk>/lessons/<int:curriculum_id>/work/<int:lesson_id>/",
         views.lesson_work, name="lesson_work"),
    path("<int:pk>/lessons/<int:curriculum_id>/work/<int:lesson_id>/remove/",
         views.lesson_work_delete, name="lesson_work_delete"),
    path("<int:pk>/edit/", views.student_update, name="student_update"),
    path("<int:pk>/delete/", views.student_delete, name="student_delete"),
]

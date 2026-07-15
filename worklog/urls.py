from django.urls import path

from . import views

app_name = "worklog"

urlpatterns = [
    path("", views.worklog_list, name="worklog_list"),
    path("report/", views.worklog_report, name="worklog_report"),
    path("charter-report/", views.charter_report, name="charter_report"),
    path("charter-report/<int:entry_pk>/stamp/", views.report_stamp, name="report_stamp"),
    path("sample-report/", views.sample_report, name="sample_report"),
    path("add/", views.worklog_create, name="worklog_create"),
    path("<int:pk>/", views.worklog_detail, name="worklog_detail"),
    path("<int:pk>/edit/", views.worklog_update, name="worklog_update"),
    path("<int:pk>/delete/", views.worklog_delete, name="worklog_delete"),
]

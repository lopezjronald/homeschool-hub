from django.urls import path

from . import views

app_name = "lingua"

urlpatterns = [
    path("approvals/", views.batch_approval, name="approvals"),
    path("progress/", views.progress, name="progress"),
    path("read/<int:story_id>/", views.read_story, name="read"),
    # Curated Library List + physical-book reading log (LGA-75)
    path("library/", views.library_list, name="library_list"),
    path("books/", views.book_log, name="book_log"),
    path("books/add/", views.book_log_add, name="book_log_add"),
    path("books/<int:entry_id>/delete/", views.book_log_delete, name="book_log_delete"),
]

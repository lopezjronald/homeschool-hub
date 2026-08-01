from django.urls import path

from . import views

app_name = "lingua"

urlpatterns = [
    path("approvals/", views.batch_approval, name="approvals"),
    path("progress/", views.progress, name="progress"),
    path("read/<int:story_id>/", views.read_story, name="read"),
    # Curated Library List + physical-book reading log (LGA-75)
    # "La sesión": the parent-led session kit — routine + phrases + printable sheet.
    path("session/", views.session_kit, name="session"),
    path("session/error/", views.session_log_error, name="session_log_error"),
    path("library/", views.library_list, name="library_list"),
    path("library/mark-read/", views.library_mark_read, name="mark_read"),
    # The parent reading log lives in the Work Log now; keep the name so stale
    # links and bookmarks land somewhere sensible instead of 500-ing (HH-143).
    path("books/", views.book_log_redirect, name="book_log"),
]

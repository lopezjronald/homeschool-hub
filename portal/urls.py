from django.urls import path

from . import views

app_name = "portal"

urlpatterns = [
    path("<str:token>/", views.portal_home, name="portal_home"),
    path("<str:token>/materials/<int:pk>/done/", views.portal_material_done,
         name="portal_material_done"),
    path("<str:token>/calendar/", views.portal_calendar, name="portal_calendar"),
    path("<str:token>/calendar/feed/", views.portal_calendar_feed, name="portal_calendar_feed"),
    # Lingua (Spanish) kid surface — tokenless, resolves Student→Learner in this host
    # layer and delegates the reader to lingua.views.render_reader (keeps lingua core
    # free of host imports, D-04).
    path("<str:token>/lingua/", views.lingua_plan, name="lingua_plan"),
    path("<str:token>/lingua/path/", views.lingua_path, name="lingua_path"),
    path("<str:token>/lingua/path/check/", views.lingua_path_check, name="lingua_path_check"),
    path("<str:token>/lingua/library/", views.lingua_library, name="lingua_library"),
    path("<str:token>/lingua/books/", views.lingua_books, name="lingua_books"),
    path("<str:token>/lingua/books/log/", views.lingua_book_log, name="lingua_book_log"),
    path("<str:token>/lingua/phonics/", views.lingua_phonics, name="lingua_phonics"),
    path("<str:token>/lingua/listen/", views.lingua_listen, name="lingua_listen"),
    path("<str:token>/lingua/listen/log/", views.lingua_listen_log, name="lingua_listen_log"),
    path("<str:token>/lingua/listen/open/<int:resource_id>/", views.lingua_listen_open,
         name="lingua_listen_open"),
    path("<str:token>/lingua/tutor/", views.lingua_tutor, name="lingua_tutor"),
    path("<str:token>/lingua/tutor/<int:packet_id>/", views.lingua_tutor_packet, name="lingua_tutor_packet"),
    path("<str:token>/lingua/capture-word/", views.lingua_capture_word, name="lingua_capture_word"),
    path("<str:token>/lingua/read/<int:story_id>/", views.lingua_read, name="lingua_read"),
    path("<str:token>/lingua/read/<int:story_id>/finish/", views.lingua_finish, name="lingua_finish"),
    path("<str:token>/lingua/read/<int:story_id>/record/", views.lingua_record, name="lingua_record"),
    path("<str:token>/parents/", views.portal_parent_gate, name="portal_parent_gate"),
    path("<str:token>/subject/<int:curriculum_id>/", views.portal_subject, name="portal_subject"),
    path("<str:token>/materials/<int:pk>/", views.portal_material, name="portal_material"),
    path("<str:token>/questions/<int:set_pk>/", views.portal_questions, name="portal_questions"),
    path("<str:token>/questions/<int:set_pk>/autosave/", views.portal_autosave, name="portal_autosave"),
    path("<str:token>/questions/<int:set_pk>/word-help/", views.portal_word_help, name="portal_word_help"),
    path("<str:token>/questions/<int:set_pk>/spellcheck/", views.portal_spellcheck, name="portal_spellcheck"),
    path(
        "<str:token>/questions/<int:set_pk>/coach/",
        views.portal_draft_feedback,
        name="portal_draft_feedback",
    ),
    path("<str:token>/questions/<int:set_pk>/feedback/", views.portal_feedback, name="portal_feedback"),
    path(
        "<str:token>/questions/<int:set_pk>/feedback/generate/",
        views.portal_feedback_generate,
        name="portal_feedback_generate",
    ),
    path(
        "<str:token>/questions/<int:set_pk>/feedback/start/",
        views.portal_feedback_start,
        name="portal_feedback_start",
    ),
    path(
        "<str:token>/questions/<int:set_pk>/feedback/status/",
        views.portal_feedback_status,
        name="portal_feedback_status",
    ),
]

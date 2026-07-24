from django.apps import AppConfig


class LinguaConfig(AppConfig):
    """Spanish acquisition module. Extractable by design — see lingua/SPEC.md.

    The app label is ``lingua`` so every table is prefixed ``lingua_*`` (the
    documented extraction path: ``pg_dump --table='lingua_*'``). No model here
    ever ForeignKeys to a host model; the learner is carried as a plain
    ``host_student_id`` integer (D-03).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "lingua"
    verbose_name = "Lingua (Spanish)"

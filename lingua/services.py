"""lingua orchestration + wiring.

Business logic lives here: views -> services -> ORM. No repository layer and no
custom managers (D-05) — the Django QuerySet is the repository. This module also
holds the composition helper that resolves the host-provided AIClient adapter
from settings, so lingua never imports the adapter (or tutor) directly.
"""
from django.conf import settings
from django.utils.module_loading import import_string

from .models import Learner
from .ports import AIClient


def delete_learner_for_student(host_student_id):
    """Purge the lingua Learner (+ cascaded lingua rows) for a host Student that
    was deleted. Idempotent — safe to call when no Learner exists.

    D-03 means no FK/cascade links a Student to lingua, so the host must call this
    explicitly from its delete path; ``lingua_prune_orphans`` is the scheduled
    backstop for any inline call that didn't run. Returns the rows-deleted count.
    """
    deleted, _ = Learner.objects.filter(host_student_id=host_student_id).delete()
    return deleted


def get_ai_client() -> AIClient:
    """Instantiate the host-bound AIClient adapter named in LINGUA["AI_CLIENT"].

    The dotted path is the ONLY reference to the host adapter from the lingua
    side; swapping that setting swaps the provider with zero lingua changes.
    Services take ``ai_client=None`` and fall back to this, so tests inject a
    fake implementing ``ports.AIClient``.
    """
    dotted = settings.LINGUA["AI_CLIENT"]
    return import_string(dotted)()

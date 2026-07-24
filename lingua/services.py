"""lingua orchestration + wiring.

Business logic lives here: views -> services -> ORM. No repository layer and no
custom managers (D-05) — the Django QuerySet is the repository. This module also
holds the composition helper that resolves the host-provided AIClient adapter
from settings, so lingua never imports the adapter (or tutor) directly.
"""
from django.conf import settings
from django.utils.module_loading import import_string

from .ports import AIClient


def get_ai_client() -> AIClient:
    """Instantiate the host-bound AIClient adapter named in LINGUA["AI_CLIENT"].

    The dotted path is the ONLY reference to the host adapter from the lingua
    side; swapping that setting swaps the provider with zero lingua changes.
    Services take ``ai_client=None`` and fall back to this, so tests inject a
    fake implementing ``ports.AIClient``.
    """
    dotted = settings.LINGUA["AI_CLIENT"]
    return import_string(dotted)()

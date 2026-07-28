"""Ports that lingua OWNS — pure interfaces + DTOs. NO Django, NO host imports.

The host supplies concrete adapters (e.g. homeschool_hub/adapters/lingua_ai.py)
and binds them via settings (LINGUA["AI_CLIENT"]). lingua depends only on these
interfaces, never on the host's implementation — that is what keeps the module
extractable (D-04). Keep this file import-clean: enforced by a test.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class AIResult:
    """Result of a text generation call."""

    text: str
    usage: dict = field(default_factory=dict)  # {input_tokens, output_tokens} — feeds the cost ceiling
    model: str = ""


class AIClient(ABC):
    """Text-generation seam. A host adapter wraps its own provider (Anthropic via
    the host's tutor.ai) behind this; lingua services depend only on the ABC and
    are tested against an injected fake."""

    @abstractmethod
    def is_configured(self) -> bool:
        """True if the underlying provider is usable (e.g. an API key is set)."""

    @abstractmethod
    def generate(self, *, system, user, max_tokens=1024, timeout=None, meta=None):
        """Generate text from a system + user prompt. Returns an AIResult."""


class WorkLogSink(ABC):
    """Seam for mirroring lingua activity into the HOST's work log (LGA-76).

    A physical Spanish book a child finishes is real schoolwork, so it belongs in the
    host's work log and therefore in the charter report. lingua must not import the
    host (D-04), so it calls this port and the host adapter creates its own record.
    Every method is best-effort: the host may return None and lingua must keep working
    if the sink is unbound or fails."""

    @abstractmethod
    def record_book(self, *, host_student_id, title, author="", read_on=None, note=""):
        """Record a finished book as host work-log activity. Returns the host record's
        id (an opaque int lingua stores WITHOUT a FK, D-03), or None."""

    @abstractmethod
    def remove(self, host_record_id):
        """Remove a previously recorded host work-log entry (id from record_book)."""


class ImageClient(ABC):
    """Image-generation seam (LGA-71). A host adapter wraps its own provider
    (Replicate/nano-banana via the host's tutor.imagegen) behind this; lingua
    services depend only on the ABC and are tested against an injected fake. Keeping
    it a port is what lets lingua own the illustration pipeline without importing the
    host (D-04)."""

    @abstractmethod
    def is_configured(self) -> bool:
        """True if the underlying image provider is usable (e.g. an API token is set)."""

    @abstractmethod
    def generate(self, prompt, *, reference_paths=None, extra_input=None):
        """Generate one image from ``prompt`` (+ optional reference image paths for
        character consistency). Returns raw image bytes."""

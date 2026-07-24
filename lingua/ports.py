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

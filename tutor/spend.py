"""Monthly AI spend ceiling for the tutor path (HH-145).

Lingua has had a cost ceiling since LGA-29; tutor had none, and tutor is the
higher-volume side — it fires on ordinary use (a child submitting work, a parent
pressing "AI Grade", a writing box asking for spellcheck) rather than on an
operator authoring content. A retry storm, a stuck background daemon, or simply a
heavy week had no backstop, and the first signal would have been the bill.

Two rules make this ledger trustworthy, and both are about WHERE it is called
from rather than what it computes:

1. Spend is recorded at the **provider seam** — the instant the API responds,
   before the reply is parsed. A response that fails to parse still cost money,
   and a ledger that only counted successes would under-count exactly the runaway
   case it exists to catch.
2. The ceiling is checked **before** the call, not after, so crossing it costs at
   most one more call rather than an unbounded number.

Deliberately separate from lingua's ``AiUsage``: lingua must stay extractable
(D-03/D-04), so its ledger travels with it. The two ceilings are not additive.
"""

import logging

from django.conf import settings
from django.db.models import F
from django.utils import timezone

from .models import AiSpend

logger = logging.getLogger(__name__)


class BudgetExceeded(Exception):
    """The monthly tutor AI ceiling is reached; new calls are refused until next month."""


def _period():
    return timezone.now().strftime("%Y-%m")


def prices_for(model):
    """(input, output) USD per million tokens for ``model``.

    An unknown model falls back to the most expensive tier: over-estimating stops
    spending early, which is recoverable; under-estimating sails past the ceiling,
    which is what this module exists to prevent.
    """
    table = getattr(settings, "TUTOR_AI_PRICES", {}) or {}
    fallback = getattr(settings, "TUTOR_AI_PRICE_FALLBACK", (15.0, 75.0))
    if model not in table:
        logger.warning("No price for tutor AI model %r; using the fallback tier.", model)
    return table.get(model, fallback)


def micro_usd_for(model, input_tokens, output_tokens):
    """Estimated cost of one call, in millionths of a USD (integer)."""
    price_in, price_out = prices_for(model)
    dollars = (input_tokens / 1_000_000) * price_in + (output_tokens / 1_000_000) * price_out
    return int(round(dollars * 1_000_000))


def record_usage(model, usage):
    """Accumulate one call's tokens and cost into the current month.

    Atomic F() increments, so two concurrent grades cannot lose a call. Tolerates a
    missing or partial ``usage`` object — an unbilled call is still a call, and the
    count is what reveals a runaway loop even when the token numbers are absent.
    """
    it = int(getattr(usage, "input_tokens", 0) or 0)
    ot = int(getattr(usage, "output_tokens", 0) or 0)
    period = _period()
    AiSpend.objects.get_or_create(period=period)
    AiSpend.objects.filter(period=period).update(
        input_tokens=F("input_tokens") + it,
        output_tokens=F("output_tokens") + ot,
        calls=F("calls") + 1,
        micro_usd=F("micro_usd") + micro_usd_for(model, it, ot),
        updated_at=timezone.now(),
    )


def month_to_date_usd():
    """Estimated tutor AI spend for the current calendar month (0.0 if none)."""
    row = AiSpend.objects.filter(period=_period()).first()
    return (row.micro_usd / 1_000_000) if row else 0.0


def ceiling_usd():
    return float(getattr(settings, "TUTOR_MONTHLY_COST_CEILING_USD", 25.0))


def budget_exceeded():
    """True once month-to-date spend reaches the ceiling — the hard-stop gate."""
    return month_to_date_usd() >= ceiling_usd()


def refusal_message():
    """Operator-facing explanation, for a UI that has to say why nothing happened."""
    return (
        f"AI features are paused: this month's estimated spend "
        f"(${month_to_date_usd():.2f}) has reached the "
        f"${ceiling_usd():.2f} limit. It resets on the 1st of next month, or raise "
        f"TUTOR_MONTHLY_COST_CEILING_USD to continue now."
    )

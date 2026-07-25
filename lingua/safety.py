"""Child-PII guard for the outbound AI / TTS boundary (D-52, LGA-31).

D-52 is a hard line: no child PII ever reaches an AI or TTS provider. lingua is
already built so this can't happen by construction — a learner is a bare
``host_student_id`` (D-03), so the core never even holds a child's name, and the
only text sent out is operator theme hints and generated/approved story bodies.

This module is the defence-in-depth backstop: a single guard that every outbound
AI/TTS call routes through, so a future accidental change — a prompt personalised
with an email, a phone number, a run of digits — fails LOUD instead of silently
leaking. The three current choke-points are ``services.generate_story``,
``services.critique_story`` and ``audio.synthesize``; any NEW outbound call must
call :func:`assert_no_pii` before sending text off the box.

Names are deliberately NOT scanned: they can't be detected reliably in free text,
and the core holds none anyway. We match the high-signal, low-false-positive
markers that would actually be PII in a children's-story pipeline: email
addresses, and phone / ID / SSN / date-of-birth digit runs. Story prompts spell
numbers as WORDS (STORY_SYSTEM), so a long digit run in outbound text is already
anomalous — which keeps false positives near zero.
"""
import re


class ChildPIISuspected(Exception):
    """Raised when text bound for an external AI/TTS provider looks like PII (D-52)."""


# Bounded quantifiers (RFC-ish local=64 / domain=255) keep matching LINEAR — an
# unbounded `+…+@…` is O(n^2) on long non-matching text (a PII scanner must not be
# a DoS lever on an AI-generated story body).
EMAIL_RE = re.compile(r"[a-z0-9._%+-]{1,64}@[a-z0-9.-]{1,255}\.[a-z]{2,}", re.I)
# 7+ digits in a row, allowing a single space / dot / comma / slash / hyphen between
# them, so it catches phone numbers, SSNs, long ids, and slash- or dash-formatted
# dates of birth ("01/15/2015") without firing on a lone year ("2020").
DIGIT_RUN_RE = re.compile(r"(?:\d[ .,/-]?){7,}")


def find_pii(text):
    """Return a short label for the first PII marker in ``text``, else "".

    The label is coarse on purpose (``"email"`` / ``"digit-run"``) so callers can
    report WHAT tripped the guard without ever echoing the offending value.
    """
    t = text or ""
    if "@" in t and EMAIL_RE.search(t):   # cheap pre-check: skip the scan on the common no-@ case
        return "email"
    if DIGIT_RUN_RE.search(t):
        return "digit-run"
    return ""


def fence(text, tag):
    """Wrap untrusted ``text`` as an inert DATA field for a prompt (LGA-30, D-53).

    The generation pipeline interpolates untrusted values into prompts — the
    operator's theme hint (``generate_story``) and a story body (``critique_story``,
    the load-bearing safeguard). Bare interpolation lets that text smuggle
    instructions ("ignore the rules", "mark this passed"). Fencing wraps the value
    in ``<tag>…</tag>`` and NEUTRALISES any fence tag inside it, so the content can
    never close the fence early and escape into the instruction stream. The system
    prompts tell the model to treat fenced content strictly as data, never commands.

    (lingua's only child input is a constrained felt-rating, never free text and
    never sent to AI — D-53 — so there is no child free text to fence here.)
    """
    t = (text or "").replace(f"</{tag}>", "").replace(f"<{tag}>", "")
    return f"<{tag}>\n{t}\n</{tag}>"


def assert_no_pii(*texts, where=""):
    """Raise :class:`ChildPIISuspected` if any of ``texts`` carries a PII marker.

    Call this immediately BEFORE any outbound AI or TTS request (D-52). ``where``
    names the call site for the message; the suspected value itself is never
    included, so nothing sensitive lands in logs or exception text.
    """
    for t in texts:
        kind = find_pii(t)
        if kind:
            site = f" ({where})" if where else ""
            raise ChildPIISuspected(
                f"Refusing to send text to an external provider: {kind} detected{site} "
                "— D-52 forbids child PII in AI/TTS calls."
            )

"""Polly TTS + read-along word timings (LGA-34/35, D-16..D-21).

AUTHORING-TIME ONLY. This runs inside the ``tts_build`` management command on a dev
machine — never on the web dyno (N-05). The reader serves PRE-BAKED audio + timing
JSON, so nothing here is in the request path: graceful degradation (LGA-54) lives in
the reader, and this module is free to raise on failure (the command is batch-resilient,
mirroring ``generate_stories``).

The load-bearing correctness piece (SPIKE-01 / D-21): Polly speech-mark ``start``/``end``
are UTF-8 **byte** offsets into the submitted text, and Spanish accents (á é í ó ú ñ ¿ ¡)
are 2-byte in UTF-8 — so a naive ``text[start:end]`` drifts after the first accent. We
build a byte→char map and emit **character** offsets (what a JS string indexes by). Plain
text is submitted (``TextType="text"``), so the offsets map 1:1 to the SOURCE with no SSML
escape/normalization boundary to distrust (D-19). Polly still normalizes numerals/abbrev
internally, but its marks' offsets remain offsets into the *submitted* text, so byte→char
on the original text stays correct regardless; ``tts_build`` handles the spelled-out
authoring discipline for clean 1:1 alignment.

Only story text + a voice id are ever sent to Polly — never child PII (D-52).
"""
import json
import re

from django.conf import settings

WORD_RE = re.compile(r"\S+", re.UNICODE)


class TTSError(Exception):
    """Synthesis failed (mirrors tutor's GraderError; the command catches it)."""


# ---------------------------------------------------------------------------
# byte<->char mapping + tokenization (SPIKE-01 validated; the correctness core)
# ---------------------------------------------------------------------------
def byte_to_char_map(text):
    """Map every UTF-8 byte offset in ``text`` to its Python str (code-point) index,
    including the terminal offset (== len(text)). Unmapped byte offsets (i.e. a byte
    that lands mid-character) are absent by design — a valid word boundary never does."""
    m = {}
    b = 0
    for ci, ch in enumerate(text):
        m[b] = ci
        b += len(ch.encode("utf-8"))
    m[b] = len(text)
    return m


def display_tokens(text):
    """Whitespace-delimited display tokens as (char_start, char_end, text). The reader
    wraps each in a ``<span data-i>`` and highlights by token index."""
    return [(m.start(), m.end(), m.group()) for m in WORD_RE.finditer(text)]


def _token_index_for_char(tokens, cs):
    """Index of the display token whose char range contains ``cs`` (or None)."""
    for i, (a, b, _t) in enumerate(tokens):
        if a <= cs < b:
            return i
    return None


# ---------------------------------------------------------------------------
# Polly synthesis boundary (the only AWS-touching code; client is injectable)
# ---------------------------------------------------------------------------
def _polly_client():
    """Build a boto3 Polly client from ambient AWS config (authoring machine),
    with an optional region override. boto3 is imported lazily so importing this
    module — and tests that inject a fake client — never require boto3/AWS."""
    import boto3

    region = settings.LINGUA.get("TTS_REGION")
    return boto3.client("polly", region_name=region) if region else boto3.client("polly")


def synthesize(text, *, voice=None, engine=None, client=None):
    """Render ``text`` once as audio and once as word speech marks (D-17/D-18).

    Two Polly calls on the SAME input: ``OutputFormat="mp3"`` for audio, and
    ``OutputFormat="json"`` + ``SpeechMarkTypes=["word"]`` for marks (JSON-Lines —
    parsed line-by-line, NOT as a JSON array). Returns
    ``{"audio": bytes, "marks": [word-event dict], "voice", "engine"}``.
    Voice/engine default to the LINGUA settings (es-MX). Raises TTSError on any
    Polly/parse failure. ``client`` is injectable for tests (ports-style seam)."""
    if not (text or "").strip():
        raise TTSError("Refusing to synthesize empty text.")
    voice = voice or settings.LINGUA.get("TTS_VOICE", "Mia")
    engine = engine or settings.LINGUA.get("TTS_ENGINE", "neural")
    ai = client or _polly_client()
    try:
        audio_resp = ai.synthesize_speech(
            Text=text, VoiceId=voice, Engine=engine,
            OutputFormat="mp3", TextType="text",
        )
        audio = audio_resp["AudioStream"].read()
        marks_resp = ai.synthesize_speech(
            Text=text, VoiceId=voice, Engine=engine,
            OutputFormat="json", SpeechMarkTypes=["word"], TextType="text",
        )
        raw = marks_resp["AudioStream"].read().decode("utf-8")
        # Parse INSIDE the guard: a truncated/malformed marks line must surface as
        # TTSError (the batch command skips one story on TTSError) rather than a raw
        # JSONDecodeError that aborts the whole tts_build run. isinstance guards a
        # non-dict line from crashing the .get() filter.
        marks = [json.loads(line) for line in raw.splitlines() if line.strip()]
        word_marks = [m for m in marks if isinstance(m, dict) and m.get("type") == "word"]
        if not audio:
            raise TTSError("Polly returned no audio.")
    except TTSError:
        raise
    except Exception as exc:  # noqa: BLE001 — normalize any boto/IO/parse error
        raise TTSError(f"Polly synthesis failed: {type(exc).__name__}") from exc
    return {"audio": audio, "marks": word_marks, "voice": voice, "engine": engine}


# ---------------------------------------------------------------------------
# timing transform: Polly byte-offset marks -> flat char-offset JSON (D-21)
# ---------------------------------------------------------------------------
def build_timings(text, marks, *, tail_ms=400):
    """Turn Polly word marks (byte offsets) into a flat, binary-searchable read-along
    timing structure with CHARACTER offsets (D-21). Returns::

        {"tokens": [str],                 # display tokens, for rendering spans
         "token_spans": [[cs, ce]],       # each token's char range
         "words": [{"i", "s_ms", "e_ms", "cs", "ce"}]}  # time-ordered word events

    ``i`` is the containing display-token index (what the highlighter toggles); ``cs``/
    ``ce`` are the word's own char offsets via the byte→char map; ``s_ms`` is the mark
    time and ``e_ms`` is the next word's start (the last word gets ``+tail_ms``). No byte
    offsets are ever exposed. ``words`` is monotonic in ``s_ms`` (Polly emits in order),
    so the player can binary-search it. Word marks whose byte offsets don't map to a
    clean char boundary are skipped rather than corrupting the array."""
    b2c = byte_to_char_map(text)
    tokens = display_tokens(text)
    words = []
    for e in marks:
        if e.get("type") != "word":
            continue
        cs, ce = b2c.get(e.get("start")), b2c.get(e.get("end"))
        if cs is None or ce is None:
            continue  # offset didn't land on a char boundary — drop, don't corrupt
        ti = _token_index_for_char(tokens, cs)
        if ti is None:
            continue
        words.append({"i": ti, "s_ms": int(e["time"]), "cs": cs, "ce": ce})
    for i, w in enumerate(words):
        w["e_ms"] = words[i + 1]["s_ms"] if i + 1 < len(words) else w["s_ms"] + tail_ms
    return {
        "tokens": [t[2] for t in tokens],
        "token_spans": [[t[0], t[1]] for t in tokens],
        "words": words,
    }


def synthesize_story(text, *, voice=None, engine=None, client=None, tail_ms=400):
    """One authoring call: synthesize audio + marks, then build read-along timings.
    Returns ``{"audio": bytes, "timings": {...}, "voice", "engine"}``."""
    out = synthesize(text, voice=voice, engine=engine, client=client)
    return {
        "audio": out["audio"],
        "timings": build_timings(text, out["marks"], tail_ms=tail_ms),
        "voice": out["voice"],
        "engine": out["engine"],
    }

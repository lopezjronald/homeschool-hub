"""Baked English speech for the spelling activities.

AUTHORING-TIME ONLY, like lingua's TTS: this runs inside the ``spelling_audio``
management command, never on the web dyno. The activities serve pre-baked mp3
URLs, so nothing here is in the request path.

Why baked audio at all: the browser's own ``speechSynthesis`` voice is whatever
the device happens to ship, which on Windows is a flat robotic reader. A child
being asked to spell a word from hearing it needs the word pronounced clearly
and the SAME way every time — a wobbly voice makes the exercise harder in a way
that has nothing to do with spelling.

Deliberately separate from ``lingua.audio``: that module applies Spanish IPA
overrides and a Spanish default voice. Sharing it would mean a Spanish
pronunciation rule silently reshaping an English word.
"""

import hashlib

from django.conf import settings

# US English, neural. Clear and warm at dictation speed, and available in every
# region we'd run in. Swap with --voice; Danielle/Ruth/Stephen also read well.
DEFAULT_VOICE = "Joanna"
DEFAULT_ENGINE = "neural"

# A word is said slower than a sentence — she is spelling it, not listening to a
# story, so each phoneme needs room.
WORD_RATE = "85%"
SENTENCE_RATE = "95%"


class SpellingTTSError(Exception):
    """Synthesis failed. The command catches it and keeps going."""


def _polly_client():
    """boto3 Polly from ambient AWS config. Imported lazily so importing this
    module — and tests that inject a fake client — never require boto3."""
    import boto3

    region = getattr(settings, "LINGUA", {}).get("TTS_REGION")
    return boto3.client("polly", region_name=region) if region else boto3.client("polly")


def key_for(text, *, voice, engine, rate, kind):
    """Content-addressed key, so re-baking is free and a changed voice re-bakes.

    Everything that can change the audio goes into the hash — swap the voice and
    you get a new object rather than a stale one under the old name.
    """
    digest = hashlib.sha256(
        "\x1f".join([text, voice, engine, rate, kind]).encode("utf-8")
    ).hexdigest()[:24]
    return f"spelling/{kind}/{digest}.mp3"


def _ssml(text, rate):
    """Wrap in SSML for the slower rate.

    Escaped by hand rather than with xml.sax escape(): the text here is a
    spelling word or a short sentence we authored, but it still reaches an XML
    parser, so an apostrophe in "Dad's" must not end the element.
    """
    safe = (
        text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )
    return f'<speak><prosody rate="{rate}">{safe}</prosody></speak>'


def synthesize(text, *, kind="word", voice=None, engine=None, client=None):
    """mp3 bytes for one word or sentence. Returns (audio, key)."""
    text = (text or "").strip()
    if not text:
        raise SpellingTTSError("Refusing to synthesize empty text.")
    voice = voice or DEFAULT_VOICE
    engine = engine or DEFAULT_ENGINE
    rate = WORD_RATE if kind == "word" else SENTENCE_RATE
    api = client or _polly_client()
    try:
        resp = api.synthesize_speech(
            Text=_ssml(text, rate),
            TextType="ssml",
            VoiceId=voice,
            Engine=engine,
            OutputFormat="mp3",
        )
        audio = resp["AudioStream"].read()
    except Exception as exc:  # noqa: BLE001 — normalize any boto/IO error
        raise SpellingTTSError(f"Polly synthesis failed: {type(exc).__name__}") from exc
    if not audio:
        raise SpellingTTSError("Polly returned no audio.")
    return audio, key_for(text, voice=voice, engine=engine, rate=rate, kind=kind)

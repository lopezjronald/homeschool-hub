"""Content-addressed keys for read-along assets (LGA-37, D-16 / N-04).

A baked audio/timing asset is keyed by a hash of everything that determines its
bytes: the EXACT story text plus provider/voice/engine. Editing the story text (or
switching voice/engine) changes the hash → a new R2 key → no stale audio/timings is
ever served; the old key is simply orphaned (GC-able).

The hash is over the exact text, NOT a whitespace- or unicode-normalized form —
deliberately. Whitespace and NFC/NFD changes shift CHARACTER offsets, and the
read-along timings are character-offset based (D-21), so any such change makes the
old timings mis-align. Therefore every change that alters offsets MUST bust the
cache, which means it must be part of the hash. Identity is the only safe transform.
"""
import hashlib

ASSET_PREFIX = "lingua/readalong"
IMAGE_PREFIX = "lingua/illustrations"
CLIP_PREFIX = "lingua/clips"


def content_hash(text, *, provider, voice, engine):
    """sha256 hex over (provider, voice, engine, exact text). No salt, so identical
    content authored on any machine yields the same key (stable + dedup-friendly).
    A NUL separator makes the field boundaries unambiguous (so "ab"+"c" can't collide
    with "a"+"bc")."""
    h = hashlib.sha256()
    for part in (provider, voice, engine, text):
        h.update((part or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def asset_keys(digest):
    """R2 object keys for the audio + timing assets of a content hash."""
    return {
        "audio": f"{ASSET_PREFIX}/{digest}.mp3",
        "timings": f"{ASSET_PREFIX}/{digest}.json",
    }


def image_content_hash(*, model, style, character_block, setting, tone, aspect, scene):
    """sha256 hex over everything that determines an illustration's bytes: the image
    model, the fixed house style, the per-story character block / setting / tone (all
    fed into the prompt), the aspect ratio, and the exact beat scene text (LGA-71).
    Editing any of these — the style string, the story text, ANY field of the art
    contract — busts the cache so a stale image is never served; the old R2 object is
    simply orphaned. NUL separators keep field boundaries unambiguous (mirrors
    :func:`content_hash`)."""
    h = hashlib.sha256()
    for part in (model, style, character_block, setting, tone, aspect, scene):
        h.update((part or "").encode("utf-8"))
        h.update(b"\x00")
    return h.hexdigest()


def image_key(digest, ext="webp"):
    """R2 object key for an illustration of a given content hash."""
    return f"{IMAGE_PREFIX}/{digest}.{ext}"


def clip_key(digest):
    """R2 object key for a single-utterance AudioClip mp3 (LGA-84/86)."""
    return f"{CLIP_PREFIX}/{digest}.mp3"

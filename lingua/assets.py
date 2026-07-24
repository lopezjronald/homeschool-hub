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

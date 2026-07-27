"""Public, immutably-cached storage for read-along assets (LGA-36, D-16 / N-03).

Read-along audio must be PUBLIC and long-cacheable — the default media backend uses
private ~1h signed URLs, wrong for reread/offline. This module targets a dedicated
``lingua_readalong`` storage alias (a public R2 path in prod, local filesystem in
dev) and writes content-addressed keys (assets.asset_keys), so the same content maps
to the same stable URL forever — safe to cache immutably.
"""
import json

from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import InvalidStorageError, default_storage, storages

READALONG_ALIAS = "lingua_readalong"
# Child read-aloud recordings (LGA-73) live in the PRIVATE default media store
# (signed, expiring URLs) — deliberately NOT the public read-along path.
RECORDING_PREFIX = "lingua/recordings"
# Single source of truth: settings imports this for the R2 object_parameters, so the
# on-upload Cache-Control header can never drift from what this module documents.
IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"


def _public_capable(storage):
    """A backend that serves UNSIGNED URLs (querystring_auth off) must have a
    custom_domain — otherwise .url() emits a bare S3-endpoint URL that 403s in the
    browser. Non-S3 backends (filesystem / in-memory: no querystring_auth attr) are
    always fine. Returns True when the backend can actually serve public URLs."""
    unsigned = getattr(storage, "querystring_auth", True) is False
    return not (unsigned and not getattr(storage, "custom_domain", None))


def readalong_storage():
    """The storage backend for public read-along assets. Falls back to the default
    storage if the dedicated alias isn't wired (keeps lingua extractable, D-04).

    Raises ImproperlyConfigured if the backend would hand out non-public (403-ing)
    URLs — i.e. unsigned but with no custom_domain (R2_PUBLIC_DOMAIN unset). This
    fails LOUDLY at authoring time (tts_build), never on the web dyno: the reader
    serves pre-baked URLs and never calls this, so a misconfig can't take prod down —
    it only stops a bake from silently producing dead links."""
    try:
        storage = storages[READALONG_ALIAS]
    except InvalidStorageError:
        storage = storages["default"]
    if not _public_capable(storage):
        raise ImproperlyConfigured(
            "lingua_readalong serves unsigned URLs but has no custom_domain — set "
            "R2_PUBLIC_DOMAIN (a public R2 host) so read-along URLs are actually "
            "public (LGA-36)."
        )
    return storage


def save_bytes(key, data, *, replace=False):
    """Save raw bytes at content-addressed ``key`` and return the stable public URL.

    Idempotent dedup: normally the key is a content hash, so if it already exists the
    bytes are by definition identical — skip the redundant upload. The immutable cache
    header is applied by the backend's object_parameters (settings).

    ``replace=True`` overwrites an existing object (delete-then-save). This is needed
    for the IMAGE path: image generation is non-deterministic (nano-banana has no
    seed), so the content hash covers the PROMPT inputs, not the bytes — a ``--force``
    re-bake produces different bytes under the SAME key and must actually replace the
    stored object, not silently keep the old image. Audio (Polly) is deterministic, so
    it never needs replace."""
    storage = readalong_storage()
    if replace and storage.exists(key):
        storage.delete(key)
    if not storage.exists(key):
        storage.save(key, ContentFile(data))
    return storage.url(key)


def save_audio(key, data):
    """Save mp3 bytes at content-addressed ``key`` and return the stable public URL."""
    return save_bytes(key, data)


def save_image(key, data, *, replace=False):
    """Save illustration bytes at content-addressed ``key`` and return its public URL.
    Pass ``replace=True`` on a force re-bake so new bytes actually overwrite the old
    image (the hash is over the prompt, not the non-deterministic output bytes)."""
    return save_bytes(key, data, replace=replace)


def public_url(key):
    """Stable public URL for an already-saved read-along asset."""
    return readalong_storage().url(key)


def save_timings(key, timings):
    """Save the flat timing JSON at content-addressed ``key`` and return its URL.
    Uploaded alongside the mp3 so a prod ``tts_build --link-only`` run can rebuild
    the StoryAudio row (with inline timings) WITHOUT calling Polly. Idempotent."""
    storage = readalong_storage()
    if not storage.exists(key):
        payload = json.dumps(timings, ensure_ascii=False).encode("utf-8")
        storage.save(key, ContentFile(payload))
    return storage.url(key)


def read_timings(key):
    """Read back timing JSON previously saved at ``key`` (for --link-only). Raises
    if the object is missing (the local authoring run must have uploaded it first)."""
    storage = readalong_storage()
    with storage.open(key) as fh:
        return json.loads(fh.read().decode("utf-8"))


# --- Private child recordings (LGA-73) --------------------------------------
# The DEFAULT store is the app's private media backend (signed, ~1h URLs on R2 in
# prod). Recordings of a child's voice MUST stay there, never the public read-along
# path — so a recording URL is only usable by the logged-in parent for a short window.

def save_recording(key, data):
    """Save a private recording to the default (private) media store. Returns the
    ACTUAL stored key (the backend may de-duplicate a name collision)."""
    return default_storage.save(key, ContentFile(data))


def recording_url(key):
    """The (signed, expiring) URL for a stored private recording."""
    return default_storage.url(key)


def delete_recording(key):
    """Delete a stored private recording (parent action). Idempotent."""
    if key and default_storage.exists(key):
        default_storage.delete(key)

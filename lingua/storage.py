"""Public, immutably-cached storage for read-along assets (LGA-36, D-16 / N-03).

Read-along audio must be PUBLIC and long-cacheable — the default media backend uses
private ~1h signed URLs, wrong for reread/offline. This module targets a dedicated
``lingua_readalong`` storage alias (a public R2 path in prod, local filesystem in
dev) and writes content-addressed keys (assets.asset_keys), so the same content maps
to the same stable URL forever — safe to cache immutably.
"""
from django.core.exceptions import ImproperlyConfigured
from django.core.files.base import ContentFile
from django.core.files.storage import InvalidStorageError, storages

READALONG_ALIAS = "lingua_readalong"
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


def save_audio(key, data):
    """Save mp3 bytes at content-addressed ``key`` and return the stable public URL.

    Idempotent: the key is a content hash, so if it already exists the bytes are by
    definition identical — skip the redundant upload and just return the URL. The
    immutable cache header is applied by the backend's object_parameters (settings)."""
    storage = readalong_storage()
    if not storage.exists(key):
        storage.save(key, ContentFile(data))
    return storage.url(key)


def public_url(key):
    """Stable public URL for an already-saved read-along asset."""
    return readalong_storage().url(key)

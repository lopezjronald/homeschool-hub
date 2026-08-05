"""Pure listening helpers — no Django, no models (LGA-102).

Kept out of ``services.py`` because the 0033 migration needs the same
classification and a migration must not import app code that can change under it.
The migration carries its own copy; ``test_kind_classifier_matches_the_migration``
holds the two together.
"""

VIDEO = "video"
SHELF = "shelf"

# The URL shapes that identify ONE video. Everything else — /channel/, /playlist,
# /@handle, /c/, a bare domain — is an endless well and is a SHELF.
_VIDEO_MARKERS = ("/watch", "youtu.be/", "/shorts/", "/live/", "/embed/")


def classify_url(url):
    """VIDEO if this URL points at a single video, else SHELF.

    Conservative on purpose: an unrecognised URL is a SHELF, so the worst case is
    an item that never rotates out rather than one that vanishes after one view.
    A playlist URL that also carries ``watch?v=`` (YouTube's "play this video
    within this list" form) is a VIDEO — the link opens on that one video.
    """
    text = (url or "").lower()
    return VIDEO if any(marker in text for marker in _VIDEO_MARKERS) else SHELF

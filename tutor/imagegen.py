"""Server-side image generation for manga panels (Replicate).

Mirrors ``tutor.ai`` (the grader): the token lives only in
``settings.REPLICATE_API_TOKEN`` (an env var), the model is a setting, the
client is injectable for tests, and everything degrades gracefully when no
token is set.

``MANGA_IMAGE_MODEL`` is any Replicate slug. ``google/nano-banana-2`` keeps a
cast of characters consistent across panels when their character sheets are
passed as reference images under ``MANGA_REFERENCE_KEY``.
"""

import urllib.request

from django.conf import settings


class ImageGenNotConfigured(Exception):
    """Raised when no Replicate API token is configured."""


class ImageGenError(Exception):
    """Raised when the generation call or download fails."""


def is_configured():
    """True if a Replicate API token is available."""
    return bool(getattr(settings, "REPLICATE_API_TOKEN", ""))


def _output_to_bytes(output):
    """Normalize a Replicate run() result to raw image bytes.

    Handles the shapes the SDK returns: a FileOutput, a list of them, or a
    plain URL string.
    """
    if isinstance(output, (list, tuple)):
        if not output:
            raise ImageGenError("The model returned no image.")
        output = output[0]
    # Newer SDK returns a FileOutput with .read(); older returns a URL string.
    if hasattr(output, "read"):
        return output.read()
    url = getattr(output, "url", output)
    if not isinstance(url, str):
        raise ImageGenError(f"Unexpected model output type: {type(output)!r}")
    try:
        with urllib.request.urlopen(url) as resp:  # noqa: S310 — trusted Replicate CDN
            return resp.read()
    except Exception as exc:  # noqa: BLE001
        raise ImageGenError(f"Could not download the generated image: {exc}")


def generate_image(prompt, reference_paths=None, extra_input=None, client=None):
    """Generate one image from a prompt (+ optional reference images).

    ``reference_paths`` is a list of local file paths (e.g. character sheets)
    passed to the model for character consistency. ``extra_input`` is merged
    into the model input (e.g. aspect_ratio, output_format). Returns raw image
    bytes. ``client`` is injectable so tests can supply a fake Replicate client.
    """
    if not is_configured():
        raise ImageGenNotConfigured("Replicate API token is not configured.")

    if client is None:
        import replicate

        client = replicate.Client(api_token=settings.REPLICATE_API_TOKEN)

    inputs = {"prompt": prompt}
    if extra_input:
        inputs.update(extra_input)
    handles = []
    if reference_paths:
        key = getattr(settings, "MANGA_REFERENCE_KEY", "image_input")
        handles = [open(path, "rb") for path in reference_paths]
        inputs[key] = handles

    model = getattr(settings, "MANGA_IMAGE_MODEL", "google/nano-banana-2")
    try:
        output = client.run(model, input=inputs)
    except Exception as exc:  # noqa: BLE001 — surface any API/transport error uniformly
        raise ImageGenError(str(exc))
    finally:
        for handle in handles:
            handle.close()

    return _output_to_bytes(output)

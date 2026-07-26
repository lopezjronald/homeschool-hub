"""Host adapter: binds lingua.ports.ImageClient to the host's Replicate seam.

Like lingua_ai.py, this is the ONLY place lingua's image pipeline touches the host
(D-04). It wraps ``tutor.imagegen`` (Replicate / nano-banana, with reference-image
support for character consistency) and exposes a generic ``generate()`` returning raw
bytes. To extract lingua, reimplement just this file against the new host and point
LINGUA["IMAGE_CLIENT"] at it.
"""
from lingua.ports import ImageClient
from tutor import imagegen


class TutorImageClient(ImageClient):
    def is_configured(self) -> bool:
        return imagegen.is_configured()

    def generate(self, prompt, *, reference_paths=None, extra_input=None):
        # tutor.imagegen raises ImageGenNotConfigured / ImageGenError; let them
        # propagate so the batch command can catch per-story (like tts_build).
        return imagegen.generate_image(
            prompt, reference_paths=reference_paths, extra_input=extra_input,
        )

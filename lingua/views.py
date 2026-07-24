"""lingua views. Parent-facing pages extend the host base.html (so NOT @lingua_csp
— that strict policy is reserved for the CSP-clean kid reader). Editors-only views
raise Http404 for non-editors, matching the rest of the app (tutor/views.py)."""
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.csp import CSP
from django.views.decorators.http import require_http_methods

from core.permissions import user_can_edit

from . import storage
from .csp import LINGUA_CSP, lingua_csp
from .models import Story


@login_required
@require_http_methods(["GET", "POST"])
def batch_approval(request):
    """Parent reviews pending AI-generated story drafts and approves/rejects them
    in bulk (D-50), with the critic flags + leveling signal surfaced so the parent
    approves pedagogical fit + safety at a glance. Editors only."""
    if not user_can_edit(request.user):
        raise Http404

    if request.method == "POST":
        action = request.POST.get("action")
        if action not in ("approve", "reject"):
            messages.info(request, "No action taken.")
            return redirect("lingua:approvals")
        # Sanitize ids: digits only, within bigint range — a hand-crafted POST
        # with junk/oversized values must not 500 the query.
        max_pk = 9223372036854775807
        ids = [int(x) for x in request.POST.getlist("story_ids")
               if x.isdigit() and int(x) <= max_pk]
        pending = Story.objects.filter(pk__in=ids, status=Story.PENDING)
        count = 0
        for story in pending:
            (story.approve if action == "approve" else story.reject)(request.user.id)
            count += 1
        if count:
            verb = "approved" if action == "approve" else "rejected"
            noun = "story" if count == 1 else "stories"
            messages.success(request, f"{count} {noun} {verb}.")
        else:
            messages.info(request, "No stories selected.")
        return redirect("lingua:approvals")

    drafts = Story.objects.filter(status=Story.PENDING).order_by("level", "-created_at")
    return render(request, "lingua/approvals.html", {"drafts": drafts})


@login_required
@lingua_csp
def read_story(request, story_id):
    """Read-along reader (LGA-47) — the CSP-clean kid page. Only APPROVED stories are
    servable (D-49). With baked audio the page carries the ``<audio>`` + inline timing
    JSON and the rAF player highlights each word; with no audio it degrades to plain
    readable text (LGA-54) — the reading loop never hard-depends on audio/AI, so a
    missing/broken asset shows text, never a 500.

    The strict LINGUA_CSP allows media only from SELF; the read-along mp3 lives on the
    public R2 host, so when the audio URL is cross-origin we widen ``media-src`` to
    that host (the @lingua_csp decorator leaves a view-set policy untouched)."""
    story = get_object_or_404(Story, pk=story_id, status=Story.APPROVED)
    voice = settings.LINGUA.get("TTS_VOICE", "Mia")
    engine = settings.LINGUA.get("TTS_ENGINE", "neural")
    audio = story.current_audio(voice, engine)
    audio_url, timings = "", None
    if audio:
        try:
            audio_url = storage.public_url(audio.audio_key)
            timings = audio.timings or None
        except Exception:  # noqa: BLE001 — audio is enhancement; degrade to text (LGA-54)
            audio_url, timings = "", None
    has_audio = bool(audio_url and timings and timings.get("words"))
    # Render tokens that align with the timing word indices when we have audio;
    # otherwise a plain whitespace split, purely for display.
    tokens = timings.get("tokens") if has_audio else story.body.split()
    response = render(request, "lingua/read.html", {
        "story": story, "audio_url": audio_url, "timings": timings if has_audio else None,
        "tokens": tokens, "has_audio": has_audio,
    })
    if has_audio:
        parts = urlsplit(audio_url)
        if parts.scheme and parts.netloc:  # cross-origin (prod R2) — widen media-src
            policy = {k: list(v) for k, v in LINGUA_CSP.items()}
            policy["media-src"] = [CSP.SELF, f"{parts.scheme}://{parts.netloc}"]
            response._csp_config = policy
    return response

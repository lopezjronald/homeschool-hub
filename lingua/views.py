"""lingua views. Parent-facing pages extend the host base.html (so NOT @lingua_csp
— that strict policy is reserved for the CSP-clean kid reader). Editors-only views
raise Http404 for non-editors, matching the rest of the app (tutor/views.py)."""
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.csp import CSP
from django.views.decorators.http import require_http_methods

from core.permissions import user_can_edit

from . import cognates, storage
from .csp import LINGUA_CSP
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


def render_reader(request, story, *, finish_url="", back_url=""):
    """Render the CSP-clean read-along page for a story — shared by the parent-preview
    view (below) and the tokenless kid portal (host). With baked audio the page carries
    the ``<audio>`` + inline timing JSON and the rAF player highlights each word; with
    no audio it degrades to plain text (LGA-54) — never a 500. Cognate/false-friend
    flags (LGA-51) are computed against the exact tokens rendered.

    Sets the strict LINGUA_CSP on the response ITSELF (so a caller needn't apply
    @lingua_csp), widening ``media-src`` to the public-R2 host when the audio URL is
    cross-origin. ``finish_url`` (optional) is a POST target for logging a completed
    read; ``back_url`` is the back/done link.
    """
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
    # Tokens align with the timing word indices when we have audio; else a plain
    # whitespace split. `or []` guards a corrupt timings blob (words but no tokens)
    # from crashing token_flags — degrade to text, never 500 (LGA-54).
    tokens = (timings.get("tokens") or []) if has_audio else story.body.split()
    flags = cognates.token_flags(tokens)
    token_ctx = [{"i": i, "text": tok, "cognate": fl["cognate"], "ff": fl["false_friend"]}
                 for i, (tok, fl) in enumerate(zip(tokens, flags))]
    response = render(request, "lingua/read.html", {
        "story": story, "audio_url": audio_url, "timings": timings if has_audio else None,
        "token_ctx": token_ctx, "has_audio": has_audio,
        "has_flags": any(t["cognate"] or t["ff"] for t in token_ctx),
        "finish_url": finish_url, "back_url": back_url,
    })
    policy = {k: list(v) for k, v in LINGUA_CSP.items()}
    if has_audio:
        parts = urlsplit(audio_url)
        if parts.scheme and parts.netloc:  # cross-origin (prod R2) — widen media-src
            policy["media-src"] = [CSP.SELF, f"{parts.scheme}://{parts.netloc}"]
    response._csp_config = policy
    return response


@login_required
def read_story(request, story_id):
    """Parent-preview reader (login-gated; only APPROVED stories are servable, D-49).
    The kid-facing TOKENLESS reader lives in the host portal and reuses render_reader."""
    story = get_object_or_404(Story, pk=story_id, status=Story.APPROVED)
    return render_reader(request, story, back_url=reverse("lingua:approvals"))

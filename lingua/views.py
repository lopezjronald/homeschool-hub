"""lingua views. Parent-facing pages extend the host base.html (so NOT @lingua_csp
— that strict policy is reserved for the CSP-clean kid reader). Editors-only views
raise Http404 for non-editors, matching the rest of the app (tutor/views.py)."""
import re
from urllib.parse import urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.csp import CSP
from django.views.decorators.http import require_http_methods

from core.permissions import can_edit_family, user_can_edit
from core.utils import get_selected_family

from . import cognates, illustrate, services, storage
from .csp import LINGUA_CSP
from .integrations import directory
from .models import Learner, Story


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
    # Voice picker (LGA-70): offer only voices that have CURRENT (non-stale) baked
    # audio for THIS story, so the picker never lists a dead option. Honor ?voice= when
    # it names a baked voice; otherwise fall back to the first baked voice — the reader
    # still gets audio (graceful degradation, LGA-54). All voices are Polly-neural and
    # keep word-by-word highlighting, so switching voice only swaps the mp3 + timings.
    default_engine = settings.LINGUA.get("TTS_ENGINE", "neural")
    voice_cfgs = settings.LINGUA.get("TTS_VOICES") or [
        {"id": settings.LINGUA.get("TTS_VOICE", "Mia"),
         "label": settings.LINGUA.get("TTS_VOICE", "Mia"), "engine": default_engine},
    ]
    baked_voices, audio_by_id = [], {}
    for v in voice_cfgs:
        a = story.current_audio(v["id"], v.get("engine") or default_engine)
        if a:
            baked_voices.append(v)
            audio_by_id[v["id"]] = a
    requested = request.GET.get("voice")
    current_voice = requested if requested in audio_by_id else (
        baked_voices[0]["id"] if baked_voices else "")
    audio = audio_by_id.get(current_voice)
    audio_url, timings = "", None
    if audio:
        try:
            audio_url = storage.public_url(audio.audio_key)
            timings = audio.timings or None
        except Exception:  # noqa: BLE001 — audio is enhancement; degrade to text (LGA-54)
            audio_url, timings = "", None
    # Require tokens too: a corrupt timings blob (words but no tokens) must degrade to
    # text, not render an empty story under a player (LGA-54).
    has_audio = bool(audio_url and timings and timings.get("words") and timings.get("tokens"))
    if has_audio:
        tokens = timings["tokens"]
        token_para = [0] * len(tokens)  # audio stories render flat (currently short)
    else:
        # Preserve paragraph breaks so a multi-paragraph story isn't a run-on wall:
        # tokenize per blank-line-delimited paragraph, carrying a paragraph index.
        tokens, token_para = [], []
        for pi, para in enumerate(re.split(r"\n\s*\n", (story.body or "").strip())):
            for word in para.split():
                tokens.append(word)
                token_para.append(pi)
    flags = cognates.token_flags(tokens)
    token_ctx = [{"i": i, "text": tok, "p": token_para[i],
                  "cognate": fl["cognate"], "ff": fl["false_friend"]}
                 for i, (tok, fl) in enumerate(zip(tokens, flags))]

    # Illustrated-storybook layout (LGA-71): if this story has baked pictures, group the
    # rendered tokens into beats (1–2 sentences each) and show each beat's image above
    # its text. Token ORDER is preserved, so the read-along word spans (spans[i]) still
    # line up. If nothing is baked yet, render exactly as before (no regression). A
    # token-count mismatch (unexpected tokenizer drift) disables interleaving rather
    # than risk a misaligned split.
    beats_ctx, illustrated, image_hosts = None, False, set()
    beat_list = illustrate.beats(
        story.body, max_beats=settings.LINGUA.get("ILLUSTRATION_MAX_BEATS", 8))
    # One query for all this story's images, then match each beat to its CURRENT
    # (non-stale) image in Python — same semantics as current_image() but without an
    # N-queries-per-render fan-out.
    by_beat = {}
    for si in story.images.all():
        by_beat.setdefault(si.beat_index, []).append(si)
    beat_images = []
    for b in beat_list:
        want = story.image_hash(b)
        si = next((x for x in by_beat.get(b["index"], []) if x.content_hash == want), None)
        url = ""
        if si:
            try:
                url = storage.public_url(si.image_key)
            except Exception:  # noqa: BLE001 — images are enhancement; degrade to text
                url = ""
        beat_images.append((b, si, url))
    if any(url for _, _, url in beat_images):
        counts = [len((story.body or "")[b["start"]:b["end"]].split())
                  for b, _, _ in beat_images]
        if sum(counts) == len(token_ctx):
            beats_ctx, pos = [], 0
            for (b, si, url), n in zip(beat_images, counts):
                group = token_ctx[pos:pos + n]
                pos += n
                beats_ctx.append({
                    "index": b["index"], "image_url": url,
                    "alt": (si.alt_text if si and si.alt_text else b["text"])[:300],
                    "tokens": group,
                })
                if url:
                    parts = urlsplit(url)
                    if parts.scheme and parts.netloc:
                        image_hosts.add(f"{parts.scheme}://{parts.netloc}")
            illustrated = True

    response = render(request, "lingua/read.html", {
        "story": story, "audio_url": audio_url, "timings": timings if has_audio else None,
        "token_ctx": token_ctx, "has_audio": has_audio,
        "has_flags": any(t["cognate"] or t["ff"] for t in token_ctx),
        "finish_url": finish_url, "back_url": back_url,
        # Only offer the picker when there's a real choice (>1 baked voice, LGA-70).
        "voices": baked_voices if has_audio and len(baked_voices) > 1 else [],
        "current_voice": current_voice,
        "beats_ctx": beats_ctx, "illustrated": illustrated,
    })
    policy = {k: list(v) for k, v in LINGUA_CSP.items()}
    if has_audio:
        parts = urlsplit(audio_url)
        if parts.scheme and parts.netloc:  # cross-origin (prod R2) — widen media-src
            policy["media-src"] = [CSP.SELF, f"{parts.scheme}://{parts.netloc}"]
    if image_hosts:  # widen img-src to the public-R2 host(s) serving the illustrations
        policy["img-src"] = [CSP.SELF, "data:", *sorted(image_hosts)]
    response._csp_config = policy
    return response


@login_required
def read_story(request, story_id):
    """Parent-preview reader (login-gated; only APPROVED stories are servable, D-49).
    The kid-facing TOKENLESS reader lives in the host portal and reuses render_reader."""
    story = get_object_or_404(Story, pk=story_id, status=Story.APPROVED)
    return render_reader(request, story, back_url=reverse("lingua:approvals"))


@login_required
@require_http_methods(["GET", "POST"])
def progress(request):
    """Parent progress + advancement page (editors only). For each Lingua learner in
    the selected family: the warm hero metric, the advancement recommendation (LGA-67,
    confirm to apply — never auto), and the D-67 'testing above defaults' nudge. POST
    confirms a level change or dismisses a nudge. Learners are resolved via the
    directory adapter (the only host-identity seam, D-04)."""
    if not user_can_edit(request.user):
        raise Http404

    family = get_selected_family(request)
    # Editors OF THIS family only: user_can_edit is global (edit rights in ANY family),
    # but this page reads/mutates the SELECTED family — a view-only member (teacher/
    # grandparent) of it must not confirm level changes for its learners.
    if family is not None and not can_edit_family(request.user, family):
        raise Http404
    ids = directory.list_for_family(family.id) if family else []
    learners = {l.host_student_id: l for l in
                Learner.objects.filter(host_student_id__in=ids).select_related("profile")}

    if request.method == "POST":
        learner = learners.get(_int_or_none(request.POST.get("host_student_id")))
        if learner is None:
            raise Http404  # only act on a learner in the user's own family
        action = request.POST.get("action")
        if action == "advance":
            rec = services.advancement_recommendation(learner)
            to_level = request.POST.get("to_level")
            # only honor the level the engine actually recommended (no arbitrary jumps)
            if rec["action"] in ("promote", "demote") and to_level == rec["to_level"]:
                services.apply_advancement(learner, to_level, host_user_id=request.user.id)
                messages.success(request, f"Level updated to {to_level}.")
            else:
                messages.info(request, "No level change applied.")
        elif action == "dismiss_nudge":
            services.mark_nudge_shown(learner)
        return redirect("lingua:progress")

    rows = []
    for learner in sorted(learners.values(), key=lambda l: l.host_student_id):
        display = directory.get_learner_display(learner.host_student_id) or {}
        rows.append({
            "learner": learner,
            "name": display.get("name") or f"Learner {learner.host_student_id}",
            "level": learner.profile.content_ceiling,
            "band": learner.profile.get_track_profile_display(),
            "totals": services.reading_totals(learner),
            "rec": services.advancement_recommendation(learner),
            "nudge": services.nudge_testing_above_defaults(learner),
            "reading_list": services.reading_list(learner),
        })
    return render(request, "lingua/progress.html", {"rows": rows, "no_family": family is None})


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

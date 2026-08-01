"""lingua views. Parent-facing pages extend the host base.html (so NOT @lingua_csp
— that strict policy is reserved for the CSP-clean kid reader). Editors-only views
raise Http404 for non-editors, matching the rest of the app (tutor/views.py)."""
import re
from datetime import date
from urllib.parse import urlencode, urlsplit

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.utils.csp import CSP
from django.views.decorators.http import require_POST, require_http_methods

from django.db.models import Count, Max, Q

from core.permissions import can_edit_family, can_edit_family_or_global, user_can_edit
from core.utils import get_selected_family

from . import cognates, illustrate, profiles, services, storage
from .csp import LINGUA_CSP
from .integrations import directory
from .models import BookLogEntry, Learner, LibraryBook, Story, WritingError


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


def render_reader(request, story, *, finish_url="", back_url="", record_url=""):
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
        "finish_url": finish_url, "back_url": back_url, "record_url": record_url,
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
        elif action == "delete_recording":
            if services.delete_story_recording(learner, _int_or_none(request.POST.get("recording_id"))):
                messages.success(request, "Recording deleted.")
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
            "recordings": [
                {"rec": r, "url": storage.recording_url(r.audio_key)}
                for r in services.recordings_for(learner)
            ],
        })
    return render(request, "lingua/progress.html", {"rows": rows, "no_family": family is None})


def _int_or_none(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


_GRADE_DESCRIPTORS = None


def grade_descriptor(grade):
    """The band's "defining characteristics" blurb, transcribed from the family's own
    reading list (lingua/data/library_grades.json). Cached after the first read."""
    global _GRADE_DESCRIPTORS
    if _GRADE_DESCRIPTORS is None:
        import json
        from pathlib import Path
        path = Path(__file__).resolve().parent / "data" / "library_grades.json"
        try:
            _GRADE_DESCRIPTORS = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            _GRADE_DESCRIPTORS = {}
    return _GRADE_DESCRIPTORS.get(grade, "")


@login_required
def library_list(request):
    """The Spanish bookshelf — browse AND log in one place (HH-143).

    One "shelf" rail replaces the old track+grade double-decision, and every card
    carries a REAL one-click "Mark read" control (the old one was a decorative span
    that looked like a checkbox and did nothing — the reported confusion). Logging
    writes a BookLogEntry AND mirrors into the Work Log, so reading lands in the
    charter report. Defaults to the shelf matching the selected child's grade.
    """
    family = get_selected_family(request)
    can_log = can_edit_family_or_global(request.user, family)
    children = directory.family_children(getattr(family, "pk", None))

    # --- who / when we are logging for -----------------------------------
    log_child = None
    if children:
        want = _int_or_none(request.GET.get("for"))
        log_child = next((c for c in children if c["pk"] == want), children[0])
    today = timezone.localdate()
    try:
        log_on = date.fromisoformat(request.GET.get("on", ""))
    except ValueError:
        log_on = today
    if log_on > today:
        log_on = today

    # --- shelves: ONE rail (learners | by grade | grown-ups | free) -------
    base = LibraryBook.objects.all()
    counts = {}
    for row in base.values("track", "grade").annotate(n=Count("id")):
        counts[(row["track"], row["grade"])] = row["n"]
    grade_label = dict(LibraryBook.GRADE_CHOICES)

    def _track_total(track):
        return sum(n for (t, _g), n in counts.items() if t == track)

    shelves = []
    if _track_total(LibraryBook.CI):
        shelves.append({"key": "learners", "label": "For learners",
                        "count": _track_total(LibraryBook.CI)})
    grade_shelves = [
        {"key": "g-" + g, "label": grade_label[g],
         "count": counts.get((LibraryBook.NATIVE, g), 0)}
        for g in LibraryBook.GRADE_ORDER if counts.get((LibraryBook.NATIVE, g), 0)
    ]
    if grade_shelves:
        shelves.append({"divider": "By grade"})
        shelves.extend(grade_shelves)
    more = [{"key": "adult", "label": "Grown-ups", "count": _track_total(LibraryBook.ADULT)},
            {"key": "free", "label": "Free online", "count": _track_total(LibraryBook.FREE)}]
    more = [m for m in more if m["count"]]
    if more:
        shelves.append({"divider": "More"})
        shelves.extend(more)

    valid_keys = {s["key"] for s in shelves if "key" in s}
    shelf = request.GET.get("shelf") or ""
    if shelf not in valid_keys:
        shelf = _default_shelf(log_child, valid_keys)

    # --- resolve the shelf to a queryset ----------------------------------
    descriptor, shelf_label = "", ""
    if shelf.startswith("g-"):
        grade = shelf[2:]
        books = base.filter(track=LibraryBook.NATIVE, grade=grade).order_by("title")
        shelf_label = grade_label.get(grade, grade)
        descriptor = grade_descriptor(grade)
    else:
        track = {"learners": LibraryBook.CI, "adult": LibraryBook.ADULT,
                 "free": LibraryBook.FREE}.get(shelf, LibraryBook.CI)
        books = base.filter(track=track).order_by("level_label", "title")
        shelf_label = dict(LibraryBook.TRACK_CHOICES).get(track, "")
        descriptor = LibraryBook.TRACK_BLURBS.get(track, "")

    q = request.GET.get("q", "").strip()
    if q:
        books = books.filter(Q(title__icontains=q) | Q(author__icontains=q))
    books = list(books)

    # --- annotate what this child has already read (one query) ------------
    for b in books:
        b.read_count, b.read_last, b.read_entry_id = 0, None, None
    if log_child and books:
        learner = Learner.objects.filter(host_student_id=log_child["pk"]).first()
        if learner:
            # ONE query for every read of these books, oldest first; last write wins, so
            # `entry` ends up being the same row whose date the label shows. Deliberately
            # not Count + Max("id") in SQL: those two diverge the moment a read is
            # backdated (the log bar invites exactly that), and undo would then remove a
            # different entry than the one it names. The family's reading log is small,
            # so folding it in Python costs nothing and can't get that wrong.
            reads = {}
            for book_id, entry_id, read_on in (
                BookLogEntry.objects
                .filter(learner=learner, book_id__in=[b.pk for b in books])
                .order_by("read_on", "id")
                .values_list("book_id", "id", "read_on")
            ):
                n = reads[book_id][0] + 1 if book_id in reads else 1
                reads[book_id] = (n, read_on, entry_id)
            for b in books:
                r = reads.get(b.pk)
                if r:
                    b.read_count, b.read_last, b.read_entry_id = r

    # non-native shelves group by their own ladder (CI level / adult stage)
    groups = []
    if not shelf.startswith("g-"):
        for book in books:
            key = book.level_label or "—"
            if not groups or groups[-1]["label"] != key:
                groups.append({"label": key, "books": []})
            groups[-1]["books"].append(book)

    # The child and any backdate must ride along on EVERY link, or picking "read on
    # Jul 10" and then switching shelves silently refiles the next tick as today —
    # wrong data in the charter report, entered without an error. `keep_qs` is the
    # tail appended to "?shelf=…"; `next_qs` is the full post-log redirect target.
    keep = {}
    if log_child:
        keep["for"] = str(log_child["pk"])
    if log_on != today:
        keep["on"] = log_on.isoformat()
    keep_qs = ("&" + urlencode(keep)) if keep else ""
    next_kw = dict(keep, shelf=shelf)
    if q:
        next_kw["q"] = q
    next_qs = reverse("lingua:library_list") + "?" + urlencode(next_kw)

    return render(request, "lingua/library_list.html", {
        "subnav": "library",
        "shelves": shelves, "shelf": shelf, "shelf_label": shelf_label,
        "descriptor": descriptor, "books": books, "groups": groups,
        "total": len(books), "q": q,
        "children": children, "log_child": log_child, "multi_child": len(children) > 1,
        "no_family": family is None,
        "log_on": log_on, "log_on_is_today": log_on == today, "today": today,
        # A read from a previous year must show its year, or "Jan 5" reads as this Jan.
        "this_year": str(today.year),
        "can_log": bool(can_log and log_child),
        "keep_qs": keep_qs, "next_qs": next_qs,
    })


def _default_shelf(child, valid_keys):
    """The shelf to open when none is asked for: match the child's grade, else the
    learner (CI) ladder — never Pre-K by accident."""
    grade_map = {"PREK": "PK", "K": "K"}
    raw = (child or {}).get("grade_level") or ""
    key = grade_map.get(raw) or (raw[1:].lstrip("0") if raw.startswith("G") else "")
    if key and "g-" + key in valid_keys:
        return "g-" + key
    if "learners" in valid_keys:
        return "learners"
    return next(iter(sorted(valid_keys)), "")


@login_required
@require_POST
def library_mark_read(request):
    """One-click 'this child read this book' from the shelf (HH-143).

    Logs (or undoes) a read for the child named in the sticky log bar. The child is
    resolved INSIDE the selected family's queryset — never trusted from the POST — and
    the redirect target is validated, so neither a wrong-family write nor an open
    redirect is possible.
    """
    from django.utils.http import url_has_allowed_host_and_scheme

    family = get_selected_family(request)
    if family is None or not can_edit_family_or_global(request.user, family):
        raise Http404
    child = directory.child_in_family(_int_or_none(request.POST.get("child")), family.pk)
    if child is None:
        raise Http404
    learner = services.learner_for_child(child)

    bid = (request.POST.get("book") or "").strip()
    book = (LibraryBook.objects.filter(pk=bid).first()
            if bid.isdigit() and bid.isascii() else None)
    try:
        read_on = date.fromisoformat(request.POST.get("on", ""))
    except ValueError:
        read_on = None
    # Clamp the same way the GET side does. `max=` on the date input is client-side
    # only, so a mistyped year would otherwise file a phantom entry decades out — in
    # the Work Log AND the charter report, sorted to the top forever.
    if read_on and read_on > timezone.localdate():
        read_on = timezone.localdate()

    if request.POST.get("action") == "undo":
        entry_id = _int_or_none(request.POST.get("entry"))
        if entry_id and services.delete_book_log(learner, entry_id):
            messages.success(request, "Removed from the reading log.")
        else:
            messages.info(request, "Nothing to remove.")
    else:
        entry = services.log_book(
            learner, book=book, title=request.POST.get("title", ""),
            read_on=read_on, logged_by=BookLogEntry.PARENT,
        )
        if entry is None:
            messages.info(request, "Pick a book, or type a title.")
        else:
            messages.success(
                request,
                "Logged: " + child["first_name"] + " read " + entry.display_title + ".")

    nxt = request.POST.get("next") or ""
    if not url_has_allowed_host_and_scheme(nxt, allowed_hosts=None):
        nxt = reverse("lingua:library_list")
    if book is not None:
        nxt += "#book-" + str(book.pk)
    return redirect(nxt)


@login_required
def session_kit(request):
    """"La sesión" — the parent's 20 minutes with one child (LGA-94).

    The younger girl disengaged from a screen acting as teacher, so this page is aimed
    at the PARENT, not her: the routine to follow, the Spanish to say it in, and a
    sheet to print. The audio is the load-bearing part — it lets a non-fluent parent
    run the routine in Spanish by tapping and repeating.
    """
    family = get_selected_family(request)
    children = directory.family_children(getattr(family, "pk", None))

    child = None
    if children:
        want = _int_or_none(request.GET.get("for"))
        child = next((c for c in children if c["pk"] == want), children[0])

    learner = services.learner_for_child(child) if child else None
    sheet = services.session_sheet(learner) if learner else None

    return render(request, "lingua/session.html", {
        "subnav": "session",
        "children": children, "child": child, "multi_child": len(children) > 1,
        "no_family": family is None,
        "groups": services.classroom_phrases_with_audio(),
        "sheet": sheet,
        # LGA-95: what she keeps getting wrong, and what to correct HOW. Direct for
        # the younger child (supply the form), indirect for the older (underline, she
        # self-corrects) — Kang & Han (2015): correction works either way, so match it
        # to the child and correct selectively.
        "error_categories": [
            {"value": c, "label": dict(WritingError.CATEGORY_CHOICES)[c]}
            for c in WritingError.CATEGORY_ORDER
        ],
        "top_errors": services.top_error_categories(learner) if learner else [],
        "focus": services.remediation_focus(learner) if learner else None,
        "correction_mode": (
            "indirect" if getattr(getattr(learner, "profile", None), "track_profile", "")
            == profiles.KIDS_OLDER else "direct"
        ),
        # getattr twice: a Learner without a LearnerProfile would otherwise 500 here,
        # and session_sheet already defends against exactly that case.
        "band_label": getattr(
            getattr(learner, "profile", None), "get_track_profile_display", lambda: ""
        )(),
    })


@login_required
@require_POST
def session_log_error(request):
    """Tag one mistake while marking her paper (LGA-95).

    Two taps, not a form — the parent is mid-session with a pencil in hand. The child
    is resolved INSIDE the selected family's queryset, never trusted from the POST."""
    family = get_selected_family(request)
    if family is None or not can_edit_family_or_global(request.user, family):
        raise Http404
    child = directory.child_in_family(_int_or_none(request.POST.get("child")), family.pk)
    if child is None:
        raise Http404

    learner = services.learner_for_child(child)
    entry = services.log_writing_error(
        learner,
        request.POST.get("category", ""),
        source=request.POST.get("source", ""),
        wrote=request.POST.get("wrote", ""),
        expected=request.POST.get("expected", ""),
    )
    if entry is None:
        messages.info(request, "Pick what kind of mistake it was.")
    else:
        messages.success(
            request,
            f"Noted for {child['first_name']}: {entry.get_category_display().split('—')[0].strip()}.")
    return redirect(f"{reverse('lingua:session')}?for={child['pk']}")


@login_required
def book_log_redirect(request):
    """The parent reading log now lives IN the Work Log (HH-143) — one record, one
    place. Kept under the old name so stale links/bookmarks land somewhere sensible.

    Both the host URL name and the subject come from settings, so extracting lingua
    (which takes the host's worklog with it) degrades to the module's own progress page
    instead of a NoReverseMatch 500."""
    subject = settings.LINGUA.get("WORKLOG_SUBJECT", "")
    try:
        target = reverse(settings.LINGUA.get("WORKLOG_LIST_URL_NAME") or "")
    except NoReverseMatch:
        return redirect("lingua:progress")
    return redirect(target + "?" + urlencode({"subject": subject}))

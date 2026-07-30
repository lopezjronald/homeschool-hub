"""The student portal — a kid's own view of just their work.

Every view resolves a signed token to ONE student and scopes every queryset to
that student. No login, no navigation into the parent app, nothing that isn't
theirs. Parents generate the link from the child's profile page.
"""

import json
from collections import defaultdict
from datetime import date
from itertools import groupby

from django.contrib.auth import authenticate, login
from django.core.cache import cache
from django.db.models import Q
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from activities.models import ExternalActivity
from lingua import comprehension as lingua_comprehension
from lingua import services as lingua_services
from lingua import storage as lingua_storage
from lingua import views as lingua_views
from lingua.models import LibraryBook as LinguaLibraryBook
from lingua.models import MilestoneAward as LinguaMilestone
from lingua.models import PathwayStep
from lingua.models import Story as LinguaStory
from curricula.models import Curriculum, CurriculumPlacement
from curricula.subjects import emoji_for, is_spelling
from tutor import ai, grading
from tutor.models import Material, QuestionSet, ResponseSheet
from worklog.models import WorkLogEntry

from .tokens import student_from_token


def _resolve_student(token):
    student = student_from_token(token)
    if student is None:
        raise Http404
    return student


# --- Lingua (Spanish) kid surface -----------------------------------------
# Student→Learner resolution lives HERE, in the host, so lingua core never imports
# a host model (D-03/D-04): the host knows the child's age and hands lingua a plain
# host_student_id + a track profile.

def _lingua_learner(student):
    """The lingua Learner for this student, provisioned on first entry (idempotent).

    Goes through the shared adapter so the kid portal and the parent Spanish pages
    provision identically — this used to carry its own copy of the age-band rule, which
    is exactly the kind of thing that drifts."""
    from homeschool_hub.adapters import lingua_students

    return lingua_students.learner_for(student)


def lingua_plan(request, token):
    """The kid's Spanish 'today' page: Camino Hoy CTA + trail stones (LGA-87).
    Lives in the portal shell (extends base_portal.html); the reader itself is CSP-clean."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    celebrate = None
    try:
        threshold = int(request.GET.get("celebrate", ""))
        kind = request.GET.get("kind", "")
        if kind in (LinguaMilestone.WORDS, LinguaMilestone.KNOWN):
            celebrate = {"threshold": threshold, "kind": kind}
    except (TypeError, ValueError):
        celebrate = None
    extras = lingua_services.camino_plan_extras(learner)
    return render(request, "portal/lingua_plan.html", {
        "student": student, "token": token,
        "plan": lingua_services.build_daily_plan(learner),
        "totals": lingua_services.reading_totals(learner),
        "band": learner.profile.track_profile,
        "celebrate": celebrate,
        "tutor_packets": lingua_services.tutor_packets_for(student.pk),
        "camino_hint": extras["camino_hint"],
        "review_due": extras["review_due"],
    })


def lingua_path(request, token):
    """Kid Camino map: every visible stop is open; checkbox marks Hecho (LGA-93)."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    status = lingua_services.pathway_status(learner)
    steps = []
    for row in status["steps"]:
        step = row["step"]
        if row["status"] == lingua_services.PATH_COMPLETE:
            label = "Practicar otra vez" if row["practicar"] else "Hecho"
        elif row["primary"]:
            label = "Siguiente · ¡Empezar!"
        else:
            label = "¡Empezar!"
        steps.append({
            **row,
            "href": _pathway_step_href(token, student.pk, step),
            "label": label,
        })
    return render(request, "portal/lingua_path.html", {
        "student": student, "token": token,
        "pathway": status["pathway"],
        "steps": steps,
        "band": learner.profile.track_profile,
    })


@csrf_exempt
@require_POST
def lingua_path_check(request, token):
    """Toggle a Camino map checkbox (LGA-93). Tokenless like other kid portal writes."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    try:
        step_id = int(request.POST.get("step_id", ""))
    except (TypeError, ValueError):
        step_id = None
    step = (
        PathwayStep.objects.filter(pk=step_id, pathway__active=True).first()
        if step_id else None
    )
    if step is None:
        raise Http404("Step not found.")
    # Only allow checking steps on this child's band pathway / visible tutor steps.
    status = lingua_services.pathway_status(learner)
    allowed = {row["step"].pk for row in status["steps"]}
    if step.pk not in allowed:
        raise Http404("Step not found.")
    done = request.POST.get("done", "1") not in ("0", "false", "off", "")
    lingua_services.set_pathway_checkmark(learner, step, done)
    return redirect(reverse("portal:lingua_path", args=[token]))


def _pathway_step_href(token, host_student_id, step):
    """Deeplink for a PathwayStep — never invents new content URLs."""
    kind, ref = step.kind, (step.target_ref or "").strip()
    if kind == PathwayStep.STORY and ref.isdigit():
        return reverse("portal:lingua_read", args=[token, int(ref)])
    if kind == PathwayStep.STORY_LEVEL:
        return reverse("portal:lingua_library", args=[token])
    if kind == PathwayStep.PHONICS:
        return reverse("portal:lingua_phonics", args=[token])
    if kind == PathwayStep.LISTEN:
        return reverse("portal:lingua_listen", args=[token])
    if kind == PathwayStep.TUTOR_PACKET:
        if ref.isdigit() and lingua_services.tutor_packet_for(host_student_id, int(ref)):
            return reverse("portal:lingua_tutor_packet", args=[token, int(ref)])
        return reverse("portal:lingua_tutor", args=[token])
    if kind == PathwayStep.REVIEW:
        return reverse("portal:lingua_plan", args=[token])
    if kind == PathwayStep.LINK and ref:
        # Allow only named portal lingua routes (no open redirects).
        try:
            return reverse(f"portal:{ref}", args=[token])
        except NoReverseMatch:
            return reverse("portal:lingua_plan", args=[token])
    return reverse("portal:lingua_plan", args=[token])


def lingua_library(request, token):
    """The kid's 'Biblioteca': a leveled reading list of every Spanish story, grouped
    by level with a friendly descriptor, showing how many times they've read each and
    which ones they've 'got down' (⭐). Tokenless; identity comes from the signed token.
    Lives in the portal shell; the reader it links to stays CSP-clean."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    return render(request, "portal/lingua_library.html", {
        "student": student, "token": token,
        "levels": lingua_services.reading_list(learner),
        "totals": lingua_services.reading_totals(learner),
    })


def lingua_books(request, token):
    """The kid's physical-book reading log 'Mis libros' (LGA-75): the books they've
    logged + a delightful one-to-two-tap entry (pick a suggested book or type another,
    then a feeling button submits). Tokenless; identity from the signed token."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    entries = lingua_services.book_logs(learner)
    return render(request, "portal/lingua_books.html", {
        "student": student, "token": token,
        "entries": entries, "count": len(entries),
        "suggested": lingua_services.suggested_books(learner),
        "celebrate": request.GET.get("logged") == "1",
        "nothing": request.GET.get("nothing") == "1",
        "today": timezone.localdate(),
    })


@csrf_exempt
@require_POST
def lingua_book_log(request, token):
    """Log one physical book the kid read (LGA-75). Token-authed + csrf-exempt like the
    other tokenless portal writes. The feeling button's value is ``enjoyed``; ``book_id``
    is a catalog pk or 'other' (then ``custom_title``)."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    bid = (request.POST.get("book_id") or "").strip()
    # isdigit() is True for non-ASCII digits that int()/the ORM reject, so filter on an
    # ASCII-only check to keep a hand-crafted POST from raising.
    book = (LinguaLibraryBook.objects.filter(pk=bid).first()
            if bid.isdigit() and bid.isascii() else None)
    try:
        read_on = date.fromisoformat(request.POST.get("read_on", ""))
    except ValueError:
        read_on = None          # blank/garbage → log_book defaults to today
    entry = lingua_services.log_book(
        learner, book=book,
        title=request.POST.get("custom_title", ""),
        author=request.POST.get("custom_author", ""),
        read_on=read_on,
        enjoyed=request.POST.get("enjoyed", ""),
        note=request.POST.get("note", ""),
        logged_by="kid",
    )
    # Only celebrate when something was actually logged — picking "Otro" without
    # typing a title logs nothing, and a false "¡Anotado!" would teach the child the
    # book is recorded when it isn't.
    suffix = "?logged=1" if entry is not None else "?nothing=1"
    return redirect(reverse("portal:lingua_books", args=[token]) + suffix)


def lingua_read(request, token, story_id):
    """Tokenless read-along for a kid. Identity comes from the signed token (never
    request.user); only APPROVED stories are servable (D-49). Delegates rendering to
    lingua so the page stays CSP-clean and the module stays extractable."""
    _resolve_student(token)  # 404s an invalid/tampered token before serving anything
    story = get_object_or_404(LinguaStory, pk=story_id, status=LinguaStory.APPROVED)
    # Only offer the recorder when a truly-private recordings store is configured, so a
    # child's voice can never be written to a publicly-exposed bucket (LGA-73).
    record_url = (reverse("portal:lingua_record", args=[token, story_id])
                  if lingua_storage.recordings_enabled() else "")
    return lingua_views.render_reader(
        request, story,
        finish_url=reverse("portal:lingua_finish", args=[token, story_id]),
        back_url=reverse("portal:lingua_plan", args=[token]),
        record_url=record_url,
    )


def lingua_phonics(request, token):
    """Spanish phonics mini-lesson (F-04, LGA-64/84): decoding rules + tappable
    practice words with pre-baked audio when available. Linked from the plan for
    the youngest band; any learner may open it. Provisions the learner on entry."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    lingua_services.record_station_visit(learner, PathwayStep.PHONICS)
    return render(request, "portal/lingua_phonics.html", {
        "student": student, "token": token,
        "rules": lingua_services.phonics_rules_with_audio(),
    })


def lingua_listen(request, token):
    """Spanish listening track (F-02/N-02, LGA-55/57/86): curated YouTube plus
    in-app alphabet chart and tutor practice phrases. Listening minutes feed the
    same 'minutes of input' hero metric as reading. Provisions the learner on entry."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    return render(request, "portal/lingua_listen.html", {
        "student": student, "token": token,
        "resources": lingua_services.listening_resources(learner.profile.track_profile),
        "alphabet": lingua_services.alphabet_tiles_with_audio(),
        "phrases": lingua_services.practice_phrases_for(student.pk),
        "totals": lingua_services.reading_totals(learner),
        "logged": request.GET.get("logged"),
    })


def lingua_tutor(request, token):
    """Con el maestro (LGA-85): list of tutor homework packets visible to this child."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    lingua_services.record_station_visit(learner, PathwayStep.TUTOR_PACKET)
    packets = lingua_services.tutor_packets_for(student.pk)
    return render(request, "portal/lingua_tutor.html", {
        "student": student, "token": token, "packets": packets,
    })


def lingua_tutor_packet(request, token, packet_id):
    """One tutor packet: download handout + practice phrases (LGA-85)."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    packet = lingua_services.tutor_packet_for(student.pk, packet_id)
    if packet is None:
        raise Http404("Packet not found.")
    lingua_services.record_station_visit(
        learner, PathwayStep.TUTOR_PACKET, str(packet.pk),
    )
    lingua_services.record_station_visit(learner, PathwayStep.TUTOR_PACKET)
    phrases = [
        p for p in lingua_services.practice_phrases_for(student.pk)
        if p["packet_id"] == packet.pk
    ]
    return render(request, "portal/lingua_tutor_packet.html", {
        "student": student, "token": token, "packet": packet, "phrases": phrases,
    })


@csrf_exempt
@require_POST
def lingua_listen_log(request, token):
    """Log a listening check-in (minutes of input, LGA-55/57). Tokenless like the other
    portal writes. Minutes are clamped in the service; an unknown/blank resource still
    logs the minutes (resource is optional). Redirects back to the listening page."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    resource = None
    try:
        resource = lingua_services.ListeningResource.objects.filter(
            pk=int(request.POST.get("resource_id", "")), active=True).first()
    except (TypeError, ValueError):
        resource = None
    try:
        minutes = int(request.POST.get("minutes", 0))
    except (TypeError, ValueError):
        minutes = 0
    session = lingua_services.record_listening(learner, resource, minutes)
    base = reverse("portal:lingua_listen", args=[token])
    # Only flash the "you logged N minutes" banner when a session was actually recorded —
    # a 0-minute no-op redirects clean (else "?logged=0" shows a false success banner).
    return redirect(f"{base}?logged={session.minutes}" if session else base)


@csrf_exempt
@require_POST
def lingua_capture_word(request, token):
    """Add a word the child tapped in the reader to their review deck (F-03, LGA-61).
    Tokenless like the other portal writes (the signed token is the credential). The
    scheduler + card format follow the learner's band; capture is idempotent per word,
    so tapping the same word twice never duplicates a card. Returns JSON
    {captured, format}."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    word = (request.POST.get("word") or "").strip()
    item = lingua_services.capture_word(learner, word)
    if item is None:
        return JsonResponse({"captured": False})
    return JsonResponse({"captured": True, "format": lingua_services.card_format_for(item.scheduler)})


@csrf_exempt
@require_POST
def lingua_record(request, token, story_id):
    """Save a PRIVATE recording of the child reading this story aloud (LGA-73).
    Token-authed + csrf-exempt like the other tokenless portal writes. The audio goes
    to the private media store and is NEVER sent to any AI/TTS — only the logged-in
    parent can play it back (signed URL) or delete it. Returns JSON {saved}."""
    if not lingua_storage.recordings_enabled():
        return JsonResponse({"saved": False, "error": "recording disabled"}, status=404)
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    story = get_object_or_404(LinguaStory, pk=story_id, status=LinguaStory.APPROVED)
    upload = request.FILES.get("audio")
    if upload is None:
        return JsonResponse({"saved": False, "error": "no audio"}, status=400)
    # Reject oversized BEFORE reading the body into memory (DoS guard) — the multipart
    # part's declared size; the service re-checks the actual bytes.
    if getattr(upload, "size", 0) and upload.size > lingua_services.RECORDING_MAX_BYTES:
        return JsonResponse({"saved": False, "error": "too large"}, status=400)
    try:
        seconds = int(request.POST.get("seconds", 0))
    except (TypeError, ValueError):
        seconds = 0
    try:
        lingua_services.save_story_recording(
            learner, story, upload.read(),
            content_type=getattr(upload, "content_type", "") or "", seconds=seconds,
        )
    except ValueError:
        return JsonResponse({"saved": False, "error": "invalid recording"}, status=400)
    return JsonResponse({"saved": True})


@csrf_exempt
@require_POST
def lingua_finish(request, token, story_id):
    """Log a completed read (ReadingSession) and return to the plan. Token-authed +
    csrf-exempt like the other tokenless portal writes — the unguessable signed token
    is the credential, not a cookie, so there's nothing for CSRF to ride on."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    story = get_object_or_404(LinguaStory, pk=story_id, status=LinguaStory.APPROVED)
    try:
        seconds = int(request.POST.get("seconds", 0))
    except (TypeError, ValueError):
        seconds = 0
    lingua_services.record_reading(learner, story, seconds=seconds)
    # Low-stakes comprehension self-check (LGA-52): the reader's 3-emoji tap. Optional —
    # a missing/garbage value just skips the check (the read still counts).
    felt = request.POST.get("felt")
    if felt in lingua_comprehension.FELT_TO_RESULT:
        lingua_services.record_comprehension(
            learner, story, lingua_comprehension.SELF_CHECK,
            result=lingua_comprehension.FELT_TO_RESULT[felt],
        )
    # Celebrate any milestone this read just crossed (D-60/61) — pass the biggest new
    # one to the plan as a query param (stateless; the portal is tokenless).
    url = reverse("portal:lingua_plan", args=[token])
    awarded = lingua_services.award_milestones(learner)
    if awarded:
        url += f"?celebrate={awarded[0].threshold}&kind={awarded[0].kind}"
    return redirect(url)


def _placed_curriculum_ids(student):
    return list(student.placements.values_list("curriculum_id", flat=True))


def _visible_materials(student):
    """Approved materials for this child (theirs, or unpinned ones in their curricula)."""
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        Material.objects.filter(status=Material.APPROVED)
        .filter(
            Q(child=student)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter")
        .order_by("lesson__chapter__number", "lesson__order")
    )


def _visible_question_sets(student):
    """Approved STUDENT-form question sets this child may open.

    Teacher-led discussion sets are intentionally excluded — those are for the
    parent to lead orally, not for the child to fill out.
    """
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        QuestionSet.objects.filter(status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        .filter(
            Q(child=student)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter", "lesson__chapter__curriculum")
    )


def _annotated_question_sets(student):
    """Ordered list of visible sets with this child's response attached."""
    sets = list(
        _visible_question_sets(student).order_by(
            "lesson__chapter__curriculum__name", "lesson__chapter__number", "lesson__order", "id",
        )
    )
    responses = {
        r.question_set_id: r
        for r in ResponseSheet.objects.filter(child=student, question_set__in=sets)
    }
    for qs in sets:
        qs.my_response = responses.get(qs.pk)
    return sets


def _visible_activities(student):
    """Active external activities for this child (theirs + whole-family)."""
    qs = ExternalActivity.objects.filter(is_active=True)
    if student.family_id:
        return qs.filter(Q(student=student) | Q(student__isnull=True, family=student.family))
    # Null-family child: scope whole-family activities to the owner so a null
    # family filter can't match every other user's null-family activities.
    return qs.filter(
        Q(student=student)
        | Q(student__isnull=True, family__isnull=True, parent=student.parent)
    )


def _set_is_done(qs):
    """True if this child has already turned in the set."""
    return bool(getattr(qs, "my_response", None) and qs.my_response.is_submitted)


def _subject_cards(student):
    """One card per subject the child is in: progress + the single next thing.

    Unions the child's curriculum placements with any curriculum that owns work
    they can see (question sets or materials), so nothing is hidden — but each
    subject collapses to one calm card, never a wall of rows. This is the
    "what's next, tap-a-subject" surface (autonomy to choose, one clear step).
    """
    annotated = _annotated_question_sets(student)
    materials = list(_visible_materials(student))

    sets_by_curr = defaultdict(list)
    for qs in annotated:
        sets_by_curr[qs.lesson.chapter.curriculum_id].append(qs)
    materials_by_curr = defaultdict(list)
    for m in materials:
        materials_by_curr[m.lesson.chapter.curriculum_id].append(m)

    placements = {
        p.curriculum_id: p
        for p in CurriculumPlacement.objects.filter(child=student).select_related(
            "curriculum", "current_lesson", "current_lesson__chapter",
        )
    }

    # Placements first (stable order), then any other curriculum owning work.
    curr_ids = list(placements)
    for cid in list(sets_by_curr) + list(materials_by_curr):
        if cid not in curr_ids:
            curr_ids.append(cid)

    curricula = {p.curriculum_id: p.curriculum for p in placements.values()}
    missing = [cid for cid in curr_ids if cid not in curricula]
    if missing:
        for c in Curriculum.objects.filter(id__in=missing):
            curricula[c.id] = c

    cards = []
    for cid in curr_ids:
        curriculum = curricula.get(cid)
        if curriculum is None:
            continue
        placement = placements.get(cid)
        curr_sets = sets_by_curr.get(cid, [])
        sets_total = len(curr_sets)
        sets_done = sum(1 for qs in curr_sets if _set_is_done(qs))
        cards.append({
            "curriculum": curriculum,
            "emoji": emoji_for(curriculum.subject),
            "placement": placement,
            "progress": placement.progress() if placement else None,
            "current_lesson": placement.current_lesson if placement else None,
            "next_set": next((qs for qs in curr_sets if not _set_is_done(qs)), None),
            "sets_done": sets_done,
            "sets_total": sets_total,
            "sets_pct": round(sets_done / sets_total * 100) if sets_total else 0,
            "materials_count": len(materials_by_curr.get(cid, [])),
            # Online subjects (Beast Academy, DIVE…) launch out to the website.
            "is_external": curriculum.is_external,
            "launch_url": curriculum.website_url if curriculum.is_external else "",
        })

    cards.sort(key=lambda c: (c["curriculum"].subject or "", c["curriculum"].name))
    return cards


def portal_home(request, token):
    """The kid's 'Today' surface: one calm card per subject, one next step each."""
    student = _resolve_student(token)
    return render(request, "portal/portal_home.html", {
        "student": student,
        "token": token,
        "subjects": _subject_cards(student),
        "activities": _visible_activities(student),
    })


def portal_subject(request, token, curriculum_id):
    """Drill into one subject: chapters, the current one open, finished folded."""
    student = _resolve_student(token)

    sets = [
        qs for qs in _annotated_question_sets(student)
        if qs.lesson.chapter.curriculum_id == curriculum_id
    ]
    materials = [
        m for m in _visible_materials(student)
        if m.lesson.chapter.curriculum_id == curriculum_id
    ]
    placement = (
        CurriculumPlacement.objects
        .filter(child=student, curriculum_id=curriculum_id)
        .select_related("curriculum", "current_lesson", "current_lesson__chapter")
        .first()
    )
    # Authorize: the child must be placed in this subject or own work in it.
    if placement is None and not sets and not materials:
        raise Http404
    curriculum = placement.curriculum if placement else get_object_or_404(Curriculum, pk=curriculum_id)

    next_set = next((qs for qs in sets if not _set_is_done(qs)), None)
    if next_set is not None:
        current_chapter = next_set.lesson.chapter.number
    elif placement and placement.current_lesson:
        current_chapter = placement.current_lesson.chapter.number
    else:
        current_chapter = None

    # Sets arrive ordered curriculum→chapter→lesson, so group by chapter number.
    chapters = []
    for (number, title), group in groupby(
        sets, key=lambda s: (s.lesson.chapter.number, s.lesson.chapter.title),
    ):
        items = list(group)
        chapters.append({
            "number": number,
            "title": title,
            "sets": items,
            "done": sum(1 for qs in items if _set_is_done(qs)),
            "total": len(items),
            "is_current": number == current_chapter,
        })
    # If nothing is flagged current (e.g. all finished), open the first chapter.
    if chapters and not any(ch["is_current"] for ch in chapters):
        chapters[0]["is_current"] = True

    return render(request, "portal/portal_subject.html", {
        "student": student,
        "token": token,
        "curriculum": curriculum,
        "emoji": emoji_for(curriculum.subject),
        "placement": placement,
        "progress": placement.progress() if placement else None,
        "current_lesson": placement.current_lesson if placement else None,
        "next_set": next_set,
        "chapters": chapters,
        "materials": materials,
    })


def portal_material(request, token, pk):
    """Kid view of an approved material — student layers only, never the teaching guide."""
    student = _resolve_student(token)
    material = get_object_or_404(_visible_materials(student), pk=pk)
    return render(request, "portal/portal_material.html", {
        "student": student,
        "token": token,
        "material": material,
    })


# Brute-force guard for the parent gate. Per-worker with the default LocMemCache,
# so the real ceiling is a small multiple of this — still enough to stop an
# online guessing attack from a child's device.
_GATE_MAX_ATTEMPTS = 8
_GATE_LOCKOUT_SECONDS = 15 * 60


def portal_parent_gate(request, token):
    """Cross back from a child's portal to the parent dashboard.

    The portal is the child's surface — token-authed, no login — so the child
    also holds this link. We already know *which* parent owns the child from the
    token, so returning to the parent side asks only for that parent's password
    (a re-auth, not a fresh sign-in) and then drops them straight on the
    dashboard, instead of bouncing to the public landing / full login page. A
    parent who still has a live session skips the prompt entirely.
    """
    student = _resolve_student(token)
    parent = student.parent
    if parent is None:  # no owner to re-auth against; fall back to normal sign-in
        return redirect("accounts:login")

    # Live parent session → straight through, no password needed.
    if request.user.is_authenticated:
        return redirect("dashboard:dashboard")

    # The child's link is a bookmark on a kid's device, so throttle password
    # attempts against this (already-identified) parent to blunt brute-forcing.
    fail_key = f"parentgate:fail:{parent.pk}"

    error = ""
    if request.method == "POST":
        if cache.get(fail_key, 0) >= _GATE_MAX_ATTEMPTS:
            error = "Too many tries. Please wait a few minutes, then try again."
        else:
            password = request.POST.get("password", "")
            # Authenticate the token's parent specifically — a wrong password (or a
            # different user's password) can't open this dashboard.
            user = authenticate(request, username=parent.get_username(), password=password)
            if user is not None:
                cache.delete(fail_key)
                login(request, user)
                return redirect("dashboard:dashboard")
            cache.set(fail_key, cache.get(fail_key, 0) + 1, _GATE_LOCKOUT_SECONDS)
            error = "That password doesn't match. Please try again."

    return render(request, "portal/parent_gate.html", {
        "student": student,
        "token": token,
        "parent": parent,
        "error": error,
    })


def _sheet_for(student, question_set):
    sheet, _ = ResponseSheet.objects.get_or_create(question_set=question_set, child=student)
    return sheet


def portal_questions(request, token, set_pk):
    """The response form: no autocorrect, autosaves as the child types."""
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)

    if request.method == "POST":
        sheet = _submit_sheet(student, question_set, request.POST)
        # Start grading the instant she turns it in — a head start during the
        # celebration, and NOT dependent on the feedback page's JS firing. This is
        # idempotent; the feedback page re-kicks and the grade_pending sweep are
        # additional safety nets so a submission can't stay ungraded.
        if sheet.is_submitted and sheet.work_entry_id:
            grading.start_background_grade(sheet.pk)
        return redirect("portal:portal_feedback", token=token, set_pk=set_pk)

    sheet = _sheet_for(student, question_set)
    questions = list(question_set.questions.all())
    for q in questions:
        q.my_answer = sheet.answer_for(q)
        q.my_coach = (sheet.draft_feedback or {}).get(str(q.pk))

    # Spell-check + synonym help everywhere EXCEPT spelling curricula, where the
    # child is supposed to spell the words unaided.
    spelling = is_spelling(question_set.lesson.chapter.curriculum.subject)

    return render(request, "portal/portal_questions.html", {
        "student": student,
        "token": token,
        "question_set": question_set,
        "questions": questions,
        "sheet": sheet,
        "spellcheck_on": not spelling,
        "wordhelp_on": not spelling,
    })


def _submit_sheet(student, question_set, post_data):
    """Atomically turn in a sheet: exactly one DRAFT→SUBMITTED transition.

    Locks the sheet row so a double-click or two-tab race can't create two
    WorkLogEntries; a request that loses the race sees SUBMITTED and no-ops.
    """
    with transaction.atomic():
        sheet, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if sheet.is_submitted:
            return sheet  # someone already turned it in

        _merge_answers(sheet, post_data)
        sheet.status = ResponseSheet.SUBMITTED
        sheet.submitted_at = timezone.now()
        curriculum = question_set.lesson.chapter.curriculum
        sheet.work_entry = WorkLogEntry.objects.create(
            parent=student.parent,
            family=student.family,
            child=student,
            curriculum=curriculum,
            subject=curriculum.subject or "Literature",
            description=(
                f"{question_set.title} — submitted from {student.first_name}'s portal.\n\n"
                + sheet.as_worklog_text()
            ),
            date=timezone.localdate(),
        )
        sheet.save()
        return sheet


def _merge_answers(sheet, data):
    """Merge posted answer_<id> fields into the sheet's answers JSON."""
    answers = dict(sheet.answers or {})
    question_ids = set(
        str(pk) for pk in sheet.question_set.questions.values_list("pk", flat=True)
    )
    for key, value in data.items():
        if key.startswith("answer_"):
            qid = key.removeprefix("answer_")
            if qid in question_ids:
                answers[qid] = value
    sheet.answers = answers


def portal_feedback(request, token, set_pk):
    """The 'you turned it in!' page — celebration plus the agent's quick feedback.

    If a draft assessment already exists, its child-facing pieces render at
    once; otherwise the page shows a friendly reading state and JS asks
    ``portal_feedback_generate`` to produce one. The child never sees a level.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return redirect("portal:portal_questions", token=token, set_pk=set_pk)

    from tutor.models import MasteryAssessment

    assessment = MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).first()
    from tutor import ai

    return render(request, "portal/portal_feedback.html", {
        "student": student,
        "token": token,
        "question_set": question_set,
        "sheet": sheet,
        "assessment": assessment,
        "can_generate": assessment is None and ai.is_configured(),
    })


@csrf_exempt
@require_POST
def portal_feedback_generate(request, token, set_pk):
    """Generate (idempotently) the agent's feedback for a submitted sheet.

    CSRF-exempt for the same reason as autosave: portal auth is the signed
    token in the URL, not an ambient cookie. Returns only child-facing fields.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return JsonResponse({"ok": False}, status=409)

    from tutor import ai, grading

    try:
        assessment, _created = grading.auto_grade_sheet(sheet)
    except ai.GraderError:
        return JsonResponse({"ok": False})  # kid page falls back to plain celebration
    if assessment is None:
        return JsonResponse({"ok": False})
    return JsonResponse({
        "ok": True,
        "encouragement": assessment.ai_encouragement,
        "highlights": assessment.ai_kid_highlights or [],
    })


@csrf_exempt
@require_POST
def portal_feedback_start(request, token, set_pk):
    """Kick off (idempotently) the background grade for a submitted sheet.

    Returns immediately — grading runs off the request path (no 30s wall) and the
    page then polls ``portal_feedback_status``. Safe to call repeatedly: if the
    assessment already exists we report it ready and skip re-grading; if the
    grader isn't configured we say so, so the page can stop waiting.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return JsonResponse({"ok": False}, status=409)

    from tutor.models import MasteryAssessment

    if MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).exists():
        return JsonResponse({"ok": True, "ready": True})
    if not ai.is_configured():
        return JsonResponse({"ok": True, "ready": False, "grading": False})

    grading.start_background_grade(sheet.pk)
    return JsonResponse({"ok": True, "ready": False, "grading": True})


def portal_feedback_status(request, token, set_pk):
    """Poll for the agent's feedback. Returns the child-facing pieces once ready.

    ``ready`` flips true as soon as the background grade has saved the draft
    assessment. ``grading`` tells the page whether a grade is still expected (the
    grader is configured) so it knows to keep waiting vs. fall back gracefully.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    sheet = ResponseSheet.objects.filter(question_set=question_set, child=student).first()
    if sheet is None or not sheet.is_submitted:
        return JsonResponse({"ready": False}, status=409)

    from tutor.models import MasteryAssessment

    assessment = MasteryAssessment.objects.filter(work_entry=sheet.work_entry_id).first()
    if assessment is None:
        return JsonResponse({"ready": False, "grading": ai.is_configured()})
    return JsonResponse({
        "ready": True,
        "encouragement": assessment.ai_encouragement,
        "highlights": assessment.ai_kid_highlights or [],
    })


@csrf_exempt
@require_POST
def portal_draft_feedback(request, token, set_pk):
    """Writing-coach feedback on a ROUGH draft (before the final draft).

    Token-authed like autosave. Saves the draft text first (so nothing is
    lost), asks the coach for praise + suggestions, stores them on the sheet
    (visible again on reload), and returns the kid-facing pieces. Never grades.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False}, status=400)
    if not isinstance(payload, dict):
        return JsonResponse({"ok": False}, status=400)
    qid = str(payload.get("question", ""))
    draft = payload.get("text", "")
    if not isinstance(draft, str) or len(draft.strip()) < 20:
        return JsonResponse({"ok": False, "error": "too_short"})

    question = question_set.questions.filter(pk=qid).first() if qid.isdigit() else None
    if question is None or not question.supports_draft_coach:
        return JsonResponse({"ok": False}, status=400)

    sheet = _sheet_for(student, question_set)
    if sheet.is_submitted:
        return JsonResponse({"ok": False}, status=409)

    from tutor import ai

    curriculum = question_set.lesson.chapter.curriculum
    grade = (curriculum.get_grade_level_display() if curriculum.grade_level
             else student.get_grade_level_display())
    try:
        result = ai.review_draft(
            draft=draft,
            assignment=question.prompt or question_set.intro,
            grade_level=grade,
            subject=curriculum.subject or "Writing",
        )
    except (ai.GraderNotConfigured, ai.GraderError):
        return JsonResponse({"ok": False})

    with transaction.atomic():
        locked, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if locked.is_submitted:
            return JsonResponse({"ok": False}, status=409)
        answers = dict(locked.answers or {})
        # A plain-text draft IS the answer, so persist what she asked about. A
        # paragraph question's answer is structured JSON (rough sections + final
        # draft) autosaved by its own widget — the coach's joined rough text must
        # NOT clobber it.
        if not question.is_paragraph:
            answers[qid] = draft
        feedback = dict(locked.draft_feedback or {})
        feedback[qid] = {
            "praise": result["praise"],
            "suggestions": result["suggestions"],
            "at": timezone.localtime(timezone.now()).strftime("%b %d, %I:%M %p"),
        }
        locked.answers = answers
        locked.draft_feedback = feedback
        locked.save(update_fields=["answers", "draft_feedback", "updated_at"])

    return JsonResponse({"ok": True, "praise": result["praise"],
                         "suggestions": result["suggestions"]})


@csrf_exempt
@require_POST
def portal_autosave(request, token, set_pk):
    """Autosave endpoint — merges the draft answers, returns a saved timestamp.

    CSRF-exempt by design: portal auth is the unguessable signed token in the
    URL (not an ambient cookie), so cross-site forgery has nothing to ride on,
    and exemption lets ``navigator.sendBeacon`` deliver the last-chance save.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "error": "bad payload"}, status=400)
    posted = payload.get("answers") if isinstance(payload, dict) else None
    if not isinstance(posted, dict):
        return JsonResponse({"ok": False, "error": "bad payload"}, status=400)

    question_ids = set(str(pk) for pk in question_set.questions.values_list("pk", flat=True))
    with transaction.atomic():
        sheet, _ = ResponseSheet.objects.select_for_update().get_or_create(
            question_set=question_set, child=student,
        )
        if sheet.is_submitted:
            return JsonResponse({"ok": False, "error": "already submitted"}, status=409)
        answers = dict(sheet.answers or {})
        for qid, text in posted.items():
            if str(qid) in question_ids and isinstance(text, str):
                answers[str(qid)] = text
        sheet.answers = answers
        sheet.save(update_fields=["answers", "updated_at"])

    return JsonResponse({
        "ok": True,
        "saved_at": timezone.localtime(sheet.updated_at).strftime("%I:%M %p").lstrip("0"),
        "answered": sheet.answered_count,
    })


@csrf_exempt
@require_POST
def portal_word_help(request, token, set_pk):
    """Suggest better/similar words for a word the child selected while writing.

    Token-authed like autosave. Disabled on spelling curricula. Returns only a
    small list of clean words; degrades to an empty list on any lookup failure.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    if is_spelling(question_set.lesson.chapter.curriculum.subject):
        return JsonResponse({"ok": False, "words": []})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "words": []}, status=400)
    word = str(payload.get("word", "")).strip()[:40] if isinstance(payload, dict) else ""

    from . import thesaurus

    words = thesaurus.synonyms(word, grade_level=student.get_grade_level_display())
    return JsonResponse({"ok": bool(words), "word": word, "words": words})


@csrf_exempt
@require_POST
def portal_spellcheck(request, token, set_pk):
    """Find misspelled words in the child's writing so the page can draw its own
    red squiggle + one-tap fixes. Token-authed; disabled on spelling curricula.
    Returns [{"wrong", "fixes":[...]}]; empty on any failure.
    """
    student = _resolve_student(token)
    question_set = get_object_or_404(_visible_question_sets(student), pk=set_pk)
    if is_spelling(question_set.lesson.chapter.curriculum.subject):
        return JsonResponse({"ok": False, "misspelled": []})

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (ValueError, UnicodeDecodeError):
        return JsonResponse({"ok": False, "misspelled": []}, status=400)
    text = str(payload.get("text", ""))[:4000] if isinstance(payload, dict) else ""

    from tutor import ai

    misspelled = ai.check_spelling(text, grade_level=student.get_grade_level_display())
    return JsonResponse({"ok": True, "misspelled": misspelled})

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
from django.views.decorators.http import require_GET, require_POST

from activities.models import ExternalActivity
from family_calendar import feeds as calendar_feeds
from family_calendar.models import CalendarEvent
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


def _station_ctx(learner, kind):
    """Context for the "¡Ya lo hice! ✓" control on a station page (LGA-97).

    Returns the matching stop on THIS learner's own pathway, or blanks when she has
    no such stop — the control is never rendered for a step she couldn't tick anyway,
    and `lingua_path_check` re-derives the same allow-list before writing."""
    status = lingua_services.pathway_status(learner)
    row = next((r for r in status["steps"] if r["step"].kind == kind), None)
    if row is None:
        return {"station_step_id": None, "station_done": False, "station_auto": False}
    done = row["status"] == lingua_services.PATH_COMPLETE
    # A stop the app ticked ITSELF can't be untuck by clearing a checkmark that was
    # never written — offering "undo" there is a control that visibly does nothing,
    # which is the same class of bug as the Repaso stone this work deleted.
    return {
        "station_step_id": row["step"].pk,
        "station_done": done,
        "station_auto": done and not row["checked"],
    }


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
        })  # row["title"] carries the level-resolved name
    return render(request, "portal/lingua_path.html", {
        "student": student, "token": token,
        "pathway": status["pathway"],
        "steps": steps,
        "band": learner.profile.track_profile,
        # Two timescales (LGA-100): today's count resets, the streak doesn't.
        "done": status["done"], "total": status["total"],
        "finished": status["finished"], "streak": status["streak"],
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
    band = learner.profile.track_profile
    rules = lingua_services.phonics_rules_with_audio(band=band)
    # Reuse the rules already fetched — phonics_focus takes them for this reason.
    focus = lingua_services.phonics_focus(
        learner, band=band, rules=[i["rule"] for i in rules])
    return render(request, "portal/lingua_phonics.html", {
        **_station_ctx(learner, PathwayStep.PHONICS),
        "student": student, "token": token,
        "rules": rules,
        # One sound to actually work on today; the rest stay below. A wall of eight
        # rules is a wall a 9-year-old works on none of.
        "focus_pattern": focus.pattern if focus else "",
        "focus_title": focus.title if focus else "",
    })


def lingua_listen(request, token):
    """Spanish listening track (F-02/N-02, LGA-55/57/86): curated YouTube plus
    in-app alphabet chart and tutor practice phrases. Listening minutes feed the
    same 'minutes of input' hero metric as reading. Provisions the learner on entry."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    band = learner.profile.track_profile
    return render(request, "portal/lingua_listen.html", {
        **_station_ctx(learner, PathwayStep.LISTEN),
        "student": student, "token": token,
        # Three to choose from, unseen first (LGA-102), plus the channels, which
        # never rotate out and so are never an empty page.
        "choices": lingua_services.listening_choices(learner),
        "shelves": lingua_services.listening_shelves(band),
        "alphabet": lingua_services.alphabet_tiles_with_audio(),
        "phrases": lingua_services.practice_phrases_for(student.pk),
        "totals": lingua_services.reading_totals(learner),
        "logged": request.GET.get("logged"),
    })


def lingua_tutor(request, token):
    """Con el maestro (LGA-85): list of tutor homework packets visible to this child."""
    student = _resolve_student(token)
    _lingua_learner(student)  # provisions on first entry; the return value is unused
    packets = lingua_services.tutor_packets_for(student.pk)
    return render(request, "portal/lingua_tutor.html", {
        "student": student, "token": token, "packets": packets,
    })


def lingua_tutor_packet(request, token, packet_id):
    """One tutor packet: download handout + practice phrases (LGA-85)."""
    student = _resolve_student(token)
    _lingua_learner(student)  # provisions on first entry; the return value is unused
    packet = lingua_services.tutor_packet_for(student.pk, packet_id)
    if packet is None:
        raise Http404("Packet not found.")
    phrases = [
        p for p in lingua_services.practice_phrases_for(student.pk)
        if p["packet_id"] == packet.pk
    ]
    return render(request, "portal/lingua_tutor_packet.html", {
        "student": student, "token": token, "packet": packet, "phrases": phrases,
    })


def _listening_resource_for(learner, raw_id):
    """Resolve a posted resource id, scoped to THIS learner's band.

    Scoped, not just `active=True`: without the band filter a posted id from the
    other child's band logs against it and pollutes her rotation — a sibling with
    the portal link open is the realistic way that happens, not an attacker.
    Returns None for junk, which the callers already treat as "no resource".
    """
    try:
        pk = int(raw_id)
    except (TypeError, ValueError):
        return None
    return lingua_services.ListeningResource.objects.filter(
        pk=pk, active=True, age_band=learner.profile.track_profile).first()


def lingua_listen_open(request, token, resource_id):
    """She opened this video — record the pick, then send her to YouTube (LGA-102).

    The pick is what stops a video she watched but never logged from coming back
    tomorrow as if it were new. It does NOT tick the Camino stone and adds no
    minutes: opening is not listening, and leaving the stone unearned is what
    gives her a reason to come back and press "Anotar".

    A GET that writes, deliberately: keeping it an anchor preserves the new-tab
    open with rel="noopener", which a form POST targeting _blank would not. The
    write is an idempotent-in-spirit "she looked at this" marker in a tokenless
    single-family portal, so the usual objection (a crawler firing it) costs
    nothing worse than one video moving down her queue.
    """
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    resource = _listening_resource_for(learner, resource_id)
    if resource is None:
        raise Http404("No such listening resource for this learner.")
    lingua_services.record_listening_pick(learner, resource)
    return redirect(resource.url)


@csrf_exempt
@require_POST
def lingua_listen_log(request, token):
    """Log a listening check-in (minutes of input, LGA-55/57). Tokenless like the other
    portal writes. Minutes are clamped in the service; an unknown/blank resource still
    logs the minutes (resource is optional). Redirects back to the listening page."""
    student = _resolve_student(token)
    learner = _lingua_learner(student)
    resource = _listening_resource_for(learner, request.POST.get("resource_id"))
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
    """Active placements only — deactivated subjects leave the kid portal (HH-149)."""
    return list(
        student.placements.filter(is_active=True, curriculum__is_active=True)
        .values_list("curriculum_id", flat=True)
    )


def _visible_materials(student):
    """Approved materials this child may open.

    Work pinned to THIS child stays visible even with no active placement in its
    curriculum — that's how the manga lessons are assigned, and requiring a placement
    made them vanish along with their bookmarked links. Deactivation (HH-149) applies
    to the shared branch, which is the one a parent shelves.
    """
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        Material.objects.filter(status=Material.APPROVED)
        .filter(
            # `child=student` is an exact FK match — this is the ONLY branch that
            # bypasses the placement check, and it must never widen. Dropping the
            # child predicate here exposes every sibling's and every other family's
            # pinned work across nine endpoints; there is a test for exactly that.
            Q(child=student, lesson__chapter__curriculum__is_active=True)
            | Q(child__isnull=True, lesson__chapter__curriculum_id__in=curriculum_ids)
        )
        .select_related("lesson", "lesson__chapter")
        .order_by("lesson__chapter__number", "lesson__order")
    )


def _visible_question_sets(student):
    """Approved STUDENT-form question sets this child may open.

    Teacher-led discussion sets are intentionally excluded — those are for the
    parent to lead orally, not for the child to fill out.

    Shelving a child's PLACEMENT (HH-149) hides the shared work in that curriculum but
    leaves the child's own pinned work reachable by link; retiring the whole
    CURRICULUM hides both, which is what its is_active flag promises. This is the
    authorization gate for nine endpoints — see the note in _visible_materials.
    """
    curriculum_ids = _placed_curriculum_ids(student)
    return (
        QuestionSet.objects.filter(status=QuestionSet.APPROVED, mode=QuestionSet.MODE_STUDENT)
        .filter(
            Q(child=student, lesson__chapter__curriculum__is_active=True)
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


def _visible_calendar_events(student):
    """Calendar events this child may see: theirs + whole-family. Never a
    sibling's — same shape as _visible_activities, including the null-family
    fallback that pins whole-family events to the owning parent."""
    qs = CalendarEvent.objects.all()
    if student.family_id:
        return qs.filter(Q(child=student) | Q(child__isnull=True, family=student.family))
    return qs.filter(
        Q(child=student)
        | Q(child__isnull=True, family__isnull=True, parent=student.parent)
    )


def _student_color(student):
    """The child's event color — same palette position as the parent calendar."""
    from students.models import Student

    if student.family_id:
        siblings = list(Student.objects.filter(family=student.family))
    else:
        siblings = list(Student.objects.filter(parent=student.parent, family__isnull=True))
    return calendar_feeds.child_color_map(siblings).get(
        student.pk, calendar_feeds.CHILD_PALETTE[0])


def _paced_placements(student):
    return (
        CurriculumPlacement.objects
        .filter(child=student, is_active=True, weekly_pace__isnull=False,
                curriculum__is_active=True)
        .select_related("curriculum")
    )


def portal_calendar(request, token):
    """The kid's read-only calendar: countdown chips and a Today/This-week agenda
    strip up top, the full FullCalendar grid below."""
    from datetime import timedelta

    from curricula.pacing import next_due

    student = _resolve_student(token)
    today = timezone.localdate()
    events = list(_visible_calendar_events(student).select_related("activity"))
    pace_window = (today, today + timedelta(days=56))
    breaks = calendar_feeds.break_dates(events, pace_window, child=student)

    # Countdown chips: the next projected mission per paced subject.
    from curricula.models import Lesson

    chips = []
    for placement in _paced_placements(student):
        due = next_due(placement, today, skip_dates=breaks)
        if due is None:
            continue
        lesson = Lesson.objects.filter(pk=due[0]).first()
        if lesson is None:
            continue
        days = (due[1] - today).days
        chips.append({
            "lesson": lesson,
            "curriculum": placement.curriculum,
            "due": due[1],
            "days": days,
            "when": "due today" if days == 0 else (
                "due tomorrow" if days == 1 else f"due in {days} days"),
        })
    chips.sort(key=lambda c: c["days"])

    # Server-rendered agenda: today's plan plus the coming week, grouped by day.
    # Weekdays include the daily 📖 Español habit so the day's plan is complete.
    from types import SimpleNamespace

    week = []
    for offset in range(7):
        day = today + timedelta(days=offset)
        items = []
        for event in events:
            if event.event_type == CalendarEvent.TYPE_BREAK:
                continue
            if day in event.occurrences(day, day):
                items.append(event)
        items.sort(key=lambda e: (e.start_time is None, e.start_time or timezone.datetime.min.time()))
        if day.weekday() < 5:
            items.append(SimpleNamespace(
                emoji="📖", title="Español", start_time=None, location=""))
        if items:
            week.append({"day": day, "is_today": offset == 0, "items": items})

    return render(request, "portal/portal_calendar.html", {
        "student": student,
        "token": token,
        "week": week,
        "today": today,
        "chips": chips,
    })


@require_GET
def portal_calendar_feed(request, token):
    """FullCalendar JSON feed for ONE child — token-authed, read-only. Mission
    due-date links go to the kid's own subject page (token-carrying), never a
    parent URL."""
    from datetime import timedelta

    student = _resolve_student(token)
    window = calendar_feeds.parse_window(request)
    events = list(_visible_calendar_events(student).select_related("activity"))
    colors = {student.pk: _student_color(student)}
    payload = calendar_feeds.event_layer(events, window, colors)

    today = timezone.localdate()
    pace_window = (today, today + timedelta(days=56))
    breaks = calendar_feeds.break_dates(events, pace_window, child=student)
    payload += calendar_feeds.mission_layer(
        _paced_placements(student), window, colors, breaks=breaks,
        url_for=lambda p, l: reverse(
            "portal:portal_subject",
            kwargs={"token": token, "curriculum_id": p.curriculum_id}),
    )
    # Her own ✓ history (a garden of done days) + the whole family's birthdays
    # + the daily 📖 Español habit linking straight into her Camino.
    from students.models import Student

    payload += calendar_feeds.history_layer([student], window, named=False)
    if student.family_id:
        family_kids = Student.objects.filter(family=student.family)
    else:
        family_kids = Student.objects.filter(parent=student.parent, family__isnull=True)
    payload += calendar_feeds.birthday_layer(family_kids, window)
    payload += calendar_feeds.spanish_layer(
        [student], window,
        url_for=lambda c: reverse("portal:lingua_plan", kwargs={"token": token}),
    )
    return JsonResponse(payload, safe=False)


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
        for p in CurriculumPlacement.objects.filter(
            child=student, is_active=True, curriculum__is_active=True,
        ).select_related(
            "curriculum", "current_lesson", "current_lesson__chapter",
        )
    }

    cards = []
    for cid, placement in placements.items():
        curriculum = placement.curriculum
        curr_sets = sets_by_curr.get(cid, [])
        sets_total = len(curr_sets)
        sets_done = sum(1 for qs in curr_sets if _set_is_done(qs))
        cards.append({
            "curriculum": curriculum,
            "emoji": emoji_for(curriculum.subject),
            "placement": placement,
            "progress": placement.progress(),
            "current_lesson": placement.current_lesson,
            "next_set": next((qs for qs in curr_sets if not _set_is_done(qs)), None),
            "sets_done": sets_done,
            "sets_total": sets_total,
            "sets_pct": round(sets_done / sets_total * 100) if sets_total else 0,
            "materials_count": len(materials_by_curr.get(cid, [])),
            # Online subjects (Beast Academy, DIVE…) launch out to the website.
            "is_external": curriculum.is_external,
            "launch_url": curriculum.website_url if curriculum.is_external else "",
            # …unless we ALSO have lessons for it. Saxon runs on DIVE — the video,
            # the practice set and the progress tracking all live there — but the
            # explainers live here, and a card that jumps straight out to DIVE
            # would leave them unreachable. When both exist the card opens the
            # subject page, which keeps the launch-out button at the top.
            "launches_out": curriculum.is_external and not (
                sets_total or materials_by_curr.get(cid)
            ),
        })

    cards.sort(key=lambda c: (c["curriculum"].subject or "", c["curriculum"].name))
    return cards



def _spelling_card(student, today):
    """Her spelling programme, or None if a parent hasn't placed her in it.

    Imported lazily and defensively: spelling is a separate programme, and the
    portal home is the page every child lands on — it must not break because a
    sibling programme is mid-migration or switched off.
    """
    try:
        from spelling import services as spelling_services
        from spelling.models import SpellingPlacement
    except Exception:
        return None
    placement = SpellingPlacement.objects.filter(child=student, is_active=True).first()
    if placement is None:
        return None
    kind, week = spelling_services.next_activity(student, today=today)
    if week is None:
        return None
    labels = {
        "learn": "Learn", "sort": "Sort", "quiz": "Spell", "dictation": "Write",
    }
    return {
        "label": labels.get(kind, "Done"),
        "pattern": week.pattern if kind else "all done this week!",
        "week": week,
    }


def portal_home(request, token):
    """The kid's 'Today' surface: one calm card per subject, one next step each."""
    from curricula.models import Lesson
    from curricula.pacing import next_due

    student = _resolve_student(token)
    today = timezone.localdate()
    next_up = calendar_feeds.upcoming_occurrences(
        _visible_calendar_events(student), limit=1, days=7)
    # A mission due TODAY beats next week's practice on the My Week card.
    mission_today = None
    for placement in _paced_placements(student):
        due = next_due(placement, today)
        if due and due[1] == today:
            lesson = Lesson.objects.filter(pk=due[0]).first()
            if lesson:
                mission_today = lesson
                break
    return render(request, "portal/portal_home.html", {
        "student": student,
        "token": token,
        "spelling": _spelling_card(student, today),
        "subjects": _subject_cards(student),
        "activities": _visible_activities(student),
        "calendar_next": next_up[0] if next_up else None,
        "mission_today": mission_today,
        "today": today,
    })


def portal_subject(request, token, curriculum_id):
    """Drill into one subject: chapter → lesson outline with nested manga + sets (HH-148)."""
    from curricula.models import Chapter, Lesson

    student = _resolve_student(token)
    placement = (
        CurriculumPlacement.objects
        .filter(child=student, curriculum_id=curriculum_id, is_active=True,
                curriculum__is_active=True)
        .select_related("curriculum", "current_lesson", "current_lesson__chapter")
        .first()
    )
    if placement is None:
        raise Http404
    curriculum = placement.curriculum

    sets = [
        qs for qs in _annotated_question_sets(student)
        if qs.lesson.chapter.curriculum_id == curriculum_id
    ]
    materials = [
        m for m in _visible_materials(student)
        if m.lesson.chapter.curriculum_id == curriculum_id
    ]
    sets_by_lesson = defaultdict(list)
    for qs in sets:
        sets_by_lesson[qs.lesson_id].append(qs)
    materials_by_lesson = defaultdict(list)
    for m in materials:
        materials_by_lesson[m.lesson_id].append(m)

    # One resolution pass for the whole page: parent marks, submitted work, and
    # the placement floor. This is what lets a manga-only math lesson count.
    ordered_ids, resolved = placement.resolved_lesson_ids()

    next_set = next((qs for qs in sets if not _set_is_done(qs)), None)
    if next_set is not None:
        current_chapter = next_set.lesson.chapter.number
    elif placement.current_lesson:
        current_chapter = placement.current_lesson.chapter.number
    else:
        current_chapter = None

    chapters = []
    db_chapters = (
        Chapter.objects.filter(curriculum=curriculum)
        .prefetch_related("lessons")
        .order_by("number")
    )
    for chapter in db_chapters:
        lessons_out = []
        for lesson in chapter.lessons.all():
            les_mats = materials_by_lesson.get(lesson.pk, [])
            les_sets = sets_by_lesson.get(lesson.pk, [])
            if not les_mats and not les_sets:
                continue  # skip empty openers / structure-only noise
            lessons_out.append({
                "lesson": lesson,
                "is_current": (
                    placement.current_lesson_id == lesson.pk
                    or (next_set is not None and next_set.lesson_id == lesson.pk)
                ),
                "materials": les_mats,
                "sets": les_sets,
                "sets_done": sum(1 for qs in les_sets if _set_is_done(qs)),
                "sets_total": len(les_sets),
                "is_resolved": lesson.pk in resolved,
            })
        if not lessons_out:
            continue
        # Chapter counter: lessons WITH student sets count by turned-in sets (the
        # literature/mission behavior, unchanged); material-only lessons count by
        # resolution (parent mark / kid ✓) — previously they were stuck at 0
        # forever, which is how math read "0/5" after a finished chapter.
        done = total = 0
        for les in lessons_out:
            if les["sets_total"]:
                done += les["sets_done"]
                total += les["sets_total"]
            elif les["lesson"].lesson_type == Lesson.TYPE_OPENER:
                continue  # openers are never "resolved" — don't make them undone forever
            else:
                total += 1
                done += 1 if les["is_resolved"] else 0
        chapters.append({
            "pk": chapter.pk,
            "number": chapter.number,
            "title": chapter.title,
            "lessons": lessons_out,
            "done": done,
            "total": total,
            "is_current": chapter.number == current_chapter,
        })
    if chapters and not any(ch["is_current"] for ch in chapters):
        chapters[0]["is_current"] = True

    next_material = None
    if next_set is None:
        # "Continue ➜" points at the first material of an UNFINISHED lesson —
        # not the first material ever, which pinned math at manga #1 forever.
        for ch in chapters:
            for les in ch["lessons"]:
                if les["materials"] and not les["is_resolved"]:
                    next_material = les["materials"][0]
                    break
            if next_material:
                break

    return render(request, "portal/portal_subject.html", {
        "student": student,
        "token": token,
        "curriculum": curriculum,
        "emoji": emoji_for(curriculum.subject),
        "placement": placement,
        "progress": placement.progress(precomputed=(ordered_ids, resolved)),
        "current_lesson": placement.current_lesson,
        "next_set": next_set,
        "next_material": next_material,
        "chapters": chapters,
    })


def portal_material(request, token, pk):
    """Kid view of an approved material — student layers only, never the teaching
    guide. The lesson's whole workflow lives HERE: its journal/quiz sets render as
    Start/Turned-in buttons under the lesson, and a set-less lesson (manga math)
    gets an "I finished this ✓" self-mark instead."""
    from curricula.models import LessonProgress

    student = _resolve_student(token)
    material = get_object_or_404(_visible_materials(student), pk=pk)
    lesson_sets = [
        qs for qs in _annotated_question_sets(student)
        if qs.lesson_id == material.lesson_id
    ]
    # Resolve the same way the subject outline does (marks ∪ submitted work ∪
    # the placement floor) — otherwise the outline says "Finished ✓" while this
    # page still offers the finish button for the same lesson.
    curriculum_id = material.lesson.chapter.curriculum_id
    placement = CurriculumPlacement.objects.filter(
        child=student, curriculum_id=curriculum_id, is_active=True,
        curriculum__is_active=True,
    ).first()
    if placement is not None:
        _, resolved = placement.resolved_lesson_ids()
        is_resolved = material.lesson_id in resolved
    else:
        # A bookmarked material whose placement is shelved: fall back to marks.
        is_resolved = LessonProgress.objects.filter(
            child=student, lesson_id=material.lesson_id,
            status__in=(LessonProgress.COMPLETED, LessonProgress.SKIPPED),
        ).exists()
    return render(request, "portal/portal_material.html", {
        "student": student,
        "token": token,
        "material": material,
        "lesson_sets": lesson_sets,
        "is_resolved": is_resolved,
        "can_mark_done": not lesson_sets and not is_resolved,
        # The subject page 404s without an active placement, so a bookmarked
        # link from a shelved subject must go home instead of to a dead end.
        "back_url": (
            reverse("portal:portal_subject",
                    kwargs={"token": token, "curriculum_id": curriculum_id})
            if placement is not None
            else reverse("portal:portal_home", kwargs={"token": token})
        ),
        "back_label": (
            material.lesson.chapter.curriculum.name if placement is not None
            else "my portal"
        ),
    })


@require_POST
def portal_material_done(request, token, pk):
    """The kid's own "I finished this ✓" on a material whose lesson has no
    turn-in work (manga math and friends). Idempotent: a second tap, or a lesson
    the parent already marked, changes nothing. The parent's weekly checklist
    (students:student_lessons) can always override."""
    from curricula.models import LessonProgress

    student = _resolve_student(token)
    material = get_object_or_404(_visible_materials(student), pk=pk)
    has_sets = any(
        qs.lesson_id == material.lesson_id
        for qs in _visible_question_sets(student)
    )
    if not has_sets:
        LessonProgress.objects.get_or_create(
            child=student, lesson_id=material.lesson_id,
            defaults={
                "status": LessonProgress.COMPLETED,
                "note": f"{student.first_name} marked it done from the portal.",
            },
        )
    return redirect("portal:portal_material", token=token, pk=material.pk)


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

    # Mission-course journals get a themed skin: an explorer's log (parchment/map)
    # for Social Studies, a lab notebook (graph paper) for Science. Those two
    # subjects are exclusively the mission courses, so keying on subject is safe;
    # literature/writing/math sets get no skin. The log's own name (Explorer's Log /
    # History Log / Science Log / Lab Notebook) rides in the QuestionSet title.
    subject = (question_set.lesson.chapter.curriculum.subject or "").strip().lower()
    journal_theme = ""
    if question_set.mode == QuestionSet.MODE_STUDENT:
        journal_theme = {"social studies": "explorer", "science": "lab"}.get(subject, "")
    journal_label = journal_emoji = ""
    if journal_theme:
        journal_label = question_set.title.split("·")[-1].strip()
        journal_emoji = {
            "Explorer's Log": "🧭", "History Log": "📜",
            "Science Log": "🔬", "Lab Notebook": "🔬",
        }.get(journal_label, "📓")

    # Mid-log, a kid often needs to re-check a step — link the lesson's material
    # (the mission instructions) when one exists. Filter in the DB: scanning every
    # visible material would drag each one's parent teaching guide into a kid
    # request, and this page is student-layers-only.
    lesson_material = _visible_materials(student).filter(
        lesson_id=question_set.lesson_id).first()

    return render(request, "portal/portal_questions.html", {
        "student": student,
        "token": token,
        "question_set": question_set,
        "questions": questions,
        "sheet": sheet,
        "spellcheck_on": not spelling,
        "wordhelp_on": not spelling,
        "journal_theme": journal_theme,
        "journal_label": journal_label,
        "journal_emoji": journal_emoji,
        "lesson_material": lesson_material,
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

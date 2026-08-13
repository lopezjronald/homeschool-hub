"""Spelling OS surfaces.

Kid surfaces are reached by the same signed portal token the rest of the child
portal uses — no login on her device. The parent dashboard is a normal
logged-in, family-scoped page.
"""

import json

from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.permissions import viewable_queryset
from portal.tokens import student_from_token
from students.models import Student

from . import services
from .models import SpellingCard, SpellingSession, SpellingWeek


def _resolve_student(token):
    student = student_from_token(token)
    if student is None:
        raise Http404
    placement = services.placement_for(student)
    if not placement.is_active:
        raise Http404      # switched off for her: spelling isn't there at all
    return student


def home(request, token):
    """One button: today's activity. No menu for the child."""
    student = _resolve_student(token)
    today = timezone.localdate()
    kind, week = services.next_activity(student, today=today)
    if week is None:
        raise Http404
    services.ensure_cards(student, week)
    labels = dict(SpellingSession.KIND_CHOICES)
    # Build the URL here rather than composing a view name in the template.
    route = {SpellingSession.LEARN: "learn", SpellingSession.SORT: "sort",
             SpellingSession.QUIZ: "quiz", SpellingSession.DICTATION: "dictation"}
    return render(request, "spelling/home.html", {
        "token": token,
        "student": student,
        "week": week,
        "kind": kind,
        "kind_label": labels.get(kind, ""),
        "next_url": reverse(f"spelling:{route[kind]}", args=[token]) if kind else "",
        "streak": services.streak(student, today=today),
        "due_count": len(services.due_cards(student, week, today=today)),
    })


def learn(request, token):
    """Meet the pattern: the rule, then every word, tapped through once."""
    student = _resolve_student(token)
    week = SpellingWeek.objects.filter(
        number=services.placement_for(student).current_week).first()
    if week is None:
        raise Http404
    services.ensure_cards(student, week)
    return render(request, "spelling/learn.html", {
        "token": token, "student": student, "week": week,
        "words": list(week.pattern_words), "heart_words": list(week.heart_words),
    })


def quiz(request, token):
    """The core loop: hear the word, type it, fix it if it's wrong.

    The corrective retype is the part the research hangs on, so it is enforced
    client-side and the result is only recorded once per word.
    """
    student = _resolve_student(token)
    today = timezone.localdate()
    week = SpellingWeek.objects.filter(
        number=services.placement_for(student).current_week).first()
    if week is None:
        raise Http404
    services.ensure_cards(student, week)
    cards = services.due_cards(student, week, today=today)
    payload = [
        {
            "card": c.pk,
            "word": c.word.word,
            "sentence": c.word.sentence,
            "heart": c.word.is_heart,
            "tricky": c.word.tricky_part,
            # Baked speech when we have it; the client falls back to the
            # browser's own voice when we don't.
            "audio": c.word.audio_url,
            "sentence_audio": c.word.sentence_audio_url,
        }
        for c in cards
    ]
    return render(request, "spelling/quiz.html", {
        "token": token, "student": student, "week": week,
        "items_json": json.dumps(payload),
        "count": len(payload),
    })


@require_POST
def answer(request, token):
    """Record one answer and return the card's new state."""
    student = _resolve_student(token)
    try:
        data = json.loads(request.body or "{}")
        card_id = int(data["card"])
        correct = bool(data["correct"])
    except (ValueError, TypeError, KeyError):
        return JsonResponse({"error": "bad request"}, status=400)

    # Scoped to THIS child: the card id comes from the client.
    card = SpellingCard.objects.filter(pk=card_id, child=student).first()
    if card is None:
        raise Http404
    mastered = card.record(correct)
    return JsonResponse({
        "box": card.box, "mastered": mastered, "due": card.due.isoformat(),
    })


@require_POST
def finish(request, token):
    """Log a completed activity, then advance the week if the flow is done."""
    student = _resolve_student(token)
    try:
        data = json.loads(request.body or "{}")
        kind = str(data.get("kind", ""))
        asked = int(data.get("asked") or 0)
        right = int(data.get("right") or 0)
        missed = [str(w)[:40] for w in (data.get("missed") or [])][:50]
    except (ValueError, TypeError):
        return JsonResponse({"error": "bad request"}, status=400)
    if kind not in dict(SpellingSession.KIND_CHOICES):
        return JsonResponse({"error": "unknown activity"}, status=400)

    week = SpellingWeek.objects.filter(
        number=services.placement_for(student).current_week).first()
    SpellingSession.objects.create(
        child=student, week=week, kind=kind,
        asked=asked, right=right, missed_words=missed,
    )
    services.advance_if_ready(student)
    return JsonResponse({"ok": True})


def sort_words(request, token):
    """Drag each word under the column its pattern belongs to."""
    student = _resolve_student(token)
    week = SpellingWeek.objects.filter(
        number=services.placement_for(student).current_week).first()
    if week is None:
        raise Http404
    buckets = list(week.sort_buckets or [])
    words = [
        {"word": w.word, "bucket": w.sort_bucket, "heart": w.is_heart,
         "audio": w.audio_url}
        for w in week.words.all()
    ]
    return render(request, "spelling/sort.html", {
        "token": token, "student": student, "week": week,
        "buckets": buckets + ["Heart Words"],
        "items_json": json.dumps(words),
    })


def dictation(request, token):
    """Three sentences, read aloud, typed whole."""
    student = _resolve_student(token)
    week = SpellingWeek.objects.filter(
        number=services.placement_for(student).current_week).first()
    if week is None:
        raise Http404
    picks = list(week.pattern_words[:3])
    return render(request, "spelling/dictation.html", {
        "token": token, "student": student, "week": week,
        "items_json": json.dumps([
            {"word": w.word, "sentence": w.sentence,
             "audio": w.audio_url, "sentence_audio": w.sentence_audio_url}
            for w in picks
        ]),
    })


@login_required
def parent_dashboard(request, pk):
    """Under five minutes a week: where she is, what's stuck, is she showing up."""
    child = get_object_or_404(
        viewable_queryset(Student.objects.all(), request.user), pk=pk)
    today = timezone.localdate()
    placement = services.placement_for(child)
    week = SpellingWeek.objects.filter(number=placement.current_week).first()

    cards = list(
        SpellingCard.objects.filter(child=child).select_related("word", "word__week"))
    introduced = len(cards)
    strong = sum(1 for c in cards if c.box >= 4)
    trouble = sorted(
        (c for c in cards if c.is_trouble),
        key=lambda c: (-c.misses, c.word.word),
    )[:20]
    this_week = SpellingSession.objects.filter(
        child=child, on_date__gte=services.week_start(today))

    return render(request, "spelling/parent.html", {
        "child": child,
        "placement": placement,
        "week": week,
        "introduced": introduced,
        "strong": strong,
        "mastery_pct": round(strong / introduced * 100) if introduced else 0,
        "trouble": trouble,
        "sessions_this_week": this_week.count(),
        "streak": services.streak(child, today=today),
        "repeat_flagged": placement.repeat_flagged_on,
        "recent": SpellingSession.objects.filter(child=child)[:10],
    })

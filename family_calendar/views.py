"""Parent-side family calendar: the FullCalendar page, its JSON feed, and event CRUD.

Scoping mirrors activities/views.py exactly: reads via scoped_queryset on the
selected family, writes 404-gated on user_can_edit + editable_queryset.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST

from core.permissions import (
    can_edit_family_or_global, editable_queryset, scoped_queryset, user_can_edit,
)
from core.utils import get_selected_family, resolve_family_for_write
from students.models import Student

from . import feeds
from .forms import CalendarEventForm
from .models import CalendarEvent


def _scoped_events(request, family):
    return scoped_queryset(CalendarEvent.objects.all(), request.user, family)


def _scoped_children(request, family):
    return scoped_queryset(Student.objects.all(), request.user, family)


@login_required
def calendar_page(request):
    from curricula.models import CurriculumPlacement

    family = get_selected_family(request)
    children = list(_scoped_children(request, family))
    colors = feeds.child_color_map(children)
    for child in children:
        child.color = colors[child.pk]
    placements = (
        CurriculumPlacement.objects
        .filter(child__in=children, is_active=True, curriculum__is_active=True)
        .select_related("child", "curriculum")
        .order_by("child__first_name", "curriculum__name")
    )

    # LRM prep: a charter-school meeting inside the next week gets a callout
    # pointing at the charter report — walk in with the record already printed.
    from datetime import timedelta

    from django.utils import timezone

    today = timezone.localdate()
    lrm = None
    for event in _scoped_events(request, family).filter(
            event_type=CalendarEvent.TYPE_CHARTER):
        for occ in event.occurrences(today, today + timedelta(days=7)):
            if lrm is None or occ < lrm["date"]:
                lrm = {"event": event, "date": occ}

    return render(request, "family_calendar/calendar.html", {
        "children": children,
        "family_color": feeds.FAMILY_COLOR,
        "can_edit": can_edit_family_or_global(request.user, family),
        "placements": placements,
        "lrm": lrm,
        "today": today,
    })


@login_required
@require_GET
def events_feed(request):
    """FullCalendar JSON feed: event occurrences + projected mission due dates."""
    from curricula.models import CurriculumPlacement

    family = get_selected_family(request)
    window = feeds.parse_window(request)
    children = list(_scoped_children(request, family))
    colors = feeds.child_color_map(children)
    layers = set(
        (request.GET.get("layers") or "events,missions,history,birthdays").split(","))

    all_events = list(_scoped_events(request, family).select_related("activity"))
    raw_children = request.GET.get("children", "")
    shown_children = children
    events = all_events
    if raw_children:
        # Validate against the scoped children — a foreign id is silently dropped,
        # so the filter can never widen access. Whole-family events always pass.
        valid_ids = {c.pk for c in children}
        wanted = {int(v) for v in raw_children.split(",") if v.strip().isdecimal()} & valid_ids
        events = [e for e in all_events if e.child_id is None or e.child_id in wanted]
        shown_children = [c for c in children if c.pk in wanted]

    payload = []
    if "events" in layers:
        payload += feeds.event_layer(
            events, window, colors,
            url_for=lambda e: reverse("family_calendar:event_update", args=[e.pk]),
        )
    if "missions" in layers:
        from datetime import timedelta

        from django.utils import timezone

        placements = (
            CurriculumPlacement.objects
            .filter(child__in=shown_children, is_active=True,
                    weekly_pace__isnull=False, curriculum__is_active=True)
            .select_related("child", "curriculum")
        )
        by_child = {}
        for p in placements:
            by_child.setdefault(p.child_id, []).append(p)
        # Breaks must span the PACING window (today → horizon), not the display
        # window — the feed may be showing a past month while pacing runs forward.
        today = timezone.localdate()
        pace_window = (today, today + timedelta(days=56))
        for child in shown_children:
            child_placements = by_child.get(child.pk)
            if not child_placements:
                continue
            # A break tagged to another child doesn't pause this child's pacing.
            breaks = feeds.break_dates(all_events, pace_window, child=child)
            payload += feeds.mission_layer(
                child_placements, window, colors, breaks=breaks,
                label_for=lambda p, l: f"{p.child.first_name} · {l.title or l.code}",
                url_for=lambda p, l: reverse(
                    "students:student_lessons", args=[p.child_id, p.curriculum_id]),
            )
    if "history" in layers:
        payload += feeds.history_layer(shown_children, window)
    if "birthdays" in layers:
        # Birthdays ignore the child filter — nobody's birthday gets hidden.
        payload += feeds.birthday_layer(children, window)
    return JsonResponse(payload, safe=False)


@login_required
def event_create(request):
    if not user_can_edit(request.user):
        raise Http404
    family = get_selected_family(request)
    if request.method == "POST":
        form = CalendarEventForm(request.POST, user=request.user, family=family)
        if form.is_valid():
            event = form.save(commit=False)
            event.parent = request.user
            event.family = resolve_family_for_write(request)
            event.save()
            messages.success(request, "Event added to the calendar.")
            return redirect("family_calendar:calendar")
    else:
        # A click on an empty calendar day lands here with ?date=YYYY-MM-DD.
        initial = {}
        preset = feeds.safe_parse_date(request.GET.get("date"))
        if preset:
            initial["date"] = preset
        child_id = request.GET.get("child", "")
        if child_id.isdecimal():
            initial["child"] = int(child_id)
        form = CalendarEventForm(user=request.user, family=family, initial=initial)
    return render(request, "family_calendar/event_form.html", {"form": form, "action": "Add"})


@login_required
def event_update(request, pk):
    if not user_can_edit(request.user):
        raise Http404
    event = get_object_or_404(
        editable_queryset(CalendarEvent.objects.all(), request.user), pk=pk,
    )
    family = get_selected_family(request)
    if request.method == "POST":
        form = CalendarEventForm(request.POST, instance=event, user=request.user, family=family)
        if form.is_valid():
            form.save()
            messages.success(request, "Event updated.")
            return redirect("family_calendar:calendar")
    else:
        form = CalendarEventForm(instance=event, user=request.user, family=family)
    upcoming = []
    if event.repeats_weekly:
        from datetime import timedelta
        from django.utils import timezone
        today = timezone.localdate()
        upcoming = event.occurrences(today, today + timedelta(days=90))[:10]
    return render(request, "family_calendar/event_form.html", {
        "form": form, "event": event, "action": "Edit",
        "upcoming": upcoming,
        "skipped": sorted(s for s in (event.skip_dates or []) if isinstance(s, str)),
    })


@login_required
def event_delete(request, pk):
    if not user_can_edit(request.user):
        raise Http404
    event = get_object_or_404(
        editable_queryset(CalendarEvent.objects.all(), request.user), pk=pk,
    )
    if request.method == "POST":
        event.delete()
        messages.success(request, "Event removed.")
        return redirect("family_calendar:calendar")
    return render(request, "family_calendar/event_confirm_delete.html", {"event": event})


@login_required
@require_POST
def set_pace(request, placement_pk):
    """Set (or clear) a placement's weekly pace from the calendar's Pacing panel."""
    from core.permissions import viewable_queryset
    from curricula.models import Curriculum, CurriculumPlacement

    if not user_can_edit(request.user):
        raise Http404
    # Gate on the curriculum AND the child (mirrors curriculum_set_placement) so a
    # shared/global curriculum can never let an editor pace another family's kid.
    placement = get_object_or_404(
        CurriculumPlacement.objects.filter(
            curriculum__in=editable_queryset(Curriculum.objects.all(), request.user),
            child__in=viewable_queryset(Student.objects.all(), request.user),
        ).select_related("child", "curriculum"),
        pk=placement_pk,
    )
    raw = (request.POST.get("weekly_pace") or "").strip()
    if raw == "" or raw == "0":
        placement.weekly_pace = None
        placement.save(update_fields=["weekly_pace", "updated_at"])
        messages.info(request, f"{placement.curriculum.name}: due dates off for "
                               f"{placement.child.first_name}.")
    elif raw.isdecimal() and 1 <= int(raw) <= 10:
        placement.weekly_pace = int(raw)
        placement.save(update_fields=["weekly_pace", "updated_at"])
        messages.success(
            request,
            f"{placement.child.first_name} · {placement.curriculum.name}: "
            f"{raw}/week — due dates updated.",
        )
    else:
        messages.error(request, "Pace must be a number from 1 to 10 (or 0 to turn off).")
    return redirect("family_calendar:calendar")


@login_required
@require_POST
def occurrence_skip(request, pk):
    """Cancel (or restore) ONE date of a repeating event, leaving the series alone."""
    if not user_can_edit(request.user):
        raise Http404
    event = get_object_or_404(
        editable_queryset(CalendarEvent.objects.all(), request.user), pk=pk,
    )
    when = feeds.safe_parse_date(request.POST.get("date"))
    if when is None:
        messages.error(request, "That date didn't make sense — nothing changed.")
        return redirect("family_calendar:event_update", pk=event.pk)
    iso = when.isoformat()
    skips = [s for s in (event.skip_dates or []) if isinstance(s, str)]
    if request.POST.get("action") == "restore":
        skips = [s for s in skips if s != iso]
        messages.success(request, f"Restored {event.title} on {when.strftime('%b %d')}.")
    elif iso not in skips:
        skips.append(iso)
        messages.success(
            request,
            f"Cancelled {event.title} on {when.strftime('%b %d')} — the rest of the "
            f"series is unchanged.",
        )
    event.skip_dates = sorted(skips)
    event.save(update_fields=["skip_dates", "updated_at"])
    return redirect("family_calendar:event_update", pk=event.pk)

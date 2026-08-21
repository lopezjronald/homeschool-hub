from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST

from core.forms import FamilyForm, InviteSignupForm, TeacherInviteForm
from core.models import FamilyMembership, Invitation
from core.permissions import can_edit_family
from core.utils import get_active_family, get_selected_family

# Friendly label for an invitation role. Two grantable roles; the retired ones
# keep an entry so an invitation sent before the change still reads sensibly.
_ROLE_LABELS = {
    "parent": "parent",
    "teacher": "teacher or guardian",
    "admin": "admin",
    "guardian": "teacher or guardian",
    "grandparent": "teacher or guardian",
}


def _role_label(role):
    return _ROLE_LABELS.get(role, role)


def _send_invite_email(invite, request):
    """Send (or resend) the invitation email for a given Invitation."""
    accept_path = reverse("core:accept_invite", kwargs={"invite_id": invite.id})
    accept_url = request.build_absolute_uri(accept_path)
    max_age = getattr(settings, "INVITE_MAX_AGE_DAYS", 7)
    inviter = request.user.get_full_name() or request.user.username
    role_label = _role_label(invite.role)

    send_mail(
        subject=f"You're invited to join {invite.family.name} on Steadfast Scholars",
        message=(
            f"Hi,\n\n"
            f"{inviter} has invited you to join "
            f"{invite.family.name} as a {role_label} on Steadfast Scholars.\n\n"
            f"Open the link below to accept — you can create your account there if "
            f"you don't have one yet:\n"
            f"{accept_url}\n\n"
            f"This invitation expires in {max_age} days.\n\n"
            f"-- Steadfast Scholars"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
        fail_silently=False,
    )


def how_it_works(request):
    """The 'How it works' guide — what the app does, how to use it, and why.

    Open to anyone (it doubles as an overview for prospective and brand-new
    users); linked prominently in-app for signed-in parents and teachers.
    """
    return render(request, "core/how_it_works.html", {})


@login_required
def family_settings(request):
    """Rename the household (editors only). Members are managed on the invite page.

    Operates on the family SELECTED in the navbar switcher (not the user's primary
    family), so a parent of 2+ families renames the household they're actually looking
    at — gated by edit permission on that family."""
    family = get_selected_family(request)
    if family is None or not can_edit_family(request.user, family):
        raise Http404

    if request.method == "POST":
        form = FamilyForm(request.POST, instance=family)
        if form.is_valid():
            form.save()
            messages.success(request, "Family name updated.")
            return redirect("core:family_settings")
    else:
        form = FamilyForm(instance=family)
    return render(request, "core/family_settings.html", {"form": form, "family": family})


@login_required
def invite_teacher(request):
    """Invite someone (co-parent, guardian, grandparent, teacher) to the SELECTED
    family — the one shown in the navbar switcher — gated by edit permission, so a
    multi-family parent never invites into the wrong household."""
    family = get_selected_family(request)
    if family is None:
        if FamilyMembership.objects.filter(user=request.user).exists():
            raise Http404
        return render(request, "core/invite_teacher.html", {"no_family": True})
    if not can_edit_family(request.user, family):
        raise Http404  # a view-only member of the selected family can't invite

    if request.method == "POST":
        form = TeacherInviteForm(request.POST, family=family)
        if form.is_valid():
            invite = Invitation.objects.create(
                email=form.cleaned_data["email"],
                family=family,
                invited_by=request.user,
                role=form.cleaned_data["role"],
            )
            _send_invite_email(invite, request)
            messages.success(request, f"Invitation ready for {form.cleaned_data['email']}.")
            return redirect("core:invite_teacher")
    else:
        form = TeacherInviteForm(family=family)

    pending_invites = Invitation.objects.filter(family=family, status=Invitation.PENDING)
    primary = _primary_parent_membership(family)
    memberships = list(
        family.memberships.select_related("user").order_by("role", "created_at", "id")
    )
    for m in memberships:
        m.is_primary = primary is not None and m.pk == primary.pk
        m.is_self = m.user_id == request.user.id
    return render(request, "core/invite_teacher.html", {
        "form": form,
        "family": family,
        "pending_invites": pending_invites,
        "memberships": memberships,
    })


def _primary_parent_membership(family):
    """The family's primary parent — the earliest parent-role member.

    Serves as the protected owner: the primary parent can't be removed, so a
    family can never be left with no one in charge.
    """
    return family.memberships.filter(role="parent").order_by("created_at", "id").first()


@login_required
@require_POST
def remove_member(request, membership_id):
    """Parent-only: remove a member from the SELECTED family (never the primary parent)."""
    family = get_selected_family(request)
    if family is None or not can_edit_family(request.user, family):
        raise Http404  # must be an editor of the selected family

    membership = get_object_or_404(FamilyMembership, pk=membership_id, family=family)
    primary = _primary_parent_membership(family)
    if primary is not None and membership.pk == primary.pk:
        messages.warning(request, "The primary parent can't be removed from the family.")
        return redirect("core:invite_teacher")

    who = membership.user.get_full_name() or membership.user.username
    membership.delete()
    if membership.user_id == request.user.id:
        messages.success(request, f"You've left {family.name}.")
    else:
        messages.success(request, f"Removed {who} from {family.name}.")
    return redirect("core:invite_teacher")


@login_required
def resend_invite(request, invite_id):
    """Resend a pending invitation email (editors of the SELECTED family, POST-only)."""
    family = get_selected_family(request)
    if family is None or not can_edit_family(request.user, family):
        raise Http404

    invite = get_object_or_404(Invitation, pk=invite_id, family=family)

    if request.method != "POST":
        return redirect("core:invite_teacher")

    if not invite.is_resendable:
        if invite.status == Invitation.ACCEPTED:
            messages.info(request, "This invitation has already been accepted.")
        elif invite.is_expired:
            messages.warning(request, "This invitation has expired. Please send a new one.")
        else:
            messages.warning(request, "This invitation can no longer be resent.")
        return redirect("core:invite_teacher")

    _send_invite_email(invite, request)
    invite.resent_at = timezone.now()
    invite.save(update_fields=["resent_at"])
    messages.success(request, f"Invitation resent to {invite.email}.")
    return redirect("core:invite_teacher")


def _finalize_acceptance(user, invite):
    """Create the membership and mark the invitation accepted."""
    FamilyMembership.objects.get_or_create(
        user=user, family=invite.family, defaults={"role": invite.role},
    )
    invite.status = Invitation.ACCEPTED
    invite.accepted_at = timezone.now()
    invite.save(update_fields=["status", "accepted_at"])


def accept_invite(request, invite_id):
    """Accept an invitation. New users can create an account on the spot."""
    invite = get_object_or_404(Invitation, pk=invite_id)

    if invite.status == Invitation.ACCEPTED:
        return render(request, "core/invite_accept_result.html", {
            "error": "This invitation has already been accepted.",
        })
    if invite.is_expired:
        if invite.status == Invitation.PENDING:
            invite.status = Invitation.EXPIRED
            invite.save(update_fields=["status"])
        return render(request, "core/invite_accept_result.html", {
            "error": "This invitation has expired. Please ask for a new invitation.",
        })
    if invite.status != Invitation.PENDING:
        return render(request, "core/invite_accept_result.html", {
            "error": "This invitation is no longer valid.",
        })

    role_label = _role_label(invite.role)

    # Signed-in users join directly.
    if request.user.is_authenticated:
        _finalize_acceptance(request.user, invite)
        messages.success(
            request, f"Welcome! You've joined {invite.family.name} as a {role_label}.",
        )
        return redirect("dashboard:dashboard")

    # Anonymous users create an account via the link.
    if request.method == "POST":
        form = InviteSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            _finalize_acceptance(user, invite)
            messages.success(
                request,
                f"Welcome! Your account is ready and you've joined "
                f"{invite.family.name} as a {role_label}.",
            )
            return redirect("dashboard:dashboard")
    else:
        form = InviteSignupForm(initial={"email": invite.email})

    return render(request, "core/invite_signup.html", {
        "form": form,
        "invite": invite,
        "role_label": role_label,
    })


# ---------------------------------------------------------------------------
# Handoff — telling the other household what the girls finished.
# ---------------------------------------------------------------------------

def _handoff_window(request, family):
    """The stretch a handoff covers, from the querystring or the default.

    A date the parent typed means the WHOLE of that day, so `until` runs to the
    end of it — picking today and being told today's work is missing would be a
    small daily lie.
    """
    from datetime import datetime, time

    from core import handoff as handoff_lib

    def _day(name):
        raw = (request.GET.get(name) or "").strip()
        if not raw:
            return None
        try:
            return datetime.strptime(raw, "%Y-%m-%d").date()
        except ValueError:
            return None

    start, end = _day("since"), _day("until")
    # Swap the DATES, not the moments. Swapping after the times are applied
    # turns the pair into (end-of-day, start-of-day) — a window that excludes
    # the whole of both days the parent named, while the page cheerfully prints
    # those two dates above it.
    if start and end and start > end:
        start, end = end, start
    since = (timezone.make_aware(datetime.combine(start, time.min))
             if start else handoff_lib.default_since(family))
    until = (timezone.make_aware(datetime.combine(end, time.max))
             if end else timezone.now())
    if since > until:
        since, until = until, since       # one side defaulted; read it their way
    return since, until


@login_required
def handoff_new(request):
    """Compose a handoff. Nothing leaves until a person presses send.

    Edit access only: this discloses the children's school records outside the
    app, which is not something a view-only teacher or guardian should be able
    to do on the household's behalf.
    """
    from core import handoff as handoff_lib
    from core.models import Handoff, HandoffRecipient
    from students.models import Student

    family = get_selected_family(request) or get_active_family(request.user)
    if family is None or not can_edit_family(request.user, family):
        raise Http404

    # The window is pickable. It defaults to "since the last handoff", which is
    # right most weeks — but a handover that slipped, or a first one covering a
    # whole term, needs a different range and should not need a database to get
    # one. Dates, not datetimes: nobody hands over at 14:32.
    since, until = _handoff_window(request, family)
    children = list(Student.objects.filter(family=family).order_by("first_name"))
    summaries = [handoff_lib.summarise(child, since, until) for child in children]

    return render(request, "core/handoff_new.html", {
        "family": family,
        "since": since,
        "until": until,
        "since_date": timezone.localtime(since).date().isoformat(),
        "until_date": timezone.localtime(until).date().isoformat(),
        "window_is_default": not (request.GET.get("since") or request.GET.get("until")),
        "summaries": [s for s in summaries if s.has_anything],
        "nothing_found": not any(s.has_anything for s in summaries),
        "recipients": HandoffRecipient.objects.filter(family=family, is_active=True),
        "previous": Handoff.objects.filter(family=family).exclude(sent_at=None)[:5],
    })


@login_required
@require_POST
def handoff_preview(request):
    """Build the exact message, from exactly what was ticked.

    A separate step on purpose. Nobody should be able to send a message they
    have not read, and rebuilding from the ticked keys — rather than from the
    whole window again — is what makes the preview the SAME text that sends.
    """
    from core import handoff as handoff_lib
    from core.models import Handoff
    from django.utils.dateparse import parse_datetime
    from students.models import Student

    family = get_selected_family(request) or get_active_family(request.user)
    if family is None or not can_edit_family(request.user, family):
        raise Http404

    # parse_datetime RAISES on well-formed-but-impossible dates ("2026-02-30"),
    # where it merely returns None for garbage. Both are user-controlled, and
    # neither should be a 500 on the page a parent is mid-handover on.
    def _when(field, fallback):
        try:
            return parse_datetime(request.POST.get(field, "")) or fallback
        except ValueError:
            return fallback

    since = _when("since", handoff_lib.default_since(family))
    until = _when("until", timezone.now())
    keep = set(request.POST.getlist("include"))
    note = request.POST.get("note", "")

    summaries = []
    for child in Student.objects.filter(family=family).order_by("first_name"):
        summary = handoff_lib.summarise(child, since, until)
        for subject in summary.subjects:
            subject.items = [i for i in subject.items if i.key in keep]
        summary.subjects = [s for s in summary.subjects if s.items]
        if summary.has_anything:
            summaries.append(summary)

    body = handoff_lib.compose(summaries, note=note, author=request.user)
    draft = Handoff.objects.create(
        family=family, created_by=request.user,
        covers_since=since, covers_until=until, note=note, body=body,
    )
    return render(request, "core/handoff_preview.html", {
        "family": family,
        "draft": draft,
        "recipients": family.handoff_recipients.filter(is_active=True),
    })


@login_required
@require_POST
def handoff_send(request, pk):
    """Email the draft, or record that it was copied for a text.

    Copying is NOT sending, and the record says which — a log that claims a
    message went out when it was only put on a clipboard is worse than no log.
    """
    from core.models import Handoff, HandoffRecipient

    draft = get_object_or_404(Handoff, pk=pk)
    if not can_edit_family(request.user, draft.family):
        raise Http404
    if draft.sent_at:
        messages.info(request, "That handoff has already been sent.")
        return redirect("core:handoff_new")

    if request.POST.get("how") == "copied":
        draft.copied_at = timezone.now()
        draft.status = Handoff.SENT
        draft.sent_to = "copied for texting"
        draft.save(update_fields=["copied_at", "status", "sent_to"])
        messages.success(request, "Copied. The next handoff will start from here.")
        return redirect("core:handoff_new")

    chosen = HandoffRecipient.objects.filter(
        pk__in=request.POST.getlist("recipient"), family=draft.family, is_active=True,
    ).exclude(email="")
    emails = [r.email for r in chosen]
    if not emails:
        messages.error(request, "Choose at least one person with an email address.")
        return redirect("core:handoff_new")

    send_mail(
        subject="School update — %s" % timezone.localtime(draft.covers_until).strftime("%d %b"),
        message=draft.body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        recipient_list=emails,
        fail_silently=False,
    )
    draft.sent_at = timezone.now()
    draft.status = Handoff.SENT
    draft.sent_to = ", ".join(emails)
    draft.save(update_fields=["sent_at", "status", "sent_to"])
    messages.success(request, "Sent to %s." % ", ".join(r.name for r in chosen))
    return redirect("core:handoff_new")


@login_required
def handoff_recipients(request):
    """Who a handoff can go to. Managed here so the preview can promise it.

    The preview page told parents to "add the other parent under Family
    settings" — a control that did not exist, which made the email half of the
    feature impossible to use rather than merely awkward.
    """
    from core.forms import HandoffRecipientForm
    from core.models import HandoffRecipient

    family = get_selected_family(request) or get_active_family(request.user)
    if family is None or not can_edit_family(request.user, family):
        raise Http404

    form = HandoffRecipientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        recipient = form.save(commit=False)
        recipient.family = family
        recipient.save()
        messages.success(request, f"{recipient.name} can now be sent handoffs.")
        return redirect("core:handoff_recipients")

    return render(request, "core/handoff_recipients.html", {
        "family": family,
        "form": form,
        "recipients": HandoffRecipient.objects.filter(family=family),
    })


@login_required
@require_POST
def handoff_recipient_remove(request, pk):
    """Stop sending to someone. Deactivated, not deleted — a handoff already
    sent should keep saying who it went to."""
    from core.models import HandoffRecipient

    recipient = get_object_or_404(HandoffRecipient, pk=pk)
    if not can_edit_family(request.user, recipient.family):
        raise Http404
    recipient.is_active = False
    recipient.save(update_fields=["is_active"])
    messages.success(request, f"{recipient.name} won't be offered any more.")
    return redirect("core:handoff_recipients")

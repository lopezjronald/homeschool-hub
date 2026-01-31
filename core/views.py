from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from core.forms import TeacherInviteForm
from core.models import FamilyMembership, Invitation
from core.utils import get_active_family


def _send_invite_email(invite, request):
    """Send (or resend) the invitation email for a given Invitation."""
    accept_path = reverse(
        "core:accept_invite", kwargs={"invite_id": invite.id},
    )
    accept_url = request.build_absolute_uri(accept_path)
    max_age = getattr(settings, "INVITE_MAX_AGE_DAYS", 7)
    inviter = request.user.get_full_name() or request.user.username

    send_mail(
        subject=f"You're invited to join {invite.family.name} on Steadfast Scholars",
        message=(
            f"Hi,\n\n"
            f"{inviter} has invited you to join "
            f"{invite.family.name} as a teacher on Steadfast Scholars.\n\n"
            f"Click the link below to accept:\n"
            f"{accept_url}\n\n"
            f"This invitation expires in {max_age} days.\n\n"
            f"-- Steadfast Scholars"
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
        fail_silently=False,
    )


@login_required
def invite_teacher(request):
    """Parent-only view to invite a teacher to their active family."""
    family = get_active_family(request.user)
    if family is None:
        # User has memberships but none with parent role → 404
        if FamilyMembership.objects.filter(user=request.user).exists():
            raise Http404
        # User has no memberships at all → helpful message
        return render(request, "core/invite_teacher.html", {"no_family": True})

    if request.method == "POST":
        form = TeacherInviteForm(request.POST, family=family)
        if form.is_valid():
            invite = Invitation.objects.create(
                email=form.cleaned_data["email"],
                family=family,
                invited_by=request.user,
                role="teacher",
            )
            _send_invite_email(invite, request)
            messages.success(
                request,
                f"Invitation sent to {form.cleaned_data['email']}.",
            )
            return redirect("core:invite_teacher")
    else:
        form = TeacherInviteForm(family=family)

    pending_invites = Invitation.objects.filter(
        family=family, status=Invitation.PENDING,
    )
    return render(request, "core/invite_teacher.html", {
        "form": form,
        "family": family,
        "pending_invites": pending_invites,
    })


@login_required
def resend_invite(request, invite_id):
    """Resend a pending invitation email (parent-only, POST-only)."""
    family = get_active_family(request.user)
    if family is None:
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


@login_required
def accept_invite(request, invite_id):
    """Accept a teacher invitation and join the family."""
    invite = get_object_or_404(Invitation, pk=invite_id)

    # Already accepted
    if invite.status == Invitation.ACCEPTED:
        return render(request, "core/invite_accept_result.html", {
            "error": "This invitation has already been accepted.",
        })

    # Expired
    if invite.is_expired:
        if invite.status == Invitation.PENDING:
            invite.status = Invitation.EXPIRED
            invite.save(update_fields=["status"])
        return render(request, "core/invite_accept_result.html", {
            "error": "This invitation has expired. Please ask for a new invitation.",
        })

    # Not pending (e.g. manually expired)
    if invite.status != Invitation.PENDING:
        return render(request, "core/invite_accept_result.html", {
            "error": "This invitation is no longer valid.",
        })

    # Accept: create membership (idempotent via get_or_create)
    FamilyMembership.objects.get_or_create(
        user=request.user,
        family=invite.family,
        defaults={"role": invite.role},
    )
    invite.status = Invitation.ACCEPTED
    invite.accepted_at = timezone.now()
    invite.save(update_fields=["status", "accepted_at"])

    messages.success(
        request,
        f"Welcome! You've joined {invite.family.name} as a "
        f"{invite.role}.",
    )
    return redirect("dashboard:dashboard")

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

from core.forms import InviteSignupForm, TeacherInviteForm
from core.models import FamilyMembership, Invitation
from core.utils import get_active_family

# Friendly label for an invitation role (co-parent stores as "parent").
_ROLE_LABELS = {
    "parent": "co-parent",
    "guardian": "guardian",
    "grandparent": "grandparent",
    "teacher": "teacher",
    "admin": "admin",
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


@login_required
def invite_teacher(request):
    """Parent-only view to invite someone (co-parent, guardian, grandparent, teacher)."""
    family = get_active_family(request.user)
    if family is None:
        if FamilyMembership.objects.filter(user=request.user).exists():
            raise Http404
        return render(request, "core/invite_teacher.html", {"no_family": True})

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
    """Parent-only: remove a member from the active family (never the primary parent)."""
    family = get_active_family(request.user)
    if family is None:
        raise Http404  # only a parent-role user has an active family here

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

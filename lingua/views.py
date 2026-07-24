"""lingua views. Parent-facing pages extend the host base.html (so NOT @lingua_csp
— that strict policy is reserved for the CSP-clean kid reader). Editors-only views
raise Http404 for non-editors, matching the rest of the app (tutor/views.py)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from core.permissions import user_can_edit

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

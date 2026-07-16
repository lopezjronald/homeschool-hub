from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from accounts.models import UserProfile
from core.services import get_inbox_buckets
from core.utils import get_selected_family


@login_required
def inbox_view(request):
    """The parent action inbox — everything needing me, in one place.

    Renders the buckets (their "new since last visit" flags are computed against
    the pre-visit ``inbox_seen_at``), then stamps ``inbox_seen_at`` to now so the
    nav badge's "new" indicator clears for next time.
    """
    family = get_selected_family(request)
    inbox = get_inbox_buckets(request, family)

    profile = UserProfile.get_for(request.user)
    profile.inbox_seen_at = timezone.now()
    profile.save(update_fields=["inbox_seen_at"])

    return render(request, "inbox/inbox.html", {"inbox": inbox})

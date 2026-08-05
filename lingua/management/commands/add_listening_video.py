"""Add curated listening videos by pasting their links (LGA-102).

Curating the rotation pool should not mean editing Python. Paste one or more
YouTube URLs and this fills in the title and channel for you, classifies video vs
channel, and refuses anything it cannot confirm.

    python manage.py add_listening_video --band KIDS_OLDER --level L1 \\
        https://www.youtube.com/watch?v=AAAAAAAAAAA \\
        https://youtu.be/BBBBBBBBBBB

    python manage.py add_listening_video --band KIDS_EARLY --title "Los colores" \\
        --minutes 4 https://www.youtube.com/watch?v=CCCCCCCCCCC

Verification uses YouTube's public oEmbed endpoint, which returns the real title
and channel — so a mistyped id, or a link that is secretly a different channel,
is caught before a child ever sees it. TWO REAL TRAPS this caught while the
feature was being built: a search result for "123 Andrés" that was actually the
unrelated channel "123 Kids Fun España", and two links that were already dead.

Some good channels turn embedding OFF (Dreaming Spanish is one), and oEmbed
answers 401 for those. That is NOT evidence the link is bad — the link still
opens fine, and this page only ever links out. Those need ``--force`` plus a
``--title`` you supply yourself, so the guess is yours and is recorded as such.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand, CommandError

from lingua import profiles
from lingua.listening import VIDEO, classify_url
from lingua.models import ListeningResource

OEMBED = "https://www.youtube.com/oembed"


def lookup(url):
    """(title, channel) from YouTube, or (None, reason)."""
    query = urllib.parse.urlencode({"url": url, "format": "json"})
    try:
        with urllib.request.urlopen(f"{OEMBED}?{query}", timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("title"), data.get("author_name")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None, "no such video — deleted, or the id is mistyped"
        return None, (f"HTTP {exc.code} — embedding is off for this one, so the title "
                      f"cannot be confirmed here (the link itself may be perfectly fine)")
    except Exception as exc:                      # noqa: BLE001 — report, never crash
        return None, f"could not reach YouTube ({exc})"


class Command(BaseCommand):
    help = "Add curated listening videos from pasted YouTube links (verified, idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("urls", nargs="+", help="YouTube video URLs.")
        parser.add_argument("--band", required=True,
                            choices=[c[0] for c in profiles.TRACK_CHOICES],
                            help="Which age band this is for.")
        parser.add_argument("--level", default="L1",
                            help="Content level (L1..L8). Default L1.")
        parser.add_argument("--minutes", type=int, default=5,
                            help="Rough length, used as the check-in default.")
        parser.add_argument("--title", default="",
                            help="Override the fetched title (required with --force).")
        parser.add_argument("--force", action="store_true",
                            help="Add even when the title cannot be confirmed.")

    def handle(self, *args, **options):
        band, force = options["band"], options["force"]
        added = skipped = 0

        # Put new videos after everything already in the band so the curator's
        # existing order is preserved and the newest arrive at the back of the queue.
        start = (ListeningResource.objects.filter(age_band=band)
                 .order_by("-order").values_list("order", flat=True).first() or 0)

        for offset, url in enumerate(options["urls"], start=1):
            title, channel = lookup(url)
            if title is None:
                reason = channel
                if not force:
                    self.stdout.write(self.style.ERROR(f"  skipped  {url}\n           {reason}"))
                    skipped += 1
                    continue
                if not options["title"]:
                    raise CommandError(
                        f"--force needs --title, so the unconfirmed name is one you chose: {url}")
                title, channel = options["title"], "(unconfirmed)"

            resource, created = ListeningResource.objects.get_or_create(
                url=url, age_band=band,
                defaults={
                    "title": options["title"] or title,
                    "provider": channel or "",
                    "level": options["level"],
                    "minutes": options["minutes"],
                    "order": start + offset,
                    "kind": classify_url(url),
                },
            )
            if not created:
                self.stdout.write(f"  already   {resource.title[:50]}")
                skipped += 1
                continue
            added += 1
            note = "" if resource.kind == VIDEO else "  (a channel/playlist — will not rotate)"
            self.stdout.write(self.style.SUCCESS(
                f"  added     {resource.title[:46]:<48} {channel or ''}{note}"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"{added} added, {skipped} skipped."))
        if added:
            self.stdout.write(
                "These are live for that band immediately — nothing to approve. "
                "Watch a few seconds of each yourself: this checks that a link works "
                "and who published it, not whether the content suits your child.")

"""Check that every curated listening link still resolves (LGA-102).

Individual videos rot — deleted, made private, region-locked — far faster than
channels do, and a dead link on the listening page is a dead end for a child who
cannot debug it. Rotation made single videos first-class, so this is the chore
that came with them.

Uses YouTube's public oEmbed endpoint: no API key, no quota, and it returns the
title so a link that silently became a DIFFERENT video is visible too.

    python manage.py check_listening_links            # report only
    python manage.py check_listening_links --deactivate  # also switch dead ones off

``--deactivate`` sets ``active=False`` rather than deleting: the minutes she
already logged point at the row (SET_NULL), and a region-locked video may come
back.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from django.core.management.base import BaseCommand

from lingua.models import ListeningResource

OEMBED = "https://www.youtube.com/oembed"
TIMEOUT = 10


def probe(url):
    """(ok, detail) for one curated URL.

    oEmbed only understands single videos and playlists, so a /channel/ URL comes
    back 404 from an endpoint that never supported it. Reporting that as "dead"
    would cry wolf every run until someone stopped reading the output, so channels
    are reported as UNCHECKED rather than guessed at.
    """
    if "/channel/" in url or "/@" in url or "/user/" in url or "/c/" in url:
        return None, "channel — oEmbed cannot check these"
    query = urllib.parse.urlencode({"url": url, "format": "json"})
    try:
        with urllib.request.urlopen(f"{OEMBED}?{query}", timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return True, f"{data.get('author_name', '?')} — {data.get('title', '?')}"
    except urllib.error.HTTPError as exc:
        # 404 means gone. 401/403 does NOT: it is oEmbed's answer for "embedding is
        # turned off for this video", which many good channels do (Dreaming Spanish
        # among them) and which does not stop the LINK from working — and linking
        # out is all this page ever does. Treating those as dead would have
        # switched off perfectly usable videos on the first --deactivate run.
        if exc.code == 404:
            return False, "HTTP 404 — deleted or the id is wrong"
        return None, f"HTTP {exc.code} — embedding is off; the link itself may be fine"
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        # A network wobble is NOT evidence a video is dead. Never deactivate on it.
        return None, f"could not reach YouTube ({exc})"


class Command(BaseCommand):
    help = "Verify curated listening links still resolve (idempotent, read-only by default)."

    def add_arguments(self, parser):
        parser.add_argument("--deactivate", action="store_true",
                            help="Set active=False on links that are definitely gone.")

    def handle(self, *args, **options):
        alive = dead = unchecked = 0
        for resource in ListeningResource.objects.filter(active=True).order_by("age_band", "order"):
            ok, detail = probe(resource.url)
            label = f"{resource.age_band:<11} {resource.kind:<6} {resource.title[:38]:<40}"
            if ok is True:
                alive += 1
                self.stdout.write(f"  ok        {label} {detail[:60]}")
            elif ok is False:
                dead += 1
                self.stdout.write(self.style.ERROR(f"  DEAD      {label} {detail}"))
                if options["deactivate"]:
                    resource.active = False
                    resource.save(update_fields=["active"])
            else:
                unchecked += 1
                self.stdout.write(self.style.WARNING(f"  unchecked {label} {detail}"))

        self.stdout.write("")
        summary = f"{alive} ok, {dead} dead, {unchecked} unchecked"
        self.stdout.write(self.style.ERROR(summary) if dead else self.style.SUCCESS(summary))
        if dead and not options["deactivate"]:
            self.stdout.write("Re-run with --deactivate to switch the dead ones off.")

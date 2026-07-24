"""Bake read-along audio + timings for stories (LGA-38, D-16 / D-19 / N-05).

Run LOCALLY for the full synthesis — Polly runs off the web dyno (heavy + costs +
needs AWS creds). Run on prod with ``--link-only`` to create the StoryAudio rows from
the already-uploaded R2 assets WITHOUT any Polly call, mirroring the manga
``generate_* --link-only`` flow. Idempotent by content hash: an unchanged story is
skipped; editing its text (new hash) re-bakes it.

    python manage.py tts_build 12 13 --voice Mia         # local: synthesize + upload
    python manage.py tts_build --all-approved            # local: bake every approved story
    python manage.py tts_build --all-approved --link-only  # prod: link from R2, no Polly

Author numerals/abbreviations SPELLED OUT for clean 1:1 word alignment (D-19); the
command warns when a story body still contains digits.
"""
import re

from django.core.management.base import BaseCommand, CommandError

from lingua import services
from lingua.models import Story

_DIGIT_RE = re.compile(r"\d")


class Command(BaseCommand):
    help = "Bake (or --link-only) read-along audio + timings for stories."

    def add_arguments(self, parser):
        parser.add_argument("story_ids", nargs="*", type=int, help="Story pks to bake.")
        parser.add_argument("--all-approved", action="store_true",
                            help="Bake every APPROVED story (instead of listing ids).")
        parser.add_argument("--voice", default=None, help="Polly voice (default: settings).")
        parser.add_argument("--engine", default=None, help="Polly engine (default: settings).")
        parser.add_argument("--link-only", action="store_true",
                            help="Prod: link rows from already-uploaded R2 assets, no Polly.")
        parser.add_argument("--force", action="store_true",
                            help="Re-bake even if a current asset already exists.")

    def handle(self, *args, **options):
        if options["all_approved"]:
            stories = list(Story.objects.filter(status=Story.APPROVED))
        elif options["story_ids"]:
            stories = list(Story.objects.filter(pk__in=options["story_ids"]))
        else:
            raise CommandError("Give one or more story ids, or --all-approved.")
        if not stories:
            self.stdout.write("No matching stories.")
            return

        baked = linked = skipped = failed = 0
        for story in stories:
            if _DIGIT_RE.search(story.body):
                self.stderr.write(
                    f"  warning: story {story.pk} has digits — spell numerals out for "
                    f"clean 1:1 alignment (D-19)."
                )
            try:
                obj, action = services.bake_story_audio(
                    story, voice=options["voice"], engine=options["engine"],
                    link_only=options["link_only"], force=options["force"],
                )
            except Exception as exc:  # noqa: BLE001 — one failure must not abort the batch
                failed += 1
                self.stderr.write(f"  story {story.pk} failed: {type(exc).__name__}: {exc}")
                continue
            if action == "baked":
                baked += 1
            elif action == "linked":
                linked += 1
            else:
                skipped += 1
            self.stdout.write(
                f"[{action}] story {story.pk} {story.title!r} "
                f"-> {obj.audio_key} ({obj.duration_ms}ms)"
            )
        self.stdout.write(self.style.SUCCESS(
            f"Done: {baked} baked, {linked} linked, {skipped} skipped, {failed} failed."
        ))

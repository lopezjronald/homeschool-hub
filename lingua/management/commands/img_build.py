"""Bake illustrated-storybook pictures for stories (LGA-71, D-16 / N-05).

Runs image generation OFF the web dyno — it's heavy, costs money, and needs a
Replicate token. Run it locally, or (the primary path here) via ``heroku run`` on
prod, where the approved stories and the public R2 bucket both live. The image
provider must be configured wherever it runs (``REPLICATE_API_TOKEN``); unlike
tts_build there is no ``--link-only`` mode, because the stories and real object store
only exist on prod, so generation happens there directly.

One image per 1–2 sentences (a "beat"). Idempotent by content hash: an unchanged
story is skipped; editing its text (or the house style / art contract) re-bakes the
affected beats. The first image anchors the rest for character consistency. Each
generation is billed against the shared monthly cost ceiling; hitting it stops the run.

    python manage.py img_build 12 13            # bake these stories' images
    python manage.py img_build --all-approved   # bake every approved story
    python manage.py img_build 12 --force       # re-bake even if current
"""
from django.core.management.base import BaseCommand, CommandError

from lingua import services
from lingua.models import Story


class Command(BaseCommand):
    help = "Bake illustrated-storybook pictures (one per 1–2 sentences) for stories."

    def add_arguments(self, parser):
        parser.add_argument("story_ids", nargs="*", type=int, help="Story pks to illustrate.")
        parser.add_argument("--all-approved", action="store_true",
                            help="Illustrate every APPROVED story (instead of listing ids).")
        parser.add_argument("--force", action="store_true",
                            help="Re-bake even if a current image already exists.")

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

        if not services.get_image_client().is_configured():
            raise CommandError(
                "No image provider configured (set REPLICATE_API_TOKEN where this runs)."
            )

        baked = skipped = failed = 0
        for story in stories:
            try:
                summary = services.bake_story_images(story, force=options["force"])
            except services.BudgetExceeded as exc:
                self.stderr.write(self.style.WARNING(f"  stopping: {exc}"))
                break
            except Exception as exc:  # noqa: BLE001 — one failure must not abort the batch
                failed += 1
                self.stderr.write(f"  story {story.pk} failed: {type(exc).__name__}: {exc}")
                continue
            baked += summary["baked"]
            skipped += summary["skipped"]
            self.stdout.write(
                f"story {story.pk} {story.title!r}: {summary['baked']} baked, "
                f"{summary['skipped']} skipped ({summary['beats']} beats)"
            )
        self.stdout.write(self.style.SUCCESS(
            f"Done: {baked} images baked, {skipped} skipped, {failed} stories failed."
        ))

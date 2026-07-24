"""Generate leveled Spanish story DRAFTS for a theme (AI + LLM-critic).

Run LOCALLY (like the manga generate_* commands) — content authoring happens off
the web dyno. Each draft goes through the LLM-critic pre-filter: critic-passed
drafts land PENDING (ready for batch approval), flagged ones land DRAFT with the
flags recorded (D-48/49/50). Requires the Anthropic key to be configured.
"""
from django.core.management.base import BaseCommand, CommandError

from lingua import profiles, services
from lingua.models import Theme


class Command(BaseCommand):
    help = "Generate leveled Spanish story drafts for a theme (AI generation + LLM-critic)."

    def add_arguments(self, parser):
        parser.add_argument("theme_slug", help="slug of an existing lingua.Theme")
        parser.add_argument("--level", default="L1", help="target level L1..L8")
        parser.add_argument("--count", type=int, default=1)

    def handle(self, *args, **options):
        level = options["level"]
        if level not in profiles.LADDER:
            raise CommandError(f"--level must be one of {profiles.LADDER}, got {level!r}.")
        try:
            theme = Theme.objects.get(slug=options["theme_slug"])
        except Theme.DoesNotExist:
            raise CommandError(f"No Theme with slug {options['theme_slug']!r}.")

        ai = services.get_ai_client()
        if not ai.is_configured():
            raise CommandError("AI client is not configured (set ANTHROPIC_API_KEY).")

        count = options["count"]
        for i in range(count):
            try:
                story = services.create_story_draft(theme=theme, level=level, ai_client=ai)
            except Exception as exc:  # noqa: BLE001 — one bad reply must not abort the batch
                self.stderr.write(f"  story {i + 1}/{count} failed: {exc}")
                continue
            flags = f" flags={story.critic_flags}" if story.critic_flags else ""
            self.stdout.write(
                f"[{story.status}] {story.title!r} (critic_passed={story.critic_passed}){flags}"
            )

"""Seed several Saxon Pre-Algebra lessons in one go.

Each lesson keeps its own ``seed_saxon_<n>`` command — that is where the content
lives and how a single lesson gets re-seeded after a revision. This is only a
runner over them, because the deploy story does not scale otherwise: thirty
``heroku run`` invocations is thirty dyno starts, about fifteen minutes of
waiting, and thirty chances to typo a lesson number.

    python manage.py seed_saxon --curriculum 100 --lesson all
    python manage.py seed_saxon --curriculum 100 --lesson 74-80
    python manage.py seed_saxon --curriculum 100 --lesson 74,77,80

Lessons are seeded in ascending order and the run STOPS at the first failure, so
a broken lesson cannot be hidden by the twenty that seeded after it.
"""

import os
import re

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError


def available_lessons():
    """Lesson numbers that actually have a seeder, discovered by looking."""
    here = os.path.dirname(__file__)
    return sorted(
        int(m.group(1))
        for name in os.listdir(here)
        for m in [re.fullmatch(r"seed_saxon_(\d+)\.py", name)]
        if m
    )


def parse_selection(spec, available):
    """'all' | '74-80' | '74,77' | '74' -> a sorted list of lesson numbers.

    Unknown numbers are an ERROR rather than a silent skip: asking for a lesson
    that has no seeder means either a typo or a missing file, and both are things
    to hear about before a deploy rather than after.
    """
    if spec.strip().lower() == "all":
        return list(available)

    wanted = []
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", part)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if lo > hi:
                raise CommandError(f"'{part}' counts backwards")
            wanted.extend(range(lo, hi + 1))
        elif part.isdigit():
            wanted.append(int(part))
        else:
            raise CommandError(f"don't understand {part!r} — use 'all', '74-80' or '74,77'")

    missing = sorted(set(wanted) - set(available))
    if missing:
        raise CommandError(
            "no seeder for lesson(s) %s. Available: %s"
            % (", ".join(str(n) for n in missing),
               ", ".join(str(n) for n in available) or "none")
        )
    return sorted(set(wanted))


class Command(BaseCommand):
    help = "Seed a range of Saxon Pre-Algebra lessons (wraps seed_saxon_<n>)."

    def add_arguments(self, parser):
        parser.add_argument("--lesson", default="all",
                            help="'all', '74-80', '74,77,80' or a single number.")
        parser.add_argument("--curriculum", type=int,
                            help="Curriculum id to attach the lessons to.")
        parser.add_argument("--for-user", help="Username whose curriculum to use.")
        parser.add_argument("--child-name", default="Kaylin",
                            help="Child first name to link the materials to.")

    def handle(self, *args, **options):
        available = available_lessons()
        lessons = parse_selection(options["lesson"], available)
        if not lessons:
            self.stdout.write("nothing selected")
            return

        passthrough = []
        if options.get("curriculum"):
            passthrough += ["--curriculum", str(options["curriculum"])]
        if options.get("for_user"):
            passthrough += ["--for-user", options["for_user"]]
        if options.get("child_name"):
            passthrough += ["--child-name", options["child_name"]]

        for n in lessons:
            try:
                call_command(f"seed_saxon_{n}", *passthrough, stdout=self.stdout,
                             stderr=self.stderr)
            except CommandError as exc:
                # Say which lesson, then stop. Continuing would bury the failure
                # under later successes and leave a half-seeded curriculum that
                # nobody knows is half-seeded.
                raise CommandError(f"lesson {n} failed: {exc}") from exc

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(lessons)} lesson(s): "
            f"{', '.join(str(n) for n in lessons)}."))

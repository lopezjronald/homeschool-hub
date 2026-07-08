"""Seed the real Lopez family onto a live/local database (idempotent).

Creates (or reuses) the parent account, the family, both children with their
Levels, Violet's Dimensions Math 3A curriculum + the "Number Besties" manga, and
a starting placement. Safe to re-run — everything is get-or-create and an
existing user's password is never touched.

Examples:
    python manage.py seed_family
    python manage.py seed_family --username lopezjronald --superuser
    python manage.py seed_family --password "TempPass123" --superuser
"""

import secrets

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import Family, FamilyMembership
from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from students.models import Student

User = get_user_model()

# (first_name, level code, age note) for the children.
CHILDREN = [
    ("Violet", "G03"),
    ("Kaylin", "G07"),
]


class Command(BaseCommand):
    help = "Seed the Lopez family (parent, children, Violet's math + manga). Idempotent."

    def add_arguments(self, parser):
        parser.add_argument("--username", default="lopezjronald")
        parser.add_argument("--email", default="lopez.j.ronald@gmail.com")
        parser.add_argument("--family", default="Lopez Family")
        parser.add_argument("--last-name", default="Lopez")
        parser.add_argument(
            "--password",
            help="Password for a newly-created parent. Ignored if the user already exists. "
            "If omitted and the user is new, a temporary one is generated and printed.",
        )
        parser.add_argument(
            "--superuser",
            action="store_true",
            help="Grant the parent staff+superuser (admin) access.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        temp_password = None

        # 1. Parent account — adopt an existing one (email is unique, so match on
        #    it first, then username), otherwise create. An existing password is
        #    never reset.
        parent = (
            User.objects.filter(email__iexact=email).first()
            or User.objects.filter(username=username).first()
        )
        if parent is None:
            temp_password = options.get("password") or secrets.token_urlsafe(9)
            parent = User(username=username, email=email)
            parent.set_password(temp_password)
        if options["superuser"] and not (parent.is_staff and parent.is_superuser):
            parent.is_staff = True
            parent.is_superuser = True
        parent.save()
        # From here on use the real account username (an adopted account may
        # differ from the --username default).
        username = parent.username

        # 2. Family + parent membership — adopt the parent's existing family if
        #    they already have one, otherwise create the named family.
        family = get_active_family(parent)
        if family is None:
            family, _ = Family.objects.get_or_create(name=options["family"])
            FamilyMembership.objects.get_or_create(
                user=parent, family=family, defaults={"role": "parent"},
            )

        # 3. Children with their Levels.
        children = {}
        for first_name, level in CHILDREN:
            child, _ = Student.objects.get_or_create(
                parent=parent,
                family=family,
                first_name=first_name,
                defaults={"last_name": options["last_name"], "grade_level": level},
            )
            # keep level in sync if it changed
            if child.grade_level != level:
                child.grade_level = level
                child.save(update_fields=["grade_level"])
            children[first_name] = child

        # 4. Violet's math curriculum + structure + manga (reuse the commands).
        call_command("apply_blueprint", "dimensions_math_3a", for_user=username)
        call_command("seed_violet_manga", for_user=username, child_name="Violet")

        # 5. Point Violet at the manga lesson (Ch 2, L6) so progress shows.
        curriculum = Curriculum.objects.filter(
            parent=parent, name="Dimensions Math 3A",
        ).first()
        placement_note = "skipped (no curriculum)"
        if curriculum:
            lesson = (
                Lesson.objects.filter(
                    chapter__curriculum=curriculum, chapter__number=2, number=6,
                )
                .first()
            )
            if lesson:
                CurriculumPlacement.objects.update_or_create(
                    child=children["Violet"],
                    curriculum=curriculum,
                    defaults={"current_lesson": lesson},
                )
                placement_note = f"Violet -> {lesson.code}"

        # 6. Report.
        self.stdout.write(self.style.SUCCESS("Family seeded:"))
        self.stdout.write(f"  Parent   : {parent.username} <{parent.email}>"
                          f"{' (superuser)' if parent.is_superuser else ''}")
        self.stdout.write(f"  Family   : {family.name} (#{family.id})")
        for first_name, level in CHILDREN:
            label = dict(Student.LEVEL_CHOICES).get(level, level)
            self.stdout.write(f"  Child    : {children[first_name]} — {label}")
        self.stdout.write(f"  Placement: {placement_note}")
        if temp_password:
            self.stdout.write(self.style.WARNING(
                f"  Password : {temp_password}   <-- temporary; log in and change it."
            ))
        else:
            self.stdout.write("  Password : unchanged (existing account).")

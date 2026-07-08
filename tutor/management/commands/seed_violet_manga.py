"""Seed the manually-authored Ch2 L6 "Number Besties" MANGA onto a curriculum.

Requires the Dimensions Math 3A blueprint to have been applied first (so the
Chapter 2, Lesson 6 lesson exists).

Examples:
    python manage.py seed_violet_manga --curriculum 5
    python manage.py seed_violet_manga --for-user lopezjronald --child-name Violet
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

TITLE = "Number Besties — Operation: Full Hundred"

STUDENT_CONTENT = """NUMBER BESTIES  ——  Operation: Full Hundred
(a math manga · Chapter 6: Strategies for Numbers Close to Hundreds)

〈 PAGE 1 〉

PANEL 1 — Wide shot. HQ rooftop at dusk.
CAPTION: Every number has a secret partner. Together, they make one hundred.
NINETY-EIGHT (thinking): I'm only 2 away from a full hundred... so close it hurts.

PANEL 2 — Close-up. Determined eyes.
TWO (leaping in, grinning): Then borrow me, partner! You + me = 100. That's what besties are for.
SFX: BA-DUMP

PANEL 3 — Mission briefing screen glows.
▷ MISSION: 234 + 98
NINETY-EIGHT: Adding 98 is a trap. But adding 100? Child's play.

〈 PAGE 2 〉

PANEL 4 — BIG panel. Ninety-Eight powers up into a shining 100.
SFX: DODON!!
234 + 100 = 334
TWO: Careful — we borrowed 2 EXTRA power.

PANEL 5 — Cooldown. Return the borrowed energy.
Give the 2 back:  334 − 2 = 332
NINETY-EIGHT: Mission... complete. ✦

PANEL 6 — Split panel. A rival smirks from the shadows: "There's more than one way, you know."
▷ THE OTHER ORDER
Adjust FIRST:  234 − 2 = 232
THEN use the hundred:  232 + 100 = 332
CAPTION: Same answer. A true hero has more than one move.

〈 PAGE 3 — FINAL BATTLE 〉

PANEL 7 — A bigger foe rises: 456 + 397.
Three-Ninety-Seven's bestie is THREE (together they make 400!).
456 + 400 = 856
Return the 3:  856 − 3 = 853
SFX: KA-KOOM!!

PANEL 8 — Victory pose, the besties stand back-to-back.
★ RULE OF THE NUMBER BESTIES ★
When a number is 1, 2, or 3 away from a hundred —
borrow its bestie to make the hundred, do the easy math, then return the bestie.
NINETY-EIGHT: Never underestimate a number close to a hundred.  To be continued →"""

PARENT_CONTENT = """Goal: flexible mental math for numbers just below a hundred (1-3 less), like 98,
197, or 397. The child should see that adding or subtracting such a number can be
done by using the nearby hundred and then adjusting.

Two valid orders (both correct — encourage flexibility):
  - Use the hundred, then adjust:  234 + 98  ->  234 + 100 = 334  ->  334 - 2 = 332
  - Adjust first, then the hundred: 234 + 98  ->  (234 - 2) + 100 = 332

The classic misconception: confusing whether to GIVE BACK or TAKE BACK the
adjustment after using the hundred.
  - Adding 98 = adding 100 but 2 too many, so SUBTRACT 2.
  - Subtracting 98 = subtracting 100 but 2 too many, so ADD 2 back:
    234 - 98  ->  234 - 100 + 2 = 136.
  Ask: "Did we use too much or too little? So do we give it back or take it back?"

If she's stuck: model it with base-ten blocks — trade up to the full hundred,
then physically add or remove the small "bestie" amount. Then do the matching
workbook exercise for this lesson.

Extend: three-away numbers (397 -> 400, bestie 3). Same idea, bigger hundred.

Manga note: the "Number Besties" is her world — same warm, playful, triumphant
tone across future chapters. Keep the math exact; let the story carry the drama."""


class Command(BaseCommand):
    help = "Seed the Ch2 L6 'Number Besties' manga onto a curriculum (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help="Username whose 'Dimensions Math 3A' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = self._resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(chapter__curriculum=curriculum, chapter__number=2, number=6)
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                "Chapter 2, Lesson 6 not found. Apply the Dimensions Math 3A blueprint first "
                "(manage.py apply_blueprint dimensions_math_3a --curriculum <id>)."
            )

        child = None
        if options.get("child_name") and curriculum.family_id:
            child = Student.objects.filter(
                family_id=curriculum.family_id, first_name__iexact=options["child_name"],
            ).first()

        material, created = Material.objects.get_or_create(
            lesson=lesson,
            title=TITLE,
            skill_type=Material.SKILL_MANGA,
            defaults={
                "student_content": STUDENT_CONTENT,
                "parent_content": PARENT_CONTENT,
                "child": child,
                "family": curriculum.family,
                "status": Material.DRAFT,
            },
        )
        # Self-heal the child link: an earlier run may have created the material
        # before the child's profile existed (leaving child NULL).
        if not created and child and material.child_id is None:
            material.child = child
            material.save(update_fields=["child"])

        verb = "Created" if created else "Already present"
        self.stdout.write(self.style.SUCCESS(
            f"{verb}: Material #{material.pk} '{material.title}' on {lesson.code} "
            f"(status: {material.get_status_display()})."
        ))

    def _resolve_curriculum(self, options):
        if options.get("curriculum"):
            try:
                return Curriculum.objects.get(pk=options["curriculum"])
            except Curriculum.DoesNotExist:
                raise CommandError(f"Curriculum #{options['curriculum']} does not exist.")
        if options.get("for_user"):
            from django.contrib.auth import get_user_model

            User = get_user_model()
            try:
                user = User.objects.get(username=options["for_user"])
            except User.DoesNotExist:
                raise CommandError(f"User '{options['for_user']}' does not exist.")
            curriculum = Curriculum.objects.filter(parent=user, name="Dimensions Math 3A").first()
            if curriculum is None:
                raise CommandError(
                    f"No 'Dimensions Math 3A' curriculum found for {user.username}."
                )
            return curriculum
        raise CommandError("Provide either --curriculum <id> or --for-user <username>.")

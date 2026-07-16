"""Seed the manually-authored Ch2 L9 "Word Problems - Part 1" MANGA (Chi's Sweet Home).

A cozy cat manga that teaches part-whole bar models for one-step word problems:
whole unknown -> add (6 + 8 = 14), and a part unknown -> subtract (12 - 5 = 7).
Direct sequel to the Ch2 L8 "Sum & Difference" lesson (same cats, Chi & Blackie).
Requires the Dimensions Math 3A blueprint applied first (so Ch2 L9 exists).

Examples:
    python manage.py seed_violet_word_problems_1 --curriculum 6
    python manage.py seed_violet_word_problems_1 --for-user ronald --child-name Violet
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

TITLE = "Chi Shares the Catch — Word Problems with Bars"

STUDENT_CONTENT = """CHI SHARES THE CATCH  ——  Word Problems with Bars
(a math manga · Chapter 2, Lesson 9: Word Problems – Part 1)

〈 PAGE 1 〉

PANEL 1 — Wide. A bright morning by the pond. Chi and Blackie sit by two little piles of fish they caught.
CAPTION: A bright morning by the pond. Two happy fishers!
CHI (grinning): We caught SO many fishies today!

PANEL 2 — Chi looks between the two fish piles, counting on a paw.
CHI (thinking): Chi caught six… Blackie caught eight…
CHI: How many fishies all together?

PANEL 3 — Blackie lifts a paw, calm and gruff.
BLACKIE: A story with numbers? Draw a bar, Chi.
BLACKIE: Two parts… one whole.

〈 PAGE 2 — FIND THE WHOLE (add the parts) 〉

PANEL 4 — BIG panel. The two fish piles line up under one long bar: a part of 6, then a part of 8, under one whole marked "?".
▷ PART-WHOLE BAR:   [ Chi's 6 ][ Blackie's 8 ] = ?
CAPTION: Both parts known — the whole is the SUM. Add.
6 + 8 = 14
CHI (delighted): Fourteen fishies! We caught fourteen!

〈 PAGE 3 — FIND A PART (take the known part away) 〉

PANEL 5 — A bowl of treats with a few crumbs; some were nibbled. Chi looks worried-cute.
CHI: There were twelve treats… five got nibbled up…
CHI: How many treats are LEFT?

PANEL 6 — BIG. A part-whole bar: whole 12, one part 5 (nibbled), the other part glowing with "?".
▷ PART-WHOLE BAR:   whole 12,  part 5,  other part ?
CAPTION: Whole and one part known — find the missing PART. Take away.
12 − 5 = 7
CHI (relieved): Seven treats left! Phew!

〈 PAGE 4 〉

PANEL 7 — Blackie, wise and warm; Chi nods proudly.
BLACKIE: Looking for the WHOLE? Put the parts together — add.
BLACKIE: Looking for a PART? Take the known part away — subtract.

PANEL 8 — Full. Sunset. Chi snuggled happily against Blackie, the fish pile and treat bowl side by side.
★ CHI'S RULE ★
Draw the bar.  Whole = ADD the parts.  A missing part = SUBTRACT.
A "?" just means "the number we're looking for."
CHI (sleepy, happy): Draw the bar… then add or take away. Chi can do word problems!   To be continued →"""

STUDENT_INTRO = (
    "A word problem is just a little story with numbers hiding in it. Draw a "
    "PART-WHOLE bar and the story becomes easy to see: two parts and one whole. "
    "If the WHOLE is missing, put the parts together and add. If a PART is "
    "missing, take the known part away and subtract. Follow Chi and Blackie as "
    "they count their catch and their treats — then try drawing your own bars!"
)

PARENT_CONTENT = """## The big idea

A one-step word problem is a **part-whole** story. Drawing the bar *first* turns "add or subtract?" from a guess into something she can **see**.

- **Whole unknown** → put the parts together → **add**  (6 + 8 = 14).
- **A part unknown** → take the known part from the whole → **subtract**  (12 − 5 = 7).

Same bar, two questions — what's *missing* tells her which operation.

## How to read the story into a bar

1. Find the two **parts** and the **whole**.
2. Mark what you **know**; put a **?** on what you're looking for.
3. **?** on the whole → add.  **?** on a part → subtract.

> Ask: *"Are we looking for the whole, or for a part?"* That one question picks the operation.

## The classic mix-up

Kids grab the operation the *words* seem to suggest ("left" = subtract, "all together" = add) and get tripped up by trickier wording. The bar model sidesteps that: **the picture, not the keyword, decides.** A missing part is always a subtraction — even when the story never says "take away."

## Help her hands-on

Use counters (or toy fish!):

1. **Whole unknown:** make both parts, slide them together, count → the whole.
2. **Part unknown:** make the whole, remove the known part, count what's left → the missing part.

## Extend it

Give her the whole and one part and ask for the other ("We need 14; Chi has 6 — how many more must Blackie bring?"). Then flip it: give both parts, ask for the whole. Have her **draw the bar every time** before she computes.

## A note on the manga

This continues Chi's Sweet Home from Lesson 8 — same cozy tone, same cats. The bars do the teaching; Chi and Blackie carry the warmth. Numbers stay small so the *method* is the star."""


class Command(BaseCommand):
    help = "Seed the Ch2 L9 'Chi Shares the Catch' part-whole word-problems manga (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help="Username whose 'Dimensions Math 3A' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = self._resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(chapter__curriculum=curriculum, chapter__number=2, number=9)
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                "Chapter 2, Lesson 9 not found. Apply the Dimensions Math 3A blueprint first "
                "(manage.py apply_blueprint dimensions_math_3a --curriculum <id>)."
            )

        child = self._resolve_child(curriculum, options.get("child_name"))

        material, created = Material.objects.get_or_create(
            lesson=lesson,
            title=TITLE,
            skill_type=Material.SKILL_MANGA,
            defaults={
                "student_intro": STUDENT_INTRO,
                "student_content": STUDENT_CONTENT,
                "parent_content": PARENT_CONTENT,
                "child": child,
                "family": curriculum.family,
                "status": Material.DRAFT,
                # Art is drawn with a reserved balloon zone up top (see
                # generate_chi_word_problems), so speech floats over the art.
                "manga_text_layout": Material.LAYOUT_FLOAT,
            },
        )
        # Refresh authored text on re-run so content edits ship, and self-heal the child link.
        updates = []
        if not created:
            if material.student_intro != STUDENT_INTRO:
                material.student_intro = STUDENT_INTRO
                updates.append("student_intro")
            if material.student_content != STUDENT_CONTENT:
                material.student_content = STUDENT_CONTENT
                updates.append("student_content")
            if material.parent_content != PARENT_CONTENT:
                material.parent_content = PARENT_CONTENT
                updates.append("parent_content")
            if child and material.child_id is None:
                material.child = child
                updates.append("child")
            if material.manga_text_layout != Material.LAYOUT_FLOAT:
                material.manga_text_layout = Material.LAYOUT_FLOAT
                updates.append("manga_text_layout")
            if updates:
                material.save(update_fields=updates)

        verb = "Created" if created else ("Updated" if updates else "Already present")
        self.stdout.write(self.style.SUCCESS(
            f"{verb}: Material #{material.pk} '{material.title}' on {lesson.code} "
            f"(status: {material.get_status_display()})."
        ))

    def _resolve_child(self, curriculum, name):
        """Find the child this material belongs to, tolerant of legacy data."""
        if name:
            by_name = Student.objects.filter(first_name__iexact=name)
            if curriculum.family_id:
                child = by_name.filter(family_id=curriculum.family_id).first()
                if child:
                    return child
            child = by_name.filter(parent=curriculum.parent).first()
            if child:
                return child
        placement = curriculum.placements.select_related("child").first()
        return placement.child if placement else None

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

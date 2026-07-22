"""Seed the manually-authored Ch3 L1 "Addition with Regrouping" MANGA (Pokemon Gen 9).

A bright Pokemon-themed manga that teaches addition with regrouping (carrying):
add place by place, and when a column reaches 10 or more, bundle ten and carry
it to the next place. Worked example 156 + 128 = 284 (one regroup in the ones:
6 + 8 = 14 -> write 4, carry 1 ten). Stars the latest (Gen 9 / Scarlet & Violet)
starters Sprigatito & Fuecoco on a Paldea berry-picking day.
Requires the Dimensions Math 3A blueprint applied first (so Ch3 L1 exists).

Examples:
    python manage.py seed_violet_regrouping --curriculum 6
    python manage.py seed_violet_regrouping --for-user lopezjronald --child-name Violet
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

TITLE = "Sprigatito's Berry Bundle — Adding with Regrouping"

STUDENT_CONTENT = """SPRIGATITO'S BERRY BUNDLE  ——  Adding with Regrouping
(a math manga · Chapter 3, Lesson 1: Addition with Regrouping)

〈 PAGE 1 〉

PANEL 1 — Wide. A sunny berry field in Paldea. Sprigatito and Fuecoco sit beside two big baskets of berries.
CAPTION: A big berry-picking day in Paldea!
SPRIGATITO (grinning): We picked SO many berries today!

PANEL 2 — Sprigatito looks between the two baskets, counting on a paw.
SPRIGATITO (thinking): Sprigatito picked one hundred fifty-six… Fuecoco picked one hundred twenty-eight…
SPRIGATITO: How many berries ALL TOGETHER?

PANEL 3 — Fuecoco, warm and clever, lifts its little flame tail like a teacher.
FUECOCO: Add them place by place — start with the ONES.
FUECOCO: But watch out — sometimes the ones OVERFLOW!

〈 PAGE 2 — ADD THE ONES (they overflow → regroup) 〉

PANEL 4 — BIG panel. The loose "ones" berries pooled together: 6 + 8 = 14 loose berries, clearly more than nine.
▷ ONES:  6 + 8 = 14  — that's MORE than 9!
CAPTION: 6 ones + 8 ones = 14 ones. Ten or more — time to REGROUP!
SPRIGATITO (surprised): Fourteen ones! That's too many to keep loose!

PANEL 5 — BIG. Ten loose berries get tied into ONE bundle-of-ten and slide over toward the tens; 4 loose berries stay behind.
▷ REGROUP:  bundle 10 ones → 1 ten,  4 ones left over
CAPTION: Trade 10 ones for 1 TEN. Write 4 in the ones, carry the 1 ten over.
FUECOCO: Bundle ten, carry one! Four ones stay behind.

〈 PAGE 3 — FINISH THE TENS AND HUNDREDS 〉

PANEL 6 — BIG. The tens line up: 5 tens + 2 tens + the 1 carried ten = 8 tens; the hundreds: 1 + 1 = 2. One full basket reads the total.
▷ TENS: 5 + 2 + 1 = 8     HUNDREDS: 1 + 1 = 2
CAPTION: Now add the rest.   156 + 128 = 284
SPRIGATITO (delighted): Two hundred eighty-four berries all together!

〈 PAGE 4 〉

PANEL 7 — Fuecoco, wise and warm; Sprigatito nods proudly.
FUECOCO: Add each place. If a place makes 10 or more…
FUECOCO: …bundle ten and carry it to the next place. That's REGROUPING!

PANEL 8 — Full. Sunset over the berry field; Sprigatito snuggled happily beside Fuecoco with one big basket of berries.
★ REGROUPING RULE ★
Add place by place. When a column makes 10 or more, bundle 10 and CARRY it to the next place. Ones → tens → hundreds.
SPRIGATITO (sleepy, happy): Bundle ten, carry one… Sprigatito can regroup!   To be continued →"""

STUDENT_INTRO = (
    "When you add and a column makes 10 or more, you REGROUP: bundle ten together "
    "and carry it to the next place. Add place by place — ones first, then tens, "
    "then hundreds — and any time a place reaches ten, trade those ten for one of "
    "the next-bigger place. Follow Sprigatito and Fuecoco as they add their two "
    "baskets of berries (156 + 128) and have to bundle ten ones into a ten — then "
    "try your own regrouping!"
)

PARENT_CONTENT = """## The big idea

Regrouping (a.k.a. "carrying") is what you do when a place-value column adds up to **10 or more**. You can only keep 0–9 in a place, so you **bundle ten and carry it** to the next-bigger place.

- **156 + 128** → ones: **6 + 8 = 14** → write **4**, carry **1 ten**.
- tens: **5 + 2 + 1 = 8**; hundreds: **1 + 1 = 2** → **284**.

The whole idea is one move — *trade ten of these for one of those* — repeated place by place.

## How to add with regrouping

1. Line the numbers up by place (ones under ones, tens under tens…).
2. Add the **ones**. If the total is 10 or more, write the ones digit and **carry the ten**.
3. Add the **tens** (plus any carried ten). Regroup again if needed.
4. Continue into the hundreds.

> Ask: *"Did this column reach ten? Then bundle ten and carry it."*

## The classic mix-up

Kids often write the whole two-digit total in one place ("6 + 8 = 14" → writing 14 under the ones) instead of writing **4** and carrying the **1**. Bundling ten *physically* — ten loose things become one stick/bundle — makes the carry make sense, not just a rule.

## Help her hands-on

Use bundles of ten (craft sticks, straws banded in tens, or base-ten blocks):

1. Build both numbers with ten-bundles and loose ones.
2. Add the loose ones; when you reach ten, **band ten into a new bundle** and move it to the tens.
3. Count the tens (including the new bundle), then the hundreds.

Say it out loud each time: *"Ten ones make one ten — carry it."*

## Extend it

Try one that regroups in the **tens** too (e.g. 176 + 158), or ask her to *predict* which columns will need regrouping before she adds. Have her **estimate first** ("about 150 + 130 ≈ 280") so the exact answer has something to check against.

## A note on the manga

A fresh Gen 9 cast — Sprigatito and Fuecoco, the newest starters (from *Pokémon Scarlet & Violet* — yes, *Violet!*). The berries model place value: loose ones bundle into tens. Numbers stay clean with a single regroup so the *bundle-and-carry* move is the star."""


class Command(BaseCommand):
    help = "Seed the Ch3 L1 'Sprigatito's Berry Bundle' addition-with-regrouping manga (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help="Username whose 'Dimensions Math 3A' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = self._resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(chapter__curriculum=curriculum, chapter__number=3, number=1)
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                "Chapter 3, Lesson 1 not found. Apply the Dimensions Math 3A blueprint first "
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
                # Art reserves an open balloon zone up top (see generate_pokemon_regrouping),
                # so speech floats over the art.
                "manga_text_layout": Material.LAYOUT_FLOAT,
            },
        )
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

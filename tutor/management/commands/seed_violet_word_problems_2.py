"""Seed the manually-authored Ch2 L10 "Word Problems - Part 2" MANGA (Pokemon theme).

A bright Pokemon-themed manga that teaches COMPARISON bar models for one-step
word problems: line up two amounts as a longer bar and a shorter bar, and the
gap between them is the difference. Both amounts known -> subtract for the gap
(340 - 210 = 130, "how many more"); one amount + the gap known -> add to find
the bigger (210 + 130 = 340). A fresh cast (Pikachu & Bulbasaur at a Catching
Contest) after the Chi's Sweet Home part-whole lessons.
Requires the Dimensions Math 3A blueprint applied first (so Ch2 L10 exists).

Examples:
    python manage.py seed_violet_word_problems_2 --curriculum 6
    python manage.py seed_violet_word_problems_2 --for-user lopezjronald --child-name Violet
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

TITLE = "Pikachu's Catching Contest — Comparing with Bars"

STUDENT_CONTENT = """PIKACHU'S CATCHING CONTEST  ——  Comparing with Bars
(a math manga · Chapter 2, Lesson 10: Word Problems – Part 2)

〈 PAGE 1 〉

PANEL 1 — Wide. The Catching Contest field after a big Pokémon swarm. Pikachu and Bulbasaur stand with two bulging catch bags.
CAPTION: The Catching Contest! What a swarm today!
PIKACHU (grinning): Pika-pika! We caught SO many today!

PANEL 2 — Pikachu looks between the two catch tallies, thinking hard.
PIKACHU (thinking): Pikachu caught three hundred forty… Bulbasaur caught two hundred ten…
PIKACHU: How many MORE did Pikachu catch?

PANEL 3 — Bulbasaur, calm and wise, lifts a vine like a teacher.
BULBASAUR: Line them up, Pika — a longer bar and a shorter bar.
BULBASAUR: The gap at the end is the difference.

〈 PAGE 2 — FIND THE DIFFERENCE (both amounts known → subtract) 〉

PANEL 4 — BIG panel. Two long rows of Poké Balls: Pikachu's row (340) above Bulbasaur's shorter row (210), lined up at the left; the extra Poké Balls at the right end marked "?".
▷ COMPARISON BARS:   Pikachu [—— 340 ——],   Bulbasaur [— 210 —],   gap = ?
CAPTION: Both amounts known — line up the bars. The extra part is the difference. Subtract.
340 − 210 = 130
PIKACHU (delighted): One hundred thirty more! Pikachu caught 130 more than Bulbasaur!

〈 PAGE 3 — FIND THE BIGGER AMOUNT (one amount + the gap → add) 〉

PANEL 5 — Next round. Bulbasaur shows its tally proudly; Pikachu's is still hidden under a leaf.
BULBASAUR: Next round! Bulbasaur caught two hundred ten again…
BULBASAUR: and you caught 130 MORE than me. How many did YOU catch?

PANEL 6 — BIG. Bulbasaur's bar (210) with a glowing "130 more" piece added onto the end, reaching up to Pikachu's longer "?" bar.
▷ COMPARISON BARS:   Bulbasaur [— 210 —] + 130 more  =  Pikachu [—— ? ——]
CAPTION: One amount and the difference known — add them to find the bigger.
210 + 130 = 340
PIKACHU (proud): Three hundred forty! Adding the extra gives my total!

〈 PAGE 4 〉

PANEL 7 — Bulbasaur, warm and wise; Pikachu nods along.
BULBASAUR: Line up two bars. Both amounts known? Subtract for the gap.
BULBASAUR: Know the gap? Add or take away to find the other.

PANEL 8 — Full. Sunset over the contest field, ribbons fluttering, Pikachu snuggled happily beside Bulbasaur with their catch.
★ PIKA'S RULE ★
Line up two bars. The gap is the difference. Both amounts → SUBTRACT. One amount + the gap → ADD.
A "?" just means "the number we're looking for."
PIKACHU (happy): Line up the bars… then compare! Pika can do comparing!   To be continued →"""

STUDENT_INTRO = (
    "A comparison word problem lines up TWO amounts to see how they measure up. "
    "Draw two bars — a longer one and a shorter one — starting from the same "
    "place. The GAP at the end is the difference. If both amounts are known, "
    "subtract to find the gap ('how many more?'). If you know one amount and the "
    "gap, add or take away to find the other. Follow Pikachu and Bulbasaur at the "
    "Catching Contest — then try drawing your own comparison bars!"
)

PARENT_CONTENT = """## The big idea

A comparison word problem lines up **two amounts** to compare them. Two bars drawn from the same starting line — a longer one and a shorter one — make "how many more/fewer" something she can **see**: the difference is the overhang at the end.

- **Difference unknown** → both amounts known → **subtract**  (340 − 210 = 130).
- **A quantity unknown** → one amount and the difference known → **add** (or subtract) to find the other  (210 + 130 = 340).

## How to draw it

1. Draw the bigger amount as a longer bar and the smaller as a shorter bar, **lined up at the left**.
2. Mark the **difference** as the gap at the right end.
3. Both amounts known → subtract for the gap. One amount + the gap known → add/subtract for the missing bar.

> Ask: *"Which is bigger, and how much longer is its bar?"* That overhang is the difference.

## The classic mix-up

"How many more" and "how many fewer" describe the **same gap** — the distance between the two bars — so both are found the same way. Kids often add when they should compare (or grab the operation a keyword seems to suggest); the two-bar picture keeps the *comparison*, not the keyword, in charge.

## Help her hands-on

Use two rows of counters (or Poké Balls, coins, beans), one row per amount, lined up at the left:

1. **Difference:** lay both rows side by side; the bit sticking out past the shorter row is "how many more."
2. **Missing amount:** lay out the smaller row, add the "extra" onto the end, and count → the bigger amount.

## Extend it

Flip the question: give the bigger amount and the difference, ask for the smaller ("Pikachu caught 340, and that's 130 more than Bulbasaur — how many did Bulbasaur catch?" → subtract). Have her **draw the two bars every time** before she computes.

## A note on the manga

A brighter, Pokémon-themed change of pace after Chi's Sweet Home. The bars do the teaching; Pikachu and Bulbasaur carry the fun. The numbers are bigger here on purpose — the *method* (line up, compare) is exactly the same whether the amounts are 6 and 8 or 340 and 210."""


class Command(BaseCommand):
    help = "Seed the Ch2 L10 'Pikachu's Catching Contest' comparison-bar word-problems manga (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help="Username whose 'Dimensions Math 3A' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = self._resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(chapter__curriculum=curriculum, chapter__number=2, number=10)
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                "Chapter 2, Lesson 10 not found. Apply the Dimensions Math 3A blueprint first "
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
                # generate_pokemon_comparison), so speech floats over the art.
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

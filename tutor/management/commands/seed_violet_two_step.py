"""Seed the manually-authored Ch2 L11 "2-Step Word Problems" MANGA (Pokemon theme).

A bright Pokemon-themed manga that teaches how to solve TWO-STEP word problems
with bar models: find the hidden middle number first (step 1), then use it to
answer the real question (step 2). It stitches together the part-whole bar
(Lesson 9) and the comparison bar (Lesson 10): Pikachu caught 250, Bulbasaur
caught 100 fewer -> step 1 compare/subtract (250 - 100 = 150); the judge asks
for the TOTAL -> step 2 part-whole/add (250 + 150 = 400). Reuses the Pikachu &
Bulbasaur cast from the Ch2 L10 comparison lesson.
Requires the Dimensions Math 3A blueprint applied first (so Ch2 L11 exists).

Examples:
    python manage.py seed_violet_two_step --curriculum 6
    python manage.py seed_violet_two_step --for-user lopezjronald --child-name Violet
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

TITLE = "Pikachu's Two-Step Catch — Bar Models, One Step at a Time"

STUDENT_CONTENT = """PIKACHU'S TWO-STEP CATCH  ——  Bar Models, One Step at a Time
(a math manga · Chapter 2, Lesson 11: 2-Step Word Problems)

〈 PAGE 1 〉

PANEL 1 — Wide. Back at the Catching Contest, Pikachu and Bulbasaur stand with two catch bags as a judge poses a tricky question.
CAPTION: Back at the Catching Contest — and today there's a TRICKY question!
PIKACHU (grinning): Pika! The judge wants our TOTAL, all together!

PANEL 2 — Pikachu scratches its head, puzzling over the question.
PIKACHU (thinking): Pikachu caught two hundred fifty… Bulbasaur caught one hundred FEWER…
PIKACHU: How many did we catch ALL TOGETHER?

PANEL 3 — Bulbasaur, calm and wise, raises two vines — one for each step.
BULBASAUR: That's a TWO-step question, Pika. First find MY number…
BULBASAUR: …THEN put both together. Draw one bar for each step!

〈 PAGE 2 — STEP 1: FIND THE HIDDEN NUMBER (compare → subtract) 〉

PANEL 4 — BIG panel. Comparison bars: Pikachu's row (250) above Bulbasaur's shorter row (100 fewer), lined up at the left; Bulbasaur's total marked "?".
▷ STEP 1 — COMPARE:   Pikachu [—— 250 ——],   Bulbasaur is 100 fewer = ?
CAPTION: Step 1 — Bulbasaur caught 100 FEWER. Compare and subtract.
250 − 100 = 150
BULBASAUR (calm): So Bulbasaur caught one hundred fifty. Now we know BOTH numbers!

〈 PAGE 3 — STEP 2: ANSWER THE REAL QUESTION (combine → add) 〉

PANEL 5 — Pikachu's eyes light up, then it points back at the judge's question.
PIKACHU: One hundred fifty for Bulba! But the judge asked for ALL TOGETHER…
PIKACHU: …so there's ONE more step!

PANEL 6 — BIG. Part-whole bar: Pikachu's 250 group and Bulbasaur's 150 group pushed together into ONE long total bar marked "?".
▷ STEP 2 — COMBINE:   [ Pikachu 250 ][ Bulbasaur 150 ]  =  ?
CAPTION: Step 2 — now put BOTH parts together. Add.
250 + 150 = 400
PIKACHU (delighted): Four hundred! We caught four hundred all together!

〈 PAGE 4 〉

PANEL 7 — Bulbasaur, warm and wise; Pikachu nods along, proud.
BULBASAUR: A two-step problem hides a middle number. Find it FIRST…
BULBASAUR: …then answer what was really asked. A bar for each step.

PANEL 8 — Full. Sunset over the contest field, a big prize ribbon fluttering; Pikachu snuggled happily beside Bulbasaur with their catch.
★ PIKA'S TWO-STEP RULE ★
Step 1: find the hidden number (draw a bar). Step 2: use it to answer the real question (draw another bar). One step at a time!
PIKACHU (happy): One step, then the next… Pika can do two-step problems!   To be continued →"""

STUDENT_INTRO = (
    "A two-step word problem hides a middle number you need before you can answer "
    "the real question. Take it one step at a time, and draw a bar for each step. "
    "Step 1: find the hidden number (here, compare and subtract). Step 2: use it to "
    "answer what was actually asked (here, add the parts together). Follow Pikachu "
    "and Bulbasaur as they work out their combined catch — then try your own "
    "two-step problems!"
)

PARENT_CONTENT = """## The big idea

A two-step word problem can't be answered in one move — it hides a **middle number** she has to find first. The skill: (1) spot what's missing, (2) draw a bar to find it, then (3) draw a second bar to answer what was really asked.

- **Step 1 (compare → subtract):** Bulbasaur caught 100 fewer than Pikachu's 250 → 250 − 100 = 150.
- **Step 2 (combine → add):** the question asked for the total → 250 + 150 = 400.

Same two bar models she already knows — a comparison bar, then a part-whole bar — just used one after the other.

## How to work a two-step problem

1. Read to the end and find the **actual question** ("how many altogether?").
2. Notice you can't answer it yet — something's missing (Bulbasaur's number). That missing piece is **step 1**.
3. Draw a bar for step 1 and solve it. Write the number down.
4. Draw a bar for step 2 using that number, and answer the real question.

> Ask: *"What do we need to know BEFORE we can answer this?"* That question finds step 1.

## The classic mix-up

Kids rush to combine the two numbers they see (250 and 100) in one step. But 100 isn't Bulbasaur's catch — it's how many *fewer* Bulbasaur caught. Drawing step 1 first makes the real middle number (150) visible before she adds.

## Help her hands-on

Use two rows of counters (or Poké Balls):

1. **Step 1:** lay out Pikachu's 250 and take away 100 → that's Bulbasaur's 150.
2. **Step 2:** push both rows together and count the whole → 400.

Have her say each step out loud: "First I find Bulbasaur's number. Then I add both."

## Extend it

Change the final question ("How many MORE did Pikachu catch?" → one step only; "How many altogether?" → two steps). Or flip step 1 to an addition ("Bulbasaur caught 100 MORE"). Have her **name the two steps before she computes**.

## A note on the manga

Pikachu and Bulbasaur's last adventure in this chapter — it stitches together the part-whole bar (Lesson 9) and the comparison bar (Lesson 10) into a two-step solve. The numbers stay clean so the *two-step method* is the star."""


class Command(BaseCommand):
    help = "Seed the Ch2 L11 'Pikachu's Two-Step Catch' 2-step word-problems manga (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help="Username whose 'Dimensions Math 3A' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = self._resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(chapter__curriculum=curriculum, chapter__number=2, number=11)
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                "Chapter 2, Lesson 11 not found. Apply the Dimensions Math 3A blueprint first "
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
                # generate_pokemon_two_step), so speech floats over the art.
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

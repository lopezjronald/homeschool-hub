"""Seed the manually-authored Ch2 L8 "Sum & Difference" MANGA (Chi's Sweet Home).

A cozy cat manga that teaches part-whole (sum) and comparison (difference) bar
models with one pair of numbers, 8 and 5 (sum 13, difference 3). Requires the
Dimensions Math 3A blueprint to have been applied first (so the Chapter 2,
Lesson 8 lesson exists).

Examples:
    python manage.py seed_violet_sum_difference --curriculum 6
    python manage.py seed_violet_sum_difference --for-user ronald --child-name Violet
"""

from django.core.management.base import BaseCommand, CommandError

from curricula.models import Curriculum, Lesson
from students.models import Student
from tutor.models import Material

TITLE = "Chi Counts the Cats — Sums & Differences"

STUDENT_CONTENT = """CHI COUNTS THE CATS  ——  Sums & Differences
(a math manga · Chapter 2, Lesson 8: Sum and Difference)

〈 PAGE 1 〉

PANEL 1 — Wide. A sunny park. A group of cats resting by a big tree; a smaller group by a little pond.
CAPTION: One warm afternoon in the park. Cats everywhere!
CHI (wide-eyed, grinning): So many kitties! Chi never saw so many!

PANEL 2 — Chi counts on her little paws. Blackie sits beside her, calm and serious.
CHI (thinking): Eight kitties here… five kitties there…
CHI: How many is that all together? Chi wants to know!

PANEL 3 — Blackie lifts a paw. Plain and gruff.
BLACKIE: Two ways, Chi. Put 'em together… or line 'em up.
BLACKIE: Draw a bar. You'll see.

〈 PAGE 2 — PUT THEM TOGETHER (the SUM) 〉

PANEL 4 — BIG panel. The tree group and the pond group slide together — still two clear clusters — into one long bar: a part of 8, then a part of 5, under one whole marked "?".
▷ PART-WHOLE BAR:   [ 8 by the tree ][ 5 by the pond ] = ?
CAPTION: Put the parts together — the whole is the SUM.
8 + 5 = 13
CHI (delighted): Thirteen! Chi counted thirteen kitties!

PANEL 5 — Blackie taps the bar; now one part is hidden.
BLACKIE: Got the whole and one part? Take it away.
▷  whole 13,  part 8,  other part ?    →    13 − 8 = 5
CHI (eyes wide): Ohh! Five kitties by the pond!

〈 PAGE 3 — LINE THEM UP (the DIFFERENCE) 〉

PANEL 6 — Two little bowls of fishy treats: Blackie's fuller than Chi's.
CHI (pouty-cute): Blackieee… you got MORE fishies than Chi!
BLACKIE: Line 'em up. Count what's extra.

PANEL 7 — Wide. Comparison bars: a longer bar of 8 above a shorter bar of 5, their ends matched; the extra piece glows.
▷ COMPARISON BARS:   8  over  5,   extra = ?
CAPTION: Line them up — the extra piece is the DIFFERENCE.
8 − 5 = 3
BLACKIE: Three more for me. Three fewer for you. …Here. Share.

PANEL 8 — Full. Sunset. Chi snuggled happily against Blackie, both bowls side by side.
★ CHI'S RULE ★
Put groups TOGETHER to find the SUM.    Line groups UP to find the DIFFERENCE.
A "?" just means "the number we're looking for."
CHI (sleepy, happy): Sums and diff'rences… Chi loves counting kitties!   To be continued →"""

STUDENT_INTRO = (
    "Two groups of cats can answer TWO questions! When you put the groups "
    "TOGETHER, you get the sum. When you LINE them UP to see which is bigger, "
    "the extra part is the difference. A bar model helps you SEE both. Follow "
    "Chi and Blackie as they count cats in the park and share fishy treats — "
    "then try drawing your own bars!"
)

PARENT_CONTENT = """## The big idea

This lesson opens the door to **bar models** — the tool she'll use for word problems all year. Two numbers can answer **two** questions:

- **Sum** — put the groups *together* → draw a **part-whole** bar.
- **Difference** — *line the groups up* → draw a **comparison** bar.

We use one pair, **8 and 5**, so she meets both at once.

## Part-whole bar (the SUM)

Two parts sit end-to-end under one whole: **8 + 5 = 13**. The **whole is the sum** of the parts.

The same bar also answers a *subtraction* question: if you know the whole and one part, the **missing part = whole − part** — so **13 − 8 = 5**.

> Ask: *"Are we looking for the whole, or a part? If it's a part, we take away."*

## Comparison bar (the DIFFERENCE)

Line the two amounts up, longer over shorter; the extra bit is the difference: **8 − 5 = 3** (3 more, or 3 fewer).

> Ask: *"Which is longer? By how much? That extra bit is the difference."*

## The classic mix-up

Kids often *add* when a problem says "how many more." Tie it to the picture: "more" and "fewer" mean we're **comparing** — line the bars up and find the gap.

## Help her hands-on

Use 8 counters (or toy cats!) and 5 counters:

1. **Together:** slide both groups into one line and count → the sum.
2. **Line up:** set them in two rows, ends matched, and count what sticks out → the difference.

## Extend it

Give her the whole and one part, and ask for the other (a missing-part problem). Then hide the difference: *"I have 8, you have 5 — draw the bars; how many more do I have?"*

## A note on the manga

Chi's world is gentle and cozy, so keep the tone warm. The math stays exact — let Chi and Blackie carry the story while the bar models do the teaching."""


class Command(BaseCommand):
    help = "Seed the Ch2 L8 'Chi Counts the Cats' sum-and-difference manga (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--curriculum", type=int, help="Curriculum id to attach the manga to.")
        parser.add_argument("--for-user", help="Username whose 'Dimensions Math 3A' curriculum to use.")
        parser.add_argument("--child-name", default="Violet", help="Child first name to link (optional).")

    def handle(self, *args, **options):
        curriculum = self._resolve_curriculum(options)
        lesson = (
            Lesson.objects.filter(chapter__curriculum=curriculum, chapter__number=2, number=8)
            .select_related("chapter")
            .first()
        )
        if lesson is None:
            raise CommandError(
                "Chapter 2, Lesson 8 not found. Apply the Dimensions Math 3A blueprint first "
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
                # The Chi art is generated with a reserved balloon zone up top
                # (see generate_chi_sum_difference), so speech floats over the art.
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

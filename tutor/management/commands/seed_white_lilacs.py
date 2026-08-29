"""Seed Kaylin's Blackbird "White Lilacs" course (idempotent).

    python manage.py seed_white_lilacs --for-user ronald

Digitises the family's purchased Blackbird & Company Literature Discovery Guide
for White Lilacs by Carolyn Meyer, for private family use: the five-section
shape (Read → Journal → Acquire → Recollect → Explore, then Glean), the guide's
own chapter divisions (1–5, 6–10, 11–15, 16–19), its vocabulary, comprehension
questions, writing exercises and discussion questions.

HOW THIS WAS TRANSCRIBED, AND WHAT THAT MEANS FOR THE ANSWERS. The family's PDF
of this guide is a pure scan — 59 pages with no text layer at all, so every word
below was read off a rendered page rather than extracted. There is also NO
teacher edition and NO answer key: the guide is the student workbook. So the
questions are the publisher's printed wording, and `answer_key` is deliberately
EMPTY rather than filled with something invented. Joyce marks this one from the
book.

PRINTED AS PRINTED. Kaylin is answering the page in front of her, so a silent
correction makes the app and the book disagree. This list is COMPLETE — every
slip the guide contains is below, and every one of them is deliberate here. If
you are about to fix one, it is in the book:

  * Section 1 discussion 2 — "Mrs Bell" (no full stop) and "How does She
    describe them?" (capital S mid-sentence).
  * Section 1 recollect 12 and 13 — "Miss. Firth" (a period that should not be
    there), twice.
  * Section 2 recollect 8 — "show here thoughtlessness" (for "her").
  * Section 2 recollect 13 — "fiance" (unaccented).
  * Section 2 writing option 1 — "detail the law and it's intent" (for "its").
  * Section 2 discussion 10 — "argue to his parent" (singular).
  * Section 3 recollect 12 — "wanting to cry for the school having burned down".
  * Section 4 discussion 4 — "the aspersions, hopes, and dreams" (for
    "aspirations"). This is the one most likely to be "corrected" by someone
    skim-reading, which is why it is named here.

THE BOOK IS ABOUT A REAL ERASURE. White Lilacs is Quakertown, in Denton, Texas:
a Black community bought out and cleared in 1921 to make a city park. The guide
does not soften its language and neither does this file — the discussion
questions say "Negroes", "Ku Klux Klan", "tarring and feathering", because the
1921 characters do. Read them before Kaylin does; the Glean options include
researching Quakertown itself, which is the point of the whole guide.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.utils import get_active_family
from curricula.models import Curriculum, CurriculumPlacement, Lesson
from curricula.services import apply_blueprint, get_blueprint
from students.models import Student
from tutor.models import Question, QuestionSet, ResponseSheet


MASTERY_NOTE = (
    "\n\nAssess mastery, not perfection — Beginning · Developing · Proficient · "
    "Mastered. Reward complete, thoughtful work that reaches past the minimum."
)

# The guide's own points, from its Grading Guidelines page.
JOURNAL_RUBRIC = """## Blackbird grading — Journal (4 points: Characters 2 · Setting 1 · Plot 1)
Section weights (20 pts): Read 4 · Journal 4 · Acquire 2 · Recollect 3 · Explore 7
(Writing 4, Discussion 3). Award the Read points for completing the section's reading.
- Characters: notes describe who a character IS — appearance, personality, and how they act, think and feel.
- Setting: where and when, and why the place matters. Freedomtown is not scenery; it is what the book is about.
- Plot: the major events in order — reminders, not a retelling.
- Bullet points are perfect.""" + MASTERY_NOTE

ACQUIRE_RUBRIC = """## Blackbird grading — Acquire (2 points)
Definitions in her OWN words, from a printed dictionary, plus a sentence for each
word that shows the meaning rather than repeats the definition.""" + MASTERY_NOTE

RECOLLECT_RUBRIC = """## Blackbird grading — Recollect (3 points)
Complete sentences, drawn from the book and her journal notes.

**There is no publisher answer key for this guide** — the family's copy is the
student workbook, so mark these against the book. Accept any answer that
captures the idea in her own words.""" + MASTERY_NOTE

WRITING_RUBRIC = """## Blackbird grading — Explore: Writing (4 points)
- **Accomplished (4)** — creatively focused; logical progression with supporting details; varied sentences; strong word choice; mature conventions.
- **Proficient (3)** — focused with adequate support; mostly logical; some sentence variety; general command of conventions.
- **Basic (2.5)** — topic addressed but unclear; weak support and progression; average word choice; partial command of conventions.
- **Limited (2)** — topic mentioned but not clearly addressed; weak organisation; fragments and run-ons.
- **Poor (1)** — topic not addressed or clearly supported; organisation lacking; frequent errors.

The guide's process: brainstorm → rough draft → conference → re-write → edit →
final draft. She writes the rough draft here; the final draft is copied out in
her best penmanship.""" + MASTERY_NOTE

DISCUSSION_RUBRIC = """## Blackbird grading — Explore: Discussion (3 points)
Oral, and the culmination of the week. There is no single right answer to any of
these. Award the points for thinking out loud, listening, and using the book.

Do encourage her to think. Don't settle for "I dunno." Don't worry if the
discussion goes a little off track as long as she is thinking creatively.""" + MASTERY_NOTE

GLEAN_RUBRIC = """## Blackbird grading — Glean: Final Project (20 points)
One or more of the guide's nine options, worth the whole of Section 5. Research,
writing and hands-on work all count equally — she chooses.""" + MASTERY_NOTE

JOURNAL_INTRO = (
    "As you read this section, keep notes here. Characters first, then Setting, "
    "then Plot — bullet points are perfect."
)
ACQUIRE_INTRO = (
    "Define each word using a printed dictionary, in your own words. Then use "
    "each one in a sentence that shows what it means."
)
RECOLLECT_INTRO = (
    "Answer the following questions using complete sentences. You may refer to "
    "both the book and your journal notes."
)
WRITING_INTRO = (
    "Write a complete paragraph based on the topic below. Remember to include a "
    "topic sentence, several supporting sentences, and a concluding sentence."
)
DISCUSSION_INTRO = "Think about and discuss the following questions."


# ---------------------------------------------------------------------------
# The guide, section by section. Everything here is the printed wording.
# ---------------------------------------------------------------------------

SECTIONS = [
    {   # ---------------------------------------------------- Section 1
        "number": 1,
        "chapters": "Chapters 1–5",
        "characters": "Grandfather Jim Williams · Aunt Tillie · Rose Lee Jefferson · Catherine Jane Bell",
        "setting_hint": (
            "Freedomtown and the white side of Dillon, Texas, in 1921 — and "
            "Grandfather's garden, which matters more than any of it."
        ),
        "vocab": ["counterpane", "colicky", "midwife", "Quaker", "radical", "veranda"],
        "recollect": [
            "What makes the white lilac so special?",
            "What does Mrs. Bell claim about her garden?",
            "What job is Rose Lee called upon to do for the first time?",
            "What topic of the women's conversation catches Rose Lee's attention?",
            "What four things do the women suggest be built in Freedomtown after they remove all the residents?",
            "What does Miss Firth say when Mrs. Bell says she cannot think of a single soul who would object to the plan?",
            "Where do most of the people of Freedomtown find work?",
            "How is Henry different from most of his family and why?",
            "What two places are Rose Lee's favorite?",
            "What important news does Rose Lee give the men at her father's barbershop?",
            "What does Miss Firth tell Rose Lee she would like to sketch while she's in the garden?",
            "What does Rose Lee share with Miss. Firth that she usually keeps hidden?",
            "What are Miss. Firth's thoughts of Rose Lee's tablet and what does she offer to do for her?",
            "What news does Pastor Mobley relay to Poppa and how would this affect the people of Freedomtown?",
        ],
        "writing_prompt": (
            "Henry and Miss Firth held opinions that were contrary to the "
            "majority. Write about a time when your opinion of something was "
            "different from other people's opinion."
        ),
        "discussion": [
            ("setting",
             "How are Grandfather's and Mrs. Bell's gardens different? Which do you prefer?"),
            ("theme",
             "Mrs Bell tries to explain to Miss Firth how Negroes in the south are different "
             "from Negroes in the north. How does She describe them? What do you think that "
             "means? How is that description demeaning?"),
            ("character",
             "According to Poppa, how is Henry's thinking different from theirs about “his "
             "place”? How do you think Henry's service in the war had broadened his thinking?"),
            ("application",
             "Rose Lee's favorite places were Grandpa's garden and Grandma's parlor. What are "
             "your two favorite places to spend time and why?"),
            ("theme",
             "Henry and Poppa have very different ideas about what black folks should do "
             "politically. What are those two different views?"),
            ("application",
             "Rose Lee had to give up the opportunity to take drawing lessons in order to work "
             "at the Bell's house. What is one thing you enjoy doing or are looking forward to "
             "that you would be sad or reluctant to give up?"),
            ("character",
             "What do you think Rose Lee felt about the big differences between her home and "
             "the Bell's home? What differences do you see?"),
            ("character",
             "Why do you think Catherine Jane and Rose Lee grew apart? What changed?"),
        ],
    },
    {   # ---------------------------------------------------- Section 2
        "number": 2,
        "chapters": "Chapters 6–10",
        "characters": "Henry · Rose Lee · Papa · Aunt Susannah",
        "setting_hint": (
            "The Bells' dining room, the Train Station, Forgiveness Baptist "
            "Church, and Freedomtown on Juneteenth."
        ),
        "vocab": ["benefactor", "blight", "carpetbaggers", "chenille",
                  "emancipation", "prohibition"],
        "recollect": [
            "What fears does Mrs. Bell express about Catherine Jane attending the academy in a year or two?",
            "What does Rose Lee notice about how the guests at dinner respond to her presence?",
            "What plans does Rose Lee's momma have for July 4th?",
            "What good news does Rose Lee's momma reveal amongst all the bad news?",
            "What does Juneteenth celebrate?",
            "How does Aunt Susannah stand out at the Train Station?",
            "How was Aunt Susannah's plan to stay at the boarding house going to affect Rose Lee's family?",
            "How does Mrs. Bell show here thoughtlessness on the eve of Juneteenth?",
            "What goodies does Rose Lee's momma fix on Juneteenth?",
            "How does Henry disrupt Sunday service on Juneteenth?",
            "Who visits Freedomtown the night of Juneteenth?",
            "What do the men of Freedomtown do before the vote is taken?",
            "What do the parents of Aunt Susannah's fiance threaten if they were to marry?",
            "What idea does Henry have for showing the white folk how much they need the Negroes?",
        ],
        "writing_prompt": (
            "Choose one of the following and write a detailed paragraph based "
            "on what you learn:\n\n"
            "1. Read about various Jim Crow laws. Choose one and detail the law "
            "and it's intent.\n"
            "2. Research Marcus Garvey and the “back to Africa” movement.\n"
            "3. Read “I, Too” by Langston Hughes. Describe the hopefulness in "
            "this poem. What would you say is Langston's mindset?"
        ),
        "discussion": [
            ("theme",
             "What do you think Mrs. Bell was implying about the people of Freedomtown when she "
             "says she's worried about Catherine Jane's safety and welfare? Do you think it's "
             "fair to judge a whole group of people because of irrational fear? Why or why not?"),
            ("character",
             "What do you think it was like for Rose Lee when she was present in the dining room "
             "while the guests talked about “the inhabitants of Freedomtown” as if she was "
             "invisible and couldn't hear or comprehend what they were saying? What do you think "
             "it feels like to feel invisible? How would you handle those emotions?"),
            ("character",
             "Why do you think Mrs. Bell compares Miss Firth to a carpetbagger? Do you think Miss "
             "Firth came to the south to profit off southerners? Why or why not?"),
            ("theme",
             "Rose Lee says that the people of Freedomtown were more than just neighbors and "
             "friends, they were like a big family. How would that make it worse if they were "
             "forced out? Why do you think this will be devastating?"),
            ("context",
             "Why do you think celebrating Juneteenth was much more meaningful for blacks than "
             "celebrating Memorial Day?"),
            ("application",
             "Rose Lee says she didn't believe Mrs. Eunice Bell was mean, just thoughtless. What "
             "do you think it means to be “thoughtless”? Does it have to do with thinking of "
             "others thoughts and needs? Does it take effort to be “thoughtful”? Discuss "
             "specific ways you can try to be more thoughtful in your everyday interactions with "
             "friends and family."),
            ("setting",
             "Discuss how the community church, Forgiveness Baptist Church, was integral to "
             "Freedomtown society."),
            ("context",
             "What do you think were the main goals of the Ku Klux Klan?"),
            ("theme",
             "What do you think it says about racism in the Northern states that Miss Firth's "
             "potential in-laws were against her marrying their white son, even though it was "
             "legal to have interracial marriage in the north?"),
            ("theme",
             "What do you think the larger point is that Henry is trying to argue to his parent "
             "about the work relationship all the black people have with the white people?"),
        ],
    },
    {   # ---------------------------------------------------- Section 3
        "number": 3,
        "chapters": "Chapters 11–15",
        "characters": "Aunt Tillie · Henry Jefferson · Rose Lee · Catherine Jane",
        "setting_hint": (
            "The 4th of July picnic, the Bells' office and library, and "
            "Freedomtown's school — before and after it burns."
        ),
        "vocab": ["coax", "shrewd", "souvenir", "suffragist", "undertaker", "vision"],
        "recollect": [
            "What does Aunt Tillie beg Rose Lee to do for her on July 4th?",
            "What does Rose Lee's Momma promise to save for her?",
            "What does Catherine Jane want to do with her hair?",
            "How does Miss Firth shock the townspeople at the picnic?",
            "What does Miss Firth's mother work for years to accomplish?",
            "Why does Henry go to the white people picnic?",
            "How does Grandpa come to marry Grandma?",
            "What does Rose Lee see early one morning while going to the privy?",
            "What does Catherine Jane ask Rose Lee to do for her before she leaves on her trip?",
            "What dreadful thing does Rose Lee find while cleaning Mrs. Bell's office/library?",
            "How much money is Mr. Lipscomb offered for his boarding house and how much does he say it is worth?",
            "What three reasons does Rose Lee give for wanting to cry for the school having burned down?",
            "What exotic dessert does Catherine Jane want for her birthday that Aunt Tillie thinks is impossible to bake?",
            "What does Catherine Jane do to show she is grown up?",
        ],
        "writing_prompt": (
            "Catherine Jane tries to assert her independence and maturity by "
            "cutting her hair into a bob. What is something you have done, or "
            "might do, to show your independence and maturity?"
        ),
        "discussion": [
            ("character",
             "Mrs. Bell says the following to Rose Lee the day of the 4th of July picnic: “I "
             "suppose Rose Lee will do, she's learning to be a good worker. And you won't come "
             "dragging in late will you? Can I trust you to do that Rose Lee? Not to make a mess "
             "of things?” How would you describe these comments? What do they imply? Do these "
             "comments carry a subtle message and what do you think that message is?"),
            ("character",
             "Where do you think Miss Firth developed her sense of justice? Who was her example "
             "and how do you think that taught Miss Firth about justice?"),
            ("application",
             "What do you think of Henry's plan to walk away from the white people's picnic with "
             "all the other black people? What would you have done if you were in a similar "
             "circumstance?"),
            ("context",
             "Tarring and feathering has been used for centuries as a way to punish and publicly "
             "humiliate a person. How did the white racists use this against Henry and what do "
             "you think they were trying to accomplish? Why do you think they were trying to "
             "crush his vision?"),
            ("theme",
             "What do you think of Miss Firth's idea of trying to make a record of drawings of "
             "Freedomtown? Why do you think it's important to make a record?"),
            ("character",
             "On one level, Catherine Jane sneaking Rose Lee up to see her new dresses is "
             "something girls might do, but on another level it was insensitive and cruel. What "
             "is Catherine Jane missing here? How do you think she was blinded to what she was "
             "doing? What do you think the expression “self-centeredness” means?"),
            ("theme",
             "What message is being communicated to the Freedomtown residents when their school "
             "is burned down?"),
        ],
    },
    {   # ---------------------------------------------------- Section 4
        "number": 4,
        "chapters": "Chapters 16–19",
        "characters": "Catherine Jane · Henry Jefferson · Rose Lee · Aunt Susannah",
        "setting_hint": (
            "Freedomtown being packed up and moved, the Flats, and the new "
            "school — the last of the town Rose Lee draws."
        ),
        "vocab": ["bitter", "charlatan", "counterpane", "dejected", "fancywork",
                  "porte cochere"],
        "recollect": [
            "How do the people of Freedomtown react to Rose Lee's Project to draw the town?",
            "What problems does Mr. Prince, the school principal, have about starting school again?",
            "What idea does Rose Lee have for her future after graduation?",
            "What honor is Grandfather given?",
            "What is the last picture Rose Lee draws of Freedomtown?",
            "Who was the only person who seemed to be happy about something?",
            "How does Grandfather try to improve his house at the Flats?",
            "What job does Poppa take once he has to close his barbershop?",
            "What does the family feel is the solution for Henry's situation?",
            "How does Rose Lee help with the plan to get Henry out of town?",
            "Whose help does Rose Lee seek and what does she ask that person to do?",
            "What danger is involved with the plan to secretly drive Henry to Blue Springs?",
            "What sacrificial gift does Rose Lee give Henry?",
            "What promise does Grandfather ask of Rose Lee?",
        ],
        "writing_prompt": (
            "Write about your neighborhood and what it feels like to be in it. "
            "Do you know any of your neighbors? Write about any wishes and "
            "dreams you may have for your neighborhood."
        ),
        "discussion": [
            ("theme",
             "What effect do you think it had on the sense of community and family cohesiveness "
             "when everyone started packing up and moving from Freedomtown? How might uprooting "
             "the community set people back in their lives?"),
            ("character",
             "Why do you think Rose Lee considered her job as an artist to be just as important "
             "as going to school?"),
            ("application",
             "Imagine coming to school and having no books and no supplies to work with. Imagine "
             "you were only able to learn from your teacher and what knowledge they had. What do "
             "you think that would be like? Do you think having textbooks is important to "
             "education? Why or why not?"),
            ("theme",
             "Why does it matter what the people of Freedomtown call their new school? How might "
             "a certain name express the aspersions, hopes, and dreams of the students who will "
             "attend that school?"),
            ("theme",
             "What is the purpose of the “album quilt” Grandmother sent with the Ragsdales? "
             "What will it be a reminder of?"),
            ("setting",
             "Why do you think it's important for Grandfather to plant a new garden at the "
             "Flats? How does bringing in trees and plants from Freedomtown ultimately help "
             "people?"),
            ("theme",
             "What do you think about how the Janitors were treated at the academy?"),
            ("application",
             "How do Henry, Rose Lee and Catherine Jane express bravery in the face of real "
             "danger? Have you ever been daring and brave? Share about it."),
            ("character",
             "Rose Lee gives her drawing book to Henry before he leaves, why do you think she "
             "did that? What purpose would having that book serve for Henry?"),
        ],
    },
]


GLEAN_OPTIONS = [
    "Research the Suffragist movement. Create an illustrated timeline of the movement.",
    "Start a sketchbook of the houses or apartments in your neighborhood. Write about your observations.",
    "If you can, interview one of your grandparents and ask them about where and when they grew up. Write about what you learn about their lives growing up.",
    "Research the Civil Rights movement and create a timeline of some of the most significant events, roughly from the late 1940's to the late 1960's.",
    "Research Booker T. Washington or Frederick Douglass and make a poster about their lives.",
    "Research W. E. B. DuBois and his founding of the NAACP. Write a small essay about the goals and accomplishments of the NAACP.",
    "Research Quakertown in Denton, Texas. Write about what you learned.",
    "Research what an “album quilt” is and make a paper quilt of your own design or you could have family and friends make a square for you that you will incorporate into your quilt.",
    "Make a diorama of your favorite scene from the book. Write a personal reflection.",
]


class Command(BaseCommand):
    help = "Seed the Blackbird 'White Lilacs' course for Kaylin (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--for-user", required=True,
                            help="Username who owns the curriculum.")
        parser.add_argument("--child-name", default="Kaylin",
                            help="Child to place in the course.")

    @transaction.atomic
    def handle(self, *args, **options):
        from django.contrib.auth import get_user_model

        User = get_user_model()
        try:
            user = User.objects.get(username=options["for_user"])
        except User.DoesNotExist:
            raise CommandError("User '%s' does not exist." % options["for_user"])

        blueprint = get_blueprint("blackbird_white_lilacs")
        family = get_active_family(user)
        curriculum, created = Curriculum.objects.get_or_create(
            parent=user, name=blueprint["name"],
            defaults={
                "subject": blueprint["subject"],
                "grade_level": blueprint["grade_level"],
                "family": family,
            },
        )
        chapters, lessons = apply_blueprint(curriculum, blueprint)
        self.stdout.write(
            "%s curriculum #%d (%d sections, %d lessons)."
            % ("Created" if created else "Using", curriculum.pk, chapters, lessons))

        child = Student.objects.filter(
            parent=user, first_name__iexact=options["child_name"]).first()
        if child is None:
            raise CommandError(
                "No child named '%s' found for %s."
                % (options["child_name"], user.username))
        first_lesson = Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=1, order=1)
        CurriculumPlacement.objects.get_or_create(
            child=child, curriculum=curriculum,
            defaults={"current_lesson": first_lesson})

        sets = questions = 0
        for section in SECTIONS:
            n, chs = section["number"], section["chapters"]

            s, q = self._seed_set(
                self._lesson(curriculum, n, 2), family,
                title="Section %d · Journal" % n,
                reading=chs, intro=JOURNAL_INTRO, rubric=JOURNAL_RUBRIC,
                questions=[
                    ("character",
                     "CHARACTERS — as you read, note interesting and important things "
                     "you learn about the characters. Describe such things as their "
                     "personality and appearance, including details about the way they "
                     "act, think, and feel.",
                     "Bullet points are perfect. Describe who each person IS — save what "
                     "they DO for Plot.",
                     {"response_type": Question.TYPE_CHARACTERS,
                      "passage": section["characters"]}),
                    ("setting",
                     "SETTING — as you read, note where the story is happening. Explain "
                     "how the setting is significant to the story and include any "
                     "descriptive details you find.",
                     section["setting_hint"]),
                    ("plot",
                     "PLOT — summarize what happens in this section of the story.",
                     "Major events only — simple reminders, not a retelling."),
                ],
            )
            sets += s; questions += q

            s, q = self._seed_set(
                self._lesson(curriculum, n, 3), family,
                title="Section %d · Acquire: Vocabulary" % n,
                reading=chs, intro=ACQUIRE_INTRO, rubric=ACQUIRE_RUBRIC,
                questions=[
                    ("vocabulary",
                     "**%s** — define it in your own words, then use it in a sentence "
                     "that shows what it means." % word,
                     "Printed dictionary, not a search box. The sentence should make the "
                     "meaning obvious to someone who did not look it up.")
                    for word in section["vocab"]
                ],
            )
            sets += s; questions += q

            s, q = self._seed_set(
                self._lesson(curriculum, n, 4), family,
                title="Section %d · Recollect: Comprehension" % n,
                reading=chs, intro=RECOLLECT_INTRO, rubric=RECOLLECT_RUBRIC,
                questions=[
                    ("comprehension", prompt,
                     "Complete sentences. You may look back at the book and at your "
                     "journal notes.")
                    for prompt in section["recollect"]
                ],
            )
            sets += s; questions += q

            s, q = self._seed_set(
                self._lesson(curriculum, n, 5), family,
                title="Section %d · Explore: Writing" % n,
                reading=chs, intro=WRITING_INTRO, rubric=WRITING_RUBRIC,
                questions=[
                    ("writing", section["writing_prompt"],
                     "Rough draft first. Read it aloud to someone, change what needs "
                     "changing, then copy out the final draft in your best penmanship."),
                ],
            )
            sets += s; questions += q

            s, q = self._seed_set(
                self._lesson(curriculum, n, 5), family,
                title="Section %d · Explore: Discussion" % n,
                reading=chs, intro=DISCUSSION_INTRO, rubric=DISCUSSION_RUBRIC,
                mode=QuestionSet.MODE_DISCUSSION,
                questions=[
                    (category, prompt, "Oral. There is no single right answer.")
                    for category, prompt in section["discussion"]
                ],
            )
            sets += s; questions += q

        glean = self._lesson(curriculum, 5, 1)
        s, q = self._seed_set(
            glean, family,
            title="Section 5 · Glean: Final Project",
            reading="The whole book",
            intro=("Complete one or more of the following assignments. Section 5 "
                   "is worth as much as a whole week, so pick something you want "
                   "to spend real time on."),
            rubric=GLEAN_RUBRIC,
            questions=[
                ("application", "**Option %d.** %s" % (i, option),
                 "Only if you choose this one — you do not have to do them all.")
                for i, option in enumerate(GLEAN_OPTIONS, start=1)
            ],
        )
        sets += s; questions += q

        # One more Glean option beside the guide's nine: the same thing she
        # MAKES rather than writes. The guide's own options are kept exactly as
        # printed, so the record still shows the purchased guide followed — she
        # picks.
        from tutor import glean_handson

        hands_on = glean_handson.hands_on_title("white_lilacs")
        glean_handson.retire_superseded(glean, hands_on)
        s, q = self._seed_set(
            glean, family,
            title=hands_on,
            reading="",
            intro=glean_handson.BOOKS["white_lilacs"]["intro"],
            rubric=glean_handson.BOOKS["white_lilacs"]["rubric"],
            questions=glean_handson.questions("white_lilacs"),
        )
        sets += s; questions += q

        # The house literature standard: a Socratic story-grammar seminar and
        # the literary toolbox, both oral, both scaled to her grade. Every other
        # Blackbird book here carries them, and `apply_literature_standard`
        # exists to be called exactly at this moment.
        from tutor import literature

        s, q = literature.apply_literature_standard(
            curriculum, child.grade_level, family=family)
        sets += s; questions += q

        # No CurriculumResource here: the other Blackbird guides link the
        # publisher's answer key, and this one has none to link — the family's
        # copy is the student workbook. Saying so belongs where a parent
        # actually reads it, which is the Recollect rubric, not a link with no
        # URL behind it.
        self.stdout.write(self.style.SUCCESS(
            "White Lilacs seeded for %s — %d question sets, %d questions."
            % (child.first_name, sets, questions)))

    def _lesson(self, curriculum, chapter_number, order):
        return Lesson.objects.get(
            chapter__curriculum=curriculum, chapter__number=chapter_number,
            order=order)

    def _seed_set(self, lesson, family, *, title, reading, intro, rubric,
                  questions, mode=QuestionSet.MODE_STUDENT, answer_key=""):
        qset, _ = QuestionSet.objects.update_or_create(
            lesson=lesson, title=title,
            defaults={
                "family": family, "intro": intro, "reading": reading,
                "rubric": rubric, "answer_key": answer_key,
                "status": QuestionSet.APPROVED, "mode": mode,
            },
        )
        count = 0
        for i, item in enumerate(questions, start=1):
            category, prompt, hint = item[0], item[1], item[2]
            extra = item[3] if len(item) > 3 else {}
            Question.objects.update_or_create(
                question_set=qset, order=i,
                defaults={
                    "category": category, "prompt": prompt, "hint": hint,
                    "response_type": extra.get("response_type", Question.TYPE_TEXT),
                    "passage": extra.get("passage", ""),
                },
            )
            count += 1
        # Drop stale rows beyond the current list — but never one she has
        # already answered, which would orphan her response.
        stale = qset.questions.filter(order__gt=len(questions))
        answered = set()
        for sheet in ResponseSheet.objects.filter(question_set=qset):
            answered |= {int(k) for k, v in (sheet.answers or {}).items()
                         if str(v).strip() and str(k).isdecimal()}
        stale.exclude(pk__in=answered).delete()
        return 1, count

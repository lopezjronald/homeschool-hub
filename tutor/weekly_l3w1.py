"""Studies Weekly Level 3, Week 1 — Developing Inquiries.

California Studies Weekly: Past and Present / Continuity and Change. Unit 1
("Inquiry"), Lesson 1.1. Violet's.

A DIFFERENT SHAPE FROM KAYLIN'S. Level 7 week 1 is one long article and a check
that leans on its maps. This issue is five short articles across four pages —
What Is an Inquiry?, Types of Questions, Make a Claim, Different Lenses, The
Inquiry Process — and its eight-question check is about the process itself, so
only one question has a picture.

The questions and their wording are the student page's (1.20-1.22); the answers
are the teacher edition's marked answers (1.8-1.9). The vocabulary is the
teacher edition's Student Edition Vocabulary list (1.7), verbatim, plus
"evidence" — the check tests it and the article defines it, but the list leaves
it out.

ONE THING WORTH NOT "CORRECTING". The inquiry process puts **Make a claim** at
step 2 — before searching for answers — which looks wrong if you expect a claim
to follow its evidence. It is not a transcription slip: the article numbers the
five steps 1-5 with "Make a claim" second (issue page 4), and the answer key
lists them the same way. This curriculum teaches the claim as a starting
position you then test and may change, which is exactly what question 8 checks.

Digitized from the family's purchased Studies Weekly issue for private use.
"""

from .weekly import choice, fill_two, matching, order, written, figure, page_images

LEVEL = 3
WEEK = 1
UNIT = 1
LESSON = "1.1"
TITLE = "Developing Inquiries"
SUBTITLE = "What Is an Inquiry?"
ESSENTIAL_QUESTION = "What is inquiry?"
PUBLICATION = "California Studies Weekly: Past and Present"

# Four article pages: the three-part inquiry, types of questions, making a
# claim, the five lenses, and the numbered process. Kept as scans — the lenses
# are laid out as five illustrated panels of questions, and retyping them as
# prose would throw the whole point of the page away.
PAGES = page_images(LEVEL, WEEK, 4)

STUDENT_NOTE = ("Nearly every question is about the words this week — inquiry, "
                "compelling, claim, evidence — so read the word list before you "
                "start.")
PARENT_NOTE = """**Where the answers come from.** All eight come out of the
articles rather than off a picture or a chart, so a wrong answer here is a
reading question, not a looking-at-the-picture one. The two worth talking about
are 1 and 8: the process puts *make a claim* SECOND, before the research, and
question 8 is why — a claim is a starting position she is allowed to change when
the evidence says so. If she puts "make a claim" last, she has the sensible
grown-up answer and not this curriculum's."""
GRADER_NOTE = ("The written task asks her to pick a lens and give a compelling "
               "question of her own. A compelling question is one that could "
               "not be answered in a sentence, so look for whether hers has "
               "room to be investigated — not whether it is tidy.")

# The teacher edition's Student Edition Vocabulary (1.7), verbatim. "evidence"
# is the article's own sentence (issue page 1); question 7 assesses it.
VOCABULARY = [
    ("inquiry", "a way to investigate a problem or to ask for more information"),
    ("compelling question", "the big question that guides inquiry"),
    ("supporting question", "questions that look at a smaller part of a "
                            "compelling question and help make the compelling "
                            "question clearer"),
    ("claim", "a statement about what we believe"),
    ("evidence", "the facts we see that help us find answers to our questions"),
    ("reflect", "to think a lot about something"),
]

# The five researchers the "Different Lenses" article introduces, each with the
# one question the check pairs them with. Question 2 is built from these.
LENSES = [
    ("economist", "How do people make money?"),
    ("historian", "When did it happen?"),
    ("social scientist", "How did that impact people?"),
    ("political scientist", "How are laws created?"),
    ("geographer", "Where is it?"),
]

# The inquiry process, in the article's own numbering.
STEPS = [
    "Ask a compelling question",
    "Make a claim",
    "Search for answers / Experiment",
    "Interpret the information",
    "Present your conclusions",
]

# The check's word banks, in the order they are printed. Question 3 prints ONE
# bank of four and uses it for both blanks.
BANK_Q3 = ["supporting", "mystery", "compelling", "research"]

# What the teacher edition says this week assesses (1.6). History-Social Science
# is marked N/A — week 1 teaches the method rather than any content — so the
# standards are the two ELA ones, and each question is filed under the one it
# actually calls for.
RI_3_1 = ("RI.3.1 Ask and answer questions to demonstrate understanding of a "
          "text, referring explicitly to the text as the basis for the answers.")
W_3_2 = ("W.3.2 Write informative/explanatory texts to examine a topic and "
         "convey ideas and information clearly.")

QUESTIONS = [
    order(
        "Place the steps to the inquiry process in order.",
        # As printed on 1.20 — scrambled; she numbers them.
        steps=["Make a claim",
               "Present your conclusions",
               "Ask a compelling question",
               "Search for answers / Experiment",
               "Interpret the information"],
        correct=STEPS,
        hint="Start with the question you want answered. The last one is where "
             "you tell somebody what you found out.",
        standard=RI_3_1,
    ),
    matching(
        "Match the person to the question they ask.",
        pairs=LENSES,
        # As printed on 1.20.
        word_order=["How are laws created?", "How do people make money?",
                    "Where is it?", "How did that impact people?",
                    "When did it happen?"],
        hint="Each name tells you what that person studies. An economist "
             "studies money; a geographer studies places.",
        standard=RI_3_1,
    ),
    fill_two(
        "A ______ question guides inquiry. ______ questions look at smaller "
        "parts of the big question.",
        bank_a=BANK_Q3,
        bank_b=BANK_Q3,
        correct_a="compelling",
        correct_b="supporting",
        hint="One of them is the BIG question. The other kind breaks the big "
             "one into pieces you can go and find out about.",
        standard=RI_3_1,
    ),
    choice(
        "What might be a compelling question based on this image?",
        options=[
            ("a", "Where are these mountains?"),
            ("b", "How did mountains form in California?"),
            ("c", "When does it rain in these mountains?"),
            ("d", "What town is closest to these mountains?"),
        ],
        correct="b",
        figure=figure(LEVEL, WEEK, "q4-mountains"),
        figure_caption="Mountains in California",
        hint="A compelling question is a big one — it takes real investigating "
             "to answer. Three of these could be answered in one sentence.",
        standard=RI_3_1,
    ),
    choice(
        "The ______ lens is used when researching how people use natural "
        "resources.",
        # As printed on 1.21 — a word bank, not letters.
        options=[
            ("a", "historian"),
            ("b", "geographer"),
            ("c", "economist"),
            ("d", "social scientist"),
        ],
        correct="c",
        hint="Using resources is about what people make, buy and sell — that is "
             "the lens that thinks about money and goods.",
        standard=RI_3_1,
    ),
    choice(
        "What question should be answered when presenting conclusions?",
        options=[
            ("a", "What is the main idea?"),
            ("b", "What do I already know?"),
            ("c", "What is a possible answer?"),
            ("d", "Where can I find resources?"),
        ],
        correct="a",
        hint="Presenting is the LAST step. Look at step 5 in the article — the "
             "other three are questions from the steps before it.",
        standard=RI_3_1,
    ),
    choice(
        "Claims must be supported by ______.",
        # As printed on 1.22 — a word bank, not letters.
        options=[
            ("a", "lenses"),
            ("b", "evidence"),
            ("c", "tasks"),
            ("d", "supporting questions"),
        ],
        correct="b",
        hint="It is one of your words this week: the facts we see that help us "
             "find answers.",
        standard=RI_3_1,
    ),
    choice(
        "Claims can be changed during an inquiry.",
        options=[("a", "TRUE"), ("b", "FALSE")],
        correct="a",
        hint="What happens if you go looking and find out something that "
             "surprises you? Read the part about reflecting.",
        standard=RI_3_1,
    ),
]

# The issue's own "Let's Write" task (teacher edition 1.8), which the printed
# assessment leaves off. It is the only place this week she writes anything of
# her own, so it carries the type-it/write-it picker.
REFLECTION = written(
    "**Let's write.** Choose one of the lenses — historian, geographer, "
    "political scientist, social scientist, or economist. Write a paragraph "
    "that shares a compelling question you have and why it is interesting to "
    "you.",
    hint="Pick the lens that matches the kind of thing you wonder about. Then "
         "check your question: if you could answer it in one sentence, it is "
         "not compelling yet — make it bigger.",
    standard=W_3_2,
)

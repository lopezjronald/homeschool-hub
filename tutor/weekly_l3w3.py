"""Studies Weekly Level 3, Week 3 — Unit 1 (Inquiry), Lesson 3.

Examining Evidence and Communicating Conclusions. Studies Weekly Third Grade:
Our Community — People and Places. Violet's.

Two questions on this check are OPEN (4 and 6). The teacher edition does not
give a single right answer for either — it gives a sample, prefixed "Answers may
include but are not limited to" — so those are recorded as written questions and
the sample is passed to the grader rather than pretended to be the answer.

The questions are the printed Weekly Assessment (3.10-3.12); the closed answers
are the teacher edition's red-marked key (lesson plan p.2), extracted by colour.

Digitized from the family's purchased Studies Weekly issue for private use.
"""

from .weekly import choice, part, video, written

LEVEL = 3
WEEK = 3
UNIT = 1
UNIT_TITLE = "Inquiry"
LESSON = "3"
TITLE = "Examining Evidence and Communicating Conclusions"
SUBTITLE = "Searching for Answers"
ESSENTIAL_QUESTION = "What does it mean to interpret information?"
PUBLICATION = "Studies Weekly Third Grade: Our Community — People and Places"

HSS = "HSS Analysis Skills (K-5): Research, Evidence, and Point of View"
RI = "CCSS RI.3.1 — ask and answer questions, referring to the text"
W = "CCSS W.3.8 — gather information from sources"

PAGES = ["weekly/l3w3/page%d.jpg" % n for n in range(1, 4)]

# Verified against YouTube's oEmbed endpoint. Question 1 of her own assessment
# is "All information on the internet is reliable. True/False" — this is that
# question, animated. Pitched a little older than she is: watch it WITH her, and
# the one idea to land is that a rumour repeated by a hundred people is still
# one rumour.
WATCH_3 = video(
    "cSKGa_7XJkg",
    "How false news can spread",
    channel="TED-Ed",
    length="4 minutes",
    why=("A made-up fact gets copied by one website, then another, then a "
         "newspaper — and suddenly it looks true because it is *everywhere*. "
         "Watch how that happens, then decide how you would tell."),
    question=("If lots of places say the same thing, does that make it true? "
              "What would you check?"),
)

PARTS = [
    part("3.1", "Examining Evidence and Communicating Conclusions",
         pages=PAGES[:2], watch=WATCH_3,
         intro=("Where to look for information, and what to do with it once "
                "you have found it: analyze, evaluate, connect."),
         vocabulary=[
             ("interpret", "to decide what information means"),
             ("close reading", "focusing on the important details in the text"),
             ("annotations", "responses to different parts of what you read"),
             ("sequence", "how ideas or events follow each other"),
             ("context", "information that affects how a source is presented — "
                         "when, where and why it was made"),
             ("historical context", "the events or trends that were happening "
                                    "when the source was made"),
             ("reliable", "something you can trust"),
             ("evaluate", "to determine which information is most useful to you"),
             ("evidence", "information or data that supports a claim"),
         ]),
    part("3.2", "Searching for Answers", pages=PAGES[2:], activity=True,
         intro=("Take the compelling question — can kids make a difference in "
                "their community? — and go looking for evidence."),
         vocabulary=[]),
]

STUDENT_NOTE = ("Two of these questions want you to write a real answer, not "
                "pick one. Take your time on those.")
PARENT_NOTE = """**Watch the film with her.** It is pitched a little older than
eight, and it is the exact content of question 1 on her check. The one idea to
land is that a rumour repeated by a hundred websites is still one rumour — ask
her the question underneath it.

**Questions 4 and 6 are open, and the teacher edition does not give one right
answer.** For 4 it suggests kids helping their parents, or volunteering in their
community. For 6 it suggests browsing safely and finding reliable sources. Both
are samples, not the answer — credit anything she can back up.

**The compelling question is worth doing for real.** "Can kids make a difference
in their community?" is the article's running example, and question 4 asks her
for evidence supporting it. If she can name a real thing a real kid did, that IS
the lesson working."""
GRADER_NOTE = ("Questions 4 and 6 are open. The teacher edition gives samples "
               "only — for 4, kids helping parents or volunteering; for 6, "
               "browsing safely and finding reliable sources. Credit any answer "
               "she supports, not just those.")

# --------------------------------------------------------------------------
# Week 3 Assessment, verbatim (3.10-3.12).
# --------------------------------------------------------------------------

QUESTIONS = [
    choice(
        "All information on the internet is reliable.",
        options=[("a", "True"), ("b", "False")],
        correct="b",
        hint="The Internet research paragraph says it straight out. And think "
             "about the film you watched.",
        standard=HSS,
    ),
    choice(
        "Choose the word that best completes the sentence. Analyzing, "
        "evaluating, and connecting are used to __________ information.",
        options=[
            ("a", "consider"),
            ("b", "eliminate"),
            ("c", "interpret"),
            ("d", "produce"),
        ],
        correct="c",
        hint="Those three words are the three headings under one big heading. "
             "What is that big heading called?",
        standard=HSS,
    ),
    choice(
        "Identify the compelling question.",
        options=[
            ("a", "What are problems in the community?"),
            ("b", "What does it mean to “make a difference”?"),
            ("c", "What have kids done to make a difference?"),
            ("d", "Can kids make a difference in their community?"),
        ],
        correct="d",
        hint="A compelling question is the BIG one; the others are the smaller "
             "questions that help you answer it. Which one is the big one on "
             "page 2?",
        standard=HSS,
    ),
    written(
        "What evidence supports the claim that kids can make a difference?",
        hint="Evidence means real examples. Think of something a kid has "
             "actually done — helping at home, cleaning something up, raising "
             "money, looking after someone.",
        standard="%s · %s" % (HSS, W),
    ),
    choice(
        "Choose the word that best completes the sentence. "
        "A __________ source is reliable.",
        options=[
            ("a", "hated"),
            ("b", "known"),
            ("c", "liked"),
            ("d", "trusted"),
        ],
        correct="d",
        hint="The article says reliable means “something you can trust”. "
             "Which of these words means the same thing?",
        standard=HSS,
    ),
    written(
        "Why do kids need the help of teachers and parents to browse the "
        "internet?",
        hint="The Internet research paragraph gives two reasons — one about "
             "whether what you find is true, and one about staying safe.",
        standard="%s · %s" % (HSS, RI),
    ),
    choice(
        "What does “evaluate” mean?",
        options=[
            ("a", "to support conclusions with evidence"),
            ("b", "to focus on important details in the text"),
            ("c", "to learn the definition of unknown words"),
            ("d", "to determine the most useful information"),
        ],
        correct="d",
        hint="Careful — option b is the definition of CLOSE READING. Find the "
             "Evaluating box and read its first sentence.",
        standard=HSS,
    ),
    choice(
        "Choose the word that best completes the sentence. The __________ is a "
        "reliable source to learn about local community problems.",
        options=[
            ("a", "local news"),
            ("b", "national newspaper"),
            ("c", "school textbook"),
            ("d", "state governor"),
        ],
        correct="a",
        hint="The word doing the work is **local**. Which of these is about "
             "your own town rather than the whole country?",
        standard=HSS,
    ),
]

REFLECTION = written(
    "Pick one problem you have actually noticed in our community. Write four or "
    "five sentences: what the problem is, where you would go to find out more "
    "about it (name a real place or source), and one thing a kid your age could "
    "do about it.",
    hint="The article gives you three places to look — the news, a library, and "
         "the internet with a grown-up. Which would help most with YOUR problem?",
    standard="%s · %s" % (HSS, W),
)

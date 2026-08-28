"""Studies Weekly Level 3, Week 2 — Unit 1 (Inquiry), Lesson 2: Sources.

Studies Weekly Third Grade: Our Community — People and Places. Violet's.

A NOTE ON THE PUBLICATION. Week 1's module names this course "California
Studies Weekly: Past and Present"; these issues call themselves "Our Community:
People and Places" on every page, and the assessment header says "Studies Weekly
Third Grade: People And Places". Each week is recorded with the wording printed
on it rather than quietly unified — if that is a subscription change, the record
should show it.

Kaylin is doing the same unit at Level 7 the same fortnight (weekly_l7w2), which
is a real opportunity: both girls are on primary vs secondary sources and
perspective at once, at their own reading levels.

The questions and their wording are the printed Weekly Assessment (2.12-2.13);
the answers are the teacher edition's own answer key, which marks the correct
option in RED on page 2 of the lesson plan — extracted by colour rather than by
eye. The vocabulary is the article's own bolded terms.

Digitized from the family's purchased Studies Weekly issue for private use.
"""

from .weekly import choice, figure, part, video, written

LEVEL = 3
WEEK = 2
UNIT = 1
UNIT_TITLE = "Inquiry"
LESSON = "2"
TITLE = "Sources"
SUBTITLE = "Thinking Like a Historian"
ESSENTIAL_QUESTION = "How does asking questions about history help us?"
PUBLICATION = "Studies Weekly Third Grade: Our Community — People and Places"


def F(name):
    return figure(LEVEL, WEEK, name)


HSS = "HSS Analysis Skills (K-5): Historical Interpretation"
CRP = "HSS Analysis Skills (K-5): Research, Evidence, and Point of View"
RI = "CCSS RI.3.1 — ask and answer questions, referring to the text"

PAGES = ["weekly/l3w2/page%d.jpg" % n for n in range(1, 4)]

# Verified against YouTube's oEmbed endpoint: this id really is this video on
# TED-Ed. Chosen over the usual "what is a primary source" tutorial because
# those are a definition read aloud, and this is the definition in action —
# archaeologists working out how children lived from the toys they left behind,
# which is exactly what page 4 asks her to do with photographs of the 1920s.
WATCH_2 = video(
    "aob7rM5PV5A",
    "What toys have kids played with throughout history?",
    channel="TED-Ed",
    length="5 minutes",
    why=("Nobody wrote down what it was like to be a kid 5,000 years ago. So "
         "how do we know? From their **toys** — a little clay carriage, a "
         "whistle, a board game, dug up thousands of years later. Those toys "
         "are primary sources, and this is you doing a historian's job."),
    question=("The people who made those toys left no diary and no photograph. "
              "What did the toys tell us anyway?"),
)

PARTS = [
    part("2.1", "Sources", pages=PAGES[:2], watch=WATCH_2,
         intro=("Primary and secondary sources, how historians examine them, "
                "and why more than one perspective matters."),
         vocabulary=[
             ("historians", "people who identify, select, analyze, and evaluate "
                            "sources to understand the past"),
             ("primary sources", "sources created by people who saw or "
                                 "experienced something themselves"),
             ("secondary sources", "sources made by people who did not see or "
                                   "experience the event themselves"),
             ("analyze", "to study something carefully"),
             ("perspective", "a way of seeing things — everyone has their own"),
         ]),
    part("2.2", "Life for Children in the 1920s", pages=PAGES[2:],
         activity=True,
         intro=("Be the historian. Look at real photographs of school, work "
                "and play a hundred years ago, and work out what they tell you."),
         vocabulary=[]),
]

STUDENT_NOTE = ("Look at the photographs properly before you answer — they are "
                "the evidence, not decoration.")
PARENT_NOTE = """**The film is the way in.** It shows archaeologists working out
how ancient children lived from the toys they left behind — which is exactly the
move page 4 asks of Violet with photographs of the 1920s. Ask her the question
under the video before she reads anything.

**Part 2.2 is a looking exercise, not a reading one.** The photographs of
children in 1920s schools, cotton mills and streets are the whole lesson. The
strongest question on the page is the last one: *what primary sources could a
historian use to write about YOUR life?* That one is worth saying out loud.

**Where the answers come from.** Question 6 is read off a photograph, not the
article. Everything else is in the two-page spread."""
GRADER_NOTE = ("Question 6 asks her to draw a conclusion from a photograph. "
               "Look for whether she points at something the picture actually "
               "shows rather than repeating a sentence from the article.")

# --------------------------------------------------------------------------
# Week 2 Assessment, verbatim (2.12-2.13). Answers are the teacher edition's
# own red-marked key (lesson plan p.2).
# --------------------------------------------------------------------------

QUESTIONS = [
    choice(
        "Choose the word that best completes the sentence. "
        "A(n) __________ is an example of a secondary source.",
        options=[
            ("a", "bibliography"),
            ("b", "interview"),
            ("c", "journal"),
            ("d", "letter"),
        ],
        correct="a",
        hint="A secondary source is made by somebody who was NOT there. Three "
             "of these come straight from a person who was.",
        standard=HSS,
    ),
    choice(
        "Which characteristic do historians display when asking questions?",
        options=[
            ("a", "carelessness"),
            ("b", "curiosity"),
            ("c", "respect"),
            ("d", "responsibility"),
        ],
        correct="b",
        hint="Which of these words means wanting to know more?",
        standard=HSS,
    ),
    choice(
        "Choose the phrase that best completes the sentence. "
        "Historians analyze sources by __________.",
        options=[
            ("a", "asking questions"),
            ("b", "finding answers"),
            ("c", "generating solutions"),
            ("d", "discovering problems"),
        ],
        correct="a",
        hint="Look at the blue boxes on the spread — Author/Creator, Purpose, "
             "Format. What is inside every one of them?",
        standard=HSS,
    ),
    choice(
        "Only one perspective is important when learning about history.",
        options=[("a", "True"), ("b", "False")],
        correct="b",
        hint="The Multiple Perspectives box says looking at several gives us a "
             "\"deeper understanding\". So is one enough?",
        standard=CRP,
    ),
    choice(
        "Art can be an important piece of evidence.",
        options=[("a", "True"), ("b", "False")],
        correct="a",
        hint="Think about the painting of Washington crossing the river on the "
             "cover. Could a historian learn anything from it?",
        standard=HSS,
    ),
    choice(
        "Which conclusion is supported by this image?",
        options=[
            ("a", "There were no schools for children."),
            ("b", "Men did not participate in family life."),
            ("c", "More girls than boys were born to families."),
            ("d", "Women worked to help support their family."),
        ],
        correct="d",
        figure=F("q6-family"),
        figure_caption="A family at home",
        hint="Only count what the photograph actually SHOWS. What is the woman "
             "in the middle doing with her hands?",
        standard="%s · %s" % (HSS, RI),
    ),
    choice(
        "Which question is not important when analyzing sources?",
        options=[
            ("a", "Who is the author?"),
            ("b", "When was it created?"),
            ("c", "Where is the source located?"),
            ("d", "Is it a primary or secondary source?"),
        ],
        correct="c",
        hint="Three of these are on the spread's blue question boxes. One of "
             "them is about where the thing is kept, which does not tell you "
             "anything about whether to trust it.",
        standard=HSS,
    ),
    choice(
        "Mary shared her beach trip with the class. Luis told his mother about "
        "Mary's trip. Luis is a primary source.",
        options=[("a", "True"), ("b", "False")],
        correct="b",
        hint="Who actually went to the beach? Luis is telling somebody about "
             "somebody else's trip.",
        standard=HSS,
    ),
]

REFLECTION = written(
    "The last question on page 4 asks: **what primary sources could a historian "
    "use to write about YOUR life?** Write three or four sentences answering it. "
    "Name at least two real things — something in this house, or on a phone, or "
    "in a drawer — and say what each one would tell a historian about you.",
    hint="Think about what somebody a hundred years from now would find. A "
         "photograph? A drawing you made? A message? What would each one give "
         "away about how you lived?",
    standard="%s · %s" % (CRP, RI),
)

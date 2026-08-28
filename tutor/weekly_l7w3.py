"""Studies Weekly Level 7, Week 3 — Unit 1, Lesson 3: What Is an Inquiry?

California Studies Weekly: World History and Geography, Medieval and Early
Modern Times. Kaylin's.

Lesson 3 has two parts of different kinds: 3.1 is the article, 3.2 is a printed
ACTIVITY — build a poster explaining the inquiry process to someone who has
never heard of it. The activity is marked as such so the booklet can say "make"
rather than "read", and so nobody expects a comprehension check to cover it.

Transcribed from the family's issue; the check is the printed wording (pp.
1.40-1.41). Digitized from the family's purchased issue for private use.
"""

from .weekly import choice, figure, part, video, written

LEVEL = 7
WEEK = 3
UNIT = 1
UNIT_TITLE = "Historical Thinking Skills"
LESSON = "3"
TITLE = "What Is an Inquiry?"
SUBTITLE = "Becoming a History Detective"
ESSENTIAL_QUESTION = "How do we know what happened in the past?"
PUBLICATION = "California Studies Weekly: Medieval and Early Modern Times"


def F(name):
    return figure(LEVEL, WEEK, name)


HSS = "HSS Analysis Skills: Historical Interpretation"
RH = "CCSS RH.6-8.1 — cite textual evidence"
WHST = "CCSS WHST.6-8.7 — conduct short research projects"
C3 = "C3 D1 — developing questions and planning inquiries"

PAGES = ["weekly/l7w3/page%d.jpg" % n for n in range(1, 9)]

# Verified against YouTube's oEmbed endpoint: this id is this video on TED-Ed.
WATCH_3_1 = video(
    "jvWncVbXfJ0",
    "What really happened to the Library of Alexandria?",
    channel="TED-Ed",
    length="5 minutes",
    why=("Everyone \"knows\" the greatest library of the ancient world burned "
         "down in one dramatic fire. Almost none of that is settled — the "
         "evidence is thin, the sources disagree, and historians are still "
         "arguing. This is what a compelling question actually looks like."),
    question=("The film never gives you one clean answer. Why not — and does "
              "that make it a bad question, or a good one?"),
)

PARTS = [
    part("3.1", "What Is an Inquiry?",
         pages=PAGES[:4], watch=WATCH_3_1,
         intro=("Compelling questions, supporting questions, and the five steps "
                "of an inquiry."),
         vocabulary=[
             ("claim", "a statement made about what is believed and can be "
                       "supported with evidence"),
             ("compelling question", "a question that guides an inquiry"),
             ("inquiry", "a process that helps people investigate eras, events, "
                         "or people they are curious about"),
         ]),
    part("3.2", "Inquiry Process Poster",
         pages=PAGES[4:], activity=True,
         intro=("Make a poster that explains the inquiry process to somebody "
                "who has never heard of it. Fact-find, plan it, then build it."),
         vocabulary=[]),
]

STUDENT_NOTE = ("Part 3.2 is a make, not a read — you are building a poster, so "
                "give yourself space and something to draw on.")
PARENT_NOTE = """**The film is doing real work here.** The Library of Alexandria
is the rare famous story where the honest answer is "we are not sure", and the
lesson she is about to read is entirely about questions that do not have one
clean answer. Ask her the question under the video before she reads anything.

**3.2 is an activity, not a worksheet.** The printed rubric asks for three
things on the poster: the steps of the inquiry process, a summary of each in her
own words, and why inquiry is worth doing at all. Photograph the finished poster
and upload it — the picture is the work.

**Question 7 is the only open one in the check.** It wants the three things the
article names for choosing a topic: interest, focus, and whether enough sources
exist."""
GRADER_NOTE = ("Question 7 has three named parts in the article — interest, "
               "focus, and research potential. Credit her for naming them in "
               "her own words; she does not need the textbook's nouns.")

# --------------------------------------------------------------------------
# Lesson 3 Comprehension Check, verbatim (pp. 1.40-1.41).
# --------------------------------------------------------------------------

QUESTIONS = [
    choice(
        "Which is a description of compelling questions? Choose all that apply.",
        options=[
            ("a", "simple"),
            ("b", "limited"),
            ("c", "intriguing"),
            ("d", "open-ended"),
            ("e", "single answer"),
            ("f", "thought-provoking"),
        ],
        correct=["c", "d", "f"],
        multi=True,
        hint="The article gives a three-item list under \"A compelling question "
             "is:\". Three of these six are that list, word for word.",
        standard=C3,
    ),
    choice(
        "Identify the compelling question.",
        options=[
            ("a", "Who is your history teacher?"),
            ("b", "What is the history lesson today?"),
            ("c", "How do we know what happened in the past?"),
            ("d", "When was the San Francisco bridge constructed?"),
        ],
        correct="c",
        hint="Three of these have one short, checkable answer. One of them you "
             "could argue about all year — and it is printed at the top of "
             "every page of this unit.",
        standard=C3,
    ),
    choice(
        "Which is a description of supporting questions? Choose all that apply.",
        options=[
            ("a", "broad"),
            ("b", "focused"),
            ("c", "informative"),
            ("d", "answerable"),
            ("e", "interpreting"),
            ("f", "evidence-based"),
        ],
        correct=["b", "c", "d"],
        multi=True,
        hint="The article's box is headed \"Here's how supporting questions "
             "work\" and gives exactly three: Focused, Answerable, Informative.",
        standard=C3,
    ),
    choice(
        "Look at the image. Which is a supporting question?",
        options=[
            ("a", "Is the image a primary source?"),
            ("b", "How was the Constitution created?"),
            ("c", "How do primary sources help historians?"),
            ("d", "What can we learn from the Constitution?"),
        ],
        correct="a",
        figure=F("q4-constitution"),
        figure_caption="The United States Constitution",
        hint="A supporting question is focused and has one verifiable answer. "
             "Three of these are big open questions; one is a yes-or-no you "
             "could settle in a second.",
        standard=C3,
    ),
    choice(
        "Which question **best** helps a researcher understand the impact of "
        "the Gold Rush in California?",
        options=[
            ("a", "When did the Gold Rush start?"),
            ("b", "Were there banks during the Gold Rush?"),
            ("c", "How many miners died in the Gold Rush?"),
            ("d", "How did the Gold Rush affect California's economy?"),
        ],
        correct="d",
        hint="The word to zero in on is **impact** — what it changed. Which "
             "question asks what changed rather than a single fact?",
        standard=C3,
    ),
    choice(
        "Supporting questions help answer the compelling question.",
        options=[("a", "True"), ("b", "False")],
        correct="a",
        hint="The article calls them \"the building blocks of evidence you need "
             "to support your developing argument\".",
        standard=C3,
    ),
    written(
        "What are ideas to consider when deciding an inquiry topic?",
        hint="\"Finding Your Inquiry Topic\" names three things to weigh. One is "
             "about you, one is about how big the topic is, and one is about "
             "whether you could actually find sources.",
        standard="%s · %s" % (C3, WHST),
    ),
    choice(
        "Choose the words that best complete the sentence. The most successful "
        "thinkers know how to ____A____ and ____B____ their thinking if needed. "
        "**Blank A:**",
        options=[
            ("a", "reflect"),
            ("b", "build"),
            ("c", "share"),
            ("d", "stop"),
        ],
        correct="a",
        hint="This exact sentence is pulled out in big blue type on the page "
             "about point of view.",
        standard=HSS,
    ),
    choice(
        "…and **Blank B**: The most successful thinkers know how to reflect and "
        "____B____ their thinking if needed.",
        options=[
            ("a", "change"),
            ("b", "ignore"),
            ("c", "ponder"),
            ("d", "withhold"),
        ],
        correct="a",
        hint="The whole point of the section is that good thinkers are willing "
             "to be wrong. Which word means you would actually do something "
             "about it?",
        standard=HSS,
    ),
    choice(
        "Good historians only analyze secondary sources.",
        options=[("a", "True"), ("b", "False")],
        correct="b",
        hint="Think back to 2.1. Which kind of source is the one made by "
             "someone who was actually there — and would a good historian skip "
             "it?",
        standard=RH,
    ),
    choice(
        "Greta is trying to solve a problem. How can Greta gather different "
        "perspectives on this problem?",
        options=[
            ("a", "Eat dinner and go to sleep."),
            ("b", "Talk about it with other people."),
            ("c", "Stop thinking about it for a day."),
            ("d", "Ignore it and hope it goes away."),
        ],
        correct="b",
        hint="A perspective is somebody else's point of view. Where would you "
             "have to go to get one?",
        standard=HSS,
    ),
]

REFLECTION = written(
    "The film left the Library of Alexandria unsolved on purpose. Write your "
    "own **compelling question** about the medieval world — one you could not "
    "settle with a single web search — and then three **supporting questions** "
    "that would help you answer it. Say in a sentence why your compelling "
    "question interests you.",
    hint="Test it: if you can imagine two sensible people disagreeing about the "
         "answer, it is compelling. If a search box would settle it in ten "
         "seconds, it is a supporting question — which is still useful, just "
         "not the big one.",
    standard="%s · %s" % (C3, WHST),
)

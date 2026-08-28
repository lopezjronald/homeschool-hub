"""Studies Weekly Level 7, Week 2 — Unit 1, Lesson 2: Historical Thinking Skills.

California Studies Weekly: World History and Geography, Medieval and Early
Modern Times. Kaylin's.

Lesson 2 is printed as ONE eight-page issue split into two parts — 2.1 on pages
1-4, 2.2 on pages 5-8 — with a single comprehension check covering both. That is
why this module has PARTS rather than one flat page list, and why there is one
QUESTIONS list and not two.

Transcribed from the family's issue: the questions and their options are the
printed wording. Where the printed check depends on a figure (the time-period
arrows, the communication timeline, the artifacts) the figure is cropped from
the page it was printed on — a substitute would make the question unanswerable.

WHERE THESE ANSWERS COME FROM — read this before marking anything wrong.
The Grade 7 material the family has for this unit is the STUDENT edition only:
there is no teacher edition and no marked key, unlike week 1 (which had one) and
unlike both of Violet's weeks (whose keys are printed in red in her lesson
plan). So the questions and options below are the publisher's printed wording,
but the ANSWERS ARE DERIVED — worked out from the article by us, not read off a
key. Every one is directly supported by a sentence or a picture in the issue,
and each hint points at where. But if she argues with one, she may be right:
check the issue, not this file.

Digitized from the family's purchased Studies Weekly issue for private use.
"""

from .weekly import choice, figure, fill_two, part, video, written

LEVEL = 7
WEEK = 2
UNIT = 1
UNIT_TITLE = "Historical Thinking Skills"
LESSON = "2"
TITLE = "Historical Thinking Skills"
SUBTITLE = "Thinking Like a Time Traveler"
ESSENTIAL_QUESTION = "How do we know what happened in the past?"
PUBLICATION = "California Studies Weekly: Medieval and Early Modern Times"


def F(name):
    return figure(LEVEL, WEEK, name)


# The California History-Social Science framework strands the printed teacher
# edition maps this lesson to.
HSS = "HSS Analysis Skills: Historical Interpretation"
CRP = "HSS Analysis Skills: Chronological and Spatial Thinking"
RH = "CCSS RH.6-8.1 — cite textual evidence"
RH2 = "CCSS RH.6-8.2 — central ideas"
RH6 = "CCSS RH.6-8.6 — identify aspects of a text that reveal point of view"

PAGES = ["weekly/l7w2/page%d.jpg" % n for n in range(1, 9)]

# --------------------------------------------------------------------------
# The two sub-units, each opened by a film.
#
# Both videos were checked against YouTube's oEmbed endpoint, so the id really
# is the video named here on the channel named here. The first candidate I was
# handed for 2.1 turned out to be a different TED-Ed lesson entirely, which is
# the reason that check exists.
# --------------------------------------------------------------------------

WATCH_2_1 = video(
    "A542ixwyBhc",
    'Why is Herodotus called "The Father of History"?',
    channel="TED-Ed",
    length="6 minutes",
    why=("Before anyone *had* to check a story, one man decided he would. "
         "Herodotus went and asked both sides why a war happened — and by doing "
         "that he more or less invented history. Watch what he did differently, "
         "because the rest of this lesson is his method."),
    question=("He was nicknamed both the Father of History **and** the Father "
              "of Lies. After the film, what do you think earned him the "
              "second one?"),
)

WATCH_2_2 = video(
    "Eq-Wk3YqeH4",
    "History vs. Genghis Khan",
    channel="TED-Ed",
    length="5 minutes",
    why=("The same man, put on trial: the prosecution calls him a butcher, the "
         "defence calls him the reason Europe and Asia ever talked to each "
         "other. Nobody is lying — they are choosing what to leave out. That is "
         "exactly what part 2.2 is about."),
    question=("Both lawyers used real facts. So how did they end up with "
              "opposite pictures of the same man?"),
)

PARTS = [
    part("2.1", "Thinking Like a Time Traveler",
         pages=PAGES[:4], watch=WATCH_2_1,
         intro=("Chronology, and the difference between a source made AT the "
                "time and one made about it afterwards."),
         vocabulary=[
             ("artifacts", "human-made objects that help us learn about past "
                           "civilizations and how they developed"),
             ("B.C.E.", "Before the Common Era"),
             ("C.E.", "Common Era"),
             ("cause and effect", "the concept that one event can lead to another"),
             ("chronology", "the order in which events happen"),
             ("context", "the setting, background, or circumstances that give "
                         "meaning to an event or idea"),
             ("corroboration", "the process of looking for other evidence that "
                               "supports a piece of historical evidence"),
             ("eras", "large segments of time"),
             ("oral histories", "interviews, recorded on audio or video, with "
                                "someone who experienced an event in the past"),
             ("primary sources", "artifacts that are created by people who saw "
                                 "or experienced something"),
             ("secondary sources", "items made by people who didn't directly "
                                   "see or experience the event"),
             ("timelines", "visual representations of events"),
         ]),
    part("2.2", "Seeing History Through Different Eyes",
         pages=PAGES[4:], watch=WATCH_2_2,
         intro=("Why two honest people can describe the same event completely "
                "differently — and how to spot it."),
         vocabulary=[
             ("bias", "favoring one side over another"),
             ("historical bias", "when someone's personal views or opinions "
                                 "influence how they write or talk about history"),
             ("historical empathy", "understanding the motivations and "
                                    "experiences of people who lived in the past"),
             ("perspectives", "different viewpoints people have on historical events"),
             ("propaganda", "information, especially biased or misleading, used "
                            "to promote a particular cause or point of view"),
         ]),
]

STUDENT_NOTE = ("Watch the short film at the top of each part before you read "
                "it — it is the quickest way in.")
PARENT_NOTE = """**The answers here are ours, not the publisher's.** This unit came without a teacher edition, so they are derived from the article rather than read off a key. Each hint points at the sentence or picture it came from. If she disputes one, check the issue — she may be right.

**The two films are the hook, not decoration.** 2.1 opens with
Herodotus inventing the idea of checking a story; 2.2 puts Genghis Khan on trial
so she watches two people build opposite pictures out of the same true facts.
Each one asks her a question underneath — that question is the lesson, and it is
worth two minutes of talking before she reads anything.

**Where the answers come from.** Questions 3, 4 and 6 are read off the pictures
printed with them, not the article. If she is guessing on those, sit with her and
the picture."""
GRADER_NOTE = ("Question 4 asks her to use two sources together. Look for "
               "whether she actually connects them — the artifact definition "
               "AND the timeline — rather than describing only one.")

# --------------------------------------------------------------------------
# Lesson 2 Comprehension Check, verbatim from the printed check (pp. 1.29-1.31).
# --------------------------------------------------------------------------

QUESTIONS = [
    choice(
        "Which is a key tool for historians thinking chronologically? "
        "Choose all that apply.",
        options=[
            ("a", "eras"),
            ("b", "timelines"),
            ("c", "itineraries"),
            ("d", "inventions"),
            ("e", "B.C.E and C.E."),
            ("f", "cardinal directions"),
        ],
        correct=["a", "b", "e"],
        multi=True,
        hint="The article lists three key tools in a row, each with its own "
             "bullet. An itinerary is a travel plan — is that one of them?",
        standard="%s · %s" % (CRP, RH2),
    ),
    choice(
        "Thinking chronologically can help people see how one event leads to "
        "another.",
        options=[("a", "True"), ("b", "False")],
        correct="a",
        hint="The article gives the printing press as its example: 1439, then "
             "ideas spreading, then 1776. What is that pattern called?",
        standard=CRP,
    ),
    # The printed question is a sort, but the six periods are given as loose
    # words under the figure rather than as a list to drag, so it is asked the
    # way the page asks it and marked on the order she writes.
    written(
        "Study the image. Sort these periods from **shortest to longest**: "
        "six months · two weeks · one century · four years · five days · "
        "three decades.",
        hint="The picture gives you the length of each unit. Turn every one of "
             "the six into days or years first, then line them up.",
        standard=CRP,
        answer_mode=False,
        figure=F("q3-time-periods"),
        figure_caption="How long each period lasts",
    ),
    written(
        "**Source A.** \"Artifacts are usually human-made objects that help us "
        "learn about past civilizations and how they developed. They can also "
        "be ordinary objects used in the past by people working or interacting "
        "with others.\" — \"Primary and Secondary Sources,\" Studies Weekly\n\n"
        "**Source B** is the History of Communication timeline below.\n\n"
        "Study sources A and B. How have ideas spread over time?",
        hint="Source B is a row of artifacts: a drum, a telegraph, a phone, an "
             "iPhone. What happens to the SPEED and the REACH of an idea as you "
             "move along it?",
        standard="%s · %s" % (HSS, RH),
        figure=F("q4-communication"),
        figure_caption="Source B — History of Communication",
    ),
    choice(
        "Tracy tells a story to the class. Soldiers invaded his grandfather's "
        "hometown. Tracy's grandfather was a small boy. Which is the primary "
        "source?",
        options=[
            ("a", "the class"),
            ("b", "grandfather"),
            ("c", "the story"),
            ("d", "Tracy"),
        ],
        correct="b",
        hint="A primary source is the person who was actually there. Who in "
             "this list saw the soldiers?",
        standard=HSS,
    ),
    choice(
        "Study the artifact. Which claim can be supported about the people who "
        "made the artifacts?",
        options=[
            ("a", "Family was the foundation of their culture."),
            ("b", "They were forbidden to imitate living things."),
            ("c", "The sun represents the Creator of all existence."),
            ("d", "Birds were an important symbol in their culture."),
        ],
        correct="d",
        figure=F("q6-artifacts"),
        figure_caption="Artifacts",
        hint="Only count what you can actually SEE in the picture. How many of "
             "the five objects are birds?",
        standard="%s · %s" % (HSS, RH),
    ),
    choice(
        "Janelle discovers a new source about California's history. Which is a "
        "question Janelle should **not** ask about the source?",
        options=[
            ("a", "Who created this document?"),
            ("b", "When did California become a state?"),
            ("c", "Was the author partial to one side over another?"),
            ("d", "What were the background and circumstances of this idea?"),
        ],
        correct="b",
        hint="Three of these are questions about the SOURCE. One is a question "
             "about California.",
        standard=HSS,
    ),
    choice(
        "Which is an example of corroboration?",
        options=[
            ("a", "evaluating when an online article was published"),
            ("b", "researching about the Magna Carta with a partner"),
            ("c", "reading about Judaism from an online article and a book"),
            ("d", "studying about the Roman Empire from a textbook in class"),
        ],
        correct="c",
        hint="Corroboration is looking for OTHER evidence that supports what "
             "you have. Which answer uses two sources instead of one?",
        standard=HSS,
    ),
    choice(
        "Choose the word that best completes the sentence. "
        "__________ means favoring one opinion over another.",
        options=[
            ("a", "Bias"),
            ("b", "Artifact"),
            ("c", "Belief"),
            ("d", "Perspective"),
        ],
        correct="a",
        hint="It is one of the vocabulary words in part 2.2, and its definition "
             "there is almost this exact sentence.",
        standard=RH6,
    ),
    choice(
        "What is the purpose of propaganda?",
        options=[
            ("a", "to inform"),
            ("b", "to persuade"),
            ("c", "to question"),
            ("d", "to reflect"),
        ],
        correct="b",
        hint="The article says propaganda is used \"to promote a particular "
             "cause or point of view\". Promote means what?",
        standard=RH6,
    ),
]

REFLECTION = written(
    "The film put Genghis Khan on trial and both lawyers used **true facts** to "
    "reach opposite conclusions. Pick one person or event you have learned "
    "about and write four or five sentences describing it twice — once from a "
    "point of view that admires them, once from a point of view that does not. "
    "Do not invent anything: change only what you choose to mention.",
    hint="Try it out loud first. The trick is not lying — it is leaving things "
         "out, and choosing words like \"defended\" instead of \"attacked\".",
    standard="%s · %s" % (RH6, HSS),
)

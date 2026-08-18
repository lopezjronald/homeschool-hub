"""Intro to Composition: The Essay, Volume 2 — the guide's content.

Blackbird & Company. Ten weeks, five descriptive essays: an orange, a person,
an object, a photograph, a room. The publisher places Volume 2 at Grades 6-8,
so this is Kaylin's.

Each essay takes two weeks, and the two weeks are NOT the same shape:

  odd week   the lesson opens — an observation exercise that warms up the
             senses, then a set of questions that develop the idea
  even week  "(cont.)" — rough draft, student self-evaluation, final draft,
             and the teacher's grading form

That maps onto the app without inventing anything: the odd week is a page of
short typed answers, and the even week is ONE paragraph question, whose
rough-draft sections are the guide's own five-paragraph blueprint and whose
final-draft box is the essay she publishes. The writing coach already sits
between the two halves of that widget, which is exactly where the guide puts
"conference, then revise".

WHY THIS ONE IS TYPED and her other Blackbird guides are handwritten: those ask
her to COPY (Dickinson) or to craft single sentences (Tools of Style), where
forming the letters is the point. Here she is composing five paragraphs and
revising them, and the guide itself ends the writing process with "Type out your
polished final draft and share it with someone" (folio 10). Handwritten, the
essay would also be unreadable to the grader — and the grader is carrying the
guide's own fifty-point form, which is most of this volume's value.

Transcribed by reading the rendered pages; this PDF's text layer is scanner OCR
garbage ("The Model - DeiCriptive Eiiay") and was used for navigation only.
"""

CURRICULUM_NAME = "Intro to Composition: The Essay, Volume 2"

# ---------------------------------------------------------------------------
# The front matter she is told to refer back to. Folio numbers are the numbers
# PRINTED on the page, which is what the guide's own cross-references use
# ("the descriptive essay blueprint on page 13"). The PDF page is one higher.
# ---------------------------------------------------------------------------

# folio 10 — the five steps, verbatim.
WRITING_PROCESS = [
    {
        "step": 1,
        "title": "Imagine a big idea.",
        "body": "Brainstorming begins! Make a list, diagram, topic wheel, or "
                "outline to help organize your thoughts before you begin "
                "writing. Remember, your ideas are important!",
    },
    {
        "step": 2,
        "title": "Get your idea on paper.",
        "body": "It's called a rough draft for a reason! Don't worry about "
                "being perfect here. Get your words out of your head and onto "
                "the page using a free flow of ideas. Skip lines during this "
                "initial stage in the writing process so you can easily modify "
                "your ideas when you revise.",
    },
    {
        "step": 3,
        "title": "Conference, then revise your idea.",
        "body": "Before you get a second opinion, read your work aloud to "
                "yourself and then ask someone else to read it. See if the "
                "content conveys the idea you set out to communicate in a clear "
                "and stylish manner. Make sure your voice shines!",
    },
    {
        "step": 4,
        "title": "Proofread your idea.",
        "body": "Now that you've received feedback and made changes, re-read "
                "your writing carefully, making additional spelling, grammar, "
                "and punctuation edits where necessary.",
    },
    {
        "step": 5,
        "title": "Publish your idea.",
        "body": "Remember, your idea is a gift meant to be shared. Type out "
                "your polished final draft and share it with someone.",
    },
]

# folio 12 — the shape of an essay, and where its named parts live.
STRUCTURE = [
    {
        "part": "INTRODUCTION",
        "body": "The first paragraph of an essay invites the reader into the "
                "writer's big idea. The essay begins with a general statement "
                "called the hook that grabs the reader's attention. The second "
                "sentence of your introduction provides context and sets the "
                "stage for your big idea. The introduction ends with a very "
                "important sentence called the thesis statement that clearly "
                "states the big idea and introduces the three sub-topics you "
                "will be using to support it.",
    },
    {
        "part": "BODY",
        "body": "The body of the essay consists of three paragraphs, structured "
                "according to a blueprint, which will fully develop the three "
                "sub-topics of the thesis statement and allow the reader to "
                "explore the architecture of the writer's big idea.",
    },
    {
        "part": "CONCLUSION",
        "body": "The last paragraph of the essay opens with a sentence that "
                "weaves the sub-topics together and leads the reader to the "
                "next sentence, an echo of the thesis statement. The essay ends "
                "with a thought provoking sentence called the twist that will "
                "leave the reader with a memorable snapshot of the writer's big "
                "idea.",
    },
]

# folio 13 — "The Blueprint - Descriptive Essay": the plan in thirty sentences.
# This is the spine of the whole volume: every rough draft she writes is built
# from it, and the even-week paragraph question uses these five paragraphs as
# its rough-draft sections.
BLUEPRINT_INTRO = ('This is the "plan" for writing your descriptive essay in '
                   "thirty sentences. It consists of five paragraphs: an "
                   "introduction, three body paragraphs, and a conclusion.")

BLUEPRINT = [
    {
        "tag": "P1",
        "name": "INTRODUCTION",
        "sentences": 3,
        "note": "",
        "lines": [
            ("Hook", "this sentence grabs your reader's attention"),
            ("Context", "this sentence sets the stage for your big idea"),
            ("Thesis Statement", "this sentence introduces the three sub-topics "
                                 "you will use to develop, explore, and prove "
                                 "your big idea in the body paragraphs"),
        ],
    },
    {
        "tag": "P2",
        "name": "BODY - Sub-Topic #1",
        "sentences": 8,
        "note": "This paragraph discusses the first reason your big idea matters",
        "lines": [
            ("Opener", "the topic sentence that transitions into your first "
                       "sub-topic"),
            ("Factual detail #1", '"tell" something about sub-topic #1'),
            ("Sensory detail", '"show" something that expands on factual detail #1'),
            ("Factual detail #2", '"tell" something about sub-topic #1'),
            ("Sensory detail", '"show" something that expands on factual detail #2'),
            ("Factual detail #3", '"tell" something about sub-topic #1'),
            ("Sensory detail", '"show" something that expands on factual detail #3'),
            ("Clincher", "this sentence closes your first body paragraph"),
        ],
    },
    {
        "tag": "P3",
        "name": "BODY - Sub-Topic #2",
        "sentences": 8,
        "note": "This paragraph discusses the second reason your big idea matters",
        "lines": [
            ("Opener", "the topic sentence that transitions into your second "
                       "sub-topic"),
            ("Factual detail #1", '"tell" something about sub-topic #2'),
            ("Sensory detail", '"show" something that expands on factual detail #1'),
            ("Factual detail #2", '"tell" something about sub-topic #2'),
            ("Sensory detail", '"show" something that expands on factual detail #2'),
            ("Factual detail #3", '"tell" something about sub-topic #2'),
            ("Sensory detail", '"show" something that expands on factual detail #3'),
            ("Clincher", "this sentence closes your second body paragraph"),
        ],
    },
    {
        "tag": "P4",
        "name": "BODY - Sub-Topic #3",
        "sentences": 8,
        "note": "This paragraph discusses the third reason your big idea matters",
        "lines": [
            ("Opener", "the topic sentence that transitions into your third "
                       "sub-topic"),
            ("Factual detail #1", '"tell" something about sub-topic #3'),
            ("Sensory detail", '"show" something that expands on factual detail #1'),
            ("Factual detail #2", '"tell" something about sub-topic #3'),
            ("Sensory detail", '"show" something that expands on factual detail #2'),
            ("Factual detail #3", '"tell" something about sub-topic #3'),
            ("Sensory detail", '"show" something that expands on factual detail #3'),
            ("Clincher", "this sentence closes your third body paragraph"),
        ],
    },
    {
        "tag": "P5",
        "name": "CONCLUSION",
        "sentences": 3,
        "note": "",
        "lines": [
            ("Weave", "this sentence links the reader back to your big idea"),
            ("Echo", "this sentence reminds the reader of your specific thesis "
                     "statement"),
            ("Twist", "this sentence leaves your reader with something "
                      "compelling to think about"),
        ],
    },
]

# The rough-draft section labels the paragraph widget shows her, derived from
# the blueprint so the two can never drift apart.
PARAGRAPH_SECTIONS = [
    "%s · %s (%d sentences)" % (p["tag"], p["name"], p["sentences"])
    for p in BLUEPRINT
]

# folio 8 — "Writing Evaluation Rubric", the five bands the teacher pages hand
# the parent. This is prose guidance, not a score; the numbers come from the
# fifty-point form below.
EVALUATION_RUBRIC_INTRO = ("Use this rubric as a guideline when assessing your "
                           "student's writing:")

EVALUATION_RUBRIC = [
    ("ACCOMPLISHED", [
        "Creatively focuses on the topic",
        "Uses logical progression of ideas to develop and supports topic with details",
        "Varies sentence structure",
        "Uses interesting transitions",
        "Makes strong word choice",
        "Mature understanding of writing conventions",
    ]),
    ("PROFICIENT", [
        "Focuses on topic and includes adequate support",
        "Uses logical progression of ideas to develop and loosely supports topic",
        "Some varied sentence structure",
        "Transitions are adequate but not creative",
        "Word choice is adequate but not creative",
        "General understanding of writing conventions",
    ]),
    ("BASIC", [
        "Topic is addressed, but unclear",
        "Lacks logical progression of ideas and support is weak",
        "Sentences are stagnant and uninteresting",
        "Lack of transitions",
        "Average word choice",
        "Partial understanding of writing conventions",
    ]),
    ("LIMITED", [
        "Topic may be mentioned, but not clearly addressed and loosely supported",
        "Organization pattern is weak",
        "Writing contains sentence fragments and run-ons",
        "Poor transitions",
        "Poor word choice",
        "Definite misunderstanding of writing conventions",
    ]),
    ("POOR", [
        "Topic is not addressed or clearly supported",
        "Organizational pattern is lacking",
        "Sentence structure is insufficient",
        "Non-existent transitions",
        "Weak word choice",
        "Frequent errors in basic writing conventions",
    ]),
]

# The "Teacher's Feedback" form printed at the end of every even week. Fifty
# points, and every line item names something the blueprint taught — which is
# why it can be handed to the grader as-is.
TEACHER_FORM = [
    ("Process", 6, [
        ("Rough", 2), ("Conference", 2), ("Final", 2),
    ]),
    ("Mechanics/Appearance", 10, [
        ("Format (Margins, Indentation, Spacing)", 2), ("Spelling", 2),
        ("Grammar", 2), ("Sentence Structure (Fragments, Run-ons)", 2),
        ("Neatness", 2),
    ]),
    ("Content", 24, [
        ("Hook", 1), ("Context", 1), ("Thesis Statement", 1),
        ("Body Paragraphs on Topic", 6), ("Supporting Facts & Details", 6),
        ("Clear Sequence of Ideas", 6), ("Weave", 1), ("Echo", 1), ("Twist", 1),
    ]),
    ("Style", 10, [
        ("Sentence Variation", 2), ("Vocal Creativity", 2),
        ("Vivid Words - Concrete", 2), ("Precise Words - Concise", 2),
        ("Consistent Tense", 2),
    ]),
]

TOTAL_POINTS = 50

# The student-facing reference pages, kept as images of the real thing: the
# blueprint is a diagram and the model essay is annotated in the author's own
# hand, and neither survives being retyped as prose.
REFERENCE_PAGES = [
    {"folio": 10, "pdf_page": 11, "title": "The Writing Process"},
    {"folio": 11, "pdf_page": 12, "title": "The Architecture of Good Writing"},
    {"folio": 12, "pdf_page": 13, "title": "The Structure of an Essay"},
    {"folio": 13, "pdf_page": 14, "title": "The Blueprint - Descriptive Essay"},
    {"folio": 14, "pdf_page": 15, "title": "The Model - Descriptive Essay"},
]


def reference_images():
    """The reference pages as static paths, in printed order."""
    return [("essay/reference/p%02d.jpg" % p["pdf_page"], p["title"])
            for p in REFERENCE_PAGES]


def blueprint_total():
    """Thirty, unless someone edits a paragraph and forgets to say so."""
    return sum(p["sentences"] for p in BLUEPRINT)

"""Built-in curriculum blueprints (scope & sequence) applied to a Curriculum.

A blueprint is plain data transcribed from a published curriculum's scope &
sequence. Applying one populates Chapter/Lesson rows for a given Curriculum via
``manage.py apply_blueprint``. Objectives are included where available. For
Dimensions Math 3A, Ch1–2 are transcribed from the Home Instructor's Guide 3A;
Ch3's describe the same lesson content but were written here rather than copied
from the guide, so check them against your edition before relying on the exact
wording. Later chapters can be filled in over time.

Objectives are not decoration: ``tutor.views._entry_objectives`` feeds them to
the AI grader as concept context, so a lesson with none is graded blind.

Lesson dict keys: order, number (None for openers/reviews), title, type
(opener|lesson|practice|review), objectives.
"""

OPENER = "opener"
LESSON = "lesson"
PRACTICE = "practice"
REVIEW = "review"


def _op(order):
    return {"order": order, "number": None, "title": "Chapter Opener", "type": OPENER, "objectives": ""}


def _ls(order, number, title, objectives="", type=LESSON):
    return {"order": order, "number": number, "title": title, "type": type, "objectives": objectives}


DIMENSIONS_MATH_3A = {
    "slug": "dimensions_math_3a",
    "name": "Dimensions Math 3A",
    "subject": "Math",
    "grade_level": "G03",
    "source": "Dimensions Math Home Instructor's Guide 3A (Singapore Math Inc., 2021)",
    "chapters": [
        {
            "number": 1,
            "title": "Numbers to 10,000",
            "lessons": [
                _op(0),
                _ls(1, 1, "Numbers to 10,000", "Interpret four-digit numbers."),
                _ls(2, 2, "Place Value - Part 1",
                    "Identify the value of each digit in a four-digit number. "
                    "Identify the position of each digit by naming its place value."),
                _ls(3, 3, "Place Value - Part 2",
                    "Determine the total number of tens and hundreds in a four-digit number."),
                _ls(4, 4, "Comparing Numbers", "Compare numbers within 10,000."),
                _ls(5, 5, "The Number Line",
                    "Interpret number lines. Locate numbers on a number line."),
                _ls(6, 6, "Practice A", type=PRACTICE),
                _ls(7, 7, "Number Patterns",
                    "Count on or back by ones, tens, hundreds, or thousands. Identify whether a "
                    "number pattern is increasing or decreasing by ones, tens, hundreds, or thousands."),
                _ls(8, 8, "Rounding to the Nearest Thousand",
                    "Round a four-digit number to the nearest thousand."),
                _ls(9, 9, "Rounding to the Nearest Hundred",
                    "Round a three-digit or four-digit number to the nearest hundred."),
                _ls(10, 10, "Rounding to the Nearest Ten",
                    "Round a two-digit, three-digit, or four-digit number to the nearest ten."),
                _ls(11, 11, "Practice B", type=PRACTICE),
            ],
        },
        {
            "number": 2,
            "title": "Addition and Subtraction - Part 1",
            "lessons": [
                _op(0),
                _ls(1, 1, "Mental Addition - Part 1",
                    "Use mental math strategies to add two-digit numbers."),
                _ls(2, 2, "Mental Addition - Part 2",
                    "Use mental math strategies to add three-digit numbers where the ones is 0."),
                _ls(3, 3, "Mental Subtraction - Part 1",
                    "Use mental math strategies to subtract two-digit numbers."),
                _ls(4, 4, "Mental Subtraction - Part 2",
                    "Use mental math strategies to subtract three-digit numbers where the ones is 0."),
                _ls(5, 5, "Making 100 and 1,000",
                    "Use mental math strategies to subtract from hundreds or thousands."),
                _ls(6, 6, "Strategies for Numbers Close to Hundreds",
                    "Use mental math strategies to add or subtract a number that is 1, 2, or 3 "
                    "less than hundreds."),
                _ls(7, 7, "Practice A", type=PRACTICE),
                _ls(8, 8, "Sum and Difference",
                    "Draw part-whole or comparison bar models to represent expressions or "
                    "equations with an unknown value."),
                _ls(9, 9, "Word Problems - Part 1",
                    "Draw part-whole bar models to represent information given in one-step word problems."),
                _ls(10, 10, "Word Problems - Part 2",
                    "Draw comparison bar models to represent information given in one-step word problems."),
                _ls(11, 11, "2-Step Word Problems",
                    "Draw bar models to represent information given in two-step word problems."),
                _ls(12, 12, "Practice B", type=PRACTICE),
            ],
        },
        {
            "number": 3,
            "title": "Addition and Subtraction - Part 2",
            "lessons": [
                _op(0),
                _ls(1, 1, "Addition with Regrouping",
                    "Add numbers within 10,000 using the standard algorithm, regrouping "
                    "ten ones as one ten, ten tens as one hundred, and ten hundreds as "
                    "one thousand."),
                _ls(2, 2, "Subtraction with Regrouping - Part 1",
                    "Subtract numbers within 10,000 using the standard algorithm, "
                    "regrouping one of a larger place into ten of the next place."),
                _ls(3, 3, "Subtraction with Regrouping - Part 2",
                    "Subtract from numbers containing zeros, regrouping across more than "
                    "one place."),
                _ls(4, 4, "Estimating Sums and Differences - Part 1",
                    "Round numbers to the nearest hundred to estimate a sum, and use the "
                    "estimate to check whether an exact answer is reasonable."),
                _ls(5, 5, "Estimating Sums and Differences - Part 2",
                    "Round numbers to estimate a difference, and choose a rounding place "
                    "that gives a useful estimate."),
                _ls(6, 6, "Word Problems",
                    "Solve one- and two-step word problems involving addition and "
                    "subtraction within 10,000, using bar models to represent the "
                    "information."),
                _ls(7, 7, "Practice", type=PRACTICE),
            ],
        },
        {
            "number": 4,
            "title": "Multiplication and Division",
            "lessons": [
                _op(0),
                _ls(1, 1, "Looking Back at Multiplication",
                    "Interpret multiplication as equal groups and as repeated addition, "
                    "and relate the two."),
                _ls(2, 2, "Strategies for Finding the Product",
                    "Find a product by building on a known fact — doubling, adding one "
                    "more group, or splitting a factor."),
                _ls(3, 3, "Looking Back at Division",
                    "Interpret division as sharing equally and as grouping, and relate "
                    "division to the multiplication fact it undoes."),
                _ls(4, 4, "Multiplying and Dividing with 0 and 1",
                    "Multiply and divide with 0 and 1, and recognize that dividing 0 by "
                    "a number gives 0."),
                _ls(5, 5, "Division with Remainders",
                    "Divide when the groups do not come out even, and say what the "
                    "remainder means in the situation."),
                _ls(6, 6, "Odd and Even Numbers",
                    "Identify odd and even numbers by whether they can be split into "
                    "two equal groups."),
                _ls(7, 7, "Word Problems - Part 1",
                    "Solve one-step multiplication word problems, using bar models to "
                    "show the equal groups."),
                _ls(8, 8, "Word Problems - Part 2",
                    "Solve one-step division word problems, choosing between sharing "
                    "and grouping to match the question."),
                _ls(9, 9, "2-Step Word Problems",
                    "Solve two-step word problems that mix multiplication or division "
                    "with addition or subtraction."),
                _ls(10, 10, "Practice", type=PRACTICE),
                _ls(11, None, "Review 1", type=REVIEW),
            ],
        },
        {
            "number": 5,
            "title": "Multiplication",
            "lessons": [
                _op(0),
                _ls(1, 1, "Multiplying Ones, Tens, and Hundreds",
                    "Multiply a one-digit number by ones, tens and hundreds, using "
                    "place value rather than counting on."),
                _ls(2, 2, "Multiplication Without Regrouping",
                    "Multiply a two-digit number by a one-digit number when no place "
                    "reaches ten."),
                _ls(3, 3, "Multiplication with Regrouping Tens",
                    "Multiply when the tens reach ten or more, regrouping ten tens as "
                    "one hundred."),
                _ls(4, 4, "Multiplication with Regrouping Ones",
                    "Multiply when the ones reach ten or more, regrouping ten ones as "
                    "one ten and carrying it."),
                _ls(5, 5, "Multiplication with Regrouping Ones and Tens",
                    "Multiply when both the ones and the tens need regrouping in the "
                    "same problem."),
                _ls(6, 6, "Practice A", type=PRACTICE),
                _ls(7, 7, "Multiplying a 3-Digit Number with Regrouping Once",
                    "Multiply a three-digit number by a one-digit number with a single "
                    "regroup."),
                _ls(8, 8, "Multiplication with Regrouping More Than Once",
                    "Multiply a three-digit number when more than one place needs "
                    "regrouping."),
                _ls(9, 9, "Practice B", type=PRACTICE),
            ],
        },
        {
            "number": 6,
            "title": "Division",
            "lessons": [
                _op(0),
                _ls(1, 1, "Dividing Tens and Hundreds",
                    "Divide tens and hundreds by a one-digit number using place value."),
                _ls(2, 2, "Dividing a 2-Digit Number by 2 - Part 1",
                    "Divide a two-digit number by 2 when each place divides evenly."),
                _ls(3, 3, "Dividing a 2-Digit Number by 2 - Part 2",
                    "Divide a two-digit number by 2 when a ten must be regrouped into "
                    "the ones, and when there is a remainder."),
                _ls(4, 4, "Dividing a 2-Digit Number by 3, 4, and 5",
                    "Divide a two-digit number by 3, 4 or 5, regrouping and recording "
                    "any remainder."),
                _ls(5, 5, "Practice A", type=PRACTICE),
                _ls(6, 6, "Dividing a 3-Digit Number by 2",
                    "Divide a three-digit number by 2, working from the largest place "
                    "down."),
                _ls(7, 7, "Dividing a 3-Digit Number by 3, 4, and 5",
                    "Divide a three-digit number by 3, 4 or 5."),
                _ls(8, 8, "Dividing a 3-Digit Number, Quotient Is 2 Digits",
                    "Divide a three-digit number when the hundreds will not divide, so "
                    "the answer has two digits."),
                _ls(9, 9, "Practice B", type=PRACTICE),
            ],
        },
        {
            "number": 7,
            "title": "Graphs and Tables",
            "lessons": [
                _op(0),
                _ls(1, 1, "Picture Graphs and Bar Graphs",
                    "Read a picture graph and a bar graph, including a picture graph "
                    "whose symbol stands for more than one."),
                _ls(2, 2, "Bar Graphs and Tables",
                    "Read a scaled bar graph and a table, and answer comparison "
                    "questions from the data."),
                _ls(3, 3, "Practice", type=PRACTICE),
                _ls(4, None, "Review 2", type=REVIEW),
            ],
        },
    ],
}


def _bb_section(number, chapters):
    """One Blackbird & Company section: Read → Journal → Acquire → Recollect → Explore."""
    return {
        "number": number,
        "title": f"Section {number}: Chapters {chapters}",
        "lessons": [
            _ls(1, 1, f"Read: Chapters {chapters}",
                "Read the entire assignment before beginning any guide work. "
                "Silent reading plus read-aloud opportunities build fluency, accuracy, "
                "pacing, intonation, and dramatic expression."),
            _ls(2, 2, "Journal: Characters, Setting & Plot",
                "As you read, take bullet-point notes. Characters: who a character IS "
                "(appearance, personality, background, strengths, weaknesses) — not what "
                "he does. Setting: historical time period, geographic location, details. "
                "Plot: simple reminders of major events, not a retelling."),
            _ls(3, 3, "Acquire: Vocabulary",
                "Use a traditional printed dictionary to define the week's words, then "
                "use five of them in original sentences that illustrate their meaning."),
            _ls(4, 4, "Recollect: Comprehension Questions",
                "Answer in complete sentences after finishing the reading. You may refer "
                "to both the book and your journal notes; note page numbers."),
            _ls(5, 5, "Explore: Writing & Discussion",
                "Writing: brainstorm → rough draft → conference → re-write → edit → final "
                "draft. Discussion: the culmination of the week — springboard questions "
                "with no single right answer."),
        ],
    }


# Blackbird & Company Literature Discovery Guide: I Am David (Anne Holm), Level 7.
# Five-week course: four reading sections (two novel chapters each) + a final
# project week. Digitized from the family's purchased guide for private use.
BLACKBIRD_I_AM_DAVID = {
    "slug": "blackbird_i_am_david",
    "name": "I Am David — Literature Discovery",
    "subject": "Literature",
    "grade_level": "G07",
    "source": "Blackbird & Company Educational Press — Literature Discovery Guide: "
              "I Am David by Anne Holm (Level 7)",
    "chapters": [
        _bb_section(1, "1–2"),
        _bb_section(2, "3–4"),
        _bb_section(3, "5–6"),
        _bb_section(4, "7–8"),
        {
            "number": 5,
            "title": "Section 5: Glean — Final Project",
            "lessons": [
                _ls(1, 1, "Glean: Final Project",
                    "Complete one or more of the final project options: an epilogue, an "
                    "alternate ending, a change-one-decision reflection, a research essay "
                    "on unjust imprisonment today, the map of David's journey, or an "
                    "essay on the guide's most thought-provoking discussion question."),
            ],
        },
    ],
}


# Blackbird & Company Literature Discovery Guide: The Folk Keeper (Franny
# Billingsley), Level 3 guide used at grade 7. Same five-week shape as I Am David
# — four reading sections plus a final project week — but the sections are uneven
# (4, 4, 3 and 5 chapters), which is the guide's own division, not a mistake.
# Digitized from the family's purchased guide for private use.
BLACKBIRD_THE_FOLK_KEEPER = {
    "slug": "blackbird_the_folk_keeper",
    "name": "The Folk Keeper — Literature Discovery",
    "subject": "Literature",
    "grade_level": "G07",
    "source": "Blackbird & Company Educational Press — Literature & Writing "
              "Discovery Guide: The Folk Keeper by Franny Billingsley (Level 3)",
    "chapters": [
        _bb_section(1, "1–4"),
        _bb_section(2, "5–8"),
        _bb_section(3, "9–11"),
        _bb_section(4, "12–16"),
        {
            "number": 5,
            "title": "Section 5: Glean — Final Project",
            "lessons": [
                _ls(1, 1, "Glean: Final Project",
                    "Complete one or more of the guide's assignment options: research the "
                    "mythical sealfolk, research a Celtic feast, write journal entries as "
                    "Corinna after the novel ends, show how Corin and Corinna differed, "
                    "build a diorama or draw a scene, or write three poems describing "
                    "things you find beautiful."),
            ],
        },
    ],
}


BLACKBIRD_A_MOUSE_CALLED_WOLF = {
    "slug": "blackbird_a_mouse_called_wolf",
    "name": "A Mouse Called Wolf — Literature Discovery",
    "subject": "Literature",
    "grade_level": "G03",
    "source": "Blackbird & Company Educational Press — Literature Discovery Guide: "
              "A Mouse Called Wolf by Dick King-Smith (Level 3). Family-owned guide; "
              "content follows the workbook for private family use.",
    "chapters": [
        _bb_section(1, "1–3"),
        _bb_section(2, "4–6"),
        _bb_section(3, "7–9"),
        _bb_section(4, "10–11"),
        {
            "number": 5,
            "title": "Section 5: Glean — Final Project",
            "lessons": [
                _ls(1, 1, "Glean: Final Project",
                    "Complete one or more of the guide's final project options: compare "
                    "Schubert, Beethoven, and Mozart; research Mozart's life; research and "
                    "draw a labeled grand piano; research the history and meaning of your "
                    "own name; or define the story's musical terms."),
            ],
        },
    ],
}


# Essentials in Writing — Grade 3 (2nd ed). Scope & sequence transcribed from the
# family's Teacher Handbook; lesson titles come from tutor._eiw_content.
_EIW_SECTIONS = [
    (1, "Writing Sentences", [
        (1, "Introduction to Writing"), (2, "Complete Subjects"), (3, "Simple Subjects"),
        (4, "Complete Predicates"), (5, "Simple Predicates"),
        (6, "Complete and Incomplete Sentences"), (7, "Types of Sentences and Punctuation"),
    ]),
    (2, "Parts of Speech", [
        (8, "Common and Proper Nouns"), (9, "Singular and Plural Nouns"),
        (10, "Pronouns and Antecedents"), (11, "Singular Possessive Nouns"),
        (12, "Plural Possessive Nouns"), (13, "More Plural Possessive Nouns"),
        (14, "Adjectives"), (15, "Action Verbs"),
        (16, "Present, Past, and Future Tense Action Verbs"), (17, "Irregular Action Verbs"),
        (18, "Linking Verbs"), (19, "Present, Past, and Future Tense Linking Verbs"),
        (20, "Adverbs That Modify Verbs"),
    ]),
    (3, "Common Problems", [
        (21, "Pronoun/Antecedent Agreement"), (22, "Subject/Verb Agreement"),
        (23, "Contractions"), (24, "Don't/Doesn't Problem"),
    ]),
    (4, "Applying Grammar", [
        (25, "Adjectives in Action"), (26, "Action Verbs in Action"), (27, "Adverbs in Action"),
        (28, "Writing Items in a Series"), (29, "Simple and Compound Sentences"),
        (30, "Incomplete Sentences (Fragments)"), (31, "Run-On Sentences"),
    ]),
    (5, "The Writing Process", [
        (32, "The Writing Process"), (33, "Brainstorm"), (34, "Organize"),
        (35, "Draft"), (36, "Revise"), (37, "Final Draft"),
    ]),
    (6, "Paragraphs", [
        (38, "Parts of a Paragraph"), (39, "Staying on Topic"),
        (40, "Paragraph Practice — Brainstorm & Organize"), (41, "Paragraph Practice — Draft"),
        (42, "Paragraph Practice — Revise"), (43, "Paragraph Practice — Final Draft"),
    ]),
    (7, "Expository Writing", [
        (44, "Expository Paragraph — Brainstorm"), (45, "Organize"), (46, "Draft"),
        (47, "Revise"), (48, "Final Draft"), (49, "Expository Letter — Brainstorm"),
        (50, "Organize"), (51, "Draft"), (52, "Revise"), (53, "Final Draft"),
    ]),
    (8, "Persuasive Writing", [
        (54, "Persuasive Paragraph — Brainstorm"), (55, "Organize"), (56, "Draft"),
        (57, "Revise"), (58, "Final Draft"), (59, "Persuasive Letter — Brainstorm"),
        (60, "Organize"), (61, "Draft"), (62, "Revise"), (63, "Final Draft"),
    ]),
    (9, "Descriptive & Narrative", [
        (64, "Descriptive Paragraph — Brainstorm"), (65, "Organize"), (66, "Draft"),
        (67, "Revise"), (68, "Final Draft"), (69, "Narrative — Order & Transitions"),
        (70, "Brainstorm & Organize"), (71, "Draft"), (72, "Revise"), (73, "Final Draft"),
    ]),
    (10, "Research Project", [
        (74, "Research Process"), (75, "Brainstorm"), (76, "Gather Information"),
        (77, "Organize"), (78, "Draft"), (79, "Revise"), (80, "Final Draft"),
        (81, "Visual Presentation"), (82, "Writing a Bibliography"),
    ]),
]


# Essentials in Writing 3 objectives, keyed by the printed lesson number. Written
# from each lesson's own exercises rather than transcribed from the teacher's
# manual, so they describe what the child is asked to DO — which is what the AI
# grader needs as concept context.
#
# The writing cycles (Brainstorm -> Organize -> Draft -> Revise -> Final) repeat
# across paragraph types, so their objectives name the STAGE and the form rather
# than saying "write a paragraph" five times: what a child does at Revise is a
# different skill from what she does at Draft, and grading them the same way
# helps nobody.
_EIW_OBJECTIVES = {
    1: "Respond to a prompt in complete sentences about a given topic.",
    2: "Identify the complete subject - every word that tells who or what the sentence is about.",
    3: "Identify the simple subject - the one main noun or pronoun within the complete subject.",
    4: "Identify the complete predicate - every word that tells what the subject does or is.",
    5: "Identify the simple predicate - the verb alone within the complete predicate.",
    6: "Tell a complete sentence from an incomplete one by checking for both a subject and a predicate.",
    7: "Identify declarative, interrogative, exclamatory and imperative sentences, and end each with the right punctuation mark.",
    8: "Tell common nouns from proper nouns, and capitalize proper nouns.",
    9: "Form plural nouns, including words ending in s, x, ch, sh and y.",
    10: "Identify pronouns and the antecedents they stand for.",
    11: "Form singular possessive nouns by adding an apostrophe and s.",
    12: "Form plural possessive nouns by adding an apostrophe after the s.",
    13: "Form possessives of irregular plural nouns, which take an apostrophe and s.",
    14: "Identify adjectives and the nouns they describe.",
    15: "Identify action verbs - the words that tell what the subject does.",
    16: "Tell present, past and future tense action verbs apart, and write a verb in a given tense.",
    17: "Use irregular action verbs whose past tense is not formed by adding -ed.",
    18: "Identify linking verbs, which join the subject to a word that renames or describes it.",
    19: "Tell present, past and future tense linking verbs apart.",
    20: "Identify adverbs that modify verbs, telling how, when or where.",
    21: "Make a pronoun agree with its antecedent in number and gender.",
    22: "Make a verb agree with its subject in number.",
    23: "Form contractions and identify the two words each one replaces.",
    24: "Choose between don't and doesn't according to the subject.",
    25: "Replace a plain adjective with a more precise and interesting one.",
    26: "Replace a plain action verb with a more precise and interesting one.",
    27: "Use adverbs to make a sentence more precise about how, when or where.",
    28: "Punctuate three or more items in a series with commas.",
    29: "Tell a simple sentence from a compound one, and join two simple sentences with a comma and a conjunction.",
    30: "Recognize a sentence fragment and repair it by supplying what is missing.",
    31: "Recognize a run-on sentence and repair it by separating or joining the parts correctly.",
    32: "Name the stages of the writing process and say what each one is for.",
    33: "Brainstorm ideas for a topic without yet judging or ordering them.",
    34: "Organize brainstormed ideas into a plan, grouping related ideas together.",
    35: "Write a first draft from a plan, getting the ideas down without stopping to perfect them.",
    36: "Revise a draft for content and clarity, and edit it for capitalization, punctuation and spelling.",
    37: "Produce a neat final draft that incorporates the revisions.",
    38: "Identify the parts of a paragraph - indent, opening sentence, body sentences and closing sentence.",
    39: "Keep every sentence in a paragraph on the stated topic, and spot a sentence that wanders off it.",
    40: "Brainstorm and organize ideas for a paragraph.",
    41: "Draft a paragraph with an opening sentence, body sentences and a closing sentence.",
    42: "Revise and edit a paragraph draft.",
    43: "Produce a final draft of a paragraph.",
    44: "Brainstorm ideas for an expository paragraph, which explains or informs.",
    45: "Organize expository ideas in an order a reader can follow.",
    46: "Draft an expository paragraph.",
    47: "Revise and edit an expository paragraph.",
    48: "Produce a final draft of an expository paragraph.",
    49: "Brainstorm ideas for an expository personal letter.",
    50: "Organize the ideas and parts of a personal letter - heading, greeting, body, closing and signature.",
    51: "Draft an expository personal letter.",
    52: "Revise and edit a personal letter.",
    53: "Produce a final draft of an expository personal letter.",
    54: "Brainstorm reasons for a persuasive paragraph, which argues a position.",
    55: "Organize persuasive reasons in a deliberate order, such as strongest last.",
    56: "Draft a persuasive paragraph that states an opinion and supports it with reasons.",
    57: "Revise and edit a persuasive paragraph, checking that each reason supports the opinion.",
    58: "Produce a final draft of a persuasive paragraph.",
    59: "Brainstorm reasons for a persuasive personal letter.",
    60: "Organize a persuasive letter's reasons within the parts of a letter.",
    61: "Draft a persuasive personal letter.",
    62: "Revise and edit a persuasive personal letter.",
    63: "Produce a final draft of a persuasive personal letter.",
    64: "Brainstorm sensory details for a descriptive paragraph.",
    65: "Organize descriptive details in a deliberate order, such as by space or by importance.",
    66: "Draft a descriptive paragraph using precise adjectives and sensory detail.",
    67: "Revise and edit a descriptive paragraph, replacing vague words with vivid ones.",
    68: "Produce a final draft of a descriptive paragraph.",
    69: "Put narrative events in chronological order and join them with time-order transitions.",
    70: "Brainstorm and organize the events of an imaginative narrative.",
    71: "Draft an imaginative narrative with a beginning, middle and end.",
    72: "Revise and edit an imaginative narrative, checking that the order is clear.",
    73: "Produce a final draft of an imaginative narrative.",
    74: "Name the stages of a research project and say what each one is for.",
    75: "Brainstorm and narrow a research topic.",
    76: "Gather information about a topic from sources, and take notes in your own words.",
    77: "Organize research notes under topic headings.",
    78: "Draft a research report from organized notes.",
    79: "Revise and edit a research report.",
    80: "Produce a final draft of a research report.",
    81: "Plan and prepare a visual presentation of a research project.",
    82: "Write a bibliography that credits the sources used.",
}


def _eiw_chapters():
    chapters = []
    for number, title, lessons in _EIW_SECTIONS:
        chapters.append({
            "number": number,
            "title": title,
            "lessons": [
                _ls(order, num, f"Lesson {num}: {name}",
                    _EIW_OBJECTIVES.get(num, ""))
                for order, (num, name) in enumerate(lessons, start=1)
            ],
        })
    return chapters


ESSENTIALS_IN_WRITING_3 = {
    "slug": "essentials_in_writing_3",
    "name": "Essentials in Writing 3",
    "subject": "Writing",
    "grade_level": "G03",
    "source": "Essentials in Writing Level 3, 2nd Edition (Matthew Stephens)",
    "chapters": _eiw_chapters(),
}


# ---------------------------------------------------------------------------
# DIVE / Saxon Pre-Algebra — Kaylin's course, from Lesson 71 on.
#
# Saxon has no chapters: it is a flat run of numbered lessons, each introducing
# one idea and then mixing it into every later problem set. So the chapters here
# are synthetic, grouped by ten — and numbered as (lesson - 1) // 10 + 1 so that
# lessons 1-70, if they are ever added, become chapters 1-7 without renumbering
# anything or colliding with unique_chapter_number_per_curriculum.
#
# `number` is the printed Saxon lesson number and `order` is its position within
# its ten, so Lesson.code reads "Ch 8, L71".
#
# No chapter openers: _op() exists for Singapore Math's opener pages, Saxon has
# none, and openers are excluded from progress counts.
#
# Titles are transcribed from the family's purchased DIVE lesson PDFs
# ((c) 2021 DIVE, LLC) for private use.
# ---------------------------------------------------------------------------

# {printed lesson number: (title, objective)}
_SAXON_LESSONS = {
    71: ("Proportion Word Problems, Part II: Ratios Involving Totals, Including Percent",
         "Solve proportion word problems where the ratio parts must first be added to "
         "give a total, including problems stated in percents."),
    72: ("Operations with Scientific Notation",
         "Add, subtract, multiply and divide numbers in scientific notation, and write "
         "every answer in standard scientific notation form."),
    73: ("Functions with Graphing: Nonlinear Functions",
         "Recognize the graph shapes of the basic function families, and identify which "
         "function a table of ordered pairs represents."),
    74: ("Data Interpretation and Representation with Charts",
         "Read and build charts and graphs, and choose a representation that suits the "
         "data being shown."),
    75: ("The Binary Numeral System; Pixels",
         "Convert between binary and decimal, and explain how binary values describe "
         "pixels on a screen."),
    76: ("Functions with Graphing: Domain and Range from Graphs; Dividing Terms and Canceling",
         "Read the domain and range of a function from its graph, and divide algebraic "
         "terms by canceling common factors."),
    77: ("More on Linear Functions: Creating a Linear Equation to Solve a Problem",
         "Write a linear equation that models a described situation, then use it to "
         "answer the question asked."),
    78: ("Simplifying More Complex Operations with Exponents; Evaluating Scientific Formulas",
         "Simplify expressions combining several exponent rules, and evaluate a "
         "scientific formula by substituting given values."),
    79: ("More on Linear Functions: Creating a Linear Equation from a Graph",
         "Read the slope and y-intercept off a graphed line and write its equation in "
         "slope-intercept form."),
    80: ("More on Linear Functions: Horizontal and Vertical Lines",
         "Graph and write equations for horizontal and vertical lines, and explain why a "
         "vertical line has no defined slope."),
    81: ("Logic: Converse, Inverse and Contrapositive; What is Calculus?",
         "Form the converse, inverse and contrapositive of a conditional statement and "
         "judge each one's truth; describe in plain terms what calculus studies."),
    82: ("Two Step Equations, Inequalities",
         "Solve two-step equations and inequalities, remembering to reverse the "
         "inequality sign when multiplying or dividing by a negative."),
    83: ("More on Linear Functions: Linear Inequalities",
         "Graph a linear inequality in two variables, choosing a solid or dashed "
         "boundary line and shading the correct side."),
    84: ("Systems of Equations; More on Roots and Radical Signs",
         "Solve a system of two linear equations, and simplify expressions containing "
         "roots and radical signs."),
    85: ("Addition and Subtraction with Mixed Measures; Simplifying Complex Fractions",
         "Add and subtract mixed measures with regrouping between units, and simplify a "
         "fraction whose numerator or denominator is itself a fraction."),
    86: ("Trigonometry Basics",
         "Identify the opposite, adjacent and hypotenuse sides of a right triangle and "
         "use sine, cosine and tangent ratios."),
    87: ("Word Problems and Data from a Chart; Bits, Bytes and Binary Numbers",
         "Answer word problems using data read from a chart, and convert between bits, "
         "bytes and the values they can hold."),
    88: ("Logic: The Syllogism; Surface Area",
         "Test whether a syllogism is valid, and find the surface area of prisms, "
         "cylinders and other solids."),
    89: ("Infinitesimals and the Limit",
         "Describe what happens to a quantity as it approaches a value without reaching "
         "it, and read limit notation."),
    90: ("The Derivative and Slope; Solving Multivariable Equations",
         "Explain the derivative as the slope of a curve at a point, and solve an "
         "equation for one variable in terms of the others."),
    91: ("Calculus and the Trinity; Area and Volume Conversions",
         "Convert between units of area and of volume using squared and cubed unit "
         "multipliers."),
    92: ("More on Derivatives and Tangent Lines; Calculus and the Study of Speed",
         "Relate a tangent line to a derivative, and describe speed as the rate at which "
         "distance changes."),
    93: ("Interest Rate, Savings and Debt",
         "Compute simple and compound interest, and explain how interest works for and "
         "against you in savings and debt."),
    94: ("The Integral and Counting Squares; Imaginary Numbers",
         "Estimate the area under a curve by counting squares, and simplify expressions "
         "containing the square root of a negative number."),
    95: ("Mean, Median, Mode and Range",
         "Find the mean, median, mode and range of a data set, and say which measure "
         "best describes it."),
    96: ("Probability: Compound Events",
         "Find the probability of compound events, distinguishing independent from "
         "dependent events."),
    97: ("Linear Regression and Best Fit",
         "Draw a line of best fit through scattered data and use it to make a "
         "prediction."),
    98: ("Sequences and Series",
         "Identify arithmetic and geometric sequences, find a term from the pattern, and "
         "tell a sequence from a series."),
    99: ("Sigma Means Sum",
         "Read and evaluate a sum written in sigma notation."),
    100: ("Matrices",
          "Read a matrix by its rows and columns, and add, subtract and scalar-multiply "
          "matrices."),
}


def _saxon_chapters():
    """Group the flat Saxon lessons into chapters of ten.

    Only lessons present in _SAXON_LESSONS are emitted, so the course can grow
    lesson by lesson as the PDFs arrive without inventing titles — and
    `audit_content` compares the blueprint against the database, so an invented
    lesson would be reported as drift.
    """
    chapters = {}
    for num in sorted(_SAXON_LESSONS):
        title, objective = _SAXON_LESSONS[num]
        chapter_number = (num - 1) // 10 + 1
        low = (chapter_number - 1) * 10 + 1
        chapter = chapters.setdefault(chapter_number, {
            "number": chapter_number,
            "title": f"Lessons {low}-{low + 9}",
            "lessons": [],
        })
        chapter["lessons"].append(
            _ls(len(chapter["lessons"]) + 1, num, f"Lesson {num}: {title}", objective)
        )
    return [chapters[n] for n in sorted(chapters)]


SAXON_PREALGEBRA_DIVE = {
    "slug": "saxon_prealgebra_dive",
    "name": "Saxon Pre-Algebra (DIVE)",
    "subject": "Math",
    "grade_level": "G07",
    "source": "DIVE Pre-Algebra lesson guides ((c) 2021 DIVE, LLC), used with Saxon Math",
    "chapters": _saxon_chapters(),
}


SOCIAL_STUDIES_G3 = {
    "slug": "social_studies_g3",
    "name": "Social Studies 3 — Continuity and Change",
    "subject": "Social Studies",
    "grade_level": "G03",
    "source": "CA HSS Grade 3 (3.1–3.5), Sacramento/West Sacramento local focus. "
              "Self-directed 'mission' course from the family's commissioned research build (2026).",
    "chapters": [
        {"number": 1, "title": "Unit 1 — Maps & Our Place", "lessons": [
            _ls(1, 1, "Mission 1: Map Detective",
                "Use a map, compass rose, and key to locate home and the local region (3.1)."),
            _ls(2, 2, "Mission 2: Landforms of Our Valley",
                "Name Central Valley landforms — valley, river, delta, foothills, mountains (3.1)."),
            _ls(3, 3, "Mission 3: Rivers Are Why We're Here",
                "Explain that rivers flow downhill and why communities grow beside them (3.1)."),
            _ls(4, 4, "Mission 4: People Change the Land",
                "Describe how people changed the land with levees and dams (3.1)."),
        ]},
        {"number": 2, "title": "Unit 2 — First People: Nisenan & Miwok", "lessons": [
            _ls(1, 5, "Mission 5: Who Lived Here First?",
                "Locate the Nisenan, Plains Miwok, and Patwin homelands on a local map (3.2)."),
            _ls(2, 6, "Mission 6: Acorns & Salmon — Food from the Land",
                "Connect Nisenan food sources (acorns, salmon) to local geography (3.2)."),
            _ls(3, 7, "Mission 7: Build a Tule House",
                "Explain how local materials shaped Nisenan shelter (3.2)."),
            _ls(4, 8, "Mission 8: Stories, Trade & Daily Life",
                "Describe Nisenan baskets, trade, and oral storytelling (3.2)."),
            _ls(5, 9, "Mission 9: The Tribes Today — Wilton Rancheria",
                "Recognize Wilton Rancheria and tribal continuity to the present (3.2)."),
        ]},
        {"number": 3, "title": "Unit 3 — Newcomers & Our Community's Story", "lessons": [
            _ls(1, 10, "Mission 10: Sutter's Fort — Newcomers Arrive",
                "Explain how settlers' arrival changed life for Native people (3.3)."),
            _ls(2, 11, "Mission 11: Gold!",
                "Describe the Gold Rush and why Sacramento grew from it (3.3)."),
            _ls(3, 12, "Mission 12: Capital City & the Railroad",
                "Identify Sacramento as the state capital and railroad starting point (3.3)."),
            _ls(4, 13, "Mission 13: Then vs. Now",
                "Define a primary source and compare the community past to present (3.3)."),
            _ls(5, 14, "Mission 14: Oral History Interview",
                "Create an oral-history primary source through an interview (3.3)."),
        ]},
        {"number": 4, "title": "Unit 4 — Rules, Government & Citizenship", "lessons": [
            _ls(1, 15, "Mission 15: Why Rules?",
                "Explain why communities need laws, and name real laws (3.4)."),
            _ls(2, 16, "Mission 16: The Constitution — Our Rulebook",
                "Describe the U.S. Constitution as the country's highest law (3.4)."),
            _ls(3, 17, "Mission 17: Three Branches — the Three-Legged Stool",
                "Name the legislative, executive, and judicial branches (3.4)."),
            _ls(4, 18, "Mission 18: Our Local Government",
                "Distinguish city, state, and national levels of government (3.4)."),
            _ls(5, 19, "Mission 19: Symbols & Heroes",
                "Identify national symbols and the deeds of one American hero (3.4)."),
        ]},
        {"number": 5, "title": "Unit 5 — Our Local Economy", "lessons": [
            _ls(1, 20, "Mission 20: Goods & Services",
                "Sort goods vs. services and producers vs. consumers (3.5)."),
            _ls(2, 21, "Mission 21: Resources of Our Region",
                "Classify natural, human, and capital resources in the region (3.5)."),
            _ls(3, 22, "Mission 22: Where Was It Made?",
                "Explain why communities trade with other places (3.5)."),
            _ls(4, 23, "Mission 23: Lemonade Stand Math",
                "Weigh cost, price, and profit trade-offs in a simple business (3.5)."),
        ]},
        {"number": 6, "title": "Capstone", "lessons": [
            _ls(1, 24, "Mission 24: History Museum Day",
                "Review 3.1–3.5: how our community has changed and what has stayed the same."),
        ]},
    ],
}


WORLD_HISTORY_G7 = {
    "slug": "world_history_g7",
    "name": "World History 7 — Medieval & Early Modern Times",
    "subject": "Social Studies",
    "grade_level": "G07",
    "source": "CA HSS Grade 7 (7.1–7.11), ~300–1789 CE. Self-directed 'mission' course "
              "with a course-long wall timeline. From the family's commissioned research build (2026).",
    "chapters": [
        {"number": 1, "title": "Unit 1 — Rome Falls, Byzantium Rises", "lessons": [
            _ls(1, 1, "Mission 1: Set Up + Why Rome Fell",
                "Build the wall timeline; explain why the Western Roman Empire fell (7.1)."),
            _ls(2, 2, "Mission 2: Byzantium — Rome Lives On in the East",
                "Describe the Byzantine Empire and what it preserved from Rome (7.1)."),
            _ls(3, 3, "Mission 3: One Empire, Two Churches",
                "Compare the Roman Catholic West and Orthodox East; the Great Schism (7.1)."),
        ]},
        {"number": 2, "title": "Unit 2 — The World of Islam", "lessons": [
            _ls(1, 4, "Mission 4: Arabia — Crossroads of Trade",
                "Explain the rise of Islam and the Five Pillars (7.2)."),
            _ls(2, 5, "Mission 5: An Empire in a Century",
                "Trace the rapid spread of Islam under the Umayyad and Abbasid caliphates (7.2)."),
            _ls(3, 6, "Mission 6: The Golden Age — House of Wisdom",
                "Describe Golden Age scholarship — algebra, medicine, Arabic numerals (7.2)."),
            _ls(4, 7, "Mission 7: Trade Ties the World Together",
                "Explain how Muslim trade networks moved goods and ideas across three continents (7.2)."),
        ]},
        {"number": 3, "title": "Unit 3 — Medieval Europe", "lessons": [
            _ls(1, 8, "Mission 8: Feudalism — The Pyramid of Power",
                "Explain feudalism, the manor, and Charlemagne (7.6)."),
            _ls(2, 9, "Mission 9: The Church at the Center",
                "Describe the medieval Church and monasteries copying books (7.6)."),
            _ls(3, 10, "Mission 10: Crusades & Magna Carta",
                "Explain the Crusades' effects and the Magna Carta's big idea (7.6)."),
            _ls(4, 11, "Mission 11: The Black Death",
                "Link the plague to labor shortage and the decline of feudalism (7.6)."),
        ]},
        {"number": 4, "title": "Unit 4 — Imperial China: Tang & Song", "lessons": [
            _ls(1, 12, "Mission 12: The Exam That Ran an Empire",
                "Compare the civil-service exam to birth-based power in Europe (7.3)."),
            _ls(2, 13, "Mission 13: Invented in China",
                "Describe paper, printing, gunpowder, and the compass (7.3)."),
            _ls(3, 14, "Mission 14: Silk Road & the Mongols",
                "Explain the Silk Road and the dual legacy of the Mongols (7.3)."),
        ]},
        {"number": 5, "title": "Unit 5 — Medieval Japan", "lessons": [
            _ls(1, 15, "Mission 15: Islands That Borrowed and Made It Their Own",
                "Explain how island geography and borrowing from China shaped Japan (7.5)."),
            _ls(2, 16, "Mission 16: Shoguns & Samurai",
                "Compare Japanese feudalism/bushido to European knights and chivalry (7.5)."),
        ]},
        {"number": 6, "title": "Unit 6 — West African Kingdoms", "lessons": [
            _ls(1, 17, "Mission 17: Gold for Salt",
                "Explain the trans-Saharan gold-salt trade and the middleman kingdoms (7.4)."),
            _ls(2, 18, "Mission 18: Mansa Musa — Richest Man in History",
                "Describe Mansa Musa's hajj and Mali's fame (7.4)."),
            _ls(3, 19, "Mission 19: Timbuktu & the Griots",
                "Compare knowledge-keeping across civilizations; Timbuktu and griots (7.4)."),
        ]},
        {"number": 7, "title": "Unit 7 — The Americas: Maya, Aztec, Inca", "lessons": [
            _ls(1, 20, "Mission 20: Maya — Masters of Time and Number",
                "Describe Maya math (base-20, zero), writing, and astronomy (7.7)."),
            _ls(2, 21, "Mission 21: Aztec — City on a Lake",
                "Explain Tenochtitlán, chinampas, and the Triple Alliance (7.7)."),
            _ls(3, 22, "Mission 22: Inca — Empire of the Andes",
                "Describe Inca roads, terrace farming, and quipu (7.7)."),
        ]},
        {"number": 8, "title": "Unit 8 — Renaissance & Reformation", "lessons": [
            _ls(1, 23, "Mission 23: Rebirth in Italy",
                "Explain humanism, patrons, and Renaissance art/perspective (7.8)."),
            _ls(2, 24, "Mission 24: The Machine That Changed Everything",
                "Explain how Gutenberg's press let ideas spread (7.8)."),
            _ls(3, 25, "Mission 25: Luther Lights the Fuse",
                "Explain the 95 Theses and the Protestant Reformation (7.9)."),
            _ls(4, 26, "Mission 26: The Catholic Comeback & a Divided Europe",
                "Describe the Counter-Reformation and a religiously divided Europe (7.9)."),
        ]},
        {"number": 9, "title": "Unit 9 — Scientific Revolution", "lessons": [
            _ls(1, 27, "Mission 27: The Universe Rearranged",
                "Trace Copernicus → Galileo → Newton (7.10)."),
            _ls(2, 28, "Mission 28: The Method Behind It All",
                "Run one full scientific-method cycle; trace its roots (7.10)."),
        ]},
        {"number": 10, "title": "Unit 10 — Exploration & Enlightenment", "lessons": [
            _ls(1, 29, "Mission 29: The Age of Exploration",
                "Map the voyages of Dias, da Gama, Columbus, and Magellan (7.11)."),
            _ls(2, 30, "Mission 30: The Columbian Exchange",
                "Weigh the gains and terrible costs of the Columbian Exchange (7.11)."),
            _ls(3, 31, "Mission 31: The Enlightenment — Ideas That Built America",
                "Match Locke/Montesquieu/Rousseau to the Constitution; Magna Carta→1776 (7.11)."),
            _ls(4, 32, "Mission 32: Capstone — Museum of a Thousand Years",
                "Review 7.1–7.11: how the world of 1789 differs from 300 CE."),
        ]},
    ],
}


SCIENCE_G3 = {
    "slug": "science_g3",
    "name": "Science 3 — You're the Scientist",
    "subject": "Science",
    "grade_level": "G03",
    "source": "Grade 3 NGSS (3-PS2, 3-LS1/3/4, 3-ESS2/3). Self-directed household "
              "experiments from the family's commissioned research build (2026).",
    "chapters": [
        {"number": 1, "title": "Unit 1 — Forces & Motion", "lessons": [
            _ls(1, 1, "Mission 1: Push It, Pull It", "Identify pushes and pulls as forces (3-PS2)."),
            _ls(2, 2, "Mission 2: The Great Ramp Races", "Measure how ramp height changes motion (3-PS2-2)."),
            _ls(3, 3, "Mission 3: Friction — The Invisible Brake", "Test friction on different surfaces (3-PS2)."),
            _ls(4, 4, "Mission 4: Balloon Rocket", "Explore action–reaction forces (3-PS2)."),
            _ls(5, 5, "Mission 5: Balanced vs. Unbalanced", "Distinguish balanced from unbalanced forces (3-PS2-1)."),
        ]},
        {"number": 2, "title": "Unit 2 — Invisible Forces: Magnets & Static", "lessons": [
            _ls(1, 6, "Mission 6: Magnet Detective", "Discover magnets attract iron/steel; poles attract/repel (3-PS2-3)."),
            _ls(2, 7, "Mission 7: Force Through Walls", "Test magnetic force at a distance and through materials (3-PS2-4)."),
            _ls(3, 8, "Mission 8: Make a Compass", "Build a floating compass from a magnetized needle (3-PS2)."),
            _ls(4, 9, "Mission 9: Static Electricity", "Explore static charge as a non-contact force (3-PS2-3)."),
        ]},
        {"number": 3, "title": "Unit 3 — Life Cycles", "lessons": [
            _ls(1, 10, "Mission 10: Sprout Lab — Setup Day", "Set up a fair test of light on bean growth (3-LS1-1)."),
            _ls(2, 11, "Mission 11: Every Living Thing Has a Cycle", "Model animal life cycles and metamorphosis (3-LS1-1)."),
            _ls(3, 12, "Mission 12: Sprout Lab — Results Day", "Compare and measure the sprout results (3-LS1-1)."),
            _ls(4, 13, "Mission 13: Plant Life Cycle Wheel + Seed Hunt", "Model the plant life cycle; find seeds (3-LS1-1)."),
        ]},
        {"number": 4, "title": "Unit 4 — Traits & Families", "lessons": [
            _ls(1, 14, "Mission 14: The Family Trait Lab", "Survey inherited traits across the family (3-LS3-1)."),
            _ls(2, 15, "Mission 15: Inherited or Acquired?", "Sort inherited vs. acquired; environment's effect (3-LS3-2)."),
            _ls(3, 16, "Mission 16: Same Species, All Different", "Measure variation within one kind (3-LS3-1)."),
        ]},
        {"number": 5, "title": "Unit 5 — Survival, Adaptation & Fossils", "lessons": [
            _ls(1, 17, "Mission 17: The Beak Buffet", "Model how beak shape is an adaptation (3-LS4-3)."),
            _ls(2, 18, "Mission 18: Camouflage Hunt", "Model how camouflage aids survival (3-LS4-3)."),
            _ls(3, 19, "Mission 19: Fossil Factory", "Make imprint fossils; explain what fossils are (3-LS4-1)."),
            _ls(4, 20, "Mission 20: Fossil Detective", "Read fossil evidence; match traits to environments (3-LS4-1/2)."),
        ]},
        {"number": 6, "title": "Unit 6 — Weather, Climate & Hazards", "lessons": [
            _ls(1, 21, "Mission 21: Weather Station — Rain Gauge & Log", "Measure and log daily weather (3-ESS2-1)."),
            _ls(2, 22, "Mission 22: Cloud in a Jar", "Model how clouds form (3-ESS2-1). ⚠️ adult assist (hot water)."),
            _ls(3, 23, "Mission 23: Weather vs. Climate", "Distinguish weather from climate (3-ESS2-2)."),
            _ls(4, 24, "Mission 24: Design vs. Disaster — Wind!", "Engineer to reduce weather-hazard damage (3-ESS3-1)."),
            _ls(5, 25, "Mission 25: Flood Fighters", "Engineer flood protection like local levees (3-ESS3-1)."),
        ]},
        {"number": 7, "title": "Capstone", "lessons": [
            _ls(1, 26, "Mission 26: Violet's Science Fair", "Review 3-PS2/LS/ESS: what a scientist does."),
        ]},
    ],
}


SCIENCE_G7 = {
    "slug": "science_g7",
    "name": "Science 7 — Integrated Science Lab",
    "subject": "Science",
    "grade_level": "G07",
    "source": "CA Grade 7 Integrated (MS-PS1/PS3, MS-ESS2/ESS3, MS-LS1/LS2, MS-ETS1). "
              "Self-directed experiments + PhET; CER write-ups. Commissioned research build (2026).",
    "chapters": [
        {"number": 1, "title": "Unit 1 — Matter & the Particle Model", "lessons": [
            _ls(1, 1, "Mission 1: Everything Is Particles", "Model matter as moving particles; temperature = speed (MS-PS1-1/4)."),
            _ls(2, 2, "Mission 2: Ice Balloon Lab", "Investigate density and phase (why ice floats) (MS-PS1-4)."),
            _ls(3, 3, "Mission 3: Phase Change Numbers", "Graph phase-change plateaus (MS-PS1-4). ⚠️ adult (stove)."),
            _ls(4, 4, "Mission 4: Density Tower", "Explain density layering (MS-PS1)."),
        ]},
        {"number": 2, "title": "Unit 2 — Chemical Reactions", "lessons": [
            _ls(1, 5, "Mission 5: Signs of a Reaction", "Distinguish chemical vs. physical change by evidence (MS-PS1-2)."),
            _ls(2, 6, "Mission 6: Conservation of Mass — Wait, Weight!", "Show mass is conserved in a reaction (MS-PS1-5)."),
            _ls(3, 7, "Mission 7: Hot and Cold Reactions", "Classify exothermic vs. endothermic reactions (MS-PS1-6)."),
            _ls(4, 8, "Mission 8: Reaction Engineering — Balloon Blow-Up", "Find the limiting reactant (MS-PS1-2/6)."),
        ]},
        {"number": 3, "title": "Unit 3 — Thermal Energy", "lessons": [
            _ls(1, 9, "Mission 9: Heat Moves Three Ways", "Model conduction, convection, radiation (MS-PS3-3). ⚠️ adult (hot water)."),
            _ls(2, 10, "Mission 10: Build a Cooler — Design", "Design an insulator to slow heat flow (MS-PS3-3)."),
            _ls(3, 11, "Mission 11: Build a Cooler — Test & Iterate", "Test and iterate the insulation design (MS-PS3-3)."),
            _ls(4, 12, "Mission 12: Thermos Autopsy & Home Heat Audit", "Apply heat-transfer ideas to real devices (MS-PS3-4)."),
        ]},
        {"number": 4, "title": "Unit 4 — Plate Tectonics & the Rock Cycle", "lessons": [
            _ls(1, 13, "Mission 13: The Puzzle Earth", "Explain plate tectonics with Pangaea evidence (MS-ESS2-3)."),
            _ls(2, 14, "Mission 14: Boundaries — Where the Action Is", "Model the three plate boundaries (MS-ESS2-2)."),
            _ls(3, 15, "Mission 15: The Crayon Rock Cycle", "Model the rock cycle (MS-ESS2-1). ⚠️ adult (hot water)."),
            _ls(4, 16, "Mission 16: Rocks of California", "Classify local rocks by observation (MS-ESS2-1)."),
        ]},
        {"number": 5, "title": "Unit 5 — Earth's Natural Resources", "lessons": [
            _ls(1, 17, "Mission 17: Cookie Mining", "Model resource extraction cost-benefit (MS-ESS3-1)."),
            _ls(2, 18, "Mission 18: Renewable vs. Nonrenewable", "Compare renewable and nonrenewable energy (MS-ESS3-3/4)."),
            _ls(3, 19, "Mission 19: Design a Resource Plan", "Weigh energy trade-offs in a 20-year plan (MS-ESS3-4)."),
        ]},
        {"number": 6, "title": "Unit 6 — Ecosystems & Biodiversity", "lessons": [
            _ls(1, 20, "Mission 20: Backyard Biodiversity Survey", "Measure biodiversity in two zones (MS-LS2-1/5)."),
            _ls(2, 21, "Mission 21: Build the Food Web", "Model energy flow through a food web (MS-LS2-3)."),
            _ls(3, 22, "Mission 22: Pull a Thread — Ecosystem Jenga", "Test how species loss destabilizes a web (MS-LS2-4)."),
            _ls(4, 23, "Mission 23: Competition & Invasion", "Explain competition and invasive species (MS-LS2-1/2)."),
        ]},
        {"number": 7, "title": "Unit 7 — Cycling of Matter & Energy", "lessons": [
            _ls(1, 24, "Mission 24: Photosynthesis You Can SEE", "Observe photosynthesis producing oxygen (MS-LS1-6)."),
            _ls(2, 25, "Mission 25: The Carbon & Water Merry-Go-Round", "Model the water and carbon cycles (MS-LS2-3/LS1-7)."),
            _ls(3, 26, "Mission 26: Decomposer Detectives", "Model decomposition recycling matter (MS-LS2-3)."),
        ]},
        {"number": 8, "title": "Unit 8 — Engineering Design", "lessons": [
            _ls(1, 27, "Mission 27: The Egg-Drop Lander — Design", "Define a problem and brainstorm designs (MS-ETS1-1/2)."),
            _ls(2, 28, "Mission 28: The Egg-Drop Lander — Test & Iterate", "Test and iterate to find the limit (MS-ETS1-3/4)."),
            _ls(3, 29, "Mission 29: Build Something the Family Needs", "Run the full design process for a real client (MS-ETS1)."),
        ]},
        {"number": 9, "title": "Capstone", "lessons": [
            _ls(1, 30, "Mission 30: The Lab Report & Science Showcase",
                "Review all units: how matter and energy move through the world."),
        ]},
    ],
}


BLUEPRINTS = {
    DIMENSIONS_MATH_3A["slug"]: DIMENSIONS_MATH_3A,
    SOCIAL_STUDIES_G3["slug"]: SOCIAL_STUDIES_G3,
    WORLD_HISTORY_G7["slug"]: WORLD_HISTORY_G7,
    SCIENCE_G3["slug"]: SCIENCE_G3,
    SCIENCE_G7["slug"]: SCIENCE_G7,
    BLACKBIRD_I_AM_DAVID["slug"]: BLACKBIRD_I_AM_DAVID,
    BLACKBIRD_THE_FOLK_KEEPER["slug"]: BLACKBIRD_THE_FOLK_KEEPER,
    BLACKBIRD_A_MOUSE_CALLED_WOLF["slug"]: BLACKBIRD_A_MOUSE_CALLED_WOLF,
    ESSENTIALS_IN_WRITING_3["slug"]: ESSENTIALS_IN_WRITING_3,
    SAXON_PREALGEBRA_DIVE["slug"]: SAXON_PREALGEBRA_DIVE,
}

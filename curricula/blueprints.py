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


BLUEPRINTS = {
    DIMENSIONS_MATH_3A["slug"]: DIMENSIONS_MATH_3A,
    BLACKBIRD_I_AM_DAVID["slug"]: BLACKBIRD_I_AM_DAVID,
    BLACKBIRD_A_MOUSE_CALLED_WOLF["slug"]: BLACKBIRD_A_MOUSE_CALLED_WOLF,
    ESSENTIALS_IN_WRITING_3["slug"]: ESSENTIALS_IN_WRITING_3,
}

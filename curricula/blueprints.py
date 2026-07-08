"""Built-in curriculum blueprints (scope & sequence) applied to a Curriculum.

A blueprint is plain data transcribed from a published curriculum's scope &
sequence. Applying one populates Chapter/Lesson rows for a given Curriculum via
``manage.py apply_blueprint``. Objectives are included where available (Ch1–2
of Dimensions Math 3A, from the Home Instructor's Guide 3A); others can be
filled in over time.

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
                _ls(1, 1, "Addition with Regrouping"),
                _ls(2, 2, "Subtraction with Regrouping - Part 1"),
                _ls(3, 3, "Subtraction with Regrouping - Part 2"),
                _ls(4, 4, "Estimating Sums and Differences - Part 1"),
                _ls(5, 5, "Estimating Sums and Differences - Part 2"),
                _ls(6, 6, "Word Problems"),
                _ls(7, 7, "Practice", type=PRACTICE),
            ],
        },
        {
            "number": 4,
            "title": "Multiplication and Division",
            "lessons": [
                _op(0),
                _ls(1, 1, "Looking Back at Multiplication"),
                _ls(2, 2, "Strategies for Finding the Product"),
                _ls(3, 3, "Looking Back at Division"),
                _ls(4, 4, "Multiplying and Dividing with 0 and 1"),
                _ls(5, 5, "Division with Remainders"),
                _ls(6, 6, "Odd and Even Numbers"),
                _ls(7, 7, "Word Problems - Part 1"),
                _ls(8, 8, "Word Problems - Part 2"),
                _ls(9, 9, "2-Step Word Problems"),
                _ls(10, 10, "Practice", type=PRACTICE),
                _ls(11, None, "Review 1", type=REVIEW),
            ],
        },
        {
            "number": 5,
            "title": "Multiplication",
            "lessons": [
                _op(0),
                _ls(1, 1, "Multiplying Ones, Tens, and Hundreds"),
                _ls(2, 2, "Multiplication Without Regrouping"),
                _ls(3, 3, "Multiplication with Regrouping Tens"),
                _ls(4, 4, "Multiplication with Regrouping Ones"),
                _ls(5, 5, "Multiplication with Regrouping Ones and Tens"),
                _ls(6, 6, "Practice A", type=PRACTICE),
                _ls(7, 7, "Multiplying a 3-Digit Number with Regrouping Once"),
                _ls(8, 8, "Multiplication with Regrouping More Than Once"),
                _ls(9, 9, "Practice B", type=PRACTICE),
            ],
        },
        {
            "number": 6,
            "title": "Division",
            "lessons": [
                _op(0),
                _ls(1, 1, "Dividing Tens and Hundreds"),
                _ls(2, 2, "Dividing a 2-Digit Number by 2 - Part 1"),
                _ls(3, 3, "Dividing a 2-Digit Number by 2 - Part 2"),
                _ls(4, 4, "Dividing a 2-Digit Number by 3, 4, and 5"),
                _ls(5, 5, "Practice A", type=PRACTICE),
                _ls(6, 6, "Dividing a 3-Digit Number by 2"),
                _ls(7, 7, "Dividing a 3-Digit Number by 3, 4, and 5"),
                _ls(8, 8, "Dividing a 3-Digit Number, Quotient Is 2 Digits"),
                _ls(9, 9, "Practice B", type=PRACTICE),
            ],
        },
        {
            "number": 7,
            "title": "Graphs and Tables",
            "lessons": [
                _op(0),
                _ls(1, 1, "Picture Graphs and Bar Graphs"),
                _ls(2, 2, "Bar Graphs and Tables"),
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


BLUEPRINTS = {
    DIMENSIONS_MATH_3A["slug"]: DIMENSIONS_MATH_3A,
    BLACKBIRD_I_AM_DAVID["slug"]: BLACKBIRD_I_AM_DAVID,
}

"""The shape of the multiplication table, for the teaching guide (HH-203).

The single most useful thing you can show a child who thinks she has a hundred
facts to learn is that she does not. Order does not matter, so half the grid is
a duplicate of the other half; five tables are one-step rules; four more are
derivable from those; and what is left is six facts.

Every number quoted on the guide page is counted from this classification rather
than typed into the prose, so the page cannot drift away from the grid it is
printed next to — or from the game, which uses the same clusters.
"""

#: Rules that take one step, taught first.
ONE_STEP = (0, 1, 2, 5, 10)

#: Rules that lean on a one-step table: double-double, ten-take-one, and so on.
DERIVABLE = (3, 4, 6, 8, 9)

#: The residue. No rule reaches these, so they are learned as themselves — with
#: a mnemonic to get them in and spaced practice to keep them there.
STUBBORN = frozenset({(6, 7), (6, 8), (7, 7), (7, 8), (8, 8), (8, 9)})

MAX_FACTOR = 10

KINDS = {
    "twin": "The same fact backwards",
    "one_step": "One-step rule",
    "derived": "Built from an easier fact",
    "square": "A number times itself",
    "stubborn": "No rule — learn it",
}


def classify(a, b):
    """What kind of work `a` x `b` is. `b` < `a` means it is a duplicate."""
    if b < a:
        return "twin"
    if (a, b) in STUBBORN:
        return "stubborn"
    if a in ONE_STEP or b in ONE_STEP:
        return "one_step"
    if a == b:
        return "square"
    if a in DERIVABLE or b in DERIVABLE:
        return "derived"
    return "stubborn"


def grid():
    """Rows of cells for the diagram, top-left 0x0 to bottom-right 10x10."""
    return [
        [{"a": a, "b": b, "product": a * b, "kind": classify(a, b)}
         for b in range(MAX_FACTOR + 1)]
        for a in range(MAX_FACTOR + 1)
    ]


def tally():
    """How many facts fall in each kind, plus the headline numbers."""
    counts = {key: 0 for key in KINDS}
    for row in grid():
        for cell in row:
            counts[cell["kind"]] += 1
    total = (MAX_FACTOR + 1) ** 2
    unique = total - counts["twin"]
    return {
        "counts": counts,
        "total": total,
        "unique": unique,
        "twins": counts["twin"],
        # What is actually left to sit down and learn.
        "to_learn": counts["square"] + counts["stubborn"],
        "stubborn": counts["stubborn"],
    }


#: One line per level of Fact Dash, in the order she meets them. The wording is
#: what to SAY to her — the game shows the same strategy when she gets one wrong.
STRATEGIES = [
    ("Ones & Twos", "×1, ×2", "Times one stays the same. Times two is a double: 7 and 7 is 14."),
    ("Fives", "×5", "Five is half of ten. Ten 8s is 80, so five 8s is 40."),
    ("Tens", "×10", "Say the number, then put a zero on the end."),
    ("Squares", "×itself", "A number times itself. Draw 6 rows of 6 once and she will not forget it is a square."),
    ("Threes", "×3", "Double it, then add one more group: 14 plus 7 is 21."),
    ("Fours", "×4", "Double, then double again: 7, 14, 28."),
    ("Nines", "×9", "Do the ten, then give one group back: 70 take away 7 is 63."),
    ("Sixes", "×6", "Five sets and one more: 35 plus 7 is 42."),
    ("Sevens", "×7", "Nothing left but 7×8 by now — and that one is 5, 6, 7, 8."),
    ("The Tricky Ones", "mixed", "The ones that get muddled, shuffled deliberately so she has to tell them apart."),
]

#: The stubborn six, each with a way in AND a way to work it out — because a
#: rhyme on its own is fragile, and a derivation on its own is slow.
MNEMONICS = [
    ("7 × 8 = 56", "5, 6, 7, 8 — the digits in order.", "7×7 is 49, add one more 7."),
    ("6 × 8 = 48", "6 and 8 went on a date.", "Five 8s is 40, add one more 8."),
    ("8 × 8 = 64", "I ate and ate and was sick on the floor.", "Double 8 three times: 16, 32, 64."),
    ("7 × 7 = 49", "7 and 7 went out to dine.", "Five 7s is 35, add two more 7s."),
    ("6 × 7 = 42", "Six times seven is forty-two.", "Five 7s is 35, add one more 7."),
    ("8 × 9 = 72", "The digits add to 9, and the tens digit is one less than 8.",
     "Ten 8s is 80, give one 8 back."),
]

#: Only the ones a nine-year-old can actually run. Padding this list with tricks
#: that are slower than knowing the fact would make the page look generous and
#: make her slower.
DIVISION_SHORTCUTS = [
    ("÷ 2", "Halve it.", True),
    ("÷ 4", "Halve it, then halve it again. 28 → 14 → 7.", True),
    ("÷ 10", "How many tens? 70 is 7 tens.", True),
    ("÷ 5", "How many fives fit? Or do the tens and double: 60 ÷ 10 is 6, so 60 ÷ 5 is 12.", False),
    ("÷ 6", "Split it: ÷2 then ÷3. 42 → 21 → 7.", False),
    ("÷ 9", "The digits of a 9-fact add to 9, and the tens digit is one less. 54 → tens is 5 → answer 6.", False),
    ("÷ 3", "Nothing to hold. Think '3 times what makes 21?'", None),
    ("÷ 7", "Nothing at all. This one is just known.", None),
    ("÷ 8", "Halving three times works but is slow. Think '8 times what?' and lean on 8×8 = 64.", None),
]


def page_context(request, guide):
    """Everything the guide template needs. Wired in via the registry."""
    return {
        "grid": grid(),
        "tally": tally(),
        "kinds": KINDS,
        "strategies": STRATEGIES,
        "mnemonics": MNEMONICS,
        "division_shortcuts": DIVISION_SHORTCUTS,
    }

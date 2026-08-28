"""The strategy behind each fact, in words a nine-year-old can hold (HH-203).

A hint is shown at the ONE moment it teaches anything: straight after she gets a
fact wrong. Not before — offering a hint up front turns a recall game into a
reading exercise, and the whole point is to pull the answer out of memory.

Every hint carries real numbers, not the rule in the abstract. "Do the five and
add one more group" is a sentence about arithmetic; "five 8s is 40, add one more
8" is the actual thing to do. The second one she can follow; the first she has to
decode first.

Two ideas from the research shape this file:

* DIVISION IS NOT A SEPARATE TABLE. Skilled solvers recast a division fact as a
  missing-factor multiplication, and the format-effect studies show they answer
  faster when it is put to them that way. So every division hint leads with
  "what times 6 makes 48?" — the multiplication sentence — and only then adds a
  division-native shortcut where a real one exists (halving, and not much else).
* A HANDFUL OF FACTS RESIST EVERY RULE. After the derivable tables, six facts
  are left that no strategy reaches. Those get a mnemonic, which is strong for
  getting a fact into memory quickly and weak for keeping it there — so they get
  a derivation as well, and the game's spaced repetition does the keeping.
"""

from .models import Operation

#: The stubborn ones. A rhyme or a digit pattern is genuinely the best available
#: route to these, so they are checked before any rule.
MNEMONICS = {
    (7, 8): "5, 6, 7, 8 — say it in order: 56 = 7 × 8.",
    (6, 8): "6 and 8 went on a date: 6 × 8 is 48.",
    (8, 8): "I ate and ate and was sick on the floor: 8 × 8 is 64.",
    (7, 7): "7 and 7 went out to dine: 7 × 7 is 49.",
}

#: Which factor's rule to reach for when both have one. Lower wins. The order is
#: how reliable the rule is in a nine-year-old's head, not how "easy" the number
#: looks — 9 beats 4 because take-one-group-away is one step and double-double
#: is two.
PRIORITY = [0, 1, 10, 2, 5, 9, 4, 3, 6, 8, 7]


def _rank(n):
    try:
        return PRIORITY.index(n)
    except ValueError:
        return len(PRIORITY)


def _rule(anchor, other):
    """The strategy for `anchor` x `other`, worked through with real numbers."""
    if anchor == 0:
        return "Zero groups of anything is nothing at all."
    if anchor == 1:
        return "Times one leaves it exactly as it was."
    if anchor == 10:
        return "Say the number, then put a zero on the end: %d0." % other
    if anchor == 2:
        return "Double it: %d + %d is %d." % (other, other, 2 * other)
    if anchor == 5:
        return ("Five is half of ten. Ten %ds is %d, and half of that is %d."
                % (other, 10 * other, 5 * other))
    if anchor == 9:
        return ("Do the ten, then give one group back: %d take away %d is %d."
                % (10 * other, other, 9 * other))
    if anchor == 4:
        return ("Double, then double again: %d, %d, %d."
                % (other, 2 * other, 4 * other))
    if anchor == 3:
        return ("Double it, then add one more group: %d plus %d is %d."
                % (2 * other, other, 3 * other))
    if anchor == 6:
        return ("Five %ds is %d, then add one more %d to get %d."
                % (other, 5 * other, other, 6 * other))
    if anchor == 8:
        return ("Double three times: %d, %d, %d, %d."
                % (other, 2 * other, 4 * other, 8 * other))
    if anchor == 7:
        # Seven has no rule of its own, so split it into two that do.
        return ("Split the 7 into a 5 and a 2: %d plus %d is %d."
                % (5 * other, 2 * other, 7 * other))
    return ""


def multiplication_hint(fact):
    a, b = fact.factor_a, fact.factor_b
    mnemonic = MNEMONICS.get((min(a, b), max(a, b)))
    if mnemonic:
        return mnemonic
    # Zero and one outrank the square framing: 0 x 0 is the zero rule, not
    # "a real square", and 1 x 1 is the times-one rule.
    if fact.is_square and a not in (0, 1):
        return "A square — a number times itself. %d × %d is %d." % (a, a, fact.product)
    # Apply the better of the two rules to the other factor.
    anchor, other = (a, b) if _rank(a) <= _rank(b) else (b, a)
    return _rule(anchor, other)


#: Division shortcuts that are real rather than invented. Halving is the genuine
#: one; the rest of the table has nothing a child can hold that beats simply
#: knowing the multiplication, and padding the list with fake tricks would slow
#: her down while looking helpful.
def _division_shortcut(divisor, quotient):
    if divisor == 2:
        return "Or just halve it."
    if divisor == 4:
        return "Or halve it twice: down to %d, then %d." % (2 * quotient, quotient)
    if divisor == 10:
        return "Or count the tens — there are %d." % quotient
    return ""


def division_hint(fact, operation):
    total = fact.product
    divisor = fact.factor_a if operation == Operation.DIV_A else fact.factor_b
    quotient = fact.answer(operation)
    lead = "Turn it into a times question: what times %d makes %d? %d." % (
        divisor, total, quotient)
    extra = _division_shortcut(divisor, quotient)
    return lead + (" " + extra if extra else "")


def hint_for(fact, operation):
    """One short line of strategy, or "" when there is nothing honest to say."""
    if operation == Operation.MULT:
        return multiplication_hint(fact)
    return division_hint(fact, operation)

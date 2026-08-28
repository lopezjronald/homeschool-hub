"""Fact Dash — multiplication and division fact fluency (HH-203).

WHY THIS SHAPE. The pedagogy the research settled on drives every model here:

  * facts are grouped by DERIVATION STRATEGY, not numeric order, so a level is a
    cluster (fives, squares, nines) rather than "the 7 times table";
  * division lives inside the fact family — knowing 6x8 is knowing 48/8 — so a
    Fact carries its division forms rather than there being separate rows;
  * fluent means fast AND right. A correct-but-slow answer is a reconstruction
    (skip counting, deriving) rather than recall, so it does NOT promote;
  * the child never sees a clock. Response time is measured and used, and never
    displayed as a countdown, because the visible clock is what causes anxiety.

EVERYTHING IS KEYED TO A STUDENT, NOT A USER. Children in this app have no login
— they reach the portal through a signed token (portal/tokens.py). A design
keyed to request.user would be unreachable by the only person meant to play it.
"""

from django.db import models
from django.utils import timezone

# A correct answer inside this many milliseconds counts as fluent. 3000 is the
# day-one default because the fact has to be READ before it can be answered; the
# literature's 2-3 second recall benchmark assumes the fact was spoken aloud.
# Tighten toward 2500 and 2000 as recall speeds up.
FLUENCY_THRESHOLD_MS = 3000

# At most this many never-seen facts enter one round. Small sets are the whole
# finding behind incremental rehearsal — a wall of new facts is how a child
# learns that practice feels bad.
NEW_FACTS_PER_ROUND = 4

# Leitner intervals in days, by box. These schedule REVIEW — they say when a
# fact comes back, not whether it is known.
BOX_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}
MAX_BOX = 5

# Mastery is a STREAK, not a box, and the distinction matters more than it
# looks. Reaching box 5 takes 1+2+4+8 days of waiting, so gating a level on it
# would unlock the next one on the calendar rather than on skill — she could be
# perfectly fluent at the fives on Tuesday and still be locked out of the tens
# a fortnight later. Three fluent answers in a row is evidence; the boxes go on
# scheduling review underneath.
MASTERY_STREAK = 3


class Cluster(models.TextChoices):
    ONES_TWOS = "ones_twos", "Ones & Twos"
    FIVES = "fives", "Fives"
    TENS = "tens", "Tens"
    SQUARES = "squares", "Squares"
    THREES = "threes", "Threes"
    FOURS = "fours", "Fours"
    NINES = "nines", "Nines"
    SIXES = "sixes", "Sixes"
    SEVENS = "sevens", "Sevens"
    EIGHTS = "eights", "Eights"


class Operation(models.TextChoices):
    """Three ways to ask one fact.

    A fact family has one multiplication and TWO divisions — 48 has both 48/6
    and 48/8 — and they are genuinely different recalls. Collapsing them to a
    single "div" would let a child who only ever meets 48/8 be marked fluent on
    a form she has never seen. A square has only one division form.
    """

    MULT = "mult", "Multiplication"
    DIV_A = "div_a", "Divide by the first factor"
    DIV_B = "div_b", "Divide by the second factor"


class Fact(models.Model):
    """One canonical single-digit fact, stored once per commutative pair."""

    factor_a = models.PositiveSmallIntegerField()
    factor_b = models.PositiveSmallIntegerField()
    product = models.PositiveSmallIntegerField()
    cluster = models.CharField(max_length=16, choices=Cluster.choices)
    # 6x7, 6x8, 7x8, 4x7, 4x8. Few, and they interfere with each other — related
    # facts compete for the same memory trace and the wrong one sometimes wins —
    # so the last level deliberately interleaves them to force discrimination.
    is_hard_core = models.BooleanField(default=False)

    class Meta:
        ordering = ["factor_a", "factor_b"]
        constraints = [
            models.UniqueConstraint(fields=["factor_a", "factor_b"],
                                    name="unique_fact_pair"),
        ]

    def __str__(self):
        return "%d x %d" % (self.factor_a, self.factor_b)

    @property
    def is_square(self):
        return self.factor_a == self.factor_b

    def operations(self):
        """The forms this fact can be asked in.

        Three rules, and the first one is not optional:

        * a fact with a ZERO factor has no division forms. 0x5 would generate
          "0 / 0", which is undefined, and the naive inverse would answer 5 to
          it. The other form, 0 / 5, is real but is not Grade 3 fact-family
          material and drilling it teaches nothing the multiplication did not.
        * a fact with a ONE factor has no division forms either. n/1 and n/n
          are RULES ("divided by one it stays"; "divided by itself, one") — and
          they are the documented confusion pair, which blurs precisely when
          the two are drilled side by side instead of reasoned each time.
        * a square has ONE division form: 7x7=49 gives 49/7 and nothing else.
        * everything else has both.
        """
        if (self.factor_a in (0, 1)) or (self.factor_b in (0, 1)):
            return [Operation.MULT]
        if self.is_square:
            return [Operation.MULT, Operation.DIV_A]
        return [Operation.MULT, Operation.DIV_A, Operation.DIV_B]

    def prompt(self, operation):
        if operation == Operation.MULT:
            return "%d × %d" % (self.factor_a, self.factor_b)
        if operation == Operation.DIV_A:
            return "%d ÷ %d" % (self.product, self.factor_a)
        return "%d ÷ %d" % (self.product, self.factor_b)

    def answer(self, operation):
        if operation == Operation.MULT:
            return self.product
        if operation == Operation.DIV_A:
            return self.factor_b
        return self.factor_a


class Level(models.Model):
    """One strategy cluster, unlocked by beating the one before it."""

    order = models.PositiveSmallIntegerField(unique=True)
    slug = models.SlugField(max_length=32, unique=True)
    name = models.CharField(max_length=64)
    blurb = models.CharField(max_length=200, blank=True)
    cluster = models.CharField(max_length=16, choices=Cluster.choices)
    facts = models.ManyToManyField(Fact, related_name="levels")
    # A level counts as beaten when this fraction of its forms are mastered.
    mastery_threshold = models.FloatField(default=0.9)
    # A CHALLENGE level re-mixes facts already met elsewhere — the hard core,
    # which she masters in fours, sixes and sevens. Its mastery bar would
    # therefore read 100% before she answered a single question, so it has no
    # bar and no gate: it is scored on records, and its job is discrimination
    # practice between facts that compete with each other.
    is_challenge = models.BooleanField(default=False)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return "%d. %s" % (self.order, self.name)

    def form_count(self):
        """How many (fact, operation) pairs this level contains.

        Not the fact count: a level of six facts is sixteen or eighteen things to
        recall once the divisions are counted, and the mastery bar has to be
        measured against what she is actually asked.
        """
        return sum(len(f.operations()) for f in self.facts.all())


class StudentFactState(models.Model):
    """Where one child stands on one form of one fact."""

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="fact_states")
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, related_name="states")
    operation = models.CharField(max_length=8, choices=Operation.choices)

    leitner_box = models.PositiveSmallIntegerField(default=1)
    due_at = models.DateTimeField(default=timezone.now)
    last_response_ms = models.PositiveIntegerField(null=True, blank=True)
    consecutive_fluent = models.PositiveSmallIntegerField(default=0)
    is_mastered = models.BooleanField(default=False)
    total_attempts = models.PositiveIntegerField(default=0)
    total_correct = models.PositiveIntegerField(default=0)
    # The session that last counted toward this fact's streak. A round repeats
    # its small new set several times — that is the drill working — but three
    # fluent hits thirty seconds apart is not durable recall, so only the FIRST
    # fluent hit in a session promotes or extends the streak. Mastery therefore
    # takes three separate sittings, which is the spacing doing its job.
    last_counted_session = models.PositiveIntegerField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "fact", "operation"],
                                    name="unique_fact_state_per_student"),
        ]
        indexes = [models.Index(fields=["student", "due_at"])]

    def __str__(self):
        return "%s %s box %d" % (self.student, self.fact, self.leitner_box)


class GameSession(models.Model):
    """One speed round."""

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="fact_sessions")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="sessions")
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration_ms = models.PositiveIntegerField(null=True, blank=True)
    num_attempted = models.PositiveSmallIntegerField(default=0)
    num_correct = models.PositiveSmallIntegerField(default=0)
    num_fluent = models.PositiveSmallIntegerField(default=0)
    longest_streak = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["-started_at"]

    def __str__(self):
        return "%s · %s" % (self.student, self.level.name)

    @property
    def accuracy(self):
        if not self.num_attempted:
            return 0.0
        return self.num_correct / self.num_attempted


class Attempt(models.Model):
    """One question answered."""

    session = models.ForeignKey(
        GameSession, on_delete=models.CASCADE, related_name="attempts")
    fact = models.ForeignKey(Fact, on_delete=models.CASCADE, related_name="attempts")
    operation = models.CharField(max_length=8, choices=Operation.choices)
    answer_given = models.IntegerField(null=True, blank=True)
    is_correct = models.BooleanField()
    response_ms = models.PositiveIntegerField()
    was_fluent = models.BooleanField()
    # The client may retry a failed POST after a flaky moment; without this a
    # retry would count the same question twice and inflate her record. Scoped
    # to the session: globally-unique meant one child posting a colliding uuid
    # could silently mute another child's genuine attempt.
    client_uuid = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]
        constraints = [
            models.UniqueConstraint(fields=["session", "client_uuid"],
                                    name="unique_attempt_per_session"),
        ]

    def __str__(self):
        return "%s = %s" % (self.fact.prompt(self.operation), self.answer_given)


class RecordType(models.TextChoices):
    BEST_TIME = "best_time", "Fastest clean round"
    BEST_ACCURACY = "best_accuracy", "Best accuracy"
    LONGEST_STREAK = "longest_streak", "Longest streak"


class PersonalRecord(models.Model):
    """Her own best, per level. There is no leaderboard and never will be —
    she is racing herself."""

    student = models.ForeignKey(
        "students.Student", on_delete=models.CASCADE, related_name="fact_records")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="records")
    record_type = models.CharField(max_length=16, choices=RecordType.choices)
    value = models.FloatField()
    achieved_at = models.DateTimeField(auto_now=True)
    session = models.ForeignKey(
        GameSession, on_delete=models.SET_NULL, null=True, blank=True, related_name="+")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["student", "level", "record_type"],
                                    name="unique_record_per_student_level"),
        ]

    def __str__(self):
        return "%s %s %s" % (self.student, self.level.slug, self.record_type)

    @property
    def lower_is_better(self):
        return self.record_type == RecordType.BEST_TIME

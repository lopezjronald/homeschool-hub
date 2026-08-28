"""The ten levels and their facts (HH-203).

Ordered by DERIVATION STRATEGY rather than by times table, which is the whole
pedagogical bet: anchor facts first (twos, fives, tens), then the ones you can
derive from them (squares, threes = doubles plus one set, fours = double-double,
nines = tens minus one set), leaving the genuinely hard residue for last.

Each fact appears in exactly ONE level — the first cluster that earns it — so a
level's list is what is NEW there, and 6x8 is met once rather than in both the
sixes and the eights.

Used by the data migration and re-runnable by `manage.py seed_fact_dash`.
"""

from .models import Cluster

# 6x7, 6x8, 7x8, 4x7, 4x8 — few, and they interfere with each other.
HARD_CORE = {(6, 7), (6, 8), (7, 8), (4, 7), (4, 8)}

# (order, slug, name, cluster, blurb, [(a, b), ...]) with a <= b throughout.
LEVELS = [
    # Zeros and ones are RULES, not facts — "zero groups is nothing", "times
    # one stays the same". Three examples each is enough to meet the rule over
    # and over; nineteen separate Leitner cards for two one-step rules was most
    # of this level's bulk without being any of its content. The twos are the
    # content: doubles, and their divisions.
    (1, "ones-twos", "Ones & Twos", Cluster.ONES_TWOS,
     "Anything times one is itself. Anything times two is a double.",
     [(0, 2), (0, 6), (0, 9),
      (1, 3), (1, 7), (1, 9),
      (2, 2), (2, 3), (2, 4), (2, 5), (2, 6), (2, 7), (2, 8), (2, 9)]),

    (2, "fives", "Fives", Cluster.FIVES,
     "Count by fives, or take half of the tens.",
     [(3, 5), (4, 5), (5, 5), (5, 6), (5, 7), (5, 8), (5, 9)]),

    (3, "tens", "Tens", Cluster.TENS,
     "Say the number, then add a nought.",
     [(3, 10), (4, 10), (5, 10), (6, 10), (7, 10), (8, 10), (9, 10),
      (2, 10), (10, 10)]),

    (4, "squares", "Squares", Cluster.SQUARES,
     "A number times itself — the ones that make a real square.",
     [(3, 3), (4, 4), (6, 6), (7, 7), (8, 8), (9, 9)]),

    (5, "threes", "Threes", Cluster.THREES,
     "Double it, then add one more set.",
     [(3, 4), (3, 6), (3, 7), (3, 8), (3, 9)]),

    (6, "fours", "Fours", Cluster.FOURS,
     "Double, then double again.",
     [(4, 6), (4, 7), (4, 8), (4, 9)]),

    (7, "nines", "Nines", Cluster.NINES,
     "Take the tens, then give one set back.",
     [(6, 9), (7, 9), (8, 9)]),

    (8, "sixes", "Sixes", Cluster.SIXES,
     "Five sets, and one more.",
     [(6, 7), (6, 8)]),

    (9, "sevens", "Sevens", Cluster.SEVENS,
     "The last one standing.",
     [(7, 8)]),

    # A CHALLENGE, not a gate — see Level.is_challenge. Every fact in it has
    # been met before; the point is answering them side by side, because the
    # failure with these is not forgetting, it is answering the neighbour.
    (10, "the-tricky-ones", "The Tricky Ones", Cluster.EIGHTS,
     "All the ones that try to trick you, shuffled together.",
     []),
]

# The final level introduces nothing. It exists to interleave the facts that
# compete with each other — 6x7 against 6x8 against 7x8 — because the failure
# mode with these is not forgetting, it is answering the neighbour.
BOSS_FACTS = sorted(HARD_CORE)


def seed(apps=None):
    """Create or update every Fact and Level. Idempotent.

    ``apps`` is the migration's historical registry when called from a data
    migration; None means use the real models.
    """
    if apps is None:
        from .models import Fact, Level
    else:
        Fact = apps.get_model("factfluency", "Fact")
        Level = apps.get_model("factfluency", "Level")

    def only_real(model, values):
        """Drop keys the model does not have yet.

        A data migration runs against the HISTORICAL model, so when this
        function grows a new field the old migration would start failing on a
        fresh database — which is exactly what happened when is_challenge was
        added. Filtering keeps one seed function instead of a frozen copy per
        migration, and it cannot break again the next time a field appears.
        """
        names = {f.name for f in model._meta.get_fields()}
        return {k: v for k, v in values.items() if k in names}

    facts = {}
    for order, slug, name, cluster, blurb, pairs in LEVELS:
        for a, b in pairs:
            key = (a, b)
            if key in facts:
                continue
            fact, _ = Fact.objects.update_or_create(
                factor_a=a, factor_b=b,
                defaults=only_real(Fact, {
                    "product": a * b,
                    "cluster": cluster.value if hasattr(cluster, "value") else cluster,
                    "is_hard_core": key in HARD_CORE,
                }),
            )
            facts[key] = fact

    for order, slug, name, cluster, blurb, pairs in LEVELS:
        level, _ = Level.objects.update_or_create(
            slug=slug,
            defaults=only_real(Level, {
                "order": order, "name": name, "blurb": blurb,
                "is_challenge": not pairs,
                "cluster": cluster.value if hasattr(cluster, "value") else cluster,
            }),
        )
        wanted = list(pairs) if pairs else list(BOSS_FACTS)
        level.facts.set([facts[p] for p in wanted])

    return len(facts), len(LEVELS)

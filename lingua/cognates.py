"""English↔Spanish cognate detection + false-friend blocklist (pedagogy point 8, D-28).

Cheap and dependency-free (the leveling review's recommendation): orthographic
similarity (Sørensen–Dice over character bigrams of diacritic-stripped forms) plus
a curated false-friend blocklist that is subtracted first — auto-crediting a false
friend would teach the wrong meaning, so that's the critical safety net.

Used by: the reader's cognate flagging / false-friend warnings (E-05) and the
cold-start cognate auto-crediting in the i+1 bootstrap (D-28, M3). The curated
lists are intentionally small and grown by hand; the Dice scorer enables dynamic
detection later once an es→en dictionary exists (the tap-a-word dict).
"""
import re
import unicodedata

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def normalize(word):
    """Lowercase + strip diacritics (á→a, ñ→n) for order-robust matching."""
    decomposed = unicodedata.normalize("NFKD", word.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _bigrams(s):
    return {s[i:i + 2] for i in range(len(s) - 1)} if len(s) >= 2 else {s}


def dice_similarity(a, b):
    """Sørensen–Dice coefficient over character bigrams of the normalized forms
    (0.0–1.0). 1.0 for identical normalized forms."""
    a, b = normalize(a), normalize(b)
    if a == b:
        return 1.0
    ba, bb = _bigrams(a), _bigrams(b)
    if not ba or not bb:
        return 0.0
    return 2 * len(ba & bb) / (len(ba) + len(bb))


# Curated Spanish false friends: word -> (looks like, actually means). The safety
# net — these are NEVER treated as cognates and warrant an explicit warning.
FALSE_FRIENDS = {
    "embarazada": ("embarrassed", "pregnant"),
    "éxito": ("exit", "success"),
    "librería": ("library", "bookstore"),
    "ropa": ("rope", "clothes"),
    "sopa": ("soap", "soup"),
    "carpeta": ("carpet", "folder"),
    "actual": ("actual", "current"),
    "asistir": ("assist", "to attend"),
    "sensible": ("sensible", "sensitive"),
    "constipado": ("constipated", "having a cold"),
    "molestar": ("molest", "to bother"),
    "recordar": ("record", "to remember"),
    "pariente": ("parent", "relative"),
    "largo": ("large", "long"),
    "fábrica": ("fabric", "factory"),
    "realizar": ("realize", "to carry out"),
    "colegio": ("college", "school"),
    "vaso": ("vase", "drinking glass"),
    "carta": ("cart", "letter"),
}

# Curated common es↔en cognates transparent to an English L1 reader.
COGNATES = {
    "animal", "animales", "familia", "hospital", "problema", "importante",
    "diferente", "historia", "información", "actividad", "chocolate", "elefante",
    "planta", "color", "favorito", "música", "delicioso", "idea", "grupo",
    "área", "tigre", "león", "jirafa", "dragón", "princesa", "monstruo",
    "computadora", "teléfono", "familia", "posible", "necesario",
}

_FF_NORM = {normalize(k): (k, v) for k, v in FALSE_FRIENDS.items()}
_COG_NORM = {normalize(w) for w in COGNATES}


def is_false_friend(word):
    return normalize(word) in _FF_NORM


def false_friend_note(word):
    """(looks_like, actually_means) for a false friend, or None."""
    hit = _FF_NORM.get(normalize(word))
    return hit[1] if hit else None


def is_cognate(word):
    """True if the word is a curated cognate (and NOT a false friend)."""
    n = normalize(word)
    return n in _COG_NORM and n not in _FF_NORM


def looks_cognate(spanish, english, threshold=0.6):
    """Dynamic check for when both forms are known (e.g. tap-a-word): high
    orthographic similarity AND not a curated false friend."""
    if is_false_friend(spanish):
        return False
    return dice_similarity(spanish, english) >= threshold


def analyze_text(text):
    """Scan a Spanish text and return the curated cognates + false friends found.
    Feeds the reader's flagging (E-05) and the approval view's warnings."""
    cognates, false_friends = {}, {}  # normalized -> original surface form (for display)
    for tok in {m.group() for m in WORD_RE.finditer(text)}:
        if is_false_friend(tok):
            false_friends.setdefault(normalize(tok), tok)
        elif is_cognate(tok):
            cognates.setdefault(normalize(tok), tok)
    return {"cognates": sorted(cognates.values()),
            "false_friends": sorted(false_friends.values())}

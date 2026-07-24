"""Frequency-band leveling (D-25/D-28), productized from SPIKE-03.

Coverage-first: the share of a text's words that are "out of band" (rarer than a
beginner reader knows, per the wordfreq es corpus) maps to a suggested L1..L8
level, and the out-of-band words are surfaced as a soft signal for authoring /
approval. This is a SOFT signal atop hand-assigned levels for v1 (validated fit
in SPIKE-03) — NOT a hard gate. The M3 engine adds lemmatization (D-26, so
conjugations collapse to lemmas) + learner-known-words coverage (true i+1).
"""
import re

from wordfreq import zipf_frequency

# Calibrated in SPIKE-03 for the beginner range: at 3.5 the coverage % ordered a
# public-domain gradient correctly (simple->L1 ... Don Quijote->L3). Higher cutoffs
# saturated and flagged conjugations as false-rare (why M3 needs lemmatization).
RARE_ZIPF = 3.5

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)  # letters only; keeps á é í ó ú ñ

# out-of-band % -> level (coverage-first ladder, D-28 spirit).
_LADDER_CAPS = [(6, "L1"), (12, "L2"), (20, "L3"), (30, "L4"),
                (42, "L5"), (55, "L6"), (70, "L7")]


def _tokens(text):
    return [m.group().lower() for m in WORD_RE.finditer(text)]


def _level_for(out_of_band_pct):
    for cap, level in _LADDER_CAPS:
        if out_of_band_pct <= cap:
            return level
    return "L8"


def analyze(text, language="es"):
    """Return {suggested_level, out_of_band_pct, out_of_band_words} for a text.
    suggested_level is None for empty text. out_of_band_words is capped for storage."""
    toks = _tokens(text)
    if not toks:
        return {"suggested_level": None, "out_of_band_pct": 0.0, "out_of_band_words": []}
    scored = [(t, zipf_frequency(t, language)) for t in toks]
    n_oob = sum(1 for _, z in scored if z < RARE_ZIPF)
    pct = 100 * n_oob / len(toks)
    # Unique out-of-band words, RAREST first (most useful to surface), capped.
    oob = {t: z for t, z in scored if z < RARE_ZIPF}
    oob_words = [w for w, _ in sorted(oob.items(), key=lambda kv: kv[1])][:50]
    return {
        "suggested_level": _level_for(pct),
        "out_of_band_pct": round(pct, 1),
        "out_of_band_words": oob_words,
    }

"""SPIKE-03 (LGA-25): frequency-band leveling on Spanish text, calibrated.

Coverage-first leveling (D-25/D-28): tokenize accent-aware, look each token up in
a real Spanish frequency corpus (wordfreq, chosen over the OSF SUBTLEX download),
compute the "out-of-band" (rare/unknown) rate, and map it to an L1..L8 level.

Corpus: `wordfreq.zipf_frequency(word, "es")` — a 0–8 scale (higher = more common:
`el`≈7.4, `gato`≈4.6, `felino`≈3.1, `adarga`≈1.7, unknown=0.0). A word is
"out-of-band" for a beginner if its zipf is below RARE_ZIPF.

Calibration set is LEGALLY CLEAN (D-47): a hand-authored L1 text + public-domain
graded texts spanning easy→hard (a traditional nursery rhyme; a Samaniego fable,
public domain d.1801; the Don Quijote opening). No copyrighted graded-reader text.

Production refinement (M1): add lemmatization (simplemma, D-26) so conjugations
collapse to lemmas before the frequency lookup; pin `wordfreq` in requirements.
"""
import re
import statistics

from wordfreq import zipf_frequency

# Words rarer than this zipf are "out-of-band". Calibrated on the gradient below:
# 3.5 orders the texts correctly for the BEGINNER range (simple→L1, folk texts→L2,
# classic→L3). 4.5 saturates (~32% for every literary text, so Quijote stopped
# separating from a nursery rhyme) AND flagged conjugations (come/duerme/juegan) as
# false-rare — which is why production needs lemmatization (D-26) and, for a wider
# spread + true i+1, learner-known-words coverage (M3), not corpus frequency alone.
RARE_ZIPF = 3.5

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)  # letters only; keeps á é í ó ú ñ


def tokenize(text):
    return [m.group().lower() for m in WORD_RE.finditer(text)]


def level_for(rare_pct):
    """Coverage-first ladder (D-28 spirit): fewer out-of-band words => lower level."""
    for cap, lvl in [(6, "L1"), (12, "L2"), (20, "L3"), (30, "L4"),
                     (42, "L5"), (55, "L6"), (70, "L7")]:
        if rare_pct <= cap:
            return lvl
    return "L8"


def score(text):
    toks = tokenize(text)
    if not toks:
        return None
    zipfs = [zipf_frequency(t, "es") for t in toks]
    rare = sorted({t for t, z in zip(toks, zipfs) if z < RARE_ZIPF})
    rare_pct = 100 * sum(1 for z in zipfs if z < RARE_ZIPF) / len(toks)
    return {
        "tokens": len(toks),
        "rare_pct": round(rare_pct, 1),
        "median_zipf": round(statistics.median(zipfs), 2),
        "level": level_for(rare_pct),
        "rare_sample": rare[:8],
    }


# Ordered easy -> hard. All legally clean (hand-authored or public domain).
TEXTS = [
    ("L1 hand-authored (simple story)",
     "Hay un gato pequeño. El gato es blanco. El gato come pan y agua. Un niño "
     "ve el gato. El niño y el gato juegan en la casa. La mamá mira y está "
     "feliz. El gato duerme. Es un buen día."),
    ("Public-domain nursery rhyme (Los pollitos)",
     "Los pollitos dicen pío, pío, pío, cuando tienen hambre, cuando tienen "
     "frío. La gallina busca el maíz y el trigo, les da la comida y les presta "
     "abrigo. Bajo sus dos alas, acurrucaditos, duermen los pollitos hasta el "
     "otro día."),
    ("Public-domain fable (Samaniego, La cigarra y la hormiga)",
     "Cantando la Cigarra pasó el verano entero, sin hacer provisiones allá "
     "para el invierno. Los fríos la obligaron a guardar el silencio y a "
     "acogerse al abrigo de su estrecho aposento."),
    ("Public-domain classic (Don Quijote opening)",
     "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha mucho "
     "tiempo que vivía un hidalgo de los de lanza en astillero, adarga antigua, "
     "rocín flaco y galgo corredor."),
]


if __name__ == "__main__":
    print(f"Corpus: wordfreq (es). RARE_ZIPF={RARE_ZIPF}. Level = out-of-band %% -> L1..L8.\n")
    for name, text in TEXTS:
        r = score(text)
        print(f"{r['level']:>3}  rare={r['rare_pct']:>5}%  median_zipf={r['median_zipf']:>4}  "
              f"({r['tokens']:>2} tok)  {name}")
        if r["rare_sample"]:
            print(f"      out-of-band e.g.: {', '.join(r['rare_sample'])}")
        print()

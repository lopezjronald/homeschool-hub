"""SPIKE-03 (LGA-25): validate frequency-band leveling on Spanish text.

Validates the MECHANISM of coverage-first leveling (D-25/D-28): tokenize
accent-aware, look each token up in a Spanish frequency band, compute the
out-of-band ("unknown") rate, and map it to an L1..L8 level. Shows that an
easy top-frequency text scores low and a lexically rich / archaic text scores
high — i.e. the coverage signal discriminates difficulty.

HONESTY / SCOPE: this uses a small ~150-word SAMPLE frequency list (a stand-in
for the real corpus) and legally-clean texts (hand-authored + public-domain Don
Quijote). It validates the ALGORITHM, not final CALIBRATION. Calibrating
"Fluency Matters L1 actually scores as L1" needs two decisions (see DECISIONS.md
SPIKE-03):
  1. the real frequency corpus — SUBTLEX-ESP (OSF download) or the `wordfreq`
     package (pip; bundles Spanish incl. SUBTLEX-derived data);
  2. legally-sourced graded L2 texts — their published text is copyrighted
     (D-47), so validate against owned copies (local fair-use analysis) or
     public-domain graded readers.
Swapping the sample list for the real corpus is a one-line data change; the
scorer below is the reusable M1 engine core.
"""
import re

# ~150 most-common Spanish words (rough frequency order) — SAMPLE stand-in for
# SUBTLEX-ESP. Rank = list position. Function words + common kid-story vocab +
# frequent verb surface forms (production uses lemmatization — simplemma, D-26 —
# so conjugations collapse to lemmas; here we include a few surface forms so the
# demo doesn't over-count unknowns for lack of a lemmatizer).
FREQ_SAMPLE = [
    "el", "la", "de", "que", "y", "a", "en", "un", "una", "ser", "es", "se",
    "no", "haber", "por", "con", "su", "para", "como", "estar", "está", "tener",
    "tiene", "le", "lo", "los", "las", "del", "al", "pero", "más", "o", "si",
    "sí", "ya", "muy", "cuando", "porque", "este", "esta", "eso", "ese", "me",
    "mi", "te", "tu", "nos", "yo", "él", "ella", "hay", "son", "fue", "era",
    "dos", "tres", "también", "hasta", "desde", "donde", "aquí", "allí", "bien",
    "poco", "mucho", "todo", "toda", "todos", "nada", "algo", "cada", "otro",
    "otra", "uno", "primero",
    # verbs (base + frequent conjugations)
    "ir", "va", "voy", "ver", "ve", "veo", "dar", "hacer", "hace", "decir",
    "dice", "poder", "puede", "querer", "quiere", "saber", "sabe", "comer",
    "come", "jugar", "juega", "juegan", "mirar", "mira", "correr", "corre",
    "dormir", "duerme", "vivir", "vive", "llegar", "llega", "gustar", "gusta",
    "leer", "lee",
    # common kid-story nouns
    "gato", "perro", "casa", "niño", "niña", "mamá", "papá", "agua", "pan",
    "libro", "escuela", "amigo", "amiga", "sol", "luna", "árbol", "pájaro",
    "flor", "día", "noche", "mano", "cosa", "tiempo", "año", "vez", "hombre",
    "mujer", "gente", "vida",
    # adjectives / descriptors
    "grande", "pequeño", "pequeña", "bueno", "buen", "buena", "malo", "nuevo",
    "feliz", "blanco", "negro", "rojo", "azul", "verde", "bonito", "alto",
    "bajo", "contento",
]
RANK = {w: i for i, w in enumerate(FREQ_SAMPLE)}

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)  # letters only; keeps á é í ó ú ñ


def tokenize(text):
    return [m.group().lower() for m in WORD_RE.finditer(text)]


def level_for(unknown_pct):
    """Coverage-first ladder (D-28 spirit): fewer out-of-band words => lower level."""
    for cap, lvl in [(2, "L1"), (5, "L2"), (10, "L3"), (18, "L4"),
                     (28, "L5"), (40, "L6"), (55, "L7")]:
        if unknown_pct <= cap:
            return lvl
    return "L8"


def score(text):
    toks = tokenize(text)
    if not toks:
        return None
    unknown = [t for t in toks if t not in RANK]
    unknown_pct = 100 * len(unknown) / len(toks)
    return {
        "tokens": len(toks),
        "unknown_pct": round(unknown_pct, 1),
        "level": level_for(unknown_pct),
        "sample_unknown": sorted(set(unknown))[:8],
    }


TEXTS = {
    "L1 hand-authored (top-frequency only)": (
        "Hay un gato pequeño. El gato es blanco. El gato come pan y agua. "
        "Un niño ve el gato. El niño y el gato juegan en la casa. La mamá "
        "mira y está feliz. El gato duerme. Es un buen día."
    ),
    "Rich vocabulary (hand-authored, harder)": (
        "El felino acechaba sigilosamente entre la espesura, contemplando el "
        "ocaso mientras reflexionaba sobre su melancólica existencia."
    ),
    "Public-domain (Don Quijote opening)": (
        "En un lugar de la Mancha, de cuyo nombre no quiero acordarme, no ha "
        "mucho tiempo que vivía un hidalgo de los de lanza en astillero, adarga "
        "antigua, rocín flaco y galgo corredor."
    ),
}


if __name__ == "__main__":
    print(f"Sample corpus: {len(FREQ_SAMPLE)} words. Level = out-of-band %% -> L1..L8.\n")
    for name, text in TEXTS.items():
        r = score(text)
        print(f"{r['level']:>3}  unknown={r['unknown_pct']:>5}%  "
              f"({r['tokens']:>2} tokens)  {name}")
        print(f"      out-of-band e.g.: {', '.join(r['sample_unknown'])}\n")

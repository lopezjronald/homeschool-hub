"""Explicit pronunciations for words whose SOUND is the whole lesson (LGA-101).

Polly is normally left to its own devices, which is fine for a story. It is not fine
on the phonics page, where the entire point of tapping "llama" is to hear what ``ll``
does — the owner reported it coming out closer to a plain /l/. A phonics example that
mispronounces the sound it is teaching is worse than no audio at all.

So the handful of words that demonstrate a contrast carry an IPA transcription, and
``synthesize_clip`` wraps them in SSML ``<phoneme>``. Everything else still goes
through as plain text; this is a targeted override, not a pronunciation dictionary.

Transcriptions are MEXICAN Spanish (D-02: es-MX):
  * yeísmo — ``ll`` and ``y`` are both /ʝ/, so "llama" is /ˈʝama/, never /ˈlama/
  * seseo  — ``c`` before e/i and ``z`` are /s/, never /θ/
  * ``rr`` is the trill /r/; a single intervocalic ``r`` is the tap /ɾ/

Stress is marked with ˈ before the stressed syllable, and syllables are separated with
. so Polly places the beat where the spelling says it should.
"""

# word -> IPA. Keys are matched EXACTLY against the seeded example words.
IPA = {
    # ll — yeísmo. This is the one the owner reported as sounding like a plain "l".
    "llama": "ˈʝa.ma",
    "pollo": "ˈpo.ʝo",
    "calle": "ˈka.ʝe",
    "lluvia": "ˈʝu.βja",
    # y — the same sound, which is the point of pairing them
    "yema": "ˈʝe.ma",
    "ya": "ʝa",
    # rr — the trill, so it is audibly not the tap in "pero"
    "perro": "ˈpe.ro",
    "carro": "ˈka.ro",
    "gorra": "ˈɡo.ra",
    "tierra": "ˈtje.ra",
    # ñ
    "niño": "ˈni.ɲo",
    "España": "es.ˈpa.ɲa",
    "mañana": "ma.ˈɲa.na",
    "señor": "se.ˈɲoɾ",
    # j and g before e/i — the velar fricative, not an English "j"
    "jugar": "xu.ˈɣaɾ",
    "caja": "ˈka.xa",
    "rojo": "ˈro.xo",
    "trabajo": "tɾa.ˈβa.xo",
    "gente": "ˈxen.te",
    # gu keeps the hard g; ü makes the u sound again
    "guitarra": "ɡi.ˈta.ra",
    "guerra": "ˈɡe.ra",
    "pingüino": "piŋ.ˈɡwi.no",
    "vergüenza": "beɾ.ˈɡwen.sa",
    "bilingüe": "bi.ˈliŋ.ɡwe",
    "cigüeña": "si.ˈɣwe.ɲa",
    # h muda — silent, so it must not be aspirated
    "hola": "ˈo.la",
    "hoy": "oi̯",
    "huevo": "ˈwe.βo",
    "hermano": "eɾ.ˈma.no",
}


def ipa_for(text):
    """The IPA override for this exact word, or None to let Polly decide."""
    return IPA.get((text or "").strip())

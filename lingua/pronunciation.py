"""Pronunciation overrides for the handful of texts Polly gets WRONG (LGA-101).

Deliberately tiny. An earlier version of this file transcribed 29 phonics words on the
theory that "llama" was coming out as a plain /l/. Measuring it against Polly proved
that wrong: plain-text ``llama`` already yields viseme ``J`` (palatal /ʝ/, correct
yeísmo) and the SSML override produced a byte-identical mp3. Overrides that change
nothing are worse than none — they imply a fix that isn't happening, and they churn
content hashes so clips re-bake for no reason.

What IS wrong is one alphabet tile. Measured with Polly viseme speech marks, voice
Mia / neural / es-MX:

    ll -> "elle"  ->  e-t        <-- alveolar /l/, and truncated to two visemes
    l  -> "ele"   ->  e-t-e
    y  -> "ye"    ->  J-e        (correct palatal)
    ñ  -> "eñe"   ->  e-J-e      (correct)
    rr -> "erre"  ->  e-r-e      (trill present, correct)

So tapping the ``ll`` tile said something close to the letter L — exactly the report.
Every other tile and every phonics example word measured correct and is left alone.

Add an entry here only after measuring that it changes the output, and record what you
measured. ``J`` is the palatal viseme, ``t`` the alveolar one; that pair is what
distinguishes these two sounds.
"""

# text -> IPA, for texts Polly demonstrably mispronounces. es-MX (D-02): yeísmo means
# ll and y are both /ʝ/; ʎ is es-ES only and Polly's es-MX table doesn't carry it.
IPA = {
    # The letter NAME for ll. Polly reads it as /el/; the Spanish name is /ˈe.ʝe/.
    "elle": "ˈe.ʝe",
}


def ipa_for(text):
    """The IPA override for this exact text, or None to let Polly decide.

    None is the overwhelmingly common answer and the right default — Polly's es-MX is
    good, and a wrong transcription is worse than no transcription because Polly
    silently ignores symbols outside its table rather than erroring.
    """
    return IPA.get((text or "").strip())

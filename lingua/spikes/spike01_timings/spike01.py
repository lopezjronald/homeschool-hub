"""SPIKE-01 (LGA-23): Polly vs edge-tts word timings for Spanish read-along.

Validates the #1 build risk: can we pre-generate accurate word-level timings for a
Spanish story (with accents / ñ / ¿¡) and highlight the SOURCE word as audio plays?

Key hazard under test: Amazon Polly speech-mark start/end are UTF-8 BYTE offsets into
the submitted text. Spanish accented chars (á é í ó ú ñ ¿ ¡) are 2 bytes in UTF-8, so
naive text[start:end] drifts after the first accent. We build a byte->char map and
store CHARACTER offsets (what JS strings use). edge-tts gives spoken-word text + audio
offset (100ns ticks) but NO source offsets, so we align spoken words to source tokens.

Usage (each provider needs its own venv):
  # free credential/connectivity + es-MX voice check (no synthesis, no cost):
  <hub .venv>/python spike01.py check
  # Polly arm (boto3; ~$0.02 for this story on neural):
  <hub .venv>/python spike01.py polly --voice Mia
  # edge-tts arm (free, no key):
  <fitness .venv>/python spike01.py edge --voice es-MX-DaliaNeural
  # offline self-test of the byte->char mapping (no API, no deps):
  python spike01.py selftest
  # build the read-along HTML from whatever <provider>.timings.json exist:
  python spike01.py build-html

Outputs (in this dir): <provider>.mp3, <provider>.timings.json, readalong.html
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORY = (HERE / "story_es.txt").read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# byte<->char mapping (the load-bearing correctness piece)
# ---------------------------------------------------------------------------
def byte_to_char_map(text):
    """Map every UTF-8 byte offset in `text` to its Python str (code-point) index.
    Includes the terminal offset (== len(text))."""
    m = {}
    b = 0
    for ci, ch in enumerate(text):
        m[b] = ci
        b += len(ch.encode("utf-8"))
    m[b] = len(text)
    return m


# ---------------------------------------------------------------------------
# source tokenization: split into display tokens (word + trailing punct) with
# char ranges, so the front end can wrap each in a <span data-i>.
# ---------------------------------------------------------------------------
WORD_RE = re.compile(r"\S+", re.UNICODE)


def display_tokens(text):
    """Whitespace-delimited display tokens with (char_start, char_end)."""
    return [(m.start(), m.end(), m.group()) for m in WORD_RE.finditer(text)]


def token_index_for_char(tokens, cs):
    for i, (a, b, _t) in enumerate(tokens):
        if a <= cs < b:
            return i
    return None


# ---------------------------------------------------------------------------
# Polly arm
# ---------------------------------------------------------------------------
def polly_client():
    import boto3
    return boto3.client("polly")


def run_check():
    """Free: confirm creds + list es-MX neural voices."""
    try:
        c = polly_client()
        resp = c.describe_voices(LanguageCode="es-MX")
    except Exception as exc:  # noqa: BLE001
        print(f"CHECK FAILED: {exc}")
        return 1
    voices = [(v["Id"], v["Gender"], ",".join(v.get("SupportedEngines", [])))
              for v in resp.get("Voices", [])]
    print("Polly reachable. es-MX voices:")
    for vid, gender, engines in voices:
        print(f"  {vid:10} {gender:7} engines={engines}")
    return 0


def run_polly(voice="Mia"):
    c = polly_client()
    # audio
    audio = c.synthesize_speech(Text=STORY, VoiceId=voice, Engine="neural",
                                OutputFormat="mp3")
    (HERE / "polly.mp3").write_bytes(audio["AudioStream"].read())
    # marks (separate render; JSON-Lines, NOT a JSON array)
    marks = c.synthesize_speech(Text=STORY, VoiceId=voice, Engine="neural",
                                OutputFormat="json", SpeechMarkTypes=["word"])
    raw = marks["AudioStream"].read().decode("utf-8")
    events = [json.loads(line) for line in raw.splitlines() if line.strip()]

    b2c = byte_to_char_map(STORY)
    src_bytes = STORY.encode("utf-8")
    tokens = display_tokens(STORY)

    words = []
    drift_errors = 0
    for e in events:
        if e.get("type") != "word":
            continue
        bstart, bend = e["start"], e["end"]
        # byte-sliced source word (correct) vs value Polly reports
        byte_word = src_bytes[bstart:bend].decode("utf-8")
        cs, ce = b2c.get(bstart), b2c.get(bend)
        # naive (WRONG) char slice to demonstrate the drift
        naive = STORY[bstart:bend]
        if byte_word != e.get("value"):
            # Polly may normalize (e.g. numerals); note but don't fail
            pass
        ti = token_index_for_char(tokens, cs) if cs is not None else None
        words.append({"t_ms": e["time"], "cs": cs, "ce": ce,
                      "value": e.get("value"), "byte_word": byte_word,
                      "naive_char_slice": naive, "token": ti})
        if naive != byte_word:
            drift_errors += 1

    # end times = next word start (last = +400ms)
    for i, w in enumerate(words):
        w["s_ms"] = w["t_ms"]
        w["e_ms"] = words[i + 1]["t_ms"] if i + 1 < len(words) else w["t_ms"] + 400

    flat = _flat_by_token(words, tokens)
    out = {"provider": "polly", "voice": voice, "audio": "polly.mp3",
           "story": STORY, "tokens": [t[2] for t in tokens],
           "token_spans": [[t[0], t[1]] for t in tokens], "words": flat,
           "n_word_events": len(words),
           "naive_char_slice_drift_count": drift_errors}
    (HERE / "polly.timings.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    print(f"Polly: {len(words)} word marks; naive-char-slice drift on "
          f"{drift_errors}/{len(words)} words (byte->char map fixes all of them).")
    print("Wrote polly.mp3 + polly.timings.json")
    return 0


# ---------------------------------------------------------------------------
# edge-tts arm
# ---------------------------------------------------------------------------
def run_edge(voice="es-MX-DaliaNeural"):
    import asyncio
    import edge_tts

    async def synth():
        # edge-tts 7.x defaults boundary="SentenceBoundary"; word-level read-along
        # REQUIRES explicitly requesting WordBoundary.
        comm = edge_tts.Communicate(STORY, voice, boundary="WordBoundary")
        audio = bytearray()
        boundaries = []
        async for chunk in comm.stream():
            if chunk["type"] == "audio":
                audio.extend(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                boundaries.append(chunk)
        return bytes(audio), boundaries

    audio, boundaries = asyncio.run(synth())
    (HERE / "edge.mp3").write_bytes(audio)

    tokens = display_tokens(STORY)
    # edge gives spoken text + offset(100ns) + duration; no source offsets.
    # Align each WordBoundary to the next display token sequentially.
    words = []
    for i, wb in enumerate(boundaries):
        s_ms = wb["offset"] / 10000.0
        e_ms = (wb["offset"] + wb["duration"]) / 10000.0
        ti = i if i < len(tokens) else None
        words.append({"s_ms": round(s_ms), "e_ms": round(e_ms),
                      "value": wb["text"], "token": ti})

    flat = _flat_by_token(words, tokens)
    out = {"provider": "edge", "voice": voice, "audio": "edge.mp3",
           "story": STORY, "tokens": [t[2] for t in tokens],
           "token_spans": [[t[0], t[1]] for t in tokens], "words": flat,
           "n_word_events": len(words),
           "align_note": "sequential spoken->source token alignment (edge has no source offsets)",
           "token_count_vs_events": [len(tokens), len(words)]}
    (HERE / "edge.timings.json").write_text(json.dumps(out, ensure_ascii=False, indent=2),
                                            encoding="utf-8")
    print(f"edge-tts: {len(words)} WordBoundary events vs {len(tokens)} source tokens.")
    print("Wrote edge.mp3 + edge.timings.json")
    return 0


def _flat_by_token(words, tokens):
    """Collapse word events onto display tokens -> [{i, s, e}] for the player."""
    by_token = {}
    for w in words:
        ti = w.get("token")
        if ti is None:
            continue
        if ti not in by_token:
            by_token[ti] = {"i": ti, "s": w["s_ms"], "e": w["e_ms"]}
        else:
            by_token[ti]["e"] = w["e_ms"]  # extend to cover multi-word tokens
    return [by_token[i] for i in sorted(by_token)]


# ---------------------------------------------------------------------------
# offline self-test: prove the byte->char map fixes accent drift with no API
# ---------------------------------------------------------------------------
def run_selftest():
    text = "¿Dónde está el pájaro? ¡Ñoño corre!"
    b = text.encode("utf-8")
    b2c = byte_to_char_map(text)
    # simulate what a byte-offset provider would report for each word
    ok = True
    drift = 0
    for m in WORD_RE.finditer(text):
        cs, ce = m.start(), m.end()
        # byte offsets for this word
        bstart = len(text[:cs].encode("utf-8"))
        bend = len(text[:ce].encode("utf-8"))
        naive = text[bstart:bend]              # WRONG (treats byte idx as char idx)
        mapped = text[b2c[bstart]:b2c[bend]]   # RIGHT (via byte->char map)
        if naive != m.group():
            drift += 1
        if mapped != m.group():
            ok = False
            print(f"  MISMATCH: word={m.group()!r} mapped={mapped!r}")
    print(f"selftest text: {text!r}")
    print(f"  naive byte-as-char slicing was WRONG on {drift} words")
    print(f"  byte->char map recovered the correct word on ALL words: {ok}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# read-along HTML (rAF highlight; eyeball the sync)
# ---------------------------------------------------------------------------
HTML = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<title>SPIKE-01 read-along</title><style>
body{font:1.4rem/1.9 system-ui;margin:2rem auto;max-width:44rem;color:#222}
.tok{padding:.05em .1em;border-radius:.2em}
.tok.on{background:#ffd54a;box-shadow:0 0 0 .1em #ffd54a}
h1{font-size:1rem;color:#666;font-weight:600}
.row{margin:1rem 0}audio{width:100%}button{font-size:1rem;padding:.4em .8em;margin-right:.5em}
</style></head><body>
<h1>SPIKE-01 &mdash; word-level read-along sync test</h1>
<div class="row" id="controls"></div>
<div class="row" id="story"></div>
<script>
const DATA = __DATA__;
const story = document.getElementById('story');
const controls = document.getElementById('controls');
function build(key){
  const d = DATA[key]; if(!d){return;}
  story.innerHTML='';
  const spans=[];
  d.tokens.forEach((t,i)=>{const s=document.createElement('span');
    s.className='tok';s.dataset.i=i;s.textContent=t;story.appendChild(s);
    story.appendChild(document.createTextNode(' '));spans[i]=s;
    s.onclick=()=>{const w=d.words.find(w=>w.i===i);if(w){audio.currentTime=w.s/1000;audio.play();}};});
  const audio=new Audio(d.audio);audio.controls=true;
  const wrap=document.createElement('div');wrap.appendChild(audio);story.parentNode.insertBefore(wrap,story);
  const words=d.words; let raf;
  function tick(){const tms=audio.currentTime*1000;
    // binary search for active token
    let lo=0,hi=words.length-1,act=-1;
    while(lo<=hi){const mid=(lo+hi)>>1;if(words[mid].s<=tms){act=mid;lo=mid+1;}else{hi=mid-1;}}
    spans.forEach(s=>s.classList.remove('on'));
    if(act>=0 && tms<=words[act].e+120){spans[words[act].i]?.classList.add('on');}
    raf=requestAnimationFrame(tick);}
  audio.onplay=()=>{cancelAnimationFrame(raf);tick();};
  audio.onpause=()=>cancelAnimationFrame(raf);
  window.scrollTo(0,0);
}
Object.keys(DATA).forEach(k=>{const b=document.createElement('button');
  b.textContent=DATA[k].provider+' / '+DATA[k].voice;b.onclick=()=>build(k);controls.appendChild(b);});
if(Object.keys(DATA).length)build(Object.keys(DATA)[0]);
</script></body></html>"""


def run_build_html():
    data = {}
    for p in ("polly", "edge"):
        f = HERE / f"{p}.timings.json"
        if f.exists():
            data[p] = json.loads(f.read_text(encoding="utf-8"))
    if not data:
        print("No <provider>.timings.json found yet. Run the polly/edge arm first.")
        return 1
    html = HTML.replace("__DATA__", json.dumps(data, ensure_ascii=False))
    (HERE / "readalong.html").write_text(html, encoding="utf-8")
    print(f"Wrote readalong.html ({', '.join(data)})")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "selftest"
    kw = {}
    if "--voice" in sys.argv:
        kw["voice"] = sys.argv[sys.argv.index("--voice") + 1]
    sys.exit({
        "check": run_check,
        "polly": run_polly,
        "edge": run_edge,
        "selftest": run_selftest,
        "build-html": run_build_html,
    }[cmd](**kw))

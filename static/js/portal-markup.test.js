/* Tests for the markup stroke reader. Run by tutor.tests.MarkupStrokeReaderTests
   via `node`, so it goes through `manage.py test` with no extra toolchain.

   The geometry is MEASURED from the real reader, not invented. A word span is
   the font's full ascent+descent — 27px for the reader's 24px Georgia — while
   the letters occupy only ~11.6px of it, sitting low in the box. Guessing those
   numbers is exactly what made the first version read a strike as an underline
   and a snug circle as a strike, so the fixtures use the real ratios:

       line box   y 0.30 .. 0.66   (height 0.36)
       letters    y 0.44 .. 0.59   (glyph band, low in the box)
*/
const { readMarkup } = require("./portal-markup.js");

const BOX = { y0: 0.30, y1: 0.66 };
const GLY = { gy0: 0.44, gy1: 0.59 };
const word = (i, text, x0, x1) =>
  Object.assign({ i: i, text: text, x0: x0, x1: x1 }, BOX, GLY);

const WORDS = [
  word(0, "Seth", 0.05, 0.25),
  word(1, "is", 0.30, 0.45),
  word(2, "a", 0.50, 0.56),      // one letter: narrow
  word(3, "vet.", 0.61, 0.90),
];

const stroke = (pts) => ({ c: "#333", w: 3, p: pts });
let pass = 0, fail = 0;

function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}
const kinds = (r) => r.marks.map((m) => `${m.kind} "${m.word}"`);

// ---- the three gestures, drawn where a child actually draws them ----

check("underline just below the letters",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.62], [0.15, 0.625], [0.24, 0.62]])])),
  ['underlined "Seth"']);

// A strike goes through the middle of the LETTERS (~0.515) — which is well below
// the middle of the line box (0.48). Reading this as an underline was the bug.
check("strike through the letters is not an underline",
  kinds(readMarkup(WORDS, [stroke([[0.31, 0.515], [0.38, 0.515], [0.44, 0.517]])])),
  ['crossed out "is"']);

// A circle hugging the letters never reaches the line-box edges, which is why
// closure — not vertical reach — is what identifies it.
check("circle hugging the letters is not a cross-out",
  kinds(readMarkup(WORDS, [stroke([
    [0.60, 0.515], [0.66, 0.42], [0.80, 0.42], [0.91, 0.515],
    [0.80, 0.61], [0.66, 0.61], [0.605, 0.52]])])),
  ['circled "vet."']);

check("a loose, larger circle still reads as circled",
  kinds(readMarkup(WORDS, [stroke([
    [0.58, 0.51], [0.65, 0.33], [0.85, 0.33], [0.93, 0.51],
    [0.85, 0.66], [0.65, 0.66], [0.585, 0.52]])])),
  ['circled "vet."']);

// ---- open gestures that must NOT become circles ----

check("a check mark is not a circle",
  kinds(readMarkup(WORDS, [stroke([[0.31, 0.50], [0.36, 0.58], [0.45, 0.36]])])),
  []);

check("a caret / insertion mark reads as nothing",
  kinds(readMarkup(WORDS, [stroke([[0.46, 0.62], [0.48, 0.52], [0.50, 0.62]])])),
  []);

check("a diagonal slash across the sentence is not a gesture",
  kinds(readMarkup(WORDS, [stroke([[0.05, 0.30], [0.50, 0.50], [0.90, 0.66]])])),
  []);

// ---- spans and ordering ----

check("one long underline covers every word it passes under",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.62], [0.50, 0.62], [0.89, 0.62]])])),
  ['underlined "Seth"', 'underlined "is"', 'underlined "a"', 'underlined "vet."']);

check("marks sort by word position, not stroke order",
  kinds(readMarkup(WORDS, [
    stroke([[0.61, 0.62], [0.90, 0.62]]),
    stroke([[0.06, 0.62], [0.25, 0.62]]),
  ])),
  ['underlined "Seth"', 'underlined "vet."']);

check("re-tracing a word does not duplicate the mark",
  kinds(readMarkup(WORDS, [
    stroke([[0.06, 0.62], [0.25, 0.62]]),
    stroke([[0.06, 0.615], [0.25, 0.615]]),
  ])),
  ['underlined "Seth"']);

// ---- refusals: an unread mark beats a wrong one ----

const scribble = readMarkup(WORDS, [stroke([[0.30, 0.05], [0.40, 0.10], [0.35, 0.02]])]);
check("a scribble above the line reads nothing", kinds(scribble), []);
check("...and is counted unread", scribble.unread, 1);

check("a line drawn far below the sentence underlines nothing",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.95], [0.25, 0.95]])])),
  []);

check("a stroke grazing the edge of a word is ignored",
  kinds(readMarkup(WORDS, [stroke([[0.24, 0.62], [0.28, 0.62]])])),
  []);

// ---- degenerate input ----

check("a single-point tap is unread", readMarkup(WORDS, [stroke([[0.1, 0.5]])]).unread, 1);
check("no words means everything is unread", readMarkup([], [stroke([[0, 0], [1, 1]])]).unread, 1);
check("no strokes means no marks", readMarkup(WORDS, []).marks, []);
check("a word with no glyph band falls back to its line box",
  kinds(readMarkup([{ i: 0, text: "Seth", x0: 0.05, x1: 0.25, y0: 0.30, y1: 0.66 }],
                   [stroke([[0.06, 0.70], [0.24, 0.70]])])),
  ['underlined "Seth"']);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

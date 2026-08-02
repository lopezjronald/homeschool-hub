/* Tests for the markup stroke reader. Run by tutor.tests.MarkupStrokeReaderTests
   via `node`, so it goes through `manage.py test` with no extra toolchain.

   Geometry is realistic:
   One line of four words across a surface: each word ~20% wide, sitting in the
   vertical band 0.30 - 0.70 (so word height 0.40, mid-line 0.50). */
const { readMarkup } = require("./portal-markup.js");

const WORDS = [
  { i: 0, text: "Seth", x0: 0.05, x1: 0.25, y0: 0.30, y1: 0.70 },
  { i: 1, text: "is",   x0: 0.30, x1: 0.45, y0: 0.30, y1: 0.70 },
  { i: 2, text: "a",    x0: 0.50, x1: 0.58, y0: 0.30, y1: 0.70 },
  { i: 3, text: "vet.", x0: 0.63, x1: 0.90, y0: 0.30, y1: 0.70 },
];

const stroke = (pts) => ({ c: "#333", w: 3, p: pts });
let pass = 0, fail = 0;

function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}

const kinds = (r) => r.marks.map((m) => `${m.kind} "${m.word}"`);

// --- underline: flat line below the word ---
check("underline under Seth",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.66], [0.15, 0.67], [0.24, 0.66]])])),
  ['underlined "Seth"']);

// --- circle: loop that goes above and below ---
check("circle round vet.",
  kinds(readMarkup(WORDS, [stroke([
    [0.64, 0.50], [0.70, 0.28], [0.85, 0.30], [0.89, 0.50],
    [0.85, 0.72], [0.70, 0.71], [0.64, 0.50]])])),
  ['circled "vet."']);

// --- strike: flat line through the middle ---
check("cross out is",
  kinds(readMarkup(WORDS, [stroke([[0.31, 0.50], [0.38, 0.50], [0.44, 0.51]])])),
  ['crossed out "is"']);

// --- a stroke spanning several words underlines each of them ---
check("one long underline covers three words",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.66], [0.50, 0.66], [0.89, 0.66]])])),
  ['underlined "Seth"', 'underlined "is"', 'underlined "a"', 'underlined "vet."']);

// --- marks come back in reading order regardless of drawing order ---
check("marks sort by word position, not stroke order",
  kinds(readMarkup(WORDS, [
    stroke([[0.64, 0.66], [0.89, 0.66]]),   // vet. drawn first
    stroke([[0.06, 0.66], [0.24, 0.66]]),   // Seth drawn second
  ])),
  ['underlined "Seth"', 'underlined "vet."']);

// --- a scribble in empty space is UNREAD, not a wrong guess ---
const scribble = readMarkup(WORDS, [stroke([[0.30, 0.05], [0.40, 0.10], [0.35, 0.02]])]);
check("scribble above the line reads nothing", kinds(scribble), []);
check("...and is counted unread", scribble.unread, 1);

// --- a stroke barely clipping a word is not counted ---
check("a stroke grazing the edge of a word is ignored",
  kinds(readMarkup(WORDS, [stroke([[0.24, 0.66], [0.27, 0.66]])])),
  []);

// --- a line drawn well BELOW the text is not "underlining" it ---
// Found in a real browser: "below the middle of the word" had no floor, so a
// stroke way beneath the sentence still claimed the word above it.
check("a stroke far below the word is not an underline",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.95], [0.24, 0.95]])])),
  []);

// --- but a normal underline sitting just under the word still reads ---
check("an underline just beneath the baseline still reads",
  kinds(readMarkup(WORDS, [stroke([[0.06, 0.74], [0.24, 0.74]])])),
  ['underlined "Seth"']);

// --- degenerate input ---
check("a single-point tap is unread", readMarkup(WORDS, [stroke([[0.1, 0.5]])]).unread, 1);
check("no words means everything is unread", readMarkup([], [stroke([[0, 0], [1, 1]])]).unread, 1);
check("no strokes means no marks", readMarkup(WORDS, []).marks, []);

// --- the same word underlined twice is one mark ---
check("re-tracing a word does not duplicate the mark",
  kinds(readMarkup(WORDS, [
    stroke([[0.06, 0.66], [0.24, 0.66]]),
    stroke([[0.06, 0.65], [0.24, 0.65]]),
  ])),
  ['underlined "Seth"']);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

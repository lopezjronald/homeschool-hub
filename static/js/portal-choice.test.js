/* Tests for the ordering widget's core. Run by tutor.tests via node.

   This is the part that decides whether a question counts as ANSWERED, and the
   counter it feeds sits directly above "Turn it in 🚀", which she cannot undo.
   A half-numbered question that reports itself finished is how a child submits
   work she thought she still had time on. */
const { placeSteps } = require("./portal-choice.js");

let pass = 0, fail = 0;
function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}

const STEPS = ["Make a claim", "Present your conclusions", "Ask a compelling question",
               "Search for answers / Experiment", "Interpret the information"];

// The whole point: the right numbering rebuilds the right sequence.
check("a complete numbering is the sequence she meant",
  placeSteps(STEPS, ["2", "5", "1", "3", "4"]).order,
  ["Ask a compelling question", "Make a claim", "Search for answers / Experiment",
   "Interpret the information", "Present your conclusions"]);
check("...and only then does it count as answered",
  placeSteps(STEPS, ["2", "5", "1", "3", "4"]).full, true);

// The bug this file exists for. One number in the LAST slot used to make a
// bare array of length 5 whose holes every() skips.
const lastOnly = placeSteps(STEPS, ["", "5", "", "", ""]);
check("one number in the last slot is not a finished answer", lastOnly.full, false);
check("...and the empty slots store as blanks, never as holes or nulls",
  lastOnly.order, ["", "", "", "", "Present your conclusions"]);
check("...which survives JSON without turning into null",
  JSON.parse(JSON.stringify(lastOnly.order)),
  ["", "", "", "", "Present your conclusions"]);

check("one number in the first slot is not finished either",
  placeSteps(STEPS, ["1", "", "", "", ""]).full, false);
check("four of five is still not five",
  placeSteps(STEPS, ["2", "5", "1", "3", ""]).full, false);

// Nothing entered is nothing stored — the widget writes '' and the report says
// "(no answer)" rather than five blank lines.
const blank = placeSteps(STEPS, ["", "", "", "", ""]);
check("an untouched question has not been started", blank.started, false);
check("...and is not answered", blank.full, false);
check("one number means she has started", placeSteps(STEPS, ["3", "", "", "", ""]).started, true);

// Junk in the picker must not land a step in a slot that does not exist, or
// silently drop one and call the rest complete.
check("a number past the end is ignored, not stored off the end",
  placeSteps(STEPS, ["9", "", "", "", ""]).order, ["", "", "", "", ""]);
check("zero is not a position", placeSteps(STEPS, ["0", "", "", "", ""]).started, false);
check("a negative is not a position",
  placeSteps(STEPS, ["-1", "", "", "", ""]).order, ["", "", "", "", ""]);
check("nonsense is not a position",
  placeSteps(STEPS, ["abc", "", "", "", ""]).started, false);
check("out-of-range junk cannot make an incomplete answer look complete",
  placeSteps(STEPS, ["2", "5", "1", "3", "99"]).full, false);

// A collision should be impossible from the UI (the widget swaps), but if two
// rows ever claim the same number, the answer must not read as finished.
const clash = placeSteps(STEPS, ["1", "1", "2", "3", "4"]);
check("two rows claiming one number leaves a gap, so it is not finished",
  clash.full, false);

console.log(`\n  ${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);

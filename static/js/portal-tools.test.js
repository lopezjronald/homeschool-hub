/* Tests for the Lesson 71 and 72 tool cores. Run by tutor.tests via node. */
const ratio = require("./portal-ratiobar.js");
const sci = require("./portal-scislide.js");

let pass = 0, fail = 0;
function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}

// ---- Lesson 71: the ratio bar ----
const HATS = [{ name: "Red", ratio: 3, tone: "move" }, { name: "Blue", ratio: 4, tone: "start" }];

check("the ratio parts add up to the ratio total",
  ratio.scaleRows(HATS, 1).ratioTotal, 7);

// The whole worked example: 3:4, 60 red -> 140 hats altogether.
const at20 = ratio.scaleRows(HATS, 20);
check("at scale 20 the red row reads 60", at20.parts[0].actual, 60);
check("...and the total reads 140", at20.actualTotal, 140);

// The trap the lesson names: comparing part to part gives 80, and it feels fine.
check("part-to-part would have given the wrong 80, part-to-total gives 140",
  at20.actualTotal === 140 && at20.parts[1].actual === 80, true);

check("scale 1 is just the ratio itself",
  ratio.scaleRows(HATS, 1).parts.map(p => p.actual), [3, 4]);

// ---- Lesson 72: sliding the decimal ----
// The promise the tool makes: the value never changes.
const V = sci.value(3.2, 3);
check("sliding left does not change the value",
  sci.value(sci.shift(3.2, 3, 1).mantissa, sci.shift(3.2, 3, 1).exponent), V);
check("sliding right does not change the value either",
  sci.value(sci.shift(3.2, 3, -1).mantissa, sci.shift(3.2, 3, -1).exponent), V);

// 3.2 x 10^3 -> 0.32 x 10^4, the exact move in Example 72.1a.
const eq = sci.shift(3.2, 3, 1);
check("3.2e3 becomes 0.32e4 when the point slides left",
  [Math.round(eq.mantissa * 100) / 100, eq.exponent], [0.32, 4]);

// 3.2 x 10^5 -> 32 x 10^4, the move in Example 72.2b.
const eq2 = sci.shift(3.2, 5, -1);
check("3.2e5 becomes 32e4 when the point slides right",
  [Math.round(eq2.mantissa * 100) / 100, eq2.exponent], [32, 4]);

check("standard form means one digit before the point",
  [sci.isStandard(1.51), sci.isStandard(15.1), sci.isStandard(0.32)],
  [true, false, false]);

// 15.1 x 10^5 is the answer she must renormalise to 1.51 x 10^6.
check("15.1 is one slide away from standard form", sci.movesToStandard(15.1), 1);
check("0.32 is one slide the other way", sci.movesToStandard(0.32), -1);
check("an already-standard mantissa needs no slide", sci.movesToStandard(4.42), 0);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

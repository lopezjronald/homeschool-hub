/* Tests for the chart and binary cores. Run by tutor.tests.SaxonLessonToolTests
   through node, so they go through `manage.py test` with no extra toolchain.

   The assertions are pinned to the numbers in the Saxon lessons themselves —
   the fish-catch data of Lesson 74 and the binary conversions of Lesson 75 — so
   a tool that stops agreeing with the lesson it serves fails here. */
const C = require("./portal-chart.js");
const B = require("./portal-binary.js");

let pass = 0, fail = 0;
function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}

// Lesson 74's dataset, as the lesson states it.
const FISH = [1000, 2000, 4000, 5000, 6000];

// ---- axis ----
check("the axis top is never below the tallest value",
  C.niceMax(FISH) >= Math.max(...FISH), true);
check("...and lands on a readable round number", C.niceMax(FISH), 6000);
check("a lone value still gets a sane axis", C.niceMax([37]) >= 37, true);
check("an all-zero dataset does not divide by zero", C.niceMax([0, 0]), 1);
check("gridlines run from 0 to the top", C.ticks(6000, 5), [0, 1200, 2400, 3600, 4800, 6000]);

// ---- bars ----
const bars = C.barLayout(FISH, C.niceMax(FISH));
check("the tallest bar reaches the top of the plot",
  Math.abs(bars[4].y - C.plotBox().y) < 0.001, true);
check("every bar sits ON the axis, not through it",
  bars.every(b => Math.abs((b.y + b.h) - (C.plotBox().y + C.plotBox().h)) < 0.001), true);
check("a bar worth half as much is half as tall",
  Math.abs(bars[0].h * 4 - bars[2].h) < 0.001, true);   // 1000 x4 = 4000
check("no bar overflows its own axis",
  bars.every(b => b.h <= C.plotBox().h + 0.001), true);

// ---- pie ----
const slices = C.pieSlices(FISH);
check("slice percentages add to 100",
  Math.abs(slices.reduce((s, x) => s + x.percent, 0) - 100) < 1e-9, true);
check("the sweep of the whole pie is 360 degrees",
  Math.abs(slices.reduce((s, x) => s + x.sweep, 0) - 360) < 1e-9, true);
/* Example 74.4 asks which month held about 1/3 of the catch, and answers
   October at 33.3%. If the widget's own arithmetic disagreed with the lesson's
   stated answer the page would contradict itself in front of her. */
check("October is the ~1/3 slice the lesson says it is",
  slices[4].percent.toFixed(1), "33.3");
check("a single-value pie still draws a full circle, not nothing",
  C.slicePath(C.pieSlices([5])[0], 0, 0, 10).includes("A"), true);
check("an empty dataset yields no slices", C.pieSlices([]), []);

// ---- pictograph ----
/* The practice set states the rule outright: "Half an airplane = 50,000
   tourists." Rounding to whole symbols would delete the half and change the
   answer she is being asked for. */
check("2.5 symbols is two wholes and a half", C.pictoCounts(250000, 100000),
  { whole: 2, half: true });
check("4 exact symbols has no half", C.pictoCounts(4000, 1000),
  { whole: 4, half: false });
check("August is exactly four blocks", C.pictoCounts(4000, 1000).whole, 4);
check("a zero 'per' cannot divide by zero", C.pictoCounts(10, 0),
  { whole: 0, half: false });

// ---- scatter trend ----
/* Example 74.5 in full: Month 1 is (1,1000), Month 5 is (5,6000),
   dy = 5000, dx = 4, slope = 1,250 fish per month. */
check("the lesson's own slope estimate comes out at 1250",
  C.slopeBetween({ index: 1, value: 1000 }, { index: 5, value: 6000 }), 1250);
check("two readings from the same month give no slope, not Infinity",
  C.slopeBetween({ index: 3, value: 10 }, { index: 3, value: 20 }), null);

// ---- binary (Lesson 75) ----
check("place values run biggest first", B.places(5), [16, 8, 4, 2, 1]);
// Example 75.1 a) 1011 = 11, b) 1001 = 9, c) 10011 = 19.
check("75.1a  1011 -> 11", B.toDecimal([1, 0, 1, 1]), 11);
check("75.1b  1001 -> 9", B.toDecimal([1, 0, 0, 1]), 9);
check("75.1c  10011 -> 19", B.toDecimal([1, 0, 0, 1, 1]), 19);
check("every number in the lesson's 1-20 table round-trips",
  Array.from({ length: 20 }, (_, i) => i + 1)
       .every(n => B.toDecimal(B.toBits(n, 5)) === n), true);
check("the table's own binary strings are what the lesson prints",
  [1, 2, 3, 4, 8, 15, 16, 20].map(n => B.toString2(B.toBits(n, 5))),
  ["00001", "00010", "00011", "00100", "01000", "01111", "10000", "10100"]);
/* Showing 19 as "0011" on a four-wide chart would teach that 19 is 3. */
check("a number too big for the chart returns null, not wrong digits",
  B.toBits(19, 4), null);
check("negatives and fractions are refused", [B.toBits(-1, 5), B.toBits(2.5, 5)],
  [null, null]);
/* The zero terms are the lesson's teaching point - "ignore it because you are
   multiplying by 0" - so they have to be ON the page. */
check("the worked line shows the OFF places too",
  B.workedLine([1, 0, 1, 1]), "1(8) + 0(4) + 1(2) + 1(1) = 8 + 2 + 1 = 11");
check("...and matches the lesson for 10011",
  B.workedLine([1, 0, 0, 1, 1]),
  "1(16) + 0(8) + 0(4) + 1(2) + 1(1) = 16 + 2 + 1 = 19");
check("all switches off reads zero without an empty sum",
  B.workedLine([0, 0, 0]), "0(4) + 0(2) + 0(1) = 0");

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

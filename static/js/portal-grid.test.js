/* Tests for the graph-paper core. Run by tutor.tests.SaxonGridToolTests via node,
   so it goes through `manage.py test` with no extra toolchain.

   The arithmetic is the part that can be subtly wrong — a curve that misses her
   points, or an answer marked wrong when it was right — so it is tested directly.
   The DOM half only reads rectangles. */
const { snapToLattice, matchingFamilies, isDecisive, dedupe, sampleCurve,
        transform, FAMILIES, VIEW, SIZE, PAD } = require("./portal-grid.js");

let pass = 0, fail = 0;
function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}

// ---- snapping ----
check("a click near a lattice point snaps to it", snapToLattice(1.8, -2.2), [2, -2]);
check("exactly halfway rounds up, consistently", snapToLattice(1.5, 2.5), [2, 3]);
check("a drag off the right edge parks on the edge", snapToLattice(99, 0), [6, 0]);
check("a drag off the bottom parks on the edge", snapToLattice(0, -99), [0, -6]);

// ---- the two tables from the Saxon lesson ----
const SQUARE = [[-2, 4], [-1, 1], [0, 0], [1, 1], [2, 4]];
const CUBE = [[-2, -8], [-1, -1], [0, 0], [1, 1], [2, 8]];

check("the x squared table matches x^2", matchingFamilies(SQUARE).includes("x^2"), true);
check("...and does NOT match x^3", matchingFamilies(SQUARE).includes("x^3"), false);
check("the x cubed table matches x^3", matchingFamilies(CUBE).includes("x^3"), true);
check("...and does NOT match x^2", matchingFamilies(CUBE).includes("x^2"), false);

// |x| and x^2 agree at -1,0,1 but part company at 2 — the discriminator the
// lesson teaches. Make sure the checker knows the difference.
check("|x| is distinguished from x^2 once x = 2 is plotted",
  matchingFamilies([[-2, 2], [-1, 1], [0, 0], [1, 1], [2, 2]]),
  ["|x|"]);

// ---- ambiguity is reported honestly, not guessed ----
// Through (0,0) and (1,1) alone, five families fit. Claiming one would mark a
// correct answer wrong.
check("a two-point table is ambiguous and says so",
  matchingFamilies([[0, 0], [1, 1]]).length > 1, true);
check("no points means no claim", matchingFamilies([]), []);

// ---- curve sampling ----
const seg = (key) => sampleCurve(key, VIEW);
check("a line is one unbroken segment", seg("x").length, 1);
check("1/x is TWO segments — it must not join across the asymptote",
  seg("1/x").length, 2);
check("sqrt only exists to the right of zero",
  seg("sqrt").every(s => s.every(p => p[0] >= 0)), true);
check("every sampled point stays inside the visible window",
  seg("x^3").every(s => s.every(p => p[1] >= VIEW.ymin && p[1] <= VIEW.ymax)), true);
check("an unknown family samples to nothing rather than throwing",
  sampleCurve("nope", VIEW), []);

// ---- the curve actually passes through her plotted points ----
// This is the promise the widget makes when it draws: "that goes through every
// one of your dots." If sampling and matching disagreed, it would be a lie.
const onCurve = SQUARE.every(([x, y]) => Math.abs(FAMILIES["x^2"].f(x) - y) < 1e-9);
check("the drawn family really does pass through the plotted points", onCurve, true);

// ---- every family offered in a lesson can be drawn ----
check("all eight families sample to at least one segment",
  Object.keys(FAMILIES).filter(k => sampleCurve(k, VIEW).length === 0), []);


// ---- the click-lands-where-she-aimed transform ----
// Appended after the fact because a real browser could not be laid out in this
// environment to check hit-testing by hand. A round-trip proves the same thing
// and proves it for every point, not the three I would have clicked.

function roundTripsCleanly(view) {
  const tf = transform(view);
  const v = tf.view;
  for (let gx = v.xmin; gx <= v.xmax; gx++) {
    for (let gy = v.ymin; gy <= v.ymax; gy++) {
      const [px, py] = tf.toBoard(gx, gy);
      const [bx, by] = tf.toGrid(px, py);
      const [sx, sy] = snapToLattice(bx, by, v);
      if (sx !== gx || sy !== gy) return `(${gx}, ${gy}) came back as (${sx}, ${sy})`;
    }
  }
  return "ok";
}

check("every lattice point survives grid → board → grid → snap (default view)",
  roundTripsCleanly(), "ok");
check("...and on Lesson 73's taller window for the x³ table",
  roundTripsCleanly({ xmin: -5, xmax: 5, ymin: -9, ymax: 9 }), "ok");
check("...and on a wide, short window",
  roundTripsCleanly({ xmin: -12, xmax: 12, ymin: -3, ymax: 3 }), "ok");

// A click in the middle of a square still resolves to that square's corner point.
const tf = transform();
const [cx, cy] = tf.toBoard(2, 3);
check("a click a third of a square off still snaps to the intended point",
  snapToLattice(...tf.toGrid(cx + 9, cy - 9)), [2, 3]);

// The corners of the board map to the corners of the window.
check("the top-left of the board is the top-left of the window",
  snapToLattice(...tf.toGrid(PAD, PAD)), [-6, 6]);
check("the bottom-right of the board is the bottom-right of the window",
  snapToLattice(...tf.toGrid(SIZE - PAD, SIZE - PAD)), [6, -6]);

// ---- a child can only plot whole numbers, so the check must allow for that ----
// Demanding exact equality told a child who had plotted sqrt PERFECTLY that her
// curve "misses some of your points". She placed every dot on the nearest
// intersection, which is the best any plot on graph paper can do.
check("a correctly plotted sqrt table is accepted",
  matchingFamilies([[0,0],[1,1],[2,1],[4,2],[9,3]]).includes("sqrt"), true);
check("a correctly plotted 1/x table is accepted",
  matchingFamilies([[-2,-1],[-1,-1],[1,1],[2,1]]).includes("1/x"), true);
check("a correctly plotted 2^x table is accepted",
  matchingFamilies([[-1,1],[0,1],[1,2],[2,4]]).includes("a^x"), true);
check("a correctly plotted 0.5^x table is accepted",
  matchingFamilies([[-2,4],[-1,2],[0,1],[1,1]]).includes("a^-x"), true);
check("tolerance does not make x^2 fit a cubic table",
  matchingFamilies([[-2,-8],[-1,-1],[0,0],[1,1],[2,8]]).includes("x^2"), false);

// ---- "enough points" is about ambiguity, not a count ----
// On a small grid the only three plottable x^3 points are (-1,-1) (0,0) (1,1),
// which fit the straight line equally well. Counting to three said "Yes, and
// only that one fits" to a child who had picked the wrong family.
check("three points that fit two families are not decisive",
  isDecisive([[-1,-1],[0,0],[1,1]], "x^3"), false);
check("...and the line is not decisive there either",
  isDecisive([[-1,-1],[0,0],[1,1]], "x"), false);
check("the full cubic table IS decisive",
  isDecisive([[-2,-8],[-1,-1],[0,0],[1,1],[2,8]], "x^3"), true);
check("the full square table IS decisive",
  isDecisive([[-2,4],[-1,1],[0,0],[1,1],[2,4]], "x^2"), true);

// ---- dragging one dot onto another must not manufacture evidence ----
check("duplicate points collapse", dedupe([[0,0],[1,1],[1,1]]), [[0,0],[1,1]]);
check("a duplicate cannot make an ambiguous plot look decisive",
  isDecisive([[0,0],[1,1],[1,1]], "x^2"), false);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

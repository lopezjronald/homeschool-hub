/* Tests for the trig triangle and the linear-inequality core (HH-155, L83/L86).
   Run by tutor.tests.SaxonLessonToolTests through node. */
const T = require("./portal-triangle.js");
const G = require("./portal-grid.js");

let pass = 0, fail = 0;
function check(name, got, want) {
  const g = JSON.stringify(got), w = JSON.stringify(want);
  if (g === w) { pass++; console.log(`  ok   ${name}`); }
  else { fail++; console.log(`  FAIL ${name}\n        got  ${g}\n        want ${w}`); }
}
const near = (a, b, tol) => Math.abs(a - b) < (tol == null ? 1e-9 : tol);

// ---- Lesson 86: trigonometry ----
/* Saxon builds the lesson on three similar 30-60-90 triangles: "similar triangles
   are proportional to each other... all three have the same three angles". The
   point is that the RATIOS are a property of the angle, not of the triangle. */
check("a 30-60-90 has the side ratios everyone memorises",
  [near(T.ratios(30, 1).sin, 0.5), near(T.ratios(30, 1).cos, Math.sqrt(3) / 2),
   near(T.ratios(30, 1).tan, 1 / Math.sqrt(3))], [true, true, true]);
check("scaling the triangle does not move the ratios",
  [1, 2, 7.5, 100].every(h => near(T.ratios(30, h).sin, T.ratios(30, 1).sin)), true);
check("...which is Saxon's similar-triangles point, so the SIDES do change",
  near(T.sides(30, 2).opposite, 2 * T.sides(30, 1).opposite), true);
check("45 degrees makes the two legs equal",
  near(T.sides(45, 1).opposite, T.sides(45, 1).adjacent), true);
check("tan 45 is exactly 1", near(T.ratios(45, 1).tan, 1), true);
/* The hypotenuse is the longest side — Saxon's definition, and a cheap way to
   catch opposite and hypotenuse being swapped. */
check("the hypotenuse is always the longest side",
  [5, 15, 30, 45, 60, 80].every(a => {
    const s = T.sides(a, 1);
    return s.hypotenuse > s.opposite && s.hypotenuse > s.adjacent;
  }), true);
check("Pythagoras holds for every angle",
  [10, 30, 45, 72].every(a => {
    const s = T.sides(a, 3);
    return near(s.opposite ** 2 + s.adjacent ** 2, s.hypotenuse ** 2, 1e-9);
  }), true);

/* THE lesson: which leg is "opposite" depends on where you stand. */
check("the two acute angles add to 90", T.complement(30), 60);
check("standing at the other angle SWAPS opposite and adjacent",
  [T.legNames("A").vertical, T.legNames("B").vertical], ["opposite", "adjacent"]);
check("...and so sin at one corner is cos at the other",
  near(T.ratios(30, 1).sin, T.ratios(T.complement(30), 1).cos), true);
check("a degenerate angle does not divide by zero or return NaN",
  [T.ratios(0, 1).tan !== null, isFinite(T.ratios(0, 1).sin)], [true, true]);

// ---- Lesson 83: linear inequalities ----
/* Saxon's rule, verbatim: "y > mx + b, and y < mx + b are represented by dashed
   lines. y >= mx + b, and y <= mx + b are represented by solid lines." and
   "greater than means shaded above". */
check("strict inequalities are dashed, inclusive ones solid",
  ["lt", "gt", "le", "ge"].map(k => G.OPS[k].dashed), [true, true, false, false]);
check("greater-than shades above, less-than below",
  ["gt", "ge", "lt", "le"].map(k => G.OPS[k].above), [true, true, false, false]);

// Example 83.1a: shaded BELOW a DASHED line, b = 2, m = 1  ->  y < x + 2
check("83.1a  (0,0) is inside y < x + 2", G.satisfiesInequality(0, 0, 1, 2, "lt"), true);
check("83.1a  (0,5) is outside", G.satisfiesInequality(0, 5, 1, 2, "lt"), false);
/* The dashed/solid distinction IS the boundary rule — the same point, in or out,
   depending only on the symbol. */
check("a point ON the line is OUT for dashed (<)",
  G.satisfiesInequality(0, 2, 1, 2, "lt"), false);
check("...and IN for solid (<=)", G.satisfiesInequality(0, 2, 1, 2, "le"), true);
check("a point ON the line is OUT for dashed (>)",
  G.satisfiesInequality(0, 2, 1, 2, "gt"), false);
check("...and IN for solid (>=)", G.satisfiesInequality(0, 2, 1, 2, "ge"), true);

// Example 83.1b: shaded ABOVE a SOLID line, b = 1, m = -2  ->  y >= -2x + 1
check("83.1b  (0,5) is inside y >= -2x + 1", G.satisfiesInequality(0, 5, -2, 1, "ge"), true);
check("83.1b  (0,-5) is outside", G.satisfiesInequality(0, -5, -2, 1, "ge"), false);
check("83.1b  the boundary point (0,1) is included",
  G.satisfiesInequality(0, 1, -2, 1, "ge"), true);

const VIEW = { xmin: -6, xmax: 6, ymin: -6, ymax: 6 };
check("the shaded region is a closed quadrilateral",
  G.halfPlanePolygon(1, 2, "lt", VIEW).length, 4);
check("shading below uses the BOTTOM corners",
  G.halfPlanePolygon(1, 2, "lt", VIEW).slice(2).map(p => p[1]), [-6, -6]);
check("shading above uses the TOP corners",
  G.halfPlanePolygon(1, 2, "gt", VIEW).slice(2).map(p => p[1]), [6, 6]);
check("an unknown operator shades nothing rather than guessing",
  [G.halfPlanePolygon(1, 2, "nope", VIEW), G.satisfiesInequality(0, 0, 1, 2, "nope")],
  [[], false]);

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);

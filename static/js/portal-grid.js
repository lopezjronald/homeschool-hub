/* Interactive graph paper for the Saxon lessons (HH-155).

   The parent asked for graph paper she can use "with her hand or with a click,"
   so it does both: click or tap to drop a point that snaps to the nearest whole
   number, drag to move it, or switch to the pen and sketch freehand. Then she
   names the family and the widget draws the TRUE curve through her dots — that
   moment is the reason this is built rather than printed.

   Coordinates are stored in GRID UNITS, not the 0-1 normalised space that
   portal-markup.js uses. That is a deliberate difference: a pen stroke's meaning
   is pixels, but a plotted point's meaning is the mathematics. (-2, 4) has to
   survive a window resize, a re-render and being read aloud — so it is stored as
   -2 and 4.

   The core below is pure (numbers in, numbers out) and exported for node, because
   the arithmetic is the part that can be subtly wrong. The DOM half only reads
   rectangles. */
(function () {
  "use strict";

  /* ---------- the function families she has to recognise ---------- */
  var FAMILIES = {
    "x":     { label: "x",    f: function (x) { return x; } },
    "x^2":   { label: "x²", f: function (x) { return x * x; } },
    "x^3":   { label: "x³", f: function (x) { return x * x * x; } },
    "|x|":   { label: "|x|",  f: function (x) { return Math.abs(x); } },
    "sqrt":  { label: "√x", f: function (x) { return x < 0 ? null : Math.sqrt(x); } },
    "1/x":   { label: "1/x",  f: function (x) { return x === 0 ? null : 1 / x; } },
    "a^x":   { label: "aˣ (a>1)",  f: function (x) { return Math.pow(2, x); } },
    "a^-x":  { label: "aˣ (0<a<1)", f: function (x) { return Math.pow(0.5, x); } },
  };

  var VIEW = { xmin: -6, xmax: 6, ymin: -6, ymax: 6 };

  /* Nearest whole-number lattice point to a position already in grid units.
     Clamped to the visible window so a drag off the edge parks on the edge
     rather than vanishing. */
  function snapToLattice(gx, gy, view) {
    view = view || VIEW;
    return [
      Math.min(view.xmax, Math.max(view.xmin, Math.round(gx))),
      Math.min(view.ymax, Math.max(view.ymin, Math.round(gy))),
    ];
  }

  /* Duplicate points are the same claim made twice. Counting them twice would
     let a child drag one dot onto another and satisfy a "you plotted enough
     points" check with two real points and a copy. */
  function dedupe(points) {
    var seen = {}, out = [];
    (points || []).forEach(function (p) {
      var k = p[0] + "," + p[1];
      if (!seen[k]) { seen[k] = 1; out.push(p); }
    });
    return out;
  }

  /* Which families are consistent with these plotted points?

     TOLERANCE, not equality. She can only place a dot on a whole-number
     intersection, so for sqrt, 1/x and the exponentials the best she can
     possibly do is the NEAREST lattice point — sqrt(2) = 1.414 becomes (2, 1).
     Demanding exactness told a child who had plotted sqrt perfectly that her
     curve "misses some of your points". Half a lattice step is the right bar
     because half a step is the most her plotting can be off by.

     Returns a LIST, because a small table is often ambiguous: (0,0) and (1,1)
     alone fit x, x^2, x^3, |x| and sqrt at once. Naming one of them would mark
     four correct answers wrong. */
  function matchingFamilies(points, tolerance) {
    var pts = dedupe(points);
    if (!pts.length) return [];
    var tol = tolerance == null ? 0.5 : tolerance;
    return Object.keys(FAMILIES).filter(function (key) {
      var f = FAMILIES[key].f;
      return pts.every(function (p) {
        var y = f(p[0]);
        return y !== null && isFinite(y) && Math.abs(y - p[1]) <= tol;
      });
    });
  }

  /* Enough points to tell the families apart? Not a count — a question about
     whether the plot still fits more than one answer. Three points sounds like
     plenty and is not: on a small grid the only three plottable x^3 points are
     (-1,-1), (0,0) and (1,1), which fit the straight line just as well. */
  function isDecisive(points, key) {
    var fits = matchingFamilies(points);
    return fits.length === 1 && fits[0] === key;
  }

  /* A polyline for the family across the visible window, in grid units.
     Returns SEGMENTS — 1/x is two separate curves and must not be joined across
     the asymptote, and sqrt simply does not exist left of zero. */
  function sampleCurve(key, view, stepsPerUnit) {
    var fam = FAMILIES[key];
    if (!fam) return [];
    view = view || VIEW;
    var step = 1 / (stepsPerUnit || 16);
    var segments = [];
    var current = [];
    for (var x = view.xmin; x <= view.xmax + 1e-9; x += step) {
      var gx = Math.round(x * 1e6) / 1e6;
      var y = fam.f(gx);
      var ok = y !== null && isFinite(y) && y >= view.ymin && y <= view.ymax;
      if (ok) {
        current.push([gx, y]);
      } else if (current.length) {
        segments.push(current);
        current = [];
      }
    }
    if (current.length) segments.push(current);
    return segments.filter(function (s) { return s.length > 1; });
  }

  var SIZE = 440, PAD = 8;

  /* The board <-> grid transform, as pure functions.

     This is the arithmetic that decides whether a click lands where she aimed,
     so it lives in the tested core rather than inside the DOM code. A round-trip
     (grid -> board -> grid -> snap) must return the point it started from; if it
     does not, every dot lands one square off and nothing else will tell us. */
  function transform(view) {
    view = Object.assign({}, VIEW, view || {});
    var uxs = (SIZE - 2 * PAD) / (view.xmax - view.xmin);
    var uys = (SIZE - 2 * PAD) / (view.ymax - view.ymin);
    return {
      view: view,
      toBoard: function (gx, gy) {
        return [PAD + (gx - view.xmin) * uxs, SIZE - PAD - (gy - view.ymin) * uys];
      },
      toGrid: function (px, py) {
        return [view.xmin + (px - PAD) / uxs, view.ymin + (SIZE - PAD - py) / uys];
      },
    };
  }

  var core = {
    FAMILIES: FAMILIES, VIEW: VIEW, SIZE: SIZE, PAD: PAD,
    snapToLattice: snapToLattice,
    matchingFamilies: matchingFamilies,
    isDecisive: isDecisive,
    dedupe: dedupe,
    sampleCurve: sampleCurve,
    transform: transform,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.portalGridCore = core;
  if (typeof document === "undefined") return;   // required as a module, not a page

  /* ---------------------------- the widget ---------------------------- */

  function build(host, cfg) {
    var tf = transform(cfg.view);
    var view = tf.view;
    var X = function (gx) { return tf.toBoard(gx, 0)[0]; };
    var Y = function (gy) { return tf.toBoard(0, gy)[1]; };
    var gX = function (px) { return tf.toGrid(px, 0)[0]; };
    var gY = function (py) { return tf.toGrid(0, py)[1]; };

    var svgns = "http://www.w3.org/2000/svg";
    function el(name, attrs) {
      var n = document.createElementNS(svgns, name);
      Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
      return n;
    }

    var svg = el("svg", {
      "class": "lesson-board", viewBox: "0 0 " + SIZE + " " + SIZE,
      role: "img", "aria-label": cfg.label || "coordinate grid",
    });

    // grid + axes
    var g = el("g", {});
    for (var i = Math.ceil(view.xmin); i <= view.xmax; i++) {
      g.appendChild(el("line", { x1: X(i), y1: Y(view.ymin), x2: X(i), y2: Y(view.ymax),
                                 stroke: "#DCE6D6", "stroke-width": 1 }));
    }
    for (var j = Math.ceil(view.ymin); j <= view.ymax; j++) {
      g.appendChild(el("line", { x1: X(view.xmin), y1: Y(j), x2: X(view.xmax), y2: Y(j),
                                 stroke: "#DCE6D6", "stroke-width": 1 }));
    }
    g.appendChild(el("line", { x1: X(view.xmin), y1: Y(0), x2: X(view.xmax), y2: Y(0),
                               stroke: "#1E2A24", "stroke-width": 2 }));
    g.appendChild(el("line", { x1: X(0), y1: Y(view.ymin), x2: X(0), y2: Y(view.ymax),
                               stroke: "#1E2A24", "stroke-width": 2 }));
    for (var t = Math.ceil(view.xmin); t <= view.xmax; t += 2) {
      if (t === 0) continue;
      var tx = el("text", { x: X(t), y: Y(0) + 14, "font-size": 11, fill: "#5A6A60",
                            "text-anchor": "middle", "font-family": "monospace" });
      tx.textContent = t; g.appendChild(tx);
    }
    for (var u = Math.ceil(view.ymin); u <= view.ymax; u += 2) {
      if (u === 0) continue;
      var ty = el("text", { x: X(0) - 7, y: Y(u) + 4, "font-size": 11, fill: "#5A6A60",
                            "text-anchor": "end", "font-family": "monospace" });
      ty.textContent = u; g.appendChild(ty);
    }
    svg.appendChild(g);

    var curveLayer = el("g", {});
    var inkLayer = el("g", {});
    var dotLayer = el("g", {});
    svg.appendChild(curveLayer); svg.appendChild(inkLayer); svg.appendChild(dotLayer);
    host.appendChild(svg);

    var readout = document.createElement("div");
    readout.className = "lesson-tool-readout";
    readout.setAttribute("aria-live", "polite");
    host.appendChild(readout);

    var points = (cfg.points || []).slice();
    var strokes = [];
    var mode = "plot";

    function drawDots() {
      while (dotLayer.firstChild) dotLayer.removeChild(dotLayer.firstChild);
      points.forEach(function (p) {
        dotLayer.appendChild(el("circle", { cx: X(p[0]), cy: Y(p[1]), r: 6, fill: "#14568C" }));
      });
    }
    function drawInk() {
      while (inkLayer.firstChild) inkLayer.removeChild(inkLayer.firstChild);
      strokes.forEach(function (s) {
        if (s.length < 2) return;
        inkLayer.appendChild(el("polyline", {
          points: s.map(function (q) { return X(q[0]) + "," + Y(q[1]); }).join(" "),
          fill: "none", stroke: "#C2571A", "stroke-width": 2.5,
          "stroke-linecap": "round", "stroke-linejoin": "round",
        }));
      });
    }
    function drawCurve(key) {
      while (curveLayer.firstChild) curveLayer.removeChild(curveLayer.firstChild);
      sampleCurve(key, view).forEach(function (seg) {
        curveLayer.appendChild(el("polyline", {
          points: seg.map(function (q) { return X(q[0]) + "," + Y(q[1]); }).join(" "),
          fill: "none", stroke: "#1E7A50", "stroke-width": 3, opacity: 0.85,
        }));
      });
    }

    function at(evt) {
      var r = svg.getBoundingClientRect();
      // A zero-size rect means the board is not laid out — inside a closed
      // <details>, a hidden tab, or simply not yet painted. Dividing by it gives
      // NaN, and a NaN point renders as an invisible dot that silently breaks
      // every later answer check. Refuse the event instead.
      if (!r.width || !r.height) return null;
      var px = (evt.clientX - r.left) / r.width * SIZE;
      var py = (evt.clientY - r.top) / r.height * SIZE;
      return [gX(px), gY(py)];
    }

    var dragging = null, penning = null;
    var pickRow = null;      // set below when the lesson offers family choices
    svg.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      svg.setPointerCapture(e.pointerId);
      var raw = at(e);
      if (!raw) return;
      if (mode === "pen") { penning = [raw]; strokes.push(penning); return; }
      var snap = snapToLattice(raw[0], raw[1], view);
      var hit = -1;
      points.forEach(function (p, i) {
        if (p[0] === snap[0] && p[1] === snap[1]) hit = i;
      });
      if (hit >= 0) { points.splice(hit, 1); drawDots(); readout.textContent = "removed"; return; }
      points.push(snap);
      dragging = points.length - 1;
      drawDots();
      readout.textContent = "(" + snap[0] + ", " + snap[1] + ")";
    });
    svg.addEventListener("pointermove", function (e) {
      var moved = at(e);
      if (!moved) return;
      if (penning) { penning.push(moved); drawInk(); return; }
      if (dragging === null) return;
      var snap = snapToLattice(moved[0], moved[1], view);
      points[dragging] = snap;
      drawDots();
      readout.textContent = "(" + snap[0] + ", " + snap[1] + ")";
    });
    function release() { dragging = null; penning = null; }
    svg.addEventListener("pointerup", release);
    svg.addEventListener("pointercancel", release);
    svg.addEventListener("pointerleave", release);

    // controls
    var ctl = document.createElement("div");
    ctl.className = "lesson-tool-controls";
    function button(label, cls, fn) {
      var b = document.createElement("button");
      b.type = "button"; b.className = cls || "lesson-btn lesson-btn--ghost";
      b.textContent = label;
      b.addEventListener("click", fn);
      ctl.appendChild(b);
      return b;
    }
    var penBtn = button("✏️ Pen", "lesson-btn lesson-btn--ghost", function () {
      mode = mode === "pen" ? "plot" : "pen";
      penBtn.textContent = mode === "pen" ? "● Plotting points" : "✏️ Pen";
      readout.textContent = mode === "pen" ? "sketch freely" : "click to plot";
    });
    button("Undo", "lesson-btn lesson-btn--ghost", function () {
      if (mode === "pen") strokes.pop(); else points.pop();
      // The drawn curve and the verdict were about the OLD set of points.
      while (curveLayer.firstChild) curveLayer.removeChild(curveLayer.firstChild);
      if (pickRow) pickRow.querySelectorAll(".lesson-choice").forEach(function (o) {
        o.classList.remove("is-picked", "is-right");
      });
      readout.textContent = "";
      drawDots(); drawInk();
    });
    button("Clear", "lesson-btn lesson-btn--ghost", function () {
      points = []; strokes = [];
      while (curveLayer.firstChild) curveLayer.removeChild(curveLayer.firstChild);
      drawDots(); drawInk(); readout.textContent = "";
    });
    host.appendChild(ctl);

    // family choices — the payoff
    if (cfg.choices && cfg.choices.length) {
      var pick = document.createElement("div");
      pick.className = "lesson-tool-controls";
      pickRow = pick;
      cfg.choices.forEach(function (key) {
        var fam = FAMILIES[key];
        if (!fam) return;
        var b = document.createElement("button");
        b.type = "button"; b.className = "lesson-choice"; b.textContent = fam.label;
        b.addEventListener("click", function () {
          pick.querySelectorAll(".lesson-choice").forEach(function (o) {
            o.classList.remove("is-picked", "is-right");
          });
          drawCurve(key);
          b.classList.add("is-picked");
          // A reference gallery has nothing to check against — it exists to be
          // looked at, and telling her to "plot the table first" when the block
          // has no table is just wrong.
          if (cfg.reference) {
            readout.textContent = FAMILIES[key].label + " — look at what the left side does.";
            return;
          }
          var plotted = dedupe(points);
          if (plotted.length < 2) {
            readout.textContent = "Plot the points from the table first, then pick a shape.";
            return;
          }
          var fits = matchingFamilies(plotted);
          if (fits.indexOf(key) < 0) {
            // Do NOT hint at the left-hand side here: that is the x2-vs-x3 tell
            // and it is misleading for sqrt or 1/x, which fail for other reasons.
            readout.textContent = "That curve doesn't pass through all your points. "
              + "Check each one against the table.";
            return;
          }
          if (fits.length > 1) {
            // Honest, and the more useful answer: her points genuinely do not
            // rule the others out yet.
            readout.textContent = "That fits — but so would "
              + fits.filter(function (k) { return k !== key; })
                    .map(function (k) { return FAMILIES[k].label; }).join(", ")
              + ". Plot another point to tell them apart.";
            return;
          }
          b.classList.remove("is-picked");
          b.classList.add("is-right");
          readout.textContent = "Yes — and only that one fits your points.";
        });
        pick.appendChild(b);
      });
      host.appendChild(pick);
    }

    drawDots();
    if (cfg.curve) drawCurve(cfg.curve);
    if (cfg.readonly) { svg.style.pointerEvents = "none"; ctl.remove(); }
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.lesson-tool[data-tool="grid"]').forEach(function (host) {
      var node = document.getElementById(host.dataset.configId);
      var cfg = {};
      try { cfg = JSON.parse(node.textContent); } catch (e) { cfg = {}; }
      build(host, cfg);
    });
  });
})();

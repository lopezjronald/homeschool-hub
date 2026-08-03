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

  /* Which families pass through EVERY one of these points exactly?
     Returns a list, because a small table can be ambiguous — (0,0) and (1,1) fit
     x, x^2, x^3, |x| and sqrt all at once, and pretending otherwise would mark a
     right answer wrong. */
  function matchingFamilies(points) {
    if (!points || !points.length) return [];
    return Object.keys(FAMILIES).filter(function (key) {
      var f = FAMILIES[key].f;
      return points.every(function (p) {
        var y = f(p[0]);
        return y !== null && Math.abs(y - p[1]) < 1e-9;
      });
    });
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

  var core = {
    FAMILIES: FAMILIES, VIEW: VIEW,
    snapToLattice: snapToLattice,
    matchingFamilies: matchingFamilies,
    sampleCurve: sampleCurve,
  };
  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.portalGridCore = core;
  if (typeof document === "undefined") return;   // required as a module, not a page

  /* ---------------------------- the widget ---------------------------- */

  var SIZE = 440, PAD = 8;

  function build(host, cfg) {
    var view = Object.assign({}, VIEW, cfg.view || {});
    var uxs = (SIZE - 2 * PAD) / (view.xmax - view.xmin);
    var uys = (SIZE - 2 * PAD) / (view.ymax - view.ymin);
    var X = function (gx) { return PAD + (gx - view.xmin) * uxs; };
    var Y = function (gy) { return SIZE - PAD - (gy - view.ymin) * uys; };
    var gX = function (px) { return view.xmin + (px - PAD) / uxs; };
    var gY = function (py) { return view.ymin + (SIZE - PAD - py) / uys; };

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
      var px = (evt.clientX - r.left) / r.width * SIZE;
      var py = (evt.clientY - r.top) / r.height * SIZE;
      return [gX(px), gY(py)];
    }

    var dragging = null, penning = null;
    svg.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      svg.setPointerCapture(e.pointerId);
      var raw = at(e);
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
      if (penning) { penning.push(at(e)); drawInk(); return; }
      if (dragging === null) return;
      var raw = at(e);
      var snap = snapToLattice(raw[0], raw[1], view);
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
          var fits = matchingFamilies(points);
          var right = fits.indexOf(key) >= 0 && points.length >= 3;
          b.classList.add(right ? "is-right" : "is-picked");
          readout.textContent = right
            ? "Yes — that curve goes through every one of your points."
            : (points.length < 3
                ? "Plot the points from the table first, then pick a shape."
                : "That curve misses some of your points. Look at the left-hand side.");
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

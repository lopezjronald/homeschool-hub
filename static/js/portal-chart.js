/* Charts for Saxon Lesson 74 (HH-155).

   Saxon makes one point in this lesson, and says it out loud: "Did you notice we
   are using the same data, just with different chart types? The reason for using
   the same data is to show you how some charts are better than others for the
   same set of data."

   So the widget is a SWITCHER, not five pictures. One dataset, and she flips
   between pictograph, bar, line, pie and scatter watching the numbers stay put
   while the picture changes. A page of five static images would state Saxon's
   point; this one lets her check it.

   Everything is SVG geometry attributes — no inline style, no images to go
   missing. The layout arithmetic is a pure core exported for node, because
   "which bar is how tall" is exactly the kind of thing that can be quietly off
   by one axis-step and still look plausible. */
(function () {
  "use strict";

  var W = 460, H = 300, PAD_L = 56, PAD_B = 40, PAD_T = 16, PAD_R = 12;

  /* The top of the axis: a round number at or above the largest value.

     Never below it — a bar drawn past the top of its own axis is a chart that
     lies. Rounds up to 1, 2 or 5 times a power of ten so the gridlines land on
     numbers a child can read (2,000 / 4,000 / 6,000), not on 4,730. */
  /* Choose the STEP first, then the top — not the other way round.

     Picking a nice-looking maximum and then cutting it into five equal pieces is
     the trap: 6,000 in five parts is 1,200 / 2,400 / 3,600, and a child told to
     "find the scale first" finds a scale that cannot show her the numbers the
     lesson is talking about. Lesson 74 says August's 4,000 "lands exactly on a
     line" and June sits "halfway between 0 and 2,000"; with 1,200-steps neither
     line exists and the page contradicts itself.

     So: round the rough gap UP to 1, 2, 2.5 or 5 times a power of ten, then take
     the top to the next whole step. Gridlines are numbers a person would choose. */
  function niceScale(values, gaps) {
    var top = 0;
    (values || []).forEach(function (v) { if (v > top) top = v; });
    var want = gaps || 5;
    if (!(top > 0)) return { max: 1, step: 1 };
    var rough = top / want;
    var mag = Math.pow(10, Math.floor(Math.log(rough) / Math.LN10));
    var step = null;
    [1, 2, 2.5, 5, 10].forEach(function (s) {
      if (step === null && s * mag >= rough - 1e-9) step = s * mag;
    });
    if (step === null) step = 10 * mag;
    return { max: Math.ceil(top / step - 1e-9) * step, step: step };
  }

  /* The top of the axis: never below the tallest value, always a whole number of
     gridline steps. A bar drawn past the top of its own axis is a chart that lies. */
  function niceMax(values, gaps) {
    return niceScale(values, gaps).max;
  }

  /* Gridline values from 0 up to max, one per step. */
  function ticks(max, step) {
    var out = [];
    if (!(step > 0)) return [0];
    for (var v = 0; v <= max + 1e-9; v += step) out.push(Math.round(v * 1e6) / 1e6);
    return out;
  }

  function plotBox() {
    return { x: PAD_L, y: PAD_T, w: W - PAD_L - PAD_R, h: H - PAD_T - PAD_B };
  }

  /* One rectangle per value, in SVG coordinates. */
  function barLayout(values, max) {
    var box = plotBox();
    var top = max || niceMax(values);
    var n = values.length || 1;
    var slot = box.w / n;
    var width = slot * 0.62;
    return values.map(function (v, i) {
      var h = top ? (v / top) * box.h : 0;
      return {
        x: box.x + slot * i + (slot - width) / 2,
        y: box.y + box.h - h,
        w: width,
        h: h,
        cx: box.x + slot * (i + 0.5),
      };
    });
  }

  /* One point per value — used by the line graph and the scatterplot, which
     differ only in whether the dots get joined. */
  function pointLayout(values, max) {
    var box = plotBox();
    var top = max || niceMax(values);
    var n = values.length || 1;
    var slot = box.w / n;
    return values.map(function (v, i) {
      return {
        x: box.x + slot * (i + 0.5),
        y: box.y + box.h - (top ? (v / top) * box.h : 0),
      };
    });
  }

  /* Pie slices as angles and percentages.

     Percentages come from the real total, so they sum to 100 and the lesson's
     "which month was about 1/3?" question has a truthful answer. Angles are
     measured clockwise from twelve o'clock, which is where a reader expects a
     pie to start. */
  function pieSlices(values) {
    var total = 0;
    (values || []).forEach(function (v) { total += v; });
    if (!(total > 0)) return [];
    var at = 0;
    return values.map(function (v) {
      var sweep = v / total * 360;
      var slice = { start: at, end: at + sweep, sweep: sweep,
                    percent: v / total * 100 };
      at += sweep;
      return slice;
    });
  }

  /* An SVG path for one slice of a pie of radius r centred at (cx, cy). */
  function slicePath(slice, cx, cy, r) {
    function at(deg) {
      var rad = (deg - 90) * Math.PI / 180;
      return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)];
    }
    var a = at(slice.start), b = at(slice.end);
    if (slice.sweep >= 359.999) {
      // A single slice IS the whole circle; an arc from a point to itself draws
      // nothing at all, so draw two half-arcs instead.
      var m = at(slice.start + 180);
      return "M" + a[0] + "," + a[1] + "A" + r + "," + r + " 0 0 1 " + m[0] + "," + m[1] +
             "A" + r + "," + r + " 0 0 1 " + a[0] + "," + a[1] + "Z";
    }
    var large = slice.sweep > 180 ? 1 : 0;
    return "M" + cx + "," + cy + " L" + a[0] + "," + a[1] +
           " A" + r + "," + r + " 0 " + large + " 1 " + b[0] + "," + b[1] + " Z";
  }

  /* How many whole symbols and whether a half is left over.

     The lesson's practice set hinges on this: "Half an airplane = 50,000
     tourists." Rounding to whole symbols would silently delete the half and give
     her the wrong count. */
  function pictoCounts(value, per) {
    if (!(per > 0)) return { whole: 0, half: false };
    var units = value / per;
    var whole = Math.floor(units + 1e-9);
    return { whole: whole, half: (units - whole) >= 0.25 };
  }

  /* Rise over run between two labelled data points — Example 74.5 exactly. */
  function slopeBetween(a, b) {
    var run = b.index - a.index;
    if (!run) return null;
    return (b.value - a.value) / run;
  }

  var core = {
    W: W, H: H, niceMax: niceMax, ticks: ticks, plotBox: plotBox,
    barLayout: barLayout, pointLayout: pointLayout, pieSlices: pieSlices,
    slicePath: slicePath, pictoCounts: pictoCounts, slopeBetween: slopeBetween,
    niceScale: niceScale,
  };

  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.PortalChart = core;

  if (typeof document === "undefined") return;

  var NS = "http://www.w3.org/2000/svg";
  function el(name, attrs) {
    var node = document.createElementNS(NS, name);
    Object.keys(attrs || {}).forEach(function (k) {
      node.setAttribute(k, attrs[k]);
    });
    return node;
  }

  var PALETTE = ["#14568C", "#C2571A", "#1E7A50", "#7A4E9E", "#B03A5B", "#0E7C86"];

  function build(host, cfg) {
    var labels = (cfg.data || []).map(function (d) { return d.label; });
    var values = (cfg.data || []).map(function (d) { return Number(d.value) || 0; });
    var kinds = cfg.kinds && cfg.kinds.length ? cfg.kinds : ["bar"];
    var scale = niceScale(values);
    var max = scale.max;

    var svg = el("svg", {
      viewBox: "0 0 " + W + " " + H, class: "lesson-chart",
      role: "img", "aria-label": cfg.label || "chart",
    });
    var readout = document.createElement("p");
    readout.className = "lesson-tool-readout";
    readout.setAttribute("aria-live", "polite");

    function clear() { while (svg.firstChild) svg.removeChild(svg.firstChild); }

    function axes(showY) {
      var box = plotBox();
      if (showY) {
        ticks(max, scale.step).forEach(function (t) {
          var y = box.y + box.h - (t / max) * box.h;
          svg.appendChild(el("line", { x1: box.x, y1: y, x2: box.x + box.w, y2: y,
                                       stroke: "#DCE6D6", "stroke-width": 1 }));
          var lab = el("text", { x: box.x - 8, y: y + 4, "font-size": 11,
                                 fill: "#5A6A60", "text-anchor": "end" });
          lab.textContent = t >= 1000 ? (t / 1000) + "k" : String(t);
          svg.appendChild(lab);
        });
        svg.appendChild(el("line", { x1: box.x, y1: box.y, x2: box.x, y2: box.y + box.h,
                                     stroke: "#1E2A24", "stroke-width": 2 }));
      }
      svg.appendChild(el("line", { x1: box.x, y1: box.y + box.h,
                                   x2: box.x + box.w, y2: box.y + box.h,
                                   stroke: "#1E2A24", "stroke-width": 2 }));
    }

    function xLabels(positions) {
      var box = plotBox();
      positions.forEach(function (cx, i) {
        var t = el("text", { x: cx, y: box.y + box.h + 16, "font-size": 11,
                             fill: "#5A6A60", "text-anchor": "middle" });
        t.textContent = labels[i];
        svg.appendChild(t);
      });
    }

    function drawBar() {
      axes(true);
      var bars = barLayout(values, max);
      bars.forEach(function (b, i) {
        svg.appendChild(el("rect", { x: b.x, y: b.y, width: b.w, height: b.h,
                                     fill: PALETTE[0], rx: 2 }));
      });
      xLabels(bars.map(function (b) { return b.cx; }));
    }

    function drawLine() {
      axes(true);
      var pts = pointLayout(values, max);
      svg.appendChild(el("polyline", {
        points: pts.map(function (p) { return p.x + "," + p.y; }).join(" "),
        fill: "none", stroke: PALETTE[1], "stroke-width": 3,
        "stroke-linecap": "round", "stroke-linejoin": "round",
      }));
      pts.forEach(function (p) {
        svg.appendChild(el("circle", { cx: p.x, cy: p.y, r: 4, fill: PALETTE[1] }));
      });
      xLabels(pts.map(function (p) { return p.x; }));
    }

    function drawScatter() {
      axes(true);
      var pts = pointLayout(values, max);
      pts.forEach(function (p) {
        svg.appendChild(el("circle", { cx: p.x, cy: p.y, r: 5, fill: PALETTE[2] }));
      });
      if (cfg.trend && pts.length > 1) {
        var a = pts[0], b = pts[pts.length - 1];
        svg.appendChild(el("line", { x1: a.x, y1: a.y, x2: b.x, y2: b.y,
                                     stroke: PALETTE[1], "stroke-width": 2,
                                     "stroke-dasharray": "6 4" }));
      }
      xLabels(pts.map(function (p) { return p.x; }));
    }

    function drawPie() {
      var cx = W / 2, cy = H / 2 + 4, r = Math.min(W, H) / 2 - 34;
      pieSlices(values).forEach(function (s, i) {
        svg.appendChild(el("path", { d: slicePath(s, cx, cy, r),
                                     fill: PALETTE[i % PALETTE.length],
                                     stroke: "#FFFFFF", "stroke-width": 2 }));
        var mid = (s.start + s.end) / 2;
        var rad = (mid - 90) * Math.PI / 180;
        var t = el("text", { x: cx + (r + 20) * Math.cos(rad),
                             y: cy + (r + 20) * Math.sin(rad) + 4,
                             "font-size": 11, fill: "#3A4A40", "text-anchor": "middle" });
        t.textContent = labels[i] + " " + s.percent.toFixed(1) + "%";
        svg.appendChild(t);
      });
    }

    function drawPictograph() {
      var per = Number(cfg.per) || 1;
      var box = plotBox();
      var rowH = Math.min(30, box.h / Math.max(values.length, 1));
      values.forEach(function (v, i) {
        var y = box.y + rowH * i + rowH / 2;
        var lab = el("text", { x: box.x - 8, y: y + 4, "font-size": 11,
                               fill: "#5A6A60", "text-anchor": "end" });
        lab.textContent = labels[i];
        svg.appendChild(lab);
        var c = pictoCounts(v, per);
        for (var k = 0; k < c.whole; k++) {
          svg.appendChild(el("rect", { x: box.x + 4 + k * 22, y: y - 7,
                                       width: 18, height: 14, rx: 3,
                                       fill: PALETTE[0] }));
        }
        if (c.half) {
          svg.appendChild(el("rect", { x: box.x + 4 + c.whole * 22, y: y - 7,
                                       width: 9, height: 14, rx: 3,
                                       fill: PALETTE[0], opacity: 0.55 }));
        }
      });
      var key = el("text", { x: box.x, y: H - 10, "font-size": 11, fill: "#5A6A60" });
      key.textContent = "one block = " + per + " " + (cfg.unit || "");
      svg.appendChild(key);
    }

    var DRAW = { bar: drawBar, line: drawLine, pie: drawPie,
                 scatter: drawScatter, pictograph: drawPictograph };
    var NOTE = {
      bar: "Bars are easy to compare — taller means more.",
      line: "A line suggests the values flow between the labels. For monthly "
            + "counts that is not really true, which is why Saxon says this one "
            + "is not the best choice here.",
      pie: "A pie shows each part as a share of the whole. Percentages add to 100.",
      scatter: "Dots only. Look for a trend — a direction the dots roughly follow.",
      pictograph: "Each block stands for a fixed amount. Count blocks, then multiply.",
    };

    function show(kind) {
      clear();
      (DRAW[kind] || drawBar)();
      readout.textContent = NOTE[kind] || "";
    }

    if (kinds.length > 1) {
      var row = document.createElement("div");
      row.className = "lesson-tool-controls";
      kinds.forEach(function (kind) {
        var b = document.createElement("button");
        b.type = "button";
        b.className = "lesson-choice";
        b.textContent = kind;
        b.addEventListener("click", function () {
          row.querySelectorAll(".lesson-choice").forEach(function (o) {
            o.classList.remove("is-picked");
          });
          b.classList.add("is-picked");
          show(kind);
        });
        row.appendChild(b);
      });
      host.appendChild(row);
      row.querySelector(".lesson-choice").classList.add("is-picked");
    }
    host.appendChild(svg);
    host.appendChild(readout);
    show(kinds[0]);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.lesson-tool[data-tool="chart"]').forEach(function (host) {
      var node = document.getElementById(host.dataset.configId);
      if (!node) return;
      try {
        build(host, JSON.parse(node.textContent));
      } catch (err) {
        host.textContent = "";
      }
    });
  });
})();

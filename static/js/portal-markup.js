/* Portal markup: draw on a sentence with the mouse or finger to add punctuation,
   cross out words, and mark corrections. Strokes are stored (relative coords, so
   they replay at any size) in a hidden input that the autosave picks up. No deps. */
(function () {
  "use strict";

  /* Name the strokes: given word boxes and strokes in the SAME 0-1 space, work
     out which words were underlined, circled or crossed out.

     Pure — no DOM, no layout — so it can be tested directly. The DOM half is
     just reading rectangles, which is the part that cannot go subtly wrong.

     Deliberately conservative. A stroke that doesn't clearly match a gesture is
     counted as UNREAD rather than guessed at: a wrong reading marks a correct
     answer wrong, which is worse than admitting we couldn't tell. */
  function readMarkup(words, strokes) {
    strokes = strokes || [];
    if (!words || !words.length) return { marks: [], unread: strokes.length };

    var seen = {}, marks = [], unread = 0;

    strokes.forEach(function (s) {
      var pts = (s && s.p) || [];
      if (pts.length < 2) { unread++; return; }
      var x0 = Infinity, x1 = -Infinity, y0 = Infinity, y1 = -Infinity;
      pts.forEach(function (pt) {
        if (pt[0] < x0) x0 = pt[0];
        if (pt[0] > x1) x1 = pt[0];
        if (pt[1] < y0) y0 = pt[1];
        if (pt[1] > y1) y1 = pt[1];
      });

      // Is the path closed? A loop comes back to where it started. This is a
      // property of the GESTURE, not of the font, which is why circles are
      // detected this way: measuring "reaches above and below the word" against
      // the span's box got it badly wrong, because a span's box is the font's
      // full ascent+descent while the letters fill barely half of it — a circle
      // drawn snugly round the letters never reached the box edges and came back
      // as a cross-out.
      var span = Math.max(x1 - x0, y1 - y0);
      var first = pts[0], last = pts[pts.length - 1];
      var gap = Math.sqrt(Math.pow(last[0] - first[0], 2) + Math.pow(last[1] - first[1], 2));
      var closed = span > 0 && gap <= 0.45 * span && pts.length >= 5;

      var hit = 0;
      words.forEach(function (w) {
        var ww = w.x1 - w.x0;
        // The band the LETTERS occupy, not the line box. Falls back to the box
        // when glyph metrics are unavailable.
        var gy0 = (w.gy0 == null ? w.y0 : w.gy0);
        var gy1 = (w.gy1 == null ? w.y1 : w.gy1);
        var gh = gy1 - gy0;
        if (ww <= 0 || gh <= 0) return;
        // How much of this word's width the stroke spans.
        var cover = (Math.min(x1, w.x1) - Math.max(x0, w.x0)) / ww;
        if (cover < 0.5) return;

        var mid = (y0 + y1) / 2;
        var flat = (y1 - y0) <= 0.8 * gh;

        var kind = null;
        if (closed && cover >= 0.6 && y0 <= gy0 + 0.35 * gh && y1 >= gy1 - 0.35 * gh) {
          // A loop drawn around the letters.
          kind = "circled";
        } else if (flat && y0 >= gy1 - 0.15 * gh && y0 <= gy1 + 1.2 * gh) {
          // Flat, sitting below the letters — and not so far below that it is
          // really underlining nothing.
          kind = "underlined";
        } else if (flat && mid >= gy0 + 0.15 * gh && mid <= gy1 - 0.15 * gh) {
          // Flat, passing through the letters.
          kind = "crossed out";
        }
        if (!kind) return;

        hit++;
        var key = w.i + ":" + kind;
        if (seen[key]) return;      // one circle round three words is three marks, not nine
        seen[key] = true;
        marks.push({ i: w.i, word: w.text, kind: kind });
      });
      if (!hit) unread++;           // she drew something we could not name
    });

    marks.sort(function (a, b) { return a.i - b.i; });
    return { marks: marks, unread: unread };
  }

  if (typeof window !== "undefined") window.portalReadMarkup = readMarkup;
  if (typeof module !== "undefined" && module.exports) module.exports = { readMarkup: readMarkup };

  var form = typeof document !== "undefined" && document.getElementById("response-form");
  if (!form && typeof document === "undefined") return;   // required as a module, not a page
  var locked = form && form.dataset.submitted === "1";

  function setup(widget) {
    var surface = widget.querySelector(".markup-surface");
    var canvas = widget.querySelector(".markup-canvas");
    var input = widget.querySelector("input[data-question]");
    var ctx = canvas.getContext("2d");

    // Answers saved before marks existed are a bare array of strokes; newer ones
    // are {strokes, marks, unread}. Both have to load, or a child's earlier work
    // would come back as an empty canvas.
    var strokes = [];
    try {
      var saved = JSON.parse(input.value || "[]");
      strokes = Array.isArray(saved) ? saved : (saved && saved.strokes) || [];
    } catch (e) { strokes = []; }

    var tool = { color: "#333333", width: 3 };
    var drawing = false;
    var current = null;

    function fit() {
      var rect = surface.getBoundingClientRect();
      var dpr = window.devicePixelRatio || 1;
      canvas.width = Math.round(rect.width * dpr);
      canvas.height = Math.round(rect.height * dpr);
      canvas.style.width = rect.width + "px";
      canvas.style.height = rect.height + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      redraw();
    }

    function drawStroke(s) {
      var rect = canvas.getBoundingClientRect();
      if (!s.p.length) return;
      ctx.strokeStyle = s.c;
      ctx.lineWidth = s.w;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      s.p.forEach(function (pt, i) {
        var x = pt[0] * rect.width, y = pt[1] * rect.height;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      });
      // a single dot (e.g. a period/tap) still shows
      if (s.p.length === 1) {
        ctx.lineTo(s.p[0][0] * rect.width + 0.1, s.p[0][1] * rect.height);
      }
      ctx.stroke();
    }

    function redraw() {
      var rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      strokes.forEach(drawStroke);
    }

    /* Read the strokes back as marks on words.

       The whole point of this file used to be lost at save time: strokes are
       coordinates, so a marked-up sentence reached the grader as "annotated:
       yes" and nothing else — 260 exercises that could not be graded. Every word
       is now its own span, so the browser can say where it sits, and a stroke
       over it can be named.

       Deliberately conservative. A stroke that doesn't clearly match a gesture is
       left UNREAD rather than guessed at, and the unread count is saved too: a
       wrong reading would mark a correct answer wrong, which is worse than
       admitting we couldn't tell. */
    var metricsCtx = null;

    /* Where the LETTERS sit inside a word's line box.

       A span's rectangle is the font's full ascent+descent — for the reader's
       24px Georgia that is 27px tall while the letters fill about 11px of it. A
       child aiming at the middle of the letters is well below the middle of the
       box, so thresholds measured against the box read a strike as an underline
       and a snug circle as a strike. Measured for real here instead. */
    function glyphBand(el, topPx, heightPx) {
      try {
        if (!metricsCtx) metricsCtx = document.createElement("canvas").getContext("2d");
        var cs = window.getComputedStyle(el);
        metricsCtx.font = cs.fontStyle + " " + cs.fontWeight + " " +
                          cs.fontSize + " " + cs.fontFamily;
        var m = metricsCtx.measureText(el.textContent || "x");
        if (m.fontBoundingBoxAscent == null || m.actualBoundingBoxAscent == null) return null;
        var baseline = topPx + m.fontBoundingBoxAscent;
        return {
          top: baseline - m.actualBoundingBoxAscent,
          bottom: baseline + Math.max(0, m.actualBoundingBoxDescent),
        };
      } catch (e) {
        return null;    // older browser: fall back to the line box
      }
    }

    function wordBoxes() {
      // Measured against the CANVAS, because that is the space strokes are
      // recorded and replayed in. The canvas sits a pixel inside the surface, so
      // measuring words against the surface put the two in different spaces and
      // read every stroke slightly low.
      var srect = canvas.getBoundingClientRect();
      if (!srect.width || !srect.height) return [];
      var words = [];
      widget.querySelectorAll(".markup-word").forEach(function (el) {
        var r = el.getBoundingClientRect();
        var band = glyphBand(el, r.top, r.height);
        words.push({
          i: parseInt(el.dataset.word, 10),
          text: el.textContent,
          x0: (r.left - srect.left) / srect.width,
          x1: (r.right - srect.left) / srect.width,
          y0: (r.top - srect.top) / srect.height,
          y1: (r.bottom - srect.top) / srect.height,
          gy0: band ? (band.top - srect.top) / srect.height : null,
          gy1: band ? (band.bottom - srect.top) / srect.height : null,
        });
      });
      return words;
    }

    function readMarks() {
      return window.portalReadMarkup(wordBoxes(), strokes);
    }

    function persist() {
      if (!strokes.length) {
        input.value = "";
      } else {
        var read = readMarks();
        // Object form, with the strokes under a key. Older answers are a bare
        // array of strokes and are still parsed — see ResponseSheet._parse_markup.
        input.value = JSON.stringify({
          strokes: strokes, marks: read.marks, unread: read.unread,
        });
      }
      if (window.portalMarkDirty) window.portalMarkDirty();
    }

    function pointOf(e) {
      var rect = canvas.getBoundingClientRect();
      return [
        Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width)),
        Math.min(1, Math.max(0, (e.clientY - rect.top) / rect.height)),
      ];
    }

    if (!locked) {
      canvas.addEventListener("pointerdown", function (e) {
        e.preventDefault();
        canvas.setPointerCapture(e.pointerId);
        drawing = true;
        current = { c: tool.color, w: tool.width, p: [pointOf(e)] };
        strokes.push(current);
        redraw();
      });
      canvas.addEventListener("pointermove", function (e) {
        if (!drawing) return;
        current.p.push(pointOf(e));
        redraw();
      });
      function end() {
        if (!drawing) return;
        drawing = false;
        persist();
      }
      canvas.addEventListener("pointerup", end);
      canvas.addEventListener("pointercancel", end);
      canvas.addEventListener("pointerleave", end);

      widget.querySelectorAll("[data-color]").forEach(function (btn) {
        btn.addEventListener("click", function () {
          tool.color = btn.dataset.color;
          widget.querySelectorAll("[data-color]").forEach(function (b) { b.classList.remove("is-active"); });
          btn.classList.add("is-active");
        });
      });
      var undo = widget.querySelector("[data-tool=undo]");
      if (undo) undo.addEventListener("click", function () { strokes.pop(); redraw(); persist(); });
      var clear = widget.querySelector("[data-tool=clear]");
      if (clear) clear.addEventListener("click", function () {
        if (!strokes.length || confirm("Erase all your marks on this sentence?")) {
          strokes = []; redraw(); persist();
        }
      });
    } else {
      canvas.style.pointerEvents = "none";
      var tb = widget.querySelector(".markup-toolbar");
      if (tb) tb.style.display = "none";
    }

    fit();
    window.addEventListener("resize", fit);
    // Fonts/layout can settle a beat after load; refit so strokes line up.
    setTimeout(fit, 150);
  }

  document.querySelectorAll(".markup-widget").forEach(setup);
})();

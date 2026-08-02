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

      var hit = 0;
      words.forEach(function (w) {
        var ww = w.x1 - w.x0, wh = w.y1 - w.y0;
        if (ww <= 0 || wh <= 0) return;
        // How much of this word's width the stroke spans.
        var cover = (Math.min(x1, w.x1) - Math.max(x0, w.x0)) / ww;
        if (cover < 0.5) return;

        var kind = null;
        if (y0 <= w.y0 + 0.25 * wh && y1 >= w.y1 - 0.25 * wh && cover >= 0.6) {
          // Reaches above the word AND below it: drawn around it.
          kind = "circled";
        } else if (y0 >= w.y0 + 0.55 * wh && y0 <= w.y1 + 0.6 * wh &&
                   (y1 - y0) <= 0.9 * wh) {
          // Flat, sitting just under the word. The upper bound on y0 matters:
          // without it a line drawn well BELOW the text still claimed to
          // underline it, because "below the middle" has no floor.
          kind = "underlined";
        } else if ((y1 - y0) <= 0.7 * wh &&
                   (y0 + y1) / 2 >= w.y0 + 0.2 * wh &&
                   (y0 + y1) / 2 <= w.y1 - 0.2 * wh) {
          // Flat, through the middle.
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
        words.push({
          i: parseInt(el.dataset.word, 10),
          text: el.textContent,
          x0: (r.left - srect.left) / srect.width,
          x1: (r.right - srect.left) / srect.width,
          y0: (r.top - srect.top) / srect.height,
          y1: (r.bottom - srect.top) / srect.height,
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

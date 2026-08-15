/* Handwriting: write the answer by hand, on ruled lines, with a finger or pen.
 *
 * Third-grade writing IS handwriting. Asking her to type these would swap the
 * skill being practised for keyboard hunting, so there is no text box here —
 * the strokes are the answer.
 *
 * Strokes are stored in exactly the shape portal-markup.js uses
 * ({c, w, p:[[x,y]…]} normalized 0..1, plus the surface size), so the parent's
 * work browser and the printed charter report replay them with the machinery
 * that already exists rather than a second copy of it.
 */
(function () {
  "use strict";

  document.querySelectorAll(".handwriting-widget").forEach(function (widget) {
    var surface = widget.querySelector(".handwriting-surface");
    var canvas = widget.querySelector(".handwriting-canvas");
    var input = widget.querySelector('input[name^="answer_"]');
    if (!surface || !canvas || !input) return;

    var ctx = canvas.getContext("2d");
    var strokes = [];
    var readOnly = widget.dataset.readonly === "1";

    var saved = null;
    try { saved = JSON.parse(input.value || "null"); } catch (e) { saved = null; }
    if (saved && Array.isArray(saved.strokes)) strokes = saved.strokes;
    else if (Array.isArray(saved)) strokes = saved;

    var tool = { color: "#1d3557", width: 3 };
    var drawing = false, current = null;

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
      if (!s.p || !s.p.length) return;
      ctx.strokeStyle = s.c;
      ctx.lineWidth = s.w;
      ctx.lineCap = "round";
      ctx.lineJoin = "round";
      ctx.beginPath();
      s.p.forEach(function (pt, i) {
        var x = pt[0] * rect.width, y = pt[1] * rect.height;
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      });
      if (s.p.length === 1) {
        ctx.lineTo(s.p[0][0] * rect.width + 0.1, s.p[0][1] * rect.height);
      }
      ctx.stroke();
    }

    function redraw() {
      var rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      strokes.forEach(drawStroke);
      var empty = widget.querySelector(".handwriting-empty");
      // "Write here…" on work already turned in invites her to write
      // on a surface that will not accept it.
      if (empty) empty.hidden = strokes.length > 0 || readOnly;
    }

    function persist() {
      if (!strokes.length) {
        input.value = "";
      } else {
        var srect = surface.getBoundingClientRect();
        // Same payload shape as the markup widgets, including the surface size —
        // the replay rebuilds the box at the width she wrote on, or her letters
        // land in the wrong place on the printed page.
        input.value = JSON.stringify({
          strokes: strokes,
          surface: srect.width
            ? { w: Math.round(srect.width), h: Math.round(srect.height) }
            : null,
        });
      }
      input.dataset.answered = strokes.length ? "1" : "0";
      if (window.portalMarkDirty) window.portalMarkDirty();
    }

    function pointOf(e) {
      var rect = canvas.getBoundingClientRect();
      // Four decimals is a quarter of a pixel on a 2000px canvas — finer than
      // anyone can draw, and finer than the replay can render (it formats into
      // a 1000-unit viewBox at one decimal, so the rest is discarded anyway).
      // Raw float64 costs ~40 bytes per point, and a long handwritten answer
      // then blows past DATA_UPLOAD_MAX_MEMORY_SIZE — at which point she cannot
      // turn her work in at all and the portal just says "couldn't save".
      return [
        Math.round(Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width)) * 1e4) / 1e4,
        Math.round(Math.min(1, Math.max(0, (e.clientY - rect.top) / rect.height)) * 1e4) / 1e4,
      ];
    }

    if (!readOnly) {
      canvas.addEventListener("pointerdown", function (e) {
        drawing = true;
        canvas.setPointerCapture(e.pointerId);
        current = { c: tool.color, w: tool.width, p: [pointOf(e)] };
        strokes.push(current);
        redraw();
      });
      canvas.addEventListener("pointermove", function (e) {
        if (!drawing || !current) return;
        // A ceiling so one very long session can't produce an answer too big to
        // submit. Four ruled lines of handwriting is a few thousand points; this
        // is far above that and still an order of magnitude inside the limit.
        if (current.p.length >= 4000) return;
        current.p.push(pointOf(e));
        redraw();
      });
      ["pointerup", "pointercancel", "pointerleave"].forEach(function (evt) {
        canvas.addEventListener(evt, function () {
          if (!drawing) return;
          drawing = false;
          current = null;
          persist();
        });
      });

      widget.querySelectorAll(".handwriting-pen").forEach(function (btn) {
        btn.addEventListener("click", function () {
          widget.querySelectorAll(".handwriting-pen").forEach(function (b) {
            b.classList.remove("is-active");
          });
          btn.classList.add("is-active");
          tool.color = btn.dataset.color;
        });
      });
      var undo = widget.querySelector('[data-tool="undo"]');
      if (undo) undo.addEventListener("click", function () {
        strokes.pop(); redraw(); persist();
      });
      var clear = widget.querySelector('[data-tool="clear"]');
      if (clear) clear.addEventListener("click", function () {
        strokes = []; redraw(); persist();
      });
    }

    fit();
    window.addEventListener("resize", fit);
  });
})();

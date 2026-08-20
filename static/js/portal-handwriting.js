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
    if (!input) {
      // Answer-mode picker: the writing surface and the typing box are two
      // ways into ONE answer, so the strokes go into the question's own
      // textarea rather than a second field that would collide with it.
      var modes = widget.closest('.answer-modes');
      if (modes) input = modes.querySelector('textarea[name^="answer_"]');
    }
    if (!surface || !canvas || !input) return;

    var ctx = canvas.getContext("2d");
    var strokes = [];
    var readOnly = widget.dataset.readonly === "1";

    var saved = null;
    try { saved = JSON.parse(input.value || "null"); } catch (e) { saved = null; }
    if (saved && Array.isArray(saved.strokes)) strokes = saved.strokes;
    else if (Array.isArray(saved)) strokes = saved;

    // Restore the height she actually wrote on, BEFORE anything measures the
    // box. Strokes are stored 0..1 against their surface, so a page that grew
    // to ten lines and then reloaded at the CSS default of four would squash
    // every letter into the top of the page — and persist() would write the
    // squashed version back, compounding on every visit and reaching the
    // parent's work browser and the printed report.
    if (saved && saved.surface && saved.surface.h > 0) {
      surface.style.height = saved.surface.h + "px";
    }

    // Start on whichever pen is drawn as selected, not on a colour of our own:
    // the drawing widget's palette begins with black, and a child who sees
    // black ringed and draws navy has been told something untrue by the page.
    var activePen = widget.querySelector(".handwriting-pen.is-active");
    var tool = {
      color: (activePen && activePen.dataset.color) || "#1d3557",
      width: 3,
    };
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

    // A surface that was HIDDEN when this ran measured zero, and every stroke
    // drawn on it afterwards lands in the wrong place. The answer-mode picker
    // shows the writing surface only when she asks for it, so it needs to say
    // "you are visible now, measure again".
    widget.addEventListener("handwriting:show", fit);

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
      // Setting .value fires no event, so anything that wants to react to "she
      // has written something now" has to be told. The lexicon cards use this
      // to light their tick and spine; without it they would have to guess from
      // pointerup, and guess wrong on undo, erase, and a release off-canvas.
      widget.dispatchEvent(new CustomEvent("handwriting:change", {
        bubbles: true, detail: { answered: strokes.length > 0 },
      }));
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
          grow();
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
        // Undo pops one stroke; this drops them all and cannot be undone. It
        // sits next to Undo and is a small target for a stylus — survivable
        // when the box held four lines, not now it holds a whole paragraph.
        if (strokes.length > 2 &&
            !window.confirm("Erase everything you have written here?")) return;
        strokes = []; redraw(); persist();
      });
    }

    function grow() {
      // A whole paragraph in a nine-year-old's handwriting does not fit in the
      // four ruled lines the surface starts with, and there is no scroll: she
      // would run out of room mid-sentence with nothing to do but Erase all.
      // So the paper grows — always by a whole 48px line, so the ruling stays
      // aligned — whenever she writes near the bottom.
      if (readOnly) return;
      var lowest = 0;
      strokes.forEach(function (s) {
        (s.p || []).forEach(function (pt) { if (pt[1] > lowest) lowest = pt[1]; });
      });
      var height = surface.getBoundingClientRect().height;
      if (!height || lowest * height < height - 48) return;
      surface.style.height = (Math.round(height / 48) + 2) * 48 + "px";
      // Strokes are stored 0..1 against the surface, so a taller box would
      // stretch them. Rescale to keep every letter exactly where she put it.
      var scale = height / surface.getBoundingClientRect().height;
      strokes.forEach(function (s) {
        (s.p || []).forEach(function (pt) { pt[1] = Math.round(pt[1] * scale * 1e4) / 1e4; });
      });
      persist();
      fit();
    }

    fit();
    grow();
    window.addEventListener("resize", fit);
  });
})();

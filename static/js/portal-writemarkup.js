/* Portal write-then-markup: the child types a sentence, it auto-populates a
   drawing surface below, and she underlines / circles the parts right on it
   (e.g. "circle the simple predicate, underline the complete predicate").

   The answer is stored as JSON {"text": "...", "strokes": [...]} in a hidden
   input that the autosave layer picks up. Strokes use relative [0-1] coords so
   they replay at any size. The typed sentence also carries the class
   `portal-answer`, so the spelling + word helpers attach to it. No deps. */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  var locked = !!(form && form.dataset.submitted === "1");

  function setup(widget) {
    var textarea = widget.querySelector(".writemark-input");
    var passage = widget.querySelector(".writemark-passage");
    var surface = widget.querySelector(".markup-surface");
    var canvas = widget.querySelector(".markup-canvas");
    var input = widget.querySelector("input[data-question]");
    if (!textarea || !passage || !canvas || !input) return;
    var ctx = canvas.getContext("2d");

    var strokes = [];
    var saved = null;
    try { saved = JSON.parse(input.value || "{}"); } catch (e) { saved = null; }
    if (saved && typeof saved === "object" && !Array.isArray(saved)) {
      if (typeof saved.text === "string") textarea.value = saved.text;
      if (Array.isArray(saved.strokes)) strokes = saved.strokes;
    } else if ((input.value || "").trim()) {
      textarea.value = input.value;   // legacy plain-text answer (was a typed question) — keep her words
    }
    passage.textContent = textarea.value;   // mirror the sentence into the drawing surface

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
      if (s.p.length === 1) ctx.lineTo(s.p[0][0] * rect.width + 0.1, s.p[0][1] * rect.height);
      ctx.stroke();
    }

    function redraw() {
      var rect = canvas.getBoundingClientRect();
      ctx.clearRect(0, 0, rect.width, rect.height);
      strokes.forEach(drawStroke);
    }

    function persist() {
      var text = textarea.value;
      input.value = (text.trim() || strokes.length)
        ? JSON.stringify({ text: text, strokes: strokes }) : "";
      input.dataset.answered = text.trim() ? "1" : "0";
      if (window.portalMarkDirty) window.portalMarkDirty();
    }

    function pointOf(e) {
      var rect = canvas.getBoundingClientRect();
      return [
        Math.min(1, Math.max(0, (e.clientX - rect.left) / rect.width)),
        Math.min(1, Math.max(0, (e.clientY - rect.top) / rect.height)),
      ];
    }

    // Typing updates the drawing surface live and saves the text. Strokes use
    // relative coords, so editing the sentence AFTER marking it up can shift the
    // marks off the words — the flow (and hint) steers her to write first, mark last.
    textarea.addEventListener("input", function () {
      passage.textContent = textarea.value;
      persist();
      requestAnimationFrame(fit);   // the sentence may have grown a line — resize the canvas
    });

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
    setTimeout(fit, 150);  // fonts/layout settle a beat after load
  }

  document.querySelectorAll(".writemark-widget").forEach(setup);
})();

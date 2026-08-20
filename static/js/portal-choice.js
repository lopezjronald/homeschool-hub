/* Two small widgets for the Studies Weekly pages.

   1. CHOICE — pick one, or pick several. Answers persist as
      {"picked": ["a"]} through the same hidden-input contract every other
      widget uses, so autosave, submit and the reports need no special case.

   2. ANSWER MODE — on a written-answer question, let her choose how to answer:
      type it, or write it by hand. Both surfaces are rendered; the picker shows
      one and tells the other it is hidden. The handwriting canvas must be told
      when it becomes visible, because a canvas measured while hidden is zero
      pixels wide and every stroke afterwards lands in the wrong place. */
(function () {
  "use strict";

  /* ---- multiple choice ---- */
  Array.prototype.slice.call(
    document.querySelectorAll(".choice-widget")
  ).forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    if (!hidden) return;
    var inputs = Array.prototype.slice.call(widget.querySelectorAll(".choice-input"));

    var picked = [];
    try {
      var parsed = JSON.parse(hidden.value || "{}");
      if (parsed && Array.isArray(parsed.picked)) picked = parsed.picked.map(String);
    } catch (e) {
      // A legacy plain answer ("a") is still an answer — keep it rather than
      // silently clearing what she chose last time.
      if (hidden.value) picked = [String(hidden.value)];
    }
    inputs.forEach(function (i) {
      if (picked.indexOf(i.value) !== -1) i.checked = true;
      i.closest(".choice-option").classList.toggle("is-picked", i.checked);
    });

    function sync() {
      var chosen = inputs.filter(function (i) { return i.checked; })
                         .map(function (i) { return i.value; });
      inputs.forEach(function (i) {
        i.closest(".choice-option").classList.toggle("is-picked", i.checked);
      });
      hidden.value = chosen.length ? JSON.stringify({ picked: chosen }) : "";
      hidden.dataset.answered = chosen.length ? "1" : "0";
      if (window.portalTouch) window.portalTouch("Saving…");
    }

    hidden.dataset.answered = picked.length ? "1" : "0";
    widget.addEventListener("change", function (e) {
      if (e.target && e.target.classList.contains("choice-input")) sync();
    });
  });

  /* ---- how do you want to answer? ---- */
  Array.prototype.slice.call(
    document.querySelectorAll(".answer-mode")
  ).forEach(function (picker) {
    var wrap = picker.closest(".answer-modes");
    if (!wrap) return;
    var panes = {
      type: wrap.querySelector('[data-mode-pane="type"]'),
      write: wrap.querySelector('[data-mode-pane="write"]'),
    };
    var buttons = Array.prototype.slice.call(picker.querySelectorAll(".answer-mode-btn"));

    function show(mode) {
      Object.keys(panes).forEach(function (k) {
        if (!panes[k]) return;
        var on = k === mode;
        panes[k].hidden = !on;
        if (on) {
          // Tell a handwriting surface it can measure itself now.
          var hw = panes[k].querySelector(".handwriting-widget");
          if (hw) hw.dispatchEvent(new CustomEvent("handwriting:show"));
        }
      });
      buttons.forEach(function (b) {
        b.classList.toggle("is-active", b.dataset.mode === mode);
        b.setAttribute("aria-pressed", b.dataset.mode === mode ? "true" : "false");
      });
      try {
        window.localStorage.setItem("answerMode", mode);
      } catch (e) { /* private browsing — the choice just will not persist */ }
    }

    buttons.forEach(function (b) {
      b.addEventListener("click", function () { show(b.dataset.mode); });
    });

    // Open on whichever she used last, so a child who writes everything by
    // hand is not re-choosing on every question of every page.
    var remembered = null;
    try { remembered = window.localStorage.getItem("answerMode"); } catch (e) {}
    show(panes[remembered] ? remembered : "type");
  });
})();

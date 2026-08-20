/* Three small widgets for the Studies Weekly pages.

   1. CHOICE — pick one, or pick several. Answers persist as
      {"picked": ["a"]} through the same hidden-input contract every other
      widget uses, so autosave, submit and the reports need no special case.

   2. ANSWER MODE — on a written-answer question, let her choose how to answer:
      type it, or write it by hand. Both surfaces are rendered; the picker shows
      one and tells the other it is hidden. The handwriting canvas must be told
      when it becomes visible, because a canvas measured while hidden is zero
      pixels wide and every stroke afterwards lands in the wrong place.

   3. ORDER — a scrambled list she numbers back into sequence. `placeSteps` is
      the DOM-free core, exported so portal-choice.test.js can run it under
      plain node; it decides both what gets STORED and whether the question
      counts as answered, and getting that second part wrong put "10 of 10
      answered" above a one-way submit button on a half-finished page. */
(function () {
  "use strict";

  /* Turn the numbers she typed into the ordered list, plus whether it is
     finished. Pure: takes step names and the raw picker values, in row order. */
  function placeSteps(steps, values) {
    // Pre-filled with '' rather than left sparse. A bare [] with only slot 5
    // set has length 5 and holes everywhere else, and every()/map()/some() all
    // SKIP holes — so one number read as fully answered, and JSON.stringify
    // wrote nulls that printed as "1. None" on the parent's report.
    var order = steps.map(function () { return ''; });
    steps.forEach(function (step, i) {
      var n = parseInt(values[i], 10);
      if (n >= 1 && n <= steps.length) order[n - 1] = step;
    });
    return {
      order: order,
      full: order.every(function (x) { return !!x; }),
      started: order.some(Boolean),
    };
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { placeSteps: placeSteps };
    return;
  }

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

  /* ---- put the steps in order ---- */
  Array.prototype.slice.call(
    document.querySelectorAll('.order-widget')
  ).forEach(function (widget) {
    var hidden = widget.querySelector('input[type=hidden][data-question]');
    if (!hidden) return;
    var steps = Array.prototype.slice.call(widget.querySelectorAll('.order-step'));
    var picks = steps.map(function (li) { return li.querySelector('.order-pick'); });

    var saved = [];
    try {
      var parsed = JSON.parse(hidden.value || '{}');
      if (parsed && Array.isArray(parsed.order)) saved = parsed.order.map(String);
    } catch (e) { /* unreadable answers hydrate blank, never crash the page */ }
    if (saved.length) {
      steps.forEach(function (li, i) {
        var at = saved.indexOf(li.dataset.step);
        if (at !== -1) picks[i].value = String(at + 1);
      });
    }

    function sync(quiet) {
      var placed = placeSteps(
        steps.map(function (li) { return li.dataset.step; }),
        picks.map(function (p) { return p.value; }));
      hidden.value = placed.started ? JSON.stringify({ order: placed.order }) : '';
      hidden.dataset.answered = placed.full ? '1' : '0';
      if (!quiet && window.portalTouch) window.portalTouch('Saving…');
    }

    widget.addEventListener('change', function (e) {
      if (!e.target.classList.contains('order-pick')) return;
      var chosen = e.target.value;
      if (chosen) {
        // Taking a number that is already used SWAPS the two, so she can never
        // end up with two step 3s and no step 1 — and never has to clear one
        // box before filling another.
        picks.forEach(function (p) {
          if (p !== e.target && p.value === chosen) p.value = e.target.dataset.was || '';
        });
      }
      picks.forEach(function (p) { p.dataset.was = p.value; });
      sync();
    });
    picks.forEach(function (p) { p.dataset.was = p.value; });
    // Declare the answered state on load, the way every sibling widget does.
    // Without it the autosave counter falls back to "the field is not empty",
    // and a half-numbered question she came back to counted as done. Quietly —
    // arriving on a page is not saving.
    sync(true);
  });
})();

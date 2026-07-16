/* AI-assisted one-tap spelling fixes for the writing boxes.

   The browser draws the red squiggle natively (the textarea keeps
   spellcheck="true"). On top of that, this adds a small "Fix spelling" bar
   under the box: on a typing pause we ask the server (tutor.ai.check_spelling —
   a small fast model that also catches phonetic kid spellings like
   "becuse"->"because") for misspelled words and offer tap-to-fix corrections.
   We do NOT draw our own squiggle — the native one handles that, so there is
   only ever one underline. Runs only when the form exposes a spellcheck URL
   (i.e. NOT on spelling curricula). */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  if (!form || form.dataset.submitted === "1") return;
  var url = form.dataset.spellcheckUrl;
  if (!url) return;

  var WORD_CHAR = /[A-Za-z'\-]/;
  function reEscape(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  // Every place the child types: the answer textareas AND the inline fill-in-the-
  // blank (cloze) inputs, so the spelling help is everywhere she writes.
  Array.prototype.slice.call(document.querySelectorAll("textarea.portal-answer, .cloze-input")).forEach(function (area) {
    if (area.readOnly) return;
    area.spellcheck = true;  // let the browser draw the squiggle; we add the one-tap fixes

    var bar = document.createElement("div");
    bar.className = "spellfix-bar";
    bar.hidden = true;
    // An inline cloze blank drops its fix bar below the whole passage, not inline
    // after the input; a textarea keeps its bar right after it.
    (area.closest(".vocab-cloze") || area).insertAdjacentElement("afterend", bar);

    var misspelled = [];   // [{wrong, fixes:[...]}] from the server (no-ops already dropped)
    var timer = null;
    var seq = 0;           // guards against out-of-order responses
    var lastChecked = null;

    // The word the caret sits inside right now (lowercased), or null if the
    // caret is between words, there's a selection, or the box isn't focused.
    // We never flag that word — she's still typing it.
    function wordUnderCaret() {
      if (document.activeElement !== area) return null;
      if (area.selectionStart !== area.selectionEnd) return null;
      var v = area.value, i = area.selectionStart, l = i, r = i;
      while (l > 0 && WORD_CHAR.test(v.charAt(l - 1))) l--;
      while (r < v.length && WORD_CHAR.test(v.charAt(r))) r++;
      return r > l ? v.slice(l, r).toLowerCase() : null;
    }

    // Flagged words worth showing: still present in the text, with a real fix,
    // and not the word she's mid-typing. Returns cleaned {wrong, fixes}.
    function visible() {
      var low = area.value.toLowerCase();
      var skip = wordUnderCaret();
      var out = [];
      misspelled.forEach(function (m) {
        if (!m.wrong) return;
        var wl = m.wrong.toLowerCase();
        if (wl === skip || low.indexOf(wl) === -1) return;
        // Defensive: drop any "fix" that just echoes the word (the server does
        // this too), so a stray "bullied -> bullied" never renders or loops.
        var fixes = (m.fixes || []).filter(function (f) { return f && f.toLowerCase() !== wl; });
        if (fixes.length) out.push({ wrong: m.wrong, fixes: fixes });
      });
      return out;
    }

    function renderBar() {
      var items = visible();
      if (!items.length) { bar.hidden = true; bar.textContent = ""; return; }
      bar.hidden = false;
      bar.textContent = "";
      var label = document.createElement("span");
      label.className = "spellfix-label";
      label.textContent = "✏️ Fix spelling:";
      bar.appendChild(label);
      items.forEach(function (m) {
        var group = document.createElement("span");
        group.className = "spellfix-group";
        var wrong = document.createElement("span");
        wrong.className = "spellfix-wrong";
        wrong.textContent = m.wrong;
        group.appendChild(wrong);
        var arrow = document.createElement("span");
        arrow.className = "spellfix-arrow";
        arrow.textContent = "→";
        group.appendChild(arrow);
        m.fixes.slice(0, 3).forEach(function (fix) {
          var chip = document.createElement("button");
          chip.type = "button";
          chip.className = "spellfix-chip";
          chip.textContent = fix;
          chip.addEventListener("mousedown", function (ev) { ev.preventDefault(); });  // keep focus/caret
          chip.addEventListener("click", function () { applyFix(m.wrong, fix); });
          group.appendChild(chip);
        });
        bar.appendChild(group);
      });
    }

    function applyFix(wrong, fix) {
      var re = new RegExp("\\b" + reEscape(wrong) + "\\b", "gi");
      area.value = area.value.replace(re, function (match) {
        return (match.charAt(0) === match.charAt(0).toUpperCase())
          ? fix.charAt(0).toUpperCase() + fix.slice(1) : fix;
      });
      area.dispatchEvent(new Event("input", { bubbles: true }));  // autosave
      misspelled = misspelled.filter(function (m) {
        return m.wrong.toLowerCase() !== wrong.toLowerCase();
      });
      renderBar();
      schedule();
    }

    function schedule() {
      if (timer) clearTimeout(timer);
      timer = setTimeout(check, 1200);  // wait until she's paused before asking
    }

    function check() {
      var text = area.value;
      if (text.trim().length < 2) { misspelled = []; lastChecked = text; renderBar(); return; }
      if (text === lastChecked) { renderBar(); return; }  // unchanged → no API call (saves tokens)
      lastChecked = text;
      var mine = ++seq;
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }),
        credentials: "same-origin",
      })
        .then(function (r) { return r.ok ? r.json() : { misspelled: [] }; })
        .then(function (d) {
          if (mine !== seq) return;  // a newer check superseded this one
          misspelled = d.misspelled || [];
          renderBar();
        })
        .catch(function () { /* keep whatever we had */ });
    }

    // Typing schedules a fresh check; moving the caret only re-filters the bar
    // (cheap, no API call) so the word she's on drops out and reappears once she
    // moves off it.
    area.addEventListener("input", function () { renderBar(); schedule(); });
    area.addEventListener("keyup", renderBar);
    area.addEventListener("click", renderBar);
    area.addEventListener("blur", renderBar);

    schedule();  // check any pre-filled answer on load
  });
})();

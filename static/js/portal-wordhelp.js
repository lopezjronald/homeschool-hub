/* Word helper: pick a word while writing → get better/similar words.

   When the child selects a single word in an answer box, a little bar of
   suggestions appears under it; tapping one swaps the word in (and autosaves).
   Backed by the token-authed /word-help/ endpoint (disabled on spelling
   curricula, so the bar simply never wires up there). Kid-facing, plain text. */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  if (!form || form.dataset.submitted === "1") return;
  var url = form.dataset.wordhelpUrl;
  if (!url) return;  // spelling curriculum, or the feature is off

  var WORD_RE = /^[A-Za-z][A-Za-z'-]{1,24}$/;
  var cache = {};

  // Answer textareas AND inline fill-in-the-blank (cloze) inputs, so "better
  // words" works everywhere the child writes her own words.
  Array.prototype.slice.call(document.querySelectorAll("textarea.portal-answer, .cloze-input")).forEach(function (area) {
    if (area.readOnly) return;

    var bar = document.createElement("div");
    bar.className = "wordhelp-bar";
    bar.hidden = true;
    // A cloze blank shows its suggestions below the whole passage, not inline.
    (area.closest(".vocab-cloze") || area).insertAdjacentElement("afterend", bar);

    var current = { start: 0, end: 0 };
    var seq = 0;

    function selectedWord() {
      var s = area.selectionStart, e = area.selectionEnd;
      if (s === e) return null;
      var chunk = area.value.slice(s, e);
      var word = chunk.trim();
      if (!WORD_RE.test(word)) return null;      // must be ONE clean word
      var lead = chunk.indexOf(word);
      return { start: s + lead, end: s + lead + word.length, word: word };
    }

    function hide() { bar.hidden = true; bar.textContent = ""; }

    function onSelect() {
      var sel = selectedWord();
      if (!sel) { hide(); return; }
      current = { start: sel.start, end: sel.end };
      render(sel.word, null);                     // loading state
      var mine = ++seq;
      lookup(sel.word).then(function (words) {
        if (mine === seq) render(sel.word, words);
      });
    }

    function lookup(word) {
      var key = word.toLowerCase();
      if (cache[key]) return Promise.resolve(cache[key]);
      return fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ word: word }),
        credentials: "same-origin",
      })
        .then(function (r) { return r.ok ? r.json() : { words: [] }; })
        .then(function (d) { cache[key] = (d && d.words) || []; return cache[key]; })
        .catch(function () { return []; });
    }

    function render(word, words) {
      bar.hidden = false;
      bar.textContent = "";
      var label = document.createElement("span");
      label.className = "wordhelp-label";
      label.textContent = "✨ Better words for “" + word + "”:";
      bar.appendChild(label);

      if (words === null) {
        var loading = document.createElement("span");
        loading.className = "wordhelp-note";
        loading.textContent = "looking…";
        bar.appendChild(loading);
        return;
      }
      if (!words.length) {
        var none = document.createElement("span");
        none.className = "wordhelp-note";
        none.textContent = "no ideas for that one — try another word!";
        bar.appendChild(none);
        return;
      }
      words.forEach(function (w) {
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "wordhelp-chip";
        chip.textContent = w;
        // Keep the textarea selection when the chip is pressed.
        chip.addEventListener("mousedown", function (ev) { ev.preventDefault(); });
        chip.addEventListener("click", function () { replace(w); });
        bar.appendChild(chip);
      });
    }

    function replace(w) {
      var v = area.value;
      var orig = v.slice(current.start, current.end);
      if (orig && orig.charAt(0) === orig.charAt(0).toUpperCase()) {
        w = w.charAt(0).toUpperCase() + w.slice(1);   // match the original's capitalisation
      }
      area.value = v.slice(0, current.start) + w + v.slice(current.end);
      var caret = current.start + w.length;
      area.focus();
      area.setSelectionRange(caret, caret);
      area.dispatchEvent(new Event("input", { bubbles: true }));  // fire autosave
      hide();
    }

    area.addEventListener("select", onSelect);
    area.addEventListener("mouseup", onSelect);
    area.addEventListener("dblclick", onSelect);
    area.addEventListener("keyup", onSelect);
    area.addEventListener("blur", function () { setTimeout(hide, 200); });
  });
})();

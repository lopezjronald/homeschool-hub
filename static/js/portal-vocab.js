/* Portal vocabulary widgets — replicating the Blackbird workbook's Acquire page.

   1) Matching: tap a word and a numbered definition (either order, tap again to
      un-pick). A correct pair locks green with the number in the word's slot; a
      wrong pair shakes gently and clears so the child can try again.
   2) Fill-in-the-blank: each sentence has a blank; the child picks the best
      word from the word bank. Correct locks green; wrong shakes and resets.
   3) Cloze: a passage with inline blanks the child fills in her OWN words
      (no auto-checking — the parent reviews it).

   Answers persist as JSON in a hidden field that the existing autosave layer
   saves and submits (same pattern as the markup/character widgets). Each hidden
   field also carries data-answered ("1"/"0") so the "N of M answered" counter
   reflects a COMPLETED exercise, not a first lucky tap. No external deps. */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  var submitted = !!(form && form.dataset.submitted === "1");
  var hasOwn = function (obj, key) { return Object.prototype.hasOwnProperty.call(obj, key); };

  function parse(value) {
    try {
      var data = JSON.parse(value || "{}");
      return data && typeof data === "object" && !Array.isArray(data) ? data : {};
    } catch (e) { return {}; }
  }

  function shake(el) {
    el.classList.add("vocab-shake");
    setTimeout(function () { el.classList.remove("vocab-shake"); }, 500);
  }

  function touch(label) {
    if (!submitted && window.portalTouch) window.portalTouch(label);
  }

  /* ---------------- Matching ---------------- */
  Array.prototype.slice.call(document.querySelectorAll(".vocab-matching")).forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    var words = Array.prototype.slice.call(widget.querySelectorAll(".vocab-word"));
    var defs = Array.prototype.slice.call(widget.querySelectorAll(".vocab-def"));
    var done = widget.querySelector(".vocab-done");
    if (!hidden || !words.length || !defs.length) return;

    var saved = parse(hidden.value);
    var matches = (saved.matches && typeof saved.matches === "object" && !Array.isArray(saved.matches))
      ? saved.matches : {};
    var tries = typeof saved.tries === "number" ? saved.tries : 0;
    var selWord = null, selDef = null;

    function defFor(n) {
      return defs.filter(function (d) { return d.dataset.n === String(n); })[0] || null;
    }

    function lockPair(wordBtn, defBtn, n) {
      wordBtn.classList.add("is-locked");
      wordBtn.disabled = true;
      wordBtn.querySelector(".vocab-slot").textContent = n;
      if (defBtn) { defBtn.classList.add("is-locked"); defBtn.disabled = true; }
    }

    function allDone() {
      return words.every(function (w) { return w.classList.contains("is-locked"); });
    }

    function persist() {
      var complete = allDone();
      hidden.value = (Object.keys(matches).length || tries)
        ? JSON.stringify({ matches: matches, tries: tries })
        : "";
      hidden.dataset.answered = complete ? "1" : "0";
    }

    function checkDone() {
      if (allDone() && done) done.hidden = false;
    }

    // Hydrate previously-locked pairs; drop stale saves that no longer match
    // the exercise (e.g. the numbering changed after a re-seed).
    words.forEach(function (w) {
      var word = w.dataset.word;
      if (!hasOwn(matches, word)) return;
      var d = defFor(matches[word]);
      if (d && d.dataset.word === word) {
        lockPair(w, d, matches[word]);
      } else {
        delete matches[word];
      }
    });
    persist();
    checkDone();

    if (submitted) {
      words.concat(defs).forEach(function (b) { b.disabled = true; });
      return;
    }

    function deselect() {
      if (selWord) selWord.classList.remove("is-selected");
      if (selDef) selDef.classList.remove("is-selected");
      selWord = selDef = null;
    }

    function evaluate() {
      if (!selWord || !selDef) return;
      var word = selWord.dataset.word;
      if (selDef.dataset.word === word) {
        matches[word] = parseInt(selDef.dataset.n, 10);
        lockPair(selWord, selDef, selDef.dataset.n);
      } else {
        tries += 1;
        shake(selWord); shake(selDef);
      }
      deselect();                                  // immediate — no timer races
      persist();
      touch("Matching…");
      checkDone();
    }

    words.forEach(function (w) {
      w.addEventListener("click", function () {
        if (w.classList.contains("is-locked")) return;
        if (selWord === w) {                       // tap again to un-pick
          w.classList.remove("is-selected");
          selWord = null;
          return;
        }
        if (selWord) selWord.classList.remove("is-selected");
        selWord = w;
        w.classList.add("is-selected");
        evaluate();
      });
    });
    defs.forEach(function (d) {
      d.addEventListener("click", function () {
        if (d.classList.contains("is-locked")) return;
        if (selDef === d) {                        // tap again to un-pick
          d.classList.remove("is-selected");
          selDef = null;
          return;
        }
        if (selDef) selDef.classList.remove("is-selected");
        selDef = d;
        d.classList.add("is-selected");
        evaluate();
      });
    });
  });

  /* ---------------- Fill in the blank ---------------- */
  Array.prototype.slice.call(document.querySelectorAll(".vocab-fillblank")).forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    var rows = Array.prototype.slice.call(widget.querySelectorAll(".vocab-sentence"));
    var done = widget.querySelector(".vocab-done");
    if (!hidden || !rows.length) return;

    var saved = parse(hidden.value);
    var blanks = (saved.blanks && typeof saved.blanks === "object" && !Array.isArray(saved.blanks))
      ? saved.blanks : {};
    var tries = typeof saved.tries === "number" ? saved.tries : 0;

    function allDone() {
      return rows.every(function (r) { return r.classList.contains("is-locked"); });
    }

    function persist() {
      hidden.value = (Object.keys(blanks).length || tries)
        ? JSON.stringify({ blanks: blanks, tries: tries })
        : "";
      hidden.dataset.answered = allDone() ? "1" : "0";
    }

    function markUsedWords() {
      // A word can only be used once — gray it out in the other dropdowns.
      var used = Object.keys(blanks).map(function (k) { return blanks[k]; });
      rows.forEach(function (row) {
        var select = row.querySelector("select");
        if (!select || select.disabled) return;
        Array.prototype.slice.call(select.options).forEach(function (opt) {
          if (opt.value) opt.disabled = used.indexOf(opt.value) !== -1;
        });
      });
    }

    function lockRow(row, word) {
      var select = row.querySelector("select");
      select.value = word;
      select.disabled = true;
      row.classList.add("is-locked");
    }

    function checkDone() {
      if (allDone() && done) done.hidden = false;
    }

    rows.forEach(function (row) {
      var idx = row.dataset.index;
      if (hasOwn(blanks, idx)) {
        if (blanks[idx] === row.dataset.word) {
          lockRow(row, blanks[idx]);
        } else {
          delete blanks[idx];                      // stale save from an old exercise
        }
      }
    });
    markUsedWords();
    persist();
    checkDone();

    if (submitted) {
      rows.forEach(function (row) { row.querySelector("select").disabled = true; });
      return;
    }

    rows.forEach(function (row) {
      var select = row.querySelector("select");
      select.addEventListener("change", function () {
        if (!select.value) return;
        if (select.value === row.dataset.word) {
          blanks[row.dataset.index] = select.value;
          lockRow(row, select.value);
          markUsedWords();
        } else {
          tries += 1;
          shake(row);
          select.value = "";
        }
        persist();
        touch("Filling in…");
        checkDone();
      });
    });
  });

  /* ---------------- Cloze (own words, no auto-check) ---------------- */
  Array.prototype.slice.call(document.querySelectorAll(".vocab-cloze")).forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    var inputs = Array.prototype.slice.call(widget.querySelectorAll(".cloze-input"));
    if (!hidden || !inputs.length) return;

    var saved = parse(hidden.value);
    var blanks = (saved.blanks && typeof saved.blanks === "object" && !Array.isArray(saved.blanks))
      ? saved.blanks : {};

    inputs.forEach(function (input) {
      var idx = input.dataset.blank;
      if (hasOwn(blanks, idx)) input.value = blanks[idx];
    });

    function persist() {
      var any = false;
      inputs.forEach(function (input) {
        if (input.value.trim()) {
          blanks[input.dataset.blank] = input.value;
          any = true;
        } else {
          delete blanks[input.dataset.blank];
        }
      });
      hidden.value = any ? JSON.stringify({ blanks: blanks }) : "";
      hidden.dataset.answered = any ? "1" : "0";
    }
    persist();

    if (submitted) {
      inputs.forEach(function (input) { input.readOnly = true; });
      return;
    }

    inputs.forEach(function (input) {
      input.addEventListener("input", function () {
        persist();
        touch("Typing…");
      });
    });
  });
})();

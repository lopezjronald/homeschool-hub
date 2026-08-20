/* The LINE # / SYLLABLES grid — the final-poem step of every Small Forms
 * section.
 *
 * One input per line of the form, each labelled with its target count, and a
 * live syllable ESTIMATE as she types. The estimate is a check, not a judge:
 * English syllable counting by rule is approximate (the guide has her clap it
 * out), so the meter turns green at the target and amber near it, and never
 * blocks anything. Her own count wins.
 *
 * The whole poem is stored as plain text lines (title first) in the hidden
 * textarea that autosave already watches — the grader, the work browser and
 * the printed report read it with no new machinery.
 */
(function () {
  "use strict";

  function syllables(word) {
    var w = word.toLowerCase().replace(/[^a-z]/g, "");
    if (!w) return 0;
    if (w.length <= 2) return 1;
    // Trailing silent e ("time", "shore") — but not "-le" ("little") which
    // carries its own syllable. Test the CLEANED word: testing the raw token
    // meant "little," (with punctuation) failed the -le check and lost a
    // syllable — and poems put punctuation exactly where -le words land.
    if (!/[^aeiouy]le$/.test(w)) w = w.replace(/e$/, "");
    var groups = w.match(/[aeiouy]+/g);
    return groups ? Math.max(1, groups.length) : 1;
  }

  function countLine(text) {
    return text.split(/\s+/).filter(Boolean)
      .reduce(function (n, w) { return n + syllables(w); }, 0);
  }

  document.querySelectorAll(".po-grid").forEach(function (grid) {
    var store = grid.querySelector(".po-grid-store");
    var title = grid.querySelector(".po-grid-title");
    var rows = [].slice.call(grid.querySelectorAll(".po-grid-row:not(.po-grid-row--title)"));
    if (!store) return;
    var readOnly = grid.dataset.readonly === "1";

    // Restore: title on line 1, then one line per row.
    var saved = (store.value || "").replace(/\r/g, "").split("\n");
    if (saved.length && title) title.value = saved[0] || "";
    rows.forEach(function (row, i) {
      row.querySelector(".po-grid-input").value = saved[i + 1] || "";
    });

    function paintRow(row) {
      var input = row.querySelector(".po-grid-input");
      var count = row.querySelector(".po-grid-count");
      var target = parseInt(row.dataset.target, 10);
      if (!count || !target) return;
      var got = countLine(input.value);
      var b = count.querySelector(".po-got");
      if (b) b.textContent = got;
      row.classList.toggle("po-hit", got === target && input.value.trim() !== "");
      row.classList.toggle("po-near", Math.abs(got - target) === 1 && input.value.trim() !== "");
    }

    function persist() {
      var lines = [(title ? title.value : "")].concat(
        rows.map(function (r) { return r.querySelector(".po-grid-input").value; }));
      // Trim trailing empties so a blank grid stays a blank answer.
      while (lines.length && !lines[lines.length - 1].trim()) lines.pop();
      store.value = lines.join("\n");
      if (window.portalMarkDirty) window.portalMarkDirty();
    }

    rows.forEach(function (row) {
      paintRow(row);
      var input = row.querySelector(".po-grid-input");
      if (readOnly) return;
      input.addEventListener("input", function () { paintRow(row); persist(); });
      // Enter moves to the next line, the way paper does.
      input.addEventListener("keydown", function (e) {
        if (e.key !== "Enter") return;
        e.preventDefault();
        var next = rows[rows.indexOf(row) + 1];
        if (next) next.querySelector(".po-grid-input").focus();
      });
    });
    if (title && !readOnly) {
      title.addEventListener("input", persist);
      title.addEventListener("keydown", function (e) {
        if (e.key !== "Enter") return;
        e.preventDefault();
        if (rows[0]) rows[0].querySelector(".po-grid-input").focus();
      });
    }
  });
})();

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

  // Words whose adjacent vowels are TWO beats, against the rule that counts a
  // vowel run as one. Kept as a short list rather than guessed at: "io" is two
  // sounds in "lion" and one in "nation", and no compact rule tells them apart.
  // Everything here is a word a child actually reaches for in a nature poem —
  // "violet" among them, which counted 2 and is 3.
  var SPLIT_VOWELS = ("quiet quietly poem poems poet poets poetry lion lions "
    + "being science giant diary radio area idea violet violets cruel ruin "
    + "fluid riot trial dial dying lying flying crying trying drying frying "
    + "prior real really create creates creating creation piano serial genius "
    + "medium").split(" ");
  var SPLIT = Object.create(null);
  SPLIT_VOWELS.forEach(function (w) { SPLIT[w] = 1; });

  // Contractions, which no rule gets right: "don't" is one beat and "isn't" is
  // two, and the only difference is whether the letter before the n is a vowel.
  // Written out rather than reasoned about — "aren't" is one beat and breaks
  // every rule that gets the rest of them right.
  var EXACT = Object.assign(Object.create(null), {
    dont: 1, cant: 1, wont: 1, arent: 1, werent: 1, im: 1, ive: 1, ill: 1,
    id: 1, its: 1, thats: 1, whats: 1, hes: 1, shes: 1, theyre: 1, youre: 1,
    isnt: 2, wasnt: 2, hasnt: 2, havent: 2, doesnt: 2, didnt: 2, couldnt: 2,
    wouldnt: 2, shouldnt: 2, wouldve: 2, couldve: 2, shouldve: 2,
  });

  // "-ed" that is still a beat. The silent-e rule below is right for verbs
  // ("walked", "danced") and wrong for adjectives ("wicked", "sacred") and for
  // words that merely end that way ("hundred"). Same shape as SPLIT_VOWELS,
  // and for the same reason: no rule separates them, so they are listed.
  var ED_IS_A_BEAT = Object.create(null);
  ("sacred naked wicked crooked jagged rugged ragged wretched blessed beloved "
   + "hundred hatred kindred aged learned cursed rugged dogged").split(" ")
    .forEach(function (w) { ED_IS_A_BEAT[w] = 1; });

  function syllables(word) {
    // Apostrophes are dropped, not treated as a break: "don't" is one beat.
    var w = word.toLowerCase().replace(/[^a-z']/g, "").replace(/'/g, "");
    if (!w) return 0;
    if (EXACT[w]) return EXACT[w];
    var bonus = SPLIT[w] ? 1 : 0;
    if (w.length <= 2) return 1 + bonus;

    // Silent "-ed": walked, danced, reached are ONE beat. Not after t or d
    // ("wanted", "needed"), where the ending is its own beat. This was the
    // single biggest error — past tense is everywhere in a poem, and every one
    // of them was counted a syllable long.
    if (/[^td]ed$/.test(w) && !ED_IS_A_BEAT[w]) w = w.slice(0, -2) + "d";
    // Silent "-es": leaves, makes, hopes are ONE beat. Not after a sibilant
    // ("roses", "wishes", "branches"), where it is a beat of its own.
    else if (/es$/.test(w) && !/(s|x|z|ch|sh|c|g|i)es$/.test(w)) {
      w = w.slice(0, -2) + "s";
    }

    // Trailing silent e ("time", "shore") — but not "-le" ("little") which
    // carries its own syllable. Test the CLEANED word: testing the raw token
    // meant "little," (with punctuation) failed the -le check and lost a
    // syllable — and poems put punctuation exactly where -le words land.
    if (!/[^aeiouy]le$/.test(w)) w = w.replace(/e$/, "");
    var groups = w.match(/[aeiouy]+/g);
    return Math.max(1, groups ? groups.length : 1) + bonus;
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

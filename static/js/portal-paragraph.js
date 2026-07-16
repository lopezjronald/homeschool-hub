/* Portal paragraph writing: a rough draft split into labeled sections (like the
   workbook — Topic Sentence / Supporting Sentences / Concluding Sentence), then
   a final draft where she writes the whole paragraph. The section boxes + final
   box serialize to {rough: [...], final: "..."} JSON in a hidden field the
   autosave layer already saves + submits (mirrors the character-boxes widget).
   A "Pull in my rough draft" button seeds the final draft from the sections. */
(function () {
  "use strict";

  Array.prototype.slice.call(document.querySelectorAll(".paragraph-widget")).forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    var boxes = Array.prototype.slice.call(widget.querySelectorAll(".para-box"));
    var finalBox = widget.querySelector(".para-final-box");
    var pull = widget.querySelector(".para-pull");
    if (!hidden || !finalBox) return;

    // Hydrate from the saved {rough:[...], final:"..."} map. A legacy plain-text
    // answer (from before this widget, or a text question converted to paragraph)
    // isn't that shape — keep it in the first box so nothing she wrote is lost.
    var data = {};
    var legacy = "";
    try {
      var parsed = JSON.parse(hidden.value || "{}");
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) data = parsed;
      else legacy = hidden.value || "";
    } catch (e) { legacy = hidden.value || ""; }
    var rough = Array.isArray(data.rough) ? data.rough : [];
    boxes.forEach(function (box, i) { if (rough[i] != null) box.value = rough[i]; });
    if (typeof data.final === "string") finalBox.value = data.final;

    // Rebuild the hidden field from the boxes; empty when nothing is written yet
    // (so the answered-count doesn't treat a blank exercise as answered).
    function sync() {
      var roughVals = boxes.map(function (b) { return b.value; });
      var finalVal = finalBox.value;
      var any = finalVal.trim() || roughVals.some(function (v) { return v.trim(); });
      hidden.value = any ? JSON.stringify({ rough: roughVals, final: finalVal }) : "";
      if (window.portalTouch) window.portalTouch("Typing…");
    }

    boxes.forEach(function (box) { box.addEventListener("input", sync); });
    finalBox.addEventListener("input", sync);

    // Carry over a legacy plain-text answer (a converted text question): drop it
    // into the first box and immediately re-save as structured JSON, so it isn't
    // lost even if she reviews it and turns it in without touching a box.
    if (legacy.trim() && boxes.length && !boxes[0].value) {
      boxes[0].value = legacy;
      sync();
    }

    if (pull) {
      pull.addEventListener("click", function () {
        // Join the rough sections into one flowing paragraph.
        var joined = boxes
          .map(function (b) { return b.value.trim(); })
          .filter(Boolean)
          .join(" ");
        if (!joined) { finalBox.focus(); return; }
        if (finalBox.value.trim() &&
            !window.confirm("Replace your final draft with your rough draft?")) {
          return;
        }
        finalBox.value = joined;
        // Fire input so sync + autosave + the spell/word helpers all catch up.
        finalBox.dispatchEvent(new Event("input", { bubbles: true }));
        finalBox.focus();
        finalBox.setSelectionRange(finalBox.value.length, finalBox.value.length);
      });
    }
  });
})();

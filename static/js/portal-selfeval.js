/* Self-evaluation widget: she rates each part of her own draft and notes how
   she would strengthen it.

   Stored as {ratings: {"0": "Excellent", …}, notes: {"0": "…", …}} — keyed by
   the component's INDEX, as a string, so the map survives a re-seed that
   rewords a component without silently re-attaching her rating to a different
   line. Same hidden-input contract as the paragraph and markup widgets. */
(function () {
  "use strict";

  Array.prototype.slice.call(
    document.querySelectorAll(".selfeval-widget")
  ).forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    if (!hidden) return;
    var items = Array.prototype.slice.call(widget.querySelectorAll(".se-item"));
    if (!items.length) return;

    var data = {};
    try {
      var parsed = JSON.parse(hidden.value || "{}");
      if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) {
        data = parsed;
      }
    } catch (e) { /* an unparseable answer hydrates as blank, never as a crash */ }
    var ratings = (data.ratings && typeof data.ratings === "object") ? data.ratings : {};
    var notes = (data.notes && typeof data.notes === "object") ? data.notes : {};

    items.forEach(function (item) {
      var key = item.getAttribute("data-index");
      var saved = ratings[key];
      if (saved) {
        Array.prototype.slice.call(
          item.querySelectorAll(".se-rating")
        ).forEach(function (radio) {
          if (radio.value === saved) radio.checked = true;
        });
      }
      var note = item.querySelector(".se-note");
      if (note && typeof notes[key] === "string") note.value = notes[key];
    });

    function sync() {
      var outRatings = {};
      var outNotes = {};
      var any = false;
      items.forEach(function (item) {
        var key = item.getAttribute("data-index");
        var picked = item.querySelector(".se-rating:checked");
        if (picked) { outRatings[key] = picked.value; any = true; }
        var note = item.querySelector(".se-note");
        if (note && note.value.trim()) { outNotes[key] = note.value; any = true; }
      });
      // Blank stays blank: an untouched form must not count toward the
      // answered tally, or the page tells her she has finished when she has not.
      hidden.value = any
        ? JSON.stringify({ ratings: outRatings, notes: outNotes })
        : "";
      if (window.portalTouch) window.portalTouch("Saving…");
    }

    widget.addEventListener("change", function (e) {
      if (e.target && e.target.classList.contains("se-rating")) sync();
    });
    widget.addEventListener("input", function (e) {
      if (e.target && e.target.classList.contains("se-note")) sync();
    });
  });
})();

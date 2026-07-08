/* Portal character boxes: one labeled box per character (like the book's
   Characters section). The child writes about each character separately; the
   boxes are serialized to {name: text} JSON in a hidden field that the autosave
   layer already saves + submits. Mirrors the markup widget's hidden-field trick.
   No external dependencies. */
(function () {
  "use strict";

  var widgets = Array.prototype.slice.call(document.querySelectorAll(".character-widget"));

  widgets.forEach(function (widget) {
    var hidden = widget.querySelector("input[type=hidden][data-question]");
    var boxes = Array.prototype.slice.call(widget.querySelectorAll(".character-box"));
    if (!hidden || !boxes.length) return;

    // Hydrate each box from the saved {name: text} map.
    var data = {};
    try { data = JSON.parse(hidden.value || "{}") || {}; } catch (e) { data = {}; }
    if (typeof data !== "object" || Array.isArray(data)) data = {};
    boxes.forEach(function (box) {
      var name = box.dataset.character;
      if (data[name] != null) box.value = data[name];
    });

    // Rebuild the hidden field from the boxes; empty when nothing is written
    // (so the answered-count doesn't treat a blank set as answered).
    function sync() {
      var obj = {};
      var any = false;
      boxes.forEach(function (box) {
        if (box.value && box.value.trim()) {
          obj[box.dataset.character] = box.value;
          any = true;
        }
      });
      hidden.value = any ? JSON.stringify(obj) : "";
      if (window.portalTouch) window.portalTouch("Typing…");
    }

    boxes.forEach(function (box) {
      box.addEventListener("input", sync);
    });
  });
})();

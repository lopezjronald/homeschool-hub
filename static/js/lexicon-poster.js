/* Tap a collected word to see what it means.
 *
 * Only words she has earned are buttons — the rest are plain text, so there is
 * nothing to tap and nothing to be disappointed by. The panel is sticky at the
 * bottom so a tap never scrolls the page away from the word she just touched.
 */
(function () {
  "use strict";
  var panel = document.getElementById("meaning");
  var wordEl = document.getElementById("meaning-word");
  var textEl = document.getElementById("meaning-text");
  if (!panel) return;

  var open = null;

  function show(btn) {
    if (open) open.classList.remove("is-open");
    if (open === btn) {           // tapping the same word again closes it
      panel.hidden = true;
      open = null;
      return;
    }
    btn.classList.add("is-open");
    wordEl.textContent = btn.dataset.word;
    textEl.textContent = btn.dataset.definition;
    panel.hidden = false;
    open = btn;
  }

  document.querySelectorAll(".lx-word.is-earned").forEach(function (btn) {
    btn.addEventListener("click", function () { show(btn); });
  });
})();

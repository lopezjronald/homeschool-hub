/* The three "what amazes you" cards.
 *
 * She writes these by hand with a stylus, so the JS here does one job: keep the
 * card's FILLED MARK honest. A tick by the label and a coloured spine down the
 * edge, so she can see at a glance which of the three are done — without a
 * character counter, which turns a reward into a quota.
 *
 * The canvas keeps her answer in a hidden input and writes to it directly,
 * which fires no event of its own; it announces `handwriting:change` instead,
 * and following that covers erasing and undoing as well as writing.
 */
(function () {
  "use strict";

  var boxes = [].slice.call(document.querySelectorAll(".lxa-box"));
  if (!boxes.length) return;

  boxes.forEach(function (box) {
    var hand = box.querySelector(".lxa-hand input[name^='answer_']");
    if (!hand) return;

    function paint() {
      box.classList.toggle("is-filled", (hand.value || "").trim().length > 0);
    }

    box.addEventListener("handwriting:change", paint);
    paint();
  });
})();

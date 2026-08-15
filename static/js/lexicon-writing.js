/* The three "what amazes you" boxes.
 *
 * Three behaviours, each for a specific reason:
 *
 *  - AUTO-GROW. She is a slow typist. A box that visibly grows with her
 *    keystrokes rewards the effort; a fixed box she is scrolling inside after
 *    one line punishes it. Never shrinks below the three lines it starts with,
 *    so the task never looks smaller than it is.
 *
 *  - THE FILLED MARK. A tick by the label and a coloured spine on the card, so
 *    she can see at a glance which of the three are done — without a character
 *    counter, which turns a reward into a quota.
 *
 *  - KEEPING THE BOX ABOVE THE KEYBOARD. On a tablet the on-screen keyboard
 *    covers the lower half of the screen and the browser does not reliably
 *    scroll the focused box clear of it. Box 3 sitting under the keyboard is a
 *    real way a child gives up.
 */
(function () {
  "use strict";

  var boxes = [].slice.call(document.querySelectorAll(".lxa-box"));
  if (!boxes.length) return;

  boxes.forEach(function (box) {
    // Handwriting boxes keep their answer in a hidden input the canvas writes
    // to; watch that instead so the tick and spine still track "has she
    // written anything".
    var hand = box.querySelector(".lxa-hand input[name^='answer_']");
    if (hand) {
      var paint = function () {
        box.classList.toggle("is-filled", (hand.value || "").trim().length > 0);
      };
      // The canvas writes the value directly, which fires no event of its own —
      // so it announces the change and we follow that, which covers erasing and
      // undoing as well as writing.
      box.addEventListener("handwriting:change", paint);
      paint();
      return;
    }

    var input = box.querySelector(".lxa-input");
    if (!input) return;

    var floor = input.offsetHeight;

    function grow() {
      input.style.height = "auto";
      input.style.height = Math.max(floor, input.scrollHeight) + "px";
    }

    function mark() {
      box.classList.toggle("is-filled", input.value.trim().length > 0);
    }

    input.addEventListener("input", function () { grow(); mark(); });

    if (!input.readOnly) {
      input.addEventListener("focus", function () {
        // Centre it now, and again once the keyboard has actually opened —
        // the viewport resize is the only reliable signal that it has.
        input.scrollIntoView({ block: "center", behavior: "smooth" });
        if (window.visualViewport) {
          var once = function () {
            input.scrollIntoView({ block: "center" });
            window.visualViewport.removeEventListener("resize", once);
          };
          window.visualViewport.addEventListener("resize", once);
        }
      });
    }

    grow();
    mark();
  });
})();

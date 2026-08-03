/* Step-through worked examples — the closest thing to a lecture she can pause.

   The parent asked for "maybe a video or a lecture," and this is the mechanism
   from the Lesson 70 page he liked: one beat per click, so a worked example
   arrives at the speed of the person reading it rather than all at once.

   Deliberately degrades: with JS off, `.lesson-stepper-step` is hidden by CSS
   but `@media print` reveals every step, so a printed lesson is complete. The
   first step is revealed on load so the block never looks empty. */
(function () {
  "use strict";

  function setup(root) {
    var steps = Array.prototype.slice.call(root.querySelectorAll(".lesson-stepper-step"));
    var next = root.querySelector("[data-stepper-next]");
    var reset = root.querySelector("[data-stepper-reset]");
    if (!steps.length || !next) return;

    var shown = 1;

    function render() {
      steps.forEach(function (li, i) {
        li.classList.toggle("is-on", i < shown);
      });
      var done = shown >= steps.length;
      next.disabled = done;
      next.textContent = done ? "That's the whole thing" : "Next step";
    }

    next.addEventListener("click", function () {
      if (shown < steps.length) {
        shown += 1;
        render();
        // Bring the step she just revealed into view — on a phone the button is
        // below the fold of the step it uncovers.
        steps[shown - 1].scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    });
    if (reset) {
      reset.addEventListener("click", function () {
        shown = 1;
        render();
        root.scrollIntoView({ block: "nearest", behavior: "smooth" });
      });
    }
    render();
  }

  if (typeof document !== "undefined") {
    document.addEventListener("DOMContentLoaded", function () {
      document.querySelectorAll(".lesson-stepper").forEach(setup);
    });
  }
})();

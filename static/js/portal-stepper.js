/* Step-through worked examples — the closest thing to a lecture she can pause.

   The parent asked for "maybe a video or a lecture," and this is the mechanism
   from the Lesson 70 page he liked: one beat per click, so a worked example
   arrives at the speed of the person reading it rather than all at once.

   Progressive enhancement, not graceful degradation: the steps are all visible
   until this script marks the container, so a reader with JS off gets the whole
   worked example rather than an equation and two dead buttons. */
(function () {
  "use strict";

  function setup(root) {
    var steps = Array.prototype.slice.call(root.querySelectorAll(".lesson-stepper-step"));
    var next = root.querySelector("[data-stepper-next]");
    var reset = root.querySelector("[data-stepper-reset]");
    if (!steps.length || !next) return;

    // Only now does the CSS start hiding steps — before this line the whole
    // worked example is on the page, which is what a reader with no JS gets.
    root.classList.add("is-stepped");
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

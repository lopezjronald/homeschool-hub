/* Animate the Discovery Method diagrams as they scroll into view (HH-201).
 *
 * The order matters here: the page must be COMPLETE without JavaScript. So the
 * stylesheet's default state is the finished diagram, and this file opts in by
 * adding `tg-anim` (which hides the pieces) and then `is-live` (which brings
 * them back). If the script never runs, or dies, the reader still gets a whole
 * diagram rather than an empty box.
 *
 * Once only. This is a reference page somebody checks mid-week, not a landing
 * page — a bar that re-wipes every time it scrolls past would be a nuisance by
 * the third visit.
 */
(function () {
  "use strict";

  var roots = document.querySelectorAll("[data-tg-animate]");
  if (!roots.length) return;

  // Somebody who asked their system for less motion gets the finished diagram
  // and no movement at all — not a slower version of the movement.
  var still = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)");
  if (still && still.matches) return;

  // IntersectionObserver is what makes "when you scroll to it" cheap. Without
  // it (very old browsers) leave the diagrams finished rather than animating
  // everything at load, which would be over before the reader arrives.
  if (!("IntersectionObserver" in window)) return;

  Array.prototype.forEach.call(roots, function (el) {
    el.classList.add("tg-anim");
  });

  // FAILSAFE. Arming hides the pieces, so anything that stops the observer from
  // firing — a browser that never composites the pane, a background tab that is
  // discarded, an observer that simply does not run — would leave the diagrams
  // permanently blank. That is worse than no animation at all, so a timer
  // reveals everything regardless after a moment. It is a no-op in the normal
  // case, because the observer has already unobserved by then.
  var FAILSAFE_MS = 2500;

  function reveal(el) {
    el.classList.add("is-live");
  }

  var seen = new WeakSet();
  var watcher = new IntersectionObserver(function (entries) {
    entries.forEach(function (entry) {
      if (!entry.isIntersecting || seen.has(entry.target)) return;
      seen.add(entry.target);
      reveal(entry.target);
      watcher.unobserve(entry.target);
    });
  }, {
    // Fire a little before the diagram is fully on screen, so the movement has
    // started by the time the reader's eye lands on it.
    rootMargin: "0px 0px -12% 0px",
    threshold: 0.2,
  });

  Array.prototype.forEach.call(roots, function (el) {
    watcher.observe(el);
  });

  window.setTimeout(function () {
    Array.prototype.forEach.call(roots, function (el) {
      if (!el.classList.contains("is-live")) reveal(el);
    });
  }, FAILSAFE_MS);
})();

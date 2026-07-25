/* Lingua reader "finish" helper (E-08). CSP-clean: external, no inline handlers.
 * Stamps elapsed seconds onto the finish form before it POSTs, so a completed read
 * logs its reading time. Degrades gracefully — if this never runs, the form still
 * submits with seconds=0 (the read still counts, just with 0 minutes). */
(function () {
  "use strict";
  document.addEventListener("DOMContentLoaded", function () {
    var form = document.getElementById("lingua-finish");
    if (!form) return;
    var secs = document.getElementById("lingua-seconds");
    var start = Date.now();
    form.addEventListener("submit", function () {
      if (secs) secs.value = String(Math.max(0, Math.round((Date.now() - start) / 1000)));
    });
  });
})();

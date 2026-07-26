/* Lingua read-along player (LGA-47, D-22).
 *
 * CSP-clean: external file, no inline handlers; config comes from the DOM (an
 * <audio> element, a <script type="application/json"> timing block, and .w spans
 * carrying data-i). A requestAnimationFrame loop (NOT timeupdate) reads
 * audio.currentTime and highlights the current word; tapping a word binary-searches
 * the flat timing array and seeks. The active-word search is a pure function exported
 * for node tests; the browser path wires up the DOM on DOMContentLoaded.
 */
(function () {
  "use strict";

  // Pure: index of the active word for time `ms`. `cursor` is a forward hint — the
  // common case (audio advancing) is O(1); backward/discontinuous jumps fall back to
  // a binary search (words are ascending in s_ms). Returns -1 before the first word.
  function activeIndex(words, ms, cursor) {
    var n = words.length;
    if (!n) return -1;
    if (typeof cursor === "number" && cursor >= 0 && cursor < n) {
      // forward fast path: current or next word still/becomes active without a rescan
      if (words[cursor].s_ms <= ms && (cursor + 1 >= n || words[cursor + 1].s_ms > ms)) {
        return cursor;
      }
      if (cursor + 1 < n && words[cursor + 1].s_ms <= ms &&
          (cursor + 2 >= n || words[cursor + 2].s_ms > ms)) {
        return cursor + 1;
      }
    }
    var lo = 0, hi = n - 1, act = -1;  // last word with s_ms <= ms
    while (lo <= hi) {
      var mid = (lo + hi) >> 1;
      if (words[mid].s_ms <= ms) { act = mid; lo = mid + 1; } else { hi = mid - 1; }
    }
    return act;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { activeIndex: activeIndex };
    return;  // node test context — don't touch the DOM
  }

  document.addEventListener("DOMContentLoaded", function () {
    var audio = document.getElementById("lingua-audio");
    var dataEl = document.getElementById("lingua-timings");
    var storyEl = document.getElementById("lingua-story");
    if (!audio || !dataEl || !storyEl) return;  // no player without all three (degrade)
    var timings;
    try { timings = JSON.parse(dataEl.textContent); } catch (e) { return; }
    var words = (timings && timings.words) || [];
    var spans = storyEl.querySelectorAll(".w");
    var cursor = -1, raf = 0, lastSpan = null;
    var TAIL_SLACK_MS = 150;  // keep a word lit briefly past its end for a smooth feel

    // Default to a gentle 0.75x for young readers; the speed <select> (if present) drives
    // it. The rAF highlighter reads audio.currentTime (the audio's own timeline in ms),
    // so word-sync holds at ANY rate. Re-apply on loadedmetadata/play — some browsers
    // reset playbackRate when the source loads.
    var speedEl = document.getElementById("lingua-speed");
    function applySpeed() {
      var r = speedEl ? parseFloat(speedEl.value) : 0.75;
      audio.playbackRate = (r > 0) ? r : 0.75;
    }
    applySpeed();
    audio.addEventListener("loadedmetadata", applySpeed);
    if (speedEl) speedEl.addEventListener("change", applySpeed);

    function clear() { if (lastSpan) { lastSpan.classList.remove("on"); lastSpan = null; } }

    function paint(ms) {
      var idx = activeIndex(words, ms, cursor);
      cursor = idx;
      var w = idx >= 0 ? words[idx] : null;
      var span = (w && ms <= w.e_ms + TAIL_SLACK_MS) ? spans[w.i] : null;
      if (span !== lastSpan) {
        if (lastSpan) lastSpan.classList.remove("on");
        if (span) span.classList.add("on");
        lastSpan = span || null;
      }
    }

    function tick() { paint(audio.currentTime * 1000); raf = requestAnimationFrame(tick); }

    audio.addEventListener("play", function () { applySpeed(); cancelAnimationFrame(raf); tick(); });
    audio.addEventListener("pause", function () { cancelAnimationFrame(raf); });
    audio.addEventListener("ended", function () { cancelAnimationFrame(raf); clear(); });

    // Tap a word -> seek to the first timing entry for that token and play.
    for (var i = 0; i < spans.length; i++) {
      spans[i].addEventListener("click", function () {
        var ti = parseInt(this.dataset.i, 10);
        for (var j = 0; j < words.length; j++) {
          if (words[j].i === ti) {
            audio.currentTime = words[j].s_ms / 1000;
            cursor = j;
            paint(words[j].s_ms);
            audio.play();
            return;
          }
        }
      });
    }
  });
})();

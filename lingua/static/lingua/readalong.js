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

  // Pure: parity class ("s0"/"s1") per word for shared-reading turns (LGA-74). A word
  // whose text ends a sentence (.!?… + optional closing quote/paren) closes the current
  // sentence, so the NEXT word flips parity. Exported for node tests.
  function sentenceParities(texts) {
    var out = [], sen = 0, END = /[.!?…][")»'”]*$/;
    for (var k = 0; k < texts.length; k++) {
      out.push(sen % 2 ? "s1" : "s0");
      if (END.test((texts[k] || "").trim())) sen++;
    }
    return out;
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { activeIndex: activeIndex, sentenceParities: sentenceParities };
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

    // Shared-reading (LGA-74): tag each word with its sentence's parity (s0/s1) so a
    // "por turnos" toggle can color alternating sentences two colors for turn-taking.
    // No effect until .shared is on. Parity is computed by the exported pure fn.
    var _texts = [];
    for (var t = 0; t < spans.length; t++) _texts.push(spans[t].textContent || "");
    var _par = sentenceParities(_texts);
    for (var p = 0; p < spans.length; p++) spans[p].classList.add(_par[p]);
    var sharedBtn = document.getElementById("lingua-shared");
    if (sharedBtn) {
      sharedBtn.addEventListener("click", function () {
        var on = storyEl.classList.toggle("shared");
        sharedBtn.setAttribute("aria-pressed", on ? "true" : "false");
      });
    }

    // Tap-a-word hint (LGA-74): a tapped cognate/false-friend word shows its meaning
    // (mobile has no hover for the title attr), auto-hiding. Positioned in page coords.
    var hintEl = document.getElementById("lingua-hint");
    var hintTimer = 0;
    function showHint(span) {
      if (!hintEl) return;
      var msg = "";
      if (span.classList.contains("false-friend")) {
        msg = span.getAttribute("title") || "¡Amigo falso! No significa lo que parece.";
      } else if (span.classList.contains("cognate")) {
        msg = "Se parece al inglés — ¡puedes adivinarlo! 👍";
      }
      if (!msg) { hintEl.hidden = true; return; }
      // Content only — position is fixed in CSS (a bottom toast). Avoid writing
      // element.style so the strict reader CSP (style-src 'self') can't block it.
      hintEl.textContent = msg;
      hintEl.hidden = false;
      clearTimeout(hintTimer);
      hintTimer = setTimeout(function () { hintEl.hidden = true; }, 4500);
    }

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

    // Voice picker (LGA-70): each voice is a separately-baked mp3 + timing set, so
    // switching reloads the page with ?voice=<id> (the server picks that voice's asset
    // and re-embeds its timings). Preserves the rest of the URL; CSP-clean (no inline
    // handler). Guard against re-navigating to the already-current voice.
    var voiceEl = document.getElementById("lingua-voice");
    if (voiceEl) {
      voiceEl.addEventListener("change", function () {
        var url = new URL(window.location.href);
        if (url.searchParams.get("voice") === voiceEl.value) return;
        url.searchParams.set("voice", voiceEl.value);
        window.location.assign(url.toString());
      });
    }

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
        showHint(this);                       // cognate/false-friend meaning on tap (LGA-74)
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

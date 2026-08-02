/**
 * Tap-to-hear for Lingua AudioClips (LGA-84 / LGA-86 / LGA-97).
 *
 * - Buttons with [data-audio-url] play that clip; a new tap interrupts the previous.
 * - [data-play-all] inside a rule card plays sibling clip buttons in order.
 * - A FAILED clip says so, visibly and to screen readers. Silence used to be the only
 *   feedback, so a child could not tell "I did it wrong" from "it's broken" — which is
 *   exactly the failure mode that makes a kid give up on a screen.
 */
(function () {
  "use strict";

  var audio = new Audio();
  var playingBtn = null;
  var queue = [];
  var queueIdx = 0;
  var live = null;
  var playToken = 0;

  function liveRegion() {
    if (live) return live;
    live = document.createElement("p");
    live.className = "lingua-clip-toast";
    live.setAttribute("role", "status");
    live.setAttribute("aria-live", "polite");
    // Stays IN the DOM, always. Toggling `hidden` in the same tick as setting the
    // text is the pattern screen readers reliably fail to announce; and appended
    // plain to the end of <body> the message rendered far below the tapped button,
    // so it was neither heard nor seen. Fixed toast: visible wherever she tapped.
    document.body.appendChild(live);
    return live;
  }

  function announce(msg) {
    var el = liveRegion();
    el.textContent = msg || "";
    el.classList.toggle("is-shown", !!msg);
  }

  function clearPlaying() {
    if (playingBtn) {
      playingBtn.classList.remove("lingua-clip-playing");
      playingBtn = null;
    }
  }

  function failed(btn) {
    clearPlaying();
    if (btn) btn.classList.add("is-audio-error");
    announce("Ese sonido no funciona ahora. 🔇");
  }

  function start(url, btn) {
    if (btn) btn.classList.remove("is-audio-error");
    announce("");
    playingBtn = btn || null;
    if (playingBtn) playingBtn.classList.add("lingua-clip-playing");
    var token = ++playToken;
    audio.src = url;
    var p = audio.play();
    if (p && typeof p.catch === "function") {
      p.catch(function () {
        // A newer tap (or the next queue item) already reassigned src, which aborts
        // this play() — that is not a failure, and flagging it red would show an
        // error for a queue that recovered fine.
        if (token !== playToken) return;
        if (queue.length && queueIdx < queue.length) next();
        else failed(btn);
      });
    }
  }

  function playUrl(url, btn) {
    if (!url) return;
    clearPlaying();
    queue = [];
    queueIdx = 0;
    audio.pause();
    start(url, btn);
  }

  function next() {
    clearPlaying();
    if (queueIdx >= queue.length) {
      queue = [];
      return;
    }
    var url = queue[queueIdx];
    var btn = queue.btns ? queue.btns[queueIdx] : null;
    queueIdx += 1;
    start(url, btn);
  }

  // ONE ended handler. There used to be both an onended property and an addEventListener
  // registration, so every clip advanced the queue twice.
  audio.addEventListener("ended", function () {
    if (queue.length) next();
    else clearPlaying();
  });

  audio.addEventListener("error", function () {
    if (!audio.src) return;         // src cleared, not a real failure
    if (queue.length && queueIdx < queue.length) {
      next();                       // skip a broken clip mid play-all
    } else {
      failed(playingBtn);
    }
  });

  document.addEventListener("click", function (ev) {
    var playAll = ev.target.closest("[data-play-all]");
    if (playAll) {
      ev.preventDefault();
      var card = playAll.closest(".portal-subject-card") || playAll.parentElement;
      var btns = card
        ? Array.prototype.slice.call(card.querySelectorAll(".lingua-clip-btn[data-audio-url]"))
        : [];
      var urls = btns.map(function (b) { return b.getAttribute("data-audio-url"); })
                     .filter(Boolean);
      if (urls.length) {
        queue = urls.slice();
        queue.btns = btns;
        queueIdx = 0;
        next();
      }
      return;
    }
    var btn = ev.target.closest(".lingua-clip-btn[data-audio-url]");
    if (!btn) return;
    ev.preventDefault();
    playUrl(btn.getAttribute("data-audio-url"), btn);
  });
})();

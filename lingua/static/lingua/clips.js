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

  function liveRegion() {
    if (live) return live;
    live = document.createElement("p");
    live.className = "lingua-clip-error";
    live.setAttribute("role", "status");
    live.setAttribute("aria-live", "polite");
    live.hidden = true;
    document.body.appendChild(live);
    return live;
  }

  function announce(msg) {
    var el = liveRegion();
    el.textContent = msg;
    el.hidden = !msg;
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
    audio.src = url;
    var p = audio.play();
    if (p && typeof p.catch === "function") {
      p.catch(function () { failed(btn); });
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

  function playQueue(urls, btns) {
    queue = urls.slice();
    queueIdx = 0;
    next();
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

/**
 * Tap-to-hear for Lingua AudioClips (LGA-84 / LGA-86).
 *
 * - Buttons with [data-audio-url] play that clip; a new tap interrupts the previous.
 * - [data-play-all] inside a rule card plays sibling clip buttons in order.
 * - Missing/failed audio is a no-op (text still readable).
 */
(function () {
  "use strict";

  var audio = new Audio();
  var playingBtn = null;
  var queue = [];
  var queueIdx = 0;

  function clearPlaying() {
    if (playingBtn) {
      playingBtn.classList.remove("active", "btn-primary");
      if (playingBtn.classList.contains("btn-outline-primary") === false &&
          playingBtn.classList.contains("lingua-clip-btn")) {
        /* restore outline style if we flipped it */
      }
      playingBtn.classList.remove("lingua-clip-playing");
      playingBtn = null;
    }
  }

  function playUrl(url, btn) {
    if (!url) return;
    clearPlaying();
    queue = [];
    queueIdx = 0;
    playingBtn = btn || null;
    if (playingBtn) playingBtn.classList.add("lingua-clip-playing");
    audio.pause();
    audio.src = url;
    var p = audio.play();
    if (p && typeof p.catch === "function") {
      p.catch(function () { clearPlaying(); });
    }
  }

  function playQueue(urls, btns) {
    queue = urls.slice();
    queueIdx = 0;
    function next() {
      clearPlaying();
      if (queueIdx >= queue.length) {
        queue = [];
        return;
      }
      var url = queue[queueIdx];
      playingBtn = (btns && btns[queueIdx]) || null;
      if (playingBtn) playingBtn.classList.add("lingua-clip-playing");
      queueIdx += 1;
      audio.src = url;
      var p = audio.play();
      if (p && typeof p.catch === "function") {
        p.catch(function () { next(); });
      }
    }
    audio.onended = function () {
      if (queue.length) next();
      else clearPlaying();
    };
    next();
  }

  audio.addEventListener("ended", function () {
    if (!queue.length) clearPlaying();
  });
  audio.addEventListener("error", function () {
    clearPlaying();
    if (queue.length && queueIdx < queue.length) {
      /* skip broken clip in a play-all queue */
      var urls = queue.slice(queueIdx);
      var btns = [];
      playQueue(urls, btns);
    }
  });

  document.addEventListener("click", function (ev) {
    var playAll = ev.target.closest("[data-play-all]");
    if (playAll) {
      ev.preventDefault();
      var card = playAll.closest(".portal-subject-card") || playAll.parentElement;
      var btns = card ? Array.prototype.slice.call(card.querySelectorAll(".lingua-clip-btn[data-audio-url]")) : [];
      var urls = btns.map(function (b) { return b.getAttribute("data-audio-url"); }).filter(Boolean);
      if (urls.length) playQueue(urls, btns);
      return;
    }
    var btn = ev.target.closest(".lingua-clip-btn[data-audio-url]");
    if (!btn) return;
    ev.preventDefault();
    playUrl(btn.getAttribute("data-audio-url"), btn);
  });
})();

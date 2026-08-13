/* Learn the pattern: tap each word, hear it, and the button fills in.
   Completion is "met every word", not "waited long enough". */
(function () {
  "use strict";
  var root = document.getElementById("learn");
  if (!root) return;

  var words = [].slice.call(root.querySelectorAll(".sp-word"));
  var doneBtn = document.getElementById("done-btn");
  var heard = Object.create(null);
  var voice = null;

  function pickVoice() {
    var all = (window.speechSynthesis && speechSynthesis.getVoices()) || [];
    voice = all.filter(function (v) { return /^en[-_]US/i.test(v.lang); })[0]
         || all.filter(function (v) { return /^en/i.test(v.lang); })[0] || null;
  }
  if (window.speechSynthesis) { pickVoice(); speechSynthesis.onvoiceschanged = pickVoice; }

  function say(text) {
    if (!window.speechSynthesis) return;
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US"; u.rate = 0.85;
    if (voice) u.voice = voice;
    speechSynthesis.speak(u);
  }

  words.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var w = btn.dataset.word;
      say(w);
      btn.classList.add("is-heard");
      heard[w] = true;
      var left = words.length - Object.keys(heard).length;
      if (left > 0) {
        doneBtn.textContent = left + " more to tap";
      } else {
        doneBtn.disabled = false;
        doneBtn.textContent = "I've met them all ➜";
      }
    });
  });

  doneBtn.addEventListener("click", function () {
    doneBtn.disabled = true;
    window.spellingPost(root.dataset.finishUrl, { kind: "learn", asked: words.length, right: words.length }).then(function () { window.location.href = root.dataset.homeUrl; })
      .catch(function () { window.location.href = root.dataset.homeUrl; });
  });
})();

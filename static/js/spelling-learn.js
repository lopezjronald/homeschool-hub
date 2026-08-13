/* Learn the pattern: tap each word, hear it, and the button fills in.
   Completion is "met every word", not "waited long enough". */
(function () {
  "use strict";
  var root = document.getElementById("learn");
  if (!root) return;

  var words = [].slice.call(root.querySelectorAll(".sp-word"));
  var doneBtn = document.getElementById("done-btn");
  var heard = Object.create(null);

  words.forEach(function (btn) {
    btn.addEventListener("click", function () {
      var w = btn.dataset.word;
      spellingSpeaker.word({ word: w, audio: btn.dataset.audio || '' });
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

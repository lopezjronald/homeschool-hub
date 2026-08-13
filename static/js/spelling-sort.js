/* Word sort: tap a word, then tap its column.
 *
 * Tap-to-place rather than drag: it works identically with a mouse, a finger
 * and a keyboard, and a drag that misses is a frustration a nine-year-old
 * doesn't need. A wrong drop bounces back and says the word again, so the
 * feedback is immediate and the word gets heard once more.
 */
(function () {
  "use strict";
  var root = document.getElementById("sort");
  if (!root) return;

  var items;
  try { items = JSON.parse(root.dataset.items || "[]"); } catch (e) { items = []; }
  if (!items.length) return;

  var pool = document.getElementById("pool");
  var buckets = [].slice.call(root.querySelectorAll(".sp-bucket"));
  var heartIndex = buckets.length - 1;      // the last column is Heart Words
  var selected = null, placed = 0, tries = 0, wrong = 0;


  // Shuffle so the answer isn't the printed order. Fisher-Yates.
  for (var s = items.length - 1; s > 0; s--) {
    var j = Math.floor(Math.random() * (s + 1));
    var t = items[s]; items[s] = items[j]; items[j] = t;
  }

  items.forEach(function (item) {
    var btn = document.createElement("button");
    btn.type = "button";
    btn.className = "sp-chip";
    btn.textContent = item.word;
    btn.dataset.target = item.heart ? heartIndex : item.bucket;
    btn.dataset.audio = item.audio || "";
    btn.addEventListener("click", function () {
      if (selected) selected.classList.remove("is-picked");
      selected = (selected === btn) ? null : btn;
      if (selected) {
        selected.classList.add("is-picked");
        spellingSpeaker.word(item);
      }
    });
    pool.appendChild(btn);
  });

  buckets.forEach(function (bucket, index) {
    bucket.addEventListener("click", function () {
      if (!selected) return;
      tries += 1;
      if (parseInt(selected.dataset.target, 10) === index) {
        selected.classList.remove("is-picked");
        selected.disabled = true;
        selected.classList.add("is-placed");
        bucket.querySelector(".sp-bucket-body").appendChild(selected);
        bucket.classList.add("is-hit");
        setTimeout(function () { bucket.classList.remove("is-hit"); }, 350);
        selected = null;
        placed += 1;
        if (placed === items.length) finish();
      } else {
        wrong += 1;
        spellingSpeaker.word({ word: selected.textContent,
                               audio: selected.dataset.audio || '' });
        selected.classList.add("is-bounce");
        var chip = selected;
        setTimeout(function () { chip.classList.remove("is-bounce"); }, 400);
      }
    });
  });

  function finish() {
    document.getElementById("sort-score").textContent =
      items.length + " sorted" + (wrong ? " · " + wrong + " to look at again" : " · no mistakes!");
    document.getElementById("sort-done").hidden = false;
    window.spellingPost(root.dataset.finishUrl, { kind: "sort", asked: items.length, right: items.length - wrong }).catch(function () {});
  }
})();

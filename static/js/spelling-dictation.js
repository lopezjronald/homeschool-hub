/* Sentence dictation: hear a whole sentence, write it out.
 *
 * Scored on the target word's spelling plus the two mechanics the lesson cares
 * about — a capital at the start and an end mark. Not on comma placement or
 * exact wording, because this is a SPELLING exercise and marking her down for
 * grammar she hasn't been taught teaches her that writing is a trap.
 */
(function () {
  "use strict";
  var root = document.getElementById("dictation");
  if (!root) return;

  var items;
  try { items = JSON.parse(root.dataset.items || "[]"); } catch (e) { items = []; }
  if (!items.length) return;

  var el = function (id) { return document.getElementById(id); };
  var i = 0, right = 0, awaitingFix = false;
  var voice = null;

  function pickVoice() {
    var all = (window.speechSynthesis && speechSynthesis.getVoices()) || [];
    voice = all.filter(function (v) { return /^en[-_]US/i.test(v.lang); })[0]
         || all.filter(function (v) { return /^en/i.test(v.lang); })[0] || null;
  }
  if (window.speechSynthesis) { pickVoice(); speechSynthesis.onvoiceschanged = pickVoice; }
  function say(text, rate) {
    if (!window.speechSynthesis) return;
    speechSynthesis.cancel();
    var u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US"; u.rate = rate || 1.0;
    if (voice) u.voice = voice;
    speechSynthesis.speak(u);
  }

  function check(typed, item) {
    var problems = [];
    var clean = typed.trim();
    if (!clean) return ["Nothing written yet."];
    if (clean[0] !== clean[0].toUpperCase()) problems.push("start with a capital letter");
    if (".?!".indexOf(clean[clean.length - 1]) === -1) problems.push("end with . ? or !");
    var words = clean.toLowerCase().replace(/[.,!?;:]/g, "").split(/\s+/);
    if (words.indexOf(item.word.toLowerCase()) === -1) {
      problems.push("spell “" + item.word + "” correctly");
    }
    return problems;
  }

  function show() {
    var item = items[i];
    el("d-at").textContent = i + 1;
    el("d-typed").value = "";
    el("d-feedback").hidden = true;
    el("d-fixbox").hidden = true;
    el("d-next").hidden = true;
    el("d-form").hidden = false;
    awaitingFix = false;
    say(item.sentence);
    el("d-typed").focus();
  }

  el("d-total").textContent = items.length;

  el("d-start").addEventListener("click", function () {
    el("d-gate").hidden = true;
    el("d-play").hidden = false;
    show();
  });

  el("d-say").addEventListener("click", function () { say(items[i].sentence); });

  el("d-form").addEventListener("submit", function (e) {
    e.preventDefault();
    var item = items[i];
    var problems = check(el("d-typed").value, item);
    el("d-form").hidden = true;
    el("d-feedback").hidden = false;
    el("d-right").textContent = item.sentence;

    if (!problems.length) {
      right += 1;
      el("d-verdict").textContent = "✅ Yes!";
      el("d-verdict").className = "sp-verdict is-right";
      el("d-next").hidden = false;
      el("d-next").focus();
    } else {
      el("d-verdict").textContent = "Almost — " + problems.join(", ") + ".";
      el("d-verdict").className = "sp-verdict is-wrong";
      el("d-fixbox").hidden = false;
      awaitingFix = true;
      el("d-fix").value = "";
      el("d-fix").focus();
      say(item.sentence);
    }
  });

  el("d-fix").addEventListener("input", function () {
    if (!awaitingFix) return;
    if (!check(el("d-fix").value, items[i]).length) {
      awaitingFix = false;
      el("d-next").hidden = false;
      el("d-next").focus();
    }
  });

  el("d-next").addEventListener("click", function () {
    i += 1;
    if (i >= items.length) {
      el("d-play").hidden = true;
      el("d-score").textContent = right + " out of " + items.length + " first try";
      el("d-done").hidden = false;
      window.spellingPost(root.dataset.finishUrl, { kind: "dictation", asked: items.length, right: right }).catch(function () {});
    } else {
      show();
    }
  });
})();

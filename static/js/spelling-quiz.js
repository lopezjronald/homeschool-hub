/* Hear-and-type spelling quiz.
 *
 * The corrective loop is the point: a missed word is shown against what she
 * typed and she must type it correctly before moving on. That immediate
 * correction is what separates this from a Friday test, so it is not skippable
 * — and the MISS is what gets recorded, not the retype, or the box would go up
 * for a word she got wrong.
 *
 * Speech uses the browser's own voice. iOS will not speak until the page has
 * had a real tap, hence the start gate.
 */
(function () {
  "use strict";
  var root = document.getElementById("quiz");
  if (!root) return;

  var items;
  try { items = JSON.parse(root.dataset.items || "[]"); } catch (e) { items = []; }
  if (!items.length) return;

  var el = function (id) { return document.getElementById(id); };
  var i = 0, right = 0, missed = [], mastered = 0, awaitingFix = false;

  /* ---- speech ------------------------------------------------------- */
  var voice = null;
  function pickVoice() {
    var all = (window.speechSynthesis && speechSynthesis.getVoices()) || [];
    voice = all.filter(function (v) { return /^en[-_]US/i.test(v.lang); })[0]
         || all.filter(function (v) { return /^en/i.test(v.lang); })[0]
         || null;
  }
  if (window.speechSynthesis) {
    pickVoice();
    speechSynthesis.onvoiceschanged = pickVoice;
  }
  function say(text, rate, then) {
    if (!window.speechSynthesis) { if (then) then(); return; }
    var u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    u.rate = rate;
    if (voice) u.voice = voice;
    if (then) u.onend = then;
    speechSynthesis.speak(u);
  }
  function sayItem(item) {
    // Word, then the sentence for context, then the word again — the way a
    // teacher dictates, so she hears it in use and not just in isolation.
    speechSynthesis.cancel();
    say(item.word, 0.85, function () {
      say(item.sentence, 1.0, function () { say(item.word, 0.85); });
    });
  }

  /* ---- plumbing ------------------------------------------------------ */
  function post(url, body) {
    // A lost answer is worse than a visible error: she would be scored on
    // screen and have nothing recorded. Surface it instead of swallowing it.
    return window.spellingPost(url, body).catch(function () {
      var warn = document.getElementById("savewarn");
      if (warn) warn.hidden = false;
      return null;
    });
  }

  function progress() {
    el("at").textContent = Math.min(i + 1, items.length);
    el("bar").style.width = (i / items.length * 100) + "%";
  }

  function show(item) {
    progress();
    el("typed").value = "";
    el("feedback").hidden = true;
    el("compare").hidden = true;
    el("fixbox").hidden = true;
    el("fixhint").hidden = true;
    el("next").hidden = true;
    el("form").hidden = false;
    el("heart").hidden = !item.heart;
    if (item.heart) el("tricky").textContent = item.tricky || "watch this one";
    awaitingFix = false;
    sayItem(item);
    el("typed").focus();
  }

  function finishUp() {
    el("play").hidden = true;
    el("bar").style.width = "100%";
    el("score").textContent = right + " out of " + items.length;
    el("moved").textContent = mastered
      ? mastered + " word" + (mastered === 1 ? "" : "s") + " mastered! 🌟" : "";
    el("done").hidden = false;
    post(root.dataset.finishUrl, {
      kind: "quiz", asked: items.length, right: right, missed: missed
    });
  }

  function advance() {
    i += 1;
    if (i >= items.length) finishUp(); else show(items[i]);
  }

  /* ---- the loop ------------------------------------------------------ */
  el("start").addEventListener("click", function () {
    el("gate").hidden = true;
    el("play").hidden = false;
    show(items[0]);
  });

  el("say").addEventListener("click", function () { sayItem(items[i]); });

  el("form").addEventListener("submit", function (e) {
    e.preventDefault();
    var item = items[i];
    var typed = el("typed").value.trim();
    if (!typed) return;
    var ok = typed.toLowerCase() === item.word.toLowerCase();

    if (ok) right += 1; else missed.push(item.word);
    post(root.dataset.answerUrl, { card: item.card, correct: ok })
      .then(function (res) { if (res && res.mastered) mastered += 1; });

    el("form").hidden = true;
    el("feedback").hidden = false;
    el("verdict").textContent = ok ? "✅ Yes!" : "Almost —";
    el("verdict").className = "sp-verdict " + (ok ? "is-right" : "is-wrong");

    if (ok) {
      el("next").hidden = false;
      el("next").focus();
    } else {
      // Show hers against the real spelling, then make her write it right.
      el("yours").innerHTML = diff(typed, item.word);
      el("right").textContent = item.word;
      el("compare").hidden = false;
      el("fixbox").hidden = false;
      awaitingFix = true;
      el("fix").value = "";
      el("fix").focus();
      say(item.word, 0.8);
    }
  });

  el("fix").addEventListener("input", function () {
    if (!awaitingFix) return;
    var item = items[i];
    if (el("fix").value.trim().toLowerCase() === item.word.toLowerCase()) {
      awaitingFix = false;
      el("fixhint").hidden = true;
      el("fix").disabled = true;
      el("next").hidden = false;
      el("next").focus();
    }
  });

  el("fix").addEventListener("blur", function () {
    if (awaitingFix && el("fix").value.trim()) el("fixhint").hidden = false;
  });

  el("next").addEventListener("click", function () {
    el("fix").disabled = false;
    advance();
  });

  /* Mark the letters that differ, so the correction is visible rather than
     something she has to spot herself. */
  function diff(typed, word) {
    var out = "", n = Math.max(typed.length, word.length);
    for (var k = 0; k < n; k++) {
      var c = typed[k];
      if (c === undefined) { out += '<span class="sp-miss">_</span>'; continue; }
      var same = word[k] && c.toLowerCase() === word[k].toLowerCase();
      out += same ? escapeHtml(c) : '<span class="sp-miss">' + escapeHtml(c) + "</span>";
    }
    return out;
  }
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (m) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[m];
    });
  }

  el("total").textContent = items.length;
  progress();
})();

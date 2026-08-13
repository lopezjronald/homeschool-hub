/* Saying things out loud, for every spelling activity.
 *
 * Prefers BAKED audio (Polly, synthesized at authoring time) and falls back to
 * the browser's own speechSynthesis voice when a word hasn't been baked yet.
 * The device voice is whatever the machine ships — on Windows a flat robotic
 * reader — and a child being asked to spell a word she has only heard needs it
 * pronounced clearly and identically every time. A wobbly voice makes the task
 * harder in a way that has nothing to do with spelling.
 *
 * Both paths are behind one call so the activities don't each grow their own
 * copy of the fallback logic.
 */
window.spellingSpeaker = (function () {
  "use strict";

  var voice = null;
  var current = null;         // the <audio> in flight, so a replay can cut it off

  function pickVoice() {
    var all = (window.speechSynthesis && speechSynthesis.getVoices()) || [];
    // Prefer a natural-sounding local voice over the default robot where the
    // device offers one.
    var en = all.filter(function (v) { return /^en[-_]US/i.test(v.lang); });
    var nice = en.filter(function (v) {
      return /natural|neural|premium|enhanced|zira|aria|jenny|samantha/i.test(v.name);
    });
    voice = nice[0] || en[0]
         || all.filter(function (v) { return /^en/i.test(v.lang); })[0] || null;
  }
  if (window.speechSynthesis) {
    pickVoice();
    speechSynthesis.onvoiceschanged = pickVoice;
  }

  function stop() {
    if (current) { try { current.pause(); } catch (e) {} current = null; }
    if (window.speechSynthesis) speechSynthesis.cancel();
  }

  function speakBrowser(text, rate, then) {
    if (!window.speechSynthesis) { if (then) then(); return; }
    var u = new SpeechSynthesisUtterance(text);
    u.lang = "en-US";
    u.rate = rate;
    if (voice) u.voice = voice;
    if (then) u.onend = then;
    speechSynthesis.speak(u);
  }

  /* Say `text`. If `url` is a baked clip, play that instead.
     `rate` only applies to the fallback — baked clips carry their own pacing. */
  function say(text, url, rate, then) {
    if (!url) { speakBrowser(text, rate, then); return; }
    var audio = new Audio(url);
    current = audio;
    var moved = false;
    var next = function () {
      if (moved) return;
      moved = true;
      if (current === audio) current = null;
      if (then) then();
    };
    audio.addEventListener("ended", next);
    // A dead URL or a blocked play must not strand her on a silent screen —
    // drop back to the device voice rather than doing nothing.
    audio.addEventListener("error", function () {
      if (moved) return;
      moved = true;
      if (current === audio) current = null;
      speakBrowser(text, rate, then);
    });
    var played = audio.play();
    if (played && played.catch) {
      played.catch(function () {
        if (moved) return;
        moved = true;
        if (current === audio) current = null;
        speakBrowser(text, rate, then);
      });
    }
  }

  return {
    stop: stop,
    say: say,
    /* Word → sentence → word again, the way a teacher dictates: she hears the
       word, hears it used so she knows WHICH word, then hears it once more to
       spell. */
    dictate: function (item) {
      stop();
      say(item.word, item.audio, 0.85, function () {
        say(item.sentence, item.sentence_audio, 1.0, function () {
          say(item.word, item.audio, 0.85);
        });
      });
    },
    word: function (item) {
      stop();
      say(item.word, item.audio, 0.85);
    },
    sentence: function (item) {
      stop();
      say(item.sentence, item.sentence_audio, 1.0);
    }
  };
})();

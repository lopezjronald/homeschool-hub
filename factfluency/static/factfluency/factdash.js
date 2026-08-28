/* Fact Dash — the speed-round engine (HH-203).
 *
 * The client checks answers locally so the tick appears the instant she
 * finishes typing, with no round trip. The SERVER re-marks every attempt, so
 * the local check is a UI nicety and never the record of what happened.
 *
 * There is no visible clock. Response time is measured per question and never
 * shown, because a countdown ticking down is the thing that makes a nine-year-
 * old freeze — not the measuring.
 */
(function () {
  "use strict";

  var root = document.querySelector(".fd-play");
  if (!root) return;

  var csrf = root.dataset.csrf;
  var screens = {};
  root.querySelectorAll("[data-screen]").forEach(function (el) {
    screens[el.dataset.screen] = el;
  });

  var els = {
    prompt: root.querySelector("[data-prompt]"),
    answer: root.querySelector("[data-answer]"),
    mark: root.querySelector("[data-mark]"),
    tip: root.querySelector("[data-tip]"),
    qnow: root.querySelector("[data-qnow]"),
    qtotal: root.querySelector("[data-qtotal]"),
    track: root.querySelector("[data-progress-track]"),
    progress: root.querySelector("[data-progress]"),
    tally: root.querySelector("[data-tally]"),
    beaten: root.querySelector("[data-beaten]"),
    doneTitle: root.querySelector("[data-done-title]"),
    mastery: root.querySelector("[data-mastery]"),
    masteryFill: root.querySelector("[data-mastery-fill]"),
    masteryLabel: root.querySelector("[data-mastery-label]"),
    again: root.querySelector('[data-action="again"]'),
  };

  var state = {
    sessionId: null,
    questions: [],
    index: 0,
    typed: "",
    askedAt: 0,
    answeredAt: 0,
    locked: false,
    pending: [],
    correct: 0,
    streak: 0,
    bestStreak: 0,
  };

  // ---- plumbing -----------------------------------------------------------

  function show(name) {
    Object.keys(screens).forEach(function (key) {
      screens[key].hidden = key !== name;
    });
    // Drives the mid-round chrome collapse in CSS. Without it the Done key sits
    // below the fold on a phone.
    root.classList.toggle("is-playing", name === "round");
  }

  function post(url, body) {
    return fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": csrf },
      body: JSON.stringify(body || {}),
      credentials: "same-origin",
    }).then(function (r) {
      if (!r.ok) throw new Error("HTTP " + r.status);
      return r.json();
    });
  }

  function sessionUrl(template) {
    // The template was reversed with session_id=0; swap in the real one.
    return template.replace(/\/0\//, "/" + state.sessionId + "/");
  }

  function uuid() {
    if (window.crypto && window.crypto.randomUUID) return window.crypto.randomUUID();
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, function (c) {
      var r = (Math.random() * 16) | 0;
      return (c === "x" ? r : (r & 0x3) | 0x8).toString(16);
    });
  }

  // Attempts that failed to send wait here rather than being lost, so a flaky
  // moment mid-round costs nothing. Deduped server-side on client_uuid.
  var QUEUE_KEY = "factdash:queue";

  function readQueue() {
    try { return JSON.parse(localStorage.getItem(QUEUE_KEY) || "[]"); }
    catch (e) { return []; }
  }

  function writeQueue(rows) {
    try { localStorage.setItem(QUEUE_KEY, JSON.stringify(rows.slice(-200))); }
    catch (e) { /* private mode, or full — the round still plays */ }
  }

  function flush(attempts) {
    var queued = readQueue().concat(attempts || []);
    if (!queued.length) return Promise.resolve({});
    var mine = queued.filter(function (row) { return row.session_id === state.sessionId; });
    var theirs = queued.filter(function (row) { return row.session_id !== state.sessionId; });
    if (!mine.length) { writeQueue(theirs); return Promise.resolve({}); }
    return post(sessionUrl(root.dataset.attemptsUrl), {
      attempts: mine.map(function (row) {
        var copy = Object.assign({}, row);
        delete copy.session_id;
        return copy;
      }),
    }).then(function (data) {
      writeQueue(theirs);
      return data;
    }).catch(function () {
      writeQueue(queued);          // keep them; try again at the end of the round
      return {};
    });
  }

  // ---- the round ----------------------------------------------------------

  function start() {
    show("round");
    els.mark.textContent = "";
    post(root.dataset.startUrl).then(function (data) {
      state.sessionId = data.session_id;
      state.questions = data.questions || [];
      state.index = 0;
      state.correct = 0;
      state.streak = 0;
      state.bestStreak = 0;
      state.pending = [];
      els.qtotal.textContent = String(state.questions.length);
      // Notch the bar into one segment per question, so it reads as countable
      // progress rather than as a timer draining.
      els.track.style.setProperty("--steps", String(state.questions.length || 1));
      if (!state.questions.length) {
        finish();
        return;
      }
      ask();
      els.prompt.focus();
    }).catch(function (err) {
      // Do NOT swallow this as "check the wifi" — a broken selector throws in
      // here too, and a fetch failure and a coding mistake need different
      // reactions from whoever is looking at it.
      show("start");
      els.mark.textContent = "";
      console.error("Fact Dash could not start a round:", err);
      alert("Couldn't start that round. Try again in a moment.");
    });
  }

  function ask() {
    var q = state.questions[state.index];
    state.typed = "";
    state.answeredAt = 0;
    state.locked = false;
    els.prompt.textContent = q.prompt;
    els.answer.textContent = " ";
    els.answer.className = "fd-answer";
    els.mark.textContent = "";
    els.mark.className = "fd-mark";
    els.tip.hidden = true;
    els.tip.textContent = "";
    els.qnow.textContent = String(state.index + 1);
    var pct = Math.round((state.index / state.questions.length) * 100);
    els.progress.style.width = pct + "%";
    els.track.setAttribute("aria-valuenow", String(pct));
    state.askedAt = performance.now();
  }

  function type(ch) {
    if (state.locked) return;
    if (ch === "enter") {
      if (state.typed) submit();
      return;
    }
    if (ch === "del") {
      state.typed = state.typed.slice(0, -1);
    } else if (state.typed.length < 3) {
      state.typed += ch;
    }
    els.answer.textContent = state.typed || " ";

    // NOTHING auto-submits. A mis-tap used to commit an answer she could not
    // take back, and on a two-digit answer the first digit alone could end the
    // question. She types, looks at it, then confirms.
    //
    // But the clock stops HERE, at the last digit — not at Enter. Confirming is
    // not part of remembering 6x8, and counting it would quietly make every
    // fact look half a second slower than it is, against a 3000ms threshold.
    if (state.typed) state.answeredAt = performance.now();
  }

  function submit() {
    if (state.locked || !state.typed) return;
    state.locked = true;
    var q = state.questions[state.index];
    var stopped = state.answeredAt || performance.now();
    var elapsed = Math.round(stopped - state.askedAt);
    var given = parseInt(state.typed, 10);
    var right = given === q.answer;
    if (right) {
      state.correct += 1;
      state.streak += 1;
      state.bestStreak = Math.max(state.bestStreak, state.streak);
    } else {
      state.streak = 0;
    }

    // On a miss, say the whole sentence. Two bare numbers stacked — her wrong
    // one above the right one — reads as "5 4", or as a score.
    els.mark.textContent = right ? "✓" : q.prompt + " = " + q.answer;
    els.mark.className = "fd-mark " + (right ? "is-right" : "is-wrong");
    if (!right) {
      els.answer.className = "fd-answer is-wrong";
      // The strategy, at the only moment it teaches anything: she has just
      // discovered she does not know this one.
      if (q.hint) { els.tip.textContent = q.hint; els.tip.hidden = false; }
    }

    state.pending.push({
      session_id: state.sessionId,
      client_uuid: uuid(),
      fact_id: q.fact_id,
      operation: q.operation,
      answer_given: given,
      response_ms: elapsed,
    });

    // Send in small batches so a long round is not one all-or-nothing post.
    if (state.pending.length >= 5) {
      var batch = state.pending.splice(0, state.pending.length);
      flush(batch);
    }

    window.setTimeout(function () {
      state.index += 1;
      if (state.index >= state.questions.length) finish();
      else ask();
    }, right ? 260 : 2600);        // long enough on a miss to read the strategy
  }

  function finish() {
    els.progress.style.width = "100%";
    els.track.setAttribute("aria-valuenow", "100");
    var batch = state.pending.splice(0, state.pending.length);
    flush(batch).then(function () {
      return post(sessionUrl(root.dataset.finishUrl));
    }).then(render).catch(function () {
      // Even if the server never answered, she still played a round.
      render({ num_correct: state.correct, num_attempted: state.questions.length,
               records_beaten: [], offline: true });
    });
  }

  function render(out) {
    show("done");
    var beaten = out.records_beaten || [];
    var attempted = out.num_attempted || 0;
    var clean = attempted > 0 && out.num_correct === attempted;

    els.doneTitle.textContent =
      out.level_beaten ? "Level complete! 🏆"
      : beaten.length ? "New record! ⭐"
      : clean ? "Every single one! 🎉"
      : "Nice work!";

    // The tally stands ALONE. It used to be glued to the mastery percentage
    // with a middot — "10 right out of 12 · 0% of this level nailed" — which
    // reads as "you got nothing" on the one screen that decides whether she
    // plays again. Mastery needs repeated fast recall, so it sits at 0 for days.
    els.tally.textContent = out.num_correct + " right out of " + attempted;

    els.beaten.innerHTML = "";
    // A streak the round always earns, so the reward list is not empty on the
    // ~6 days out of 7 when nothing is a personal best.
    var streak = out.longest_streak !== undefined ? out.longest_streak : state.bestStreak;
    if (streak >= 2) addChip("🔥 " + streak + " in a row");
    beaten.forEach(function (rec) { addChip(rec.label); });
    if (out.offline) addChip("Saved on this device — it'll sync next time.");

    // Only once there is something to show. "0 of 20 mastered" on day one is
    // just a zero with more words.
    var mastered = out.mastered || 0;
    if (mastered > 0 && out.total) {
      els.mastery.hidden = false;
      els.masteryFill.style.width = (out.pct || 0) + "%";
      els.masteryLabel.textContent =
        mastered + " of " + out.total + " facts mastered";
    } else {
      els.mastery.hidden = true;
    }

    // A clean round earns confetti on its own merit. Gating the entire reward
    // behind a personal best fired it maybe once a week.
    if (beaten.length || out.level_beaten || clean) celebrate();
    if (els.again) els.again.focus();
  }

  function addChip(text) {
    var li = document.createElement("li");
    li.textContent = text;
    els.beaten.appendChild(li);
  }

  // ---- celebration --------------------------------------------------------

  function celebrate() {
    var still = window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (still) return;
    var host = document.createElement("div");
    host.className = "fd-confetti";
    for (var i = 0; i < 24; i++) {
      var bit = document.createElement("i");
      bit.style.left = Math.random() * 100 + "%";
      bit.style.animationDelay = (Math.random() * 0.3).toFixed(2) + "s";
      bit.style.setProperty("--drift", (Math.random() * 80 - 40).toFixed(0) + "px");
      host.appendChild(bit);
    }
    document.body.appendChild(host);
    window.setTimeout(function () { host.remove(); }, 2200);
  }

  // ---- input --------------------------------------------------------------

  root.addEventListener("click", function (e) {
    var key = e.target.closest("[data-key]");
    if (key) { type(key.dataset.key); return; }
    var action = e.target.closest("[data-action]");
    if (!action) return;
    if (action.dataset.action === "start" || action.dataset.action === "again") start();
  });

  document.addEventListener("keydown", function (e) {
    if (screens.round.hidden) return;
    if (e.key >= "0" && e.key <= "9") { type(e.key); e.preventDefault(); }
    else if (e.key === "Backspace") { type("del"); e.preventDefault(); }
    else if (e.key === "Enter") {
      // If she has tabbed onto a keypad button, Enter belongs to that button —
      // it should type the 7, not commit the answer. Swallowing it here meant
      // Enter on a focused "7" submitted whatever was already in the box.
      if (document.activeElement && document.activeElement.closest("[data-key]")) return;
      type("enter");
      e.preventDefault();
    }
  });
})();

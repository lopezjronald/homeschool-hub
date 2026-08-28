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
    qnow: root.querySelector("[data-qnow]"),
    qtotal: root.querySelector("[data-qtotal]"),
    progress: root.querySelector("[data-progress]"),
    tally: root.querySelector("[data-tally]"),
    beaten: root.querySelector("[data-beaten]"),
    doneTitle: root.querySelector("[data-done-title]"),
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
  };

  // ---- plumbing -----------------------------------------------------------

  function show(name) {
    Object.keys(screens).forEach(function (key) {
      screens[key].hidden = key !== name;
    });
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
      state.pending = [];
      els.qtotal.textContent = String(state.questions.length);
      if (!state.questions.length) {
        finish();
        return;
      }
      ask();
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
    els.answer.textContent = " ";
    els.mark.textContent = "";
    els.mark.className = "fd-mark";
    els.qnow.textContent = String(state.index + 1);
    els.progress.style.width =
      Math.round((state.index / state.questions.length) * 100) + "%";
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
    if (right) state.correct += 1;

    els.mark.textContent = right ? "✓" : String(q.answer);
    els.mark.className = "fd-mark " + (right ? "is-right" : "is-wrong");

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
    }, right ? 260 : 900);         // a beat longer on a miss, to read the answer
  }

  function finish() {
    els.progress.style.width = "100%";
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
    els.doneTitle.textContent =
      out.level_beaten ? "Level complete! 🏆"
      : beaten.length ? "New record! ⭐"
      : "Nice work!";
    els.tally.textContent =
      out.num_correct + " right out of " + out.num_attempted +
      (out.pct !== undefined ? " · " + out.pct + "% of this level nailed" : "");
    els.beaten.innerHTML = "";
    beaten.forEach(function (rec) {
      var li = document.createElement("li");
      li.textContent = rec.label;
      els.beaten.appendChild(li);
    });
    if (out.offline) {
      var li = document.createElement("li");
      li.textContent = "Saved on this device — it'll sync next time.";
      els.beaten.appendChild(li);
    }
    if (beaten.length || out.level_beaten) celebrate();
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
    else if (e.key === "Enter") { type("enter"); e.preventDefault(); }
  });
})();

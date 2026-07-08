/* Portal autosave: saves the child's answers 3 seconds after they stop typing.
   Also saves on blur and (via sendBeacon) when leaving the page. Shows a
   friendly status + live word counts. No external dependencies. */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  if (!form || form.dataset.submitted === "1") return;

  var url = form.dataset.autosaveUrl;
  var csrf = form.querySelector("input[name=csrfmiddlewaretoken]");
  var statusEl = document.getElementById("save-status");
  var progressEl = document.getElementById("answered-progress");
  var areas = Array.prototype.slice.call(form.querySelectorAll("textarea[data-question]"));

  var IDLE_MS = 3000; // save 3s after the child stops typing
  var timer = null;
  var dirty = false;
  var saving = false;
  var submitting = false; // set on real submit — stops blur/beacon racing the POST

  function setStatus(text, cls) {
    if (!statusEl) return;
    statusEl.textContent = text;
    statusEl.className = "portal-save-status " + (cls || "");
  }

  function collect() {
    var answers = {};
    areas.forEach(function (t) { answers[t.dataset.question] = t.value; });
    return answers;
  }

  function wordCount(text) {
    var words = text.trim().split(/\s+/).filter(Boolean);
    return words.length;
  }

  function refreshCounts() {
    var answered = 0;
    areas.forEach(function (t) {
      var el = document.querySelector('[data-count-for="' + t.dataset.question + '"]');
      var n = wordCount(t.value);
      if (el) el.textContent = n ? n + (n === 1 ? " word" : " words") : "";
      if (t.value.trim()) answered += 1;
    });
    if (progressEl) {
      progressEl.textContent = answered + " of " + progressEl.dataset.total + " answered";
    }
  }

  function save() {
    if (saving) return;
    saving = true;
    dirty = false; // typing during the request re-marks it dirty
    setStatus("Saving…", "is-saving");
    fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrf ? csrf.value : "",
      },
      body: JSON.stringify({ answers: collect() }),
      credentials: "same-origin",
    })
      .then(function (resp) {
        saving = false;
        if (resp.status === 409) {   // already turned in (e.g. another tab)
          lockAsSubmitted();
          return null;
        }
        if (!resp.ok) {              // terminal client error — do NOT hot-loop
          dirty = true;
          setStatus("Couldn't save — please tell your teacher", "is-error");
          return null;
        }
        return resp.json();
      })
      .then(function (data) {
        if (!data) return;
        if (data.ok) {
          setStatus("Saved ✓ " + data.saved_at, "is-saved");
        } else {
          dirty = true;
          setStatus("Couldn't save — check your connection", "is-error");
        }
        // Anything typed while the request was in flight gets its own save.
        if (dirty && !submitting) { clearTimeout(timer); timer = setTimeout(save, 800); }
      })
      .catch(function () {           // network error only — retry gently
        saving = false;
        dirty = true;
        setStatus("Couldn't save — check your connection", "is-error");
        if (!submitting) { clearTimeout(timer); timer = setTimeout(save, 5000); }
      });
  }

  function lockAsSubmitted() {
    submitting = true; // stops further saves, blur saves, and the beacon
    clearTimeout(timer);
    setStatus("Already turned in ✓", "is-saved");
    areas.forEach(function (t) { t.readOnly = true; });
  }

  areas.forEach(function (t) {
    t.addEventListener("input", function () {
      if (submitting) return;
      dirty = true;
      setStatus("Typing…", "");
      refreshCounts();
      clearTimeout(timer);
      timer = setTimeout(save, IDLE_MS);
    });
    t.addEventListener("blur", function () {
      if (dirty && !submitting) { clearTimeout(timer); save(); }
    });
  });

  // Last-chance save when the page is closed or backgrounded.
  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "hidden" && dirty && !submitting && navigator.sendBeacon) {
      var payload = new Blob([JSON.stringify({ answers: collect() })], { type: "application/json" });
      navigator.sendBeacon(url, payload);
      dirty = false;
    }
  });

  // On real submit: stop autosaving and lock the button so a slow connection
  // can't be double-clicked into two submissions.
  form.addEventListener("submit", function () {
    submitting = true;
    clearTimeout(timer);
    var btn = form.querySelector("button[type=submit]");
    if (btn) { btn.disabled = true; btn.textContent = "Turning it in…"; }
  });

  refreshCounts();
})();

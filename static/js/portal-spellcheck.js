/* Our own spell-checker for the writing boxes.

   The browser's native red squiggle depends on a device setting we can't
   control (and never offers fixes), so we draw our own: a backdrop div mirrors
   the textarea's text with a red wavy underline under misspelled words, and a
   little bar under the box offers one-tap corrections. Detection is AI-backed
   (see tutor.ai.check_spelling) so it catches phonetic kid spellings. Runs only
   when the form exposes a spellcheck URL (i.e. NOT on spelling curricula). */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  if (!form || form.dataset.submitted === "1") return;
  var url = form.dataset.spellcheckUrl;
  if (!url) return;

  var MIRROR = ["fontFamily", "fontSize", "fontWeight", "fontStyle", "fontVariant",
    "letterSpacing", "wordSpacing", "lineHeight", "textTransform", "textIndent",
    "paddingTop", "paddingRight", "paddingBottom", "paddingLeft",
    "borderTopWidth", "borderRightWidth", "borderBottomWidth", "borderLeftWidth",
    "boxSizing", "tabSize"];

  function esc(s) {
    return s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }
  function reEscape(s) { return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }

  Array.prototype.slice.call(document.querySelectorAll("textarea.portal-answer")).forEach(function (area) {
    if (area.readOnly) return;
    area.spellcheck = false;  // we draw our own squiggle; the native one is unreliable

    var bg = getComputedStyle(area).backgroundColor;

    // Wrap the textarea so a backdrop can sit exactly behind it.
    var wrap = document.createElement("div");
    wrap.className = "spellwrap";
    area.parentNode.insertBefore(wrap, area);
    var backdrop = document.createElement("div");
    backdrop.className = "spell-backdrop";
    backdrop.setAttribute("aria-hidden", "true");
    wrap.appendChild(backdrop);
    wrap.appendChild(area);
    area.style.background = "transparent";  // let the backdrop (and its squiggles) show

    var bar = document.createElement("div");
    bar.className = "spellfix-bar";
    bar.hidden = true;
    wrap.insertAdjacentElement("afterend", bar);

    var misspelled = [];   // [{wrong, fixes}]
    var timer = null;

    function syncStyles() {
      var cs = getComputedStyle(area);
      MIRROR.forEach(function (p) { backdrop.style[p] = cs[p]; });
      backdrop.style.backgroundColor = bg;
      backdrop.style.borderRadius = cs.borderRadius;
      backdrop.style.width = area.offsetWidth + "px";
      backdrop.style.height = area.offsetHeight + "px";
      // If the textarea shows a scrollbar its text wraps at a narrower width;
      // pad the mirror by the scrollbar width so the words stay aligned.
      var sb = area.offsetWidth - area.clientWidth
        - parseFloat(cs.borderLeftWidth || 0) - parseFloat(cs.borderRightWidth || 0);
      backdrop.style.paddingRight = (parseFloat(cs.paddingRight || 0) + Math.max(0, sb)) + "px";
    }

    function paint() {
      var text = area.value;
      if (!misspelled.length) {
        backdrop.textContent = text;   // plain mirror, no marks
      } else {
        var words = misspelled.map(function (m) { return m.wrong; })
          .filter(function (w, i, a) { return a.indexOf(w) === i; })
          .sort(function (a, b) { return b.length - a.length; })
          .map(reEscape);
        var re = new RegExp("\\b(" + words.join("|") + ")\\b", "gi");
        backdrop.innerHTML = esc(text).replace(re, function (m) {
          return '<span class="spell-err">' + m + "</span>";
        });
      }
      backdrop.scrollTop = area.scrollTop;
      backdrop.scrollLeft = area.scrollLeft;
      renderBar();
    }

    function renderBar() {
      if (!misspelled.length) { bar.hidden = true; bar.textContent = ""; return; }
      bar.hidden = false;
      bar.textContent = "";
      var label = document.createElement("span");
      label.className = "spellfix-label";
      label.textContent = "✏️ Fix spelling:";
      bar.appendChild(label);
      misspelled.forEach(function (m) {
        var fix = m.fixes[0];
        if (!fix) return;
        var chip = document.createElement("button");
        chip.type = "button";
        chip.className = "spellfix-chip";
        var a = document.createElement("span"); a.className = "spellfix-wrong"; a.textContent = m.wrong;
        var arrow = document.createElement("span"); arrow.className = "spellfix-arrow"; arrow.textContent = "→";
        var b = document.createElement("span"); b.className = "spellfix-fix"; b.textContent = fix;
        chip.appendChild(a); chip.appendChild(arrow); chip.appendChild(b);
        chip.addEventListener("mousedown", function (ev) { ev.preventDefault(); });
        chip.addEventListener("click", function () { applyFix(m.wrong, fix); });
        bar.appendChild(chip);
      });
    }

    function applyFix(wrong, fix) {
      var re = new RegExp("\\b" + reEscape(wrong) + "\\b", "gi");
      area.value = area.value.replace(re, function (match) {
        return (match.charAt(0) === match.charAt(0).toUpperCase())
          ? fix.charAt(0).toUpperCase() + fix.slice(1) : fix;
      });
      area.dispatchEvent(new Event("input", { bubbles: true }));  // autosave
      misspelled = misspelled.filter(function (m) {
        return m.wrong.toLowerCase() !== wrong.toLowerCase();
      });
      paint();
      schedule();
    }

    function schedule() {
      if (timer) clearTimeout(timer);
      timer = setTimeout(check, 900);
    }

    function check() {
      var text = area.value;
      if (text.trim().length < 2) { misspelled = []; paint(); return; }
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text }),
        credentials: "same-origin",
      })
        .then(function (r) { return r.ok ? r.json() : { misspelled: [] }; })
        .then(function (d) {
          var low = area.value.toLowerCase();
          misspelled = (d.misspelled || []).filter(function (m) {
            return m.wrong && low.indexOf(m.wrong.toLowerCase()) !== -1;
          });
          paint();
        })
        .catch(function () { /* keep whatever we had */ });
    }

    area.addEventListener("input", function () { paint(); schedule(); });
    area.addEventListener("scroll", function () {
      backdrop.scrollTop = area.scrollTop;
      backdrop.scrollLeft = area.scrollLeft;
    });
    window.addEventListener("resize", syncStyles);
    if (window.ResizeObserver) {
      new ResizeObserver(function () { syncStyles(); paint(); }).observe(area);
    }

    syncStyles();
    paint();
    schedule();  // check any pre-filled answer on load
  });
})();

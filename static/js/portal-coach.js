/* Writing coach: "Get feedback on my draft" for rough-draft questions.

   Sends the CURRENT textarea text (also saved server-side so nothing is lost)
   and renders praise + suggestions. Feedback persists on the sheet, so it's
   still there after a reload. Kid-facing only — no grades, no rewriting. */
(function () {
  "use strict";

  var form = document.getElementById("response-form");
  if (!form || form.dataset.submitted === "1") return;

  Array.prototype.slice.call(document.querySelectorAll(".coach-widget")).forEach(function (widget) {
    var qid = widget.dataset.coachFor;
    var url = widget.dataset.coachUrl;
    var btn = widget.querySelector(".coach-btn");
    var box = widget.querySelector(".coach-box");
    var praiseEl = widget.querySelector(".coach-praise");
    var listEl = widget.querySelector(".coach-suggestions");
    var area = document.getElementById("q" + qid);
    if (!btn || !area) return;

    btn.addEventListener("click", function () {
      var text = area.value.trim();
      if (text.length < 20) {
        show("Write a little more first — then I can give you good feedback!", []);
        return;
      }
      btn.disabled = true;
      var original = btn.textContent;
      btn.textContent = "📖 Reading your draft…";
      fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: qid, text: area.value }),
        credentials: "same-origin",
      })
        .then(function (resp) { return resp.ok ? resp.json() : { ok: false }; })
        .then(function (data) {
          if (data.ok) {
            show(data.praise, data.suggestions || []);
            btn.textContent = "✨ Get new feedback";
          } else if (data.error === "too_short") {
            show("Write a little more first — then I can give you good feedback!", []);
            btn.textContent = original;
          } else {
            show("The coach is taking a break — ask your teacher, or try again in a bit!", []);
            btn.textContent = original;
          }
        })
        .catch(function () {
          show("The coach is taking a break — ask your teacher, or try again in a bit!", []);
          btn.textContent = original;
        })
        .then(function () { btn.disabled = false; });
    });

    function show(praise, suggestions) {
      box.hidden = false;
      praiseEl.textContent = praise || "";
      listEl.innerHTML = "";
      suggestions.forEach(function (s) {
        var li = document.createElement("li");
        li.textContent = s;              // plain text — model output can't inject markup
        listEl.appendChild(li);
      });
    }
  });
})();

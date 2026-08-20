/* Same-origin POST helper for the kid surfaces.
 *
 * These write to the database, so they carry the CSRF token like any other
 * form. A missing token fails with 403 — and a silent failure here means her
 * answer is scored on screen and lost in the database, which is worse than an
 * error, so the caller is told.
 */
window.spellingPost = function (url, body) {
  var field = document.querySelector("input[name=csrfmiddlewaretoken]");
  return fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": field ? field.value : ""
    },
    credentials: "same-origin",
    body: JSON.stringify(body)
  }).then(function (r) {
    if (!r.ok) throw new Error("save failed: " + r.status);
    return r.json();
  });
};

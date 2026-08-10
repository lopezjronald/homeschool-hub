/* Kid portal calendar — read-only FullCalendar.
 *
 * Same wiring as calendar-page.js but stripped: no filters, no day-click, no
 * edit URLs (the feed never sends any). Mission links (S3) navigate natively.
 */
(function () {
  "use strict";

  var el = document.getElementById("portal-calendar");
  if (!el || typeof FullCalendar === "undefined") return;

  var feedUrl = el.dataset.feedUrl;
  var phone = window.matchMedia("(max-width: 576px)").matches;

  var calendar = new FullCalendar.Calendar(el, {
    initialView: phone ? "listWeek" : "dayGridMonth",
    timeZone: "local",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,listWeek",
    },
    buttonText: { today: "Today", dayGridMonth: "Month", listWeek: "List" },
    height: "auto",
    dayMaxEventRows: 3,
    events: function (info, success, failure) {
      var params = new URLSearchParams({ start: info.startStr, end: info.endStr });
      fetch(feedUrl + "?" + params.toString(), { credentials: "same-origin" })
        .then(function (resp) {
          if (!resp.ok) throw new Error("feed " + resp.status);
          return resp.json();
        })
        .then(success)
        .catch(failure);
    },
    eventClassNames: function (arg) {
      var layer = (arg.event.extendedProps || {}).layer;
      return layer ? ["cal-layer-" + layer] : [];
    },
  });
  calendar.render();
})();

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
    // The agenda strip above already covers this week, so even on phones the
    // widget's job is the future: month view, not a duplicate week list.
    initialView: "dayGridMonth",
    timeZone: "local",
    headerToolbar: {
      left: "prev,next today",
      center: "title",
      right: "dayGridMonth,listWeek,timeGridDay",
    },
    buttonText: { today: "Today", dayGridMonth: "Month", listWeek: "List", timeGridDay: "Day" },
    height: "auto",
    dayMaxEventRows: phone ? 2 : 3,
    eventOrder: "prio,start,title",
    scrollTime: "08:00:00",
    slotMinTime: "06:00:00",
    slotMaxTime: "21:00:00",
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

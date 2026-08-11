/* Parent family calendar — FullCalendar wiring.
 *
 * Progressive enhancement: the page renders its controls server-side; this
 * script mounts FullCalendar into #calendar using data- attributes for URLs so
 * the file stays static. Child filter checkboxes re-fetch the feed with a
 * `children=` param (the server validates ids — the filter can only narrow).
 */
(function () {
  "use strict";

  var el = document.getElementById("calendar");
  if (!el || typeof FullCalendar === "undefined") return;

  var feedUrl = el.dataset.feedUrl;
  var addUrl = el.dataset.addUrl || "";

  function checkedChildIds() {
    return Array.prototype.slice
      .call(document.querySelectorAll(".cal-child-filter:checked"))
      .map(function (box) { return box.value; });
  }

  function checkedLayers() {
    var layers = ["events", "missions"];
    Array.prototype.slice
      .call(document.querySelectorAll(".cal-layer-toggle:checked"))
      .forEach(function (box) { layers.push(box.value); });
    return layers;
  }

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
    dayMaxEventRows: 4,
    events: function (info, success, failure) {
      var params = new URLSearchParams({ start: info.startStr, end: info.endStr });
      var ids = checkedChildIds();
      if (ids.length) params.set("children", ids.join(","));
      params.set("layers", checkedLayers().join(","));
      fetch(feedUrl + "?" + params.toString(), { credentials: "same-origin" })
        .then(function (resp) {
          if (!resp.ok) throw new Error("feed " + resp.status);
          return resp.json();
        })
        .then(success)
        .catch(failure);
    },
    dateClick: addUrl
      ? function (info) { window.location.href = addUrl + "?date=" + info.dateStr.slice(0, 10); }
      : undefined,
    eventClassNames: function (arg) {
      var layer = (arg.event.extendedProps || {}).layer;
      return layer ? ["cal-layer-" + layer] : [];
    },
  });
  calendar.render();

  document.querySelectorAll(".cal-child-filter, .cal-layer-toggle").forEach(function (box) {
    box.addEventListener("change", function () { calendar.refetchEvents(); });
  });
})();

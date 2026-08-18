/* Right-click (or long-press) an event → Edit · Duplicate · Delete.
 *
 * The case this exists for: several meetings that are the same in every
 * respect except the date. Duplicating and changing one field beats retyping
 * the title, place, time and child each time.
 *
 * Only real calendar rows get a menu. The generated layers — missions,
 * birthdays, Spanish, history — carry no pk in the feed because there is no
 * row behind them to edit, and offering "Delete" on a child's birthday would
 * be a lie.
 *
 * Long-press covers the tablet, where there is no right button. It is
 * cancelled by any movement, so a scroll or a drag never opens the menu.
 */
(function () {
  "use strict";

  var el = document.getElementById("calendar");
  if (!el) return;
  var editUrl = el.dataset.editUrl;
  var dupUrl = el.dataset.duplicateUrl;
  var delUrl = el.dataset.deleteUrl;
  var csrf = el.dataset.csrf;
  if (!editUrl || !dupUrl || !delUrl || !csrf) return;   // read-only viewer

  var menu = null;

  function close() {
    if (menu) { menu.remove(); menu = null; }
  }

  function post(url) {
    // A form POST rather than fetch: both actions end in a redirect the
    // browser should follow (duplicate → the copy's edit page, delete → back
    // to the calendar), and this keeps the CSRF handling ordinary.
    var f = document.createElement("form");
    f.method = "post";
    f.action = url;
    var t = document.createElement("input");
    t.type = "hidden";
    t.name = "csrfmiddlewaretoken";
    t.value = csrf;
    f.appendChild(t);
    document.body.appendChild(f);
    f.submit();
  }

  function open(x, y, info) {
    close();
    var pk = (info.event.extendedProps || {}).pk;
    if (!pk) return;                       // a generated chip: nothing to edit

    menu = document.createElement("div");
    menu.className = "cal-menu";
    menu.setAttribute("role", "menu");

    var title = document.createElement("div");
    title.className = "cal-menu-title";
    title.textContent = info.event.title;
    menu.appendChild(title);

    [
      ["✏️ Edit", function () { window.location.href = editUrl.replace("/0/", "/" + pk + "/"); }],
      ["📋 Duplicate", function () { post(dupUrl.replace("/0/", "/" + pk + "/")); }],
      ["🗑️ Delete", function () {
        if (window.confirm("Delete “" + info.event.title + "”?")) {
          post(delUrl.replace("/0/", "/" + pk + "/"));
        }
      }],
    ].forEach(function (pair) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "cal-menu-item";
      b.setAttribute("role", "menuitem");
      b.textContent = pair[0];
      b.addEventListener("click", function (e) {
        e.stopPropagation();
        close();
        pair[1]();
      });
      menu.appendChild(b);
    });

    // Place first, THEN measure and correct. Measuring before the menu has a
    // position of its own gave a height that had not laid out yet, so a menu
    // opened near the bottom ran off the screen instead of flipping above the
    // pointer — the exact case of a right-click on the last row of the month.
    menu.style.visibility = "hidden";
    menu.style.left = x + "px";
    menu.style.top = y + "px";
    document.body.appendChild(menu);

    var r = menu.getBoundingClientRect();
    var pad = 8;
    var left = x, top = y;
    if (r.right > window.innerWidth - pad) left = window.innerWidth - r.width - pad;
    if (r.bottom > window.innerHeight - pad) {
      // Flip above the pointer; if it still will not fit, sit it against the
      // bottom edge rather than off it.
      top = y - r.height;
      if (top < pad) top = Math.max(pad, window.innerHeight - r.height - pad);
    }
    menu.style.left = Math.max(pad, left) + "px";
    menu.style.top = Math.max(pad, top) + "px";
    menu.style.visibility = "";
    menu.querySelector(".cal-menu-item").focus();
  }

  document.addEventListener("click", close);
  document.addEventListener("scroll", close, true);
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") close();
  });

  // FullCalendar gives us the event on its own hooks; wire them from the page
  // via a global the calendar script calls after it builds each chip.
  window.calendarMenuAttach = function (info) {
    var node = info.el;
    node.addEventListener("contextmenu", function (e) {
      e.preventDefault();
      open(e.clientX, e.clientY, info);
    });

    var timer = null, sx = 0, sy = 0;
    node.addEventListener("touchstart", function (e) {
      var t = e.touches[0];
      sx = t.clientX; sy = t.clientY;
      timer = window.setTimeout(function () {
        timer = null;
        open(sx, sy, info);
      }, 500);
    }, { passive: true });
    ["touchmove", "touchend", "touchcancel"].forEach(function (evt) {
      node.addEventListener(evt, function (e) {
        if (evt === "touchmove" && e.touches[0]) {
          var t = e.touches[0];
          if (Math.abs(t.clientX - sx) < 10 && Math.abs(t.clientY - sy) < 10) return;
        }
        if (timer) { window.clearTimeout(timer); timer = null; }
      }, { passive: true });
    });
  };
})();

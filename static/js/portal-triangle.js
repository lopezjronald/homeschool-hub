/* Right-triangle explorer for Saxon Lesson 86 (HH-155).

   Saxon's own framing: "For such a big word like 'trigonometry,' it is really just
   about the ratios of the three sides, defined relative to one of the angles."

   RELATIVE TO ONE OF THE ANGLES is the whole lesson, and it is the thing a static
   picture cannot teach. The hypotenuse never moves — it is always across from the
   right angle — but which leg is "opposite" and which is "adjacent" DEPENDS ON
   WHERE YOU ARE STANDING. Move theta to the other acute angle and those two labels
   swap. A printed diagram shows one of those two worlds and lets a child assume it
   is the only one; here she can move the angle and watch the words trade places.

   The second thing it shows is Saxon's similar-triangles point: scale the whole
   triangle and every side changes while the three RATIOS do not. That is why sine
   is a property of the angle rather than of the triangle.

   Pure core exported for node: the side lengths, the ratios, and which leg is
   which. Those are what can be quietly wrong. */
(function () {
  "use strict";

  var SIZE = 320, PAD = 46;

  function rad(deg) { return deg * Math.PI / 180; }

  /* The three sides of a right triangle from one acute angle and the hypotenuse.

     Kept in this order deliberately: opposite is defined FROM theta, so the caller
     cannot compute it without saying which angle it means. */
  function sides(theta, hyp) {
    var h = hyp > 0 ? hyp : 1;
    var t = Math.max(0.0001, Math.min(89.9999, theta));
    return {
      hypotenuse: h,
      opposite: h * Math.sin(rad(t)),
      adjacent: h * Math.cos(rad(t)),
    };
  }

  /* sin / cos / tan as Saxon writes them — as RATIOS of the named sides, not as
     calls to Math.sin. Computing them the other way would hide the definition the
     lesson is trying to teach, and would agree with itself even if `sides` were
     wrong. */
  function ratios(theta, hyp) {
    var s = sides(theta, hyp);
    return {
      sin: s.opposite / s.hypotenuse,
      cos: s.adjacent / s.hypotenuse,
      tan: s.adjacent === 0 ? null : s.opposite / s.adjacent,
    };
  }

  /* The other acute angle. The two always sum to 90 in a right triangle, which is
     why standing at the other corner swaps opposite and adjacent. */
  function complement(theta) {
    return 90 - theta;
  }

  /* Which named side each leg becomes, seen from `corner` ("A" or "B").

     A is the bottom-left acute angle, B the top. From A the vertical leg is
     opposite; from B it is adjacent. This function IS the lesson. */
  function legNames(corner) {
    return corner === "B"
      ? { vertical: "adjacent", horizontal: "opposite" }
      : { vertical: "opposite", horizontal: "adjacent" };
  }

  var core = { SIZE: SIZE, PAD: PAD, sides: sides, ratios: ratios,
               complement: complement, legNames: legNames };

  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.PortalTriangle = core;

  if (typeof document === "undefined") return;

  var NS = "http://www.w3.org/2000/svg";
  function el(name, attrs) {
    var n = document.createElementNS(NS, name);
    Object.keys(attrs || {}).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    return n;
  }

  function build(host, cfg) {
    var theta = Number(cfg.angle) || 30;
    var corner = "A";
    var scale = 1;

    var svg = el("svg", { viewBox: "0 0 " + SIZE + " " + SIZE, class: "lesson-triangle",
                          role: "img", "aria-label": "right triangle" });
    var readout = document.createElement("p");
    readout.className = "lesson-tool-readout";
    readout.setAttribute("aria-live", "polite");

    function draw() {
      while (svg.firstChild) svg.removeChild(svg.firstChild);
      var span = (SIZE - 2 * PAD) * scale;
      // Right angle at the bottom-right. A is bottom-left, B is top.
      var ax = PAD, ay = SIZE - PAD;
      var cx = PAD + span, cy = SIZE - PAD;
      var by = SIZE - PAD - span * Math.tan(rad(theta));
      var bx = cx;

      svg.appendChild(el("polygon", {
        points: ax + "," + ay + " " + bx + "," + by + " " + cx + "," + cy,
        fill: "#EAF2FA", stroke: "#14568C", "stroke-width": 3,
        "stroke-linejoin": "round",
      }));
      // The little square that marks the right angle — the anchor for "hypotenuse
      // is the side across from it".
      svg.appendChild(el("path", {
        d: "M" + (cx - 14) + "," + cy + " L" + (cx - 14) + "," + (cy - 14) +
           " L" + cx + "," + (cy - 14),
        fill: "none", stroke: "#1E2A24", "stroke-width": 2,
      }));

      var at = corner === "A" ? { x: ax, y: ay } : { x: bx, y: by };
      svg.appendChild(el("circle", { cx: at.x, cy: at.y, r: 9, fill: "none",
                                     stroke: "#C2571A", "stroke-width": 3 }));
      var th = el("text", { x: at.x + (corner === "A" ? 18 : -8),
                            y: at.y + (corner === "A" ? -10 : 26),
                            "font-size": 15, fill: "#C2571A", "font-weight": "700" });
      th.textContent = "θ = " + (corner === "A" ? theta : complement(theta)).toFixed(0) + "°";
      svg.appendChild(th);

      var names = legNames(corner);
      function label(x, y, text, anchor) {
        var t = el("text", { x: x, y: y, "font-size": 13, fill: "#3A4A40",
                             "text-anchor": anchor || "middle" });
        t.textContent = text;
        svg.appendChild(t);
      }
      label((ax + cx) / 2, cy + 22, names.horizontal);          // the base
      label(cx + 8, (by + cy) / 2, names.vertical, "start");    // the upright
      label((ax + bx) / 2 - 16, (ay + by) / 2 - 8, "hypotenuse", "end");

      var t2 = corner === "A" ? theta : complement(theta);
      var r = ratios(t2, 1);
      readout.textContent =
        "sen θ = opuesto/hipotenusa = " + r.sin.toFixed(3) +
        "   ·   cos θ = adyacente/hipotenusa = " + r.cos.toFixed(3) +
        "   ·   tan θ = opuesto/adyacente = " + (r.tan === null ? "—" : r.tan.toFixed(3));
    }

    var controls = document.createElement("div");
    controls.className = "lesson-tool-controls";
    function button(label, fn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "lesson-btn lesson-btn--ghost";
      b.textContent = label;
      b.addEventListener("click", function () { fn(); draw(); });
      controls.appendChild(b);
    }
    // THE control. Everything else is decoration.
    button("Stand at the other angle", function () {
      corner = corner === "A" ? "B" : "A";
    });
    button("Bigger", function () { scale = Math.min(1.35, scale + 0.15); });
    button("Smaller", function () { scale = Math.max(0.5, scale - 0.15); });

    var slider = document.createElement("input");
    slider.type = "range";
    slider.min = "10";
    slider.max = "80";
    slider.step = "1";
    slider.value = String(theta);
    slider.className = "lesson-slider";
    slider.setAttribute("aria-label", "angle in degrees");
    slider.addEventListener("input", function () {
      theta = Number(slider.value);
      draw();
    });

    host.appendChild(svg);
    host.appendChild(slider);
    host.appendChild(controls);
    host.appendChild(readout);
    draw();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.lesson-tool[data-tool="triangle"]').forEach(function (host) {
      var node = document.getElementById(host.dataset.configId);
      if (!node) return;
      try {
        build(host, JSON.parse(node.textContent));
      } catch (err) {
        host.textContent = "";
      }
    });
  });
})();

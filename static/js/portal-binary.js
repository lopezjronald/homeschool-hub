/* The binary place-value chart, with switches — Saxon Lesson 75 (HH-155).

   The lesson's own framing is the design: "in converting from base 2 to base 10,
   1 = ON and 0 = OFF." So the bits ARE switches. She flips them and watches the
   sum rebuild itself, place by place, the same way the lesson writes it out:

       1(8) + 0(4) + 1(2) + 1(1) = 8 + 2 + 1 = 11

   Saxon adds a note that matters here: "If you are having trouble understanding
   binary numbers, that's okay! EVERY Practice Set problem will be about one of
   the numbers listed in the Rules." A child who is stuck is meant to be able to
   look the answer up and see the pattern. Flipping switches is that lookup table
   made touchable.

   Pure core exported for node: the conversion both ways, and the worked line the
   lesson writes. Those are the parts that can be subtly wrong. */
(function () {
  "use strict";

  /* Place values for a chart `bits` wide, biggest first: [16, 8, 4, 2, 1]. */
  function places(bits) {
    var out = [];
    for (var i = bits - 1; i >= 0; i--) out.push(Math.pow(2, i));
    return out;
  }

  /* Bits (biggest first) -> base ten. Missing/blank entries count as off. */
  function toDecimal(onBits) {
    var bits = onBits || [];
    var total = 0;
    for (var i = 0; i < bits.length; i++) {
      if (bits[i]) total += Math.pow(2, bits.length - 1 - i);
    }
    return total;
  }

  /* Base ten -> bits, biggest first, padded to `bits` wide.

     Returns null when the number will not fit rather than silently dropping the
     high bits: showing 19 as "0011" on a four-wide chart would teach that 19 is
     3, which is worse than showing nothing. */
  function toBits(value, bits) {
    if (!(value >= 0) || value !== Math.floor(value)) return null;
    if (value >= Math.pow(2, bits)) return null;
    var out = [];
    for (var i = bits - 1; i >= 0; i--) {
      out.push(Math.floor(value / Math.pow(2, i)) % 2 === 1 ? 1 : 0);
    }
    return out;
  }

  /* The line the lesson writes out: "1(8) + 0(4) + 1(2) + 1(1) = 8 + 2 + 1 = 11".

     Every place is shown, including the zeros, because the zeros are the point:
     the lesson says to "ignore it because you are multiplying by 0", and she can
     only see that if the term is on the page. */
  function workedLine(onBits) {
    var vals = places((onBits || []).length);
    var terms = vals.map(function (v, i) { return (onBits[i] ? 1 : 0) + "(" + v + ")"; });
    var live = vals.filter(function (v, i) { return !!onBits[i]; });
    var total = toDecimal(onBits);
    if (!live.length) return terms.join(" + ") + " = 0";
    return terms.join(" + ") + " = " + live.join(" + ") + " = " + total;
  }

  /* Binary string for display, e.g. [1,0,1,1] -> "1011". */
  function toString2(onBits) {
    return (onBits || []).map(function (b) { return b ? "1" : "0"; }).join("");
  }

  var core = { places: places, toDecimal: toDecimal, toBits: toBits,
               workedLine: workedLine, toString2: toString2 };

  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.PortalBinary = core;

  if (typeof document === "undefined") return;

  function build(host, cfg) {
    var width = Number(cfg.bits) || 5;
    var start = toBits(Number(cfg.value) || 0, width) || toBits(0, width);
    var on = start.slice();

    var chart = document.createElement("div");
    chart.className = "lesson-binary";

    var readout = document.createElement("p");
    readout.className = "lesson-tool-readout";
    readout.setAttribute("aria-live", "polite");

    var switches = [];
    places(width).forEach(function (place, i) {
      var cell = document.createElement("button");
      cell.type = "button";
      cell.className = "lesson-bit";
      // The place value is part of the label, not decoration: the whole method is
      // "which places are on, and what are they worth".
      cell.innerHTML = "";
      var digit = document.createElement("span");
      digit.className = "lesson-bit-digit";
      var value = document.createElement("span");
      value.className = "lesson-bit-place";
      value.textContent = "2^" + (width - 1 - i) + " = " + place;
      cell.appendChild(digit);
      cell.appendChild(value);
      cell.addEventListener("click", function () {
        on[i] = on[i] ? 0 : 1;
        render();
      });
      switches.push({ node: cell, digit: digit });
      chart.appendChild(cell);
    });

    function render() {
      switches.forEach(function (s, i) {
        s.digit.textContent = on[i] ? "1" : "0";
        s.node.classList.toggle("is-on", !!on[i]);
        s.node.setAttribute("aria-pressed", on[i] ? "true" : "false");
        s.node.setAttribute(
          "aria-label",
          places(width)[i] + "s place, " + (on[i] ? "on" : "off"));
      });
      readout.textContent = "binary " + toString2(on) + "   →   " + workedLine(on);
    }

    var controls = document.createElement("div");
    controls.className = "lesson-tool-controls";
    function button(label, fn) {
      var b = document.createElement("button");
      b.type = "button";
      b.className = "lesson-btn lesson-btn--ghost";
      b.textContent = label;
      b.addEventListener("click", fn);
      controls.appendChild(b);
    }
    button("All off", function () {
      on = on.map(function () { return 0; });
      render();
    });
    button("Count up", function () {
      // Adding one and re-rendering shows the carry happening, which is the
      // thing a static table of 1-20 cannot show.
      var next = toDecimal(on) + 1;
      var bits = toBits(next, width);
      on = bits || toBits(0, width);
      render();
    });

    host.appendChild(chart);
    host.appendChild(controls);
    host.appendChild(readout);
    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.lesson-tool[data-tool="binary"]').forEach(function (host) {
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

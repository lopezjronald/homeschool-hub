/* Lesson 72's tool: slide the decimal point.

   Scientific notation has exactly one idea hiding in it — the decimal point and
   the exponent are the same fact told two ways, and moving one PAYS FOR the other
   so the value never changes. Every rule in the lesson falls out of that:

     - "same size shoes" before adding: slide until the exponents match
     - renormalise at the end: slide until one digit sits before the point
     - the sign trap: left is +1 to the exponent, right is -1

   So the tool shows one number, a slider, and the value. She slides; the digits
   and the exponent move in opposite directions; the value stubbornly does not.
   That refusal to change is the lesson. */
(function () {
  "use strict";

  /* Pure: shift `moves` places and report the same value written differently.
     Positive `moves` slides the point LEFT (mantissa shrinks, exponent grows). */
  function shift(mantissa, exponent, moves) {
    return {
      mantissa: mantissa / Math.pow(10, moves),
      exponent: exponent + moves,
    };
  }

  function value(mantissa, exponent) {
    return mantissa * Math.pow(10, exponent);
  }

  /* Is it in standard form? Exactly one non-zero digit before the point. */
  function isStandard(mantissa) {
    var m = Math.abs(mantissa);
    return m >= 1 && m < 10;
  }

  /* How many places from standard form — what the renormalise step must undo. */
  function movesToStandard(mantissa) {
    if (mantissa === 0) return 0;
    var m = Math.abs(mantissa), n = 0;
    while (m >= 10) { m /= 10; n += 1; }
    while (m < 1) { m *= 10; n -= 1; }
    return n;
  }

  function format(n) {
    // Keep it readable without exponent soup from toString().
    if (n === 0) return "0";
    var s = Math.abs(n) < 1e-4 || Math.abs(n) >= 1e15
      ? n.toExponential(4) : String(Math.round(n * 1e10) / 1e10);
    return s;
  }

  var core = { shift: shift, value: value, isStandard: isStandard,
               movesToStandard: movesToStandard };
  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.portalSciCore = core;
  if (typeof document === "undefined") return;

  function build(host, cfg) {
    var m0 = cfg.mantissa, e0 = cfg.exponent;
    var span = cfg.span || 4;
    var moves = 0;

    var wrap = document.createElement("div");
    wrap.className = "scislide";
    var display = document.createElement("p");
    display.className = "scislide-display";
    var truth = document.createElement("p");
    truth.className = "scislide-truth";
    var slider = document.createElement("input");
    slider.type = "range"; slider.min = String(-span); slider.max = String(span);
    slider.value = "0"; slider.className = "ratiobar-scale";
    slider.setAttribute("aria-label", "Slide the decimal point");
    var readout = document.createElement("div");
    readout.className = "lesson-tool-readout";
    readout.setAttribute("aria-live", "polite");

    function render() {
      var s = shift(m0, e0, moves);
      display.innerHTML = "";
      var mant = document.createElement("span");
      mant.className = "scislide-mantissa";
      mant.textContent = format(s.mantissa);
      var rest = document.createElement("span");
      rest.className = "scislide-exponent";
      rest.textContent = " × 10";
      var sup = document.createElement("sup");
      sup.textContent = s.exponent;
      display.appendChild(mant); display.appendChild(rest); display.appendChild(sup);

      truth.textContent = "= " + format(value(s.mantissa, s.exponent));
      display.classList.toggle("is-standard", isStandard(s.mantissa));
      readout.textContent = isStandard(s.mantissa)
        ? "Standard form: one digit before the point."
        : (Math.abs(s.mantissa) >= 10
            ? "Too big — slide left to move a digit past the point."
            : "Too small — slide right to bring a digit in front.");
    }

    slider.addEventListener("input", function () {
      moves = parseInt(slider.value, 10) || 0;
      render();
    });

    wrap.appendChild(display);
    wrap.appendChild(truth);
    wrap.appendChild(slider);
    wrap.appendChild(readout);
    host.appendChild(wrap);
    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.lesson-tool[data-tool="scislide"]').forEach(function (host) {
      var node = document.getElementById(host.dataset.configId);
      var cfg = {};
      try { cfg = JSON.parse(node.textContent); } catch (e) { cfg = {}; }
      if (typeof cfg.mantissa === "number") build(host, cfg);
    });
  });
})();

/* Lesson 71's tool: a ratio bar you can scale.

   The whole lesson is one move — a ratio tells you the size of the SLICES, and
   adding the slices gives you the WHOLE. Stating that does not land; watching the
   total move in step with the parts does.

   Drag the scale factor and every row moves together: 3 red : 4 blue at scale 20
   is 60 red, 80 blue, 140 altogether. The number she was given (60 red) and the
   number she wants (140 total) are on screen at the same time, in the same
   picture, which is the thing the ratio box on paper cannot show.

   Same bar-model language Violet uses for her word problems, on purpose — it is
   the family's shared vocabulary for "part, part, whole." */
(function () {
  "use strict";

  /* Pure: the numbers behind the picture at a given scale. */
  function scaleRows(parts, scale) {
    var total = parts.reduce(function (a, p) { return a + p.ratio; }, 0);
    return {
      parts: parts.map(function (p) {
        return { name: p.name, ratio: p.ratio, actual: p.ratio * scale, tone: p.tone };
      }),
      ratioTotal: total,
      actualTotal: total * scale,
      scale: scale,
    };
  }

  var core = { scaleRows: scaleRows };
  if (typeof module !== "undefined" && module.exports) module.exports = core;
  if (typeof window !== "undefined") window.portalRatioCore = core;
  if (typeof document === "undefined") return;

  var TONES = { start: "#14568C", move: "#C2571A", quiet: "#5A6A60" };

  function build(host, cfg) {
    var parts = cfg.parts || [];
    var target = cfg.target || null;      // {name, actual} — the number she is given
    var maxScale = cfg.maxScale || 25;
    var scale = cfg.scale || 1;

    var wrap = document.createElement("div");
    wrap.className = "ratiobar";
    host.appendChild(wrap);

    var bars = document.createElement("div");
    wrap.appendChild(bars);

    var slider = document.createElement("input");
    slider.type = "range"; slider.min = "1"; slider.max = String(maxScale);
    slider.value = String(scale);
    slider.className = "ratiobar-scale";
    slider.setAttribute("aria-label", "How many of each ratio unit");

    var readout = document.createElement("div");
    readout.className = "lesson-tool-readout";
    readout.setAttribute("aria-live", "polite");

    function render() {
      var s = scaleRows(parts, scale);
      var widest = s.actualTotal || 1;
      bars.innerHTML = "";
      s.parts.concat([{ name: "TOTAL", ratio: s.ratioTotal, actual: s.actualTotal, tone: "quiet", isTotal: true }])
        .forEach(function (row) {
          var line = document.createElement("div");
          line.className = "ratiobar-row" + (row.isTotal ? " is-total" : "");
          var label = document.createElement("span");
          label.className = "ratiobar-label";
          label.textContent = row.name;
          var track = document.createElement("span");
          track.className = "ratiobar-track";
          var fill = document.createElement("span");
          fill.className = "ratiobar-fill";
          fill.style.width = (row.actual / widest * 100) + "%";
          fill.style.background = TONES[row.tone] || TONES.quiet;
          track.appendChild(fill);
          var value = document.createElement("span");
          value.className = "ratiobar-value";
          value.textContent = row.ratio + " → " + row.actual;
          line.appendChild(label); line.appendChild(track); line.appendChild(value);
          bars.appendChild(line);
        });

      if (target) {
        var hit = s.parts.filter(function (p) { return p.name === target.name; })[0];
        readout.textContent = hit && hit.actual === target.actual
          ? "That's it — " + target.actual + " " + target.name.toLowerCase() +
            ", so the total is " + s.actualTotal + "."
          : "Slide until " + target.name + " reads " + target.actual + ".";
      } else {
        readout.textContent = "Each ratio unit is worth " + scale + ".";
      }
    }

    slider.addEventListener("input", function () {
      scale = parseInt(slider.value, 10) || 1;
      render();
    });

    wrap.appendChild(slider);
    wrap.appendChild(readout);
    render();
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll('.lesson-tool[data-tool="ratiobar"]').forEach(function (host) {
      var node = document.getElementById(host.dataset.configId);
      var cfg = {};
      try { cfg = JSON.parse(node.textContent); } catch (e) { cfg = {}; }
      build(host, cfg);
    });
  });
})();

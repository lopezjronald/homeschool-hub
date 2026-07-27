/* Lingua read-aloud recorder (LGA-73). CSP-clean: external file, no inline handlers.
 *
 * Optional + progressive: the recorder container ships hidden; we reveal it only when
 * the browser actually supports MediaRecorder + getUserMedia (a secure context). Tap
 * to start (mic permission prompt), tap to stop; on stop we POST the audio blob to a
 * token-authed same-origin endpoint (connect-src 'self'). The recording is private —
 * parent-only playback, never sent to any AI. Nothing is uploaded until the child
 * chooses to record and stop, and a denied mic permission just resets the control.
 */
(function () {
  "use strict";

  document.addEventListener("DOMContentLoaded", function () {
    var box = document.getElementById("lingua-recorder");
    var btn = document.getElementById("lingua-rec-btn");
    var status = document.getElementById("lingua-rec-status");
    if (!box || !btn || !status) return;

    var supported = typeof MediaRecorder !== "undefined" &&
      navigator.mediaDevices && navigator.mediaDevices.getUserMedia;
    if (!supported) return;      // leave hidden — no half-working UI on old browsers
    box.hidden = false;

    var recorder = null, chunks = [], stream = null, startedAt = 0, busy = false;

    function setStatus(msg) { status.textContent = msg || ""; }

    function stopTracks() {
      if (stream) { stream.getTracks().forEach(function (t) { t.stop(); }); stream = null; }
    }

    function reset(msg) {
      recorder = null; chunks = [];
      stopTracks();
      btn.textContent = "🎤 Grábate leyendo";
      btn.disabled = false;
      busy = false;
      setStatus(msg || "");
    }

    function mimeType() {
      var prefs = ["audio/webm;codecs=opus", "audio/webm", "audio/ogg", "audio/mp4"];
      for (var i = 0; i < prefs.length; i++) {
        try { if (MediaRecorder.isTypeSupported(prefs[i])) return prefs[i]; } catch (e) {}
      }
      return "";
    }

    function upload(blob) {
      var url = box.getAttribute("data-record-url");
      if (!url) { reset(); return; }
      var secs = Math.round((Date.now() - startedAt) / 1000);
      var fd = new FormData();
      // filename extension is cosmetic; the server keys off the content type.
      fd.append("audio", blob, "lectura.webm");
      fd.append("seconds", String(secs));
      setStatus("Guardando…");
      fetch(url, { method: "POST", body: fd, credentials: "same-origin" })
        .then(function (r) { return r.ok ? r.json() : Promise.reject(); })
        .then(function (d) { reset(d && d.saved ? "✓ ¡Grabado! Se lo puede escuchar un adulto." : "No se pudo guardar."); })
        .catch(function () { reset("No se pudo guardar. Inténtalo otra vez."); });
    }

    function start() {
      setStatus("Pidiendo permiso del micrófono…");
      btn.disabled = true;
      navigator.mediaDevices.getUserMedia({ audio: true }).then(function (s) {
        stream = s;
        var mt = mimeType();
        recorder = mt ? new MediaRecorder(s, { mimeType: mt }) : new MediaRecorder(s);
        chunks = [];
        recorder.addEventListener("dataavailable", function (e) {
          if (e.data && e.data.size) chunks.push(e.data);
        });
        recorder.addEventListener("stop", function () {
          var blob = new Blob(chunks, { type: recorder.mimeType || "audio/webm" });
          upload(blob);
        });
        startedAt = Date.now();
        recorder.start();
        btn.textContent = "⏹ Detener";
        btn.disabled = false;
        setStatus("● Grabando… lee en voz alta 🎤");
      }).catch(function () {
        reset("No se pudo usar el micrófono.");
      });
    }

    function stop() {
      if (!recorder || recorder.state === "inactive") { reset(); return; }
      busy = true;
      btn.disabled = true;
      setStatus("Guardando…");
      recorder.stop();          // fires 'stop' → upload()
    }

    btn.addEventListener("click", function () {
      if (busy) return;
      if (recorder && recorder.state === "recording") stop();
      else start();
    });
  });
})();

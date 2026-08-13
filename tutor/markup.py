"""Replay a child's drawn-on-the-sentence work so it can be read and printed.

The portal stores markup answers as normalized strokes — ``{"c": colour, "w":
width, "p": [[x, y], ...]}`` with x/y in 0..1 of the drawing surface — plus the
machine-read ``marks`` ("underlined 'It'"). Until now only the marks escaped the
portal: the parent's review page and the charter report showed a sentence and a
sentence of prose about it, never the work itself. A report of a
mark-the-sentence exercise that cannot show the marks is not a report of that
exercise.

Rendered as inline SVG rather than a canvas on purpose: it needs no JavaScript,
survives print and print-to-PDF, and scales without going fuzzy.
"""

import json
import re

from django.utils.safestring import mark_safe

# Strokes are normalized 0..1; scale into a viewBox for readable path data.
VIEW = 1000

# Only literal hex colours from the portal's own pen set reach the page.
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_DEFAULT_COLOUR = "#333333"


def _colour(raw):
    raw = str(raw or "").strip()
    return raw if _HEX.match(raw) else _DEFAULT_COLOUR


def _width(raw):
    try:
        return max(1.0, min(float(raw), 12.0))
    except (TypeError, ValueError):
        return 3.0


def _points(stroke):
    out = []
    for point in stroke.get("p") or []:
        try:
            x, y = float(point[0]), float(point[1])
        except (TypeError, ValueError, IndexError, KeyError):
            continue
        if x != x or y != y:          # NaN survives float(); it would poison the path
            continue
        out.append((x * VIEW, y * VIEW))
    return out


def strokes_svg(strokes):
    """Inline SVG for a list of strokes, or "" when there is nothing drawn.

    ``preserveAspectRatio="none"`` so the drawing stretches back over the same
    normalized space it was drawn in, and ``vector-effect`` so stretching does
    not squash the pen into an ellipse.
    """
    if not isinstance(strokes, list):
        return ""
    paths = []
    for stroke in strokes:
        if not isinstance(stroke, dict):
            continue
        pts = _points(stroke)
        if not pts:
            continue
        if len(pts) == 1:
            # A tap (a period, a dot) is one point; a polyline of one draws
            # nothing, so give it the same hair of length the canvas does.
            pts = [pts[0], (pts[0][0] + 0.1, pts[0][1])]
        coords = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        paths.append(
            f'<polyline points="{coords}" fill="none" stroke="{_colour(stroke.get("c"))}" '
            f'stroke-width="{_width(stroke.get("w")):.1f}" vector-effect="non-scaling-stroke" '
            f'stroke-linecap="round" stroke-linejoin="round"/>'
        )
    if not paths:
        return ""
    return mark_safe(
        f'<svg class="markup-replay-ink" viewBox="0 0 {VIEW} {VIEW}" '
        f'preserveAspectRatio="none" aria-hidden="true" focusable="false" '
        f'style="position:absolute;inset:0;width:100%;height:100%;">'
        + "".join(paths) +
        "</svg>"
    )


def _lines(text):
    """Words per line, matching Question.markup_lines so the two render alike."""
    lines, index = [], 0
    for raw in (text or "").splitlines():
        words = []
        for word in raw.split():
            words.append({"i": index, "text": word})
            index += 1
        lines.append(words)
    return lines


# The width a replayed surface is scaled down to fit. Comfortably inside both
# the parent's work card and a printed Letter page's content column.
TARGET_WIDTH = 620

# What the portal's drawing surface is on a typical laptop. Only used for answers
# saved before the surface size was recorded, where any choice is a guess.
_LEGACY_WIDTH = 700
_LEGACY_HEIGHT = 120


class MarkupReplay:
    """What a template needs to redraw one marked-up answer.

    The surface is rebuilt at the exact pixel width she drew on — that is what
    makes the sentence wrap the same way and keeps the words under her marks —
    and then scaled as a whole to fit the column it is being printed into.
    Scaling after layout moves the ink and the words together.
    """

    def __init__(self, text, strokes, marks, unread, surface=None):
        self.text = text
        self.lines = _lines(text)
        self.svg = strokes_svg(strokes)
        self.marks = marks
        self.unread = unread
        self.width, self.height, self.exact = self._surface(surface)

    @staticmethod
    def _surface(surface):
        """(width, height, exact) in CSS pixels; exact=False when we had to guess."""
        if isinstance(surface, dict):
            try:
                w, h = float(surface["w"]), float(surface["h"])
            except (KeyError, TypeError, ValueError):
                w = h = 0
            if 80 <= w <= 4000 and 20 <= h <= 4000:
                return round(w), round(h), True
        return _LEGACY_WIDTH, _LEGACY_HEIGHT, False

    @property
    def has_drawing(self):
        return bool(self.svg)

    @property
    def scale(self):
        """Shrink-to-fit only — a small drawing is never blown up."""
        return min(1.0, TARGET_WIDTH / self.width)

    @property
    def surface_style(self):
        return (f"width:{self.width}px;height:{self.height}px;"
                f"transform:scale({self.scale:.4f});transform-origin:top left;")

    @property
    def wrapper_style(self):
        """Reserve the post-scale footprint; a transform does not affect layout."""
        return (f"width:{self.width * self.scale:.0f}px;"
                f"height:{self.height * self.scale:.0f}px;max-width:100%;")

    @property
    def summary(self):
        """"underlined "It"; circled "Jim"" — the reading, for anyone checking."""
        by_kind = {}
        for mark in self.marks:
            word = str(mark.get("word", "")).strip()
            kind = str(mark.get("kind", "")).strip()
            if word and kind:
                by_kind.setdefault(kind, []).append(word)
        parts = []
        for kind in ("underlined", "circled", "crossed out"):
            words = by_kind.get(kind)
            if words:
                parts.append(f"{kind} " + ", ".join(f'“{w}”' for w in words))
        if not parts:
            return ""
        text = "; ".join(parts)
        if self.unread:
            text += f" (plus {self.unread} more mark(s) the reader could not name)"
        return text


def replay_for(raw, question):
    """Build a MarkupReplay from a stored answer, or None if there is nothing.

    Handles both markup questions (the sentence lives on the question) and
    write-then-markup ones (she typed the sentence herself, so it lives in the
    answer alongside the strokes).
    """
    try:
        data = json.loads(raw or "")
    except (ValueError, TypeError):
        return None

    if isinstance(data, list):
        # Pre-marks answers are a bare stroke list. The drawing is still hers and
        # still worth printing, even though nothing can name what it marked.
        data = {"strokes": data}
    if not isinstance(data, dict):
        return None

    strokes = data.get("strokes")
    strokes = strokes if isinstance(strokes, list) else []
    if not strokes:
        return None

    marks = [m for m in (data.get("marks") or []) if isinstance(m, dict)]
    try:
        unread = int(data.get("unread") or 0)
    except (TypeError, ValueError):
        unread = 0
    if getattr(question, "is_write_markup", False):
        text = str(data.get("text", "")).strip()
    else:
        text = question.passage or ""

    return MarkupReplay(text, strokes, marks, unread, data.get("surface"))

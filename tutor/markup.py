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
        width = float(raw)
    except (TypeError, ValueError):
        return 3.0
    if width != width:      # NaN compares false against everything, so clamping
        return 3.0          # it silently yields the low bound rather than the pen
    return max(1.0, min(width, 12.0))


def _points(stroke):
    # Answers are child-supplied JSON stored verbatim by autosave, so `p` is not
    # guaranteed to be a list: an int slices with TypeError and a dict with
    # KeyError, and one poisoned row would 500 the whole report for that date
    # range rather than degrading to "nothing drawn".
    points = stroke.get("p")
    if not isinstance(points, list):
        return []
    out = []
    for point in points[:MAX_POINTS]:
        try:
            x, y = float(point[0]), float(point[1])
        except (TypeError, ValueError, IndexError, KeyError):
            continue
        # NaN survives float() and both infinities format as literal "inf"/"-inf"
        # in the path data; a huge finite formats as hundreds of digits. Drop the
        # unusable and clamp the rest.
        if x != x or y != y:
            continue
        if not (COORD_MIN <= x <= COORD_MAX and COORD_MIN <= y <= COORD_MAX):
            x = min(max(x, COORD_MIN), COORD_MAX)
            y = min(max(y, COORD_MIN), COORD_MAX)
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
    for stroke in strokes[:MAX_STROKES]:
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


# Widths a replayed surface is scaled down to fit. Screen and print differ and
# must be measured, not assumed: the report's Bootstrap .container keeps a
# 540px max-width in print (its media query carries no media type), so a single
# "comfortably fits both" number silently cropped every printed drawing.
SCREEN_TARGET = 560   # the work card is ~582px wide at 992-1199px viewports
PRINT_TARGET = 600

# Bounds on child-supplied drawing data. Autosave stores whatever the client
# posts, and one stored answer fans out into ~34x its size as SVG path text, so
# an unbounded answer is an unopenable report page rather than a big drawing.
MAX_STROKES = 400
MAX_POINTS = 2000
# Coordinates are normalized 0..1; allow a little overdraw past the edges and
# reject the rest. Without this, inf reaches the path data as literal "inf" and
# 1e300 as a 302-digit number.
COORD_MIN, COORD_MAX = -1.0, 2.0

# What the portal's drawing surface is on a typical laptop. Only used for answers
# saved before the surface size was recorded, where any choice is a guess.
_LEGACY_WIDTH = 700
_LEGACY_HEIGHT = 120

# Measured advance widths of Georgia at 24px (the size .markup-replay-text
# renders at), for ASCII 32..126. Used only to work out how many lines a legacy
# passage wraps to, so its box is tall enough to hold the text. Georgia is the
# first family in the stack; the fallbacks (Times New Roman, serif) are
# narrower, so these round up rather than down.
# Control characters that force a new line in CSS (vertical tab, form feed)
# plus the rest of the control range, which renders unpredictably. Counting
# each as its own line is the safe direction.
_HARD_BREAKS = re.compile("[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f]+")
# Break opportunities inside a line. Capturing, so the separator run comes
# back alongside the words and can be charged its own width — a tab is a
# break opportunity too, and wider than a space.
_BREAK_POINTS = re.compile("([ \\t]+)")

GEORGIA_24 = (
    6.0, 8.0, 10.0, 15.0, 15.0, 20.0, 17.0, 5.0, 9.0, 9.0, 11.0, 15.0, 6.0,
    9.0, 6.0, 11.0, 15.0, 10.0, 13.0, 13.0, 14.0, 13.0, 14.0, 12.0, 14.0,
    14.0, 8.0, 8.0, 15.0, 15.0, 15.0, 11.0, 22.0, 16.0, 16.0, 15.0, 18.0,
    16.0, 14.0, 17.0, 20.0, 9.0, 12.0, 17.0, 14.0, 22.0, 18.0, 18.0, 15.0,
    18.0, 17.0, 13.0, 15.0, 18.0, 16.0, 23.0, 17.0, 15.0, 14.0, 9.0, 11.0,
    9.0, 15.0, 15.0, 12.0, 12.0, 13.0, 11.0, 14.0, 12.0, 8.0, 12.0, 14.0,
    7.0, 7.0, 13.0, 7.0, 21.0, 14.0, 13.0, 14.0, 13.0, 10.0, 10.0, 8.0,
    14.0, 12.0, 18.0, 12.0, 12.0, 11.0, 10.0, 9.0, 10.0, 15.0,
)


class MarkupReplay:
    """What a template needs to redraw one marked-up answer.

    The surface is rebuilt at the exact pixel width she drew on — that is what
    makes the sentence wrap the same way and keeps the words under her marks —
    and then scaled as a whole to fit the column it is being printed into.
    Scaling after layout moves the ink and the words together.
    """

    def __init__(self, text, strokes, marks, unread, surface=None, typed=False):
        self.text = text
        # Words she typed herself are mirrored into the portal's drawing surface
        # verbatim under white-space:pre-wrap, so re-joining them on whitespace
        # would shift every word after a double space. A printed passage is
        # rebuilt from its words; a typed one is reproduced as typed.
        self.typed = typed
        self.lines = [] if typed else _lines(text)
        self.svg = strokes_svg(strokes)
        self.marks = marks
        self.unread = unread
        self.width, self.height, self.exact = self._surface(surface)
        if not self.exact:
            # No recorded height, so estimate one from the text rather than
            # pinning a guess. A box that is too short hides the end of a long
            # sentence and prints it over the caption; letting it size to its own
            # content instead (height:auto) collapses the percentage-height ink
            # overlay to nothing when Chrome lays the page out for PRINT — the
            # drawing then renders on screen and silently vanishes on paper.
            # A definite height keeps one code path for both.
            self.height = self._estimated_height()

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

    _PADDING = 12 * 2 + 4        # vertical padding, plus a little slack
    _LINE_HEIGHT = 48
    _SIDE_PADDING = 16 * 2 + 3   # padding plus the surface's 1.5px borders
    _LETTER_SPACING = 0.48       # 0.02em at 24px
    _WORD_SPACING = 8.4          # 0.35em at 24px, added to each space
    _WIDE_CHAR = 24.0            # a full em: CJK and accented Latin
    _EMOJI_CHAR = 48.0           # emoji render far wider than an em at this size
    # Control characters and DEL. A tab advances to the next tab stop rather
    # than by its own width, and a control renders as a glyph box — both wider
    # than an em, and both would otherwise take the _WIDE_CHAR guess and clip.
    # Unreachable from real content (a Tab keypress moves focus rather than
    # inserting one), but the estimate has to be an upper bound for every input,
    # not just the plausible ones.
    _CONTROL_CHAR = 48.0
    _SLACK = 0.99                # a hair narrower than reality, so a borderline
                                 # break costs a line here too rather than only
                                 # in the browser

    def _estimated_height(self):
        """Height a legacy box needs, by wrapping the text the way the page will.

        A single average character width cannot do this: Georgia at 24px runs
        from 5px (l) to 23px (W), so an average tuned to lowercase under-counts
        an upper-case sentence by a third and the box clips it — on screen behind
        a scrollbar, in print on top of the caption. These are the real measured
        advances, so ordinary text lands exactly and unknown glyphs round up.
        """
        avail = max(1, (self.width - self._SIDE_PADDING) * self._SLACK)
        lines = 0
        for raw in (self.text or "").split("\n") or [""]:
            # Vertical tab and form feed break the line in CSS, and the rest of
            # the control range renders unpredictably; counting each as its own
            # line is the safe direction.
            for segment in _HARD_BREAKS.split(raw):
                lines += self._wrapped_lines(segment, avail)
        return self._PADDING + max(1, lines) * self._LINE_HEIGHT

    @classmethod
    def _advance(cls, word):
        total = 0.0
        for ch in word:
            code = ord(ch)
            index = code - 32
            if 0 <= index < len(GEORGIA_24):
                total += GEORGIA_24[index]
            elif code < 0x20 or code == 0x7F:
                total += cls._CONTROL_CHAR
            elif code >= 0x1F000:
                total += cls._EMOJI_CHAR
            else:
                total += cls._WIDE_CHAR
            total += cls._LETTER_SPACING
        return total

    @classmethod
    def _wrapped_lines(cls, raw, avail):
        """Greedy wrap, matching how the browser breaks the line.

        Breaks at tabs as well as spaces: a tab is a break opportunity, so
        splitting on spaces alone treats a tab-separated line as one unbreakable
        run and under-counts it by however many times it actually wraps.
        """
        if not raw.strip():
            return 1
        # Capturing split keeps the separators, so each one is charged its own
        # width — a tab advances to a tab stop and is wider than a space.
        parts = _BREAK_POINTS.split(raw)
        lines, used, gap = 1, 0.0, 0.0
        for i, word in enumerate(parts):
            if i % 2:                       # a separator run
                gap = sum(cls._CONTROL_CHAR if c == "\t"
                          else cls._advance(" ") + cls._WORD_SPACING
                          for c in word)
                continue
            width = cls._advance(word)
            space, gap = gap, 0.0
            if width > avail:
                if used:
                    lines += 1
                if word.isascii():
                    # A long Latin run does not break mid-word; it overflows the
                    # box on one line, exactly as the portal renders it.
                    used = avail
                else:
                    # CJK and emoji break between characters, so a long run of
                    # them wraps onto as many lines as it needs.
                    lines += max(0, -(-int(width) // int(avail)) - 1)
                    used = width % avail
                continue
            # `space` is the separator run preceding this word, and it takes
            # room even at the start of a line under pre-wrap — dropping it
            # there under-counts an indented line.
            step = space + width
            if used + step > avail:
                lines += 1
                used = width
            else:
                used += step
        return lines

    @property
    def has_drawing(self):
        return bool(self.svg)

    def _scale(self, target):
        """Shrink-to-fit only — a small drawing is never blown up."""
        return min(1.0, target / self.width)

    @property
    def scale(self):
        return self._scale(SCREEN_TARGET)

    @property
    def print_scale(self):
        return self._scale(PRINT_TARGET)

    @property
    def style_vars(self):
        """Custom properties for markup-replay.css.

        Screen and print get their own scale and their own reserved footprint —
        a transform does not affect layout, so the wrapper has to carry the
        post-scale size, and the two contexts have different room.
        """
        s, p = self.scale, self.print_scale
        return (
            f"--mr-w:{self.width}px;--mr-h:{self.height}px;"
            f"--mr-scale:{s:.4f};--mr-fit-w:{self.width * s:.0f}px;"
            f"--mr-fit-h:{self.height * s:.0f}px;"
            f"--mr-print-scale:{p:.4f};--mr-print-w:{self.width * p:.0f}px;"
            f"--mr-print-h:{self.height * p:.0f}px;"
        )

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
            # Still say something when nothing could be named. Silence here reads
            # as "she marked nothing", which is the opposite of what happened.
            return (f"{self.unread} mark(s) the reader could not name"
                    if self.unread else "")
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

    raw_marks = data.get("marks")
    # Same reason as the stroke points: a non-list here is a 500, not a
    # bad answer. `{"marks": 5}` reaches this from autosave.
    marks = ([m for m in raw_marks if isinstance(m, dict)]
             if isinstance(raw_marks, list) else [])
    try:
        unread = int(data.get("unread") or 0)
    except (TypeError, ValueError, OverflowError):   # 1e400 -> inf -> int() raises
        unread = 0
    typed = bool(getattr(question, "is_write_markup", False))
    if typed:
        text = str(data.get("text", ""))
    elif getattr(question, "is_drawing", False):
        # A drawing has no sentence behind it — she drew on blank paper. And
        # `passage` on these holds the widget's CONFIG, so printing it as the
        # passage stamps {"height": 560} across her picture, in Georgia, on the
        # report that goes to the charter school. Blank paper stays blank.
        text = ""
    else:
        text = question.passage or ""

    replay = MarkupReplay(text, strokes, marks, unread, data.get("surface"), typed=typed)
    # Strokes that yield no drawable ink (every point unusable) are nothing to
    # replay: fall back to the old rendering, which says "[nothing marked on …]"
    # rather than showing an empty box and implying she left it blank.
    return replay if replay.has_drawing else None

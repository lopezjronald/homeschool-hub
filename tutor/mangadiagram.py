"""Deterministic diagram art for math manga panels.

The image model draws lovely characters and cannot count. Across two passes on
Chapter 4 it put 16 berries under "4 x 3 = 12", 48 under "6 rows of 7", and 14
under "13 berries came in" — 35% of diagram panels still wrong after the prompts
were tightened as far as they go. A picture that contradicts its own caption
teaches a nine-year-old the wrong thing, so the panels the MATH depends on are
drawn here instead, from the numbers themselves. Exact by construction, free,
and identical every run.

House rules this module keeps:

* **No text, numerals or speech balloons.** The equations live in the panel
  caption and the dialogue in floating balloons, both overlaid by CSS. Anything
  drawn in here is objects only.
* **The upper third stays empty.** Balloons are anchored at y≈11-20%, so every
  composition is staged in the lower two-thirds against calm background.
* Output goes to the same ``static/manga/<slug>/pN.jpg`` path the generated art
  uses, so nothing downstream — model, template or link-only deploy — changes.

Every helper takes the counts as arguments and draws exactly that many things.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFilter

# Dawn Harbor, warmed for the orchard: parchment ground, teal props, red fruit.
SKY_TOP = (196, 226, 238)
SKY_BOTTOM = (226, 240, 246)
GROUND = (203, 219, 178)
GROUND_DARK = (176, 197, 150)
BERRY = (206, 54, 52)
BERRY_SHADE = (162, 34, 36)
BERRY_LIGHT = (240, 138, 128)
LEAF = (74, 128, 62)
WOOD = (176, 130, 78)
WOOD_DARK = (132, 94, 52)
WOOD_LIGHT = (206, 165, 110)
INK = (61, 48, 38)
GLOW = (255, 214, 130)
CUP = (222, 226, 230)
CUP_DARK = (172, 178, 186)

SPAN_SIZE = {
    "full": (1100, 471),    # 21:9
    "wide": (1100, 619),    # 16:9
    "normal": (1100, 825),  # 4:3
    "tall": (825, 1100),    # 3:4
}


# ---------------------------------------------------------------- canvas ----

def _canvas(span="full"):
    """A staged orchard backdrop with the top third left calm and empty."""
    w, h = SPAN_SIZE[span]
    img = Image.new("RGB", (w, h), SKY_BOTTOM)
    d = ImageDraw.Draw(img)
    horizon = int(h * 0.62)
    for y in range(horizon):
        t = y / max(horizon - 1, 1)
        d.line([(0, y), (w, y)], fill=(
            round(SKY_TOP[0] + (SKY_BOTTOM[0] - SKY_TOP[0]) * t),
            round(SKY_TOP[1] + (SKY_BOTTOM[1] - SKY_TOP[1]) * t),
            round(SKY_TOP[2] + (SKY_BOTTOM[2] - SKY_TOP[2]) * t),
        ))
    d.rectangle([0, horizon, w, h], fill=GROUND)
    d.rectangle([0, horizon, w, horizon + 5], fill=GROUND_DARK)
    return img, d


def _shadow(d, cx, cy, rx, ry=None):
    ry = ry if ry is not None else max(rx // 3, 4)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=GROUND_DARK)


def berry(d, cx, cy, r=17):
    """One unmistakably countable berry: solid, outlined, well separated."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=BERRY, outline=BERRY_SHADE, width=3)
    d.ellipse([cx - r * 0.45 - 1, cy - r * 0.55, cx - r * 0.05, cy - r * 0.18],
              fill=BERRY_LIGHT)
    d.line([(cx, cy - r), (cx + 2, cy - r - 7)], fill=LEAF, width=4)


def _row_positions(n, cx, gap):
    """n evenly spaced x-centres around cx."""
    span = (n - 1) * gap
    return [cx - span / 2 + i * gap for i in range(n)]


def _band_top(h):
    """The lowest y a diagram may touch — everything above belongs to balloons."""
    return h * 0.36


def _fit(img, cols, rows, pad=90, max_gap=96, min_gap=30):
    """The biggest spacing that fits a cols x rows block BELOW the balloon band.

    Diagrams are drawn to the numbers, so their shape changes a lot between
    panels (3x4 upright, 7x6 rack, one long bar). Sizing from the frame instead
    of a fixed constant keeps a small array from swimming in a 21:9 panel and a
    big one from spilling into the top third.
    """
    w, h = img.size
    avail_w = w - pad * 2
    avail_h = (h - _band_top(h)) - pad * 0.8   # everything below the reserved band
    gw = avail_w / max(cols - 1, 1) if cols > 1 else avail_w
    gh = avail_h / max(rows - 1, 1) if rows > 1 else avail_h
    return max(min(gw, gh, max_gap), min_gap)


def _grid(d, cols, rows, cx, cy, gap=48, r=17):
    """Exactly cols x rows berries. The count IS the loop, so it cannot drift."""
    xs = _row_positions(cols, cx, gap)
    ys = _row_positions(rows, cy, gap)
    for y in ys:
        for x in xs:
            berry(d, x, y, r)
    return (min(xs) - r, min(ys) - r, max(xs) + r, max(ys) + r)


# ------------------------------------------------------------ containers ----

def basket(d, cx, base_y, w=132, h=74):
    """A simple open basket, drawn behind its fruit."""
    left, right = cx - w / 2, cx + w / 2
    top = base_y - h
    _shadow(d, cx, base_y + 6, int(w * 0.52))
    d.arc([left - 14, top - 46, right + 14, top + 52], 200, 340, fill=WOOD_DARK, width=7)
    d.polygon([(left, top), (right, top), (right - 14, base_y), (left + 14, base_y)],
              fill=WOOD, outline=WOOD_DARK)
    for i in range(1, 4):
        y = top + (base_y - top) * i / 4
        inset = 14 * (i / 4)
        d.line([(left + inset, y), (right - inset, y)], fill=WOOD_DARK, width=3)
    d.rectangle([left - 4, top - 7, right + 4, top + 7], fill=WOOD_LIGHT, outline=WOOD_DARK)
    return top


def tray(d, x0, y0, x1, y1):
    """A flat wooden tray — the frame for an array."""
    _shadow(d, (x0 + x1) / 2, y1 + 8, int((x1 - x0) * 0.5))
    d.rectangle([x0, y0, x1, y1], fill=WOOD_LIGHT, outline=WOOD_DARK, width=6)
    d.rectangle([x0 + 12, y0 + 12, x1 - 12, y1 - 12], outline=WOOD, width=3)


def cup(d, cx, base_y, w=64, h=62, empty=True):
    left, right, top = cx - w / 2, cx + w / 2, base_y - h
    _shadow(d, cx, base_y + 5, int(w * 0.5))
    d.polygon([(left, top), (right, top), (right - 9, base_y), (left + 9, base_y)],
              fill=CUP, outline=CUP_DARK)
    d.ellipse([left - 3, top - 9, right + 3, top + 9], fill=CUP, outline=CUP_DARK, width=3)
    if not empty:
        d.ellipse([left + 4, top - 2, right - 4, top + 12], fill=BERRY_SHADE)
    return top


# ------------------------------------------------------------- diagrams -----

def equal_groups(counts, span="full", container="basket"):
    """One container per entry, holding exactly that many berries.

    ``equal_groups([3, 3, 4, 3])`` is the unequal-groups beat; ``[3] * 4`` is
    four groups of three. The odd one out is obvious because it is drawn.
    """
    img, d = _canvas(span)
    w, h = img.size
    base = int(h * 0.86)
    gap = min(230, (w - 150) / max(len(counts), 1))
    for cx, n in zip(_row_positions(len(counts), w / 2, gap), counts):
        top = basket(d, cx, base, w=int(gap * 0.62), h=76)
        if n:
            per_row = min(n, 3)
            rows = math.ceil(n / per_row)
            for r_i in range(rows):
                in_row = min(per_row, n - r_i * per_row)
                for x in _row_positions(in_row, cx, 40):
                    berry(d, x, top - 6 - r_i * 34, 15)
    return img


def array(cols, rows, span="full"):
    """A cols x rows rectangle of berries on a tray sized to match."""
    img, d = _canvas(span)
    w, h = img.size
    gap = _fit(img, cols, rows)
    r = max(int(gap * 0.32), 11)
    gw, gh = (cols - 1) * gap, (rows - 1) * gap
    cx = w / 2
    # Sit the block in the lower band: never above the balloon zone, never off
    # the bottom edge.
    pad = r + 26
    cy = max(_band_top(h) + gh / 2 + pad, h - gh / 2 - pad - 24)
    tray(d, cx - gw / 2 - pad, cy - gh / 2 - pad, cx + gw / 2 + pad, cy + gh / 2 + pad)
    _grid(d, cols, rows, cx, cy, gap, r)
    return img


def split_array(cols, rows_kept, rows_added, span="full"):
    """An array cut by a slat: rows_kept above, rows_added below."""
    img, d = _canvas(span)
    w, h = img.size
    total = rows_kept + rows_added
    gap = _fit(img, cols, total)
    r = max(int(gap * 0.32), 10)
    gw, gh = (cols - 1) * gap, (total - 1) * gap
    cx = w / 2
    pad = r + 22
    cy = max(_band_top(h) + gh / 2 + pad, h - gh / 2 - pad - 20)
    tray(d, cx - gw / 2 - pad, cy - gh / 2 - pad, cx + gw / 2 + pad, cy + gh / 2 + pad)
    ys = _row_positions(total, cy, gap)
    for y in ys:
        for x in _row_positions(cols, cx, gap):
            berry(d, x, y, r)
    slat_y = (ys[rows_kept - 1] + ys[rows_kept]) / 2
    d.rectangle([cx - gw / 2 - pad - 12, slat_y - 7, cx + gw / 2 + pad + 12, slat_y + 7],
                fill=WOOD_DARK, outline=INK, width=2)
    return img


def bar_model(units, per_unit, span="full", highlight=None):
    """One long bar cut into ``units`` equal sections of ``per_unit`` berries."""
    img, d = _canvas(span)
    w, h = img.size
    bar_w = w * 0.82
    x0, y1 = (w - bar_w) / 2, int(h * 0.80)
    seg = bar_w / units
    y0 = y1 - 96
    for i in range(units):
        sx = x0 + i * seg
        fill = GLOW if (highlight is not None and i == highlight) else WOOD_LIGHT
        d.rectangle([sx, y0, sx + seg, y1], fill=fill, outline=WOOD_DARK, width=5)
        for x in _row_positions(per_unit, sx + seg / 2, min(36, seg / (per_unit + 0.6))):
            berry(d, x, (y0 + y1) / 2, 13)
    d.rectangle([x0, y0, x0 + bar_w, y1], outline=INK, width=5)
    return img


def compare_bars(unit, times, span="full"):
    """Two bars from the SAME left edge — one unit above, `times` copies below."""
    img, d = _canvas(span)
    w, h = img.size
    seg = (w * 0.84) / times
    x0 = (w - seg * times) / 2
    top_y = int(h * 0.56)
    bot_y = int(h * 0.78)
    bar_h = 74

    def _seg(sx, sy, glow=False):
        d.rectangle([sx, sy, sx + seg, sy + bar_h],
                    fill=GLOW if glow else WOOD_LIGHT, outline=WOOD_DARK, width=5)
        for x in _row_positions(unit, sx + seg / 2, min(34, seg / (unit + 0.6))):
            berry(d, x, sy + bar_h / 2, 12)

    _seg(x0, top_y, glow=True)
    for i in range(times):
        _seg(x0 + i * seg, bot_y)
    d.line([(x0, top_y - 22), (x0, bot_y + bar_h + 22)], fill=INK, width=5)
    return img


def remainder(total, group_size, span="full"):
    """Full groups of ``group_size``, with the true leftover set clearly apart."""
    img, d = _canvas(span)
    w, h = img.size
    groups, left = divmod(total, group_size)
    base = int(h * 0.86)
    slots = groups + (1 if left else 0)
    gap = min(215, (w - 170) / max(slots, 1))
    xs = _row_positions(slots, w / 2, gap)
    for i in range(groups):
        top = basket(d, xs[i], base, w=int(gap * 0.6), h=72)
        for j, x in enumerate(_row_positions(min(group_size, 3), xs[i], 38)):
            berry(d, x, top - 6, 14)
        for j, x in enumerate(_row_positions(max(group_size - 3, 0), xs[i], 38)):
            berry(d, x, top - 38, 14)
    if left:
        cx = xs[-1]
        top = cup(d, cx, base, w=int(gap * 0.42), h=64)
        for x in _row_positions(left, cx, 32):
            berry(d, x, top - 4, 13)
        d.line([(cx - gap * 0.30, base - 118), (cx - gap * 0.30, base + 10)],
               fill=INK, width=4)
    return img


def groups_and_leftover(groups, group_size, leftover, span="full", show_slot=False):
    """An EXPLICIT packing state — not necessarily the correct one.

    Lesson 5 turns on Pawmi getting it wrong first (2 baskets of 4 with 5 still
    loose), so the drawing has to be able to show an unfinished attempt. With
    ``show_slot`` an empty basket sits beside the leftover, which is the
    comparison the caption asks the child to make: is the leftover smaller than
    a basketful, or can another whole basket still be filled?
    """
    img, d = _canvas(span)
    w, h = img.size
    base = int(h * 0.86)
    slots = groups + (1 if leftover else 0) + (1 if show_slot else 0)
    gap = min(210, (w - 170) / max(slots, 1))
    xs = _row_positions(slots, w / 2, gap)
    bw = int(gap * 0.58)

    def _fill(cx, n):
        top = basket(d, cx, base, w=bw, h=72)
        per_row = min(max(n, 1), 3)
        for r_i in range(math.ceil(n / per_row) if n else 0):
            in_row = min(per_row, n - r_i * per_row)
            for x in _row_positions(in_row, cx, 36):
                berry(d, x, top - 6 - r_i * 32, 14)

    for i in range(groups):
        _fill(xs[i], group_size)
    if leftover:
        cx = xs[groups]
        top = cup(d, cx, base, w=int(gap * 0.46), h=66)
        per_row = min(leftover, 3)
        for r_i in range(math.ceil(leftover / per_row)):
            in_row = min(per_row, leftover - r_i * per_row)
            for x in _row_positions(in_row, cx, 30):
                berry(d, x, top - 4 - r_i * 30, 13)
        d.line([(cx - gap * 0.32, base - 128), (cx - gap * 0.32, base + 12)],
               fill=INK, width=4)
    if show_slot:
        _fill(xs[-1], 0)
        cx = xs[-1]
        top = base - 72
        per_row = min(group_size, 3)
        for r_i in range(math.ceil(group_size / per_row)):
            in_row = min(per_row, group_size - r_i * per_row)
            for x in _row_positions(in_row, cx, 36):
                d.ellipse([x - 14, top - 20 - r_i * 32, x + 14, top + 8 - r_i * 32],
                          outline=WOOD_DARK, width=3)
    return img


def two_sets(left_counts, right_counts, span="full"):
    """Two clearly SEPARATED collections of baskets, divided by a rule.

    A comparison is only visible if the eye can tell where one set ends and the
    other begins: an evenly-spaced row of four baskets cannot show "one basket
    versus three". Pass an empty list for a side that is meant to be bare — that
    is how "no groups at all" gets drawn.
    """
    img, d = _canvas(span)
    w, h = img.size
    base = int(h * 0.86)
    d.line([(w / 2, base - 150), (w / 2, base + 18)], fill=INK, width=5)

    def _side(counts, cx_centre, half_w):
        if not counts:
            return
        gap = min(190, (half_w - 60) / max(len(counts), 1))
        bw = int(gap * 0.62)
        for cx, n in zip(_row_positions(len(counts), cx_centre, gap), counts):
            top = basket(d, cx, base, w=bw, h=74)
            per_row = min(max(n, 1), 3)
            for r_i in range(math.ceil(n / per_row) if n else 0):
                in_row = min(per_row, n - r_i * per_row)
                for x in _row_positions(in_row, cx, 38):
                    berry(d, x, top - 6 - r_i * 32, 14)

    _side(left_counts, w * 0.26, w * 0.44)
    _side(right_counts, w * 0.74, w * 0.44)
    return img


def zero_vs_pile(empties, pile, span="full"):
    """N empty shares on one side; an untouched pile still sitting on the other.

    This is the ``6 / 0`` beat: however many empty containers you line up, the
    six berries have not gone anywhere — so there is no answer. The undivided
    pile has to be VISIBLE or the argument is only in the caption.
    """
    img, d = _canvas(span)
    w, h = img.size
    base = int(h * 0.86)
    d.line([(w / 2, base - 150), (w / 2, base + 18)], fill=INK, width=5)
    gap = min(120, (w * 0.42) / max(empties, 1))
    for cx in _row_positions(empties, w * 0.27, gap):
        cup(d, cx, base, w=int(gap * 0.62), h=62)
    crate_w = min(300, w * 0.34)
    x0, x1 = w * 0.74 - crate_w / 2, w * 0.74 + crate_w / 2
    y1 = base
    y0 = y1 - 128
    tray(d, x0, y0, x1, y1)
    per_row = min(pile, 3)
    for r_i in range(math.ceil(pile / per_row)):
        in_row = min(per_row, pile - r_i * per_row)
        for x in _row_positions(in_row, (x0 + x1) / 2, 62):
            berry(d, x, y0 + 42 + r_i * 52, 18)
    return img


def pairs(n, span="full"):
    """n berries walked into twos — the odd one is visibly alone."""
    img, d = _canvas(span)
    w, h = img.size
    full, odd = divmod(n, 2)
    slots = full + odd
    gap = min(150, (w - 150) / max(slots, 1))
    xs = _row_positions(slots, w / 2, gap)
    y = int(h * 0.74)
    for i in range(full):
        d.rounded_rectangle([xs[i] - 54, y - 44, xs[i] + 54, y + 44], 22,
                            fill=WOOD_LIGHT, outline=WOOD_DARK, width=5)
        berry(d, xs[i] - 25, y, 17)
        berry(d, xs[i] + 25, y, 17)
    if odd:
        d.rounded_rectangle([xs[-1] - 54, y - 44, xs[-1] + 54, y + 44], 22,
                            fill=(238, 224, 198), outline=WOOD_DARK, width=5)
        berry(d, xs[-1] - 25, y, 17)
    return img


def heap(n, span="full", cols=None):
    """Exactly n berries, loosely staged but each one separate and countable."""
    img, d = _canvas(span)
    w, h = img.size
    cols = cols or min(n, 10)
    rows = math.ceil(n / cols)
    gap = min(56, (w - 190) / max(cols, 1))
    cy = int(h * 0.72)
    ys = _row_positions(rows, cy, gap * 0.82)
    drawn = 0
    for r_i, y in enumerate(ys):
        in_row = min(cols, n - drawn)
        for x in _row_positions(in_row, w / 2, gap):
            berry(d, x, y, 16)
            drawn += 1
    return img


def take_away(total, removed, span="full", cols=8):
    """total berries, with `removed` of them lifted away and faded."""
    img, d = _canvas(span)
    w, h = img.size
    kept = total - removed
    gap = min(56, (w * 0.44) / max(cols, 1))
    # Two clearly separate zones: what is LEFT on the left, what was EATEN on the
    # right, with a rule between them. Overlapping the two made 24 - 9 unreadable.
    left_cx, right_cx = w * 0.30, w * 0.76
    cy = h * 0.72
    ghosts = []

    def _block(n, cx, keep):
        rows = math.ceil(n / cols) if n else 0
        ys = _row_positions(rows, cy, gap * 0.9)
        drawn = 0
        for y in ys:
            in_row = min(cols, n - drawn)
            for x in _row_positions(in_row, cx, gap):
                if keep:
                    berry(d, x, y, 15)
                else:
                    ghosts.append((x, y))
                drawn += 1

    _block(kept, left_cx, True)
    _block(removed, right_cx, False)
    d.line([(w * 0.53, cy - 110), (w * 0.53, cy + 110)], fill=INK, width=5)
    if ghosts:
        layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(layer)
        for x, y in ghosts:
            gd.ellipse([x - 15, y - 15, x + 15, y + 15],
                       fill=BERRY + (95,), outline=BERRY_SHADE + (150,), width=3)
        img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return img


# ------------------------------------------------------------------ save ----

def save(img, path, quality=88):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.filter(ImageFilter.SMOOTH).save(
        path, format="JPEG", quality=quality, optimize=True, progressive=True)
    return path

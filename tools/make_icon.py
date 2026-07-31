#!/usr/bin/env python3
"""Draw the application icon into src/app/resources/.

The icon this replaced was the 2002 one out of legacy/mfc/res/ed.ico: the words
"W.E. 2002" in maroon, three colours, 16x16 and 32x32, and nothing else. It read
as a blob at any size and said nothing about what the program does.

This one is a shirt, because a shirt is what the program edits -- kits, flags
and squads -- and because a shirt has a silhouette, which a circle does not. At
16 pixels it is a white T on green and still legible; every other candidate
tried (a pitch from above, a disc, a ball) collapsed into the same dark-centred
circle at that size.

The maroon of the stripes is the maroon of the original icon. It is the only
thing carried over.

Drawing happens at 16x the target size and is downsampled with LANCZOS, which
is what keeps the diagonal of the sleeves clean. Small sizes are not scaled
copies of a master: 16 and 24 are drawn without the stripes and with a bigger
neck, because at that size the stripes turn into grey mush.

    python3 tools/make_icon.py

The PNGs are committed. Re-run only to change the art, and look at the result:
this is the one generated thing in the tree that a test cannot judge.
"""

from __future__ import annotations

import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "src" / "app" / "resources"

SIZES = [16, 24, 32, 48, 64, 128, 256]
#: Below this, the shirt is drawn plain.
SIMPLE_BELOW = 32
#: Supersampling factor. 16 is enough that the sleeve diagonals come out clean.
SS = 16

PITCH_TOP = (30, 138, 76)
PITCH_BOT = (17, 94, 51)
PITCH_EDGE = (12, 74, 40)
SHIRT = (247, 250, 248)
#: The maroon of legacy/mfc/res/ed.ico, lifted a little to survive downsampling.
MAROON = (156, 26, 30)

#: The shirt, as fractions of the icon's side. Hem is wider than the chest and
#: the sleeves fall away from the shoulder, which is what stops it reading as a
#: plain cross.
SHIRT_OUTLINE = [
    (0.320, 0.248),                                     # left shoulder
    (0.404, 0.206),                                     # neck, left of
    (0.430, 0.286), (0.462, 0.322),                     # neck, into the dip
    (0.538, 0.322), (0.570, 0.286),                     # neck, out of the dip
    (0.596, 0.206),                                     # neck, right of
    (0.680, 0.248),                                     # right shoulder
    (0.886, 0.404), (0.828, 0.576),                     # right sleeve
    (0.706, 0.508),                                     # right armpit
    (0.738, 0.868), (0.262, 0.868),                     # hem
    (0.294, 0.508),                                     # left armpit
    (0.172, 0.576), (0.114, 0.404),                     # left sleeve
]
#: Left edge and width of each stripe, again as fractions of the side. They
#: start below the neck opening on purpose: run up to the shoulder seam and the
#: white of the neck dip becomes a spike between them.
STRIPES = [(0.374, 0.068), (0.558, 0.068)]
STRIPE_TOP = 0.330
STRIPE_BOTTOM = 0.900


def _gradient(side: int) -> Image.Image:
    """A vertical two-stop gradient, top to bottom."""
    img = Image.new("RGBA", (side, side))
    draw = ImageDraw.Draw(img)
    for y in range(side):
        t = y / max(1, side - 1)
        colour = tuple(int(a + (b - a) * t) for a, b in zip(PITCH_TOP, PITCH_BOT))
        draw.line([(0, y), (side, y)], fill=colour + (255,))
    return img


def _tile(side: int) -> Image.Image:
    """The rounded square, with a darker edge so it reads on a pale panel."""
    radius = int(side * 0.22)
    mask = Image.new("L", (side, side), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, side - 1, side - 1],
                                           radius=radius, fill=255)
    img = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    img.paste(_gradient(side), (0, 0), mask)
    ImageDraw.Draw(img).rounded_rectangle(
        [0, 0, side - 1, side - 1], radius=radius,
        outline=PITCH_EDGE + (255,), width=max(1, int(side * 0.016)))
    return img


def _shirt(side: int, simple: bool) -> Image.Image:
    points = [(x * side, y * side) for x, y in SHIRT_OUTLINE]
    if simple:
        # A wider, shallower neck: at 16 pixels the drawn dip is a third of a
        # pixel deep and disappears, leaving a shoulder line that looks broken.
        points = [(x * side, y * side) for x, y in _widen_neck(SHIRT_OUTLINE)]

    shirt = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    ImageDraw.Draw(shirt).polygon(points, fill=SHIRT + (255,))
    if simple:
        return shirt

    body = Image.new("L", (side, side), 0)
    ImageDraw.Draw(body).polygon(points, fill=255)
    stripes = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    stripe_draw = ImageDraw.Draw(stripes)
    for left, width in STRIPES:
        stripe_draw.rectangle([left * side, STRIPE_TOP * side,
                               (left + width) * side, STRIPE_BOTTOM * side],
                              fill=MAROON + (255,))
    # Clip the stripes to the shirt: the intersection of the two alphas.
    shirt.paste(stripes, (0, 0),
                Image.composite(body, Image.new("L", (side, side), 0),
                                stripes.split()[3]))
    return shirt


def _widen_neck(outline):
    out = []
    for x, y in outline:
        if 0.40 < x < 0.60 and y < 0.36:
            out.append((x, min(y + 0.014, 0.320)))
        else:
            out.append((x, y))
    return out


def icon(size: int) -> Image.Image:
    side = size * SS
    img = _tile(side)
    img.alpha_composite(_shirt(side, size < SIMPLE_BELOW))
    return img.resize((size, size), Image.LANCZOS)


def main() -> int:
    if not OUT.is_dir():
        raise SystemExit(f"nao existe: {OUT}")
    for size in SIZES:
        path = OUT / f"newWe2002-{size}.png"
        icon(size).save(path, optimize=True)
        print(f"{path.relative_to(ROOT)}  {path.stat().st_size} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

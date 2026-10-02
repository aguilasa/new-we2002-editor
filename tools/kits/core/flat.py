"""A kit in 2D: image + palette to RGBA, the community's work bitmap, the palette grid.

PLAN-KITS-PY.md section 3.1.  Everything here returns data -- `FlatImage`
with its bytes, `PaletteEntry` per colour -- and writes nothing; the PNG is
the CLI's.

The colour rule is the console's: a palette entry is BGR555 with the STP bit
on top, and the entry that is all zero with STP clear is the transparent one.
The community's rule -- "index 0, pure black, is transparent" -- is the same
rule seen from the tools: they force black into index 0, so index 0 is the
transparent entry wherever the palette was made that way (SUPERPACK-UNIFORMES
section 2).

The work bitmap is the 256x128 the community edits (SUPERPACK-UNIFORMES
section 2): the uniform image (128x128) on the left, the long-sleeves image
(128x128) on the right, painted with one palette.  Which images and which
palette is `kit_set` (1 = first set, 2 = second) and `figure` (0 = outfield
player, 1 = goalkeeper), the `looks` convention.
"""

from __future__ import annotations

from dataclasses import dataclass

from .errors import KitRefused

KIT_SETS = (1, 2)
FIGURES = (0, 1)
"""0: the outfield player, 1: the goalkeeper (figure numbers of `looks`)."""

UNIFORM = {1: 0, 2: 4}
SLEEVES = {1: 1, 2: 5}
PALETTE_OF = {(1, 0): 2, (1, 1): 3, (2, 0): 6, (2, 1): 7}
"""Record numbers (tex.RECORD_NAMES) of each set's images and of the palette
each figure wears with them."""
FLAG, FLAG_PALETTE, REFEREE = 8, 9, 10

WORK_W, WORK_H = 256, 128

GAME_PAIRS = tuple(
    [(img, PALETTE_OF[(s, f)]) for s in KIT_SETS for f in FIGURES
     for img in (UNIFORM[s], SLEEVES[s])] + [(FLAG, FLAG_PALETTE)])
"""(image record, palette record) of every pairing the game draws: each set's
uniform and sleeves with that set's player and goalkeeper palettes, and the
flag with its own.  The referee is not here: which palette the game gives it
is section 4.5's open question."""

STP = 0x8000


@dataclass(frozen=True)
class PaletteEntry:
    """One colour of a palette, as the file holds it and as it is shown."""

    index: int
    bgr555: int
    rgba: tuple

    @property
    def stp(self) -> bool:
        return bool(self.bgr555 & STP)

    @property
    def transparent(self) -> bool:
        return self.rgba[3] == 0


@dataclass(frozen=True)
class FlatImage:
    """An image painted with a palette: 8-bit `indices`, the 256 `palette`
    colours they index, and the same pixels as RGBA bytes."""

    width: int
    height: int
    indices: bytes
    palette: tuple
    rgba: bytes


def colour(v: int) -> tuple:
    """(r, g, b, a) of one BGR555 halfword; 5 bits widened to 8 by repeating
    the top bits."""
    r, g, b = v & 0x1F, (v >> 5) & 0x1F, (v >> 10) & 0x1F
    alpha = 0 if (v & 0x7FFF) == 0 and not v & STP else 255
    return (r << 3 | r >> 2, g << 3 | g >> 2, b << 3 | b >> 2, alpha)


def palette_rgba(raw: bytes) -> tuple:
    """(r, g, b, a) of every BGR555 halfword in *raw*."""
    return tuple(colour(raw[i] | raw[i + 1] << 8) for i in range(0, len(raw) - 1, 2))


def palette_grid(palette) -> tuple:
    """The 256 `PaletteEntry` of a `tex.Palette`, in index order -- the 16x16
    grid reads row by row, 16 colours to a row."""
    raw = palette.raw
    return tuple(PaletteEntry(i // 2, raw[i] | raw[i + 1] << 8, colour(raw[i] | raw[i + 1] << 8))
                 for i in range(0, len(raw) - 1, 2))


def paint(width: int, height: int, indices: bytes, colours: tuple) -> FlatImage:
    lut = [bytes(c) for c in colours]
    if any(i >= len(lut) for i in set(indices)):
        raise KitRefused("an index of the image is past the %d colours of its palette" % len(lut))
    return FlatImage(width, height, bytes(indices), tuple(colours),
                     b"".join(lut[i] for i in indices))


def _record(items, record: int, what: str, label: str):
    for item in items:
        if item.record == record:
            return item
    raise KitRefused("%s has no %s record %d (it may have been refused by the guard)"
                     % (label, what, record))


def flat(kit, image: int, palette: int) -> FlatImage:
    """Image record *image* of *kit* painted with palette record *palette*."""
    im = _record(kit.images, image, "image", kit.label)
    pal = _record(kit.palettes, palette, "palette", kit.label)
    return paint(im.width, im.height, im.indices, palette_rgba(pal.raw))


def work_bitmap(kit, kit_set: int, figure: int) -> FlatImage:
    """The 256x128: set *kit_set*'s uniform | sleeves, in *figure*'s palette."""
    if kit_set not in KIT_SETS or figure not in FIGURES:
        raise KitRefused("kit_set is 1 or 2 and figure 0 or 1, not %r and %r" % (kit_set, figure))
    left = _record(kit.images, UNIFORM[kit_set], "image", kit.label)
    right = _record(kit.images, SLEEVES[kit_set], "image", kit.label)
    if (left.width + right.width, left.height) != (WORK_W, WORK_H) or left.height != right.height:
        raise KitRefused("%s: uniform %dx%d and sleeves %dx%d do not make %dx%d"
                         % (kit.label, left.width, left.height, right.width, right.height,
                            WORK_W, WORK_H))
    rows = b"".join(left.indices[y * left.width:(y + 1) * left.width]
                    + right.indices[y * right.width:(y + 1) * right.width]
                    for y in range(WORK_H))
    pal = _record(kit.palettes, PALETTE_OF[(kit_set, figure)], "palette", kit.label)
    return paint(WORK_W, WORK_H, rows, palette_rgba(pal.raw))

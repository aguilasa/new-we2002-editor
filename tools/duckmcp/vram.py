"""BGR555 halfwords of the GPU's VRAM to 8-bit (r, g, b), and back.

A VRAM halfword is `r | g << 5 | b << 10`, five bits a channel, plus the
mask bit (STP) on top. The emulator answers `read_vram_region` and
`dump_vram` with a PNG of 8-bit channels, so a caller comparing VRAM with
data off a disc goes PNG pixel -> halfword with `to_halfword`, and the other
way with `to_rgb`.

The rounding is the one every copy in this repository used, so there is
nothing to choose between: down is a plain shift (`channel >> 3`, the low
three bits dropped), up is a plain shift (`five << 3`, no bit replication,
so 31 becomes 248 and not 255). Down after up is exact for all 32768
fifteen-bit values; up after down is exact for any 8-bit channel whose low
three bits are zero, and for a channel the emulator wrote by bit replication
too, since `>> 3` drops exactly those bits. The mask bit does not survive a
PNG either way: `to_halfword` never sets it.
"""

# lineage: _halfword, _five_bits and _disc_five_bits of
# tools/looks/oracle.py (down: >> 3); vram_rows and the palette expansion of
# save_picture in tools/kits/oracle.py (down: >> 3, up: << 3).

import struct

from duckmcp import psx

COLOUR_BITS = (1 << 15) - 1
"""The fifteen colour bits of a halfword."""

MASK_BIT = 1 << 15
"""The sixteenth bit: the mask (semi-transparency) flag, lost in a PNG."""


def split(halfword):
    """`(r, g, b)` five-bit fields of a halfword (mask bit ignored)."""
    return (halfword & 31, (halfword >> 5) & 31, (halfword >> 10) & 31)


def join(r, g, b):
    """The halfword of three five-bit fields."""
    for channel in (r, g, b):
        if not 0 <= channel <= 31:
            raise ValueError("%r is not a five-bit channel" % (channel,))
    return r | g << 5 | b << 10


def five_bits(pixel):
    """An 8-bit `(r, g, b[, a])` pixel down to its three five-bit fields."""
    return tuple(channel >> 3 for channel in pixel[:3])


def to_halfword(pixel):
    """An 8-bit `(r, g, b[, a])` pixel as the halfword's low fifteen bits."""
    r, g, b = pixel[:3]
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def to_rgb(halfword):
    """The 8-bit `(r, g, b)` of a halfword: each five-bit field shifted up."""
    r, g, b = split(halfword)
    return (r << 3, g << 3, b << 3)


def to_rgba(halfword, alpha=255):
    """`to_rgb` with an alpha channel, the shape a palette PNG wants."""
    return to_rgb(halfword) + (alpha,)


def rows_to_halfwords(rows):
    """PNG rows of pixels (what `png.read_png` returns) as rows of halfwords."""
    return [[to_halfword(pixel) for pixel in row] for row in rows]


def rows_to_bytes(rows):
    """PNG rows of pixels as rows of little-endian halfword bytes.

    The shape of a VRAM dump in memory: `bytes.find` over a row searches for a
    rectangle of the disc in it.
    """
    return [struct.pack("<%dH" % len(row), *(to_halfword(p) for p in row))
            for row in rows]


def halfwords_to_rows(halfwords, width):
    """A flat sequence of halfwords as rows of `width` 8-bit `(r, g, b)`."""
    if width <= 0 or len(halfwords) % width:
        raise ValueError("%d halfword(s) do not make rows of %d"
                         % (len(halfwords), width))
    return [[to_rgb(h) for h in halfwords[at:at + width]]
            for at in range(0, len(halfwords), width)]


def self_check():
    """The round trips over every fifteen-bit value, and the edges.

    Returns one `(name, passed, detail)` per assertion.
    """
    out = []
    broken = [h for h in range(1 << 15) if to_halfword(to_rgb(h)) != h]
    out.append(("to_halfword(to_rgb(h)) == h for all 32768 values",
                not broken, broken[:8]))
    split_broken = [h for h in range(1 << 15) if join(*split(h)) != h]
    out.append(("join(split(h)) == h for all 32768 values",
                not split_broken, split_broken[:8]))
    out.append(("the mask bit is dropped, never kept",
                to_halfword(to_rgb(MASK_BIT | 1234)) == 1234
                and split(MASK_BIT) == (0, 0, 0), ""))
    out.append(("white is 248, not 255 (no bit replication)",
                to_rgb(COLOUR_BITS) == (248, 248, 248), to_rgb(COLOUR_BITS)))
    replicated = [(v << 3 | v >> 2) for v in range(32)]
    out.append(("a bit-replicated channel still comes back to its five bits",
                [five_bits((c, c, c))[0] for c in replicated]
                == list(range(32)), ""))
    out.append(("red is the low field, blue the high",
                to_halfword((255, 0, 0)) == 31
                and to_halfword((0, 0, 255)) == 31 << 10, ""))
    out.append(("alpha is ignored on the way down",
                to_halfword((8, 16, 24, 0)) == to_halfword((8, 16, 24)), ""))
    rows = halfwords_to_rows(list(range(12)), 4)
    out.append(("rows round-trip through halfwords and bytes",
                rows_to_halfwords(rows) == [[0, 1, 2, 3], [4, 5, 6, 7],
                                            [8, 9, 10, 11]]
                and rows_to_bytes(rows)[1] == struct.pack("<4H", 4, 5, 6, 7),
                ""))
    try:
        join(32, 0, 0)
        out.append(("join refuses a six-bit channel", False, ""))
    except ValueError:
        out.append(("join refuses a six-bit channel", True, ""))
    out.append(("a full VRAM row is VRAM_WIDTH halfwords of bytes",
                len(rows_to_bytes([[(0, 0, 0)] * psx.VRAM_WIDTH])[0])
                == 2 * psx.VRAM_WIDTH, ""))
    return out

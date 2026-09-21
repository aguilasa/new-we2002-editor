#!/usr/bin/env python3
"""The screen's sprites, built off the disc: title, icon, boxes, bar, plate, arrows.

What the game draws on LOOKS SET that is an image and not a polygon is a
SPRITE -- a textured rectangle the list hands the GPU with a point, a size, a
texel corner `uv`, a CLUT and the page in force (`oracle.py --scenery`,
LOOKS-TASK-31).  The texels are the disc's: EDT_2D.BIN holds the screen's own
art and DAT2D.BIN the rest, and the eight CLUTs are all in DAT2D.BIN.  This
module lays those containers out in VRAM the way the console does, and cuts a
sprite out of them the way the GPU does:

  * a 4-bit page holds four texels a halfword, the lowest nibble first, and a
    texel is an index into sixteen CLUT entries;
  * an entry that is the halfword 0x0000 -- black with the mask bit clear --
    is TRANSPARENT, and nothing is drawn there.  It is the entry, not index 0,
    that decides: `texture.read_palette` already reads the rule;
  * unless the command is "raw", each channel is modulated by the sprite's own
    colour, 128 being one: `min(255, texel * colour / 128)`.  The arrows beside
    the cursor pulse exactly this way, their colour changing frame to frame
    (LOOKS-TASK-36).

Nothing here knows where on the screen a sprite goes; that is the table's.
And nothing knows an address: pages and CLUTs arrive as VRAM coordinates, the
groups are `layout.SCREEN_SPRITES`, and the files are read through the guard.

Semi-transparent sprites are REFUSED.  None of the static ones is, and drawing
one opaque would be a picture that disagrees with the game and says nothing.
"""

from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402
import texture  # noqa: E402

SKIP = 77

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pes2"))

FILES = ("EDT_2D", "DAT2D")
"""The containers a sprite's texels are read from, by `layout` name.

The two hold disjoint parts of VRAM on this disc (LOOKS-TASK-31); where two
records would cover one halfword, the first file named here wins."""

TEXELS_PER_HALFWORD = {4: 4, 8: 2, 16: 1}
"""How many texels one VRAM halfword holds, by the page's colour depth."""

NEUTRAL = 128
"""The colour a sprite is drawn at unchanged: modulation divides by it."""


class BadSprite(Exception):
    """A sprite this module will not draw, with the reason."""


def vram_of(containers: dict) -> dict:
    """{(x, y): halfword} of every image record of *containers*, in VRAM.

    *containers* maps a file's bytes by the names of `FILES`, read off the
    disc by whoever calls -- through `iso_source`, which is the guard.  The
    halfwords are whole, mask bit included: the disc keeps it, and a VRAM read
    back through the fork does not.
    """
    import lzss

    held = {}
    for name in FILES:
        data = containers[name]
        for record in texture.images(data):
            plain, _used = lzss.decompress(data, record.offset)
            for row in range(record.h):
                for col in range(record.w):
                    at = 2 * (row * record.w + col)
                    key = (record.x + col, record.y + row)
                    if key in held or at + 1 >= len(plain):
                        continue
                    held[key] = plain[at] | plain[at + 1] << 8
    return held


def clut_of(dat2d: bytes, clut, colours: int) -> list:
    """The RGBA entries a CLUT at VRAM *clut* holds, from DAT2D.BIN's palettes."""
    try:
        record, first = texture.window_for(texture.palettes(dat2d), clut[0],
                                           clut[1], colours)
    except texture.NoPalette as exc:
        raise BadSprite("no palette of DAT2D.BIN covers the CLUT at %r: %s"
                        % (tuple(clut), exc)) from exc
    return texture.read_palette(dat2d, record, colours, first)


def texel(vram: dict, page, bits: int, u: int, v: int) -> int:
    """The index (or colour) at texel (u, v) of a page, or `BadSprite`."""
    per = TEXELS_PER_HALFWORD.get(bits)
    if per is None:
        raise BadSprite("a %d-bit page is not one this screen draws" % bits)
    key = (page[0] + u // per, page[1] + v)
    if key not in vram:
        raise BadSprite("no image on the disc holds VRAM %r, which the "
                        "texel (%d, %d) of page %r samples"
                        % (key, u, v, tuple(page)))
    word = vram[key]
    if per == 1:
        return word
    width = 16 // per
    return (word >> (width * (u % per))) & ((1 << width) - 1)


def image(sprite: dict, vram: dict, clut: list) -> bytes:
    """The sprite as RGBA, row by row, `size[0] * size[1] * 4` bytes.

    Transparent where the CLUT entry is (alpha 0), modulated by the sprite's
    colour unless the command is raw.  *clut* is the entries `clut_of` read.
    """
    if sprite.get("semi"):
        raise BadSprite("a semi-transparent sprite at %r is not drawn: none of "
                        "the measured static ones is" % (sprite["point"],))
    (width, height), (u0, v0) = sprite["size"], sprite["uv"]
    colour = sprite.get("colour", (NEUTRAL,) * 3)
    raw = sprite.get("raw", False)
    out = bytearray(4 * width * height)
    for row in range(height):
        for col in range(width):
            index = texel(vram, sprite["page"], sprite["bits"], u0 + col,
                          v0 + row)
            if index >= len(clut):
                raise BadSprite("texel index %d past a %d-entry CLUT"
                                % (index, len(clut)))
            r, g, b, a = clut[index]
            if not raw:
                r, g, b = (min(255, one * tint // NEUTRAL)
                           for one, tint in zip((r, g, b), colour))
            at = 4 * (row * width + col)
            out[at:at + 4] = bytes((r, g, b, a))
    return bytes(out)


def paint(picture: bytearray, size, point, width: int, height: int,
          rgba: bytes) -> int:
    """Lay an RGBA sprite on an RGB *picture* at *point*; the pixels drawn.

    Opaque texels replace what is under them, transparent ones leave it, and
    what falls off the picture is clipped -- the GPU clips to the drawing area
    the same way.
    """
    frame_w, frame_h = size
    drawn = 0
    for row in range(height):
        y = point[1] + row
        if not 0 <= y < frame_h:
            continue
        for col in range(width):
            x = point[0] + col
            if not 0 <= x < frame_w:
                continue
            at = 4 * (row * width + col)
            if not rgba[at + 3]:
                continue
            here = 3 * (y * frame_w + x)
            picture[here:here + 3] = rgba[at:at + 3]
            drawn += 1
    return drawn


class Art:
    """The two containers laid out in VRAM once, and sprites cut from them."""

    __slots__ = ("vram", "dat2d", "_cluts")

    def __init__(self, containers: dict):
        self.vram = vram_of(containers)
        self.dat2d = containers["DAT2D"]
        self._cluts = {}

    def clut(self, sprite: dict) -> list:
        colours = 1 << sprite["bits"]
        key = (tuple(sprite["clut"]), colours)
        if key not in self._cluts:
            self._cluts[key] = clut_of(self.dat2d, sprite["clut"], colours)
        return self._cluts[key]

    def image(self, sprite: dict) -> bytes:
        return image(sprite, self.vram, self.clut(sprite))

    def paint(self, picture: bytearray, size, sprites) -> int:
        """Every sprite of *sprites* onto *picture*, in order; pixels drawn."""
        drawn = 0
        for one in sprites:
            width, height = one["size"]
            drawn += paint(picture, size, one["point"], width, height,
                           self.image(one))
        return drawn


def group_of(sprite: dict) -> str | None:
    """Which of `layout.SCREEN_SPRITES` a sprite belongs to, or None.

    By page and CLUT.  The plate shares its page with the shirt boxes and is
    told apart by a CLUT that is one of `layout.PLATE_CLUT`'s.
    """
    page, clut = tuple(sprite["page"]), tuple(sprite["clut"])
    for name, want_page, want_clut in layout.SCREEN_SPRITES:
        if page != want_page:
            continue
        if want_clut is None:
            if clut in layout.PLATE_CLUT.values():
                return name
        elif clut == tuple(want_clut):
            return name
    return None


def static(sprites, plate: str) -> list:
    """The static sprites of a measured table, the plate's CLUT from *plate*.

    The CLUT the table recorded for the plate is NOT used: it is the state's,
    and the screen needs the position's (`layout.PLATE_CLUT`).  A position no
    state was measured in is refused -- the plate would come out in somebody
    else's colours with nothing to say so.
    """
    if plate not in layout.PLATE_CLUT:
        raise BadSprite("no plate CLUT was measured for %r; the two states "
                        "hold %s" % (plate, ", ".join(sorted(layout.PLATE_CLUT))))
    out = []
    for one in sprites:
        name = group_of(one)
        if name is None:
            continue
        if name == "plate":
            one = dict(one, clut=list(layout.PLATE_CLUT[plate]))
        out.append(dict(one, group=name))
    return out


# -- the self-check ---------------------------------------------------------

def _synthetic():
    """Two containers with one 4-bit image and one palette, built in memory.

    The image is 2 halfwords wide and 2 rows: eight texels a row, the indices
    0..7 and then 8..15.  The palette's entry 0 is 0x0000, transparent; entry
    1 is black WITH the mask bit, opaque; the rest are greys.
    """
    import lzss

    halfwords = [0x3210, 0x7654, 0xBA98, 0xFEDC]  # not-an-address: packed nibbles
    plain = b"".join(struct.pack("<H", one) for one in halfwords)
    entries = [0x0000, 0x8000] + [(i << 10) | (i << 5) | i  # not-an-address: BGR555
                                  for i in range(2, 15)] + [0x7FFF]  # not-an-address: white
    palette = b"".join(struct.pack("<H", one) for one in entries)
    edt = _container([(texture.KIND_IMAGE, 40, 8, 2, 2, lzss.compress(plain))])
    dat = _container([(texture.KIND_CLUT, 16, 490, 16, 1, palette)])
    return {"EDT_2D": edt, "DAT2D": dat}


def _container(entries, bank: int = 1) -> bytes:
    """A container holding *entries* -- (kind, x, y, w, h, payload) -- and the
    record list that indexes them, laid out one bank in like the disc's.

    `texture.build_container` builds palettes only; a sprite needs an image
    record too, and one written here in the same shape is read back by the
    same `texture.images`, which is the point."""
    body = bytearray(bank * layout.RECORD_BANK)
    records = []
    for kind, x, y, w, h, payload in entries:
        records.append((kind, x, y, w, h, len(body)))
        body += payload
    tag = layout.RECORD_TAG_BASE + bank
    table = bytearray()
    for kind, x, y, w, h, offset in records:
        table += struct.pack("<8H", kind, x, y, w, h, 0,
                             offset - bank * layout.RECORD_BANK, tag)
    table += struct.pack("<H", layout.RECORD_LIST_END)
    return bytes(body + table)


def self_check(verbose: bool = True) -> int:
    return harness.run("sprites.py", _checks, verbose=verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    containers = attempt("build two synthetic containers", _synthetic)
    if containers is None:
        return
    art = attempt("lay them out in VRAM", lambda: Art(containers))
    if art is None:
        return
    ok("four halfwords land where the record says",
       sorted(art.vram) == [(40, 8), (40, 9), (41, 8), (41, 9)],
       "%r" % sorted(art.vram))
    ok("the lowest nibble is the first texel",
       [texel(art.vram, (40, 8), 4, u, 0) for u in range(8)]
       == list(range(8)))
    sprite = {"point": (0, 0), "size": (8, 2), "uv": (0, 0),
              "clut": (16, 490), "page": (40, 8), "bits": 4,
              "colour": (NEUTRAL,) * 3, "raw": False, "semi": False}
    rgba = attempt("cut the sprite", lambda: art.image(sprite))
    if rgba is None:
        return
    ok("entry 0x0000 is transparent", rgba[3] == 0)
    ok("black WITH the mask bit is opaque, not transparent",
       rgba[4:8] == bytes((0, 0, 0, 255)), "%r" % (rgba[4:8],))
    grey = rgba[8:12]
    ok("an entry of 2 in five bits reads 16 in eight", grey[:3] == bytes(
        (16, 16, 16)), "%r" % (grey,))
    dim = attempt("cut it at colour 64", lambda: art.image(
        dict(sprite, colour=(64, 64, 64))))
    ok("colour 64 halves the texel", dim is not None and dim[8:11]
       == bytes((8, 8, 8)), "%r" % (dim[8:12] if dim else None,))
    bright = art.image(dict(sprite, colour=(255, 255, 255)))
    ok("modulation saturates at 255 rather than wrapping",
       bright[4 * 15:4 * 15 + 3] == bytes((255, 255, 255)),
       "%r" % (bright[60:64],))
    raw = art.image(dict(sprite, colour=(64, 64, 64), raw=True))
    ok("a raw sprite is not modulated", raw[8:11] == bytes((16, 16, 16)))

    picture = bytearray(3 * 10 * 3)
    for i in range(0, len(picture), 3):
        picture[i:i + 3] = bytes((1, 2, 3))
    drawn = paint(picture, (10, 3), (5, 1), 8, 2, rgba)
    ok("paint clips at the right edge and skips transparent texels",
       drawn == 5 - 1 + 5, "drew %d" % drawn)
    ok("under the transparent texel the picture is untouched",
       picture[3 * (1 * 10 + 5):3 * (1 * 10 + 5) + 3] == bytes((1, 2, 3)))

    table = [dict(sprite, page=[576, 0], clut=[208, 499]),  # not-an-address: VRAM
             dict(sprite, page=[576, 0], clut=[176, 496]),  # not-an-address: VRAM
             dict(sprite, page=[704, 256], clut=[0, 497])]  # not-an-address: VRAM
    kept = static(table, "GK")
    ok("the font is not a static sprite", len(kept) == 2,
       "%r" % [one["group"] for one in kept])
    ok("the plate takes the POSITION's CLUT, not the state's",
       kept[0]["group"] == "plate"
       and tuple(kept[0]["clut"]) == layout.PLATE_CLUT["GK"],
       "%r" % (kept[0],))

    # -- red: what must not pass ------------------------------------------
    try:
        static(table, "SW")
    except BadSprite:
        ok("a position no state was measured in is refused", True)
    else:
        ok("a position no state was measured in is refused", False)
    try:
        art.image(dict(sprite, uv=(16, 0)))
    except BadSprite:
        ok("a texel no image holds is refused, not drawn black", True)
    else:
        ok("a texel no image holds is refused, not drawn black", False)
    try:
        art.image(dict(sprite, clut=(32, 490)))
    except BadSprite:
        ok("a CLUT no palette covers is refused", True)
    else:
        ok("a CLUT no palette covers is refused", False)
    try:
        art.image(dict(sprite, semi=True))
    except BadSprite:
        ok("a semi-transparent sprite is refused", True)
    else:
        ok("a semi-transparent sprite is refused", False)
    swapped = bytes(rgba[4 * 1:4 * 2] + rgba[0:4])
    ok("the transparent and the opaque black are told apart",
       swapped != rgba[0:8])


# -- against the disc -------------------------------------------------------

def containers_of(disc) -> dict:
    """The two files by `FILES` name, read through the guard."""
    return {name: disc.read(getattr(layout, name)) for name in FILES}


ARROWS = {"left": (128, 240), "right": (128, 248)}  # not-an-address: uv on the page
"""The texel corner of each arrow on `layout.ARROW_PAGE`, measured."""

ARROW_CLUT = (80, 497)  # not-an-address: VRAM
ARROW_SIZE = (8, 8)


def arrow_sprite(side: str, point, colour=NEUTRAL) -> dict:
    """One arrow as a sprite, at *point*, pulsing at *colour*."""
    return {"point": list(point), "size": list(ARROW_SIZE),
            "uv": list(ARROWS[side]), "clut": list(ARROW_CLUT),
            "page": list(layout.ARROW_PAGE), "bits": 4,
            "colour": [colour] * 3, "raw": False, "semi": False, "blend": 0}


def _check_image(image_path: str) -> int:
    """`--check-image`: every static group and both arrows cut off the disc."""
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        art = Art(containers_of(disc))
    problems = 0
    for name, page, clut in layout.SCREEN_SPRITES:
        cluts = ([clut] if clut is not None
                 else sorted(layout.PLATE_CLUT.values()))
        for one in cluts:
            entries = attempt_clut(art, one)
            held = sum(1 for (x, y) in art.vram
                       if page[0] <= x < page[0] + 64 and page[1] <= y < page[1] + 256)
            print("  %-12s page %r clut %r: %s, %d halfword(s) of the page held"
                  % (name, page, tuple(one),
                     "%d entries" % len(entries) if entries else "NO PALETTE",
                     held))
            problems += not entries or not held
    shapes = {}
    for side in ARROWS:
        rgba = art.image(arrow_sprite(side, (0, 0)))
        shapes[side] = [rgba[4 * i + 3] != 0 for i in range(64)]
        print("  arrow %-5s uv %r: %d of 64 texels opaque"
              % (side, ARROWS[side], sum(shapes[side])))
        problems += not any(shapes[side])
    mirrored = all(shapes["left"][row * 8 + col]
                   == shapes["right"][row * 8 + 7 - col]
                   for row in range(8) for col in range(8))
    print("  the left arrow %s the right one mirrored"
          % ("is" if mirrored else "is NOT"))
    problems += not mirrored
    print("sprites --check-image: %d problem(s)" % problems)
    return 1 if problems else 0


def attempt_clut(art: Art, clut) -> list:
    try:
        return clut_of(art.dat2d, clut, 16)
    except BadSprite as exc:
        print("  %s" % exc)
        return []


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[1] == "--check-image":
        import iso_source

        if len(argv) > 2:
            return _check_image(argv[2])
        try:
            image_path = iso_source.image_from_env()
        except RuntimeError as exc:
            print("sprites --check-image: skipped -- %s" % exc)
            return SKIP
        return _check_image(image_path)
    return self_check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

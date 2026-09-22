#!/usr/bin/env python3
"""The game's font: from a character code to the sprite the screen draws.

LOOKS SET writes its rows, its values, `SHIRT N` and the plate through one
routine, `layout.SCREEN_GLYPH`, which fills a `GsSPRITE` per character: the
page and CLUT are always the same (`layout.GLYPH_PAGE`, `GLYPH_CLUT`), the
height is always 12, and the code decides three things -- the texel column
`u`, the texel row `v` and the width.  Read off the routine on 2026-09-22
(LOOKS-TASK-37), for the codes this screen draws, 32 to 126:

  * `u` and the width are a PAIR of bytes of a table in the overlay,
    `layout.GLYPH_TABLE`, indexed by `code - 32`.  Read from the disc here;
  * `v` is a band of codes, each band one row of glyphs on the page --
    `V_BANDS` below, transcribed from the chain of `sltiu`/`addiu` pairs that
    stores the byte at 0xC7 of the sprite;
  * a space has a width and draws nothing: 13 of the 134 draw calls of a
    frame are spaces, and the list holds 121 sprites.

Transcribing code is only safe against the code it was read from, so the rule
is REFUSED unless the routine's bytes on the disc hash to
`layout.GLYPH_ROUTINE_DIGEST` -- the same bytes on the Japanese disc, the
English disc and the running game's RAM.  The table is the Japanese disc's,
through the guard (`/SELECTC.BIN` differs between the discs, in its text).

How far the pen moves after a glyph is its width plus the SPACING of the text
object being printed -- byte 14 of the object `SCREEN_PRINT` receives (2 for
the labels, 1 for `Unknown`, 0 for `SHIRT N` and the digits).  Where a string
STARTS inside its object's box is alignment, and that is LOOKS-TASK-38's.

What the routine does with the other codes -- 161 to 223 by arithmetic, and a
search of two-byte Shift-JIS codes above that -- is recorded in the plan and
NOT implemented: no string of this screen reaches it, so nothing could check a
transcription of it, and a code outside the range is refused.
"""

from __future__ import annotations

import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402

SKIP = 77

FIRST, LAST = 32, 126
"""The codes the rule answers: the ASCII this screen prints."""

V_BANDS = (
    (33, 0),
    (34, 218),
    (48, 230),
    (58, 146),
    (64, 230),
    (65, 242),
    (75, 146),
    (91, 158),
    (97, 230),
    (103, 158),
    (123, 170),
    (128, 230),
)
"""(first code NOT in the band, v) in code order, read off the routine.

From 0x8010BE68 on: `sltiu v0, v1, LIMIT` then, in the delay slot or the
branch target, `addiu v0, zero, V` and `sb v0, 0xc7(t1)`.  Below 33 the store
is `sb zero`: the space's row is 0, and it draws nothing anyway.  So `A` to
`J` (65 to 74) sit on the digits' row, 146, and `K` to `Z` on the next, 158 --
the page packs the font eleven-odd glyphs a row, not alphabet by alphabet."""

TABLE_PAIRS = LAST - FIRST + 1


class BadGlyph(Exception):
    """A code, a routine or a table this module will not draw from."""


def routine_offset() -> tuple:
    """(start, end) of the glyph routine inside `/SELECTC.BIN`."""
    start, end = layout.GLYPH_ROUTINE
    return (start - layout.SELECTC_BASE, end - layout.SELECTC_BASE)


def table_of(selectc: bytes) -> bytes:
    """The (u, width) pairs out of the overlay, or `BadGlyph`.

    Refused unless the routine the bands were transcribed from is the one in
    *selectc*: a table read next to other code would be indexed by rules
    nobody has read.
    """
    start, end = routine_offset()
    routine = selectc[start:end]
    got = hashlib.sha256(routine).hexdigest()
    if len(routine) != end - start or got != layout.GLYPH_ROUTINE_DIGEST:
        raise BadGlyph("the glyph routine at %#x of this overlay hashes to %s, "
                       "and V_BANDS were read from %s -- a different routine, "
                       "so the transcription does not apply"
                       % (start, got[:16], layout.GLYPH_ROUTINE_DIGEST[:16]))
    at = layout.GLYPH_TABLE - layout.SELECTC_BASE
    table = selectc[at:at + 2 * TABLE_PAIRS]
    if len(table) != 2 * TABLE_PAIRS:
        raise BadGlyph("the overlay ends inside the glyph table")
    return table


class Font:
    """The rule for one table: code -> (u, v, width), and text -> sprites."""

    __slots__ = ("table",)

    def __init__(self, table: bytes):
        if len(table) != 2 * TABLE_PAIRS:
            raise BadGlyph("a glyph table holds %d pairs, not %d bytes"
                           % (TABLE_PAIRS, len(table)))
        self.table = table

    def glyph(self, code: int) -> tuple:
        """(u, v, width) of one code, or `BadGlyph` outside 32..126."""
        if not FIRST <= code <= LAST:
            raise BadGlyph("code %#x is outside the %d..%d the glyph rule was "
                           "read and checked for" % (code, FIRST, LAST))
        index = code - FIRST
        u, width = self.table[2 * index], self.table[2 * index + 1]
        v = next(value for limit, value in V_BANDS if code < limit)
        return (u, v, width)

    def run(self, text: str, point, spacing: int, colour) -> list:
        """*text* laid out from *point*, as the sprites the game would draw.

        The pen starts at *point* -- the top-left of the first glyph, in
        native pixels -- and moves on by each glyph's width plus *spacing*.
        A space moves it and draws nothing, as the game's list shows.
        """
        out, x = [], point[0]
        for char in text:
            u, v, width = self.glyph(ord(char))
            if char != " " and width:
                out.append({"point": [x, point[1]],
                            "size": [width, layout.GLYPH_HEIGHT],
                            "uv": [u, v], "clut": list(layout.GLYPH_CLUT),
                            "page": list(layout.GLYPH_PAGE), "bits": 4,
                            "colour": list(colour), "raw": False,
                            "semi": False, "blend": 0, "code": ord(char)})
            x += width + spacing
        return out

    def width(self, text: str, spacing: int) -> int:
        """How far *text* moves the pen -- the measuring pass's answer."""
        return sum(self.glyph(ord(char))[2] + spacing for char in text)


def font_of(disc) -> Font:
    """The rule off the Japanese disc, through the guard."""
    return Font(table_of(disc.read(layout.SELECTC)))


# -- the self-check ---------------------------------------------------------

def _toy_table() -> bytes:
    """A table where code c has u = c and width = c % 7 + 3."""
    return bytes(value for code in range(FIRST, LAST + 1)
                 for value in (code, code % 7 + 3))


def self_check(verbose: bool = True) -> int:
    return harness.run("glyphs.py", _checks, verbose=verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    font = attempt("build a font on a toy table", lambda: Font(_toy_table()))
    if font is None:
        return
    ok("u and width come from the pair of the code",
       font.glyph(ord("A"))[0] == 65 and font.glyph(ord("A"))[2] == 65 % 7 + 3)
    ok("A..J share the digits' row and K..Z the next",
       font.glyph(ord("A"))[1] == font.glyph(ord("0"))[1] == 146
       and font.glyph(ord("J"))[1] == 146 and font.glyph(ord("K"))[1] == 158
       and font.glyph(ord("Z"))[1] == 158)
    ok("lower case from g sits on row 170, a..f on 158",
       font.glyph(ord("f"))[1] == 158 and font.glyph(ord("g"))[1] == 170)
    ok("the bands are in code order and end past 126",
       [limit for limit, _ in V_BANDS] == sorted(limit for limit, _ in V_BANDS)
       and V_BANDS[-1][0] > LAST)
    blank = bytearray(_toy_table())
    blank[2 * (ord("@") - FIRST) + 1] = 0
    empty = Font(bytes(blank))
    ok("a code of width 0 draws nothing and does not move the pen",
       empty.run("@", (0, 0), 2, (128,) * 3) == []
       and empty.width("@", 0) == 0)
    drawn = font.run("A B", (10, 20), 2, (112, 112, 240))
    ok("a space moves the pen and draws nothing", len(drawn) == 2)
    wa, ws = font.glyph(ord("A"))[2], font.glyph(ord(" "))[2]
    ok("the pen moves by width plus the object's spacing",
       drawn[1]["point"] == [10 + wa + 2 + ws + 2, 20], "%r" % (drawn,))
    ok("every glyph is 12 tall, on the font's page, in its CLUT",
       all(one["size"][1] == 12 and tuple(one["page"]) == layout.GLYPH_PAGE
           and tuple(one["clut"]) == layout.GLYPH_CLUT for one in drawn))
    ok("the measuring pass agrees with the drawing one",
       font.width("A B", 2) == wa + ws + font.glyph(ord("B"))[2] + 3 * 2)

    # -- red: what must not pass ------------------------------------------
    for code in (31, 127, 0x82):  # not-an-address: character codes
        try:
            font.glyph(code)
        except BadGlyph:
            ok("code %#x, outside what was read, is refused" % code, True)
        else:
            ok("code %#x, outside what was read, is refused" % code, False)
    try:
        table_of(bytes(0x20000))  # not-an-address: a file size
    except BadGlyph:
        ok("an overlay whose routine is not the transcribed one is refused",
           True)
    else:
        ok("an overlay whose routine is not the transcribed one is refused",
           False)
    try:
        Font(_toy_table()[:-2])
    except BadGlyph:
        ok("a table one pair short is refused", True)
    else:
        ok("a table one pair short is refused", False)


# -- against the disc -------------------------------------------------------

def _check_image(image_path: str) -> int:
    """`--check-image`: the rule off the Japanese overlay, and what it says."""
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        font = font_of(disc)
    print("glyphs: the routine at %#x-%#x of %s is the one V_BANDS were read "
          "from; the table at %#x holds %d pairs"
          % (routine_offset() + (layout.SELECTC,
                                 layout.GLYPH_TABLE - layout.SELECTC_BASE,
                                 TABLE_PAIRS)))
    problems, empty = 0, []
    for limit_index, (limit, v) in enumerate(V_BANDS):
        first = V_BANDS[limit_index - 1][0] if limit_index else FIRST
        codes = range(max(first, FIRST), min(limit, LAST + 1))
        text = "".join(chr(code) for code in codes)
        widths = [font.glyph(code)[2] for code in codes]
        print("  v %3d: %-26r widths %s" % (v, text, widths))
        empty += [chr(code) for code in codes if not font.glyph(code)[2]]
    # Width 0 is the table's own "no glyph" -- the routine draws nothing and
    # does not move the pen -- and is printed, not failed.  What would be a
    # problem is a letter or a digit without one: the screen draws all of them.
    print("  no glyph (width 0): %s" % " ".join(empty))
    missing = [char for char in empty if char.isalnum()]
    problems += len(missing)
    if missing:
        print("  FAIL  letters or digits without a glyph: %s" % " ".join(missing))
    print("glyphs --check-image: %d problem(s)" % problems)
    return 1 if problems else 0


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[1] == "--check-image":
        import iso_source

        if len(argv) > 2:
            return _check_image(argv[2])
        try:
            image_path = iso_source.image_from_env()
        except RuntimeError as exc:
            print("glyphs --check-image: skipped -- %s" % exc)
            return SKIP
        return _check_image(image_path)
    return self_check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

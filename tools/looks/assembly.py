#!/usr/bin/env python3
"""A tuple of LOOKS to a draw list: which primitive, which image, which window.

Provenance (plan section 3.4): measured, on the running game.  Every row of the
table below came out of `oracle.py --assembly`, which walks a field from the
bottom of its range to the top and reads the section it owns after every press.

## What the game actually does, and what that makes this module

**The geometry never changes.**  Not one vertex moved in any field's walk, and
no field swaps a section for another: what a LOOKS field rewrites is the
**CLUT id** of some primitives, or the **`v`** of some primitives, and nothing
else.  So a draw list is the disc's own sections with a small, measured edit
applied -- not a choice between meshes.

    SKIN      the CLUT's ROW      +0x40 a step   the bare-skin primitives
    H.COL     the CLUT's COLUMN   +1             seven head primitives
    H.F.COL.  the CLUT's COLUMN   +1             the two beard primitives
    BOOTS     the CLUT's COLUMN   +1             42 primitives of each foot
    FACE      the `v`             +16 a band     the two beard primitives

...with **one exception, and it is the biggest row of the screen**.

## HAIR does not edit a section: it picks one

Measured 2026-09-16 by `oracle.py --patched HAIR`, which walks the row from the
bottom and reads the **whole loaded file** after every press.  What changes at
press N is the section value N uses, and the shape of the answer is:

* the **letter** of a style's label is a head section of `MODEL.BIN`'s first
  run -- A is 24, B is 26, C 30, D 48, F 52, G 28, I 34, J 36, K 32, L 46,
  O 44, P 50, and **E is split in two**: E1 in 48, which is D's, and E2 in 54,
  which is its own.  Thirteen sections, twelve whole letters and one split;
* the **digit** is a band of sixteen rows of the hair sheet at 3,568, written
  into that section's hair quads;
* and section 24 -- the section every earlier walk in this cycle watched -- is
  family **A** alone.  Three values of 32 use it, which is exactly the "three
  states" that walk saw and read as the field's whole reach.  The screen was
  moving all 32: measured twice by `oracle.py --hair`, the row's value cell
  moves on 32 of 32 presses while section 24 settles into three states.

The writer is in the game, and it is four stores:

    andi  v0, a2, 0x00ff      the band, as the caller passed it
    sll   v0, v0, 4           sixteen rows a band
    addiu v1, v0, 15
    addiu v0, v0, 1
    sb    v1, 0x1(a0)         the `v` of the quad's four corners
    sb    v0, 0x5(a0)
    sb    v1, 0x9(a0)
    sb    v0, 0xd(a0)

`HAIR_MAP` is that measurement, with the three values that wrote nothing left
empty rather than filled in.

## What is still a hole

**Three styles of 32 wrote nothing** -- H1, M1 and N1 -- and three even sections
of the run, 38, 40 and 42, were never named.  The pair of threes is suggestive
and is not a measurement, so `head_of` refuses those three instead of handing
back a head that would draw perfectly and be somebody else's.  **E1 is a fourth
oddity**: it rewrote D's section, which may be the game putting D's head back
rather than naming E1's own.

**And the quads are named for four heads of thirteen.**  An execute breakpoint
on the store itself, walked over the whole row (`oracle.py --writes`), reads
`a0` at every write and names the primitive: section 24 is 1 and 14, section 26
is 1 and 3, section 34 is 0, 1 and 12, section 46 is 0, 9 and 17.  The other
nine sections never stopped that instruction, so something else writes them and
this module leaves their window alone.  The obvious rule is measured wrong:
section 30 has twelve primitives on the hair sheet in the hair colour's column
and the game rewrites two.

**FACE reaches five**, of the seven its third-party labels name and the eight
its three bits hold.  Bands 0 to 4 of the same image, 16 rows each, and then it
clamps.

**And every field clamps; none wraps.**  Measured on all six.

Usage:
    python tools/looks/assembly.py --check
    python tools/looks/assembly.py --check-image
    python tools/looks/assembly.py --tuple A-I3-A-F-A
    python tools/looks/assembly.py --corpus <folder of the 50 renders>
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402
import looks  # noqa: E402
import skin  # noqa: E402
import texture  # noqa: E402

SKIP = 77

CLUT_ROW = "clut row"
CLUT_COLUMN = "clut column"
BAND = "v band"


class BadAssembly(Exception):
    """A tuple this table cannot turn into a draw list."""


class Effect:
    """One field, and the measured edit it makes to a named set of primitives.

    `reach` is how many values the SCREEN offers, walked end to end; `looks`
    knows how many the field HOLDS.  The two differ for three of the six, and
    keeping them apart is the whole honesty of this table.
    """

    __slots__ = ("row", "what", "step", "reach", "where", "why")

    def __init__(self, row, what, step, reach, where, why):
        self.row = row
        self.what = what
        self.step = step
        self.reach = reach
        self.where = where
        self.why = why

    @property
    def field(self):
        return looks.BY_ROW[self.row]

    @property
    def resolved(self) -> bool:
        """Does the screen reach every value the field holds?"""
        return self.reach == self.field.values


HEAD = (layout.MODEL, layout.HEAD_SECTION)
"""The head the colour rows were MEASURED on, and a placeholder key.

Section 24 is family A's head and no other's (HAIR_MAP).  `edits()` rewrites
this key to whichever head the tuple actually wears -- without that, a tuple
whose HAIR is not an A addresses a section the scene does not draw, the plan
comes back empty, and SKIN, H.COL, H.F.COL. and FACE move nothing at all while
the figure draws perfectly (CORR-LOOKS-034).
"""

EFFECTS = (
    Effect("SKIN", CLUT_ROW, 1, 4,
           {HEAD: layout.SKIN_COLOUR_PRIMITIVES},
           "one whole 256-entry record a step, so one VRAM row: the four "
           "Pieles.  It moves the bare-skin primitives of the figure's own "
           "sections as well, which are pieces.SKIN_SECTIONS"),
    Effect("H.COL", CLUT_COLUMN, 1, 8,
           {HEAD: layout.HAIR_COLOUR_PRIMITIVES},
           "one 16-entry window a step, from column 1: the eight hair "
           "colours of the zeta table, and the eight of hair_colour"),
    Effect("H.F.COL.", CLUT_COLUMN, 1, 7,
           {HEAD: layout.FACE_PRIMITIVES},
           "one window a step, from column 9, and the record ends at 15"),
    Effect("BOOTS", CLUT_COLUMN, 1, 8,
           {(layout.EDT_MOD, s): None for s in layout.BOOT_SECTIONS},
           "one window a step of the boots record at VRAM (0, 484); 42 of "
           "the 56 primitives of each foot move"),
    Effect("FACE", BAND, layout.ATLAS_BAND, 5,
           {HEAD: layout.FACE_PRIMITIVES},
           "16 rows a band of the same image, bands 0 to 4, and then it "
           "clamps.  Its labels name seven and its bits hold eight"),
)

BY_ROW = {effect.row: effect for effect in EFFECTS}

CHOOSES = {
    "HAIR": "does not edit a primitive of one section at all: it picks WHICH "
            "head section of MODEL.BIN's first run is drawn, and which band "
            "of the hair sheet that section's quads sample.  HAIR_MAP is the "
            "measurement",
}
"""The rows that choose a section instead of editing one -- one, so far.

Kept apart from EFFECTS because the difference is the whole finding of
2026-09-16: an effect edits named primitives of a section the figure already
draws, and this replaces the section.
"""

HAIR_MAP = (
    (24, (0,)), (24, (2,)), (24, (1,)),
    (26, (0, 1)), (26, (2,)), (26, (1,)), (26, (5,)), (26, (3,)), (26, (4,)),
    (30, (0, 1)), (30, (2,)),
    (48, (0, 1)), (48, (2,)),
    (48, (0,)), (54, (0, 1)),
    (52, (0, 1, 3)), (52, (1,)), (52, (4,)),
    (28, (0, 1)),
    None,
    (34, (0,)), (34, (2,)), (34, (1,)),
    (36, (0, 1)),
    (32, (0, 1, 3, 4)),
    (46, (5,)), (46, (6,)), (46, (7,)),
    None, None,
    (44, (0, 1)),
    (50, (0, 1)),
)
"""Style index -> (MODEL.BIN section, the bands its rewritten quads landed in).

**Measured 2026-09-16 on slot 2** by `oracle.py --patched HAIR`, which walks the
row from the bottom and reads the WHOLE loaded file after every press: what
changes at press N is the section that value N uses.  It is the anchor
LOOKS-TASK-14 was missing, and it says what the one-section walk could not:

* the letter of a style's label is its **section** -- A is 24, B is 26, C 30,
  D 48, F 52, G 28, I 34, J 36, K 32, L 46, O 44, P 50, and every one of those
  letters' variants rewrites that same section -- **except E**, the one letter
  split across two: E1 rewrites 48, which is D's, and E2 rewrites 54, which no
  other style names.  That is why HAIR_MAP_SECTIONS is thirteen and the letters
  above are twelve (CORR-LOOKS-030);
* the digit is the **band** of the hair sheet at 3,568 -- B's six variants come
  back as bands 0/1, 2, 1, 5, 3 and 4 of one section;
* and section 24, the one every earlier walk watched, is family **A** alone.
  Three values of 32 use it, which is exactly the "three states" that walk saw
  and read as the field's whole reach.

`None` is a value that rewrote **nothing** in the file: measured, not assumed.
Three of them -- H1, M1 and N1 -- and three even sections of the run (38, 40
and 42) never appeared, which is a suggestive pair of threes and no more than
that.  The pair only closes with 54 counted as named: the run holds sixteen
even sections and 16 - 13 = 3.  E1 is a fourth oddity: it rewrote section 48,
which is D's, and may be the game putting D's section back rather than naming
E1's own -- the question is why E1 uses D's, not whether E has one of its own,
which E2 answers.  Guessing any of
the four would be the mapping that draws perfectly and is wrong.
"""

HEAD_BAND = Effect(
    "HAIR", BAND, layout.ATLAS_BAND, len(HAIR_MAP),
    {HEAD: layout.HAIR_PRIMITIVES},
    "the band HAIR_MAP measured for this style, applied to the hair quads of "
    "the head the style names -- for the four sections whose quads the "
    "breakpoint of oracle.py --writes caught by index (layout.HAIR_QUADS).  "
    "The other nine keep the disc's own window, because the instruction that "
    "writes them has not been found")
"""HAIR's edit where it IS known: family A's own section.

Not in EFFECTS, and that is the point: `edits()` walks EFFECTS with the field's
value as the step, and HAIR's value is not a band -- it is a row of HAIR_MAP.
"""

HAIR_MAP_SILENT = 3
HAIR_MAP_SECTIONS = 13
"""How many values wrote nothing, and how many distinct sections were named.

Asserted in `_checks` so that a later measurement which fills the holes has to
come here and change these two numbers.
"""

HAIR_MAP_MULTI_BAND = 10
HAIR_MAP_BANDS_UNMEASURED = 1
"""How many styles landed in more than one band, and how many of those draw.

`--patched` says WHICH bands a style's rewritten quads landed in; it does not
say **which quad took which**.  For a style with one band there is nothing to
choose.  For the ten with two or more there is, and `draw_list` applies the
first -- which is a choice and not a measurement, so it is named here, printed
in the draw list, and counted, rather than left to the reader of a `band +0`
that looks like every other.

Only one of the ten reaches the draw list today (`B1`, section 26): the other
nine name sections whose quads `layout.HAIR_QUADS` does not know, so no band is
applied to them at all and there is nothing to choose.  When
`oracle.py --writes` fills those in -- it reads `a0`, the primitive, and `a2`,
the band, at the SAME breakpoint hit, so the pairing is one run away -- this
number goes up before the measurement lands, which is the point of counting it.
"""


def multi_band_styles() -> list:
    """[(style index, section, bands)] for every style with more than one band."""
    return [(index, entry[0], entry[1])
            for index, entry in enumerate(HAIR_MAP)
            if entry is not None and len(entry[1]) > 1]


def hair_texcoords(texcoords, rows: int) -> tuple:
    """The four (u, v) the game draws a hair quad with, at *rows* into the sheet.

    `u` is the file's.  `v` is NOT the file's plus the band: the store at
    `layout.HAIR_QUAD_STORE` writes an absolute row into every corner --
    `rows + 15` into corners 0 and 2 and `rows + 1` into 1 and 3 -- and the file
    holds other rows than those, on all four sections whose quads are known
    (CORR-LOOKS-042).
    """
    if len(texcoords) != len(layout.HAIR_QUAD_ROWS):
        raise BadAssembly("a hair quad has %d corners and this has %d"
                          % (len(layout.HAIR_QUAD_ROWS), len(texcoords)))
    return tuple((u, rows + row)
                 for (u, _v), row in zip(texcoords, layout.HAIR_QUAD_ROWS))


def unmeasured_bands(chosen: int, bands) -> tuple:
    """The bands `draw_list` drops when it applies the first one.

    Empty for a style with one band, and empty for a section whose quads are
    unknown -- there no band is applied at all, so nothing was chosen.  What
    comes back non-empty is exactly the case where the picture depends on a
    pairing nobody measured.
    """
    if not layout.HAIR_QUADS.get(chosen) or len(bands) < 2:
        return ()
    return tuple(bands[1:])


UNTOUCHED = {
    "BODY": "works in buffers: LOOKS-TASK-08 measured it moving no byte of "
            "either model file",
    "HEIG": "does not move the loaded geometry either; it scales at draw "
            "time, in the display list",
    "AGE": "moves four bytes in all of RAM and none of them geometry",
    "NAT": "not a stored field at all -- see looks.UNSTORED",
    "DEFAUL": "not a stored field at all -- see looks.UNSTORED",
    "FOOT": "not measured against the geometry; nothing in this cycle has "
            "walked it",
}
"""The rows that reach no primitive, and why -- a named hole each.

Six of the twelve, which is why this table has six rows and not twelve.  A
line here is a measurement or a declared gap; neither is a guess.
"""


# ---- the edit ------------------------------------------------------------

def edits(values: dict, head: int | None = None) -> dict:
    """{(file, section): {primitive: (clut, band)}} for one tuple of LOOKS.

    `clut` is the id to write, `band` how many rows to add to every `v`.  A
    primitive absent from the answer is one the tuple does not touch, which is
    most of them: the edit is small by measurement, not by choice.

    **The inner key is (row, primitives) and not primitives alone**, because
    two rows can own the same primitives: H.F.COL. and FACE both move the
    beard's two, one by CLUT column and the other by band.  Keyed by the tuple
    of primitives, the second silently replaced the first and H.F.COL. moved
    nothing on ANY head -- found while asserting that all four colour rows
    reach the head a tuple wears (CORR-LOOKS-034).

    *head* is the MODEL.BIN section the tuple's HAIR names, and every effect
    that owns the HEAD key is re-addressed to it.  The default keeps the
    measured head, so a caller with no tuple in hand gets what the constants
    describe.
    """
    where_head = HEAD if head is None else (layout.MODEL, head)
    out: dict = {}
    for effect in EFFECTS:
        name = effect.field.name
        if name not in values:
            continue
        step = values[name] - effect.field.bias
        if not 0 <= step < effect.reach:
            raise BadAssembly(
                "%s=%s is value %d, and the screen was measured to reach %d "
                "-- %s" % (effect.row, effect.field.label(values[name]), step,
                           effect.reach, effect.why))
        for key, primitives in effect.where.items():
            key = where_head if key == HEAD else key
            out.setdefault(key, {})
            out[key][(effect.row, primitives)] = (effect, step)
    return out


HEAD_COLOUR_MEASURED = layout.HEAD_SECTION
"""The one head whose colour primitives were measured, by index.

`SKIN_COLOUR_PRIMITIVES`, `HAIR_COLOUR_PRIMITIVES` and `FACE_PRIMITIVES` were
read off section 24 with the game running, and the thirteen heads do not hold
the same number of primitives -- 34 draws 23 where 24 draws 18.  Applying the
same indices to the other twelve is the plausible assumption this cycle refuses
elsewhere (HAIR_QUADS covers four heads of thirteen BY MEASUREMENT, and head_of
refuses three styles rather than invent them).

So they are applied -- a head that takes no colour at all is the defect
CORR-LOOKS-034 fixed -- and every part they touch on another head is marked.
What fills this in is the sibling of LOOKS-TASK-14's --writes run: which
primitives of each of the thirteen heads each colour row moves.
"""


def colour_is_measured(head: int) -> bool:
    """Whether the colour rows' primitive indices were measured on *head*."""
    return head == HEAD_COLOUR_MEASURED


def head_of(values: dict) -> tuple:
    """(section, band) of the head one tuple draws, out of HAIR_MAP.

    Refuses for the three values that wrote nothing when the map was measured.
    A fallback to section 24 would draw every one of them as an A, perfectly
    and wrongly, which is the failure this whole task exists to avoid.
    """
    style = values.get(looks.BY_ROW["HAIR"].name)
    if style is None:
        raise BadAssembly("this tuple says nothing about HAIR")
    if not 0 <= style < len(HAIR_MAP):
        raise BadAssembly("hair style %d, and the field holds %d"
                          % (style, len(HAIR_MAP)))
    found = HAIR_MAP[style]
    if found is None:
        raise BadAssembly(
            "hair style %s wrote nothing to either model file when the map "
            "was measured, so which head it draws is not known -- see "
            "assembly.HAIR_MAP" % looks.BY_ROW["HAIR"].label(style))
    return found


def apply_to(clut: int, band: int, effect, step) -> tuple:
    """(clut, band) after one field's step, applied to what is already there.

    **It takes the running value and not the disc's**, because two fields can
    own the same primitive: seven of the head's are moved by H.COL and eight by
    SKIN, six of them by both.  Reading the disc afresh for each made the
    second field undo the first, and SKIN A to D came out moving nothing at all
    -- green in the self-check, empty against the disc.
    """
    row, column = skin.grid(clut)
    if effect.what == CLUT_ROW:
        return (skin.clut_id(row + step * effect.step, column), band)
    if effect.what == CLUT_COLUMN:
        return (skin.clut_id(row, column + step * effect.step), band)
    return (clut, band + step * effect.step)


def combine(primitive, byname: dict, at: int) -> tuple:
    """(clut, band) of one primitive after every field that owns it.

    Separate from `draw_list` so it can be checked with no disc in the room --
    and because it is the one line of this module that has already been wrong:
    the fields have to compose, not each start again from the file.
    """
    clut, band = primitive.clut, 0
    for (_row, primitives), (effect, step) in byname.items():
        if primitives is not None and at not in primitives:
            continue
        clut, band = apply_to(clut, band, effect, step)
    return (clut, band)


def draw_list(disc, values: dict, figure: int) -> list:
    """Every primitive to draw for one tuple, with its image and its palette.

    Returns a list of dicts, one per primitive: the file and section it lives
    in, its index, the image record its first corner resolves to, and the
    palette window its CLUT id names -- both AFTER the tuple's edit.
    """
    import atlas
    import modelfile
    import section

    data2d = disc[layout.DAT2D]
    images = texture.images(data2d)
    palettes = texture.palettes(data2d)

    out = []
    dropped: dict = {}
    borrowed: dict = {}
    stored: dict = {}
    head = head_of(values)[0] if figure == HEAD_FIGURE else None
    plan = edits(values, head)
    if figure == HEAD_FIGURE:
        chosen, bands = head_of(values)
        if not colour_is_measured(chosen):
            # The colour rows reach this head now, and their primitive
            # indices were read off section 24.  Applied, and said.
            borrowed[(layout.MODEL, chosen)] = tuple(
                sorted({at for _row, primitives in plan.get(
                    (layout.MODEL, chosen), {})
                    if primitives is not None for at in primitives}))
        quads = layout.HAIR_QUADS.get(chosen)
        if quads:
            # Four of the thirteen heads have their quads named by index, by
            # the breakpoint of LOOKS-TASK-14.  The other nine are written by
            # some other instruction and keep the disc's own window until
            # something measures them -- a wrong guess here repaints the skull.
            plan.setdefault((layout.MODEL, chosen), {})[
                (HEAD_BAND.row, quads)] = (HEAD_BAND, bands[0])
            # And their `v` is what the game's store writes, not the file's
            # plus the band -- see hair_texcoords.
            stored[(layout.MODEL, chosen)] = quads
            # And when the style landed in more than one band, WHICH quad took
            # which was never measured.  The first is applied, and every
            # primitive it is applied to carries the ones that were dropped, so
            # the choice travels with the picture instead of disappearing into
            # a `band +0` that reads like any other.
            left = unmeasured_bands(chosen, bands)
            if left:
                dropped[(layout.MODEL, chosen)] = (quads, left)
    for name, index in sections_of(disc, figure, values):
        scan = section.scan(disc[name], layout.GEOMETRY_START[name])
        one = scan.sections[index]
        for at, primitive in enumerate(one.primitives):
            clut, band = combine(primitive, plan.get((name, index), {}), at)
            texcoords = None
            if at in stored.get((name, index), ()):
                texcoords = hair_texcoords(primitive.texcoords, band)
                corner = atlas.texel(primitive, *texcoords[0])
            else:
                corner = atlas.texel(primitive, primitive.texcoords[0][0],
                                     primitive.texcoords[0][1] + band)
            record = atlas.image_at(images, *corner)
            x, y = skin.grid(clut)[1] * texture.NARROW, skin.grid(clut)[0]
            try:
                window = texture.covering(palettes, x, y, texture.NARROW)
            except texture.NoPalette:
                window = None
            quads, left = dropped.get((name, index), ((), ()))
            lent = borrowed.get((name, index), ())
            out.append({
                "file": name, "section": index, "primitive": at,
                "clut": clut, "band": band,
                "image": record.offset if record else None,
                "palette": None if window is None else (x, y, texture.NARROW),
                "band_unmeasured": left if at in quads else (),
                "colour_borrowed": at in lent,
                "texcoords": texcoords,
            })
    del modelfile  # imported for the reader below; the draw list does not need it
    return out


def sections_of(disc, figure: int, values: dict | None = None) -> list:
    """(file, section) of every piece of one figure, plus the head it wears.

    The figure comes first and the fields come second: the two models do not
    share the arm pieces (CORR-LOOKS-021), so loading one and recolouring it
    draws the goalkeeper in short sleeves.

    **The head is the tuple's**, when a tuple is given: `HAIR_MAP` says which of
    MODEL.BIN's heads the style names.  Without one the disc's own
    `layout.HEAD_SECTION` stands in, which is style A1's head and no other's.

    The map was measured on the OUTFIELD player, figure 0.  The second run of
    heads (74..105) is the other figure's, and nothing has walked the row on it
    -- so figure 1 keeps its own head here, and that is a named gap, not a
    reading.
    """
    import modelfile

    models = modelfile.read_models(disc[layout.EDT_MOD])
    if not 0 <= figure < len(models):
        raise BadAssembly("figure %d, and this disc holds %d"
                          % (figure, len(models)))
    import section

    scan = section.scan(disc[layout.EDT_MOD],
                        layout.GEOMETRY_START[layout.EDT_MOD])
    where = {one.offset: i for i, one in enumerate(scan.sections)}
    out = [(layout.EDT_MOD, where[target])
           for target in models[figure].targets]
    head = HEAD
    if values is not None and figure == HEAD_FIGURE:
        head = (layout.MODEL, head_of(values)[0])
    return out + [head]


HEAD_FIGURE = 0
"""The figure HAIR_MAP was measured on: slot 2, the outfield player."""


# ---- the corpus, as an outside witness -----------------------------------

CORPUS_REFERENCE = "A-A1-A-A-A"
CORPUS_PAIRS = (
    ("FACE", "A-A1-A-F-A"),
    ("FACE", "A-A1-A-C-A"),
    ("H.COL", "A-A1-C-A-A"),
    ("H.COL", "A-A1-F-A-A"),
    ("HAIR", "A-I3-A-A-A"),
    ("HAIR", "A-L3-A-A-A"),
    ("SKIN", "B-A1-A-A-A"),
)
"""Renders that differ from the reference in exactly ONE field of the tuple.

Seven of the corpus's fifty, covering four rows of the screen.  Which field each
one moves is not asserted here -- `parse_tuple` is asked, and a pair that turns
out to move two fields is a failure of this list rather than a reading.
"""

CORPUS_TOLERANCE = 40
"""Sum over three channels, above which two renders differ at a pixel.

They are JPEGs, so a threshold cannot be avoided; this one is measured to leave
the background at zero while the beard of `A-A1-A-F-A` comes out at 730 pixels.
"""

AGREEMENT = 0.8
"""How well the two orderings must agree, as Spearman's rho over the rows.

Not 1.0, and the reason is measured: HAIR and H.COL sit at 0.25 and 0.44 of the
head on the disc and their renders change at 0.361 and 0.353 -- **0.008 apart**,
so which of the two is higher is inside the noise of both.  What the corpus
witnesses is the order of the extremes -- the beard at the bottom, the hair at
the top.

**And 0.8 is the step immediately below 1.0, not a round number.**  Over four
rows Spearman's rho can only be 1.0, 0.8, 0.6 and so on down, and one inversion
between neighbours costs exactly 0.2.  So this floor tolerates one such
inversion and nothing else -- which is what keeps it from being a threshold
calibrated on the result it had to accept.  The 0.008 is the number the run
prints, and it is printed rather than quoted here for the same reason
(CORR-LOOKS-031).
"""


def rank_agreement(first: dict, second: dict) -> float:
    """Spearman's rho between two orderings of the same keys.

    Pure arithmetic, so the gate has something to be wrong about without a disc
    or a folder of JPEGs: `self_check` shuffles one side and demands it fall.
    """
    keys = sorted(first)
    if sorted(second) != keys or len(keys) < 2:
        raise BadAssembly("the two orderings do not cover the same rows")

    def ranked(values):
        order = sorted(keys, key=lambda key: values[key])
        return {key: index for index, key in enumerate(order)}

    ours, theirs = ranked(first), ranked(second)
    count = len(keys)
    squares = sum((ours[key] - theirs[key]) ** 2 for key in keys)
    return 1.0 - 6.0 * squares / (count * (count * count - 1))


def field_heights(data: bytes) -> dict:
    """{row: how high its primitives sit}, 0 at the crown and 1 at the chin.

    Out of the disc's own vertices, and this is what makes the corpus a test:
    the table says which primitives a row owns, the mesh says how high they are,
    and the renders say where the picture changes.  Three independent things
    that have to come out in the same order.
    """
    import section

    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    head = scan.sections[layout.HEAD_SECTION]
    ys = [vertex.y for vertex in head.vertices]
    low, high = min(ys), max(ys)
    owners = {
        "HAIR": layout.HAIR_PRIMITIVES,
        "FACE": layout.FACE_PRIMITIVES,
        "H.COL": layout.HAIR_COLOUR_PRIMITIVES,
        "SKIN": layout.SKIN_COLOUR_PRIMITIVES,
    }
    out = {}
    for row, primitives in owners.items():
        picked = [head.vertices[index].y
                  for one in primitives
                  for index in head.primitives[one].corners]
        out[row] = (sum(picked) / len(picked) - low) / (high - low)
    return out


def corpus_rows(folder: str) -> dict:
    """{row: where the renders change}, 0 at the top of the picture, 1 at the
    bottom.

    One number per row of the screen, averaged over the pairs that move it.
    """
    try:
        from PIL import Image
    except ImportError:
        raise BadAssembly("PIL is not installed, so the renders cannot be "
                          "read") from None

    def load(name):
        path = os.path.join(folder, name + ".jpg")
        if not os.path.isfile(path):
            raise BadAssembly("the corpus has no %s.jpg" % name)
        return Image.open(path).convert("RGB")

    reference = load(CORPUS_REFERENCE)
    width, height = reference.size
    here = reference.load()
    base = looks.parse_tuple(CORPUS_REFERENCE)
    found = {}
    for row, name in CORPUS_PAIRS:
        moved = [field for field, value in looks.parse_tuple(name).items()
                 if base[field] != value]
        if [looks.BY_NAME[field].row for field in moved] != [row]:
            raise BadAssembly("%s differs from %s in %r, not in %s alone"
                              % (name, CORPUS_REFERENCE, moved, row))
        other = load(name)
        if other.size != reference.size:
            raise BadAssembly("%s is %r and the reference is %r"
                              % (name, other.size, reference.size))
        there = other.load()
        rows = []
        for y in range(height):
            for x in range(width):
                if sum(abs(one - two)
                       for one, two in zip(here[x, y], there[x, y])) \
                        > CORPUS_TOLERANCE:
                    rows.append(y)
        if not rows:
            raise BadAssembly("%s and %s are the same picture, and their "
                              "tuples are not" % (name, CORPUS_REFERENCE))
        found.setdefault(row, []).append(sum(rows) / len(rows) / height)
    return {row: sum(values) / len(values) for row, values in found.items()}


def _corpus(image_path: str, folder: str) -> int:
    """The cross-check: the disc, this table, and somebody else's renders."""
    disc = _load(image_path)
    heights = field_heights(disc[layout.MODEL])
    rows = corpus_rows(folder)
    print("  the corpus: %s, %d pair(s) over %d row(s) of the screen"
          % (folder, len(CORPUS_PAIRS), len(rows)))
    for row in sorted(heights, key=lambda one: heights[one]):
        print("      %-8s the mesh puts it at %.3f of the head, and the "
              "renders change at %.3f" % (row, heights[row], rows[row]))
    rho = rank_agreement(heights, rows)
    print("      the two orderings agree to rho = %.2f (the floor is %.2f)"
          % (rho, AGREEMENT))
    problems = []
    if rho < AGREEMENT:
        problems.append("the mesh's order and the renders' order agree to "
                        "%.2f, under the %.2f floor" % (rho, AGREEMENT))
    lowest = max(heights, key=lambda one: heights[one])
    if max(rows, key=lambda one: rows[one]) != lowest:
        problems.append("the mesh puts %s lowest and the renders do not"
                        % lowest)
    highest = min(heights, key=lambda one: heights[one])
    if rows[highest] >= 0.5:
        problems.append("%s is the highest thing this table owns and its "
                        "renders change at %.3f, below the middle"
                        % (highest, rows[highest]))
    print("assembly --corpus: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line)
    return 1 if problems else 0


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("assembly.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(BadAssembly)

    ok("every effect names a row of the screen",
       all(e.row in looks.SCREEN for e in EFFECTS))
    ok("and every row is either an effect, a choice, or a named hole",
       set(looks.SCREEN) == set(BY_ROW) | set(UNTOUCHED) | set(CHOOSES),
       "%r" % sorted(set(looks.SCREEN)
                     ^ (set(BY_ROW) | set(UNTOUCHED) | set(CHOOSES))))
    ok("no row is in two of the three",
       not (set(BY_ROW) & set(UNTOUCHED) or set(BY_ROW) & set(CHOOSES)
            or set(UNTOUCHED) & set(CHOOSES)))
    ok("four effects move a palette and one moves an atlas band",
       sorted(e.what for e in EFFECTS).count(BAND) == 1)

    # The hole that is left, asserted rather than described.
    unresolved = sorted(e.row for e in EFFECTS if not e.resolved)
    ok("one row of the five does not walk to the end of what its bits hold",
       unresolved == ["FACE", "H.F.COL."], "%r" % (unresolved,))

    # The colour rows have to reach the head the tuple WEARS, not the head
    # they were measured on.  Without this every tuple whose HAIR is not an A
    # draws a figure no colour field touches (CORR-LOOKS-034).
    away = attempt("parse a tuple whose head is not section 24",
                   lambda: looks.parse_tuple("B-I3-A-A-A"))
    if away is not None:
        chosen = head_of(away)[0]
        ok("a style of another letter wears another section",
           chosen != layout.HEAD_SECTION, "got %d" % chosen)
        plan = attempt("plan the edits for it",
                       lambda: edits(away, chosen))
        if plan is not None:
            ok("and the colour rows are addressed to the head it wears",
               (layout.MODEL, chosen) in plan,
               "keys: %r" % (sorted(plan),))
            ok("with nothing left addressed to the head they were measured on",
               HEAD not in plan, "keys: %r" % (sorted(plan),))
            ok("and all four colour rows reach it",
               len(plan[(layout.MODEL, chosen)]) == 4,
               "%d row(s)" % len(plan[(layout.MODEL, chosen)]))
        home = attempt("plan the edits for a head-24 tuple",
                       lambda: edits(looks.parse_tuple("B-A1-A-A-A"),
                                     layout.HEAD_SECTION))
        if home is not None:
            ok("a family A tuple still addresses section 24", HEAD in home)
        ok("and only section 24's colour primitives were measured by index",
           colour_is_measured(layout.HEAD_SECTION)
           and not colour_is_measured(chosen))

    # The band a multi-band style draws with is a CHOICE, not a measurement.
    # Asserted here so the day --writes pairs quad to band -- it reads a0, the
    # primitive, and a2, the band, at the same breakpoint hit -- the numbers
    # have to come through this file (CORR-LOOKS-028).
    multi = multi_band_styles()
    ok("ten styles landed in more than one band",
       len(multi) == HAIR_MAP_MULTI_BAND,
       "%d: %s" % (len(multi), [looks.HAIR_STYLES[i] for i, _s, _b in multi]))
    reach = [i for i, chosen, bands in multi
             if unmeasured_bands(chosen, bands)]
    ok("and exactly one of them reaches the draw list: the other nine name "
       "sections whose quads are unknown, so no band is applied at all",
       len(reach) == HAIR_MAP_BANDS_UNMEASURED
       and [looks.HAIR_STYLES[i] for i in reach] == ["B1"],
       "%d: %s" % (len(reach), [looks.HAIR_STYLES[i] for i in reach]))
    # The hair quad's `v`, the way the game's store writes it: an absolute
    # row per corner, not the file's plus the band (CORR-LOOKS-042).  Section
    # 24's quad 1 is on the disc as rows 14/1/14/1; the game draws 15/1/15/1.
    disc_quad = ((188, 14), (188, 1), (199, 14), (199, 1))
    ok("a hair quad is drawn with the rows the store writes, at band 0",
       hair_texcoords(disc_quad, 0)
       == ((188, 15), (188, 1), (199, 15), (199, 1)),
       "%r" % (hair_texcoords(disc_quad, 0),))
    ok("and a band moves all four corners by whole bands",
       [v for _u, v in hair_texcoords(disc_quad, 2 * layout.ATLAS_BAND)]
       == [47, 33, 47, 33],
       "%r" % (hair_texcoords(disc_quad, 2 * layout.ATLAS_BAND),))
    ok("and u is the file's, untouched",
       [u for u, _v in hair_texcoords(disc_quad, 0)]
       == [u for u, _v in disc_quad])
    refuses("a quad without four corners is refused",
            lambda: hair_texcoords(disc_quad[:3], 0), "corners")

    ok("a style with one band chooses nothing",
       unmeasured_bands(24, (0,)) == ())
    ok("and neither does a multi-band style whose quads are unknown",
       unmeasured_bands(30, (0, 1)) == ())
    ok("but B1 reports the band the draw list dropped",
       unmeasured_bands(26, (0, 1)) == (1,),
       "%s" % (unmeasured_bands(26, (0, 1)),))

    # The map, and the three values it could not place.  A later run that
    # fills them has to come here and change these numbers.
    ok("the map has a row for every value the field holds",
       len(HAIR_MAP) == looks.BY_ROW["HAIR"].values == 32)
    ok("three of them wrote nothing and are left empty",
       sum(1 for one in HAIR_MAP if one is None) == HAIR_MAP_SILENT)
    named = {one[0] for one in HAIR_MAP if one}
    ok("the sections it names are %d, all even, all in the first head run"
       % HAIR_MAP_SECTIONS,
       len(named) == HAIR_MAP_SECTIONS
       and all(index % 2 == 0 for index in named)
       and all(layout.HEAD_RUNS[0][0] <= index < layout.HEAD_RUNS[0][1]
               for index in named),
       "%r" % sorted(named))
    ok("every band it names is one of the sheet's eight",
       all(0 <= band < texture.tall(layout.HAIR_IMAGE) // layout.ATLAS_BAND
           for one in HAIR_MAP if one for band in one[1])
       if hasattr(texture, "tall") else
       all(0 <= band < 8 for one in HAIR_MAP if one for band in one[1]))
    # A letter is a section: every variant of a label's letter names the same
    # one.  E1 is the measured exception, and it is named rather than smoothed
    # over -- it rewrote D's section, which may be the game putting D's head
    # back rather than naming E1's own.
    letters = {}
    for index, one in enumerate(HAIR_MAP):
        if one is None:
            continue
        letters.setdefault(looks.HAIR_STYLES[index][0], set()).add(one[0])
    astray = sorted(k for k, v in letters.items() if len(v) > 1)
    ok("each letter of the labels is one section, and E is the exception",
       astray == ["E"], "%r" % (astray,))
    ok("family A is section 24, which is why one-section walks saw three",
       letters["A"] == {layout.HEAD_SECTION}
       and sum(1 for one in HAIR_MAP
               if one and one[0] == layout.HEAD_SECTION) == 3)
    # H.F.COL. is the one of the three that is NOT a hole: its bits hold
    # eight, its labels name seven, and seven is what the screen walks --
    # the eighth is an index nobody named (LOOKS-TASK-13), not a value this
    # cycle failed to reach.
    ok("H.F.COL. reaches every value anyone has named",
       BY_ROW["H.F.COL."].reach == len(BY_ROW["H.F.COL."].field.labels))
    ok("FACE does not, which is what makes it a hole and not a gap in naming",
       BY_ROW["FACE"].reach < len(BY_ROW["FACE"].field.labels))

    # The edit itself, on a primitive built here so the check needs no disc.
    class Fake:
        clut = skin.clut_id(layout.CLUT_ROW_FIRST, layout.HAIR_COLUMN)
        texcoords = ((176, 1), (176, 15), (188, 1), (188, 15))
        tpage = 0x0018  # not-an-address: the page the head declares

    one = Fake()
    ok("a step of SKIN moves the row and leaves the column",
       apply_to(one.clut, 0, BY_ROW["SKIN"], 2)[0]
       == skin.clut_id(layout.CLUT_ROW_FIRST + 2, layout.HAIR_COLUMN))
    ok("a step of H.COL moves the column and leaves the row",
       apply_to(one.clut, 0, BY_ROW["H.COL"], 3)[0]
       == skin.clut_id(layout.CLUT_ROW_FIRST, layout.HAIR_COLUMN + 3))
    ok("a band of HAIR moves no CLUT and answers rows of the sheet",
       apply_to(one.clut, 0, HEAD_BAND, 2)
       == (one.clut, 2 * layout.ATLAS_BAND))
    # The two together, in both orders, because a primitive that both own is
    # the case that went wrong: the answer may not depend on which came first.
    both_ways = []
    for order in (("SKIN", "H.COL"), ("H.COL", "SKIN")):
        byname = {(r, BY_ROW[r].where[HEAD]): (BY_ROW[r], 2) for r in order}
        both_ways.append(combine(one, byname, 0))
    ok("two fields on the same primitive compose, and in either order",
       both_ways[0] == both_ways[1]
       == (skin.clut_id(layout.CLUT_ROW_FIRST + 2, layout.HAIR_COLUMN + 2), 0),
       "%r" % (both_ways,))
    ok("and a field passes over a primitive it does not own",
       combine(one, {("H.F.COL.", BY_ROW["H.F.COL."].where[HEAD]):
                     (BY_ROW["H.F.COL."], 3)}, 0) == (one.clut, 0))
    # Two ROWS that own the SAME primitives, which is the case the plan's key
    # lost: H.F.COL. moves the beard's column and FACE moves the beard's band,
    # and both name layout.FACE_PRIMITIVES.  Keyed by the primitives alone the
    # second replaced the first and H.F.COL. moved nothing, on any head
    # (CORR-LOOKS-034).
    beard = looks.parse_tuple("A-A1-A-A-E")
    rows = [effect.row
            for effect, _step in edits(beard, layout.HEAD_SECTION)[HEAD]
            .values()]
    ok("two rows that own the same primitives both survive the plan",
       sorted(rows) == ["FACE", "H.COL", "H.F.COL.", "SKIN"], "%r" % (rows,))
    ok("and a step of H.F.COL. is in it, so the beard colour reaches the head",
       ("H.F.COL.", 4) in [(e.row, s) for e, s
                           in edits(beard, layout.HEAD_SECTION)[HEAD].values()],
       "%r" % ([(e.row, s) for e, s
                in edits(beard, layout.HEAD_SECTION)[HEAD].values()],))

    ok("a tuple inside every reach becomes an edit",
       len(edits(looks.parse_tuple("A-A1-A-A-A"))) >= 1)
    # The anchor, and the assertion an off-by-one in the table trips: the
    # LOWEST value of every field is what the disc already holds.  Measured --
    # 32 presses of Left on HAIR, and 8 on the others, land on the bytes the
    # file has.  So the bottom tuple must ask for no edit at all.
    bottom = edits(looks.parse_tuple("A-A1-A-A-A"))
    steps = sorted({step for byname in bottom.values()
                    for _prims, (_effect, step) in byname.items()})
    ok("and the bottom of every field is the state the disc already holds",
       steps == [0], "%r" % (steps,))
    ok("so applying the bottom tuple changes nothing",
       apply_to(one.clut, 0, BY_ROW["SKIN"], 0) == (one.clut, 0)
       and apply_to(one.clut, 0, HEAD_BAND, 0) == (one.clut, 0))
    refuses("a beard style past the five the screen reaches is refused",
            lambda: edits(looks.parse_tuple("A-A1-A-F-A")), "measured to reach")

    # The quads the breakpoint named, tied back to the map and to the pair
    # LOOKS-TASK-08 measured by hand.
    named = {one[0] for one in HAIR_MAP if one}
    ok("every head whose quads are named is a head the map names",
       set(layout.HAIR_QUADS) <= named,
       "%r" % sorted(set(layout.HAIR_QUADS) - named))
    ok("and section 24's entry is the pair the field walk named",
       layout.HAIR_QUADS[layout.HEAD_SECTION] == layout.HAIR_PRIMITIVES)
    ok("the quads are named for four of the thirteen heads",
       len(layout.HAIR_QUADS) == 4 and len(named) == HAIR_MAP_SECTIONS)

    # The corpus's arithmetic, which needs neither a disc nor the JPEGs.
    same = {"a": 0.1, "b": 0.2, "c": 0.3, "d": 0.4}
    ok("two orderings that agree come out at 1.0",
       rank_agreement(same, dict(same)) == 1.0)
    swapped = dict(same, a=0.2, b=0.1)
    ok("one inversion between neighbours costs 0.2, which is the floor",
       abs(rank_agreement(same, swapped) - AGREEMENT) < 1e-9)
    upside = {key: -value for key, value in same.items()}
    ok("and an ordering read backwards is under the floor",
       rank_agreement(same, upside) < AGREEMENT)
    refuses("two orderings over different rows are refused",
            lambda: rank_agreement(same, {"a": 1.0, "b": 2.0}),
            "same rows")

    # The head a tuple wears: the map answers, and refuses where it is empty.
    ok("the bottom tuple wears section 24, band 0",
       head_of(looks.parse_tuple("A-A1-A-A-A")) == (layout.HEAD_SECTION, (0,)))
    ok("and a style of another letter wears another section",
       head_of(looks.parse_tuple("A-I3-A-A-A"))[0] != layout.HEAD_SECTION)
    refuses("a style the map could not place is refused, not defaulted",
            lambda: head_of(looks.parse_tuple("A-H1-A-A-A")),
            "wrote nothing")
    refuses("and a tuple with no HAIR at all is refused",
            lambda: head_of({}), "says nothing")


# ---- the disc ------------------------------------------------------------

def _load(image_path):
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        return {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D)}


def head_runs(data: bytes) -> list:
    """[(first, last, byte-distinct sections, distinct meshes, hairy)] per run.

    The 32 heads of each run, counted rather than asserted: `layout.HEAD_RUNS`
    says where they are and this says what is in them, so a disc that does not
    hold them comes out as a number and not as a crash.

    **Two counts, because they disagree and the difference is the finding.**
    Byte-distinct sections is 32 in both runs -- that is the file, and calling
    it "bodies" is what let a second reading of this run conclude "two blocks of
    32 heads" (CORR-LOOKS-029).  Distinct VERTEX ARRAYS is **12** in the first
    run and 24 in the second: the sections differ, the meshes repeat, and
    fifteen of the sixteen pairs share theirs byte for byte.
    """
    import atlas
    import section

    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    out = []
    for first, stop in layout.HEAD_RUNS:
        blobs, meshes, hairy = set(), set(), 0
        for index in range(first, stop):
            one = scan.sections[index]
            blobs.add(bytes(data[one.offset:one.end]))
            meshes.add(tuple((v.x, v.y, v.z) for v in one.vertices))
            if any(True for p in one.primitives
                   if (atlas.image_at(_IMAGES, *atlas.corners(p)[0])
                       or _NOTHING).offset == layout.HAIR_IMAGE):
                hairy += 1
        out.append((first, stop - 1, len(blobs), len(meshes), hairy))
    return out


def hair_windows(data: bytes, run: int = 0) -> dict:
    """{(first v, last v) or None: [section]} over one run of heads.

    The window a head takes on the hair sheet, read the way LOOKS-TASK-14
    defines one: the `v` span of the primitives that sample HAIR_IMAGE in the
    CLUT's hair column.  It is a dict rather than a count because the shape is
    what matters -- the windows REPEAT, and four sections have none at all.
    """
    import atlas
    import section

    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    first, stop = layout.HEAD_RUNS[run]
    out: dict = {}
    for index in range(first, stop):
        rows = []
        for primitive in scan.sections[index].primitives:
            image = atlas.image_at(_IMAGES, *atlas.corners(primitive)[0])
            if (image is not None and image.offset == layout.HAIR_IMAGE
                    and skin.grid(primitive.clut)[1] == layout.HAIR_COLUMN):
                rows += [corner[1] for corner in atlas.corners(primitive)]
        key = (min(rows), max(rows)) if rows else None
        out.setdefault(key, []).append(index)
    return out


def head_pairs(data: bytes) -> tuple:
    """(pairs, primitives that differ, {(column before, column after): count}).

    The first run of heads is **sixteen pairs**, not thirty-two independent
    bodies: section 24 and section 25 differ in 28 bytes of 592, and so on down
    the run.  What differs inside a pair is measured here rather than described,
    because it decides what the run IS -- and the answer is the beard: every
    primitive that changes its palette inside a pair moves from the hair
    colour's column to the beard colour's, and none moves the other way.

    So "32 sections and hair_style holds 32" is a coincidence worth refusing
    until something measures the mapping.  Sixteen pairs is what the disc holds.
    """
    import section

    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    first, stop = layout.HEAD_RUNS[0]
    pairs, differ, columns = 0, 0, {}
    for index in range(first, stop, 2):
        pairs += 1
        one, other = scan.sections[index], scan.sections[index + 1]
        for left, right in zip(one.primitives, other.primitives):
            if (left.texcoords, left.clut, left.tpage) ==                     (right.texcoords, right.clut, right.tpage):
                continue
            differ += 1
            key = (skin.grid(left.clut)[1], skin.grid(right.clut)[1])
            columns[key] = columns.get(key, 0) + 1
    return (pairs, differ, columns)


HEAD_PAIR_COLUMNS = {(1, 1): 18, (1, 9): 32, (9, 9): 41}
"""What the sixteen pairs' 91 differing primitives do to the CLUT's column.

Measured 2026-09-16, and the shape is the finding: 32 primitives move from
column 1 to column 9 -- the hair colour's window to the beard colour's -- 41
were already in the beard's and only move on the sheet, and 18 stay in the hair
colour's and move by a row or two.  **Nothing goes from 9 back to 1.**  A run
whose pairs differ by "more beard" is sixteen heads twice over, not 32 hairs.
"""

HEAD_RUN_MESHES = (12, 24)
"""How many DISTINCT VERTEX ARRAYS each run of 32 sections holds.

Measured 2026-09-16 (CORR-LOOKS-029).  The sections are 32 byte-distinct blobs
in both runs; the meshes are twelve and 24.  This is the number that says the
first run is sixteen pairs and not 32 heads, and it is asserted rather than
described because the word "body" was read as mesh once already.
"""

HEAD_RUN_WINDOWS = 14
HEAD_RUN_NO_WINDOW = (32, 33, 36, 37)
"""How many distinct hair windows the first run's 32 sections take, and who
takes none.

Fourteen, not 32: the windows repeat -- sections 25, 26 and 27 share one, and
34, 35, 40 and 41 share another -- and four sections sample the hair sheet in
the hair column not at all.  "Each with its own window" was written from the
count of sections, without comparing the windows (CORR-LOOKS-029).
"""

HEAD_RUN_HAIRY = (32, 16)
"""How many of each run's 32 heads sample the hair sheet.

All of the first run and half of the second, measured 2026-09-16.  Written down
because it is the one asymmetry between the two runs, and because a run that
came out 32 and 32 would mean the reader had stopped telling them apart.
"""


class _NothingHere:
    offset = None


_NOTHING = _NothingHere()
_IMAGES: list = []


def _check_image(image_path: str) -> int:
    disc = _load(image_path)
    problems = []

    global _IMAGES
    _IMAGES = texture.images(disc[layout.DAT2D])
    runs = head_runs(disc[layout.MODEL])
    for (first, last, blobs, meshes, hairy), want, shapes in zip(
            runs, HEAD_RUN_HAIRY, HEAD_RUN_MESHES):
        print("  MODEL.BIN sections %d..%d: %d byte-distinct section(s) but "
              "only %d distinct mesh(es), %d of them sampling the hair sheet"
              % (first, last, blobs, meshes, hairy))
        if blobs != last - first + 1:
            problems.append("sections %d..%d hold %d byte-distinct section(s) "
                            "and the run is %d long" % (first, last, blobs,
                                                        last - first + 1))
        if meshes != shapes:
            problems.append("sections %d..%d hold %d distinct mesh(es) and %d "
                            "was measured" % (first, last, meshes, shapes))
        if hairy != want:
            problems.append("sections %d..%d: %d sample the hair sheet, and "
                            "%d was measured" % (first, last, hairy, want))
    windows = hair_windows(disc[layout.MODEL])
    blind = tuple(sorted(windows.get(None, ())))
    print("  and they take %d distinct window(s) on the hair sheet, not %d: "
          "%s take none at all"
          % (len(windows), layout.HEAD_RUNS[0][1] - layout.HEAD_RUNS[0][0],
             ", ".join(str(i) for i in blind) if blind else "none"))
    if len(windows) != HEAD_RUN_WINDOWS:
        problems.append("the first run takes %d distinct window(s) and %d was "
                        "measured" % (len(windows), HEAD_RUN_WINDOWS))
    if blind != HEAD_RUN_NO_WINDOW:
        problems.append("the sections with no window are %s and %s was "
                        "measured" % (blind, HEAD_RUN_NO_WINDOW))
    pairs, differ, columns = head_pairs(disc[layout.MODEL])
    print("  MODEL.BIN sections %d..%d are %d pair(s): %d primitive(s) differ "
          "inside a pair, and their columns move %s"
          % (layout.HEAD_RUNS[0][0], layout.HEAD_RUNS[0][1] - 1, pairs, differ,
             ", ".join("%d->%d: %d" % (a, b, n)
                       for (a, b), n in sorted(columns.items()))))
    if columns != HEAD_PAIR_COLUMNS:
        problems.append("the pairs' columns came out %r and %r was measured"
                        % (columns, HEAD_PAIR_COLUMNS))
    if any(b == layout.HAIR_COLUMN and a == layout.BEARD_COLUMN
           for a, b in columns):
        problems.append("a primitive moves from the beard's column back to "
                        "the hair colour's, which no pair did when this was "
                        "measured")
    if len(runs) != 2 or any(r[1] - r[0] + 1 != looks.BY_ROW["HAIR"].values
                             for r in runs):
        problems.append("the two runs are not %d sections each, which is what "
                        "hair_style holds" % looks.BY_ROW["HAIR"].values)
    base = looks.parse_tuple("A-A1-A-A-A")
    for figure in (0, 1):
        parts = draw_list(disc, base, figure)
        missing = [p for p in parts if p["palette"] is None]
        nowhere = [p for p in parts if p["image"] is None]
        print("  figure %d: %d primitive(s) over %d section(s); %d with no "
              "palette in this file, %d sampling outside it"
              % (figure, len(parts),
                 len({(p["file"], p["section"]) for p in parts}),
                 len(missing), len(nowhere)))
        if not parts:
            problems.append("figure %d draws nothing" % figure)

    # The edit has to CHANGE something, and only what it names: two tuples
    # that differ in one field differ in exactly that field's primitives.
    other = dict(base)
    other["skin_colour"] = 3
    first = {(p["file"], p["section"], p["primitive"]): p["clut"]
             for p in draw_list(disc, base, 0)}
    second = {(p["file"], p["section"], p["primitive"]): p["clut"]
              for p in draw_list(disc, other, 0)}
    moved = [k for k in first if first[k] != second[k]]
    print("  SKIN A to D moves the CLUT of %d primitive(s)" % len(moved))
    if not moved:
        problems.append("SKIN A to D changed nothing, so the edit is not "
                        "being applied")
    if any(skin.grid(second[k])[0] - skin.grid(first[k])[0] != 3
           for k in moved):
        problems.append("SKIN moved something by other than three rows")

    # The map, against the disc: two tuples that differ only in HAIR have to
    # draw a different head, and the same one twice is the failure a defaulted
    # map would hide.
    heads = {}
    for text in ("A-A1-A-A-A", "A-I3-A-A-A", "A-B4-A-A-A"):
        parts = draw_list(disc, looks.parse_tuple(text), HEAD_FIGURE)
        heads[text] = sorted({p["section"] for p in parts
                              if p["file"] == layout.MODEL})
    print("  the head each tuple wears: %s"
          % ", ".join("%s -> %s" % (text, sections)
                      for text, sections in heads.items()))
    if len({tuple(v) for v in heads.values()}) != len(heads):
        problems.append("two of the three tuples wear the same head, and they "
                        "name three different sections in HAIR_MAP")
    if any(len(v) != 1 for v in heads.values()):
        problems.append("a tuple drew %r head section(s) out of MODEL.BIN, "
                        "and a figure wears one" % [len(v) for v in
                                                    heads.values()])

    print("assembly --check-image: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line)
    return 1 if problems else 0


def _tuple(image_path: str, text: str, figure: int = 0) -> int:
    disc = _load(image_path)
    values = looks.parse_tuple(text)
    parts = draw_list(disc, values, figure)
    print("%s, figure %d: %d primitive(s)" % (text, figure, len(parts)))
    seen: dict = {}
    for part in parts:
        key = (part["file"], part["section"], part["image"], part["palette"],
               part["band"], part["band_unmeasured"], part["colour_borrowed"])
        seen[key] = seen.get(key, 0) + 1
    for (name, index, image, palette, band, left, lent), count in sorted(
            seen.items(), key=lambda kv: str(kv[0])):
        print("    %-18s section %-3d image %-6s palette %-16s band %+d  "
              "x%d%s%s"
              % (name, index, image, palette, band, count,
                 "" if not left
                 else "   BAND NOT MEASURED: the style also landed in band(s)"
                      " %s, and which quad takes which was never measured"
                      % ", ".join(str(b) for b in left),
                 "" if not lent
                 else "   COLOUR BY BORROWED INDEX: the colour rows were "
                      "measured on section %d, not this one"
                      % HEAD_COLOUR_MEASURED))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return self_check()
    if len(argv) >= 2 and argv[1] in ("--check-image", "--tuple", "--corpus"):
        import iso_source

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("assembly: skipped -- %s" % exc)
            return SKIP
        if argv[1] == "--corpus":
            import looks as _looks

            try:
                folder = _looks.corpus_from_env(
                    argv[2] if len(argv) > 2 else None)
            except RuntimeError as exc:
                print("assembly: skipped -- %s" % exc)
                return SKIP
            return _corpus(image, folder)
        if argv[1] == "--tuple":
            if len(argv) < 3:
                print("--tuple needs a tuple, like A-A1-A-A-A")
                return 2
            return _tuple(image, argv[2])
        return _check_image(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

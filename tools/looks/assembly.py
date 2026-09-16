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
  O 44, P 50;
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

**And which primitives of the other twelve heads take the band is not
measured** -- only section 24's pair is named by index (LOOKS-TASK-08), so only
family A's band is applied here.

**FACE reaches five**, of the seven its third-party labels name and the eight
its three bits hold.  Bands 0 to 4 of the same image, 16 rows each, and then it
clamps.

**And every field clamps; none wraps.**  Measured on all six.

Usage:
    python tools/looks/assembly.py --check
    python tools/looks/assembly.py --check-image
    python tools/looks/assembly.py --tuple A-I3-A-F-A
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
  letters' variants rewrites that same section;
* the digit is the **band** of the hair sheet at 3,568 -- B's six variants come
  back as bands 0/1, 2, 1, 5, 3 and 4 of one section;
* and section 24, the one every earlier walk watched, is family **A** alone.
  Three values of 32 use it, which is exactly the "three states" that walk saw
  and read as the field's whole reach.

`None` is a value that rewrote **nothing** in the file: measured, not assumed.
Three of them -- H1, M1 and N1 -- and three even sections of the run (38, 40
and 42) never appeared, which is a suggestive pair of threes and no more than
that.  E1 is a fourth oddity: it rewrote section 48, which is D's, and may be
the game putting D's section back rather than naming E1's own.  Guessing any of
the four would be the mapping that draws perfectly and is wrong.
"""

HEAD_BAND = Effect(
    "HAIR", BAND, layout.ATLAS_BAND, len(HAIR_MAP),
    {HEAD: layout.HAIR_PRIMITIVES},
    "the band HAIR_MAP measured for this style, applied to the two hair quads "
    "of section 24 -- the one section whose hair quads are named by index "
    "(LOOKS-TASK-08).  The other twelve heads keep the disc's own window, "
    "because which of their primitives take the band is not measured")
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

def edits(values: dict) -> dict:
    """{(file, section): {primitive: (clut, band)}} for one tuple of LOOKS.

    `clut` is the id to write, `band` how many rows to add to every `v`.  A
    primitive absent from the answer is one the tuple does not touch, which is
    most of them: the edit is small by measurement, not by choice.
    """
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
            out.setdefault(key, {})
            out[key][primitives] = (effect, step)
    return out


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
    for primitives, (effect, step) in byname.items():
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
    plan = edits(values)

    out = []
    if figure == HEAD_FIGURE:
        chosen, bands = head_of(values)
        if chosen == layout.HEAD_SECTION:
            # The only section whose hair quads are known BY INDEX: the walk
            # of LOOKS-TASK-08 named them on this one.  Which primitives of
            # the other twelve take the band is not measured, so nothing is
            # banded there -- they keep the disc's own window.
            plan.setdefault((layout.MODEL, chosen), {})[
                layout.HAIR_PRIMITIVES] = (HEAD_BAND, bands[0])
    for name, index in sections_of(disc, figure, values):
        scan = section.scan(disc[name], layout.GEOMETRY_START[name])
        one = scan.sections[index]
        for at, primitive in enumerate(one.primitives):
            clut, band = combine(primitive, plan.get((name, index), {}), at)
            corner = atlas.texel(primitive, primitive.texcoords[0][0],
                                 primitive.texcoords[0][1] + band)
            record = atlas.image_at(images, *corner)
            x, y = skin.grid(clut)[1] * texture.NARROW, skin.grid(clut)[0]
            try:
                window = texture.covering(palettes, x, y, texture.NARROW)
            except texture.NoPalette:
                window = None
            out.append({
                "file": name, "section": index, "primitive": at,
                "clut": clut, "band": band,
                "image": record.offset if record else None,
                "palette": None if window is None else (x, y, texture.NARROW),
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


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("assembly.py", _checks, verbose)


def _checks(c) -> None:
    ok = c.ok
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
        byname = {BY_ROW[r].where[HEAD]: (BY_ROW[r], 2) for r in order}
        both_ways.append(combine(one, byname, 0))
    ok("two fields on the same primitive compose, and in either order",
       both_ways[0] == both_ways[1]
       == (skin.clut_id(layout.CLUT_ROW_FIRST + 2, layout.HAIR_COLUMN + 2), 0),
       "%r" % (both_ways,))
    ok("and a field passes over a primitive it does not own",
       combine(one, {BY_ROW["H.F.COL."].where[HEAD]: (BY_ROW["H.F.COL."], 3)},
               0) == (one.clut, 0))

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
    """[(first, last, distinct bodies, how many sample the hair sheet)] per run.

    The 32 heads of each run, counted rather than asserted: `layout.HEAD_RUNS`
    says where they are and this says what is in them, so a disc that does not
    hold them comes out as a number and not as a crash.
    """
    import atlas
    import section

    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    out = []
    for first, stop in layout.HEAD_RUNS:
        bodies, hairy = set(), 0
        for index in range(first, stop):
            one = scan.sections[index]
            bodies.add(bytes(data[one.offset:one.end]))
            if any(True for p in one.primitives
                   if (atlas.image_at(_IMAGES, *atlas.corners(p)[0])
                       or _NOTHING).offset == layout.HAIR_IMAGE):
                hairy += 1
        out.append((first, stop - 1, len(bodies), hairy))
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
    for (first, last, bodies, hairy), want in zip(runs, HEAD_RUN_HAIRY):
        print("  MODEL.BIN sections %d..%d: %d distinct body(ies), %d of them "
              "sampling the hair sheet" % (first, last, bodies, hairy))
        if bodies != last - first + 1:
            problems.append("sections %d..%d hold %d distinct body(ies) and "
                            "the run is %d long" % (first, last, bodies,
                                                    last - first + 1))
        if hairy != want:
            problems.append("sections %d..%d: %d sample the hair sheet, and "
                            "%d was measured" % (first, last, hairy, want))
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
               part["band"])
        seen[key] = seen.get(key, 0) + 1
    for (name, index, image, palette, band), count in sorted(
            seen.items(), key=lambda kv: str(kv[0])):
        print("    %-18s section %-3d image %-6s palette %-16s band %+d  "
              "x%d" % (name, index, image, palette, band, count))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return self_check()
    if len(argv) >= 2 and argv[1] in ("--check-image", "--tuple"):
        import iso_source

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("assembly: skipped -- %s" % exc)
            return SKIP
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

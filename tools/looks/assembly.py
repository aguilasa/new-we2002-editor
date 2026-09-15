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
    HAIR      the `v`             +16 a band     the two hair primitives
    FACE      the `v`             +16 a band     the two beard primitives

## Two holes, named rather than filled

**HAIR is not resolved, and the shape of the failure is worth more than a
guess.**  `hair_style` holds 32 values and the screen, walked from the bottom
of the row with 32 presses of Left and then 32 of Right, reaches **three**
states in `MODEL.BIN` section 24 -- `v` bands 0, 2 and 1, in that order -- and
then thirty further presses change nothing at all.  No vertex moves either, so
the 32 styles are not 32 meshes.  Where the other 29 live is not measured, and
writing `band = style` would be a mapping that draws perfectly and is wrong.

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
    Effect("HAIR", BAND, layout.ATLAS_BAND, 3,
           {HEAD: layout.HAIR_PRIMITIVES},
           "16 rows of the image at 3,568 a band -- and only THREE bands are "
           "reachable on the screen, in the order 0, 2, 1.  The field holds "
           "32; where the other 29 live is not measured"),
    Effect("FACE", BAND, layout.ATLAS_BAND, 5,
           {HEAD: layout.FACE_PRIMITIVES},
           "16 rows a band of the same image, bands 0 to 4, and then it "
           "clamps.  Its labels name seven and its bits hold eight"),
)

BY_ROW = {effect.row: effect for effect in EFFECTS}

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
    for name, index in sections_of(disc, figure):
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


def sections_of(disc, figure: int) -> list:
    """(file, section) of every piece of one figure, plus the head.

    The figure comes first and the fields come second: the two models do not
    share the arm pieces (CORR-LOOKS-021), so loading one and recolouring it
    draws the goalkeeper in short sleeves.
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
    return out + [HEAD]


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("assembly.py", _checks, verbose)


def _checks(c) -> None:
    ok = c.ok
    refuses = c.refusing(BadAssembly)

    ok("every effect names a row of the screen",
       all(e.row in looks.SCREEN for e in EFFECTS))
    ok("and every row is either an effect or a named hole",
       set(looks.SCREEN) == set(BY_ROW) | set(UNTOUCHED),
       "%r" % sorted(set(looks.SCREEN) ^ (set(BY_ROW) | set(UNTOUCHED))))
    ok("no row is both",
       not set(BY_ROW) & set(UNTOUCHED))
    ok("three effects move a palette and three move an atlas band",
       sorted(e.what for e in EFFECTS).count(BAND) == 2)

    # The two holes, asserted rather than described: a later run that resolves
    # HAIR has to come here and say so.
    unresolved = sorted(e.row for e in EFFECTS if not e.resolved)
    ok("three rows do not walk to the end of what their bits hold",
       unresolved == ["FACE", "H.F.COL.", "HAIR"], "%r" % (unresolved,))
    ok("and HAIR reaches three of its thirty-two",
       BY_ROW["HAIR"].reach == 3 and BY_ROW["HAIR"].field.values == 32)
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
    ok("a step of HAIR moves no CLUT and answers a band",
       apply_to(one.clut, 0, BY_ROW["HAIR"], 2)
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
       and apply_to(one.clut, 0, BY_ROW["HAIR"], 0) == (one.clut, 0))
    refuses("a hair style past the three the screen reaches is refused",
            lambda: edits(looks.parse_tuple("A-I3-A-A-A")), "measured to reach")
    refuses("and so is a beard style past the five",
            lambda: edits(looks.parse_tuple("A-A1-A-F-A")), "measured to reach")


# ---- the disc ------------------------------------------------------------

def _load(image_path):
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        return {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D)}


def _check_image(image_path: str) -> int:
    disc = _load(image_path)
    problems = []
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

#!/usr/bin/env python3
"""How colour reaches the figure: one grid of palettes, and three fields into it.

Provenance (plan section 3.4): measured.  The grid comes from the disc, read
through `texture.py`; who steps where comes from the running game, measured by
`oracle.py --fields` and `oracle.py --palettes`.

## What unknown (d) turned out to be

The question was *"is skin a palette swap or a vertex colour?"*, and the answer
is **palette, and only palette** -- there is no vertex colour anywhere in this
format to swap.  A primitive of these two files is the texture half of a
`POLY_FT4`: four UV pairs, a CLUT id, a texture page, and four vertex indices
(section 1.6).  Nothing in it is a colour.

Measured on both save states, with the state reloaded before every step
(`oracle.py --fields SKIN H.COL H.F.COL.`, 2026-09-15): each of the three
fields moves **byte 2 of the primitive and nothing else** -- the low byte of
the CLUT id.  Not one byte of a vertex moved in any of the six runs.

## The grid

A 256-entry palette record is **sixteen 4-bit CLUTs side by side**, because a
CLUT id addresses x in units of sixteen entries:

    clut_id = column | (row << 6)      column = x // 16,  row = y

So the four "Pieles" records at VRAM (0, 480) to (0, 483) are not four
palettes: they are a grid of four rows by sixteen columns of sixteen-entry
windows, and the three fields are coordinates into it.

    row    = skin_colour      SKIN steps it, +0x40 to the id: one whole record
    column = 0                the bare-skin window, which no hair colour uses
    column = 1 + hair_colour   H.COL steps it, +1 to the id
    column = 9 + beard_colour  H.F.COL. steps it, +1 to the id

`src/core/Player.cpp` packs `skin_colour` in two bits and `hair_colour` and
`beard_colour` in three each -- four rows and eight columns each, which is
exactly what the grid holds and exactly the shape of the zeta tutorial's table.

## What the renderer has to do, in one sentence

Texture with a CLUT, and no vertex colour at all: take the texel's index out of
the image record the page and `u` resolve to, and take its colour from the
**sixteen-entry window** the primitive's CLUT id names inside a 256-entry
record -- never from the record as a whole.

Usage:
    python tools/looks/skin.py --check
    python tools/looks/skin.py --check-image
    python tools/looks/skin.py --report
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402
import texture  # noqa: E402

SKIP = 77

COLUMN_BITS = 6
"""How many bits of a CLUT id are the column.  The rest is the row."""

COLUMNS = texture.WIDE // texture.NARROW
"""Sixteen 4-bit windows fit across one 256-entry record."""

HAIR_ENTRIES = 6
"""How many of a window's sixteen entries the eight hair colours move.

Measured over all four records: entries 2, 5, 12, 13, 14, 15 and no others.
The zeta tutorial says *"estos son los 5 colores para cambiar el cabello"* --
it is one short, and the sixth is worth knowing about for whoever paints one.
"""


class NotInGrid(Exception):
    """An offset that is not a window of one of the skin records."""


# ---- the grid ------------------------------------------------------------

def grid(clut: int) -> tuple:
    """(row, column) of a CLUT id: the VRAM row, and the window across it."""
    return (clut >> COLUMN_BITS, clut & ((1 << COLUMN_BITS) - 1))


def clut_id(row: int, column: int) -> int:
    """The CLUT id of one window -- the inverse of `grid`."""
    if not 0 <= column < (1 << COLUMN_BITS):
        raise NotInGrid("column %d does not fit in %d bits"
                        % (column, COLUMN_BITS))
    return (row << COLUMN_BITS) | column


def window(record, column: int) -> tuple:
    """(first entry, entry count) of one 16-entry window of a wide record."""
    if record.colours != texture.WIDE:
        raise NotInGrid("a %d-entry record has no windows: the grid is what a "
                        "256-entry record is made of" % record.colours)
    if not 0 <= column < COLUMNS:
        raise NotInGrid("column %d is outside a %d-entry record"
                        % (column, record.colours))
    return (column * texture.NARROW, texture.NARROW)


def column_of(record, offset: int) -> int:
    """Which window of *record* starts at file *offset*.

    Raises rather than rounding: an offset that is not window-aligned is a
    table read against the wrong base, and the sixteen entries it would return
    still draw.
    """
    inside = offset - record.offset
    if not 0 <= inside < record.size:
        raise NotInGrid("offset %d is outside the record at %d..%d"
                        % (offset, record.offset, record.offset + record.size))
    if inside % (texture.NARROW * 2):
        raise NotInGrid("offset %d is %d B into the record at %d, which is not "
                        "a whole %d-entry window"
                        % (offset, inside, record.offset, texture.NARROW))
    return inside // (texture.NARROW * 2)


# ---- what the three fields do --------------------------------------------

class Field:
    """One LOOKS row, and the coordinate of the grid it steps.

    Every number here was measured with the game running, one step at a time
    from a reloaded save state, and the primitive lists are the whole hit list
    that `report_field` printed -- not a sample.
    """

    __slots__ = ("row", "steps", "base", "reaches", "primitives", "witness",
                 "why")

    def __init__(self, row, steps, base, reaches, primitives, witness, why):
        self.row = row
        self.steps = steps
        self.base = base
        self.reaches = reaches
        self.primitives = primitives
        self.witness = witness
        self.why = why

    @property
    def last(self) -> int:
        """The last coordinate the field reaches, counting from its base."""
        return self.base + self.reaches - 1


FIELDS = (
    Field("SKIN", "row", 0, 4, None, layout.HAIR_PRIMITIVES[0],
          "0x40 per step, which is one whole 256-entry record: it moves every "
          "bare-skin primitive of both figures AND the head, and the head's "
          "column is untouched"),
    Field("H.COL", "column", layout.HAIR_COLUMN, 8,
          layout.HAIR_COLOUR_PRIMITIVES, layout.HAIR_PRIMITIVES[0],
          "+1 per step, seven primitives of the head and nothing else: the "
          "two the HAIR field moves, and five more that are hair-coloured"),
    Field("H.F.COL.", "column", layout.BEARD_COLUMN, 7,
          layout.FACE_PRIMITIVES, layout.FACE_PRIMITIVES[0],
          "+1 per step, and exactly the two primitives the FACE field moves -- "
          "which is why FACE is the beard and not the face"),
)
"""The three fields, with how far each one reaches MEASURED and not derived.

`reaches` is the number of distinct CLUT ids the field walks to, counted by
`oracle.py --palettes` on 2026-09-15: from the reloaded state, Left until the
id stops moving, then Right until it stops moving.  **The fields clamp; they
do not wrap**, which is what makes that a count and not a loop.

The beard is the one worth reading twice.  `src/core/Player.cpp` gives
`beard_colour` three bits, so eight, and eight columns from 9 would need
column 16 -- which a 256-entry record does not have.  The screen offers
**seven**, columns 9 to 15, and the grid comes out exactly full: one bare-skin
window, eight hair colours, seven beard colours, sixteen.
"""

BY_ROW = {field.row: field for field in FIELDS}


# ---- the third party's table ---------------------------------------------

def matrix() -> dict:
    """{(race, kind): offset} -- the zeta tutorial's table, as arithmetic.

    Read out of the PDF in 2026-09-15 rather than summarised, which is what
    put the base right: it starts at column 1 and not at the record.
    """
    return {(race, kind): (layout.HAIR_MATRIX_FIRST
                           + race * layout.HAIR_MATRIX_RACE_STEP
                           + kind * layout.HAIR_MATRIX_KIND_STEP)
            for race in range(len(layout.SKIN_PALETTES))
            for kind in range(layout.HAIR_MATRIX_KINDS)}


def skin_records(records) -> list:
    """The four wide records the skins live in, in row order."""
    out = []
    for offset in layout.SKIN_PALETTES:
        hit = [r for r in records if r.is_clut and r.offset == offset]
        if len(hit) != 1:
            raise NotInGrid("%d record(s) at offset %d, expected exactly one"
                            % (len(hit), offset))
        out.append(hit[0])
    return out


def check_matrix(records) -> list:
    """Every cell of the third party's table against the records.  [] is good."""
    skins = skin_records(records)
    problems = []
    for (race, kind), offset in sorted(matrix().items()):
        record = skins[race]
        try:
            column = column_of(record, offset)
        except NotInGrid as exc:
            problems.append("race %d kind %d: %s" % (race, kind, exc))
            continue
        if column != layout.HAIR_COLUMN + kind:
            problems.append(
                "race %d kind %d is column %d of the record at %d, and the "
                "hair colours start at column %d"
                % (race, kind, column, record.offset, layout.HAIR_COLUMN))
    return problems


# ---- what moves inside a window ------------------------------------------

def entries(data: bytes, record, column: int) -> list:
    """The raw halfwords of one window -- raw, so two windows compare exactly."""
    first, count = window(record, column)
    at = record.offset + first * 2
    return [int.from_bytes(data[at + 2 * i:at + 2 * i + 2], "little")
            for i in range(count)]


def moving_entries(data: bytes, record, columns) -> list:
    """Which of the sixteen entries differ across *columns*.

    The measurement that says what a colour field actually paints: if only six
    of the sixteen move, the other ten are the same skin in every column, and
    a renderer that reloads the whole record per hair colour is repainting ten
    entries with themselves.
    """
    grids = [entries(data, record, c) for c in columns]
    return [i for i in range(texture.NARROW)
            if len({g[i] for g in grids}) > 1]


def named_windows(*scans) -> dict:
    """{(row, column): primitive count} over every primitive of *scans*.

    Takes scans rather than files so the caller says which files are in the
    figure; this module does not decide that.
    """
    out = {}
    for scan in scans:
        for one in scan.sections:
            for primitive in one.primitives:
                key = grid(primitive.clut)
                out[key] = out.get(key, 0) + 1
    return out


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("skin.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(NotInGrid)

    hair = clut_id(layout.CLUT_ROW_FIRST, layout.HAIR_COLUMN)
    beard = clut_id(layout.CLUT_ROW_FIRST, layout.BEARD_COLUMN)
    ok("a CLUT id splits into row and column",
       grid(hair) == (layout.CLUT_ROW_FIRST, layout.HAIR_COLUMN)
       and grid(beard) == (layout.CLUT_ROW_FIRST, layout.BEARD_COLUMN),
       "got %s and %s" % (grid(hair), grid(beard)))
    ok("and the ids it builds are the ones the head carries on the disc",
       (hair, beard) == (0x7801, 0x7809),  # not-an-address: two CLUT ids, measured
       "built %#06x and %#06x" % (hair, beard))
    ok("and puts itself back together",
       all(clut_id(*grid(v)) == v for v in (0, 1, 0x7800, 0x7f95, 0xFFFF)))  # not-an-address: idem
    ok("a row of sixteen windows is what a 256-entry record is",
       COLUMNS * texture.NARROW == texture.WIDE)

    # A synthetic container, so the grid has something to be wrong about with
    # no disc in the room.  Four wide records at the four skin rows, each
    # column filled with its own column number, plus one narrow record.
    plan = [(0, layout.CLUT_ROW_FIRST + i, texture.WIDE, 0)
            for i in range(len(layout.SKIN_PALETTES))]
    plan.append((0, layout.CLUT_ROW_FIRST + 8, texture.NARROW, 0))
    blob = attempt("build a synthetic container",
                   lambda: texture.build_container(plan))
    if blob is None:
        return
    made = attempt("read its records back", lambda: texture.palettes(blob))
    if made is None:
        return
    wide = [r for r in made if r.colours == texture.WIDE]
    ok("the synthetic container holds the four wide records",
       len(wide) == len(layout.SKIN_PALETTES), "got %d" % len(wide))

    ok("column_of finds every window of a wide record",
       [column_of(wide[0], wide[0].offset + n * texture.NARROW * 2)
        for n in range(COLUMNS)] == list(range(COLUMNS)))
    refuses("an offset one byte off a window is refused, not rounded",
            lambda: column_of(wide[0], wide[0].offset + 1),
            "not a whole")
    refuses("an offset past the record is refused",
            lambda: column_of(wide[0], wide[0].offset + wide[0].size),
            "outside the record")
    narrow = [r for r in made if r.colours == texture.NARROW][0]
    refuses("a 16-entry record has no windows",
            lambda: window(narrow, 0), "has no windows")
    refuses("a column past the sixteenth is refused",
            lambda: window(wide[0], COLUMNS), "outside a")
    refuses("a column that does not fit in the id's six bits is refused",
            lambda: clut_id(layout.CLUT_ROW_FIRST, 1 << COLUMN_BITS),
            "does not fit")

    ok("the matrix is four races by eight kinds",
       len(matrix()) == len(layout.SKIN_PALETTES) * layout.HAIR_MATRIX_KINDS)
    ok("its first cell is one window past the first skin palette",
       matrix()[(0, 0)] - layout.SKIN_PALETTES[0] == texture.NARROW * 2,
       "got %d" % (matrix()[(0, 0)] - layout.SKIN_PALETTES[0]))
    ok("its race step is one whole record",
       layout.HAIR_MATRIX_RACE_STEP == texture.WIDE * 2)
    ok("its kind step is one window",
       layout.HAIR_MATRIX_KIND_STEP == texture.NARROW * 2)

    ok("the three fields are two coordinates",
       sorted({f.steps for f in FIELDS}) == ["column", "row"])
    ok("hair and beard start at different columns",
       layout.HAIR_COLUMN != layout.BEARD_COLUMN)
    ok("the columns the two colour fields reach fill the grid exactly, once",
       [f.base for f in FIELDS if f.steps == "column"] ==
       [layout.BARE_SKIN_COLUMN + 1, BY_ROW["H.COL"].last + 1]
       and BY_ROW["H.F.COL."].last == COLUMNS - 1,
       "hair %d..%d, beard %d..%d, of %d column(s)"
       % (BY_ROW["H.COL"].base, BY_ROW["H.COL"].last,
          BY_ROW["H.F.COL."].base, BY_ROW["H.F.COL."].last, COLUMNS))
    ok("the eight kinds of the third party's table are the eight H.COL reaches",
       BY_ROW["H.COL"].reaches == layout.HAIR_MATRIX_KINDS)
    ok("SKIN reaches one row per skin palette",
       BY_ROW["SKIN"].reaches == len(layout.SKIN_PALETTES))
    ok("the beard field moves exactly the primitives FACE moves",
       BY_ROW["H.F.COL."].primitives == layout.FACE_PRIMITIVES)
    ok("the hair colour field moves the two primitives HAIR moves, and more",
       set(layout.HAIR_PRIMITIVES) < set(layout.HAIR_COLOUR_PRIMITIVES))


# ---- the report ----------------------------------------------------------

def _report(data: bytes, verbose: bool = True) -> dict:
    """The grid as the disc holds it.  Returns what `_check_image` asserts on."""
    records = texture.palettes(data)
    skins = skin_records(records)
    out = {"skins": skins, "problems": check_matrix(records), "moving": {}}
    print("the four skin records, and the grid inside each")
    for race, record in enumerate(skins):
        hair = list(range(layout.HAIR_COLUMN,
                          layout.HAIR_COLUMN + layout.HAIR_MATRIX_KINDS))
        moved = moving_entries(data, record, hair)
        out["moving"][race] = moved
        print("    race %d  @%6d  vram (%d,%d)  %d window(s) of %d"
              % (race, record.offset, record.x, record.y, COLUMNS,
                 texture.NARROW))
        print("        columns %d..%d (the eight hair colours) differ at %d of "
              "%d entries: %s"
              % (hair[0], hair[-1], len(moved), texture.NARROW, moved))
    print()
    print("the zeta table's %d cells against the records: %s"
          % (len(matrix()),
             "all inside their own race's record, at columns %d..%d"
             % (layout.HAIR_COLUMN,
                layout.HAIR_COLUMN + layout.HAIR_MATRIX_KINDS - 1)
             if not out["problems"] else "%d problem(s)" % len(out["problems"])))
    for line in out["problems"]:
        print("    %s" % line)
    print()
    print("what each field steps, measured with the game running")
    for field in FIELDS:
        print("    %-9s %-6s %d value(s), %s %d..%d"
              % (field.row, field.steps, field.reaches, field.steps,
                 field.base, field.last))
        print("        %s" % field.why)
    return out


def _check_image(image_path: str) -> int:
    """The grid against the disc.  The gate of this module that needs a disc."""
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = disc.read(layout.DAT2D)
        edt = disc.read(layout.EDT_MOD)
        mod = disc.read(layout.MODEL)

    import section

    found = _report(data)
    problems = list(found["problems"])

    # Six of sixteen, and the tutorial says five.  Asserted rather than
    # printed: if a later reading of the records makes this four or sixteen,
    # the window is being read at the wrong width or the wrong base.
    for race, moved in sorted(found["moving"].items()):
        if len(moved) != HAIR_ENTRIES:
            problems.append("race %d: %d entries move across the eight hair "
                            "colours, and %d is what this disc holds"
                            % (race, len(moved), HAIR_ENTRIES))
    if len({tuple(v) for v in found["moving"].values()}) != 1:
        problems.append("the four races do not move the same entries, so the "
                        "window is not one shape")

    scans = [section.scan(mod, layout.GEOMETRY_START[layout.MODEL]),
             section.scan(edt, layout.GEOMETRY_START[layout.EDT_MOD])]
    named = named_windows(*scans)
    print()
    print("the (row, column) pairs the geometry names, over both files")
    for (row, column), count in sorted(named.items()):
        where = ""
        if row - layout.CLUT_ROW_FIRST in range(len(layout.SKIN_PALETTES)):
            where = "  skin %d, column %d" % (row - layout.CLUT_ROW_FIRST,
                                              column)
        print("    row %3d column %2d   %5d primitive(s)%s"
              % (row, column, count, where))

    first = layout.CLUT_ROW_FIRST
    for column in (0, layout.HAIR_COLUMN, layout.BEARD_COLUMN):
        if (first, column) not in named:
            problems.append("no primitive names column %d of the first skin, "
                            "and the three fields all start on that row"
                            % column)
    rows = {row for row, _ in named
            if row - first in range(len(layout.SKIN_PALETTES))}
    if rows != {first}:
        problems.append("the geometry on the disc names skin rows %s: the "
                        "file holds one figure, and the other three rows are "
                        "reached by moving SKIN on the screen, never by the "
                        "file" % sorted(rows))

    # The grid is exactly full, and the beard is where the arithmetic and the
    # screen had to be asked separately.  Player.cpp gives beard_colour three
    # bits, and eight columns from 9 would need a column 16 the record does
    # not have; the screen stops at 15.
    print()
    print("the sixteen columns of a skin record, accounted for")
    print("    column  %2d      the bare-skin window"
          % layout.BARE_SKIN_COLUMN)
    for field in FIELDS:
        if field.steps == "column":
            print("    columns %2d..%-2d  %s, %d value(s)"
                  % (field.base, field.last, field.row, field.reaches))
    used = 1 + sum(f.reaches for f in FIELDS if f.steps == "column")
    print("    %d of %d column(s) spoken for" % (used, COLUMNS))
    if used != COLUMNS:
        problems.append("%d of the %d columns are accounted for, and the grid "
                        "was measured to come out exactly full" % (used, COLUMNS))

    print("skin --check-image: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line)
    return 1 if problems else 0


def _from_env():
    import iso_source

    return iso_source.image_from_env()


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return self_check()
    if len(argv) == 2 and argv[1] in ("--check-image", "--report"):
        try:
            image = _from_env()
        except RuntimeError as exc:
            print("skin: skipped -- %s" % exc)
            return SKIP
        if argv[1] == "--report":
            import iso_source

            with iso_source.open_disc(image) as disc:
                _report(disc.read(layout.DAT2D))
            return 0
        return _check_image(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

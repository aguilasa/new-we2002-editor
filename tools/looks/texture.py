#!/usr/bin/env python3
"""The palettes of `DAT2D.BIN`, and the field that was never a tag.

Provenance (plan section 3.4): measured here, on the Japanese disc, against the
CLUT ids the geometry of `EDT_MOD.BIN` and `MODEL.BIN` already names.

## The lacuna, and what it really was

`tools/pes2/bin_archive.py` answers `23 image(s), 0 clut(s)` for this file, and
section 1.7 of the plan read that as a scanner that cannot find the second
list.  It is not.  The list is there -- 267 records, ending at the file's last
bytes -- and the walk misses it because of one word in the record:

    [7] 0x800f    a constant tag, and the thing that makes the record
                  findable without knowing where the list is

**It is not a constant and it is not a tag.**  It is the 64 KiB bank of the
16-bit offset in field 6, biased so that bank 0 reads `0x800f`:

    offset = fields[6] + (fields[7] - RECORD_TAG_BASE) * RECORD_BANK

Four containers of this disc settle it, and the assertion is not the arithmetic
but what lands at the resolved address -- an LZSS stream that decompresses to
exactly the rectangle its own record declares:

| file | bytes | tag | bank | images decompressing to their declared rect |
|---|---:|---|---:|---|
| `DAT2D.BIN`   |  81,124 | 0x800f | +0 | 23 of 23 |
| `DATSEL3.BIN` |  65,884 | 0x800f | +0 | 20 of 20 |
| `EDTR_2D.BIN` |  73,856 | 0x8010 | +1 |   2 of 2 |
| `DATSEL2.BIN` | 124,812 | 0x8010 | +1 | 15 of 15 |
| `DAT_CG.BIN`  | 101,416 | 0x8010 | +1 |   9 of 9 |
| `DATSEL.BIN`  | 223,496 | 0x8012 | +3 |   6 of 6 |

With the bank ignored, `DATSEL.BIN`'s six records point at 2,012..25,856 and
none of them decompresses to its rect.  A constant `0x800f` works on every
container whose payload fits in the first 64 KiB, which is every container of
the four PES2-family discs the other project measured -- so the constant was
never wrong there, and it was never right either.

## What the file holds, measured

The image list closes at 65,878 and the palette bank begins at 65,892, after
fourteen zero bytes.  From there to 76,836 the payloads **tile exactly**: 262
palettes of 16 entries and 5 of 256 come to 10,944 bytes, and 65,892 + 10,944
is where the CLUT record list itself starts.  Tiling is the check this module
runs, not the offsets: an arithmetic that resolves to a plausible-looking place
and leaves a hole has got something wrong.

The strip lands in VRAM in three shapes, and the geometry uses all three:

| VRAM rows | records | entries | what the geometry does with them |
|---|---:|---:|---|
| 480, 481, 482, 483 | 1 each | 256 | the four skin tones |
| 484 | 7 | 256 and 16 | the boots, and six narrow palettes beside them |
| 496 to 511 | 16 each | 16 | 256 narrow palettes in a 16x16 grid |

**A 4-bit CLUT id can point INSIDE a 256-entry palette**, and this disc does it
constantly: the bare skin samples (0, 480), the head samples (16, 480) and
(144, 480), and all three are entries of the one wide record at (0, 480).  So
"which palette" is not a lookup by equality -- it is the record whose span
COVERS the id, at the width the primitive's own page depth asks for.  That is
what `covering()` does, and getting it wrong is the silent failure of this
phase: the wrong sixteen entries are still sixteen entries and still draw.

## The two third-party labels, and how they fared

The CARP table (`Offsets WE2002 - CARP/Dat/DAT2D.BIN.txt`) names five blocks.
Both survive contact with the disc, and neither was taken on trust:

- **"Pieles" at 65,892 / 66,404 / 66,916 / 67,428** are the four records at
  VRAM (0, 480) to (0, 483), 256 entries each.  What confirms the label is not
  the stride: it is that LOOKS-TASK-08 measured `SKIN` moving every affected
  primitive's CLUT id by `+0x40`, which is **exactly one VRAM row**, and that
  the pieces with bare skin are the ones it moves.
- **"Botines" at 67,940** is the fifth wide record, at VRAM (0, 484).  The
  confirmation is independent of the label: sections 9 and 10 -- the two that
  LOOKS-TASK-09 named the boots, by mirrors and by being shared between the
  two figures -- sample **(0, 484) and nothing else**, and no other section
  samples it.

Usage:
    python tools/looks/texture.py --check
    python tools/looks/texture.py --check-image [<japanese.bin>]
    python tools/looks/texture.py --report [<japanese.bin>]
    python tools/looks/texture.py --survey [<japanese.bin>]
"""

from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import layout  # noqa: E402

RECORD = 16
"""Bytes in one container record: eight little-endian 16-bit fields."""

KIND_IMAGE = 10
KIND_CLUT = 9

NARROW = 16
"""Entries in a 4-bit CLUT."""

WIDE = 256
"""Entries in an 8-bit CLUT."""


class BadTable(Exception):
    """A record list that does not hold together."""


class NoPalette(Exception):
    """No record covers the CLUT id a primitive names."""


class Record:
    """One container record, with its offset already resolved out of its bank."""

    __slots__ = ("pos", "kind", "param", "x", "y", "w", "h", "offset", "bank")

    def __init__(self, pos: int, fields, bank: int):
        self.pos = pos
        self.kind = fields[0] & 0xFF  # not-an-address: the record's own layout
        self.param = fields[0] >> 8
        self.x, self.y, self.w, self.h = fields[1:5]
        self.bank = bank
        self.offset = fields[6] + bank * layout.RECORD_BANK

    @property
    def is_image(self) -> bool:
        return self.kind == KIND_IMAGE

    @property
    def is_clut(self) -> bool:
        return self.kind == KIND_CLUT

    @property
    def colours(self) -> int:
        """How many entries this palette holds -- 16 or 256 on this disc."""
        return self.w

    @property
    def depth(self) -> int:
        """4 or 8, from THIS palette's width and nothing else.

        Per record, never per file: `DAT2D.BIN` holds both widths, and a
        per-file answer lets five outvote 262 or the other way round.
        """
        return 4 if self.w <= NARROW else 8

    @property
    def size(self) -> int:
        """Bytes of payload: a palette is `colours` entries of BGR555."""
        return self.w * self.h * 2

    def covers(self, x: int, y: int, colours: int) -> bool:
        """Does this record hold the `colours` entries starting at VRAM (x, y)?"""
        return (self.y == y and self.x <= x
                and x + colours <= self.x + self.w)

    def __repr__(self) -> str:
        name = {KIND_IMAGE: "image", KIND_CLUT: "clut"}.get(self.kind, "?")
        return ("%-5s @%6d  vram (%4d,%4d) %3dx%-3d" %
                (name, self.offset, self.x, self.y, self.w, self.h))


class Table:
    """One record list: every record shares the bank word that closes it."""

    __slots__ = ("tag", "bank", "start", "end", "records")

    def __init__(self, tag: int, start: int, end: int, records: list):
        self.tag = tag
        self.bank = tag - layout.RECORD_TAG_BASE
        self.start = start
        self.end = end
        self.records = records

    def __repr__(self) -> str:
        return ("Table(tag=0x%04x, bank=%+d, %d record(s) at %d..%d)"
                % (self.tag, self.bank, len(self.records), self.start, self.end))


def _kind_ok(fields, size: int) -> bool:
    """The record says it is an image or a CLUT."""
    return fields[0] & 0xFF in (KIND_IMAGE, KIND_CLUT)  # not-an-address: the record's own layout


def _shape_ok(fields, size: int) -> bool:
    """It has a width and a height, and the word that is always zero is."""
    return fields[5] == 0 and fields[3] != 0 and fields[4] != 0


def _vram_ok(fields, size: int) -> bool:
    """It lands somewhere a PSX frame buffer has."""
    return fields[1] <= layout.VRAM_WIDTH and fields[2] < layout.VRAM_HEIGHT


def _clut_ok(fields, size: int) -> bool:
    """A CLUT is one row of 16 or 256, below the palette rows."""
    if fields[0] & 0xFF != KIND_CLUT:  # not-an-address: idem
        return True
    return (fields[4] == 1 and fields[3] in (NARROW, WIDE)
            and fields[2] >= layout.CLUT_ROW_FIRST)


def _size_ok(fields, size: int) -> bool:
    """An image starts inside the file that holds it."""
    if fields[0] & 0xFF == KIND_CLUT:  # not-an-address: idem
        return True
    return fields[6] < size


CONDITIONS = (("kind", _kind_ok), ("shape", _shape_ok), ("vram", _vram_ok),
              ("clut", _clut_ok), ("size", _size_ok))
"""The five tests of `plausible()`, separately, so `--survey` can drop one.

**Only `kind` suppresses anything on this disc**, and that is measured, not
assumed: dropping any one of the other four -- or three of them together --
changes zero records across all 245 files, while dropping `kind` alone lets
**123** more through and keeping ONLY `kind` lets **197**.  Those two are
different numbers for different questions, and the prose this replaces had them
confused.  The other four conditions are here for the record this disc does not
contain, not for the one it does; `--survey` is what keeps the claim honest
(CORR-LOOKS-022).
"""


def plausible(fields, size: int, skip=()) -> bool:
    """Is this eight-field tuple a record, or a coincidence in a stream?

    The tag alone is two bytes and turns up inside compressed data; what makes
    a run of records a list is that every one of them describes something a
    container can hold.  Without the whole filter the same sweep over this disc
    reports **70,978** more "records", the stadium meshes included; with the
    `kind` test dropped and the rest kept, **123** more.  Both come out of
    `--survey`, which exists because the number this docstring used to carry --
    2,151 in 40 files -- reproduced under no reading at all.
    """
    return all(test(fields, size) for name, test in CONDITIONS
               if name not in skip)


def tables(data: bytes, skip=()) -> list:
    """Every record list in one container, found by its terminator.

    The marker is the pair `[bank word][0x00ff]`, which is the same one
    `bin_archive.entries()` looks for; what is not assumed here is the value of
    the bank word, because it is the file's own 64 KiB page and not a tag.
    """
    found: dict = {}
    i = 0
    end = struct.pack("<H", layout.RECORD_LIST_END)
    while True:
        i = data.find(end, i + 1)
        if i < 0:
            break
        if i < RECORD:
            continue
        tag = struct.unpack_from("<H", data, i - 2)[0]
        if tag < layout.RECORD_TAG_BASE or not tag & 0x8000:  # not-an-address: the sign bit the word always carries
            continue
        bank = tag - layout.RECORD_TAG_BASE
        run: list = []
        q = i - RECORD
        while q >= 0 and struct.unpack_from("<H", data, q + RECORD - 2)[0] == tag:
            fields = struct.unpack_from("<8H", data, q)
            if not plausible(fields, len(data), skip):
                break
            run.append(Record(q, fields, bank))
            q -= RECORD
        if run:
            run.reverse()
            found[run[0].pos] = Table(tag, run[0].pos, i + 2, run)
    return [found[k] for k in sorted(found)]


def images(data: bytes) -> list:
    """Every image record of a container, in file order."""
    return [r for t in tables(data) for r in t.records if r.is_image]


def palettes(data: bytes) -> list:
    """Every CLUT record of a container, in file order."""
    return [r for t in tables(data) for r in t.records if r.is_clut]


def widths(records) -> dict:
    """{entries: how many records} -- the count criterion 2 of the task asks for."""
    out: dict = {}
    for rec in records:
        if rec.is_clut:
            out[rec.colours] = out.get(rec.colours, 0) + 1
    return out


def span(records) -> tuple:
    """(first byte, last byte) of the payloads of `records`."""
    if not records:
        raise BadTable("no record to span")
    return (min(r.offset for r in records),
            max(r.offset + r.size for r in records))


def tiling(records, upto: int) -> list:
    """The holes and the overlaps between consecutive payloads, in order.

    Empty is the answer that means the resolution is right.  It is the check
    worth running because it cannot be satisfied by accident: an offset rule
    that is off by a bank, or a width read at the wrong depth, leaves a gap or
    an overlap immediately, and `upto` makes the last payload answer for the
    end of the bank as well.
    """
    problems = []
    ordered = sorted(records, key=lambda r: r.offset)
    for before, after in zip(ordered, ordered[1:]):
        gap = after.offset - (before.offset + before.size)
        if gap:
            problems.append((before.offset, after.offset, gap))
    last = ordered[-1]
    tail = upto - (last.offset + last.size)
    if tail:
        problems.append((last.offset, upto, tail))
    return problems


def covering(records, x: int, y: int, colours: int) -> Record:
    """The record holding the `colours` entries at VRAM (x, y).

    Raises NoPalette rather than guessing.  Returning "the nearest" or "the
    first" would hand back sixteen entries that draw perfectly and are the
    wrong colours, which is the one failure of this phase that has no symptom.
    """
    hits = [r for r in records if r.is_clut and r.covers(x, y, colours)]
    if not hits:
        raise NoPalette(
            "nothing in this container covers %d entries at VRAM (%d, %d)"
            % (colours, x, y))
    if len(hits) > 1:
        # Narrower wins: a wide record covers its own sub-ranges, and the
        # narrow record that names one exactly is the more specific answer.
        hits.sort(key=lambda r: r.w)
    return hits[0]


def read_palette(data: bytes, record: Record, colours: int | None = None,
                 first: int = 0) -> list:
    """`colours` RGBA entries from a palette record, BGR555 on the disc.

    The top bit is the PSX semi-transparency flag; an entry that is black with
    that bit clear is the transparent one.  `colours` defaults to the record's
    own width and is passed in when a 4-bit primitive samples a slice of a
    256-entry palette.

    `first` is WHICH slice, in entries from the start of the record, and it is
    not decoration: a 4-bit CLUT id that lands inside a 256-entry record names
    one of its sixteen windows, and reading from the record's own start hands
    back window zero -- sixteen entries that draw perfectly and are somebody
    else's colours.  `window_for` is what resolves the pair.
    """
    want = record.colours if colours is None else colours
    if first < 0 or first + want > record.colours:
        raise BadTable("asked for %d entries from %d of a %d-entry palette"
                       % (want, first, record.colours))
    at = record.offset + first * 2
    raw = data[at:at + want * 2]
    if len(raw) < want * 2:
        raise BadTable("palette at %d wants %d B and the file has %d left"
                       % (at, want * 2, len(raw)))
    return [_rgba(struct.unpack_from("<H", raw, 2 * i)[0])
            for i in range(want)]


def _rgba(value: int) -> tuple:
    """One BGR555 halfword as the RGBA tuple `read_palette` returns.

    Written once and used by both, so the gate compares against the reading
    rule rather than against a second copy of it.
    """
    r = (value & 0x1F) << 3  # not-an-address: the BGR555 field
    g = ((value >> 5) & 0x1F) << 3  # not-an-address: idem
    b = ((value >> 10) & 0x1F) << 3  # not-an-address: idem
    opaque = value & 0x8000 or (value & 0x7FFF)  # not-an-address: the STP bit
    return (r | r >> 5, g | g >> 5, b | b >> 5, 255 if opaque else 0)


def window_for(records, x: int, y: int, colours: int) -> tuple:
    """(record, first entry) of the `colours` entries at VRAM (x, y).

    The second half is what `covering` alone cannot say.  A record's `x` is
    where the record starts, not where the read does, so a narrow id inside a
    wide record has to be told how far in it sits -- and getting that wrong
    costs no error and no crash, only the wrong colours.
    """
    record = covering(records, x, y, colours)
    return (record, x - record.x)


def palette_for(data: bytes, primitive, records=None) -> list:
    """The entries one primitive samples, at the width its own page declares.

    `tpage_depth` is 0 for a 4-bit CLUT and 1 for an 8-bit one, and it -- not
    the record -- decides how many entries the primitive reads.  The record
    decides where they start.
    """
    if records is None:
        records = palettes(data)
    colours = WIDE if primitive.tpage_depth else NARROW
    x, y = primitive.clut_vram
    record, first = window_for(records, x, y, colours)
    return read_palette(data, record, colours, first)


# ---- the synthetic container, for a gate that runs without a disc --------

def build_container(entries, bank: int = 1, gap: int = 0) -> bytes:
    """A container holding `entries` palettes and the list that indexes them.

    `entries` is a sequence of (x, y, colours, fill).  The payloads are laid
    out contiguously starting one bank in, so the record offsets have to be
    resolved to be read at all -- which is what makes the red case of the bank
    rule reachable with no disc image in the room.  `gap` pads between them,
    which is the shape a wrongly resolved bank leaves behind.
    """
    body = bytearray(bank * layout.RECORD_BANK)
    records = []
    for x, y, colours, fill in entries:
        if records:
            body += bytes(gap)
        records.append((len(body), x, y, colours))
        # `fill` may be one halfword for every entry, or one per entry.  The
        # second shape exists so a gate can tell one window of a wide record
        # from another: with a single fill every window reads back the same,
        # and an offset that is never applied passes.
        values = ([fill] * colours if isinstance(fill, int)
                  else list(fill))
        if len(values) != colours:
            raise BadTable("%d fill value(s) for a %d-entry palette"
                           % (len(values), colours))
        for value in values:
            body += struct.pack("<H", value)
    tag = layout.RECORD_TAG_BASE + bank
    table = bytearray()
    for offset, x, y, colours in records:
        table += struct.pack("<8H", KIND_CLUT, x, y, colours, 1, 0,
                             offset - bank * layout.RECORD_BANK, tag)
    table += struct.pack("<H", layout.RECORD_LIST_END)
    return bytes(body + table)


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    import harness
    return harness.run("texture.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(NoPalette)
    bad = c.refusing(BadTable)

    # Two palettes, one wide and one narrow, on two VRAM rows, laid out one
    # bank in -- the shape DAT2D.BIN really has, at a size a gate can hold.
    plan = ((0, layout.CLUT_ROW_FIRST, WIDE, 0x1234),          # not-an-address: a fill
            (0, layout.CLUT_ROW_FIRST + 1, NARROW, 0x0555),    # not-an-address: idem
            (16, layout.CLUT_ROW_FIRST + 1, NARROW, 0x7FFF))   # not-an-address: idem
    data = build_container(plan)

    found = attempt("scan the synthetic container", lambda: tables(data), default=[])
    ok("one list, and every record of it is a palette",
       len(found) == 1 and len(found[0].records) == len(plan)
       and all(r.is_clut for r in found[0].records),
       "%r" % (found,))
    ok("the list's bank came out of its own closing word",
       found and found[0].bank == 1, "%r" % (found,))

    recs = palettes(data)
    ok("the widths are counted apart, not averaged",
       widths(recs) == {WIDE: 1, NARROW: 2}, "%r" % (widths(recs),))

    # The bank, and why it is the whole point: with it dropped, every offset
    # here lands in the leading zeros and the palettes read back black.
    first = recs[0]
    ok("a resolved offset is a bank past the raw field",
       first.offset >= layout.RECORD_BANK, "%d" % first.offset)
    ok("and the bytes there are the ones that were written",
       read_palette(data, first, 1)[0][:3] != (0, 0, 0),
       "%r" % (read_palette(data, first, 1)[0],))

    # The payloads tile: no hole, no overlap, and the last one ends where the
    # list begins.  This is the assertion that a wrong bank cannot pass.
    ok("the payloads tile up to the start of the list",
       tiling(recs, found[0].start) == [], "%r" % (tiling(recs, found[0].start),))

    # Red: a hole is reported rather than smoothed over.
    holed = build_container(plan, gap=8)
    holed_recs = palettes(holed)
    ok("a bank that does not tile is reported",
       tiling(holed_recs, tables(holed)[0].start) != [])

    # Covering, which is where a swapped palette would be born.  The narrow id
    # at (16, row+1) has its OWN record, and the wide record on the row below
    # covers (16, row) -- so the two ids differ by one row and must not come
    # back as the same palette.
    row = layout.CLUT_ROW_FIRST
    inside = attempt("a 4-bit id inside a 256-entry palette",
                     lambda: covering(recs, 16, row, NARROW))
    ok("a narrow id inside a wide record resolves to that record",
       inside is not None and inside.w == WIDE and inside.y == row,
       "%r" % (inside,))
    own = attempt("a 4-bit id with a record of its own",
                  lambda: covering(recs, 16, row + 1, NARROW))
    ok("and the record that names it exactly wins over any wider one",
       own is not None and own.w == NARROW and own.y == row + 1, "%r" % (own,))
    ok("the two ids are NOT the same palette",
       inside is not None and own is not None and inside.offset != own.offset,
       "%r %r" % (inside, own))
    ok("and they do not read back the same entries",
       read_palette(data, inside, NARROW) != read_palette(data, own, NARROW))

    # The window inside a wide record, which is the half `covering` does not
    # answer.  Every entry of this one differs from every other, so a read that
    # ignores the offset comes back with window zero and is caught; with a
    # single fill value the two reads are equal and the defect passes.
    steps = tuple(range(1, WIDE + 1))
    graded = build_container(((0, layout.CLUT_ROW_FIRST, WIDE, steps),))
    wide = palettes(graded)[0]
    pair = attempt("resolve the window of a narrow id inside a wide record",
                   lambda: window_for(palettes(graded), 3 * NARROW,
                                      layout.CLUT_ROW_FIRST, NARROW),
                   default=(None, None))
    ok("the record is the wide one and the offset is the window, in entries",
       pair[0] is not None and pair[0].w == WIDE and pair[1] == 3 * NARROW,
       "%r" % (pair,))
    shifted = attempt("read that window",
                      lambda: read_palette(graded, wide, NARROW, pair[1]),
                      default=[])
    zeroth = attempt("read window zero of the same record",
                     lambda: read_palette(graded, wide, NARROW), default=[])
    ok("a window past the first does not read back as the first",
       bool(shifted) and shifted != zeroth, "%r" % (shifted[:2],))
    ok("and it is the entries the record really holds there",
       shifted == [_rgba(v) for v in steps[3 * NARROW:4 * NARROW]],
       "%r" % (shifted[:2],))

    # Red: a window that runs off the end of the record refuses instead of
    # reading whatever follows it in the file.
    bad("a window past the end of a record refuses",
        lambda: read_palette(graded, wide, NARROW, WIDE - 8), "asked for")

    # Red: an id nothing covers refuses instead of falling back on a neighbour.
    refuses("an uncovered CLUT id refuses",
            lambda: covering(recs, 0, row + 8, NARROW), "nothing in this container")
    refuses("and so does one that starts inside a record but runs off its end",
            lambda: covering(recs, 240, row, WIDE), "nothing in this container")

    # Red: asking a 16-entry palette for 256 is a BadTable, not a short list.
    bad("a wide read of a narrow palette refuses",
        lambda: read_palette(data, own, WIDE), "asked for")

    # Red: a coincidence in a stream is not a list.  The bytes below end with
    # the right marker and carry nothing a container can hold.
    noise = b"\x00" * 32 + struct.pack("<H", layout.RECORD_TAG_BASE + 1) \
        + struct.pack("<H", layout.RECORD_LIST_END)
    ok("a marker with no plausible record before it yields no list",
       tables(noise) == [], "%r" % (tables(noise),))

    # Rule 1: every number this module carries about the disc comes from
    # layout.py.  The check is cheap and states the intent.
    ok("the bank size and the tag base are layout's, not this module's",
       layout.RECORD_BANK > 0 and layout.RECORD_TAG_BASE > 0)


def _report(data: bytes, disc_path: str) -> None:
    found = tables(data)
    for table in found:
        kinds = {}
        for rec in table.records:
            kinds[rec.kind] = kinds.get(rec.kind, 0) + 1
        print("  %r" % table)
        print("      %d image(s), %d clut(s)"
              % (kinds.get(KIND_IMAGE, 0), kinds.get(KIND_CLUT, 0)))
    pal = palettes(data)
    if pal:
        counts = widths(pal)
        print("  %d palette(s): %s"
              % (len(pal), ", ".join("%d of %d entries (%d bpp)"
                                     % (n, w, 4 if w <= NARROW else 8)
                                     for w, n in sorted(counts.items()))))
        first, last = span(pal)
        print("  the bank runs %d..%d (%d B) and the list starts at %d"
              % (first, last, last - first, found[-1].start))
        rows: dict = {}
        for rec in pal:
            rows.setdefault(rec.y, []).append(rec)
        for y in sorted(rows):
            here = rows[y]
            print("      VRAM row %d: %2d record(s), x %s"
                  % (y, len(here),
                     ", ".join("%d(%d)" % (r.x, r.w) for r in here[:8])
                     + (" ..." if len(here) > 8 else "")))


def _check_image(image_path: str) -> int:
    """Every claim in this module's docstring, against the real disc."""
    import collections

    import iso_source
    import modelfile

    failures = 0
    with iso_source.open_disc(image_path) as disc:
        try:
            data = disc.read(layout.DAT2D)
        except layout.WrongDisc as exc:
            print("  FAILED %s" % exc)
            print("texture --check-image: 1 failure(s)")
            return 1
        print("  %s accepted, so this is the Japanese disc" % layout.DAT2D)

        _report(data, layout.DAT2D)

        found = tables(data)
        pal = palettes(data)
        img = images(data)
        counts = widths(pal)
        want_images, want_cluts, want_narrow, want_wide = \
            layout.TEXTURE_EXPECTED[layout.DAT2D]
        for name, got, expect in (
                ("image records", len(img), want_images),
                ("clut records", len(pal), want_cluts),
                ("palettes of %d entries" % NARROW, counts.get(NARROW, 0), want_narrow),
                ("palettes of %d entries" % WIDE, counts.get(WIDE, 0), want_wide)):
            if got != expect:
                failures += 1
                print("  FAILED %s: %d, recorded %d" % (name, got, expect))

        bank_start, list_start = layout.TEXTURE_BANK[layout.DAT2D]
        first, _ = span(pal)
        if first != bank_start:
            failures += 1
            print("  FAILED the palette bank starts at %d, recorded %d"
                  % (first, bank_start))
        if found[-1].start != list_start:
            failures += 1
            print("  FAILED the clut list starts at %d, recorded %d"
                  % (found[-1].start, list_start))
        holes = tiling(pal, found[-1].start)
        if holes:
            failures += 1
            print("  FAILED the bank does not tile: %r" % (holes,))
        else:
            print("  the %d palette(s) tile %d..%d with no hole and no overlap"
                  % (len(pal), first, found[-1].start))

        # -- the geometry answers for the pairing ---------------------------
        #
        # Every CLUT id the two model files name, resolved against this file.
        # The ones that do not resolve are a RESULT, not a failure: section 1.7
        # already records that pages the geometry names are not all here, and
        # naming which palettes are missing is what LOOKS-TASK-11 and 12 need.
        used = collections.Counter()
        # Per file as well as in total: the sum alone hid that six MODEL.BIN
        # sections sample the boots palette, because the boots line below was
        # measured inside EDT_MOD.BIN only and the totals were never split
        # (CORR-LOOKS-023).
        by_file = collections.defaultdict(collections.Counter)
        sections_of = {}
        for path in (layout.EDT_MOD, layout.MODEL):
            body = disc.read(path)
            sections_of[path] = modelfile.scan(body, path).sections
            for index, sec in enumerate(sections_of[path]):
                for prim in sec.primitives:
                    used[(prim.clut_vram, prim.tpage_depth)] += 1
                    by_file[(prim.clut_vram, prim.tpage_depth)][path] += 1
        here = absent = 0
        print("  the %d distinct CLUT id(s) the geometry names:" % len(used))
        for (vram, depth), n in sorted(used.items()):
            colours = WIDE if depth else NARROW
            split = "  (%s)" % ", ".join(
                "%s %d" % (os.path.basename(f), c)
                for f, c in sorted(by_file[(vram, depth)].items()))
            try:
                rec = covering(pal, vram[0], vram[1], colours)
            except NoPalette:
                absent += 1
                print("      vram %-11s %d bpp  x%-4d  NOT in %s%s"
                      % ("(%d,%d)" % vram, 4 if not depth else 8, n,
                         layout.DAT2D, split))
                continue
            here += 1
            print("      vram %-11s %d bpp  x%-4d  <- %d entries at %d%s"
                  % ("(%d,%d)" % vram, 4 if not depth else 8, n,
                     rec.colours, rec.offset, split))
        print("  %d of %d resolve in this file; %d come from elsewhere"
              % (here, len(used), absent))

        # -- the two CARP labels --------------------------------------------
        skins = [r for r in pal if r.colours == WIDE
                 and layout.CLUT_ROW_FIRST <= r.y < layout.CLUT_ROW_FIRST + 4]
        if len(skins) != 4 or sorted(r.y for r in skins) != \
                list(range(layout.CLUT_ROW_FIRST, layout.CLUT_ROW_FIRST + 4)):
            failures += 1
            print("  FAILED the four skin palettes are not four consecutive "
                  "VRAM rows: %r" % (skins,))
        else:
            print("  CARP's \"Pieles\": %s -- four %d-entry palettes on rows "
                  "%d..%d, and SKIN moves a CLUT id by one row"
                  % (", ".join(str(r.offset) for r in sorted(skins, key=lambda r: r.y)),
                     WIDE, layout.CLUT_ROW_FIRST, layout.CLUT_ROW_FIRST + 3))

        # The boots, named by the geometry and not by the label: the sections
        # LOOKS-TASK-09 called the feet have to sample one palette, alone.
        import pieces
        edt = disc.read(layout.EDT_MOD)
        sections = modelfile.scan(edt, layout.EDT_MOD).sections
        named = pieces.name_pieces(edt)[0]
        feet, others = set(), set()
        for index, piece in named.items():
            where = others if piece.name != pieces.FOOT else feet
            for prim in sections[index].primitives:
                where.add(prim.clut_vram)
        only = feet - others
        if len(only) != 1:
            failures += 1
            print("  FAILED the feet sample %r and the rest %r: no palette is "
                  "theirs alone" % (sorted(feet), sorted(others)))
        else:
            vram = only.pop()
            rec = covering(pal, vram[0], vram[1], NARROW)
            # The exclusivity holds among the pieces pieces.name_pieces()
            # knows, which are EDT_MOD.BIN's.  Saying only "no other piece
            # touches it" invited the reader to doubt the CLUT reading when
            # MODEL.BIN turned up sampling it too -- so the scope is stated,
            # and what falls outside it is counted rather than left out.
            elsewhere = {
                index: sum(1 for prim in sec.primitives
                           if prim.clut_vram == vram)
                for index, sec in enumerate(sections_of[layout.MODEL])
                if any(prim.clut_vram == vram for prim in sec.primitives)}
            print("  CARP's \"Botines\": %d -- the only palette the %s "
                  "section(s) sample among the NAMED pieces, at vram (%d,%d)"
                  % (rec.offset, pieces.FOOT, vram[0], vram[1]))
            print("      %d primitive(s) in %d %s section(s) share it: %s"
                  % (sum(elsewhere.values()), len(elsewhere),
                     os.path.basename(layout.MODEL),
                     ", ".join("%d x%d" % kv for kv in sorted(elsewhere.items()))
                     or "none"))
            if rec.offset != layout.BOOTS_PALETTE:
                failures += 1
                print("  FAILED the boots palette is at %d, recorded %d"
                      % (rec.offset, layout.BOOTS_PALETTE))

    if failures:
        print("texture --check-image: %d failure(s)" % failures)
        return 1
    print("texture --check-image: ok")
    return 0


def _survey(image_path: str) -> int:
    """What the sweep costs across the whole disc, as a command.

    Three questions, all of them once answered in prose and none of them
    reproducible afterwards (CORR-LOOKS-022):

    * how many records the sweep finds, and in how many files;
    * how many MORE a fixed tag word would miss -- which is the decision this
      cycle took, to fix the record model here and not in the sweep
      `tools/pes2/bin_archive.py` owns;
    * what each of the five conditions of `plausible()` actually suppresses.

    It is a disc read and nothing else: no emulator, no venv.
    """
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        paths = sorted(disc._image.files)
        bodies = {}
        for one in paths:
            try:
                bodies[one] = disc.read_unchecked(one)
            except Exception:  # noqa: BLE001 -- Form 2 and unreadable entries
                pass

    def count(skip=(), tag=None):
        total, files = 0, 0
        per = {}
        for one, body in bodies.items():
            found = [t for t in tables(body, skip)
                     if tag is None or t.tag == tag]
            n = sum(len(t.records) for t in found)
            if n:
                total += n
                files += 1
                per[one] = n
        return total, files, per

    print("  %d file(s) on the disc, %d readable" % (len(paths), len(bodies)))
    strict, files, per = count()
    print("  the sweep as it stands: %d record(s) in %d file(s)"
          % (strict, files))

    # The decision: a fixed tag word against a bank word read as a bank.
    fixed, _f, per_fixed = count(tag=layout.RECORD_TAG_BASE)
    extra = {one: per[one] - per_fixed.get(one, 0) for one in per
             if per[one] != per_fixed.get(one, 0)}
    outside = {one: n for one, n in extra.items() if one != layout.DAT2D}
    print("  a fixed tag word would find %d -- so reading the bank as a bank "
          "costs %d record(s) in %d file(s)"
          % (fixed, sum(extra.values()), len(extra)))
    print("      outside %s: %d record(s) in %d file(s) -- %s"
          % (layout.DAT2D, sum(outside.values()), len(outside),
             ", ".join("%s %d" % (os.path.basename(k), v)
                       for k, v in sorted(outside.items(),
                                          key=lambda kv: -kv[1]))))
    print("      stadium (GDC*) file(s) among them: %d"
          % sum(1 for one in outside if "GDC" in one.upper()))

    # And what each condition is worth, which is the claim a docstring cannot
    # carry on its own.
    print("  what each condition of plausible() suppresses:")
    for name, _test in CONDITIONS:
        total, _files, changed = count(skip=(name,))
        moved = sum(1 for one in changed
                    if changed[one] != per.get(one, 0))
        print("      without %-6s %+6d record(s), %d file(s) change"
              % (name, total - strict, moved))
    # Both readings of "only kind matters", because they are different
    # numbers and the prose that opened CORR-LOOKS-022 had them swapped.
    total, _files, _changed = count(
        skip=tuple(n for n, _ in CONDITIONS if n != "kind"))
    print("      with ONLY kind    %+6d record(s)" % (total - strict))
    total, _files, _changed = count(skip=tuple(n for n, _ in CONDITIONS))
    print("      with none of them  %+6d record(s)" % (total - strict))
    return 0


def _from_env():
    import iso_source
    return iso_source.image_from_env()


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    if argv[1:2] == ["--check-image"]:
        if len(argv) == 3:
            return _check_image(argv[2])
        try:
            return _check_image(_from_env())
        except RuntimeError as exc:
            print("texture --check-image: skipped -- %s" % exc)
            return 77
    if argv[1:2] == ["--survey"]:
        try:
            image = argv[2] if len(argv) == 3 else _from_env()
        except RuntimeError as exc:
            print("texture --survey: skipped -- %s" % exc)
            return 77
        return _survey(image)
    if argv[1:2] == ["--report"]:
        import iso_source
        try:
            image = argv[2] if len(argv) == 3 else _from_env()
        except RuntimeError as exc:
            print("texture --report: skipped -- %s" % exc)
            return 77
        with iso_source.open_disc(image) as disc:
            _report(disc.read(layout.DAT2D), layout.DAT2D)
        return 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

#!/usr/bin/env python3
"""Which image of `DAT2D.BIN` each primitive samples -- and so which is hair.

Provenance (plan section 3.4): measured here, from the geometry of
`MODEL.BIN` and `EDT_MOD.BIN` against the image records `texture.py` reads.

## The contradiction this module settles

Two documents of the scene disagree, and section 1.8 of the plan has kept both
at arm's length since the cycle opened:

* the **CARP** offset table calls offset **8** *"Pelos Cuerpos y botines"* --
  hair, bodies and boots -- and offset **3,568** *"Caras"*, faces;
* the **zeta** hair tutorial tells the reader to open **3,568** to paint hair.

They cannot both be right, and nothing in the cycle was allowed to assume
either.  The disc decides, and it decides without anyone looking at a picture:
**a primitive says which page it samples and where in it**, and a page is wider
than one image record.

## Why the page is the whole argument

A PSX texture page is 64 VRAM halfwords wide.  At 4 bits per texel that is 256
texels across, so `u` runs 0..255 over **two** of this file's 32-unit image
records side by side:

    page (512, 256)      u   0..127  ->  VRAM x 512..543  ->  the record at 8
                         u 128..255  ->  VRAM x 544..575  ->  the record at 3,568

Every one of the eighteen primitives of `MODEL.BIN` section 24 -- the head,
named by LOOKS-TASK-09 -- declares page `0x0018`, which is that page at 4 bits.
So the question "which image is the hair" is answered by a subtraction, not by
an opinion: **take the two primitives that `HAIR` moves and read their `u`.**

LOOKS-TASK-08 measured which two they are, in RAM, with the game running:
`HAIR` walks the `v` of the four corners of **primitives 1 and 14** by 0x20 a
step.  LOOKS-TASK-11 measured the same for `FACE` -- **primitives 8 and 13**,
0x10 a step, both save states.  Their `u` is 152..199, all of it past 128, so
past x 543.

**The hair is the record at 3,568**, and so is the face.  Neither field touches
the record at 8, which the same subtraction gives the other fourteen primitives,
`u` 16..62.

Two more witnesses say the same thing, and neither is this module:

* **the tutorial itself**, read rather than summarised: *"ubiquémonos en el
  gráfico en el offset 3568 ... Tendremos la imagen base de los cabellos"*, and
  every one of the 32 rows of its own table has 3,568 in the Gráfico column;
* **its palette table**, which reproduces what LOOKS-TASK-10 measured without
  having been asked to.  Its four columns are *blanca, amarilla, canela, negra*
  at 65,892 / 66,404 / 66,916 / 67,428 -- the four "Pieles" -- and its eight
  hair types step 32 bytes inside each, which is 16 VRAM halfwords, which is
  the CLUT id (16, 480) the head primitives carry.

So: **the zeta tutorial is right.  The CARP table's "Pelos" on offset 8 is
wrong**; its "Caras" on 3,568 is not wrong -- the face column is there and FACE
samples it -- it is incomplete, and what it leaves out is the hair.

## The file named after the answer is the other image

`Caras - zeta/cabellowe2002.bmp` -- "hair we2002", 128x128 at 4 bits -- is
**byte for byte the record at 8**, not the hair at all: 100.0% of its texel
indices equal that record in zeta's own patched `DAT2D.BIN`, and 85.7% in the
stock one.  Against 3,568 it scores 9.2%, which is *below* the 16.4% that
guessing the commonest index everywhere would score.

That null is the point.  85.7% reads as a match and 9.2% reads as a miss only
once you know what agreeing by accident is worth on a sheet where one index
covers a fifth of the pixels.  **A third-party file's name is a label like any
other**, and this one is wrong while the tutorial beside it is right.

## What else fell out of the same sweep

Of the 23 images in this container the player model samples **three**.  Every
other one belongs to a menu or a pitch, and this module does not guess at them:
a label it did not measure is printed as what it is, somebody's opinion.

`--elsewhere` answers the other half of section 1.7's leftover -- the pages and
palettes the geometry names and this file does not hold.  They are the kits, and
they are per team: 105 `TEX_*.BIN` containers hold the same three VRAM rects,
and `TEX_00.BIN` holds the 256-entry CLUTs at rows 486 and 488 as well, two of
each.  One palette the geometry names is in **no** container of this disc.

And the CARP table has a transcription error worth knowing about before
trusting a row of it: its line 20 reads its own hex `D59C` and writes 23,964,
which is not 54,684.  The hex is right and the decimal is wrong.

Usage:
    python tools/looks/atlas.py --check
    python tools/looks/atlas.py --check-image [<japanese.bin>]
    python tools/looks/atlas.py --labels [<japanese.bin>]
    python tools/looks/atlas.py --export <dir> [<japanese.bin>]
    python tools/looks/atlas.py --elsewhere [<japanese.bin>]
    python tools/looks/atlas.py --compare <other.bmp> [<japanese.bin>]
"""

from __future__ import annotations

import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "pes2"))

import layout  # noqa: E402
import texture  # noqa: E402

import lzss  # noqa: E402

PAGE_UNITS = 64
"""VRAM halfwords across one PSX texture page, whatever the depth."""

COORD = 256
"""The range of `u` and `v` inside a page: one byte each."""


class NoImage(Exception):
    """No image record holds the texel a primitive names."""


def texels_per_unit(depth: int) -> int:
    """Texels in one VRAM halfword: 4 at 4 bits, 2 at 8 bits, 1 direct."""
    return (4, 2, 1)[min(depth, 2)]


def texel(primitive, u: int, v: int) -> tuple:
    """VRAM (x, y) of one texel of one primitive.

    The depth is the primitive's own -- `tpage_depth` -- and not the image's,
    because the image record carries no depth field at all.  Reading it from
    the palette instead is the mistake CORR-LOOKS-018 measured on the other
    side of the same coin.
    """
    page_x, page_y = primitive.tpage_vram
    return (page_x + u // texels_per_unit(primitive.tpage_depth), page_y + v)


def corners(primitive) -> list:
    """The four texels of a textured quad, in VRAM coordinates."""
    return [texel(primitive, u, v) for u, v in primitive.texcoords]


def image_at(records, x: int, y: int):
    """The image record covering VRAM (x, y), or None.

    A record's rect is in halfword units for x and rows for y, which is why
    this cannot be done with the pixel width -- the same rect is 128 texels
    wide at 4 bits and 64 at 8.
    """
    for rec in records:
        if not rec.is_image:
            continue
        if rec.x <= x < rec.x + rec.w and rec.y <= y < rec.y + rec.h:
            return rec
    return None


def sampled_by(sections, records) -> dict:
    """{image offset: Counter of (file, section) -> primitives} over a scan.

    A primitive lands in the count once per distinct record its four corners
    touch, because a quad may straddle two records and pretending it cannot is
    exactly the assumption that made the CARP label survive this long.
    """
    out: dict = {}
    for label, index, prim in sections:
        seen = set()
        for x, y in corners(prim):
            rec = image_at(records, x, y)
            if rec is None:
                seen.add(None)
            else:
                seen.add(rec.offset)
        for offset in seen:
            out.setdefault(offset, collections.Counter())[(label, index)] += 1
    return out


def read_image(data: bytes, record, depth: int) -> tuple:
    """(indices, width, height) of one image record, at one page *depth* code.

    `depth` is the primitive's `tpage_depth` -- 0, 1 or 2 -- and not a number
    of bits.  Both spellings are two small integers and both look right in a
    call; passing 4 where 0 belongs made `texels_per_unit` answer 1, and the
    export came out 32 px wide instead of 128 with no error at all.

    The payload is an LZSS stream of `w * h * 2` bytes either way; only the
    reading of a byte changes.  `tools/pes2/lzss.py` is the codec, reused
    rather than rewritten -- it is disc reading, which this cycle shares.
    """
    if depth not in (0, 1, 2):
        raise NoImage("depth %r is not a page depth code (0, 1 or 2)" % (depth,))
    plain, _used = lzss.decompress(data, record.offset)
    if len(plain) != record.size:
        raise NoImage("the stream at %d gave %d B and the rect declares %d"
                      % (record.offset, len(plain), record.size))
    per = texels_per_unit(depth)
    width, height = record.w * per, record.h
    if per == 4:
        out = bytearray(len(plain) * 2)
        out[0::2] = bytes(b & 0x0F for b in plain)  # not-an-address: low nibble first, the PSX order
        out[1::2] = bytes(b >> 4 for b in plain)
        return bytes(out), width, height
    return bytes(plain), width, height


def write_png(path: str, width: int, height: int, indices: bytes,
              palette) -> int:
    """An 8-bit palette PNG, written by hand so this tree keeps no dependency.

    Same shape as the one `tools/pes2/bin_archive.py` carries; it lives here
    too because importing that module would drag its disc reader and its own
    record model -- the one LOOKS-TASK-10 measured wrong -- into this cycle.
    """
    import struct
    import zlib

    def chunk(tag, body):
        head = struct.pack(">I", len(body)) + tag
        return head + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)  # not-an-address: a CRC mask

    while len(palette) < COORD:
        palette = list(palette) + [(0, 0, 0, 0)]
    plte = b"".join(bytes(c[:3]) for c in palette)
    trns = bytes(c[3] for c in palette)
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        raw += indices[row * width:(row + 1) * width]
    body = (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
            + chunk(b"PLTE", plte)
            + chunk(b"tRNS", trns)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))
    with open(path, "wb") as fh:
        fh.write(body)
    return len(body)


def read_png(path: str) -> tuple:
    """(width, height, [rows of (r, g, b)]) out of an 8-bit PNG.

    Written by hand for the same reason `write_png` was: this tree keeps no
    image dependency.  What it is FOR is the emulator -- `read_vram_region`
    answers with a PNG file and not with halfwords, so the only way to compare
    what the GPU holds against what the disc holds is to decode it.

    Colour types 0, 2, 3 and 6 at eight bits, which is every shape DuckStation
    writes.  Anything else raises rather than guessing: a misread PNG comes out
    as plausible colours.
    """
    import struct
    import zlib

    with open(path, "rb") as handle:
        blob = handle.read()
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        raise NoImage("%s does not open with a PNG signature" % path)
    at = 8
    header, palette, data = None, [], bytearray()
    while at + 8 <= len(blob):
        length, tag = struct.unpack_from(">I4s", blob, at)
        body = blob[at + 8:at + 8 + length]
        at += 12 + length
        if tag == b"IHDR":
            header = struct.unpack(">IIBBBBB", body)
        elif tag == b"PLTE":
            palette = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif tag == b"IDAT":
            data += body
        elif tag == b"IEND":
            break
    if header is None:
        raise NoImage("%s has no IHDR" % path)
    width, height, depth, colour, _comp, _filt, interlace = header
    if depth != 8 or interlace or colour not in (0, 2, 3, 6):
        raise NoImage("%s is depth %d colour type %d interlace %d, and this "
                      "reader does 8-bit non-interlaced 0/2/3/6"
                      % (path, depth, colour, interlace))
    channels = {0: 1, 2: 3, 3: 1, 6: 4}[colour]
    raw = zlib.decompress(bytes(data))
    stride = width * channels
    out, previous = [], bytearray(stride)
    at = 0
    for _ in range(height):
        kind = raw[at]
        line = bytearray(raw[at + 1:at + 1 + stride])
        at += 1 + stride
        for i in range(stride):
            left = line[i - channels] if i >= channels else 0
            up = previous[i]
            upleft = previous[i - channels] if i >= channels else 0
            if kind == 1:
                line[i] = (line[i] + left) & 0xFF  # not-an-address: a byte mask
            elif kind == 2:
                line[i] = (line[i] + up) & 0xFF  # not-an-address: idem
            elif kind == 3:
                line[i] = (line[i] + (left + up) // 2) & 0xFF  # not-an-address: idem
            elif kind == 4:
                guess = left + up - upleft
                best = min((abs(guess - left), 0, left),
                           (abs(guess - up), 1, up),
                           (abs(guess - upleft), 2, upleft))
                line[i] = (line[i] + best[2]) & 0xFF  # not-an-address: idem
            elif kind:
                raise NoImage("%s uses filter %d on a row" % (path, kind))
        previous = line
        if colour == 3:
            out.append([palette[v] for v in line])
        elif colour == 0:
            out.append([(v, v, v) for v in line])
        else:
            out.append([tuple(line[i:i + 3])
                        for i in range(0, stride, channels)])
    return (width, height, out)


# ---- the labels ----------------------------------------------------------

MEASURED = "measured"
SCENE = "scene opinion"
UNLABELLED = "unlabelled"

CARP_LABELS = layout.DAT2D_SCENE_LABELS
"""`Offsets WE2002 - CARP/Dat/DAT2D.BIN.txt`, read 2026-09-15.

Opinion, not measurement, and keyed by offset -- so it lives in `layout.py`,
which owns every address in this cycle.  Two of its five palette labels were
confirmed by LOOKS-TASK-10; that says the table was written looking at the
file, and says nothing about any particular row.
"""

VERDICT = {
    layout.SKIN_IMAGE:
        "bodies, boots and bare skin -- 1,297 primitives across both files",
    layout.HAIR_IMAGE:
        "hair and face -- the primitives HAIR and FACE move, u 152..199",
    layout.FLAG_IMAGE:
        "not the player: only MODEL.BIN sections 0 and 1 sample it",
}
"""What the geometry says, and only what it says.

Section 1.8 asked which of two images is the hair.  The answer is 3,568, and
CARP puts the hair on 8 -- so its label for 8 is wrong.  Its label for 3,568,
"Caras", is not: FACE samples that record too.  The verdict is about one word
in one cell, not about a table.

10,248 carries no name here on purpose.  The geometry says what it is NOT --
none of the twelve pieces LOOKS-TASK-09 named touches it -- and saying "corner
flag and balls" because CARP does would be exactly the step this cycle refuses.
"""


def label_rows(data: bytes, sections) -> list:
    """One row per image record: what samples it, and whose label it carries."""
    records = texture.images(data)
    use = sampled_by(sections, records)
    rows = []
    for rec in records:
        hits = use.get(rec.offset, collections.Counter())
        if rec.offset in VERDICT:
            status, text = MEASURED, VERDICT[rec.offset]
        elif rec.offset in CARP_LABELS:
            status, text = SCENE, CARP_LABELS[rec.offset]
        else:
            status, text = UNLABELLED, ""
        rows.append((rec, sum(hits.values()), sorted(hits), status, text))
    return rows


# ---- the gate ------------------------------------------------------------

def _scan_sections(disc):
    """[(file, section index, primitive)] over both model files."""
    import modelfile

    out = []
    for path in (layout.EDT_MOD, layout.MODEL):
        body = disc.read(path)
        for index, sec in enumerate(modelfile.scan(body, path).sections):
            for prim in sec.primitives:
                out.append((path, index, prim))
    return out


class _Fake:
    """A primitive-shaped object, for a gate that runs with no disc."""

    def __init__(self, page, depth, coords):
        self.tpage_vram = page
        self.tpage_depth = depth
        self.texcoords = coords


def self_check(verbose: bool = True) -> int:
    import harness
    return harness.run("atlas.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    # The arithmetic that settles section 1.8, on the numbers that settle it.
    page = (512, 256)
    left = _Fake(page, 0, [(16, 1), (30, 1), (16, 11), (30, 11)])
    right = _Fake(page, 0, [(188, 1), (199, 1), (188, 14), (199, 14)])
    ok("a 4-bit page is four texels to the halfword",
       texels_per_unit(0) == 4 and texels_per_unit(1) == 2,
       "%d %d" % (texels_per_unit(0), texels_per_unit(1)))
    ok("u below half the page stays in the first record's columns",
       max(x for x, _ in corners(left)) < page[0] + 32,
       "%r" % (corners(left),))
    ok("and u past it lands in the next record's columns",
       min(x for x, _ in corners(right)) >= page[0] + 32,
       "%r" % (corners(right),))

    # The same two quads against two records side by side: the pairing has to
    # come out different, or the module cannot tell the two labels apart.
    plan = ((page[0], page[1], 32, 128, layout.SKIN_IMAGE),
            (page[0] + 32, page[1], 32, 128, layout.HAIR_IMAGE))
    records = [_record(*one) for one in plan]
    sections = [("/M", 24, left), ("/M", 24, right)]
    use = sampled_by(sections, records)
    ok("the two quads resolve to two different records",
       len(use) == 2 and None not in use, "%r" % (sorted(use),))
    ok("and the left one is the record with the lower x",
       image_at(records, *corners(left)[0]).x < image_at(records, *corners(right)[0]).x)

    # Red: a texel outside every record is reported as None, not snapped to
    # the nearest.  A silent snap is how an atlas comes out plausible.
    far = _Fake((896, 256), 0, [(0, 0)] * 4)
    ok("a texel no record holds resolves to None",
       image_at(records, *corners(far)[0]) is None)
    ok("and it is counted, not dropped",
       None in sampled_by([("/M", 0, far)], records))

    # An 8-bit page is half as wide in texels, so the SAME u lands elsewhere.
    # Reading the depth from the image instead of the primitive is the error
    # this asserts against.
    deep = _Fake(page, 1, [(188, 1)] * 4)
    ok("the same u at 8 bits lands in a different record",
       image_at(records, *corners(deep)[0]) is not image_at(records, *corners(right)[0]),
       "%r vs %r" % (corners(deep)[0], corners(right)[0]))

    # The PNG writer pads a short palette rather than writing a broken chunk:
    # a 16-entry CLUT with 8-bit indices is exactly what this file exports.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "one.png")
        size = write_png(out, 2, 2, bytes([0, 1, 2, 3]),
                         [(255, 0, 0, 255), (0, 255, 0, 255)])
        ok("a PNG with a short palette is still written whole",
           size > 0 and os.path.getsize(out) == size)
        with open(out, "rb") as fh:
            head = fh.read(8)
        ok("and it carries the PNG signature", head == b"\x89PNG\r\n\x1a\n")

        # Round trip, because the reader exists to decode a PNG this tree did
        # not write -- the emulator's VRAM answer -- and the only way to test
        # it without one in the room is against the writer next door.
        back = attempt("read the PNG back", lambda: read_png(out))
        ok("the reader returns the size the writer was given",
           back is not None and back[:2] == (2, 2), "%r" % (back and back[:2],))
        ok("and the pixels come back in the order they went in",
           back is not None and back[2] == [[(255, 0, 0), (0, 255, 0)],
                                            [(0, 0, 0), (0, 0, 0)]],
           "%r" % (back and back[2],))
        broken = os.path.join(tmp, "not.png")
        with open(broken, "wb") as fh:
            fh.write(b"not a png at all")
        c.refuses("a file that is not a PNG is refused, not decoded",
                  lambda: read_png(broken), "PNG signature", NoImage)

    # The labels are a table with provenance, and the two claims this module
    # makes are the two the geometry measured.
    ok("the two records section 1.8 argues about both carry a measured label",
       {layout.SKIN_IMAGE, layout.HAIR_IMAGE} <= set(VERDICT),
       "%r" % (sorted(VERDICT),))
    ok("and no measured label is the scene's label copied across",
       all(CARP_LABELS.get(k, "") not in VERDICT[k] for k in VERDICT))
    ok("the hair and the face are recorded on the SAME record",
       layout.HAIR_IMAGE != layout.SKIN_IMAGE
       and layout.HAIR_PRIMITIVES != layout.FACE_PRIMITIVES,
       "%r %r" % (layout.HAIR_PRIMITIVES, layout.FACE_PRIMITIVES))


def _record(x, y, w, h, offset):
    """An image record, built rather than read -- for the gate."""
    import struct
    fields = struct.unpack("<8H", struct.pack(
        "<8H", texture.KIND_IMAGE, x, y, w, h, 0, offset,
        layout.RECORD_TAG_BASE))
    return texture.Record(0, fields, 0)


def _check_image(image_path: str) -> int:
    import iso_source

    failures = 0
    with iso_source.open_disc(image_path) as disc:
        try:
            data = disc.read(layout.DAT2D)
        except layout.WrongDisc as exc:
            print("  FAILED %s" % exc)
            print("atlas --check-image: 1 failure(s)")
            return 1
        print("  %s accepted, so this is the Japanese disc" % layout.DAT2D)

        sections = _scan_sections(disc)
        records = texture.images(data)
        use = sampled_by(sections, records)

        print("  %d primitive(s) over both model files, %d image record(s)"
              % (len(sections), len(records)))
        inside = sum(sum(v.values()) for k, v in use.items() if k is not None)
        outside = sum(use.get(None, collections.Counter()).values())
        print("  %d primitive-record pairing(s) land in this file, %d land "
              "outside every record in it" % (inside, outside))

        # -- the verdict on section 1.8 ---------------------------------
        head = [(f, i, p) for f, i, p in sections
                if f == layout.MODEL and i == layout.HEAD_SECTION]
        if not head:
            failures += 1
            print("  FAILED %s section %d has no primitives"
                  % (layout.MODEL, layout.HEAD_SECTION))
        far = [p for f, i, p in head
               if min(u for u, _ in p.texcoords) >= COORD // 2]
        near = [p for f, i, p in head
                if max(u for u, _ in p.texcoords) < COORD // 2]
        print("  the head is %d primitive(s): %d sample the first half of the "
              "page and %d the second" % (len(head), len(near), len(far)))
        for name, group in (("first half ", near), ("second half", far)):
            if not group:
                continue
            got = {image_at(records, *corners(p)[0]).offset for p in group
                   if image_at(records, *corners(p)[0])}
            print("      %s: u %d..%d -> record(s) %s"
                  % (name,
                     min(u for p in group for u, _ in p.texcoords),
                     max(u for p in group for u, _ in p.texcoords),
                     sorted(got)))
            if len(got) != 1:
                failures += 1
                print("      FAILED that half is not one record")

        for field, prims in (("HAIR", layout.HAIR_PRIMITIVES),
                             ("FACE", layout.FACE_PRIMITIVES)):
            for prim in prims:
                p = head[prim][2]
                rec = image_at(records, *corners(p)[0])
                where = None if rec is None else rec.offset
                print("  primitive %2d -- %s moves it -- samples the record "
                      "at %s" % (prim, field, where))
                if where != layout.HAIR_IMAGE:
                    failures += 1
                    print("      FAILED %s does not sample %d"
                          % (field, layout.HAIR_IMAGE))

        # -- the 23 rows ------------------------------------------------
        print("  the %d image record(s), and whose label each carries:"
              % len(records))
        rows = label_rows(data, sections)
        for rec, n, who, status, text in rows:
            print("      @%6d vram (%4d,%4d)  %4d primitive(s)  %-13s %s"
                  % (rec.offset, rec.x, rec.y, n, status, text))
        measured = {r[0].offset for r in rows if r[3] == MEASURED}
        sampled = {r[0].offset for r in rows if r[1]}
        # One direction only, and deliberately.  A measured label that nothing
        # samples would be a claim with no evidence left; a sampled record with
        # no measured label is just work not done yet, and saying so is the
        # honest half of a labelling task.
        if measured - sampled:
            failures += 1
            print("  FAILED %r carry a measured label and nothing samples them"
                  % sorted(measured - sampled))
        print("  %d of %d record(s) carry a measured label; %d carry the "
              "scene's opinion and %d carry none"
              % (len(measured), len(rows),
                 sum(1 for r in rows if r[3] == SCENE),
                 sum(1 for r in rows if r[3] == UNLABELLED)))
        if sampled - measured:
            print("  %r are sampled and still unmeasured" % sorted(sampled - measured))

    if failures:
        print("atlas --check-image: %d failure(s)" % failures)
        return 1
    print("atlas --check-image: ok")
    return 0


def _export(image_path: str, out_dir: str) -> int:
    """Every image the model samples, as a PNG, with the palette it names."""
    import iso_source

    os.makedirs(out_dir, exist_ok=True)
    with iso_source.open_disc(image_path) as disc:
        data = disc.read(layout.DAT2D)
        sections = _scan_sections(disc)
        records = texture.images(data)
        pal = texture.palettes(data)
        use = sampled_by(sections, records)

        for rec in records:
            hits = use.get(rec.offset)
            if hits:
                prims = [p for f, i, p in sections
                         if any(image_at(records, *c) is rec
                                for c in corners(p))]
                depth = collections.Counter(p.tpage_depth for p in prims).most_common(1)[0][0]
                clut = collections.Counter(p.clut_vram for p in prims).most_common(1)[0][0]
                note = "%d primitive(s), page depth %d, clut %r" % (
                    sum(hits.values()), 4 if not depth else 8, clut)
            else:
                depth, clut = 0, (0, layout.CLUT_ROW_FIRST)
                note = "no primitive samples it; drawn with the first skin"
            colours = texture.WIDE if depth else texture.NARROW
            try:
                entries = texture.read_palette(
                    data, texture.covering(pal, clut[0], clut[1], colours),
                    colours)
            except texture.NoPalette:
                # Not a failure.  The palette a sampler names can live in
                # another container -- the kits do -- or, for VRAM (336, 510),
                # in none of them at all.  Drawing it grey says so on the face
                # of the PNG instead of stopping the export.
                entries = [(i, i, i, 255) for i in range(0, COORD, COORD // colours)]
                note += "; its palette %r is in no container, so this is grey" % (clut,)
            indices, width, height = read_image(data, rec, depth)
            path = os.path.join(out_dir, "dat2d-%06d.png" % rec.offset)
            size = write_png(path, width, height, indices, entries)
            print("  %s  %dx%d  %d B  -- %s"
                  % (os.path.basename(path), width, height, size, note))
    print("atlas --export: %d image(s) into %s" % (len(records), out_dir))
    return 0


def bmp_indices(path: str) -> tuple:
    """(indices, width, height) of a Windows BMP, bottom-up or top-down.

    Only what this cross-check needs: uncompressed, 4 or 8 bits, one plane.
    Rows are padded to four bytes and the default order is bottom-up, and
    getting either wrong turns a match into a miss with no message.
    """
    import struct

    raw = open(path, "rb").read()
    if raw[:2] != b"BM":
        raise NoImage("%s does not start with BM" % path)
    start = struct.unpack_from("<I", raw, 10)[0]
    width, signed, planes, bits = struct.unpack_from("<iiHH", raw, 18)
    if planes != 1 or bits not in (4, 8):
        raise NoImage("%s is %d plane(s) at %d bit(s)" % (path, planes, bits))
    height = abs(signed)
    stride = ((width * bits + 31) // 32) * 4
    rows = []
    for y in range(height):
        line = raw[start + y * stride: start + (y + 1) * stride]
        if bits == 8:
            rows.append(list(line[:width]))
            continue
        out = []
        for byte in line:
            out.append(byte >> 4)
            out.append(byte & 0x0F)  # not-an-address: the low nibble
        rows.append(out[:width])
    if signed > 0:
        rows.reverse()
    return bytes(v for row in rows for v in row), width, height


def _compare(image_path: str, other: str) -> int:
    """One outside image against every record this container holds.

    **With the null beside every score**, which is the whole reason this is a
    command.  On a sheet where one index covers a fifth of the texels, guessing
    that index everywhere already scores about a sixth; a bare "85.7% equal"
    cannot be read without knowing that, and a bare "9.2%" cannot either --
    9.2% is *worse* than the guess, which says the two are unrelated rather
    than merely different.
    """
    import collections

    import iso_source

    outside, width, height = bmp_indices(other)
    print("  %s: %dx%d, %d texel(s)"
          % (os.path.basename(other), width, height, len(outside)))
    with iso_source.open_disc(image_path) as disc:
        data = disc.read(layout.DAT2D)
    best = None
    for rec in texture.images(data):
        try:
            indices, w, h = read_image(data, rec, 0)
        except Exception as exc:  # noqa: BLE001
            print("      @%6d  unreadable: %s" % (rec.offset, exc))
            continue
        if (w, h) != (width, height):
            continue
        agree = sum(1 for a, b in zip(indices, outside) if a == b)
        top, count = collections.Counter(indices).most_common(1)[0]
        null = sum(1 for v in outside if v == top)
        share = 100.0 * agree / len(indices)
        print("      @%6d  %5.1f%% equal   (index %2d covers %4.1f%% of the "
              "record, so a blind guess of it scores %4.1f%%)"
              % (rec.offset, share, top, 100.0 * count / len(indices),
                 100.0 * null / len(outside)))
        if best is None or share > best[1]:
            best = (rec.offset, share)
    if best:
        print("  closest: the record at %d, %.1f%% equal" % best)
    return 0


def _elsewhere(image_path: str) -> int:
    """The pages and palettes the geometry names and `DAT2D.BIN` lacks.

    Section 1.7 recorded that two of the three texture pages the geometry
    names have no entry in that file, and LOOKS-TASK-10 added four of its nine
    CLUT ids to the same list.  Both halves have one answer, and it is not a
    guess: sweep every container of the disc and ask which of them holds the
    rect.  A number that decides something has to come from a command
    (CORR-LOOKS-022), so this is that command.
    """
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        sections = _scan_sections(disc)
        here = texture.images(disc.read(layout.DAT2D))
        bodies = {}
        for one in sorted(disc._image.files):
            try:
                bodies[one] = disc.read_unchecked(one)
            except Exception:  # noqa: BLE001 -- Form 2 and unreadable entries
                pass

    wanted_rects = collections.Counter()
    wanted_cluts = collections.Counter()
    for _f, _i, prim in sections:
        colours = texture.WIDE if prim.tpage_depth else texture.NARROW
        wanted_cluts[prim.clut_vram + (colours,)] += 1
        for x, y in corners(prim):
            if image_at(here, x, y) is None:
                wanted_rects[(x // 32 * 32, y // 128 * 128)] += 1

    records = {}
    for one, body in bodies.items():
        if one == layout.DAT2D:
            continue
        records[one] = [r for t in texture.tables(body) for r in t.records]

    print("  %d container(s) swept beside %s" % (len(records), layout.DAT2D))
    print("  VRAM rect(s) the geometry samples and %s does not hold:"
          % layout.DAT2D)
    for (x, y), n in sorted(wanted_rects.items()):
        owners = [one for one, rr in records.items()
                  if image_at(rr, x, y) is not None]
        print("      (%4d,%4d)  %5d corner(s)  in %3d container(s)%s"
              % (x, y, n, len(owners),
                 ": " + ", ".join(sorted(os.path.basename(o) for o in owners)[:3])
                 + (" ..." if len(owners) > 3 else "") if owners else
                 "  -- IN NONE OF THEM"))
    print("  CLUT id(s) the geometry names and %s does not hold:"
          % layout.DAT2D)
    held = texture.palettes(bodies[layout.DAT2D])
    for (x, y, colours), n in sorted(wanted_cluts.items()):
        try:
            texture.covering(held, x, y, colours)
            continue
        except texture.NoPalette:
            pass
        owners = {}
        for one, rr in records.items():
            hits = [r for r in rr if r.is_clut and r.covers(x, y, colours)]
            if hits:
                owners[one] = len(hits)
        print("      (%4d,%4d) x%-3d  %5d primitive(s)  in %3d container(s)%s"
              % (x, y, colours, n, len(owners),
                 ": " + ", ".join("%s x%d" % (os.path.basename(k), v)
                                  for k, v in sorted(owners.items())[:2])
                 + (" ..." if len(owners) > 2 else "") if owners else
                 "  -- IN NONE OF THEM"))
        # How many palettes of this width the container holds ALTOGETHER, and
        # not only how many answer this id.  The "x2" above was read as "the
        # file has two, home and away" and written into a task log; the file
        # has five (CORR-LOOKS-025).  Two counts that differ by a factor of
        # two and a half print one line apart now.
        if owners:
            totals = collections.Counter(
                sum(1 for r in records[one] if r.is_clut
                    and r.colours == colours)
                for one in owners)
            print("          %d-entry palette(s) per container, in total: %s"
                  % (colours, ", ".join("%d in %d file(s)" % (k, v)
                                        for k, v in sorted(totals.items()))))
    return 0


def _labels(image_path: str) -> int:
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = disc.read(layout.DAT2D)
        rows = label_rows(data, _scan_sections(disc))
    print("| offset | VRAM | primitives | label | provenance |")
    print("|---:|---|---:|---|---|")
    for rec, n, _who, status, text in rows:
        print("| %d | (%d, %d) | %d | %s | %s |"
              % (rec.offset, rec.x, rec.y, n, text or "--", status))
    return 0


def _from_env():
    import iso_source
    return iso_source.image_from_env()


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    if argv[1:2] == ["--check-image"]:
        try:
            image = argv[2] if len(argv) == 3 else _from_env()
        except RuntimeError as exc:
            print("atlas --check-image: skipped -- %s" % exc)
            return 77
        return _check_image(image)
    if argv[1:2] == ["--labels"]:
        try:
            image = argv[2] if len(argv) == 3 else _from_env()
        except RuntimeError as exc:
            print("atlas --labels: skipped -- %s" % exc)
            return 77
        return _labels(image)
    if argv[1:2] == ["--compare"] and len(argv) >= 3:
        try:
            image = argv[3] if len(argv) == 4 else _from_env()
        except RuntimeError as exc:
            print("atlas --compare: skipped -- %s" % exc)
            return 77
        return _compare(image, argv[2])
    if argv[1:2] == ["--elsewhere"]:
        try:
            image = argv[2] if len(argv) == 3 else _from_env()
        except RuntimeError as exc:
            print("atlas --elsewhere: skipped -- %s" % exc)
            return 77
        return _elsewhere(image)
    if argv[1:2] == ["--export"] and len(argv) >= 3:
        try:
            image = argv[3] if len(argv) == 4 else _from_env()
        except RuntimeError as exc:
            print("atlas --export: skipped -- %s" % exc)
            return 77
        return _export(image, argv[2])
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

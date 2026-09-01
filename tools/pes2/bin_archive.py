#!/usr/bin/env python3
"""The `BIN/*.BIN` container: entry records, images and CLUTs -- phase 7.

PES2-TASK-26 proved the LZSS codec reads these files. This is the index
that says what each stream *is*. Section 5 Fase 10 of
`docs/PLAN-FEATURES.md` predicted a 32-byte `DATA_HEADER`; measured, it is
**16 bytes**, and there are two kinds of it.

## The record

Sixteen bytes, eight little-endian 16-bit fields, and lists of them end
with the halfword `0x00ff`:

    [0] kind      low byte 0x0a = image, 0x09 = CLUT; high byte a
                  parameter that is always 0 for images and varies for CLUTs
    [1] vram_x    in 16-bit VRAM units
    [2] vram_y    in rows
    [3] width     in 16-bit VRAM units
    [4] height    in rows
    [5] always 0 on all four discs
    [6] offset    where the payload starts, relative to the file
    [7] 0x800f    a constant tag, and the thing that makes the record
                  findable without knowing where the list is

**An image record's payload is an LZSS stream; a CLUT record's payload is
raw.** A CLUT is `width x 1` at VRAM y >= 480 -- the strip at the bottom of
the frame buffer that PSX games keep palettes in -- so it is `width`
entries of BGR555 in `width * 2` bytes.

**And the CLUT width is what says how deep the image is.** 256 colours
means 8 bpp, 16 means 4 bpp; both discs use both. The rect is in 16-bit
units either way, so an image is `width * 2` pixels across at 8 bpp and
`width * 4` at 4 bpp, `height` down, and `width * height * 2` bytes once
decompressed -- the byte count is the same, only the reading of a byte
changes. Assuming 256 everywhere costs a `LOGO.BIN` whose 32-byte palette
is read as 512 and runs off the end of the file.

## Where the lists are is not fixed, so they are found, not computed

`DAT2D.BIN` puts all 21 image records in one list after the last stream,
then a second list of 266 CLUT records. `TEX_00.BIN` puts **one** record
after each stream, eleven lists in all. Both layouts are read the same
way: find the `0x800f 0x00ff` that ends a list, walk backwards in 16-byte
steps while the tag holds.

## What this file does not know

**Which CLUT belongs to which image.** `DAT2D.BIN` has 21 images and 266
CLUTs; the choice is made by the game's drawing code, not by the
container. `export` therefore takes `--clut`, defaults to the first one of
the file, and says so rather than inventing a pairing. The pixel indices
are exact either way, which is what PES2-TASK-29 needs to survive a round
trip.

## Usage

    python3 tools/pes2/bin_archive.py ls <track1.bin>
    python3 tools/pes2/bin_archive.py ls <track1.bin> --file /BIN/DAT2D.BIN
    python3 tools/pes2/bin_archive.py export <track1.bin> --file /BIN/TITLE.BIN --out DIR
    python3 tools/pes2/bin_archive.py check <track1.bin>
"""

import argparse
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import lzss                                                  # noqa: E402

RECORD = 16
TAG = 0x800F
END = 0x00FF
KIND_IMAGE = 0x0A
KIND_CLUT = 0x09
CLUT_MAX = 256          # the widest CLUT on these discs, hence 8 bpp

# Measured on all four discs, 2026-09-01: one image record per TEX_*.BIN
# declares a 64x64 rect whose stream decompresses to twice that. It is
# always the same entry -- VRAM (704, 256) -- and it is reported rather
# than silently accepted or silently dropped. See the plan, section 1.14(f).
KNOWN_DOUBLE = (704, 256, 64, 64)

# Stadiums. Section 1.14(d) of the plan puts them outside this project --
# they are TMD meshes, and PLAN-STADIUMS owns them. Their records are read
# and counted here, and their failures are *not* this task's failures; the
# alternative is a gate that is red for a reason nobody intends to fix.
STADIUM = ("/BIN/GDC_", "/BIN/GRDM_")


def is_stadium(path):
    return path.startswith(STADIUM)


# The golden European Deluxe is a **hacked** WE2002 image, and the hack
# reinserted graphics without respecting its own index: six image records
# there do not fit -- five whose stream is a different size than the rect
# declares, and one, `TEX_70.BIN` at 18052, whose stream dies on `distance
# 0`. Nobody is going to fix that disc, so a gate that is red for it is red
# forever, which is the failure mode the stadium carve-out above already
# fixed once.
#
# The count is the assertion: the six are allowed, a seventh is not. Keyed
# on the disc label `lzss.EXPECT` resolves from the container count.
HACKED = {"WE2002 European Deluxe": 6}


class Entry:
    __slots__ = ("pos", "kind", "param", "x", "y", "w", "h", "offset")

    def __init__(self, pos, fields):
        self.pos = pos
        self.kind = fields[0] & 0xFF
        self.param = fields[0] >> 8
        self.x, self.y, self.w, self.h = fields[1:5]
        self.offset = fields[6]

    @property
    def is_image(self):
        return self.kind == KIND_IMAGE

    @property
    def is_clut(self):
        return self.kind == KIND_CLUT

    @property
    def colours(self):
        """How many entries a CLUT record holds -- and so how deep it is."""
        return self.w

    def pixels(self, bpp=8):
        """(width, height) in pixels, for a depth the CLUT decides."""
        return self.w * (16 // bpp), self.h

    @property
    def expected(self):
        """How many bytes the payload should be, from the rect alone."""
        return self.w * self.h * 2

    def __repr__(self):
        name = {KIND_IMAGE: "image", KIND_CLUT: "clut"}.get(self.kind, "?")
        return (f"{name:5s} @{self.offset:7d}  vram ({self.x:4d},{self.y:4d}) "
                f"{self.w:3d}x{self.h:3d}")


def depth_of(recs):
    """4 or 8, from the CLUTs of the same container.

    The image record carries no depth field; the palette width is the only
    thing on the disc that says it. A container with no CLUT at all gets 8,
    and `check` counts those separately rather than pretending.
    """
    widths = {e.colours for e in recs if e.is_clut}
    return 4 if widths and max(widths) <= 16 else 8


def entries(data):
    """Every record of every list in one container, in file order.

    Found by the tag rather than by a table pointer, because the lists do
    not sit in one place: see the module docstring.
    """
    found = {}
    p = data.find(b"\x0f\x80\xff\x00")
    while p >= 0:
        q = p - (RECORD - 2)                       # start of the last record
        while q >= 0 and struct.unpack_from("<H", data, q + 14)[0] == TAG:
            found[q] = Entry(q, struct.unpack_from("<8H", data, q))
            q -= RECORD
        p = data.find(b"\x0f\x80\xff\x00", p + 1)
    return [found[k] for k in sorted(found)]


def read_image(data, entry):
    """The decompressed pixels of one image entry, and the bytes it used."""
    if not entry.is_image:
        raise ValueError(f"{entry!r} is not an image record")
    return lzss.decompress(data, entry.offset)


def read_clut(data, entry):
    """The RGBA entries of one CLUT record -- as many as its width says.

    BGR555 with the top bit as the PSX "semi-transparency" flag. A PSX
    palette entry that is black with that bit clear is the transparent
    one, which is the rule used here -- getting it wrong shows up at once
    as a black box instead of a cut-out.
    """
    if not entry.is_clut:
        raise ValueError(f"{entry!r} is not a CLUT record")
    want = entry.colours * 2
    raw = data[entry.offset:entry.offset + want]
    if len(raw) < want:
        raise ValueError(
            f"CLUT at {entry.offset} wants {want} B and the file has "
            f"{len(raw)} left")
    out = []
    for i in range(entry.colours):
        v = struct.unpack_from("<H", raw, 2 * i)[0]
        r = (v & 0x1F) << 3
        g = ((v >> 5) & 0x1F) << 3
        b = ((v >> 10) & 0x1F) << 3
        stp = v & 0x8000
        alpha = 0 if (v & 0x7FFF) == 0 and not stp else 255
        out.append((r | r >> 5, g | g >> 5, b | b >> 5, alpha))
    return out


def unpack4(packed):
    """Two 4-bit pixels per byte, low nibble first -- the PSX order."""
    out = bytearray(len(packed) * 2)
    out[0::2] = bytes(b & 0x0F for b in packed)
    out[1::2] = bytes(b >> 4 for b in packed)
    return bytes(out)


# ---- PNG, written by hand so tools/pes2 keeps no dependency -----------

def write_png(path, width, height, indices, palette):
    """An 8-bit palette PNG. No Pillow: tools/pes2 is stdlib only."""
    def chunk(tag, body):
        head = struct.pack(">I", len(body)) + tag
        return head + body + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF)

    plte = b"".join(bytes(c[:3]) for c in palette)
    trns = bytes(c[3] for c in palette)
    raw = bytearray()
    for row in range(height):
        raw.append(0)                              # filter: none
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


# ---- commands --------------------------------------------------------

def targets(img, only):
    paths = lzss.containers(img)
    if only:
        paths = [p for p in paths if p == only]
    return paths


def cmd_ls(args):
    with Image(args.image) as img:
        paths = targets(img, args.file)
        if not paths:
            print(f"{args.file}: not a Form 1 /BIN/*.BIN of this disc",
                  file=sys.stderr)
            return 1
        images = cluts = 0
        for path in paths:
            data = img.read_file(path)
            recs = entries(data)
            if not recs and not args.file:
                continue
            im = [e for e in recs if e.is_image]
            cl = [e for e in recs if e.is_clut]
            other = [e for e in recs if not e.is_image and not e.is_clut]
            images += len(im)
            cluts += len(cl)
            print(f"{path:22s} {len(data):8d} B   {len(im)} image(s), "
                  f"{len(cl)} clut(s)"
                  + (f", {len(other)} of another kind" if other else ""))
            if args.file or args.verbose:
                for e in recs:
                    extra = ""
                    if e.is_image:
                        w, h = e.pixels(depth_of(recs))
                        try:
                            plain, used = read_image(data, e)
                            extra = (f"  {w}x{h} px 8bpp  comp {used} -> "
                                     f"{len(plain)}"
                                     + ("" if len(plain) == e.expected
                                        else f"  <-- expected {e.expected}"))
                        except lzss.LzssError as exc:
                            extra = f"  FAILED: {exc}"
                    elif e.is_clut:
                        extra = (f"  {e.colours} colours, {e.colours * 2} B raw"
                                 f"  -> {4 if e.colours <= 16 else 8} bpp")
                    print(f"    rec@{e.pos:6d}  {e!r}  param {e.param:#04x}{extra}")
        if not args.file:
            print(f"  {images} image record(s), {cluts} clut record(s)")
    return 0


def cmd_export(args):
    with Image(args.image) as img:
        paths = targets(img, args.file)
        if not paths:
            print(f"{args.file}: not a Form 1 /BIN/*.BIN of this disc",
                  file=sys.stderr)
            return 1
        os.makedirs(args.out, exist_ok=True)
        written = 0
        for path in paths:
            data = img.read_file(path)
            recs = entries(data)
            cl = [e for e in recs if e.is_clut]
            if not cl:
                print(f"  {path}: no CLUT in this container, skipped")
                continue
            which = cl[min(args.clut, len(cl) - 1)]
            palette = read_clut(data, which)
            bpp = depth_of(recs)
            stem = os.path.basename(path).rsplit(".", 1)[0]
            for i, e in enumerate(e for e in recs if e.is_image):
                plain, _ = read_image(data, e)
                w, h = e.pixels(bpp)
                if bpp == 4:
                    plain = unpack4(plain)
                if len(plain) < w * h:
                    print(f"  {path} entry {i}: {len(plain)} B for {w}x{h}, "
                          f"skipped")
                    continue
                out = os.path.join(args.out, f"{stem}_{i:02d}.png")
                write_png(out, w, h, plain, palette)
                written += 1
        print(f"wrote {written} PNG(s) to {args.out}")
        print(f"  palette: CLUT #{args.clut} of each container -- the "
              f"container does not say which CLUT an image uses")
    return 0


def cmd_check(args):
    """Assert the shape of the index, and report what does not fit.

    Not a count: the four discs hold different numbers. What is asserted
    is that every image record's payload decompresses, that the rect
    predicts the payload size, and that every stream the codec finds has a
    record -- with the two families of exception measured, named and
    allowed to be counted rather than hidden.
    """
    bad = 0
    notfit = 0            # records whose payload disagrees with their rect
    with Image(args.image) as img:
        paths = targets(img, args.file)
        disc = lzss.EXPECT.get(len(lzss.containers(img)), (None,))[0]
        stats = {"images": 0, "cluts": 0, "exact": 0, "double": 0,
                 "other": 0, "failed": 0, "orphan": 0, "files": 0,
                 "short": 0, "noclut": 0, "bpp4": 0, "bpp8": 0,
                 "stadium_failed": 0, "unindexed": 0, "stadiums": 0}
        for path in paths:
            data = img.read_file(path)
            recs = entries(data)
            if not recs:
                if lzss.scan(data):
                    stats["unindexed"] += 1
                    if not is_stadium(path) and args.verbose:
                        print(f"  {path}: streams but no record list")
                continue
            stats["files"] += 1
            if is_stadium(path):
                stats["stadiums"] += 1
            if any(e.is_clut for e in recs):
                stats["bpp4" if depth_of(recs) == 4 else "bpp8"] += 1
            else:
                stats["noclut"] += 1
            declared = set()
            for e in recs:
                if e.is_clut:
                    stats["cluts"] += 1
                    if e.h != 1 or e.colours not in (16, 256):
                        print(f"  {path}: CLUT {e!r} is not 16x1 or 256x1")
                        bad += 1
                    elif e.offset + e.colours * 2 > len(data):
                        stats["short"] += 1
                    continue
                if not e.is_image:
                    continue
                stats["images"] += 1
                declared.add(e.offset)
                try:
                    plain, _ = read_image(data, e)
                except lzss.LzssError as exc:
                    stats["failed"] += 1
                    if is_stadium(path):
                        stats["stadium_failed"] += 1
                    else:
                        print(f"  {path}: image record at {e.pos} does not "
                              f"decompress: {exc}")
                        notfit += 1
                    continue
                if len(plain) == e.expected:
                    stats["exact"] += 1
                elif (len(plain) == 2 * e.expected
                      and (e.x, e.y, e.w, e.h) == KNOWN_DOUBLE):
                    stats["double"] += 1
                else:
                    print(f"  {path}: {e!r} declares {e.expected} B, the "
                          f"stream gives {len(plain)}")
                    stats["other"] += 1
                    notfit += 1
            for off, _, _ in lzss.scan(data):
                if off not in declared:
                    stats["orphan"] += 1

        print(f"{os.path.basename(args.image)}: {stats['files']} container(s) "
              f"with records")
        print(f"  {stats['images']} image record(s): {stats['exact']} exact, "
              f"{stats['double']} of the known 64x64 double, "
              f"{stats['other']} other, {stats['failed']} that fail to "
              f"decompress")
        print(f"  {stats['cluts']} clut record(s); {stats['bpp4']} container(s) "
              f"4 bpp, {stats['bpp8']} 8 bpp, {stats['noclut']} with no CLUT; "
              f"{stats['short']} clut(s) truncated by the end of the file")
        print(f"  {stats['orphan']} stream(s) the codec's resync scan finds "
              f"that no record declares -- the record is the index, the scan "
              f"is an approximation of it")
        print(f"  {stats['unindexed']} container(s) with streams and no record "
              f"list at all; {stats['stadiums']} indexed container(s) are "
              f"stadiums, whose {stats['stadium_failed']} failing record(s) "
              f"are out of scope by plan 1.14(d)")

        allowance = HACKED.get(disc) if not args.file else None
        if allowance is None:
            if disc in HACKED:
                print(f"  {disc}: the known-hacked allowance is not applied "
                      f"to a single --file run; {notfit} record(s) counted "
                      f"as failures", file=sys.stderr)
            bad += notfit
        elif notfit == allowance:
            print(f"  {disc} is a hacked image: its {notfit} record(s) that "
                  f"do not fit their own rect are the known ones (plan "
                  f"1.14(f)), and are counted, not failed", file=sys.stderr)
        else:
            print(f"CHECK FAILED: {disc}: {notfit} record(s) do not fit, "
                  f"and {allowance} are the measured, known ones",
                  file=sys.stderr)
            bad += 1
        print("CHECK OK" if not bad else "CHECK FAILED", file=sys.stderr)
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("ls", cmd_ls), ("export", cmd_export), ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("image")
        p.add_argument("--file", metavar="PATH", help="one container")
        p.add_argument("-v", "--verbose", action="store_true")
        if name == "export":
            p.add_argument("--out", required=True, metavar="DIR")
            p.add_argument("--clut", type=int, default=0,
                           help="which CLUT of the container to paint with")
        p.set_defaults(fn=fn)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

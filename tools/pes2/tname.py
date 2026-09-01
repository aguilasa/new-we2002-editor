#!/usr/bin/env python3
"""`T_NAME_*.BIN`: the rasterised presentation names -- phase 7.

Section 6.12 of the plan says the copy set of `T_NAME` is by language, and
`tools/pes2/lang_map.py` sweeps it. This is the other half: what is
*inside* the file, and what it would take to put a new name there.

## What is inside

28 image entries, 32x128 VRAM units each, **4 bpp** -- so 128x128 pixels,
and the container carries no CLUT of its own. Entries 0 to 23 hold **team**
names, four to a tile on a 32-pixel pitch; entry 0 is `Ireland`,
`Scotland`, `Wales`, `England`. The last entries hold **stadium** names, on
a tighter pitch. The glyphs are 12 to 13 pixels tall.

## The font is not on this disc, and that is a measured result

Section 6.12 used to say the italic face came from two blocks of
`DAT2D_I.BIN`. It does not: those blocks band at 18, 15 and 9 pixels and
none of them is 12. `fontscan` is the search that settled it -- every image
entry of every non-stadium container, looking for the regular band grid an
alphabet sheet would make at this size. What it finds is **rendered text**,
never an alphabet: the `LC_*`, `EDT_2D` and `CG<lang>` hits are UI strings,
and the `T_NAME` hits are the names themselves.

So the presentation names were rasterised **off the disc**, by whatever the
developers used -- which is what CARP's `T_NAME-Maker` does from the other
side, with a PC font. Composing a new name from the disc's own pixels is
not possible letter by letter either: the face is italic and the letters
touch, so `Ireland` is a single unbroken run of 92 ink columns and there is
no column gap to cut on.

**What is possible, and what `swap` does**, is to move a name that is
already rasterised into another slot. It is the operation an editor can
offer honestly today, and it exercises the whole write path -- the band
geometry, the container, and the copy set of section 6.12 -- without
inventing a glyph.

## Usage

    python3 tools/pes2/tname.py bands    <track1.bin>
    python3 tools/pes2/tname.py fontscan <track1.bin>
    python3 tools/pes2/tname.py swap     <track1.bin> --tmpdir DIR [--png DIR]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import bin_archive as BA                                     # noqa: E402
import lang_map as LM                                        # noqa: E402
import lzss                                                  # noqa: E402

BPP = 4
GLYPH_MIN, GLYPH_MAX = 11, 14      # the band heights an alphabet would make
GREY = [(i * 17,) * 3 + (255,) for i in range(16)]


def tname_paths(img):
    """Every `/BIN/T_NAME*.BIN` of this disc, in path order."""
    return [p for p in sorted(img.files)
            if p.startswith("/BIN/T_NAME") and img.is_form1(p)]


def tile_pixels(data, entry):
    """One entry as 4-bpp pixel indices, and its width in pixels."""
    plain, _ = BA.read_image(data, entry)
    return BA.unpack4(plain), entry.w * 4


def ink_bands(px, width, height):
    """(y0, y1) of every run of rows that has ink -- the text lines."""
    out = []
    run = None
    for y in range(height):
        row = px[y * width:(y + 1) * width]
        if any(row):
            if run is None:
                run = y
        elif run is not None:
            out.append((run, y - 1))
            run = None
    if run is not None:
        out.append((run, height - 1))
    return out


def cmd_bands(args):
    with Image(args.image) as img:
        paths = tname_paths(img)
        if not paths:
            print("no /BIN/T_NAME*.BIN on this disc", file=sys.stderr)
            return 1
        data = img.read_file(paths[0])
        recs = [e for e in BA.entries(data) if e.is_image]
        print(f"{paths[0]}: {len(recs)} entries, {BPP} bpp, "
              f"{recs[0].w * 4}x{recs[0].h} px each")
        heights = []
        for i, e in enumerate(recs):
            px, w = tile_pixels(data, e)
            bands = ink_bands(px, w, e.h)
            heights += [b - a + 1 for a, b in bands]
            if args.verbose or i < 3:
                print(f"  entry {i:2d}  {len(bands)} band(s): "
                      + ", ".join(f"{a}-{b}" for a, b in bands))
        lo, hi = min(heights), max(heights)
        print(f"  {len(heights)} text band(s) in all, "
              f"heights {lo}..{hi}, most common "
              f"{max(set(heights), key=heights.count)}")
    return 0


def cmd_fontscan(args):
    """Look for an alphabet sheet at the T_NAME glyph size. There is none.

    The test is the shape an alphabet makes: several equal, short bands in
    one tile. It is deliberately generous -- it reports every candidate and
    lets a human look -- because a negative result is only worth something
    if the search was wide enough to have found the thing.
    """
    with Image(args.image) as img:
        hits = []
        for path in lzss.containers(img):
            if BA.is_stadium(path):
                continue
            data = img.read_file(path)
            for i, e in enumerate(e for e in BA.entries(data) if e.is_image):
                try:
                    px, w = tile_pixels(data, e)
                except lzss.LzssError:
                    continue
                if len(px) < w * e.h:
                    continue
                bands = [b - a + 1 for a, b in ink_bands(px, w, e.h)]
                n = sum(1 for h in bands if GLYPH_MIN <= h <= GLYPH_MAX)
                if n >= 3:
                    hits.append((path, i, n))
        by_file = {}
        for path, i, n in hits:
            by_file.setdefault(path, []).append(i)
        print(f"{os.path.basename(args.image)}: {len(hits)} tile(s) with "
              f"{GLYPH_MIN}..{GLYPH_MAX} px bands, in {len(by_file)} file(s)")
        for path in sorted(by_file):
            print(f"  {path:22s} entries {by_file[path]}")
        print("  every one of these is rendered text, not an alphabet -- "
              "see the module docstring")
    return 0


def cmd_swap(args):
    """Move one rasterised name over another, in every copy, then undo it.

    The measurement is the same pair `lang_map` asserts: every copy carries
    the new pixels, and no file on the disc still carries the old ones.
    """
    import shutil
    import tempfile

    bad = 0
    with Image(args.image) as img:
        paths = tname_paths(img)
        if not paths:
            print("no /BIN/T_NAME*.BIN on this disc", file=sys.stderr)
            return 1
        original = img.read_file(paths[0])
        recs = [e for e in BA.entries(original) if e.is_image]
        entry = recs[args.entry]
        px, w = tile_pixels(original, entry)
        bands = ink_bands(px, w, entry.h)
        if len(bands) <= max(args.src, args.dst):
            print(f"entry {args.entry} has {len(bands)} bands", file=sys.stderr)
            return 1
        print(f"{paths[0]} entry {args.entry}: bands "
              + ", ".join(f"{a}-{b}" for a, b in bands))
        print(f"  moving band {args.src} onto band {args.dst}")

    # The pitch is 32 rows; copying a whole slot rather than the ink rows
    # keeps the vertical alignment the game expects.
    pitch = 32
    edited = bytearray(px)
    for y in range(pitch):
        s = (args.src * pitch + y) * w
        d = (args.dst * pitch + y) * w
        edited[d:d + w] = px[s:s + w]

    packed = bytearray(len(edited) // 2)
    for i in range(0, len(edited), 2):
        packed[i // 2] = (edited[i] & 0x0F) | ((edited[i + 1] & 0x0F) << 4)
    if len(packed) != entry.expected:
        print(f"repacked {len(packed)} B against {entry.expected} declared",
              file=sys.stderr)
        return 1

    work = tempfile.mkdtemp(prefix="pes2-tname-", dir=args.tmpdir)
    copy = os.path.join(work, "track1.bin")
    try:
        print(f"copying {os.path.getsize(args.image) // (1 << 20)} MiB ...")
        shutil.copyfile(args.image, copy)

        # The entry is one LZSS stream inside the container, and a rewritten
        # stream is not the same length -- so the whole container cannot be
        # reassembled in place without the budget policy PES2-TASK-29 owns.
        # What is written here is the *decompressed* tile back through the
        # compressor, and the container is only accepted if it still fits.
        blob = lzss.compress(bytes(packed))
        room = _stream_room(original, entry, recs)
        print(f"  recompressed {len(packed)} B -> {len(blob)} B, "
              f"room {room} B")
        if len(blob) > room:
            print(f"  REFUSED: {len(blob) - room} B over budget -- this is "
                  f"the fit-or-fail of PES2-TASK-29, and it is working")
            return 0
        new = bytearray(original)
        new[entry.offset:entry.offset + len(blob)] = blob

        with Image(copy, writable=True) as img:
            plan, old = LM.write_all(img, paths[0], bytes(new))
            print(f"  wrote {len(plan)} copy/copies")
        with Image(copy) as img:
            for p in plan:
                got, _ = BA.read_image(img.read_file(p), entry)
                ok = BA.unpack4(got)[:len(edited)] == bytes(edited)
                print(f"    {p:22s} {'new pixels' if ok else 'MISMATCH'}")
                bad += 0 if ok else 1
            left = LM.survivors(img, old, plan)
            if left:
                print(f"    FAILED: {len(left)} file(s) still hold the old "
                      f"content: {left}")
                bad += 1
            else:
                print("    swept the disc: no file still holds the old bytes")
            if args.png:
                os.makedirs(args.png, exist_ok=True)
                out = os.path.join(args.png, "tname_swapped.png")
                BA.write_png(out, w, entry.h, bytes(edited), GREY)
                print(f"    wrote {out}")

        before = LM._sha(args.image)
        with Image(copy, writable=True) as img:
            LM.write_all(img, paths[0], original)
        if LM._sha(copy) == before:
            print("  round-trip OK: the image is byte for byte the original")
        else:
            print("  ROUND-TRIP FAILED")
            bad += 1
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("\nSWAP FAILED" if bad else "\nSWAP OK")
    return 1 if bad else 0


def _stream_room(data, entry, recs):
    """How many bytes this entry's stream may grow into.

    The next thing in the file is the next record or the next stream,
    whichever comes first, so the budget is the gap to it. Nothing here
    moves anything: that policy belongs to PES2-TASK-29.
    """
    after = [e.offset for e in recs if e.offset > entry.offset]
    after += [e.pos for e in BA.entries(data) if e.pos > entry.offset]
    return (min(after) if after else len(data)) - entry.offset


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("bands", cmd_bands), ("fontscan", cmd_fontscan),
                     ("swap", cmd_swap)):
        p = sub.add_parser(name)
        p.add_argument("image")
        p.add_argument("-v", "--verbose", action="store_true")
        if name == "swap":
            p.add_argument("--tmpdir", required=True)
            p.add_argument("--png", metavar="DIR")
            p.add_argument("--entry", type=int, default=0)
            p.add_argument("--src", type=int, default=3)
            p.add_argument("--dst", type=int, default=2)
        p.set_defaults(fn=fn)
    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())

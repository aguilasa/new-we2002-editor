#!/usr/bin/env python3
"""Write an edited asset back into the image -- phase 7, fit-or-fail.

PES2-TASK-27 read the container index; this writes to it. Two decisions
come ready from section 5(a) and 5(c) of `docs/PLAN-FEATURES.md`, and this
tool exists to enforce them rather than restate them:

**Fit-or-fail.** Nothing moves and nothing grows. A rewritten entry that
does not fit is **refused, with the byte count**, and rebuilding the ISO is
out of the project -- the game reaches these overlays by hardcoded LBA, so
a corrected directory record would not help.

**An untouched entry never recompresses.** Only the entry the user edited
is regenerated; every other byte of the container is carried through. That
is what gives the invariant `save` asserts: open and save with no edit
returns a byte-identical image.

## The two budgets, because there are two

The task text names one -- the file's extent, rounded up to its last
sector. That one is enforced for free: `iso.py write_file` refuses any
length change at all, so the container is spliced in place.

The one that actually bites is the **entry** budget: the distance from a
stream's offset to the next record or the next stream, whichever comes
first. PES2-TASK-28 measured it biting -- a recompressed `T_NAME` tile at
1904 bytes against 1868 of room, refused 36 over. Both are checked here,
and the entry one is checked first because it is the one that fails.

## Every rewrite is verified before it reaches the disk

`decompress(compress(x)) == x` is asserted on the actual bytes about to be
written, not on a sample and not behind a flag. Section 5(c) is why the
assertion is that way round and never the other: the compressor here is
not Konami's and never reproduces her output.

## Usage

    python3 tools/pes2/asset_write.py save     <copy.bin>
    python3 tools/pes2/asset_write.py export   <copy.bin> --file P --entry N --png F
    python3 tools/pes2/asset_write.py import   <copy.bin> --file P --entry N --png F
    python3 tools/pes2/asset_write.py palette  <copy.bin> --file P --clut N --index I --rgb R,G,B
    python3 tools/pes2/asset_write.py negative <copy.bin> --file P --entry N
    python3 tools/pes2/asset_write.py budget   <copy.bin> [--file P] -v
"""

import argparse
import os
import struct
import sys
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image, RAW_SECTOR, HEADER, FORM1_DATA        # noqa: E402
import bin_archive as BA                                     # noqa: E402
import lzss                                                  # noqa: E402


class Refused(Exception):
    """A write this tool will not do, with the reason a human needs."""


def refuse_roms(path):
    """`roms/` holds the originals and every command here writes in place.

    The same guard `poke.py` carries, for the same reason: PES2 has no
    save-as, and a mistake there costs a fresh download.
    """
    if "roms" in os.path.abspath(path).split(os.sep):
        raise Refused(
            f"{path} is under a roms/ directory -- those are the originals "
            f"and this writes in place. Copy the release first.")


# ---- PNG in, the reverse of bin_archive.write_png --------------------

def read_png(path):
    """(width, height, indices, palette) from an 8-bit palette PNG.

    Written out because `tools/pes2` has no dependencies, and the five
    filter types are implemented because the PNG will come from whatever
    the user edits in, not from `bin_archive.write_png`.
    """
    with open(path, "rb") as fh:
        blob = fh.read()
    if blob[:8] != b"\x89PNG\r\n\x1a\n":
        raise Refused(f"{path} is not a PNG")
    p = 8
    width = height = depth = colour = None
    palette = []
    trns = b""
    idat = bytearray()
    while p + 8 <= len(blob):
        length = struct.unpack_from(">I", blob, p)[0]
        tag = blob[p + 4:p + 8]
        body = blob[p + 8:p + 8 + length]
        p += 12 + length
        if tag == b"IHDR":
            width, height, depth, colour = struct.unpack_from(">IIBB", body, 0)
        elif tag == b"PLTE":
            palette = [tuple(body[i:i + 3]) for i in range(0, len(body), 3)]
        elif tag == b"tRNS":
            trns = body
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
    if colour != 3 or depth != 8:
        raise Refused(
            f"{path} is colour type {colour} depth {depth}; this writer takes "
            f"8-bit palette PNG only, because that is what the disc stores")

    raw = zlib.decompress(bytes(idat))
    out = bytearray(width * height)
    prev = bytearray(width)
    q = 0
    for y in range(height):
        ftype = raw[q]
        q += 1
        line = bytearray(raw[q:q + width])
        q += width
        if ftype == 1:
            for x in range(1, width):
                line[x] = (line[x] + line[x - 1]) & 0xFF
        elif ftype == 2:
            for x in range(width):
                line[x] = (line[x] + prev[x]) & 0xFF
        elif ftype == 3:
            for x in range(width):
                left = line[x - 1] if x else 0
                line[x] = (line[x] + ((left + prev[x]) >> 1)) & 0xFF
        elif ftype == 4:
            for x in range(width):
                a = line[x - 1] if x else 0
                b = prev[x]
                c = prev[x - 1] if x else 0
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                line[x] = (line[x] + pred) & 0xFF
        elif ftype != 0:
            raise Refused(f"{path} row {y} uses filter {ftype}")
        out[y * width:(y + 1) * width] = line
        prev = line
    alpha = list(trns) + [255] * (len(palette) - len(trns))
    return width, height, bytes(out), [c + (a,) for c, a in zip(palette, alpha)]


# ---- the container ---------------------------------------------------

def png_depth(palette):
    """4 or 8, from how many colours the PNG carries.

    The depth has to be recovered from the palette because a VRAM rect is
    the *same* pixel width at both depths -- 32 units is 128 px at 4 bpp
    and 64 units is 128 px at 8 bpp -- so dimensions alone never say which
    slot a picture belongs to. CORR-PES2-019 is the write that proved it:
    a 4 bpp export of LOGO.BIN went into an 8 bpp slot of TITLE.BIN with
    every existing check green.
    """
    return 4 if len(palette) <= 16 else 8


def find(data, index, kind):
    recs = [e for e in BA.entries(data)
            if (e.is_image if kind == "image" else e.is_clut)]
    if not 0 <= index < len(recs):
        raise Refused(f"this container has {len(recs)} {kind} record(s)")
    return recs[index], recs


def entry_room(data, entry):
    """Bytes an entry's payload may occupy before it hits the next thing."""
    after = [e.offset for e in BA.entries(data) if e.offset > entry.offset]
    after += [e.pos for e in BA.entries(data) if e.pos > entry.offset]
    return (min(after) if after else len(data)) - entry.offset


def depth_for(data, entry, override=None):
    """4 or 8 for an image entry, from the container's palettes.

    `DAT2D.BIN` holds 261 palettes of 16 colours and 5 of 256, so the file
    has no single answer -- CORR-PES2-016 is why `BA.depth_of` returns
    `None` there instead of letting five outvote 261. The caller has to
    say, and `--bpp` is how; guessing would write a picture of the wrong
    width and the byte count would not notice.
    """
    if override:
        return override
    recs = BA.entries(data)
    bpp = BA.depth_of(recs)
    if bpp is None:
        raise Refused(
            "this container's CLUTs do not agree on a depth, so the width of "
            "an image here is not decidable -- pass --bpp 4 or --bpp 8")
    return bpp


def pack(indices, bpp):
    if bpp == 8:
        return bytes(indices)
    out = bytearray(len(indices) // 2)
    for i in range(0, len(indices), 2):
        out[i // 2] = (indices[i] & 0x0F) | ((indices[i + 1] & 0x0F) << 4)
    return bytes(out)


def splice(data, entry, blob):
    """Put a payload back where it was, with the budget already checked."""
    out = bytearray(data)
    out[entry.offset:entry.offset + len(blob)] = blob
    if len(out) != len(data):
        raise Refused("splicing changed the container length")
    return bytes(out)


def rewrite_image(data, entry, indices, bpp):
    """Compressed bytes for one image entry, verified, budget checked."""
    packed = pack(indices, bpp)
    if len(packed) != entry.expected:
        raise Refused(
            f"{len(packed)} B of pixels against the {entry.expected} B the "
            f"record declares -- the picture is the wrong size for this slot")
    blob = lzss.compress(packed)

    # Before the disk, never after, and with no way to turn it off.
    back, _ = lzss.decompress(blob, 0)
    if back != packed:
        raise Refused("the recompressed stream does not decompress to what "
                      "was compressed -- refusing to write it")

    room = entry_room(data, entry)
    if len(blob) > room:
        raise Refused(
            f"the entry needs {len(blob)} B and has {room} B before the next "
            f"record -- {len(blob) - room} B over budget. Nothing was written; "
            f"growing it would mean moving what follows, which is out of scope")
    return blob, room


# ---- commands --------------------------------------------------------

def cmd_save(args):
    """Open and save with no edit. The whole image must not move a byte."""
    import hashlib

    def sha(p):
        h = hashlib.sha256()
        with open(p, "rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 22), b""):
                h.update(chunk)
        return h.hexdigest()

    refuse_roms(args.image)
    before = sha(args.image)
    with Image(args.image, writable=True) as img:
        paths = [p for p in sorted(img.files)
                 if p.startswith("/BIN/") and img.is_form1(p)]
        touched = 0
        for path in paths:
            data = img.read_file(path)
            recs = BA.entries(data)
            if not recs:
                continue
            img.write_file(path, data)      # carried through, not regenerated
            touched += 1
    after = sha(args.image)
    print(f"saved {touched} indexed container(s) with no edit")
    if after != before:
        print(f"FAILED: the image changed -- {before} != {after}")
        return 1
    print("SAVE OK: the image is byte for byte what it was")
    return 0


def cmd_export(args):
    with Image(args.image) as img:
        data = img.read_file(args.file)
        entry, _ = find(data, args.entry, "image")
        bpp = depth_for(data, entry, getattr(args, 'bpp', None))
        plain, _ = BA.read_image(data, entry)
        px = BA.unpack4(plain) if bpp == 4 else plain
        w, h = entry.pixels(bpp)
        cl = [e for e in BA.entries(data) if e.is_clut]
        palette = (BA.read_clut(data, cl[args.clut]) if cl
                   else [(i, i, i, 255) for i in range(1 << bpp)])
        # The PNG has to carry the depth, and the only place it fits is the
        # palette length -- so pad or refuse rather than write a 16-colour
        # table for an 8 bpp slot and lose the distinction on the way out.
        if len(palette) > (1 << bpp):
            raise Refused(
                f"the CLUT has {len(palette)} colours and this slot is "
                f"{bpp} bpp -- pick another --clut")
        palette = palette + [(0, 0, 0, 0)] * ((1 << bpp) - len(palette))
        BA.write_png(args.png, w, h, px, palette)
        print(f"{args.file} entry {args.entry}: {w}x{h} px {bpp} bpp -> "
              f"{args.png}")
    return 0


def cmd_import(args):
    refuse_roms(args.image)
    with Image(args.image) as img:
        data = img.read_file(args.file)
        entry, _ = find(data, args.entry, "image")
        bpp = depth_for(data, entry, getattr(args, 'bpp', None))
        want_w, want_h = entry.pixels(bpp)

        width, height, indices, palette = read_png(args.png)
        if (width, height) != (want_w, want_h):
            raise Refused(
                f"{args.png} is {width}x{height} and this slot is "
                f"{want_w}x{want_h} -- refusing to resize it for you")
        got = png_depth(palette)
        if got != bpp:
            raise Refused(
                f"{args.png} is {got} bpp ({len(palette)} colours) and this "
                f"slot is {bpp} bpp. The two have the same pixel size, so the "
                f"dimensions agreeing means nothing -- pick the right slot, or "
                f"re-export the picture at {bpp} bpp")
        if bpp == 4 and any(i > 15 for i in indices):
            raise Refused(
                f"{args.png} uses index {max(indices)} and this slot is 4 bpp, "
                f"so only 0..15 exist here")

        cl = [e for e in BA.entries(data) if e.is_clut]
        if cl and not args.repaint:
            here = BA.read_clut(data, cl[args.clut])
            here = here + [(0, 0, 0, 0)] * ((1 << bpp) - len(here))
            if [c[:3] for c in palette] != [c[:3] for c in here]:
                first = next(i for i, (a, b) in enumerate(zip(palette, here))
                             if a[:3] != b[:3])
                raise Refused(
                    f"{args.png} does not carry the palette of CLUT "
                    f"{args.clut}: they first differ at colour {first}, "
                    f"{palette[first][:3]} against {here[first][:3]}. Pass "
                    f"--repaint to write the pixels anyway, knowing the game "
                    f"paints them with the CLUT that is on the disc")

        blob, room = rewrite_image(data, entry, indices, bpp)
        print(f"{args.file} entry {args.entry}: {width}x{height} {bpp} bpp, "
              f"{len(blob)} B of {room} B")
    with Image(args.image, writable=True) as img:
        img.write_file(args.file, splice(data, entry, blob))
    print("written, and verified before it went")
    return 0


def cmd_palette(args):
    refuse_roms(args.image)
    r, g, b = (int(x) for x in args.rgb.split(","))
    with Image(args.image) as img:
        data = img.read_file(args.file)
        clut, _ = find(data, args.clut, "clut")
        if not 0 <= args.index < clut.colours:
            raise Refused(f"this CLUT has {clut.colours} colours")
        at = clut.offset + 2 * args.index
        was = struct.unpack_from("<H", data, at)[0]
        value = ((b >> 3) << 10) | ((g >> 3) << 5) | (r >> 3) | (was & 0x8000)
        out = bytearray(data)
        struct.pack_into("<H", out, at, value)
        entry_lba = img.entry(args.file).lba
        lba = entry_lba + at // FORM1_DATA
        absolute = lba * RAW_SECTOR + HEADER + at % FORM1_DATA
        crosses = at // FORM1_DATA != (at + 1) // FORM1_DATA
        print(f"{args.file} clut {args.clut} colour {args.index}: "
              f"{was:#06x} -> {value:#06x}")
        print(f"  file offset {at}, sector {lba}, absolute {absolute}"
              + ("  (the halfword crosses a sector boundary)" if crosses else ""))
        print(f"  one 16-bit entry, so {1 if not crosses else 2} sector(s) of "
              f"this file change and nothing else does")
    with Image(args.image, writable=True) as img:
        img.write_file(args.file, bytes(out))
    print("written -- a CLUT payload is raw, so there is no stream to fit")
    return 0


def cmd_negative(args):
    """One pixel changed must produce a small, countable difference.

    The control the plan asks for, and the reason it exists is the same as
    `iso.py negative`: a guard that cannot be made to go red proves
    nothing when it is green.
    """
    with Image(args.image) as img:
        data = img.read_file(args.file)
        entry, _ = find(data, args.entry, "image")
        bpp = depth_for(data, entry, getattr(args, 'bpp', None))
        plain, _ = BA.read_image(data, entry)
        px = bytearray(BA.unpack4(plain) if bpp == 4 else plain)
        px[0] = (px[0] + 1) % (1 << bpp)
        blob, room = rewrite_image(data, entry, px, bpp)
        new = splice(data, entry, blob)
        differ = sum(1 for a, b in zip(data, new) if a != b)
        first = next((i for i, (a, b) in enumerate(zip(data, new)) if a != b),
                     None)
        print(f"{args.file} entry {args.entry}: one pixel changed")
        print(f"  {differ} byte(s) differ in the container, first at {first}")
        print(f"  the entry starts at {entry.offset}, room {room} B")
        if differ == 0:
            print("NEGATIVE CONTROL FAILED: nothing changed")
            return 1
        if first < entry.offset:
            print(f"NEGATIVE CONTROL FAILED: the first difference is before "
                  f"the entry")
            return 1
        print("NEGATIVE CONTROL OK: the change is inside the entry it was "
              "made in")
    return 0


def cmd_budget(args):
    """Per entry: what Konami spent, what we spend, and the room there is.

    It exists because the number it prints went into the plan once from a
    listing that was filtered for screen -- `if i < 4 or ok` -- which hid
    the one entry of LOGO.BIN that overruns, and the doc said 10 of 13
    where the truth is 9. A count belongs to a command that prints the
    total, not to whoever reads the rows.
    """
    fits = total = 0
    slack_lo = slack_hi = None
    with Image(args.image) as img:
        paths = [args.file] if args.file else [
            p for p in sorted(img.files)
            if p.startswith("/BIN/") and img.is_form1(p)]
        for path in paths:
            data = img.read_file(path)
            recs = [e for e in BA.entries(data) if e.is_image]
            if not recs:
                continue
            try:
                bpp = depth_for(data, recs[0], getattr(args, "bpp", None))
            except Refused as exc:
                if args.verbose:
                    print(f"{path:22s} skipped: {exc}")
                continue
            for i, e in enumerate(recs):
                try:
                    plain, used = BA.read_image(data, e)
                except lzss.LzssError:
                    continue
                again = lzss.compress(plain)
                room = entry_room(data, e)
                slack = room - used
                slack_lo = slack if slack_lo is None else min(slack_lo, slack)
                slack_hi = slack if slack_hi is None else max(slack_hi, slack)
                ok = len(again) <= room
                total += 1
                fits += ok
                if args.verbose or args.file:
                    print(f"{path:22s} {i:3d}  konami {used:6d}  ours "
                          f"{len(again):6d}  room {room:6d}  slack {slack:3d}  "
                          + ("fits" if ok else f"OVER by {len(again) - room}"))
    print(f"{fits} of {total} entries re-encode inside their own budget; "
          f"{total - fits} do not")
    print(f"slack (room minus the original stream): {slack_lo}..{slack_hi} bytes")
    return 0


def cmd_check(args):
    """Everything this tool promises, on a copy, then put back.

    Registered in `check_image.py`, so `ctest -R pes2_image` covers the
    write path the way it covers the read one. It needs a writable copy,
    which is why it lives behind WE2002_PES2_TMPDIR like the negative
    control and the poke do.
    """
    import shutil
    import tempfile

    bad = 0
    work = tempfile.mkdtemp(prefix="pes2-write-", dir=args.tmpdir)
    copy = os.path.join(work, "track1.bin")
    try:
        print(f"copying {os.path.getsize(args.image) // (1 << 20)} MiB ...")
        shutil.copyfile(args.image, copy)
        before = _sha(copy)

        print("\n-- open and save, no edit --")
        bad += cmd_save(_Args(image=copy))
        if _sha(copy) != before:
            print("  FAILED: save moved a byte")
            bad += 1

        print("\n-- the budget refusing --")
        try:
            with Image(copy) as img:
                data = img.read_file("/BIN/TITLE.BIN")
                entry, _ = find(data, 0, "image")
                plain, _ = BA.read_image(data, entry)
                rewrite_image(data, entry, plain, 8)
            print("  FAILED: TITLE entry 0 was accepted; it does not fit")
            bad += 1
        except Refused as exc:
            print(f"  refused: {exc}")

        print("\n-- import refusing the wrong depth --")
        shot = os.path.join(work, "four-bpp.png")
        cmd_export(_Args(image=copy, file="/BIN/LOGO.BIN", entry=2,
                         png=shot, clut=0, bpp=None))
        try:
            cmd_import(_Args(image=copy, file="/BIN/TITLE.BIN", entry=2,
                             png=shot, clut=0, bpp=None, repaint=False))
            print("  FAILED: a 4 bpp picture was accepted by an 8 bpp slot")
            bad += 1
        except Refused as exc:
            print(f"  refused: {exc}")

        print("\n-- the negative control --")
        bad += cmd_negative(_Args(image=copy, file="/BIN/LOGO.BIN",
                                  entry=2, bpp=None))

        print("\n-- a palette colour, and the sectors it touches --")
        bad += cmd_palette(_Args(image=copy, file="/BIN/TITLE.BIN", clut=0,
                                 index=5, rgb="255,0,255"))
        touched = _diff_sectors(args.image, copy)
        print(f"  measured: {len(touched)} sector(s) differ from the "
              f"original -- {sorted(touched)}")
        if len(touched) != 1:
            print("  FAILED: a 16-bit palette entry must touch one sector")
            bad += 1
        if not _tails_intact(args.image, copy, touched):
            print("  FAILED: an EDC/ECC tail changed")
            bad += 1
        else:
            print("  EDC/ECC tails preserved, as section 6.7 requires")
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("\nWRITE CHECK FAILED" if bad else "\nWRITE CHECK OK")
    return 1 if bad else 0


class _Args:
    def __init__(self, **kw):
        self.__dict__.update(kw)


def _sha(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 22), b""):
            h.update(chunk)
    return h.hexdigest()


def _diff_sectors(p1, p2):
    out = set()
    off = 0
    with open(p1, "rb") as f1, open(p2, "rb") as f2:
        while True:
            a = f1.read(1 << 22)
            b = f2.read(1 << 22)
            if not a:
                return out
            if a != b:
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        out.add((off + i) // RAW_SECTOR)
            off += len(a)


def _tails_intact(p1, p2, sectors):
    """The 280 bytes after the data area must survive every write."""
    with open(p1, "rb") as f1, open(p2, "rb") as f2:
        for lba in sectors:
            at = lba * RAW_SECTOR + HEADER + FORM1_DATA
            f1.seek(at)
            f2.seek(at)
            if f1.read(RAW_SECTOR - HEADER - FORM1_DATA) != \
               f2.read(RAW_SECTOR - HEADER - FORM1_DATA):
                return False
    return True


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("save", cmd_save), ("export", cmd_export),
                     ("import", cmd_import), ("palette", cmd_palette),
                     ("negative", cmd_negative), ("budget", cmd_budget),
                     ("check", cmd_check)):
        p = sub.add_parser(name)
        p.add_argument("image")
        if name == "budget":
            p.add_argument("--file", metavar="PATH")
            p.add_argument("--bpp", type=int, choices=(4, 8))
            p.add_argument("-v", "--verbose", action="store_true")
        if name == "check":
            p.add_argument("--tmpdir", required=True)
        if name not in ("save", "check", "budget"):
            p.add_argument("--file", required=True, metavar="PATH")
        if name in ("export", "import", "negative"):
            p.add_argument("--entry", type=int, default=0)
            p.add_argument("--bpp", type=int, choices=(4, 8),
                           help="depth, when the container's CLUTs disagree")
        if name in ("export", "import"):
            p.add_argument("--png", required=True)
        if name in ("export", "import"):
            p.add_argument("--clut", type=int, default=0)
        if name == "import":
            p.add_argument("--repaint", action="store_true",
                           help="accept a picture whose palette is not the "
                                "slot's CLUT")
        if name == "palette":
            p.add_argument("--clut", type=int, default=0)
            p.add_argument("--index", type=int, required=True)
            p.add_argument("--rgb", required=True, metavar="R,G,B")
        p.set_defaults(fn=fn)
    args = ap.parse_args(argv)
    try:
        return args.fn(args)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

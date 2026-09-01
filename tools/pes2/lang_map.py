#!/usr/bin/env python3
"""The copy set of an asset, swept by content -- phase 7.

Section 6.1 of the plan says a written copy is worse than no copy, and
PES2-TASK-02 paid for it: the five team-name lists the plan listed were
eight on the disc, and only a sweep found the other three. Section 6.12
says the same trap exists one layer up, for assets, and that the set is
**by language**.

Measured here, and the name is a bad guide:

  `T_NAME_I.BIN` and `T_NAME_S.BIN` on `(EsIt)`, and `T_NAME_E.BIN`,
  `T_NAME_F.BIN` and `T_NAME_G.BIN` on `(EnFrDe)`, are **one file** --
  the same 62.196 bytes, the same digest, across both releases. Five
  copies, two discs, one content.

  `DAT2D_I` and `DAT2D_S` are **not** copies of each other: 39.820 against
  37.728 bytes. Neither are the three `DATSEL*I`, nor the fourteen `LC_*`.
  They are language *variants*, which is the opposite problem.

  And the suffix does not even survive the release: `(EsIt)` ships
  `DATSEL_I`, `DATSEL2I`, `DATSEL3I` and no unsuffixed form, while
  `(EnFrDe)` ships `DATSEL`, `DATSEL2`, `DATSEL3` and no suffixed one.

So the set is grouped by **content digest**, never by name, and the
grouping runs over the whole disc rather than `/BIN/` -- `FNOTE_G`,
`FNOTE_I` and `FNOTE_S`, which section 6.12 lists among the language
files, live in the root.

## Usage

    python3 tools/pes2/lang_map.py <track1.bin>
    python3 tools/pes2/lang_map.py <track1.bin> --asset /BIN/T_NAME_I.BIN
    python3 tools/pes2/lang_map.py <track1.bin> --check
    python3 tools/pes2/lang_map.py <track1.bin> --self-check --tmpdir DIR
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402

# Measured on 2026-09-01. A group is every path whose content is byte for
# byte the same; the key is the sorted tuple of basenames so the assertion
# does not depend on which member is asked about.
EXPECT = {
    "(Es,It)": [("LC_MS.BIN", "LC_OL.BIN"),
                ("TEX_99.BIN", "TEX_A0.BIN", "TEX_A1.BIN", "TEX_A2.BIN"),
                ("T_NAME_I.BIN", "T_NAME_S.BIN")],
    "(En,Fr,De)": [("LC_MS.BIN", "LC_OL.BIN"),
                   ("TEX_99.BIN", "TEX_A0.BIN", "TEX_A1.BIN", "TEX_A2.BIN"),
                   ("T_NAME_E.BIN", "T_NAME_F.BIN", "T_NAME_G.BIN")],
}

# The presentation font, measured in PES2-TASK-28. Section 6.12 asked which
# container holds it; it is the language copy of DAT2D, in two adjacent
# 128x128 tiles at 4 bpp -- the same italic face the T_NAME bitmaps are
# drawn in. Offsets are of `(EsIt)`; on another release they move, so the
# record is found through bin_archive rather than read from here.
FONT_FILE = "DAT2D_"
FONT_VRAM = ((640, 0), (672, 0))


class Refused(Exception):
    """A write this tool will not do, with the reason a human needs."""


def digest(data):
    return hashlib.sha256(data).hexdigest()


def groups(img, prefix=""):
    """Every set of two or more files with identical content, in path order."""
    by = {}
    for path in sorted(img.files):
        if not path.startswith(prefix) or not img.is_form1(path):
            continue
        by.setdefault(digest(img.read_file(path)), []).append(path)
    return [v for _, v in sorted(by.items(), key=lambda kv: kv[1][0])
            if len(v) > 1]


def copies_of(img, path):
    """Every path holding the same bytes as `path`, including `path`."""
    want = digest(img.read_file(path))
    return [p for p in sorted(img.files)
            if img.is_form1(p) and digest(img.read_file(p)) == want]


def write_all(img, path, new, allow_partial=False):
    """Write `new` into every copy of `path`, or refuse and say why.

    The refusal is the point, and it is the lesson of PES2-TASK-02 moved up
    a layer: a set computed from one file is only as good as the sweep that
    produced it, so the caller is told the size of the set before anything
    is written, and a set of one is refused unless it was asked for.
    """
    plan = copies_of(img, path)
    if len(plan) == 1 and not allow_partial:
        raise Refused(
            f"{path} has no other copy on this disc -- if that is really "
            f"true, pass --allow-partial and say so in the log")
    old = digest(img.read_file(path))
    for p in plan:
        img.write_file(p, new)
    return plan, old


def survivors(img, old, plan):
    """Files that still hold the old content after a write. Must be empty."""
    return [p for p in sorted(img.files)
            if p not in plan and img.is_form1(p)
            and digest(img.read_file(p)) == old]


def release_of(image):
    """The tag EXPECT is keyed by, taken from the file name."""
    name = os.path.basename(image)
    for key in EXPECT:
        if key in name:
            return key
    return None


def report(img, args):
    found = groups(img)
    print(f"{os.path.basename(args.image)}: {len(found)} copy set(s)")
    for g in found:
        size = len(img.read_file(g[0]))
        print(f"  {len(g)} x {size} B   "
              + ", ".join(p.replace('/BIN/', '') for p in g))
    return found


def cmd(args):
    with Image(args.image) as img:
        if args.asset:
            plan = copies_of(img, args.asset)
            print(f"{args.asset} has {len(plan)} copy/copies:")
            for p in plan:
                print(f"  {p}")
            return 0

        found = report(img, args)

        if args.check:
            key = release_of(args.image)
            if key is None:
                print("CHECK SKIPPED: this image is not one of the two "
                      "releases EXPECT was measured on", file=sys.stderr)
                return 0
            got = sorted(tuple(os.path.basename(p) for p in g) for g in found)
            want = sorted(EXPECT[key])
            if got != want:
                print(f"CHECK FAILED {key}:\n  got      {got}\n"
                      f"  expected {want}", file=sys.stderr)
                return 1
            print("CHECK OK", file=sys.stderr)
    return 0


def self_check(image, tmpdir):
    """Write one asset to its whole copy set on a copy, then put it back.

    What it proves is the pair the task asks for: every copy carries the
    new bytes, **and** no file anywhere on the disc still carries the old
    ones -- which is the half of section 6.1 that a screenshot of the right
    language would never catch.
    """
    bad = 0
    with Image(image) as img:
        sets = groups(img)
        target = None
        for g in sets:
            if "T_NAME" in g[0]:
                target = g
                break
        if target is None:
            print("no T_NAME copy set on this image", file=sys.stderr)
            return 1
        print(f"copy set: {len(target)} file(s) -- "
              + ", ".join(p.replace('/BIN/', '') for p in target))
        original = img.read_file(target[0])

        print("\n-- the refusal, on the original, read-only --")
        try:
            write_all(img, "/BIN/TITLE.BIN", b"")
            print("  FAILED: a lone file was accepted")
            bad += 1
        except Refused as exc:
            print(f"  refused a lone file: {exc}")

    before = _sha(image)
    work = tempfile.mkdtemp(prefix="pes2-lang-", dir=tmpdir)
    copy = os.path.join(work, "track1.bin")
    try:
        print(f"\ncopying {os.path.getsize(image) // (1 << 20)} MiB ...")
        shutil.copyfile(image, copy)

        # A change that is real but cannot break the container: swap the
        # two halves of the first name tile's pixel data. Same length, same
        # records, and it moves bytes the game would draw.
        edited = bytearray(original)
        half = len(edited) // 2
        edited[:half], edited[half:] = edited[half:], edited[:half]

        with Image(copy, writable=True) as img:
            plan, old = write_all(img, target[0], bytes(edited))
            print(f"wrote {len(plan)} copy/copies")
        with Image(copy) as img:
            for p in plan:
                ok = img.read_file(p) == bytes(edited)
                print(f"  {p:22s} {'new' if ok else 'MISMATCH'}")
                bad += 0 if ok else 1
            left = survivors(img, old, plan)
            if left:
                print(f"  FAILED: {len(left)} file(s) still hold the old "
                      f"content: {left}")
                bad += 1
            else:
                print("  swept the disc: no file still holds the old content")

        with Image(copy, writable=True) as img:
            write_all(img, target[0], original)
        after = _sha(copy)
        if after == before:
            print("\nround-trip OK: the image is byte for byte the original")
        else:
            print(f"\nROUND-TRIP FAILED: {before} != {after}")
            bad += 1
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print("\nSELF-CHECK FAILED" if bad else "\nSELF-CHECK OK")
    return 1 if bad else 0


def _sha(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                return h.hexdigest()
            h.update(b)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--asset", metavar="PATH",
                    help="the copy set of one file")
    ap.add_argument("--check", action="store_true",
                    help="assert the copy sets measured on 2026-09-01")
    ap.add_argument("--self-check", action="store_true",
                    help="write a copy set on a copy and put it back")
    ap.add_argument("--tmpdir", metavar="DIR")
    args = ap.parse_args(argv)
    try:
        if args.self_check:
            if not args.tmpdir or not os.path.isdir(args.tmpdir):
                print("--self-check needs --tmpdir", file=sys.stderr)
                return 2
            return self_check(args.image, args.tmpdir)
        return cmd(args)
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

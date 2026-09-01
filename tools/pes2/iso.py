#!/usr/bin/env python3
"""Read, extract and re-inject files in a PES2 (PSX) CD image -- phase 0.

The disc is MODE2/2352: every sector is 24 bytes of header, then a data
area, then a tail. Nothing in this repository ever rewrites that tail --
the game does not verify EDC/ECC and the original editors do not
recompute it, so preserving it byte for byte is the policy (see the plan,
section 6.6). Injection therefore writes *into* the data area of the
sectors a file already occupies, and refuses anything that would change a
length.

Two facts about this image shape the code:

  Form 1 vs Form 2.  Submode bit 0x20 of the subheader says which. Form 1
  carries 2048 bytes of data and 280 of EDC/ECC; Form 2 carries 2324 and
  no ECC. About 60% of the sectors of track 1 are Form 2 -- the XA audio
  and the video stream. Reading 2048 out of one of those yields garbage,
  so every read checks the form and raises instead of guessing.

  Multi-track.  The `(EsIt)` and `(EnFrDe)` dumps ship eight files: one
  data track and seven audio. Offsets only mean anything inside track 1,
  so that is what this tool opens (plan, section 6.4).

Usage:

    python3 tools/pes2/iso.py ls        <track1.bin>
    python3 tools/pes2/iso.py extract   <track1.bin> /SELECT.BIN -o out.bin
    python3 tools/pes2/iso.py inject    <track1.bin> /SELECT.BIN new.bin
    python3 tools/pes2/iso.py anchors   <track1.bin>
    python3 tools/pes2/iso.py roundtrip <track1.bin>
    python3 tools/pes2/iso.py negative  <track1.bin>

`roundtrip` is the phase-0 guard: it copies the image, reads every Form 1
file and writes it straight back, then compares against the original. A
single differing byte means the extract/inject pair is wrong and every
offset measured through it is noise.

`negative` is the other half of that guard, and the half a green run is
worthless without: it makes one deliberate one-byte change and insists
the comparison goes red, at the byte sector arithmetic predicts and
nowhere else.
"""

import argparse
import os
import shutil
import struct
import sys
import tempfile

RAW_SECTOR = 2352
HEADER = 24            # 12 sync + 4 header + 8 subheader
FORM1_DATA = 2048
FORM2_DATA = 2324
SUBMODE_FORM2 = 0x20

PVD_LBA = 16

# The marker literals of section 1.13 of the plan. Each occurs exactly once
# in its file, in both European releases, which is what lets a table be
# located without a constant offset -- three of the seven copies move
# between releases because the localized interface text ahead of them is a
# different length.
ANCHORS = [
    ("team names", "/SELECT.BIN", b"MASTER DATA\x00"),
    ("abbreviations", "/SELECT.BIN", b"PTA\x00MRA\x00BZA\x00"),
    ("abbreviations (copy)", "/SELECT8.BIN", b"PTA\x00MRA\x00BZA\x00"),
    ("abbreviations (copy)", "/REPLAYS.BIN", b"PTA\x00MRA\x00BZA\x00"),
    ("team names (copy)", "/ENDING.BIN", b"PATAGONIA\x00"),
    ("mixed case (copy)", "/RESULT.BIN", b"Patagonia\x00"),
    ("mixed case (copy)", "/SELECT.BIN", b"Patagonia\x00"),
    ("teams + players", "/SELECTC.BIN", b"Belarus\x00Georgia\x00"),
    ("mixed case (copy)", "/SELECT3.BIN", b"Belarus\x00Georgia\x00"),
    ("mixed case (copy)", "/SELFORM.BIN", b"Belarus\x00Georgia\x00"),
    ("club players, 10 B records", "/SELECT.BIN", b"Oranges001"),
]


class Form2Sector(Exception):
    """Raised rather than returning 2048 bytes that do not exist."""


class OutsideTrack(Exception):
    """Raised for a sector the data track does not reach.

    The ISO directory spans the whole disc, so it names files that live on
    the later tracks -- in the `(EsIt)` dump the seven `/SD/DA/*.DA` entries
    start at LBA 198606 while track 1 ends at 198456. In a multi-track dump
    those sectors are simply in another file, and this tool only opens
    track 1 (plan, section 6.4).
    """


class Entry:
    __slots__ = ("path", "lba", "size")

    def __init__(self, path, lba, size):
        self.path = path
        self.lba = lba
        self.size = size

    @property
    def sectors(self):
        return (self.size + FORM1_DATA - 1) // FORM1_DATA

    def __repr__(self):
        return f"Entry({self.path!r}, lba={self.lba}, size={self.size})"


class Image:
    """One data track of a MODE2/2352 PSX disc."""

    def __init__(self, path, writable=False):
        self.path = path
        self.f = open(path, "r+b" if writable else "rb")
        # Everything past the open() can raise -- a truncated track, a
        # missing PVD, a directory record that does not parse. Without this
        # the descriptor leaks, and on a writable image that also means the
        # lock outlives the failure.
        try:
            size = os.path.getsize(path)
            if size % RAW_SECTOR:
                raise ValueError(
                    f"{path}: {size} bytes is not a whole number of 2352-byte "
                    f"sectors -- is this the data track?"
                )
            self.sector_count = size // RAW_SECTOR
            self.files = {}
            self._read_filesystem()
        except BaseException:
            self.f.close()
            raise

    # ---- sectors ----------------------------------------------------

    def subheader(self, lba):
        if not 0 <= lba < self.sector_count:
            raise OutsideTrack(
                f"sector {lba} is past the end of this track ({self.sector_count})"
            )
        self.f.seek(lba * RAW_SECTOR + 16)
        return self.f.read(8)

    def form(self, lba):
        return 2 if self.subheader(lba)[2] & SUBMODE_FORM2 else 1

    def read_sector(self, lba):
        """The 2048 data bytes of a Form 1 sector."""
        if self.form(lba) != 1:
            raise Form2Sector(f"sector {lba} is Form 2; it has no 2048-byte area")
        self.f.seek(lba * RAW_SECTOR + HEADER)
        return self.f.read(FORM1_DATA)

    def write_sector(self, lba, data, offset=0):
        """Overwrite part of a Form 1 data area. Header and tail untouched."""
        if self.form(lba) != 1:
            raise Form2Sector(f"sector {lba} is Form 2; refusing to write 2048 bytes")
        if offset + len(data) > FORM1_DATA:
            raise ValueError(
                f"sector {lba}: {len(data)} bytes at {offset} runs past the "
                f"2048-byte data area and would land in the EDC/ECC tail"
            )
        self.f.seek(lba * RAW_SECTOR + HEADER + offset)
        self.f.write(data)

    # ---- ISO 9660 ---------------------------------------------------

    def _read_dir(self, lba, size):
        data = b"".join(
            self.read_sector(lba + i) for i in range((size + FORM1_DATA - 1) // FORM1_DATA)
        )
        out = []
        p = 0
        while p < len(data):
            length = data[p]
            if length == 0:
                # Records never straddle a sector; a zero byte means the
                # rest of this sector is padding.
                p = (p // FORM1_DATA + 1) * FORM1_DATA
                if p >= len(data):
                    break
                continue
            rec = data[p : p + length]
            child_lba = struct.unpack("<I", rec[2:6])[0]
            child_size = struct.unpack("<I", rec[10:14])[0]
            flags = rec[25]
            name = rec[33 : 33 + rec[32]].decode("latin-1")
            out.append((name, child_lba, child_size, flags))
            p += length
        return out

    def _read_filesystem(self):
        pvd = self.read_sector(PVD_LBA)
        if pvd[1:6] != b"CD001":
            raise ValueError(f"{self.path}: no CD001 at sector {PVD_LBA}")
        root = pvd[156:190]
        root_lba = struct.unpack("<I", root[2:6])[0]
        root_size = struct.unpack("<I", root[10:14])[0]
        self.volume_id = pvd[40:72].decode("latin-1").strip()

        def walk(lba, size, prefix, depth):
            for name, child_lba, child_size, flags in self._read_dir(lba, size):
                if name in ("\x00", "\x01"):        # "." and ".."
                    continue
                if flags & 0x02:
                    if depth < 8:
                        walk(child_lba, max(child_size, FORM1_DATA),
                             prefix + name + "/", depth + 1)
                else:
                    clean = prefix + name.split(";")[0]
                    self.files[clean] = Entry(clean, child_lba, child_size)

        walk(root_lba, root_size, "/", 0)

    # ---- files ------------------------------------------------------

    def entry(self, path):
        try:
            return self.files[path]
        except KeyError:
            raise KeyError(f"{path}: not on this disc") from None

    def status(self, path):
        """"form1", "form2" or "outside" -- whether this tool can read it."""
        e = self.entry(path)
        if e.lba + e.sectors > self.sector_count:
            return "outside"
        for i in range(e.sectors):
            if self.form(e.lba + i) != 1:
                return "form2"
        return "form1"

    def is_form1(self, path):
        """Whether every sector of the file is Form 1, hence readable here."""
        return self.status(path) == "form1"

    def read_file(self, path):
        e = self.entry(path)
        return b"".join(self.read_sector(e.lba + i) for i in range(e.sectors))[: e.size]

    def write_file(self, path, data):
        """Write a file back in place. The length must not change.

        Growing a file would mean moving it, which means rewriting the
        directory record and every sector after it -- and the game reaches
        several of these overlays by hardcoded LBA, not through the
        filesystem. In-place is the only safe edit.
        """
        e = self.entry(path)
        if len(data) != e.size:
            raise ValueError(
                f"{path}: is {e.size} bytes, refusing to write {len(data)} -- "
                f"in-place only"
            )
        # Check the whole run *before* writing a byte. Trusting write_sector
        # to raise would leave a mixed file half rewritten and the image in a
        # state no one asked for: on a 445 MiB working copy that is a slow
        # recopy to undo. None of the 244 form1 files is mixed today, so this
        # is a latent defect -- but inject is the tool of the poke cycle.
        state = self.status(path)
        if state != "form1":
            raise (OutsideTrack if state == "outside" else Form2Sector)(
                f"{path}: {state}; refusing to write any of it"
            )
        for i in range(e.sectors):
            chunk = data[i * FORM1_DATA : (i + 1) * FORM1_DATA]
            # The final sector is usually part slack. Write only the bytes
            # the file actually owns, so whatever follows it stays put.
            self.write_sector(e.lba + i, chunk)

    def find(self, path, marker):
        """Offset of `marker` in a file, asserting it occurs exactly once."""
        data = self.read_file(path)
        n = data.count(marker)
        if n != 1:
            raise ValueError(f"{path}: marker {marker!r} occurs {n} times, expected 1")
        return data.index(marker)

    def close(self):
        self.f.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


# ---- commands -------------------------------------------------------


def cmd_ls(args):
    with Image(args.image) as img:
        print(f"{img.volume_id}  --  {len(img.files)} files, "
              f"{img.sector_count} sectors")
        for path in sorted(img.files):
            e = img.files[path]
            print(f"  {path:34s} lba={e.lba:7d} size={e.size:10d} "
                  f"{img.status(path)}")


def cmd_extract(args):
    with Image(args.image) as img:
        data = img.read_file(args.path)
    out = args.output or os.path.basename(args.path)
    with open(out, "wb") as fh:
        fh.write(data)
    print(f"{args.path} -> {out} ({len(data)} bytes)")


def cmd_inject(args):
    with open(args.source, "rb") as fh:
        data = fh.read()
    with Image(args.image, writable=True) as img:
        img.write_file(args.path, data)
    print(f"{args.source} -> {args.image}:{args.path} ({len(data)} bytes)")


def cmd_anchors(args):
    with Image(args.image) as img:
        print(f"{os.path.basename(args.image)}")
        bad = 0
        for label, path, marker in ANCHORS:
            try:
                off = img.find(path, marker)
                print(f"  {label:28s} {path:14s} @{off:7d}  {marker[:16]!r}")
            except (KeyError, ValueError) as exc:
                bad += 1
                print(f"  {label:28s} {path:14s} FAILED: {exc}")
    return 1 if bad else 0


def cmd_roundtrip(args):
    """Extract every Form 1 file and write it straight back, then compare.

    This is the phase-0 guard. It exercises the write path for real rather
    than reasoning about it: if reading and re-writing a file is not the
    identity, no offset measured through this tool means anything.
    """
    with Image(args.image) as img:
        state = {p: img.status(p) for p in sorted(img.files)}
    form1 = [p for p, s in state.items() if s == "form1"]
    skipped = [(p, s) for p, s in state.items() if s != "form1"]

    tmpdir = tempfile.mkdtemp(prefix="pes2-roundtrip-", dir=args.tmpdir)
    copy = os.path.join(tmpdir, "track1.bin")
    try:
        print(f"copying {os.path.getsize(args.image) // (1 << 20)} MiB to {copy} ...")
        shutil.copyfile(args.image, copy)

        with Image(copy, writable=True) as img:
            for p in form1:
                img.write_file(p, img.read_file(p))
        print(f"rewrote {len(form1)} files; skipped {len(skipped)}")
        for p, why in skipped:
            print(f"    skipped ({why}): {p}")

        diff = _first_difference(args.image, copy)
        if diff is None:
            print("ROUND-TRIP OK: image is byte-identical")
            return 0
        off, a, b = diff
        print(f"ROUND-TRIP FAILED: first difference at byte {off} "
              f"(sector {off // RAW_SECTOR}, offset {off % RAW_SECTOR} in sector): "
              f"{a:#04x} != {b:#04x}")
        return 1
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


# The negative control of section 5.1 of the plan. PIEMONTE is a good
# subject for one reason beyond being easy to spell: its record crosses a
# sector boundary, which is trap 6.3. A write path that forgot the 304
# bytes of header and tail would land somewhere else, or on two bytes.
NEGATIVE_FILE = "/SELECT.BIN"
NEGATIVE_WORD = b"PIEMONTE"
NEGATIVE_BYTE = ord("X")


def cmd_negative(args):
    """Change one byte on purpose, and insist the guard notices.

    A green round-trip only means something if the same comparison can go
    red. This proves it can, and proves the sector arithmetic at the same
    time: the expected absolute offset is computed from the file's LBA and
    the record's offset inside it, then checked against where the byte
    actually moved.
    """
    with Image(args.image) as img:
        entry = img.entry(NEGATIVE_FILE)
        data = img.read_file(NEGATIVE_FILE)
    n = data.count(NEGATIVE_WORD)
    if n != 1:
        print(f"{NEGATIVE_FILE}: {NEGATIVE_WORD!r} occurs {n} times, expected 1")
        return 1
    rel = data.index(NEGATIVE_WORD)

    lba = entry.lba + rel // FORM1_DATA
    inside = rel % FORM1_DATA
    expected = lba * RAW_SECTOR + HEADER + inside
    crosses = (rel % FORM1_DATA) != rel

    tmpdir = tempfile.mkdtemp(prefix="pes2-negative-", dir=args.tmpdir)
    copy = os.path.join(tmpdir, "track1.bin")
    try:
        print(f"copying {os.path.getsize(args.image) // (1 << 20)} MiB to {copy} ...")
        shutil.copyfile(args.image, copy)

        edited = bytearray(data)
        edited[rel] = NEGATIVE_BYTE
        with Image(copy, writable=True) as img:
            img.write_file(NEGATIVE_FILE, bytes(edited))

        print(f"{NEGATIVE_FILE} starts at LBA {entry.lba}; {NEGATIVE_WORD.decode()} "
              f"at file offset {rel}")
        print(f"  {rel} / {FORM1_DATA} = LBA {lba}, remainder {inside}, "
              f"+{HEADER} header -> absolute {expected}"
              f"{'   (crosses a sector boundary)' if crosses else ''}")

        diff = _first_difference(args.image, copy)
        if diff is None:
            print("NEGATIVE CONTROL FAILED: the image did not change at all -- "
                  "the guard cannot go red")
            return 1
        off, a, b = diff
        n_diff = _count_differences(args.image, copy)
        ok = (off == expected and n_diff == 1
              and a == NEGATIVE_WORD[0] and b == NEGATIVE_BYTE)
        print(f"  first difference at {off}: {a:#04x} -> {b:#04x}; "
              f"{n_diff} byte(s) changed in the whole image")
        if not ok:
            print(f"NEGATIVE CONTROL FAILED: expected exactly 1 byte at {expected}")
            return 1
        print("NEGATIVE CONTROL OK: one byte, where the arithmetic says, "
              "header and tail untouched")
        return 0
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def _count_differences(p1, p2, chunk=1 << 22):
    total = 0
    with open(p1, "rb") as f1, open(p2, "rb") as f2:
        while True:
            a = f1.read(chunk)
            b = f2.read(chunk)
            if not a:
                return total
            if a != b:
                total += sum(1 for x, y in zip(a, b) if x != y)


def _first_difference(p1, p2, chunk=1 << 22):
    if os.path.getsize(p1) != os.path.getsize(p2):
        return (min(os.path.getsize(p1), os.path.getsize(p2)), 0, 0)
    off = 0
    with open(p1, "rb") as f1, open(p2, "rb") as f2:
        while True:
            a = f1.read(chunk)
            b = f2.read(chunk)
            if not a:
                return None
            if a != b:
                for i, (x, y) in enumerate(zip(a, b)):
                    if x != y:
                        return (off + i, x, y)
            off += len(a)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    def add(name, fn, **kw):
        p = sub.add_parser(name, **kw)
        p.add_argument("image", help="the data track (.bin) of the disc")
        p.set_defaults(fn=fn)
        return p

    add("ls", cmd_ls, help="list the files on the disc")
    p = add("extract", cmd_extract, help="write one file out")
    p.add_argument("path", help="absolute path on the disc, e.g. /SELECT.BIN")
    p.add_argument("-o", "--output")
    p = add("inject", cmd_inject, help="write one file back in place")
    p.add_argument("path")
    p.add_argument("source", help="local file, must be exactly the same size")
    add("anchors", cmd_anchors, help="resolve the marker literals of plan 1.13")
    p = add("roundtrip", cmd_roundtrip, help="extract-and-reinject guard")
    p.add_argument("--tmpdir", default=None,
                   help="where to put the working copy (needs ~450 MiB)")
    p = add("negative", cmd_negative,
            help="prove the round-trip guard can go red")
    p.add_argument("--tmpdir", default=None,
                   help="where to put the working copy (needs ~450 MiB)")

    args = ap.parse_args(argv)
    return args.fn(args) or 0


if __name__ == "__main__":
    sys.exit(main())

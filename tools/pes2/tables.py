#!/usr/bin/env python3
"""Locate, count and dump the text tables of PES2 (PSX) -- phase 2 groundwork.

Section 1.6 of the plan states counts and a canonical order as measured
fact. This is the measurement. It exists because a number quoted in prose
and a number a tool prints again are not the same claim: the second one
can go red.

Every table is described the way section 1.13 says a map entry must look
-- **(file, marker, signed delta)** -- plus the two things 1.13 does not
yet provide and section 4 of docs/PES2-AJUSTES.md asks for:

  a record scheme -- variable-length NUL-terminated, or a fixed width;
  an end rule -- because **no table on this disc has a sentinel**. What
  separates one from the next is nothing but the count, so the end has to
  be stated, never discovered.

The delta is signed on purpose. `Oranges001` is inside the table it
anchors, at record 174 of 463, so its delta is -1740.

Usage:

    python3 tools/pes2/tables.py <track1.bin>            # summary
    python3 tools/pes2/tables.py <track1.bin> --dump team-names
    python3 tools/pes2/tables.py <track1.bin> --check    # assert 1.6

`--check` asserts the count *and* a digest of the joined entries. The
digests are identical in `(EsIt)` and `(EnFrDe)`, which is what makes
section 1.12's "same database, one editor" a test rather than a memory.
"""

import argparse
import hashlib
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402

BOOT = "@BOOT"          # stands for whatever SYSTEM.CNF names

PRINTABLE = range(0x20, 0x7F)


class Table:
    """One text table: where it starts, how a record looks, where it ends."""

    def __init__(self, key, label, file, anchor, delta, scheme, stop,
                 expect=None, digest=None, note=""):
        self.key = key
        self.label = label
        self.file = file
        self.anchor = anchor
        self.delta = delta
        self.scheme = scheme        # "cstr" or ("fixed", width)
        self.stop = stop            # ("anchor", m) | ("value", v) | ("shape",)
        self.expect = expect
        self.digest = digest
        self.note = note


# The end rule of the two uppercase lists is a *value*, not a marker: both
# run to the last real nation and stop, and IRELAND/Ireland is the last one
# in every list on this disc. Using a value keeps the rule readable and
# keeps it honest -- a list that grew would fail loudly instead of running
# on into whatever follows.
TABLES = [
    Table("team-names", "team name, upper case",
          "/SELECT.BIN", b"MASTER DATA\x00", 0, "cstr",
          ("anchor", b"PTA\x00MRA\x00BZA\x00"), 106, "8a6ade4e37651f9a",
          note="2 header entries + 104 teams; ends exactly where the "
               "abbreviations begin -- zero bytes of slack"),
    Table("abbreviations", "abbreviation, 3 letters",
          "/SELECT.BIN", b"PTA\x00MRA\x00BZA\x00", 0, ("fixed", 4),
          ("value", b"IRL"), 95, "7cdfb5d4be0c40f1",
          note="covers only the first 95 teams: the 7 classics and the "
               "2 allstars have none"),
    Table("club-players", "club player, 10 B records",
          "/SELECT.BIN", b"Oranges001", -1740, ("fixed", 10),
          ("shape",), 463, "3e406786e53525ed",
          note="the marker sits at record 174 of the table it anchors"),
    Table("team-names-ending", "team name, upper case (copy)",
          "/ENDING.BIN", b"PATAGONIA\x00", 0, "cstr",
          ("value", b"IRELAND"), 95, "a96cebda3be5b6a4",
          note="drops the 2 header entries, the 7 classics and the "
               "2 allstars"),
    Table("abbreviations-select8", "abbreviation (copy)",
          "/SELECT8.BIN", b"PTA\x00MRA\x00BZA\x00", 0, ("fixed", 4),
          ("value", b"IRL"), 95, "7cdfb5d4be0c40f1"),
    Table("abbreviations-replays", "abbreviation (copy)",
          "/REPLAYS.BIN", b"PTA\x00MRA\x00BZA\x00", 0, ("fixed", 4),
          ("value", b"IRL"), 95, "7cdfb5d4be0c40f1",
          note="here the shape rule alone would not stop: the mixed-case "
               "copy starts 1 byte later and `Pata` passes for a record"),
    Table("team-names-replays", "team name, mixed case (copy)",
          "/REPLAYS.BIN", b"PTA\x00MRA\x00BZA\x00", 380, "cstr",
          ("value", b"Ireland"), 123, "bbf2633d23b3108d",
          note="a *different* list: 32 fictitious, then Edit/Free/Default, "
               "then the full nation roster of the edit mode"),
    Table("team-names-result", "team name, mixed case (copy)",
          "/RESULT.BIN", b"Patagonia\x00", 0, "cstr",
          ("value", b"Ireland"), 94, "fbed0aa8536eb1ca",
          note="also a different list: where the upper-case one has the 7 "
               "themed sides and the 2 elites, this one has the classics "
               "and the allstars"),
    Table("team-names-selectc", "team name, mixed case",
          "/SELECTC.BIN", b"Belarus\x00Georgia\x00", 0, "cstr",
          ("value", b"Ireland"), 99, "035b8ad4e45d62da",
          note="opens with 4 nations no other list has -- Belarus, "
               "Georgia, Uzbekistan, Iceland"),
    Table("player-names", "player name",
          "/SELECTC.BIN", b"Belarus\x00Georgia\x00", 1028, "cstr",
          ("shape",), 1399, "016956f1676ef44c",
          note="fictitious first, then the real ones from Bonano on"),
    Table("player-names-boot", "player name, 10 B records",
          BOOT, b"Given\x00\x00\x00\x00\x00Staunton\x00\x00", 0, ("fixed", 10),
          ("shape",), 1449, "2861ded7b6949ab7",
          note="the same span as player-names, stored backwards and 50 "
               "entries longer -- the squads section 3.3 could not find "
               "in SELECTC.BIN"),
]


def boot_executable(img):
    """The name SYSTEM.CNF gives the boot binary, as an absolute disc path.

    `BOOT = cdrom:SLES_039.57;1` in `(EsIt)`, `SLES_039.46` in `(EnFrDe)`.
    Resolving it rather than hardcoding either is what lets one table
    definition serve both releases.
    """
    text = img.read_file("/SYSTEM.CNF").decode("latin-1")
    for line in text.splitlines():
        if line.strip().upper().startswith("BOOT"):
            value = line.split("=", 1)[1].strip()
            name = value.split(":")[-1].split(";")[0].strip()
            return "/" + name.lstrip("\\/")
    raise ValueError("SYSTEM.CNF has no BOOT line")


def _printable(bs):
    return bool(bs) and all(c in PRINTABLE for c in bs)


def _read_cstr(data, start, stop_at, stop_value):
    """NUL-terminated entries, padding NULs skipped."""
    out = []
    p = start
    while p < len(data):
        if stop_at is not None and p >= stop_at:
            break
        if data[p] == 0:                      # padding between entries
            p += 1
            continue
        end = data.find(b"\x00", p)
        if end < 0:
            break
        s = data[p:end]
        if not _printable(s):
            break
        out.append((p, s))
        p = end + 1
        if stop_value is not None and s == stop_value:
            break
    return out


def _read_fixed(data, start, width, stop_at, stop_value):
    """Fixed-width records, right-padded with NUL. A name may fill it whole.

    `McAllister`, `S.Caldwell` and `Eddington` are exactly 10 characters
    and carry no terminator at all, so "ends with NUL" is not the test --
    "every byte before the first NUL is printable, and everything from it
    on is NUL" is.
    """
    out = []
    p = start
    while p + width <= len(data):
        if stop_at is not None and p >= stop_at:
            break
        rec = data[p:p + width]
        z = rec.find(b"\x00")
        body = rec if z < 0 else rec[:z]
        tail = b"" if z < 0 else rec[z:]
        if not _printable(body) or any(c != 0 for c in tail):
            break
        out.append((p, body))
        p += width
        if stop_value is not None and body == stop_value:
            break
    return out


def resolve(img, table):
    """(path, offset, entries) for one table in this image."""
    path = boot_executable(img) if table.file is BOOT else table.file
    data = img.read_file(path)
    n = data.count(table.anchor)
    if n != 1:
        raise ValueError(
            f"{path}: marker {table.anchor[:16]!r} occurs {n} times, expected 1"
        )
    offset = data.index(table.anchor) + table.delta
    if offset < 0:
        raise ValueError(f"{path}: delta {table.delta} puts the table at {offset}")

    kind, arg = (table.stop + (None,))[:2] if len(table.stop) > 1 else \
                (table.stop[0], None)
    stop_at = stop_value = None
    if kind == "anchor":
        if data.count(arg) != 1:
            raise ValueError(f"{path}: end marker {arg!r} is not unique")
        stop_at = data.index(arg)
    elif kind == "value":
        stop_value = arg

    if table.scheme == "cstr":
        entries = _read_cstr(data, offset, stop_at, stop_value)
    else:
        entries = _read_fixed(data, offset, table.scheme[1], stop_at, stop_value)
    return path, offset, entries


def digest_of(entries):
    h = hashlib.sha256()
    for _, s in entries:
        h.update(s + b"\n")
    return h.hexdigest()[:16]


def cmd(args):
    with Image(args.image) as img:
        boot = boot_executable(img)
        print(f"{os.path.basename(args.image)}   boot={boot.lstrip('/')}")
        bad = 0
        for t in TABLES:
            if args.dump and t.key != args.dump:
                continue
            try:
                path, offset, entries = resolve(img, t)
            except (KeyError, ValueError) as exc:
                bad += 1
                print(f"  {t.key:22s} FAILED: {exc}")
                continue
            d = digest_of(entries)
            flag = ""
            if args.check:
                if t.expect is not None and len(entries) != t.expect:
                    flag = f"  <-- expected {t.expect}"
                    bad += 1
                elif t.digest and d != t.digest:
                    flag = f"  <-- digest, expected {t.digest}"
                    bad += 1
            span = entries[-1][0] + len(entries[-1][1]) - offset if entries else 0
            print(f"  {t.key:22s} {path:14s} @{offset:7d} "
                  f"n={len(entries):5d} span={span:6d} {d}{flag}")
            if args.verbose or args.dump:
                print(f"      {t.label} -- marker {t.anchor[:20]!r} "
                      f"delta {t.delta:+d}")
                if t.note:
                    print(f"      note: {t.note}")
            if args.dump:
                for i, (off, s) in enumerate(entries):
                    print(f"      {i:5d} @{off:7d}  {s.decode('latin-1')}")
            elif args.verbose:
                for i in (0, 1, 2):
                    if i < len(entries):
                        o, s = entries[i]
                        print(f"      {i:5d} @{o:7d}  {s.decode('latin-1')}")
                if len(entries) > 6:
                    print("      ...")
                for i in range(max(3, len(entries) - 3), len(entries)):
                    o, s = entries[i]
                    print(f"      {i:5d} @{o:7d}  {s.decode('latin-1')}")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", help="the data track (.bin) of the disc")
    ap.add_argument("--check", action="store_true",
                    help="assert the counts and digests of plan section 1.6")
    ap.add_argument("--dump", metavar="KEY",
                    help="print every entry of one table")
    ap.add_argument("-v", "--verbose", action="store_true",
                    help="first and last entries, and the end rule")
    ap.add_argument("--list", action="store_true", help="list the table keys")
    args = ap.parse_args(argv)
    if args.list:
        for t in TABLES:
            print(f"{t.key:22s} {t.label}")
        return 0
    return cmd(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""Write one team's name into **every** copy that holds it -- phase 2.

Section 6.1 of the plan says a written copy is worse than no copy: an
editor that touches only `SELECT.BIN` produces a game showing the new
name on the team-select screen and the old one in the replay and in the
result. So the unit of a write is not a table, it is the **set of copies**
of one logical entity.

And the word "copy" is the trap. The five team-name lists hold 106, 99,
95, 94 and 123 entries and differ in *content*: index 34 is
`ALWAYS ARGENTINA` in one and `Classic Brazil` in another. The
correspondence therefore comes from `team_map.where()`, which matches on
the name, and never from the position.

Three more rules this tool cannot violate:

  **truncate, never shift** (6.2, 1.10). The margin between the last
  team name and the abbreviations that follow it is *zero bytes*. A
  longer name is refused; `--truncate` cuts it, and nothing ever moves.

  **the record scheme is a property of the table** (1.10). These five are
  string + terminator, aligned to 4; `SELECT.BIN` @5320 is 463 records of
  10 fixed bytes with no terminator when the name fills them. Writing a
  NUL into the latter eats the first character of the neighbour.

  **the slot is measured, not assumed.** `Toscana` is 7 characters and
  sits in a 12-byte slot in `RESULT.BIN` and an 8-byte one in
  `SELECT.BIN`. The capacity comes from the distance to the next record.

Usage:

    python3 tools/pes2/poke.py <track1.bin> --team 12 --name PIEMONTE2 --dry-run
    python3 tools/pes2/poke.py <copy.bin>   --team 12 --name PIEMONTE2
    python3 tools/pes2/poke.py <track1.bin> --self-check --tmpdir <dir>

`--dry-run` opens the image read-only. Every other mode writes in place,
and refuses outright to touch anything under a `roms/` directory.
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image, RAW_SECTOR, HEADER, FORM1_DATA        # noqa: E402
import tables as T                                           # noqa: E402
import team_map as TM                                        # noqa: E402

# The five lists, and the case each one stores. It is declared rather than
# guessed, and then *checked* against what is on the disc before any write
# -- see `case_of`. `SELECT.BIN` and `ENDING.BIN` hold `ALWAYS ARGENTINA`;
# the other three hold `Always Argentina`.
CASE = {
    "team-names": "upper",
    "team-names-selectc": "mixed",
    "team-names-ending": "upper",
    "team-names-result": "mixed",
    "team-names-replays": "mixed",
    "team-names-select2": "mixed",
    "team-names-select3": "mixed",
    "team-names-selform": "mixed",
}

KEYS = [TM.CANONICAL] + TM.COPIES

PRINTABLE = range(0x20, 0x7F)


class Refused(Exception):
    """A write this tool will not do, with the reason a human needs."""


def absolute(entry, rel):
    """File-relative offset -> byte offset in the raw 2352-byte track.

    Section 6.3: a record that crosses the end of the 2048-byte data area
    jumps 304 bytes. Every offset this tool carries is relative; the
    conversion happens here and nowhere else.
    """
    return (entry.lba + rel // FORM1_DATA) * RAW_SECTOR + HEADER \
        + rel % FORM1_DATA


def resolve_all(img):
    """key -> (path, offset, entries, end) for the five team-name lists."""
    out = {}
    for key in KEYS:
        t = next(x for x in T.TABLES if x.key == key)
        path, offset, entries, end = T.resolve_full(img, t)
        out[key] = (path, offset, entries, end)
    return out


def as_lists(resolved):
    """The shape `team_map.where()` expects, from one resolution pass."""
    return {k: (path, [(o, s.decode("latin-1")) for o, s in entries])
            for k, (path, offset, entries, end) in resolved.items()}


def slot_of(table, entries, index, end):
    """How many bytes record `index` owns, measured.

    For every record but the last, the distance to the next one -- which
    is the truth, and differs between lists holding the same name. For the
    last, the table's end when the end rule is an offset, and otherwise
    the 4-byte alignment of what is there now, which is the conservative
    reading.
    """
    off, body = entries[index]
    if table.scheme != "cstr":
        return table.scheme[1]
    if index + 1 < len(entries):
        return entries[index + 1][0] - off
    if end is not None:
        return end - off
    return -(-(len(body) + 1) // 4) * 4


def capacity(table, slot):
    """The longest name that fits: a fixed record may fill its width."""
    return slot if table.scheme != "cstr" else slot - 1


def encode(table, text, slot):
    """The bytes of one record: the name, then NUL to the end of the slot.

    A fixed-width record that the name fills exactly carries no terminator
    at all -- `NachtegallHeggem` is how two 10-character names read on the
    disc -- so the padding is what is left over, which may be nothing.
    """
    raw = text.encode("latin-1")
    return raw.ljust(slot, b"\x00")


def case_for(key, value):
    """`value` in the case this list stores, from a name given either way."""
    if CASE[key] == "upper":
        return value.upper()
    return value if any(c.islower() for c in value) else value.title()


def case_of(text):
    """What case a record on the disc is written in, so CASE can be checked."""
    if not any(c.isalpha() for c in text):
        return None                       # `? ? ? ?` says nothing either way
    return "upper" if text == text.upper() else "mixed"


def anchor_ranges(img, path, cache):
    """[(what, start, end)] of every table marker that lives in this file.

    Measured, and it bites at once: `PATAGONIA\0` is the marker that
    anchors `team-names-ending` and `Patagonia\0` the one that anchors
    `team-names-result` -- so renaming canonical team 2, the first team of
    the disc, makes two of the five tables unfindable. A tool that only
    guarded the *end* of a table would have written it and produced an
    image no reader here can open.
    """
    if path in cache:
        return cache[path]
    data = img.read_file(path)
    out = []
    for t in T.TABLES:
        where = T.boot_executable(img) if t.file is T.BOOT else t.file
        if where != path:
            continue
        if data.count(t.anchor) == 1:
            o = data.index(t.anchor)
            out.append((f"{t.key} start marker", o, o + len(t.anchor)))
        if t.stop[0] == "anchor" and data.count(t.stop[1]) == 1:
            o = data.index(t.stop[1])
            out.append((f"{t.key} end marker", o, o + len(t.stop[1])))
    cache[path] = out
    return out


def stop_values():
    """Every value some table's end rule depends on, by table key."""
    out = {}
    for t in T.TABLES:
        if t.stop[0] == "value":
            out.setdefault(t.key, set()).add(t.stop[1].decode("latin-1"))
    return out


def plan(img, team, value, allow_partial=False, truncate=False,
         verbatim=False, force=False):
    """What a poke would write, per copy. Raises Refused rather than guess."""
    if not value:
        raise Refused("the new name is empty")
    if any(ord(c) not in PRINTABLE for c in value):
        raise Refused(f"{value!r} has a byte outside the printable range "
                      f"0x20..0x7E that the disc uses")

    resolved = resolve_all(img)
    lists = as_lists(resolved)
    canon = lists[TM.CANONICAL][1]
    if not 0 <= team < len(canon):
        raise Refused(f"canonical team index must be 0..{len(canon) - 1}")

    places = TM.where(lists, team)
    found = {key for key, _, _, _ in places}
    missing = [k for k in KEYS if k not in found]
    if missing and not allow_partial:
        raise Refused(
            f"canonical team {team} ({canon[team][1]!r}) is not in "
            + ", ".join(missing)
            + " -- pass --allow-partial to write the "
            f"{len(places)} list(s) that do have it")

    stops = stop_values()
    markers = {}
    steps = []
    for key, path, off, index in places:
        table = next(x for x in T.TABLES if x.key == key)
        _, _, entries, end = resolved[key]
        old = entries[index][1].decode("latin-1")

        declared, actual = CASE[key], case_of(old)
        if actual is not None and actual != declared:
            raise Refused(
                f"{key}: {old!r} is {actual} case but this list is declared "
                f"{declared} -- refusing to write until that is settled")

        if not force:
            if old in stops.get(key, ()):
                raise Refused(
                    f"{key}: {old!r} is the value that table's end rule stops "
                    f"on -- renaming it makes the table unreadable. --force "
                    f"if that is really what you want")
            if index == len(entries) - 1:
                raise Refused(
                    f"{key}: {old!r} is the last record of the table, and no "
                    f"table on this disc has a sentinel -- --force to insist")

        slot = slot_of(table, entries, index, end)
        if not force:
            for what, a, b in anchor_ranges(img, path, markers):
                if off < b and a < off + slot:
                    raise Refused(
                        f"{key}: the {slot}-byte slot at {off} overlaps the "
                        f"{what} at {a}..{b} -- writing it would leave a table "
                        f"no tool here can locate. --force to insist")
        room = capacity(table, slot)
        text = value if verbatim else case_for(key, value)
        if len(text) > room:
            if not truncate:
                raise Refused(
                    f"{key} ({path}): {text!r} is {len(text)} characters and "
                    f"the slot at {off} holds {room} "
                    f"({slot} bytes, {'fixed' if table.scheme != 'cstr' else 'string + terminator'})"
                    f" -- pass --truncate to cut it, never to move anything")
            text = text[:room]

        entry = img.entry(path)
        steps.append({
            "key": key, "path": path, "index": index, "rel": off,
            "abs": absolute(entry, off), "slot": slot, "room": room,
            "old": old, "new": text,
            "old_bytes": encode(table, old, slot),
            "new_bytes": encode(table, text, slot),
            "crosses": off // FORM1_DATA != (off + slot - 1) // FORM1_DATA,
        })
    return canon[team][1], steps, missing


def leftovers(img, steps):
    """Every whole record on the disc still holding the old name.

    This is the check that makes "all the copies" a measurement instead of
    a claim, and it earned its place the first time it ran: the five lists
    the plan listed were not all of them. `SELECT.BIN` holds a second,
    mixed-case list; `SELECT3.BIN` and `SELFORM.BIN` hold the 99-entry one
    again. Writing five of eight is section 6.1 word for word -- the new
    name on one screen and the old one on the next.

    A hit counts only when the match is a whole NUL-delimited record, so a
    name that is a prefix of another does not raise one.
    """
    wanted = {s["old"] for s in steps}
    planned = [(s["path"], s["rel"], s["rel"] + s["slot"]) for s in steps]
    out = []
    for path in sorted(img.files):
        if not img.is_form1(path):
            continue
        data = img.read_file(path)
        for name in wanted:
            raw = name.encode("latin-1")
            i = data.find(raw)
            while i >= 0:
                whole = (i == 0 or data[i - 1] == 0) \
                    and i + len(raw) < len(data) and data[i + len(raw)] == 0
                covered = any(p == path and a <= i < b for p, a, b in planned)
                if whole and not covered:
                    out.append((path, i, name))
                i = data.find(raw, i + 1)
    return out


def show(name, steps, missing):
    print(f"canonical team {name!r} -- {len(steps)} copy/copies")
    for s in steps:
        print(f"  {s['key']:22s} {s['path']:14s} index {s['index']:3d}  "
              f"rel @{s['rel']:7d}  abs @{s['abs']:10d}  slot {s['slot']:2d} "
              f"(room {s['room']:2d})"
              + ("  crosses a sector boundary" if s["crosses"] else ""))
        print(f"      {s['old']!r} -> {s['new']!r}")
        print(f"      old {s['old_bytes'].hex(' ')}")
        print(f"      new {s['new_bytes'].hex(' ')}")
    for key in missing:
        print(f"  {key:22s} -- team absent from this list, left alone")


def show_leftovers(rest):
    for path, off, name in rest:
        print(f"  UNMAPPED {path:14s} rel @{off:7d}  {name!r} -- no table "
              f"here knows this record")


def invert(steps):
    """The same writes, backwards -- what puts the original bytes back.

    Deriving the restore from the plan rather than re-casing the old name
    keeps the round-trip honest: it replays measured bytes, so a bug in
    the casing rule cannot cancel itself out.
    """
    out = []
    for s in steps:
        t = dict(s)
        t["old"], t["new"] = s["new"], s["old"]
        t["old_bytes"], t["new_bytes"] = s["new_bytes"], s["old_bytes"]
        out.append(t)
    return out


def apply(img, steps):
    """Write, one file at a time, whole-file so `write_file` guards the run."""
    by_file = {}
    for s in steps:
        by_file.setdefault(s["path"], []).append(s)
    for path, group in by_file.items():
        data = bytearray(img.read_file(path))
        for s in group:
            data[s["rel"]:s["rel"] + s["slot"]] = s["new_bytes"]
        img.write_file(path, bytes(data))
    return len(by_file)


def refuse_roms(path):
    parts = os.path.abspath(path).split(os.sep)
    if "roms" in parts:
        raise Refused(
            f"{path} is under a roms/ directory -- those are the originals "
            f"and this writes in place. Copy the release first.")


# ---- the self-check -------------------------------------------------

def _sha(path, chunk=1 << 22):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                return h.hexdigest()
            h.update(b)


def _first_pokeable(img):
    """The lowest canonical index in all five lists that the guards allow.

    Not merely "in all five": canonical team 2 is `PATAGONIA`, which is in
    all five *and* is the marker two of the tables are anchored on. The
    only honest test of "may I write this" is to plan the write.
    """
    lists = as_lists(resolve_all(img))
    for i in range(len(lists[TM.CANONICAL][1])):
        if len({k for k, _, _, _ in TM.where(lists, i)}) != len(KEYS):
            continue
        try:
            plan(img, i, lists[TM.CANONICAL][1][i][1])
        except Refused:
            continue
        return i
    raise Refused("no canonical team can be written in all five lists")


def _expect_refusal(img, what, **kw):
    try:
        plan(img, **kw)
    except Refused as exc:
        print(f"  refused {what}: {exc}")
        return 0
    print(f"  FAILED: {what} was accepted and should have been refused")
    return 1


def self_check(image, tmpdir):
    """Poke a copy, read it back through the tables, then poke it back.

    The last step is the one that matters: writing the old name back has
    to give a file `cmp` cannot tell from the original. That proves the
    padding was preserved, the sector headers were left alone, and the
    EDC/ECC tail was never touched.
    """
    bad = 0
    with Image(image) as img:
        team = _first_pokeable(img)
        lists = as_lists(resolve_all(img))
        original = lists[TM.CANONICAL][1][team][1]
        print(f"canonical team {team} = {original!r}, in all five lists")

        print("\n-- refusals, on the original, read-only --")
        bad += _expect_refusal(img, "a name past the slot",
                               team=team, value=original + "XXXXXXXXXXXX")
        bad += _expect_refusal(img, "a partial team without --allow-partial",
                               team=102, value="Classic Gaul")
        bad += _expect_refusal(img, "the record an end rule stops on",
                               team=96, value="Eire")
        bad += _expect_refusal(img, "a non-printable name",
                               team=team, value="Piemonteé")
        bad += _expect_refusal(img, "a record a marker is anchored on",
                               team=2, value="Patagonza")

        room = min(s["room"] for s in plan(img, team, original)[1])
        probe = (original[:1] + "Z" * (room - 1))
        print(f"\n-- the poke: {room} characters, the tightest of the "
              f"{len(KEYS)} slots --")
        name, steps, _ = plan(img, team, probe)
        show(name, steps, [])
        rest = leftovers(img, steps)
        show_leftovers(rest)
        if rest:
            print(f"  FAILED: {len(rest)} copy/copies of {original!r} that "
                  f"no table knows -- the copy set is incomplete")
            bad += 1
        else:
            print(f"  swept every Form 1 file: no unmapped copy of "
                  f"{original!r} left behind")

    before = _sha(image)
    work = tempfile.mkdtemp(prefix="pes2-poke-", dir=tmpdir)
    copy = os.path.join(work, "track1.bin")
    try:
        size = os.path.getsize(image)
        print(f"\ncopying {size // (1 << 20)} MiB to {copy} ...")
        shutil.copyfile(image, copy)

        with Image(copy) as img:
            _, steps, _ = plan(img, team, probe)
        with Image(copy, writable=True) as img:
            files = apply(img, steps)
        print(f"wrote {len(steps)} record(s) in {files} file(s)")

        with Image(copy) as img:
            got = as_lists(resolve_all(img))
            for s in steps:
                have = got[s["key"]][1][s["index"]][1]
                ok = have == s["new"]
                print(f"  {s['key']:22s} reads {have!r} {'ok' if ok else 'MISMATCH'}")
                bad += 0 if ok else 1
            if got[TM.CANONICAL][1][team][1] == original:
                print("  FAILED: the canonical list still reads the old name")
                bad += 1

        if _sha(copy) == before:
            print("  FAILED: the image did not change at all")
            bad += 1

        with Image(copy, writable=True) as img:
            apply(img, invert(steps))

        after = _sha(copy)
        if after == before:
            print("\nround-trip OK: writing the old name back gives the "
                  "original image, byte for byte")
        else:
            print(f"\nROUND-TRIP FAILED: {before} != {after}")
            bad += 1
    finally:
        shutil.rmtree(work, ignore_errors=True)

    print("\nSELF-CHECK FAILED" if bad else "\nSELF-CHECK OK")
    return 1 if bad else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", help="the data track (.bin) of the disc")
    ap.add_argument("--team", type=int, metavar="N",
                    help="canonical team index, as team_map.py numbers them")
    ap.add_argument("--name", metavar="TEXT", help="the new team name")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the write and open the image read-only")
    ap.add_argument("--truncate", action="store_true",
                    help="cut a name that does not fit, instead of refusing")
    ap.add_argument("--allow-partial", action="store_true",
                    help="write the lists that have the team, skip the rest")
    ap.add_argument("--verbatim", action="store_true",
                    help="write the name as given, without per-list casing")
    ap.add_argument("--force", action="store_true",
                    help="allow writing a record a table's end rule needs")
    ap.add_argument("--allow-unmapped", action="store_true",
                    help="write even though the old name survives somewhere "
                         "no table knows -- section 6.1 says do not")
    ap.add_argument("--self-check", action="store_true",
                    help="poke a copy and poke it back; needs --tmpdir")
    ap.add_argument("--tmpdir", metavar="DIR",
                    help="where --self-check may put its ~450 MiB copy")
    args = ap.parse_args(argv)

    try:
        if args.self_check:
            if not args.tmpdir or not os.path.isdir(args.tmpdir):
                print("--self-check needs --tmpdir pointing at a directory "
                      "with ~450 MiB free", file=sys.stderr)
                return 2
            return self_check(args.image, args.tmpdir)

        if args.team is None or args.name is None:
            print("--team and --name are both required", file=sys.stderr)
            return 2

        if not args.dry_run:
            refuse_roms(args.image)

        with Image(args.image) as img:
            name, steps, missing = plan(
                img, args.team, args.name,
                allow_partial=args.allow_partial, truncate=args.truncate,
                verbatim=args.verbatim, force=args.force)
            show(name, steps, missing)
            rest = leftovers(img, steps)
            show_leftovers(rest)
        if rest and not args.allow_unmapped:
            raise Refused(
                f"{len(rest)} record(s) would keep the old name after this "
                f"write, in files no table describes -- a game showing the "
                f"new name on one screen and the old one on the next is the "
                f"failure section 6.1 catalogues. Map them, or pass "
                f"--allow-unmapped knowing that")

        if args.dry_run:
            print("\n--dry-run: nothing written")
            return 0

        with Image(args.image, writable=True) as img:
            files = apply(img, steps)
        print(f"\nwrote {len(steps)} record(s) in {files} file(s)")
        return 0
    except Refused as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

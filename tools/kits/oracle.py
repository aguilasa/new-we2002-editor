#!/usr/bin/env python3
"""Which kit, and which of its two sets, the console holds in VRAM.

PLAN-KITS-PY.md section 4.1 (KITS-TASK-27): "are the first and second team's
kits the first and second pair of the TEX?"  Asked of the game, not of the
file: a save state of a match is loaded in the fork, the whole 1024x512 VRAM is
dumped, and every record of every one of the 105 kit containers is looked for
in it -- ANYWHERE, not at the rectangle the container declares, because two
teams share a match and both cannot sit on (576, 256).

A record is found when its whole rectangle is in VRAM, halfword for halfword
at the five bits a channel the dump keeps.  The uniform and sleeve images of
set 1 are records 0 and 1, of set 2 records 4 and 5; the palettes are 2, 3 and
6, 7 (section 1.1).  So a kit whose two sets differ says, by which of its
records the console uploaded, which set it is wearing.

The controls, before an answer counts:

  **two dumps** -- VRAM dumped twice, a frame apart, gives the same matches,
      or the reading is the emulator's mood;
  **a record that matches everywhere** (a page of one colour) names nothing,
      and is reported as such instead of being counted.

**The answer is asserted, not only printed** (CORR-KITS-047): `--expect
TAG=SET` says which set a kit is worn in, and the run exits 1 unless the exact
player palette found is that set's alone and both pages come out nearer to it.
The goalkeeper palette is left out on purpose: in the match measured the
first team's goalkeeper wears the second set's (section 4.1).

Usage:
    python tools/kits/oracle.py --png <vram dump.png>        # offline, no emulator
    python tools/kits/oracle.py --slot N [--cue <disc.cue>]  # load slot N in the fork
    python tools/kits/oracle.py --png <dump> --expect 01=1 --expect 13=2
    python tools/kits/oracle.py --png <dump> --lines --flags

`--lines` counts, for the uniform and the sleeves of each set, the lines of
the page that are not flat (more than one distinct 15-bit value) and how many
of those are in VRAM halfword for halfword at the place `closest_sets` picks:
a match uploads part of a page, and a set is worn when its lines are there.
`--flags` names each kit by its flag -- the commonest colours of record 8
painted with record 9, black left out -- and says which records of set 1 are
byte for byte their set-2 twin (CORR-KITS-048).

The kit containers are read from `WE2002_LOOKS_IMAGE` (the Japanese track; the
105 are byte-identical on the English disc).  The cue is
`WE2002_LOOKS_DRIVE_IMAGE` unless given: the disc the state was saved on.
"""

from __future__ import annotations

import argparse
import os
import struct
import sys
import tempfile

KITS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(KITS_DIR)
for _sub in ("looks", "pes2"):
    _path = os.path.join(TOOLS_DIR, _sub)
    if _path not in sys.path:
        sys.path.insert(0, _path)

import atlas  # noqa: E402  (tools/looks)
import layout  # noqa: E402
import lzss  # noqa: E402  (tools/pes2)
import texture  # noqa: E402

IMAGE_VARIABLE = "WE2002_LOOKS_IMAGE"
DRIVE_VARIABLE = "WE2002_LOOKS_DRIVE_IMAGE"
VRAM_W, VRAM_H = 1024, 512
SETS = {0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2}
"""Record index -> the set it belongs to (section 1.1); 8-10 are shared."""
NAMES = ("uniform", "sleeves", "player palette", "goalkeeper palette",
         "uniform", "sleeves", "player palette", "goalkeeper palette",
         "flag", "flag palette", "referee")
MIN_DISTINCT = 4
"""A record with fewer distinct halfwords than this matches flat VRAM anywhere
and names nothing."""
SKIP = 77


def records_of(body: bytes) -> list:
    """The 11 records of a kit container, in file order."""
    return [r for t in texture.tables(body) for r in t.records]


def payload(body: bytes, record) -> tuple:
    """The halfwords one record uploads: a palette plain, a page out of LZSS,
    cut to the rectangle it declares."""
    if record.is_clut:
        raw = body[record.offset:record.offset + record.size]
    else:
        plain, _used = lzss.decompress(body, record.offset)
        raw = bytes(plain[:record.size])
    return struct.unpack("<%dH" % (len(raw) // 2), raw)


def five(value: int) -> int:
    """A BGR555 halfword with the STP bit dropped: what a PNG dump keeps."""
    return value & 0x7FFF


def vram_rows(path: str) -> list:
    """The dump as rows of 15-bit values, from the PNG `dump_vram` writes."""
    width, height, rows = atlas.read_png(path)
    if (width, height) != (VRAM_W, VRAM_H):
        raise ValueError("%s is %dx%d, not the %dx%d VRAM" % (path, width, height,
                                                             VRAM_W, VRAM_H))
    return [b"".join(struct.pack("<H", (p[0] >> 3) | (p[1] >> 3) << 5 | (p[2] >> 3) << 10)
                     for p in row) for row in rows]


def find(vram: list, record, words: tuple) -> list:
    """Every (x, y) where the whole rectangle of *record* is in *vram*."""
    w, h = record.w, record.h
    lines = [b"".join(struct.pack("<H", five(v)) for v in words[r * w:(r + 1) * w])
             for r in range(h)]
    out = []
    for y in range(VRAM_H - h + 1):
        row, at = vram[y], 0
        while True:
            at = row.find(lines[0], at)
            if at < 0:
                break
            if at % 2 == 0:
                x = at // 2
                if x + w <= VRAM_W and all(vram[y + r][at:at + 2 * w] == lines[r]
                                           for r in range(1, h)):
                    out.append((x, y))
            at += 1
    return out


KIT_AREA = (range(512, VRAM_W, 64), (256, 384))
"""Where a match puts the kit pages, measured 2026-10-04: one team at
x 576, the other at x 640, uniform at y 256 and sleeves at y 384.  Searched as
a grid of 64-halfword columns from x 512 so a third place would be found."""
IMAGE_SETS = ((0, 4), (1, 5))
"""(set-1 record, set-2 record) of the uniform and of the sleeves."""


def difference(vram: list, x: int, y: int, record, words: tuple) -> int:
    """Halfwords of *record* that differ from VRAM at (x, y)."""
    w, out = record.w, 0
    for r in range(record.h):
        row = struct.unpack("<%dH" % w, vram[y + r][2 * x:2 * (x + w)])
        out += sum(1 for a, b in zip(row, words[r * w:(r + 1) * w]) if a != five(b))
    return out


def closest_sets(vram: list, body: bytes) -> list:
    """[(name, (x, y), set-1 difference, set-2 difference)] for the uniform and
    the sleeves: the place in KIT_AREA where either set comes closest, and
    how far each set is from VRAM there.

    In a match the page is NOT uploaded whole -- parts of it hold something
    else -- so the exact search above finds no page; the closer set, by a
    margin, is what names it."""
    records = records_of(body)
    out = []
    for one, two in IMAGE_SETS:
        a, b = records[one], records[two]
        wa, wb = payload(body, a), payload(body, b)
        best = None
        for x in KIT_AREA[0]:
            for y in KIT_AREA[1]:
                if y + a.h > VRAM_H or x + a.w > VRAM_W or y != a.y:
                    continue
                da, db = difference(vram, x, y, a, wa), difference(vram, x, y, b, wb)
                if best is None or min(da, db) < min(best[2], best[3]):
                    best = (NAMES[one], (x, y), da, db)
        out.append(best)
    return out


def read_kits(image_path: str) -> dict:
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        return {tag: disc.read(layout.kit_path(tag)) for tag in layout.KIT_TAGS}


def search(vram: list, bodies: dict) -> list:
    """[(tag, record index, positions, flat, shared)] for every record found
    at least once; *flat* says the record has too few distinct halfwords to
    name anything, *shared* that it is byte for byte the same record of the
    kit's other set (index +-4), so finding it names neither set."""
    out = []
    for tag in sorted(bodies):
        body = bodies[tag]
        records = records_of(body)
        words_of = [payload(body, record) for record in records]
        for index, record in enumerate(records):
            words = words_of[index]
            flat = len(set(five(v) for v in words)) < MIN_DISTINCT
            twin = index + 4 if index < 4 else index - 4 if index in SETS else None
            shared = twin is not None and words_of[twin] == words
            at = find(vram, record, words)
            if at:
                out.append((tag, index, tuple(at), flat, shared))
    return out


def report(hits: list) -> dict:
    """Prints the hits and returns {tag: sorted sets} of the kits that name a
    set: an image or palette record of set 1 or 2 found, not flat, and not
    shared byte for byte with the other set of the same kit."""
    worn, unnamed = {}, set()
    for tag, index, at, flat, shared in hits:
        where = ", ".join("(%d,%d)" % p for p in at[:4]) + (" …" if len(at) > 4 else "")
        mark = ("flat, names nothing" if flat
                else "the same in both sets, names neither" if shared else "")
        print("  TEX_%s  record %2d %-18s set %s  at %s  %s"
              % (tag, index, NAMES[index], SETS.get(index, "-"), where, mark))
        if not flat and not shared and index in SETS:
            worn.setdefault(tag, set()).add(SETS[index])
        elif shared and index in SETS:
            unnamed.add(tag)
    for tag in sorted(worn):
        print("  TEX_%s: exact records of set %s" % (tag, " and ".join(str(s) for s in sorted(worn[tag]))))
    for tag in sorted(unnamed - set(worn)):
        print("  TEX_%s: its set records are found, but both sets are the same: no set named" % tag)
    return {tag: sorted(sets) for tag, sets in worn.items()}


def expectation_failures(vram: list, bodies: dict, hits: list, expect: dict) -> list:
    """Why the dump does not show kit *tag* in set *expect[tag]*, for every
    tag: the exact player palette found has to be that set's and no other,
    and the uniform and the sleeves have to come out nearer to it."""
    out = []
    for tag, want in sorted(expect.items()):
        if tag not in bodies:
            out.append("TEX_%s: not a kit container on this disc" % tag)
            continue
        found = sorted({SETS[index] for t, index, _at, flat, shared in hits
                        if t == tag and NAMES[index] == "player palette"
                        and not flat and not shared})
        if found != [want]:
            out.append("TEX_%s: exact player palette of set %s, expected set %d"
                       % (tag, " and ".join(map(str, found)) or "none", want))
        for name, _at, one, two in closest_sets(vram, bodies[tag]):
            nearer = 1 if one < two else 2 if two < one else None
            if nearer != want:
                out.append("TEX_%s: the %s page is nearer to %s, expected set %d"
                           % (tag, name, "set %d" % nearer if nearer else "neither", want))
    return out


def parse_expect(values) -> dict:
    """['01=1', '13=2'] -> {'01': 1, '13': 2}; anything else raises ValueError."""
    out = {}
    for value in values or ():
        tag, _, kit_set = value.partition("=")
        if not tag or kit_set not in ("1", "2"):
            raise ValueError("--expect wants TAG=1 or TAG=2, not %r" % value)
        out[tag.upper()] = int(kit_set)
    return out


def judge(vram: list, bodies: dict, hits: list, expect: dict) -> int:
    """Prints the verdict of --expect; 0 when it holds, 1 when it does not."""
    if not expect:
        return 0
    bad = expectation_failures(vram, bodies, hits, expect)
    for line in bad:
        print("  FAIL  %s" % line)
    if not bad:
        print("  ok    %s" % ", ".join("TEX_%s in set %d" % kv for kv in sorted(expect.items())))
    return 1 if bad else 0


def is_flat_line(line) -> bool:
    """A line of one 15-bit value: it matches flat VRAM and names nothing."""
    return len(set(five(v) for v in line)) <= 1


def report_lines(vram: list, bodies: dict, tags) -> dict:
    """{(tag, record): (not flat, exact)} for the uniform and the sleeves of
    both sets, at the place `closest_sets` picks for each page."""
    out = {}
    for tag in sorted(tags):
        body = bodies[tag]
        records = records_of(body)
        places = {name: at for name, at, _one, _two in closest_sets(vram, body)}
        for index in (0, 4, 1, 5):
            r = records[index]
            x, y = places[NAMES[index]]
            words = payload(body, r)
            not_flat = exact = 0
            for k in range(r.h):
                line = words[k * r.w:(k + 1) * r.w]
                if is_flat_line(line):
                    continue
                not_flat += 1
                there = struct.unpack("<%dH" % r.w, vram[y + k][2 * x:2 * (x + r.w)])
                exact += all(a == five(v) for a, v in zip(there, line))
            out[(tag, index)] = (not_flat, exact)
            print("  TEX_%s %-8s set %d at (%d,%d): %3d of %d lines not flat, %3d of them exact"
                  % (tag, NAMES[index], SETS[index], x, y, not_flat, r.h, exact))
    return out


def report_flags(image_path: str, bodies: dict, tags) -> None:
    """Each kit's flag colours and which set-1 records equal their set-2 twin."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    source = api.open_source(image_path)
    for tag in sorted(tags):
        picture = source.kit(tag).flat(8, 9)
        counts = {}
        for at in range(0, len(picture.rgba), 4):
            rgb = tuple(picture.rgba[at:at + 3])
            if rgb != (0, 0, 0):
                counts[rgb] = counts.get(rgb, 0) + 1
        total = sum(counts.values()) or 1
        top = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:3]
        print("  TEX_%s flag, black left out: %s"
              % (tag, ", ".join("%s %.0f %%" % (rgb, 100.0 * n / total) for rgb, n in top)))
        records = records_of(bodies[tag])
        same = ["%s 1==2 %s" % (NAMES[i], payload(bodies[tag], records[i])
                                == payload(bodies[tag], records[i + 4])) for i in range(4)]
        print("  TEX_%s %s" % (tag, ", ".join(same)))


def report_pages(vram: list, bodies: dict, tags) -> dict:
    """The pages of each kit in *tags*, set against set; {tag: {name: set}}."""
    out = {}
    for tag in sorted(tags):
        for name, at, one, two in closest_sets(vram, bodies[tag]):
            size = 64 * 128
            nearer = 1 if one < two else 2 if two < one else None
            out.setdefault(tag, {})[name] = nearer
            print("  TEX_%s %-8s at (%d,%d): set 1 differs in %4d of %d halfwords, set 2 in "
                  "%4d -- %s" % (tag, name, at[0], at[1], one, size, two,
                                 "set %d nearer" % nearer if nearer else "a tie"))
    return out


def dump_slot(slot: int, cue: str, out_dir: str) -> list:
    """Two VRAM dumps, a frame apart, of slot *slot* loaded in the fork."""
    import fork
    from oracle import OneSession, hide_window  # tools/looks

    paths = []
    pid, window, client = fork.launch(cue, verbose=True, match=fork.ANY_WINDOW)
    client = OneSession(client)
    try:
        hide_window(window)
        client.call("pause")
        client.call("load_state", slot=slot)
        for _ in range(30):
            client.call("frame_step")
        for n in range(2):
            client.call("frame_step")
            path = os.path.join(out_dir, "vram-%d.png" % n)
            if os.path.exists(path):
                os.remove(path)
            client.call("dump_vram", path=path, format="png")
            if not os.path.exists(path):
                raise RuntimeError("dump_vram wrote nothing at %s" % path)
            paths.append(path)
        shot = os.path.join(out_dir, "screen.png")
        client.call("take_screenshot", path=shot)
        print("  screen: %s" % shot)
    finally:
        fork.kill(verbose=False)
    return paths


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--png", help="a VRAM dump (1024x512 PNG) to search, no emulator")
    source.add_argument("--slot", type=int, help="load this save-state slot in the fork")
    parser.add_argument("--cue", help="the disc the state was saved on (default $%s)"
                        % DRIVE_VARIABLE)
    parser.add_argument("--out", default=os.path.join("work", "kits-oracle"),
                        help="where the dumps go")
    parser.add_argument("--lines", action="store_true",
                        help="count the exact page lines of each set of each kit found")
    parser.add_argument("--flags", action="store_true",
                        help="each kit found: its flag colours and which records both sets share")
    parser.add_argument("--expect", action="append", metavar="TAG=SET",
                        help="the set kit TAG has to be worn in; exits 1 if not (repeatable)")
    args = parser.parse_args(argv)
    try:
        expect = parse_expect(args.expect)
    except ValueError as exc:
        parser.error(str(exc))
    image = os.environ.get(IMAGE_VARIABLE)
    if not image:
        print("oracle: skipped -- %s is not set (the Japanese data track .bin)"
              % IMAGE_VARIABLE)
        return SKIP
    bodies = read_kits(image)
    print("  %d kit container(s) read from %s" % (len(bodies), image))
    if args.png:
        vram = vram_rows(args.png)
        hits = search(vram, bodies)
        report(hits)
        tags = {tag for tag, *_ in hits}
        report_pages(vram, bodies, tags)
        if args.lines:
            report_lines(vram, bodies, tags)
        if args.flags:
            report_flags(image, bodies, tags)
        return judge(vram, bodies, hits, expect)
    cue = args.cue or os.environ.get(DRIVE_VARIABLE)
    if not cue:
        print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
        return SKIP
    out = os.path.abspath(args.out)     # the fork wants absolute paths
    os.makedirs(out, exist_ok=True)
    paths = dump_slot(args.slot, cue, out)
    first, second = (search(vram_rows(p), bodies) for p in paths)
    if first != second:
        print("  FAIL  two dumps a frame apart give different matches: the reading "
              "is not stable")
        return 1
    print("  control: two dumps a frame apart give the same %d match(es)" % len(first))
    report(first)
    vram = vram_rows(paths[0])
    tags = {tag for tag, *_ in first}
    report_pages(vram, bodies, tags)
    if args.lines:
        report_lines(vram, bodies, tags)
    if args.flags:
        report_flags(image, bodies, tags)
    return judge(vram, bodies, first, expect)


if __name__ == "__main__":
    raise SystemExit(main())

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
    python tools/kits/oracle.py --sleeves 2|5 [--expect-sleeves none|drawn] [--plant-sleeves]
    python tools/kits/oracle.py --back 2 [--expect-back untouched] [--plant-back numbers]

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

`--sleeves SLOT` asks the open half of section 4.3 (KITS-TASK-39): which
primitive of the frame samples the sleeves image (576,384), where the long
sleeves and the captain's armband live.  The list the frame hands the GPU is
walked (`tools/looks/oracle.py`, the `--scenery` reader), every textured
polygon and sprite is placed in VRAM by its page, CLUT and texels, and those
that sample the kit page are counted per image and per zone of
`core/zones.py`.  When the sleeves image is drawn, every distinct quad of it
is looked for on the disc by its four texels, and placed in a section of
`MODEL.BIN`; the same quads one texel right are the search's control.  The
uniform image is the reading's control: the figure is drawn from it, so its
count has to be above 0.  `--expect-sleeves none|drawn` asserts the verdict
-- `drawn` meaning sleeves and armband primitives, every quad found in one
geometry file -- and `--plant-sleeves` moves every texel to the other image
and one texel right, which has to turn either verdict red.

`--back SLOT` asks section 4.7 (KITS-TASK-38): does the LOOKS SET fill the
torso gap -- (0,80) 20x24 of the player, (100,104) 20x24 of the goalkeeper,
index 0 on the disc -- with the back and the shirt number before it draws?
The state is loaded in the fork through `tools/looks/oracle.py`, the uniform
page at (576,256) is read back from VRAM twice, and each gap is compared pixel
for pixel with the same rectangle of the TEX the screen wears
(`layout.KIT_ON_SCREEN`).  The VRAM comes back as a PNG, so the STP bit of
each halfword is lost: an odd pixel keeps seven of its eight index bits, and
both sides are compared at those bits.  `--expect-back untouched|written`
asserts the verdict; `--plant-back numbers|tex` is the control -- the
numbers zone read in place of the gap, or another TEX as the disc side -- and
has to come out red.

In a match the area under the map is a grid of 20x24 back panels, one per
player on the pitch, and `--back SLOT --page X --tag TT --panels` reads it
(KITS-TASK-42): each panel is the figure's shirt back with the digits of the
numbers zone centred on row 7, one at x 7, two at x 3 and 11.  `--keeper-set`
takes the goalkeeper zones from the other set, `--plant-back panels` reads
every panel a row up, and `--blocks` / `--picture` show what differs.
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


# --- section 4.3: who samples the sleeves image ---------------------------

KIT_PAGE = (576, 256)
"""The VRAM page both kit images sit in on the LOOKS SET: the uniform at v
0-127, the sleeves at v 128-255 (section 1.1)."""
KIT_PAGES = tuple((x, 256) for x in KIT_AREA[0])
"""Every page a kit can sit in: a match puts the second team's beside the
first's -- (640,256) in slot 5 -- so the reading takes the whole kit area."""
KIT_CLUTS = tuple((0, y) for y in range(486, 494))
"""The kit palettes' VRAM rows: player and goalkeeper of the first team at
486 and 488, of the second at 487 and 489, and their set-2 twins four rows
down (`--slot 5`, Norway against Ecuador).  A kit page in a match also holds
4-bit graphics that are no kit, and the CLUT is what tells them apart."""
KIT_BITS = 8
STATES_DIR = os.path.join("work", "kits-states")
"""The master copies of this cycle's match states (slots 3 to 5)."""
IMAGE_HEIGHT = 128
TEXTURED_POLYGON_FAMILY = 1


def textured_samples(commands) -> list:
    """Every textured primitive of a command list as
    {"code", "page", "bits", "clut", "uv"}: the page and depth in VRAM, the
    CLUT's VRAM corner and the texel corners.  A polygon carries its own page
    and CLUT; a sprite takes the page of the draw mode in force."""
    import oracle as looks_oracle  # tools/looks

    out, mode = [], 0
    for words in commands:
        code = words[0] >> 24
        if code == looks_oracle.DRAW_MODE_SET:
            mode = words[0] & looks_oracle.DRAW_MODE_BITS
            continue
        if code >> 5 == TEXTURED_POLYGON_FAMILY and code & 4:
            corners = 4 if code & 8 else 3
            per = 3 if code & 16 else 2
            first = 2
            texels = [words[first + per * i] for i in range(corners)
                      if first + per * i < len(words)]
            if len(texels) != corners:
                continue
            page = (texels[1] >> 16) & looks_oracle.DRAW_MODE_BITS
            mode = page
            clut = texels[0] >> 16
            uv = [(t & 0xFF, (t >> 8) & 0xFF) for t in texels]
        elif code in looks_oracle.SPRITE_CODES:
            _words, fixed = looks_oracle.SPRITE_CODES[code]
            if len(words) < 3:
                continue
            u, v = words[2] & 0xFF, (words[2] >> 8) & 0xFF
            if fixed is None:
                if len(words) < 4:
                    continue
                w, h = words[3] & 0xFFFF, words[3] >> 16
            else:
                w = h = fixed
            page, clut = mode, words[2] >> 16
            uv = [(u, v), (u + w - 1, v), (u, v + h - 1), (u + w - 1, v + h - 1)]
        else:
            continue
        x, y, bits = looks_oracle.page_vram(page)
        out.append({"code": code, "page": (x, y), "bits": bits,
                    "clut": looks_oracle.clut_vram(clut), "uv": uv})
    return out


def kit_image_of(sample) -> str:
    """Which kit image a primitive samples: "uniform", "sleeves", "both" or
    None when its page is not the kit's."""
    if (sample["page"] not in KIT_PAGES or sample["bits"] != KIT_BITS
            or sample["clut"] not in KIT_CLUTS):
        return None
    halves = {"uniform" if v < IMAGE_HEIGHT else "sleeves" for _u, v in sample["uv"]}
    return halves.pop() if len(halves) == 1 else "both"


def work_point(u: int, v: int) -> tuple:
    """A texel of the kit page in work-bitmap pixels: the uniform on the left,
    the sleeves image on the right (core/flat.py)."""
    return (u, v) if v < IMAGE_HEIGHT else (IMAGE_HEIGHT + u, v - IMAGE_HEIGHT)


def sample_zones(sample) -> set:
    """The names of the zones the texel box of one primitive touches."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    points = [work_point(u, v) for u, v in sample["uv"]]
    x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
    x1, y1 = max(p[0] for p in points), max(p[1] for p in points)
    return {z.name for z in api.ZONES
            if z.x <= x1 and x0 < z.x + z.w and z.y <= y1 and y0 < z.y + z.h}


def sleeves_kind(names) -> str:
    """One primitive on the sleeves image, by the zones it touches, armband
    first: a quad of the armband also touches the captain's long-sleeve rows
    around it, and counts once (CORR-KITS-068)."""
    return ("armband" if any(n.startswith("armband") for n in names)
            else "long sleeve" if any(n.startswith("long sleeve") for n in names)
            else "other sleeves")


def sleeves_tally(samples) -> dict:
    """{"uniform", "sleeves", "both", "long sleeve", "armband", "other sleeves",
    "other page"} counts over the textured primitives of one frame; the three
    of the sleeves image are a partition of "sleeves" + "both"."""
    out = {"uniform": 0, "sleeves": 0, "both": 0, "long sleeve": 0,
           "armband": 0, "other sleeves": 0, "other page": 0}
    for one in samples:
        image = kit_image_of(one)
        if image is None:
            out["other page"] += 1
            continue
        out[image] += 1
        if image != "uniform":
            out[sleeves_kind(sample_zones(one))] += 1
    return out


SLEEVES_VERDICTS = ("none", "drawn")


def sleeves_judge(tally: dict, expect=None, found=None) -> list:
    """Failures of one frame's reading.  The control first: the figure is
    drawn from the uniform image, so a reading that finds nothing there has
    read nothing.  Then the verdict, when asked: `none` is no primitive on
    the sleeves image; `drawn` is long-sleeve and armband primitives, and
    every distinct quad of them in one disc file (*found*, from
    `geometry_sources`)."""
    out = []
    if tally["uniform"] == 0:
        out.append("no primitive samples the uniform image: the list read is not "
                   "the figure's")
    on_sleeves = tally["sleeves"] + tally["both"]
    parts = tally["long sleeve"] + tally["armband"] + tally["other sleeves"]
    if parts != on_sleeves:
        out.append("long sleeve %d + armband %d + other %d = %d, not the %d on the "
                   "sleeves image" % (tally["long sleeve"], tally["armband"],
                                      tally["other sleeves"], parts, on_sleeves))
    if expect == "none" and on_sleeves:
        out.append("%d primitive(s) sample the sleeves image, not none" % on_sleeves)
    if expect == "drawn":
        if not (tally["long sleeve"] and tally["armband"]):
            out.append("long sleeve %d, armband %d: not both drawn"
                       % (tally["long sleeve"], tally["armband"]))
        files = (found or {}).get("files", {})
        whole = [p for p, hits in files.items() if len(hits) == (found or {}).get("quads")]
        if not whole:
            out.append("no disc file holds every sleeves quad (%s)"
                       % (", ".join("%s %d" % (p, len(h)) for p, h in files.items())
                          or "none found"))
    return out


def planted(samples) -> list:
    """`--plant-sleeves`: every texel moved to the other image (v + 128) and
    one texel right -- the uniform read as sleeves, and quads no file holds."""
    return [dict(one, uv=[(u + 1, (v + IMAGE_HEIGHT) % (2 * IMAGE_HEIGHT))
                          for u, v in one["uv"]]) for one in samples]


def load_slot(game, slot: int, label: str) -> None:
    """Load *slot* in the fork: a LOOKS SET state through the `looks` oracle,
    which proves the screen; a match state from its master copy in
    `STATES_DIR`, restored into the emulator's slot first."""
    import shutil

    import oracle as looks_oracle  # tools/looks

    if slot in looks_oracle.SLOTS:
        looks_oracle.restore_state(slot, verbose=False)
        game.load_looks(slot, label=label)
        return
    master = os.path.join(STATES_DIR, os.path.basename(looks_oracle.emulator_state(slot)))
    if not os.path.isfile(master):
        raise RuntimeError("slot %d has no master copy at %s" % (slot, master))
    shutil.copyfile(master, looks_oracle.emulator_state(slot))
    game.pause()
    game.client.call("load_state", slot=slot)
    game.step(looks_oracle.LOAD_FRAMES)
    game.capture(label)


def texel_pattern(uv) -> bytes:
    """The regex a quad's four texel corners make in a model on the disc: the
    texture half of a POLY_FT4, u0 v0 CLUT u1 v1 page u2 v2 0 0 u3 v3 0 0
    (tools/looks/section.py), the CLUT and page left open because the game
    patches them per team."""
    import re

    (u0, v0), (u1, v1), (u2, v2), (u3, v3) = uv
    return (re.escape(bytes((u0, v0))) + b".." + re.escape(bytes((u1, v1))) + b".."
            + re.escape(bytes((u2, v2, 0, 0, u3, v3, 0, 0))))


def geometry_sources(samples, image_path: str) -> dict:
    """{disc file: [distinct sleeves quads whose texels it holds]}, over every
    Form 1 file of the disc, read raw; plus the count of distinct quads."""
    import re

    import iso_source

    quads = sorted({tuple(one["uv"]) for one in samples
                    if kit_image_of(one) in ("sleeves", "both") and len(one["uv"]) == 4})
    out = {}
    with iso_source.open_disc(image_path) as disc:
        image = disc._image  # noqa: SLF001 -- the listing, which Disc does not expose
        for path in sorted(image.files):
            if image.status(path) != "form1":
                continue
            data = image.read_file(path)
            hits = [q for q in quads
                    if re.search(texel_pattern(q), data, re.DOTALL)]
            if hits:
                out[path] = hits
    return {"quads": len(quads), "files": out}


def model_sections(samples, image_path: str) -> dict:
    """{section index of MODEL.BIN: {"long sleeve": n, "armband": n, "other": n}}
    for the distinct sleeves quads of a frame, matched by their four texels
    against the sections `tools/looks/section.py` reads."""
    import iso_source
    import section

    with iso_source.open_disc(image_path) as disc:
        data = disc.read(layout.MODEL)
    sections = section.scan(data, layout.MODEL_GEOMETRY_START).sections
    quads = {}
    for one in samples:
        if kit_image_of(one) in ("sleeves", "both") and len(one["uv"]) == 4:
            quads[tuple(one["uv"])] = one
    out = {}
    for uv, one in sorted(quads.items()):
        kind = sleeves_kind(sample_zones(one))
        kind = "other" if kind == "other sleeves" else kind
        where = [i for i, sec in enumerate(sections)
                 if any(tuple(p.texcoords) == uv for p in sec.primitives)]
        for index in where or [None]:
            out.setdefault(index, {"long sleeve": 0, "armband": 0, "other": 0})[kind] += 1
    return out


def shifted(samples) -> list:
    """The control of the disc search: every sample with u one texel right."""
    return [dict(one, uv=[(u + 1, v) for u, v in one["uv"]]) for one in samples]


def read_frame(slot: int, cue: str) -> list:
    """The textured primitives of the list one frame of *slot* hands the GPU,
    walked from the heads it submits."""
    import oracle as looks_oracle  # tools/looks

    with looks_oracle.Oracle(cue) as game:
        load_slot(game, slot, "sleeves-%d" % slot)
        game.step(looks_oracle.SCENERY_SETTLE)
        heads = looks_oracle.gpu_list_heads(game)
        first, size, step = layout.SCENERY_SWEEP
        ram = b"".join(game.read_ram(base, step, os.path.join(
            game.out_dir, "sleeves-%08x.bin" % base))
            for base in range(first, first + size, step))
        nodes = []
        for head in dict.fromkeys(heads[len(heads) // 2:]):
            nodes += looks_oracle.walk_gpu_list(ram, head)
    return textured_samples(looks_oracle.commands_of(nodes))


def run_sleeves(slot: int, cue: str, expect=None, plant=False) -> int:
    """`--sleeves SLOT`: section 4.3, on the LOOKS SET or in a match."""
    samples = read_frame(slot, cue)
    if plant:
        samples = planted(samples)
        print("  PLANT  every texel moved to the other image and one texel right")
    tally = sleeves_tally(samples)
    print("  %d textured primitive(s) in the frame's list" % len(samples))
    print("  kit pages: uniform image %d, sleeves image %d, both %d; other pages %d"
          % (tally["uniform"], tally["sleeves"], tally["both"], tally["other page"]))
    pages = {}
    for one in samples:
        image = kit_image_of(one)
        if image:
            pages.setdefault(one["page"], {}).setdefault(image, 0)
            pages[one["page"]][image] += 1
    for page in sorted(pages):
        print("    page (%d,%d): %s" % (page + (", ".join(
            "%s %d" % kv for kv in sorted(pages[page].items())),)))
    print("  of those on the sleeves image, each once (armband first): long sleeve %d, "
          "armband %d, other %d" % (tally["long sleeve"], tally["armband"],
                                    tally["other sleeves"]))
    zones = {}
    for one in samples:
        if kit_image_of(one) in ("sleeves", "both"):
            for name in sample_zones(one):
                zones[name] = zones.get(name, 0) + 1
    for name in sorted(zones, key=lambda n: -zones[n]):
        print("    zone %-48s %d primitive(s)" % (name, zones[name]))
    clut = {}
    for one in samples:
        if kit_image_of(one):
            key = (one["clut"], one["bits"])
            clut[key] = clut.get(key, 0) + 1
    print("  on the kit pages, by CLUT and depth: %s" % ", ".join(
        "(%d,%d) %d-bit x%d" % (k[0][0], k[0][1], k[1], n) for k, n in sorted(clut.items())))
    found = None
    if tally["sleeves"] or tally["both"]:
        found = geometry_sources(samples, os.environ[IMAGE_VARIABLE])
        print("  where the sleeves quads' texels are on the disc (%d distinct quad(s), "
              "every Form 1 file read raw):" % found["quads"])
        for path, hits in sorted(found["files"].items(), key=lambda kv: -len(kv[1])):
            print("    %-28s %d of %d" % (path, len(hits), found["quads"]))
        if not found["files"]:
            print("    in no file")
        control = geometry_sources(shifted(samples), os.environ[IMAGE_VARIABLE])
        print("  control, the same quads one texel right: found in %s"
              % (", ".join("%s %d" % (p, len(h)) for p, h in sorted(control["files"].items()))
                 or "no file"))
        print("  in the sections of %s (quads by zone):" % layout.MODEL)
        for index, kinds in sorted(model_sections(samples, os.environ[IMAGE_VARIABLE]).items(),
                                   key=lambda kv: (kv[0] is None, kv[0] or 0)):
            print("    section %-4s long sleeve %d, armband %d, other %d"
                  % ("none" if index is None else index, kinds["long sleeve"],
                     kinds["armband"], kinds["other"]))
    failures = sleeves_judge(tally, expect, found)
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        print("  ok    %d primitive(s) sample the uniform image%s"
              % (tally["uniform"], "; sleeves %s" % expect if expect else ", no verdict asked"))
    return 1 if failures else 0


# --- section 4.7: the back and the number ---------------------------------

UNIFORM_RECORD = 0
UNIFORM_SET2 = 4
"""The set-2 uniform page; records 0 and 4 share the rectangle (section 1.1)."""
"""The set-1 uniform page, (576,256) 64x128 halfwords = 128x128 pixels."""
BACK_PLANTS = ("numbers", "tex", "panels")
BLOCKS_SHOWN = 24
BACK_VERDICTS = ("untouched", "written")
BACK_SOURCE = "shirt back"
"""The zone the measured copy comes from (section 4.7)."""
PLANT_TAG = "00"
"""The TEX the `tex` plant compares against instead of the one on screen."""


def back_rects() -> list:
    """(name, x, y, w, h, figure) of each torso gap, in work-bitmap pixels, from the
    zones module -- the one place the rectangles live."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    out = []
    for gap in api.GAPS:
        if gap.name.startswith("torso"):
            who = "player" if gap.figure == 0 else "goalkeeper"
            out.append((who, gap.x, gap.y, gap.w, gap.h, gap.figure))
    return out


def numbers_rect() -> tuple:
    """(x, y, w, h) of the "numbers 0-9" zone, the candidate source."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    zone = next(z for z in api.ZONES if z.name == "numbers 0-9")
    return (zone.x, zone.y, zone.w, zone.h)


def pixel_index(words, width: int, x: int, y: int) -> int:
    """The 8-bit index of pixel (x, y) of an 8 bpp page held as 15-bit
    halfwords, *width* halfwords a row: the low byte for an even pixel, the
    high byte -- seven bits, the STP bit lost -- for an odd one."""
    word = words[y * width + x // 2] & 0x7FFF
    return word & 0xFF if x % 2 == 0 else word >> 8


def back_count(vram_words, disc_words, width: int, rect, disc_rect=None) -> dict:
    """One gap: pixels whose index is not 0 in VRAM and on the disc, and
    pixels where the two differ.  *disc_rect* reads the disc elsewhere, which
    only the plant does."""
    x0, y0, w, h = rect
    dx, dy = (disc_rect or rect)[:2]
    vram_set = disc_set = differ = 0
    for y in range(h):
        for x in range(w):
            v = pixel_index(vram_words, width, x0 + x, y0 + y)
            d = pixel_index(disc_words, width, dx + x, dy + y)
            vram_set += v != 0
            disc_set += d != 0
            differ += v != d
    return {"pixels": w * h, "vram": vram_set, "disc": disc_set, "differ": differ}


def back_indices(words, width: int, rect) -> list:
    """The rows of indices of one rectangle of an 8 bpp page."""
    x0, y0, w, h = rect
    return [[pixel_index(words, width, x0 + x, y0 + y) for x in range(w)] for y in range(h)]


def back_sources(words, width: int, height: int, rect) -> list:
    """Every other place of the page whose pixels equal *rect*'s, straight
    or mirrored left to right: (x, y, "straight"|"mirrored").  Compared at
    seven bits a pixel, the most both parities keep."""
    x0, y0, w, h = rect
    want = [[v & 0x7F for v in row] for row in back_indices(words, width, rect)]
    mirrored = [row[::-1] for row in want]
    out = []
    for y in range(height - h + 1):
        for x in range(2 * width - w + 1):
            if (x, y) == (x0, y0):
                continue
            got = [[v & 0x7F for v in row] for row in back_indices(words, width, (x, y, w, h))]
            if got == want:
                out.append((x, y, "straight"))
            elif got == mirrored:
                out.append((x, y, "mirrored"))
    return out


def source_zone(found, w: int, h: int, figure: int):
    """The name of the zone of *figure* that wholly holds the first straight
    copy in *found*, or None."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    for x, y, how in found:
        if how != "straight":
            continue
        for z in api.ZONES:
            if (z.figure == figure and z.x <= x and x + w <= z.x + z.w
                    and z.y <= y and y + h <= z.y + z.h):
                return z.name
    return None


def back_judge(counts: dict, whole_differ: int, expect=None) -> list:
    """Failures of one slot's reading: the disc side has to be the page the
    console holds outside the gaps, and the verdict, when asked, has to hold
    -- `written` meaning a straight copy of the figure's own shirt back."""
    out = []
    if whole_differ:
        out.append("the disc page differs from VRAM in %d halfword(s) outside the rewritten rectangles, "
                   "so it is not the page the screen holds" % whole_differ)
    for name, c in counts.items():
        verdict = "written" if c["differ"] else "untouched"
        if expect and verdict != expect:
            out.append("%s gap: %s, not %s (%d of %d pixels differ from the disc)"
                       % (name, verdict, expect, c["differ"], c["pixels"]))
        elif expect == "written" and c.get("source") != BACK_SOURCE:
            out.append("%s gap: written, but not a copy of the %s (the copy found sits in %s)"
                       % (name, BACK_SOURCE, c.get("source") or "no zone of its figure"))
    return out


def outside_differ(vram_words, disc_words, width: int, height: int, rects) -> int:
    """Halfwords outside every gap where VRAM and the disc page differ."""
    inside = set()
    for _name, x0, y0, w, h, _figure in rects:
        for y in range(y0, y0 + h):
            for x in range(x0 // 2, (x0 + w + 1) // 2):
                inside.add((x, y))
    return sum(1 for y in range(height) for x in range(width)
               if (x, y) not in inside
               and (vram_words[y * width + x] & 0x7FFF) != (disc_words[y * width + x] & 0x7FFF))


def read_back(slot: int, cue: str, page_x=None) -> list:
    """The uniform image's VRAM rectangle as 15-bit halfwords, read twice --
    each after its own `load_state` -- from *slot*, at the kit page *page_x*
    (default: where the record declares it, (576,256))."""
    import oracle as looks_oracle  # tools/looks

    record = records_of(_screen_body())[UNIFORM_RECORD]
    x = record.x if page_x is None else page_x
    reads = []
    with looks_oracle.Oracle(cue) as game:
        for n in range(2):
            load_slot(game, slot, "back-%d-%d" % (slot, n))
            rows = looks_oracle.vram_region(game, x, record.y, record.w, record.h)
            reads.append([(p[0] >> 3) | (p[1] >> 3) << 5 | (p[2] >> 3) << 10
                          for row in rows for p in row])
    return reads


_BODIES = {}


def _body(tag: str) -> bytes:
    if tag not in _BODIES:
        _BODIES.update(read_kits(os.environ[IMAGE_VARIABLE]))
    return _BODIES[tag]


def _screen_body() -> bytes:
    return _body(layout.KIT_ON_SCREEN)


def diff_blocks(vram_words, disc_words, width: int, height: int) -> list:
    """The pixels where VRAM and the disc page differ (at seven bits a
    pixel), grouped into 8-connected blocks: [(x0, y0, x1, y1, pixels)],
    biggest first, in work-bitmap pixels of the uniform image."""
    differ = {(x, y) for y in range(height) for x in range(2 * width)
              if (pixel_index(vram_words, width, x, y) & 0x7F)
              != (pixel_index(disc_words, width, x, y) & 0x7F)}
    blocks = []
    while differ:
        todo = [differ.pop()]
        seen = list(todo)
        while todo:
            x, y = todo.pop()
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    n = (x + dx, y + dy)
                    if n in differ:
                        differ.remove(n)
                        todo.append(n)
                        seen.append(n)
        xs = [p[0] for p in seen]
        ys = [p[1] for p in seen]
        blocks.append((min(xs), min(ys), max(xs), max(ys), len(seen)))
    return sorted(blocks, key=lambda b: -b[4])


def block_zones(block) -> list:
    """The zones of the map a block's rectangle touches."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    x0, y0, x1, y1, _n = block
    return [z.name + ("" if z.figure is None else " (%s)" % ("player", "goalkeeper")[z.figure])
            for z in api.ZONES
            if z.x <= x1 and x0 < z.x + z.w and z.y <= y1 and y0 < z.y + z.h]


# --- section 4.7 in a match: the back panels ------------------------------

PANEL_W, PANEL_H = 20, 24
"""A back panel: the torso gap's size, (0,80) 20x24 (core/zones.py GAPS)."""
GLYPH_W = 6
"""The "numbers 0-9" zone is 60x12: ten glyphs of 6x12, 0 to 9 left to right."""
PANEL_TOP = 80
"""The first row of the panels, which is the torso gap's (core/zones.py)."""
DIGIT_Y = 7
DIGIT_STEP = 8
"""Where the digits fall in a panel, measured in slot 5: row 7, one digit at
x 7, two at x 3 and 11 -- centred, a glyph every 8 pixels."""


def digit_xs(count: int) -> list:
    """The x of each of *count* digits in a panel, centred at DIGIT_STEP."""
    first = (PANEL_W - (GLYPH_W + DIGIT_STEP * (count - 1))) // 2
    return [first + DIGIT_STEP * i for i in range(count)]


def panels_judge(panels: list) -> list:
    """Failures of the back-panel rule: every panel holds a number, every
    pixel of it is the shirt back or a digit, and the digits sit where
    `digit_xs` puts them."""
    out = []
    for one in panels:
        figure, cx, cy = one["cell"]
        where = "panel (%d,%d)" % (cx, cy)
        if one["number"] is None:
            out.append("%s holds no digit" % where)
            continue
        if one["unexplained"]:
            out.append("%s: %d pixel(s) are neither the shirt back nor a digit"
                       % (where, one["unexplained"]))
        at = [(x, y) for x, y, _d in one["digits"]]
        want = [(x, DIGIT_Y) for x in digit_xs(len(at))]
        if at != want:
            out.append("%s: digits at %s, the rule puts them at %s" % (where, at, want))
    return out


def panel_cells() -> list:
    """(figure, x, y) of every 20x24 cell under the map: the two torso gaps
    start the two rows, and the rows run on to the right in steps of 20."""
    out = []
    for _name, x, y, w, h, figure in back_rects():
        if figure == 0:
            for row in range(2):
                for k in range(5):
                    out.append((0, x + k * w, y + row * h))
        else:
            out.append((1, x, y))
    return out


def glyphs(words, width: int) -> tuple:
    """The ten digit glyphs of the numbers zone as rows of 7-bit indices, and
    the zone's background index (its commonest value)."""
    zx, zy, zw, zh = numbers_rect()
    rows = back_indices(words, width, (zx, zy, zw, zh))
    tally = {}
    for row in rows:
        for v in row:
            tally[v & 0x7F] = tally.get(v & 0x7F, 0) + 1
    ground = max(tally, key=tally.get)
    out = [[[v & 0x7F for v in row[d * GLYPH_W:(d + 1) * GLYPH_W]] for row in rows]
           for d in range(zw // GLYPH_W)]
    return out, ground


def read_panel(words, width: int, cell, back, glyph_set, ground) -> dict:
    """One panel against the rule: the figure's shirt back underneath, digits
    of the numbers zone on top.  Says which digit sits where, how many pixels
    neither explains."""
    _figure, cx, cy = cell
    panel = [[v & 0x7F for v in row]
             for row in back_indices(words, width, (cx, cy, PANEL_W, PANEL_H))]
    found = []
    for gy in range(PANEL_H - len(glyph_set[0]) + 1):
        for gx in range(PANEL_W - GLYPH_W + 1):
            for digit, glyph in enumerate(glyph_set):
                ink = [(x, y) for y, row in enumerate(glyph) for x, v in enumerate(row)
                       if v != ground]
                if ink and all(panel[gy + y][gx + x] == glyph[y][x] for x, y in ink):
                    found.append((gx, gy, digit, len(ink)))
    # a narrow glyph (the 1) also fits inside wider ones: keep the placements
    # whose ink no other placement covers more of
    found.sort(key=lambda f: -f[3])
    kept, covered = [], set()
    for gx, gy, digit, n in found:
        ink = {(gx + x, gy + y) for y, row in enumerate(glyph_set[digit])
               for x, v in enumerate(row) if v != ground}
        if ink & covered:
            continue
        kept.append((gx, gy, digit))
        covered |= ink
    kept.sort()
    unexplained = sum(1 for y in range(PANEL_H) for x in range(PANEL_W)
                      if (x, y) not in covered and panel[y][x] != back[y][x])
    return {"cell": cell, "digits": kept, "unexplained": unexplained,
            "number": int("".join(str(d) for _x, _y, d in kept)) if kept else None}


def read_panels(words, width: int, shift: int = 0) -> list:
    """Every back panel of a match page, read against the rule; *shift*
    moves every cell that many rows (negative is up), which only the plant does."""
    glyph_set, ground = glyphs(words, width)
    out = []
    for figure, x, y in panel_cells():
        cell = (figure, x, y + shift)
        sx = 44 if cell[0] == 0 else 108
        back = [[v & 0x7F for v in row]
                for row in back_indices(words, width, (sx, 6, PANEL_W, PANEL_H))]
        out.append(read_panel(words, width, cell, back, glyph_set, ground))
    return out


PLAYER_PALETTE = {1: 2, 2: 6}
"""Set -> the record of its player palette (section 1.1)."""


def save_picture(path: str, words, width: int, height: int, body: bytes, kit_set: int) -> None:
    """The 8 bpp image held in *words*, as a PNG painted with the kit's
    player palette -- to look at, not to measure: odd pixels lose bit 7."""
    import atlas

    raw = payload(body, records_of(body)[PLAYER_PALETTE[kit_set]])
    colours = [((v & 0x1F) << 3, (v >> 5 & 0x1F) << 3, (v >> 10 & 0x1F) << 3, 255)
               for v in raw]
    indices = bytes(pixel_index(words, width, x, y)
                    for y in range(height) for x in range(2 * width))
    atlas.write_png(path, 2 * width, height, indices, colours)


def compose_sets(player_words, keeper_words, width: int, height: int) -> list:
    """One page whose goalkeeper zones (core/zones.py) come from
    *keeper_words* and every other pixel from *player_words*: a match can dress
    the goalkeeper in the other set (section 4.1)."""
    if KITS_DIR not in sys.path:
        sys.path.insert(0, KITS_DIR)
    from core import api

    out = list(player_words)
    for y in range(height):
        for x in range(2 * width):
            zone = api.zone_at(x, y)
            if zone is not None and zone.figure == 1:
                at = y * width + x // 2
                mask = 0x00FF if x % 2 == 0 else 0xFF00
                out[at] = (out[at] & ~mask) | (keeper_words[at] & mask)
    return out


def run_back(slot: int, cue: str, expect=None, plant=None, grid=False,
             page_x=None, tag=None, kit_set=1, blocks=False, picture=None,
             panels=False, keeper_set=None) -> int:
    """`--back SLOT`: section 4.7, on the LOOKS SET or, with `--page`,
    `--tag` and `--set`, at either kit page of a match."""
    if tag is None:
        tag = layout.KIT_ON_SCREEN
    if plant == "tex":
        tag = PLANT_TAG
    record = records_of(_screen_body())[UNIFORM_RECORD]
    image = UNIFORM_RECORD if kit_set == 1 else UNIFORM_SET2
    disc = [five(v) for v in payload(_body(tag), records_of(_body(tag))[image])]
    if keeper_set and keeper_set != kit_set:
        other = UNIFORM_RECORD if keeper_set == 1 else UNIFORM_SET2
        disc = compose_sets(disc, [five(v) for v in payload(_body(tag),
                                                             records_of(_body(tag))[other])],
                            record.w, record.h)
    first, second = read_back(slot, cue, page_x)
    if page_x is not None:
        print("  page (%d,%d) against TEX_%s set %d%s"
              % (page_x, record.y, tag, kit_set,
                 ", goalkeeper zones from set %d" % keeper_set
                 if keeper_set and keeper_set != kit_set else ""))
    if first != second:
        print("  FAIL  the uniform page read twice, each after its own load_state, "
              "differs: nothing below is measured")
        return 1
    print("  control: the uniform page (%d,%d) %dx%d read twice, identical"
          % (record.x if page_x is None else page_x, record.y, record.w, record.h))
    rects = back_rects()
    skip = rects + ([("panel", x, y, PANEL_W, PANEL_H, f) for f, x, y in panel_cells()]
                    if panels else [])
    whole = outside_differ(first, disc, record.w, record.h, skip)
    print("  disc side TEX_%s: %d halfword(s) of %d differ from VRAM outside the %s"
          % (tag, whole, record.w * record.h, "panels" if panels else "gaps"))
    counts = {}
    numbers = numbers_rect()
    for name, x, y, w, h, figure in rects:
        at = (numbers[0], numbers[1], w, min(h, numbers[3])) if plant == "numbers" else (x, y, w, h)
        disc_at = (x, y) if plant == "numbers" else None
        c = back_count(first, disc, record.w, at, disc_at)
        counts[name] = c
        verdict = "written" if c["differ"] else "untouched"
        print("  %-10s gap (%d,%d) %dx%d%s: index != 0 in %d of %d pixel(s) in VRAM, %d on "
              "the disc; %d differ -- %s"
              % (name, x, y, w, h,
                 " [read at the numbers zone (%d,%d)]" % at[:2] if plant == "numbers" else "",
                 c["vram"], c["pixels"], c["disc"], c["differ"], verdict))
        rows = back_indices(first, record.w, at)
        tally = {}
        for row in rows:
            for v in row:
                tally[v] = tally.get(v, 0) + 1
        print("             VRAM indices: %s" % ", ".join(
            "%d x%d" % (v, n) for v, n in sorted(tally.items(), key=lambda t: -t[1])[:8]))
        found = back_sources(first, record.w, record.h, at)
        c["source"] = source_zone(found, at[2], at[3], figure)
        print("             the same pixels elsewhere in the page: %s -- %s"
              % (", ".join("(%d,%d) %s" % f for f in found) or "nowhere",
                 "inside the %s" % c["source"] if c["source"] else "inside no zone of its figure"))
        if grid:
            for row in rows:
                print("             " + " ".join("%3d" % v for v in row))
    if blocks:
        both = {n: [five(v) for v in payload(_body(tag), records_of(_body(tag))[r])]
                for n, r in ((1, UNIFORM_RECORD), (2, UNIFORM_SET2))}
        for label, x0, x1 in (("player half", 0, 64), ("goalkeeper half", 64, 128)):
            counts_by_set = []
            for n in (1, 2):
                counts_by_set.append(sum(
                    1 for y in range(PANEL_TOP) for x in range(x0, x1)
                    if (pixel_index(first, record.w, x, y) & 0x7F)
                    != (pixel_index(both[n], record.w, x, y) & 0x7F)))
            print("  %s, rows 0-%d: %d pixel(s) differ from set 1, %d from set 2"
                  % ((label, PANEL_TOP - 1) + tuple(counts_by_set)))
        found = diff_blocks(first, disc, record.w, record.h)
        print("  %d block(s) of pixels differ from the disc in the whole image:" % len(found))
        for block in found[:BLOCKS_SHOWN]:
            print("    (%3d,%3d)-(%3d,%3d) %4d pixel(s): %s"
                  % (block + (", ".join(block_zones(block)) or "no zone",)))
    panel_failures = []
    if panels:
        print("  back panels, each against the figure's shirt back (44,6)/(108,6) 20x24 "
              "with digits of the numbers zone on top:")
        shift = -1 if plant == "panels" else 0
        if shift:
            print("  PLANT  every panel read one row up")
        read = read_panels(first, record.w, shift)
        for one in read:
            figure, cx, cy = one["cell"]
            print("    %-10s panel (%3d,%3d): number %-4s digits %s; %d pixel(s) the rule "
                  "does not explain"
                  % (("player", "goalkeeper")[figure], cx, cy, one["number"],
                     " ".join("%d at (%d,%d)" % (d, x, y) for x, y, d in one["digits"]) or "none",
                     one["unexplained"]))
        panel_failures = panels_judge(read)
    if picture:
        save_picture(picture, first, record.w, record.h, _body(tag), kit_set)
        print("  picture: %s (the VRAM image painted with TEX_%s's set-%d player palette)"
              % (picture, tag, kit_set))
    failures = back_judge(counts, whole, None if panels else expect) + panel_failures
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        print("  ok    %s" % ("every panel holds the shirt back and its centred number"
                                if panels else "every gap %s" % expect if expect
                                else "read, no verdict asked"))
    return 1 if failures else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--png", help="a VRAM dump (1024x512 PNG) to search, no emulator")
    source.add_argument("--slot", type=int, help="load this save-state slot in the fork")
    source.add_argument("--sleeves", type=int, metavar="SLOT",
                        help="section 4.3: which primitives of this slot's frame sample "
                             "the sleeves image")
    source.add_argument("--back", type=int, metavar="SLOT",
                        help="section 4.7: does the LOOKS SET of this slot fill the torso gaps")
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
    parser.add_argument("--expect-back", choices=BACK_VERDICTS,
                        help="with --back: the verdict every gap has to give; exits 1 if not")
    parser.add_argument("--plant-back", choices=BACK_PLANTS,
                        help="with --back: the control -- read the numbers zone, or another TEX")
    parser.add_argument("--expect-sleeves", choices=SLEEVES_VERDICTS,
                        help="with --sleeves: the verdict the frame has to give; exits 1 if not")
    parser.add_argument("--plant-sleeves", action="store_true",
                        help="with --sleeves: the control -- every texel to the other image, "
                             "one texel right")
    parser.add_argument("--page", type=int, metavar="X",
                        help="with --back: the kit page's VRAM x (576 or 640 in a match)")
    parser.add_argument("--tag", help="with --back: the TEX worn at that page (default the "
                                      "LOOKS SET's)")
    parser.add_argument("--set", type=int, choices=(1, 2), default=1,
                        help="with --back: which set of the TEX the page is compared with")
    parser.add_argument("--keeper-set", type=int, choices=(1, 2),
                        help="with --back: the set the goalkeeper zones are compared with")
    parser.add_argument("--blocks", action="store_true",
                        help="with --back: every block of pixels that differs from the disc")
    parser.add_argument("--panels", action="store_true",
                        help="with --back: read every back panel under the map (a match)")
    parser.add_argument("--picture", metavar="PNG",
                        help="with --back: write the VRAM image painted with the kit's palette")
    parser.add_argument("--grid", action="store_true",
                        help="with --back: print each gap's indices, row by row")
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
    if args.sleeves is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_sleeves(args.sleeves, cue, args.expect_sleeves, args.plant_sleeves)
    if args.back is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_back(args.back, cue, args.expect_back, args.plant_back, args.grid,
                        args.page, args.tag, args.set, args.blocks, args.picture,
                        args.panels, args.keeper_set)
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

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
    python tools/kits/oracle.py --match-pose 5 [--frame-json <capture>] [--plant-pose]
    python tools/kits/oracle.py --match-pose 5 --write|--check     # core/match_pose.json
    python tools/kits/oracle.py --match-silhouette 5 --tag 14 [--plant-silhouette]
                                [--pair-by indices|corners]
    python tools/kits/oracle.py --edt-arms [--plant-edt-arms]      # disc only
    python tools/kits/oracle.py --keeper-armband 7 [--frame-json <stops>] [--plant-keeper-armband]
    python tools/kits/oracle.py --replay-idle 9                    # frames the paused replay lasts
    python tools/kits/oracle.py --replay 9 [--rotate R1|L1] [--frame-json <capture>] [--plant-replay]
    python tools/kits/oracle.py --replay-confront 9                # the 3D tab against the capture

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

`--match-pose SLOT` (KITS-TASK-45) stops at every per-piece matrix load and
every list handed to the GPU in one run, and proves the matrices on the list
they were loaded for: each MODEL.BIN vertex through its piece's matrix and the
GTE projection lands on the frame's corner of the same texel, under
`POSE_LIMIT`.  The pose of a captain and of an outfield player goes to
`work/kits-pose/`; `--plant-pose` drops the pointer lag and has to fail.
`--write` versions the pose as `core/match_pose.json`, the file the 3D tab
draws the match figure from, and `--check` fails when that file is not what
the run measures.  `--match-silhouette SLOT --tag TT` (KITS-TASK-47) draws
that figure through `api.match_figure` in the game camera's view and compares
its silhouette with the player the game drew, by intersection over union
against `SILHOUETTE_LIMIT`; `--plant-silhouette` draws every piece with the
body's matrix and has to fail.

In a match the area under the map is a grid of 20x24 back panels, one per
player on the pitch, and `--back SLOT --page X --tag TT --panels` reads it
(KITS-TASK-42): each panel is the figure's shirt back with the digits of the
numbers zone centred on row 7, one at x 7, two at x 3 and 11.  `--keeper-set`
takes the goalkeeper zones from the other set, `--plant-back panels` reads
every panel a row up, and `--blocks` / `--picture` show what differs.

`--edt-arms` (KITS-AJUSTES-3D.md G3, K3D-TASK-07) needs no emulator: it lays
each sleeve and armband section of MODEL.BIN on the EDT_MOD.BIN arm pieces and
asserts `ARM_PIECES` -- the piece each one stands in for, in that piece's frame
within `FRAME_SLACK` -- and that both figures give each arm piece the same
pose by name.  That last one holds by construction: `scene.pose` poses a
section by its `pieces.py` name, and both figures' arm sections share the
names, so the run cannot print "posed apart" (CORR-K3D-012).
`--plant-edt-arms` moves every MODEL.BIN arm out of its frame, keeping its
nearest piece, and has to fail on the frame alone.
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
"""The master copies of the game states that are not the LOOKS SET's: the
match slots 3 to 7, the EDIT PL. NUM screen in slot 8 (K3D-TASK-16) and the
paused replays of slots 9 and 10 (K3D-TASK-17)."""
IMAGE_HEIGHT = 128
TEXTURED_POLYGON_FAMILY = 1


def textured_samples(commands) -> list:
    """Every textured primitive of a command list as
    {"code", "page", "bits", "clut", "uv", "xy", "rgb"}: the page and depth in
    VRAM, the CLUT's VRAM corner, the texel and screen corners, and a polygon's
    colour at each corner -- one colour four times when it is flat, its own per
    corner when it is shaded (G8).  A polygon carries its own page and CLUT; a
    sprite takes the page of the draw mode in force."""
    import oracle as looks_oracle  # tools/looks

    out, mode = [], 0
    for words in commands:
        code = words[0] >> 24
        rgb = None
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
            xy = [looks_oracle._signed_vertex(words[1 + per * i]) for i in range(corners)]
            rgb = [looks_oracle._packet_colour(words[per * i] if code & 16 else words[0])
                   for i in range(corners)]
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
            sx, sy = looks_oracle._signed_vertex(words[1])
            xy = [(sx, sy), (sx + w - 1, sy), (sx, sy + h - 1), (sx + w - 1, sy + h - 1)]
        else:
            continue
        x, y, bits = looks_oracle.page_vram(page)
        out.append({"code": code, "page": (x, y), "bits": bits,
                    "clut": looks_oracle.clut_vram(clut), "uv": uv, "xy": xy, "rgb": rgb})
    return out


DRAW_OFFSET = 0xE5
"""The GP0 command that sets the drawing offset: every polygon's vertices are
relative to it, so the frame buffer pixel of a screen corner is offset + xy."""


def draw_offset(commands):
    """(x, y) of the last drawing offset a command list sets, or None; both
    halves are signed 11-bit."""
    found = None
    for words in commands:
        if words and words[0] >> 24 == DRAW_OFFSET:
            x, y = words[0] & 0x7FF, (words[0] >> 11) & 0x7FF
            found = (x - 0x800 if x & 0x400 else x, y - 0x800 if y & 0x400 else y)
    return found


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


# --- section 4.3: where MODEL.BIN's sleeves and armband attach -------------

ATTACH_DIR = os.path.join("work", "kits-oracle")
ARMBAND_SECTION = 93
LONG_SLEEVE_SECTIONS = tuple(range(95, 103))
"""The MODEL.BIN sections `--sleeves 5` found (KITS-TASK-39)."""
MIN_FIT_POINTS = 6
"""A projective camera has 11 unknowns, two equations a point."""
REPLACED_SECTION = 97
"""The long-sleeve section the armband takes the place of: in slot 5 both
captains draw 2 7 8 9 10 93 95 96 98 and every other outfield player
2 7 8 9 10 95 96 97 98."""
PLANT_ARMBAND = 94
"""`--plant-attach` names this section the armband instead of 93."""


def model_index(image_path: str) -> dict:
    """{(file, section): Section} and {texel corners: [(file, section, prim)]}
    over EDT_MOD.BIN and MODEL.BIN, read by `tools/looks/section.py`."""
    import iso_source
    import section

    sections, by_uv = {}, {}
    with iso_source.open_disc(image_path) as disc:
        for name in (layout.EDT_MOD, layout.MODEL):
            data = disc.read(name)
            start = (layout.MODEL_GEOMETRY_START if name == layout.MODEL
                     else layout.geometry_start(data))
            for i, sec in enumerate(section.scan(data, start).sections):
                sections[(name, i)] = sec
                for k, prim in enumerate(sec.primitives):
                    by_uv.setdefault(tuple(tuple(t) for t in prim.texcoords), []).append(
                        (name, i, k))
    return {"sections": sections, "by_uv": by_uv}


def is_figure(sample) -> bool:
    """A primitive of a kit: 8 bits, a kit CLUT, a kit page."""
    return kit_image_of(sample) is not None


def players(samples, gap: int = 2) -> list:
    """The figure primitives grouped into players: two primitives are one
    player's when their screen boxes come within *gap* pixels, transitively.
    Players far apart on the pitch never touch; two that overlap merge, and
    the fit below says so instead of hiding it."""
    figure = [one for one in samples if is_figure(one)]
    boxes = []
    for one in figure:
        xs = [p[0] for p in one["xy"]]
        ys = [p[1] for p in one["xy"]]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    parent = list(range(len(figure)))

    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    for i, a in enumerate(boxes):
        for j in range(i + 1, len(boxes)):
            b = boxes[j]
            if a[0] - gap <= b[2] and b[0] - gap <= a[2] and a[1] - gap <= b[3] and b[1] - gap <= a[3]:
                parent[root(i)] = root(j)
    groups = {}
    for i, one in enumerate(figure):
        groups.setdefault(root(i), []).append(one)
    return sorted(groups.values(), key=len, reverse=True)


def solve(matrix, vector):
    """Least squares by the normal equations and Gauss-Jordan; None when the
    system is singular."""
    n = len(matrix[0])
    ata = [[sum(row[i] * row[j] for row in matrix) for j in range(n)] for i in range(n)]
    atb = [sum(row[i] * b for row, b in zip(matrix, vector)) for i in range(n)]
    m = [ata[i] + [atb[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(m[r][col]))
        if abs(m[pivot][col]) < 1e-9:
            return None
        m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        m[col] = [v / div for v in m[col]]
        for r in range(n):
            if r != col and m[r][col]:
                f = m[r][col]
                m[r] = [a - f * b for a, b in zip(m[r], m[col])]
    return [m[i][n] for i in range(n)]


def fit_camera(pairs):
    """The 3x4 projective camera, last entry 1, that best sends the model
    points of *pairs* [((x, y, z), (sx, sy))] to their screen points; None
    under MIN_FIT_POINTS distinct points or when they do not pin it."""
    points = {}
    for model, screen in pairs:
        points[model] = screen
    if len(points) < MIN_FIT_POINTS:
        return None
    rows, rhs = [], []
    for (x, y, z), (u, v) in points.items():
        rows.append([x, y, z, 1, 0, 0, 0, 0, -u * x, -u * y, -u * z])
        rhs.append(u)
        rows.append([0, 0, 0, 0, x, y, z, 1, -v * x, -v * y, -v * z])
        rhs.append(v)
    p = solve(rows, rhs)
    return None if p is None else p + [1.0]


def project(camera, point):
    """*point* through *camera*, or None behind it."""
    x, y, z = point
    w = camera[8] * x + camera[9] * y + camera[10] * z + camera[11]
    if abs(w) < 1e-9:
        return None
    return ((camera[0] * x + camera[1] * y + camera[2] * z + camera[3]) / w,
            (camera[4] * x + camera[5] * y + camera[6] * z + camera[7]) / w)


def fit_error(camera, pairs) -> float:
    """Mean distance in screen pixels between *pairs*' screen points and the
    model points sent through *camera*."""
    total = 0.0
    for model, screen in pairs:
        got = project(camera, model)
        if got is None:
            return float("inf")
        total += ((got[0] - screen[0]) ** 2 + (got[1] - screen[1]) ** 2) ** 0.5
    return total / len(pairs)


def section_pairs(player, index, file_name=None) -> dict:
    """{(file, section): [(model point, screen point)]} of one player: every
    figure primitive matched to a model primitive by its texels, and its four
    corners paired in the order `section.Primitive.corners` gives.  A
    primitive whose texels more than one section holds is left out: in slot 5
    six sections (59, 91, 93, 94, 97, 100) share one quad and three (57, 95,
    99) another."""
    out = {}
    for one in player:
        if len(one["uv"]) != 4:
            continue
        candidates = [c for c in index["by_uv"].get(tuple(tuple(t) for t in one["uv"]), ())
                      if not file_name or c[0] == file_name]
        if len({(name, i) for name, i, _k in candidates}) != 1:
            continue        # texels several sections share name no section
        for name, i, k in candidates[:1]:
            sec = index["sections"][(name, i)]
            prim = sec.primitives[k]
            corners = prim.corners
            pairs = []
            for vi, screen in zip(corners, one["xy"]):
                vert = sec.vertices[vi]
                pairs.append(((vert.x, vert.y, vert.z), tuple(screen)))
            out.setdefault((name, i), []).extend(pairs)
    return out


def attach_report(samples, image_path: str) -> dict:
    """What `--attach` measures, from a frame's samples: which file each
    figure primitive comes from, and for each player that wears the armband
    or the long sleeves, which body section's projection carries them."""
    index = model_index(image_path)
    figure = [one for one in samples if is_figure(one)]
    origin = {"MODEL.BIN only": 0, "EDT_MOD.BIN only": 0, "both": 0, "neither": 0}
    for one in figure:
        files = {name for name, _i, _k in index["by_uv"].get(tuple(tuple(t) for t in one["uv"]), ())}
        key = ("both" if len(files) == 2 else "MODEL.BIN only" if layout.MODEL in files
               else "EDT_MOD.BIN only" if files else "neither")
        origin[key] += 1
    shared = {}
    for one in figure:
        held = {i for name, i, _k in index["by_uv"].get(tuple(tuple(t) for t in one["uv"]), ())
                if name == layout.MODEL}
        if len(held) > 1:
            key = tuple(sorted(held))
            shared[key] = shared.get(key, 0) + 1
    rows, sets = [], []
    for number, player in enumerate(players(samples)):
        pairs = section_pairs(player, index, layout.MODEL)
        drawn = sorted(i for (_n, i) in pairs)
        sets.append({"player": number, "primitives": len(player), "sections": drawn,
                     "team": sorted({one["clut"] for one in player})})
        worn = [i for (_n, i) in pairs if i == ARMBAND_SECTION or i in LONG_SLEEVE_SECTIONS]
        if not worn:
            continue
        own = {}
        for (_n, i), these in pairs.items():
            camera = fit_camera(these)
            if camera is not None:
                own[i] = fit_error(camera, these)
        for i in sorted(set(worn)):
            if i not in own:
                continue
            these = pairs[(layout.MODEL, i)]
            joint = []
            for (_n, j), others in pairs.items():
                if j == i or j not in own:
                    continue
                camera = fit_camera(these + others)
                if camera is not None:
                    joint.append((fit_error(camera, these + others), j))
            joint.sort()
            rows.append({"player": number, "primitives": len(player), "section": i,
                         "points": len({m for m, _s in these}), "own": own[i],
                         "joint": joint[:3]})
    return {"origin": origin, "figure": len(figure), "rows": rows, "sets": sets,
            "shared": shared}


def own_quads(index, section: int) -> set:
    """The texel quads of MODEL.BIN section *section* that no other section
    holds: the only ones by which a frame primitive names it alone."""
    sec = index["sections"].get((layout.MODEL, section))
    out = set()
    for prim in (sec.primitives if sec else ()):
        uv = tuple(tuple(t) for t in prim.texcoords)
        if {(n, i) for n, i, _k in index["by_uv"].get(uv, ())} == {(layout.MODEL, section)}:
            out.add(uv)
    return out


def attach_judge(report: dict, armband: int = ARMBAND_SECTION,
                 replaced: int = REPLACED_SECTION, own_drawn=None) -> list:
    """Failures of the attachment rule: the figure's texels are MODEL.BIN's,
    some player draws *armband*, and every such player draws exactly what an
    armless player of the frame draws, *replaced* swapped for it -- 93 for 97
    in long sleeves, 90 for 4 in short (`SLEEVE_LENGTHS`, CORR-KITS-079)."""
    out = []
    origin = report["origin"]
    if origin["EDT_MOD.BIN only"] or not origin["MODEL.BIN only"]:
        out.append("the figure is not MODEL.BIN's: %s" % origin)
    sets = [tuple(one["sections"]) for one in report["sets"]]
    captains = [one for one in sets if armband in one]
    if not captains and own_drawn == 0:
        # The armband's own quads are not in this frame, so no player can be
        # named by it alone (CORR-KITS-079): what the texels still decide is
        # that its shared quads are drawn and that some outfield players lack
        # the piece it replaces while others draw it.
        if not any(armband in key for key in report.get("shared", {})):
            out.append("section %d is not in the frame, alone or shared" % armband)
        outfield = [one for one in sets if ROOT_SECTIONS[0] in one]
        with_it = [one for one in outfield if replaced in one]
        if not with_it or len(with_it) == len(outfield):
            out.append("of %d outfield player(s), %d draw section %d: no captain is seen "
                       "by its absence" % (len(outfield), len(with_it), replaced))
        return out
    if not captains:
        out.append("no player draws section %d" % armband)
    for one in captains:
        swapped = tuple(sorted((set(one) - {armband}) | {replaced}))
        if swapped not in sets:
            out.append("a player draws %s, and no player draws it with %d in place of %d"
                       % (" ".join(map(str, one)), replaced, armband))
    return out


def run_attach(slot: int, cue: str, cache=None, plant=False, length: str = "long") -> int:
    """`--attach SLOT`: section 4.3, where the armband and the long sleeves
    of MODEL.BIN sit on a match figure."""
    import json

    path = cache or os.path.join(ATTACH_DIR, "attach-%d.json" % slot)
    if cache and os.path.isfile(cache):
        with open(cache) as fh:
            samples = [dict(one, page=tuple(one["page"]), clut=tuple(one["clut"]),
                            uv=[tuple(t) for t in one["uv"]], xy=[tuple(t) for t in one["xy"]])
                       for one in json.load(fh)]
        print("  frame read from %s, no emulator" % cache)
    else:
        samples = read_frame(slot, cue)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(samples, fh)
        print("  frame kept at %s (--frame-json reads it back)" % path)
    report = attach_report(samples, os.environ[IMAGE_VARIABLE])
    print("  %d figure primitive(s); by the file their texels are in: %s"
          % (report["figure"], ", ".join("%s %d" % kv for kv in report["origin"].items())))
    for key, n in sorted(report["shared"].items(), key=lambda kv: -kv[1]):
        print("  %d primitive(s) whose texels sections %s all hold: left out"
              % (n, " ".join(map(str, key))))
    print("  MODEL.BIN sections each player draws (texels one section holds only):")
    for one in report["sets"]:
        print("    player %2d (%3d prims, CLUT %s): %s"
              % (one["player"], one["primitives"],
                 " ".join("(%d,%d)" % c for c in one["team"]),
                 " ".join(str(i) for i in one["sections"])))
    print("  one camera fitted to a worn section alone, and to it with each other section:")
    for row in report["rows"]:
        print("    player %2d (%3d prims) section %3d, %2d point(s): alone %.2f px; one "
              "camera with section %s"
              % (row["player"], row["primitives"], row["section"], row["points"], row["own"],
                 ", ".join("%d %.2f px" % (j, err) for err, j in row["joint"])))
    rule = SLEEVE_LENGTHS[length]
    armband = PLANT_ARMBAND if plant else rule["armband"]
    replaced = rule["neighbour"] if plant else rule["replaced"]
    print("  %s sleeves: the armband is %d, in place of %d" % (length, rule["armband"],
                                                             rule["replaced"]))
    index = model_index(os.environ[IMAGE_VARIABLE])
    own = own_quads(index, armband)
    drawn = {tuple(tuple(t) for t in one["uv"]) for one in samples}
    own_drawn = len(own & drawn)
    print("  section %d on the disc: %d quad(s), %d of them its own; %d own quad(s) in "
          "this frame" % (armband, len(index["sections"][(layout.MODEL, armband)].primitives),
                          len(own), own_drawn))
    if not own_drawn:
        print("  no quad of its own in the frame: no player is named by it alone, and "
              "the swap is --attach-matrix's to judge (by the pointers)")
    if plant:
        print("  PLANT  section %d named the armband, in place of %d" % (armband, replaced))
    failures = attach_judge(report, armband, replaced, own_drawn)
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures and own_drawn:
        print("  ok    the figure is MODEL.BIN's, and section %d takes the place of %d"
              % (armband, replaced))
    elif not failures:
        print("  ok    the figure is MODEL.BIN's; section %d is drawn in shared quads, and "
              "the outfield players without %d are the captains" % (armband, replaced))
    return 1 if failures else 0


# --- section 4.3: the GTE matrix of each MODEL.BIN section in a match -----

ROOT_SECTIONS = (2, 56)
"""The first body piece of an outfield figure and of a goalkeeper, in the
order the stops of slot 5 draw them."""
FIGURE_SPREAD = 500
"""How far, in GTE units, a piece's translation may sit from its figure's
median: one player.  Measured on slot 5 (`--attach-matrix 5`): 119 to 210
with the matrix given to the piece named a stop later, 878 to 4065 with it
given to the piece named at its own stop, where a figure takes the next
player's head."""
MATRIX_STOPS = 600
"""Matrix loads read per run: a match frame draws some twenty figures of
nine sections each, so this is a few frames' worth."""


def resident_models(game, image_path: str) -> dict:
    """{name: bytes that differ}: each model file against RAM at the load
    address the LOOKS SET measured (`layout.BASE`).  A match patches the CLUT
    ids per team, so a few differing bytes are expected and a file that is
    not there differs everywhere."""
    import iso_source

    out = {}
    with iso_source.open_disc(image_path) as disc:
        for name, base in sorted(layout.BASE.items()):
            data = disc.read(name)
            got = game.read_ram(base, len(data), os.path.join(game.out_dir, "resident.bin"))
            out[name] = sum(1 for a, b in zip(got, data) if a != b) + abs(len(got) - len(data))
    return out


def matrix_stops(game, maps, count: int = MATRIX_STOPS, partial: bool = False,
                 wait: int = None) -> list:
    """*count* stops at the per-piece matrix load, each as {"named": (file,
    section) or None, "rotation", "translation"}, in drawing order.  The name
    is what the live pointers say, which -- the `looks` measured -- is the
    piece drawn BEFORE the matrix (`DRAW_LAG`).  When the load stops firing
    within *wait* seconds (`WATCH_SECONDS`), the run is refused -- or, with
    *partial*, returned as far as it got (`--edit-number` asks for that after
    the press, G7; in slot 8 after Circle the load keeps firing through all of
    `EDIT_TURN_STOPS`, so nothing is cut short there)."""
    import who_writes

    import oracle as looks_oracle  # tools/looks

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.POSE_PIECE_MATRIX))
    path = os.path.join(game.out_dir, "match-matrix.bin")
    out = []
    try:
        for _ in range(count):
            client.call("continue")
            if not looks_oracle._wait_for_hit(game, wait or looks_oracle.WATCH_SECONDS):
                if partial:
                    break
                raise RuntimeError("%s stopped %d time(s) and then stopped stopping"
                                   % (who_writes.hx(layout.POSE_PIECE_MATRIX), len(out)))
            registers = client.call("read_registers", group="gpr")
            seen = {(where[0], where[1]) for _n, _v, where
                    in looks_oracle.pointers_into_models(registers, maps)
                    if where[1] is not None}
            base = who_writes.register_value(registers, layout.POSE_PIECE_MATRIX_BASE)
            rotation, translation = looks_oracle._matrix_struct(game, base, path)
            out.append({"named": sorted(seen), "rotation": rotation,
                        "translation": translation})
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    return out


def matrix_pieces(stops, lag: int = 1) -> list:
    """The stops turned into drawn pieces: the matrix of stop k belongs to the
    section the pointers name *lag* stops later (`looks` DRAW_LAG, 1), each as
    {"section", "matrix"}; a stop naming no section, or several, is a None
    section."""
    out = []
    for k in range(len(stops) - lag):
        named = stops[k + lag]["named"]
        out.append({"section": named[0][1] if len(named) == 1 else None,
                    "matrix": (tuple(stops[k]["rotation"]), tuple(stops[k]["translation"]))})
    return out


def matrix_passes(pieces, roots_of=ROOT_SECTIONS) -> list:
    """The pieces cut into figures: a figure opens at its root, section 2
    (outfield) or 56 (goalkeeper) unless *roots_of* says otherwise, and takes
    the piece before it, its head."""
    roots = [k for k, p in enumerate(pieces) if p["section"] in roots_of]
    out = []
    for at, start in enumerate(roots):
        end = roots[at + 1] - 1 if at + 1 < len(roots) else None
        if start == 0 or end is None:
            continue        # the first and the last figure are cut off
        out.append(pieces[start - 1:end])
    return out


from core.figure import ARM_PIECES, KEEPER_ARMBAND, SLEEVE_LENGTHS  # noqa: E402,F401  (the core's tables)


def matrix_report(passes, worn_sections=SLEEVE_LENGTHS["long"]["worn"]) -> dict:
    """For the worn sections of every whole figure, which other piece of the
    same figure has the same matrix (None: its own), and the order each kind
    of figure draws.  A figure with a piece no stop names -- the last of a
    frame, whose next stop is the next frame's -- is kept for the matrices
    and left out of the orders."""
    figures, orders, cut = [], {}, 0
    for number, figure in enumerate(passes):
        sections = [p["section"] for p in figure]
        if None in sections:
            cut += 1
        else:
            orders[tuple(sections)] = orders.get(tuple(sections), 0) + 1
        worn = []
        for p in figure:
            if p["section"] in worn_sections:
                same = [q["section"] for q in figure
                        if q is not p and q["matrix"] == p["matrix"]]
                worn.append((p["section"], same or None))
        translations = [p["matrix"][1] for p in figure]
        median = [sorted(t[i] for t in translations)[len(translations) // 2] for i in range(3)]
        spread = max(sum((t[i] - median[i]) ** 2 for i in range(3)) ** 0.5
                     for t in translations)
        figures.append({"figure": number, "head": sections[0], "worn": worn,
                        "spread": spread, "cut": None in sections})
    return {"figures": figures, "orders": orders, "cut": cut}


def matrix_judge(report: dict, armband_slot: int = REPLACED_SECTION,
                 armband: int = ARMBAND_SECTION) -> list:
    """Failures of the rule the matrices give: every worn section has its own
    matrix, and a captain draws exactly an outfield figure's order with the
    armband where *armband_slot* is."""
    out = ["figure %d: section %d shares its matrix with %s" % (f["figure"], section, same)
           for f in report["figures"] for section, same in f["worn"] if same]
    out += ["figure %d: a translation %.0f from the figure's median, over %d -- the "
            "matrices are not this figure's" % (f["figure"], f["spread"], FIGURE_SPREAD)
            for f in report["figures"] if f["spread"] > FIGURE_SPREAD]
    orders = {o[1:] for o in report["orders"]}      # the head names the player, not the kind
    captains = [o for o in orders if armband in o]
    if not captains:
        out.append("no figure draws section %d" % armband)
    for order in captains:
        plain = tuple(armband_slot if s == armband else s for s in order)
        if plain not in orders:
            out.append("a captain draws %s, and no figure draws it with %d where %d is"
                       % (" ".join(map(str, order)), armband_slot, armband))
    return out


def run_attach_matrix(slot: int, cue: str, cache=None, plant=None, length="long") -> int:
    """`--attach-matrix SLOT`: which matrix each MODEL.BIN section is drawn
    with in a match."""
    import json

    import oracle as looks_oracle  # tools/looks

    image = os.environ[IMAGE_VARIABLE]
    maps = looks_oracle.model_maps(image)
    path = cache or os.path.join(ATTACH_DIR, "matrix-%d.json" % slot)
    if cache and os.path.isfile(cache):
        with open(cache) as fh:
            kept = json.load(fh)
        print("  stops read from %s, no emulator" % cache)
    else:
        with looks_oracle.Oracle(cue) as game:
            load_slot(game, slot, "matrix-%d" % slot)
            resident = resident_models(game, image)
            stops = matrix_stops(game, maps)
        kept = {"resident": resident, "stops": stops}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(kept, fh)
        print("  stops kept at %s (--frame-json reads them back)" % path)
    for name, differ in sorted(kept["resident"].items()):
        print("  %s against RAM at its LOOKS SET address: %s byte(s) differ" % (name, differ))
    named = {}
    for one in kept["stops"]:
        key = " ".join("%s:%s" % (n.rsplit("/", 1)[-1], i) for n, i in one["named"]) or "none"
        named[key] = named.get(key, 0) + 1
    matrices = [(tuple(one["rotation"]), tuple(one["translation"])) for one in kept["stops"]]
    print("  %d stop(s), %d distinct matrices (%d distinct rotations)"
          % (len(matrices), len(set(matrices)), len({r for r, _ in matrices})))
    print("  %d stop(s); what the pointers name, by count:" % len(kept["stops"]))
    for key, n in sorted(named.items(), key=lambda kv: -kv[1]):
        print("    %-30s %d" % (key, n))
    lag = 0 if plant == "lag" else 1
    passes = matrix_passes(matrix_pieces(kept["stops"], lag))
    rule = SLEEVE_LENGTHS[length]
    report = matrix_report(passes, rule["worn"])
    print("  %d whole figure(s), %d of them with a last piece no stop names; the "
          "matrix of a stop goes to the piece named %d stop(s) later.  The order "
          "each figure draws, head first:" % (len(passes), report["cut"], lag))
    for order, n in sorted(report["orders"].items(), key=lambda kv: -kv[1]):
        print("    x%-3d %s" % (n, " ".join(str(s) for s in order)))
    spreads = [f["spread"] for f in report["figures"]]
    if spreads:
        print("  every figure's translations within %.0f to %.0f of its median (limit %d)"
              % (min(spreads), max(spreads), FIGURE_SPREAD))
    print("  the worn sections of every figure, each against every other piece of it:")
    for f in report["figures"]:
        print("    figure %2d, head %-4s %s"
              % (f["figure"], f["head"], ", ".join(
                  "%d %s" % (section, "same as %s" % same if same else "own")
                  for section, same in f["worn"])))
    slot = rule["neighbour"] if plant == "slot" else rule["replaced"]
    if plant:
        print("  PLANT  %s" % ("matrices given to the piece named at their own stop"
                               if plant == "lag" else "the armband expected where %d is" % slot))
    failures = matrix_judge(report, slot, rule["armband"])
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        print("  ok    %s sleeves: every worn section has its own matrix, and section %d is "
              "drawn where %d is" % (length, rule["armband"], slot))
    return 1 if failures else 0


# --- section 4.3: the pose of a match figure, against its own frame -------

POSE_DIR = os.path.join("work", "kits-pose")
POSE_SUBMITS = 7
"""Stops at `layout.GPU_LIST_SUBMIT` a `--match-pose` run takes: three per
frame (the `looks` measured: a one-node list twice and the ordering table
once), so seven close two whole frames after the first, cut-off one."""
POSE_MATRIX_LIMIT = 4000
"""Matrix stops a run may take before it gives up on the submits."""
POSE_LIMIT = 2.0
"""The mean error in pixels a piece may have.  Measured on slot 5
(`--match-pose 5`, KITS-TASK-45): 0.62 to 1.01 over the 24 pieces of the two
figures, the integer screen coordinates' rounding; with `--plant-pose` the
best piece is 4.72 and the worst 264.70."""


def pose_capture(game, maps, submits: int = POSE_SUBMITS) -> dict:
    """One run of the frame loop with two breakpoints: every per-piece matrix
    load (as `matrix_stops` reads it, plus the GTE projection in force) and
    every list handed to the GPU, in the order they happen.  Paused at the
    last submit, both ordering tables are still whole in RAM, and each head
    is walked into its textured samples."""
    import who_writes

    import oracle as looks_oracle  # tools/looks

    client = game.client
    client.call("breakpoint", action="clear")
    for address in (layout.POSE_PIECE_MATRIX, layout.GPU_LIST_SUBMIT):
        client.call("breakpoint", action="add", type="execute",
                    address=who_writes.hx(address))
    path = os.path.join(game.out_dir, "pose-matrix.bin")
    events, seen_submits, matrices = [], 0, 0
    try:
        while seen_submits < submits:
            client.call("continue")
            if not looks_oracle._wait_for_hit(game, looks_oracle.WATCH_SECONDS):
                raise RuntimeError("the frame loop stopped after %d event(s)" % len(events))
            registers = client.call("read_registers", group="gpr")
            pc = who_writes.register_value(registers, "pc")
            if pc == layout.GPU_LIST_SUBMIT:
                events.append({"kind": "submit", "head": who_writes.register_value(
                    registers, layout.GPU_LIST_HEAD)})
                seen_submits += 1
                continue
            matrices += 1
            if matrices > POSE_MATRIX_LIMIT:
                raise RuntimeError("%d matrix stops and %d submit(s)" % (matrices, seen_submits))
            named = {(where[0], where[1]) for _n, _v, where
                     in looks_oracle.pointers_into_models(registers, maps)
                     if where[1] is not None}
            base = who_writes.register_value(registers, layout.POSE_PIECE_MATRIX_BASE)
            rotation, translation = looks_oracle._matrix_struct(game, base, path)
            events.append({"kind": "matrix", "named": sorted(named), "rotation": rotation,
                           "translation": translation,
                           "projection": looks_oracle.gte_projection(
                               client.call("get_gte_registers"))})
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    first, size, step = layout.SCENERY_SWEEP
    ram = b"".join(game.read_ram(base, step, os.path.join(game.out_dir, "pose-%08x.bin" % base))
                   for base in range(first, first + size, step))
    lists, offsets = {}, {}
    for one in events:
        if one["kind"] == "submit" and one["head"] not in lists:
            try:
                nodes = looks_oracle.walk_gpu_list(ram, one["head"])
            except Exception:  # noqa: BLE001 -- a list the next frame overwrote
                continue
            commands = looks_oracle.commands_of(nodes)
            lists[one["head"]] = textured_samples(commands)
            offsets[one["head"]] = draw_offset(commands)
    return {"events": events, "lists": {"%d" % k: v for k, v in lists.items()},
            "offsets": {"%d" % k: v for k, v in offsets.items()}}


def pose_frames(capture: dict) -> list:
    """The frames of a capture: for each submit of a list with figure
    primitives, the matrix stops since the previous such submit.  The first
    is left out, its stops having begun mid-frame."""
    blocks, current, out = [], [], []
    for one in capture["events"]:
        if one["kind"] == "matrix":
            current.append(one)
            continue
        samples = capture["lists"].get("%d" % one["head"])
        if not samples or not any(is_figure(s) for s in samples):
            continue
        blocks.append((one["head"], current))
        current = []
    for k, (head, stops) in enumerate(blocks):
        if k == 0:
            continue        # its stops began mid-frame
        out.append({"head": head, "stops": stops})
    return out


def pose_project(rotation, translation, projection, vertex):
    """A model vertex through one piece's GTE matrix and the projection:
    RTPS, `SX = OFX + H * X / Z`, rotation in 4.12."""
    x, y, z = vertex
    r = rotation
    cx = (r[0] * x + r[1] * y + r[2] * z) / 4096.0 + translation[0]
    cy = (r[3] * x + r[4] * y + r[5] * z) / 4096.0 + translation[1]
    cz = (r[6] * x + r[7] * y + r[8] * z) / 4096.0 + translation[2]
    if cz <= 0:
        return None
    h = projection["H"]
    return (projection["OFX"] + h * cx / cz, projection["OFY"] + h * cy / cz)


PAIRINGS = ("indices", "corners")
"""How a primitive's texels are paired with its vertices: `indices`, the
stored order, is the one the game uses; `corners` is what `--pair-by
corners` shows it is not (CORR-KITS-083)."""


def piece_error(piece, projection, sec, group, pair: str = "indices") -> tuple:
    """(mean pixel distance, primitives matched) of one piece: each primitive
    of its section projected with the piece's matrix and matched, by its four
    texels, to the nearest primitive of *group* that carries them.  *pair*
    says which vertex each texel goes with (`PAIRINGS`)."""
    by_uv = {}
    for one in group:
        if len(one["uv"]) == 4:
            by_uv.setdefault(tuple(tuple(t) for t in one["uv"]), []).append(one)
    total, corners, matched = 0.0, 0, 0
    rotation, translation = piece["matrix"]
    for prim in sec.primitives:
        drawn = by_uv.get(tuple(tuple(t) for t in prim.texcoords))
        if not drawn:
            continue        # culled, or a texel quad the frame does not draw
        points = {}
        # texcoords follow the STORED order, not `corners`: `--pair-by
        # corners` prints what the other pairing gives
        order = prim.indices if pair == "indices" else prim.corners
        for vi, texel in zip(order, prim.texcoords):
            v = sec.vertices[vi]
            points[tuple(texel)] = pose_project(rotation, translation, projection,
                                                (v.x, v.y, v.z))
        if None in points.values() or len(points) != 4:
            continue        # behind the eye, or a quad two corners of which share a texel
        best = min(sum(((points[uv][0] - xy[0]) ** 2 + (points[uv][1] - xy[1]) ** 2) ** 0.5
                       for uv, xy in zip(one["uv"], one["xy"])) for one in drawn)
        total += best
        corners += len(points)
        matched += 1
    return ((total / corners) if corners else None, matched)


POSE_MARGIN = 16
"""Pixels around a player's kit primitives within which the frame's other
textured primitives -- head, boots, skin -- are taken as that player's."""


def pose_groups(samples, margin: int = POSE_MARGIN) -> list:
    """The players of a frame (`players`, kit primitives only) each widened
    to every textured primitive whose corners all fall in its screen box
    grown by *margin*."""
    out = []
    for group in players(samples):
        xs = [p[0] for one in group for p in one["xy"]]
        ys = [p[1] for one in group for p in one["xy"]]
        box = (min(xs) - margin, min(ys) - margin, max(xs) + margin, max(ys) + margin)
        out.append([one for one in samples if len(one["uv"]) == 4 and all(
            box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])])
    return out


def pose_figure(figure, projection, index, groups, pair: str = "indices") -> dict:
    """One figure against the frame: the player group whose primitives its
    pieces land on best, and each piece's error there."""
    best = None
    for number, group in enumerate(groups):
        rows = []
        for piece in figure:
            sec = index["sections"].get((layout.MODEL, piece["section"]))
            error, matched = (piece_error(piece, projection, sec, group, pair) if sec
                              else (None, 0))
            rows.append({"section": piece["section"], "error": error, "matched": matched})
        errors = [r["error"] for r in rows if r["error"] is not None]
        if not errors:
            continue
        score = sum(errors) / len(errors)
        if best is None or score < best["score"]:
            best = {"group": number, "score": score, "rows": rows}
    return best


def pose_choose(passes) -> dict:
    """{"outfield": figure, "captain": figure}: the first whole outfield
    figure that draws the armband, and the first that does not."""
    out = {}
    for figure in passes:
        sections = [p["section"] for p in figure]
        if None in sections or sections[1] != ROOT_SECTIONS[0]:
            continue
        kind = "captain" if ARMBAND_SECTION in sections else "outfield"
        out.setdefault(kind, figure)
    return out


def pose_report(frame: dict, index, lag: int = 1, pair: str = "indices") -> dict:
    """The chosen figures of one frame, measured against its list."""
    stops = frame["stops"]
    pieces = matrix_pieces(stops, lag)
    for piece, stop in zip(pieces, stops):
        piece["projection"] = stop["projection"]
    chosen = pose_choose(matrix_passes(pieces))
    return {kind: {"figure": figure, "fit": pose_figure(
        figure, figure[0]["projection"], index, frame["groups"], pair)}
        for kind, figure in sorted(chosen.items())}


def pose_judge(report: dict, limit: float) -> list:
    """Failures: a kind of figure missing, a piece the frame never matched,
    or a piece whose mean error is over *limit*."""
    out = ["no %s figure in the frame" % kind for kind in ("captain", "outfield")
           if kind not in report]
    for kind, one in sorted(report.items()):
        if one["fit"] is None:
            out.append("%s: no piece lands on any player" % kind)
            continue
        for row in one["fit"]["rows"]:
            if row["error"] is None:
                out.append("%s: section %s has no primitive in the frame"
                           % (kind, row["section"]))
            elif row["error"] > limit:
                out.append("%s: section %s is %.2f px from the frame, over %.2f"
                           % (kind, row["section"], row["error"], limit))
    return out


def pose_file(slot: int, report: dict) -> dict:
    """What `--write` versions as `core/match_pose.json`: the projection and,
    per figure kind, its head and each piece's section, rotation and
    translation, in drawing order."""
    first = next(iter(report.values()))["figure"]
    return {"source": "python tools/kits/oracle.py --match-pose %d --write (KITS-TASK-45)"
                      % slot,
            "slot": slot, "projection": first[0]["projection"],
            "figures": {kind: {"head": one["figure"][0]["section"], "pieces": [
                {"section": p["section"], "rotation": list(p["matrix"][0]),
                 "translation": list(p["matrix"][1])} for p in one["figure"]]}
                for kind, one in sorted(report.items())}}


def load_capture(slot: int, cue: str, cache=None) -> dict:
    """The capture of `--match-pose`: read back from *cache*, or taken in the
    fork and kept; with every sample's tuples restored."""
    import json

    import oracle as looks_oracle  # tools/looks

    path = cache or os.path.join(ATTACH_DIR, "pose-%d.json" % slot)
    if cache and os.path.isfile(cache):
        with open(cache) as fh:
            capture = json.load(fh)
        print("  capture read from %s, no emulator" % cache)
    else:
        maps = looks_oracle.model_maps(os.environ[IMAGE_VARIABLE])
        with looks_oracle.Oracle(cue) as game:
            load_slot(game, slot, "pose-%d" % slot)
            capture = pose_capture(game, maps)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(capture, fh)
        print("  capture kept at %s (--frame-json reads it back)" % path)
    for one in capture["lists"].values():
        for s in one:
            s.update(page=tuple(s["page"]), clut=tuple(s["clut"]),
                     uv=[tuple(t) for t in s["uv"]], xy=[tuple(t) for t in s["xy"]])
    return capture


# --- section 4.3: the match figure drawn, against the game's frame ---------

SILHOUETTE_SCALE = 4
"""Cells per screen pixel each way when a silhouette is rasterised."""
SILHOUETTE_LIMIT = 0.70
"""The intersection over union a drawn match figure has to reach against the
game's.  Measured on slot 5 with TEX_14 (`--match-silhouette 5`,
KITS-TASK-47): 0.800 for the outfield figure and 0.821 for the captain, a
figure some forty pixels tall losing its edge cells to the GPU's whole-pixel
corners (rounding ours to whole pixels gives 0.793 and 0.787, no better);
with `--plant-silhouette` 0.322 and 0.284."""


def raster(triangles, scale: int = SILHOUETTE_SCALE) -> set:
    """The cells (x, y), at *scale* per pixel, whose centres fall inside any
    of *triangles* [((x, y), (x, y), (x, y))] given in screen pixels."""
    out = set()
    for a, b, c in triangles:
        xs, ys = (a[0], b[0], c[0]), (a[1], b[1], c[1])
        area = (b[0] - a[0]) * (c[1] - a[1]) - (c[0] - a[0]) * (b[1] - a[1])
        if abs(area) < 1e-12:
            continue
        for cy in range(int(min(ys) * scale) - 1, int(max(ys) * scale) + 2):
            for cx in range(int(min(xs) * scale) - 1, int(max(xs) * scale) + 2):
                px, py = (cx + 0.5) / scale, (cy + 0.5) / scale
                w0 = (b[0] - px) * (c[1] - py) - (c[0] - px) * (b[1] - py)
                w1 = (c[0] - px) * (a[1] - py) - (a[0] - px) * (c[1] - py)
                w2 = (a[0] - px) * (b[1] - py) - (b[0] - px) * (a[1] - py)
                if (w0 >= 0 and w1 >= 0 and w2 >= 0) or (w0 <= 0 and w1 <= 0 and w2 <= 0):
                    out.add((cx, cy))
    return out


def quad_triangles(points) -> list:
    """A quad's four corners as the GPU draws them: (0 1 2) and (1 2 3)."""
    return [(points[0], points[1], points[2]), (points[1], points[2], points[3])]


def iou(one: set, two: set) -> float:
    return len(one & two) / float(len(one | two)) if one or two else 0.0


def game_silhouette(group, index, sections) -> list:
    """The triangles of a player group's primitives that a section of the
    figure holds by its texels: what the game drew of that figure."""
    held = {tuple(tuple(t) for t in prim.texcoords)
            for (name, i), sec in index["sections"].items()
            if name == layout.MODEL and i in sections for prim in sec.primitives}
    out = []
    for one in group:
        if len(one["xy"]) == 4 and tuple(tuple(t) for t in one["uv"]) in held:
            out += quad_triangles(one["xy"])
    return out


def drawn_silhouette(drawn) -> list:
    """The triangles of a camera-view match scene on the game's screen."""
    from core import api

    out = []
    for part in drawn.parts:
        points = api.screen_points(drawn, part)
        if None not in points:
            out += quad_triangles(points)
    return out


def rigid_pose(pose: dict) -> dict:
    """The plant: every piece of every figure given its root's matrix."""
    import copy

    out = copy.deepcopy(pose)
    for figure in out["figures"].values():
        root = next(p for p in figure["pieces"] if p["section"] == ROOT_SECTIONS[0])
        for p in figure["pieces"]:
            p["rotation"], p["translation"] = list(root["rotation"]), list(root["translation"])
    return out


def run_match_silhouette(slot: int, cue: str, tag: str, cache=None, plant=False) -> int:
    """`--match-silhouette SLOT --tag TT`: the match figure the 3D tab draws
    (`api.match_figure`, camera view), each kind against the player the game
    drew in the frame of the capture, silhouette for silhouette."""
    from core import api

    image = os.environ[IMAGE_VARIABLE]
    capture = load_capture(slot, cue, cache)
    frames = pose_frames(capture)
    if not frames:
        print("  FAIL  no whole frame with figure primitives in the capture")
        return 1
    frame = frames[-1]
    frame["groups"] = pose_groups(capture["lists"]["%d" % frame["head"]])
    index = model_index(image)
    report = pose_report(frame, index)
    kit = api.open_source(image).kit(tag)
    geometry = api.read_geometry(image)
    pose = api.match_pose()
    if plant:
        pose = rigid_pose(pose)
        print("  PLANT  every piece drawn with its figure's body matrix")
    failures, scores = [], []
    for kind in api.MATCH_FIGURES:
        one = report.get(kind)
        if one is None or one["fit"] is None:
            failures.append("no %s figure in the frame" % kind)
            continue
        drawn = api.match_figure(kit, 1, armband=(kind == "captain"), figure=kind,
                                 view="camera", geometry=geometry, pose=pose)
        sections = {p["section"] for p in one["figure"]}
        game = raster(game_silhouette(frame["groups"][one["fit"]["group"]], index, sections))
        ours = raster(drawn_silhouette(drawn))
        score = iou(game, ours)
        scores.append(score)
        print("  %-8s TEX_%s, order %s: game %d cell(s), ours %d, both %d; IoU %.3f"
              % (kind, tag, " ".join(map(str, drawn.notes["order"])), len(game), len(ours),
                 len(game & ours), score))
        if score < SILHOUETTE_LIMIT:
            failures.append("%s: IoU %.3f under %.3f" % (kind, score, SILHOUETTE_LIMIT))
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        print("  ok    both figures within IoU %.3f of the game's (worst %.3f; cells of 1/%d px)"
              % (SILHOUETTE_LIMIT, min(scores), SILHOUETTE_SCALE))
    return 1 if failures else 0


def run_match_pose(slot: int, cue: str, cache=None, plant=False, pair="indices",
                   write=False, check=False) -> int:
    """`--match-pose SLOT`: section 4.3, the pose of a match figure -- each
    MODEL.BIN piece's matrix, proved on the frame it was drawn in."""
    import json

    image = os.environ[IMAGE_VARIABLE]
    capture = load_capture(slot, cue, cache)
    matrices = sum(1 for e in capture["events"] if e["kind"] == "matrix")
    print("  %d event(s): %d matrix stop(s), %d submit(s), %d list(s) walked"
          % (len(capture["events"]), matrices, len(capture["events"]) - matrices,
             len(capture["lists"])))
    frames = pose_frames(capture)
    if not frames:
        print("  FAIL  no whole frame with figure primitives in the capture")
        return 1
    frame = frames[-1]
    frame["groups"] = pose_groups(capture["lists"]["%d" % frame["head"]])
    projections = {(p["projection"]["H"], p["projection"]["OFX"], p["projection"]["OFY"])
                   for p in frame["stops"]}
    print("  frame of list %#x: %d matrix stop(s) since the previous one, %d player "
          "group(s); projection (H, OFX, OFY) %s"
          % (frame["head"], len(frame["stops"]), len(frame["groups"]),
             ", ".join("(%d, %.1f, %.1f)" % p for p in sorted(projections))))
    index = model_index(image)
    lag = 0 if plant else 1
    if plant:
        print("  PLANT  each matrix given to the piece named at its own stop (no lag)")
    if pair != "indices":
        print("  PAIR   texels paired with the vertices in `%s` order, not the stored one" % pair)
    report = pose_report(frame, index, lag, pair)
    for kind, one in sorted(report.items()):
        fit = one["fit"]
        print("  %s, head %s, order %s:" % (kind, one["figure"][0]["section"], " ".join(
            str(p["section"]) for p in one["figure"])))
        if fit is None:
            continue
        print("    on player group %d; per piece, the mean distance in pixels between "
              "its projected corners and the frame's:" % fit["group"])
        for row in fit["rows"]:
            print("      section %-4s %s over %d primitive(s)"
                  % (row["section"], "none" if row["error"] is None
                     else "%6.2f px" % row["error"], row["matched"]))
    errors = [r["error"] for one in report.values() if one["fit"]
              for r in one["fit"]["rows"] if r["error"] is not None]
    if errors:
        print("  worst piece %.2f px, limit %.2f" % (max(errors), POSE_LIMIT))
    failures = pose_judge(report, POSE_LIMIT)
    for line in failures:
        print("  FAIL  %s" % line)
    if pair != "indices":
        print("  (--pair-by %s is a report: nothing is written)" % pair)
        return 1 if failures else 0
    if failures:
        return 1
    if plant:
        print("  ok    the plant passed, so nothing is written: the limit measures nothing")
        return 1
    os.makedirs(POSE_DIR, exist_ok=True)
    for kind, one in sorted(report.items()):
        figure = one["figure"]
        out = os.path.join(POSE_DIR, "slot%d-%d.json" % (slot, figure[0]["section"]))
        with open(out, "w") as fh:
            json.dump({"slot": slot, "kind": kind, "head": figure[0]["section"],
                       "file": layout.MODEL, "projection": figure[0]["projection"],
                       "pieces": [{"section": p["section"], "rotation": list(p["matrix"][0]),
                                   "translation": list(p["matrix"][1])} for p in figure]},
                      fh, indent=1)
        print("  wrote %s" % out)
    from core import figure as _figure

    text = json.dumps(pose_file(slot, report), indent=1) + "\n"
    if write:
        with open(_figure.MATCH_POSE, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print("  wrote %s" % os.path.relpath(_figure.MATCH_POSE))
    if check:
        try:
            with open(_figure.MATCH_POSE, encoding="utf-8") as fh:
                kept = fh.read()
        except OSError:
            kept = None
        if kept != text:
            print("  FAIL  %s is not what this run measures: rerun with --write"
                  % os.path.relpath(_figure.MATCH_POSE))
            return 1
        print("  ok    %s is what this run measures" % os.path.relpath(_figure.MATCH_POSE))
    print("  ok    every piece of both figures lands within %.2f px of its frame"
          % POSE_LIMIT)
    return 0


# --- section 4.3: short sleeves are the sleeves image, rewritten ----------

SLEEVES_SET = {1: 1, 2: 5}
"""Set -> the record of its sleeves image, (576,384) 64x128 (section 1.1)."""


def read_image(slot: int, cue: str, x: int, y: int, w: int, h: int) -> list:
    """One VRAM rectangle as 15-bit halfwords, read twice, each after its own
    `load_state` of *slot*; raises when the two differ."""
    import oracle as looks_oracle  # tools/looks

    reads = []
    with looks_oracle.Oracle(cue) as game:
        for n in range(2):
            load_slot(game, slot, "image-%d-%d" % (slot, n))
            rows = looks_oracle.vram_region(game, x, y, w, h)
            reads.append([(p[0] >> 3) | (p[1] >> 3) << 5 | (p[2] >> 3) << 10
                          for row in rows for p in row])
    if reads[0] != reads[1]:
        raise RuntimeError("the rectangle read twice differs: nothing is measured")
    return reads[0]


def run_sleeves_image(slot: int, cue: str, page_x: int, tag: str, kit_set: int = 1,
                      picture=None) -> int:
    """`--sleeves-image SLOT`: the sleeves image the match holds in VRAM at
    page *page_x*, against TEX_*tag*'s on the disc -- which blocks differ, and
    which zones of the map they cover.  A report only: it asserts nothing and
    always exits 0, so its numbers are leads, never a verdict (CORR-KITS-082,
    section 4.3)."""
    body = _body(tag)
    record = records_of(body)[SLEEVES_SET[kit_set]]
    disc = [five(v) for v in payload(body, record)]
    vram = read_image(slot, cue, page_x, record.y, record.w, record.h)
    print("  sleeves image (%d,%d) %dx%d against TEX_%s set %d; read twice, identical"
          % (page_x, record.y, 2 * record.w, record.h, tag, kit_set))
    found = diff_blocks(vram, disc, record.w, record.h)
    total = sum(b[4] for b in found)
    print("  %d pixel(s) of %d differ from the disc, in %d block(s):"
          % (total, 2 * record.w * record.h, len(found)))
    for x0, y0, x1, y1, n in found[:BLOCKS_SHOWN]:
        zones = block_zones((x0 + IMAGE_HEIGHT, y0, x1 + IMAGE_HEIGHT, y1, n))
        print("    (%3d,%3d)-(%3d,%3d) %4d pixel(s): %s"
              % (x0 + IMAGE_HEIGHT, y0, x1 + IMAGE_HEIGHT, y1, n,
                 ", ".join(zones) or "no zone"))
    if picture:
        save_picture(picture, vram, record.w, record.h, body, kit_set)
        print("  picture: %s" % picture)
    return 0


# --- section 4.7: the back and the number ---------------------------------

UNIFORM_RECORD = 0
"""The set-1 uniform page, (576,256) 64x128 halfwords = 128x128 pixels."""
UNIFORM_SET2 = 4
"""The set-2 uniform page; records 0 and 4 share the rectangle (section 1.1)."""
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
from core.figure import DIGIT_STEP, DIGIT_Y, GLYPH_W  # noqa: E402,F401  (the core's rule)
from core.figure import BACK_COPY, digit_xs as _digit_xs  # noqa: E402
PANEL_TOP = 80
"""The first row of the panels, which is the torso gap's (core/zones.py)."""


def digit_xs(count: int) -> list:
    """The x of each of *count* digits in a panel, centred at DIGIT_STEP
    (`core.figure.digit_xs`, the one the 3D tab paints with)."""
    return _digit_xs(count, PANEL_W)


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
        sx, sy = BACK_COPY[cell[0]]
        back = [[v & 0x7F for v in row]
                for row in back_indices(words, width, (sx, sy, PANEL_W, PANEL_H))]
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


# --- G4: the goalkeeper captain's armband, in a match ------------------------

KEEPER_ROOTS = ROOT_SECTIONS + (13,)
"""The roots a frame is cut at by `--keeper-armband`: 2 and 56 as in slot 5,
and 13, the body of the goalkeeper slot 7 draws -- on the ball, in a close
camera, with legs 18-21 and long arms 14 16 15 17 (K3D-TASK-08)."""
KEEPER_ARMBANDS = {13: {"armband": KEEPER_ARMBAND, "replaced": 15}}
"""The rule `--keeper-armband 7` measures (KITS-AJUSTES-3D.md G4): the
goalkeeper whose body is section 13 draws the captain's armband as section 92
in place of 15, its upper arm b.  92 has 15's vertices, vertex for vertex,
and other texels."""
PLANT_KEEPER_ARMBAND = 103
"""`--plant-keeper-armband` expects this section instead of 92: it also has
15's vertices, so only the drawing can tell the two apart."""


def same_vertices(index, one: int, other: int) -> bool:
    """Whether MODEL.BIN sections *one* and *other* hold the same vertices."""
    def points(i):
        sec = index["sections"].get((layout.MODEL, i))
        return sorted((v.x, v.y, v.z) for v in sec.vertices) if sec else None
    return points(one) is not None and points(one) == points(other)


KEEPER_ARMS = (57, 59, 99, 100)
"""The upper arms of the goalkeeper of slots 5 and 6 (`SLEEVE_LENGTHS`): the
pieces a captain's armband of that figure would take the place of."""


def keeper_candidates(index, drawn: set) -> list:
    """[(section, arm, "same" or "mirror")]: the MODEL.BIN sections, none of
    them `KEEPER_ARMS` and none in *drawn*, that hold the vertices of one of
    those arms or their mirror in z -- where an armband of that goalkeeper
    could be, by geometry alone."""
    def points(i, mirror=False):
        sec = index["sections"][(layout.MODEL, i)]
        return sorted((v.x, v.y, -v.z if mirror else v.z) for v in sec.vertices)
    count = 1 + max(i for name, i in index["sections"] if name == layout.MODEL)
    out = []
    for arm in KEEPER_ARMS:
        for i in range(count):
            if i in KEEPER_ARMS or i in drawn or i in SLEEVE_LENGTHS["short"]["worn"] \
                    or i in SLEEVE_LENGTHS["long"]["worn"]:
                continue
            if points(i) == points(arm):
                out.append((i, arm, "same"))
            elif points(i) == points(arm, True):
                out.append((i, arm, "mirror"))
    return out


def armband_zones(index, armband: int) -> list:
    """[(zone name, figure)] the texels of MODEL.BIN section *armband* touch."""
    from core import api

    names = set()
    for prim in index["sections"][(layout.MODEL, armband)].primitives:
        points = [work_point(u, v) for u, v in prim.texcoords]
        x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
        x1, y1 = max(p[0] for p in points), max(p[1] for p in points)
        names |= {(z.name, z.figure) for z in api.ZONES
                  if z.x <= x1 and x0 < z.x + z.w and z.y <= y1 and y0 < z.y + z.h}
    return sorted(names, key=lambda n: (str(n[1]), n[0]))


def keeper_armband_judge(report: dict, root: int, armband: int, replaced: int,
                         geometry_same: bool) -> list:
    """Failures of the goalkeeper's armband rule: some figure opened at
    *root* draws *armband*; none of those also draws *replaced*; each worn
    section has its own matrix and each figure its own translations; and
    *armband* has *replaced*'s vertices (*geometry_same*)."""
    out = ["figure %d: section %d shares its matrix with %s" % (f["figure"], section, same)
           for f in report["figures"] for section, same in f["worn"] if same]
    out += ["figure %d: a translation %.0f from the figure's median, over %d"
            % (f["figure"], f["spread"], FIGURE_SPREAD)
            for f in report["figures"] if f["spread"] > FIGURE_SPREAD]
    keepers = [o for o in report["orders"] if len(o) > 1 and o[1] == root]
    captains = [o for o in keepers if armband in o]
    if not captains:
        out.append("no figure opened at section %d draws section %d" % (root, armband))
    out += ["a figure draws %d and %d both: %s" % (armband, replaced, " ".join(map(str, o)))
            for o in captains if replaced in o]
    if not geometry_same:
        out.append("section %d does not have section %d's vertices" % (armband, replaced))
    return out


def run_keeper_armband(slot: int, cue: str, cache=None, plant=False) -> int:
    """`--keeper-armband SLOT`: section G4, what the goalkeeper captain draws."""
    import json

    import oracle as looks_oracle  # tools/looks

    image = os.environ[IMAGE_VARIABLE]
    path = cache or os.path.join(ATTACH_DIR, "matrix-%d.json" % slot)
    if cache and os.path.isfile(cache):
        with open(cache) as fh:
            kept = json.load(fh)
        print("  stops read from %s, no emulator" % cache)
    else:
        maps = looks_oracle.model_maps(image)
        with looks_oracle.Oracle(cue) as game:
            load_slot(game, slot, "matrix-%d" % slot)
            stops = matrix_stops(game, maps)
        kept = {"resident": {}, "stops": stops}
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(kept, fh)
        print("  stops kept at %s (--frame-json reads them back)" % path)
    index = model_index(image)
    passes = matrix_passes(matrix_pieces(kept["stops"], 1), KEEPER_ROOTS)
    failures = []
    for root, rule in sorted(KEEPER_ARMBANDS.items()):
        armband = PLANT_KEEPER_ARMBAND if plant else rule["armband"]
        replaced = rule["replaced"]
        report = matrix_report([p for p in passes if p[1]["section"] == root],
                               (armband, replaced))
        # matrix_report keeps the cut figures (last piece unnamed) in
        # "figures" for the matrices and out of "orders" (CORR-K3D-014).
        print("  %d stop(s); %d whole and %d cut figure(s) opened at section %d; "
              "the whole ones in the order:"
              % (len(kept["stops"]), len(report["figures"]) - report["cut"], report["cut"],
                 root))
        for order, n in sorted(report["orders"].items(), key=lambda kv: -kv[1]):
            print("    x%-3d %s" % (n, " ".join(str(s) for s in order)))
        spreads = [f["spread"] for f in report["figures"] if not f["cut"]]
        if spreads:
            print("  every whole figure's translations within %.0f to %.0f of its median "
                  "(limit %d)" % (min(spreads), max(spreads), FIGURE_SPREAD))
        same = same_vertices(index, armband, replaced)
        print("  section %d %s section %d's vertices; its texels touch: %s"
              % (armband, "has" if same else "does not have", replaced,
                 ", ".join("%s (%s)" % (name, ("player", "goalkeeper")[fig]
                                         if fig is not None else "shared")
                           for name, fig in armband_zones(index, armband))))
        # "In place of" rests on the shared vertices and the captain texels:
        # no figure of this family draws the replaced section (CORR-K3D-015).
        family = [p for p in passes if p[1]["section"] == root]
        print("  section %d is drawn by %d of these %d figure(s); its texels touch: %s"
              % (replaced, sum(1 for p in family if any(q["section"] == replaced for q in p)),
                 len(family),
                 ", ".join("%s (%s)" % (name, ("player", "goalkeeper")[fig]
                                         if fig is not None else "shared")
                           for name, fig in armband_zones(index, replaced))))
        seen = {i for p in passes for i in (q["section"] for q in p) if i is not None}
        for i, arm, how in keeper_candidates(index, seen):
            print("  not drawn here: section %d has the %svertices of goalkeeper arm %d; "
                  "its texels touch: %s"
                  % (i, "mirrored " if how == "mirror" else "", arm,
                     ", ".join("%s (%s)" % (name, ("player", "goalkeeper")[fig]
                                             if fig is not None else "shared")
                               for name, fig in armband_zones(index, i))))
        if plant:
            print("  PLANT  section %d expected as the armband, in place of %d"
                  % (armband, rule["armband"]))
        failures += keeper_armband_judge(report, root, armband, replaced, same)
        if not failures:
            print("  ok    the goalkeeper opened at section %d draws section %d in place of %d"
                  % (root, armband, replaced))
    for line in failures:
        print("  FAIL  %s" % line)
    return 1 if failures else 0


# --- G7: the EDIT PL. NUM screen -------------------------------------------

EDIT_HEADS = (24, 34)
"""The MODEL.BIN sections an EDT_MOD.BIN figure opens with: 24 is the head
the LOOKS SET draws (`pieces.HEAD_SECTION`) and the EDIT PL. NUM screen's
outfield player, 34 the one its goalkeeper opens with (slot 8, K3D-TASK-16)."""
EDIT_STOPS = 180
"""Matrix stops `--edit-number` takes of the still figure: 15 frames of 12."""
EDIT_TURN_STOPS = 1200
"""Matrix stops it takes after the confirming press, at most: 100 frames,
which have to hold the whole turn and the settling after it.  The run ends
earlier when the load stops firing for `EDIT_TURN_WAIT` seconds, and how
many stops it got is reported.  Measured in slot 8 after Circle: the load
keeps firing, all 1200 stops come in (99 whole figures), and no "stopped
firing" line is printed (`--edit-number 8 --frame-json
work/kits-oracle/edit-8-0.json`, CORR-K3D-021)."""
EDIT_TURN_WAIT = 20
"""Seconds `matrix_stops` waits for the next matrix load after the press
before taking the capture as over: shorter than the looks oracle's
`WATCH_SECONDS` (90), so a press that leaves the screen ends the capture
without the long wait."""
EDIT_YAW_STEP = 3.0
"""Degrees of torso yaw a frame has to move before it counts as turning:
the walk sways the torso by up to two degrees a frame (slot 8, front: -9.9
to -11.4), the turn moves it by 5.6 (4.2 once)."""
EDIT_BUTTONS = ("Circle", "Cross")
"""The buttons tried to confirm a player, in this order, the state reloaded
before each; the one that turns the figure is reported.  Measured first the
other way round: on this disc Cross leaves the screen for the team list."""
EDIT_TURN_LEAST = 90.0
"""Degrees the torso has to turn, start to end, before a press counts as
having turned the figure: the walk sways it by about a degree a frame."""
PLANT_EDIT_HEAD = 103
"""`--plant-edit-number` expects figures opened with this section, which
nothing draws."""
EDIT_EXPECT = {
    (8, 0): {"head": 34, "family": "goalkeeper", "number": 1, "frames": 30,
             "tag": "41", "set": 1},
    (8, 1): {"head": 24, "family": "player", "number": 5, "frames": 30,
             "tag": "41", "set": 1},
}
"""What G7 measured on the EDIT PL. NUM screen, by (slot, row of the list):
the head section the figure opens with, its family, the number on its back
panel, the frames the turn took, and the kit the screen wears (K3D-TASK-16,
`work/kits-oracle/edit-8-0.json` and `edit-8-1.json`).  `edit_number_judge`
asserts them; a (slot, row) with no entry is reported, not judged
(CORR-K3D-020)."""
EDIT_FRAMES_SLACK = 2
"""Frames the turn may take more or fewer than `EDIT_EXPECT` says."""
EDIT_ROW_MOVED = 0.005
"""How much of the screen a row down the list has to change for the press to
count: measured 0.0148 in slot 8 (the cursor's box and the row's colours),
under the 0.02 the looks oracle asks of a press by default."""


def edit_pieces(stops, lag: int = 1) -> list:
    """`matrix_pieces` keeping the file: the matrix of stop k belongs to the
    (file, section) the pointers name *lag* stops later, each as {"file",
    "section", "matrix"}; a stop naming nothing or several is (None, None)."""
    out = []
    for k in range(len(stops) - lag):
        named = stops[k + lag]["named"]
        file, section = (named[0][0], named[0][1]) if len(named) == 1 else (None, None)
        out.append({"file": file, "section": section,
                    "matrix": (tuple(stops[k]["rotation"]), tuple(stops[k]["translation"]))})
    return out


def edit_figures(pieces, heads=EDIT_HEADS) -> list:
    """The pieces cut into figures, each opening at a head section of
    MODEL.BIN (*heads*) and running to the piece before the next head.  The
    pieces before the first head and after the last are cut off."""
    starts = [k for k, p in enumerate(pieces)
              if p["file"] == layout.MODEL and p["section"] in heads]
    return [pieces[a:b] for a, b in zip(starts, starts[1:])]


def piece_yaw(matrix) -> float:
    """The turn about the view's vertical of one piece, in degrees: where the
    piece's own x axis points in the view's x-z plane (the rotation is row
    major, so that axis is the first column)."""
    import math

    rotation = matrix[0]
    return math.degrees(math.atan2(rotation[6], rotation[0]))


def figure_family(figure, lists: dict) -> str:
    """"player" or "goalkeeper" by which EDT_MOD.BIN list most of the figure's
    sections belong to (`scene._figure_sections`), else "neither"."""
    votes = {}
    for p in figure:
        if p["file"] != layout.EDT_MOD:
            continue
        for index, members in lists.items():
            if p["section"] in members:
                votes[index] = votes.get(index, 0) + 1
    if not votes:
        return "neither"
    return ("player", "goalkeeper")[max(votes, key=votes.get)]


def figure_torso(figure, names: dict):
    """The piece `pieces.py` names the torso, else the first EDT_MOD.BIN piece."""
    import pieces

    for p in figure:
        if names.get((p["file"], p["section"])) == pieces.TORSO:
            return p
    return next((p for p in figure if p["file"] == layout.EDT_MOD), figure[0])


def edit_turn(yaws: list, step: float = EDIT_YAW_STEP) -> dict:
    """What a run of torso yaws, one per frame, says about a turn: the first
    unbroken run of frames moving *step* degrees or more -- the yaw it starts
    and ends at, the frames it took and their steps.  What comes after the
    run (the walk's sway, on the back) is not the turn."""
    def delta(k):
        return (yaws[k] - yaws[k - 1] + 180.0) % 360.0 - 180.0

    moving = [k for k in range(1, len(yaws)) if abs(delta(k)) >= step]
    if not moving:
        return {"start": yaws[0] if yaws else None, "end": yaws[-1] if yaws else None,
                "first": None, "last": None, "frames": 0, "steps": []}
    run = [moving[0]]
    for k in moving[1:]:
        if k != run[-1] + 1:
            break
        run.append(k)
    return {"start": yaws[run[0] - 1], "end": yaws[run[-1]], "first": run[0],
            "last": run[-1], "frames": len(run), "steps": [delta(k) for k in run]}


def turned_through(turn: dict, least: float = EDIT_TURN_LEAST) -> bool:
    """Whether a run of yaws turned the torso by *least* degrees or more."""
    if not turn["frames"]:
        return False
    return abs((turn["end"] - turn["start"] + 180.0) % 360.0 - 180.0) >= least


def edit_panels(words, disc_words, width: int, height: int, shift: int = 0) -> list:
    """The back panels of a kit page that is not a match's grid: every block
    of pixels differing from the disc that is a panel's size is read as one,
    at its own corner, against the shirt back of the figure its half of the
    page belongs to.  *shift* moves the cell that many rows (the plant)."""
    glyph_set, ground = glyphs(words, width)
    out = []
    for x0, y0, x1, y1, pixels in diff_blocks(words, disc_words, width, height):
        if (x1 - x0 + 1, y1 - y0 + 1) != (PANEL_W, PANEL_H):
            continue
        figure = 0 if x0 < width else 1
        cell = (figure, x0, y0 + shift)
        sx, sy = BACK_COPY[figure]
        back = [[v & 0x7F for v in row]
                for row in back_indices(words, width, (sx, sy, PANEL_W, PANEL_H))]
        one = read_panel(words, width, cell, back, glyph_set, ground)
        one["pixels"] = pixels
        out.append(one)
    return out


def edit_number_judge(report: dict, head: int, panels: list, expect: dict = None) -> list:
    """Failures of what G7 asks: some figure opens at *head*; every figure
    is one family and has its own translations; the turn moved the torso and
    settled; and after it the panel of the family shown -- the torso gap of
    that figure, `BACK_COPY`'s corner shifted down by the gap -- holds the
    number, read by the match's rule (`panels_judge`).  The other figure's
    panel is only reported: the screen writes its shirt back with no digit.
    With *expect* (an `EDIT_EXPECT` entry) the family, the number, the
    frames of the turn and the kit have to be the measured ones too."""
    out = []
    if expect is not None:
        out += ["figure %d is the %s, %s expected" % (f["figure"], f["family"], expect["family"])
                for f in report["figures"]
                if f["family"] not in ("neither", expect["family"])]
        turn = report.get("turn") or {}
        if abs(turn.get("frames", 0) - expect["frames"]) > EDIT_FRAMES_SLACK:
            out.append("the turn took %d frame(s), %d expected (slack %d)"
                       % (turn.get("frames", 0), expect["frames"], EDIT_FRAMES_SLACK))
        if (report.get("tag"), report.get("set")) != (expect["tag"], expect["set"]):
            out.append("the screen wears TEX_%s set %s, TEX_%s set %s expected"
                       % (report.get("tag"), report.get("set"), expect["tag"], expect["set"]))
        numbers = [p["number"] for p in panels
                   if ("player", "goalkeeper")[p["cell"][0]] == expect["family"]]
        if numbers and numbers != [expect["number"]]:
            out.append("the %s's back panel holds %s, number %d expected"
                       % (expect["family"], ", ".join(map(str, numbers)), expect["number"]))
    if not any(f["head"] == head for f in report["figures"]):
        out.append("no figure opened at section %d" % head)
    out += ["figure %d: a translation %.0f from the figure's median, over %d"
            % (f["figure"], f["spread"], FIGURE_SPREAD)
            for f in report["figures"] if f["spread"] > FIGURE_SPREAD]
    out += ["figure %d is of no family: %s" % (f["figure"], f["order"])
            for f in report["figures"] if f["family"] == "neither"]
    turn = report.get("turn")
    if turn is not None:
        if not turned_through(turn):
            out.append("the torso did not turn %.0f degrees through the per-piece matrix "
                       "load after the press" % EDIT_TURN_LEAST)
        elif turn["last"] is not None and turn["last"] >= report["turn_frames"] - 1 \
                and not report.get("turn_ended"):
            out.append("the torso was still turning at the last frame captured")
    families = {f["family"] for f in report["figures"]}
    shown = [p for p in panels if ("player", "goalkeeper")[p["cell"][0]] in families]
    if not shown:
        out.append("no panel of %dx%d of the figure shown (%s) differs from the disc after "
                   "the turn" % (PANEL_W, PANEL_H, ", ".join(sorted(families)) or "none"))
    out += panels_judge(shown)
    return out


def edit_figure_report(figures, lists: dict, names: dict) -> dict:
    """{figures, orders}: each figure's head, family, order, torso yaw and
    translation spread, and the count of each order drawn."""
    out, orders = [], {}
    for number, figure in enumerate(figures):
        order = " ".join("%s:%s" % (p["file"].rsplit("/", 1)[-1], p["section"])
                         if p["file"] else "?" for p in figure)
        orders[order] = orders.get(order, 0) + 1
        translations = [p["matrix"][1] for p in figure]
        median = [sorted(t[i] for t in translations)[len(translations) // 2] for i in range(3)]
        spread = max(sum((t[i] - median[i]) ** 2 for i in range(3)) ** 0.5
                     for t in translations)
        torso = figure_torso(figure, names)
        out.append({"figure": number, "head": figure[0]["section"], "order": order,
                    "family": figure_family(figure, lists), "spread": spread,
                    "yaw": piece_yaw(torso["matrix"]), "torso": torso["matrix"][1]})
    return {"figures": out, "orders": orders}


def _edit_page(game, page_x: int):
    """The uniform page at *page_x* as 15-bit halfwords (`read_back`'s reading)."""
    import oracle as looks_oracle  # tools/looks

    record = records_of(_screen_body())[UNIFORM_RECORD]
    rows = looks_oracle.vram_region(game, page_x, record.y, record.w, record.h)
    return [(p[0] >> 3) | (p[1] >> 3) << 5 | (p[2] >> 3) << 10 for row in rows for p in row]


def _edit_kit(game, bodies: dict, label: str):
    """(hits, tag, set, page x) of the kit the screen holds in VRAM, by the
    same search `--slot` makes on a dump."""
    path = os.path.join(game.out_dir, "%s-vram.png" % label)
    if os.path.exists(path):
        os.remove(path)
    game.client.call("dump_vram", path=path, format="png")
    hits = search(vram_rows(path), bodies)
    for tag, index, at, flat, shared in hits:
        if index in (0, 1, 4, 5) and not flat and not shared:
            return hits, tag, SETS[index], at[0][0]
    return hits, None, None, None


def edit_capture(game, maps, bodies: dict, slot: int, player: int,
                 buttons=EDIT_BUTTONS) -> dict:
    """Everything `--edit-number` reads from the running screen: the still
    figure's stops, the kit, the uniform page before the press, the press
    that turned the figure and the stops through the turn, and the page
    after it."""
    import oracle as looks_oracle  # tools/looks

    name = "edit-%d-%d%s" % (slot, player,
                             "" if tuple(buttons) == EDIT_BUTTONS else "-" + "-".join(buttons))

    def arrive(label):
        load_slot(game, slot, label)
        for _ in range(player):
            game.press("Down", least=EDIT_ROW_MOVED)
        if player:
            game.capture(name + "-row")

    arrive(name + "-front")
    out = {"front": matrix_stops(game, maps, EDIT_STOPS)}
    hits, tag, kit_set, page_x = _edit_kit(game, bodies, name + "-front")
    out.update(hits=[list(h[:2]) + [list(h[2]), h[3], h[4]] for h in hits],
               tag=tag, set=kit_set, page_x=page_x)
    if page_x is not None:
        out["page_front"] = _edit_page(game, page_x)
    out["button"], out["turn"], out["pressed"] = None, [], {}
    for n, button in enumerate(buttons):
        if n:
            arrive(name + "-again")
        game.client.call("press_button", button=button,
                         duration_frames=looks_oracle.CONFIRM_FRAMES)
        stops = matrix_stops(game, maps, EDIT_TURN_STOPS, partial=True, wait=EDIT_TURN_WAIT)
        yaws = [piece_yaw(figure_torso(f, {})["matrix"])
                for f in edit_figures(edit_pieces(stops))]
        out["turn"] = stops
        out["pressed"][button] = {"stops": len(stops), "figures": len(yaws),
                                  "turned": turned_through(edit_turn(yaws))}
        if turned_through(edit_turn(yaws)):
            out["button"] = button
            break
        out.setdefault("ignored", []).append(button)
    game.capture(name + "-back")
    if page_x is not None:
        out["page_back"] = _edit_page(game, page_x)
    return out


def run_edit_number(slot: int, cue: str, player: int = 0, cache=None, plant: bool = False,
                    button: str = None) -> int:
    """`--edit-number SLOT [--player ROW]`: G7, what the EDIT PL. NUM screen
    draws -- the family of the figure, its kit, its still pose, the turn a
    confirming press makes, and the number panel written for the back."""
    import json

    import scene

    import oracle as looks_oracle  # tools/looks
    from core import figure as _figure

    image = os.environ[IMAGE_VARIABLE]
    suffix = "-" + button if button else ""
    path = cache or os.path.join(ATTACH_DIR, "edit-%d-%d%s.json" % (slot, player, suffix))
    if cache and os.path.isfile(cache):
        with open(cache) as fh:
            kept = json.load(fh)
        print("  capture read from %s, no emulator" % cache)
    else:
        maps = looks_oracle.model_maps(image)
        bodies = read_kits(image)
        with looks_oracle.Oracle(cue) as game:
            kept = edit_capture(game, maps, bodies, slot, player,
                                (button,) if button else EDIT_BUTTONS)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(kept, fh)
        print("  capture kept at %s (--frame-json reads it back)" % path)
    geometry = _figure.read_geometry(image)
    lists = scene._figure_sections(geometry)
    names = scene.piece_names(geometry)
    expect = EDIT_EXPECT.get((slot, player))
    head = PLANT_EDIT_HEAD if plant else expect["head"] if expect else None
    if expect is None:
        print("  no measured expectation for slot %d row %d (EDIT_EXPECT): the head, family, "
              "number and turn are printed, not judged" % (slot, player))
    reports = {}
    for phase in ("front", "turn"):
        figures = edit_figures(edit_pieces(kept[phase]))
        report = edit_figure_report(figures, lists, names)
        reports[phase] = report
        print("  %s: %d stop(s), %d whole figure(s); the order each draws, head first:"
              % (phase, len(kept[phase]), len(figures)))
        for order, n in sorted(report["orders"].items(), key=lambda kv: -kv[1]):
            family = next(f["family"] for f in report["figures"] if f["order"] == order)
            print("    x%-3d %s  (%s)" % (n, order, family))
        if report["figures"]:
            spreads = [f["spread"] for f in report["figures"]]
            yaws = [f["yaw"] for f in report["figures"]]
            print("  %s: every figure's translations within %.0f to %.0f of its median "
                  "(limit %d); torso yaw %.1f to %.1f degrees, torso at %s"
                  % (phase, min(spreads), max(spreads), FIGURE_SPREAD, min(yaws), max(yaws),
                     report["figures"][0]["torso"]))
        if head is None and report["figures"]:
            head = report["figures"][0]["head"]
    print("  kit: %s" % (", ".join(
        "TEX_%s record %d %s at (%d,%d)" % (tag, index, NAMES[index], at[0][0], at[0][1])
        for tag, index, at, flat, shared in kept["hits"] if not flat) or "nothing found"))
    print("  the screen wears TEX_%s set %s, uniform page at (%s,256)"
          % (kept["tag"], kept["set"], kept["page_x"]))
    turn_yaws = [f["yaw"] for f in reports["turn"]["figures"]]
    turn = edit_turn(turn_yaws)
    print("  torso yaw per frame after the press: %s"
          % " ".join("%.0f" % v for v in turn_yaws))
    if kept["button"]:
        print("  %s turned the figure%s: torso yaw %.1f to %.1f in %d frame(s) (frames %s to %s "
              "of %d), steps %s"
              % (kept["button"],
                 " (%s ignored)" % ", ".join(kept["ignored"]) if kept.get("ignored") else "",
                 turn["start"], turn["end"], turn["frames"], turn["first"], turn["last"],
                 len(turn_yaws),
                 " ".join("%+.1f" % v for v in turn["steps"][:12])
                 + (" …" if len(turn["steps"]) > 12 else "")))
    else:
        print("  no button of %s turned the figure through the per-piece matrix load; the "
              "last press's torso yaw %s to %s"
              % (", ".join(EDIT_BUTTONS), turn["start"], turn["end"]))
    for pressed, what in sorted(kept.get("pressed", {}).items()):
        print("  %s pressed: %s the figure; the per-piece matrix load gave %d of %d stop(s) "
              "(%d whole figure(s))%s"
              % (pressed, "turned" if what["turned"] else "did not turn", what["stops"],
                 EDIT_TURN_STOPS, what["figures"],
                 ", then stopped firing for %d s" % EDIT_TURN_WAIT
                 if what["stops"] < EDIT_TURN_STOPS else ""))
    ended = len(kept["turn"]) < EDIT_TURN_STOPS
    if ended:
        print("  the per-piece matrix load stopped firing after %d stop(s), %d whole figure(s)"
              % (len(kept["turn"]), len(turn_yaws)))
    report = dict(reports["front"], turn=turn, turn_frames=len(turn_yaws), turn_ended=ended,
                  tag=kept.get("tag"), set=kept.get("set"))
    report["figures"] = reports["front"]["figures"] + reports["turn"]["figures"]
    disc_words = None
    if kept.get("tag"):
        body = _body(kept["tag"])
        image_record = UNIFORM_RECORD if kept["set"] == 1 else UNIFORM_SET2
        disc_words = [five(v) for v in payload(body, records_of(body)[image_record])]
    record = records_of(_screen_body())[UNIFORM_RECORD]
    panels = []
    for when in ("page_front", "page_back"):
        if disc_words is None or when not in kept:
            print("  %s: not read" % when)
            continue
        blocks = diff_blocks(kept[when], disc_words, record.w, record.h)
        print("  %s: %d block(s) differ from the disc: %s"
              % (when, len(blocks), "; ".join("(%d,%d)-(%d,%d) %d px" % b for b in blocks[:6])
                 or "none"))
        shift = -1 if plant and when == "page_back" else 0
        read = edit_panels(kept[when], disc_words, record.w, record.h, shift)
        for one in read:
            figure, cx, cy = one["cell"]
            print("    %-10s panel (%3d,%3d): number %-4s digits %s; %d pixel(s) the rule "
                  "does not explain"
                  % (("player", "goalkeeper")[figure], cx, cy, one["number"],
                     " ".join("%d at (%d,%d)" % (d, x, y) for x, y, d in one["digits"]) or "none",
                     one["unexplained"]))
        picture = os.path.join(ATTACH_DIR, "edit-%d-%d%s-%s.png"
                               % (slot, player, suffix, when[5:]))
        save_picture(picture, kept[when], record.w, record.h, _body(kept["tag"]), kept["set"])
        print("    picture: %s" % picture)
        if when == "page_back":
            panels = read
    for phase, kind in (("front", "front"), ("turn", "back")):
        figures = reports[phase]["figures"]
        if not figures:
            continue
        whole = edit_figures(edit_pieces(kept[phase]))[-1]
        os.makedirs(POSE_DIR, exist_ok=True)
        pose_path = os.path.join(POSE_DIR, "slot%d-row%d%s-%s.json" % (slot, player, suffix, kind))
        with open(pose_path, "w") as fh:
            json.dump({"slot": slot, "player": player, "pose": kind,
                       "head": whole[0]["section"],
                       "pieces": [{"file": p["file"], "section": p["section"],
                                   "name": names.get((p["file"], p["section"])),
                                   "rotation": list(p["matrix"][0]),
                                   "translation": list(p["matrix"][1])} for p in whole]},
                      fh, indent=1)
        print("  %s pose kept at %s (%d pieces)" % (kind, pose_path, len(whole)))
    if plant:
        print("  PLANT  figures expected to open at section %d, and every panel read one row up"
              % PLANT_EDIT_HEAD)
    failures = edit_number_judge(report, head, panels, expect)
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        families = {f["family"] for f in report["figures"]}
        print("  ok    the %s opens at section %d, %s turned it %.0f degrees in %d frame(s), "
              "and its back panel holds number %s"
              % (", ".join(sorted(families)), head, kept["button"],
                 (turn["end"] - turn["start"] + 180.0) % 360.0 - 180.0, turn["frames"],
                 ", ".join(str(p["number"]) for p in panels
                           if ("player", "goalkeeper")[p["cell"][0]] in families)))
    return 1 if failures else 0


# --- G8: the replays of slots 9 and 10, the captain up close (K3D-TASK-17) ---

REPLAY_SUBMITS = 13
"""Stops at the GPU list submit a `--replay` capture takes: three a frame, so
four whole frames after the first, cut-off one -- two at least to say the
pose is still."""
REPLAY_ROTATE = ("R1", "L1")
"""The buttons that turn the replay camera about the player it follows (the
user's account, KITS-AJUSTES-3D.md G8); `--rotate` picks one, R1 by default."""
REPLAY_BACK = 150.0
"""Degrees the torso has to have turned from its front yaw before the back
capture is taken: past this the panel faces the camera."""
REPLAY_ROTATE_MOST = 40
"""Taps of the rotate button a run may make before it gives the back up."""
REPLAY_YAW_STOPS = (36, 300)
"""Matrix stops read after each tap to know the torso's yaw: the first count,
and the second only if the followed figure is not in it.  Facing the figure the
zoomed replay draws it alone, twelve stops a frame; turned toward the pitch it
draws the other players too, and in slot 9 the 36 stops of three lone frames
no longer reached the goalkeeper at the 18th tap of R1.  Reading 300 after
every tap is no answer either: some 75 frames a tap, and by the 14th tap of
slot 10 the camera had drawn back to 12636 and R1 no longer moved it."""
REPLAY_STILL = 0
"""GTE units the followed figure's matrices may differ by between two frames
of the paused replay and still count as one still pose."""
REPLAY_SETTLE = 2
"""Frames stepped after a capture before the frame buffer is read: both
buffers then hold a frame of the still pose."""
REPLAY_IDLE_STEP = 30
"""Frames `--replay-idle` steps between two looks at the screen."""
REPLAY_HUD = (0.06, 0.88, 0.18, 0.93)
"""The fractional box of the replay's "SAVE" plate, bottom left: the screen
is the replay while it stands.  The whole screen will not do -- the crowd's
flags wave in the paused replay and move it by 0.0357 in 150 frames of
slot 9."""
REPLAY_IDLE_MOST = 9000
"""Frames `--replay-idle` lets run before it says the replay did not end."""
REPLAY_IDLE = {9: 390, 10: 390}
"""Slot -> the frames the paused replay lasts with no input, as `--replay-idle`
measured it (K3D-TASK-17: left between 360 and 390 in both, stepped 30 at a
time); a capture has to stay under it."""
REPLAY_EXPECT = {slot: {"root": 13, "head": 34, "armband": KEEPER_ARMBAND, "replaced": 15,
                        "panel": (576, 100, 104), "number": 1} for slot in (9, 10)}
"""Slot -> what G8 measured of the followed figure (K3D-TASK-17, Marcos in
both, `work/kits-oracle/replay-9.json` and `replay-10.json`): its root and head, the
armband in place of what, the panel cell its back samples and the number in
it.  `replay_judge` asserts them; a slot with no entry is printed, not
judged."""
PLANT_REPLAY_ROOT = 103
"""`--plant-replay` expects the followed figure to open at this section, which
nothing draws."""


def frame_now(game) -> int:
    """The emulator's frame counter."""
    return game.client.call("get_status").get("frame_number")


def replay_figures(pieces, roots=KEEPER_ROOTS) -> list:
    """One frame's pieces cut into figures: each opens at a root and takes the
    piece before it, its head, up to the head of the next.  The last piece of
    the frame is the one the draw lag leaves unnamed, so the last figure is
    one piece short."""
    starts = [k for k, p in enumerate(pieces) if p["section"] in roots and k > 0]
    out = []
    for at, start in enumerate(starts):
        end = starts[at + 1] - 1 if at + 1 < len(starts) else len(pieces)
        out.append(pieces[start - 1:end])
    return out


def figure_depth(figure) -> float:
    """The median z of a figure's translations: the view's depth of it."""
    zs = sorted(p["matrix"][1][2] for p in figure)
    return zs[len(zs) // 2]


def replay_focus(figures, nth: int = 0):
    """The figure the camera follows: the *nth* nearest by `figure_depth`
    (0, the nearest; the plant asks for the next one).  None if there is not
    that many."""
    ranked = sorted(figures, key=figure_depth)
    return ranked[nth] if nth < len(ranked) else None


def replay_frames(capture: dict, nth: int = 0) -> list:
    """[{"head", "figures", "focus"}] of every frame of a `pose_capture`, the
    pieces named one stop late as `matrix_pieces` does within the frame."""
    out = []
    for frame in pose_frames(capture):
        pieces = matrix_pieces(frame["stops"], 1)
        for piece, stop in zip(pieces, frame["stops"]):
            piece["projection"] = stop["projection"]
        figures = replay_figures(pieces)
        out.append({"head": frame["head"], "figures": figures,
                    "focus": replay_focus(figures, nth)})
    return out


def pose_change(one, other) -> int:
    """The largest difference, entry by entry, between two figures' matrices;
    None when they are not the same pieces."""
    if [p["section"] for p in one] != [p["section"] for p in other]:
        return None
    return max(abs(a - b) for p, q in zip(one, other)
               for a, b in zip(p["matrix"][0] + p["matrix"][1], q["matrix"][0] + q["matrix"][1]))


def section_samples(group, index, section: int) -> list:
    """The primitives of a player group whose four texels are a primitive of
    MODEL.BIN section *section* on the disc."""
    sec = index["sections"].get((layout.MODEL, section))
    if sec is None:
        return []
    held = {tuple(tuple(t) for t in prim.texcoords) for prim in sec.primitives}
    return [one for one in group if tuple(tuple(t) for t in one["uv"]) in held]


def shading_of(samples) -> dict:
    """What the GPU is told to do with the texels of *samples*: how many are
    shaded per corner, how many raw (texture not modulated), the CLUTs and
    pages, and the range of the corner colours."""
    colours = [c for one in samples for c in (one.get("rgb") or [])]
    return {"n": len(samples),
            "shaded": sum(1 for one in samples if one["code"] & 16),
            "raw": sum(1 for one in samples if one["code"] & 1),
            "semi": sum(1 for one in samples if one["code"] & 2),
            "cluts": sorted({tuple(one["clut"]) for one in samples}),
            "pages": sorted({tuple(one["page"]) for one in samples}),
            "low": tuple(min(c[i] for c in colours) for i in range(3)) if colours else None,
            "high": tuple(max(c[i] for c in colours) for i in range(3)) if colours else None}


NEUTRAL = 128
"""The colour a modulated texel is drawn unchanged under: the GPU multiplies
by colour / 128."""


def triangle_pixels(xy, uv, rgb):
    """[(x, y, u, v, (r, g, b))] of the pixel centres inside one triangle, with
    texel and colour interpolated the way `core/raster.py` interpolates UV."""
    (x0, y0), (x1, y1), (x2, y2) = xy
    area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if area == 0:
        return []
    out = []
    for py in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
        for px in range(min(x0, x1, x2), max(x0, x1, x2) + 1):
            sx, sy = px + 0.5, py + 0.5
            a = ((x1 - sx) * (y2 - sy) - (x2 - sx) * (y1 - sy)) / area
            b = ((x2 - sx) * (y0 - sy) - (x0 - sx) * (y2 - sy)) / area
            g = 1.0 - a - b
            if a < 0 or b < 0 or g < 0:
                continue
            u = a * uv[0][0] + b * uv[1][0] + g * uv[2][0]
            v = a * uv[0][1] + b * uv[1][1] + g * uv[2][1]
            colour = tuple(a * rgb[0][i] + b * rgb[1][i] + g * rgb[2][i] for i in range(3))
            out.append((px, py, int(u), int(v), colour))
    return out


def sample_pixels(one) -> list:
    """`triangle_pixels` of a quad as the GPU splits it, (0 1 2) and (1 2 3)."""
    rgb = one.get("rgb") or [(NEUTRAL,) * 3] * len(one["xy"])
    out = triangle_pixels(one["xy"][:3], one["uv"][:3], rgb[:3])
    if len(one["xy"]) == 4:
        out += triangle_pixels(one["xy"][1:], one["uv"][1:], rgb[1:])
    return out


def texel_colour(texture: dict, page, clut, u: int, v: int):
    """The 15-bit texel at (u, v) of an 8-bit page, through its CLUT, as five-
    bit (r, g, b); None if the capture did not keep that page or CLUT.  Odd
    texels lose bit 7 on the way through the PNG, as `save_picture` says."""
    words = texture["pages"].get("%d,%d,%d" % (tuple(page) + (KIT_BITS,)))
    row = texture["cluts"].get("%d,%d" % tuple(clut))
    if words is None or row is None:
        return None
    half = words[v * TEXTURE_HALFWORDS + u // 2]
    index = (half >> (8 * (u & 1))) & 0xFF
    if u & 1:
        index &= 0x7F
    return row[index] if index < len(row) else None


TEXTURE_HALFWORDS = 128
"""Halfwords across an 8-bit texture page: 256 texels."""


def colour_confront(group, buffer, texture: dict, sections: dict) -> dict:
    """Section -> the game's drawn pixels against the texels they sample:
    the mean frame-buffer colour, the mean texel (what the 3D tab paints), the
    mean texel times the corner colour / 128 (what the GPU's modulation
    gives), and the mean distance of the game's to each.  A pixel counts for
    the primitive of the group drawn last over it -- the list's order is the
    GPU's -- so what a later quad covers is not read as an earlier one's."""
    owners = {}
    for k, one in enumerate(group):
        for px, py, _u, _v, _c in sample_pixels(one):
            owners[(px, py)] = k
    x0, y0 = buffer["origin"]
    out = {}
    for section, samples in sections.items():
        rows = []
        for one in samples:
            if one["bits"] != KIT_BITS:
                continue        # only 8-bit pages are kept (`replay_capture`)
            k = next(i for i, g in enumerate(group) if g is one)
            for px, py, u, v, colour in sample_pixels(one):
                if owners.get((px, py)) != k:
                    continue
                by, bx = py - y0, px - x0
                if not (0 <= by < len(buffer["rows"]) and 0 <= bx < len(buffer["rows"][0])):
                    continue
                texel = texel_colour(texture, one["page"], one["clut"], u, v)
                if texel is None:
                    continue
                game = buffer["rows"][by][bx]
                shaded = tuple(min(31, int(t * c / NEUTRAL)) for t, c in zip(texel, colour))
                rows.append((game, texel, shaded))
        if not rows:
            out[section] = None
            continue
        mean = lambda i: tuple(sum(r[i][c] for r in rows) / len(rows) for c in range(3))  # noqa: E731
        far = lambda i: sum(abs(r[0][c] - r[i][c]) for r in rows for c in range(3)) / (3.0 * len(rows))  # noqa: E731
        out[section] = {"pixels": len(rows), "game": mean(0), "texel": mean(1),
                        "shaded": mean(2), "texel_far": far(1), "shaded_far": far(2)}
    return out


def panel_samples(group) -> dict:
    """Panel cell -> the primitives of *group* whose four texels lie in it:
    which back panel of the page the figure's torso shows."""
    out = {}
    for one in group:
        if kit_image_of(one) != "uniform":
            continue
        for figure, cx, cy in panel_cells():
            if all(cx <= u < cx + PANEL_W and cy <= v < cy + PANEL_H for u, v in one["uv"]):
                out.setdefault((figure, cx, cy), []).append(one)
    return out


def replay_capture(game, maps, bodies: dict, index, slot: int, rotate: str) -> dict:
    """Everything `--replay` reads from the paused replay: the front capture
    (`pose_capture`) with the frame buffer under the followed figure and the
    texture pages and CLUTs it samples; the kit pages; then, from the state
    reloaded, taps of *rotate* until the torso has turned `REPLAY_BACK`, and
    the back capture.  Each run counts the frames it spends."""
    import oracle as looks_oracle  # tools/looks

    label = "replay-%d" % slot
    load_slot(game, slot, label)
    start = frame_now(game)
    front = pose_capture(game, maps, REPLAY_SUBMITS)
    front_frames = frame_now(game) - start
    game.step(REPLAY_SETTLE)
    hits, tag, kit_set, page_x = _edit_kit(game, bodies, label)
    frames = replay_frames(front)
    head = frames[-1]["head"] if frames else None
    samples = front["lists"].get("%d" % head, []) if head is not None else []
    figure, fit = figure_group(frames[-1]["focus"] if frames else None, samples, index)
    buffer, texture = None, {"pages": {}, "cluts": {}}
    # the drawing offset rides in the one-node list submitted before each
    # ordering table, not in the table the figure is in: the last one set
    offsets = [front["offsets"].get("%d" % e["head"]) for e in front["events"]
               if e["kind"] == "submit"]
    offset = next((o for o in reversed(offsets) if o is not None), None)
    if figure and offset is not None:
        box = tuple(int(round(v)) for v in fit["box"])
        rows = looks_oracle.vram_region(game, offset[0] + box[0], offset[1] + box[1],
                                        box[2] - box[0] + 1, box[3] - box[1] + 1)
        buffer = {"origin": box[:2], "offset": offset,
                  "rows": [[looks_oracle._five_bits(p) for p in row] for row in rows]}
        for page in sorted({tuple(one["page"]) for one in figure if one["bits"] == KIT_BITS}):
            rows = looks_oracle.vram_region(game, page[0], page[1], TEXTURE_HALFWORDS, 256)
            texture["pages"]["%d,%d,%d" % (page + (KIT_BITS,))] = [
                (p[0] >> 3) | (p[1] >> 3) << 5 | (p[2] >> 3) << 10 for row in rows for p in row]
        for clut in sorted({tuple(one["clut"]) for one in figure}):
            row = looks_oracle.vram_region(game, clut[0], clut[1], 256, 1)[0]
            texture["cluts"]["%d,%d" % clut] = [looks_oracle._five_bits(p) for p in row]
    pages = {}
    for x in sorted({one["page"][0] for one in samples if is_figure(one)}):
        pages["%d" % x] = _edit_page(game, x)
    game.capture(label + "-front")
    load_slot(game, slot, label + "-turn")
    start = frame_now(game)
    yaws, depths, turned, tapped = [], [], None, start
    root = frames[-1]["focus"][1]["section"] if frames and frames[-1]["focus"] else None
    for _tap in range(REPLAY_ROTATE_MOST):
        try:
            tapped = frame_now(game)
            game.press(rotate)
        except looks_oracle.NotArrived as exc:
            turned = "refused: %s" % exc
            break
        # the followed figure's own family: past the goal line the camera
        # sees another goalkeeper nearer than a cut-off frame's own one
        focus = None
        for count in REPLAY_YAW_STOPS:
            stops = matrix_stops(game, maps, count, partial=True)
            focus = replay_focus([f for f in replay_figures(matrix_pieces(stops, 1))
                                  if f[1]["section"] == root])
            if focus is not None:
                break
        if focus is None:
            turned = "no figure in the stops after the tap"
            break
        yaws.append(piece_yaw(focus[1]["matrix"]))
        depths.append([focus[1]["section"], figure_depth(focus)])
        front_yaw = piece_yaw(frames[-1]["focus"][1]["matrix"]) if frames else yaws[0]
        if abs((yaws[-1] - front_yaw + 180.0) % 360.0 - 180.0) >= REPLAY_BACK:
            turned = "back"
            break
    back = pose_capture(game, maps, REPLAY_SUBMITS) if turned == "back" else None
    turn_frames = frame_now(game) - start
    back_frames = frame_now(game) - tapped
    back_samples = []
    if back is not None:
        back_frames_list = replay_frames(back)
        if back_frames_list:
            back_samples = back["lists"].get("%d" % back_frames_list[-1]["head"], [])
        for x in sorted({one["page"][0] for one in back_samples if is_figure(one)}):
            pages.setdefault("%d" % x, _edit_page(game, x))
    game.capture(label + "-back")
    return {"front": front, "back": back, "front_frames": front_frames,
            "back_frames": back_frames, "turn_frames": turn_frames, "rotate": rotate, "yaws": yaws, "depths": depths, "turned": turned,
            "hits": hits, "tag": tag, "set": kit_set, "page_x": page_x, "pages": pages,
            "buffer": buffer, "texture": texture}


def replay_idle(game, slot: int) -> dict:
    """{"frames", "moved"}: how many frames the paused replay of *slot* lasts
    with no input before the screen leaves it, stepped `REPLAY_IDLE_STEP` at a
    time; frames None if it had not left by `REPLAY_IDLE_MOST`."""
    import oracle as looks_oracle  # tools/looks

    load_slot(game, slot, "replay-idle-%d" % slot)
    reference = game.capture("replay-idle-%d-start" % slot)
    start = frame_now(game)
    moved = 0.0
    while frame_now(game) - start < REPLAY_IDLE_MOST:
        game.step(REPLAY_IDLE_STEP)
        shot = game.capture("replay-idle-%d-now" % slot)
        moved = reference.difference(shot, looks_oracle.pixels(reference, REPLAY_HUD))
        if moved > looks_oracle.MOVED:
            game.capture("replay-idle-%d-end" % slot)
            return {"frames": frame_now(game) - start, "moved": moved}
    return {"frames": None, "moved": moved}


def _restore_samples(capture) -> None:
    """The tuples a JSON round trip turned into lists, put back."""
    if capture is None:
        return
    for one in capture["lists"].values():
        for s in one:
            s.update(page=tuple(s["page"]), clut=tuple(s["clut"]),
                     uv=[tuple(t) for t in s["uv"]], xy=[tuple(t) for t in s["xy"]],
                     rgb=[tuple(c) for c in s["rgb"]] if s.get("rgb") else None)


def figure_group(figure, samples, index):
    """The textured quads of a frame that fall inside the screen box of
    *figure*'s own vertices, each through its piece's matrix, grown by
    `POSE_MARGIN`; and each piece's mean pixel error there (`piece_error`).
    Grouping by touching kit primitives (`players`) splits a figure drawn this
    close, and the box needs no kit at all."""
    if figure is None:
        return None, None
    projection = figure[0]["projection"]
    points = []
    for piece in figure:
        sec = index["sections"].get((layout.MODEL, piece["section"]))
        for v in (sec.vertices if sec else []):
            at = pose_project(piece["matrix"][0], piece["matrix"][1], projection, (v.x, v.y, v.z))
            if at is not None:
                points.append(at)
    if not points:
        return None, None
    box = (min(p[0] for p in points) - POSE_MARGIN, min(p[1] for p in points) - POSE_MARGIN,
           max(p[0] for p in points) + POSE_MARGIN, max(p[1] for p in points) + POSE_MARGIN)
    group = [one for one in samples if len(one["uv"]) == 4 and all(
        box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])]
    rows = []
    for piece in figure:
        sec = index["sections"].get((layout.MODEL, piece["section"]))
        error, matched = (piece_error(piece, projection, sec, group) if sec else (None, 0))
        rows.append({"section": piece["section"], "error": error, "matched": matched})
    return group, {"box": box, "rows": rows}


def replay_judge(report: dict, expect: dict, plant: bool = False) -> list:
    """Failures of what G8 measured: the followed figure opens at the expected
    root with the expected head, draws the armband and not the arm it
    replaces, holds one still pose, turned its back, shows the expected panel
    and number there, and every capture stayed under the replay's idle
    frames."""
    out = []
    focus = report["focus"]
    order = [p["section"] for p in focus] if focus is not None else []
    root = PLANT_REPLAY_ROOT if plant else expect["root"]
    if focus is None:
        out.append("no %s figure in the frame" % ("second" if plant else "followed"))
    elif len(order) < 2 or order[1] != root:
        out.append("the followed figure opens at %s, not at section %d"
                   % (order[1] if len(order) > 1 else None, root))
    if focus is not None and order[0] != expect["head"]:
        out.append("the followed figure's head is section %s, not %d" % (order[0], expect["head"]))
    if focus is not None and expect["armband"] not in order:
        out.append("the followed figure does not draw section %d" % expect["armband"])
    if expect["replaced"] in order:
        out.append("the followed figure draws section %d beside the armband" % expect["replaced"])
    if report["still"] is None or report["still"] > REPLAY_STILL:
        out.append("the pose changed by %s between two frames, over %d"
                   % (report["still"], REPLAY_STILL))
    if report["turned"] != "back":
        out.append("the back was not reached: %s" % report["turned"])
    if report["panel"] != expect["panel"]:
        out.append("the back samples panel %s, not %s" % (report["panel"], expect["panel"]))
    if report["number"] != expect["number"]:
        out.append("the panel holds %s, not %d" % (report["number"], expect["number"]))
    out += ["panel %s: %s" % (report["panel"], line) for line in report["panel_failures"]]
    idle = report["idle"]
    for what in ("front_frames", "back_frames"):
        if idle is None or report[what] >= idle:
            out.append("%s %d, not under the replay's idle %s" % (what, report[what], idle))
    return out


def run_replay(slot: int, cue: str, rotate: str = None, cache=None, plant: bool = False) -> int:
    """`--replay SLOT`: G8, the followed figure of a paused replay up close --
    its family and armband, the GPU's colours for its arms, its still pose,
    the panel its back shows and the number in it."""
    import json

    import oracle as looks_oracle  # tools/looks

    image = os.environ[IMAGE_VARIABLE]
    rotate = rotate or REPLAY_ROTATE[0]
    path = cache or os.path.join(ATTACH_DIR, "replay-%d.json" % slot)
    if cache and os.path.isfile(cache):
        with open(cache) as fh:
            kept = json.load(fh)
        print("  capture read from %s, no emulator" % cache)
    else:
        maps = looks_oracle.model_maps(image)
        bodies = read_kits(image)
        with looks_oracle.Oracle(cue) as game:
            kept = replay_capture(game, maps, bodies, model_index(image), slot, rotate)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as fh:
            json.dump(kept, fh)
        print("  capture kept at %s (--frame-json reads it back)" % path)
    _restore_samples(kept["front"])
    _restore_samples(kept["back"])
    index = model_index(image)
    nth = 1 if plant else 0
    frames = replay_frames(kept["front"], nth)
    idle = REPLAY_IDLE.get(slot)
    print("  front: %d frame(s) of %d stop(s) in %d emulator frame(s) (idle %s, the replay's "
          "frames with no input: --replay-idle)"
          % (len(frames), sum(1 for e in kept["front"]["events"] if e["kind"] == "matrix"),
             kept["front_frames"], idle))
    for k, frame in enumerate(frames):
        print("    frame %d: %d figure(s), depths %s" % (
            k, len(frame["figures"]),
            " ".join("%.0f" % figure_depth(f) for f in sorted(frame["figures"],
                                                             key=figure_depth))))
    focus = frames[-1]["focus"] if frames else None
    if focus is not None:
        print("  followed figure, head first: %s  (one more piece the draw lag leaves unnamed)"
              % " ".join(str(p["section"]) for p in focus))
    still = None
    if len(frames) >= 2 and frames[-2]["focus"] is not None and focus is not None:
        still = pose_change(frames[-2]["focus"], focus)
    print("  still pose: the followed figure's matrices differ by %s between the last two "
          "frames (limit %d)" % (still, REPLAY_STILL))
    if focus is not None:
        pose_path = os.path.join(POSE_DIR, "slot%d-keeper-front.json" % slot)
        os.makedirs(POSE_DIR, exist_ok=True)
        with open(pose_path, "w") as fh:
            json.dump({"slot": slot, "source": "python3 tools/kits/oracle.py --replay %d" % slot,
                       "projection": focus[0]["projection"],
                       "pieces": [{"section": p["section"], "rotation": list(p["matrix"][0]),
                                   "translation": list(p["matrix"][1])} for p in focus]},
                      fh, indent=1)
        print("  pose kept at %s (projection H %s, OFX %s, OFY %s)"
              % (pose_path, focus[0]["projection"]["H"], focus[0]["projection"]["OFX"],
                 focus[0]["projection"]["OFY"]))
    samples = kept["front"]["lists"].get("%d" % frames[-1]["head"], []) if frames else []
    group, fit = figure_group(focus, samples, index)
    if fit:
        print("  %d quad(s) of the frame inside the figure's box %s; mean pixels off the "
              "frame, by section: %s"
              % (len(group), "(%.0f,%.0f)-(%.0f,%.0f)" % fit["box"], " ".join("%s:%s" % (r["section"], "%.2f" % r["error"]
                                                    if r["error"] is not None else "-")
                                        for r in fit["rows"])))
    sections = {}
    if group is not None and focus is not None:
        for piece in focus:
            if piece["section"] is not None:
                sections[piece["section"]] = section_samples(group, index, piece["section"])
        print("  what the GPU is told, by section (shaded: a colour per corner; raw: texel "
              "not modulated):")
        for section, found in sections.items():
            s = shading_of(found)
            zones = sorted({z for one in found for z in sample_zones(one)
                            if kit_image_of(one)})
            print("    %3d: %2d prim(s), %2d shaded, %d raw, %d semi; CLUT %s; page %s; "
                  "corner colours %s to %s; zones %s"
                  % (section, s["n"], s["shaded"], s["raw"], s["semi"],
                     " ".join("(%d,%d)" % c for c in s["cluts"]) or "-",
                     " ".join("(%d,%d)" % p for p in s["pages"]) or "-",
                     s["low"], s["high"], "; ".join(zones) or "-"))
    if kept.get("buffer") and sections:
        colours = colour_confront(group, kept["buffer"], kept["texture"], sections)
        print("  the frame buffer under each section against its texels (five bits a "
              "channel; far: mean distance per channel):")
        for section, c in colours.items():
            if c is None:
                print("    %3d: no pixel of its own" % section)
                continue
            print("    %3d: %4d px; game %s, texel %s (far %.2f), texel x colour/128 %s "
                  "(far %.2f)" % (section, c["pixels"],
                                  "(%.1f %.1f %.1f)" % c["game"], "(%.1f %.1f %.1f)" % c["texel"],
                                  c["texel_far"], "(%.1f %.1f %.1f)" % c["shaded"],
                                  c["shaded_far"]))
        save_buffer(os.path.join(ATTACH_DIR, "replay-%d-frame.png" % slot), kept["buffer"])
        print("    picture: %s" % os.path.join(ATTACH_DIR, "replay-%d-frame.png" % slot))
    print("  kit: %s" % (", ".join(
        "TEX_%s record %d %s at (%d,%d)" % (tag, i, NAMES[i], at[0][0], at[0][1])
        for tag, i, at, flat, shared in kept["hits"] if not flat) or "nothing found"))
    print("  turn: %s tapped %d time(s), torso yaw %s; %s; %d emulator frame(s) from the load, "
          "%d from the last tap to the end of the back capture (idle %s)"
          % (kept["rotate"], len(kept["yaws"]), " ".join("%.0f" % y for y in kept["yaws"]),
             kept["turned"], kept["turn_frames"], kept["back_frames"], idle))
    print("    the figure each tap read, root and depth: %s"
          % " ".join("%s@%.0f" % tuple(d) for d in kept.get("depths", [])))
    panel, number, panel_failures = None, None, []
    if kept["back"] is not None:
        back_frames = replay_frames(kept["back"], nth)
        back_focus = back_frames[-1]["focus"] if back_frames else None
        back_samples = (kept["back"]["lists"].get("%d" % back_frames[-1]["head"], [])
                        if back_frames else [])
        back_group, _fit = figure_group(back_focus, back_samples, index)
        cells = panel_samples(back_group or [])
        for cell, found in sorted(cells.items()):
            held = section_samples(found, index, back_focus[1]["section"]) if back_focus else []
            print("  back: %d primitive(s) of the figure sample panel (%d,%d) of page (%d,%d); "
                  "%d of them are torso %s's own texels on the disc"
                  % (len(found), cell[1], cell[2], found[0]["page"][0], found[0]["page"][1],
                     len(held), back_focus[1]["section"] if back_focus else "-"))
        if cells:
            cell = max(cells, key=lambda c: len(cells[c]))
            page_x = cells[cell][0]["page"][0]
            panel = (page_x,) + cell[1:]
            words = kept["pages"].get("%d" % page_x)
            if words is not None:
                record = records_of(_screen_body())[UNIFORM_RECORD]
                read = read_panels(words, record.w)
                shown = [one for one in read if one["cell"][1:] == cell[1:]]
                for one in read:
                    print("    page %d panel (%3d,%3d): number %s, digits %s, %d unexplained"
                          % (page_x, one["cell"][1], one["cell"][2], one["number"],
                             " ".join("%d at (%d,%d)" % (d, x, y) for x, y, d in one["digits"])
                             or "none", one["unexplained"]))
                if shown:
                    number = shown[0]["number"]
                    panel_failures = panels_judge(shown)
    expect = REPLAY_EXPECT.get(slot)
    report = {"focus": replay_frames(kept["front"], nth)[-1]["focus"] if frames else None,
              "still": still, "turned": kept["turned"], "panel": panel, "number": number,
              "panel_failures": panel_failures, "idle": idle,
              "front_frames": kept["front_frames"], "back_frames": kept["back_frames"]}
    if plant:
        print("  PLANT  the second-nearest figure followed, front and back, expected to open "
              "at section %d" % PLANT_REPLAY_ROOT)
    if expect is None:
        print("  no measured expectation for slot %d (REPLAY_EXPECT): printed, not judged" % slot)
        return 0
    failures = replay_judge(report, expect, plant)
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        print("  ok    the followed figure opens at section %d with head %d, draws %d in place "
              "of %d, holds still, and its back shows panel %s with number %d"
              % (expect["root"], expect["head"], expect["armband"], expect["replaced"],
                 expect["panel"], expect["number"]))
    return 1 if failures else 0


def save_buffer(path: str, buffer: dict) -> None:
    """The frame buffer kept under the followed figure, as an RGB PNG at four
    times its size -- to look at."""
    import struct
    import zlib

    rows = buffer["rows"]
    scale = 4
    width, height = len(rows[0]) * scale, len(rows) * scale
    raw = bytearray()
    for y in range(height):
        raw.append(0)
        for x in range(width):
            raw += bytes(v << 3 for v in rows[y // scale][x // scale][:3])

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height,
                                                                     8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


REPLAY_TAB = {"front": 180.0, "back": 0.0}
"""The 3D tab's yaws that show the figure's front and back (`ui/figure_view.py`
opens at 180, the front)."""


def palette_check(texture: dict, tag: str, clut, record: int) -> tuple:
    """(entries compared, entries that differ) between the kit's palette
    *record* on the disc -- what the 3D tab paints with -- and the CLUT row the
    game's quads use, both at five bits a channel."""
    row = texture["cluts"].get("%d,%d" % tuple(clut))
    if row is None:
        return 0, None
    body = _body(tag)
    raw = payload(body, records_of(body)[record])
    disc = [(v & 0x1F, v >> 5 & 0x1F, v >> 10 & 0x1F) for v in raw]
    n = min(len(disc), len(row))
    return n, sum(1 for a, b in zip(disc[:n], row[:n]) if tuple(a) != tuple(b))


def run_replay_confront(slot: int, cue: str, cache=None) -> int:
    """`--replay-confront SLOT`: the 3D tab's figure against the game's, on the
    capture `--replay` kept -- whether the tab paints with the palette the game
    uses, the colours of the whole figure by histogram (front and back), and a
    side-by-side picture to look at.  It records; it asserts no limit (G8)."""
    import json
    import subprocess
    import tempfile

    import importlib.util

    # tools/kits/confront.py, not the looks' module of the same name that
    # tools/looks on the path hands `import confront`
    spec = importlib.util.spec_from_file_location(
        "kits_confront", os.path.join(KITS_DIR, "confront.py"))
    confront = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = confront       # its dataclasses look themselves up there
    spec.loader.exec_module(confront)
    image = os.environ[IMAGE_VARIABLE]
    path = cache or os.path.join(ATTACH_DIR, "replay-%d.json" % slot)
    if not os.path.isfile(path):
        print("  no capture at %s: run --replay %d first" % (path, slot))
        return 1
    with open(path) as fh:
        kept = json.load(fh)
    _restore_samples(kept["front"])
    index = model_index(image)
    frames = replay_frames(kept["front"])
    focus = frames[-1]["focus"] if frames else None
    samples = kept["front"]["lists"].get("%d" % frames[-1]["head"], []) if frames else []
    group, _fit = figure_group(focus, samples, index)
    if not group or not kept.get("buffer"):
        print("  FAIL  the capture has no figure or no frame buffer under it")
        return 1
    tag = "41" if kept.get("tag") is None else kept["tag"]
    figure = 1 if focus[1]["section"] in KEEPER_ARMBANDS or focus[1]["section"] == 56 else 0
    record = (PLAYER_PALETTE if figure == 0 else KEEPER_PALETTE)[kept.get("set") or 1]
    cluts = sorted({tuple(one["clut"]) for one in group if is_figure(one)})
    for clut in cluts:
        n, wrong = palette_check(kept["texture"], tag, clut, record)
        print("  palette: TEX_%s record %d (%s) against CLUT (%d,%d): %d entries, %s differ"
              % (tag, record, NAMES[record], clut[0], clut[1], n, wrong))
    owners = {}
    for one in group:
        for px, py, _u, _v, _c in sample_pixels(one):
            owners[(px, py)] = owners.get((px, py), 0) + 1
    x0, y0 = kept["buffer"]["origin"]
    rows = kept["buffer"]["rows"]
    game = [tuple(v << 3 for v in rows[py - y0][px - x0]) for (px, py) in owners
            if 0 <= py - y0 < len(rows) and 0 <= px - x0 < len(rows[0])]
    shown = confront.histogram(game)
    number = REPLAY_EXPECT.get(slot, {}).get("number")
    out_dir = tempfile.mkdtemp(prefix="replay-confront-")
    python = os.path.join("work", "venv-looks", "bin", "python")
    if not os.path.isfile(python):
        print("  no venv python at %s (make looks-venv)" % python)
        return 1
    scores = {}
    for side, yaw in sorted(REPLAY_TAB.items()):
        out = os.path.join(ATTACH_DIR, "replay-%d-tab-%s.png" % (slot, side))
        args = [python, confront.APP, image, "--tag", tag, "--tab", "3d", "--figure",
                str(figure), "--armband", "--yaw", "%g" % yaw, "--export-3d", out]
        if number is not None:
            args += ["--number", str(number)]
        done = subprocess.run(args, env=confront.environment(), capture_output=True, text=True,
                              timeout=confront.TIMEOUT)
        if done.returncode or not os.path.isfile(out):
            print("  FAIL  app.py exited %s: %s" % (done.returncode, done.stderr[-300:]))
            return 1
        ours = confront.histogram(confront.figure_pixels(confront.read_rgb(out)))
        scores[side] = (confront.intersection(shown, ours),
                        confront.intersection(confront.restrict(shown, set(ours)), ours))
        print("  tab %s (yaw %g): histogram intersection with the game's figure %.3f, "
              "%.3f over the colours the tab draws; picture %s"
              % (side, yaw, scores[side][0],
                 scores[side][1], out))
    save_buffer(os.path.join(ATTACH_DIR, "replay-%d-frame.png" % slot), kept["buffer"])
    print("  the game's frame: %s (%d pixel(s) under the figure's quads)"
          % (os.path.join(ATTACH_DIR, "replay-%d-frame.png" % slot), len(game)))
    return 0


KEEPER_PALETTE = {1: 3, 2: 7}
"""Set -> the record of its goalkeeper palette (section 1.1)."""


def run_replay_idle(slot: int, cue: str) -> int:
    """`--replay-idle SLOT`: how long the paused replay lasts with no input."""
    import oracle as looks_oracle  # tools/looks

    with looks_oracle.Oracle(cue) as game:
        found = replay_idle(game, slot)
    if found["frames"] is None:
        print("  the replay of slot %d did not leave in %d frame(s); the screen moved %.4f"
              % (slot, REPLAY_IDLE_MOST, found["moved"]))
        return 1
    print("  the paused replay of slot %d left after %d frame(s) with no input (stepped %d at "
          "a time; its SAVE plate moved %.4f, over %.4f)"
          % (slot, found["frames"], REPLAY_IDLE_STEP, found["moved"], looks_oracle.MOVED))
    return 0


# --- G3: where MODEL.BIN's sleeves and armband go on the EDT_MOD.BIN figure ---

ARM_NAMES = ("upper arm a", "upper arm b", "forearm a", "forearm b")
FRAME_SLACK = 3.0
"""How far, in model units, the translation that best lays a MODEL.BIN arm on
the EDT_MOD.BIN piece `ARM_PIECES` gives it may be from zero before the two
frames are not the same.  Measured on the disc: 1.9 at most (`--edt-arms`).
The fit runs against the rule's piece, not the nearest one: against the
nearest, an arm moved 20 units in y settled on the other part at 2.0 to 2.2
and passed (CORR-K3D-013).  Measured against the rule's piece with
`--plant-edt-arms`, a move of 8 in x is refused at all 23 sections.  The fit
recovers part of a move, so the slack bounds a shift only roughly."""
ARM_PLANT_SHIFT = (8.0, 0.0, 0.0)
"""`--plant-edt-arms` moves every MODEL.BIN arm by this before matching: each
section keeps its nearest piece and leaves that piece's frame, so only
`FRAME_SLACK` can refuse it (CORR-K3D-013)."""
ICP_STEPS = 30


def mean_nearest(points, others) -> float:
    """The mean distance from each of *points* to the nearest of *others*."""
    import math

    return sum(min(math.dist(p, q) for q in others) for p in points) / len(points)


def frame_offset(points, others, steps: int = ICP_STEPS) -> tuple:
    """(translation, mean nearest distance after it): the shift that best lays
    *points* on *others*, by nearest-point iteration (translation only)."""
    import math

    t = [0.0, 0.0, 0.0]
    for _ in range(steps):
        moved = [tuple(p[i] + t[i] for i in range(3)) for p in points]
        near = [min(others, key=lambda q, p=p: math.dist(p, q)) for p in moved]
        t = [t[i] + sum(q[i] - p[i] for p, q in zip(moved, near)) / len(points)
             for i in range(3)]
    moved = [tuple(p[i] + t[i] for i in range(3)) for p in points]
    return tuple(t), mean_nearest(moved, others)


def arm_side(points) -> str:
    """"a" for an arm whose mean z is below zero, "b" above (`pieces.py`'s pairs)."""
    return "a" if sum(p[2] for p in points) / len(points) < 0 else "b"


def arm_match(points, pieces: dict, want: str = None) -> dict:
    """Where one MODEL.BIN arm goes among *pieces* -- {(section, name): points}
    of EDT_MOD.BIN, both figures.  The part is the nearest piece of the arm's
    side.  The frame offset is measured against the piece *want* names (the
    rule's, the nearest section of that name), not against the nearest piece:
    started from zero, the fit settles on whatever piece is closest, so
    against the nearest one a small offset only says the arm lies on some
    arm piece (CORR-K3D-013)."""
    import math

    side = arm_side(points)
    ranked = sorted((mean_nearest(points, pts), at, name)
                    for (at, name), pts in pieces.items() if name.endswith(" " + side))
    distance, at, name = ranked[0]
    other = next((d for d, _a, n in ranked if n.split()[0] != name.split()[0]), None)
    against = next(((a, n) for _d, a, n in ranked if n == want), (at, name))
    shift, fitted = frame_offset(points, pieces[against])
    return {"piece": name, "section": at, "distance": distance, "other part": other,
            "against": against[1], "offset": math.sqrt(sum(v * v for v in shift)),
            "shift": shift, "fitted": fitted}


def arms_report(model_sections: dict, pieces: dict, shift=(0.0, 0.0, 0.0),
                expect: dict = None) -> dict:
    """{MODEL.BIN section: arm_match} for every section of `ARM_PIECES` in
    *model_sections* ({section: points}), each moved by *shift* first and
    its frame offset measured against the piece *expect* gives it."""
    expect = ARM_PIECES if expect is None else expect
    return {number: arm_match([tuple(p[i] + shift[i] for i in range(3)) for p in pts], pieces,
                              expect.get(number))
            for number, pts in sorted(model_sections.items())}


def arms_judge(report: dict, expect: dict = None, shared=None) -> list:
    """What breaks the rule: a section on another piece than `ARM_PIECES`
    says, nearer the other part, or out of the piece's frame by more than
    `FRAME_SLACK`; and, when *shared* ({name: bool}) is given, an arm name
    the two figures do not pose alike."""
    expect = ARM_PIECES if expect is None else expect
    bad = []
    for number, want in sorted(expect.items()):
        got = report.get(number)
        if got is None:
            bad.append("section %d: not measured" % number)
            continue
        if got["piece"] != want:
            bad.append("section %d: on %s, the rule says %s" % (number, got["piece"], want))
        if got["other part"] is not None and got["other part"] <= got["distance"]:
            bad.append("section %d: the other part is as near (%.1f against %.1f)"
                       % (number, got["other part"], got["distance"]))
        if got["offset"] > FRAME_SLACK:
            bad.append("section %d: %.1f units out of %s's frame, past %.1f"
                       % (number, got["offset"], got.get("against", got["piece"]),
                          FRAME_SLACK))
    for name, same in sorted((shared or {}).items()):
        if not same:
            bad.append("%s: the player and the goalkeeper pose it apart" % name)
    return bad


def run_edt_arms(image_path: str, plant: bool = False) -> int:
    """`--edt-arms`: the rule of G3, measured on the disc and asserted."""
    import iso_source
    import pieces
    import scene
    import section

    with iso_source.open_disc(image_path) as disc:
        files = {name: disc.read(name) for name in (layout.EDT_MOD, layout.MODEL, layout.ANIME)}
    edt = section.scan(files[layout.EDT_MOD],
                       layout.geometry_start(files[layout.EDT_MOD])).sections
    model = section.scan(files[layout.MODEL], layout.MODEL_GEOMETRY_START).sections
    named, _orders, _paired = pieces.name_pieces(files[layout.EDT_MOD])
    arms = {(i, piece.full_name): [(v.x, v.y, v.z) for v in edt[i].vertices]
            for i, piece in named.items() if piece.full_name in ARM_NAMES}
    # scene.pose gives each section the pose of its name, so this compares a
    # lookup with itself: it guards the naming, not the game (CORR-K3D-012).
    pose = scene.pose(files)
    shared = {}
    for name in ARM_NAMES:
        placed = {repr(pose.get((layout.EDT_MOD, at))) for at, n in arms if n == name}
        shared[name] = len(placed) == 1
    report = arms_report({n: [(v.x, v.y, v.z) for v in model[n].vertices] for n in ARM_PIECES},
                         arms, ARM_PLANT_SHIFT if plant else (0.0, 0.0, 0.0))
    print("edt-arms: %s and %s%s" % (layout.MODEL, layout.EDT_MOD,
                                     ", every MODEL.BIN arm moved by %s (the control)"
                                     % (ARM_PLANT_SHIFT,) if plant else ""))
    for name in ARM_NAMES:
        print("  %-11s EDT_MOD.BIN sections %s, %s"
              % (name, " ".join(str(at) for at, n in sorted(arms) if n == name),
                 "posed alike by name" if shared[name] else "posed apart"))
    for number, got in report.items():
        print("  section %3d -> %-11s (nearest EDT section %2d at %.1f, other part %s), "
              "frame offset %.1f (%+.1f,%+.1f,%+.1f)"
              % (number, got["piece"], got["section"], got["distance"],
                 "%.1f" % got["other part"] if got["other part"] is not None else "-",
                 got["offset"], *got["shift"]))
    failures = arms_judge(report, shared=shared)
    for line in failures:
        print("  FAIL  %s" % line)
    if not failures:
        print("  ok    every sleeve and armband section is in its EDT_MOD.BIN piece's frame "
              "(offset %.1f at most, slack %.1f)"
              % (max(g["offset"] for g in report.values()), FRAME_SLACK))
    return 1 if failures else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--png", help="a VRAM dump (1024x512 PNG) to search, no emulator")
    source.add_argument("--slot", type=int, help="load this save-state slot in the fork")
    source.add_argument("--sleeves", type=int, metavar="SLOT",
                        help="section 4.3: which primitives of this slot's frame sample "
                             "the sleeves image")
    source.add_argument("--attach", type=int, metavar="SLOT",
                        help="section 4.3: where MODEL.BIN's armband and long sleeves sit "
                             "on the figure in this match slot")
    source.add_argument("--attach-matrix", type=int, metavar="SLOT",
                        help="section 4.3: the GTE matrix each MODEL.BIN section is "
                             "drawn with in this match slot")
    source.add_argument("--match-pose", type=int, metavar="SLOT",
                        help="section 4.3: each MODEL.BIN piece's matrix in this match "
                             "slot, proved on the frame's own list")
    source.add_argument("--match-silhouette", type=int, metavar="SLOT",
                        help="section 4.3: the match figure the 3D tab draws against the "
                             "game's frame of this slot, silhouette for silhouette (--tag)")
    source.add_argument("--sleeves-image", type=int, metavar="SLOT",
                        help="section 4.3: the sleeves image this slot holds in VRAM, "
                             "against the disc (with --page, --tag, --set); a report, always exits 0")
    source.add_argument("--keeper-armband", type=int, metavar="SLOT",
                        help="G4: what the goalkeeper captain of this match slot draws "
                             "for the armband, and in place of what")
    source.add_argument("--edt-arms", action="store_true",
                        help="G3: which EDT_MOD.BIN arm piece each MODEL.BIN sleeve and "
                             "armband section stands in for, in that piece's frame (disc only)")
    source.add_argument("--back", type=int, metavar="SLOT",
                        help="section 4.7: does the LOOKS SET of this slot fill the torso gaps")
    source.add_argument("--edit-number", type=int, metavar="SLOT",
                        help="G7: what the EDIT PL. NUM screen of this slot draws -- the "
                             "figure's family, kit, still pose, the turn a confirming press "
                             "makes and the number panel written for the back")
    source.add_argument("--replay", type=int, metavar="SLOT",
                        help="G8: the figure a paused replay of this slot follows, up close -- "
                             "its family and armband, the GPU's colours for its arms, its "
                             "still pose, and the panel and number its back shows")
    source.add_argument("--replay-confront", type=int, metavar="SLOT",
                        help="G8: the 3D tab's figure against the game's, on the capture "
                             "--replay kept: the palette, the colours front and back, and a "
                             "picture of each")
    source.add_argument("--replay-idle", type=int, metavar="SLOT",
                        help="G8: how many frames the paused replay of this slot lasts "
                             "with no input")
    parser.add_argument("--rotate", choices=REPLAY_ROTATE,
                        help="with --replay: the button tapped to turn the camera to the "
                             "figure's back (default %s)" % REPLAY_ROTATE[0])
    parser.add_argument("--plant-replay", action="store_true",
                        help="with --replay: the control -- follow the second-nearest figure, "
                             "front and back, and expect it to open at section %d"
                             % PLANT_REPLAY_ROOT)
    parser.add_argument("--player", type=int, default=0, metavar="ROW",
                        help="with --edit-number: rows to go down the list before confirming "
                             "(default 0, the selected player)")
    parser.add_argument("--button", choices=EDIT_BUTTONS,
                        help="with --edit-number: press only this button after the still "
                             "capture and report what it does (CORR-K3D-022); the capture "
                             "is kept as edit-SLOT-ROW-BUTTON.json")
    parser.add_argument("--plant-edit-number", action="store_true",
                        help="with --edit-number: the control -- expect figures opened at "
                             "section %d and read every panel one row up" % PLANT_EDIT_HEAD)
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
    parser.add_argument("--frame-json", metavar="JSON",
                        help="with --attach, --attach-matrix or --match-pose: read the "
                             "capture kept by an earlier run")
    parser.add_argument("--plant-matrix", choices=("lag", "slot"),
                        help="with --attach-matrix: the control -- no pointer lag, or the "
                             "armband expected one piece over")
    parser.add_argument("--plant-silhouette", action="store_true",
                        help="with --match-silhouette: the control -- every piece drawn "
                             "with its figure's body matrix")
    parser.add_argument("--check", action="store_true",
                        help="with --match-pose: exit 1 unless core/match_pose.json is what "
                             "the run measures")
    parser.add_argument("--write", action="store_true",
                        help="with --match-pose: version the pose as core/match_pose.json")
    parser.add_argument("--plant-pose", action="store_true",
                        help="with --match-pose: the control -- each matrix given to the "
                             "piece named at its own stop")
    parser.add_argument("--pair-by", choices=PAIRINGS, default="indices",
                        help="with --match-pose: pair texels with vertices in this order "
                             "(corners is a report of the pairing the game does not use)")
    parser.add_argument("--sleeve-length", choices=sorted(SLEEVE_LENGTHS), default="long",
                        help="with --attach or --attach-matrix: the sleeves the slot wears")
    parser.add_argument("--plant-attach", action="store_true",
                        help="with --attach: the control -- name section %d the armband, "
                             "in place of the length's neighbour" % PLANT_ARMBAND)
    parser.add_argument("--plant-keeper-armband", action="store_true",
                        help="with --keeper-armband: the control -- expect section %d, "
                             "which has the same vertices, as the armband"
                             % PLANT_KEEPER_ARMBAND)
    parser.add_argument("--plant-edt-arms", action="store_true",
                        help="with --edt-arms: the control -- every MODEL.BIN arm moved "
                             "out of its frame, which has to fail")
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
    if args.edt_arms:
        return run_edt_arms(image, args.plant_edt_arms)
    if args.replay is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_replay(args.replay, cue, args.rotate, args.frame_json, args.plant_replay)
    if args.replay_confront is not None:
        return run_replay_confront(args.replay_confront, None, args.frame_json)
    if args.replay_idle is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_replay_idle(args.replay_idle, cue)
    if args.edit_number is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_edit_number(args.edit_number, cue, args.player, args.frame_json,
                               args.plant_edit_number, args.button)
    if args.keeper_armband is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_keeper_armband(args.keeper_armband, cue, args.frame_json,
                                  args.plant_keeper_armband)
    if args.sleeves is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_sleeves(args.sleeves, cue, args.expect_sleeves, args.plant_sleeves)
    if args.sleeves_image is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_sleeves_image(args.sleeves_image, cue, args.page or 576,
                                 args.tag or layout.KIT_ON_SCREEN, args.set, args.picture)
    if args.attach_matrix is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_attach_matrix(args.attach_matrix, cue, args.frame_json, args.plant_matrix,
                                 args.sleeve_length)
    if args.match_pose is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_match_pose(args.match_pose, cue, args.frame_json, args.plant_pose,
                              args.pair_by, args.write, args.check)
    if args.match_silhouette is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_match_silhouette(args.match_silhouette, cue, args.tag or "14",
                                    args.frame_json, args.plant_silhouette)
    if args.attach is not None:
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue and not args.frame_json:
            print("oracle: skipped -- no --cue and %s is not set" % DRIVE_VARIABLE)
            return SKIP
        return run_attach(args.attach, cue, args.frame_json, args.plant_attach,
                          args.sleeve_length)
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

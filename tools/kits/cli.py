#!/usr/bin/env python3
"""Command line of the kits project.  It prints; the core only returns data.

Usage:
    python tools/kits/cli.py survey <image.bin>
    python tools/kits/cli.py survey --negative <image.bin>
    python tools/kits/cli.py rects [--all] <image.bin> X,Y [X,Y ...]
    python tools/kits/cli.py rects --negative <image.bin> X,Y [X,Y ...]
    python tools/kits/cli.py rects <image.bin> X,Y [X,Y ...]
    python tools/kits/cli.py prims [--kit TAG] [--negative] <image.bin>
    python tools/kits/cli.py prims --all-kits [--tuple T] [--negative] <image.bin>
    python tools/kits/cli.py prims [--kit TAG] --tuple T [--tuple T ...] <image.bin>
    python tools/kits/cli.py uv [--kit TAG] [--json | --negative] <image.bin>
    python tools/kits/cli.py open <path> [<path> ...]
    python tools/kits/cli.py tex [--tag TAG ...] [--iso-size] [--negative] <path>
    python tools/kits/cli.py info [--tag TAG ...] <path>
    python tools/kits/cli.py export --out DIR [--tag TAG ...] [--palette K] <path>
    python tools/kits/cli.py export --confront [--negative] [--tag TAG ...] <image.bin>
"""

from __future__ import annotations

import argparse
import json
import os
import struct
import subprocess
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import api  # noqa: E402

survey_mod = api.measure

SHORT_LIST = 5
"""A count this small or smaller is printed with its tags."""


def _tags(tags) -> str:
    tags = list(tags)
    if not tags or len(tags) > SHORT_LIST:
        return ""
    return "  [" + ", ".join("TEX_" + t for t in tags) + "]"


def _count(label: str, tags, total: int) -> None:
    print("  %-46s %3d of %d%s" % (label, len(tags), total, _tags(tags)))


def _yes(flag: bool) -> str:
    return "yes" if flag else "NO"


def print_survey(s) -> None:
    n = s.total
    print("Kit container survey: %s" % s.source)
    print("  %-46s %3d" % ("TEX_<tag>.BIN containers", n))
    _count("shape %d images + %d CLUTs, same rects/order"
           % (api.IMAGE_COUNT, api.PALETTE_COUNT), s.shape_ok, n)
    print("  %-46s %3d" % ("distinct shapes", s.distinct_shapes))
    if s.shape_off:
        print("  off-shape: %s" % ", ".join("TEX_" + t for t in s.shape_off))
    for tag, problem in s.problems:
        print("  TEX_%s: %s" % (tag, problem))
    m = len(s.measured)
    _count("first set == second set (images and palettes)", s.sets_equal, m)
    _count("images differ between the two sets", s.images_differ, m)
    _count("only the palettes differ", s.only_palettes_differ, m)
    _count("player palette == keeper palette (first set)", s.player_equals_keeper, m)
    print("  %-46s %s B (record declares %s B)"
          % ("flag, decompressed size",
             " / ".join("{:,}".format(v) for v in s.flag_sizes),
             " / ".join("{:,}".format(v) for v in s.flag_declared)))
    _count("flag, 2nd half is one byte value", s.flag_tail_single, m)
    print("  %-46s %s" % ("flag, 2nd-half byte value per container",
                          ", ".join("0x%02x in %d" % vc for vc in s.flag_tail_split)))
    print("  %-46s %s (%d variant(s))" % ("referee identical in all",
                                          _yes(s.referee_variants == 1 and m == n),
                                          s.referee_variants))
    lo, hi = s.size_range
    print("  %-46s %s .. %s bytes" % ("file size", "{:,}".format(lo), "{:,}".format(hi)))


def print_controls(controls) -> int:
    """Print each planted defect; the exit code is 1 unless every one is red."""
    green = 0
    for c in controls:
        verdict = "red" if c.red else "GREEN (control failed)"
        green += not c.red
        print("  %-32s %-8s %s: %s -> %s  %s"
              % (c.name, c.planted, c.figure, c.clean, c.after, verdict))
    print("%d of %d controls red" % (len(controls) - green, len(controls)))
    return 1 if green else 0


def cmd_survey(args) -> int:
    try:
        if args.negative:
            return print_controls(survey_mod.negative_controls_image(args.image))
        result = api.survey_image(args.image)
    except api.SurveyError as exc:
        print("survey: %s" % exc, file=sys.stderr)
        return 1
    print_survey(result)
    return 0


NAMES_SHOWN = 3
"""How many file names a grouped owner line shows."""


def _point(p) -> str:
    return "(%d,%d)" % p


def print_rects(r, shown=NAMES_SHOWN) -> None:
    print("VRAM point owners: %s" % r.source)
    print("  %d files read, %d hold records; %d skipped"
          % (r.scanned, r.with_records, len(r.skipped)))
    for path, reason in r.skipped:
        print("    skipped %s (%s)" % (path, reason))
    for po in r.points:
        print("%s: %d record(s) in %d file(s) cover it, %d start there"
              % (_point(po.point), len(po.owners), len(po.files), len(po.starters)))
        for shape, paths in po.grouped():
            kind, x, y, w, h = shape
            starts = "STARTS here" if (x, y) == po.point else "covers only"
            names = ", ".join(paths if shown is None else paths[:shown])
            more = " ..." if shown is not None and len(paths) > shown else ""
            print("  %-5s origin (%4d,%4d) %3dx%3d hw  %-11s  %3d file(s): %s%s"
                  % (kind, x, y, w, h, starts, len(paths), names, more))


def print_rects_controls(controls) -> int:
    """Print the planted origin shift per point; exit 1 unless every point is red."""
    if controls:
        c = controls[0]
        print("Planted: %d image record(s) of %s moved from (%d,%d) to x=%d"
              % (c.moved, c.planted, survey_mod.RECTS_CONTROL_FROM[0],
                 survey_mod.RECTS_CONTROL_FROM[1], survey_mod.RECTS_CONTROL_TO_X))
    green = 0
    for c in controls:
        verdict = "red" if c.red else "GREEN (control failed)"
        green += not c.red
        print("  %s: files %d -> %d, records %d -> %d, %s owns it: %s -> %s  %s"
              % (_point(c.point), c.files[0], c.files[1], c.records[0], c.records[1],
                 c.planted, _yes(c.planted_owns[0]), _yes(c.planted_owns[1]), verdict))
    print("%d of %d points red" % (len(controls) - green, len(controls)))
    return 1 if green else 0


def cmd_rects(args) -> int:
    try:
        points = [survey_mod.parse_point(t) for t in args.points]
        if args.negative:
            return print_rects_controls(survey_mod.rects_negative_image(args.image, points))
        result = survey_mod.rects_image(args.image, points)
    except survey_mod.SurveyError as exc:
        print("rects: %s" % exc, file=sys.stderr)
        return 1
    print_rects(result, shown=None if args.all else NAMES_SHOWN)
    return 0


def _pairs(pairs) -> str:
    return ", ".join("%s %d" % kv for kv in pairs) if pairs else "none"


def print_prims(r) -> None:
    print("Primitives per kit record: %s" % r.source)
    print("  kit TEX_%s, tuple %s, geometry and resolution by tools/looks draw_list"
          % (r.kit, r.tuple_text))
    for f in r.figures:
        print("figure %d (%s): %d primitive(s) over %d section(s)"
              % (f.figure, "outfield" if f.figure == 0 else "goalkeeper",
                 f.total, f.sections))
        print("  %-40s %s" % ("container (draw list, first corner)", _pairs(f.containers)))
        print("  %-40s %s" % ("kit role (draw list, first corner)", _pairs(f.first)))
        print("  %-40s %s" % ("kit role (any of four corners)", _pairs(f.touch)))
        print("  %-40s %d" % ("a corner in a DAT2D image record", f.touch_dat2d))
        print("  %-40s %d" % ("a corner in no record of either file", f.touch_none))
        print("  %-40s %d" % ("corners touch a kit role first missed", f.disagree))
        print("  %-40s %s" % ("VRAM box of the corners in kit records",
                               "(%d,%d)..(%d,%d)" % f.kit_box if f.kit_box else "none"))
        print("  sleeves (576,384): %d primitive(s)" % f.sleeves)


def print_prims_controls(controls) -> int:
    """Print each planted move; exit 1 unless every expectation held."""
    bad = 0
    for c in controls:
        bad += not c.ok
        print("  %-28s moved %d  figure %d  %-24s %3d -> %3d  %-17s %s"
              % (c.name, c.moved, c.figure, c.count, c.clean, c.after, c.expect,
                 "held" if c.ok else "FAILED"))
    print("%d of %d expectations held" % (len(controls) - bad, len(controls)))
    return 1 if bad else 0


def print_prims_all_kits(sweep) -> None:
    print("Primitives per kit record, every kit: %s" % sweep.source)
    print("  tuple %s: %d kits, %d distinct result(s)"
          % (sweep.tuple_text, sweep.kits, len(sweep.groups)))
    for figures, tags in sweep.groups:
        print("  %3d kit(s)%s" % (len(tags), _tags(tags)))
        for f in figures:
            print("    figure %d: %d primitive(s); kit role %s"
                  % (f.figure, f.total, _pairs(f.first)))


def print_prims_tuples(reports) -> None:
    print("Primitives per kit record, per tuple: %s" % reports[0].source)
    print("  kit TEX_%s" % reports[0].kit)
    for r in reports:
        print("  %-14s %s" % (r.tuple_text, "; ".join(
            "figure %d: %d total, kit role %s" % (f.figure, f.total, _pairs(f.first))
            for f in r.figures)))
    distinct = len({survey_mod.kit_roles_of(r) for r in reports})
    print("  kit roles identical in all %d tuples: %s (%d distinct)"
          % (len(reports), _yes(distinct == 1), distinct))


def print_sweep_control(c) -> int:
    """Print the planted kit against both sweeps; exit 1 unless both split."""
    print("Planted: %d image record(s) of TEX_%s moved from (576,256) to (%d,%d)"
          % ((c.moved, c.kit) + survey_mod.PRIMS_AWAY))
    for label, sweep in (("clean", c.clean), ("planted", c.planted)):
        print("  %-8s %d kits, %d distinct result(s): %s"
              % (label, sweep.kits, len(sweep.groups),
                 ", ".join("%d%s" % (len(t), _tags(t)) for _, t in sweep.groups)))
    print("  kit roles of TEX_%s, clean vs planted: %d distinct" % (c.kit, c.roles_distinct))
    print("red" if c.red else "GREEN (control failed)")
    return 0 if c.red else 1


def cmd_prims(args) -> int:
    tuples = args.tuple or [survey_mod.PRIMS_TUPLE]
    try:
        if args.negative and args.all_kits:
            if len(tuples) > 1:
                print("prims: --all-kits takes one --tuple", file=sys.stderr)
                return 2
            return print_sweep_control(
                survey_mod.prims_all_kits_negative_image(args.image, args.kit, tuples[0]))
        if args.negative:
            return print_prims_controls(survey_mod.prims_negative_image(args.image, args.kit))
        if args.all_kits:
            if len(tuples) > 1:
                print("prims: --all-kits takes one --tuple", file=sys.stderr)
                return 2
            print_prims_all_kits(survey_mod.prims_all_kits_image(args.image, tuples[0]))
            return 0
        if len(tuples) > 1:
            print_prims_tuples(survey_mod.prims_tuples_image(args.image, args.kit, tuples))
            return 0
        result = survey_mod.prims_image(args.image, args.kit, tuples[0])
    except survey_mod.SurveyError as exc:
        print("prims: %s" % exc, file=sys.stderr)
        return 1
    print_prims(result)
    return 0


def _rect(r) -> str:
    return "(%d,%d)..(%d,%d)" % r if r else "none"


def print_uv(r) -> None:
    print("UV rects in the %dx%d work bitmap: %s"
          % (survey_mod.BITMAP_W, survey_mod.BITMAP_H, r.source))
    print("  kit TEX_%s, tuple %s; uniform at x 0..127, sleeves at x 128..255; "
          "pixels from page and u,v" % (r.kit, r.tuple_text))
    for f in r.figures:
        print("figure %d (%s): %d kit primitive(s), %d mapped"
              % (f.figure, "outfield" if f.figure == 0 else "goalkeeper",
                 len(f.rects), len(f.mapped)))
        roles = {}
        for u in f.mapped:
            roles[u.role] = roles.get(u.role, 0) + 1
        print("  %-44s %s" % ("mapped per image", _pairs(sorted(roles.items()))))
        print("  %-44s %s" % ("union box, bitmap px (inclusive)", _rect(f.union)))
        print("  %-44s %d" % ("distinct px in the rects (bounding-rect)", f.pixels))
        why = {}
        for u in f.outside:
            why[u.outside] = why.get(u.outside, 0) + 1
        print("  outside %dx%d: %d%s" % (survey_mod.BITMAP_W, survey_mod.BITMAP_H,
                                          len(f.outside),
                                          "  (" + _pairs(sorted(why.items())) + ")"
                                          if why else ""))
    print("sha256 of the canonical JSON: %s" % r.digest)


def print_uv_controls(controls) -> int:
    """Print each planted move; exit 1 unless every expectation held."""
    bad = 0
    for c in controls:
        bad += not c.ok
        fig = "both" if c.figure < 0 else "figure %d" % c.figure
        print("  %-26s moved %d  %-8s  %-24s %s -> %s  %s"
              % (c.name, c.moved, fig, c.measure, c.clean, c.after,
                 "held" if c.ok else "FAILED"))
    print("%d of %d expectations held" % (len(controls) - bad, len(controls)))
    return 1 if bad else 0


def cmd_uv(args) -> int:
    try:
        if args.negative:
            return print_uv_controls(survey_mod.uv_negative_image(args.image, args.kit))
        result = survey_mod.uv_image(args.image, args.kit)
    except survey_mod.SurveyError as exc:
        print("uv: %s" % exc, file=sys.stderr)
        return 1
    if args.json:
        doc = result.canonical()
        doc["kit"] = result.kit
        doc["source"] = result.source
        doc["sha256"] = result.digest
        print(json.dumps(doc, indent=1, sort_keys=True))
    else:
        print_uv(result)
    return 0


def _open_negative(paths) -> int:
    """Build the fixtures from the one disc given and check each outcome."""
    import tempfile

    if len(paths) != 1:
        print("open: --negative takes one disc image", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory(prefix="kits-open-") as folder:
        try:
            controls = api.open_controls(paths[0], folder)
        except api.KitsError as exc:
            print("open: %s" % exc, file=sys.stderr)
            return 1
        bad = 0
        for c in controls:
            bad += not c.ok
            print("%-15s %-54s expect %-16s got %-16s %s"
                  % (c.name, c.built, c.expect, c.got, "held" if c.ok else "FAILED"))
            if c.phrase or not c.ok:
                print("    %s" % c.message.replace(folder, "<tmp>"))
    print("%d of %d expectations held" % (len(controls) - bad, len(controls)))
    return 1 if bad else 0


def cmd_open(args) -> int:
    """What `api.open_source` makes of each path: its kind, or the refusal.

    Only the facade is used here.  Exit 1 when any path is refused, so a
    list that should all open fails loudly on the first one that does not.
    """
    if args.negative:
        return _open_negative(args.paths)
    refused = 0
    for path in args.paths:
        name = os.path.basename(path)
        try:
            source = api.open_source(path)
        except api.KitsError as exc:
            refused += 1
            print("REFUSE %s -> %s: %s" % (name, type(exc).__name__, exc))
            continue
        if source.kind == api.KIND_ROM:
            extra = "kit tags %d, data track %s" % (len(source.kit_tags()), source.image_path)
        else:
            extra = "%d bytes" % source.size
        print("OPEN   %s -> %s (%s)" % (name, source.kind, extra))
    return 1 if refused else 0


def _kits_of(source, tags, trust_iso_size=False):
    """(label, Kit or the KitError raised) for each kit of *source*."""
    if source.kind != api.KIND_ROM:
        return [(os.path.basename(source.path), source.kit())]
    out = []
    for tag in tags or source.kit_tags():
        try:
            out.append(("TEX_" + tag, source.kit(tag, trust_iso_size)))
        except api.KitError as exc:
            out.append(("TEX_" + tag, exc))
    return out


def _tex_negative(kits) -> int:
    """Section 5, control 4, on the first kit that passed."""
    sound = [(name, k) for name, k in kits if not isinstance(k, Exception) and k.ok]
    if not sound:
        print("tex: --negative needs a kit that passes the guard, and none did",
              file=sys.stderr)
        return 1
    name, kit = sound[0]
    c = api.stream_control(kit)
    print("control: %s, byte %d (record 0 stream +%d) 0x%02x -> 0x%02x"
          % (name, c.at, c.at - c.offset, c.before, c.after))
    print("  clean:   %s" % ("passes" if c.clean.ok else "; ".join(c.clean.problems)))
    print("  planted: %s" % ("passes" if c.planted.ok else "; ".join(c.planted.problems)))
    print("control %s" % ("held: the planted kit is refused on record 0" if c.ok
                          else "FAILED"))
    return 0 if c.ok else 1


def _disc_negative(source) -> int:
    """The two read rules of section 2.1, each planted; exit 1 unless both held."""
    try:
        controls = api.disc_controls(source)
    except api.KitsError as exc:
        print("disc controls: not run: %s" % exc)
        return 0
    bad = 0
    for c in controls:
        bad += not c.ok
        print("control: %s -- %s" % (c.name, c.planted))
        print("  clean:   %s" % c.clean)
        print("  planted: %s" % c.after)
        print("control %s" % ("held" if c.ok else "FAILED"))
    return 1 if bad else 0


def cmd_tex(args) -> int:
    """Each kit container of a source through the guard of form (section 2.1).

    Exit 1 when any kit is refused; with --negative, the exit is the
    control's alone.
    """
    try:
        source = api.open_source(args.path)
    except api.KitsError as exc:
        print("tex: %s" % exc, file=sys.stderr)
        return 1
    kits = _kits_of(source, args.tag, args.iso_size)
    if args.negative:
        code = _tex_negative(kits)
        if source.kind == api.KIND_ROM and not args.tag:
            code = max(code, _disc_negative(source))
        return code
    refused = 0
    noted = {api.NOTE_PAST_ISO_SIZE: 0, api.NOTE_FORM2_TAIL: 0}
    for name, kit in kits:
        if isinstance(kit, Exception):
            refused += 1
            print("REFUSE %s -> %s: %s" % (name, type(kit).__name__, kit))
            continue
        if kit.problems:
            refused += 1
            print("REFUSE %s (%d bytes): %s" % (name, kit.size, "; ".join(kit.problems)))
        else:
            print("PASS   %s (%d bytes): %d images, %d palettes"
                  % (name, kit.size, len(kit.images), len(kit.palettes)))
        for note in kit.notes:
            noted[note.kind] += 1
            print("  note: %s" % note)
    print("%d kits: %d pass, %d refused; %d read past the ISO size, "
          "%d with sectors marked Form 2 read as Form 1"
          % (len(kits), len(kits) - refused, refused, noted[api.NOTE_PAST_ISO_SIZE],
             noted[api.NOTE_FORM2_TAIL]))
    return 1 if refused else 0


def cmd_info(args) -> int:
    """What a source is, and with --tag (or a lone TEX) what one kit holds."""
    try:
        source = api.open_source(args.path)
    except api.KitsError as exc:
        print("info: %s" % exc, file=sys.stderr)
        return 1
    if source.kind == api.KIND_ROM:
        print("disc   %s" % source.path)
        print("  data track     %s" % source.image_path)
        print("  volume         %s" % source.volume_id)
        print("  files          %d" % source.file_count)
        print("  kit containers %d" % len(source.kit_tags()))
        if not args.tag:
            return 0
    else:
        print("lone TEX  %s (%d bytes)" % (source.path, source.size))
    bad = 0
    for name, kit in _kits_of(source, args.tag):
        if isinstance(kit, Exception):
            bad += 1
            print("%s: %s: %s" % (name, type(kit).__name__, kit))
            continue
        bad += not kit.ok
        print("%s  %d bytes  %s" % (name, kit.size, "passes the guard" if kit.ok
                                    else "REFUSED"))
        for p in kit.problems:
            print("  problem: %s" % p)
        for note in kit.notes:
            print("  note: %s" % note)
        for im in kit.images:
            print("  image   record %2d  %-30s %3dx%-3d" % (im.record, im.name, im.width,
                                                          im.height))
        for pal in kit.palettes:
            print("  palette record %2d  %-30s %3d colours" % (pal.record, pal.name,
                                                             len(pal.raw) // 2))
    return 1 if bad else 0


# -- export, and confront 1 of plan section 5 ------------------------------
#
# The PNG is written and read here with the standard library only: the CLI
# imports nothing but the facade, and the other side of confront 1 --
# tools/pes2/bin_archive.py export -- runs as its own process.

BIN_ARCHIVE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "pes2", "bin_archive.py")


def bgr555_rgba(raw: bytes) -> list:
    """(r, g, b, a) per BGR555 halfword; black with the STP bit clear is the
    transparent entry (the PSX rule)."""
    out = []
    for i in range(0, len(raw), 2):
        v = raw[i] | raw[i + 1] << 8
        r, g, b = v & 0x1F, (v >> 5) & 0x1F, (v >> 10) & 0x1F
        alpha = 0 if (v & 0x7FFF) == 0 and not v & 0x8000 else 255
        out.append((r << 3 | r >> 2, g << 3 | g >> 2, b << 3 | b >> 2, alpha))
    return out


def write_png(path: str, width: int, height: int, indices: bytes, palette) -> None:
    """An 8-bit indexed PNG with tRNS."""
    def chunk(tag, body):
        return (struct.pack(">I", len(body)) + tag + body
                + struct.pack(">I", zlib.crc32(tag + body) & 0xFFFFFFFF))
    raw = b"".join(b"\0" + indices[r * width:(r + 1) * width] for r in range(height))
    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n"
                 + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 3, 0, 0, 0))
                 + chunk(b"PLTE", b"".join(bytes(c[:3]) for c in palette))
                 + chunk(b"tRNS", bytes(c[3] for c in palette))
                 + chunk(b"IDAT", zlib.compress(raw, 9))
                 + chunk(b"IEND", b""))


def read_png(path: str) -> tuple:
    """(width, height, indices, palette as [(r, g, b, a)]) of an 8-bit
    indexed PNG with filter 0 on every row, which both writers emit."""
    with open(path, "rb") as fh:
        data = fh.read()
    p, chunks = 8, {}
    while p < len(data):
        n = struct.unpack_from(">I", data, p)[0]
        tag = data[p + 4:p + 8]
        chunks[tag] = chunks.get(tag, b"") + data[p + 8:p + 8 + n]
        p += 12 + n
    width, height, depth, kind = struct.unpack_from(">IIBB", chunks[b"IHDR"])
    if (depth, kind) != (8, 3):
        raise ValueError("%s: not an 8-bit indexed PNG" % path)
    raw = zlib.decompress(chunks[b"IDAT"])
    rows = []
    for r in range(height):
        row = raw[r * (width + 1):(r + 1) * (width + 1)]
        if row[0] != 0:
            raise ValueError("%s: row %d uses filter %d" % (path, r, row[0]))
        rows.append(row[1:])
    plte, trns = chunks[b"PLTE"], chunks.get(b"tRNS", b"")
    palette = [tuple(plte[3 * i:3 * i + 3]) + (trns[i] if i < len(trns) else 255,)
               for i in range(len(plte) // 3)]
    return width, height, b"".join(rows), palette


def export_kit(kit, stem: str, out: str, palette: int, plant=None, colour_plant=None) -> int:
    """Every image of *kit* as `<stem>_<i>.png`, painted with palette number
    *palette* (0..4, file order) -- bin_archive's naming and its --clut.
    *plant* = (image number, pixel) adds 1 to that index first: the control.
    *colour_plant* = (palette number, colour) flips the low bit of that
    colour's red when *palette* is that one: the palette control."""
    colours = bgr555_rgba(kit.palettes[palette].raw)
    if colour_plant is not None and colour_plant[0] == palette:
        r, g, b, a = colours[colour_plant[1]]
        colours[colour_plant[1]] = (r ^ 1, g, b, a)
    for i, im in enumerate(kit.images):
        indices = im.indices
        if plant is not None and plant[0] == i:
            buf = bytearray(indices)
            buf[plant[1]] = (buf[plant[1]] + 1) & 0xFF
            indices = bytes(buf)
        write_png(os.path.join(out, "%s_%02d.png" % (stem, i)), im.width, im.height,
                  indices, colours)
    return len(kit.images)


def cmd_export(args) -> int:
    if args.confront:
        return confront(args.path, args.tag, args.negative)
    try:
        source = api.open_source(args.path)
    except api.KitsError as exc:
        print("export: %s" % exc, file=sys.stderr)
        return 1
    os.makedirs(args.out, exist_ok=True)
    written = refused = 0
    for name, kit in _kits_of(source, args.tag):
        if isinstance(kit, Exception) or not kit.ok:
            refused += 1
            print("  %s not exported: %s" % (name, kit if isinstance(kit, Exception)
                                              else "; ".join(kit.problems)))
            continue
        written += export_kit(kit, name if source.kind == api.KIND_ROM
                              else os.path.splitext(os.path.basename(source.path))[0],
                              args.out, args.palette)
    print("wrote %d PNG(s) to %s with palette %d (%s); %d kit(s) refused"
          % (written, args.out, args.palette,
             api.RECORD_NAMES[api.PALETTE_RECORDS[args.palette]], refused))
    return 1 if refused else 0


CONTROL_PIXEL = (0, 4096)
"""The pixel --negative changes on our side: image 0, index 4096 (row 32)."""

CONTROL_COLOUR = (0, 1)
"""The colour --negative changes on our side, on a second kit: palette 0,
colour 1, the low bit of its red.  The indices stay equal, so only the
palette comparison can see it (CORR-KITS-021)."""


def confront(image_path: str, tags, negative: bool) -> int:
    """Confront 1: our export against `bin_archive.py export`, for every
    palette (0..4), on every kit the two can both read.  Compares the
    decoded indices and palette of each PNG pair, not the PNG bytes."""
    try:
        source = api.open_source(image_path)
    except api.KitsError as exc:
        print("export: %s" % exc, file=sys.stderr)
        return 1
    if source.kind != api.KIND_ROM:
        print("export: --confront needs a disc image, %s is a lone TEX" % image_path,
              file=sys.stderr)
        return 2
    kits = [(name, k) for name, k in _kits_of(source, tags)
            if not isinstance(k, Exception) and k.ok]
    plant_tag = kits[0][0] if (negative and kits) else None
    colour_tag = kits[1][0] if (negative and len(kits) > 1) else None
    differ = {}
    with tempfile.TemporaryDirectory(prefix="kits-confront-") as tmp:
        for k in range(api.PALETTE_COUNT):
            ours, theirs = os.path.join(tmp, "ours%d" % k), os.path.join(tmp, "theirs%d" % k)
            os.makedirs(ours)
            for name, kit in kits:
                export_kit(kit, name, ours, k,
                           CONTROL_PIXEL if name == plant_tag else None,
                           CONTROL_COLOUR if name == colour_tag else None)
            proc = subprocess.run([sys.executable, BIN_ARCHIVE, "export", source.image_path,
                                   "--clut", str(k), "--out", theirs],
                                  capture_output=True, text=True,
                                  env=dict(os.environ, MSYS_NO_PATHCONV="1"))
            if proc.returncode:
                print("export: bin_archive.py export --clut %d failed: %s"
                      % (k, proc.stderr.strip()), file=sys.stderr)
                return 1
            for name, kit in kits:
                for i in range(len(kit.images)):
                    png = "%s_%02d.png" % (name, i)
                    a, b = os.path.join(ours, png), os.path.join(theirs, png)
                    if not os.path.exists(b):
                        differ.setdefault(name, []).append("%s missing on bin_archive's side" % png)
                        continue
                    wa, ha, ia, pa = read_png(a)
                    wb, hb, ib, pb = read_png(b)
                    if (wa, ha) != (wb, hb):
                        differ.setdefault(name, []).append(
                            "%s palette %d: %dx%d against %dx%d" % (png, k, wa, ha, wb, hb))
                    elif ia != ib:
                        first = next(j for j in range(len(ia)) if ia[j] != ib[j])
                        count = sum(1 for x, y in zip(ia, ib) if x != y)
                        differ.setdefault(name, []).append(
                            "%s palette %d: %d pixel(s) differ, first at %d (%d,%d)"
                            % (png, k, count, first, first % wa, first // wa))
                    elif pa != pb:
                        differ.setdefault(name, []).append("%s palette %d: palettes differ"
                                                           % (png, k))
    same = len(kits) - len(differ)
    for name in sorted(differ):
        for line in differ[name]:
            print("  DIFFER %s" % line)
    print("confront 1: %d of %d tags equal (%d images x %d palettes each), "
          "tex.py against bin_archive.py export" % (same, len(kits), api.IMAGE_COUNT,
                                                   api.PALETTE_COUNT))
    if negative:
        pixel = plant_tag is not None and plant_tag in differ
        colour = (colour_tag is not None and colour_tag in differ
                  and all(line.endswith("palette %d: palettes differ" % CONTROL_COLOUR[0])
                          for line in differ[colour_tag]))
        held = pixel and colour and sorted(differ) == sorted((plant_tag, colour_tag))
        print("control: %s image 0 pixel %d +1, and %s palette %d colour %d red ^1, "
              "on our side -- %s"
              % (plant_tag, CONTROL_PIXEL[1], colour_tag, CONTROL_COLOUR[0],
                 CONTROL_COLOUR[1], "red, held" if held else "FAILED"))
        return 0 if held else 1
    return 0 if not differ and kits else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="cli.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("survey", help="measure the 105 kit containers of a disc")
    p.add_argument("image", help="the Japanese data track (.bin)")
    p.add_argument("--negative", action="store_true",
                   help="plant each known defect and show the figure it moves")
    p.set_defaults(fn=cmd_survey)
    p = sub.add_parser("rects", help="every record on the disc covering a VRAM point")
    p.add_argument("image", help="the Japanese data track (.bin)")
    p.add_argument("points", nargs="+", metavar="X,Y", help="VRAM point, in halfwords")
    p.add_argument("--all", action="store_true", help="name every owner file, not only %d"
                   % NAMES_SHOWN)
    p.add_argument("--negative", action="store_true",
                   help="plant the TEX_A4 origin shift and show the counts it moves")
    p.set_defaults(fn=cmd_rects)
    p = sub.add_parser("prims", help="how many primitives of each figure sample each kit record")
    p.add_argument("image", help="the Japanese data track (.bin)")
    p.add_argument("--kit", default=survey_mod.layout.KIT_ON_SCREEN,
                   help="kit tag (default %s)" % survey_mod.layout.KIT_ON_SCREEN)
    p.add_argument("--negative", action="store_true",
                   help="move the kit's sleeves and uniform records and show the counts")
    p.add_argument("--all-kits", action="store_true",
                   help="count with every kit and group identical results")
    p.add_argument("--tuple", action="append", metavar="T",
                   help="looks tuple (default %s); repeat it to compare tuples"
                   % survey_mod.PRIMS_TUPLE)
    p.set_defaults(fn=cmd_prims)
    p = sub.add_parser("uv", help="each kit primitive's UV rect in the 256x128 work bitmap")
    p.add_argument("image", help="the Japanese data track (.bin)")
    p.add_argument("--kit", default=survey_mod.layout.KIT_ON_SCREEN,
                   help="kit tag (default %s)" % survey_mod.layout.KIT_ON_SCREEN)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--json", action="store_true",
                      help="print every rect, machine-readable (digest over the geometry)")
    mode.add_argument("--negative", action="store_true",
                      help="shift and move the uniform record and check the rects follow")
    p.set_defaults(fn=cmd_uv)
    p = sub.add_parser("open", help="what the core makes of a file: a disc, a lone TEX, or a refusal")
    p.add_argument("paths", nargs="+", metavar="path")
    p.add_argument("--negative", action="store_true",
                   help="build the recognition fixtures from one disc and check each outcome")
    p.set_defaults(fn=cmd_open)
    p = sub.add_parser("tex", help="every kit container of a source through the guard of form")
    p.add_argument("path", help="a disc image, a cue sheet or a lone TEX")
    p.add_argument("--tag", action="append", help="only this tag (repeatable; disc only)")
    p.add_argument("--iso-size", action="store_true",
                   help="read each TEX to its ISO size only, not to where its header ends")
    p.add_argument("--negative", action="store_true",
                   help="change one byte of record 0's LZSS stream in the first sound kit "
                        "and check it is refused")
    p.set_defaults(fn=cmd_tex)
    p = sub.add_parser("info", help="what a source is, and what a kit of it holds")
    p.add_argument("path", help="a disc image, a cue sheet or a lone TEX")
    p.add_argument("--tag", action="append", help="describe this kit (repeatable; disc only)")
    p.set_defaults(fn=cmd_info)
    p = sub.add_parser("export", help="each image of each kit as an indexed PNG")
    p.add_argument("path", help="a disc image, a cue sheet or a lone TEX")
    p.add_argument("--out", help="folder for the PNGs (not with --confront)")
    p.add_argument("--tag", action="append", help="only this tag (repeatable; disc only)")
    p.add_argument("--palette", type=int, default=0, choices=range(5),
                   help="which of the 5 palettes, in file order (default 0)")
    p.add_argument("--confront", action="store_true",
                   help="confront 1: compare with bin_archive.py export, every palette")
    p.add_argument("--negative", action="store_true",
                   help="with --confront: change one pixel on our side, which must differ")
    p.set_defaults(fn=cmd_export)
    args = parser.parse_args(argv)
    if args.command == "export" and not args.confront and not args.out:
        parser.error("export needs --out (or --confront)")
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())

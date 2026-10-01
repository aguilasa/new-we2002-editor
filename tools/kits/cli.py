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
"""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import api  # noqa: E402
from core import survey as survey_mod  # noqa: E402

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
    images = sum(1 for r in survey_mod.EXPECTED_SHAPE if r[0] == survey_mod.KIND_IMAGE)
    cluts = len(survey_mod.EXPECTED_SHAPE) - images
    _count("shape %d images + %d CLUTs, same rects/order" % (images, cluts), s.shape_ok, n)
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
        result = survey_mod.survey_image(args.image)
    except survey_mod.SurveyError as exc:
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
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())

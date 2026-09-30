#!/usr/bin/env python3
"""Command line of the kits project.  It prints; the core only returns data.

Usage:
    python tools/kits/cli.py survey <image.bin>
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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


def cmd_survey(args) -> int:
    try:
        result = survey_mod.survey_image(args.image)
    except survey_mod.SurveyError as exc:
        print("survey: %s" % exc, file=sys.stderr)
        return 1
    print_survey(result)
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="cli.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("survey", help="measure the 105 kit containers of a disc")
    p.add_argument("image", help="the Japanese data track (.bin)")
    p.set_defaults(fn=cmd_survey)
    args = parser.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())

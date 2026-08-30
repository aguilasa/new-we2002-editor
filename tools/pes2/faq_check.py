#!/usr/bin/env python3
"""Check docs/PES2-NOMES.md against the disc, and against the two FAQs.

That appendix mixes two kinds of claim, and they need different guards:

  index, disc name, abbreviation and offset are **read from the disc**, so
  they can be re-read. `--image` does exactly that, and is the part worth
  wiring into ctest;

  the real club behind each fictitious name comes from two third-party
  FAQs, which cannot be versioned -- they carry their own copyright and
  one of them says outright it may not be republished. What *is* versioned
  is this script. Point it at the converted Markdown when the files are on
  disk again and the "30 of 32 land at 31-i" claim re-runs.

The FAQ lists appear in exactly reverse disc order, and two entries of the
BigCj34 list -- MEDOC and NORMANDIE -- are transposed. That is the claim
under test, and it is the reason the check is `>= 30`, not `== 32`.

Usage:

    python3 tools/pes2/faq_check.py --image <track1.bin>
    python3 tools/pes2/faq_check.py --faq "docs/Pro Evolution Soccer 2.md"
    python3 tools/pes2/faq_check.py --image <track1.bin> --faq A.md --faq B.md
"""

import argparse
import difflib
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import tables as T                                           # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NOMES = os.path.join(REPO, "docs", "PES2-NOMES.md")

# The 32 fictitious clubs are the first 32 team names after the two header
# entries, so their count is not a magic number -- it is where the themed
# national sides start.
FIRST_CLUB = 2
CLUB_COUNT = 32

# Two of the 32 sit in the wrong place in the BigCj34 list. See the section
# "A ordem do disco é o inverso da ordem das listas" of the appendix.
MIN_IN_PLACE = 30

ROW = re.compile(r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|\s*`([^`]+)`\s*\|\s*(\d+)\s*\|")


def disc_clubs(image):
    """[(index, name, abbreviation, offset)] for the 32 fictitious clubs."""
    with Image(image) as img:
        t_names = next(x for x in T.TABLES if x.key == "team-names")
        t_abbr = next(x for x in T.TABLES if x.key == "abbreviations")
        _, _, names = T.resolve(img, t_names)
        _, _, abbrs = T.resolve(img, t_abbr)
    out = []
    for i in range(CLUB_COUNT):
        off, name = names[FIRST_CLUB + i]
        out.append((i, name.decode("latin-1"), abbrs[i][1].decode("latin-1"), off))
    return out


def appendix_rows():
    """The `| # | nome | abrev. | offset | …` rows of docs/PES2-NOMES.md."""
    out = []
    with open(NOMES, encoding="utf-8") as fh:
        for line in fh:
            m = ROW.match(line.strip())
            if m:
                out.append((int(m.group(1)), m.group(2), m.group(3),
                            int(m.group(4))))
    return out


def faq_sequence(path, disc_names):
    """Disc club names in the order a FAQ's mapping table lists them.

    Only Markdown table rows are looked at: the same names also turn up in
    running prose and in the squad listings, and first-appearance over the
    whole file would take the order from there instead.

    Column by column, not row by row. The Dzanic FAQ lays its mapping out
    in two columns of sixteen, and faq2md.py collapses each printed row
    into one Markdown row -- read straight through, that interleaves the
    halves and turns a list in perfect order into a list in none. Reading
    cell 0 of every row, then cell 1, recovers the printed order and costs
    nothing on the single-column FAQ.

    Matching is fuzzy because the FAQs misspell three of them --
    "Pantagonia", "Vasgongadas", "Noordzeenkanaal". Where the two disagree
    on the disc spelling the disc wins, which is what this resolves.
    """
    cells = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.startswith("|"):
                continue
            for column, cell in enumerate(line.strip().strip("|").split("|")):
                for word in re.findall(r"[A-Za-z]{4,}", cell):
                    hit = difflib.get_close_matches(
                        word.upper(), disc_names, n=1, cutoff=0.85)
                    if hit:
                        cells.setdefault(column, []).append(hit[0])
    seen, order = set(), []
    for column in sorted(cells):
        for name in cells[column]:
            if name not in seen:
                seen.add(name)
                order.append(name)
    return order


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--image", help="the data track (.bin) of the disc")
    ap.add_argument("--faq", action="append", default=[],
                    help="a converted FAQ Markdown; may be given twice")
    args = ap.parse_args(argv)

    rows = appendix_rows()
    print(f"docs/PES2-NOMES.md: {len(rows)} club rows")
    bad = 0
    if len(rows) != CLUB_COUNT:
        print(f"  FAILED: expected {CLUB_COUNT} rows")
        bad += 1

    disc = None
    if args.image:
        disc = disc_clubs(args.image)
        print(f"disc: {os.path.basename(args.image)}")
        for (ri, rn, ra, ro), (di, dn, da, do) in zip(rows, disc):
            if (ri, rn, ra, ro) != (di, dn, da, do):
                print(f"  FAILED row {ri}: doc {(rn, ra, ro)} "
                      f"!= disc {(dn, da, do)}")
                bad += 1
        if not bad:
            print(f"  all {len(rows)} rows match name, abbreviation and offset")

    names = [n for _, n, _, _ in (disc or rows)]
    for path in args.faq:
        if not os.path.exists(path):
            print(f"{path}: not on disk -- the FAQs are not versioned; "
                  f"download and reconvert with tools/pes2/faq2md.py")
            continue
        order = faq_sequence(path, names)
        expected = names[::-1]
        in_place = sum(1 for i, n in enumerate(order)
                       if i < len(expected) and n == expected[i])
        print(f"{os.path.basename(path)}: {len(order)}/{CLUB_COUNT} clubs "
              f"found, {in_place} in reverse-disc position")
        for i, n in enumerate(order):
            if i < len(expected) and n != expected[i]:
                print(f"    {i:2d}: FAQ {n:16s} disc order expects "
                      f"{expected[i]}")
        if in_place < MIN_IN_PLACE:
            print(f"  FAILED: fewer than {MIN_IN_PLACE} in place")
            bad += 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

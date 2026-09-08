#!/usr/bin/env python3
"""The label tables -- THIRD-PARTY LABELS, not measurements.

Provenance (section 3.4 of the plan):

  container   --
  address     --
  semantics   the upstream, entirely
  codec       --

EVERYTHING IN THIS FILE IS SOMEONE ELSE'S NAMING. The bytes are measured and
the ranges are measured; what a `3` in `hair_style` looks like on screen is
what Zetaprog's combo box says it looks like, and nobody here has put a
PlayStation in front of it. Section 5.6 of the plan lists these under "what has
no oracle", and the distinction is not pedantry: an index out of range is a bug
we can prove, and a wrong label is an opinion we cannot.

So this module asserts RANGES and never asserts NAMES. `--check` re-reads the
lists out of the VB source to prove the transcription is faithful; it does not
and cannot prove the names are right.

THREE FIELDS HAVE FEWER LABELS THAN VALUES, measured: `beard_style` and
`beard_colour` hold 3 bits (8 values) and the upstream names 7; `foot` holds 2
bits (4 values) and it names 3. The extra index is not illegal -- it is
unlabelled. Anything that shows these to a user has to cope with an index the
upstream never named, which is why `label()` returns a marker instead of
raising.

Usage:

    python3 tools/mcr/domains.py
    python3 tools/mcr/domains.py --check work/easy-mcr
    python3 tools/mcr/domains.py --self-check
"""

import argparse
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attributes                                        # noqa: E402
import layout                                            # noqa: E402
import harness                                           # noqa: E402

UNNAMED = "?"          # what `label()` gives for an index the upstream skipped

# --- the tables -----------------------------------------------------------
# Transcribed from work/easy-mcr/lite/fifatomcr/Frmmcr.designer.vb and
# FrmFormation.Designer.vb. `--check` re-reads them from there.

POSITION = ("gk", "cb", "sb", "dh", "sh", "oh", "cf", "wg")

# Not a regular sequence -- the letters run a..p and the counts per letter are
# 3,6,2,2,2,3,1,1,3,1,1,3,1,1,1,1. Written out because guessing the pattern is
# exactly what went wrong first: an invented `c3,c4,c5,c6,...` passed every
# range check here and only `--check` against the VB source caught it.
HAIR_STYLE = ("a1", "a2", "a3", "b1", "b2", "b3", "b4", "b5", "b6", "c1",
              "c2", "d1", "d2", "e1", "e2", "f1", "f2", "f3", "g1", "h1",
              "i1", "i2", "i3", "j1", "k1", "l1", "l2", "l3", "m1", "n1",
              "o1", "p1")

HAIR_COLOUR = ("a", "b", "c", "d", "e", "f", "g", "h")
BEARD_STYLE = ("a", "b", "c", "d", "e", "f", "g")          # 7 for 8 values
BEARD_COLOUR = ("a", "b", "c", "d", "e", "f", "g")         # 7 for 8 values
SKIN_COLOUR = ("a", "b", "c", "d")
BUILD = ("a", "b", "c", "d", "e", "f", "g", "h")
BOOTS = ("A", "B", "C", "D", "E", "F", "G", "H")
FOOT = ("R", "L", "B")                                     # 3 for 4 values
OUT_OF_POSITION = ("no", "yes")

# Height and age are ranges, not names -- the upstream lists them one by one
# and `attributes.py` already carries the bias. Built here rather than pasted,
# so the two cannot drift.
HEIGHT = tuple(str(v) for v in range(attributes.BY_NAME["height"].low,
                                     attributes.BY_NAME["height"].high + 1))
AGE = tuple(str(v) for v in range(attributes.BY_NAME["age"].low,
                                  attributes.BY_NAME["age"].high + 1))
SKILL = tuple(str(v) for v in range(attributes.BY_NAME["speed"].low,
                                    attributes.BY_NAME["speed"].high + 1))

# The ten outfield positional roles. Stored as index + 2 -- see formation.py.
ROLE = ("CB-L", "CB-R", "SW", "LIB", "CB-C", "LB", "RB", "DH-L", "DH-C",
        "DH-R", "LH", "RH", "OH-L", "OH-C", "OH-R", "CF-L", "CF-C", "CF-R",
        "LW", "RW")

# The seventeen formation presets the upstream ships. NAMES ONLY: the
# coordinates behind them are its own table and there is no oracle for them
# (section 5.6, item 3).
FORMATION_PRESET = ("Stock", "4-5-1A", "4-5-1B", "4-4-2A", "4-4-2B", "4-3-3A",
                    "4-3-3B", "3-6-1A", "3-6-1B", "3-5-2A", "3-5-2B", "3-4-3A",
                    "3-4-3B", "5-4-1A", "5-4-1B", "5-3-2A", "5-3-2B")

# Which attribute field each table names, and which combo box it came from.
# Tables with no attribute field (ROLE, FORMATION_PRESET) are absent here.
FOR_FIELD = {
    "position": ("cmbposition", POSITION),
    "hair_style": ("cmbhair", HAIR_STYLE),
    "hair_colour": ("cmbhaircolor", HAIR_COLOUR),
    "beard_style": ("cmbhairface", BEARD_STYLE),
    "beard_colour": ("cmbhaircolorface", BEARD_COLOUR),
    "skin_colour": ("cmbskincolor", SKIN_COLOUR),
    "build": ("cmbbody", BUILD),
    "boots": ("cmbboots", BOOTS),
    "foot": ("cmbfood", FOOT),
    "out_of_position": ("cmbfeedoutside", OUT_OF_POSITION),
    "height": ("cmbheigth", HEIGHT),
    "age": ("cmbage", AGE),
}

# Not tied to an attribute field; still transcribed and still checkable.
FOR_COMBO = {
    "cbplayer1": ROLE,
    "LstFormation": FORMATION_PRESET,
}


class DomainError(Exception):
    """An index outside what the field holds."""


def label(field: str, index: int) -> str:
    """The upstream's name for `index`, or `UNNAMED` when it named none.

    Out of the FIELD's range raises; inside the range but past the label list
    returns `UNNAMED`. The two cases are different and must stay different: the
    first is a bug, the second is a gap in someone else's naming.
    """
    if field not in FOR_FIELD:
        raise DomainError(f"no label table for {field!r}")
    f = attributes.BY_NAME[field]
    if not f.low <= index <= f.high:
        raise DomainError(
            f"{field}={index} is outside {f.low}..{f.high}")
    _, table = FOR_FIELD[field]
    offset = index - f.low
    return table[offset] if offset < len(table) else UNNAMED


def unnamed_indices(field: str) -> list[int]:
    """The in-range indices the upstream never named."""
    f = attributes.BY_NAME[field]
    _, table = FOR_FIELD[field]
    return [f.low + i for i in range(len(table), f.high - f.low + 1)]


# --- re-reading the upstream ----------------------------------------------

_ITEMS = re.compile(r"Me\.(\w+)\.Items\.AddRange\(New Object\(\) \{([^}]*)\}")
_SOURCES = (
    os.path.join("lite", "fifatomcr", "Frmmcr.designer.vb"),
    os.path.join("lite", "fifatomcr", "FrmFormation.Designer.vb"),
)


def upstream_lists(clone: str) -> dict[str, tuple[str, ...]]:
    out: dict[str, tuple[str, ...]] = {}
    found = False
    for rel in _SOURCES:
        path = os.path.join(clone, rel)
        if not os.path.isfile(path):
            continue
        found = True
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        for m in _ITEMS.finditer(text):
            out.setdefault(
                m.group(1),
                tuple(v.strip().strip('"') for v in m.group(2).split(",")))
    if not found:
        raise DomainError(
            f"none of {_SOURCES} under {clone}. The upstream clone is "
            f"gitignored; see MCR-TASK-02 for how it is fetched.")
    return out


def check(clone: str, verbose: bool = True) -> list[str]:
    """Every transcribed table has to equal the upstream's, item for item."""
    lists = upstream_lists(clone)
    problems = []
    pairs = [(combo, table) for combo, table in FOR_FIELD.values()]
    pairs += list(FOR_COMBO.items())
    for combo, table in pairs:
        if combo not in lists:
            problems.append(f"{combo} not found in the upstream source")
            continue
        if lists[combo] != table:
            problems.append(
                f"{combo}: upstream has {len(lists[combo])} items "
                f"{lists[combo][:4]}..., we transcribed {len(table)} "
                f"{table[:4]}...")
    if verbose:
        print(f"domains.py --check: {len(pairs) - len(problems)}/{len(pairs)} "
              f"label tables match the upstream source")
        for p in problems:
            print(f"  FAIL {p}")
    return problems


# --- self-check ------------------------------------------------------------

def self_check(verbose: bool=True) -> int:
    return harness.run("domains.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(DomainError)
    ok("20 positional roles", len(ROLE) == 20, f"n={len(ROLE)}")
    ok("17 formation presets", len(FORMATION_PRESET) == 17,
       f"n={len(FORMATION_PRESET)}")
    ok("32 hairstyles", len(HAIR_STYLE) == 32, f"n={len(HAIR_STYLE)}")
    ok("8 positions", len(POSITION) == 8)
    ok("no label table has a duplicate",
       all(len(set(t)) == len(t) for _, t in FOR_FIELD.values())
       and len(set(ROLE)) == 20 and len(set(FORMATION_PRESET)) == 17)

    # No table may claim MORE than the field holds -- that would be a wrong
    # transcription, not a gap in naming.
    over = [f for f in FOR_FIELD
            if len(FOR_FIELD[f][1])
            > attributes.BY_NAME[f].high - attributes.BY_NAME[f].low + 1]
    ok("no table has more labels than its field has values", over == [],
       f"over={over}")

    # And the three that have fewer, named so the shortfall is on the record.
    short = {f: unnamed_indices(f) for f in FOR_FIELD if unnamed_indices(f)}
    ok("exactly three fields are short of labels",
       sorted(short) == ["beard_colour", "beard_style", "foot"],
       f"short={short}")
    ok("and each is short by exactly one index",
       all(len(v) == 1 for v in short.values()), f"short={short}")

    ok("height and age are built from the codec's own bias",
       HEIGHT[0] == "148" and HEIGHT[-1] == "211"
       and AGE[0] == "15" and AGE[-1] == "46"
       and len(HEIGHT) == 64 and len(AGE) == 32)
    ok("the skill range is 12..19", SKILL == tuple(str(v) for v in range(12, 20)))

    ok("label() names a value inside the list",
       attempt("label position 0", lambda: label("position", 0)) == "gk")
    ok("label() marks an in-range value the upstream never named",
       attempt("label foot 3", lambda: label("foot", 3)) == UNNAMED)
    refuses("label() refuses an out-of-range value",
            lambda: label("foot", 4), "outside 0..3")
    refuses("label() refuses a field with no table",
            lambda: label("speed", 12), "no label table")

    # --- against the upstream clone
    clone = layout.find_upward(os.path.join("work", "easy-mcr"))
    if clone is None:
        print("  skip  the upstream label tables (no work/easy-mcr)")
    else:
        problems = attempt("the upstream check runs",
                           lambda: check(clone, verbose=False), default=None)
        ok("every transcribed table matches the upstream source",
           problems == [], f"problems={problems}")


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", metavar="CLONE", nargs="?", const="work/easy-mcr",
                    help="re-read the tables from the upstream VB source")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0

    if a.check:
        try:
            return 1 if check(a.check) else 0
        except DomainError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2

    print("label tables -- THIRD-PARTY NAMES, no oracle (section 5.6)\n")
    for field, (combo, table) in sorted(FOR_FIELD.items()):
        f = attributes.BY_NAME[field]
        span = f.high - f.low + 1
        gap = "" if len(table) == span else f"   <-- {span - len(table)} unnamed"
        head = ", ".join(table[:8]) + ("..." if len(table) > 8 else "")
        print(f"  {field:<16} {len(table):>3} of {span:<3} [{combo}]{gap}")
        print(f"      {head}")
    print(f"\n  role             {len(ROLE):>3}   {', '.join(ROLE[:6])}...")
    print(f"  formation preset {len(FORMATION_PRESET):>3}   "
          f"{', '.join(FORMATION_PRESET[:5])}...")
    return 0


if __name__ == "__main__":
    sys.exit(main())

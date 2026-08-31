#!/usr/bin/env python3
"""Relate the two player-name tables -- phase 2, and it answers phase 3.

There are two of them and they are not two halves of anything:

  `SELECTC.BIN` @17604   1399 entries, NUL-terminated, variable length
  the boot executable    1449 entries, fixed 10 bytes, stored backwards

The 50-entry gap looked like the boot table holding names the other one
lacks. Measured, it is the opposite, and the real answer is worth more
than the question:

  **the two hold exactly the same 1399 distinct names** -- none is
  exclusive to either;
  `SELECTC.BIN` holds each name **once**; the boot table repeats **50**
  of them a second time;
  `SELECTC.BIN` is an exact **subsequence** of the boot table reversed.

So `SELECTC.BIN` is a **deduplicated string pool** and the boot table is
**slot-ordered**: a player who belongs to two squads gets two records
there and one here.

That explains section 3.3 without any appeal to missing data. The five
squads that only match inside the boot table -- France, Germany, Norway,
Argentina, Australia -- each contain exactly one player whose name is
duplicated, so in the pool their 23 slots collapse to 22 and stop being a
contiguous run. Nothing is missing; the pool simply does not repeat.

And 45 of the 50 repeats sit in one window of 46 slots, which is 2 x 23:
the two *elite* squads, whose members are by construction already in a
national squad.

Usage:

    python3 tools/pes2/player_map.py <track1.bin>
    python3 tools/pes2/player_map.py <track1.bin> --check
    python3 tools/pes2/player_map.py <track1.bin> --duplicates
"""

import argparse
import difflib
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import tables as T                                           # noqa: E402

POOL = "player-names"
SLOTS = "player-names-boot"
SQUAD = 23

# Measured on 2026-08-30, identical in (EsIt) and (EnFrDe).
EXPECT = {
    "pool": 1399,
    "slots": 1449,
    "distinct": 1399,
    "only_in_pool": 0,
    "only_in_slots": 0,
    "repeats": 50,
    "pool_is_subsequence": True,
}


def load(img):
    out = {}
    for key in (POOL, SLOTS):
        t = next(x for x in T.TABLES if x.key == key)
        path, _, entries = T.resolve(img, t)
        out[key] = (path, [(o, s.decode("latin-1")) for o, s in entries])
    return out


def analyse(img):
    data = load(img)
    pool = [s for _, s in data[POOL][1]]
    slots = [s for _, s in data[SLOTS][1]]
    backwards = slots[::-1]

    cp, cs = Counter(pool), Counter(slots)
    it = iter(backwards)
    subsequence = all(name in it for name in pool)

    ops = difflib.SequenceMatcher(None, pool, backwards,
                                  autojunk=False).get_opcodes()
    repeats = [len(slots) - 1 - j
               for tag, _, _, j1, j2 in ops if tag == "insert"
               for j in range(j1, j2)]
    runs = []
    for i in sorted(repeats):
        if runs and i == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], i)
        else:
            runs.append((i, i))

    return data, {
        "pool": len(pool),
        "slots": len(slots),
        "distinct": len(cp),
        "only_in_pool": sum(1 for n in cp if n not in cs),
        "only_in_slots": sum(1 for n in cs if n not in cp),
        "repeats": sum(v - 1 for v in cs.values()),
        "pool_is_subsequence": subsequence,
    }, runs, slots


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--duplicates", action="store_true",
                    help="where the 50 repeated slots are")
    args = ap.parse_args(argv)

    with Image(args.image) as img:
        data, got, runs, slots = analyse(img)

    print(f"  {POOL:20s} {data[POOL][0]:14s} {got['pool']:5d} entries")
    print(f"  {SLOTS:20s} {data[SLOTS][0]:14s} {got['slots']:5d} entries")
    print(f"  distinct names            {got['distinct']}")
    print(f"  only in the pool          {got['only_in_pool']}")
    print(f"  only in the slot table    {got['only_in_slots']}")
    print(f"  repeated slots            {got['repeats']}")
    print(f"  pool is a subsequence of the slot table reversed: "
          f"{got['pool_is_subsequence']}")

    if args.duplicates:
        print("\n  repeated slots, by index in the boot table:")
        for a, b in runs:
            n = b - a + 1
            print(f"    {a:5d}..{b:5d}  n={n:3d}  {slots[a]} … {slots[b]}"
                  + (f"   <- {n // SQUAD} squad(s) worth" if n >= SQUAD else ""))

    if args.check:
        if got != EXPECT:
            for k in EXPECT:
                if got[k] != EXPECT[k]:
                    print(f"CHECK FAILED {k}: {got[k]} != {EXPECT[k]}",
                          file=sys.stderr)
            return 1
        print("CHECK OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

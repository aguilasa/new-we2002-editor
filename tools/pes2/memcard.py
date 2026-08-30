#!/usr/bin/env python3
"""Align a PES2 memory card against the disc -- the measurement of plan 3.3.

The card is the cheapest lever in the whole project. Inside its option
save sit 1242 = 54 x 23 fixed 10-byte names: the 54 real national sides,
23 players each, in the game's own storage order. Finding each block of
23 on the disc gives the **exact boundary of that squad**, which no amount
of staring at hex does.

Section 3.3 of the plan reports the result -- 49 squads in `SELECTC.BIN`,
2 in the boot executable, 3 partial, and the storage order reversed in one
table and direct in the other. It reports it as prose. This is the script
that says it again, and can disagree.

Two things it settles that matter to every later phase:

  the squad size is 23, measured rather than assumed;
  **order is a property of the table, not of the game.** A reader that
  assumes one direction silently reverses 23 players per team in half the
  tables, and the result still looks like a squad.

Usage:

    python3 tools/pes2/memcard.py <card.mcd> <track1.bin>
    python3 tools/pes2/memcard.py <card.mcd> <track1.bin> --check
    python3 tools/pes2/memcard.py <card.mcd> --slots
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import tables as T                                           # noqa: E402

FRAME = 128
BLOCK = 8192
SQUAD = 23
NAME_RECORD = 10
NAMES_AT = 516          # offset of the name table inside the option save

# Measured on 2026-08-30 against `…(Es,It)_1.mcd` and the `(EsIt)` dump.
EXPECT = {"exact": 54, "selectc": 49, "boot": 5, "partial": 0}


def slots(card):
    """The occupied directory entries of a raw 128 KiB PSX card."""
    out = []
    for i in range(1, 16):
        fr = card[i * FRAME:(i + 1) * FRAME]
        state = int.from_bytes(fr[0:4], "little")
        if state != 0x51:                 # 0x51 = first block of a save
            continue
        size = int.from_bytes(fr[4:8], "little")
        name = fr[10:30].split(b"\x00")[0].decode("latin-1")
        out.append((i, name, size, card[i * BLOCK:i * BLOCK + size]))
    return out


def card_names(save):
    """The 1242 fixed 10-byte names of the option save."""
    out = []
    p = NAMES_AT
    while p + NAME_RECORD <= len(save):
        rec = save[p:p + NAME_RECORD]
        z = rec.find(b"\x00")
        body = rec if z < 0 else rec[:z]
        tail = b"" if z < 0 else rec[z:]
        if not body or any(c != 0 for c in tail) or \
                not all(0x20 <= c < 0x7F for c in body):
            break
        out.append(body.decode("latin-1"))
        p += NAME_RECORD
    return out


def best_window(haystack, needle):
    """(score, index, direction) of the best place `needle` fits."""
    rev = needle[::-1]
    best = (0, -1, "")
    n = len(needle)
    for i in range(len(haystack) - n + 1):
        window = haystack[i:i + n]
        fwd = sum(1 for a, b in zip(window, needle) if a == b)
        bwd = sum(1 for a, b in zip(window, rev) if a == b)
        if fwd > best[0]:
            best = (fwd, i, "direct")
        if bwd > best[0]:
            best = (bwd, i, "reverse")
    return best


def analyse(card_path, image_path):
    card = open(card_path, "rb").read()
    saves = slots(card)
    opt = next((s for s in saves if s[1].endswith("OPT")), None)
    if opt is None:
        raise ValueError(f"{card_path}: no …PES-OPT save on this card")
    names = card_names(opt[3])
    if len(names) % SQUAD:
        raise ValueError(f"{len(names)} names is not a whole number of "
                         f"{SQUAD}-player squads")
    squads = [names[i:i + SQUAD] for i in range(0, len(names), SQUAD)]

    with Image(image_path) as img:
        pools = {}
        for key in ("player-names", "player-names-boot"):
            t = next(x for x in T.TABLES if x.key == key)
            path, offset, entries = T.resolve(img, t)
            pools[key] = (path, [(o, s.decode("latin-1")) for o, s in entries])

    results = []
    for n, squad in enumerate(squads):
        best = None
        for key, (path, entries) in pools.items():
            score, i, direction = best_window([s for _, s in entries], squad)
            cand = (score, key, path, i, direction, entries)
            if best is None or score > best[0]:
                best = cand
        score, key, path, i, direction, entries = best
        results.append({
            "squad": n, "score": score, "table": key, "file": path,
            "index": i, "offset": entries[i][0], "direction": direction,
            "label": squad[0] if direction == "direct" else squad[-1],
            "names": squad,
        })
    return saves, squads, results


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", help="raw 128 KiB .mcd/.mcr memory card")
    ap.add_argument("image", nargs="?", help="the data track (.bin) of the disc")
    ap.add_argument("--slots", action="store_true", help="just list the saves")
    ap.add_argument("--check", action="store_true",
                    help="assert the counts of plan section 3.3")
    args = ap.parse_args(argv)

    if args.slots or not args.image:
        card = open(args.card, "rb").read()
        for i, name, size, _ in slots(card):
            print(f"  frame {i:2d}  {name:22s} {size:6d} B")
        return 0

    saves, squads, results = analyse(args.card, args.image)
    for i, name, size, _ in saves:
        print(f"  save   {name:22s} {size:6d} B")
    print(f"  {sum(len(s) for s in squads)} names = {len(squads)} squads "
          f"x {SQUAD}")
    print()

    counts = {"exact": 0, "selectc": 0, "boot": 0, "partial": 0}
    for r in results:
        exact = r["score"] == SQUAD
        counts["exact"] += exact
        if exact:
            counts["selectc" if r["table"] == "player-names" else "boot"] += 1
        else:
            counts["partial"] += 1
        mark = " " if exact else "~"
        print(f" {mark}squad {r['squad']:2d}  {r['score']:2d}/{SQUAD}  "
              f"{r['file']:14s} @{r['offset']:7d}  {r['direction']:7s}  "
              f"{r['names'][0]} … {r['names'][-1]}")
    print()
    print(f"  exact {counts['exact']}  "
          f"(SELECTC.BIN {counts['selectc']}, boot {counts['boot']})  "
          f"partial {counts['partial']}")

    if args.check:
        if counts != EXPECT:
            print(f"CHECK FAILED: {counts} != {EXPECT}", file=sys.stderr)
            return 1
        print("CHECK OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

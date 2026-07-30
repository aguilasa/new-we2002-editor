#!/usr/bin/env python3
"""Diff two CD images and describe the difference in terms the editor uses.

A raw `cmp -l` on a 474 MB image is unreadable. This groups the differing
bytes into contiguous runs and, for each run, reports:

  * which OFS_* region it falls in (nearest offset at or before the run),
  * which MODE2/2352 sector it lands in, and whether that is user data
    (bytes 24..2071) or header/EDC/ECC.

That last column is the one that matters most: the editor never recalculates
EDC/ECC, so a difference landing outside the data region means something is
writing where it should not.

  tools/golden_compare.py a.bin b.bin
  tools/golden_compare.py --json a.bin b.bin
"""

import argparse
import json
import re
import sys
from pathlib import Path

SECTOR = 2352
DATA_BEGIN = 24
DATA_END = 2072  # exclusive

# Runs closer together than this are reported as one.
COALESCE = 64

REPO = Path(__file__).resolve().parent.parent
OFFSETS_HPP = REPO / "src" / "core" / "include" / "we2002" / "Offsets.hpp"


def load_offsets():
    """Parse OFS_* out of the generated header, so this stays in sync."""
    text = OFFSETS_HPP.read_text(encoding="utf-8")
    found = re.findall(
        r"^inline constexpr \w+ (OFS_\w+)\s*=\s*(\d+)", text, re.MULTILINE
    )
    table = [(int(value), name) for name, value in found]
    table.sort()
    return table


def region_of(position, offsets):
    """Nearest OFS_* at or before `position`."""
    best = None
    for value, name in offsets:
        if value <= position:
            best = (value, name)
        else:
            break
    if best is None:
        return "before first offset", position
    return best[1], position - best[0]


def sector_of(position):
    sector, inside = divmod(position, SECTOR)
    if inside < DATA_BEGIN:
        kind = "header"
    elif inside < DATA_END:
        kind = "data"
    else:
        kind = "edc/ecc"
    return sector, inside, kind


# Maps 0x00 to 0x00 and every other byte to 0x01, so bytes.find can hunt for
# the next difference at C speed instead of one Python loop iteration per byte.
NONZERO = bytes([0] + [1] * 255)


def differing_positions(a, b, chunk=1 << 22):
    """Yield the index of every byte that differs, in order."""
    size = min(len(a), len(b))
    base = 0
    while base < size:
        end = min(base + chunk, size)
        block_a = a[base:end]
        block_b = b[base:end]
        if block_a == block_b:
            base = end
            continue
        # int.from_bytes/to_bytes keeps the XOR in C; a per-byte Python loop
        # over a 4 MiB chunk is roughly a thousand times slower.
        width = len(block_a)
        xor_int = int.from_bytes(block_a, "big") ^ int.from_bytes(block_b, "big")
        xor = xor_int.to_bytes(width, "big").translate(NONZERO)
        i = xor.find(1)
        while i != -1:
            yield base + i
            i = xor.find(1, i + 1)
        base = end


def diff_runs(a, b):
    """Yield (start, length, differing) for every run of differing bytes.

    `length` is the span of the run, which may include gaps of up to COALESCE
    identical bytes; `differing` is how many bytes inside it actually differ.
    """
    run_start = None
    run_end = None
    exact = 0
    for here in differing_positions(a, b):
        if run_start is None:
            run_start, run_end, exact = here, here + 1, 1
        elif here - run_end <= COALESCE:
            run_end = here + 1
            exact += 1
        else:
            yield run_start, run_end - run_start, exact
            run_start, run_end, exact = here, here + 1, 1
    if run_start is not None:
        yield run_start, run_end - run_start, exact


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--json", action="store_true", help="machine-readable")
    args = parser.parse_args()

    a = args.left.read_bytes()
    b = args.right.read_bytes()

    if len(a) != len(b):
        print(f"SIZE MISMATCH: {len(a)} vs {len(b)}", file=sys.stderr)

    offsets = load_offsets()
    runs = []
    total = 0
    for start, length, differing in diff_runs(a, b):
        name, delta = region_of(start, offsets)
        sector, inside, kind = sector_of(start)
        end_sector, _, end_kind = sector_of(start + length - 1)
        runs.append(
            {
                "start": start,
                "end": start + length - 1,
                "span": length,
                "bytes": differing,
                "region": name,
                "region_delta": delta,
                "sector": sector,
                "sector_offset": inside,
                "kind": kind if kind == end_kind else f"{kind}..{end_kind}",
                "sectors_spanned": end_sector - sector + 1,
            }
        )
        total += differing

    if args.json:
        json.dump({"total_bytes": total, "runs": runs}, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        if not runs:
            print("IDENTICAL")
            return 0
        print(f"{len(runs)} run(s), {total} byte(s) differ\n")
        header = (
            f"{'start':>10} {'end':>10} {'span':>7} {'diff':>7} "
            f"{'sector':>7} {'kind':>9}  region"
        )
        print(header)
        print("-" * len(header))
        for r in runs:
            print(
                f"{r['start']:>10} {r['end']:>10} {r['span']:>7} {r['bytes']:>7} "
                f"{r['sector']:>7} {r['kind']:>9}  "
                f"{r['region']}+{r['region_delta']}"
            )
        outside = [r for r in runs if "data" != r["kind"]]
        if outside:
            print(
                f"\nWARNING: {len(outside)} run(s) touch sector header or EDC/ECC"
            )
    return 1 if runs else 0


if __name__ == "__main__":
    sys.exit(main())

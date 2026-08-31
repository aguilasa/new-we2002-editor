#!/usr/bin/env python3
"""Compare the two European PES2 releases file by file -- phase 1.

Section 1.12 of the plan concludes "same game, one editor" from three
numbers: 236 files in common, 204 byte-identical, 32 different. Those
numbers were measured once, by hand, and had no way back. This is the way
back.

It also does what phase 1 still owes: saying **why** each of the 32
differs. A file whose size changed is localized text; a file that keeps
its size and changes content is the interesting kind, because that is
where game data could be hiding.

Usage:

    python3 tools/pes2/diff_releases.py <esit-track1.bin> <enfrde-track1.bin>
    python3 tools/pes2/diff_releases.py A.bin B.bin --markdown > out.md
    python3 tools/pes2/diff_releases.py A.bin B.bin --check
"""

import argparse
import os
import struct
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image, FORM2_DATA, RAW_SECTOR                # noqa: E402

# Measured on 2026-08-30 with this tool, against the two European dumps.
#
# These are not the numbers section 1.12 of the plan carried. It said 204
# identical and 32 different; the split below is 202 / 27, with 7 files
# neither: the seven `/SD/DA/*.DA` live past the end of track 1 and
# cannot be compared from it at all. The old pair was counted by hand and
# never written down as a procedure, which is exactly why this file
# exists.
EXPECT = {"common": 236, "identical": 202, "differ": 27, "incomparable": 7}


# PSX RAM, where every overlay is loaded.
RAM_LOW, RAM_HIGH = 0x80000000, 0x801FFFFF
# MIPS I opcodes whose low 16 bits carry an address half or an offset.
IMM16_OPS = {0x08, 0x09, 0x0F, 0x20, 0x21, 0x23, 0x24, 0x25, 0x28, 0x29, 0x2B}


def classify_word(va, vb):
    """Why one 32-bit word differs between the releases.

    The interesting question about the files that differ *without*
    changing size is whether they hold game data. They do not: they are
    MIPS overlays, and almost every differing word is the same code
    relocated, because the localized text ahead of it is a different
    length. Three shapes cover it --

      pointer   a full 0x800xxxxx address in both
      jump      a `j` or `jal` whose target moved
      imm16     a `lui`/`addiu`/load/store whose immediate moved, with
                the opcode and both registers unchanged

    -- and what is left over is worth reading one by one, because that is
    where a real difference would hide.
    """
    if RAM_LOW <= va <= RAM_HIGH and RAM_LOW <= vb <= RAM_HIGH:
        return "pointer", vb - va
    op = va >> 26
    if op != vb >> 26:
        return "other", None
    if op in (2, 3):                                   # j, jal
        return "jump", ((vb & 0x3FFFFFF) - (va & 0x3FFFFFF)) * 4
    if op in IMM16_OPS and (va & 0x03FF0000) == (vb & 0x03FF0000):
        return "imm16", (vb & 0xFFFF) - (va & 0xFFFF)
    return "other", None


def explain(a, b):
    """Break the differing words of one file down by classify_word."""
    words = sorted({i // 4 * 4 for i, (x, y) in enumerate(zip(a, b)) if x != y})
    kinds, deltas, leftovers = Counter(), Counter(), []
    for w in words:
        if w + 4 > min(len(a), len(b)):
            kinds["short"] += 1
            continue
        va = struct.unpack_from("<I", a, w)[0]
        vb = struct.unpack_from("<I", b, w)[0]
        kind, delta = classify_word(va, vb)
        kinds[kind] += 1
        if delta is not None:
            deltas[(kind, delta)] += 1
        else:
            leftovers.append((w, va, vb))
    relocated = kinds["pointer"] + kinds["jump"] + kinds["imm16"]
    return {
        "words": len(words), "kinds": kinds, "deltas": deltas,
        "leftovers": leftovers,
        "relocated": relocated / len(words) if words else 0.0,
    }


def classify(a, b):
    """Why two versions of one file differ."""
    if len(a) != len(b):
        return "size"
    n = sum(1 for x, y in zip(a, b) if x != y)
    return f"content ({n} B)"


def compare(img_a, img_b):
    names_a, names_b = set(img_a.files), set(img_b.files)
    common = sorted(names_a & names_b)
    only_a = sorted(names_a - names_b)
    only_b = sorted(names_b - names_a)

    identical, differ, incomparable = [], [], []
    for p in common:
        sa, sb = img_a.status(p), img_b.status(p)
        if sa == "outside" or sb == "outside":
            # The seven `/SD/DA/*.DA` are on the audio tracks (plan 5.2 and
            # 6.5). A multi-track dump keeps them in other files, so track 1
            # holds no version of them to compare. Saying so beats folding
            # them into either column.
            incomparable.append((p, sa, sb))
            continue
        if sa != "form1" or sb != "form1":
            # Form 2 has no 2048-byte area, so read_file refuses it. The raw
            # sectors are still there, and comparing those answers the
            # question the file-level compare was asking anyway.
            da, db = _raw(img_a, p), _raw(img_b, p)
        else:
            da, db = img_a.read_file(p), img_b.read_file(p)
        if da == db:
            identical.append(p)
        else:
            differ.append((p, len(da), len(db), classify(da, db)))
    return {
        "common": common, "only_a": only_a, "only_b": only_b,
        "identical": identical, "differ": differ, "incomparable": incomparable,
    }


def _raw(img, path):
    """Every raw byte a Form 2 file occupies, headers and all."""
    e = img.entry(path)
    n = (e.size + FORM2_DATA - 1) // FORM2_DATA
    img.f.seek(e.lba * RAW_SECTOR)
    return img.f.read(n * RAW_SECTOR)


def report(r, a_name, b_name, markdown=False):
    out = []
    add = out.append
    n_diff = len(r["differ"])
    if markdown:
        add(f"# Diff entre releases — `{a_name}` × `{b_name}`\n")
        add("Gerado por `tools/pes2/diff_releases.py`.\n")
        add("| Comparação | Resultado |")
        add("|---|---|")
        add(f"| arquivos em comum | {len(r['common'])} |")
        add(f"| byte a byte idênticos | **{len(r['identical'])}** |")
        add(f"| diferem | {n_diff} |")
        add(f"| não comparáveis do Track 1 | {len(r['incomparable'])} |")
        add(f"| exclusivos de A | {len(r['only_a'])} |")
        add(f"| exclusivos de B | {len(r['only_b'])} |")
        add("")
        add("## Os que diferem\n")
        add("| Arquivo | Tamanho A | Tamanho B | Diferença |")
        add("|---|---|---|---|")
        for p, la, lb, why in sorted(r["differ"]):
            add(f"| `{p}` | {la} | {lb} | {why} |")
        add("")
        add("## Fora do Track 1, logo não comparáveis\n")
        add("```")
        for p, sa, sb in sorted(r["incomparable"]):
            add(f"{p}   ({sa}/{sb})")
        add("```")
        add("")
        add("## Exclusivos\n")
        add("```")
        for p in r["only_a"]:
            add(f"A  {p}")
        for p in r["only_b"]:
            add(f"B  {p}")
        add("```")
    else:
        add(f"A = {a_name}")
        add(f"B = {b_name}")
        add(f"  in common   {len(r['common'])}")
        add(f"  identical   {len(r['identical'])}")
        add(f"  differ      {n_diff}")
        add(f"  not comparable from track 1   {len(r['incomparable'])}")
        add(f"  only in A   {len(r['only_a'])}")
        add(f"  only in B   {len(r['only_b'])}")
        add("")
        add("  differing files:")
        for p, la, lb, why in sorted(r["differ"]):
            add(f"    {p:28s} {la:8d} {lb:8d}  {why}")
        add("")
        add("  not comparable from track 1:")
        for p, sa, sb in sorted(r["incomparable"]):
            add(f"    {p:28s} {sa}/{sb}")
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("a", help="data track of one release")
    ap.add_argument("b", help="data track of the other")
    ap.add_argument("--markdown", action="store_true",
                    help="emit docs/samples/pes2-diff-releases.md")
    ap.add_argument("--check", action="store_true",
                    help="assert the counts of plan section 1.12")
    ap.add_argument("--explain", action="store_true",
                    help="break the same-size differences down word by word")
    args = ap.parse_args(argv)

    with Image(args.a) as ia, Image(args.b) as ib:
        r = compare(ia, ib)
        if args.explain:
            print("same-size differences, word by word:")
            for path, la, lb, why in sorted(r["differ"]):
                if la != lb:
                    continue
                e = explain(ia.read_file(path), ib.read_file(path))
                print(f"  {path:16s} {e['words']:6d} differing words, "
                      f"{e['relocated']:6.1%} relocation "
                      f"({dict(e['kinds'])})")
                for (kind, delta), n in e["deltas"].most_common(3):
                    print(f"       {n:6d} x {kind} {delta:+d}")
                for w, va, vb in e["leftovers"][:4]:
                    print(f"       left @{w:<8d} {va:#010x} -> {vb:#010x}")
                if len(e["leftovers"]) > 4:
                    print(f"       … and {len(e['leftovers']) - 4} more")
            print()
    print(report(r, os.path.basename(args.a), os.path.basename(args.b),
                 args.markdown))

    if args.check:
        got = {"common": len(r["common"]), "identical": len(r["identical"]),
               "differ": len(r["differ"]),
               "incomparable": len(r["incomparable"])}
        if got != EXPECT:
            print(f"\nCHECK FAILED: {got} != {EXPECT}", file=sys.stderr)
            return 1
        print("\nCHECK OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

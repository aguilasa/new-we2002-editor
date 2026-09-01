#!/usr/bin/env python3
"""Turn the 69 WE2002 offsets into (file, relative offset) -- phase 1.

Section 1.4 of the plan is the shortcut the whole project rests on: PES2
and WE2002 are the same disc tree, with the same overlays at the same LBA.
So the `OFS_*` of `newWe2002` -- already verified against `ed.exe`, byte
for byte -- are not trivia. They are **the index of where to look**.

But they are absolute offsets into a raw 2352-byte sector stream, and an
absolute offset is exactly the thing that does not carry across two discs.
This converts each one into the pair that does: the file it lands in, and
how far into that file's *data* it is. Sector headers are skipped on the
way, which is the whole difficulty -- 2048 usable bytes per 2352.

`--pes2` then takes the second step and says, per file, whether PES2 has
that file at all and how big it is. It does not claim the offsets match:
the tables move, which is section 1.12's whole point. It says where the
search starts.

Usage:

    python3 tools/pes2/ofs_map.py <we2002-image.bin>
    python3 tools/pes2/ofs_map.py <we2002-image.bin> --pes2 <pes2-track1.bin>
    python3 tools/pes2/ofs_map.py <we2002-image.bin> --markdown > out.md
"""

import argparse
import os
import re
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image, RAW_SECTOR, HEADER, FORM1_DATA        # noqa: E402
import tables as T                                           # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OFFSETS_HPP = os.path.join(REPO, "src", "core", "include", "we2002",
                           "Offsets.hpp")
DECL = re.compile(r"inline constexpr Offset\s+(OFS_\w+)\s*=\s*(\d+)\s*;")

# How many offsets the terminal summary prints per file before saying how
# many it left out. Four, not three, so that no file of four -- which is
# what /BIN/DAT2D.BIN holds -- is shown as three with the count saying 4.
SUMMARY_ROWS = 4

# Where an OFS_* and a table of tools/pes2/tables.py are the same thing in
# the two games. Only the five that are unambiguous: same file, same kind
# of content, and the PES2 side already located by marker. The rest need
# phase 2 to say what they are before a pairing means anything.
SAME_TABLE = {
    "OFS_TEAM_NAME_1": "team-names-ending",
    "OFS_TEAM_NAME_2": "team-names-result",
    "OFS_TEAM_ABBREV_2": "abbreviations-replays",
    "OFS_TEAM_ABBREV_3": "abbreviations-select8",
    "OFS_TEAM_MIXED_CASE_NAME": "team-names-selectc",
}


def read_offsets(path=OFFSETS_HPP):
    with open(path, encoding="utf-8") as fh:
        return [(m.group(1), int(m.group(2))) for m in DECL.finditer(fh.read())]


def locate(img, absolute):
    """(path, offset inside the file's data) for a raw image offset.

    The offset is calibrated to land in the 2048-byte user area, so the
    remainder must be between HEADER and HEADER+FORM1_DATA. Anything else
    means the offset points at a sector header or an EDC/ECC tail, and
    saying so is more useful than returning a number.
    """
    sector, inside = divmod(absolute, RAW_SECTOR)
    if not HEADER <= inside < HEADER + FORM1_DATA:
        return None, f"byte {inside} of sector {sector} is header or tail"
    inside -= HEADER
    for path, e in img.files.items():
        if e.lba <= sector < e.lba + e.sectors:
            return path, (sector - e.lba) * FORM1_DATA + inside
    return None, f"sector {sector} belongs to no file"


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", help="the WE2002 image the offsets were measured on")
    ap.add_argument("--pes2", help="a PES2 data track, to check the file exists")
    ap.add_argument("--markdown", action="store_true")
    args = ap.parse_args(argv)

    offsets = read_offsets()
    with Image(args.image) as img:
        located = [(name, value) + locate(img, value) for name, value in offsets]
        sizes = {p: img.files[p].size for p in img.files}

    pes2_sizes, pes2_tables, pes2_boot = {}, {}, None
    if args.pes2:
        with Image(args.pes2) as p2:
            pes2_sizes = {p: p2.files[p].size for p in p2.files}
            pes2_boot = T.boot_executable(p2)
            for key in set(SAME_TABLE.values()):
                t = next(x for x in T.TABLES if x.key == key)
                _, off, _ = T.resolve(p2, t)
                pes2_tables[key] = off

    by_file = defaultdict(list)
    unplaced = []
    for name, value, path, rel in located:
        if path is None:
            unplaced.append((name, value, rel))
        else:
            by_file[path].append((name, value, rel))

    order = sorted(by_file, key=lambda p: -len(by_file[p]))

    if args.markdown:
        print("# PES2 — os 69 `OFS_*` do WE2002 como (arquivo, offset relativo)\n")
        print("Gerado por `tools/pes2/ofs_map.py`. A coluna *absoluto* é o "
              "valor de [`Offsets.hpp`](../../src/core/include/we2002/Offsets.hpp), "
              "medido na imagem do WE2002; as duas seguintes são o mesmo "
              "ponto expresso de um jeito que atravessa discos.\n")
        print("**Isto não afirma que o offset relativo vale no PES2.** As "
              "tabelas se deslocam entre releases do próprio PES2 (§1.12), "
              "que dirá entre jogos. O que a tabela dá é o arquivo onde "
              "procurar e a ordem de grandeza — que é a diferença entre "
              "busca dirigida e varredura cega.\n")
        if pes2_sizes:
            print("| Arquivo | `OFS_*` | Existe no PES2 | Tamanho WE2002 | Tamanho PES2 |")
            print("|---|---:|---|---:|---:|")
            for p in order:
                here = pes2_sizes.get(p)
                note = "sim"
                if here is None:
                    # The boot executable is the one file whose *name* is
                    # release-specific: SLPM_870.56 there, SLES_039.57 here.
                    note = (f"sim, como `{pes2_boot.lstrip('/')}`"
                            if pes2_boot and p.lstrip("/").startswith("SLPM")
                            else "**não**")
                    here = pes2_sizes.get(pes2_boot) if pes2_boot else None
                print(f"| `{p}` | {len(by_file[p])} | {note} | "
                      f"{sizes.get(p, 0)} | {here if here else '—'} |")
            print()
            print("## Os cinco pares que já se pode afirmar\n")
            print("Mesma tabela, mesmo arquivo, nos dois jogos. O "
                  "deslocamento é o que sobra depois de tirar arquivo e "
                  "tipo de conteúdo da conta.\n")
            print("| `OFS_*` | Arquivo | WE2002 | PES2 `(EsIt)` | Δ |")
            print("|---|---|---:|---:|---:|")
            for name, value, path, rel in located:
                if name not in SAME_TABLE or path is None:
                    continue
                there = pes2_tables[SAME_TABLE[name]]
                print(f"| `{name}` | `{path}` | {rel} | {there} | "
                      f"{there - rel:+d} |")
            print()
        for p in order:
            print(f"### `{p}`\n")
            print("| `OFS_*` | absoluto | relativo |")
            print("|---|---:|---:|")
            for name, value, rel in sorted(by_file[p], key=lambda r: r[2]):
                print(f"| `{name}` | {value} | {rel} |")
            print()
        if unplaced:
            print("### Não localizados\n")
            print("| `OFS_*` | absoluto | por quê |")
            print("|---|---:|---|")
            for name, value, why in unplaced:
                print(f"| `{name}` | {value} | {why} |")
    else:
        print(f"{len(offsets)} offsets, {len(by_file)} files, "
              f"{len(unplaced)} unplaced")
        for p in order:
            mark = ""
            if pes2_sizes:
                mark = "  in PES2" if p in pes2_sizes else "  NOT IN PES2"
            print(f"  {p:24s} {len(by_file[p]):3d}{mark}")
            # The summary shows the first few and then *says how many it is
            # not showing*. Silently cutting at three put the header's count
            # and the list under it in contradiction on the same screen, and
            # that is how `OFS_FLAG_COLOURS_B` -- the fourth of four in
            # /BIN/DAT2D.BIN -- came to be missing from a list the plan then
            # copied as complete (CORR-PES2-015).
            rows = sorted(by_file[p], key=lambda r: r[2])
            for name, value, rel in rows[:SUMMARY_ROWS]:
                print(f"      {name:32s} {value:9d} -> {rel}")
            if len(rows) > SUMMARY_ROWS:
                print(f"      ... and {len(rows) - SUMMARY_ROWS} more; "
                      f"the full list is in the markdown output")
        for name, value, why in unplaced:
            print(f"  UNPLACED {name} = {value}: {why}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

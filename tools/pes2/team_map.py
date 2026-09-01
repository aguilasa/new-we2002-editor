#!/usr/bin/env python3
"""Align the eight team-name lists against each other -- phase 2.

Section 6.1 of the plan says a written copy is worse than no copy, and
section 6.3 of docs/PES2-AJUSTES.md says the word "copy" is the trap: the
lists hold 106, 99, 95, 94, 123, 32, 99 and 99 entries and differ in
*content*, not merely in extent. Index 34 is `ALWAYS ARGENTINA` in one of
them and `Classic Brazil` in another.

So an editor cannot write "team 34" to eight places. It needs, per team,
the set of (file, offset) that actually hold that team -- which is what
this computes, by matching on the name rather than on the position.

**Eight, not five.** The plan measured five until 2026-09-01, when the
poke of PES2-TASK-02 wrote all five and then swept the disc for the old
name: `SELECT.BIN` carries a *second*, mixed-case list of the 32
fictitious clubs, and `SELECT3.BIN` and `SELFORM.BIN` each carry the
99-entry list byte for byte. Five writes would have left three screens
showing the old name -- which is section 6.1 exactly.

The canonical list is `SELECT.BIN` @3128, the only one with all 106
entries. Every other list is expressed as a sequence of **runs** into it,
plus whatever it holds that the canonical list does not.

Usage:

    python3 tools/pes2/team_map.py <track1.bin>
    python3 tools/pes2/team_map.py <track1.bin> --team 34
    python3 tools/pes2/team_map.py <track1.bin> --markdown > out.md
    python3 tools/pes2/team_map.py <track1.bin> --check
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import tables as T                                           # noqa: E402

CANONICAL = "team-names"
COPIES = ["team-names-selectc", "team-names-ending",
          "team-names-result", "team-names-replays",
          "team-names-select2", "team-names-select3",
          "team-names-selform"]

# Measured on 2026-08-30, identical in (EsIt) and (EnFrDe). A run is
# (first copy index, last copy index, first canonical index); `None` for a
# stretch the canonical list does not contain.
EXPECT = {
    "team-names-selectc": [(0, 3, None), (4, 98, 2)],
    "team-names-ending": [(0, 94, 2)],
    "team-names-result": [(0, 31, 2), (32, 36, 97), (37, 39, 103),
                          (40, 93, 43)],
    "team-names-replays": [(0, 31, 2), (32, 59, None), (60, 122, 34)],
    # Measured on 2026-09-01, when the sweep of PES2-TASK-02 found them.
    "team-names-select2": [(0, 31, 2)],
    "team-names-select3": [(0, 3, None), (4, 98, 2)],
    "team-names-selform": [(0, 3, None), (4, 98, 2)],
}


def lists_of(img):
    out = {}
    for key in [CANONICAL] + COPIES:
        t = next(x for x in T.TABLES if x.key == key)
        path, _, entries = T.resolve(img, t)
        out[key] = (path, [(o, s.decode("latin-1")) for o, s in entries])
    return out


def runs_of(canon_upper, copy_names):
    """Compress a copy into runs of consecutive canonical indices."""
    runs = []
    previous = None
    for i, name in enumerate(copy_names):
        c = canon_upper.index(name.upper()) if name.upper() in canon_upper else None
        if runs and c is not None and previous is not None and c == previous + 1 \
                and runs[-1][2] is not None:
            runs[-1] = (runs[-1][0], i, runs[-1][2])
        elif runs and c is None and runs[-1][2] is None:
            runs[-1] = (runs[-1][0], i, None)
        else:
            runs.append((i, i, c))
        previous = c
    return runs


def where(lists, canonical_index):
    """Every (key, file, offset, copy index) that holds one canonical team."""
    name = lists[CANONICAL][1][canonical_index][1].upper()
    out = [(CANONICAL,) + (lists[CANONICAL][0],
                           lists[CANONICAL][1][canonical_index][0],
                           canonical_index)]
    for key in COPIES:
        path, entries = lists[key]
        for i, (off, s) in enumerate(entries):
            if s.upper() == name:
                out.append((key, path, off, i))
                break
    return out


def report(lists, markdown=False):
    canon_path, canon = lists[CANONICAL]
    canon_upper = [s.upper() for _, s in canon]
    out = []
    add = out.append

    if markdown:
        add(f"# PES2 — as {len(COPIES) + 1} listas de nome de time, "
            f"alinhadas\n")
        add("Gerado por `tools/pes2/team_map.py`. Offsets de `(EsIt)`.\n")
        add(f"A lista canônica é `SELECT.BIN` @3128, a única com as 106 "
            f"entradas. As outras {len(COPIES)} são expressas como "
            f"**trechos** dela.\n")
        add("| Lista | Arquivo | Entradas | Estrutura |")
        add("|---|---|---:|---|")
        add(f"| canônica | `{canon_path}` | {len(canon)} | 2 de cabeçalho "
            f"+ 32 fictícios + 7 temáticas + 2 *elite* + 54 reais + 7 "
            f"*classic* + 2 *allstars* |")
    else:
        add(f"canonical  {canon_path:14s} {len(canon)} entries")

    for key in COPIES:
        path, entries = lists[key]
        runs = runs_of(canon_upper, [s for _, s in entries])
        parts = []
        for a, b, c in runs:
            span = f"{a}" if a == b else f"{a}–{b}"
            parts.append(f"[{span}] → fora" if c is None
                         else f"[{span}] → canônica[{c}–{c + b - a}]")
        if markdown:
            add(f"| `{key}` | `{path}` | {len(entries)} | "
                + "; ".join(parts) + " |")
        else:
            add(f"  {key:22s} {path:14s} {len(entries):4d}  "
                + "  ".join(parts))

    extras = {}
    for key in COPIES:
        _, entries = lists[key]
        extras[key] = [s for _, s in entries if s.upper() not in canon_upper]

    if markdown:
        add("")
        add("## O que a canônica não tem\n")
        for key in COPIES:
            if not extras[key]:
                continue
            add(f"**`{key}`** — {len(extras[key])} entradas:\n")
            add("```")
            add(", ".join(extras[key]))
            add("```")
            add("")
        add("## As quatro armadilhas que este alinhamento fecha\n")
        add("1. **`RESULT.BIN` pula nove e traz oito outras.** Onde a "
            "canônica tem as 7 seleções temáticas e as 2 *elite* "
            "(índices 34–42), ela não tem nada; e no lugar traz 6 dos 7 "
            "*classic* mais as 2 *allstars*. **`CLASSIC FRANCE`, índice "
            "canônico 102, não existe nela.**")
        add("2. **`REPLAYS.BIN` insere 28 entradas no meio** — `Edit`, "
            "`Free`, `Default` e 25 nações que só o modo de edição "
            "conhece — entre os fictícios e as seleções temáticas.")
        add("3. **`SELECTC.BIN` insere 4 no começo** — `Belarus`, "
            "`Georgia`, `Uzbekistan`, `Iceland`. `SELECT3.BIN` e "
            "`SELFORM.BIN` trazem a mesma lista, com o mesmo digest.")
        add("4. **`SELECT.BIN` tem duas listas, não uma.** Além da "
            "canônica em caixa alta, uma segunda em caixa mista @33188 "
            "com os 32 clubes fictícios e nada mais — ela termina em "
            "`Aragon` e emenda direto nas strings de interface "
            "localizadas. Ficou fora do mapa até 2026-09-01.")
        add("")
        add("Nenhuma das quatro é visível para quem casa listas por "
            "índice, e todas fazem o editor gravar no time errado com um "
            "nome plausível — ou deixar de gravar e mostrar o nome velho "
            "numa tela.")
        add("")
        add("## Cobertura por time\n")
        add(f"Quantas das {len(COPIES) + 1} listas contêm cada faixa da "
            f"canônica.\n")
        add("| Faixa canônica | O que é | Em quantas listas |")
        add("|---|---|---:|")
        bands = [(0, 1, "cabeçalho (`MASTER DATA`, `? ? ? ?`)"),
                 (2, 33, "32 clubes fictícios"),
                 (34, 40, "7 seleções temáticas"),
                 (41, 42, "`WORLD ELITE`, `EURO ELITE`"),
                 (43, 96, "54 seleções reais"),
                 (97, 103, "7 *classic*"),
                 (104, 105, "`WORLD ALLSTARS`, `EURO ALLSTARS`")]
        for a, b, label in bands:
            counts = {len(where(lists, i)) for i in range(a, b + 1)}
            n = "–".join(str(x) for x in sorted(counts))
            add(f"| {a}–{b} | {label} | {n} |")
    else:
        for key in COPIES:
            if extras[key]:
                add(f"  {key} has {len(extras[key])} not in canonical: "
                    + ", ".join(extras[key][:6])
                    + (" …" if len(extras[key]) > 6 else ""))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--team", type=int, metavar="N",
                    help="every place canonical team N is stored")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--check", action="store_true",
                    help="assert the run structure measured on 2026-08-30")
    args = ap.parse_args(argv)

    with Image(args.image) as img:
        lists = lists_of(img)

        if args.team is not None:
            canon = lists[CANONICAL][1]
            if not 0 <= args.team < len(canon):
                print(f"canonical index must be 0..{len(canon) - 1}",
                      file=sys.stderr)
                return 1
            name = canon[args.team][1]
            print(f"canonical[{args.team}] = {name!r}")
            for key, path, off, i in where(lists, args.team):
                print(f"  {key:22s} {path:14s} @{off:7d}  index {i}")
            return 0

        print(report(lists, args.markdown))

        if args.check:
            canon_upper = [s.upper() for _, s in lists[CANONICAL][1]]
            bad = 0
            for key in COPIES:
                got = runs_of(canon_upper, [s for _, s in lists[key][1]])
                if got != EXPECT[key]:
                    print(f"\nCHECK FAILED {key}:\n  got      {got}"
                          f"\n  expected {EXPECT[key]}", file=sys.stderr)
                    bad += 1
            if bad:
                return 1
            print("\nCHECK OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

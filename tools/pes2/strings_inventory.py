#!/usr/bin/env python3
"""Sweep every readable file for text, and classify it -- phase 2.

Section 1.6 closed eleven tables. This closes the question those eleven
leave open: **what else on this disc is text, and is any of it database?**

Ranking whole files does not answer it. `SELECT.BIN` is 216 kB of MIPS
code with a 6 kB island of tables in it, so by any per-file measure it
sinks below files that are uniformly noisy. What a table looks like is a
**block**: many printable runs packed together with almost nothing
between them. So the sweep finds runs, groups them into blocks, and ranks
the blocks.

Every Form 1 file is scanned for printable ASCII runs, and each run is put
in one of six buckets. Five of them are already understood; the sixth is
the output that matters.

  team        matches an entry of the canonical team list
  abbrev      matches an entry of the abbreviation table
  player      matches an entry of the player-name pool
  namelike    shaped like a name but in neither list -- one short word,
              initial capital, some lower case. This bucket exists
              because without it those runs land in `interface` and
              disappear: SELECTC.BIN holds three further blocks of them
              past the end of the known pool
  path        looks like a disc path or a filename
  interface   prose -- has a space or lower case and is long enough to be
              a label rather than a token
  unknown     everything else, which is where phase 2 has left to look

The buckets are deliberately checked in that order: a string that is both
a player name and a plausible label is a player name.

Usage:

    python3 tools/pes2/strings_inventory.py <track1.bin>
    python3 tools/pes2/strings_inventory.py <track1.bin> --markdown > out.md
    python3 tools/pes2/strings_inventory.py <track1.bin> --file /SELECT.BIN
    python3 tools/pes2/strings_inventory.py <track1.bin> --show 3
"""

import argparse
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402
import tables as T                                           # noqa: E402

MIN_RUN = 6
# 95 of 256 byte values are printable ASCII, so random data produces runs
# on its own. A 24 MB compressed audio file yields tens of thousands of
# them, and a naive sweep ranks it above every overlay that actually holds
# text. Each file is therefore scored against what chance alone would give
# it -- see `excess_of`.
PRINTABLE_P = 95 / 256
PATH = re.compile(r"^[A-Z0-9_\\/.]*\.(BIN|STR|DA|CNF|EXE|TIM|RA|SEQ|VB)\b", re.I)
BUCKETS = ["team", "abbrev", "player", "namelike", "path", "interface",
           "unknown"]


def expected_runs(size, min_run):
    """How many runs of `min_run`+ printable bytes uniform noise would give.

    A run starts where a non-printable byte is followed by `min_run`
    printable ones, so the count is about
    size x (1 - p) x p**min_run.
    """
    return max(1.0, size * (1 - PRINTABLE_P) * PRINTABLE_P ** min_run)


def excess_of(observed, size, min_run):
    """Observed runs over what chance predicts. ~1 means the file is noise."""
    return observed / expected_runs(size, min_run)


def blocks_of(runs, gap=24, least=12):
    """Group runs into dense blocks.

    `gap` is how much slack may sit between the end of one run and the
    start of the next and still count as the same block. Tables pad to a
    4-byte boundary and leave a few NUL, so 24 is generous without
    swallowing a whole file. A block of fewer than `least` runs is not a
    table, it is a couple of labels.
    """
    out = []
    for start, text, bucket in runs:
        end = start + len(text)
        if out and start - out[-1]["end"] <= gap:
            out[-1]["end"] = end
            out[-1]["items"].append((start, text, bucket))
        else:
            out.append({"start": start, "end": end,
                        "items": [(start, text, bucket)]})
    return [b for b in out if len(b["items"]) >= least]


def vocabularies(img):
    """The three known word lists, upper-cased for matching."""
    def entries(key):
        t = next(x for x in T.TABLES if x.key == key)
        _, _, e = T.resolve(img, t)
        return {s.decode("latin-1").upper() for s in (x[1] for x in e)}

    teams = set()
    for key in ("team-names", "team-names-selectc", "team-names-ending",
                "team-names-result", "team-names-replays"):
        teams |= entries(key)
    players = entries("player-names") | entries("player-names-boot")
    return teams, entries("abbreviations"), players


def bucket_of(s, teams, abbrevs, players):
    up = s.upper()
    if up in teams:
        return "team"
    if len(s) == 3 and up in abbrevs:
        return "abbrev"
    if up in players:
        return "player"
    if PATH.match(s):
        return "path"
    if (len(s) <= 12 and " " not in s and s[0].isupper()
            and any(c.islower() for c in s) and s.isascii()
            and all(c.isalpha() or c in ".-'" for c in s)):
        return "namelike"
    if len(s) >= 6 and (" " in s or any(c.islower() for c in s)):
        return "interface"
    return "unknown"


def sweep(img, only=None, min_run=MIN_RUN):
    run = re.compile(rb"[\x20-\x7E]{%d,}" % min_run)
    teams, abbrevs, players = vocabularies(img)
    per_file = {}
    for path in sorted(img.files):
        if only and path != only:
            continue
        if img.status(path) != "form1":
            continue
        data = img.read_file(path)
        counts = Counter()
        samples = defaultdict(list)
        found = []
        for m in run.finditer(data):
            s = m.group().decode("latin-1")
            b = bucket_of(s, teams, abbrevs, players)
            counts[b] += 1
            found.append((m.start(), s, b))
            if len(samples[b]) < 6:
                samples[b].append((m.start(), s))
        if sum(counts.values()):
            per_file[path] = (counts, samples, len(data),
                              excess_of(sum(counts.values()), len(data),
                                        min_run),
                              blocks_of(found))
    return per_file


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--file", help="only this disc path")
    ap.add_argument("--show", type=int, default=0,
                    help="print this many entries of each block")
    ap.add_argument("--markdown", action="store_true")
    ap.add_argument("--top", type=int, default=25,
                    help="how many files to list (default 25)")
    ap.add_argument("--min-run", type=int, default=MIN_RUN,
                    help=f"shortest run to count (default {MIN_RUN})")
    ap.add_argument("--excess", type=float, default=4.0,
                    help="a file whose run count is below this multiple of "
                         "what chance predicts is treated as noise "
                         "(default 4)")
    args = ap.parse_args(argv)

    with Image(args.image) as img:
        per_file = sweep(img, args.file, args.min_run)

    total = Counter()
    for counts, *_ in per_file.values():
        total.update(counts)

    # One row per dense block, which is what a table looks like from here.
    rows = []
    for path, (_, _, _, _, blocks) in per_file.items():
        for b in blocks:
            kinds = Counter(k for _, _, k in b["items"])
            main, _ = kinds.most_common(1)[0]
            rows.append({
                "path": path, "start": b["start"],
                "span": b["end"] - b["start"], "n": len(b["items"]),
                "density": len(b["items"]) * min(
                    16, sum(len(t) for _, t, _ in b["items"]) / len(b["items"])
                ) / max(1, b["end"] - b["start"]),
                "kind": main, "kinds": kinds,
                "first": b["items"][0][1], "last": b["items"][-1][1],
            })
    rows.sort(key=lambda r: -r["n"])

    if args.markdown:
        print("# PES2 — inventário de texto do disco\n")
        print("Gerado por `tools/pes2/strings_inventory.py`. Trechos "
              f"imprimíveis de {args.min_run} caracteres ou mais, em todos "
              "os arquivos Form 1, agrupados em **blocos densos** — que é a "
              "forma que uma tabela tem daqui de fora.\n")
        print(f"{len(per_file)} arquivos com trecho imprimível, "
              f"{sum(total.values())} trechos, **{len(rows)} blocos**.\n")
        labels = {
            "team": "casa com a lista canônica de nome de time",
            "abbrev": "casa com a tabela de abreviações",
            "player": "casa com o pool de nomes de jogador",
            "namelike": "**tem forma de nome e não está em nenhuma das listas**",
            "path": "caminho ou nome de arquivo do disco",
            "interface": "texto de interface — tem espaço ou minúscula",
            "unknown": "**o que a Fase 2 ainda não explicou**",
        }
        print("| Balde | Trechos | O que é |")
        print("|---|---:|---|")
        for b in BUCKETS:
            print(f"| `{b}` | {total[b]} | {labels[b]} |")
        print("\n## Os maiores blocos\n")
        print("Um bloco é uma sequência de trechos separados por no máximo "
              "24 bytes. Os que interessam à Fase 2 são os de balde "
              "`unknown`.\n")
        print("| Arquivo | Offset | Trechos | Bytes | Balde | Primeiro … último |")
        print("|---|---:|---:|---:|---|---|")
        for r in rows[:args.top]:
            print(f"| `{r['path']}` | {r['start']} | {r['n']} | {r['span']} "
                  f"| `{r['kind']}` | `{r['first'][:22]}` … "
                  f"`{r['last'][:22]}` |")
        unknown_rows = [r for r in rows if r["kind"] == "unknown"]
        print(f"\n## Blocos que a Fase 2 ainda não explicou\n")
        print(f"{len(unknown_rows)} de {len(rows)}.\n")
        print("| Arquivo | Offset | Trechos | Primeiro … último |")
        print("|---|---:|---:|---|")
        for r in unknown_rows[:args.top]:
            print(f"| `{r['path']}` | {r['start']} | {r['n']} | "
                  f"`{r['first'][:26]}` … `{r['last'][:26]}` |")
    else:
        print(f"{len(per_file)} files with text, {sum(total.values())} runs, "
              f"{len(rows)} dense blocks")
        for b in BUCKETS:
            print(f"  {b:10s} {total[b]:7d}")
        print()
        for r in rows[:args.top]:
            print(f"  {r['path']:24s} @{r['start']:7d} n={r['n']:5d} "
                  f"span={r['span']:7d} {r['kind']:10s} "
                  f"{r['first'][:20]!r} … {r['last'][:20]!r}")
            if args.show:
                for off, text, kind in r["items"][:args.show] \
                        if "items" in r else []:
                    print(f"        @{off} {text!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

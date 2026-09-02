#!/usr/bin/env python3
"""Dump every text the disc holds, with where each one came from.

This exists for a question tooling cannot answer: **where on screen does
each of these lists appear?** Eight lists hold team names and they are not
the same list -- section 6.1 -- and after walking a whole match on
2026-09-02 only one of them was placed: `SELECT.BIN` @3128, on the team
selection grid. The in-play scoreboard, the replay and the RESULTADO screen
all identify teams by *flag*, so `RESULT.BIN` @524, `REPLAYS.BIN` @11380 and
`ENDING.BIN` @1256 surface somewhere that has not been found by driving the
emulator. Someone who knows the game can read a list and say where it shows.

So the output is aimed at a person, not at a checker. Three files:

  entradas.csv    every entry of every table, with file, offsets and index
  listas.csv      one row per list, with what makes it *recognisable* --
                  its size, and the entries no other list has. That is the
                  fingerprint to match against a screen
  interface.csv   the printable runs that belong to no table, grouped into
                  blocks. Menu labels live here, and a label is the easiest
                  thing of all to place

Usage:

    python3 tools/pes2/text_dump.py <track1.bin> --out-dir <dir>

The CSVs are game text and stay out of the repository, like roms/ and the
captured frames do. What is versioned is this script.
"""

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                          # noqa: E402
import tables as T                                             # noqa: E402


RAW_SECTOR, FORM1_DATA, HEADER = 2352, 2048, 24


def absolute(entry, offset):
    """Where a byte of file data really sits in the track.

    Not `start + offset`: a sector is 2352 bytes of which 2048 are data, so
    the arithmetic has to step over each header. Getting this wrong gives a
    number that looks plausible and points at nothing.
    """
    sector, within = divmod(offset, FORM1_DATA)
    return (entry.lba + sector) * RAW_SECTOR + HEADER + within


def table_rows(img):
    """Every entry of every table, with both offsets and its index."""
    rows = []
    for t in T.TABLES:
        try:
            path, base, entries = T.resolve(img, t)
        except Exception as why:                              # noqa: BLE001
            print(f"  {t.key}: {why}", file=sys.stderr)
            continue
        # O offset absoluto de um byte de dados nao e "inicio + n": o setor
        # tem 2352 B com 2048 de dados, entao a conta pula os cabecalhos.
        entry = img.files.get(path)
        for i, (off, raw) in enumerate(entries):
            text = raw.decode("latin-1")
            rows.append({
                "lista": t.key,
                "arquivo": path,
                "o_que_e": t.label,
                "indice": i,
                "offset_no_arquivo": off,
                "offset_absoluto": absolute(entry, off) if entry else "",
                "texto": text,
            })
    return rows


def list_rows(rows):
    """One row per list, carrying what makes it recognisable on screen."""
    by_list = {}
    for r in rows:
        by_list.setdefault(r["lista"], []).append(r)

    # A team name is the same team wherever it is, so compare case-folded.
    sets = {k: {r["texto"].upper() for r in v} for k, v in by_list.items()}

    out = []
    for key, entries in by_list.items():
        mine = sets[key]
        others = set()
        for other, s in sets.items():
            if other != key:
                others |= s
        only = sorted(x for x in mine if x not in others)
        # O que a lista **nao** tem e tao identificador quanto o que ela
        # tem: "a tela que traz tudo menos as all-stars" e uma descricao
        # que quem conhece o jogo reconhece na hora.
        canon = sets.get("team-names", set())
        missing = sorted(canon - mine) if mine & canon else []
        first = [r["texto"] for r in entries[:6]]
        last = [r["texto"] for r in entries[-3:]]
        out.append({
            "lista": key,
            "arquivo": entries[0]["arquivo"],
            "o_que_e": entries[0]["o_que_e"],
            "entradas": len(entries),
            "offset_no_arquivo": entries[0]["offset_no_arquivo"],
            "primeiras": " | ".join(first),
            "ultimas": " | ".join(last),
            "so_nesta_lista": " | ".join(only),
            "quantas_so_nesta": len(only),
            "falta_da_canonica": " | ".join(missing),
            "quantas_faltam": len(missing),
            "onde_aparece_na_tela": "",     # para o usuario preencher
        })
    return sorted(out, key=lambda r: (r["arquivo"], r["offset_no_arquivo"]))


PRINTABLE = bytes(range(0x20, 0x7F))

# **Um filtro frouxo aqui devolve lixo, nao planilha.** A primeira versao
# aceitava qualquer sequencia imprimivel e saiu com 1.177.288 linhas: os
# `BIN/*.BIN` sao LZSS e dados comprimidos tem bytes imprimiveis aos
# montes. Rotulo de menu tem forma -- comeca com letra, e quase todo letra
# e espaco -- e mora em bloco denso.
import re                                                      # noqa: E402

LABEL = re.compile(r"^[A-Za-z][A-Za-z0-9 .,'&()/:!?-]{2,}$")


def looks_like_label(text):
    text = text.strip()
    if not LABEL.match(text):
        return False
    letters = sum(c.isalpha() or c.isspace() for c in text)
    return letters / len(text) >= 0.8


def runs_of(data, minimum=3):
    run, start = bytearray(), 0
    for i, b in enumerate(data):
        if b in PRINTABLE:
            if not run:
                start = i
            run.append(b)
        else:
            if len(run) >= minimum:
                yield start, run.decode("latin-1")
            run = bytearray()
    if len(run) >= minimum:
        yield start, run.decode("latin-1")


def interface_rows(img, known, gap=48, least=6):
    """Printable runs no table claims, grouped into blocks.

    Grouped because a menu is a block: a dozen labels packed together with
    almost nothing between them. A run on its own is usually a fragment of
    code or a file name.
    """
    out = []
    for path in sorted(img.files):
        if img.status(path) != "form1":
            continue
        try:
            data = img.read_file(path)
        except Exception:                                     # noqa: BLE001
            continue
        found = [(o, s) for o, s in runs_of(data, minimum=4)
                 if looks_like_label(s) and s.strip().upper() not in known]
        block, previous = [], None
        blocks = []
        for o, s in found:
            if previous is not None and o - previous > gap:
                if len(block) >= least:
                    blocks.append(block)
                block = []
            block.append((o, s))
            previous = o + len(s)
        if len(block) >= least:
            blocks.append(block)
        for n, b in enumerate(blocks):
            for o, s in b:
                out.append({
                    "arquivo": path,
                    "bloco": n,
                    "offset_no_arquivo": o,
                    "texto": s,
                    "onde_aparece_na_tela": "",
                })
    return out


def write(path, rows, fields):
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print(f"  {path}  {len(rows)} linhas")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--min-run", type=int, default=3)
    args = ap.parse_args(argv)

    os.makedirs(args.out_dir, exist_ok=True)
    with Image(args.image) as img:
        rows = table_rows(img)
        known = {r["texto"].upper() for r in rows}

        write(os.path.join(args.out_dir, "entradas.csv"), rows,
              ["lista", "arquivo", "o_que_e", "indice",
               "offset_no_arquivo", "offset_absoluto", "texto"])

        write(os.path.join(args.out_dir, "listas.csv"), list_rows(rows),
              ["lista", "arquivo", "o_que_e", "entradas",
               "offset_no_arquivo", "primeiras", "ultimas",
               "so_nesta_lista", "quantas_so_nesta",
               "falta_da_canonica", "quantas_faltam",
               "onde_aparece_na_tela"])

        write(os.path.join(args.out_dir, "interface.csv"),
              interface_rows(img, known),
              ["arquivo", "bloco", "offset_no_arquivo", "texto",
               "onde_aparece_na_tela"])
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""es -> en, and the sweep that refuses what did not get translated.

Provenance (section 3.4 of the plan): none of the four columns. This module
knows about words.

Same mechanics as `tools/glossary.py`, which carries the Italian of
`legacy/mfc/` for the C++ port. The source here is Spanish -- Zetaprog's
VB.NET -- and section 3.5 of the plan settles the rule: **all of the port's
code is en-US** (identifiers, docstrings, comments, error messages, `--help`
and CLI output), and `docs/**` stays Portuguese. The boundary is the FILE, not
the sentence.

THE SWEEP READS COMMENTS AND STRINGS ON PURPOSE, which is the exact opposite
of `layout.address_monopoly()`. That one tokenises so a module can name in its
own documentation the address it operates on; this one is looking for PROSE,
and prose lives in comments and docstrings. Two sweeps over the same tree with
opposite rules about the same tokens -- worth saying out loud, because
"unify them" is a natural-looking idea that would break both.

Three rules, and the third is the one that needs no word list:

  the Spanish of the upstream, word by word (SPANISH below);
  a short list of Portuguese words that only ever appear in prose (PORTUGUESE);
  any Latin accented letter at all.

The third is the net. Portuguese and Spanish prose cannot go three lines
without one; `text.py`'s Japanese literals and its `EUR` sign are far outside
that block, so the net does not touch legitimate test data. It is checked, not
assumed: `text.py` holds five non-ASCII lines today and the sweep is silent.

Usage:

    python3 tools/mcr/glossary.py            # sweep tools/mcr/*.py
    python3 tools/mcr/glossary.py --self-check
"""

import argparse
import os
import re
import sys

MCR_DIR = os.path.dirname(os.path.abspath(__file__))

# The upstream's vocabulary. Left is what Zetaprog wrote, right is what this
# port calls it. Anything ported literally has to arrive translated.
SPANISH = {
    "jugador": "player",
    "jugadores": "players",
    "cancha": "pitch",
    "formacion": "formation",
    "grabar": "write",
    "guardar": "save",
    "leer": "read",
    "bufersizenum": "group_size",
    "equipo": "team",
    "nombre": "name",
    "dorsal": "shirt_number",
    "portero": "goalkeeper",
    "cabello": "hair",
    "barba": "beard",
    "altura": "height",
    "edad": "age",
    "pie": "foot",
    "botas": "boots",
    "tarjeta": "card",
    "archivo": "file",
    "tactica": "tactics",
}

# Portuguese that only shows up in prose. Short on purpose: a long list buys
# false positives, and the accent rule below already catches most of it.
PORTUGUESE = (
    "quadro", "cartao", "escrita", "recusa", "falha", "endereco", "jogador",
    "arquivo", "medido", "gravar", "tabela", "verdade", "campo", "bloco",
)

# Latin-1 Supplement plus Latin Extended-A/B: the accented letters of
# Portuguese and Spanish. Japanese (U+3000..U+FFxx) and the euro sign
# (U+20AC) are outside it, which is what lets `text.py` keep its fixtures.
ACCENTED = re.compile(r"[À-ɏ]")

SELF = os.path.basename(__file__)


def sweep(directory: str = MCR_DIR) -> list[str]:
    """Complaints, one per line. Empty is correct.

    This file is skipped: it CARRIES the words, and a sweep that flags its own
    dictionary is a sweep somebody switches off within a week -- the same
    reason `layout.address_monopoly()` skips `layout.py`.
    """
    complaints = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".py") or name == SELF:
            continue
        with open(os.path.join(directory, name), encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, 1):
                low = line.lower()
                for word, english in SPANISH.items():
                    if re.search(rf"\b{word}\b", low):
                        complaints.append(
                            f"{name}:{lineno}: Spanish {word!r} -- the port "
                            f"calls it {english!r}")
                for word in PORTUGUESE:
                    if re.search(rf"\b{word}\b", low):
                        complaints.append(
                            f"{name}:{lineno}: Portuguese {word!r} -- the "
                            f"code of this port is en-US (section 3.5)")
                m = ACCENTED.search(line)
                if m:
                    complaints.append(
                        f"{name}:{lineno}: {m.group()!r} is a Latin accented "
                        f"letter; the code of this port is en-US (section 3.5)")
    return complaints


# --- self-check ------------------------------------------------------------

def _checks(c) -> None:
    import shutil
    import tempfile
    ok, attempt = c.ok, c.attempt

    ok("the map has both directions written out",
       all(k and v for k, v in SPANISH.items()))
    ok("no word maps to itself",
       all(k != v for k, v in SPANISH.items()))

    found = attempt("sweep the real tree", lambda: sweep(), default=None)
    ok("the tree is clean today", found == [], f"{found}")

    # The Japanese fixtures of text.py must NOT be flagged: the accent rule is
    # about Latin accents, not about non-ASCII.
    ok("the accent rule leaves Japanese alone",
       not ACCENTED.search("P/ZIYO-RUZU") and not ACCENTED.search("ジ"))
    ok("and leaves the euro sign alone", not ACCENTED.search("€"))
    ok("but catches a Portuguese accent", bool(ACCENTED.search("endereço")))

    # The red cases: one per rule, planted in a copy.
    with tempfile.TemporaryDirectory() as tmp:
        shutil.copy(os.path.join(MCR_DIR, "harness.py"),
                    os.path.join(tmp, "victim.py"))
        base = attempt("sweep the copy", lambda: sweep(tmp), default=None)
        ok("an untouched copy is clean", base == [], f"{base}")

        def plant(text):
            with open(os.path.join(tmp, "victim.py"), "a") as fh:
                fh.write(text)
            return sweep(tmp)

        got = attempt("plant Spanish", lambda: plant("# el jugador\n"), [])
        ok("Spanish is caught, and named",
           any("jugador" in x and "player" in x for x in got), f"{got}")
        got = attempt("plant Portuguese",
                      lambda: plant("# o quadro de diretorio\n"), [])
        ok("Portuguese is caught",
           any("quadro" in x for x in got), f"{got}")
        got = attempt("plant an accent", lambda: plant("# endereço\n"), [])
        ok("an accented letter is caught",
           any("accented" in x for x in got), f"{got}")


def self_check(verbose: bool = True) -> int:
    import harness
    return harness.run("glossary.py", _checks, verbose)


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("directory", nargs="?", default=MCR_DIR)
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0

    found = sweep(a.directory)
    for line in found:
        print(line)
    print(f"glossary.py: {len(found)} complaint(s) in {a.directory}")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())

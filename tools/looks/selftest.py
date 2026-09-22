#!/usr/bin/env python3
"""The mandatory gate: every module's self-check, the design rules, the controls.

This is `looks_selftest`.  It runs with **no image, no venv and no display**,
and it must never skip its way to green -- a target that passes while printing
a note about what it did not measure is the trap `mcr_ui` paid for, and this
cycle's contract is: measured and passed, or skipped with 77.

Three things happen here, in this order:

1. every module's own `self_check()` runs, each under the harness so an
   exception becomes one named failure instead of killing the run;
2. the three design rules of plan section 3.3 are swept MECHANICALLY -- rule 1
   through `layout.sweep_addresses()`, which already exists, because two
   sweepers of one rule drift apart in silence and the unused one rots;
3. every negative control is planted and must go red.

Usage:
    python tools/looks/selftest.py
    python tools/looks/selftest.py --no-plant     # skip step 3 (it is slow)
"""

from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
import tokenize

LOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, LOOKS_DIR)

import harness  # noqa: E402

UI_DIR = os.path.join(LOOKS_DIR, "ui")

MODULES = (
    "harness",
    "layout",
    "section",
    "modelfile",
    "texture",
    "sprites",
    "glyphs",
    "atlas",
    "skin",
    "looks",
    "screen",
    "assembly",
    "scene",
    "confront",
    "corpus",
    "ui_check",
    "pieces",
    "anime",
    "stature",
    "iso_source",
    "oracle",
    "controls",
    "superpack_count",
    "cli",
)
"""Every module with a self_check, in dependency order.

Listed rather than discovered, and the list is itself checked below: a module
that appears in the directory and not here would never run, and nothing would
say so.
"""

FORBIDDEN_IN_UI = ("layout", "iso_source", "section", "modelfile")
"""Rule 3, first half: the UI knows no address and reads no disc."""

# Rule on language (plan section 3.5): documents in pt-BR, code in en-US.  The
# sweep reads comments and strings, which is the OPPOSITE of the rule-1 sweep
# -- there a digit inside a string is not an address; here a word inside a
# comment is exactly what is being looked for.
FOREIGN_WORDS = (
    "arquivo", "secao", "seção", "vertice", "vértice", "primitiva", "cabecalho",
    "cabeçalho", "ponteiro", "endereco", "endereço", "tamanho", "leitura",
    "gravacao", "gravação", "jogador", "imagem", "varredura", "guarda",
)


def _word_patterns() -> dict:
    """One anchored pattern per foreign word.

    ANCHORED, and built here rather than inline, because the inline version
    was written through a shell heredoc and its `\\b` arrived as a literal
    backspace: the compiled pattern was <BS>vertice<BS>, it matched nothing,
    and the sweep reported a clean tree.  A guard that passes by matching
    nothing is the failure this whole module exists to catch, and it happened
    to this module first.

    The anchors are not cosmetic either.  Unanchored, `vertice` matches inside
    the English "vertices" -- fifteen false positives on the first honest run,
    and a sweep that cries wolf gets its word list trimmed until it catches
    nothing.
    """
    return {word: re.compile(r"\b" + re.escape(word) + r"\b")
            for word in FOREIGN_WORDS}


_WORD = _word_patterns()


def _modules_on_disc() -> list:
    names = []
    for name in sorted(os.listdir(LOOKS_DIR)):
        if not name.endswith(".py") or name == "selftest.py":
            continue
        with open(os.path.join(LOOKS_DIR, name), encoding="utf-8") as handle:
            if "def self_check(" in handle.read():
                names.append(name[:-3])
    return names


def _foreign_words(directory: str) -> list:
    """Words from the other language in comments and strings, as `path:line`.

    Tokenised, not grepped: `FOREIGN_WORDS` above is a tuple of literals in
    this very file, and a textual sweep would report itself.  Reading only
    COMMENT and STRING tokens means the list is data, and the prose is what
    gets read.
    """
    found = []
    for root, dirs, names in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(names):
            if not name.endswith(".py") or name == os.path.basename(__file__):
                continue
            path = os.path.join(root, name)
            rel = os.path.relpath(path, directory)
            with open(path, encoding="utf-8") as handle:
                try:
                    tokens = list(tokenize.generate_tokens(handle.readline))
                except (tokenize.TokenError, IndentationError, SyntaxError):
                    found.append("%s:1: did not tokenise" % rel)
                    continue
            for kind, text, (row, _col), _end, _line in tokens:
                if kind not in (tokenize.COMMENT, tokenize.STRING):
                    continue
                lowered = text.lower()
                for word in FOREIGN_WORDS:
                    # WHOLE WORDS.  Plain substring matching reported fifteen
                    # false positives on the first run, every one of them the
                    # English "vertices" containing "vertice" -- and a sweep
                    # that cries wolf gets its word list trimmed until it
                    # catches nothing.
                    if _WORD[word].search(lowered):
                        found.append("%s:%d: %s" % (rel, row, word))
    return found


def _call_self_check(module):
    """Call a module's self_check, whichever of the two shapes it has.

    The harness-reporting ones take `verbose` and return a failure count; the
    ones written before the harness existed take nothing and assert.  Probing
    the signature beats a try/except around the call: a TypeError raised
    INSIDE a self_check would otherwise be read as "this one takes no verbose"
    and the real failure would be swallowed.
    """
    import inspect

    if "verbose" in inspect.signature(module.self_check).parameters:
        return module.self_check(verbose=False)
    return module.self_check()


def _module_checks(c) -> None:
    """Each module's own self_check, run in this process under the guard."""
    ok, attempt = c.ok, c.attempt

    on_disc = attempt("list the modules on disc", _modules_on_disc, default=[])
    missing = [n for n in on_disc if n not in MODULES]
    ok("every module with a self_check is in MODULES", missing == [],
       "not listed: %s" % missing)
    gone = [n for n in MODULES if n not in on_disc]
    ok("every module in MODULES still exists and still has a self_check",
       gone == [], "listed but absent: %s" % gone)

    for name in MODULES:
        module = attempt("import %s" % name,
                         lambda n=name: importlib.import_module(n))
        if module is None:
            c.fail("%s: did not import, so its self_check did not run" % name)
            continue

        # Two shapes coexist on purpose.  The harness-reporting modules return
        # a failure COUNT; the older ones assert and return None.  Neither is
        # wrong, and flattening them would be a refactor this task did not ask
        # for -- but a module that raises must not take the run with it, which
        # is what attempt() is for.
        outcome = attempt("%s.self_check()" % name,
                          lambda m=module: _call_self_check(m),
                          default="raised")
        if outcome == "raised":
            continue
        ok("%s reports no failure" % name, not outcome, "failures=%s" % outcome)


def _rules(c) -> None:
    """The three design rules of section 3.3, swept rather than asserted."""
    ok, attempt = c.ok, c.attempt

    layout = attempt("import layout", lambda: importlib.import_module("layout"))
    if layout is None:
        c.fail("Rule 1: layout did not import, so the sweep did not run")
    else:
        stats: dict = {}
        stray = attempt("sweep for stray addresses",
                        lambda: layout.sweep_addresses(LOOKS_DIR, stats),
                        default=None)
        ok("Rule 1: no address outside %s" % layout.ADDRESS_OWNER,
           stray == [], "%s" % (stray,))
        # Printed, not deduced.  A sweep that opened nothing prints the same
        # verdict as one that read everything, and that sentence is what a
        # reader takes for "rule 1 holds".
        print("  ..... rule 1 swept %d file(s), %d line(s)"
              % (stats.get("files", 0), stats.get("lines", 0)))
        ok("Rule 1: the sweep actually opened files", stats.get("files", 0) > 0)

    # Rule 2 -- raw bytes are normative -- is not a sweep.  It is the scan
    # closing on an exact EOF against the real file, and that lives in
    # modelfile.verify(), which the image gate runs.  Said here rather than
    # quietly omitted, so the count of rules checked is honest.
    c.skip("Rule 2: measured by modelfile --check-image, not by a sweep")

    # Rule 3, first half -- the UI knows no address.
    if not os.path.isdir(UI_DIR):
        c.skip("Rule 3 (UI imports): ui/ does not exist yet (LOOKS-TASK-15)")
    else:
        offenders = []
        # os.walk and not os.listdir: a ui/widgets/ would be invisible to the
        # latter, and the .mcr cycle lost a whole package that way.
        for root, dirs, names in os.walk(UI_DIR):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for name in sorted(names):
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                rel = os.path.relpath(path, UI_DIR)
                with open(path, encoding="utf-8") as handle:
                    for number, line in enumerate(handle, 1):
                        text = line.split("#")[0]
                        for banned in FORBIDDEN_IN_UI:
                            if ("import %s" % banned in text
                                    or "from %s import" % banned in text):
                                offenders.append("ui/%s:%d: %s"
                                                 % (rel, number, banned))
        ok("Rule 3: the UI imports no module that knows an address",
           offenders == [], "%s" % (offenders,))

    # Rule 3, second half -- the core knows no Qt.  Without this the mandatory
    # gate starts requiring PySide6 the day somebody imports it upstream of
    # the core, and a gate that needs a venv is not a gate that never skips.
    ok("Rule 3: PySide6 is not loaded by the core",
       "PySide6" not in sys.modules)

    # Language (section 3.5).
    foreign = attempt("sweep the language",
                      lambda: _foreign_words(LOOKS_DIR), default=None)
    ok("no Portuguese in tools/looks/*.py", foreign == [], "%s" % (foreign,))

    # And the sweep is watched FINDING something, on a tree built to be found
    # in.  Without this it was green for a week by matching nothing at all --
    # see _word_patterns().  Same argument as the rule-1 sweep's planted tree:
    # against a clean tree, a broken sweep and a working one print the same
    # sentence.
    def _planted():
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            with open(os.path.join(tmp, "plantado.py"), "w",
                      encoding="utf-8") as handle:
                handle.write("# o ponteiro para o arquivo\n")
                handle.write('X = \'leitura\'\n')
            # And one that must NOT be found: the English word that contains a
            # Portuguese one.
            with open(os.path.join(tmp, "clean.py"), "w",
                      encoding="utf-8") as handle:
                handle.write("# 2,461 vertices, all of them fine\n")
            return _foreign_words(tmp)

    caught = attempt("plant a foreign word and sweep for it", _planted,
                     default=None)
    hits = {entry.split(": ")[-1] for entry in (caught or [])}
    ok("the language sweep finds a planted word",
       {"ponteiro", "arquivo", "leitura"} <= hits, "%s" % (caught,))
    ok("and does not fire on the English word that contains one",
       not any(entry.startswith("clean.py") for entry in (caught or [])),
       "%s" % (caught,))


def _negative(c) -> None:
    """Every planted control has to be able to go red."""
    ok, attempt = c.ok, c.attempt
    controls = attempt("import controls",
                       lambda: importlib.import_module("controls"))
    if controls is None:
        c.fail("the negative controls did not run")
        return

    results = attempt("plant every control",
                      lambda: controls.run_all(verbose=False), default=[])
    ok("there is at least one control", bool(results))
    ok("every control is a single, matching substitution",
       all(r.matched == 1 for r in results),
       "%s" % [r.control.id for r in results if r.matched != 1])
    ok("every planted control goes red",
       bool(results) and all(r.good for r in results),
       "green=%s" % [r.control.id for r in results if not r.good])
    # The count comes from the tool.  Written in prose it disagrees with the
    # catalogue the first time somebody adds one.
    print("  ..... %d of %d controls red"
          % (sum(1 for r in results if r.good), len(results)))


def run(verbose: bool = True, plant: bool = True) -> int:
    """Everything.  Returns the failure count, which is the exit code."""
    # The gate must not depend on the fixture: with the variable set, a module
    # could take a path that is unavailable on a clean machine, and the gate
    # would pass here and fail there.
    image = os.environ.pop("WE2002_LOOKS_IMAGE", None)
    try:
        total = harness.run("modules", _module_checks, verbose)
        total += harness.run("rules", _rules, verbose)
        if plant:
            total += harness.run("controls", _negative, verbose)
        else:
            print("controls: not planted (--no-plant)")
    finally:
        if image is not None:
            os.environ["WE2002_LOOKS_IMAGE"] = image

    print("looks_selftest: %d failure(s)" % total)
    return total


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-plant", action="store_true",
                        help="skip the negative controls (they are slow)")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    return 1 if run(verbose=not args.quiet, plant=not args.no_plant) else 0


if __name__ == "__main__":
    raise SystemExit(main())

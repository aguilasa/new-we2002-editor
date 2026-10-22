#!/usr/bin/env python3
"""The kit2d gate `kit2d_selftest`: needs nothing, never skips.

In this order:

1. the self-checks of what the project imports (PLAN-KIT2D-PY.md section 2:
   the price of importing is that a break there must show up here) --
   `tools/pes2/iso.py` through `tools/pes2/selftest.py` (a synthetic disc),
   `tools/pes2/lzss.py` (`check_block_literal` and a round trip), and
   `tools/kits/core/teams.py` (its generated tables, `gen_tables.py --check`);
2. `core/layout.py`'s own `self_check()`;
3. the design rules of section 3.1 on `tools/kit2d/core/`: no print, no exit,
   no input, no Qt;
4. the one-module rule of `layout.py`: no address of section 1.1 spelled in
   any other `.py` of `tools/kit2d/`;
5. each rule of 3 and 4 planted in a scratch folder, which must turn it red.

The last line says how many checks ran and how many failed.

Usage:
    python3 tools/kit2d/selftest.py [--quiet]
"""

from __future__ import annotations

import argparse
import ast
import importlib
import importlib.util
import os
import subprocess
import sys
import tempfile
import tokenize

KIT2D_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(KIT2D_DIR)
CORE_DIR = os.path.join(KIT2D_DIR, "core")
sys.path.insert(0, KIT2D_DIR)
sys.path.insert(0, os.path.join(TOOLS_DIR, "pes2"))

from core import layout  # noqa: E402

# The two files allowed to spell the addresses, by path: a layout.py elsewhere
# in kit2d/ is not exempt.
EXEMPT_FILES = (os.path.abspath(layout.__file__), os.path.abspath(__file__))


class Checker:
    """Counts the checks that ran and the ones that failed."""

    def __init__(self, verbose: bool):
        self.verbose = verbose
        self.ran = 0
        self.failed = 0

    def ok(self, name: str, cond, detail: str = "") -> None:
        self.ran += 1
        if cond:
            if self.verbose:
                print("  ok    %s" % name)
        else:
            self.failed += 1
            print("  FAIL  %s%s" % (name, "  " + str(detail) if detail else ""))

    def attempt(self, name: str, fn, default=None):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            self.ok("%s: raised %s: %s" % (name, type(exc).__name__, exc), False)
            return default


def _run(args: list) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, *args], capture_output=True, text=True,
                          timeout=300)


# -- 1. what the project imports --------------------------------------------

KITS_CORE = "kits_core"
"""The name tools/kits/core is imported under: both projects call their
package `core`, and the first one on the path would win for both."""


def _kits_teams():
    if KITS_CORE not in sys.modules:
        folder = os.path.join(TOOLS_DIR, "kits", "core")
        spec = importlib.util.spec_from_file_location(
            KITS_CORE, os.path.join(folder, "__init__.py"),
            submodule_search_locations=[folder])
        module = importlib.util.module_from_spec(spec)
        sys.modules[KITS_CORE] = module
        spec.loader.exec_module(module)
    return importlib.import_module(KITS_CORE + ".teams")


def _imported_checks(c: Checker) -> None:
    proc = c.attempt("run tools/pes2/selftest.py",
                     lambda: _run([os.path.join(TOOLS_DIR, "pes2", "selftest.py")]))
    if proc is not None:
        c.ok("pes2 iso.py: tools/pes2/selftest.py exits 0", proc.returncode == 0,
             (proc.stdout + proc.stderr).strip().splitlines()[-1:])

    import lzss  # tools/pes2
    bad = lzss.check_block_literal()
    c.ok("pes2 lzss.py: check_block_literal() reports no failure", not bad, "; ".join(bad))
    plain = bytes(range(256)) * 3 + b"kit2d" * 40
    back = c.attempt("lzss round trip", lambda: lzss.decompress(lzss.compress(plain), 0)[0])
    c.ok("pes2 lzss.py: decompress(compress(x)) == x", back == plain)

    proc = c.attempt("run tools/kits/gen_tables.py --check",
                     lambda: _run([os.path.join(TOOLS_DIR, "kits", "gen_tables.py"), "--check"]))
    if proc is not None:
        c.ok("kits teams.py: gen_tables.py --check exits 0", proc.returncode == 0,
             (proc.stdout + proc.stderr).strip().splitlines()[-1:])
    kits_teams = c.attempt("import tools/kits/core/teams.py", _kits_teams)
    c.ok("kits teams.py: TEAM_COUNT is layout.TEAMS (%d)" % layout.TEAMS,
         kits_teams is not None and kits_teams.TEAM_COUNT == layout.TEAMS,
         getattr(kits_teams, "TEAM_COUNT", None))


# -- 2. layout --------------------------------------------------------------

def _layout_checks(c: Checker) -> None:
    bad = layout.self_check()
    c.ok("layout.self_check() reports no failure", not bad, "; ".join(bad))
    c.ok("the load base is marked inferred until section 4.1 measures it",
         layout.LOAD_BASE_STATUS == "inferred", layout.LOAD_BASE_STATUS)


# -- 3 and 4. the rules -----------------------------------------------------

FORBIDDEN_CALLS = ("print", "exit", "input")
FORBIDDEN_IMPORTS = ("PySide6", "PySide2", "PyQt5", "PyQt6")


def _tokens(path: str) -> list:
    with open(path, "rb") as fh:
        return list(tokenize.tokenize(fh.readline))


def _py_files(folder: str) -> list:
    out = []
    for root, dirs, files in os.walk(folder):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        out += [os.path.join(root, f) for f in files if f.endswith(".py")]
    return sorted(out)


def core_rule_breaks(core: str = CORE_DIR) -> list:
    """(file, line, what) for every print/exit/input call and Qt import in core/."""
    out = []
    for path in _py_files(core):
        tokens = _tokens(path)
        for a, b in zip(tokens, tokens[1:]):
            if a.type == tokenize.NAME and a.string in FORBIDDEN_CALLS and b.string == "(":
                out.append((os.path.relpath(path, core), a.start[0], a.string + "()"))
            if a.type == tokenize.NAME and a.string in FORBIDDEN_IMPORTS:
                out.append((os.path.relpath(path, core), a.start[0], a.string))
    return out


def _literal_int(tok):
    """The integer a NUMBER token spells, or a STRING token holding only an integer."""
    text = tok.string
    if tok.type == tokenize.STRING:
        try:
            text = ast.literal_eval(text)
        except (ValueError, SyntaxError):
            return None
        if not isinstance(text, str):
            return None
        text = text.strip()
    elif tok.type != tokenize.NUMBER:
        return None
    try:
        return int(text.replace("_", ""), 0)
    except ValueError:
        return None


def address_breaks(folder: str = KIT2D_DIR) -> list:
    """(file, line, literal) for every section 1.1 address spelled outside layout.py."""
    wanted = set(layout.ADDRESSES)
    out = []
    for path in _py_files(folder):
        if os.path.abspath(path) in EXEMPT_FILES:
            continue
        for tok in _tokens(path):
            value = _literal_int(tok)
            if value is None:
                continue
            if value in wanted:
                out.append((os.path.relpath(path, folder), tok.start[0], tok.string))
    return out


def _rule_checks(c: Checker) -> None:
    breaks = core_rule_breaks()
    c.ok("core/ has no print/exit/input and imports no Qt", not breaks, breaks)
    breaks = address_breaks()
    c.ok("no address of section 1.1 is spelled outside layout.py", not breaks, breaks)


# -- 5. the rules planted ---------------------------------------------------

PLANTS = (
    ("a Qt import in core/", os.path.join("core", "planted.py"),
     "import PySide6\n", core_rule_breaks, "core"),
    ("a print() in core/", os.path.join("core", "planted.py"),
     "print('x')\n", core_rule_breaks, "core"),
    ("an address literal outside layout.py", "planted.py",
     "OFFSET = 0x3F534\n", address_breaks, ""),
    ("an address literal in a file merely named layout.py",
     os.path.join("ui", "layout.py"), "OFFSET = 172096\n", address_breaks, ""),
    ("an address spelled as a string", "planted.py",
     'OFFSET = int("0x3F534", 16)\n', address_breaks, ""),
)


def _plant_checks(c: Checker) -> None:
    for name, rel, text, rule, scope in PLANTS:
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "core"))
            clean = rule(os.path.join(tmp, scope))
            os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
            with open(os.path.join(tmp, rel), "w", encoding="utf-8") as fh:
                fh.write(text)
            red = rule(os.path.join(tmp, scope))
        c.ok("planted %s turns its rule red" % name, not clean and bool(red), red)


def run(verbose: bool = True) -> int:
    c = Checker(verbose)
    for label, body in (("imported modules", _imported_checks), ("layout", _layout_checks),
                        ("rules", _rule_checks), ("planted rules", _plant_checks)):
        if verbose:
            print("%s self-check" % label)
        c.attempt(label, lambda body=body: body(c))
    print("kit2d_selftest: %d check(s) ran, %d failure(s)" % (c.ran, c.failed))
    return c.failed


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    return 1 if run(verbose=not args.quiet) else 0


if __name__ == "__main__":
    raise SystemExit(main())

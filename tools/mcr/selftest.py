#!/usr/bin/env python3
"""The mandatory gate: every module's self-check, plus the three design rules.

Provenance (section 3.4 of the plan): none of the four columns.

WHAT MAKES THIS THE MANDATORY ONE. It needs nothing -- no fixture, no venv, no
Qt, no display. Every module builds the card it needs in memory, and this file
UNSETS `WE2002_MCR_CARD` before calling any of them, on purpose: the mandatory
gate has to run identically on a machine that has never seen a memory card. The
fixture-dependent half is `cli.py check`, registered as `mcr_card`, which skips
itself with 77 when the variable is not set.

Section 4.4 of the plan:

  mcr_selftest  needs nothing                  never skips -- this file
  mcr_card      WE2002_MCR_CARD                SKIP_RETURN_CODE 77
  mcr_ui        the venv with PySide6 and :98  SKIP_RETURN_CODE 77

`layout` IS IMPORTED INSIDE `attempt`, not at module scope. Its named views
(`SHIRT_NUMBERS`, `PLAYER_ATTRIBUTES`, ...) raise `LayoutError` at import time
when a destination is missing, and CORR-MCR-008 measured what that does to a
gate: in the two controls that remove a destination, `layout.py --self-check`
left by traceback with 0 of its 29 assertions run. A broken table has to become
ONE NAMED FAILURE among the others, not a stack trace that takes the run with
it.

Usage:

    python3 tools/mcr/selftest.py
    python3 tools/mcr/selftest.py --quiet
    ctest -R mcr_selftest
"""

import argparse
import importlib
import inspect
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import harness                                           # noqa: E402

MCR_DIR = os.path.dirname(os.path.abspath(__file__))
UI_DIR = os.path.join(MCR_DIR, "ui")

# The order is the dependency order, so the first failure is the deepest one.
MODULES = ("harness", "glossary", "controls", "card", "layout", "attributes",
           "numbers", "text", "domains", "formation", "model", "mcrio")

# What the UI is forbidden to import (Rule 3, section 3.3 of the plan).
FORBIDDEN_IN_UI = ("layout", "card", "mcrio")


def _rules(c) -> None:
    """The three design rules, checked mechanically rather than asserted."""
    ok, attempt = c.ok, c.attempt

    # Rule 1 -- only layout.py carries an address. Imported HERE, not above.
    layout = attempt("import layout", lambda: importlib.import_module("layout"))
    if layout is None:
        c.fail("Rule 1: layout could not be imported, so the sweep did not run")
    else:
        stray = attempt("sweep for stray addresses",
                        lambda: layout.address_monopoly(MCR_DIR), default=None)
        ok("Rule 1: no save address outside layout.py", stray == [],
           f"{stray}")

    # Rule 3, first half -- the UI knows no address.
    if not os.path.isdir(UI_DIR):
        c.skip("Rule 3: the UI does not exist yet (MCR-TASK-11)")
    else:
        # The walk descends for the same reason the other two do
        # (CORR-MCR-014): a `ui/widgets/` would be invisible to os.listdir,
        # and this half of Rule 3 is the one the CORR's own table credited
        # with reaching the UI.
        offenders = []
        for root, dirs, names in os.walk(UI_DIR):
            dirs[:] = sorted(d for d in dirs if d != "__pycache__")
            for name in sorted(names):
                if not name.endswith(".py"):
                    continue
                path = os.path.join(root, name)
                rel = os.path.relpath(path, UI_DIR)
                with open(path, encoding="utf-8") as fh:
                    for lineno, line in enumerate(fh, 1):
                        text = line.split("#")[0]
                        for banned in FORBIDDEN_IN_UI:
                            if (f"import {banned}" in text
                                    or f"from {banned} import" in text):
                                offenders.append(f"ui/{rel}:{lineno}: {banned}")
        ok("Rule 3: the UI imports no core module that knows an address",
           offenders == [], f"{offenders}")

    # Rule 3, second half -- the core knows no Qt. Without this the mandatory
    # gate would start requiring PySide6 the day someone imports it upstream
    # of the core.
    ok("Rule 3: PySide6 is not loaded by the core",
       "PySide6" not in sys.modules)

    # Rule 2 is not checkable by a sweep: it is the round-trip, and it lives in
    # model.py and mcrio.py, which ran above.
    ok("Rule 2 is measured by the round-trip, not here", True)

    # Language (section 3.5). The sweep reads comments and strings, which is
    # the opposite of the Rule 1 sweep -- see glossary.py.
    glossary = attempt("import glossary",
                       lambda: importlib.import_module("glossary"))
    if glossary is None:
        c.fail("the language sweep did not run")
    else:
        found = attempt("sweep the language",
                        lambda: glossary.sweep(MCR_DIR), default=None)
        ok("no Spanish and no Portuguese in tools/mcr/*.py", found == [],
           f"{found}")


def _negative(c) -> None:
    """The planted controls: every guard has to be able to go red.

    Six seconds of wall clock, and it is what turns "the gate is green" into
    "the gate is green AND it knows how to be red". A guard that has never
    gone red is decoration -- the lesson of CORR-PES2-009 and -020, and the
    reason `controls.py` keeps the stimulus as a literal substitution instead
    of a sentence in a log.
    """
    ok, attempt = c.ok, c.attempt
    controls = attempt("import controls",
                       lambda: importlib.import_module("controls"))
    if controls is None:
        c.fail("the negative controls did not run")
        return
    results = attempt("plant every control",
                      lambda: controls.run_all(verbose=False), default=[])
    ok("every control is a single, matching substitution",
       all(r.matched == 1 for r in results),
       f"{[r.control.id for r in results if r.matched != 1]}")
    ok("every planted control goes red",
       bool(results) and all(r.good for r in results),
       f"green={[r.control.id for r in results if not r.good]}")
    print(f"  ..... {sum(1 for r in results if r.good)} of {len(results)} "
          f"controls red")


def run(verbose: bool = True, plant: bool = True) -> int:
    """Every module's self-check plus the rules. Returns the failure count."""
    # The mandatory gate must not depend on the fixture -- see the docstring.
    card = os.environ.pop("WE2002_MCR_CARD", None)
    total = 0
    try:
        for name in MODULES:
            c = harness.Checker(f"<import {name}>", verbose=False, silent=True)
            mod = c.attempt(name, lambda n=name: importlib.import_module(n))
            if mod is None:
                print(f"{name}.py self-check")
                print(f"  FAIL  the module could not be imported")
                print(f"{name}.py: 1 failure(s)")
                total += 1
                continue
            takes_card = "card_path" in inspect.signature(mod.self_check).parameters
            total += (mod.self_check(None, verbose) if takes_card
                      else mod.self_check(verbose))
        total += harness.run("design rules", _rules, verbose)
        if plant:
            total += harness.run("negative controls", _negative, verbose)
    finally:
        if card is not None:
            os.environ["WE2002_MCR_CARD"] = card
    print()
    print(f"mcr selftest: {total} failure(s) over {len(MODULES)} modules "
          f"plus the design rules")
    return total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true",
                    help="only the failures and the totals")
    ap.add_argument("--fast", action="store_true",
                    help="skip the planted negative controls (about 6 s)")
    a = ap.parse_args(argv)
    return 1 if run(verbose=not a.quiet, plant=not a.fast) else 0


if __name__ == "__main__":
    sys.exit(main())

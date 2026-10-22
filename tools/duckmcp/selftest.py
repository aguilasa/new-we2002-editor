#!/usr/bin/env python3
"""The duckmcp gate `duckmcp_selftest`: needs nothing, never skips.

In this order:

1. the package imports as `import duckmcp` with `tools/` on `sys.path`, and
   re-exports the errors;
2. `errors.self_check()`: `SKIP == 77` and the exception hierarchy;
3. `env.self_check()`: the new variable beats its legacy fallback, the
   legacy one alone beats the default, neither gives the default; the `:98`
   rule of `x_env`; `is_roms` on both separators; the `state_path` shape;
4. `audit.self_check()`: the audit of rule (b) over synthetic tools trees
   built in a temporary directory -- a clean one counts 0, one planted
   `import fork` counts 1, and each site category is seen once.

Each failed assertion prints one `FAIL` line naming it. The last line says
how many checks ran and how many failed; the exit is 0 only with none.

Usage:
    python3 tools/duckmcp/selftest.py [--quiet]
"""

import argparse
import os
import sys

DUCKMCP_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(DUCKMCP_DIR)
sys.path.insert(0, TOOLS_DIR)

import duckmcp  # noqa: E402
from duckmcp import audit, env, errors  # noqa: E402


class Checker:
    """Counts the checks that ran and the ones that failed."""

    def __init__(self, verbose):
        self.verbose = verbose
        self.ran = 0
        self.failed = 0

    def ok(self, name, cond, detail=""):
        self.ran += 1
        if cond:
            if self.verbose:
                print("  ok    %s" % name)
        else:
            self.failed += 1
            print("  FAIL  %s%s" % (name, "  " + str(detail) if detail else ""))

    def module(self, name, self_check):
        """Each `(name, passed, detail)` a module's self_check returns."""
        try:
            results = self_check()
        except Exception as exc:  # noqa: BLE001
            self.ok("%s.self_check() raised %s: %s"
                    % (name, type(exc).__name__, exc), False)
            return
        self.ok("%s.self_check() asserted something" % name, bool(results))
        for what, passed, detail in results:
            self.ok("%s: %s" % (name, what), passed, "" if passed else detail)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--quiet", action="store_true",
                    help="print only failures and the last line")
    args = ap.parse_args(argv)
    c = Checker(verbose=not args.quiet)

    c.ok("duckmcp is imported from tools/duckmcp/",
         os.path.dirname(os.path.abspath(duckmcp.__file__)) == DUCKMCP_DIR,
         duckmcp.__file__)
    c.ok("duckmcp has a __version__", bool(getattr(duckmcp, "__version__", "")))
    c.ok("duckmcp re-exports the errors",
         all(getattr(duckmcp, n, None) is getattr(errors, n)
             for n in ("SKIP", "Fail", "Skip", "NotRunning", "ToolError",
                       "SessionLost")))
    c.module("errors", errors.self_check)
    c.module("env", env.self_check)
    c.module("audit", audit.self_check)

    print("duckmcp_selftest: %d check(s) ran, %d failure(s)" % (c.ran, c.failed))
    return 0 if c.failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

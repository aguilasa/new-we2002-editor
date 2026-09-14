#!/usr/bin/env python3
"""Where `ok`, `attempt`, `refuses` and `skip` live -- and the guard around them.

Provenance (plan section 3.4): none of the four columns.  This module knows no
address, no format and no Qt; it knows how a self-check reports.

Adapted from `tools/mcr/harness.py`, which earned every paragraph of its own
docstring the hard way.  The reason to copy rather than import: the two cycles
share no build and no package, and a cross-project import would make this
cycle's mandatory gate depend on another project's tree staying put.

WHAT THE HELPERS ALONE CANNOT DO.  `attempt()` catches what the call you
wrapped raises.  An `ok(...)` whose expression raises, an import at the top of
a body, a helper called outside `attempt` -- none of those are covered, and
each one kills the run and hides every check after it.  `run()` closes that:
the body runs inside a try, anything escaping becomes ONE NAMED FAILURE with
the last frame, and the count still comes out.  The run cannot resume past the
escape, but the output is a report and not a stack trace.

Usage, in a module:

    def self_check(verbose=True) -> int:
        return harness.run("thing.py", _checks, verbose)

    def _checks(c) -> None:
        ok, attempt = c.ok, c.attempt
        refuses = c.refusing(ThingError)
        ...
"""

from __future__ import annotations

import functools
import sys
import traceback


class Checker:
    """Counts failures and prints one line per check."""

    def __init__(self, label: str, verbose: bool = True, silent: bool = False):
        self.label = label
        self.verbose = verbose
        # `silent` is for a checker UNDER TEST -- this module's own self-check
        # drives one and must not print its deliberate failures as if they
        # belonged to the run.  Nothing else sets it: a self-check that counts
        # in silence is a self-check nobody reads.
        self.silent = silent
        self.failures: list[str] = []

    def fail(self, name: str, detail: str = "") -> None:
        self.failures.append(name)
        if not self.silent:
            print("  FAIL  %s%s" % (name, "  " + detail if detail else ""))

    def ok(self, name, cond, detail="") -> None:
        if cond:
            if self.verbose and not self.silent:
                print("  ok    %s" % name)
        else:
            self.fail(name, detail)

    def skip(self, name, why="") -> None:
        """Neither a pass nor a failure -- and it has to SAY so.

        A check that skips in silence is how a negative control comes out
        green: the check the planted defect should have tripped never ran, and
        "0 failures" reads as approval.
        """
        if not self.silent:
            print("  skip  %s%s" % (name, " (%s)" % why if why else ""))

    def attempt(self, name, fn, default=None):
        """Runs `fn()`; an unexpected exception is a named failure, not a stop."""
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            self.fail("%s: raised %s: %s" % (name, type(exc).__name__, exc))
            return default

    def refuses(self, name, fn, fragment, kind=Exception) -> None:
        """Demands `fn()` raise *kind* with *fragment* in the message.

        The fragment is the point: the assertion is about WHICH refusal fires,
        not that some refusal did.  This cycle has two guards that both refuse
        a wrong disc -- one about palettes and one about a third disc -- and
        only the message tells them apart.
        """
        try:
            fn()
        except kind as exc:
            if fragment in str(exc):
                if self.verbose and not self.silent:
                    print("  ok    %s" % name)
            else:
                self.fail("%s: refused without saying %r: %s"
                          % (name, fragment, exc))
        except Exception as exc:  # noqa: BLE001
            self.fail("%s: raised %s, expected %s: %s"
                      % (name, type(exc).__name__, kind.__name__, exc))
        else:
            self.fail("%s: did NOT refuse" % name)

    def refusing(self, kind):
        """`refuses` with a module's own exception as the default kind."""
        return functools.partial(self.refuses, kind=kind)

    def report(self) -> int:
        if not self.silent:
            print("%s: %d failure(s)" % (self.label, len(self.failures)))
        return len(self.failures)


def run(label: str, body, verbose: bool = True, silent: bool = False,
        **kwargs) -> int:
    """Runs `body(checker, **kwargs)` under the outer guard.  Returns failures."""
    checker = Checker(label, verbose, silent)
    if not silent:
        print("%s self-check" % label)
    try:
        body(checker, **kwargs)
    except Exception as exc:  # noqa: BLE001
        where = ""
        frames = traceback.extract_tb(sys.exc_info()[2])
        if frames:
            frame = frames[-1]
            where = " at %s:%d in %s" % (
                frame.filename.replace("\\", "/").split("/")[-1],
                frame.lineno, frame.name)
        checker.fail(
            "the self-check itself raised %s%s" % (type(exc).__name__, where),
            "%s -- checks after this point did not run" % exc)
    return checker.report()


# --- self-check ------------------------------------------------------------

def _checks(c: Checker) -> None:
    ok = c.ok

    # THE HARNESS CANNOT CHECK ITSELF WITH ITSELF, and this is the one place
    # in this tree where a bare `raise` is the right tool.  Every assertion
    # below is an `ok(...)`, so a blind `ok` -- its failure branch replaced by
    # `pass` -- would approve its own blindness, this check included.  A raise
    # reaches the outer guard, which counts through `fail`, a path `ok` is not
    # on.  (`fail` is the primitive: a control on it is undetectable by
    # construction, which is why it is four lines long and does nothing else.)
    probe = Checker("<probe>", verbose=False, silent=True)
    probe.ok("deliberately false", False)
    if len(probe.failures) != 1:
        raise RuntimeError(
            "Checker.ok does not count a false check as a failure -- the "
            "harness is blind, and so is every module that reports through it")

    inner = Checker("<inner>", verbose=False, silent=True)
    inner.ok("a true check", True)
    ok("a true check is not a failure", inner.failures == [])
    inner.ok("a false check", False)
    ok("a false check is counted", len(inner.failures) == 1)

    ok("attempt returns the value", inner.attempt("x", lambda: 42) == 42)
    ok("attempt returns the default on a raise",
       inner.attempt("y", lambda: 1 // 0, default="fallback") == "fallback")
    ok("and counts it", len(inner.failures) == 2)

    inner.refuses("a real refusal", lambda: 1 // 0, "division", ZeroDivisionError)
    ok("a matching refusal passes", len(inner.failures) == 2)
    inner.refuses("wrong fragment", lambda: 1 // 0, "nothing like it",
                  ZeroDivisionError)
    ok("a refusal with the wrong message fails", len(inner.failures) == 3)
    inner.refuses("wrong type", lambda: 1 // 0, "division", KeyError)
    ok("a refusal of the wrong type fails", len(inner.failures) == 4)
    inner.refuses("no refusal at all", lambda: None, "anything", ValueError)
    ok("not refusing fails", len(inner.failures) == 5)

    partial = inner.refusing(ZeroDivisionError)
    partial("the default kind", lambda: 1 // 0, "division")
    ok("refusing() binds the default kind", len(inner.failures) == 5)
    partial("an override", lambda: 1 // 0, "division", kind=KeyError)
    ok("and the default can still be overridden", len(inner.failures) == 6)

    # skip is neither: it must not move the count in either direction.
    before = len(inner.failures)
    inner.skip("something that did not run", "no image")
    ok("a skip is not a failure", len(inner.failures) == before)

    # THE OUTER GUARD, exercised.  This is the whole reason the module exists:
    # a body that raises outside any helper must still produce a report.
    def exploding(checker):
        checker.ok("one check that runs", True)
        raise RuntimeError("boom")

    failures = run("<exploding>", exploding, verbose=False, silent=True)
    ok("a body that raises still reports", failures == 1,
       "failures=%s" % failures)

    def clean(checker):
        checker.ok("fine", True)

    ok("a clean body reports zero",
       run("<clean>", clean, verbose=False, silent=True) == 0)


def self_check(verbose: bool = True) -> int:
    return run("harness.py", _checks, verbose)


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

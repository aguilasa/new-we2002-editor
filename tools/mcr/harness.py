#!/usr/bin/env python3
"""The one house for `ok`, `attempt`, `refuses` -- and the guard around them.

Provenance (section 3.4 of the plan): none of the four columns. This module
knows no address, no codec and no container; it knows how a self-check
reports.

WHY IT EXISTS. The three helpers were copied into nine modules, and copies
drift: `card.py` called the fourth argument of `refuses` `exception` while the
others called it `kind`, and each copy carried its own docstring about the same
measurement. That is the cheap reason.

THE EXPENSIVE ONE IS THE OUTER GUARD, and it is what the helpers alone cannot
give. `attempt()` catches an exception raised by the call you WRAPPED. An
`ok(...)` whose expression raises, an import at the top of a body, a helper
called outside `attempt` -- none of those are covered, and each one kills the
run and hides every check after it. That happened five times in this cycle:
MCR-TASK-04 (`find_save`), MCR-TASK-06 (a hand-written `try/except` that let
every other exception through), and three times in MCR-TASK-07 (`encode_table`,
`read_all`, `decode_name`). Each was fixed by wrapping one more call, and the
sixth came back anyway -- CORR-MCR-008 measured the shape of it: with a
destination removed, `layout.py --self-check` left the run by traceback with
0 of its 29 assertions executed. Exit code 1, and nothing said what broke.

`run()` closes that: the body is called inside a `try`, anything that escapes
becomes ONE NAMED FAILURE with the last frame of the traceback, and the count
still comes out. The run stops at the escape -- it cannot resume -- but the
report is a report and not a stack trace, and the gate says which module and
which line.

Usage, in a module:

    def self_check(card_path=None, verbose=True) -> int:
        return harness.run("thing.py", _checks, verbose, card_path=card_path)

    def _checks(c, card_path=None) -> None:
        ok, attempt = c.ok, c.attempt
        refuses = c.refusing(ThingError)
        ...
"""

import functools
import sys
import traceback


class Checker:
    """Counts failures and prints one line per check."""

    def __init__(self, label: str, verbose: bool = True,
                 silent: bool = False):
        self.label = label
        self.verbose = verbose
        # `silent` is for a checker UNDER TEST -- the harness's own self-check
        # drives one and must not print its deliberate failures as if they
        # were the run's. Nothing else should set it: a self-check that counts
        # in silence is a self-check nobody reads.
        self.silent = silent
        self.failures: list[str] = []

    def fail(self, name: str, detail: str = "") -> None:
        self.failures.append(name)
        if not self.silent:
            print(f"  FAIL  {name}" + (f"  {detail}" if detail else ""))

    def ok(self, name, cond, detail="") -> None:
        if cond:
            if self.verbose and not self.silent:
                print(f"  ok    {name}")
        else:
            self.fail(name, detail)

    def skip(self, name, why="") -> None:
        """Not a failure and not a pass. It has to SAY so -- a check that
        skips in silence is the shape MCR-TASK-08 measured: a negative control
        came out green because the check the defect should have tripped never
        ran."""
        if not self.silent:
            print(f"  skip  {name}" + (f" ({why})" if why else ""))

    def attempt(self, name, fn, default=None):
        """Runs `fn()`; an unexpected exception is a named failure, not a stop."""
        try:
            return fn()
        except Exception as e:                        # noqa: BLE001
            self.fail(f"{name}: raised {type(e).__name__}: {e}")
            return default

    def refuses(self, name, fn, fragment, kind=Exception) -> None:
        """Demands that `fn()` raise `kind` with `fragment` in the message.

        The fragment is the point: the assertion is about WHICH refusal fires,
        not about some refusal firing. MCR-TASK-04 measured the difference --
        with the size check disabled, a truncated buffer still refused, by the
        magic instead, and only the fragment told the two apart.
        """
        try:
            fn()
        except kind as e:
            if fragment in str(e):
                if self.verbose and not self.silent:
                    print(f"  ok    {name}")
            else:
                self.fail(f"{name}: refused without saying {fragment!r}: {e}")
        except Exception as e:                        # noqa: BLE001
            self.fail(f"{name}: raised {type(e).__name__}, "
                      f"expected {kind.__name__}: {e}")
        else:
            self.fail(f"{name}: did NOT refuse")

    def refusing(self, kind):
        """`refuses` with this module's own exception as the default kind."""
        return functools.partial(self.refuses, kind=kind)

    def report(self) -> int:
        if not self.silent:
            print(f"{self.label}: {len(self.failures)} failure(s)")
        return len(self.failures)


def run(label: str, body, verbose: bool = True, silent: bool = False,
        **kwargs) -> int:
    """Runs `body(checker, **kwargs)` under the outer guard. Returns failures."""
    c = Checker(label, verbose, silent)
    if not silent:
        print(f"{label} self-check")
    try:
        body(c, **kwargs)
    except Exception as e:                            # noqa: BLE001
        where = ""
        frames = traceback.extract_tb(sys.exc_info()[2])
        if frames:
            f = frames[-1]
            where = f" at {f.filename.split('/')[-1]}:{f.lineno} in {f.name}"
        c.fail(f"the self-check itself raised {type(e).__name__}{where}",
               f"{e} -- checks after this point did not run")
    return c.report()


# --- self-check ------------------------------------------------------------

def _checks(c: Checker) -> None:
    ok = c.ok

    # THE HARNESS CANNOT CHECK ITSELF WITH ITSELF, and this is the one place in
    # the port where a bare `raise` is the right tool. Measured as the control
    # `harness-counts-nothing`: replacing the failure branch of `Checker.ok`
    # with `pass` left ALL FOURTEEN self-checks green, this one included --
    # every assertion below is an `ok(...)`, so a blind `ok` approves its own
    # blindness. A raise reaches the outer guard, which counts through `fail`,
    # a path `ok` is not on. (`fail` itself is the primitive: a control on it
    # is undetectable by construction, which is why it is four lines long and
    # does nothing else.)
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

    # THE OUTER GUARD, exercised. This is the whole reason the module exists:
    # a body that raises outside any helper must still produce a report.
    def exploding(checker):
        checker.ok("one check that runs", True)
        raise RuntimeError("boom")

    failures = run("<exploding>", exploding, verbose=False,
                   silent=True)
    ok("a body that raises still reports", failures == 1,
       f"failures={failures}")

    def clean(checker):
        checker.ok("fine", True)

    ok("a clean body reports zero",
       run("<clean>", clean, verbose=False, silent=True) == 0)


def self_check(verbose: bool = True) -> int:
    return run("harness.py", _checks, verbose)


if __name__ == "__main__":
    sys.exit(1 if self_check() else 0)

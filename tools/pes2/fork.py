#!/usr/bin/env python3
"""Shim: the fork launcher moved to `tools/duckmcp/fork.py` (PLAN-DUCKMCP-PY §2).

Every name the importers of this module use is the lib's own object, not a
copy -- `except fork.Fail` catches what `duckmcp.fork` raises because they
are the same class -- with two exceptions that are PES2's and stay here:

* `GAME_WINDOW`, the title of the PES2 window. The lib is game-agnostic
  (§2.1) and its `launch` has no default title; this module's `launch` is a
  thin function that passes `match=GAME_WINDOW` unless the caller names
  another (`ANY_WINDOW` included), and it calls `duckmcp.fork.launch`
  **at call time**, so a test that replaces `duckmcp.fork.launch` reaches
  every caller of this one too.
* `PES2_IMAGE` as the image of `launch` when the command line gives none.

`FORK_HOME` and `APPIMAGE` are read from `duckmcp.env` each time they are
asked for (a module `__getattr__`), not frozen at import.

**What a monkeypatch reaches.** `refuse_joysticks`, `joysticks`, `kill` and
`running_pids` here *are* the lib's functions, and they look their helpers
up in `duckmcp.fork`. Replacing `fork.joysticks` on *this* module therefore
reaches nothing; replace `duckmcp.fork.joysticks` (and
`duckmcp.fork.launch`), which is what `tools/kits/selftest.py` does since
DMCP-TASK-09.

This file goes away when the cycle closes (§2, decision 2); new code imports
`duckmcp.fork` with `tools/` on `sys.path`, and command lines call

    python3 tools/duckmcp/cli.py launch|kill|procs|recipe|which

The old command line still works and is translated onto that one:

    tools/pes2/fork.py launch [<copy.cue>]   # PES2_IMAGE when omitted
    tools/pes2/fork.py status                # = cli.py procs
    tools/pes2/fork.py kill|recipe|which
    tools/pes2/fork.py --self-check          # no emulator needed
"""

import argparse
import os
import sys

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from duckmcp import cli, env  # noqa: E402
from duckmcp import fork as _lib  # noqa: E402
from duckmcp.client import Client  # noqa: E402,F401
from duckmcp.errors import SKIP, Fail, NotRunning, Skip  # noqa: E402,F401
from duckmcp.fork import (ANY_WINDOW, DIALOGS, JOYSTICK_DIR,  # noqa: E402,F401
                          NOT_THE_GAME, PROCESS_NAMES, RECIPE, WINDOWS,
                          WINDOWS_PROCESS_NAMES, binary, hide_window,
                          installed, is_roms, joysticks, kill, pick_window,
                          refuse_joysticks, running_pids, size_window, status,
                          wait_for_mcp, which_binary)

GAME_WINDOW = "^Pro Evolution Soccer 2$"
"""The PES2 window title, which the lib may not spell (§2.1)."""


def __getattr__(name):
    """`FORK_HOME` and `APPIMAGE`, from `duckmcp.env` at the moment asked."""
    if name == "FORK_HOME":
        return env.fork_home()
    if name == "APPIMAGE":
        return env.appimage()
    raise AttributeError("module %r has no attribute %r" % (__name__, name))


def env_for(display, home=None):
    """The old name of `duckmcp.fork.child_env`."""
    return _lib.child_env(display, home)


def launch(image, display=None, timeout=120, home=None, verbose=True,
           log=None, match=GAME_WINDOW):
    """`duckmcp.fork.launch` with the PES2 title as the default `match`.

    The old positional order (`display` second) is kept; the lib's has
    `match` second. Resolved through the lib module at call time.
    """
    return _lib.launch(image, match=match, display=display, timeout=timeout,
                       home=home, verbose=verbose, log=log)


# --- the old command line ---------------------------------------------

def translate(argv, environ=None):
    """The old `fork.py` command line as a `duckmcp/cli.py` one.

    Returns `(cli_argv, self_check)`; `cli_argv` is None for a `launch` with
    no image anywhere. `environ` stands in for `os.environ` in the
    self-check.
    """
    environ = os.environ if environ is None else environ
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?",
                    choices=("launch", "kill", "status", "recipe", "which"),
                    default="status")
    ap.add_argument("image", nargs="?", help=".cue of a working copy")
    ap.add_argument("--display", default=None,
                    help="X display (default: duckmcp.env.display())")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--window", default=GAME_WINDOW,
                    help="regex of the game window title, or ANY to take the "
                         "widest window the process owns")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)
    if args.self_check:
        return None, True
    if args.command == "status":
        return ["procs"], False
    if args.command != "launch":
        return [args.command], False
    image = args.image or environ.get("PES2_IMAGE")
    if not image:
        return None, False
    line = ["launch", image, "--timeout", str(args.timeout),
            "--match", args.window]
    if args.display:
        line += ["--display", args.display]
    return line, False


def main(argv=None):
    line, check = translate(sys.argv[1:] if argv is None else argv)
    if check:
        return 1 if self_check() else 0
    if line is None:
        print("FORK FAILED: give the .cue of a working copy (or PES2_IMAGE)",
              file=sys.stderr)
        return 1
    return cli.main(line)


# --- self-check --------------------------------------------------------

def self_check(verbose=True):
    """The lib's `fork.self_check()` plus what this shim adds.

    Returns failure strings, empty when green.
    """
    results = list(_lib.self_check())

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    import inspect
    default = inspect.signature(launch).parameters["match"].default
    check("the shim's launch defaults to the PES2 title", default == GAME_WINDOW,
          repr(default))

    # The seam the kits selftest relies on: replacing duckmcp.fork.launch and
    # duckmcp.fork.joysticks reaches the callers of this module.
    seen = []
    real_launch, real_joysticks = _lib.launch, _lib.joysticks
    try:
        _lib.launch = lambda image, **kw: seen.append((image, kw)) or "stub"
        got = launch("x.cue", ":5", verbose=False)
        launch("y.cue", match=ANY_WINDOW, verbose=False)
        check("launch forwards to duckmcp.fork.launch at call time",
              got == "stub" and len(seen) == 2, seen)
        check("launch passes GAME_WINDOW unless told otherwise",
              [kw.get("match") for _, kw in seen] == [GAME_WINDOW, ANY_WINDOW]
              and seen[0][1].get("display") == ":5", seen)
        _lib.joysticks = lambda root=None: ["/dev/input/js0"]
        try:
            refuse_joysticks()
            check("a patched duckmcp.fork.joysticks reaches refuse_joysticks",
                  False, "it was let through")
        except Fail as exc:
            check("a patched duckmcp.fork.joysticks reaches refuse_joysticks",
                  "js0" in str(exc), str(exc))
    finally:
        _lib.launch, _lib.joysticks = real_launch, real_joysticks

    check("FORK_HOME is env.fork_home(), read when asked",
          globals().get("FORK_HOME") is None
          and sys.modules[__name__].FORK_HOME == env.fork_home())
    child = env_for(":98", home="/nowhere")
    check("env_for blanks XAUTHORITY on :98", child.get("XAUTHORITY") == "")

    line, _ = translate(["launch", "a.cue", "--display", ":7"], environ={})
    check("the old launch line becomes cli.py launch --match GAME_WINDOW",
          line == ["launch", "a.cue", "--timeout", "120", "--match",
                   GAME_WINDOW, "--display", ":7"], line)
    line, _ = translate(["launch", "--window", "ANY"],
                        environ={"PES2_IMAGE": "b.cue"})
    check("PES2_IMAGE is the image when none is given, --window is --match",
          line == ["launch", "b.cue", "--timeout", "120", "--match", "ANY"],
          line)
    check("a launch with no image anywhere is refused",
          translate(["launch"], environ={})[0] is None)
    check("the old status is cli.py procs",
          translate([], environ={})[0] == ["procs"])

    bad = ["%s: %s" % (name, detail) if detail else name
           for name, passed, detail in results if not passed]
    if verbose:
        for name, passed, detail in results:
            print("  %s   %s" % ("ok" if passed else "FAIL", name)
                  + ("  (%s)" % (detail,) if detail and not passed else ""))
        print("SELF-CHECK " + ("FAILED" if bad else "OK: %d checks"
                               % len(results)))
    return bad


if __name__ == "__main__":
    sys.exit(main())

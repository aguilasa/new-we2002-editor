#!/usr/bin/env python3
"""The `mcr_ui` gate: the window comes up on :98, or the test skips with 77.

Provenance (section 3.4 of the plan): none of the four columns.

THREE THINGS CAN BE MISSING, and none of them is a failure:

  the venv with PySide6 (`make mcr-venv`);
  `tools/mcr/ui/app.py`, which is MCR-TASK-11;
  a reachable X display.

Any of those exits 77, which is what tells ctest the test skipped -- the same
convention as the golden tests and `pes2_image`. Section 4.4 of the plan wants
a clean machine to report `1 passed, 2 skipped`, never `0 tests` and never a
red run.

THE CONTRACT WITH THE UI, and MCR-TASK-11 has to satisfy it: `ui/app.py
--smoke` opens the window, lets Qt paint one frame, and exits 0 without
waiting for a human. That keeps the gate to one process and no `xdotool`. The
same file carries the line, so whoever builds the UI reads it there.

THE DISPLAY IS `:98`, always. `:1` is the user's real session and a window
there interrupts them; the rule is in `CLAUDE.md` and has no exception in this
cycle. The server runs without `-auth`, so an EMPTY `XAUTHORITY` is the correct
value -- this file resolves it the same way `make run-98` does, by looking for
an `-auth` in the running Xvfb's command line and clearing the variable when
there is none.

Usage:

    python3 tools/mcr/ui_check.py
    ctest -R mcr_ui
"""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout                                            # noqa: E402

SKIP = 77
DISPLAY = ":98"
MCR_DIR = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(MCR_DIR, "ui", "app.py")
TIMEOUT = 120


def skip(why: str) -> int:
    print(f"skipped: {why}")
    return SKIP


def venv_python() -> str | None:
    found = layout.find_upward(os.path.join("work", "venv-mcr", "bin",
                                            "python"))
    return found if found and os.access(found, os.X_OK) else None


def xauthority() -> str:
    """The Xvfb's own cookie, or the empty string when it has none."""
    try:
        out = subprocess.run(["ps", "-o", "args=", "-C", "Xvfb"],
                             capture_output=True, text=True).stdout
    except OSError:
        return ""
    for line in out.splitlines():
        if f"Xvfb {DISPLAY} " in line + " " and "-auth" in line:
            parts = line.split()
            return parts[parts.index("-auth") + 1]
    return ""


def main() -> int:
    python = venv_python()
    if python is None:
        return skip("no venv with PySide6 -- run `make mcr-venv`")
    probe = subprocess.run([python, "-c", "import PySide6"],
                           capture_output=True, text=True)
    if probe.returncode:
        return skip("the venv has no PySide6 -- run `make mcr-venv`")
    if not os.path.isfile(APP):
        return skip("tools/mcr/ui/app.py does not exist yet (MCR-TASK-11)")

    env = dict(os.environ, DISPLAY=DISPLAY)
    auth = xauthority()
    if auth:
        env["XAUTHORITY"] = auth
    else:
        env.pop("XAUTHORITY", None)

    try:
        run = subprocess.run([python, APP, "--smoke"], env=env,
                             capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        print(f"FAIL: {APP} --smoke did not exit within {TIMEOUT}s")
        return 1
    output = run.stdout + run.stderr
    if "could not connect to display" in output or "cannot open display" in output:
        return skip(f"no X server on {DISPLAY} -- "
                    f"`Xvfb {DISPLAY} -screen 0 1280x1024x24 -nolisten tcp &`")
    print(output.rstrip())
    if run.returncode:
        print(f"FAIL: {APP} --smoke exited {run.returncode}")
        return 1
    print(f"ok: the UI came up on {DISPLAY} and exited cleanly")
    return 0


if __name__ == "__main__":
    sys.exit(main())

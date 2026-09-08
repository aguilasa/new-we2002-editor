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

THE SECOND CONTRACT IS MCR-TASK-12'S, and it is why this file imports `mcrio`.
`app.py --write-probe DIR` edits through the real widgets and writes two cards;
it reports what it did and judges nothing, because judging needs an address and
Rule 3 keeps `layout` and `mcrio` out of `ui/`. So the screen measures and this
file decides: the bytes that moved for one attribute are inside that player's
record and nowhere else, both written cards pass the round-trip, and the values
come back off the disk. It runs only when there is a card, and never on the
card itself -- a COPY in a temporary directory, like every other write in this
cycle.

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

import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attributes                                        # noqa: E402
import layout                                            # noqa: E402
import mcrio                                             # noqa: E402

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


def _bytes(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def write_probe(python: str, env: dict) -> int:
    """The MCR-TASK-12 half: edit through the widgets and judge the files.

    Returns 0 when it passed or when there is no card to run it on -- the
    smoke run above is what makes the target pass, and a machine without a
    fixture must not turn this into a failure. It prints what it measured
    either way.
    """
    card = env.get(mcrio.CARD_ENV)
    if not card or not os.path.isfile(card):
        print(f"note: no {mcrio.CARD_ENV}, so the write probe did not run")
        return 0

    with tempfile.TemporaryDirectory() as tmp:
        # A COPY, always. The fixture is what every measurement in this cycle
        # is anchored to, and `mcrio.check_destination` would refuse it anyway.
        source = os.path.join(tmp, "probe.mcr")
        shutil.copyfile(card, source)
        before = _bytes(source)

        run = subprocess.run([python, APP, source, "--write-probe", tmp],
                             env=env, capture_output=True, text=True,
                             timeout=TIMEOUT)
        output = run.stdout + run.stderr
        line = next((l for l in run.stdout.splitlines()
                     if l.startswith("probe-json ")), None)
        if run.returncode or line is None:
            print(output.rstrip())
            print(f"FAIL: {APP} --write-probe exited {run.returncode}")
            return 1
        r = json.loads(line[len("probe-json "):])

        bad = []
        one, full = r.get("one_attribute"), r.get("full")
        if not one or not os.path.isfile(one):
            bad.append("the default Save wrote no file")
        if not r.get("copy_target_differs"):
            bad.append("the default Save wrote over the card that was opened")
        if _bytes(source) != before:
            bad.append("the card the window opened was written to")

        moved = mcrio.differing(before, _bytes(one)) if one else []
        base = layout.player_attribute_address(r["slot"])
        window = range(base, base + attributes.BLOB_BYTES)
        if not moved:
            bad.append("one attribute through the form moved no byte")
        elif not all(i in window for i in moved):
            bad.append(f"an attribute moved bytes outside the record: "
                       f"{[hex(i) for i in moved]}")

        for name, target in (("one attribute", one), ("everything", full)):
            if not target or not os.path.isfile(target):
                bad.append(f"the {name} card was not written")
                continue
            for form in (1, 2):
                differ = mcrio.roundtrip(target, form=form)
                if differ:
                    bad.append(f"the {name} card fails round-trip form {form} "
                               f"at {hex(differ[0])}")

        if full and os.path.isfile(full):
            back = mcrio.load(full)
            p = back.players[r["slot"]]
            f = back.formation
            for what, got, want in (
                    ("attribute", p.attributes[r["field"]], r["attribute"]),
                    ("name", p.name, r["name"]),
                    ("shirt number (table)", p.shirt_number, r["number"]),
                    ("shirt number (record)", p.attributes["number"],
                     r["number"]),
                    ("x", [f.x[0], f.y[0]], r["xy_after"]),
                    ("role", f.role[0], r["role"]),
                    ("kicker", f.kickers[0], r["kicker"])):
                if got != want:
                    bad.append(f"{what} came back {got}, the screen set {want}")
            if r["xy_after"] == r["xy_before"]:
                bad.append("the drag moved no player")

        print(f"probe: one attribute moved {len(moved)} byte(s) at "
              f"{[hex(i) for i in moved]}, inside slot {r['slot']}'s record "
              f"at {base:#07x}")
        print(f"probe: the drag moved outfield slot 1 from {r['xy_before']} to "
              f"{r['xy_after']}, in the card's own units")
        print(f"probe: both written cards round-trip, and "
              f"{os.path.basename(one)} is a copy, not the card opened")
        if bad:
            for line in bad:
                print(f"FAIL: {line}")
            return 1
    return 0


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

    try:
        return write_probe(python, env)
    except subprocess.TimeoutExpired:
        print(f"FAIL: {APP} --write-probe did not exit within {TIMEOUT}s")
        return 1


if __name__ == "__main__":
    sys.exit(main())

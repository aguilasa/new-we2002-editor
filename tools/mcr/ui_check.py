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

AND THE GATE CHOOSES WHERE THE DRAG LANDS. CORR-MCR-018 measured the shape this
had first: the probe pushed a marker by a fixed number of pixels and reported
where the model said it ended up, and that number is the OUTPUT of the
conversion under test -- so the judge was comparing it against itself, and
removing the division from `to_card_x` left the gate green while it printed
`[48, 43]` "in the card's own units". Now the destination is read off the card
here, passed in as `--drag-to`, and the screen has to hit it. The same
substitution is planted in a copy of the tree at the end of every run, and the
gate demands the red.

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


# The defect the negative step plants, and the only place it is written down.
# Same convention as `controls.py`: file, function, the exact line, and what it
# becomes -- because CORR-MCR-009 measured that prose does not reproduce. It
# does NOT live in `controls.py`, and that is not an oversight: that engine
# plants a copy of the tree and runs `<module>.py --self-check` under the system
# interpreter, and the module that catches this one is THIS file, which needs
# PySide6, the venv and a display. So the red case lives where it can run, the
# way `mcrio.negative` keeps the five injections of section 5.2.
BREAK_FILE = os.path.join("ui", "formation_view.py")
BREAKS = (
    ("to_card_x",
     "    return max(0, min(X_MAX, round(pitch_px / X_SCALE)))",
     "    return max(0, min(X_MAX, round(pitch_px)))"),
    ("to_card_y",
     "    return max(0, min(Y_MAX, round(pitch_px / Y_SCALE)))",
     "    return max(0, min(Y_MAX, round(pitch_px)))"),
)

# How far the gate asks the drag to go, in the CARD's units, and the pitch
# limits it stays inside. Away from the touchline on purpose, so the clamp in
# `to_card_*` is never what decides where the marker lands.
DRAG_STEP = (3, 11)
DRAG_LIMIT = (40, 80)


def _step(value: int, delta: int, limit: int) -> int:
    """`value` moved by `delta`, or the other way when there is no room."""
    return value + delta if value + delta <= limit else value - delta


def _target(source: str) -> tuple[int, int]:
    """Where the drag must land, chosen by the GATE from the card itself.

    CORR-MCR-018: while this came out of the screen -- push some pixels, report
    where the model ended up -- the judge was comparing the conversion against
    itself, and removing the division from `to_card_x` left everything green.
    Reading the card here costs one `mcrio.load` and makes the expected value
    independent of the code under test.
    """
    f = mcrio.load(source).formation
    return (_step(f.x[0], DRAG_STEP[0], DRAG_LIMIT[0]),
            _step(f.y[0], DRAG_STEP[1], DRAG_LIMIT[1]))


def _run(python: str, app: str, source: str, out_dir: str,
         target: tuple[int, int], env: dict):
    """One probe run. Returns `(report, output)`; report is None on failure."""
    run = subprocess.run(
        [python, app, source, "--write-probe", out_dir,
         "--drag-to", f"{target[0]},{target[1]}"],
        env=env, capture_output=True, text=True, timeout=TIMEOUT)
    line = next((l for l in run.stdout.splitlines()
                 if l.startswith("probe-json ")), None)
    if run.returncode or line is None:
        return None, run.stdout + run.stderr
    return json.loads(line[len("probe-json "):]), run.stdout + run.stderr


def _judge(r: dict, source: str, before: bytes,
           target: tuple[int, int]) -> list[str]:
    """Everything wrong with one probe run. Empty is the pass.

    This is the whole of the judging, in one function, because the negative
    step below runs the SAME judge against a planted tree -- a guard that has
    never been red is decoration, and a guard whose red path is a different
    piece of code is worse.
    """
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

    # The drag, judged against the destination THIS file chose.
    dx, dy = r["drag_pixels"]
    sx, sy = r["scales"]
    if r["xy_after"] != list(target):
        # The displacement is in WIDGET pixels, which carry the widget's own
        # scaling on top of the two factors -- so it is printed as diagnosis
        # and never divided here. The expectation is `target`, which came off
        # the card and owes the screen nothing.
        bad.append(
            f"the drag was told to land on {list(target)} in the card's own "
            f"units, starting from {r['xy_before']}, and the model says "
            f"{r['xy_after']}; the mouse moved {dx:.0f},{dy:.0f} widget "
            f"pixels and the screen's factors are {sx} and {sy}")
    if r["xy_after"] == r["xy_before"]:
        bad.append("the drag moved no player")

    for name, path in (("one attribute", one), ("everything", full)):
        if not path or not os.path.isfile(path):
            bad.append(f"the {name} card was not written")
            continue
        for form in (1, 2):
            differ = mcrio.roundtrip(path, form=form)
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
                ("shirt number (record)", p.attributes["number"], r["number"]),
                ("the dragged position", [f.x[0], f.y[0]], list(target)),
                ("role", f.role[0], r["role"]),
                ("kicker", f.kickers[0], r["kicker"]),
                ("captain", f.captain, r["captain"])):
            if got != want:
                bad.append(f"{what} came back {got}, the gate asked for {want}")
    return bad


def _plant(python: str, card: str, env: dict, name: str, old: str,
           new: str) -> tuple[bool, str]:
    """One substitution in a copy of the tree. `(did the gate redden, why)`."""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = os.path.join(tmp, "mcr")
        shutil.copytree(MCR_DIR, sandbox,
                        ignore=shutil.ignore_patterns("__pycache__"))
        broken = os.path.join(sandbox, BREAK_FILE)
        with open(broken, encoding="utf-8") as fh:
            text = fh.read()
        if text.count(old) != 1:
            return False, (f"the substitution for {name} matched "
                           f"{text.count(old)} times, not once -- a literal "
                           f"that does not match leaves the copy intact and "
                           f"the run comes out green for the wrong reason")
        with open(broken, "w", encoding="utf-8") as fh:
            fh.write(text.replace(old, new))

        source = os.path.join(tmp, "probe.mcr")
        shutil.copyfile(card, source)
        before = _bytes(source)
        target = _target(source)
        r, output = _run(python, os.path.join(sandbox, "ui", "app.py"),
                         source, tmp, target, env)
        if r is None:
            # The planted tree failing to run at all is red for the wrong
            # reason, and saying so is cheaper than believing it.
            return False, (f"the planted probe for {name} did not run, so "
                           f"nothing was proved:\n{output.rstrip()}")
        bad = _judge(r, source, before, target)
        if not bad:
            return False, (f"{BREAK_FILE} :: {name} was broken "
                           f"({old.strip()} -> {new.strip()}) and the gate "
                           f"still passed -- it reported {r['xy_after']} for "
                           f"a drag to {list(target)}")
        return True, bad[0]


def negative_probe(python: str, card: str, env: dict) -> int:
    """Break each half of the conversion, and demand the gate reddens.

    Section 5.2's rule, applied to the one guard MCR-TASK-12 added: the drag's
    way back from pitch pixels to the card's units. CORR-MCR-018 measured the
    `to_card_x` substitution going green; `to_card_y` is planted beside it
    because the judge compares the PAIR, and a guard that only ever saw one
    half broken is half a guard.
    """
    failed = 0
    for name, old, new in BREAKS:
        red, why = _plant(python, card, env, name, old, new)
        if red:
            print(f"negative: breaking {name} reddens the gate -- {why}")
        else:
            print(f"FAIL: {why}")
            failed += 1
    return 1 if failed else 0


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
        target = _target(source)

        r, output = _run(python, APP, source, tmp, target, env)
        if r is None:
            print(output.rstrip())
            print(f"FAIL: {APP} --write-probe did not report")
            return 1

        bad = _judge(r, source, before, target)
        moved = mcrio.differing(before, _bytes(r["one_attribute"])) \
            if r.get("one_attribute") else []
        base = layout.player_attribute_address(r["slot"])
        print(f"probe: one attribute moved {len(moved)} byte(s) at "
              f"{[hex(i) for i in moved]}, inside slot {r['slot']}'s record "
              f"at {base:#07x}")
        print(f"probe: the gate asked for {list(target)} in the card's own "
              f"units and the drag landed on {r['xy_after']}, from "
              f"{r['xy_before']}")
        print(f"probe: both written cards round-trip, and "
              f"{os.path.basename(r['one_attribute'])} is a copy, not the "
              f"card opened")
        if bad:
            for line in bad:
                print(f"FAIL: {line}")
            return 1

    return negative_probe(python, card, env)


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

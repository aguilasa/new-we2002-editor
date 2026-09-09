#!/usr/bin/env python3
"""The `mcr_ui` gate: the window comes up on :98, or the test skips with 77.

Provenance (section 3.4 of the plan): none of the four columns.

THREE THINGS CAN BE MISSING, and none of them is a failure:

  the venv with PySide6 (`make mcr-venv`);
  `tools/mcr/ui/app.py`, which is MCR-TASK-11;
  a reachable X display.

Any of those exits 77, which is what tells ctest the test skipped -- the same
convention as the golden tests and `pes2_image`. Section 4.4 of the plan wants
a clean machine to report `2 passed, 2 skipped`, never `0 tests` and never a
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

THE THIRD CONTRACT IS MCR-TASK-15'S. `app.py --open-probe` brings the window up
with NO card and reports how it offers to open one; this file judges. The rule
it enforces is that the window is the way in: it comes up empty rather than
throwing a file dialog on screen ahead of itself, the empty page carries a
button, the button reaches the same action as the menu item, cancelling changes
nothing, a named card opens, and unsaved edits are not discarded without a
question. Two substitutions are planted in a copy of `ui/main_window.py` at the
end -- the button's wiring and the dirty guard -- and the gate demands the red.

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

# The break for the out-of-domain step, kept apart because it is judged by a
# different probe: putting the cap back is exactly the defect CORR-MCR-020
# found, and the box then shows 10 for a card holding 15 with nothing saying so.
OUTSIDE_BREAKS = (
    ("the captain's range",
     "        self.captain.setRange(0, BYTE_MAX)",
     "        self.captain.setRange(0, STARTERS - 1)"),
    ("the annotation",
     "        spin.setSuffix(OUTSIDE_SUFFIX)",
     "        spin.setSuffix(\"\")"),
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


def _sandbox(tmp: str, name: str, old: str, new: str,
             where: str = BREAK_FILE) -> tuple[str | None, str]:
    """A copy of the tree with one substitution applied. `(path, why not)`.

    Shared by every plant below, so the rule about a literal matching exactly
    once is written down in one place -- it is the same rule `controls.py`
    enforces, and the same failure it reports as a broken control. `where` is
    the file to break: the drag and the domain plants live in
    `ui/formation_view.py`, the open plants in `ui/main_window.py`.
    """
    sandbox = os.path.join(tmp, "mcr")
    shutil.copytree(MCR_DIR, sandbox,
                    ignore=shutil.ignore_patterns("__pycache__"))
    broken = os.path.join(sandbox, where)
    with open(broken, encoding="utf-8") as fh:
        text = fh.read()
    if text.count(old) != 1:
        return None, (f"the substitution for {name} matched "
                      f"{text.count(old)} times, not once -- a literal "
                      f"that does not match leaves the copy intact and "
                      f"the run comes out green for the wrong reason")
    with open(broken, "w", encoding="utf-8") as fh:
        fh.write(text.replace(old, new))
    return sandbox, ""


def _plant(python: str, card: str, env: dict, name: str, old: str,
           new: str) -> tuple[bool, str]:
    """One substitution in a copy of the tree. `(did the gate redden, why)`."""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, old, new)
        if sandbox is None:
            return False, why

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


# The two values the out-of-domain probe plants. Both outside the oracle's
# grid of 0..10, and both legal bytes: the core validates the byte and
# preserves what it finds, so a card like this round-trips at zero and every
# other measurement of this cycle stays green. CORR-MCR-020 measured the
# screen showing 10 for each of them, with no label, no tooltip and no colour.
OUTSIDE_CAPTAIN = 15
OUTSIDE_KICKER = 19
# The starting eleven, derived rather than typed: it is the ten the
# formation carries X and Y for, plus the goalkeeper, which is why the
# oracle's grid has eleven rows. `ui/formation_view.py` calls it STARTERS.
STARTERS = layout.OUTFIELD_COUNT + 1


def _report_formation(python: str, app: str, source: str, env: dict):
    """One `--report-formation` run. `(report, output)`; report None on failure."""
    run = subprocess.run([python, app, source, "--report-formation"],
                         env=env, capture_output=True, text=True,
                         timeout=TIMEOUT)
    line = next((l for l in run.stdout.splitlines()
                 if l.startswith("formation-json ")), None)
    if run.returncode or line is None:
        return None, run.stdout + run.stderr
    return json.loads(line[len("formation-json "):]), run.stdout + run.stderr


def _judge_formation(r: dict) -> list[str]:
    """Everything wrong with one out-of-domain run. Empty is the pass.

    THE RULE IS "SHOW IT OR SAY IT", and either answer is honest: the box may
    carry the card's number, or it may carry another number and a LABEL naming
    the card's. What it may not do is display a different number with nothing
    saying so, which is what it did before CORR-MCR-020.

    THE LABEL MEANS THE SUFFIX, NOT THE TOOLTIP, and that distinction is the
    whole strictness of this judge. A tooltip is not a display: it costs a
    hover nobody performs on a value that looks ordinary, and the number that
    looks ordinary is exactly the failure. Measured while writing this: with
    the cap put back, the tooltip still named 15 while the box read 10, and a
    judge that accepted the tooltip called that a pass. The tooltip is carried
    through anyway and printed in the complaint -- as diagnosis, never as the
    answer.
    """
    bad = []
    card, shown = r["card"], r["shown"]
    pairs = [("captain", card["captain"], shown["captain"],
              r["suffix"]["captain"], r["tooltip"]["captain"])]
    for i, (held, on_screen, suffix, tip) in enumerate(zip(
            card["kickers"], shown["kickers"],
            r["suffix"]["kickers"], r["tooltip"]["kickers"])):
        pairs.append((f"kicker {i}", held, on_screen, suffix, tip))

    for what, held, on_screen, suffix, tip in pairs:
        inside = 0 <= held < STARTERS
        if on_screen == held:
            if not inside and not suffix.strip():
                bad.append(f"{what} holds {held}, outside the starting "
                           f"{STARTERS}, and the box shows it with no visible "
                           f"mark -- tooltip={tip[:40]!r}")
            continue
        # The number differs, so a VISIBLE label has to name the card's value.
        if str(held) not in suffix:
            bad.append(f"{what} holds {held} and the screen shows "
                       f"{on_screen}, with no visible label naming {held} -- "
                       f"suffix={suffix!r} tooltip={tip[:40]!r}")
    return bad


def _outside_card(card: str, dest: str) -> None:
    """A copy of `card` with a captain and a kicker outside the grid."""
    shutil.copyfile(card, dest)
    save = mcrio.load(dest)
    save.formation.captain = OUTSIDE_CAPTAIN
    save.formation.kickers[0] = OUTSIDE_KICKER
    save.write()
    mcrio.store(save, dest, force=True)


def outside_probe(python: str, card: str, env: dict) -> int:
    """Open a card the oracle's grid cannot express, and demand it be told.

    The core is not the thing under test here and is checked anyway: the
    planted copy has to round-trip at zero in both forms, because that is what
    made this defect invisible -- the byte was safe the whole time and only the
    window lied about it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        source = os.path.join(tmp, "outside.mcr")
        _outside_card(card, source)
        for form in (1, 2):
            differ = mcrio.roundtrip(source, form=form)
            if differ:
                print(f"FAIL: the planted card does not round-trip in form "
                      f"{form}, at {hex(differ[0])} -- the probe would be "
                      f"measuring the core, not the screen")
                return 1

        r, output = _report_formation(python, APP, source, env)
        if r is None:
            print(output.rstrip())
            print(f"FAIL: {APP} --report-formation did not report")
            return 1
        bad = _judge_formation(r)
        print(f"outside: the card holds captain={r['card']['captain']} "
              f"kickers={r['card']['kickers']}, and the screen shows "
              f"captain={r['shown']['captain']}{r['suffix']['captain']!r} "
              f"kicker0={r['shown']['kickers'][0]}"
              f"{r['suffix']['kickers'][0]!r}")
        if bad:
            for line in bad:
                print(f"FAIL: {line}")
            return 1

    return _outside_negative(python, card, env)


def _plant_outside(python: str, card: str, env: dict, name: str, old: str,
                   new: str) -> tuple[bool, str]:
    """The same substitution machinery, judged by `_judge_formation`."""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, old, new)
        if sandbox is None:
            return False, why
        source = os.path.join(tmp, "outside.mcr")
        _outside_card(card, source)
        r, output = _report_formation(
            python, os.path.join(sandbox, "ui", "app.py"), source, env)
        if r is None:
            return False, (f"the planted probe for {name} did not run, so "
                           f"nothing was proved:\n{output.rstrip()}")
        bad = _judge_formation(r)
        if not bad:
            return False, (f"{BREAK_FILE} :: {name} was broken "
                           f"({old.strip()} -> {new.strip()}) and the gate "
                           f"still passed -- it reported "
                           f"{r['shown']['captain']} for a card holding "
                           f"{r['card']['captain']}")
        return True, bad[0]


def _outside_negative(python: str, card: str, env: dict) -> int:
    """Put the clamp back, and demand the step above reddens."""
    failed = 0
    for name, old, new in OUTSIDE_BREAKS:
        red, why = _plant_outside(python, card, env, name, old, new)
        if red:
            print(f"negative: breaking {name} reddens the gate -- {why}")
            PLANTED.append(name)
        else:
            print(f"FAIL: {why}")
            failed += 1
    return 1 if failed else 0


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
            PLANTED.append(name)
        else:
            print(f"FAIL: {why}")
            failed += 1
    return 1 if failed else 0


# The two substitutions the open step plants, both in the window rather than in
# the pitch -- so `_sandbox` is told where. The first unwires the empty page's
# button from the action the menu item carries: the two ways in stop being one
# path, and the probe's click reaches nothing. The second removes the guard
# that asks before unsaved edits are discarded.
OPEN_BREAK_FILE = os.path.join("ui", "main_window.py")
OPEN_BREAKS = (
    ("the button's wiring",
     "        self.open_button.clicked.connect(self.act_open.trigger)",
     "        self.open_button.clicked.connect(lambda: None)"),
    ("the dirty guard",
     "        if self._dirty and not self._confirm_discard():",
     "        if False:"),
    # MCR-TASK-16's guard, planted by CORR-MCR-025. `CARD_FILTER` is a LABEL,
    # and Rule 3 keeps `gme.py` out of the window -- so the only thing tying
    # what the dialogs advertise to what the core reads and writes is the
    # assertion in `_judge_open`, and an assertion with no red case is a
    # sentence, not a guard. Breaking the first line of the literal is enough:
    # the dialogs then offer `.mcr` alone, which is exactly what they offered
    # before that task.
    ("the dialog filter",
     'CARD_FILTER = ("Memory cards (*.mcr *.mcd *.gme);;"',
     'CARD_FILTER = ("Memory cards (*.mcr);;"'),
)

# Every planted defect that actually reddened the gate, counted where it runs
# instead of written down in prose. CORR-MCR-017 measured what a copied total
# costs: the number outlives the run that produced it, in the very file the
# commands read before running anything. The profile quotes this line.
PLANTED: list[str] = []
PLANTED_TOTAL = len(BREAKS) + len(OUTSIDE_BREAKS) + len(OPEN_BREAKS)


def _run_open(python: str, app: str, card: str | None, env: dict):
    """One `--open-probe` run. `(report, output)`; report None on failure."""
    argv = [python, app, "--open-probe"]
    if card:
        argv += ["--open-with", card]
    run = subprocess.run(argv, env=env, capture_output=True, text=True,
                         timeout=TIMEOUT)
    line = next((l for l in run.stdout.splitlines()
                 if l.startswith("open-json ")), None)
    if run.returncode or line is None:
        return None, run.stdout + run.stderr
    return json.loads(line[len("open-json "):]), run.stdout + run.stderr


def _judge_open(r: dict) -> list[str]:
    """Everything wrong with one open run. Empty is the pass.

    THE WINDOW IS THE WAY IN. Before MCR-TASK-15 `app.py` called `choose()`
    ahead of `show()`, so a run with no card put a modal file dialog on screen
    over nothing at all, and cancelling it left a window with no visible way to
    open anything -- the menu item existed, and a person who had just dismissed
    a dialog had no reason to look for it.
    """
    bad = []
    if r["path"] is not None or not r["save_is_none"]:
        bad.append(f"the window came up holding {r['path']}, and nothing "
                   f"asked it to open a card")
    if not r["empty_shown"]:
        bad.append("with no card open the window is not showing the empty page")
    if not r["button_visible"]:
        bad.append("the empty page has no visible button to open a card")
    if "open" not in r["button_text"].lower():
        bad.append(f"the empty page's button says {r['button_text']!r}, which "
                   f"does not offer to open anything")
    if not r["open_enabled"] or "Open" not in r["open_text"]:
        bad.append(f"the menu item is {r['open_text']!r}, "
                   f"enabled={r['open_enabled']}")
    if r["open_shortcut"] != "Ctrl+O":
        bad.append(f"the open item's shortcut is {r['open_shortcut']!r}, "
                   f"not the standard Ctrl+O")
    if any(r["writable"]):
        bad.append(f"the save actions are enabled with no card open: "
                   f"{r['writable']}")

    # THE THREE CONTAINERS HAVE TO BE OFFERED (MCR-TASK-16). The core reads any
    # of them by content and writes the one the destination's name asks for; a
    # dialog that advertises only `.mcr` hides two of the three from the person
    # holding the file. This is a check on the LABEL -- the rule itself lives
    # in `gme.py`, where Rule 3 keeps it out of the window.
    #
    # IT IS THE FIRST GROUP THAT IS JUDGED, and CORR-MCR-025 measured why: Qt
    # opens with that one selected, so a person who never touches the combo
    # sees only what it names. Searching the whole string instead let the
    # narrower groups below it -- "Raw dumps (*.mcr *.mcd)", "DexDrive
    # containers (*.gme)" -- satisfy the check while the default offered
    # `.mcr` alone, which is exactly the state this assertion exists to catch.
    default = r.get("card_filter", "").split(";;")[0]
    missing = [e for e in (".mcr", ".mcd", ".gme") if e not in default]
    if missing:
        bad.append(f"the file dialogs open on a filter that does not offer "
                   f"{', '.join(missing)}: {default!r}")

    if r["asked_from_button"] != 1:
        bad.append(f"clicking the empty page's button reached the open path "
                   f"{r['asked_from_button']} time(s), not once -- the button "
                   f"and the menu item are not the same way in")
    if r["path_after_cancel"] is not None or not r["empty_after_cancel"]:
        bad.append(f"cancelling the dialog changed the window: path="
                   f"{r['path_after_cancel']}, empty={r['empty_after_cancel']}")

    # A file that is not a card leaves the window alive and still offering the
    # way in. The refusal is the core's and says why; what would be new damage
    # is a window that ate it and then had nothing to click.
    if not r["refusal_raised"]:
        bad.append("a file that is not a memory card was accepted")
    if r["path_after_refusal"] is not None or not r["empty_after_refusal"]:
        bad.append(f"a refused file left the window holding "
                   f"{r['path_after_refusal']}, empty="
                   f"{r['empty_after_refusal']}")
    if r["asked_after_refusal"] != 2:
        bad.append(f"after a refusal the button reached the open path "
                   f"{r['asked_after_refusal'] - 1} more time(s), not once")

    if not r.get("with_card"):
        return bad

    if r["asked_from_menu"] != 1 or r["path_after_open"] != r["card"]:
        bad.append(f"the menu item did not open the card the dialog named: "
                   f"{r['path_after_open']} for {r['card']}")
    if r["empty_after_open"]:
        bad.append("the window kept the empty page after opening a card")
    if not all(r["writable_after_open"]):
        bad.append(f"the save actions stayed disabled with a card open: "
                   f"{r['writable_after_open']}")

    if not r["dirty_after_edit"]:
        bad.append("editing through the form left the window clean, so the "
                   "discard question below proves nothing")
    if r["confirmed_while_dirty"] != 1:
        bad.append(f"opening another card with unsaved edits asked for "
                   f"confirmation {r['confirmed_while_dirty']} time(s), "
                   f"not once")
    if r["asked_while_dirty"] != 0:
        bad.append("the file dialog opened even though the discard was "
                   "refused -- the guard runs after the question, not before")
    if not r["dirty_after_refusal"]:
        bad.append("refusing the discard threw the edits away anyway")
    if r["asked_after_confirm"] != 1 or r["dirty_after_confirm"]:
        bad.append(f"accepting the discard asked for a card "
                   f"{r['asked_after_confirm']} time(s) and left "
                   f"dirty={r['dirty_after_confirm']}")
    return bad


def _plant_open(python: str, card: str, env: dict, name: str, old: str,
                new: str) -> tuple[bool, str]:
    """The same substitution machinery, judged by `_judge_open`."""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, old, new, where=OPEN_BREAK_FILE)
        if sandbox is None:
            return False, why
        source = os.path.join(tmp, "open.mcr")
        shutil.copyfile(card, source)
        r, output = _run_open(python, os.path.join(sandbox, "ui", "app.py"),
                              source, env)
        if r is None:
            return False, (f"the planted probe for {name} did not run, so "
                           f"nothing was proved:\n{output.rstrip()}")
        bad = _judge_open(r)
        if not bad:
            return False, (f"{OPEN_BREAK_FILE} :: {name} was broken "
                           f"({old.strip()} -> {new.strip()}) and the gate "
                           f"still passed")
        return True, bad[0]


def open_probe(python: str, env: dict) -> int:
    """The MCR-TASK-15 half: the window comes up, and it is the way in.

    Runs with or without a fixture. Without one it still measures the empty
    window, its button and the cancelled dialog; with one it also measures
    opening and the discard guard, and plants the two red cases.
    """
    card = env.get(mcrio.CARD_ENV)
    with tempfile.TemporaryDirectory() as tmp:
        source = None
        if card and os.path.isfile(card):
            source = os.path.join(tmp, "open.mcr")
            shutil.copyfile(card, source)
        r, output = _run_open(python, APP, source, env)
        if r is None:
            print(output.rstrip())
            print(f"FAIL: {APP} --open-probe did not report")
            return 1
        bad = _judge_open(r)
        print(f"open: the window came up with no card, showing the empty page "
              f"and a {r['button_text']!r} button behind "
              f"{r['open_text'].replace('&', '')} "
              f"({r['open_shortcut']}); cancelling changed nothing")
        print(f"open: a file that is not a card was refused "
              f"({r.get('refusal', '')[:52]}...) and the window stayed empty "
              f"and still opened on the next click")
        if r.get("with_card"):
            print(f"open: the dialog named a card and the window opened it, "
                  f"and an unsaved edit survived a refused discard "
                  f"(asked={r['asked_while_dirty']}, "
                  f"confirmed={r['confirmed_while_dirty']})")
        else:
            print(f"note: no {mcrio.CARD_ENV}, so the open probe stopped "
                  f"after the empty window")
        if bad:
            for line in bad:
                print(f"FAIL: {line}")
            return 1

    if not (card and os.path.isfile(card)):
        return 0
    failed = 0
    for name, old, new in OPEN_BREAKS:
        red, why = _plant_open(python, card, env, name, old, new)
        if red:
            print(f"negative: breaking {name} reddens the gate -- {why}")
            PLANTED.append(name)
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

    if negative_probe(python, card, env):
        return 1
    return outside_probe(python, card, env)


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
        # The open step runs with or without a fixture -- what it measures
        # first is a window with no card, which is exactly the machine that
        # has none.
        if open_probe(python, env):
            return 1
        code = write_probe(python, env)
    except subprocess.TimeoutExpired as e:
        print(f"FAIL: {e.cmd[1] if len(e.cmd) > 1 else APP} did not exit "
              f"within {TIMEOUT}s")
        return 1
    if code == 0 and PLANTED:
        print(f"ui negative controls: {len(PLANTED)} of {PLANTED_TOTAL} red")
    return code


if __name__ == "__main__":
    sys.exit(main())

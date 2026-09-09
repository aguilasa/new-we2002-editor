#!/usr/bin/env python3
"""The entry point of the Qt shell. Run it with the venv's python.

Rule 3: this file imports `model` and its own siblings. No address, no
container.

`--smoke` IS A CONTRACT, not a convenience. `tools/mcr/ui_check.py` -- the
`mcr_ui` target of MCR-TASK-10 -- runs exactly `app.py --smoke`: the window
opens, Qt paints one frame, and the process exits 0 without waiting for
anybody. Without it the gate would need `xdotool` and a timeout to decide
whether a window ever appeared.

`--write-probe` IS THE SECOND CONTRACT, and MCR-TASK-12's. It drives the real
widgets -- a spin box, a combo, a line edit and a genuine press-move-release on
the pitch -- and writes two files through the window's own Save. It ASSERTS
NOTHING about bytes: it reports what it did as JSON on stdout, and `ui_check.py`
is what judges, because judging needs `layout` and `mcrio` and Rule 3 keeps
both out of this directory. The screen measures, the gate decides.

The drag is sent as real `QMouseEvent`s rather than by calling the handler,
because the part under test is the whole path: hit detection, the grab offset,
and the division by the two screen factors. A probe that called the model
directly would prove nothing about the screen.

AND THE GATE NAMES THE DESTINATION, IN THE CARD'S OWN UNITS (`--drag-to X,Y`).
The first version of this probe pushed a marker by a fixed number of pixels and
reported where the model said it ended up -- which is the OUTPUT of the
conversion under test, handed to a judge that compared it against itself.
CORR-MCR-018 measured the cost: with the division removed from `to_card_x` the
gate stayed green and printed `[48, 43]` "in the card's own units" as
confidently as it prints the right answer. Now the screen is told where to land
and the judge asks whether it did.

`--open-probe` IS THE THIRD CONTRACT, and MCR-TASK-15's. It brings the window
up WITHOUT a card and reports how it offers to open one: the empty page, the
button on it, the menu item behind both, and what happens when the dialog is
cancelled, when it names a card, and when there are unsaved edits. It never
opens a real dialog -- it replaces `MainWindow._ask_for_card` and
`_confirm_discard`, the two seams that exist for this -- because a modal in a
gate hangs until the timeout instead of failing. Like the other two probes it
asserts nothing: `ui_check.py` judges.

THE DISPLAY IS `:98`. `:1` is the user's real session and a window there
interrupts them; the rule is in `CLAUDE.md` and has no exception in this cycle.
`make mcr-98` sets it, and so does `ui_check.py`.

Usage:

    make mcr-98
    work/venv-mcr/bin/python tools/mcr/ui/app.py <card.mcr>
    work/venv-mcr/bin/python tools/mcr/ui/app.py --smoke
    work/venv-mcr/bin/python tools/mcr/ui/app.py <card.mcr> --screenshot out.png
    work/venv-mcr/bin/python tools/mcr/ui/app.py <copy.mcr> \
        --write-probe DIR --drag-to 14,43
    work/venv-mcr/bin/python tools/mcr/ui/app.py --open-probe \
        --open-with <copy.mcr>
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attributes                                        # noqa: E402
import formation_view                                    # noqa: E402
from PySide6 import QtCore, QtGui, QtWidgets             # noqa: E402
from main_window import MainWindow                       # noqa: E402

CARD_ENV = "WE2002_MCR_CARD"
PROBE_SLOT = 0
PROBE_FIELD = "technique"
PROBE_NAME = "PROBE"
PROBE_ROLE = 5


def _settle(app: QtWidgets.QApplication, window: QtWidgets.QMainWindow,
            frames: int = 5) -> None:
    """Let Qt actually paint, instead of trusting that show() did it."""
    window.show()
    for _ in range(frames):
        app.processEvents()


def _other_value(field: str, current: int) -> int:
    """A legal value of `field` that is not the one already there."""
    f = attributes.BY_NAME[field]
    return f.low if current != f.low else f.high


def _drag(app, pitch, index: int, target: tuple[int, int]) -> list[float]:
    """A real press, move and release, landing marker `index` on `target`.

    `target` is in the CARD's units and comes from the caller, so nothing the
    conversion computes is used to decide where the mouse goes. Returns the
    widget-space displacement, for the report.
    """
    start = pitch.marker_point(index)
    end = pitch.point_for(*target)
    left = QtCore.Qt.MouseButton.LeftButton
    none = QtCore.Qt.KeyboardModifier.NoModifier
    for kind, point, button, buttons in (
            (QtCore.QEvent.Type.MouseButtonPress, start, left, left),
            (QtCore.QEvent.Type.MouseMove, end, QtCore.Qt.MouseButton.NoButton,
             left),
            (QtCore.QEvent.Type.MouseButtonRelease, end, left,
             QtCore.Qt.MouseButton.NoButton)):
        event = QtGui.QMouseEvent(kind, point, pitch.mapToGlobal(point),
                                  button, buttons, none)
        QtWidgets.QApplication.sendEvent(pitch, event)
        app.processEvents()
    return [end.x() - start.x(), end.y() - start.y()]


def report_formation(window) -> dict:
    """What the six set-piece boxes SHOW, next to what the card holds.

    The gate needs both halves from the same run, and it needs the SHOWN one to
    come off the widget rather than off the model -- CORR-MCR-020 is exactly a
    case where the two disagreed and every other measurement stayed green. The
    suffix travels too: a box may report an out-of-domain value by carrying it
    as text instead of as its number, and either is an answer.
    """
    view = window.formation
    f = window.save.formation
    return {
        "card": {"captain": f.captain, "kickers": list(f.kickers)},
        "shown": {
            "captain": view.captain.value(),
            "kickers": [s.value() for s in view.kickers],
        },
        "suffix": {
            "captain": view.captain.suffix(),
            "kickers": [s.suffix() for s in view.kickers],
        },
        "tooltip": {
            "captain": view.captain.toolTip(),
            "kickers": [s.toolTip() for s in view.kickers],
        },
    }


def write_probe(app, window, out_dir: str,
                drag_to: tuple[int, int]) -> dict:
    """Drive the widgets, write two cards, and report what was done.

    Two files on purpose. The first carries ONE attribute change, so the gate
    can demand that the bytes which moved are the bytes of that player's
    record and nothing else -- the end-to-end edit of the task. The second
    carries the rest, so the round-trip is asked about a card the screen edited
    in every way it can.
    """
    os.makedirs(out_dir, exist_ok=True)
    save = window.save
    player = save.players[PROBE_SLOT]
    form = window.squad.form
    window.squad.list.setCurrentRow(PROBE_SLOT)
    app.processEvents()

    report = {"slot": PROBE_SLOT, "field": PROBE_FIELD}

    # 1 -- one attribute, through the spin box, saved with the default Save.
    wanted = _other_value(PROBE_FIELD, player.attributes[PROBE_FIELD])
    form.editor(PROBE_FIELD).setValue(wanted)
    app.processEvents()
    report["attribute"] = wanted
    report["dirty_after_edit"] = window.dirty
    one = window.save_copy()
    report["one_attribute"] = one
    report["dirty_after_save"] = window.dirty

    # 2 -- everything else the screen can change.
    form.name.setText(PROBE_NAME)
    form.name.editingFinished.emit()
    number = 1 if player.shirt_number != 1 else 2
    form.number.setValue(number)
    app.processEvents()
    report["name"] = PROBE_NAME
    report["number"] = number

    formation = save.formation
    before = (formation.x[0], formation.y[0])
    pixels = _drag(app, window.formation.pitch, 0, drag_to)
    report["xy_before"] = list(before)
    report["drag_to"] = list(drag_to)
    report["xy_after"] = [formation.x[0], formation.y[0]]
    # The stimulus, so the judge can say what the conversion should have done
    # instead of only that it disagreed.
    report["drag_pixels"] = pixels
    report["scales"] = [formation_view.X_SCALE, formation_view.Y_SCALE]

    window.formation.roles[0].setCurrentIndex(PROBE_ROLE)
    kicker = 1 if formation.kickers[0] != 1 else 2
    window.formation.kickers[0].setValue(kicker)
    # The captain became editable in MCR-TASK-13; before it, the byte was read
    # and never written, so this is the one field whose write path is newer
    # than the probe that exercises it.
    captain = 2 if formation.captain != 2 else 3
    window.formation.captain.setValue(captain)
    app.processEvents()
    report["role"] = PROBE_ROLE
    report["kicker"] = kicker
    report["captain"] = captain

    full = window.save_as(os.path.join(out_dir, "full.mcr"))
    report["full"] = full
    report["copy_target_differs"] = bool(one) and one != window.path
    return report


def open_probe(app, window, card: str | None) -> dict:
    """How the empty window offers to open a card. Reports; judges nothing.

    The two modals of that path are replaced here rather than driven: a
    `QFileDialog` is modal and may be native, so clicking through one would
    hang this process until the gate's timeout. What is under test is the
    wiring around them -- that the button reaches the same action as the menu
    item, that cancelling changes nothing, that a named card opens, and that
    unsaved edits are not thrown away without a question -- and the seams let
    all of it run with no dialog on screen.
    """
    asked: list[str] = []
    confirmed: list[bool] = []

    def seam(answer: str):
        def ask() -> str:
            asked.append(answer)
            return answer
        return ask

    def confirm(answer: bool):
        def ask() -> bool:
            confirmed.append(answer)
            return answer
        return ask

    report = {
        "card": card,
        "path": window.path,
        "save_is_none": window.save is None,
        "empty_shown": window.showing_empty,
        "button_text": window.open_button.text(),
        "button_visible": window.open_button.isVisible(),
        "open_enabled": window.act_open.isEnabled(),
        "open_shortcut": window.act_open.shortcut().toString(),
        "open_text": window.act_open.text(),
        "writable": [a.isEnabled() for a in (window.act_save,
                                             window.act_save_as,
                                             window.act_overwrite)],
    }

    # 1 -- the button, with the dialog cancelled. Nothing may change.
    window._ask_for_card = seam("")
    window.open_button.click()
    app.processEvents()
    report["asked_from_button"] = len(asked)
    report["path_after_cancel"] = window.path
    report["empty_after_cancel"] = window.showing_empty

    # 1b -- a file that is not a card. The refusal itself is MCR-TASK-11's and
    # unchanged; what this measures is that the window SURVIVES one -- still on
    # the empty page, still holding nothing, still offering the button. The
    # modal it would show is the seam-less half of that path, and a headless
    # run raises instead of opening it, which is why this call is wrapped.
    try:
        window.open(__file__)
        report["refusal_raised"] = False
    except Exception as e:                                # noqa: BLE001
        report["refusal_raised"] = True
        report["refusal"] = str(e)[:80]
    app.processEvents()
    report["path_after_refusal"] = window.path
    report["empty_after_refusal"] = window.showing_empty
    window._ask_for_card = seam("")
    window.open_button.click()
    app.processEvents()
    report["asked_after_refusal"] = len(asked)

    if not card:
        report["with_card"] = False
        return report
    report["with_card"] = True

    # 2 -- the menu item, with the dialog naming a card. Every count from here
    # down is a DELTA: the steps above already asked twice, and an absolute
    # total would have to be updated by whoever adds a step in between.
    before = len(asked)
    window._ask_for_card = seam(card)
    window.act_open.trigger()
    app.processEvents()
    report["asked_from_menu"] = len(asked) - before
    report["path_after_open"] = window.path
    report["empty_after_open"] = window.showing_empty
    report["writable_after_open"] = [a.isEnabled() for a in (
        window.act_save, window.act_save_as, window.act_overwrite)]

    # 3 -- an edit that is in no file, and a discard that is refused.
    field = window.squad.form.editor(PROBE_FIELD)
    field.setValue(_other_value(PROBE_FIELD,
                                window.save.players[PROBE_SLOT]
                                .attributes[PROBE_FIELD]))
    app.processEvents()
    report["dirty_after_edit"] = window.dirty
    before = len(asked)  # noqa: F841 -- rebound for the next delta
    window._confirm_discard = confirm(False)
    window._ask_for_card = seam(card)
    window.act_open.trigger()
    app.processEvents()
    report["asked_while_dirty"] = len(asked) - before
    report["confirmed_while_dirty"] = len(confirmed)
    report["dirty_after_refusal"] = window.dirty

    # 4 -- and a discard that is accepted.
    before = len(asked)
    window._confirm_discard = confirm(True)
    window.act_open.trigger()
    app.processEvents()
    report["asked_after_confirm"] = len(asked) - before
    report["dirty_after_confirm"] = window.dirty
    return report


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?",
                    help="a .mcr to open; the file dialog opens one otherwise")
    ap.add_argument("--smoke", action="store_true",
                    help="open the window, paint one frame, exit 0")
    ap.add_argument("--screenshot", metavar="PNG",
                    help="save the window as a PNG and exit")
    ap.add_argument("--tab", type=int, default=0,
                    help="which tab to show before the screenshot")
    ap.add_argument("--write-probe", metavar="DIR",
                    help="edit through the widgets, write DIR/*.mcr, and "
                         "report what was done as JSON")
    ap.add_argument("--report-formation", action="store_true",
                    help="open the card and report what the six set-piece "
                         "boxes SHOW, as JSON, next to what the card holds")
    ap.add_argument("--open-probe", action="store_true",
                    help="bring the window up with no card and report how it "
                         "offers to open one, as JSON")
    ap.add_argument("--open-with", metavar="MCR",
                    help="the card the file-dialog seam names during "
                         "--open-probe; without it the probe stops after the "
                         "empty window")
    ap.add_argument("--drag-to", metavar="X,Y",
                    help="where the drag must land, in the card's own units; "
                         "required by --write-probe, and chosen by the gate "
                         "so that the screen supplies neither the answer nor "
                         "the rule")
    a = ap.parse_args(argv)

    app = QtWidgets.QApplication(sys.argv[:1])
    window = MainWindow()
    # No modal may open in a gate: a QMessageBox spins its own event loop and
    # the run would hang until the timeout, reporting "did not exit" instead
    # of the refusal that caused it.
    window.headless = bool(a.smoke or a.screenshot or a.write_probe
                           or a.report_formation or a.open_probe)

    # In smoke and screenshot runs the card may come from the variable, so the
    # gate exercises a real read when the machine has a card and still opens an
    # empty window when it does not.
    path = a.card or (os.environ.get(CARD_ENV)
                      if (a.smoke or a.screenshot) else None)
    opened = False
    if path and os.path.isfile(path):
        opened = window.open(path)

    if a.open_probe:
        _settle(app, window)
        print("open-json " + json.dumps(open_probe(app, window, a.open_with)))
        return 0

    if a.report_formation:
        if not opened:
            print("report-formation: give a card to open", file=sys.stderr)
            return 2
        _settle(app, window)
        print("formation-json " + json.dumps(report_formation(window)))
        return 0

    if a.write_probe:
        if not opened:
            print("write-probe: give a card to open", file=sys.stderr)
            return 2
        if not a.drag_to:
            print("write-probe: --drag-to X,Y is required -- the destination "
                  "is the gate's to choose", file=sys.stderr)
            return 2
        try:
            x, y = (int(v) for v in a.drag_to.split(","))
        except ValueError:
            print(f"write-probe: --drag-to {a.drag_to!r} is not X,Y",
                  file=sys.stderr)
            return 2
        _settle(app, window)
        print("probe-json " + json.dumps(write_probe(app, window,
                                                     a.write_probe, (x, y))))
        return 0

    if a.screenshot:
        window.tabs.setCurrentIndex(a.tab)
        _settle(app, window)
        if not window.grab().save(a.screenshot):
            print(f"could not write {a.screenshot}", file=sys.stderr)
            return 1
        print(f"wrote {a.screenshot}"
              + (f" with {os.path.basename(path)}" if opened else " (no card)"))
        return 0

    if a.smoke:
        _settle(app, window)
        visible = window.isVisible()
        print(f"smoke: window {'up' if visible else 'NOT up'}, "
              f"card {'loaded' if opened else 'not loaded'}, "
              f"platform {app.platformName()}")
        return 0 if visible else 1

    # The window comes up whether or not there is a card, and opening one is
    # an action of the window (MCR-TASK-15). This used to be `if not path:
    # window.choose()`, which put a modal file dialog on screen before there
    # was a window to own it, and left nothing visible when it was cancelled.
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

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

THE DISPLAY IS `:98`. `:1` is the user's real session and a window there
interrupts them; the rule is in `CLAUDE.md` and has no exception in this cycle.
`make mcr-98` sets it, and so does `ui_check.py`.

Usage:

    make mcr-98
    work/venv-mcr/bin/python tools/mcr/ui/app.py <card.mcr>
    work/venv-mcr/bin/python tools/mcr/ui/app.py --smoke
    work/venv-mcr/bin/python tools/mcr/ui/app.py <card.mcr> --screenshot out.png
    work/venv-mcr/bin/python tools/mcr/ui/app.py <copy.mcr> --write-probe DIR
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
PROBE_DRAG = 40          # widget pixels, towards the room the marker has


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


def _drag(app, pitch, index: int, dx: float, dy: float) -> None:
    """A real press, move and release on the pitch widget."""
    start = pitch.marker_point(index)
    end = QtCore.QPointF(start.x() + dx, start.y() + dy)
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


def write_probe(app, window, out_dir: str) -> dict:
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
    room = formation_view.X_MAX / 2
    _drag(app, window.formation.pitch, 0,
          PROBE_DRAG if formation.x[0] < room else -PROBE_DRAG, PROBE_DRAG)
    report["xy_before"] = list(before)
    report["xy_after"] = [formation.x[0], formation.y[0]]

    window.formation.roles[0].setCurrentIndex(PROBE_ROLE)
    kicker = 1 if formation.kickers[0] != 1 else 2
    window.formation.kickers[0].setValue(kicker)
    app.processEvents()
    report["role"] = PROBE_ROLE
    report["kicker"] = kicker

    full = window.save_as(os.path.join(out_dir, "full.mcr"))
    report["full"] = full
    report["copy_target_differs"] = bool(one) and one != window.path
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
    a = ap.parse_args(argv)

    app = QtWidgets.QApplication(sys.argv[:1])
    window = MainWindow()
    # No modal may open in a gate: a QMessageBox spins its own event loop and
    # the run would hang until the timeout, reporting "did not exit" instead
    # of the refusal that caused it.
    window.headless = bool(a.smoke or a.screenshot or a.write_probe)

    # In smoke and screenshot runs the card may come from the variable, so the
    # gate exercises a real read when the machine has a card and still opens an
    # empty window when it does not.
    path = a.card or (os.environ.get(CARD_ENV)
                      if (a.smoke or a.screenshot) else None)
    opened = False
    if path and os.path.isfile(path):
        opened = window.open(path)

    if a.write_probe:
        if not opened:
            print("write-probe: give a card to open", file=sys.stderr)
            return 2
        _settle(app, window)
        print("probe-json " + json.dumps(write_probe(app, window,
                                                     a.write_probe)))
        return 0

    if a.screenshot:
        window.centralWidget().setCurrentIndex(a.tab)
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

    if not path:
        window.choose()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

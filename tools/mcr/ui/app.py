#!/usr/bin/env python3
"""The entry point of the Qt shell. Run it with the venv's python.

Rule 3: this file imports `model` and its own siblings. No address, no
container.

`--smoke` IS A CONTRACT, not a convenience. `tools/mcr/ui_check.py` -- the
`mcr_ui` target of MCR-TASK-10 -- runs exactly `app.py --smoke`: the window
opens, Qt paints one frame, and the process exits 0 without waiting for
anybody. Without it the gate would need `xdotool` and a timeout to decide
whether a window ever appeared.

THE DISPLAY IS `:98`. `:1` is the user's real session and a window there
interrupts them; the rule is in `CLAUDE.md` and has no exception in this cycle.
`make mcr-98` sets it, and so does `ui_check.py`.

Usage:

    make mcr-98
    work/venv-mcr/bin/python tools/mcr/ui/app.py <card.mcr>
    work/venv-mcr/bin/python tools/mcr/ui/app.py --smoke
    work/venv-mcr/bin/python tools/mcr/ui/app.py <card.mcr> --screenshot out.png
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PySide6 import QtWidgets                            # noqa: E402
from main_window import MainWindow                       # noqa: E402

CARD_ENV = "WE2002_MCR_CARD"


def _settle(app: QtWidgets.QApplication, window: QtWidgets.QMainWindow,
            frames: int = 5) -> None:
    """Let Qt actually paint, instead of trusting that show() did it."""
    window.show()
    for _ in range(frames):
        app.processEvents()


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
    a = ap.parse_args(argv)

    app = QtWidgets.QApplication(sys.argv[:1])
    window = MainWindow()

    # In smoke and screenshot runs the card may come from the variable, so the
    # gate exercises a real read when the machine has a card and still opens an
    # empty window when it does not.
    path = a.card or (os.environ.get(CARD_ENV)
                      if (a.smoke or a.screenshot) else None)
    opened = False
    if path and os.path.isfile(path):
        opened = window.open(path)

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

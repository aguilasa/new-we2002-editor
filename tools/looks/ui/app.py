#!/usr/bin/env python3
"""The entry point of the window.  Run it with the venv's python.

Rule 3 (plan section 3.3): this file imports `scene` and its own sibling, and
neither an address nor a disc reader.  `scene.from_image` is the whole path
from an image on disc to points and pixels, and it lives in the core because
the core is where a check can run it without a display.

**NOTHING OPENS ON THE USER'S SCREEN.**  The window is parked off the desktop
before it is shown -- the `-32000` of `CLAUDE.md` on Windows -- and on Linux the
display is `:98`, set by whoever runs this.  `--visible` exists for the one case
the rule allows, which is the user asking to look, and it is not what a gate
runs.

`--smoke` IS A CONTRACT.  It brings the window up, lets Qt paint a frame and
exits 0, printing what it drew.  `tools/looks/ui_check.py` -- the `looks_ui`
target, which is LOOKS-TASK-16 -- is what judges; this reports.

`--screenshot` is the other half, and the reason the report carries numbers: a
run that drew nothing and a run that drew a figure both write a PNG, and only
the counts and the picture tell them apart.

Usage:
    <venv>/python tools/looks/ui/app.py --smoke
    <venv>/python tools/looks/ui/app.py --looks A-I3-A-F-A --screenshot out.png
    <venv>/python tools/looks/ui/app.py --looks A-A1-A-A-A --wireframe \\
        --screenshot wire.png
    <venv>/python tools/looks/ui/app.py --compare one.png two.png
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import scene as core  # noqa: E402
from PySide6 import QtCore, QtGui, QtWidgets  # noqa: E402
import viewer as viewer_module  # noqa: E402
from viewer import Viewer  # noqa: E402

OFF_THE_DESKTOP = -32000  # not-an-address: the parking spot CLAUDE.md names
DEFAULT_TUPLE = "A-A1-A-A-A"
DEFAULT_SIZE = (640, 640)
FRAMES = 5
"""Paints to let through before a picture is taken.

Five and not one: `show()` schedules a paint, it does not perform one, and a
grab taken on the way to the first frame comes back as the clear colour -- a
picture of nothing that saves without complaint.
"""


def _size(text: str) -> tuple:
    parts = text.lower().split("x")
    if len(parts) != 2:
        raise argparse.ArgumentTypeError("a size is WIDTHxHEIGHT, like 640x640")
    return (int(parts[0]), int(parts[1]))


def _report(view: Viewer, drawn) -> dict:
    """What was drawn, as numbers -- the gate's input and the log's."""
    numbers = core.summary(drawn)
    print("  %s, figure %d: %d primitive(s), %d textured, %d surface(s), "
          "%d triangle(s)"
          % (numbers["tuple"], numbers["figure"], numbers["parts"],
             numbers["textured"], numbers["surfaces"], numbers["triangles"]))
    print("  sections %d, shelf %s, wireframe %s, camera yaw %.0f pitch %.0f"
          % (numbers["sections"], "on" if view.shelved else "off",
             "on" if view.wireframe else "off", view.yaw, view.pitch))
    for name, count in sorted(numbers["notes"].items()):
        if count:
            print("  not textured -- %s: %d" % (name, count))
    return numbers


def _park(window: QtWidgets.QWidget, visible: bool) -> None:
    """Put the window where the user is not, unless the user asked to see it."""
    if visible:
        window.show()
        return
    window.setAttribute(QtCore.Qt.WidgetAttribute.WA_ShowWithoutActivating,
                        True)
    window.move(OFF_THE_DESKTOP, OFF_THE_DESKTOP)
    window.show()
    # Moved again after show(), because a window manager may place it on map
    # and Qt's own move before show is only a request.
    window.move(OFF_THE_DESKTOP, OFF_THE_DESKTOP)


def _settle(app: QtWidgets.QApplication, window: QtWidgets.QWidget,
            frames: int = FRAMES) -> None:
    for _ in range(frames):
        app.processEvents()
        window.repaint()


def _compare(first: str, second: str) -> int:
    """How much two pictures differ, in pixels and in percent.

    Here rather than in the core because loading a PNG is Qt's job in this
    tree, and because the pair this answers for -- two tuples, two pictures --
    is the phase's own question: a viewer that ignored the tuple would write
    two identical files and pass every other check in this file.
    """
    pictures = []
    for path in (first, second):
        image = QtGui.QImage()
        if not image.load(path):
            print("could not read %s" % path, file=sys.stderr)
            return 2
        pictures.append(image.convertToFormat(
            QtGui.QImage.Format.Format_RGBA8888))
    one, two = pictures
    if one.size() != two.size():
        print("%s is %dx%d and %s is %dx%d"
              % (first, one.width(), one.height(), second, two.width(),
                 two.height()))
        return 1
    differ = 0
    for y in range(one.height()):
        for x in range(one.width()):
            if one.pixel(x, y) != two.pixel(x, y):
                differ += 1
    total = one.width() * one.height()
    print("%s vs %s: %d of %d pixel(s) differ (%.2f%%)"
          % (os.path.basename(first), os.path.basename(second), differ, total,
             100.0 * differ / total))
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--looks", default=DEFAULT_TUPLE,
                        help="the tuple to draw, like A-I3-A-F-A")
    parser.add_argument("--figure", type=int, default=0,
                        help="0 is the outfield player, 1 the goalkeeper")
    parser.add_argument("--image", help="the Japanese data track; the "
                                        "environment names it otherwise")
    parser.add_argument("--smoke", action="store_true",
                        help="paint one frame, report, and exit 0")
    parser.add_argument("--screenshot", metavar="PNG")
    parser.add_argument("--compare", nargs=2, metavar=("ONE", "TWO"),
                        help="how much two pictures differ")
    parser.add_argument("--size", type=_size, default=DEFAULT_SIZE)
    parser.add_argument("--wireframe", action="store_true")
    parser.add_argument("--no-shelf", action="store_true",
                        help="draw every piece in the file's own coordinates, "
                             "where they all sit on the origin")
    parser.add_argument("--yaw", type=float, default=viewer_module.FRONT,
                        help="degrees around the figure; the default faces it")
    parser.add_argument("--pitch", type=float, default=0.0)
    parser.add_argument("--piece", choices=("all", "head"), default="all",
                        help="head draws the section the tuple actually "
                             "changes, and nothing else")
    parser.add_argument("--visible", action="store_true",
                        help="show the window where the user can see it")
    args = parser.parse_args(argv)

    app = QtWidgets.QApplication(sys.argv[:1])

    if args.compare:
        return _compare(*args.compare)

    image = args.image
    if not image:
        try:
            image = core.image_from_env()
        except RuntimeError as exc:
            print("app: skipped -- %s" % exc)
            return core.SKIP
    try:
        drawn = core.from_image(image, args.looks, args.figure)
    except core.BadScene as exc:
        print("app: %s refuses -- %s" % (args.looks, exc))
        return 2
    if args.piece == "head":
        drawn = core.head_only(drawn)

    view = Viewer(drawn)
    view.shelved = not args.no_shelf
    view.wireframe = args.wireframe
    view.yaw, view.pitch = args.yaw, args.pitch
    view.set_scene(drawn)
    view.resize(*args.size)
    view.setWindowTitle("looks %s" % args.looks)
    _park(view, args.visible)
    _settle(app, view)
    _report(view, drawn)

    if args.screenshot:
        picture = view.grabFramebuffer()
        if not picture.save(args.screenshot):
            print("could not write %s" % args.screenshot, file=sys.stderr)
            return 1
        print("  wrote %s, %dx%d"
              % (args.screenshot, picture.width(), picture.height()))
    if args.smoke or args.screenshot:
        print("  window %s, off the desktop at %d,%d"
              % ("up" if view.isVisible() else "NOT up", view.x(), view.y()))
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())

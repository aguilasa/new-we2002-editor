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

## Two modes, and the screen is the default

Without `--looks` this opens the **LOOKS SET screen** of the game -- the twelve
rows, the cursor, the help box -- starting from what a save state shows, which
is LOOKS-TASK-22.  With `--looks TUPLE` it opens the plain viewer of
LOOKS-TASK-15, one tuple and an orbital camera, which is what the colour pairs
of `ui_check.py` are drawn with.

`--keys Down,Right,Right` presses buttons into the screen before reporting, as
**Qt key events**, which is the path a keyboard takes: a gate that called
`press()` directly would leave `keyPressEvent` untested and pass on a window
nobody could type into.  A part may carry a count -- `Right x41` is forty-one
Rights, the one repetition form `screen.parse_keys` takes (CORR-LOOKS-082), and
what keeps a sequence that walks a row to its end from being spelled out.

Usage:
    <venv>/python tools/looks/ui/app.py --smoke
    <venv>/python tools/looks/ui/app.py --state 1 --visible
    <venv>/python tools/looks/ui/app.py --keys "Down x6,Right x41" \\
        --screenshot out.png
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
from looks_set import KEYS, LooksSet, SCALE  # noqa: E402

OFF_THE_DESKTOP = -32000  # not-an-address: the parking spot CLAUDE.md names
DEFAULT_TUPLE = "A-A1-A-A-A"
DEFAULT_STATE = 2
"""The outfield player's state.  Slot 1 is the goalkeeper, and the plate on the
screen -- `CB` against `GK` -- is the difference the walk measured."""
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
    # Two kinds of note, and they are not the same statement.  "no image",
    # "no palette" and "off the record" say a part came out UNTEXTURED; the
    # others say it was textured from something this cycle has not measured.
    # Printing both under "not textured" was true of the first three and false
    # of the rest (CORR-LOOKS-028's band, CORR-LOOKS-034's borrowed index).
    untextured = ("no image", "no palette", "off the record")
    for name, count in sorted(numbers["notes"].items()):
        if not count:
            continue
        if name in untextured:
            print("  not textured -- %s: %d" % (name, count))
        else:
            print("  textured, but %s: %d" % (name, count))
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


def _send_keys(app: QtWidgets.QApplication, window: LooksSet,
               buttons: list) -> list:
    """The buttons into the window as Qt key events, and what each one moved.

    `sendEvent`, not a call to `press`: the keyboard is the interface this task
    is about, and a gate that skipped `keyPressEvent` would pass on a window
    that never bound the arrows to anything.  One press at a time, with the
    events drained after each -- the rule of CLAUDE.md that a key fired in a
    loop lands somewhere nobody meant.
    """
    where = {name: key for key, name in KEYS.items()}
    moved = []
    for button in buttons:
        key = where[button]
        for kind in (QtCore.QEvent.Type.KeyPress,
                     QtCore.QEvent.Type.KeyRelease):
            event = QtGui.QKeyEvent(kind, key,
                                    QtCore.Qt.KeyboardModifier.NoModifier)
            # The label position counts: Left on DEFAUL moves the cursor to
            # the row's name and changes no text (CORR-LOOKS-067).
            before = (window.state.texts(), window.state.row,
                      window.state.on_label)
            app.sendEvent(window, event)
            if kind == QtCore.QEvent.Type.KeyPress:
                moved.append((window.state.texts(), window.state.row,
                              window.state.on_label) != before)
        app.processEvents()
    return moved


def _screen_report(window: LooksSet, moved: list) -> dict:
    """What the screen shows, in the shape `ui_check.py` parses."""
    seen = window.report()
    print("screen: slot %s, cursor %s, help %r"
          % (seen["slot"], seen["cursor"], seen["help"]))
    print("  plate %s, shirt %r, title %r"
          % (seen["plate"], seen["shirt"], seen["title"]))
    for name in window.state.order:
        print("  row %-9s = %r" % (name, seen["rows"][name]))
    print("  tuple %s, scene built %d time(s)"
          % (seen["tuple"], seen["builds"]))
    if seen["refused"]:
        print("  refused: %s" % seen["refused"])
    if seen["sprites"]:
        print("  sprites %s" % ", ".join(
            "%s clut %d,%d" % (name, clut[0], clut[1])
            for name, clut in sorted(seen["sprites"].items())))
    else:
        print("  sprites none: %s" % seen["sprites_note"])
    print("  glyphs %s" % " ".join("%d,%d,%d,%d" % one
                                   for one in seen["glyphs"]))
    print("  camera %s" % seen["camera"])
    if seen["camera_note"]:
        print("  camera note: %s" % seen["camera_note"])
    print("  arrows %s" % (" ".join(
        "%s@%d,%d" % (one["side"], one["point"][0], one["point"][1])
        for one in seen["arrows"]) or "none"))
    if moved:
        print("  presses %s"
              % "".join("+" if one else "." for one in moved))
    return seen


def _screen(app: QtWidgets.QApplication, args) -> int:
    """The LOOKS SET screen: the window this task is about."""
    try:
        state = core.screen_state(args.state)
        buttons = core.screen_keys(args.keys) if args.keys else []
    except core.BadScreen as exc:
        print("app: %s" % exc, file=sys.stderr)
        return 2

    image = args.image
    if not image:
        try:
            image = core.image_from_env()
        except RuntimeError as exc:
            print("app: skipped -- %s" % exc)
            return core.SKIP
    # The panel opens with the figure ASSEMBLED, which is what LOOKS-TASK-27
    # delivers: `--frame` names another frame of the walk, and the shelf is
    # still there behind `S` for looking at one piece.
    builder = core.Builder(image, state.figure(),
                           core.REFERENCE_FRAME if args.frame is None
                           else args.frame)

    window = LooksSet(state, builder, args.scale)
    window.viewer.shelved = False
    # The panel draws with the camera the game projects with, when there is a
    # measured one on disc.  Without it the window says so and keeps the v1
    # orbit -- a projection invented here would look like a measurement.
    # HEIG and BODY live in that camera, as the figure's scale (LOOKS-TASK-29),
    # so the window asks for it again whenever either row moves.
    window.camera_for = lambda values, row: builder.panel_camera(
        window.drawn, int(state.slot), window.panel_native(), values, row)
    window.aim()
    if window.camera_note is None and window.viewer.game_camera is not None:
        print("  the panel draws with the game's own camera")
    else:
        print("  the panel keeps the v1 orbit: %s" % window.camera_note)
    window.setWindowTitle("LOOKS SET -- slot %s" % state.slot)
    _park(window, args.visible)
    _settle(app, window)
    window.setFocus()
    moved = _send_keys(app, window, buttons)
    _settle(app, window)

    if window.drawn is not None:
        _report(window.viewer, window.drawn)
    _screen_report(window, moved)

    if args.screenshot:
        picture = window.picture()
        if not picture.save(args.screenshot):
            print("could not write %s" % args.screenshot, file=sys.stderr)
            return 1
        print("  wrote %s, %dx%d"
              % (args.screenshot, picture.width(), picture.height()))
    if args.smoke or args.screenshot:
        print("  window %s, off the desktop at %d,%d"
              % ("up" if window.isVisible() else "NOT up", window.x(),
                 window.y()))
        return 0
    return app.exec()


def main(argv=None) -> int:
    try:  # The help of a row carries a button glyph this console cannot spell.
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, OSError):
        pass
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--looks", default=None,
                        help="the tuple to draw, like A-I3-A-F-A; without it "
                             "the LOOKS SET screen opens instead")
    parser.add_argument("--state", default=DEFAULT_STATE,
                        choices=("1", "2", 1, 2),
                        help="which save state the screen starts from: 1 is "
                             "the goalkeeper, 2 the outfield player")
    parser.add_argument("--keys", help="buttons to press first, like "
                                       "Down,Down,Right; a repetition is "
                                       "written Right x41")
    parser.add_argument("--scale", type=int, default=SCALE,
                        help="window pixels per game pixel")
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
    parser.add_argument("--frame", type=int, default=None,
                        help="pose the figure by this frame of the screen's "
                             "animation; without it the pieces sit on a shelf")
    parser.add_argument("--piece", choices=("all", "head"), default="all",
                        help="head draws the section the tuple actually "
                             "changes, and nothing else")
    parser.add_argument("--kit", default=None,
                        help="the kit container the body wears, by tag; "
                             "without it the one the save states showed")
    parser.add_argument("--visible", action="store_true",
                        help="show the window where the user can see it")
    args = parser.parse_args(argv)

    app = QtWidgets.QApplication(sys.argv[:1])

    if args.compare:
        return _compare(*args.compare)
    if args.looks is None:
        return _screen(app, args)

    image = args.image
    if not image:
        try:
            image = core.image_from_env()
        except RuntimeError as exc:
            print("app: skipped -- %s" % exc)
            return core.SKIP
    try:
        drawn = core.from_image(image, args.looks, args.figure,
                                args.frame, *((args.kit,) if args.kit
                                              else ()))
    except core.BadScene as exc:
        print("app: %s refuses -- %s" % (args.looks, exc))
        return 2
    if args.piece == "head":
        drawn = core.head_only(drawn)

    view = Viewer(drawn)
    # A posed scene carries its own places; shelving it would move the
    # pieces a second time.
    view.shelved = not args.no_shelf and args.frame is None
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

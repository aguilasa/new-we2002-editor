#!/usr/bin/env python3
"""The LOOKS SET screen as a window: twelve rows, the cursor, the help box.

Rule 3 (plan section 3.3) again, and it is the whole shape of this file: this
widget imports `scene` and Qt, and neither an address, nor a disc reader, nor
the module that holds the measured table.  **It decides nothing about the
screen.**  Where a press lands, what each value is called, which end locks and
which wraps, and what the help box says are all in `screen.State`, written by
`oracle.py --screen --write` off the running game (LOOKS-TASK-21); this draws
what the state says and sends it the four buttons.

That separation is what lets the gate judge: `ui_check.py` re-derives the walk
from `screen.py` and compares it against what this window prints.  If the
widget did its own arithmetic the two would agree by construction, and the
agreement would measure nothing.

## What is measured here and what is not

MEASURED, and taken from the table: the twelve rows and their order, the text
of every value, the help of every row, `Visual` in the box until the first
press, the plate and the shirt, the title the band DRAWS (`S SET`, not the
`LOOKS SET` its object holds -- CORR-LOOKS-054), and where every one of those
sits, in the display's own 512x240 pixels.

NOT measured, and therefore not claimed: the colours, the gradient of the
panel, the borders and the typeface.  Whether the scenery is an image off the
disc or polygons of the GPU is LOOKS-TASK-31, and until it is measured this
draws a plain arrangement rather than an imitation that would pass for one.

## Refusal is visible

A tuple the assembly table refuses -- `H1` hair is the measured case -- puts
the table's own sentence in the help box and leaves the panel EMPTY.  It does
not fall back to another style: drawing a head nobody asked for is the failure
the project exists not to commit (plan section 0, item 3).
"""

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

import scene as core
from viewer import Viewer

SCALE = 2
"""Display pixels per game pixel.  The screen is 512x240, so this is 1024x480."""

KEYS = {
    QtCore.Qt.Key.Key_Up: "Up",
    QtCore.Qt.Key.Key_Down: "Down",
    QtCore.Qt.Key.Key_Left: "Left",
    QtCore.Qt.Key.Key_Right: "Right",
}
"""The four buttons the screen answers to, and nothing else is forwarded."""

BACKGROUND = QtGui.QColor(0, 32, 48)
BOX = QtGui.QColor(150, 150, 150)
INK = QtGui.QColor(232, 232, 232)
DIM = QtGui.QColor(150, 160, 180)
CURSOR = QtGui.QColor(181, 181, 57)
REFUSED = QtGui.QColor(232, 120, 120)
PANEL = QtGui.QColor(12, 40, 96)


class LooksSet(QtWidgets.QWidget):
    """The screen, driven by the four buttons and redrawn on every change."""

    def __init__(self, state, builder=None, scale: int = SCALE, parent=None):
        super().__init__(parent)
        self.state = state
        self.builder = builder
        self.scale = scale
        self.places = state.layout()
        self.refusal: str | None = None
        self.builds = 0
        self.drawn = None
        self.tuple_text = state.tuple_text()
        # Where the game's camera comes from, handed in by whoever built the
        # window: a callable of the rows' values.  The window does not compose
        # it -- that is the core's (`scene.panel_camera`), and the camera is
        # where HEIG and BODY live (LOOKS-TASK-29).
        self.camera_for = None
        self.camera_note: str | None = None
        # The furniture the game draws, measured (LOOKS-TASK-31).  Without it
        # the window says so and keeps the colours the v2 chose by eye -- a
        # silent fallback would make the picture a description of itself.
        try:
            self.scenery = core.load_scenery(int(state.slot))
            self.scenery_note = None
        except core.BadScene as exc:
            self.scenery, self.scenery_note = [], str(exc)
        width, height = self.places["display"]
        self.setFixedSize(width * scale, height * scale)
        self.setFocusPolicy(QtCore.Qt.FocusPolicy.StrongFocus)

        self.viewer = Viewer(None, self)
        self.viewer.setGeometry(self._rect(self.places["panel"]))
        panel = self._scenery_at(self.places["panel"])
        if panel is not None:
            # The panel's own gradient, measured: the viewer clears to its top
            # colour, which is what the figure is seen against.
            self.viewer.clear_colour = tuple(
                [one / 255.0 for one in panel["colours"][0]] + [1.0])
        self.redraw()

    # -- geometry ----------------------------------------------------------

    def panel_native(self) -> tuple:
        """The panel in the GAME's own pixels, which is what `H` is counted in.

        Not the widget's size: the widget is the panel times `scale`, and a
        projection built for it would draw the figure at native size inside a
        viewport twice as wide instead of scaling the picture up.
        """
        left, top, right, bottom = self.places["panel"]
        return (right - left + 1, bottom - top + 1)

    def _rect(self, box) -> QtCore.QRect:
        """A box of the table, in this window's pixels."""
        x0, y0, x1, y1 = box
        s = self.scale
        return QtCore.QRect(x0 * s, y0 * s, (x1 - x0 + 1) * s,
                            (y1 - y0 + 1) * s)

    def _row_rect(self, index: int) -> QtCore.QRect:
        """The cursor rectangle of row *index*, carried down by the pitch."""
        x0, y0, x1, y1 = self.places["cursor"]
        step = self.places["pitch"] * index
        return self._rect([x0, y0 + step, x1, y1 + step])

    def _font(self, size: int) -> QtGui.QFont:
        font = QtGui.QFont("Consolas")
        font.setStyleHint(QtGui.QFont.StyleHint.Monospace)
        font.setPixelSize(size)
        return font

    # -- the figure --------------------------------------------------------

    def redraw(self) -> None:
        """Rebuild the figure for the tuple the rows now spell.

        A refusal is kept, not raised: the screen has to go on showing the
        value the game shows -- the rows moved, and pretending they did not
        would be a second lie on top of the missing head.
        """
        self.tuple_text = self.state.tuple_text()
        if self.builder is None:
            self.refusal = None
            return
        try:
            drawn = self.builder.build(self.tuple_text)
        except core.BadScene as exc:
            self.refusal = str(exc)
            self.drawn = None
            self.viewer.set_scene(None)
            self.viewer.hide()
            return
        self.refusal = None
        self.builds += 1
        self.drawn = drawn
        self.viewer.set_scene(drawn)
        self.aim()
        self.viewer.show()

    def aim(self) -> None:
        """Point the panel's camera at the figure the rows now describe.

        `HEIG` and `BODY` change no piece of the figure: the game puts them in
        the CAMERA, as a scale per axis, and so does this -- by asking
        `camera_for` again with the values on screen.  Without a measured
        camera the note says why and the v1 orbit stays.
        """
        if self.camera_for is None or self.drawn is None:
            return
        try:
            self.viewer.game_camera = self.camera_for(self.state.values())
            self.camera_note = None
        except core.BadScene as exc:
            self.viewer.game_camera = None
            self.camera_note = str(exc)
        self.viewer.update()

    def picture(self) -> QtGui.QImage:
        """The whole screen as one image, the panel included.

        `QWidget.grab()` walks the widget tree and an OpenGL child does not
        always come along, so the figure is fetched from the viewer itself and
        painted into the panel.  A screenshot with a hole where the figure is
        would look exactly like a refusal, which is the one thing this window
        has to be able to show honestly.
        """
        shot = self.grab().toImage().convertToFormat(
            QtGui.QImage.Format.Format_RGBA8888)
        if self.viewer.isVisible():
            painter = QtGui.QPainter(shot)
            painter.drawImage(self.viewer.geometry(),
                              self.viewer.grabFramebuffer())
            painter.end()
        return shot

    # -- the four buttons --------------------------------------------------

    def press(self, button: str) -> bool:
        """One press, and the figure redrawn if the tuple changed.

        Or re-aimed, if what changed is the figure's stature: `HEIG` and
        `BODY` are not in the tuple, and until LOOKS-TASK-29 they moved the
        text and nothing else.
        """
        before = self.state.tuple_text()
        values = self.state.values()
        stature = (values.get("height"), values.get("build"))
        moved = core.screen_press(self.state, button)
        now = self.state.values()
        if self.state.tuple_text() != before:
            self.redraw()
        elif (now.get("height"), now.get("build")) != stature:
            self.aim()
        self.update()
        return moved

    def keyPressEvent(self, event) -> None:
        button = KEYS.get(event.key())
        if button is None:
            super().keyPressEvent(event)
            return
        self.press(button)
        event.accept()

    # -- what the window shows, as text ------------------------------------

    def report(self) -> dict:
        """What the gate reads.  Straight off the widget, never off the table:
        a report built from `screen.py` would agree with `screen.py` however
        broken the drawing was."""
        return {
            "slot": self.state.slot,
            "scenery": len(self.scenery),
            "cursor": self.state.row,
            "help": self.refusal if self.refusal else self.state.help_text(),
            "rows": {name: self.state.text_of(name)
                     for name in self.state.order},
            "tuple": self.tuple_text,
            "refused": self.refusal,
            "builds": self.builds,
            "plate": self.state.plate(),
            "shirt": self.state.shirt(),
            "title": self.state.title(),
        }

    # -- the drawing -------------------------------------------------------

    def _scenery_at(self, box):
        """The measured packet that covers *box*, or None."""
        for packet in self.scenery:
            xs = [point[0] for point in packet["points"]]
            ys = [point[1] for point in packet["points"]]
            if (abs(min(xs) - box[0]) <= 2 and abs(min(ys) - box[1]) <= 2
                    and abs(max(xs) - box[2]) <= 2
                    and abs(max(ys) - box[3]) <= 2):
                return packet
        return None

    def _paint_scenery(self, painter) -> None:
        """The measured furniture: one rectangle per packet, flat or graded.

        The packets are the game's own -- `oracle.py --scenery` reads them out
        of the display list and keeps only those whose colours are the ones
        the console showed inside them.  A gradient is drawn as the hardware
        shades it between the first corner's colour and the third's.
        """
        s = self.scale
        for packet in self.scenery:
            xs = [point[0] for point in packet["points"]]
            ys = [point[1] for point in packet["points"]]
            box = QtCore.QRect(min(xs) * s, min(ys) * s,
                               (max(xs) - min(xs)) * s,
                               (max(ys) - min(ys)) * s)
            colours = [QtGui.QColor(*one) for one in packet["colours"]]
            if packet["gradient"] and len(colours) > 2:
                shade = QtGui.QLinearGradient(box.topLeft(), box.bottomLeft())
                shade.setColorAt(0.0, colours[0])
                shade.setColorAt(1.0, colours[2])
                painter.fillRect(box, QtGui.QBrush(shade))
            else:
                painter.fillRect(box, colours[0])

    def paintEvent(self, event) -> None:
        painter = QtGui.QPainter(self)
        painter.fillRect(self.rect(), BACKGROUND)
        s = self.scale
        small = self._font(max(7, self.places["pitch"] * s - 4))
        self._paint_scenery(painter)

        # The panel.  Empty when the tuple was refused -- the viewer is hidden
        # and nothing takes its place.  Its colour is the measured gradient
        # when there is one, and the v2's own blue when there is not.
        panel = self._rect(self.places["panel"])
        if not self.scenery or self.refusal:
            painter.fillRect(panel, PANEL if not self.refusal else BACKGROUND)
        painter.setPen(BOX)
        painter.drawRect(panel.adjusted(0, 0, -1, -1))
        painter.drawRect(self._rect(self.places["rows"]).adjusted(0, 0, -1, -1))

        painter.setFont(self._font(max(9, 10 * s)))
        painter.setPen(INK)
        painter.drawText(self.places["title"][0] * s,
                         (self.places["title"][1] + 10) * s,
                         self.state.title())
        painter.setFont(small)
        painter.drawText(self.places["plate"][0] * s,
                         (self.places["plate"][1] + 9) * s, self.state.plate())
        painter.setPen(DIM)
        painter.drawText(self.places["shirt"][0] * s,
                         (self.places["shirt"][1] + 8) * s, self.state.shirt())

        # The rows.  The cursor rectangle first, so the text sits on top.
        cursor = self._row_rect(self.state.cursor)
        painter.setPen(CURSOR)
        painter.drawRect(cursor.adjusted(0, 0, -1, -1))
        for index, name in enumerate(self.state.order):
            box = self._row_rect(index)
            painter.setFont(small)
            painter.setPen(DIM)
            painter.drawText(self.places["labels_x"] * s, box.bottom() - s,
                             name)
            painter.setPen(INK if index == self.state.cursor else DIM)
            painter.drawText(self.places["values_x"] * s + 2 * s,
                             box.bottom() - s, self.state.text_of(name))

        # The help box, which carries the refusal when there is one.
        help_box = self._rect(self.places["help"])
        painter.setPen(BOX)
        painter.drawRect(help_box.adjusted(0, 0, -1, -1))
        painter.setPen(REFUSED if self.refusal else INK)
        painter.setFont(small)
        painter.drawText(help_box.adjusted(4 * s, 2 * s, -4 * s, -2 * s),
                         int(QtCore.Qt.TextFlag.TextWordWrap),
                         self.refusal if self.refusal
                         else self.state.help_text())
        painter.end()

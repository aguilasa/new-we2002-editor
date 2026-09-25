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

MEASURED too, since LOOKS-TASK-31: the furniture -- the panel, the help box,
the background, the title bar, the row bands and the borders, with their
colours and gradients -- is polygons of the GPU, and this paints the packets
the frame hands to it (`scene.furniture_picture`), not a look-alike.

MEASURED since LOOKS-TASK-36: the static sprites -- the title, the icon, the
shirt boxes, the bar and the plate -- cut off the disc by the core
(`scene.static_sprites`), the plate's CLUT from the player's position, and
painted over the furniture once, which is the order the game's list draws
them in.  And the two arrows beside the cursor's value, where the screen walk
read them (`screen.State.arrows`).

MEASURED since LOOKS-TASK-37: the typeface.  The labels, the values, the
plate and the shirt are written with the game's own glyphs -- the font rule of
`glyphs.py`, read off the overlay -- in the colour and with the spacing of the
text object that writes each (`screen.State.style`).  And, since LOOKS-TASK-38,
where each one STARTS: every value in the pieces the walk read for it -- each
text object's box, alignment and tabs --, and the plate and the shirt centred
in theirs, which is where the game puts every glyph.  NOT measured: the pulse
of the arrows: the game dims and brightens them frame to frame, and the
window draws them at 128, unmodulated -- the animation is phase 11's.

## The walk (LOOKS-TASK-33)

The panel walks by default, at the game's rhythm: the clock is `scene.WalkClock`
over the cycle `oracle.py --walk` measured, turned into seconds by the frame
rate `oracle.py --rhythm` measured -- 34 passes in 77 frames of 1/59.817 s.
`Space` pauses and goes on, `.` steps one pass; neither is an arrow, and the
arrows keep driving the rows.  On the five head rows the game walks on to one
frame and holds it (`scene.walk_held_rows`), and so does this; a changed value
leaves the walk alone, as it does in the game.  NOT modelled, and said in the
report: the other animation `FOOT` plays, and the turn of the model on the
held rows.

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

WALK_KEYS = {
    QtCore.Qt.Key.Key_Space: "pause",
    QtCore.Qt.Key.Key_Period: "step",
}
"""The two keys of the walk: neither is an arrow, so neither moves a row."""

TICK_MS = 10
"""How often the window asks the clock which pass is on: well under the two
frames of 1/59.8 s the shortest pass lasts, so no pass is skipped by waiting."""

BACKGROUND = QtGui.QColor(0, 32, 48)
BOX = QtGui.QColor(150, 150, 150)
INK = QtGui.QColor(232, 232, 232)
DIM = QtGui.QColor(150, 160, 180)
CURSOR = QtGui.QColor(181, 181, 57)
REFUSED = QtGui.QColor(232, 120, 120)
PANEL = QtGui.QColor(12, 40, 96)


class LooksSet(QtWidgets.QWidget):
    """The screen, driven by the four buttons and redrawn on every change."""

    def __init__(self, state, builder=None, scale: int = SCALE, parent=None,
                 clock=None):
        super().__init__(parent)
        self.state = state
        self.builder = builder
        # The walk: a `scene.WalkClock`, or None when there is no measured
        # cycle -- then the panel stands on one frame and the report says so.
        self.clock = clock
        self.elapsed = QtCore.QElapsedTimer()
        self.elapsed.start()
        self.shown = None
        self.passes_drawn = 0
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(TICK_MS)
        self.timer.timeout.connect(self.tick)
        self.scale = scale
        self.places = state.layout()
        self.refusal: str | None = None
        self.builds = 0
        self.drawn = None
        self.tuple_text = state.tuple_text()
        self.glyph_images = {}
        # Where the game's camera comes from, handed in by whoever built the
        # window: a callable of the rows' values.  The window does not compose
        # it -- that is the core's (`scene.panel_camera`), and the camera is
        # where HEIG and BODY live (LOOKS-TASK-29).
        self.camera_for = None
        self.camera_note: str | None = None
        # Which camera the panel is drawing with: the name of the row whose
        # own camera was measured, or None for the full figure's.  The report
        # carries it, because "the panel zooms on the rows that zoom" is a
        # claim the gate has to be able to read off the window.
        self.camera_row: str | None = None
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

        # The furniture drawn once, as the GPU draws it, by the core: it does
        # not move, and the title band's gradients run across the screen,
        # which a rectangle per packet painted here could not do.
        self.furniture = None
        # The static sprites, painted over the furniture: the list draws every
        # one of them after the furniture under it (LOOKS-TASK-36).  Without a
        # builder there is no disc to cut them from, and the note says so.
        self.sprites, self.sprites_note = [], None
        if self.scenery and builder is not None:
            try:
                self.sprites = core.static_sprites(
                    core.load_sprites(int(state.slot)), state.plate())
            except core.BadScene as exc:
                self.sprites_note = str(exc)
        self.arrow_images = {}
        if self.scenery:
            picture = core.furniture_picture(self.scenery, (width, height))
            if self.sprites:
                try:
                    builder.paint_sprites(picture, (width, height),
                                          self.sprites)
                except core.BadScene as exc:
                    self.sprites, self.sprites_note = [], str(exc)
            self.furniture = QtGui.QImage(bytes(picture), width, height,
                                          3 * width,
                                          QtGui.QImage.Format.Format_RGB888
                                          ).copy()

        self.viewer = Viewer(None, self)
        self.viewer.setGeometry(self._rect(self.places["panel"]))
        if self.furniture is not None:
            # The panel's own piece of the furniture -- gradient and border --
            # painted behind the figure.
            left, top, right, bottom = self.places["panel"]
            self.viewer.clear_image = self.furniture.copy(
                left, top, right - left + 1, bottom - top + 1)
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

    def arrows(self) -> list:
        """The arrows this window draws now, `[{"side", "point"}]`.

        What `paintEvent` paints and what `report` says are both this list,
        so the report is the drawing's own account and not the table's."""
        if self.builder is None:
            return []
        return self.state.arrows()

    def _arrow_image(self, side: str) -> QtGui.QImage:
        """The arrow off the disc, as the core cuts it, once per side."""
        if side not in self.arrow_images:
            sprite = core.arrow_sprite(side, (0, 0))
            width, height = sprite["size"]
            rgba = self.builder.sprite_rgba(sprite)
            self.arrow_images[side] = QtGui.QImage(
                rgba, width, height, 4 * width,
                QtGui.QImage.Format.Format_RGBA8888).copy()
        return self.arrow_images[side]

    def _glyph_image(self, sprite: dict) -> QtGui.QImage:
        """One glyph off the disc, as the core cuts it, once per code and
        colour -- the same letter comes grey in a label and lavender in a
        value."""
        key = (sprite["code"], tuple(sprite["colour"]))
        if key not in self.glyph_images:
            width, height = sprite["size"]
            rgba = self.builder.sprite_rgba(dict(sprite, point=[0, 0]))
            self.glyph_images[key] = QtGui.QImage(
                rgba, width, height, 4 * width,
                QtGui.QImage.Format.Format_RGBA8888).copy()
        return self.glyph_images[key]

    def glyphs(self) -> list:
        """Every glyph sprite this window writes now, in native pixels.

        The rows' names from the labels' own x, left-aligned as the game has
        them; each value in the pieces the walk read for it -- the box, the
        alignment and the tabs of every text object that writes a part of it
        (LOOKS-TASK-38) --; and the plate and the shirt, centred in theirs.
        `paintEvent` draws exactly these, and `report` gives them to the gate.
        """
        if self.builder is None:
            return []
        places, out = self.places, []
        for index, name in enumerate(self.state.order):
            y = places["rows_y"] + places["pitch"] * index
            out += self.builder.text_sprites(name, (places["labels_x"], y),
                                             self.state.style("labels"))
            for piece in self.state.value_layout(name):
                out += self.builder.placed_sprites(piece)
        for role in ("plate", "shirt"):
            out += self.builder.placed_sprites(self.state.style(role))
        return out

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
            if self.clock is not None:
                self.shown = self.clock.visit(self.now())
                drawn = self.builder.walk_build(self.tuple_text, *self.shown)
            else:
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

    # -- the walk ----------------------------------------------------------

    def now(self) -> float:
        """Seconds since the window was made: the clock's only time source."""
        return self.elapsed.nsecsElapsed() / 1e9

    def animate(self, on: bool = True) -> None:
        """Start or stop the timer that turns the clock into pictures."""
        if self.clock is None:
            return
        if on:
            self.clock.resume(self.now())
            self.timer.start()
        else:
            self.clock.pause(self.now())
            self.timer.stop()

    def tick(self) -> None:
        """Draw the pass the clock says is on, if it is not the one shown."""
        if self.clock is None or self.drawn is None or self.refusal:
            return
        visit = self.clock.visit(self.now())
        if visit == self.shown:
            return
        try:
            drawn = self.builder.walk_build(self.tuple_text, *visit)
        except core.BadScene as exc:
            self.refusal = str(exc)
            return
        self.shown = visit
        self.passes_drawn += 1
        self.drawn = drawn
        self.viewer.set_scene(drawn)

    def walk_key(self, name: str) -> None:
        """`pause` or `step`, from the keyboard or from a gate."""
        if self.clock is None:
            return
        if name == "pause":
            if self.clock.toggle(self.now()):
                self.timer.start()
            else:
                self.timer.stop()
        elif name == "step":
            self.clock.step(self.now())
            self.timer.stop()
        self.tick()

    def walk_report(self) -> dict | None:
        if self.clock is None:
            return None
        found = self.clock.report(self.now())
        found["drawn"] = self.passes_drawn
        found["shown"] = self.shown
        return found

    def aim(self) -> None:
        """Point the panel's camera at the figure the rows now describe.

        `HEIG` and `BODY` change no piece of the figure: the game puts them in
        the CAMERA, as a scale per axis, and so does this -- by asking
        `camera_for` again with the values on screen.  The row under the
        cursor goes with them: six of the twelve move the camera in the game
        (LOOKS-TASK-40), and `camera_for` answers which one it used.  Without
        a measured camera the note says why and the v1 orbit stays.
        """
        if self.camera_for is None or self.drawn is None:
            return
        try:
            matrix, row = self.camera_for(self.state.values(), self.state.row)
            self.viewer.game_camera = matrix
            self.camera_row = row
            self.camera_note = None
        except core.BadScene as exc:
            self.viewer.game_camera = None
            self.camera_row = None
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

        Or re-aimed, if what changed is the figure's stature or the ROW: `HEIG`
        and `BODY` are not in the tuple, and until LOOKS-TASK-29 they moved the
        text and nothing else; and six of the twelve rows draw the panel with a
        camera of their own (LOOKS-TASK-40), so the cursor moving is a reason
        to aim again even when nothing about the figure changed.
        """
        before = self.state.tuple_text()
        values = self.state.values()
        stature = (values.get("height"), values.get("build"))
        row = self.state.row
        moved = core.screen_press(self.state, button)
        now = self.state.values()
        if self.clock is not None:
            # What the rows do to the walk, as the game does it: a held row
            # walks on to its frame and stops, leaving one goes on from the
            # next, and a value changes nothing (LOOKS-TASK-33).
            held = core.walk_held_rows()
            if self.state.row != row:
                if row in held and self.state.row not in held:
                    self.clock.release(self.now())
                if self.state.row in held:
                    self.clock.hold(self.now(),
                                    settle=not self.timer.isActive())
            if now != values:
                self.clock.value_changed(self.now())
        if self.state.tuple_text() != before:
            self.redraw()
        elif ((now.get("height"), now.get("build")) != stature
              or self.state.row != row):
            self.aim()
            self.tick()
        self.update()
        return moved

    def keyPressEvent(self, event) -> None:
        button = KEYS.get(event.key())
        if button is None:
            walk = WALK_KEYS.get(event.key())
            if walk is None:
                super().keyPressEvent(event)
                return
            self.walk_key(walk)
            event.accept()
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
            "sprites": {one["group"]: tuple(one["clut"])
                        for one in self.sprites},
            "sprites_note": self.sprites_note,
            "arrows": self.arrows(),
            "camera": ("refused" if self.camera_note is not None
                       else self.camera_row or "full figure"),
            "camera_note": self.camera_note,
            "walk": self.walk_report(),
            "glyphs": sorted((one["point"][0], one["point"][1], one["uv"][0],
                              one["uv"][1]) for one in self.glyphs()),
        }

    # -- the drawing -------------------------------------------------------

    def _paint_scenery(self, painter) -> None:
        """The measured furniture, drawn once by the core, scaled to the window.

        The packets are the game's own -- `oracle.py --scenery` walks them off
        the list the frame hands the GPU, in drawing order, blend and all.
        """
        if self.furniture is None:
            return
        painter.drawImage(self.rect(), self.furniture)

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

        painter.setPen(INK)
        if not any(one["group"] == "title" for one in self.sprites):
            # The title is a sprite off the disc once the static sprites are
            # painted; the Qt text is only what stands in without them.
            painter.setFont(self._font(max(9, 10 * s)))
            painter.drawText(self.places["title"][0] * s,
                             (self.places["title"][1] + 10) * s,
                             self.state.title())
        painter.setFont(small)

        # The rows.  The cursor rectangle first, so the text sits on top --
        # where the state says it is, which on DEFAUL's label is over the
        # row's name and not its value (CORR-LOOKS-067).
        cursor = self._rect(self.state.cursor_box())
        painter.setPen(CURSOR)
        painter.drawRect(cursor.adjusted(0, 0, -1, -1))
        for arrow in self.arrows():
            picture = self._arrow_image(arrow["side"])
            x, y = arrow["point"]
            painter.drawImage(QtCore.QRect(x * s, y * s, picture.width() * s,
                                           picture.height() * s), picture)
        if self.builder is not None:
            for sprite in self.glyphs():
                picture = self._glyph_image(sprite)
                x, y = sprite["point"]
                painter.drawImage(QtCore.QRect(x * s, y * s,
                                               picture.width() * s,
                                               picture.height() * s), picture)
        else:
            # No disc to cut the glyphs from: Qt's font stands in, and says
            # nothing about the game's.
            for index, name in enumerate(self.state.order):
                box = self._row_rect(index)
                painter.setFont(small)
                painter.setPen(DIM)
                painter.drawText(self.places["labels_x"] * s,
                                 box.bottom() - s, name)
                painter.setPen(INK)
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

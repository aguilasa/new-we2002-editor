#!/usr/bin/env python3
"""The pitch: the ten outfield players at their X and Y, their roles, and the
drag that moves them.

Rule 3: `model` and `domains`, nothing else from the port.

THIS FILE IS WHERE `X*7` AND `Y*2` BELONG, AND THE ONLY ONE -- and MCR-TASK-12
is where that stops being a one-way statement. They are SCREEN factors, not
format: the upstream's `FrmFormation.vb` writes `PicP1.Left = 9 * 7` and
`PicP1.Top = 41 * 2` against a 353x192 pitch picture, which is exactly the
card's coordinates scaled to that widget. Trap 7 of the cycle profile is what
happens when they migrate inward -- put them in the core and the byte-identical
round-trip dies, because what goes back to the card is seven times what came
out of it.

SO THE INVERSE LIVES HERE TOO. Dragging a marker produces pitch pixels, and
`to_card_x` / `to_card_y` divide them back before anything reaches the model:
what leaves this file is the card's own units, and the core never sees a 7 or
a 2 in either direction. The two functions are the whole of it, which is what
makes the rule checkable by reading one file.

The label of each marker sits six Y-units below the marker in the upstream
(`lblPic1.Top = 47 * 2` against `PicP1.Top = 41 * 2`); the same offset is used
here, so a formation looks the way its author drew it.

THE ROLE NAMES ARE A THIRD PARTY'S. `domains.ROLE` is transcribed from
Zetaprog's combo and checked against his source every run; nothing in the
fixture confirms the MEANING of the twenty labels, and the pitch says so in its
own caption rather than quietly presenting them as measured.

`0x6500` IS READ, NEVER WRITTEN, and stays that way until MCR-TASK-13 says
what it means. `formation.write` leaves the byte alone; this view shows it and
offers no editor for it, because a screen that lets someone set a byte whose
meaning is unsettled is how a round-trip stops being evidence.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import domains                                           # noqa: E402
from PySide6 import QtCore, QtGui, QtWidgets             # noqa: E402

# The upstream's pitch picture, and the two factors it is drawn with.
PITCH_WIDTH = 353
PITCH_HEIGHT = 192
X_SCALE = 7
Y_SCALE = 2
LABEL_DROP = 6          # in card Y units, as `lblPicN.Top` does it
MARKER = 14             # marker diameter, in pitch pixels

# The pitch is 353x192, but a marker at the fixture's largest Y (87) puts its
# label at (87 + 6) * 2 = 186 and the text runs past the touchline. The
# upstream does not notice, because its labels are separate controls on the
# form and can spill below the picture; here everything is painted inside one
# widget, so the DRAWING surface is taller than the pitch and the pitch is
# drawn at the top of it. The two factors are untouched -- what changed is how
# much room the drawing gets, not where a player is.
SURFACE_HEIGHT = PITCH_HEIGHT + LABEL_DROP * Y_SCALE + 12

# How far a marker may be dragged, in the CARD's units. The byte holds 0..255
# and `formation.write` is what enforces that; this narrower limit is the
# pitch's, so a marker cannot be dropped off the drawing. A screen limit,
# declared where the other screen numbers are.
X_MAX = (PITCH_WIDTH - MARKER) // X_SCALE
Y_MAX = (PITCH_HEIGHT - MARKER) // Y_SCALE


def to_card_x(pitch_px: float) -> int:
    """Pitch pixels back to the card's X. The inverse of `x * X_SCALE`."""
    return max(0, min(X_MAX, round(pitch_px / X_SCALE)))


def to_card_y(pitch_px: float) -> int:
    """Pitch pixels back to the card's Y. The inverse of `y * Y_SCALE`."""
    return max(0, min(Y_MAX, round(pitch_px / Y_SCALE)))


class PitchWidget(QtWidgets.QWidget):
    """A 353x192 pitch, scaled to whatever room the window gives it."""

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._formation = None
        self._dragging = None
        self._grab = (0.0, 0.0)
        self.setMinimumSize(PITCH_WIDTH, SURFACE_HEIGHT)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)
        self.setMouseTracking(False)

    def set_formation(self, formation) -> None:
        self._formation = formation
        self._dragging = None
        self.update()

    # -- the one transform, and its inverse -------------------------------

    def _transform(self) -> tuple[float, float, float]:
        scale = min(self.width() / PITCH_WIDTH,
                    self.height() / SURFACE_HEIGHT)
        return (scale,
                (self.width() - PITCH_WIDTH * scale) / 2,
                (self.height() - SURFACE_HEIGHT * scale) / 2)

    def _to_pitch(self, point) -> tuple[float, float]:
        scale, dx, dy = self._transform()
        if not scale:
            return 0.0, 0.0
        return (point.x() - dx) / scale, (point.y() - dy) / scale

    # -- dragging ---------------------------------------------------------

    def _marker_at(self, px: float, py: float):
        """The index of the marker under a pitch-pixel point, or None."""
        if self._formation is None:
            return None
        for i in range(len(self._formation.x)):
            left = self._formation.x[i] * X_SCALE
            top = self._formation.y[i] * Y_SCALE
            if left <= px <= left + MARKER and top <= py <= top + MARKER:
                return i
        return None

    def marker_point(self, i: int):
        """Where marker `i` sits in WIDGET coordinates -- the transform, not
        its inverse.

        The drag reads mouse positions and divides them back; this goes the
        other way, and it is what lets a gate press exactly on a marker
        instead of guessing. Same two factors, same one transform.
        """
        scale, dx, dy = self._transform()
        left = self._formation.x[i] * X_SCALE + MARKER / 2
        top = self._formation.y[i] * Y_SCALE + MARKER / 2
        return QtCore.QPointF(dx + left * scale, dy + top * scale)

    def mousePressEvent(self, event) -> None:            # noqa: N802
        if event.button() != QtCore.Qt.MouseButton.LeftButton:
            return
        px, py = self._to_pitch(event.position())
        i = self._marker_at(px, py)
        if i is None:
            return
        self._dragging = i
        self._grab = (px - self._formation.x[i] * X_SCALE,
                      py - self._formation.y[i] * Y_SCALE)
        self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event) -> None:             # noqa: N802
        if self._dragging is None:
            return
        px, py = self._to_pitch(event.position())
        i = self._dragging
        # The inverse of the two screen factors, and the only place it happens.
        x = to_card_x(px - self._grab[0])
        y = to_card_y(py - self._grab[1])
        if (x, y) == (self._formation.x[i], self._formation.y[i]):
            return
        self._formation.x[i] = x
        self._formation.y[i] = y
        self.update()
        self.changed.emit()

    def mouseReleaseEvent(self, event) -> None:          # noqa: N802
        self._dragging = None
        self.unsetCursor()

    # -- painting ---------------------------------------------------------

    def paintEvent(self, event) -> None:                  # noqa: N802
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # One transform, so every coordinate below is in pitch pixels and the
        # two factors stay readable.
        scale, dx, dy = self._transform()
        painter.translate(dx, dy)
        painter.scale(scale, scale)

        painter.fillRect(0, 0, PITCH_WIDTH, PITCH_HEIGHT,
                         QtGui.QColor(40, 110, 60))
        pen = QtGui.QPen(QtGui.QColor(230, 230, 230))
        pen.setWidthF(1.5)
        painter.setPen(pen)
        painter.drawRect(4, 4, PITCH_WIDTH - 8, PITCH_HEIGHT - 8)
        painter.drawLine(PITCH_WIDTH // 2, 4, PITCH_WIDTH // 2,
                         PITCH_HEIGHT - 4)
        painter.drawEllipse(QtCore.QPointF(PITCH_WIDTH / 2, PITCH_HEIGHT / 2),
                            26, 26)

        if self._formation is None:
            painter.setPen(QtGui.QColor(235, 235, 235))
            painter.drawText(QtCore.QRectF(0, 0, PITCH_WIDTH, PITCH_HEIGHT),
                             QtCore.Qt.AlignmentFlag.AlignCenter,
                             "No card open")
            return

        labels = self._formation.role_labels()
        font = painter.font()
        font.setPointSizeF(6.5)
        painter.setFont(font)
        for i in range(len(self._formation.x)):
            # The two screen factors, in the one place they belong.
            left = self._formation.x[i] * X_SCALE
            top = self._formation.y[i] * Y_SCALE
            painter.setBrush(QtGui.QColor(250, 250, 250)
                             if i != self._dragging
                             else QtGui.QColor(250, 220, 120))
            painter.setPen(QtGui.QPen(QtGui.QColor(20, 20, 20), 1))
            painter.drawEllipse(QtCore.QRectF(left, top, MARKER, MARKER))
            painter.drawText(
                QtCore.QRectF(left - 12, top + LABEL_DROP * Y_SCALE + 2,
                              MARKER + 24, 12),
                QtCore.Qt.AlignmentFlag.AlignHCenter, labels[i])


class FormationView(QtWidgets.QWidget):
    """The pitch, plus what the card holds around it."""

    changed = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._formation = None
        self._loading = False

        self.pitch = PitchWidget()
        self.pitch.changed.connect(self._pitch_moved)

        self.roles = [QtWidgets.QComboBox() for _ in range(10)]
        roles_box = QtWidgets.QGroupBox("Roles, by outfield slot")
        grid = QtWidgets.QGridLayout(roles_box)
        for i, combo in enumerate(self.roles):
            combo.addItems(list(domains.ROLE))
            combo.currentIndexChanged.connect(
                lambda value, slot=i: self._commit_role(slot, value))
            grid.addWidget(QtWidgets.QLabel(str(i + 1)), i // 5, (i % 5) * 2)
            grid.addWidget(combo, i // 5, (i % 5) * 2 + 1)

        self.kickers = [QtWidgets.QSpinBox() for _ in range(5)]
        kick_box = QtWidgets.QGroupBox(
            "Free kicks and corners, in kicker order (squad slot)")
        kick_grid = QtWidgets.QHBoxLayout(kick_box)
        for k, spin in enumerate(self.kickers):
            spin.setRange(0, 22)
            spin.valueChanged.connect(
                lambda value, slot=k: self._commit_kicker(slot, value))
            kick_grid.addWidget(QtWidgets.QLabel(str(k + 1)))
            kick_grid.addWidget(spin)
        kick_grid.addStretch(1)

        self._open_byte = QtWidgets.QLabel("")
        caption = QtWidgets.QLabel(
            "Drag a marker to move a player; X and Y are the card's own "
            "units, scaled by 7 and 2 for this drawing only, and divided "
            "back before anything reaches the model. Role names come from "
            "the upstream editor and are not measured.")
        caption.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.pitch, 1)
        layout.addWidget(roles_box)
        layout.addWidget(kick_box)
        layout.addWidget(self._open_byte)
        layout.addWidget(caption)
        self._enable(False)

    def _enable(self, on: bool) -> None:
        for widget in self.roles + self.kickers:
            widget.setEnabled(on)

    def set_save(self, save) -> None:
        if save is None:
            self._formation = None
            self.pitch.set_formation(None)
            self._enable(False)
            self._open_byte.setText("")
            return
        self._formation = save.formation
        self.pitch.set_formation(self._formation)
        self._loading = True
        try:
            self._enable(True)
            for i, combo in enumerate(self.roles):
                role = self._formation.role[i]
                combo.setCurrentIndex(role if 0 <= role < combo.count() else 0)
            for k, spin in enumerate(self.kickers):
                spin.setValue(self._formation.kickers[k])
        finally:
            self._loading = False
        self._open_byte.setText(
            f"Open byte 0x6500: {self._formation.open_slot_byte} -- captain by "
            f"our reverse engineering, sixth kicker by the upstream, and read "
            f"only until MCR-TASK-13 settles it.")

    def _pitch_moved(self) -> None:
        self.changed.emit()

    def _commit_role(self, slot: int, value: int) -> None:
        if self._loading or self._formation is None:
            return
        if self._formation.role[slot] == value:
            return
        self._formation.role[slot] = value
        self.pitch.update()
        self.changed.emit()

    def _commit_kicker(self, slot: int, value: int) -> None:
        if self._loading or self._formation is None:
            return
        if self._formation.kickers[slot] == value:
            return
        self._formation.kickers[slot] = value
        self.changed.emit()

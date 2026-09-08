#!/usr/bin/env python3
"""The pitch: the ten outfield players at their X and Y, and their roles.

Rule 3: `model` and `domains`, nothing else from the port.

THIS FILE IS WHERE `X*7` AND `Y*2` BELONG, AND THE ONLY ONE. They are SCREEN
factors, not format: the upstream's `FrmFormation.vb` writes
`PicP1.Left = 9 * 7` and `PicP1.Top = 41 * 2` against a 353x192 pitch picture,
which is exactly the card's coordinates scaled to that widget. Trap 7 of the
cycle profile is what happens when they migrate inward -- put them in the core
and the byte-identical round-trip dies, because what goes back to the card is
seven times what came out of it.

The label of each marker sits six Y-units below the marker in the upstream
(`lblPic1.Top = 47 * 2` against `PicP1.Top = 41 * 2`); the same offset is used
here, so a formation looks the way its author drew it.

THE ROLE NAMES ARE A THIRD PARTY'S. `domains.ROLE` is transcribed from
Zetaprog's combo and checked against his source every run; nothing in the
fixture confirms the MEANING of the twenty labels, and the pitch says so in its
own caption rather than quietly presenting them as measured.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


class PitchWidget(QtWidgets.QWidget):
    """A 353x192 pitch, scaled to whatever room the window gives it."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._formation = None
        self.setMinimumSize(PITCH_WIDTH, SURFACE_HEIGHT)
        self.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,
                           QtWidgets.QSizePolicy.Policy.Expanding)

    def set_formation(self, formation) -> None:
        self._formation = formation
        self.update()

    def paintEvent(self, event) -> None:                  # noqa: N802
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)

        # One transform, so every coordinate below is in pitch pixels and the
        # two factors stay readable.
        scale = min(self.width() / PITCH_WIDTH,
                    self.height() / SURFACE_HEIGHT)
        painter.translate((self.width() - PITCH_WIDTH * scale) / 2,
                          (self.height() - SURFACE_HEIGHT * scale) / 2)
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
            painter.setBrush(QtGui.QColor(250, 250, 250))
            painter.setPen(QtGui.QPen(QtGui.QColor(20, 20, 20), 1))
            painter.drawEllipse(QtCore.QRectF(left, top, MARKER, MARKER))
            painter.drawText(
                QtCore.QRectF(left - 12, top + LABEL_DROP * Y_SCALE + 2,
                              MARKER + 24, 12),
                QtCore.Qt.AlignmentFlag.AlignHCenter, labels[i])


class FormationView(QtWidgets.QWidget):
    """The pitch, plus what the card holds around it."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pitch = PitchWidget()
        self._roles = QtWidgets.QLabel("")
        self._kickers = QtWidgets.QLabel("")
        self._open_byte = QtWidgets.QLabel("")
        caption = QtWidgets.QLabel(
            "Role names come from the upstream editor and are not measured; "
            "X and Y are the card's own units, scaled by 7 and 2 for this "
            "drawing only.")
        caption.setWordWrap(True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self.pitch, 1)
        layout.addWidget(self._roles)
        layout.addWidget(self._kickers)
        layout.addWidget(self._open_byte)
        layout.addWidget(caption)

    def set_save(self, save) -> None:
        if save is None:
            self.pitch.set_formation(None)
            self._roles.setText("")
            self._kickers.setText("")
            self._open_byte.setText("")
            return
        formation = save.formation
        self.pitch.set_formation(formation)
        self._roles.setText("Roles: " + ", ".join(formation.role_labels()))
        self._kickers.setText(
            "Free kicks and corners, in kicker order: "
            + ", ".join(str(slot) for slot in formation.kickers))
        self._open_byte.setText(
            f"Open byte: {formation.open_slot_byte} -- captain by our reverse "
            f"engineering, sixth kicker by the upstream. Read, never written.")

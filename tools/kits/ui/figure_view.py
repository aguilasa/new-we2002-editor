"""The 3D figure of the kit viewer, drawn by the core and shown by QPainter.

PLAN-KITS-PY.md section 3.4, "Aba 3D" (KITS-TASK-25), and KITS-AJUSTES-3D.md
G6 (K3D-TASK-14).  It is handed a looks `Scene` by `core.api.figure` and the
drawing function `core.api.draw_figure`, and reads nothing itself.

The picture is the core's (`core/raster.py`): the figure turned by yaw and
pitch, fitted to the widget, filled pixel by pixel with a depth buffer and the
UV interpolated from the screen.  Before G6 this widget painted triangle by
triangle back to front by mean depth through an affine map, which left out
every triangle whose UV has no area and painted the leg over the shorts.  The
same software drawing gives the same picture on Windows and under the Xvfb,
and `cli.py holes` counts that very picture.  A drag turns it.
"""

from __future__ import annotations

import time

from PySide6 import QtCore, QtGui, QtWidgets

BACKDROP = "#8c8c8c"
DEGREES_PER_PIXEL = 0.5
PITCH_LIMIT = 89.0
DEFAULT_YAW = 180.0
"""Facing the viewer: at 0 the figure shows its back."""
DEFAULT_PITCH = 0.0


def composed(raster) -> QtGui.QImage:
    """The core's RGBA *raster* over the backdrop, as the widget shows it."""
    out = QtGui.QImage(raster.width, raster.height, QtGui.QImage.Format.Format_RGB32)
    out.fill(QtGui.QColor(BACKDROP))
    figure = QtGui.QImage(bytes(raster.rgba), raster.width, raster.height, raster.width * 4,
                          QtGui.QImage.Format.Format_RGBA8888)
    p = QtGui.QPainter(out)
    p.drawImage(0, 0, figure)
    p.end()
    return out


class FigureView(QtWidgets.QWidget):
    """One posed figure, turned with the mouse."""

    turned = QtCore.Signal(float, float)

    def __init__(self, draw) -> None:
        super().__init__()
        self.draw = draw                 # api.draw_figure
        self.scene = None
        self.yaw, self.pitch = DEFAULT_YAW, DEFAULT_PITCH
        self.frame_ms = None             # how long the last picture took to draw
        self.drag = None
        self.setMinimumSize(320, 320)

    def set_scene(self, scene) -> None:
        self.scene = scene
        self.update()

    def reset(self) -> None:
        """Back to the turn the view opens with (KITS-TASK-37)."""
        self.turn_to(DEFAULT_YAW, DEFAULT_PITCH)

    def turn_to(self, yaw: float, pitch: float) -> None:
        self.yaw = yaw % 360.0
        self.pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT, pitch))
        self.turned.emit(self.yaw, self.pitch)
        self.update()

    # -- drawing --------------------------------------------------------------

    def picture(self) -> QtGui.QImage:
        """The figure at the widget's size and turn, drawn by the core."""
        started = time.perf_counter()
        drawn = self.draw(self.scene, self.yaw, self.pitch, self.width(), self.height())
        image = composed(drawn)
        self.frame_ms = (time.perf_counter() - started) * 1000.0
        return image

    def paintEvent(self, _event) -> None:
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(BACKDROP))
        if self.scene is None or not self.scene.parts:
            return
        p.drawImage(0, 0, self.picture())

    # -- the mouse ------------------------------------------------------------

    def mousePressEvent(self, event) -> None:
        self.drag = (event.position(), self.yaw, self.pitch)

    def mouseMoveEvent(self, event) -> None:
        if self.drag is None:
            return
        start, yaw, pitch = self.drag
        delta = event.position() - start
        self.turn_to(yaw + delta.x() * DEGREES_PER_PIXEL, pitch - delta.y() * DEGREES_PER_PIXEL)

    def mouseReleaseEvent(self, _event) -> None:
        self.drag = None

    def mouseDoubleClickEvent(self, _event) -> None:
        self.drag = None
        self.reset()

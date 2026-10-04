"""The 3D figure of the kit viewer, drawn by QPainter.

PLAN-KITS-PY.md section 3.4, "Aba 3D" (KITS-TASK-25).  It is handed a looks
`Scene` by `core.api.figure` and reads nothing itself.

Software, not OpenGL: every triangle is painted back to front through an
affine map from its texture triangle to its screen triangle, clipped to the
screen triangle.  That is the same picture on Windows and on Linux under the
Xvfb, which a GL context does not promise, and `kits_ui` compares pictures.
The camera is orthographic, turned by yaw and pitch, and fits the figure's
bounds to the widget; model y is up (the scene has already applied the looks
`UP`), screen y is down, hence the minus.  A drag turns it.
"""

from __future__ import annotations

import math

from PySide6 import QtCore, QtGui, QtWidgets

BACKDROP = "#8c8c8c"
UNTEXTURED = "#b0b0b0"
MARGIN = 0.08
"""Fraction of the widget left around the figure."""
DEGREES_PER_PIXEL = 0.5
PITCH_LIMIT = 89.0
DEFAULT_YAW = 180.0
"""Facing the viewer: at 0 the figure shows its back."""
DEFAULT_PITCH = 0.0


def rotate(point, yaw: float, pitch: float) -> tuple:
    """*point* turned by *yaw* about y, then *pitch* about x (degrees)."""
    x, y, z = point
    a, b = math.radians(yaw), math.radians(pitch)
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
    return x, y, z


class FigureView(QtWidgets.QWidget):
    """One posed figure, turned with the mouse."""

    turned = QtCore.Signal(float, float)

    def __init__(self, triangles) -> None:
        super().__init__()
        self.triangles = triangles       # api.FIGURE_TRIANGLES
        self.scene = None
        self.images = {}                 # surface key -> QImage
        self.yaw, self.pitch = DEFAULT_YAW, DEFAULT_PITCH
        self.drag = None
        self.setMinimumSize(320, 320)

    def set_scene(self, scene) -> None:
        self.scene = scene
        self.images = {}
        if scene is not None:
            for key, s in scene.surfaces.items():
                self.images[key] = QtGui.QImage(s.rgba, s.width, s.height, s.width * 4,
                                                QtGui.QImage.Format.Format_RGBA8888).copy()
        self.update()

    def turn_to(self, yaw: float, pitch: float) -> None:
        self.yaw = yaw % 360.0
        self.pitch = max(-PITCH_LIMIT, min(PITCH_LIMIT, pitch))
        self.turned.emit(self.yaw, self.pitch)
        self.update()

    # -- drawing --------------------------------------------------------------

    def _projected(self):
        """[(depth, screen points, uv, part)] of every triangle, far first."""
        parts = self.scene.parts
        centre = self.scene.centre()
        turned = [[rotate(tuple(p[i] - centre[i] for i in range(3)), self.yaw, self.pitch)
                   for p in part.points] for part in parts]
        xs = [p[0] for pts in turned for p in pts]
        ys = [p[1] for pts in turned for p in pts]
        span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
        side = min(self.width(), self.height()) * (1.0 - 2 * MARGIN)
        scale = side / span
        mx, my = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
        cx, cy = self.width() / 2.0, self.height() / 2.0
        out = []
        for part, pts in zip(parts, turned):
            screen = [QtCore.QPointF(cx + (p[0] - mx) * scale, cy - (p[1] - my) * scale)
                      for p in pts]
            for tri in self.triangles:
                depth = sum(pts[i][2] for i in tri) / 3.0
                out.append((depth, [screen[i] for i in tri], [part.uvs[i] for i in tri], part))
        out.sort(key=lambda t: t[0])
        return out

    def paintEvent(self, _event) -> None:
        p = QtGui.QPainter(self)
        p.fillRect(self.rect(), QtGui.QColor(BACKDROP))
        if self.scene is None or not self.scene.parts:
            return
        for _, screen, uvs, part in self._projected():
            polygon = QtGui.QPolygonF(screen)
            image = self.images.get(part.surface.key) if part.surface is not None else None
            if image is None:
                p.setPen(QtCore.Qt.PenStyle.NoPen)
                p.setBrush(QtGui.QColor(UNTEXTURED))
                p.drawPolygon(polygon)
                continue
            source = QtGui.QPolygonF([QtCore.QPointF(u * image.width(), v * image.height())
                                      for u, v in uvs])
            transform = QtGui.QTransform()
            if not QtGui.QTransform.quadToQuad(source, polygon, transform) \
                    and not self._affine(source, polygon, transform):
                continue
            path = QtGui.QPainterPath()
            path.addPolygon(polygon)
            path.closeSubpath()
            p.save()
            p.setClipPath(path)
            p.setTransform(transform)
            p.drawImage(0, 0, image)
            p.restore()

    @staticmethod
    def _affine(source, target, out) -> bool:
        """The affine map of three source points onto three target points."""
        (x0, y0), (x1, y1), (x2, y2) = ((q.x(), q.y()) for q in source)
        det = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(det) < 1e-9:
            return False
        (u0, v0), (u1, v1), (u2, v2) = ((q.x(), q.y()) for q in target)
        a = ((u1 - u0) * (y2 - y0) - (u2 - u0) * (y1 - y0)) / det
        b = ((u2 - u0) * (x1 - x0) - (u1 - u0) * (x2 - x0)) / det
        c = ((v1 - v0) * (y2 - y0) - (v2 - v0) * (y1 - y0)) / det
        d = ((v2 - v0) * (x1 - x0) - (v1 - v0) * (x2 - x0)) / det
        out.setMatrix(a, c, 0.0, b, d, 0.0, u0 - a * x0 - b * y0, v0 - c * x0 - d * y0, 1.0)
        return True

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

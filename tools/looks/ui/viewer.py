#!/usr/bin/env python3
"""The window that draws a scene: `QOpenGLWidget`, orbital camera, two modes.

Rule 3 of plan section 3.3, this half: **nothing here knows an address and
nothing here reads a disc.**  It is handed a `scene.Scene` -- points, texture
coordinates and RGBA bytes -- and uploads it.  Every decision about WHICH
primitive, WHICH palette window and WHICH band was taken before this file runs,
by `assembly.py` and `scene.py`, where it can be checked without a display.

`QOpenGLWidget` and not Qt3D: the Qt3D module is large and half-abandoned in
Qt6, and rasterising in Python is not on the table without `numpy`, which this
machine does not have.

Two things the GPU here is asked NOT to do, both measured decisions:

* **no lighting and no vertex colour.**  LOOKS-TASK-12 measured that a
  primitive of this format carries no colour field at all: the pixel is a texel
  index through a CLUT, and anything else would be this window inventing shade.
* **no back-face culling.**  The diagonal is measured (`scene.TRIANGLES`), and
  the winding is not: culling on an unverified winding would hide half the
  figure and look like missing geometry.

The GL constants are spelled out below because PySide6 exports none of them --
`QOpenGLFunctions` carries the calls and not the names.  They are numbers of the
API, not offsets into anything, and each is marked as such for the rule-1 sweep.
"""

from __future__ import annotations

import struct

from PySide6 import QtCore, QtGui
from PySide6.QtOpenGL import QOpenGLBuffer, QOpenGLShaderProgram, QOpenGLShader
from PySide6.QtOpenGL import QOpenGLTexture
from PySide6.QtOpenGLWidgets import QOpenGLWidget

GL_LINES = 1
GL_TRIANGLES = 4
GL_FLOAT = 0x1406  # not-an-address: the GL type enum, which PySide6 does not export
GL_DEPTH_TEST = 0x0B71  # not-an-address: idem
GL_COLOR_BUFFER_BIT = 0x4000  # not-an-address: idem
GL_DEPTH_BUFFER_BIT = 0x0100  # not-an-address: idem

FLOATS_PER_VERTEX = 5
"""x, y, z, u, v -- interleaved, one buffer for the whole scene."""

EDGES = ((0, 1), (1, 3), (3, 2), (2, 0))
"""The wireframe: the outline of a quad, and neither diagonal.

**It was (0, 1), (1, 2), (2, 3), (3, 0) until 2026-09-16, and that ring drew
BOTH diagonals.**  The GPU draws a packet as (0, 1, 2) and (1, 2, 3), so the
shared edge is 1-2 and the outline runs 0-1-3-2; the stored order is the packet
order, measured by LOOKS-TASK-17 against the game's display list.  The first
wireframe capture was a lattice of crossing lines, and it read as a busy mesh.
"""

VERTEX_SHADER = """
uniform mat4 mvp;
attribute vec3 position;
attribute vec2 uv;
varying vec2 texcoord;
void main() {
    texcoord = uv;
    gl_Position = mvp * vec4(position, 1.0);
}
"""

FRAGMENT_SHADER = """
uniform sampler2D sheet;
uniform int textured;
uniform vec4 plain;
varying vec2 texcoord;
void main() {
    vec4 colour = plain;
    if (textured == 1) {
        colour = texture2D(sheet, texcoord);
    }
    if (colour.a < 0.5) {
        discard;
    }
    gl_FragColor = colour;
}
"""

BACKGROUND = (0.12, 0.13, 0.16, 1.0)
WIRE_COLOUR = (0.85, 0.87, 0.92, 1.0)

TURN = 360.0
"""Degrees in a full turn -- the orbit wraps rather than running away."""

FRONT = 180.0
"""The yaw that faces the figure, measured by looking at it.

The model looks down -z, so a camera at yaw 0 is behind its head -- a first
render came out as a black skull and looked like a texture failure.  It is a
default and not a fact about the format, which is why it lives here and not in
the core.
"""


class Viewer(QOpenGLWidget):
    """One scene, one camera, two draw modes.

    The camera is orbital in the plain sense: yaw and pitch around the scene's
    own centre, at a distance derived from its own size.  Nothing about it is
    the game's -- the game frames each row of the screen differently, and
    section 5.6 of the plan says reproducing that is guesswork until somebody
    finds the table.
    """

    def __init__(self, scene=None, parent=None):
        super().__init__(parent)
        self._scene = None
        self._groups = []
        self._lines = 0
        self._program = None
        self._buffer = None
        self._line_buffer = None
        self._textures = {}
        self._holders = []
        self.wireframe = False
        self.shelved = True
        self.yaw = FRONT
        self.pitch = 0.0
        self.distance = 3.0
        self._centre = (0.0, 0.0, 0.0)
        self._radius = 1.0
        self._drag = None
        self.set_scene(scene)

    # -- what to draw ------------------------------------------------------

    def set_scene(self, scene, shelved: bool | None = None) -> None:
        """Take a new scene; the buffers are rebuilt at the next paint."""
        self._scene = scene
        if shelved is not None:
            self.shelved = shelved
        self._groups = []
        if scene is not None:
            self._centre, self._radius = self._frame(scene)
        if self.isValid():
            self.makeCurrent()
            self._upload()
            self.doneCurrent()
        self.update()

    def _places(self, scene) -> dict:
        if not self.shelved:
            return {}
        import scene as core  # the core module, which is what knows the layout

        return core.shelf(scene)

    def _frame(self, scene) -> tuple:
        """(centre, radius) of the scene as it will be DRAWN, shelf included."""
        places = self._places(scene)
        lows = [None, None, None]
        highs = [None, None, None]
        for part in scene.parts:
            move = places.get((part.file, part.section), (0.0, 0.0, 0.0))
            for point in part.points:
                for axis in range(3):
                    value = point[axis] + move[axis]
                    lows[axis] = value if lows[axis] is None else min(
                        lows[axis], value)
                    highs[axis] = value if highs[axis] is None else max(
                        highs[axis], value)
        if lows[0] is None:
            return ((0.0, 0.0, 0.0), 1.0)
        centre = tuple((lows[i] + highs[i]) / 2.0 for i in range(3))
        radius = max(max(highs[i] - lows[i] for i in range(3)) / 2.0, 1.0)
        return (centre, radius)

    def _vertices(self) -> tuple:
        """(interleaved triangles by group, interleaved wireframe lines).

        One flat buffer, and the groups are ranges into it: a bind per surface
        is the cost that matters here, and a scene has a handful of surfaces
        and hundreds of primitives.
        """
        scene = self._scene
        import scene as core

        places = self._places(scene)
        by_surface: dict = {}
        for part in scene.parts:
            key = part.surface.key if part.textured else None
            by_surface.setdefault(key, []).append(part)

        data = bytearray()
        lines = bytearray()
        groups = []
        for key in sorted(by_surface, key=lambda k: (k is not None, k)):
            first = len(data) // (4 * FLOATS_PER_VERTEX)
            for part in by_surface[key]:
                move = places.get((part.file, part.section), (0.0, 0.0, 0.0))
                points = [tuple(point[axis] + move[axis] for axis in range(3))
                          for point in part.points]
                for triangle in core.TRIANGLES:
                    for corner in triangle:
                        u, v = part.uvs[corner]
                        data += struct.pack("<5f", *points[corner], u, v)
                for one, two in EDGES:
                    for corner in (one, two):
                        u, v = part.uvs[corner]
                        lines += struct.pack("<5f", *points[corner], u, v)
            count = len(data) // (4 * FLOATS_PER_VERTEX) - first
            groups.append((key, first, count))
        return (bytes(data), bytes(lines), groups)

    # -- GL ---------------------------------------------------------------

    def initializeGL(self) -> None:
        functions = QtGui.QOpenGLContext.currentContext().functions()
        functions.glClearColor(*BACKGROUND)
        functions.glEnable(GL_DEPTH_TEST)

        self._program = QOpenGLShaderProgram(self)
        self._program.addShaderFromSourceCode(
            QOpenGLShader.ShaderTypeBit.Vertex, VERTEX_SHADER)
        self._program.addShaderFromSourceCode(
            QOpenGLShader.ShaderTypeBit.Fragment, FRAGMENT_SHADER)
        if not self._program.link():
            raise RuntimeError("the shaders did not link: %s"
                               % self._program.log())
        self._upload()

    def _upload(self) -> None:
        """Buffers and textures for the current scene, discarding the old."""
        for texture in self._textures.values():
            texture.destroy()
        self._textures = {}
        self._holders = []
        self._groups = []
        self._lines = 0
        if self._scene is None or self._program is None:
            return

        data, lines, groups = self._vertices()
        for buffer_name, payload in (("_buffer", data),
                                     ("_line_buffer", lines)):
            buffer = getattr(self, buffer_name)
            if buffer is None:
                buffer = QOpenGLBuffer(QOpenGLBuffer.Type.VertexBuffer)
                buffer.create()
                setattr(self, buffer_name, buffer)
            buffer.bind()
            buffer.allocate(payload, len(payload))
            buffer.release()
        self._groups = groups
        self._lines = len(lines) // (4 * FLOATS_PER_VERTEX)

        for key, _first, _count in groups:
            if key is None:
                continue
            surface = self._scene.surfaces[key]
            # The bytes have to outlive the QImage, which does not copy them.
            self._holders.append(surface.rgba)
            image = QtGui.QImage(surface.rgba, surface.width, surface.height,
                                 surface.width * 4,
                                 QtGui.QImage.Format.Format_RGBA8888)
            texture = QOpenGLTexture(image)
            # Nearest, because a texel here IS the measurement: smoothing
            # mixes two palette entries and invents a colour the disc has not
            # got.
            texture.setMinificationFilter(QOpenGLTexture.Filter.Nearest)
            texture.setMagnificationFilter(QOpenGLTexture.Filter.Nearest)
            texture.setWrapMode(QOpenGLTexture.WrapMode.ClampToEdge)
            self._textures[key] = texture

    def _camera(self) -> QtGui.QMatrix4x4:
        matrix = QtGui.QMatrix4x4()
        ratio = self.width() / float(max(self.height(), 1))
        matrix.perspective(45.0, ratio, 0.1, self._radius * 100.0)
        eye = QtGui.QVector3D(0.0, 0.0, self._radius * self.distance)
        matrix.lookAt(eye, QtGui.QVector3D(0.0, 0.0, 0.0),
                      QtGui.QVector3D(0.0, 1.0, 0.0))
        matrix.rotate(self.pitch, 1.0, 0.0, 0.0)
        matrix.rotate(self.yaw, 0.0, 1.0, 0.0)
        matrix.translate(-self._centre[0], -self._centre[1], -self._centre[2])
        return matrix

    def paintGL(self) -> None:
        functions = QtGui.QOpenGLContext.currentContext().functions()
        functions.glClearColor(*BACKGROUND)
        functions.glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        if self._program is None or not self._groups:
            return

        self._program.bind()
        self._program.setUniformValue("mvp", self._camera())
        stride = 4 * FLOATS_PER_VERTEX
        buffer = self._line_buffer if self.wireframe else self._buffer
        buffer.bind()
        self._program.enableAttributeArray("position")
        self._program.enableAttributeArray("uv")
        self._program.setAttributeBuffer("position", GL_FLOAT, 0, 3, stride)
        self._program.setAttributeBuffer("uv", GL_FLOAT, 12, 2, stride)

        if self.wireframe:
            self._program.setUniformValue1i("textured", 0)
            self._program.setUniformValue("plain", QtGui.QVector4D(*WIRE_COLOUR))
            functions.glDrawArrays(GL_LINES, 0, self._lines)
        else:
            import scene as core

            for key, first, count in self._groups:
                if key is None:
                    self._program.setUniformValue1i("textured", 0)
                    self._program.setUniformValue(
                        "plain", QtGui.QVector4D(
                            *[channel / 255.0 for channel in core.PLACEHOLDER]))
                else:
                    # setUniformValue1i and not setUniformValue: an int handed
                    # to the general form arrives as something the sampler and
                    # the flag both read as zero, and the whole figure came out
                    # in the placeholder colour with no error anywhere.
                    self._textures[key].bind()
                    self._program.setUniformValue1i("textured", 1)
                    self._program.setUniformValue1i("sheet", 0)
                functions.glDrawArrays(GL_TRIANGLES, first, count)

        self._program.disableAttributeArray("position")
        self._program.disableAttributeArray("uv")
        buffer.release()
        self._program.release()

    def resizeGL(self, width: int, height: int) -> None:
        functions = QtGui.QOpenGLContext.currentContext().functions()
        functions.glViewport(0, 0, width, height)

    # -- the camera, driven -------------------------------------------------

    def orbit(self, yaw: float, pitch: float) -> None:
        """Turn the camera.  Named so a gate can drive it without a mouse."""
        self.yaw = (self.yaw + yaw) % TURN
        self.pitch = max(-89.0, min(89.0, self.pitch + pitch))
        self.update()

    def zoom(self, factor: float) -> None:
        self.distance = max(0.5, min(20.0, self.distance * factor))
        self.update()

    def set_wireframe(self, on: bool) -> None:
        self.wireframe = bool(on)
        self.update()

    def mousePressEvent(self, event) -> None:
        self._drag = event.position()

    def mouseMoveEvent(self, event) -> None:
        if self._drag is None:
            return
        here = event.position()
        self.orbit((here.x() - self._drag.x()) / 2.0,
                   (here.y() - self._drag.y()) / 2.0)
        self._drag = here

    def mouseReleaseEvent(self, event) -> None:
        self._drag = None

    def wheelEvent(self, event) -> None:
        steps = event.angleDelta().y() / 120.0
        self.zoom(0.9 ** steps)

    def keyPressEvent(self, event) -> None:
        if event.key() == QtCore.Qt.Key.Key_W:
            self.set_wireframe(not self.wireframe)
        elif event.key() == QtCore.Qt.Key.Key_S:
            self.shelved = not self.shelved
            self.set_scene(self._scene)
        else:
            super().keyPressEvent(event)

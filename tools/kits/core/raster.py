"""The 3D figure drawn in software, pixel by pixel (KITS-AJUSTES-3D.md G6).

The 3D tab and `cli.py holes` draw the same picture from here: the scene
turned by yaw and pitch, fitted to the target, and every triangle filled pixel
by pixel.  At each pixel the nearest opaque triangle wins (a depth buffer), the
texel is the nearest one to the (u, v) interpolated from the screen triangle,
and a transparent texel writes neither colour nor depth -- so what lies behind
it shows.  Interpolating from the screen means a triangle whose UV triangle
has no area (a corner repeated, or three in a line) still paints: it samples
the texels along that line, as the PlayStation's GPU does.

`order=MEAN` and `skip_degenerate=True` are the drawing the view had before
(KITS-TASK-25): back to front by each triangle's mean depth, and a triangle
with no UV area left out.  They stay as the controls the hole count is
measured against, never as what is shown.

The camera is the view's: orthographic, model y up and screen y down, screen
x minus model x (the scene is left-handed), the figure's bounds fitted to the
smaller side less MARGIN on each edge.  A dressed figure is fitted by the
points of the figure before dressing (`notes["fit"]`, set by
`figure.dressed_scene`), so ticking a box draws the armband or the sleeve on
the same frame instead of moving the whole figure (CORR-K3D-016).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

MARGIN = 0.08
"""Fraction of the target left around the figure (the view's fit)."""
FIT = "fit"
"""The scene note holding the points the view is fitted by, when not the parts'."""
DEPTH, MEAN = "depth", "mean"
ORDERS = (DEPTH, MEAN)
"""Per-pixel depth, the drawing; per-triangle mean depth, the old one."""
UNTEXTURED = (0xB0, 0xB0, 0xB0)
"""The colour of a part with no surface (the view's UNTEXTURED)."""
DEPTH_TIE = 1e-6
"""How close two depths are before they are a tie, won by the one painted last."""
OPAQUE, TRANSPARENT, UNMAPPED = "opaque", "transparent", "unmapped"


def turn(point, yaw: float, pitch: float) -> tuple:
    """*point* turned by *yaw* about y, then *pitch* about x (degrees)."""
    x, y, z = point
    a, b = math.radians(yaw), math.radians(pitch)
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
    return x, y, z


@dataclass
class Raster:
    """One drawn picture.  `rgba` is width x height RGBA, alpha 0 where no
    triangle painted.  Per pixel, row by row: `shown` the fragment painted
    there and `nearest` the nearest fragment of any kind, each None or
    (depth, part index, kind, texel or None, paint step)."""

    width: int
    height: int
    rgba: bytearray
    shown: list
    nearest: list


def draw(drawn, yaw: float, pitch: float, width: int, height: int, triangles,
         order: str = DEPTH, skip_degenerate: bool = False) -> Raster:
    """*drawn* (a looks Scene) turned to (*yaw*, *pitch*), drawn into a
    *width* x *height* picture (see the module docstring).  *triangles* is how
    a part's four corners split into two (`figure.TRIANGLES`, the looks' own):
    this module reads no looks module, section 3.1."""
    if order not in ORDERS:
        raise ValueError("order is one of %s, not %r" % (ORDERS, order))
    size = width * height
    rgba = bytearray(size * 4)
    shown = [None] * size
    nearest = [None] * size
    raster = Raster(width, height, rgba, shown, nearest)
    parts = drawn.parts
    if not parts:
        return raster
    fit = drawn.notes.get(FIT) if isinstance(drawn.notes, dict) else None
    if fit:
        centre = tuple((min(p[i] for p in fit) + max(p[i] for p in fit)) / 2.0
                       for i in range(3))
    else:
        centre = drawn.centre()
    turned = [[turn(tuple(p[i] - centre[i] for i in range(3)), yaw, pitch)
               for p in part.points] for part in parts]
    framed = [turn(tuple(p[i] - centre[i] for i in range(3)), yaw, pitch)
              for p in fit] if fit else [p for pts in turned for p in pts]
    xs = [p[0] for p in framed]
    ys = [p[1] for p in framed]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    scale = min(width, height) * (1.0 - 2 * MARGIN) / span
    mx, my = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
    cx, cy = width / 2.0, height / 2.0
    work = []
    for n, (part, pts) in enumerate(zip(parts, turned)):
        screen = [(cx - (p[0] - mx) * scale, cy - (p[1] - my) * scale, p[2]) for p in pts]
        for tri in triangles:
            work.append((sum(pts[i][2] for i in tri) / 3.0, n,
                         [screen[i] for i in tri], [part.uvs[i] for i in tri]))
    work.sort(key=lambda t: t[0])           # back to front: the old order, and the tie-break
    for step, (_, n, tri, uvs) in enumerate(work):
        surface = parts[n].surface
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-12:
            continue
        unmapped = False
        if surface is not None:
            sw, sh, data = surface.width, surface.height, surface.rgba
            (u0, v0), (u1, v1), (u2, v2) = ((u * sw, v * sh) for u, v in uvs)
            unmapped = skip_degenerate and \
                abs((u1 - u0) * (v2 - v0) - (u2 - u0) * (v1 - v0)) < 1e-9
        for py in range(max(0, int(min(y0, y1, y2))), min(height, int(max(y0, y1, y2)) + 1)):
            sy = py + 0.5
            row = py * width
            for px in range(max(0, int(min(x0, x1, x2))), min(width, int(max(x0, x1, x2)) + 1)):
                sx = px + 0.5
                a = ((x1 - sx) * (y2 - sy) - (x2 - sx) * (y1 - sy)) / area
                b = ((x2 - sx) * (y0 - sy) - (x0 - sx) * (y2 - sy)) / area
                g = 1.0 - a - b
                if a < 0 or b < 0 or g < 0:
                    continue
                depth = a * z0 + b * z1 + g * z2
                at = row + px
                if unmapped:
                    frag = (depth, n, UNMAPPED, None, step)
                    colour = None
                elif surface is None:
                    frag = (depth, n, OPAQUE, None, step)
                    colour = UNTEXTURED + (255,)
                else:
                    tx = min(sw - 1, max(0, int(a * u0 + b * u1 + g * u2)))
                    ty = min(sh - 1, max(0, int(a * v0 + b * v1 + g * v2)))
                    k = (ty * sw + tx) * 4
                    if data[k + 3]:
                        frag = (depth, n, OPAQUE, (tx, ty), step)
                        colour = data[k:k + 4]
                    else:
                        frag = (depth, n, TRANSPARENT, (tx, ty), step)
                        colour = None
                near = nearest[at]
                if near is None or depth >= near[0] - DEPTH_TIE:
                    nearest[at] = frag
                if colour is None:
                    continue
                here = shown[at]
                if order == MEAN or here is None or depth >= here[0] - DEPTH_TIE:
                    shown[at] = frag
                    rgba[at * 4:at * 4 + 4] = bytes(colour)
    return raster

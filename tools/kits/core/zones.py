"""The zone map of the work bitmap, as data, and its confrontation with the geometry.

PLAN-KITS-PY.md sections 3.1 and 4.6.  The map is the community's: every
rectangle of `ZONES` was measured on polipoli's `Zonas We2002.png` (solid
colour components of the 256x128 work bitmap, names from his
`Zonas We2002 explicadas.png`), as SUPERPACK-UNIFORMES sections 2.1 and 2.2
transcribe it.  `MEASURES` are ramonpsx's piece sizes (`Medidas TEX
we2002.txt`), kept beside the map to say where the two readings agree.  Each
row names who it came from in its `source`.

`GAPS` are not the community's: they are what the game samples and the map
leaves without a zone, measured by KITS-TASK-16 on the draw list of the
LOOKS SET (`cli.py uv`).  `confront()` is the section 4.6 check: every UV
rect of the figure lies in the zones or in a declared gap, and every zone
nobody samples carries the reason in its `unsampled`.

Coordinates are work-bitmap pixels: x 0-127 the uniform image, 128-255 the
sleeves image (flat.work_bitmap).  Nothing here prints or reads a file but
`confront_image()`, which reads the disc through `survey.uv_image()`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Optional

from .flat import WORK_H, WORK_W

POLIPOLI = "polipoli"
"""Zonas kits y tex - polipoli/We2002/Zonas We2002.png (the map)."""
RAMONPSX = "ramonpsx"
"""Medidas TEX we2002.txt, with ramonpsx's Pes6-to-WE2002 resizer (the sizes)."""
MEASURED = "KITS-TASK-16"
"""Measured here, on the disc: the gaps."""
SOURCES = (POLIPOLI, RAMONPSX, MEASURED)

PLAYER, KEEPER, SHARED = 0, 1, None
"""Figure numbers of `looks`; SHARED is a zone both figures use."""

WHY_SLEEVES = ("the sleeves image is sampled by no primitive of the LOOKS SET "
               "(PLAN-KITS-PY.md section 4.3): long sleeve and armband are "
               "geometry this screen does not draw")
WHY_NUMBERS = ("no primitive of the LOOKS SET samples the shirt numbers; who "
               "draws them is not on this screen")


@dataclass(frozen=True)
class Zone:
    """One rectangle of the map: inclusive left/top, width and height."""

    name: str
    figure: Optional[int]
    x: int
    y: int
    w: int
    h: int
    source: str
    unsampled: str = ""      # why no primitive samples it; "" when one has to

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    @property
    def rect(self) -> tuple:
        """(x0, y0, x1, y1), inclusive, as the UV rects are."""
        return (self.x, self.y, self.x + self.w - 1, self.y + self.h - 1)


def _z(name, figure, x, y, w, h, unsampled=""):
    return Zone(name, figure, x, y, w, h, POLIPOLI, unsampled)


ZONES = (
    # uniform image (SUPERPACK-UNIFORMES 2.1): player x 0-63, goalkeeper x 64-127
    _z("shoulder, first", PLAYER, 4, 0, 16, 8),
    _z("shoulder, second", PLAYER, 24, 0, 16, 8),
    _z("shoulder, first", KEEPER, 68, 0, 16, 8),
    _z("shoulder, second", KEEPER, 88, 0, 16, 8),
    _z("shirt side, first", PLAYER, 0, 8, 12, 22),
    _z("shirt side, second", PLAYER, 32, 8, 12, 22),
    _z("shirt side, first", KEEPER, 64, 8, 12, 22),
    _z("shirt side, second", KEEPER, 96, 8, 12, 22),
    # the front is no rectangle: its collar climbs between the shoulders
    _z("shirt front", PLAYER, 12, 8, 20, 22),
    _z("shirt front, collar", PLAYER, 20, 7, 4, 1),
    _z("shirt front, collar tip, first", PLAYER, 20, 6, 1, 1),
    _z("shirt front, collar tip, second", PLAYER, 23, 6, 1, 1),
    _z("shirt front", KEEPER, 76, 8, 20, 22),
    _z("shirt front, collar", KEEPER, 84, 7, 4, 1),
    _z("shirt front, collar tip, first", KEEPER, 84, 6, 1, 1),
    _z("shirt front, collar tip, second", KEEPER, 87, 6, 1, 1),
    _z("shirt back", PLAYER, 44, 0, 20, 30),
    _z("shirt back", KEEPER, 108, 0, 20, 30),
    _z("shorts side, first", PLAYER, 0, 30, 12, 18),
    _z("shorts front", PLAYER, 12, 30, 20, 18),
    _z("shorts side, second", PLAYER, 32, 30, 12, 18),
    _z("shorts back", PLAYER, 44, 30, 20, 18),
    _z("shorts", KEEPER, 64, 30, 32, 18),
    _z("socks", PLAYER, 0, 48, 32, 18),
    _z("socks", KEEPER, 96, 30, 32, 18),
    _z("crotch", PLAYER, 32, 48, 16, 18),
    _z("crotch", KEEPER, 56, 48, 8, 18),
    _z("elbow", KEEPER, 48, 48, 8, 8),
    _z("sleeve, shoulder to elbow", KEEPER, 64, 48, 32, 15),
    _z("forearm", KEEPER, 96, 48, 32, 9),
    _z("gloves", KEEPER, 96, 57, 32, 11),
    _z("short sleeve, right", PLAYER, 0, 66, 32, 14),
    _z("short sleeve, left", PLAYER, 32, 66, 32, 14),
    _z("numbers 0-9", SHARED, 64, 68, 60, 12, WHY_NUMBERS),
    # sleeves image (SUPERPACK-UNIFORMES 2.2): the column x 160-191
    _z("long sleeve, left forearm", PLAYER, 160, 0, 32, 14, WHY_SLEEVES),
    _z("long sleeve, left, captain", PLAYER, 160, 14, 32, 6, WHY_SLEEVES),
    _z("armband, long sleeve", PLAYER, 160, 20, 32, 5, WHY_SLEEVES),
    _z("long sleeve, left, captain, under the armband", PLAYER, 160, 25, 32, 3, WHY_SLEEVES),
    _z("long sleeve, left", PLAYER, 160, 28, 32, 14, WHY_SLEEVES),
    _z("long sleeve, right", PLAYER, 160, 42, 32, 14, WHY_SLEEVES),
    _z("short sleeve, left, captain", KEEPER, 160, 56, 32, 7, WHY_SLEEVES),
    _z("armband, short sleeve", KEEPER, 160, 63, 32, 5, WHY_SLEEVES),
    _z("short sleeve, left, captain, under the armband", KEEPER, 160, 68, 32, 3, WHY_SLEEVES),
    _z("short sleeve, left, captain", PLAYER, 160, 71, 32, 6, WHY_SLEEVES),
    _z("armband, short sleeve", PLAYER, 160, 77, 32, 5, WHY_SLEEVES),
    _z("short sleeve, left, captain, under the armband", PLAYER, 160, 82, 32, 3, WHY_SLEEVES),
    _z("elbow, left", SHARED, 160, 85, 8, 8, WHY_SLEEVES),
    _z("elbow, right", SHARED, 184, 85, 8, 8, WHY_SLEEVES),
    _z("long sleeve, right forearm", PLAYER, 160, 93, 32, 14, WHY_SLEEVES),
)


@dataclass(frozen=True)
class Measure:
    """One piece size of ramonpsx's table, and the zones of the map it is
    compared with (side by side: widths add, the height is the tallest)."""

    piece: str
    figure: int
    w: int
    h: int
    zones: tuple             # zone names of the same figure; () when the map has none
    source: str = RAMONPSX


MEASURES = (
    Measure("frente", PLAYER, 22, 22, ("shirt front",)),
    Measure("costados", PLAYER, 12, 22, ("shirt side, first",)),
    Measure("espalda", PLAYER, 20, 25, ("shirt back",)),
    Measure("hombros", PLAYER, 16, 8, ("shoulder, first",)),
    Measure("short", PLAYER, 64, 18, ("shorts side, first", "shorts front",
                                      "shorts side, second", "shorts back")),
    Measure("short (entrepierna)", PLAYER, 16, 18, ("crotch",)),
    Measure("medias", PLAYER, 32, 18, ("socks",)),
    Measure("mangas", PLAYER, 32, 14, ("short sleeve, right",)),
    Measure("playera metida", PLAYER, 20, 5, ()),
    Measure("frente", KEEPER, 22, 22, ("shirt front",)),
    Measure("costados", KEEPER, 12, 22, ("shirt side, first",)),
    Measure("espalda", KEEPER, 20, 25, ("shirt back",)),
    Measure("hombros", KEEPER, 16, 8, ("shoulder, first",)),
    Measure("short", KEEPER, 64, 18, ("shorts",)),
    Measure("short (entrepierna)", KEEPER, 8, 18, ("crotch",)),
    Measure("short lado 1 + 2 + 3 (10 + 12 + 10)", KEEPER, 32, 18, ("shorts",)),
    Measure("medias", KEEPER, 32, 18, ("socks",)),
    Measure("manga", KEEPER, 32, 15, ("sleeve, shoulder to elbow",)),
    Measure("manga larga", KEEPER, 32, 9, ("forearm",)),
    Measure("codo", KEEPER, 8, 8, ("elbow",)),
    Measure("playera metida", KEEPER, 20, 5, ()),
)


@dataclass(frozen=True)
class Gap:
    """A rectangle the game samples and the map leaves without a zone."""

    name: str
    figure: int
    x: int
    y: int
    w: int
    h: int
    why: str
    source: str = MEASURED

    def contains(self, x: int, y: int) -> bool:
        return self.x <= x < self.x + self.w and self.y <= y < self.y + self.h

    @property
    def rect(self) -> tuple:
        return (self.x, self.y, self.x + self.w - 1, self.y + self.h - 1)


WHY_TORSO = ("primitives of the torso section sample it with the kit's "
             "palette; the map calls everything under y 80 unused")
WHY_NOTCH = ("the collar quad spans the notch between the shoulders, which the "
             "map leaves unused; the quad's rect, not a rasterisation")

GAPS = (
    Gap("torso, under the map", PLAYER, 0, 80, 20, 24, WHY_TORSO),
    Gap("torso, under the map", KEEPER, 100, 104, 20, 24, WHY_TORSO),
    Gap("collar, the notch between the shoulders", PLAYER, 20, 5, 4, 1, WHY_NOTCH),
    Gap("collar, between its tips", PLAYER, 21, 6, 2, 1, WHY_NOTCH),
    Gap("collar, the notch between the shoulders", KEEPER, 84, 5, 4, 1, WHY_NOTCH),
    Gap("collar, between its tips", KEEPER, 85, 6, 2, 1, WHY_NOTCH),
)

MAP_BACKGROUND = (255, 255, 0)
"""The colour polipoli's map paints what it calls unused."""
GLYPH_ZONES = ("numbers 0-9",)
"""Zones whose content is drawn on the background (the digits), so their
rectangle holds background pixels by design."""


def zone_at(x: int, y: int, zones=ZONES) -> Optional[Zone]:
    """The zone of the map at work-bitmap pixel (x, y), or None."""
    for z in zones:
        if z.contains(x, y):
            return z
    return None


def shifted(zones=ZONES, dx: int = 1, dy: int = 0) -> tuple:
    """The map moved by (dx, dy): section 5, control 4."""
    return tuple(replace(z, x=z.x + dx, y=z.y + dy) for z in zones)


def agreement(measures=MEASURES, zones=ZONES) -> tuple:
    """((Measure, map size or None), ...): ramonpsx's size against the map's,
    the named zones side by side."""
    out = []
    for m in measures:
        found = [next((z for z in zones if z.name == n and z.figure == m.figure), None)
                 for n in m.zones]
        if not found or None in found:
            out.append((m, None))
            continue
        out.append((m, (sum(z.w for z in found), max(z.h for z in found))))
    return tuple(out)


# -- the confrontation of section 4.6 ---------------------------------------

IN_ZONE = "in one zone"
ACROSS = "across zones"
IN_GAP = "in a declared gap"
OUTSIDE = "outside the map"
CLASSES = (IN_ZONE, ACROSS, IN_GAP, OUTSIDE)


@dataclass(frozen=True)
class Placed:
    """One UV rect and where it falls."""

    figure: int
    file: str
    section: int
    primitive: int
    rect: Optional[tuple]
    klass: str
    zones: tuple             # names of the zones it touches
    gaps: tuple              # names of the gaps holding its uncovered pixels
    uncovered: int           # its pixels in no zone


@dataclass(frozen=True)
class Confrontation:
    placed: tuple            # Placed, figure by figure
    sampled: tuple           # (Zone, primitives touching it), map order
    zones: tuple
    gaps: tuple

    def count(self, figure: int, klass: str) -> int:
        return sum(1 for p in self.placed if p.figure == figure and p.klass == klass)

    @property
    def outside(self) -> tuple:
        return tuple(p for p in self.placed if p.klass == OUTSIDE)

    @property
    def unsampled_unexplained(self) -> tuple:
        """Zones no primitive samples and that say no reason."""
        return tuple(z for z, n in self.sampled if not n and not z.unsampled)

    @property
    def sampled_but_excused(self) -> tuple:
        """Zones that say why nobody samples them, and somebody does."""
        return tuple(z for z, n in self.sampled if n and z.unsampled)

    @property
    def gaps_unused(self) -> tuple:
        used = {g for p in self.placed for g in p.gaps}
        return tuple(g for g in self.gaps if (g.name, g.figure) not in used)

    @property
    def ok(self) -> bool:
        return not (self.outside or self.unsampled_unexplained
                    or self.sampled_but_excused or self.gaps_unused)


def _pixels(rect):
    x0, y0, x1, y1 = rect
    return [(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)]


def place(figure: int, uv_rect, zones=ZONES, gaps=GAPS) -> Placed:
    """Where one `survey.UvRect` falls.  A rect the survey could not map (it
    leaves the bitmap or splits its corners between images) is outside."""
    key = dict(figure=figure, file=uv_rect.file, section=uv_rect.section,
               primitive=uv_rect.primitive, rect=uv_rect.rect)
    if uv_rect.outside or uv_rect.rect is None:
        return Placed(klass=OUTSIDE, zones=(), gaps=(), uncovered=0, **key)
    touched, held, uncovered, loose = [], [], 0, 0
    for x, y in _pixels(uv_rect.rect):
        z = zone_at(x, y, zones)
        if z is not None:
            if z not in touched:
                touched.append(z)
            continue
        uncovered += 1
        g = next((g for g in gaps if g.figure == figure and g.contains(x, y)), None)
        if g is None:
            loose += 1
        elif g not in held:
            held.append(g)
    if loose:
        klass = OUTSIDE
    elif uncovered:
        klass = IN_GAP
    elif len(touched) == 1:
        klass = IN_ZONE
    else:
        klass = ACROSS
    return Placed(klass=klass, zones=tuple(z.name for z in touched),
                  gaps=tuple((g.name, g.figure) for g in held), uncovered=uncovered, **key)


def confront(uv_report, zones=ZONES, gaps=GAPS) -> Confrontation:
    """Section 4.6 on a `survey.UvReport`.  Pure."""
    placed = []
    hits = {z: 0 for z in zones}
    for fig in uv_report.figures:
        for r in fig.rects:
            p = place(fig.figure, r, zones, gaps)
            placed.append(p)
            if p.rect is None:
                continue
            for z in zones:
                x0, y0, x1, y1 = p.rect
                zx0, zy0, zx1, zy1 = z.rect
                if not (x1 < zx0 or zx1 < x0 or y1 < zy0 or zy1 < y0):
                    hits[z] += 1
    return Confrontation(placed=tuple(placed), sampled=tuple((z, hits[z]) for z in zones),
                         zones=tuple(zones), gaps=tuple(gaps))


def confront_image(image_path: str, zones=ZONES, gaps=GAPS) -> Confrontation:
    """confront() on the UV rects of the disc at *image_path* (`cli.py uv`)."""
    from . import survey

    return confront(survey.uv_image(image_path), zones, gaps)


# -- the map against polipoli's PNG -------------------------------------------

@dataclass(frozen=True)
class MapCheck:
    """`ZONES` against the picture they were measured on."""

    loose: tuple             # (x, y) painted in the picture and in no zone
    background: tuple        # (Zone, background pixels inside it), when any

    @property
    def unexpected_background(self) -> tuple:
        return tuple((z, n) for z, n in self.background if z.name not in GLYPH_ZONES)

    @property
    def ok(self) -> bool:
        return not self.loose and not self.unexpected_background


def map_check(width: int, height: int, pixels, zones=ZONES) -> MapCheck:
    """*pixels* is the picture's (r, g, b) row by row.  Every painted pixel
    has to fall in a zone of the polipoli rows, and no zone may hold the
    background but the digits.  Pure."""
    if (width, height) != (WORK_W, WORK_H):
        raise ValueError("the map is %dx%d, not %dx%d" % (width, height, WORK_W, WORK_H))
    ours = [z for z in zones if z.source == POLIPOLI]
    loose, background = [], {}
    for y in range(height):
        for x in range(width):
            painted = tuple(pixels[y * width + x][:3]) != MAP_BACKGROUND
            z = zone_at(x, y, ours)
            if z is None and painted:
                loose.append((x, y))
            elif z is not None and not painted:
                background[z] = background.get(z, 0) + 1
    return MapCheck(loose=tuple(loose),
                    background=tuple((z, background[z]) for z in ours if z in background))


# -- self-check --------------------------------------------------------------

def _overlap(a, b) -> bool:
    ax0, ay0, ax1, ay1 = a.rect
    bx0, by0, bx1, by1 = b.rect
    return not (ax1 < bx0 or bx1 < ax0 or ay1 < by0 or by1 < ay0)


def self_check() -> list:
    """The map's own invariants; a list of failure sentences, empty when sound.

    The map is a partition by colour, so no two zones overlap; every row is
    inside the 256x128 and says its source; a gap overlaps no zone; every
    measure names zones the map has.
    """
    bad = []
    for z in ZONES + GAPS:
        if not (0 <= z.x and 0 <= z.y and z.x + z.w <= WORK_W and z.y + z.h <= WORK_H):
            bad.append("%s (figure %s) leaves the %dx%d" % (z.name, z.figure, WORK_W, WORK_H))
        if z.source not in SOURCES:
            bad.append("%s (figure %s) has no known source: %r" % (z.name, z.figure, z.source))
    for i, a in enumerate(ZONES):
        for b in ZONES[i + 1:]:
            if _overlap(a, b):
                bad.append("zones overlap: %s (figure %s) and %s (figure %s)"
                           % (a.name, a.figure, b.name, b.figure))
    for g in GAPS:
        for z in ZONES:
            if _overlap(g, z):
                bad.append("gap %s (figure %s) overlaps zone %s" % (g.name, g.figure, z.name))
    names = {(z.name, z.figure) for z in ZONES}
    for m in MEASURES:
        for n in m.zones:
            if (n, m.figure) not in names:
                bad.append("measure %s (figure %s) names no zone %r" % (m.piece, m.figure, n))
    return bad

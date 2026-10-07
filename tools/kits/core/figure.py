"""The one bridge between the kits core and the `looks` scene.

PLAN-KITS-PY.md section 3.1: `figure.py` asks the `scene` of `tools/looks/`
for the 3D figure, and no other module of the core does.  The geometry --
`EDT_MOD.BIN`, `MODEL.BIN`, `DAT2D.BIN`, `ANIME.BIN` -- comes from a disc the
looks guard trusts (section 2.1); the kit comes from wherever the user took it,
as the bytes `tex` already put behind the guard of form, so a TEX off a patch
or out of a file is drawn on the trusted body.

    scene = figure.scene_of(kit, kit_set, figure, geometry_path=None, frame=None)

`geometry_path=None` means `WE2002_LOOKS_IMAGE`; with neither, `NoGeometry`
says so in a sentence.  A disc the looks guard refuses is `GeometryRefused`.

`match_scene` is the match figure of section 4.3 (KITS-TASK-47): MODEL.BIN's
sections in the order and pose the game drew them in (`match_pose.json`,
written by `oracle.py --match-pose 5 --write`), with the captain's armband or
not and long or short sleeves.

`palette_swap` is control 4 of section 5: the kit with its player (486) and
goalkeeper (488) palettes swapped has to draw each figure in the other one's
colours, surface by surface.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, replace

from . import tex  # noqa: F401  (puts tools/pes2 and tools/looks on sys.path)
from .errors import FigureError, GeometryRefused, NoGeometry

import assembly  # noqa: E402  (tools/looks)
import atlas  # noqa: E402
import layout  # noqa: E402
import looks  # noqa: E402
import scene  # noqa: E402
import skin  # noqa: E402
import texture  # noqa: E402

GEOMETRY_ENV = "WE2002_LOOKS_IMAGE"
GEOMETRY_FILES = (layout.EDT_MOD, layout.MODEL, layout.DAT2D, layout.ANIME)
TUPLE = assembly.CORPUS_REFERENCE
"""The looks the figure wears: the reference tuple of the looks corpus."""
POSE_FRAME = scene.REFERENCE_FRAME
"""The frame a figure is posed in for viewing: the screen's own reference pose
(`None` would be the looks shelf, every piece at its file's origin)."""
TRIANGLES = scene.TRIANGLES
"""How a part's four corners become two triangles, as the looks draws them."""
FIGURES = (0, 1)
"""0: the outfield player, 1: the goalkeeper (the figure numbers of `looks`)."""
KIT_SETS = texture.KIT_SETS
PLAYER_ROW, KEEPER_ROW = 486, 488  # not-an-address: VRAM rows of the two palettes (section 1.1)
SLOT = layout.kit_path(layout.KIT_ON_SCREEN)
"""The name the kit's bytes go under in the files the scene reads.  A name
only: the bytes are the kit's, whatever disc or file they came from."""


def geometry_path_for(path=None) -> str:
    """*path*, or `WE2002_LOOKS_IMAGE`, or `NoGeometry`."""
    path = path or os.environ.get(GEOMETRY_ENV)
    if not path:
        raise NoGeometry("The 3D figure needs the Japanese disc for its geometry: "
                         "set %s to its data track (.bin)." % GEOMETRY_ENV)
    return path


def read_geometry(path: str) -> dict:
    """The four files the figure is built from, through the looks disc guard."""
    import iso_source

    try:
        with iso_source.open_disc(path) as disc:
            return {name: disc.read(name) for name in GEOMETRY_FILES}
    except OSError as exc:
        raise GeometryRefused("Could not open %s for the figure's geometry: %s"
                              % (path, exc.strerror or exc)) from exc
    except layout.WrongDisc as exc:
        raise GeometryRefused("%s cannot give the figure's geometry: %s" % (path, exc)) from exc
    except ValueError as exc:
        raise GeometryRefused("%s is not a readable data track: %s" % (path, exc)) from exc


def scene_of(kit, kit_set: int = 1, figure: int = 0, geometry_path=None, frame=None,
             geometry=None):
    """The looks `Scene` of *figure* wearing set *kit_set* of *kit*.

    *geometry* is the dict `read_geometry` gives, for a caller drawing more
    than one figure off the same disc."""
    if kit_set not in KIT_SETS:
        raise FigureError("Kit set %r is not one of %s." % (kit_set, KIT_SETS))
    if figure not in FIGURES:
        raise FigureError("Figure %r is not one of %s (0 player, 1 goalkeeper)."
                          % (figure, FIGURES))
    if geometry is None:
        geometry = read_geometry(geometry_path_for(geometry_path))
    kit.require()
    files = dict(geometry)
    files[SLOT] = kit.data
    try:
        built = scene.build(files, looks.parse_tuple(TUPLE), figure, frame,
                            layout.KIT_ON_SCREEN, kit_set)
    except (scene.BadScene, assembly.BadAssembly, texture.BadTable) as exc:
        raise FigureError("%s cannot be drawn on the figure: %s" % (kit.label, exc)) from exc
    # The game copies the shirt back into the torso gap on every LOOKS SET
    # figure (BACK_COPY, measured), number or not: drawn without it the back
    # showed through (KITS-AJUSTES-3D.md G5, K3D-TASK-05).
    return numbered_scene(built, kit, kit_set, figure, None)


# -- control 4 of section 5: swapping 486 and 488 -----------------------------------

def swapped_palettes(data: bytes, kit_set: int) -> bytes:
    """*data* with set *kit_set*'s player and goalkeeper palettes swapped."""
    records = texture.in_set_order(texture.palettes(data), kit_set)
    player = next(r for r in records if r.y == PLAYER_ROW)
    keeper = next(r for r in records if r.y == KEEPER_ROW)
    size = player.colours * 2
    out = bytearray(data)
    out[player.offset:player.offset + size] = data[keeper.offset:keeper.offset + size]
    out[keeper.offset:keeper.offset + size] = data[player.offset:player.offset + size]
    return bytes(out)


@dataclass(frozen=True)
class SwapControl:
    """Control 4: `ok` when every kit surface of the swapped figure is the
    original kit's indices through the OTHER figure's palette row."""

    figure: int
    kit_set: int
    rows: tuple          # the palette rows the figure's kit surfaces sample
    surfaces: int        # kit surfaces compared
    wrong: tuple         # sentences, one per surface that is not swapped

    @property
    def ok(self) -> bool:
        return self.surfaces > 0 and not self.wrong


def palette_swap(kit, kit_set: int, figure: int, geometry: dict) -> SwapControl:
    """Draws *figure* with the kit's 486/488 swapped and checks every kit
    surface against the original kit read at the other row."""
    swapped = replace(kit, data=swapped_palettes(kit.data, kit_set))
    drawn = scene_of(swapped, kit_set, figure, geometry=geometry)
    other = {PLAYER_ROW: KEEPER_ROW, KEEPER_ROW: PLAYER_ROW}
    images = {r.offset: r for r in texture.images(kit.data)}
    palettes = texture.in_set_order(texture.palettes(kit.data), kit_set)
    rows, wrong, compared = set(), [], 0
    for key, surface in sorted(drawn.surfaces.items(), key=lambda kv: repr(kv[0])):
        if key[0] != SLOT:
            continue
        row, column = skin.grid(surface.clut)
        rows.add(row)
        if row not in other:
            continue
        compared += 1
        colours = texture.WIDE if surface.depth else texture.NARROW
        indices, width, _ = atlas.read_image(kit.data, images[surface.record], surface.depth)
        # the figure carries the shirt back in its torso gap (G5): so does the reference
        indices = numbered_indices(indices, width, figure, None)
        where, first = texture.window_for(palettes, column * texture.NARROW, other[row], colours)
        entries = texture.read_palette(kit.data, where, colours, first)
        want = b"".join(bytes(entries[i]) for i in indices)
        if want != surface.rgba:
            wrong.append("record %d, row %d: not the row %d colours"
                         % (surface.record, row, other[row]))
    return SwapControl(figure, kit_set, tuple(sorted(rows)), compared, tuple(wrong))


# -- the match figure (PLAN-KITS-PY.md section 4.3, KITS-TASK-47) ---------------------

MATCH_POSE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "match_pose.json")
"""The pose of two match figures, measured in the game: written by
`oracle.py --match-pose 5 --write` (KITS-TASK-45), never by hand."""
MATCH_FIGURES = ("outfield", "captain")
MATCH_SLEEVES = ("long", "short")
MATCH_VIEWS = ("torso", "camera")
"""`torso`: the figure in its body piece's own axes, upright, for viewing;
`camera`: as the game's camera sees it, for confronting with its frame."""
ROOT_SECTION = 2
"""The body piece of an outfield match figure, the one the torso view keeps."""
SLEEVE_LENGTHS = {
    "long": {"armband": 93, "replaced": 97, "neighbour": 98,
             "worn": (93, 95, 96, 97, 98, 99, 100, 101, 102)},
    "short": {"armband": 90, "replaced": 4, "neighbour": 6,
              "worn": (90, 3, 4, 5, 6, 57, 58, 59, 60)},
}
"""What each sleeve length draws, by position in the order (KITS-TASK-44 for
long, slot 5; KITS-TASK-46 for short, slot 6): outfield arms 95 96 97 98 or
3 5 4 6, the armband 93 where 97 is or 90 where 4 is, the goalkeeper's arms
99 101 100 102 or 57 58 59 60.  `neighbour` is where `--plant-matrix slot`
expects the armband instead."""
LONG_TO_SHORT = dict(zip((95, 96, 97, 98), (3, 5, 4, 6)))
"""The outfield arms by position: a short sleeve takes the matrix of the long
one it stands for.  The two share a local frame on the disc: 93 and 97 have
the same vertex box, and 3/4 against 95/97 differ by three units in x."""


def read_match_pose(path=None) -> dict:
    """The measured match pose, or `FigureError` with the command that makes it."""
    import json

    path = path or MATCH_POSE
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as exc:
        raise FigureError("No match pose at %s (python tools/kits/oracle.py --match-pose 5 "
                          "--write measures it): %s" % (path, exc.strerror or exc)) from exc


def match_order(pieces, armband: bool, sleeves: str) -> list:
    """[(section, rotation, translation)] of a measured figure, dressed: the
    armband where the replaced arm is or not at all, and the arms of the asked
    sleeve length -- each section swapped by its position in the order, so it
    keeps the matrix the game gave that position."""
    if sleeves not in MATCH_SLEEVES:
        raise FigureError("Sleeves %r are not one of %s." % (sleeves, MATCH_SLEEVES))
    long_rule, rule = SLEEVE_LENGTHS["long"], SLEEVE_LENGTHS[sleeves]
    out = []
    for piece in pieces:
        section = piece["section"]
        if section == long_rule["armband"]:
            section = long_rule["replaced"]        # the figure as worn without it
        if sleeves == "short":
            section = LONG_TO_SHORT.get(section, section)
        if armband and section == rule["replaced"]:
            section = rule["armband"]
        out.append((section, tuple(piece["rotation"]), tuple(piece["translation"])))
    return out


def _inverse(m):
    """The inverse of a 3x3 row-major matrix."""
    a, b, c, d, e, f, g, h, i = m
    det = a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)
    if abs(det) < 1e-12:
        raise FigureError("a piece matrix of the match pose is singular")
    return tuple(v / det for v in (e * i - f * h, c * h - b * i, b * f - c * e,
                                   f * g - d * i, a * i - c * g, c * d - a * f,
                                   d * h - e * g, b * g - a * h, a * e - b * d))


def _apply(m, v):
    return tuple(m[3 * r] * v[0] + m[3 * r + 1] * v[1] + m[3 * r + 2] * v[2] for r in range(3))


class _Vertex:
    __slots__ = ("x", "y", "z")

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


def match_scene(kit, kit_set: int = 1, armband: bool = False, sleeves: str = "long",
                figure: str = "outfield", view: str = "torso", geometry=None,
                geometry_path=None, pose=None):
    """The looks `Scene` of a match figure wearing set *kit_set* of *kit*.

    The pieces are MODEL.BIN's sections in the order the game drew them, each
    through the GTE matrix it was drawn with (`read_match_pose`), and every
    primitive textured the way `assembly.draw_list` resolves one: the page and
    CLUT the disc gives it, looked for in `DAT2D.BIN` first and in the kit
    second.  The texel of each corner follows the stored vertex order, as
    `scene.part_for` reads it -- the order KITS-TASK-45 measured.  The head
    wears the disc's own CLUTs: no LOOKS SET tuple edits it."""
    import section

    if kit_set not in KIT_SETS:
        raise FigureError("Kit set %r is not one of %s." % (kit_set, KIT_SETS))
    if figure not in MATCH_FIGURES:
        raise FigureError("Match figure %r is not one of %s." % (figure, MATCH_FIGURES))
    if view not in MATCH_VIEWS:
        raise FigureError("View %r is not one of %s." % (view, MATCH_VIEWS))
    pose = pose if pose is not None else read_match_pose()
    measured = pose["figures"][figure]
    order = match_order(measured["pieces"], armband, sleeves)
    if geometry is None:
        geometry = read_geometry(geometry_path_for(geometry_path))
    kit.require()
    data2d = geometry[layout.DAT2D]
    banks = [(layout.DAT2D, data2d, texture.images(data2d), texture.palettes(data2d)),
             (SLOT, kit.data, texture.in_set_order(texture.images(kit.data), kit_set),
              texture.in_set_order(texture.palettes(kit.data), kit_set))]
    sections = section.scan(geometry[layout.MODEL], layout.MODEL_GEOMETRY_START).sections
    root = next(((r, t) for s, r, t in order if s == ROOT_SECTION), None)
    if root is None:
        raise FigureError("the match pose has no section %d" % ROOT_SECTION)
    undo = _inverse(tuple(v / scene.ONE for v in root[0]))
    surfaces, parts = {}, []
    notes = {"no image": 0, "no palette": 0, "off the record": 0, "view": view,
             "projection": dict(pose["projection"]), "order": [s for s, _r, _t in order],
             "figure": figure, "armband": armband, "sleeves": sleeves}
    for number, rotation, translation in order:
        if not 0 <= number < len(sections):
            raise FigureError("section %d is not in %s" % (number, layout.MODEL))
        one = sections[number]
        r = tuple(v / scene.ONE for v in rotation)
        moved = []
        for v in one.vertices:
            p = _apply(r, (v.x, v.y, v.z))
            p = (p[0] + translation[0], p[1] + translation[1], p[2] + translation[2])
            if view == "torso":
                p = _apply(undo, (p[0] - root[1][0], p[1] - root[1][1], p[2] - root[1][2]))
            moved.append(_Vertex(*p))
        for at, primitive in enumerate(one.primitives):
            corner = atlas.texel(primitive, *primitive.texcoords[0])
            row, column = skin.grid(primitive.clut)
            record, surface = None, None
            for path, body, images, palettes in banks:
                page = atlas.image_at(images, *corner)
                if page is None:
                    continue
                try:
                    texture.covering(palettes, column * texture.NARROW, row, texture.NARROW)
                except texture.NoPalette:
                    continue
                record = page
                key = (path, record.offset, primitive.tpage_depth, primitive.clut)
                if key not in surfaces:
                    try:
                        surfaces[key] = scene.surface_for(body, record, primitive.tpage_depth,
                                                          primitive.clut, palettes, path)
                    except texture.NoPalette:
                        surfaces[key] = None
                surface = surfaces[key]
                break
            if record is None:
                notes["no image"] += 1
            elif surface is None:
                notes["no palette"] += 1
            part = scene.part_for(primitive, moved, record, surface, primitive.clut, 0,
                                  (layout.MODEL, number), at)
            if surface is not None and part.surface is None:
                notes["off the record"] += 1
            parts.append(part)
    return scene.Scene(parts, {k: v for k, v in surfaces.items() if v is not None},
                       looks.parse_tuple(TUPLE), 0, notes)


def screen_points(drawn, part) -> list:
    """A camera-view part's corners on the game's screen: `SX = OFX + H X / Z`,
    the y the scene flipped (`scene.UP`) flipped back."""
    projection = drawn.notes["projection"]
    h = projection["H"]
    out = []
    for x, y, z in part.points:
        y *= scene.UP
        out.append(None if z <= 0 else (projection["OFX"] + h * x / z,
                                        projection["OFY"] + h * y / z))
    return out


# -- the shirt number on the back (PLAN-KITS-PY.md section 4.7, KITS-TASK-40) ---------

BACK_COPY = {0: (44, 6), 1: (108, 6)}
"""Figure -> the corner of the 20x24 block of its "shirt back" zone the game
copies into its torso gap (KITS-TASK-38, measured on the LOOKS SET)."""
GLYPH_W = 6
"""The "numbers 0-9" zone is 60x12: ten glyphs of 6x12, 0 to 9 left to right."""
DIGIT_Y = 7
DIGIT_STEP = 8
"""Where the digits fall in a back panel, measured in slot 5 (KITS-TASK-42):
row 7, one digit at x 7, two at x 3 and 11 -- centred, a glyph every 8 pixels."""
NUMBERS = (0, 99)
"""The shirt numbers a panel holds: one or two digits."""


def digit_xs(count: int, width: int = 20) -> list:
    """The x of each of *count* digits in a panel *width* wide, centred at DIGIT_STEP."""
    first = (width - (GLYPH_W + DIGIT_STEP * (count - 1))) // 2
    return [first + DIGIT_STEP * i for i in range(count)]


def numbered_indices(indices: bytes, width: int, figure: int, number) -> bytes:
    """A uniform image's indices with *figure*'s torso gap made a back panel:
    the shirt back block copied in (KITS-TASK-38), and, unless *number* is
    None, the digits of *number* painted over it with the ink of the
    "numbers 0-9" glyphs -- every pixel of a glyph that is not the zone's
    commonest index (KITS-TASK-42)."""
    from . import zones

    if number is not None and not NUMBERS[0] <= number <= NUMBERS[1]:
        raise FigureError("Shirt number %r is not one of %d to %d." % ((number,) + NUMBERS))
    gap = next(g for g in zones.GAPS if g.name.startswith("torso") and g.figure == figure)
    zone = next(z for z in zones.ZONES if z.name == "numbers 0-9")
    panel = bytearray(indices)
    sx, sy = BACK_COPY[figure]
    for y in range(gap.h):
        for x in range(gap.w):
            panel[(gap.y + y) * width + gap.x + x] = indices[(sy + y) * width + sx + x]
    if number is None:
        return bytes(panel)
    tally = {}
    for y in range(zone.h):
        for x in range(zone.w):
            v = indices[(zone.y + y) * width + zone.x + x]
            tally[v] = tally.get(v, 0) + 1
    ground = max(tally, key=tally.get)
    digits = [int(d) for d in str(number)]
    for dx, digit in zip(digit_xs(len(digits), gap.w), digits):
        for y in range(zone.h):
            for x in range(GLYPH_W):
                v = indices[(zone.y + y) * width + zone.x + digit * GLYPH_W + x]
                if v != ground:
                    panel[(gap.y + DIGIT_Y + y) * width + gap.x + dx + x] = v
    return bytes(panel)


def numbered_scene(drawn, kit, kit_set: int, figure: int, number):
    """*drawn* (a LOOKS SET figure of `scene_of`) with the shirt back copied
    into its torso gap and, unless *number* is None, the shirt number on it:
    every kit surface re-coloured from `numbered_indices`, through the same
    palette window, and every part pointed at the new surface.  Re-reads the
    kit's own indices, so applying it to a figure already backed is the same."""
    images = {r.offset: r for r in texture.images(kit.data)}
    palettes = texture.in_set_order(texture.palettes(kit.data), kit_set)
    swapped = {}
    for key, surface in drawn.surfaces.items():
        if key[0] != SLOT:
            continue
        record = images[surface.record]
        indices, width, _height = atlas.read_image(kit.data, record, surface.depth)
        indices = numbered_indices(indices, width, figure, number)
        colours = texture.WIDE if surface.depth else texture.NARROW
        row, column = skin.grid(surface.clut)
        where, first = texture.window_for(palettes, column * texture.NARROW, row, colours)
        entries = texture.read_palette(kit.data, where, colours, first)
        rgba = b"".join(bytes(entries[i]) for i in indices)
        swapped[key] = scene.Surface(surface.key, surface.width, surface.height, rgba,
                                     surface.record, surface.depth, surface.clut)
    if not swapped:
        raise FigureError("%s has no kit surface on this figure to number" % kit.label)
    by_object = {id(drawn.surfaces[k]): v for k, v in swapped.items()}
    parts = [scene.Part(p.file, p.section, p.primitive, p.points, p.uvs,
                        by_object.get(id(p.surface), p.surface), p.why, p.clut, p.band,
                        p.band_unmeasured) for p in drawn.parts]
    surfaces = dict(drawn.surfaces)
    surfaces.update(swapped)
    notes = dict(drawn.notes)
    notes["back copy"] = BACK_COPY[figure]
    if number is not None:
        notes["number"] = number
    return scene.Scene(parts, surfaces, drawn.values, drawn.figure, notes)


# -- what the turned figure lets through (KITS-AJUSTES-3D.md G5, K3D-TASK-04) ------

HOLE_SIZE = 320
"""The square the count is taken in: the 3D view's minimum size."""
HOLE_MARGIN = 0.08
HOLE_DEPTH_TIE = 1e-6
"""The view's fit (`ui/figure_view.py` MARGIN), and how close two depths are
before a disagreement between paint order and depth is a tie, not an error."""


@dataclass(frozen=True)
class HoleCount:
    """What one figure shows at one turn, counted pixel by pixel.

    At each pixel the triangle nearest the eye is what a figure drawn whole
    would show.  `transparent` counts the pixels where that triangle samples a
    transparent texel -- what shows there is whatever lies behind, the inside
    of the figure or the backdrop, and `backdrop` is how many of them show the
    backdrop; `skipped` those where it is a triangle the view cannot map (its
    UV triangle has no area, so nothing is painted); `misordered` those where
    it is opaque but the view paints another triangle last over it.
    `silhouette` is every pixel some triangle covers.  `sources` counts each
    kind by where it comes from: (kind, "file section N", zone, gap or "-")."""

    yaw: float
    pitch: float
    silhouette: int
    transparent: int
    backdrop: int
    skipped: int
    misordered: int
    sources: tuple          # ((kind, part, where, pixels), ...), most pixels first

    @property
    def missing(self) -> int:
        """Pixels where the nearest surface is not what is shown."""
        return self.transparent + self.skipped + self.misordered


def _turn(point, yaw, pitch):
    """`ui/figure_view.py` rotate(), kept equal by the selftest."""
    import math

    x, y, z = point
    a, b = math.radians(yaw), math.radians(pitch)
    x, z = x * math.cos(a) + z * math.sin(a), -x * math.sin(a) + z * math.cos(a)
    y, z = y * math.cos(b) - z * math.sin(b), y * math.sin(b) + z * math.cos(b)
    return x, y, z


def record_numbers(kit) -> dict:
    """Offset -> record number (tex.RECORD_NAMES) of *kit*'s records."""
    import bin_archive

    return {e.offset: i for i, e in enumerate(bin_archive.entries(kit.data))}


def texel_zone(numbers, surface, tx: int, ty: int, figure: int) -> str:
    """The zone or gap of the work bitmap a kit texel lies in, "-" for a texel
    of another file (or with no kit to read *numbers* from) and "no zone" for
    one of the kit outside the map.  *numbers* is `record_numbers(kit)`."""
    from . import flat, zones

    if numbers is None or surface.key[0] != SLOT:
        return "-"
    record = numbers.get(surface.record)
    if record in flat.UNIFORM.values():
        wx = tx
    elif record in flat.SLEEVES.values():
        wx = tx + flat.WORK_W // 2
    else:
        return "record %s" % record
    for gap in zones.GAPS:
        if gap.figure == figure and gap.contains(wx, ty):
            return "gap %s (%d,%d) %dx%d" % (gap.name, gap.x, gap.y, gap.w, gap.h)
    zone = zones.zone_at(wx, ty)
    return "zone %s" % zone.name if zone is not None else "no zone (%d,%d)" % (wx, ty)


def count_holes(drawn, yaw: float, pitch: float = 0.0, kit=None, size: int = HOLE_SIZE,
                triangles=TRIANGLES) -> HoleCount:
    """What *drawn* lets through at (*yaw*, *pitch*), drawn as the 3D view
    draws it: the same orthographic camera fitted to the same square, the same
    back-to-front order by each triangle's mean depth, and the texture sampled
    at each pixel's centre (nearest texel, no smoothing).  A model of the
    view's QPainter, not a capture of it: it counts, it does not compare
    pixels with a screenshot."""
    parts = drawn.parts
    centre = drawn.centre()
    turned = [[_turn(tuple(p[i] - centre[i] for i in range(3)), yaw, pitch)
               for p in part.points] for part in parts]
    xs = [p[0] for pts in turned for p in pts]
    ys = [p[1] for pts in turned for p in pts]
    span = max(max(xs) - min(xs), max(ys) - min(ys)) or 1.0
    scale = size * (1.0 - 2 * HOLE_MARGIN) / span
    mx, my = (max(xs) + min(xs)) / 2.0, (max(ys) + min(ys)) / 2.0
    c = size / 2.0
    order = []
    for n, (part, pts) in enumerate(zip(parts, turned)):
        screen = [(c - (p[0] - mx) * scale, c - (p[1] - my) * scale, p[2]) for p in pts]
        for tri in triangles:
            order.append((sum(pts[i][2] for i in tri) / 3.0, n,
                          [screen[i] for i in tri], [part.uvs[i] for i in tri]))
    order.sort(key=lambda t: t[0])
    frags = {}      # pixel -> [(order, n, depth, opaque or None if unmapped, texel)]
    numbers = record_numbers(kit) if kit is not None else None
    for step, (_, n, tri, uvs) in enumerate(order):
        part = parts[n]
        surface = part.surface
        (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = tri
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-12:
            continue
        mapped = True
        if surface is not None:
            (u0, v0), (u1, v1), (u2, v2) = ((u * surface.width, v * surface.height)
                                            for u, v in uvs)
            mapped = abs((u1 - u0) * (v2 - v0) - (u2 - u0) * (v1 - v0)) >= 1e-9
        for py in range(max(0, int(min(y0, y1, y2))), min(size, int(max(y0, y1, y2)) + 1)):
            for px in range(max(0, int(min(x0, x1, x2))), min(size, int(max(x0, x1, x2)) + 1)):
                sx, sy = px + 0.5, py + 0.5
                a = ((x1 - sx) * (y2 - sy) - (x2 - sx) * (y1 - sy)) / area
                b = ((x2 - sx) * (y0 - sy) - (x0 - sx) * (y2 - sy)) / area
                g = 1.0 - a - b
                if a < 0 or b < 0 or g < 0:
                    continue
                depth = a * z0 + b * z1 + g * z2
                texel, opaque = None, True
                if not mapped:
                    opaque = None
                elif surface is not None:
                    tx = min(surface.width - 1, max(0, int(a * u0 + b * u1 + g * u2)))
                    ty = min(surface.height - 1, max(0, int(a * v0 + b * v1 + g * v2)))
                    opaque = surface.rgba[(ty * surface.width + tx) * 4 + 3] != 0
                    texel = (tx, ty)
                frags.setdefault((px, py), []).append((step, n, depth, opaque, texel))
    tally = {}

    def name(n):
        return "%s section %d" % (parts[n].file, parts[n].section)

    def add(kind, n, where):
        key = (kind, name(n), where)
        tally[key] = tally.get(key, 0) + 1

    zone_of = {}
    transparent = backdrop = skipped = misordered = 0
    for pixel, here in frags.items():
        far = max(f[2] for f in here)
        # the nearest; among depths within the tie, the one painted last
        near = max((f for f in here if f[2] >= far - HOLE_DEPTH_TIE), key=lambda f: f[0])
        painted = [f for f in here if f[3]]
        last = max(painted, key=lambda f: f[0]) if painted else None
        if near[3] is None:
            skipped += 1
            add("skipped", near[1], "-")
        elif not near[3]:
            transparent += 1
            backdrop += last is None
            key = (near[1], near[4])
            if key not in zone_of:
                zone_of[key] = texel_zone(numbers, parts[near[1]].surface, near[4][0],
                                          near[4][1], drawn.figure) \
                    if near[4] is not None else "-"
            add("transparent", near[1], zone_of[key])
        elif last is not near and last[2] < near[2] - HOLE_DEPTH_TIE:
            misordered += 1
            add("misordered", last[1], "over %s" % name(near[1]))
    sources = tuple(sorted(((k[0], k[1], k[2], v) for k, v in tally.items()),
                           key=lambda s: (-s[3], s)))
    return HoleCount(yaw, pitch, len(frags), transparent, backdrop, skipped, misordered,
                     sources)


def planted_gap(drawn, kit, figure: int, zone_name: str = "shirt front"):
    """*drawn* with *figure*'s zone *zone_name* made transparent in the kit's
    uniform -- a gap the count has to find (the control of K3D-TASK-04)."""
    from . import flat, zones

    zone = next((z for z in zones.ZONES if z.name == zone_name and z.figure == figure), None)
    if zone is None or zone.x + zone.w > flat.WORK_W // 2:
        raise FigureError("No zone %r of figure %d in the uniform image." % (zone_name, figure))
    numbers = record_numbers(kit)
    surfaces, by_object = dict(drawn.surfaces), {}
    for key, surface in drawn.surfaces.items():
        if key[0] != SLOT or numbers.get(surface.record) not in flat.UNIFORM.values():
            continue
        rgba = bytearray(surface.rgba)
        for y in range(zone.y, min(surface.height, zone.y + zone.h)):
            for x in range(zone.x, min(surface.width, zone.x + zone.w)):
                rgba[(y * surface.width + x) * 4 + 3] = 0
        surfaces[key] = scene.Surface(surface.key, surface.width, surface.height, bytes(rgba),
                                      surface.record, surface.depth, surface.clut)
        by_object[id(surface)] = surfaces[key]
    if not by_object:
        raise FigureError("%s has no uniform surface on this figure to plant a gap in"
                          % kit.label)
    parts = [scene.Part(p.file, p.section, p.primitive, p.points, p.uvs,
                        by_object.get(id(p.surface), p.surface), p.why, p.clut, p.band,
                        p.band_unmeasured) for p in drawn.parts]
    return scene.Scene(parts, surfaces, drawn.values, drawn.figure, dict(drawn.notes))

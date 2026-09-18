#!/usr/bin/env python3
"""The draw list turned into geometry, texels and colours -- still no Qt.

Provenance (plan section 3.4): this module knows the FORMAT and the tuple; it
knows no address of its own and it does not know how to draw.  `assembly.py`
says which primitives a tuple owns and what it does to them; this says what
those primitives look like -- four points, four texture coordinates, and the
RGBA texture the pair samples.  `ui/viewer.py` uploads what comes out and
nothing else, which is how rule 3 of section 3.3 stays true: the window knows
no address because the window is handed pixels.

**The colour path is the one LOOKS-TASK-12 measured, and no other.**  The index
comes from the image record the primitive's page and `u` resolve to, and the
colour comes from the sixteen-entry window the CLUT id names inside a record
that may hold 256 -- never from the record's start, and never from the vertex,
which in this format has no colour field at all.

**Which two triangles a quad is remains unverified**, and it is said here
rather than buried: the four indices are used in the order the file stores
them, as the hardware's own `POLY_FT4` order -- (0, 1, 2) and (1, 2, 3).
`section.Primitive.corners` offers the `we3d` untangling instead, which picks
the OTHER diagonal.  Both draw; only a render against the game says which, and
that is LOOKS-TASK-17's measurement, not a choice to be made quietly here.

Usage:
    python tools/looks/scene.py --check
    WE2002_LOOKS_IMAGE=<japanese .bin> python tools/looks/scene.py --check-image
    WE2002_LOOKS_IMAGE=<japanese .bin> python tools/looks/scene.py --tuple A-I3-A-F-A
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import assembly  # noqa: E402
import atlas  # noqa: E402
import harness  # noqa: E402
import layout  # noqa: E402
import looks  # noqa: E402
import section  # noqa: E402
import skin  # noqa: E402
import texture  # noqa: E402

SKIP = 77

TRIANGLES = ((0, 1, 2), (1, 2, 3))
"""How a quad becomes two triangles, over the four indices AS STORED.

The diagonal this picks is 1-2; `Primitive.corners` would pick 0-3.  **Measured
on 2026-09-16 by LOOKS-TASK-17**, against the game's own display list on the
reference frame: of the head's quads a packet identifies unambiguously, seven
carry their texcoords in the order the file stores them and none in the `we3d`
order (`confront.py --score`).  The GPU draws a packet as (0, 1, 2) and
(1, 2, 3), so the stored order is the drawn order.
"""

UP = -1
"""Which way is up in model space, as a multiplier on `y`.

Measured, not assumed: the head sections of MODEL.BIN carry the SMALLER `y` and
the boot sections of EDT_MOD.BIN the larger, so `y` grows downward, as it does
in every PSX coordinate system this disc uses.  `--check-image` re-measures it
on the real files and fails if the two ends ever swap.
"""

PLACEHOLDER = (108, 108, 120, 255)
"""The colour of a primitive this file cannot texture, and why it is loud.

Two causes, both measured and neither a bug of this module: a primitive whose
page is not in `DAT2D.BIN` at all -- the kit, which lives in the 105 `TEX_*.BIN`
containers -- and the two CLUT ids the geometry names that no container on the
disc holds, (0, 485) and (336, 510).  A picture with grey pieces is a picture
missing a FILE, and `Scene.notes` counts them so the number is read rather than
guessed at from the screen.
"""


class BadScene(Exception):
    """A tuple, a figure or a primitive this module cannot turn into a scene."""


class OffTheRecord(BadScene):
    """A texel outside the image record its own page and CLUT resolve to."""


class Surface:
    """One texture: an image record read through one CLUT, as RGBA bytes.

    Keyed by the three things that decide the pixels -- the record, the page
    depth and the CLUT id -- because the same image drawn through two CLUTs is
    two different textures, which is exactly what a colour field does.
    """

    __slots__ = ("key", "width", "height", "rgba", "record", "depth", "clut")

    def __init__(self, key, width, height, rgba, record, depth, clut):
        self.key = key
        self.width = width
        self.height = height
        self.rgba = rgba
        self.record = record
        self.depth = depth
        self.clut = clut

    def __repr__(self):
        return ("Surface(image=%d, depth=%d, clut=%d, %dx%d)"
                % (self.record, self.depth, self.clut, self.width, self.height))


class Part:
    """One primitive, ready to draw: four points, four (u, v), one surface.

    `surface` is None for a primitive this file cannot texture, and `why` says
    which of the two causes it was.  Dropping such a primitive would be the
    quiet answer: the figure would come out whole and the missing file would
    never be noticed.
    """

    __slots__ = ("file", "section", "primitive", "points", "uvs", "surface",
                 "why", "clut", "band", "band_unmeasured")

    def __init__(self, file, index, primitive, points, uvs, surface, why,
                 clut, band, band_unmeasured=()):
        self.file = file
        self.section = index
        self.primitive = primitive
        self.points = points
        self.uvs = uvs
        self.surface = surface
        self.why = why
        self.clut = clut
        self.band = band
        self.band_unmeasured = band_unmeasured

    @property
    def textured(self) -> bool:
        return self.surface is not None


class Scene:
    """Everything one tuple draws, in one figure, with nothing left implicit."""

    __slots__ = ("parts", "surfaces", "values", "figure", "notes")

    def __init__(self, parts, surfaces, values, figure, notes):
        self.parts = parts
        self.surfaces = surfaces
        self.values = values
        self.figure = figure
        self.notes = notes

    @property
    def tuple_text(self) -> str:
        return looks.format_tuple(self.values)

    def bounds(self) -> tuple:
        """((min x, min y, min z), (max x, max y, max z)) over every point."""
        if not self.parts:
            raise BadScene("an empty scene has no bounds")
        lows = [min(p[axis] for part in self.parts for p in part.points)
                for axis in range(3)]
        highs = [max(p[axis] for part in self.parts for p in part.points)
                 for axis in range(3)]
        return (tuple(lows), tuple(highs))

    def centre(self) -> tuple:
        low, high = self.bounds()
        return tuple((low[i] + high[i]) / 2.0 for i in range(3))

    def radius(self) -> float:
        low, high = self.bounds()
        return max(high[i] - low[i] for i in range(3)) / 2.0 or 1.0

    def triangles(self) -> int:
        return len(self.parts) * len(TRIANGLES)

    def __repr__(self):
        return ("Scene(%s, figure %d, %d part(s), %d surface(s))"
                % (self.tuple_text, self.figure, len(self.parts),
                   len(self.surfaces)))


# ---- one primitive -------------------------------------------------------

def local_texel(primitive, record, u: int, v: int) -> tuple:
    """(x, y) of one texel INSIDE an image record, in texels.

    `atlas.texel` answers in VRAM halfwords, which is what finds the record;
    this is the other half, and it cannot be the same arithmetic: a halfword
    holds four texels at 4 bits, so the page offset has to be multiplied back
    up while `u` is already counted in texels.  Dropping that multiplication
    leaves a picture that is textured, seamless and sampled from a quarter of
    the sheet.
    """
    per = atlas.texels_per_unit(primitive.tpage_depth)
    page_x, page_y = primitive.tpage_vram
    x = (page_x - record.x) * per + u
    y = page_y + v - record.y
    width, height = record.w * per, record.h
    if not (0 <= x < width and 0 <= y < height):
        raise OffTheRecord(
            "texel (%d, %d) of the record at %d is outside its %dx%d rect"
            % (x, y, record.offset, width, height))
    return (x, y)


def indices_in_quad(indices: bytes, width: int, primitive, record,
                    band: int = 0) -> set:
    """The palette indices inside one quad's rect, over a decoded image.

    Split from `sampled_indices` so the gathering can be checked with a plain
    buffer and no LZSS stream in the room -- which is also what makes the
    band's red case reachable.
    """
    points = [local_texel(primitive, record, u, v + band)
              for u, v in primitive.texcoords]
    xs = [x for x, _y in points]
    ys = [y for _x, y in points]
    return {indices[y * width + x]
            for y in range(min(ys), max(ys) + 1)
            for x in range(min(xs), max(xs) + 1)}


def sampled_indices(data: bytes, primitive, record, band: int = 0) -> set:
    """The palette indices one quad's texels actually hold, at *band*.

    A colour field moves the CLUT id, which swaps the sixteen entries the
    indices are looked up in.  Whether that changes the PICTURE depends on
    which indices the quad samples -- and a window whose differing entries the
    quad never names is a palette change with no pixel behind it.  Reading
    them is the only way to tell that from a colour that failed to arrive
    (CORR-LOOKS-038).
    """
    indices, width, _height = atlas.read_image(data, record,
                                               primitive.tpage_depth)
    return indices_in_quad(indices, width, primitive, record, band)


def surface_for(data: bytes, record, depth: int, clut: int,
                palettes) -> Surface:
    """One image record read at `depth`, coloured through one CLUT id.

    The window comes from `texture.window_for`, never from the record's own
    start: a 4-bit id inside a 256-entry record names one of sixteen windows,
    and window zero is what a start-of-record read hands back -- somebody
    else's sixteen colours, drawn perfectly.
    """
    indices, width, height = atlas.read_image(data, record, depth)
    colours = texture.WIDE if depth else texture.NARROW
    row, column = skin.grid(clut)
    where, first = texture.window_for(palettes, column * texture.NARROW, row,
                                      colours)
    entries = texture.read_palette(data, where, colours, first)
    rgba = bytearray(len(indices) * 4)
    for at, index in enumerate(indices):
        if index >= len(entries):
            raise BadScene("index %d of a %d-entry window at (%d, %d)"
                           % (index, len(entries), column * texture.NARROW,
                              row))
        rgba[4 * at:4 * at + 4] = bytes(entries[index])
    return Surface((record.offset, depth, clut), width, height, bytes(rgba),
                   record.offset, depth, clut)


def part_for(primitive, vertices, record, surface, clut: int, band: int,
             where: tuple, at: int, band_unmeasured=(),
             texcoords=None) -> Part:
    """One primitive as points and normalised (u, v), or as a flat placeholder.

    Split out of `build` so the arithmetic can be checked with no disc in the
    room, which is where every mistake in it has been found so far.
    """
    points = []
    for index in primitive.indices:
        if index >= len(vertices):
            raise BadScene("vertex %d of a section with %d"
                           % (index, len(vertices)))
        vertex = vertices[index]
        points.append((float(vertex.x), float(vertex.y) * UP,
                       float(vertex.z)))

    uvs = []
    why = None
    if surface is None:
        why = ("no image record on this disc holds the page it samples"
               if record is None else "no container on this disc holds its "
                                      "palette")
    else:
        per = atlas.texels_per_unit(primitive.tpage_depth)
        width, height = record.w * per, record.h
        # A hair quad arrives with the texcoords the game's store writes,
        # which already hold the band; everything else is the file's own `v`
        # moved by it (CORR-LOOKS-042).
        corners = (texcoords if texcoords is not None
                   else [(u, v + band) for u, v in primitive.texcoords])
        try:
            for u, v in corners:
                x, y = local_texel(primitive, record, u, v)
                # Half a texel in, so a coordinate on the edge samples the
                # texel it names instead of whatever the sampler rounds to.
                uvs.append(((x + 0.5) / width, (y + 0.5) / height))
        except OffTheRecord as exc:
            surface, uvs, why = None, [], str(exc)
    if surface is None:
        uvs = [(0.0, 0.0)] * len(points)
    return Part(where[0], where[1], at, points, uvs, surface, why, clut, band,
                band_unmeasured)


# ---- the scene -----------------------------------------------------------

def build(disc, values: dict, figure: int = assembly.HEAD_FIGURE,
          frame: int = None) -> Scene:
    """Everything the tuple draws, out of the disc's own bytes.

    The draw list is `assembly`'s and is not recomputed here: which primitive
    a field owns, which head a style picks and which band it samples are all
    measurements, and a second copy of them would be a second thing to keep
    right.
    """
    parts = assembly.draw_list(disc, values, figure)
    data2d = disc[layout.DAT2D]
    images = texture.images(data2d)
    palettes = texture.palettes(data2d)

    scans: dict = {}
    surfaces: dict = {}
    notes = {"no image": 0, "no palette": 0, "off the record": 0,
             "band unmeasured": 0}
    out = []
    for entry in parts:
        name, index, at = entry["file"], entry["section"], entry["primitive"]
        if name not in scans:
            scans[name] = section.scan(disc[name], layout.GEOMETRY_START[name])
        one = scans[name].sections[index]
        primitive = one.primitives[at]
        record = None
        surface = None
        if entry["image"] is not None:
            record = next(r for r in images if r.offset == entry["image"])
            key = (record.offset, primitive.tpage_depth, entry["clut"])
            if key not in surfaces:
                try:
                    surfaces[key] = surface_for(data2d, record,
                                                primitive.tpage_depth,
                                                entry["clut"], palettes)
                except texture.NoPalette:
                    surfaces[key] = None
            surface = surfaces[key]
            if surface is None:
                notes["no palette"] += 1
        else:
            notes["no image"] += 1
        part = part_for(primitive, one.vertices, record, surface,
                        entry["clut"], entry["band"], (name, index), at,
                        entry["band_unmeasured"], entry.get("texcoords"))
        if surface is not None and part.surface is None:
            notes["off the record"] += 1
        if part.band_unmeasured:
            notes["band unmeasured"] += 1
        out.append(part)
    if frame is not None:
        out = _posed(disc, out, frame, notes)
    return Scene(out, {k: v for k, v in surfaces.items() if v is not None},
                 values, figure, notes)


def _posed(disc, parts: list, frame: int, notes: dict) -> list:
    """Every part turned and placed by the frame's own pose.

    The points are transformed HERE, in the core, and not by the window: the
    window may not import `anime`, `layout` or `pieces`, and a pose applied at
    draw time would be a second placement to keep right beside `shelf()`.
    """
    places = pose(disc, frame)
    notes["not posed"] = 0
    notes["placed by its mirror"] = 0
    out = []
    for part in parts:
        found = places.get((part.file, part.section))
        if found is None:
            notes["not posed"] += 1
            out.append(part)
            continue
        matrix, place, mirrored = found
        if mirrored:
            notes["placed by its mirror"] += 1
        moved = Part(part.file, part.section, part.primitive,
                     place_points(part.points, matrix, place), part.uvs,
                     part.surface, part.why, part.clut, part.band,
                     part.band_unmeasured)
        out.append(moved)
    return out


def from_image(image_path: str, text: str,
               figure: int = assembly.HEAD_FIGURE,
               frame: int = None) -> Scene:
    """The whole path, from a disc on disc to a scene -- what `ui/app.py` calls.

    It lives here and not in the window because the window is forbidden the
    three modules this needs, which is rule 3 and not an accident of layering.
    """
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D,
                             layout.ANIME)}
    # A tuple the table refuses arrives here as BadScene, with the table's own
    # sentence kept whole.  The window is not allowed to import `assembly` or
    # `looks` to catch their exceptions, and a refusal that reaches it as a
    # traceback reads as a crash of the viewer rather than as the measured "no"
    # it is -- three hair styles and one beard value are exactly that.
    try:
        values = looks.parse_tuple(text)
        return build(data, values, figure, frame)
    except (looks.BadLooks, assembly.BadAssembly) as exc:
        raise BadScene(str(exc)) from exc


class Builder:
    """The disc read once, and a scene per tuple after that.

    The screen redraws the figure on every press, and `from_image` opens the
    image and reads three files each time it is called -- fine for a gate that
    draws four pictures, wrong for a window where Left and Right are held down.
    The bytes do not change between presses, so they are read once.

    It lives here and not in the window for rule 3: opening the disc is
    `iso_source`'s, and `ui/` may not import it.
    """

    __slots__ = ("image_path", "figure", "_data")

    def __init__(self, image_path: str, figure: int = assembly.HEAD_FIGURE):
        import iso_source

        self.image_path = image_path
        self.figure = figure
        with iso_source.open_disc(image_path) as disc:
            self._data = {name: disc.read(name)
                          for name in (layout.EDT_MOD, layout.MODEL,
                                       layout.DAT2D, layout.ANIME)}

    def build(self, text: str, frame: int = None) -> Scene:
        """*text* as a scene, or `BadScene` carrying the table's own sentence."""
        try:
            values = looks.parse_tuple(text)
            return build(self._data, values, self.figure, frame)
        except (looks.BadLooks, assembly.BadAssembly) as exc:
            raise BadScene(str(exc)) from exc




# --- the pose: the pieces where the game puts them -------------------------

ONE = 4096  # not-an-address: 1.0 in the 4.12 the matrix is in

REFERENCE_PIECE = "root"
"""The piece every place is measured from.

It is the one load of a pass that carries no model pointer (LOOKS-TASK-25), so
nothing is drawn for it -- what it gives is the origin.  ANIME.BIN stores
places relative to one another, and the figure is assembled around this one.
"""

REFERENCE_FRAME = 0
"""The frame of the screen's animation a scene is posed in when none is asked
for.  Frame 0 of `layout.ANIME_SCREEN_ENTRY`, which is where the walk starts."""


def piece_names(disc) -> dict:
    """{(file, section): name} for every piece either figure draws.

    The names are `pieces.py`'s -- measured in LOOKS-TASK-09 -- and the head is
    MODEL.BIN's section 24.  They are what ties a section of the model files to
    a pair of an ANIME.BIN frame, which carries no section number of its own.
    """
    import pieces

    named, _orders, _paired = pieces.name_pieces(disc[layout.EDT_MOD])
    out = {(layout.MODEL, pieces.HEAD_SECTION): pieces.HEAD}
    for index, piece in named.items():
        out[(layout.EDT_MOD, index)] = piece.full_name
    return out


def mirror_of(name: str) -> str:
    """The partner of a mirrored piece, or None.

    `pieces.py` pairs the limbs and calls one of each pair `a` and the other
    `b`; ANIME.BIN carries a pair for one boot and not for the other, so the
    one it does not carry is placed from its partner's.
    """
    if name.endswith(" a"):
        return name[:-2] + " b"
    if name.endswith(" b"):
        return name[:-2] + " a"
    return None


def pose(disc, frame: int = REFERENCE_FRAME,
         animation: int = None) -> dict:
    """{(file, section): (matrix, place)} -- where the game puts each piece.

    **Twelve transforms applied, not a hierarchy composed.**  LOOKS-TASK-25
    measured that what reaches the GTE per piece is absolute, and that the
    game's skeleton is not rigid: five joints hold and the rest do not.  So
    assembling is applying what the frame stores, and inventing a chain of
    bones would draw a figure that looks right and is nobody's -- the same
    failure `shelf()` refuses to commit by being honest about being a shelf.

    The one piece whose place is NOT measured is the second boot: the file
    carries eleven pairs for twelve drawn sections, and the screen reads both
    boot sections (LOOKS-TASK-26).  It is placed by mirroring its partner in
    z, and `posed_notes()` says so rather than letting it pass for measured.
    """
    import anime

    if animation is None:
        animation = layout.ANIME_SCREEN_ENTRY
    data = disc[layout.ANIME]
    entries = anime.header(data)
    one = anime.block(data, entries[animation])
    if not 0 <= frame < len(one["frames"]):
        raise BadScene("frame %d, and animation %d has %d"
                       % (frame, animation, len(one["frames"])))
    by_name = {piece["piece"]: piece
               for piece in anime.frame_angles(data, one["frames"][frame])}
    origin = by_name[REFERENCE_PIECE]["position"]
    out = {}
    for where, name in piece_names(disc).items():
        carried = by_name.get(name)
        mirrored = False
        if carried is None:
            partner = mirror_of(name)
            carried = by_name.get(partner) if partner else None
            mirrored = carried is not None
        if carried is None:
            continue
        matrix = anime.rotation(carried["angles"])
        place = [carried["position"][axis] - origin[axis] for axis in range(3)]
        if mirrored:
            matrix = _mirrored_in_z(matrix)
            place[2] = -place[2]
        out[where] = (matrix, tuple(place), mirrored)
    return out


def _mirrored_in_z(matrix: list) -> list:
    """The same turn seen in a mirror across z.

    `pieces.py` measured that the limbs pair by reflection in z, so the
    partner's turn is this one with the z row and column negated -- which is
    `M . R . M` for `M = diag(1, 1, -1)`, written out.
    """
    signs = (1, 1, -1)
    return [matrix[row * 3 + column] * signs[row] * signs[column]
            for row in range(3) for column in range(3)]


def place_points(points, matrix, place) -> list:
    """One piece's points, turned and put where the frame says.

    The shift of twelve is the game's: the matrix is 4.12 and the points are
    whole model units, so the product comes back to model units.
    """
    out = []
    for point in points:
        # The points are floats by the time they reach here -- `part_for`
        # already divided the file's whole units -- so the shift is written as
        # the division it is, and the matrix stays the game's 4.12 integers.
        turned = [sum(matrix[axis * 3 + k] * point[k] for k in range(3))
                  / float(ONE) for axis in range(3)]
        out.append(tuple(turned[axis] + place[axis] for axis in range(3)))
    return out

SHELF_GAP = 8.0
"""Space left between two pieces on the shelf, in the file's own units."""


def shelf(scene: Scene) -> dict:
    """{(file, section): (dx, dy, dz)} that lays the pieces out side by side.

    **NEITHER MODEL FILE SAYS WHERE A PIECE GOES.**  Measured here, 2026-09-16,
    and it is the finding of this task: every section is modelled around its
    own origin -- the head spans y -15..48 and the boots y -15..18 -- so drawing
    them all in file coordinates piles twelve pieces on top of each other.  The
    placement is applied by the game at draw time, in the display list that
    LOOKS-TASK-09 measured, and it is not in the bytes this cycle reads.

    So this is a SHELF and not a pose, and the name is the honest one: pieces
    in a row, in file order, each one whole and none overlapping.  A viewer
    that invented plausible joint offsets would draw a figure that looked right
    and was nobody's -- the same failure the assembly table refuses for the
    three unmeasured hair styles.  What a real pose needs is written in
    LOOKS-TASK-17, which is where the game's own transforms get read.
    """
    spans: dict = {}
    for part in scene.parts:
        key = (part.file, part.section)
        box = spans.get(key)
        for point in part.points:
            if box is None:
                box = [point[0], point[0], point[1], point[1]]
                spans[key] = box
            box[0] = min(box[0], point[0])
            box[1] = max(box[1], point[0])
            box[2] = min(box[2], point[1])
            box[3] = max(box[3], point[1])
    out = {}
    at = 0.0
    for key in sorted(spans, key=lambda k: (k[0], k[1])):
        low_x, high_x, low_y, high_y = spans[key]
        out[key] = (at - low_x, -(low_y + high_y) / 2.0, 0.0)
        at += (high_x - low_x) + SHELF_GAP
    return out


def head_only(scene: Scene) -> Scene:
    """The same scene with the head alone, for the screen that is about it.

    Four of the five rows a tuple carries -- hair, hair colour, beard and skin
    -- reach primitives of the head section and of nothing else, so this is the
    view that shows what a tuple changed.  The counts travel with it, so a
    report of the head says how many of the head's primitives were textured
    rather than how many of the figure's.
    """
    parts = [part for part in scene.parts if part.file == layout.MODEL]
    keys = {part.surface.key for part in parts if part.textured}
    notes = {name: 0 for name in scene.notes}
    for part in parts:
        if part.textured:
            continue
        notes["no image"] = notes.get("no image", 0) + 1
    return Scene(parts, {k: v for k, v in scene.surfaces.items() if k in keys},
                 scene.values, scene.figure, notes)


def image_from_env() -> str:
    """The Japanese data track the environment names, or a RuntimeError.

    A thin pass-through, and it exists for the window: `ui/` may not import
    `iso_source` or `layout` (rule 3), so without this the window would either
    spell the name of the variable itself -- a second place to keep right --
    or reach through this module's imports, which is the same breach wearing a
    longer name.
    """
    import iso_source

    return iso_source.image_from_env()


class BadScreen(Exception):
    """What `screen_state` refuses: a slot nobody measured, a button the screen
    does not answer to, a table that does not hold together.

    A separate name from `screen.BadScreen` only so the window can catch it
    without importing the module that reads the table -- the same reason
    `image_from_env` is here, and the same rule (3) behind both.  The instance
    raised IS the one `screen.py` raised; nothing is reworded.
    """


def screen_state(slot: int | str = 2):
    """The measured LOOKS SET screen, as something the window can walk.

    **The window does not decide what a press does.**  `screen.State` carries
    the locks, the wrap, the texts of every value and the help of every row,
    all of them written by `oracle.py --screen --write` off the running game;
    the widget sends `press` and draws what comes back.  That separation is
    what the gate is able to judge: `ui_check.py` re-derives the same walk from
    `screen.py` and compares, and it could not if the widget did the walking.
    """
    import screen

    try:
        return screen.State(screen.load(), slot)
    except (OSError, screen.BadScreen) as exc:
        raise BadScreen(str(exc)) from exc


def screen_press(state, button: str) -> bool:
    """One press on *state*, with the refusal reworded into this module's."""
    import screen

    try:
        return state.press(button)
    except screen.BadScreen as exc:
        raise BadScreen(str(exc)) from exc


def screen_keys(text: str) -> list:
    """`Down,Right` to the presses it names, or this module's refusal."""
    import screen

    try:
        return screen.parse_keys(text)
    except screen.BadScreen as exc:
        raise BadScreen(str(exc)) from exc


def summary(scene: Scene) -> dict:
    """The numbers a log or a gate would otherwise count by hand."""
    low, high = scene.bounds()
    return {
        "tuple": scene.tuple_text,
        "figure": scene.figure,
        "parts": len(scene.parts),
        "textured": sum(1 for p in scene.parts if p.textured),
        "surfaces": len(scene.surfaces),
        "triangles": scene.triangles(),
        "sections": len({(p.file, p.section) for p in scene.parts}),
        "bounds": (low, high),
        "notes": dict(scene.notes),
    }


# ---- the gate ------------------------------------------------------------

class _FakePrimitive:
    """A primitive with the three fields this module reads, and nothing else."""

    def __init__(self, texcoords, indices, clut, page, depth=0):
        self.texcoords = texcoords
        self.indices = indices
        self.clut = clut
        self._page = page
        self._depth = depth

    @property
    def tpage_vram(self):
        return self._page

    @property
    def tpage_depth(self):
        return self._depth


class _FakeVertex:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class _FakeRecord:
    def __init__(self, x, y, w, h, offset):
        self.x, self.y, self.w, self.h, self.offset = x, y, w, h, offset


def self_check(verbose: bool = True) -> int:
    return harness.run("scene.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(BadScene)

    ok("a quad is two triangles over the four stored indices",
       len(TRIANGLES) == 2
       and sorted({i for tri in TRIANGLES for i in tri}) == [0, 1, 2, 3])
    ok("and the alternative reading is still reachable, not deleted",
       hasattr(section.Primitive, "corners"))

    # The texel arithmetic, at both depths.  A page starts at a multiple of 64
    # halfwords and a record starts wherever it starts, so the two have to be
    # subtracted BEFORE the depth is applied -- which is the line that has to
    # be got right and the one a control breaks.
    page = (atlas.PAGE_UNITS * 8, 0)
    rec = _FakeRecord(page[0] - atlas.PAGE_UNITS, 0, atlas.PAGE_UNITS * 2, 128,
                      10)
    four = _FakePrimitive((((0, 0)),), (0,), 0, page, 0)
    spot = attempt("a texel at 4 bits",
                   lambda: local_texel(four, rec, 3, 7), default=None)
    ok("the page offset is counted in TEXELS, not halfwords",
       spot == (atlas.PAGE_UNITS * 4 + 3, 7), "%r" % (spot,))
    eight = _FakePrimitive((((0, 0)),), (0,), 0, page, 1)
    spot8 = attempt("a texel at 8 bits",
                    lambda: local_texel(eight, rec, 3, 7), default=None)
    ok("and the multiplier is the primitive's own depth",
       spot8 == (atlas.PAGE_UNITS * 2 + 3, 7), "%r" % (spot8,))

    # Red: a texel outside the record refuses instead of wrapping into the
    # neighbouring image, which is what a modulo would do and what would look
    # like a texture seam rather than a reading error.  The record here is the
    # shape the hair sheet really has -- narrower than the page it sits in --
    # which is why `u` past its right edge samples the NEXT image on the disc
    # and not a repeat of this one.
    tight = _FakeRecord(page[0], 0, 32, 128, 11)
    refuses("a texel past the right edge refuses",
            lambda: local_texel(four, tight, atlas.COORD - 1, 0),
            "outside its")
    refuses("a texel past the bottom refuses",
            lambda: local_texel(four, tight, 0, tight.h), "outside its")

    # A whole part, with no disc: four points, four coordinates, y flipped.
    vertices = [_FakeVertex(0, 0, 0), _FakeVertex(8, 4, 0),
                _FakeVertex(0, 4, 8), _FakeVertex(8, 0, 8)]
    quad = _FakePrimitive(((0, 0), (16, 0), (0, 32), (16, 32)), (0, 1, 2, 3),
                          0, page, 0)
    fake = Surface((10, 0, 0), rec.w * 4, rec.h, b"", 10, 0, 0)
    part = attempt("build one part",
                   lambda: part_for(quad, vertices, rec, fake, 0, 0,
                                    ("/BIN/X", 0), 0), default=None)
    ok("a part is four points and four texture coordinates",
       part is not None and len(part.points) == 4 and len(part.uvs) == 4,
       "%r" % (part,))
    ok("y is flipped, so the model stands up the way the screen shows it",
       part is not None and part.points[1][1] == -4.0,
       "%r" % (part.points if part else None,))
    ok("the coordinates are normalised, and inside the record",
       part is not None
       and all(0.0 < u < 1.0 and 0.0 < v < 1.0 for u, v in part.uvs),
       "%r" % (part.uvs if part else None,))

    # The band is what a hair style moves, and it moves `v` and nothing else.
    lower = attempt("the same part, one band down",
                    lambda: part_for(quad, vertices, rec, fake, 0,
                                     layout.ATLAS_BAND, ("/BIN/X", 0), 0),
                    default=None)
    ok("a band moves every v and no u",
       lower is not None and part is not None
       and [u for u, _v in lower.uvs] == [u for u, _v in part.uvs]
       and all(b > a for (_u, a), (_u2, b) in zip(part.uvs, lower.uvs)),
       "%r" % (lower.uvs if lower else None,))

    # A primitive this disc cannot texture keeps its geometry and says why --
    # it is not dropped, because a dropped one leaves a whole figure looking
    # finished with a file missing.
    bare = attempt("build a part with no image record",
                   lambda: part_for(quad, vertices, None, None, 0, 0,
                                    ("/BIN/X", 0), 0), default=None)
    ok("an unsampled primitive still has its four points",
       bare is not None and len(bare.points) == 4 and not bare.textured)
    ok("and it says which of the two causes it was",
       bare is not None and "image record" in (bare.why or ""),
       "%r" % (bare.why if bare else None,))
    ok("the placeholder is opaque, so a missing file is visible",
       len(PLACEHOLDER) == 4 and PLACEHOLDER[3] == 255)

    # And one that runs off its record comes back as a placeholder with the
    # reason, rather than as a silently clamped texture.
    off = attempt("build a part that samples past its record",
                  lambda: part_for(
                      _FakePrimitive(((0, 0), (atlas.COORD - 1, 0), (0, 32),
                                      (16, 32)), (0, 1, 2, 3), 0, page, 0),
                      vertices, tight, fake, 0, 0, ("/BIN/X", 0), 0),
                  default=None)
    ok("a part that samples outside its record is not textured",
       off is not None and not off.textured and "outside its" in (off.why or ""),
       "%r" % (off.why if off else None,))

    # Red: a primitive naming a vertex the section does not have refuses.
    refuses("a missing vertex refuses",
            lambda: part_for(_FakePrimitive(((0, 0),) * 4, (0, 1, 2, 99), 0,
                                            page, 0),
                             vertices, rec, fake, 0, 0, ("/BIN/X", 0), 0),
            "vertex 99")

    # Which indices a quad samples, and the BAND that moves it.  A buffer
    # rather than a stream, so the arithmetic is checked with no disc here:
    # row 0 holds index 1, row 16 holds index 5, and the quad is one texel.
    flat = _FakeRecord(page[0], 0, 8, 32, 12)
    wide_flat = flat.w * atlas.texels_per_unit(0)
    buffer = bytearray(wide_flat * flat.h)
    for x in range(wide_flat):
        buffer[x] = 1
        buffer[16 * wide_flat + x] = 5
    dot = _FakePrimitive(((0, 0),) * 4, (0, 1, 2, 3), 0, page, 0)
    ok("a quad samples the indices under it",
       indices_in_quad(bytes(buffer), wide_flat, dot, flat, 0) == {1},
       "%r" % (indices_in_quad(bytes(buffer), wide_flat, dot, flat, 0),))
    ok("and a band moves it to another strip of the same sheet",
       indices_in_quad(bytes(buffer), wide_flat, dot, flat, 16) == {5},
       "%r" % (indices_in_quad(bytes(buffer), wide_flat, dot, flat, 16),))

    # The colour path, on a synthetic container: the index comes from the
    # image and the colour from the WINDOW the id names, so two ids over one
    # image are two surfaces.  This is LOOKS-TASK-12's finding, as arithmetic.
    steps = tuple(range(1, texture.WIDE + 1))
    data = texture.build_container(
        ((0, layout.CLUT_ROW_FIRST, texture.WIDE, steps),))
    palettes = texture.palettes(data)
    first = attempt("the window of column 0",
                    lambda: texture.window_for(palettes, 0,
                                               layout.CLUT_ROW_FIRST,
                                               texture.NARROW),
                    default=(None, None))
    third = attempt("the window of column 3",
                    lambda: texture.window_for(palettes,
                                               3 * texture.NARROW,
                                               layout.CLUT_ROW_FIRST,
                                               texture.NARROW),
                    default=(None, None))
    ok("a CLUT column is an offset into the record, not a record of its own",
       first[1] == 0 and third[1] == 3 * texture.NARROW,
       "%r %r" % (first, third))
    ok("and the grid agrees with skin.py about which column an id is",
       skin.grid(skin.clut_id(layout.CLUT_ROW_FIRST, 3))
       == (layout.CLUT_ROW_FIRST, 3))

    # The shelf, which exists because the files carry no placement.  Two
    # pieces that overlap in file coordinates must not overlap on it, and the
    # arrangement has to be an arrangement and not a pose: same y for all.
    made = Scene([
        Part("/BIN/X", 0, 0, [(-4.0, -4.0, 0.0), (4.0, -4.0, 0.0),
                              (4.0, 4.0, 0.0), (-4.0, 4.0, 0.0)],
             [(0.0, 0.0)] * 4, None, "", 0, 0),
        Part("/BIN/X", 1, 0, [(-2.0, -8.0, 0.0), (2.0, -8.0, 0.0),
                              (2.0, 8.0, 0.0), (-2.0, 8.0, 0.0)],
             [(0.0, 0.0)] * 4, None, "", 0, 0),
    ], {}, {}, 0, {})
    places = attempt("lay two overlapping pieces on the shelf",
                     lambda: shelf(made), default={})
    ok("every piece gets a place", len(places) == 2, "%r" % (places,))
    placed = {}
    for part in made.parts:
        move = places.get((part.file, part.section), (0.0, 0.0, 0.0))
        xs = [point[0] + move[0] for point in part.points]
        placed[(part.file, part.section)] = (min(xs), max(xs))
    ok("and the second stands clear of the first, with the gap between them",
       placed[("/BIN/X", 1)][0] - placed[("/BIN/X", 0)][1] == SHELF_GAP,
       "%r" % (placed,))
    ok("the shelf moves nothing in depth, because it is not a pose",
       all(place[2] == 0.0 for place in places.values()), "%r" % (places,))

    ok("the scene reports what it could not texture instead of hiding it",
       set(Scene([], {}, {}, 0, {"no image": 0}).notes) == {"no image"})
    refuses("an empty scene refuses to have bounds",
            lambda: Scene([], {}, {}, 0, {}).bounds(), "empty scene")


# ---- the disc ------------------------------------------------------------

def _check_image(image_path: str) -> int:
    """The same arithmetic against the real files, where it can be wrong."""
    problems = []
    scene = from_image(image_path, assembly.CORPUS_REFERENCE)
    numbers = summary(scene)
    print("  %s, figure %d: %d primitive(s), %d textured, %d surface(s)"
          % (numbers["tuple"], numbers["figure"], numbers["parts"],
             numbers["textured"], numbers["surfaces"]))
    print("      sections %d, triangles %d, notes %s"
          % (numbers["sections"], numbers["triangles"], numbers["notes"]))
    low, high = numbers["bounds"]
    print("      bounds %s .. %s" % (low, high))

    if numbers["textured"] < 1:
        problems.append("nothing came out textured, so the colour path did "
                        "not run at all")
    if not scene.surfaces:
        problems.append("no surface was built")

    # Up is measured, not declared: the head has to end up ABOVE the boots
    # once UP is applied, and if the disc ever says otherwise the constant is
    # what is wrong.
    heads = [p for p in scene.parts if p.file == layout.MODEL]
    boots = [p for p in scene.parts
             if p.file == layout.EDT_MOD and p.section in layout.BOOT_SECTIONS]
    if heads and boots:
        head_y = sum(pt[1] for p in heads for pt in p.points) / (4 * len(heads))
        boot_y = sum(pt[1] for p in boots for pt in p.points) / (4 * len(boots))
        print("      the head sits at y %.0f and the boots at y %.0f, with "
              "UP = %d" % (head_y, boot_y, UP))
        if head_y <= boot_y:
            problems.append("with UP = %d the head is not above the boots, "
                            "so the flip is backwards" % UP)
    else:
        problems.append("the scene has no head or no boots, so up was not "
                        "measured")

    # Two tuples that differ in one colour field have to differ in SURFACES:
    # same geometry, same images, different palette windows.  A renderer that
    # ignored the CLUT would pass every other check in this file.
    other = from_image(image_path, "A-A1-C-A-A")
    shared = set(scene.surfaces) & set(other.surfaces)
    print("      A-A1-A-A-A has %d surface(s), A-A1-C-A-A has %d, %d shared"
          % (len(scene.surfaces), len(other.surfaces), len(shared)))
    if set(scene.surfaces) == set(other.surfaces):
        problems.append("a hair colour changed no surface, so the CLUT id is "
                        "not reaching the texture")
    if len(other.parts) != len(scene.parts):
        problems.append("a colour field changed the number of primitives, "
                        "which is geometry and not colour")

    # And one that changes the head: a different section, and a different
    # number of parts is expected there rather than suspicious.
    head_swap = from_image(image_path, "A-I3-A-A-A")
    ours = {(p.file, p.section) for p in scene.parts}
    theirs = {(p.file, p.section) for p in head_swap.parts}
    print("      A-I3-A-A-A draws %s where A-A1-A-A-A draws %s"
          % (sorted(theirs - ours), sorted(ours - theirs)))
    if not theirs - ours:
        problems.append("a hair style drew the same sections, so head_of is "
                        "not reaching the scene")

    # And the two axes CROSSED, which is the case neither check above makes:
    # a tuple that changes the head AND the colour has to differ in surfaces
    # from the same head in another colour.  Without it, colour rows addressed
    # to a section the scene does not draw pass both checks above -- the
    # colour one runs on family A, where they work, and the head one only asks
    # which sections are drawn (CORR-LOOKS-034).
    far = from_image(image_path, "B-I3-A-A-A")
    print("      A-I3-A-A-A has %d surface(s), B-I3-A-A-A has %d, %d shared"
          % (len(head_swap.surfaces), len(far.surfaces),
             len(set(head_swap.surfaces) & set(far.surfaces))))
    if set(head_swap.surfaces) == set(far.surfaces):
        problems.append("a skin changed no surface on a head that is not "
                        "section 24, so the colour rows are addressed to a "
                        "section this tuple does not draw")
    # And the skin lands on that head's OWN primitives: measured per head,
    # never section 24's indices by borrowing (CORR-LOOKS-049).  The parts
    # whose CLUT row the skin moved are exactly the table's row for 34.
    moved = sorted(p.primitive for p in far.parts
                   if p.file == layout.MODEL and p.section == 34
                   and p.clut != next(q.clut for q in head_swap.parts
                                      if (q.file, q.section, q.primitive)
                                      == (p.file, p.section, p.primitive)))
    print("      skin B on section 34 moves primitive(s) %s" % moved)
    if tuple(moved) != layout.COLOUR_PRIMITIVES["SKIN"][34]:
        problems.append("skin B on section 34 moved %s, and the table "
                        "measured %s" % (moved,
                                         layout.COLOUR_PRIMITIVES["SKIN"][34]))

    # A colour that changes the SURFACE and changes no PIXEL: declared, with
    # the reason, instead of passing in silence.  Measured 2026-09-16
    # (CORR-LOOKS-038): FACE band 0 is the BEARDLESS face, and its two quads
    # sample none of the entries a beard colour moves -- so H.F.COL. painting
    # nothing there is correct.  Every other band samples them, and a beard
    # colour that stopped working would show up here as bands 1..4 going empty.
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data2d = disc.read(layout.DAT2D)
        model = disc.read(layout.MODEL)
    scan = section.scan(model, layout.GEOMETRY_START[layout.MODEL])
    head = scan.sections[layout.HEAD_SECTION]
    images = texture.images(data2d)
    palettes = texture.palettes(data2d)
    record = [r for r in palettes if r.is_clut
              and r.offset == layout.SKIN_PALETTES[0]][0]
    beard_columns = range(layout.BEARD_COLUMN, skin.COLUMNS)
    moves = set(skin.moving_entries(data2d, record, beard_columns))
    print("      a beard colour moves %d of the window's %d entries: %s"
          % (len(moves), texture.NARROW, sorted(moves)))
    # The bands are A to E only.  F and G are not bands 5 and 6 of these two
    # quads: they draw the head's TWIN (CORR-LOOKS-048), so they are swept
    # below on the twin's own beard quads, at the disc's band and one on.
    bands = {}
    for band in range(assembly.FACE_TWIN_FROM):
        used = set()
        for at in layout.FACE_PRIMITIVES:
            primitive = head.primitives[at]
            where = atlas.image_at(images, *atlas.corners(primitive)[0])
            used |= sampled_indices(data2d, primitive, where,
                                    band * layout.ATLAS_BAND)
        bands[band] = sorted(used & moves)
        print("      FACE band %d samples %d of them: %s"
              % (band, len(bands[band]), bands[band]))
    twin_index = assembly.twin_of(layout.HEAD_SECTION)
    twin = scan.sections[twin_index]
    for step in range(assembly.FACE_TWIN_FROM,
                      assembly.BY_ROW["FACE"].reach):
        used = set()
        for at in layout.FACE_TWIN_QUADS[twin_index]:
            primitive = twin.primitives[at]
            where = atlas.image_at(images, *atlas.corners(primitive)[0])
            used |= sampled_indices(
                data2d, primitive, where,
                (step - assembly.FACE_TWIN_FROM) * layout.ATLAS_BAND)
        bands[step] = sorted(used & moves)
        print("      FACE %s is section %d's own beard quads, %d band(s) on: "
              "they sample %d of them: %s"
              % (assembly.BY_ROW["FACE"].field.label(
                  assembly.BY_ROW["FACE"].field.bias + step), twin_index,
                 step - assembly.FACE_TWIN_FROM, len(bands[step]),
                 bands[step]))
    if bands.get(0):
        problems.append("FACE band 0 samples entries a beard colour moves, "
                        "and it was measured as the beardless face")
    empty = [band for band, used in bands.items() if band and not used]
    if empty:
        problems.append("FACE band(s) %s sample none of the entries a beard "
                        "colour moves, so H.F.COL. paints nothing on them"
                        % empty)

    print("scene --check-image: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line)
    return 1 if problems else 0


def _corpus(image_path: str, folder: str) -> int:
    """How much of the third party's corpus this viewer can draw at all.

    Not a gate, a survey -- a refusal here is the assembly table saying it did
    not measure that value, and counting refusals is how the hole gets a size
    instead of an adjective.  The disc is read once and the fifty tuples are
    built against it, so the answer costs one pass.
    """
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D)}

    names = [name[:-len(looks.CORPUS_SUFFIX)]
             for name in looks.corpus_names(folder)]
    drawn = 0
    refused: dict = {}
    for name in names:
        try:
            build(data, looks.parse_tuple(name))
        except (looks.BadLooks, assembly.BadAssembly, BadScene) as exc:
            reason = str(exc).split(" -- ")[0].split(", and")[0]
            refused.setdefault(reason, []).append(name)
        else:
            drawn += 1
    print("  the corpus: %s, %d name(s)" % (folder, len(names)))
    print("      %d drawn, %d refused" % (drawn, len(names) - drawn))
    for reason in sorted(refused, key=lambda r: -len(refused[r])):
        print("      %2d x %s" % (len(refused[reason]), reason))
        print("           %s" % ", ".join(sorted(refused[reason])))
    return 0 if drawn else 1


def _tuple(image_path: str, text: str, figure: int) -> int:
    scene = from_image(image_path, text, figure)
    numbers = summary(scene)
    print("%s, figure %d: %d primitive(s), %d textured, %d surface(s), "
          "%d triangle(s)"
          % (numbers["tuple"], numbers["figure"], numbers["parts"],
             numbers["textured"], numbers["surfaces"], numbers["triangles"]))
    for name, count in sorted(numbers["notes"].items()):
        print("    %-18s %d" % (name, count))
    for key in sorted(scene.surfaces):
        one = scene.surfaces[key]
        print("    image %-6d depth %d clut %-5d %3dx%-3d"
              % (one.record, one.depth, one.clut, one.width, one.height))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    if len(argv) >= 2 and argv[1] in ("--check-image", "--tuple", "--corpus"):
        import iso_source

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("scene: skipped -- %s" % exc)
            return SKIP
        if argv[1] == "--corpus":
            try:
                folder = looks.corpus_from_env(
                    argv[2] if len(argv) > 2 else None)
            except RuntimeError as exc:
                print("scene: skipped -- %s" % exc)
                return SKIP
            return _corpus(image, folder)
        if argv[1] == "--tuple":
            if len(argv) < 3:
                print("--tuple needs a tuple, like A-A1-A-A-A")
                return 2
            figure = int(argv[3]) if len(argv) > 3 else assembly.HEAD_FIGURE
            return _tuple(image, argv[2], figure)
        return _check_image(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

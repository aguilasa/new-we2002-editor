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

import math
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

    Keyed by the four things that decide the pixels -- the container, the
    record, the page depth and the CLUT id -- because the same image drawn
    through two CLUTs is two different textures, which is exactly what a
    colour field does.  The container joined the key in LOOKS-TASK-30: two
    containers hold records at the same offset, and without it the body's
    texture and the head's collided in the viewer's own table.
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
                palettes, container: str = None) -> Surface:
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
    return Surface((container, record.offset, depth, clut), width, height,
                   bytes(rgba), record.offset, depth, clut)


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
          frame: int = None, kit: str = None) -> Scene:
    """Everything the tuple draws, out of the disc's own bytes.

    The draw list is `assembly`'s and is not recomputed here: which primitive
    a field owns, which head a style picks and which band it samples are all
    measurements, and a second copy of them would be a second thing to keep
    right.
    """
    parts = assembly.draw_list(disc, values, figure, kit)
    # One container per primitive, and the draw list says which: the body's
    # pages are in the kit container and the head's are in the common file,
    # and reading a record out of the wrong bytes decodes perfectly into
    # somebody else's picture (LOOKS-TASK-30).
    banks = {}
    for path in {entry["container"] for entry in parts} - {None}:
        body = disc[path]
        banks[path] = (body, texture.images(body), texture.palettes(body))

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
            body, images, palettes = banks[entry["container"]]
            record = next(r for r in images if r.offset == entry["image"])
            key = (entry["container"], record.offset, primitive.tpage_depth,
                   entry["clut"])
            if key not in surfaces:
                try:
                    surfaces[key] = surface_for(body, record,
                                                primitive.tpage_depth,
                                                entry["clut"], palettes,
                                                entry["container"])
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
    import pieces

    places = pose(disc, frame)
    head = (layout.MODEL, pieces.HEAD_SECTION)
    notes["not posed"] = 0
    out = []
    for part in parts:
        found = place_for(places, (part.file, part.section), head)
        if found is None:
            notes["not posed"] += 1
            out.append(part)
            continue
        matrix, place = found
        moved = Part(part.file, part.section, part.primitive,
                     drawn_points(part.points, matrix, place), part.uvs,
                     part.surface, part.why, part.clut, part.band,
                     part.band_unmeasured)
        out.append(moved)
    return out


def place_for(places: dict, where: tuple, head: tuple):
    """The pose of one drawn section, or None.

    **Every head the HAIR row can pick takes the HEAD's pose.**  The row
    chooses a MODEL.BIN section -- 24 for A, 30 for C1, 34 for I3 -- and
    ANIME.BIN carries one head pair whichever it is.  Keyed by section alone,
    every style but the reference kept its head at the file's origin, 23 to 25
    primitives floating off the neck, and every check stayed green because the
    checks drew the reference.  Found by LOOKS-TASK-28's silhouette, which drew
    C1 and I3 headless.
    """
    found = places.get(where)
    if found is None and where[0] == layout.MODEL:
        found = places.get(head)
    return found


def from_image(image_path: str, text: str,
               figure: int = assembly.HEAD_FIGURE,
               frame: int = None, kit: str = layout.KIT_ON_SCREEN) -> Scene:
    """The whole path, from a disc on disc to a scene -- what `ui/app.py` calls.

    It lives here and not in the window because the window is forbidden the
    three modules this needs, which is rule 3 and not an accident of layering.
    """
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D,
                             layout.ANIME)}
        if kit is not None:
            data[layout.kit_path(kit)] = disc.read(layout.kit_path(kit))
    # A tuple the table refuses arrives here as BadScene, with the table's own
    # sentence kept whole.  The window is not allowed to import `assembly` or
    # `looks` to catch their exceptions, and a refusal that reaches it as a
    # traceback reads as a crash of the viewer rather than as the measured "no"
    # it is -- three hair styles and one beard value are exactly that.
    try:
        values = looks.parse_tuple(text)
        return build(data, values, figure, frame, kit)
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

    __slots__ = ("image_path", "figure", "frame", "kit", "_data")

    def __init__(self, image_path: str, figure: int = assembly.HEAD_FIGURE,
                 frame: int = None):
        import iso_source

        self.image_path = image_path
        self.figure = figure
        # The frame every `build` poses in unless one is named.  The screen
        # carries it so that the panel opens with the figure ASSEMBLED, which
        # is what LOOKS-TASK-27 delivers; `None` is the shelf, still reachable.
        self.frame = frame
        self.kit = layout.KIT_ON_SCREEN
        with iso_source.open_disc(image_path) as disc:
            self._data = {name: disc.read(name)
                          for name in (layout.EDT_MOD, layout.MODEL,
                                       layout.DAT2D, layout.ANIME,
                                       layout.SELECT8,
                                       layout.kit_path(self.kit))}

    def build(self, text: str, frame: int = None) -> Scene:
        """*text* as a scene, or `BadScene` carrying the table's own sentence."""
        try:
            values = looks.parse_tuple(text)
            return build(self._data, values, self.figure,
                         self.frame if frame is None else frame, self.kit)
        except (looks.BadLooks, assembly.BadAssembly) as exc:
            raise BadScene(str(exc)) from exc

    def scale(self, values: dict) -> tuple:
        """The figure's scale for the screen's `HEIG` and `BODY` (`stature`)."""
        return figure_scale(self._data, values)




# --- the pose: the pieces where the game puts them -------------------------

ONE = 4096  # not-an-address: 1.0 in the 4.12 the matrix is in

REFERENCE_PIECE = "foot b"
"""The piece every place is measured from.

ANIME.BIN stores places relative to one another, so assembling means picking
one of them and subtracting it; the game does the same and lets its camera
carry the rest.  This is the twelfth pair of a frame, and it is a PIECE like
the other eleven -- the second boot, measured in CORR-LOOKS-062.

It read `root` until 2026-09-18, on the reading that the twelfth load draws
nothing: `anime.PIECE_ORDER` carries the three measurements that name it.  What
changes here beyond the name is that the second boot is no longer PLACED by
mirroring the first -- it has a place of its own, and it is this one, so it
sits at the origin.

**The anchor swings, and that is a real consequence.**  A boot in a walk moves
against the body, so posing frame after frame around this one slides the whole
figure by the stride.  It does not show in one frame, which is all the panel
draws today; the walk (LOOKS-TASK-32) is where the anchor has to become
something that does not swing, and the file gives no such piece -- the game's
own camera translation is the candidate.
"""

REFERENCE_FRAME = 0
"""The frame of the screen's animation a scene is posed in when none is asked
for.  Frame 0 of `layout.ANIME_SCREEN_ENTRY`, which is where the walk starts."""

POSED_STYLES = ("A-A1-A-A-A", "A-C1-A-A-A", "A-I3-A-A-A")
"""Three hair styles whose heads are three different MODEL.BIN sections.

24, 30 and 34.  One is the reference and passes by construction; the other two
are why this exists -- a pose keyed by one head section left theirs unposed.
"""

SIDES_APART = 55
"""How far apart in y the two sides of one limb pair may sit, in file units.

Measured over ALL seventeen frames of the screen's walk and not over the one
frame the check poses (pitfall 49): the widest a pair ever gets is the BOOTS
at 36.7, then the shin at 26.7, the forearm at 16.0, the thigh at 12.1 and the
upper arm at 5.9.  A walking figure swings, so this is not zero and cannot be;
what it catches is a pose read one piece off, which puts one elbow above its
own shoulder.

**It read 45 until CORR-LOOKS-062, on a measurement that had the boots at 0.**
That zero was not the walk, it was the mirror: the second boot was placed by
reflecting the first, and a reflection in z leaves y untouched, so the pair
this check compares was the same number twice.  The widest pair of the walk
turned out to be exactly that one, and the value moved to clear it.
"""

ANKLE_DEEP = 90
"""How far in z a boot may sit from its own shin's middle, in file units.

Measured over the seventeen frames, both boots: 41.3 on the `a` side and 59.1
on the `b`, so this clears the widest by half again (pitfall 49).

This is the check the pair comparison could not be.  The two boots of a stride
are legitimately far apart in z -- 219 at the widest of the walk, because that
is what a stride IS -- so no threshold between them can separate a stride from
a boot in the wrong place.  What has a narrow range is the ANKLE, which is the
rigid joint the draw lag was settled by (`anime.PIECE_ORDER`): the mirror that
CORR-LOOKS-062 removed put `foot b` 276.5 from its shin, three times this.
"""


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


def _figure_sections(disc) -> dict:
    """{model list: the EDT_MOD sections that list draws}.

    The file's own two lists (`modelfile`), not a grouping made here: the
    goalkeeper and the outfield player share the boots and nothing else, and
    which list a section belongs to is the only thing that says whose leg a
    boot is on.
    """
    import modelfile

    data = disc[layout.EDT_MOD]
    scan = section.scan(data, layout.GEOMETRY_START[layout.EDT_MOD])
    index_of = {one.offset: i for i, one in enumerate(scan.sections)}
    return {model.index: {index_of[target] for target in model.targets}
            for model in modelfile.read_models(data)}


def mirror_of(name: str) -> str:
    """The partner of a mirrored piece, or None.

    `pieces.py` pairs the limbs and calls one of each pair `a` and the other
    `b`.  What uses it is `standing()`, to check a pair against itself; nothing
    places a piece from its partner any more (CORR-LOOKS-062).
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

    **Every drawn piece has a place of its own here, the second boot too.**
    Until CORR-LOOKS-062 that boot was the exception -- placed by mirroring its
    partner in z, because the file was read as carrying eleven pairs for twelve
    drawn sections.  It carries twelve: the pair that was called `root` is the
    second boot (`anime.PIECE_ORDER`).  The mirror was not a small error.  It
    put the boot 258 units from its own shin against the other boot's 18, and
    the leg in the air ended without a foot, because the two legs of a stride
    are not reflections of each other.
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
        if carried is None:
            continue
        matrix = anime.rotation(carried["angles"])
        place = tuple(carried["position"][axis] - origin[axis]
                      for axis in range(3))
        out[where] = (matrix, place)
    return out


CHAINS = (("head", "torso", "thigh a", "shin a", "foot a"),
          ("torso", "thigh b", "shin b", "foot b"),
          ("upper arm a", "forearm a"),
          ("upper arm b", "forearm b"))
"""The pieces that have to come in this order DOWN the figure.

Four chains and not one: the shoulder sits at the torso's own middle -- 3 units
apart, measured -- so an arm is not "below the torso", and demanding it would
be anatomy invented to make a check pass.  What is here is what the model
files themselves say: the thigh's origin is its hip and it reaches 111 units
down, the shin's is its knee, the boot's is its ankle.

**Both sides, since CORR-LOOKS-062.**  Naming only the `a` pieces left the
whole `b` leg out of every order this asserts, and the boot that was wrong was
`foot b` -- the one chain that could have caught it was the one not written.
The pair check below does not cover for that: it compares a piece with its own
partner, so a leg that is wrong in the same way on both sides passes it.
"""


def standing(middles: dict, depths: dict = None) -> list:
    """Everything wrong with where the pieces ended up.  [] is a figure.

    *middles* is {piece name: the middle of its y}, in the file's own units,
    and *depths* the same in z.  This is the assertion LOOKS-TASK-27 opened
    for and could not close until the draw lag was measured: one stop off,
    every number is in range, each piece is individually perfect, and the boot
    comes out at thigh height.

    **The depths are what makes it able to fail on a boot** (CORR-LOOKS-062).
    Height alone cannot: a boot placed by mirroring its partner has its
    partner's height exactly, so every y here agreed while the foot sat a
    stride away from its own leg.  Passing them is optional so that the
    made-up figures of the self check can still be one dict, but a run with a
    disc in hand passes both.
    """
    bad = []
    for order in CHAINS:
        for above, below in zip(order, order[1:]):
            if above in middles and below in middles \
                    and middles[above] * UP < middles[below] * UP:
                bad.append(
                    "the %s sits at y %.0f and the %s at %.0f, so the figure "
                    "does not stand: %s is not above %s"
                    % (above, middles[above], below, middles[below],
                       above, below))
    # And the two sides are the same height, which is what a pose read one
    # piece off breaks first: it puts one elbow above its own shoulder.
    for left in sorted(one for one in middles if one.endswith(" a")):
        right = mirror_of(left)
        if right not in middles:
            continue
        apart = abs(middles[left] - middles[right])
        if apart > SIDES_APART:
            bad.append(
                "%s sits %.0f from %s, over the %d a walking pose takes -- the "
                "two sides are not the same figure"
                % (left, apart, right, SIDES_APART))
    # And each boot is on the end of its OWN leg.  The ankle is the one joint
    # of this figure that holds rigid (`anime.PIECE_ORDER`), so it is the one
    # distance a threshold can be written for.
    for side in ("a", "b"):
        boot, shin = "foot " + side, "shin " + side
        if depths is None or boot not in depths or shin not in depths:
            continue
        deep = abs(depths[boot] - depths[shin])
        if deep > ANKLE_DEEP:
            bad.append(
                "%s sits %.0f in z from %s, over the %d an ankle takes -- that "
                "boot is not on that leg"
                % (boot, deep, shin, ANKLE_DEEP))
    return bad


def drawn_points(points, matrix, place) -> list:
    """`place_points`, for points that have already been flipped for drawing.

    `part_for` stores `y * UP`, so the points a Part carries are in the DRAWN
    frame and the pose is in the FILE's -- y down, as `ANIME.BIN` and the GTE
    both have it.  Applying one in the other's frame turns the figure upside
    down piece by piece while every piece stays individually upright, which is
    what the first render of the assembled figure did: head at the bottom and
    the boot in the air.  `UP` is its own inverse, so the flip undone on the
    way in and redone on the way out is the whole of it.
    """
    turned = place_points([(one[0], one[1] * UP, one[2]) for one in points],
                          matrix, place)
    return [(one[0], one[1] * UP, one[2]) for one in turned]


def place_points(points, matrix, place) -> list:
    """One piece's points, turned and put where the frame says, IN FILE SPACE.

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

# --- the game's own camera, and the shape it projects ----------------------

CAMERA_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "work", "looks-camera")
"""Where `oracle.py --camera` leaves what it measured, one JSON per slot."""


class NoCamera(BadScene):
    """No measured camera on disc, so nothing may be projected."""


def load_camera(slot: int = 2, scale=None) -> dict:
    """What `oracle.py --camera` measured, or `NoCamera`.

    It is never defaulted and never guessed at: a projection invented here
    would make every silhouette comparison a comparison of two inventions, and
    the whole point of section 10.4 (3) is that the camera comes from the game.

    **With *scale*, the camera of a figure of another height or build.**  The
    game puts `HEIG` and `BODY` INSIDE the camera (`stature`): the matrix it
    hands the GTE is the view times the figure's own turn scaled per axis.  So
    the camera for another scale is composed from the chain `--camera` read
    beside the load, and the chain has to reproduce the load at the state's own
    scale, integer for integer, before it is trusted with any other.
    """
    import json

    path = os.path.join(CAMERA_DIR, "slot%d.json" % slot)
    if not os.path.isfile(path):
        raise NoCamera("no %s -- run `oracle.py --camera %d` first, which is "
                       "what measures H and the camera matrix off the GTE"
                       % (path, slot))
    with open(path, encoding="utf-8") as handle:
        record = json.load(handle)
    projections = {tuple(sorted(one.items())) for one in record["projection"]}
    if len(projections) != 1:
        raise NoCamera("%s carries %d different projections, so there is no "
                       "one camera in it" % (path, len(projections)))
    camera = {"rotation": record["camera"]["rotation"],
              "translation": record["camera"]["translation"],
              "projection": record["projection"][0]}
    if scale is None:
        return camera
    import stature

    chain = record.get("chain")
    if chain is None:
        raise NoCamera("%s has no chain -- it was written before LOOKS-TASK-29;"
                       " run `oracle.py --camera %d` again, which reads the "
                       "view and the figure's scale beside the load"
                       % (path, slot))
    try:
        own = stature.camera(chain, chain["scale"])
    except stature.BadStature as exc:
        raise NoCamera("%s: %s" % (path, exc)) from exc
    if (own["rotation"] != camera["rotation"]
            or own["translation"] != camera["translation"]):
        raise NoCamera("%s: the chain composes %r at the state's own scale, "
                       "and the game loaded %r -- the chain is not the camera"
                       % (path, own, record["camera"]))
    try:
        composed = stature.camera(chain, scale)
    except stature.BadStature as exc:
        raise NoCamera("%s: %s" % (path, exc)) from exc
    return dict(camera, rotation=composed["rotation"],
                translation=composed["translation"])


def figure_scale(disc, values: dict) -> tuple:
    """(x, y, z) in 4.12 for the `height` and `build` of *values*.

    Read off the screen's own overlay, never written here (`stature.rule`).
    """
    import stature

    try:
        found = stature.rule(disc[layout.SELECT8])
        return stature.scale(found, values["height"], values["build"])
    except stature.BadStature as exc:
        raise BadScene(str(exc)) from exc


SCENERY_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "work", "looks-scenery")
"""Where `oracle.py --scenery --write` leaves what it measured, per slot."""


class NoScenery(BadScene):
    """No measured furniture on disc, so the window has none to draw."""


def load_scenery(slot: int = 2) -> list:
    """The screen's furniture as the game draws it, or `NoScenery`.

    One entry per packet: `{"points", "colours", "gradient"}`, in the display's
    own 512x240 pixels, measured off the display list in RAM and held against
    the frame the console showed (LOOKS-TASK-31).  It is never defaulted: the
    colours the window used before this were chosen by eye, and a table that
    quietly fell back to them would make the window's picture a description of
    itself.
    """
    import json

    path = os.path.join(SCENERY_DIR, "slot%d.json" % slot)
    if not os.path.isfile(path):
        raise NoScenery("no %s -- run `oracle.py --scenery %d --write` first, "
                        "which is what measures the furniture off the band"
                        % (path, slot))
    with open(path, encoding="utf-8") as handle:
        record = json.load(handle)
    packets = record.get("packets") or []
    if not packets:
        raise NoScenery("%s holds no packet, so there is no furniture in it"
                        % path)
    return packets


def to_camera(point, camera) -> tuple:
    """One point of the FILE's frame, in the camera's.

    `v = R * p / ONE + T`, with `R` the matrix the game hands the GTE for the
    camera and `T` its translation -- both measured, both 4.12 and whole units
    respectively, exactly as the hardware has them.
    """
    matrix, place = camera["rotation"], camera["translation"]
    return tuple(sum(matrix[axis * 3 + k] * point[k] for k in range(3))
                 / float(ONE) + place[axis] for axis in range(3))


NEAR = 1.0
"""Camera-space z under which a point is behind the lens and is not drawn."""


def project(point, camera) -> tuple:
    """(sx, sy) in pixels, by the GTE's own `RTPS`, or None behind the lens.

    `SX = OFX + H * x / z`.  The offsets measured on this screen are ZERO --
    the panel is placed by the GPU's own draw offset and not by the GTE -- so
    what comes out is in the figure's own screen frame, with the camera's axis
    at the origin.  Where that frame sits inside the panel is one translation,
    and `silhouette` takes it rather than inventing it.
    """
    view = to_camera(point, camera)
    if view[2] <= NEAR:
        return None
    found = camera["projection"]
    return (found["OFX"] + found["H"] * view[0] / view[2],
            found["OFY"] + found["H"] * view[1] / view[2])


NEAR_PLANE = 16.0
FAR_PLANE = 16384.0
"""The depth range the game's own camera space is mapped into.

They decide nothing about where a pixel lands -- `H` and the matrix do that --
and only how depth is resolved between pieces.  Wide enough to hold the whole
figure at the z the camera measured (about 4125) with room either side.
"""


def camera_matrix(camera: dict, size: tuple, centre: tuple) -> list:
    """The game's camera as one 4x4, row major, for points in the DRAWN frame.

    What it is FOR: the window draws the panel with the projection the game
    projects with, instead of the orbital camera of the v1.  What it is NOT is
    a second implementation of `project()` -- `self_check` runs the two against
    each other on made-up points and demands they land on the same pixel, so a
    change to one that the other does not follow is a failure rather than a
    slow drift between the picture and the measurement.

    Three things are folded in, in this order: the flip of `y` (`part_for`
    stores the drawn frame and the camera is in the file's), the camera's own
    rotation and translation, and `RTPS` -- `SX = OFX + H * x / z` -- turned
    into clip space for a viewport of *size* with the camera's axis at
    *centre*.
    """
    width, height = size
    found = camera["projection"]
    matrix, place = camera["rotation"], camera["translation"]
    focal = float(found["H"])
    across = 2.0 * (found["OFX"] + centre[0]) / width - 1.0
    down = 1.0 - 2.0 * (found["OFY"] + centre[1]) / height
    depth = (FAR_PLANE + NEAR_PLANE) / (FAR_PLANE - NEAR_PLANE)
    shift = -2.0 * FAR_PLANE * NEAR_PLANE / (FAR_PLANE - NEAR_PLANE)
    # view: the drawn frame flipped back, then R / ONE and + T.
    view = []
    for axis in range(3):
        row = [matrix[axis * 3 + k] / float(ONE) for k in range(3)]
        row[1] *= UP
        view.append(row + [float(place[axis])])
    view.append([0.0, 0.0, 0.0, 1.0])
    projection = [
        [2.0 * focal / width, 0.0, across, 0.0],
        [0.0, -2.0 * focal / height, down, 0.0],
        [0.0, 0.0, depth, shift],
        [0.0, 0.0, 1.0, 0.0],
    ]
    out = []
    for row in projection:
        for column in range(4):
            out.append(sum(row[k] * view[k][column] for k in range(4)))
    return out


ROOT_AT = (0.5, 0.85)
"""Where the figure's ROOT is put inside the panel, as a fraction of it.

**A framing choice, and it is said to be one.**  Where the game puts the figure
inside the panel is the GPU's draw offset, which this cycle has not measured
(`oracle.py --camera` measured the GTE's offsets and they are zero), so the
window places the root itself.  The root and not the ink box: the root is the
ground the figure stands on and does not move with the pose, where a box
centred per frame would make the figure bob as the walk swings.
"""


def panel_camera(drawn: Scene, slot: int, size: tuple, scale=None) -> list:
    """The game's camera as a 4x4 for the panel, root placed by `ROOT_AT`.

    *size* is the panel in NATIVE pixels, never the widget's: `H` is in the
    game's own pixels, so a viewport twice as wide scales the whole picture
    rather than halving the figure inside it.  *scale* is `figure_scale` of
    the rows on screen, so `HEIG` and `BODY` reach the drawing the way the
    game makes them reach it -- through the camera (LOOKS-TASK-29).
    """
    camera = load_camera(slot, scale)
    origin = project((0.0, 0.0, 0.0), camera)
    if origin is None:
        raise BadScene("the figure's root is behind the camera")
    return camera_matrix(camera, size,
                         (size[0] * ROOT_AT[0] - origin[0],
                          size[1] * ROOT_AT[1] - origin[1]))


def clip_to_pixel(clip, size: tuple) -> tuple:
    """(x, y) in pixels out of a clip-space point, or None behind the lens."""
    width, height = size
    if clip[3] <= 0.0:
        return None
    return ((clip[0] / clip[3] + 1.0) * width / 2.0,
            (1.0 - clip[1] / clip[3]) * height / 2.0)


def apply_matrix(matrix: list, point) -> list:
    """One point through a row-major 4x4, as (x, y, z, w)."""
    wide = (point[0], point[1], point[2], 1.0)
    return [sum(matrix[row * 4 + k] * wide[k] for k in range(4))
            for row in range(4)]


def _fill(mask, width, height, triangle) -> None:
    """One triangle into *mask*, by scanline, with no library.

    A top-left rule is not wanted here and would be wrong to invent: what this
    builds is a SILHOUETTE, so a pixel touched by any triangle is set, and the
    seam between two triangles of one quad must not leave a hole.
    """
    ys = [one[1] for one in triangle]
    top = max(0, int(math.floor(min(ys))))
    bottom = min(height - 1, int(math.ceil(max(ys))))
    for y in range(top, bottom + 1):
        middle = y + 0.5
        crossings = []
        for index in range(3):
            (x0, y0), (x1, y1) = triangle[index], triangle[(index + 1) % 3]
            if (y0 <= middle) == (y1 <= middle):
                continue
            crossings.append(x0 + (middle - y0) * (x1 - x0) / (y1 - y0))
        if len(crossings) < 2:
            continue
        left = max(0, int(math.floor(min(crossings))))
        right = min(width - 1, int(math.ceil(max(crossings))))
        row = y * width
        for x in range(left, right + 1):
            mask[row + x] = 1


def silhouette(drawn: Scene, camera: dict, size: tuple,
               centre: tuple) -> bytearray:
    """The figure's mask, `size` wide and tall, as one byte per pixel.

    *centre* is where the camera's own axis lands inside the picture, in
    pixels.  It is the ONE thing this cannot measure -- the GTE's offsets are
    zero on this screen and the panel is placed by the GPU's draw offset -- so
    it is an argument, measured once by the caller and then held still across
    every comparison.  A centre refitted per picture would turn a prediction
    into a fit.
    """
    width, height = size
    mask = bytearray(width * height)
    for part in drawn.parts:
        # The points are in the DRAWN frame, where `part_for` has already
        # flipped y; the camera is in the file's.  `UP` is its own inverse.
        flat = [project((one[0], one[1] * UP, one[2]), camera)
                for one in part.points]
        if any(one is None for one in flat):
            continue
        moved = [(one[0] + centre[0], one[1] + centre[1]) for one in flat]
        for corners in TRIANGLES:
            _fill(mask, width, height, [moved[at] for at in corners])
    return mask


def projected_box(drawn: Scene, camera: dict) -> tuple:
    """(left, top, right, bottom) of the projected points, UNCLIPPED.

    `silhouette` rasterises into a picture and so cannot say where a figure
    landed when it landed outside it -- and with the GTE's offsets measured at
    zero it always does, by about 170 pixels.  This is what the one
    translation is measured from.
    """
    flat = [project((one[0], one[1] * UP, one[2]), camera)
            for part in drawn.parts for one in part.points]
    flat = [one for one in flat if one is not None]
    if not flat:
        raise BadScene("every point of the scene is behind the lens")
    xs = [one[0] for one in flat]
    ys = [one[1] for one in flat]
    return (min(xs), min(ys), max(xs), max(ys))


def mask_box(mask: bytearray, size: tuple) -> tuple:
    """(left, top, right, bottom) of what is set, or None when nothing is."""
    width, _height = size
    on = [index for index, value in enumerate(mask) if value]
    if not on:
        return None
    xs = [index % width for index in on]
    ys = [index // width for index in on]
    return (min(xs), min(ys), max(xs), max(ys))


def masks_differ(one: bytearray, two: bytearray) -> int:
    """How many pixels one mask has and the other has not, both ways."""
    return sum(1 for a, b in zip(one, two) if a != b)


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

    # -- the figure stands, on numbers made up here ------------------------
    #
    # The real ones come off the disc in `--check-image`; these exist so the
    # judge itself has a red case that needs no image, and the red one is the
    # defect LOOKS-TASK-27 actually hit: the boot one stop off, at the thigh.
    upright = {"head": -380, "torso": -300, "upper arm a": -300,
               "upper arm b": -300, "forearm a": -230, "forearm b": -230,
               "thigh a": -160, "thigh b": -160, "shin a": -50, "shin b": -50,
               "foot a": 10, "foot b": 10}
    # -- whichever head the HAIR row picks, it is posed as the head ---------
    fake = {(layout.MODEL, 24): "the head's pose",
            (layout.EDT_MOD, 5): "a thigh's pose"}
    ok("a head of another style takes the head's pose",
       place_for(fake, (layout.MODEL, 34), (layout.MODEL, 24))
       == "the head's pose")
    ok("and a body section with no pose of its own gets none, not the head's",
       place_for(fake, (layout.EDT_MOD, 9), (layout.MODEL, 24)) is None)

    ok("a figure in order is a figure", standing(upright) == [],
       "%r" % (standing(upright),))
    boot_up = dict(upright, **{"foot a": -170, "foot b": -170})
    ok("a boot at thigh height is not", standing(boot_up))
    ok("and the message names the two pieces out of order",
       "foot a" in standing(boot_up)[0] and "shin a" in standing(boot_up)[0])
    # The b side, which the chains name since CORR-LOOKS-062 -- before that
    # the pair check below was the only thing that could catch it, and a boot
    # is exactly what the pair check cannot catch.
    boot_up_b = dict(upright, **{"foot b": -170})
    ok("a boot at thigh height on the b leg is not either",
       standing(boot_up_b))
    ok("and the message names the b pieces out of order",
       "foot b" in standing(boot_up_b)[0] and "shin b" in standing(boot_up_b)[0])
    lopsided = dict(upright, **{"forearm b": -230 + SIDES_APART * 2})
    ok("one arm hung far from its own pair is not either",
       standing(lopsided))
    ok("and the message names the pair", "forearm" in standing(lopsided)[0])
    ok("a pair inside the swing of a walk is left alone",
       standing(dict(upright,
                     **{"forearm b": -230 + SIDES_APART - 1})) == [])

    # -- the boot is on its own leg, in z ----------------------------------
    #
    # The red case is the defect CORR-LOOKS-062 found, written as it was: the
    # second boot placed by mirroring the first, which leaves every HEIGHT
    # right -- `mirrored` below passes `standing(middles)` with no depths, and
    # that is the point, not an aside.
    # The numbers are frame 0's own, off the disc: `--check-image` prints the
    # two ankles as 41 and 23, and the mirror put the second boot at +236.
    square = {"shin a": -195.0, "foot a": -236.0, "shin b": -40.0,
              "foot b": -17.0}
    ok("a figure whose boots are each on their own leg is a figure",
       standing(upright, square) == [], "%r" % (standing(upright, square),))
    mirrored = dict(square, **{"foot b": 236.0})
    ok("a boot placed by mirroring its partner is not",
       standing(upright, mirrored))
    ok("and it passes on heights alone, which is why the depths are here",
       standing(upright) == [])
    ok("the message names the boot and its own shin",
       "foot b" in standing(upright, mirrored)[0]
       and "shin b" in standing(upright, mirrored)[0])
    ok("an ankle inside the swing of a walk is left alone",
       standing(upright, dict(square,
                              **{"foot b": -40.0 + ANKLE_DEEP - 1})) == [])

    # -- the 4x4 the window draws with is the same arithmetic as project() --
    #
    # Two implementations of one projection is how a picture and a measurement
    # drift apart without either looking wrong.  Made-up camera, made-up
    # points, and they have to land on the same pixel.
    # not-an-address: a camera made up in the shape of the measured one
    turn = [3195, 0, 635, -27, 2488, 133, -635, -268, 3195]  # not-an-address: 4.12 matrix entries
    made_up = {"rotation": turn,
               "translation": [-480, 192, 4125],  # not-an-address: model units
               "projection": {"H": 1376, "OFX": 0.0, "OFY": 0.0}}  # not-an-address: pixels
    size, centre = (146, 120), (70.0, 55.0)
    built = camera_matrix(made_up, size, centre)
    worst = 0.0
    for point in ((0, 0, 0), (30, -200, 10), (-40, 100, -25), (5, 419, -281)):
        flat = project((point[0], point[1] * UP, point[2]), made_up)
        through = clip_to_pixel(apply_matrix(built, point), size)
        worst = max(worst, max(abs(a + b - c) for a, b, c
                               in zip(flat, centre, through)))
    ok("the window's 4x4 lands where project() lands, to the pixel",
       worst < 0.001, "worst %.6f px" % worst)
    behind = apply_matrix(built, (0, 0, -10000))  # not-an-address: a point behind the lens
    ok("and a point behind the lens has no pixel",
       clip_to_pixel(behind, size) is None)

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

    # DRESSED, and both figures: the body's pages live in the kit container
    # and not in the common file, so a figure drawn without one comes back
    # with 237 of its 593 primitives grey (429 of 629 for the goalkeeper) and
    # passes every other check here (section 6 (f), LOOKS-TASK-30).
    for figure in (assembly.HEAD_FIGURE, 1 - assembly.HEAD_FIGURE):
        dressed = from_image(image_path, assembly.CORPUS_REFERENCE, figure)
        counts = summary(dressed)
        print("      figure %d in TEX_%s: %d of %d primitive(s) textured, "
              "notes %s" % (figure, layout.KIT_ON_SCREEN, counts["textured"],
                            counts["parts"], counts["notes"]))
        if counts["textured"] != counts["parts"]:
            problems.append("figure %d left %d primitive(s) untextured with "
                            "the kit container read"
                            % (figure, counts["parts"] - counts["textured"]))
    # And the red case beside it, so the line above is a measurement and not a
    # description: with no kit, the body is grey.
    bare = summary(from_image(image_path, assembly.CORPUS_REFERENCE,
                              assembly.HEAD_FIGURE, None, None))
    print("      and with no kit at all: %d of %d textured, notes %s"
          % (bare["textured"], bare["parts"], bare["notes"]))
    if bare["textured"] == bare["parts"]:
        problems.append("a figure drawn with no kit came out fully textured, "
                        "so the kit is not what dresses it")

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

    # --- the figure stands up, and the file is what stands it up -----------
    #
    # The order of the pieces DOWN the figure, asserted rather than looked at.
    # It is the check LOOKS-TASK-27 opened for and could not close until the
    # draw lag was measured (`oracle.DRAW_LAG`): one stop off, every number
    # here is in range and the boot comes out at thigh height.  What this adds
    # to the lag measurement is the other half -- the lag is measured on the
    # captures, and this says the DISC's own bytes agree with it.
    with iso_source.open_disc(image_path) as disc:
        posed = {name: disc.read(name)
                 for name in (layout.EDT_MOD, layout.MODEL, layout.ANIME,
                              layout.DAT2D)}
    places = pose(posed, REFERENCE_FRAME)
    scans = {name: section.scan(posed[name], layout.GEOMETRY_START[name])
             for name in (layout.EDT_MOD, layout.MODEL)}
    names = piece_names(posed)
    # ONE FIGURE AT A TIME, since CORR-LOOKS-062.  The two model lists name
    # their sections apart -- the outfield player's torso is section 0 and the
    # goalkeeper's is 11 -- and both are called "torso" here, so a single dict
    # kept whichever came last and asserted a figure that is neither.  The two
    # boots are shared, which is why the leg they belong to has to be checked
    # against the legs of the SAME list.
    for lists, over in sorted(_figure_sections(posed).items()):
        middles, depths = {}, {}
        for where, (matrix, place) in places.items():
            if where[0] == layout.EDT_MOD and where[1] not in over:
                continue
            points = [(v.x, v.y, v.z) for v in scans[where[0]].sections[
                where[1]].vertices]
            moved = place_points(points, matrix, place)
            heights = [one[1] for one in moved]
            deep = [one[2] for one in moved]
            middles[names[where]] = (min(heights) + max(heights)) / 2.0
            depths[names[where]] = (min(deep) + max(deep)) / 2.0
        for order in CHAINS:
            print("      figure %d, top down: %s"
                  % (lists, ", ".join("%s %.0f" % (name, middles[name])
                                      for name in order if name in middles)))
        print("      figure %d, the ankles in z: %s"
              % (lists, ", ".join(
                  "%s to %s %.0f"
                  % (boot, shin, abs(depths[boot] - depths[shin]))
                  for boot, shin in (("foot a", "shin a"), ("foot b", "shin b"))
                  if boot in depths and shin in depths)))
        problems += standing(middles, depths)

    # --- every head the HAIR row picks is posed ------------------------------
    #
    # `standing` measures the figure the reference tuple draws, and the
    # reference wears section 24 -- the one head `pose()` knew by section.
    # Every other style picks another section and kept its head at the file's
    # origin, 23 to 25 primitives off the neck, while every check above stayed
    # green.  LOOKS-TASK-28's silhouette found it by drawing C1 and I3
    # headless; this is the guard that does not need an emulator to.
    for text in POSED_STYLES:
        drawn = build(posed, looks.parse_tuple(text), assembly.HEAD_FIGURE,
                      REFERENCE_FRAME)
        heads = sorted({part.section for part in drawn.parts
                        if part.file == layout.MODEL})
        left = drawn.notes.get("not posed", 0)
        print("      %s draws head section(s) %s, %d primitive(s) not posed"
              % (text, heads, left))
        if left:
            problems.append(
                "%s leaves %d primitive(s) without a pose -- its head sits at "
                "the file's origin, off the neck" % (text, left))

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

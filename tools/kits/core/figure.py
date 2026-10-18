"""The one bridge between the kits core and the `looks` scene.

PLAN-KITS-PY.md section 3.1: `figure.py` asks the `scene` of `tools/looks/`
for the 3D figure, and no other module of the core does.  The geometry --
`EDT_MOD.BIN`, `MODEL.BIN`, `DAT2D.BIN`, `ANIME.BIN` -- comes from a disc the
looks guard trusts (section 2.1); the kit comes from wherever the user took it,
as the bytes `tex` already put behind the guard of form, so a TEX off a patch
or out of a file is drawn on the trusted body.

    scene = figure.scene_of(kit, kit_set, figure, geometry_path=None, frame=None,
                            armband=False, sleeves=None)

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

from . import raster, tex  # noqa: F401  (tex puts tools/pes2 and tools/looks on sys.path)
from .errors import FigureError, GeometryRefused, NoGeometry

import assembly  # noqa: E402  (tools/looks)
import atlas  # noqa: E402
import layout  # noqa: E402
import looks  # noqa: E402
import pieces  # noqa: E402
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
             geometry=None, armband: bool = False, sleeves: str = None, player: str = None):
    """The looks `Scene` of *figure* wearing set *kit_set* of *kit*, with the
    captain's *armband* and *sleeves* ("short" or "long"; None, the
    figure's own: short for the player, long for the goalkeeper) put on by
    `dressed_scene`, and with *player* (a looks tuple, `A-L3-H-A-A`) the
    head that player's record draws (`player_headed`); None keeps `TUPLE`'s.

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
    if figure == KEEPER_FIGURE:
        # The goalkeeper is the match's, family 13 of MODEL.BIN in the measured
        # pose (PLAN-KITS-REPLAY section 4, the user's decision of 2026-10-12
        # reopening K3D-TASK-10); he wears long sleeves only (G4).
        if sleeves not in (None,) + KEEPER_SLEEVES:
            raise FigureError("The goalkeeper wears %s sleeves only, not %r."
                              % (" or ".join(KEEPER_SLEEVES), sleeves))
        built = keeper_scene(kit, kit_set, armband, geometry, player=player)
        return numbered_scene(built, kit, kit_set, figure, None)
    files = dict(geometry)
    files[SLOT] = kit.data
    values = looks.parse_tuple(TUPLE)
    if player is not None:
        # The body's bare skin takes the player's SKIN, by the rule the looks
        # cycle measured on LOOKS SET (CORR-LOOKS-103): the user's decision of
        # 2026-10-16, PLAN-KITS-REPLAY section 3.3.  His head comes after.
        values["skin_colour"] = player_values(player)["skin_colour"]
    try:
        built = scene.build(files, values, figure, frame,
                            layout.KIT_ON_SCREEN, kit_set)
    except (scene.BadScene, assembly.BadAssembly, texture.BadTable) as exc:
        raise FigureError("%s cannot be drawn on the figure: %s" % (kit.label, exc)) from exc
    # The game copies the shirt back into the torso gap on every LOOKS SET
    # figure (BACK_COPY, measured), number or not: drawn without it the back
    # showed through (KITS-AJUSTES-3D.md G5, K3D-TASK-05).
    if player is not None:
        built = player_headed(built, player_values(player), kit, kit_set, geometry, frame)
    backed = numbered_scene(built, kit, kit_set, figure, None)
    return dressed_scene(backed, kit, kit_set, figure, geometry, frame, armband, sleeves)


# -- the player's head (PLAN-KITS-REPLAY section 3) --------------------------------

def player_values(player: str) -> dict:
    """The five looks of a player tuple (`looks.parse_tuple`), or FigureError."""
    try:
        return looks.parse_tuple(player)
    except (looks.BadLooks, ValueError, KeyError) as exc:
        raise FigureError("%r is not a looks tuple like %s: %s" % (player, TUPLE, exc)) from exc


def player_head_section(values: dict) -> int:
    """The MODEL.BIN head the game draws for a record (KRP-TASK-09, measured on
    the 22 of slots 9 and 10): the section of its HAIR style
    (`assembly.HAIR_MAP`), the twin `FACE_TWINS` names when its beard is F or
    G."""
    number = assembly.HAIR_MAP[values["hair_style"]][0]
    if values["beard_style"] >= assembly.FACE_TWIN_FROM:
        number = assembly.FACE_TWINS[assembly.HEAD_FIGURE][number]
    return number


def player_head_clut(clut: int, values: dict) -> int:
    """The CLUT the game samples a head primitive with, from the one the disc
    gives it (KRP-TASK-09): the row of skin `skin_colour`, and the disc's hair
    column (`layout.HAIR_COLUMN`) moved to `hair_colour`'s, its beard column
    (`layout.BEARD_COLUMN`) to `beard_colour`'s.  A CLUT off the skin records
    or in another column is the disc's: the rule says nothing of it."""
    row, column = skin.grid(clut)
    if not layout.CLUT_ROW_FIRST <= row < layout.CLUT_ROW_FIRST + len(layout.SKIN_PALETTES):
        return clut
    if column == layout.HAIR_COLUMN:
        column += values["hair_colour"]
    elif column == layout.BEARD_COLUMN:
        column += values["beard_colour"]
    else:
        return clut
    return skin.clut_id(layout.CLUT_ROW_FIRST + values["skin_colour"], column)


def player_body_clut(clut: int, values: dict) -> int:
    """The CLUT the game samples a MODEL.BIN body primitive with: the bare-skin
    column (`layout.BARE_SKIN_COLUMN`) on the row of skin `skin_colour`, and the
    hair and beard columns as on the head (`player_head_clut`).  Measured on the
    walk of slot 9: the legs of Brazil's 10 and 11 sample (0,482) and (0,483),
    their torsos (16,482) and (16,483), the goalkeepers' (0,480) and (32,480)."""
    row, column = skin.grid(clut)
    if column == layout.BARE_SKIN_COLUMN and \
            layout.CLUT_ROW_FIRST <= row < layout.CLUT_ROW_FIRST + len(layout.SKIN_PALETTES):
        return skin.clut_id(layout.CLUT_ROW_FIRST + values["skin_colour"], column)
    return player_head_clut(clut, values)


def player_head_parts(values: dict, geometry, kit, kit_set: int, surfaces: dict,
                      notes: dict) -> tuple:
    """(the head's section, its parts at the file's origin): every primitive of
    `player_head_section`, with the disc's own texels and `player_head_clut`,
    textured as `match_scene` textures a MODEL.BIN primitive."""
    import copy
    import section

    number = player_head_section(values)
    one = section.scan(geometry[layout.MODEL], layout.MODEL_GEOMETRY_START).sections[number]
    banks = _model_banks(geometry, kit, kit_set)
    parts = []
    for at, primitive in enumerate(one.primitives):
        worn = copy.copy(primitive)
        worn.clut = player_head_clut(primitive.clut, values)
        parts.append(_model_part(worn, one.vertices, number, at, banks, surfaces, notes))
    return number, parts


def player_headed(drawn, values: dict, kit, kit_set: int, geometry, frame=None):
    """*drawn* (a LOOKS SET figure of `scene_of`) with its MODEL.BIN head taken
    out and the player's put in (`player_head_parts`), through the place the
    frame gives the head (`scene.place_for`: every head takes the HEAD's pose).
    Nothing else of the figure changes: the rule measured is the head's."""
    heads = {p.section for p in drawn.parts if p.file == layout.MODEL}
    if len(heads) != 1:
        raise FigureError("the figure draws %d MODEL.BIN section(s) before its head is "
                          "swapped, not one: %s" % (len(heads), sorted(heads)))
    surfaces, notes = dict(drawn.surfaces), dict(drawn.notes)
    number, head = player_head_parts(values, geometry, kit, kit_set, surfaces, notes)
    places = scene.pose(geometry, frame) if frame is not None else {}
    place = scene.place_for(places, (layout.MODEL, number),
                            (layout.MODEL, pieces.HEAD_SECTION)) if places else None
    parts = [p for p in drawn.parts if p.file != layout.MODEL]
    for part in head:
        if place is not None:
            part = scene.Part(part.file, part.section, part.primitive,
                              scene.drawn_points(part.points, *place), part.uvs,
                              part.surface, part.why, part.clut, part.band,
                              part.band_unmeasured)
        parts.append(part)
    notes["player head"] = {"section": number, "replaced": sorted(heads)[0]}
    return scene.Scene(parts, {k: v for k, v in surfaces.items() if v is not None},
                       drawn.values, drawn.figure, notes)


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

ARM_PIECES = {
    3: "upper arm a", 4: "upper arm b", 5: "forearm a", 6: "forearm b",
    90: "upper arm b",
    93: "upper arm b", 95: "upper arm a", 96: "forearm a", 97: "upper arm b", 98: "forearm b",
    57: "upper arm a", 58: "forearm a", 59: "upper arm b", 60: "forearm b",
    99: "upper arm a", 100: "upper arm b", 101: "forearm a", 102: "forearm b",
    14: "upper arm a", 15: "upper arm b", 16: "forearm a", 17: "forearm b",
    92: "upper arm b",
}
"""The rule `oracle.py --edt-arms` measures and asserts (KITS-AJUSTES-3D.md G3,
K3D-TASK-07), kept here so the drawing reads the same table: the
EDT_MOD.BIN piece, by `pieces.py`'s name, each sleeve and armband section of
MODEL.BIN stands in for.  The section sits in that piece's local frame, so it
is drawn with the matrix and place the figure gives that piece (`scene.pose`,
which is by name and the same for both figures).  The part -- upper arm or
forearm -- is the EDT_MOD.BIN piece whose vertices lie nearest; the side, a
or b, is the sign of the section's mean z, since each pair is the other one
mirrored in z vertex for vertex.  14 15 16 17 and 92 are the arms and the
armband of the goalkeeper drawn from torso 13 (K3D-TASK-08, slot 7); they lie
on the goalkeeper's own arm pieces (K3D-TASK-11)."""
KEEPER_FIGURE = 1
"""The figure number of the goalkeeper (`FIGURES`)."""
KEEPER_ARMBAND = 92
"""The goalkeeper's captain's armband: drawn in slot 7 in place of 15, whose
vertices it has (`oracle.py --keeper-armband 7`, G4 of KITS-AJUSTES-3D.md)."""
KEEPER_SLEEVES = ("long",)
"""The goalkeeper wears long sleeves only in this game (user, 2026-10-08, G4):
his own EDT_MOD.BIN arms are long, and there is no short one to draw."""


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


KEEPER_POSE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "keeper_pose.json")
"""The pose of the match goalkeeper, family 13: `work/kits-pose/slot9-keeper-front.json`
as `oracle.py --replay 9` wrote it, copied byte for byte (KRP-TASK-12, its
digest in the Log), never edited by hand."""
KEEPER_ROOT = 13
"""The torso of family 13: the piece the goalkeeper's torso view keeps upright."""
KEEPER_ARM = 15
"""The arm section the goalkeeper's armband `KEEPER_ARMBAND` stands in for."""


def read_keeper_pose(path=None) -> dict:
    """The measured goalkeeper pose, or `FigureError`."""
    import json

    path = path or KEEPER_POSE
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as exc:
        raise FigureError("No goalkeeper pose at %s: %s" % (path, exc.strerror or exc)) from exc


def keeper_order(pieces, armband: bool) -> list:
    """[(section, rotation, translation)] of the measured goalkeeper: family 13
    as the replay drew it, with `KEEPER_ARMBAND` where `KEEPER_ARM` is when
    *armband*, and `KEEPER_ARM` where the armband is when not -- each section
    keeps the matrix the game gave its position (KITS-REPLAYS-9-10 item 3)."""
    out = []
    for piece in pieces:
        section = piece["section"]
        if section in (KEEPER_ARMBAND, KEEPER_ARM):
            section = KEEPER_ARMBAND if armband else KEEPER_ARM
        out.append((section, tuple(piece["rotation"]), tuple(piece["translation"])))
    return out


def keeper_scene(kit, kit_set: int = 1, armband: bool = False, geometry=None,
                 geometry_path=None, pose=None, player: str = None, view: str = "torso"):
    """The goalkeeper as the match draws him (PLAN-KITS-REPLAY section 4): the
    MODEL.BIN family 13 in the measured pose (`keeper_pose.json`), the armband
    92 in place of 15 when *armband*, the head the looks of *player* draw
    (`TUPLE`'s without one), and every skin, hair and beard CLUT by
    `player_body_clut`.  No vertex nor texel is made here: the sections are
    MODEL.BIN's own, textured as `match_scene` textures them."""
    if kit_set not in KIT_SETS:
        raise FigureError("Kit set %r is not one of %s." % (kit_set, KIT_SETS))
    pose = pose if pose is not None else read_keeper_pose()
    values = player_values(player) if player is not None else looks.parse_tuple(TUPLE)
    order = keeper_order(pose["pieces"], armband)
    head, rotation, translation = order[0]
    order = [(player_head_section(values), rotation, translation)] + order[1:]
    if geometry is None:
        geometry = read_geometry(geometry_path_for(geometry_path))
    kit.require()
    notes = {"figure": "keeper", "armband": armband, "player head": {"section": order[0][0]}}
    return _model_scene(order, KEEPER_ROOT, pose["projection"], view, geometry, kit, kit_set,
                        values, lambda number, clut: player_body_clut(clut, values), notes)


def _model_scene(order, root_section: int, projection, view: str, geometry, kit,
                 kit_set: int, values, recolour, extra: dict):
    """The scene of MODEL.BIN sections *order* [(section, rotation, translation)]:
    each section's vertices through its matrix, in *view* ("torso": in the axes
    of *root_section*, upright), every primitive's CLUT through *recolour*
    (section, clut) -> clut, and textured as `_model_part` textures one."""
    import copy
    import section

    if view not in MATCH_VIEWS:
        raise FigureError("View %r is not one of %s." % (view, MATCH_VIEWS))
    banks = _model_banks(geometry, kit, kit_set)
    sections = section.scan(geometry[layout.MODEL], layout.MODEL_GEOMETRY_START).sections
    root = next(((r, t) for s, r, t in order if s == root_section), None)
    if root is None:
        raise FigureError("the pose has no section %d" % root_section)
    undo = _inverse(tuple(v / scene.ONE for v in root[0]))
    surfaces, parts = {}, []
    notes = {"no image": 0, "no palette": 0, "off the record": 0, "view": view,
             "projection": dict(projection), "order": [s for s, _r, _t in order]}
    notes.update(extra)
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
            worn = recolour(number, primitive.clut)
            if worn != primitive.clut:
                primitive = copy.copy(primitive)
                primitive.clut = worn
            parts.append(_model_part(primitive, moved, number, at, banks, surfaces, notes))
    return scene.Scene(parts, {k: v for k, v in surfaces.items() if v is not None},
                       values, 0, notes)


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


def _model_banks(geometry, kit, kit_set: int) -> list:
    """Where a MODEL.BIN primitive's page and CLUT are looked for, in order:
    `DAT2D.BIN` first, the kit's set *kit_set* second."""
    data2d = geometry[layout.DAT2D]
    return [(layout.DAT2D, data2d, texture.images(data2d), texture.palettes(data2d)),
            (SLOT, kit.data, texture.in_set_order(texture.images(kit.data), kit_set),
             texture.in_set_order(texture.palettes(kit.data), kit_set))]


def _model_part(primitive, vertices, number: int, at: int, banks, surfaces: dict,
                notes: dict):
    """One MODEL.BIN primitive as a part, textured the way `assembly.draw_list`
    resolves one: the page and CLUT the disc gives it, in the first of *banks*
    that holds both.  *surfaces* and *notes* are shared across the figure."""
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
        notes["no image"] = notes.get("no image", 0) + 1
    elif surface is None:
        notes["no palette"] = notes.get("no palette", 0) + 1
    part = scene.part_for(primitive, vertices, record, surface, primitive.clut, 0,
                          (layout.MODEL, number), at)
    if surface is not None and part.surface is None:
        notes["off the record"] = notes.get("off the record", 0) + 1
    return part


def match_scene(kit, kit_set: int = 1, armband: bool = False, sleeves: str = "long",
                figure: str = "outfield", view: str = "torso", geometry=None,
                geometry_path=None, pose=None, player: str = None):
    """The looks `Scene` of a match figure wearing set *kit_set* of *kit*.

    The pieces are MODEL.BIN's sections in the order the game drew them, each
    through the GTE matrix it was drawn with (`read_match_pose`), and every
    primitive textured the way `assembly.draw_list` resolves one: the page and
    CLUT the disc gives it, looked for in `DAT2D.BIN` first and in the kit
    second.  The texel of each corner follows the stored vertex order, as
    `scene.part_for` reads it -- the order KITS-TASK-45 measured.  The head
    wears the disc's own CLUTs: no LOOKS SET tuple edits it -- unless
    *player* (a looks tuple) is given: then the head is that record's, the
    section `player_head_section` and the CLUTs `player_head_clut`, in the
    measured head's matrix."""
    if kit_set not in KIT_SETS:
        raise FigureError("Kit set %r is not one of %s." % (kit_set, KIT_SETS))
    if figure not in MATCH_FIGURES:
        raise FigureError("Match figure %r is not one of %s." % (figure, MATCH_FIGURES))
    if view not in MATCH_VIEWS:
        raise FigureError("View %r is not one of %s." % (view, MATCH_VIEWS))
    pose = pose if pose is not None else read_match_pose()
    measured = pose["figures"][figure]
    order = match_order(measured["pieces"], armband, sleeves)
    values = player_values(player) if player is not None else None
    if values is not None:
        number, rotation, translation = order[0]
        order = [(player_head_section(values), rotation, translation)] + order[1:]
    if geometry is None:
        geometry = read_geometry(geometry_path_for(geometry_path))
    kit.require()
    head = order[0][0]
    notes = {"figure": figure, "armband": armband, "sleeves": sleeves}
    if values is not None:
        notes["player head"] = {"section": head}
    recolour = ((lambda number, clut: player_head_clut(clut, values) if number == head else clut)
                if values is not None else (lambda number, clut: clut))
    return _model_scene(order, ROOT_SECTION, pose["projection"], view, geometry, kit, kit_set,
                        values if values is not None else looks.parse_tuple(TUPLE), recolour,
                        notes)


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
    # The back copy and the digits are rectangles of the uniform image; the
    # sleeves image a dressed figure samples (K3D-TASK-10) keeps its texels.
    uniform = texture.in_set_order(texture.images(kit.data), kit_set)[0].offset
    swapped = {}
    for key, surface in drawn.surfaces.items():
        if key[0] != SLOT or surface.record != uniform:
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
HOLE_MARGIN = raster.MARGIN
HOLE_DEPTH_TIE = raster.DEPTH_TIE
"""The drawing's fit, and how close two depths are before a disagreement
between what is shown and what is nearest is a tie, not an error."""


@dataclass(frozen=True)
class HoleCount:
    """What one figure shows at one turn, counted pixel by pixel.

    At each pixel the triangle nearest the eye is what a figure drawn whole
    would show.  `transparent` counts the pixels where that triangle samples a
    transparent texel -- what shows there is whatever lies behind, the inside
    of the figure or the backdrop, and `backdrop` is how many of them show the
    backdrop; `skipped` those where it is a triangle the drawing leaves out
    (its UV triangle has no area, and the drawing skips such ones -- only the
    old drawing does); `misordered` those where it is opaque but another
    triangle is shown over it (only the old order by mean depth does that).
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


_turn = raster.turn
"""The drawing's turn (`core/raster.py`), the view's rotate() kept equal to it
by the selftest."""


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
                triangles=TRIANGLES, order: str = raster.DEPTH,
                skip_degenerate: bool = False) -> HoleCount:
    """What *drawn* lets through at (*yaw*, *pitch*), drawn by `core/raster.py`
    -- the 3D view's own drawing -- in a *size* square.  *order* and
    *skip_degenerate* choose the drawing counted: the defaults are the view's,
    `order=raster.MEAN, skip_degenerate=True` the one it had before G6, kept so
    the count can be seen to find what that drawing missed."""
    drawn_raster = raster.draw(drawn, yaw, pitch, size, size, triangles, order, skip_degenerate)
    parts = drawn.parts
    tally = {}

    def name(n):
        return "%s section %d" % (parts[n].file, parts[n].section)

    def add(kind, n, where):
        key = (kind, name(n), where)
        tally[key] = tally.get(key, 0) + 1

    numbers = record_numbers(kit) if kit is not None else None
    zone_of = {}
    silhouette = transparent = backdrop = skipped = misordered = 0
    for near, shown in zip(drawn_raster.nearest, drawn_raster.shown):
        if near is None:
            continue
        silhouette += 1
        depth, n, kind, texel, _step = near
        if kind == raster.UNMAPPED:
            skipped += 1
            add("skipped", n, "-")
        elif kind == raster.TRANSPARENT:
            transparent += 1
            backdrop += shown is None
            key = (n, texel)
            if key not in zone_of:
                zone_of[key] = texel_zone(numbers, parts[n].surface, texel[0], texel[1],
                                          drawn.figure)
            add("transparent", n, zone_of[key])
        elif shown is not near and shown[0] < depth - HOLE_DEPTH_TIE:
            misordered += 1
            add("misordered", shown[1], "over %s" % name(n))
    sources = tuple(sorted(((k[0], k[1], k[2], v) for k, v in tally.items()),
                           key=lambda s: (-s[3], s)))
    return HoleCount(yaw, pitch, silhouette, transparent, backdrop, skipped, misordered,
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


# -- the dressings on the LOOKS SET figure (KITS-AJUSTES-3D.md G3, K3D-TASK-10) -------

DRESSED_FIGURES = (0, 1)
"""The figures the armband and the long sleeves dress: the outfield player
(K3D-TASK-10) and the goalkeeper (K3D-TASK-11)."""


def arm_dress(armband: bool, sleeves: str = None, figure: int = 0) -> dict:
    """{EDT_MOD.BIN piece name: MODEL.BIN section} that dress *figure*, each
    section on the piece `ARM_PIECES` gives it.  The player: the long-sleeve
    arms (`LONG_TO_SHORT`'s 95 96 97 98) and the armband of the sleeve length
    in place of the arm it replaces (`SLEEVE_LENGTHS`); short sleeves and no
    armband are none -- the figure keeps its own arms.  The goalkeeper: his
    own long arms, and `KEEPER_ARMBAND` on the upper arm it was drawn on;
    sleeves that are not in `KEEPER_SLEEVES` are refused."""
    if sleeves is None:
        sleeves = KEEPER_SLEEVES[0] if figure == 1 else "short"
    if sleeves not in MATCH_SLEEVES:
        raise FigureError("Sleeves %r are not one of %s." % (sleeves, MATCH_SLEEVES))
    if figure == 1:
        if sleeves not in KEEPER_SLEEVES:
            raise FigureError("The goalkeeper wears %s sleeves only, not %s."
                              % (" or ".join(KEEPER_SLEEVES), sleeves))
        return {ARM_PIECES[KEEPER_ARMBAND]: KEEPER_ARMBAND} if armband else {}
    out = {ARM_PIECES[s]: s for s in LONG_TO_SHORT} if sleeves == "long" else {}
    if armband:
        band = SLEEVE_LENGTHS[sleeves]["armband"]
        out[ARM_PIECES[band]] = band
    return out


def dressed_scene(drawn, kit, kit_set: int, figure: int, geometry, frame=None,
                  armband: bool = False, sleeves: str = None):
    """*drawn* (a LOOKS SET figure of `scene_of`) with the armband and the
    long sleeves: each EDT_MOD.BIN arm piece `arm_dress` names is taken out
    and the MODEL.BIN section put in, through the matrix and place the frame
    gives that piece (`scene.pose`) -- the section sits in the piece's own
    frame (G3).  No geometry or UV is made here: the section's own vertices
    and texels, textured as `match_scene` textures them."""
    import section

    if figure not in DRESSED_FIGURES:
        raise FigureError("The captain's armband and the long sleeves are not measured "
                          "on figure %d." % figure)
    dress = arm_dress(armband, sleeves, figure)
    if not dress:
        return drawn
    members = scene._figure_sections(geometry)[figure]
    piece_of = {name: index for (file, index), name in scene.piece_names(geometry).items()
                if file == layout.EDT_MOD and index in members}
    taken = {piece_of[name]: number for name, number in dress.items()}
    places = scene.pose(geometry, frame) if frame is not None else {}
    sections = section.scan(geometry[layout.MODEL], layout.MODEL_GEOMETRY_START).sections
    banks = _model_banks(geometry, kit, kit_set)
    surfaces, notes = dict(drawn.surfaces), dict(drawn.notes)
    parts = [p for p in drawn.parts if not (p.file == layout.EDT_MOD and p.section in taken)]
    for index, number in sorted(taken.items()):
        one = sections[number]
        place = places.get((layout.EDT_MOD, index))
        for at, primitive in enumerate(one.primitives):
            part = _model_part(primitive, one.vertices, number, at, banks, surfaces, notes)
            if place is not None:
                part = scene.Part(part.file, part.section, part.primitive,
                                  scene.drawn_points(part.points, *place), part.uvs,
                                  part.surface, part.why, part.clut, part.band,
                                  part.band_unmeasured)
            parts.append(part)
    notes["dressed"] = {piece: number for piece, number in sorted(dress.items())}
    # framed by the undressed figure, so a box ticked moves nothing else (CORR-K3D-016)
    notes.setdefault(raster.FIT, tuple(p for part in drawn.parts for p in part.points))
    return scene.Scene(parts, {k: v for k, v in surfaces.items() if v is not None},
                       drawn.values, drawn.figure, notes)

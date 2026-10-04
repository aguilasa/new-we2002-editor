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
        return scene.build(files, looks.parse_tuple(TUPLE), figure, frame,
                           layout.KIT_ON_SCREEN, kit_set)
    except (scene.BadScene, assembly.BadAssembly, texture.BadTable) as exc:
        raise FigureError("%s cannot be drawn on the figure: %s" % (kit.label, exc)) from exc


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
        indices, _, _ = atlas.read_image(kit.data, images[surface.record], surface.depth)
        where, first = texture.window_for(palettes, column * texture.NARROW, other[row], colours)
        entries = texture.read_palette(kit.data, where, colours, first)
        want = b"".join(bytes(entries[i]) for i in indices)
        if want != surface.rgba:
            wrong.append("record %d, row %d: not the row %d colours"
                         % (surface.record, row, other[row]))
    return SwapControl(figure, kit_set, tuple(sorted(rows)), compared, tuple(wrong))

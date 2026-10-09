"""The facade of the kits core: the one module a user interface imports.

PLAN-KITS-PY.md section 3.1.  What is here today is the entry point --
`open_source` --, the kit it gives, and the types and errors they return;
the rest of the contract (teams, flat, figure) arrives with the tasks that
build it.

    source = api.open_source(path)   # disc image (.bin/.iso/.cue) or lone TEX
    source.kind                      # "rom" or "tex", decided by content
    source.kit_tags()                # rom only: the TEX tags on the disc
    source.teams()                   # rom only: 95 TeamEntry(index, name, name_origin, tag)
    kit_order(teams, tags)           # the window's kit list: teams, ML default, unworn tags
    kit = source.kit(tag)            # rom: by tag; lone TEX: the file itself
    kit.problems                     # the guard of form, one sentence per record
    kit.notes                        # how it was read, when not plainly (api.Note)
    kit.images, kit.palettes         # the 6 images and 5 palettes, by name
    kit.require()                    # the kit, or KitRefused with every problem
    kit.flat(image, palette)         # FlatImage(width, height, indices, palette, rgba)
    kit.work_bitmap(kit_set, figure) # the 256x128 uniform | sleeves (set 1/2, figure 0/1)
    kit.palette_grid(palette)        # 256 PaletteEntry(index, bgr555, rgba)
    api.zone_at(x, y)                # the map's Zone at a work-bitmap pixel, or None
    api.confront_zones(uv_report)    # section 4.6: Confrontation, `ok` the verdict
    api.figure(kit, kit_set, figure, geometry_path=None, frame=None,
               armband=False, sleeves=None)
                                     # the looks Scene of the figure in the kit,
                                     # MODEL.BIN arms put on by ARM_PIECES;
                                     # geometry from WE2002_LOOKS_IMAGE when no path
    api.match_figure(kit, kit_set, armband=False, sleeves="long", figure="outfield",
                     view="torso")   # the MODEL.BIN match figure, in its measured pose
    api.numbered(scene, kit, kit_set, figure, number)
                                     # a LOOKS SET figure with the number on its back
    api.draw_figure(scene, yaw, pitch, width, height)
                                     # Raster: the figure drawn by pixel (depth buffer),
                                     # as the 3D tab shows it
    api.count_holes(scene, yaw, pitch=0, kit=None)
                                     # HoleCount: what the turned view shows that is
                                     # not the nearest surface, and where it comes from
"""

from __future__ import annotations

from .errors import (KitError, KitMissing, KitRefused, KitsError,  # noqa: F401
                     KitUnreadable, NotASource, SourceEmpty, SourceError,
                     SourceMissing, SourceUnreadable, StreamError,
                     FigureError, NoGeometry, GeometryRefused)
from .source import KIND_ROM, KIND_TEX, OpenControl, RomSource, TexSource  # noqa: F401
from .source import open_controls as _open_controls
from .source import open_source as _open_source
from .tex import (EXPECTED_SHAPE, IMAGE_RECORDS, NOTE_FORM2_TAIL,  # noqa: F401
                  NOTE_PAST_ISO_SIZE, PALETTE_RECORDS, RECORD_NAMES, Image, Kit,
                  Note, Palette, StreamControl)
from .tex import stream_control as _stream_control
from .tex import decompress_stream as _decompress_stream
from .teams import (ORIGIN_ROM, ORIGIN_TABLE, TeamEntry, kit_order,  # noqa: F401
                    KIND_TEAM, KIND_ML_DEFAULT, KIND_UNWORN, ML_DEFAULT_KIT)
from .flat import (FIGURES, GAME_PAIRS, KIT_SETS, WORK_H, WORK_W,  # noqa: F401
                   FlatImage, PaletteEntry, paint, palette_rgba)
from .flat import PALETTE_OF as WORK_PALETTE  # noqa: F401
from .flat import SLEEVES as SLEEVES_OF_SET  # noqa: F401
from .flat import UNIFORM as UNIFORM_OF_SET  # noqa: F401
from .zones import (CLASSES as ZONE_CLASSES, GAPS, GLYPH_ZONES,  # noqa: F401
                    MAP_BACKGROUND, MEASURES, ZONES, Confrontation, Gap, MapCheck,
                    Measure, Placed, Zone)
from . import zones as _zones
from .source import DiscControl  # noqa: F401
from .source import disc_controls as _disc_controls
from . import survey as measure  # noqa: F401  (the phase-0 probes, below)
from . import figure as _figure
from .figure import SwapControl  # noqa: F401

__all__ = (
    "open_source", "open_controls", "OpenControl",
    "KIND_ROM", "KIND_TEX", "RomSource", "TexSource",
    "KitsError", "SourceError", "SourceMissing", "SourceUnreadable",
    "SourceEmpty", "NotASource",
    "Kit", "Image", "Palette", "Note", "EXPECTED_SHAPE", "RECORD_NAMES",
    "NOTE_PAST_ISO_SIZE", "NOTE_FORM2_TAIL",
    "stream_control", "StreamControl", "disc_controls", "DiscControl",
    "KitError", "KitMissing", "KitUnreadable", "KitRefused",
    "measure", "survey_image", "Survey", "SurveyError",
    "IMAGE_RECORDS", "PALETTE_RECORDS", "IMAGE_COUNT", "PALETTE_COUNT",
    "decompress_stream", "StreamError",
    "TeamEntry", "ORIGIN_TABLE", "ORIGIN_ROM",
    "kit_order", "KIND_TEAM", "KIND_ML_DEFAULT", "KIND_UNWORN", "ML_DEFAULT_KIT",
    "FlatImage", "PaletteEntry", "paint", "palette_rgba", "GAME_PAIRS", "KIT_SETS", "FIGURES",
    "WORK_W", "WORK_H", "WORK_PALETTE", "UNIFORM_OF_SET", "SLEEVES_OF_SET",
    "zone_at", "Zone", "ZONES", "Gap", "GAPS", "Measure", "MEASURES", "ZONE_CLASSES",
    "confront_zones", "Confrontation", "Placed", "shifted_zones", "zone_agreement",
    "map_check", "MapCheck", "MAP_BACKGROUND", "GLYPH_ZONES", "zones_self_check",
    "figure", "read_geometry", "palette_swap", "SwapControl", "GEOMETRY_ENV",
    "FigureError", "NoGeometry", "GeometryRefused", "FIGURE_POSE", "FIGURE_TRIANGLES",
    "match_figure", "match_pose", "screen_points", "MATCH_FIGURES", "MATCH_SLEEVES",
    "MATCH_VIEWS", "numbered", "SHIRT_NUMBERS",
)

GEOMETRY_ENV = _figure.GEOMETRY_ENV
FIGURE_POSE = _figure.POSE_FRAME
FIGURE_TRIANGLES = _figure.TRIANGLES


def figure(kit, kit_set=1, figure=0, geometry_path=None, frame=None, geometry=None,
           armband=False, sleeves=None):
    """The looks `Scene` of *figure* (0 player, 1 goalkeeper) in set *kit_set*
    of *kit*, with the captain's *armband* and *sleeves* ("short" or "long";
    None, the figure's own) put on by the rule of G3.  The geometry comes from *geometry_path*, else
    from `WE2002_LOOKS_IMAGE`; with neither, `NoGeometry` (section 3.1)."""
    return _figure.scene_of(kit, kit_set, figure, geometry_path, frame, geometry,
                            armband, sleeves)


MATCH_FIGURES = _figure.MATCH_FIGURES
MATCH_SLEEVES = _figure.MATCH_SLEEVES
MATCH_VIEWS = _figure.MATCH_VIEWS


def match_figure(kit, kit_set=1, armband=False, sleeves="long", figure="outfield",
                 view="torso", geometry=None, geometry_path=None, pose=None):
    """The match figure of section 4.3: MODEL.BIN's pieces in the pose the
    game drew them in, with the captain's armband or not and long or short
    sleeves, wearing set *kit_set* of *kit*."""
    return _figure.match_scene(kit, kit_set, armband, sleeves, figure, view, geometry,
                               geometry_path, pose)


SHIRT_NUMBERS = _figure.NUMBERS


def numbered(drawn, kit, kit_set, figure, number):
    """A LOOKS SET figure of `figure()` with the shirt number painted on its
    back (section 4.7).  Only the digits: the shirt back copied into the torso
    gap already comes from `figure()`, Number or not (K3D-TASK-05)."""
    return _figure.numbered_scene(drawn, kit, kit_set, figure, number)


FIGURE_DEPTH, FIGURE_MEAN = _figure.raster.DEPTH, _figure.raster.MEAN


def draw_figure(drawn, yaw, pitch, width, height, order=FIGURE_DEPTH, skip_degenerate=False):
    """*drawn* turned to (*yaw*, *pitch*) and drawn in software into a
    *width* x *height* RGBA picture: the 3D tab's drawing (G6).  *order* and
    *skip_degenerate* are there for the controls that bring the old drawing
    back (FIGURE_MEAN, True); the window never passes them."""
    return _figure.raster.draw(drawn, yaw, pitch, width, height, _figure.TRIANGLES, order,
                               skip_degenerate)


HoleCount = _figure.HoleCount
HOLE_SIZE = _figure.HOLE_SIZE


def count_holes(drawn, yaw, pitch=0.0, kit=None, size=None):
    """What *drawn* turned to (*yaw*, *pitch*) lets through, counted by pixel
    as `draw_figure` draws it (KITS-AJUSTES-3D.md G5, G6)."""
    return _figure.count_holes(drawn, yaw, pitch, kit, size or _figure.HOLE_SIZE)


def planted_gap(drawn, kit, figure, zone_name="shirt front"):
    """*drawn* with one zone of the uniform made transparent: the control the
    hole count has to see (K3D-TASK-04)."""
    return _figure.planted_gap(drawn, kit, figure, zone_name)


def match_pose(path=None):
    """The measured match pose (`oracle.py --match-pose 5 --write`)."""
    return _figure.read_match_pose(path)


def screen_points(drawn, part):
    """A camera-view part's corners in the game's screen pixels."""
    return _figure.screen_points(drawn, part)


def read_geometry(geometry_path=None):
    """The figure's files off the disc, read once for several `figure` calls."""
    return _figure.read_geometry(_figure.geometry_path_for(geometry_path))


def palette_swap(kit, kit_set, figure, geometry):
    """Section 5, control 4: the kit with 486 and 488 swapped, checked."""
    return _figure.palette_swap(kit, kit_set, figure, geometry)

IMAGE_COUNT = len(IMAGE_RECORDS)
"""How many image records a kit container has (6), from `EXPECTED_SHAPE`."""
PALETTE_COUNT = len(PALETTE_RECORDS)
"""How many palette (CLUT) records a kit container has (5)."""

Survey = measure.Survey
SurveyError = measure.SurveyError


def survey_image(image_path):
    """The section 1.1 survey of every kit container of the disc at
    *image_path*: a `Survey`, or `SurveyError` with the sentence to show."""
    return measure.survey_image(image_path)

# `measure` is the phase-0 measurement module as it is: survey, rects,
# prims, uv and their negative controls (PLAN-KITS-PY.md sections 1.1, 4.3,
# 4.4, 4.6).  It is reached through the facade so that the CLI imports
# nothing else (CORR-KITS-018); giving it a contract of its own is not
# what the probes are for.


def open_source(path):
    """Open *path* as a disc image or a lone kit container, by its content.

    Returns a `RomSource` (`kind == "rom"`) or a `TexSource`
    (`kind == "tex"`).  Raises a `SourceError` subclass whose message is
    the sentence to show: `SourceMissing`, `SourceUnreadable`,
    `SourceEmpty` or `NotASource`.
    """
    return _open_source(path)


def open_controls(image_path, folder):
    """Build the recognition fixtures from the disc at *image_path* in the
    empty *folder* and open each: a tuple of `OpenControl`, whose `ok` says
    whether it gave what it has to."""
    return _open_controls(image_path, folder)


def stream_control(kit):
    """Section 5, control 4: one byte of record 0's LZSS stream changed in a
    copy of *kit*, and the guard read on both.  `StreamControl.ok` says the
    sound copy passed and the planted one was refused on record 0."""
    return _stream_control(kit.data, kit.label)


def disc_controls(source):
    """The two read rules of a disc (Form 2 tail, next-file limit), each
    planted on the kit it applies to: a tuple of `DiscControl`."""
    return _disc_controls(source.image_path, source.kit_tags())


def decompress_stream(data, label="the stream"):
    """The plain bytes of a lone LZSS stream (a WEZip `.bin`), decoded by the
    same decoder as the kit records; `StreamError` with the sentence to show."""
    return _decompress_stream(data, label)


def zone_at(x, y, zones=None):
    """The zone of the map (section 1.3) at work-bitmap pixel (x, y), or None."""
    return _zones.zone_at(x, y, ZONES if zones is None else zones)


def confront_zones(uv_report, zones=None):
    """Section 4.6 on a `measure.UvReport` (`measure.uv_image`): where each UV
    rect falls in the map, which zones nobody samples; `ok` is the verdict."""
    return _zones.confront(uv_report, ZONES if zones is None else zones)


def shifted_zones(dx=1, dy=0):
    """The map moved by (dx, dy): section 5, control 4."""
    return _zones.shifted(ZONES, dx, dy)


def zone_agreement():
    """ramonpsx's piece sizes against the map's: ((Measure, (w, h) or None), ...)."""
    return _zones.agreement()


def map_check(width, height, pixels, zones=None):
    """The polipoli rows against the picture they were measured on: a `MapCheck`."""
    return _zones.map_check(width, height, pixels, ZONES if zones is None else zones)


def zones_self_check():
    """The map's own invariants, as failure sentences (empty when sound)."""
    return _zones.self_check()

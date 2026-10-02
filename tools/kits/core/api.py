"""The facade of the kits core: the one module a user interface imports.

PLAN-KITS-PY.md section 3.1.  What is here today is the entry point --
`open_source` --, the kit it gives, and the types and errors they return;
the rest of the contract (teams, flat, figure) arrives with the tasks that
build it.

    source = api.open_source(path)   # disc image (.bin/.iso/.cue) or lone TEX
    source.kind                      # "rom" or "tex", decided by content
    source.kit_tags()                # rom only: the TEX tags on the disc
    source.teams()                   # rom only: 95 TeamEntry(index, name, name_origin, tag)
    kit = source.kit(tag)            # rom: by tag; lone TEX: the file itself
    kit.problems                     # the guard of form, one sentence per record
    kit.notes                        # how it was read, when not plainly (api.Note)
    kit.images, kit.palettes         # the 6 images and 5 palettes, by name
    kit.require()                    # the kit, or KitRefused with every problem
    kit.flat(image, palette)         # FlatImage(width, height, indices, palette, rgba)
    kit.work_bitmap(kit_set, figure) # the 256x128 uniform | sleeves (set 1/2, figure 0/1)
    kit.palette_grid(palette)        # 256 PaletteEntry(index, bgr555, rgba)
"""

from __future__ import annotations

from .errors import (KitError, KitMissing, KitRefused, KitsError,  # noqa: F401
                     KitUnreadable, NotASource, SourceEmpty, SourceError,
                     SourceMissing, SourceUnreadable, StreamError)
from .source import KIND_ROM, KIND_TEX, OpenControl, RomSource, TexSource  # noqa: F401
from .source import open_controls as _open_controls
from .source import open_source as _open_source
from .tex import (EXPECTED_SHAPE, IMAGE_RECORDS, NOTE_FORM2_TAIL,  # noqa: F401
                  NOTE_PAST_ISO_SIZE, PALETTE_RECORDS, RECORD_NAMES, Image, Kit,
                  Note, Palette, StreamControl)
from .tex import stream_control as _stream_control
from .tex import decompress_stream as _decompress_stream
from .teams import ORIGIN_ROM, ORIGIN_TABLE, TeamEntry  # noqa: F401
from .flat import (FIGURES, GAME_PAIRS, KIT_SETS, WORK_H, WORK_W,  # noqa: F401
                   FlatImage, PaletteEntry, palette_rgba)
from .source import DiscControl  # noqa: F401
from .source import disc_controls as _disc_controls
from . import survey as measure  # noqa: F401  (the phase-0 probes, below)

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
    "FlatImage", "PaletteEntry", "palette_rgba", "GAME_PAIRS", "KIT_SETS", "FIGURES",
    "WORK_W", "WORK_H",
)

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

"""The facade of the kits core: the one module a user interface imports.

PLAN-KITS-PY.md section 3.1.  What is here today is the entry point --
`open_source` --, the kit it gives, and the types and errors they return;
the rest of the contract (teams, flat, figure) arrives with the tasks that
build it.

    source = api.open_source(path)   # disc image (.bin/.iso/.cue) or lone TEX
    source.kind                      # "rom" or "tex", decided by content
    source.kit_tags()                # rom only: the TEX tags on the disc
    kit = source.kit(tag)            # rom: by tag; lone TEX: the file itself
    kit.problems                     # the guard of form, one sentence per record
    kit.notes                        # how it was read, when not plainly (api.Note)
    kit.images, kit.palettes         # the 6 images and 5 palettes, by name
    kit.require()                    # the kit, or KitRefused with every problem
"""

from __future__ import annotations

from .errors import (KitError, KitMissing, KitRefused, KitsError,  # noqa: F401
                     KitUnreadable, NotASource, SourceEmpty, SourceError,
                     SourceMissing, SourceUnreadable)
from .source import KIND_ROM, KIND_TEX, OpenControl, RomSource, TexSource  # noqa: F401
from .source import open_controls as _open_controls
from .source import open_source as _open_source
from .tex import (EXPECTED_SHAPE, NOTE_FORM2_TAIL, NOTE_PAST_ISO_SIZE,  # noqa: F401
                  RECORD_NAMES, Image, Kit, Note, Palette, StreamControl)
from .tex import stream_control as _stream_control

__all__ = (
    "open_source", "open_controls", "OpenControl",
    "KIND_ROM", "KIND_TEX", "RomSource", "TexSource",
    "KitsError", "SourceError", "SourceMissing", "SourceUnreadable",
    "SourceEmpty", "NotASource",
    "Kit", "Image", "Palette", "Note", "EXPECTED_SHAPE", "RECORD_NAMES",
    "NOTE_PAST_ISO_SIZE", "NOTE_FORM2_TAIL",
    "stream_control", "StreamControl",
    "KitError", "KitMissing", "KitUnreadable", "KitRefused",
)


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

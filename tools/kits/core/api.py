"""The facade of the kits core: the one module a user interface imports.

PLAN-KITS-PY.md section 3.1.  What is here today is the entry point --
`open_source` -- and the types and errors it returns; the rest of the
contract (teams, kit, flat, figure) arrives with the tasks that build it.

    source = api.open_source(path)   # disc image (.bin/.iso/.cue) or lone TEX
    source.kind                      # "rom" or "tex", decided by content
    source.kit_tags()                # rom only: the TEX tags on the disc
"""

from __future__ import annotations

from .errors import (KitsError, NotASource, SourceEmpty, SourceError,  # noqa: F401
                     SourceMissing, SourceUnreadable)
from .source import KIND_ROM, KIND_TEX, OpenControl, RomSource, TexSource  # noqa: F401
from .source import open_controls as _open_controls
from .source import open_source as _open_source

__all__ = (
    "open_source", "open_controls", "OpenControl",
    "KIND_ROM", "KIND_TEX", "RomSource", "TexSource",
    "KitsError", "SourceError", "SourceMissing", "SourceUnreadable",
    "SourceEmpty", "NotASource",
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

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
from .source import KIND_ROM, KIND_TEX, RomSource, TexSource  # noqa: F401
from .source import open_source as _open_source

__all__ = (
    "open_source",
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

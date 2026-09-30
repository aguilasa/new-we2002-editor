"""The exceptions of the kits core.

Every error the core raises on purpose derives from `KitsError`, and its
message is the sentence a user interface shows as it is: it names the file
and says what was wrong with it, so a caller never has to rephrase it.
"""

from __future__ import annotations


class KitsError(Exception):
    """Base of every error the kits core raises on purpose."""


class SourceError(KitsError):
    """What was given to `api.open_source` cannot be opened as a source."""


class SourceMissing(SourceError):
    """The path does not exist, or a cue sheet names a track that does not."""


class SourceUnreadable(SourceError):
    """The path exists but cannot be read (a folder, no permission, I/O error)."""


class SourceEmpty(SourceError):
    """The file exists and holds zero bytes."""


class NotASource(SourceError):
    """The file was read, and it is neither a CD image nor a kit container."""

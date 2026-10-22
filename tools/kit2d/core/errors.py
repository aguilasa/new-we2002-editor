"""The exceptions of the kit2d core.

Every error the core raises on purpose derives from `Kit2DError`, and its
message is the sentence a user interface shows as it is: it names the file
and says what was wrong with it, so a caller never has to rephrase it
(PLAN-KIT2D-PY.md section 3.1).
"""

from __future__ import annotations


class Kit2DError(Exception):
    """Base of every error the kit2d core raises on purpose."""


class LayoutError(Kit2DError):
    """A file of the disc is not where, or not the size, `layout` says."""

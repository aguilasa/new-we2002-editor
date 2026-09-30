"""Recognise what was opened -- a disc image or a lone kit container -- by content.

PLAN-KITS-PY.md section 3.2: the window has one "Open..." and the core
decides.  The extension is never consulted: a disc image renamed `.tex`
is still a disc, and a kit container renamed `.bin` is still a kit.

Three things are recognised, tried in this order:

* a raw MODE2/2352 data track -- whatever `tools/pes2/iso.py` opens and
  finds an ISO 9660 filesystem on;
* a cue sheet -- short text with a `FILE "..." BINARY` line; the first
  data track it names is resolved against the cue's own folder and opened
  as the disc above;
* a kit container (`TEX_<tag>.BIN`) -- bytes whose record list has the
  11-record shape of section 1.1 (`survey.EXPECTED_SHAPE`).

Anything else is refused with a typed error from `errors`.
"""

from __future__ import annotations

import os
import re
import struct
from dataclasses import dataclass
from typing import Optional

from . import survey
from .errors import NotASource, SourceEmpty, SourceMissing, SourceUnreadable

# `survey` has already put tools/pes2 on sys.path; these are the same modules.
import bin_archive  # noqa: E402
import iso  # noqa: E402

KIND_ROM = "rom"
KIND_TEX = "tex"

CUE_MAX_BYTES = 64 * 1024
"""A cue sheet is a few hundred bytes of text; past this it is not read as one."""

_CUE_FILE = re.compile(r'^\s*FILE\s+(?:"([^"]+)"|(\S+))\s+BINARY\s*$',
                       re.IGNORECASE | re.MULTILINE)
_CUE_TRACK = re.compile(r'^\s*TRACK\s+\d+\s+(\S+)', re.IGNORECASE | re.MULTILINE)

_ISO_FAILURES = (ValueError, struct.error, IndexError, UnicodeDecodeError,
                 iso.Form2Sector, iso.OutsideTrack)
"""What `iso.Image` raises on bytes that are not a readable data track."""


@dataclass(frozen=True)
class RomSource:
    """A disc image, opened directly or through a cue sheet."""

    path: str
    """What the caller opened (the cue sheet, when it was one)."""
    image_path: str
    """The data track that was read: `path` itself, or what the cue named."""
    volume_id: str
    file_count: int
    tags: tuple
    """The kit tags on the disc (`TEX_<tag>.BIN`), sorted."""
    cue_path: Optional[str] = None

    kind = KIND_ROM

    def kit_tags(self) -> tuple:
        """The tags of every kit container on the disc, sorted."""
        return self.tags


@dataclass(frozen=True)
class TexSource:
    """A lone kit container: the file is the kit."""

    path: str
    data: bytes

    kind = KIND_TEX

    @property
    def size(self) -> int:
        return len(self.data)


def _check_readable(path: str) -> int:
    """The size of *path*, or the typed error that says why it cannot be read."""
    if not os.path.lexists(path):
        raise SourceMissing("%s does not exist." % path)
    if os.path.isdir(path):
        raise SourceUnreadable("%s is a folder, not a file." % path)
    try:
        size = os.path.getsize(path)
    except OSError as exc:
        raise SourceUnreadable("Could not read %s: %s" % (path, exc.strerror or exc)) from exc
    if size == 0:
        raise SourceEmpty("%s is empty (0 bytes)." % path)
    return size


def _read(path: str, limit: Optional[int] = None) -> bytes:
    try:
        with open(path, "rb") as f:
            return f.read() if limit is None else f.read(limit)
    except OSError as exc:
        raise SourceUnreadable("Could not read %s: %s" % (path, exc.strerror or exc)) from exc


def _try_rom(path: str, size: int):
    """(RomSource, None) if *path* is a data track, else (None, why not)."""
    if size % iso.RAW_SECTOR:
        return None, ("%d bytes is not a whole number of %d-byte sectors"
                      % (size, iso.RAW_SECTOR))
    try:
        image = iso.Image(path)
    except OSError as exc:
        raise SourceUnreadable("Could not read %s: %s" % (path, exc.strerror or exc)) from exc
    except _ISO_FAILURES as exc:
        detail = str(exc)
        if detail.startswith(path + ": "):           # iso.py prefixes the path
            detail = detail[len(path) + 2:]
        return None, "no ISO 9660 filesystem on it (%s)" % detail
    try:
        if not image.files:
            return None, "its ISO 9660 filesystem lists no file"
        tags = tuple(survey.tag_of(p) for p in survey.kit_paths(image))
        return RomSource(path=path, image_path=path, volume_id=image.volume_id,
                         file_count=len(image.files), tags=tags), None
    finally:
        image.close()


def _cue_text(head: bytes) -> Optional[str]:
    if b"\x00" in head:
        return None
    try:
        return head.decode("utf-8")
    except UnicodeDecodeError:
        return head.decode("latin-1")


def _cue_data_track(text: str) -> Optional[str]:
    """The file name of the first data track a cue sheet names, or None."""
    files = list(_CUE_FILE.finditer(text))
    for i, m in enumerate(files):
        end = files[i + 1].start() if i + 1 < len(files) else len(text)
        modes = _CUE_TRACK.findall(text, m.end(), end)
        if any(mode.upper().startswith("MODE") for mode in modes):
            return m.group(1) or m.group(2)
    return None


def _open_cue(path: str, text: str) -> Optional[RomSource]:
    name = _cue_data_track(text)
    if name is None:
        if _CUE_FILE.search(text):
            raise NotASource("%s is a cue sheet, but it names no data (MODE) track."
                             % path)
        return None
    track = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(path)), name))
    if not os.path.exists(track):
        raise SourceMissing("The cue sheet %s names %s, and %s does not exist."
                            % (path, name, track))
    size = _check_readable(track)
    rom, why = _try_rom(track, size)
    if rom is None:
        raise NotASource("The cue sheet %s names %s, which is not a CD data track: %s."
                         % (path, track, why))
    return RomSource(path=path, image_path=track, volume_id=rom.volume_id,
                     file_count=rom.file_count, tags=rom.tags, cue_path=path)


def _tex_problem(data: bytes) -> Optional[str]:
    """None if *data* has the kit container shape, else the first thing that differs."""
    shape = survey._shape_of(bin_archive.entries(data))
    expected = survey.EXPECTED_SHAPE
    if shape == expected:
        return None
    if not shape:
        return "it holds no image or palette record list"
    if len(shape) != len(expected):
        return ("it has %d image/palette records where a kit container has %d"
                % (len(shape), len(expected)))
    for i, (got, want) in enumerate(zip(shape, expected)):
        if got != want:
            return ("record %d is %s at (%d,%d) %dx%d where a kit container has "
                    "%s at (%d,%d) %dx%d" % ((i,) + got + want))
    return "its records differ from a kit container's"  # unreachable: shapes differ


def open_source(path: str):
    """Open *path* as a disc image (`RomSource`) or a kit container (`TexSource`).

    Decided by content, never by the extension.  Raises `SourceMissing`,
    `SourceUnreadable`, `SourceEmpty` or `NotASource`, each with the
    sentence a user interface shows.
    """
    path = os.fspath(path)
    size = _check_readable(path)

    rom, rom_why = _try_rom(path, size)
    if rom is not None:
        return rom

    if size <= CUE_MAX_BYTES:
        text = _cue_text(_read(path, CUE_MAX_BYTES))
        if text is not None:
            cue = _open_cue(path, text)
            if cue is not None:
                return cue

    data = _read(path)
    tex_why = _tex_problem(data)
    if tex_why is None:
        return TexSource(path=path, data=data)
    raise NotASource("%s is neither a CD image nor a kit container (TEX): "
                     "as a CD image, %s; as a TEX, %s." % (path, rom_why, tex_why))

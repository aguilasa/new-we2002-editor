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


# -- the recognition, seen deciding each way -----------------------------
#
# KITS-TASK-06 built these fixtures by hand, and its Log named the wrong byte
# for the planted one (CORR-KITS-011).  Here each fixture is made from the
# disc, the byte to plant is found from the record list instead of written
# down, and every outcome is checked against what it has to be.

CONTROL_KIT_TAG = "00"
TEX_TAG_FIELD = 14
"""Byte offset, inside a 16-byte record, of the 0x800f tag the record scan
looks for: field [7], a little-endian halfword."""

ZERO_SECTORS = 20


@dataclass(frozen=True)
class OpenControl:
    """One fixture, what opening it has to give, and what it gave."""

    name: str
    built: str          # how the fixture was made
    expect: str         # "rom", "tex", or an error class name
    phrase: str         # a piece of the message that has to be there ("" for none)
    got: str            # "rom", "tex", or the error class name raised
    message: str        # the error message, or what opened

    @property
    def ok(self) -> bool:
        return self.got == self.expect and self.phrase in self.message


def _write(path: str, data: bytes) -> None:
    with open(path, "wb") as fh:
        fh.write(data)


def build_open_fixtures(image_path: str, folder: str) -> tuple:
    """Write the fixtures into *folder* (which must exist and be empty) and
    return ((name, how it was built, expected kind or error, phrase), ...).
    The disc itself is hard-linked, never copied."""
    kit_path = survey.layout.kit_path(CONTROL_KIT_TAG)
    image = iso.Image(image_path)
    try:
        tex = image.read_file(kit_path)
    finally:
        image.close()
    first = bin_archive.entries(tex)[0]
    tag_at = first.pos + TEX_TAG_FIELD
    j = lambda name: os.path.join(folder, name)  # noqa: E731

    _write(j("kit.bin"), tex)
    os.link(image_path, j("disc.tex"))
    with open(j("disc.cue"), "w", encoding="ascii") as fh:
        fh.write('FILE "disc.tex" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    broken = bytearray(tex)
    broken[tag_at] ^= 0xFF
    _write(j("broken-tag.tex"), bytes(broken))
    kind = bytearray(tex)
    kind[first.pos] ^= 0xFF
    _write(j("broken-kind.tex"), bytes(kind))
    _write(j("note.txt"), b"this is not a CD image")
    _write(j("empty.bin"), b"")
    _write(j("zeros.iso"), bytes(ZERO_SECTORS * iso.RAW_SECTOR))
    with open(j("gone.cue"), "w", encoding="ascii") as fh:
        fh.write('FILE "nothere.bin" BINARY\n  TRACK 01 MODE2/2352\n')
    os.mkdir(j("folder"))

    n = len(survey.EXPECTED_SHAPE)
    return (
        ("disc.tex", "hard link to the disc", KIND_ROM, ""),
        ("disc.cue", "cue sheet naming disc.tex", KIND_ROM, ""),
        ("kit.bin", "%s extracted (%d bytes)" % (kit_path, len(tex)), KIND_TEX, ""),
        ("broken-tag.tex", "kit.bin, byte %d (record 0 at %d, +%d: the tag) XOR 0xFF"
         % (tag_at, first.pos, TEX_TAG_FIELD), "NotASource",
         "it has %d image/palette records where a kit container has %d" % (n - 1, n)),
        ("broken-kind.tex", "kit.bin, byte %d (record 0, +0: the kind) XOR 0xFF" % first.pos,
         "NotASource", "record 0 is kind %d" % (bin_archive.KIND_IMAGE ^ 0xFF)),
        ("note.txt", "22 bytes of text", "NotASource", "not a whole number of"),
        ("empty.bin", "0 bytes", "SourceEmpty", "is empty"),
        ("zeros.iso", "%d zeroed sectors" % ZERO_SECTORS, "NotASource", "no CD001"),
        ("gone.cue", "cue sheet naming nothere.bin", "SourceMissing", "nothere.bin"),
        ("missing.bin", "never written", "SourceMissing", "does not exist"),
        ("folder", "a folder", "SourceUnreadable", "is a folder"),
    )


def open_controls(image_path: str, folder: str) -> tuple:
    """Build the fixtures in *folder* and open each one.  Returns OpenControl
    per fixture; never raises for a fixture that is refused -- that is the
    point -- only for a disc that cannot give the fixtures at all."""
    try:
        fixtures = build_open_fixtures(image_path, folder)
    except OSError as exc:
        raise SourceUnreadable("Could not build the fixtures from %s in %s: %s"
                               % (image_path, folder, exc.strerror or exc)) from exc
    out = []
    for name, built, expect, phrase in fixtures:
        try:
            src = open_source(os.path.join(folder, name))
            got, message = src.kind, "opened as %s" % src.kind
        except (SourceMissing, SourceUnreadable, SourceEmpty, NotASource) as exc:
            got, message = type(exc).__name__, str(exc)
        out.append(OpenControl(name=name, built=built, expect=expect, phrase=phrase,
                               got=got, message=message))
    return tuple(out)

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
  11-record shape of section 1.1 (`tex.EXPECTED_SHAPE`).

Anything else is refused with a typed error from `errors`.

Either source then gives its kit containers through `kit()`, read by
`tex.read_kit` behind the guard of form.  On a disc, a sector marked
Form 2 whose bytes are in the Form 1 layout is read as Form 1, and the
kit's `notes` say so (section 2.1).
"""

from __future__ import annotations

import os
import re
import struct
from dataclasses import dataclass
from typing import Optional

from . import survey, tex
from .errors import (KitMissing, KitUnreadable, NotASource, SourceEmpty,
                     SourceMissing, SourceUnreadable)

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

    def kit(self, tag: str, trust_iso_size: bool = False) -> tex.Kit:
        """The kit container *tag*, read behind the guard of form.

        Its `problems` say whether it passed; `KitMissing` if the disc has
        no such tag, `KitUnreadable` if a sector of it is Form 2 for real.
        *trust_iso_size* reads only the ISO size, the way `iso.py` would:
        the diagnostic that shows what the header extent recovers."""
        return self.kits((tag,), trust_iso_size)[0]

    def kits(self, tags=None, trust_iso_size: bool = False) -> tuple:
        """`kit()` of each of *tags* (default: every tag), opening the disc once."""
        tags = self.tags if tags is None else tuple(tags)
        for tag in tags:
            if tag not in self.tags:
                raise KitMissing("%s has no kit container %s."
                                 % (self.path, survey.layout.KIT_PREFIX + tag
                                    + survey.layout.KIT_SUFFIX))
        try:
            image = iso.Image(self.image_path)
        except OSError as exc:
            raise SourceUnreadable("Could not read %s: %s"
                                   % (self.image_path, exc.strerror or exc)) from exc
        try:
            out = []
            for tag in tags:
                path = survey.layout.kit_path(tag)
                data, notes = read_disc_file(image, path, trust_iso_size)
                out.append(tex.read_kit(data, label="%s on %s" % (path, self.path),
                                        notes=notes))
            return tuple(out)
        finally:
            image.close()


@dataclass(frozen=True)
class TexSource:
    """A lone kit container: the file is the kit."""

    path: str
    data: bytes

    kind = KIND_TEX

    @property
    def size(self) -> int:
        return len(self.data)

    def kit(self, tag: Optional[str] = None) -> tex.Kit:
        """The file itself, read behind the guard of form; *tag* is ignored."""
        return tex.read_kit(self.data, label=self.path)


# -- the Form 2 tail ------------------------------------------------------

FORM2_TAIL = slice(iso.HEADER + iso.FORM1_DATA, iso.HEADER + 2324)
"""Bytes 2072..2347 of a raw sector: data in a real Form 2 sector, the
EDC/ECC area in Form 1.  Zero in every sector of the European Deluxe
whose subheader says Form 2 over a Form 1 layout (section 2.1)."""


def _slot_end(image, entry) -> int:
    """The first sector after *entry* that holds another file, or the end
    of the track: how far the file can reach without overlapping one."""
    later = [e.lba for e in image.files.values() if e.lba > entry.lba]
    return min(later + [image.sector_count])


def _sector_data(image, path: str, lba: int, index: int, count: int) -> tuple:
    """(2,048 data bytes, marked Form 2?) of one sector of *path*."""
    if image.form(lba) == 1:
        return image.read_sector(lba), False
    image.f.seek(lba * iso.RAW_SECTOR)
    raw = image.f.read(iso.RAW_SECTOR)
    if any(raw[FORM2_TAIL]):
        raise KitUnreadable(
            "%s on %s: sector %d (%d of %d) is Form 2 with data past byte 2048, "
            "so it is not a Form 1 sector with a wrong bit." % (
                path, image.path, lba, index + 1, count))
    return raw[iso.HEADER:iso.HEADER + iso.FORM1_DATA], True


def read_disc_file(image, path: str, trust_iso_size: bool = False) -> tuple:
    """(bytes, notes) of the kit container *path* on an opened `iso.Image`.

    Two things a patched disc gets wrong are not trusted, and the notes say
    when either was overruled:

    * **the size.**  The European Deluxe kept the Japanese ISO size for
      most of its TEX, and their own header lists records past it.  The
      file is read to where its header says it ends (`tex.declared_extent`)
      when that is past the ISO size and before the next file starts;
    * **the Form 2 bit.**  A sector marked Form 2 whose bytes 2072..2347
      are zero is in the Form 1 layout with a wrong bit, and gives the
      2,048 at byte 24 (section 2.1).  A Form 2 sector with data there is
      refused.

    *trust_iso_size* skips the first: the file is read to its ISO size.
    """
    entry = image.entry(path)
    if entry.lba + entry.sectors > image.sector_count:
        raise KitUnreadable("%s on %s runs past the end of the data track."
                            % (path, image.path))
    slot = _slot_end(image, entry) - entry.lba
    chunks, marked = [], []
    for i in range(entry.sectors):
        data, form2 = _sector_data(image, path, entry.lba + i, i, entry.sectors)
        chunks.append(data)
        if form2:
            marked.append(entry.lba + i)
    data = b"".join(chunks)
    notes = []
    extent = None if trust_iso_size else tex.declared_extent(data)
    if extent is None and not trust_iso_size and slot > entry.sectors:
        # The header's last list may itself be past the ISO size: look in the slot.
        for i in range(entry.sectors, slot):
            more, form2 = _sector_data(image, path, entry.lba + i, i, slot)
            chunks.append(more)
            if form2:
                marked.append(entry.lba + i)
            extent = tex.declared_extent(b"".join(chunks))
            if extent is not None:
                break
        data = b"".join(chunks)
    size = entry.size
    if extent is not None and entry.size < extent <= len(data):
        notes.append(tex.Note(tex.NOTE_PAST_ISO_SIZE,
                              "its ISO size is %d bytes and its own header ends at byte %d, "
                              "before the next file; read to %d."
                              % (entry.size, extent, extent)))
        size = extent
    if marked:
        reached = [m for m in marked if (m - entry.lba) * iso.FORM1_DATA < size]
        if reached:
            notes.append(tex.Note(tex.NOTE_FORM2_TAIL,
                                  "%d of the %d sectors read (%s) are marked Form 2 with "
                                  "the data in the Form 1 layout (bytes 2072-2347 zero); "
                                  "read as Form 1." % (len(reached), -(-size // iso.FORM1_DATA),
                                                      ", ".join(str(m) for m in reached))))
    return data[:size], tuple(notes)


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
    return tex.shape_problem(bin_archive.entries(data))


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
        kit_bytes = image.read_file(kit_path)
    finally:
        image.close()
    first = bin_archive.entries(kit_bytes)[0]
    tag_at = first.pos + TEX_TAG_FIELD
    j = lambda name: os.path.join(folder, name)  # noqa: E731

    _write(j("kit.bin"), kit_bytes)
    os.link(image_path, j("disc.tex"))
    with open(j("disc.cue"), "w", encoding="ascii") as fh:
        fh.write('FILE "disc.tex" BINARY\n  TRACK 01 MODE2/2352\n    INDEX 01 00:00:00\n')
    broken = bytearray(kit_bytes)
    broken[tag_at] ^= 0xFF
    _write(j("broken-tag.tex"), bytes(broken))
    kind = bytearray(kit_bytes)
    kind[first.pos] ^= 0xFF
    _write(j("broken-kind.tex"), bytes(kind))
    _write(j("note.txt"), b"this is not a CD image")
    _write(j("empty.bin"), b"")
    _write(j("zeros.iso"), bytes(ZERO_SECTORS * iso.RAW_SECTOR))
    with open(j("gone.cue"), "w", encoding="ascii") as fh:
        fh.write('FILE "nothere.bin" BINARY\n  TRACK 01 MODE2/2352\n')
    os.mkdir(j("folder"))

    n = len(tex.EXPECTED_SHAPE)
    return (
        ("disc.tex", "hard link to the disc", KIND_ROM, ""),
        ("disc.cue", "cue sheet naming disc.tex", KIND_ROM, ""),
        ("kit.bin", "%s extracted (%d bytes)" % (kit_path, len(kit_bytes)), KIND_TEX, ""),
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


# -- the two rules of read_disc_file, seen refusing -----------------------
#
# CORR-KITS-014: the Form 2 tail check and the "only up to the next file"
# limit had no planted control.  Both are planted here through a proxy of
# the opened image -- one sector's bytes, or one fake file in the
# directory -- so nothing of the disc is copied or written.

FORM2_PLANT_AT = 2100
"""Byte of the raw sector that the Form 2 control makes non-zero: inside
FORM2_TAIL (2072..2347)."""

FORM2_PLANT_VALUE = 0x55


class _PlantedFile:
    """A read-only file whose bytes at *at* read as *value*."""

    def __init__(self, f, at: int, value: int):
        self._f, self._at, self._value = f, at, value

    def seek(self, pos, whence=0):
        return self._f.seek(pos, whence)

    def tell(self):
        return self._f.tell()

    def read(self, n=-1):
        start = self._f.tell()
        data = self._f.read(n)
        if start <= self._at < start + len(data):
            buf = bytearray(data)
            buf[self._at - start] = self._value
            data = bytes(buf)
        return data


class _PlantedImage:
    """An opened `iso.Image` seen through one planted change: a byte of the
    file (*f*) or an extra entry in the directory (*files*)."""

    def __init__(self, image, f=None, files=None):
        self._image = image
        self.f = f if f is not None else image.f
        self.files = files if files is not None else image.files

    def __getattr__(self, name):
        return getattr(self._image, name)


@dataclass(frozen=True)
class DiscControl:
    """One rule of read_disc_file, its kit clean and planted."""

    name: str
    planted: str        # what was changed
    clean: str          # what the clean read gave
    after: str          # what the planted read gave
    ok: bool


def _read_kit_as(image, path: str):
    """(Kit, None) or (None, the KitUnreadable raised)."""
    try:
        data, notes = read_disc_file(image, path)
    except KitUnreadable as exc:
        return None, exc
    return tex.read_kit(data, label=path, notes=notes), None


def _describe(kit, exc) -> str:
    if exc is not None:
        return "%s: %s" % (type(exc).__name__, exc)
    kinds = ", ".join(n.kind for n in kit.notes) or "no note"
    return "%s (%d bytes; %s)" % ("passes" if kit.ok else "refused: " + "; ".join(kit.problems),
                                  kit.size, kinds)


def disc_controls(image_path: str, tags) -> tuple:
    """Plant (a) data in the Form 2 tail of the first marked sector of a kit
    and (b) a file right after the ISO sectors of the first kit whose header
    ends past them.
    (a) has to raise `KitUnreadable`; (b) has to stop the read at the ISO
    size and leave the kit refused.  Raises `SourceError` when the disc has
    no kit that either rule applies to (the Japanese disc has none)."""
    try:
        image = iso.Image(image_path)
    except OSError as exc:
        raise SourceUnreadable("Could not read %s: %s"
                               % (image_path, exc.strerror or exc)) from exc
    try:
        marked = past = None
        for tag in tags:
            path = survey.layout.kit_path(tag)
            entry = image.entry(path)
            kit, exc = _read_kit_as(image, path)
            if exc is not None:
                continue
            kinds = {n.kind for n in kit.notes}
            if marked is None and tex.NOTE_FORM2_TAIL in kinds:
                lba = next(entry.lba + i for i in range(entry.sectors)
                           if image.form(entry.lba + i) != 1)
                marked = (path, lba, kit)
            # Past the ISO size *and* past its last ISO sector: a header end
            # inside that sector's slack is read without the slot at all.
            if (past is None and tex.NOTE_PAST_ISO_SIZE in kinds and kit.ok
                    and kit.size > entry.sectors * iso.FORM1_DATA):
                past = (path, entry, kit)
            if marked and past:
                break
        if marked is None or past is None:
            raise NotASource("%s has no kit read through a wrong Form 2 bit and past "
                             "its ISO size, so the two read controls have nothing to plant."
                             % image_path)
        out = []

        path, lba, kit = marked
        at = lba * iso.RAW_SECTOR + FORM2_PLANT_AT
        planted = _PlantedImage(image, f=_PlantedFile(image.f, at, FORM2_PLANT_VALUE))
        got, exc = _read_kit_as(planted, path)
        out.append(DiscControl(
            name="Form 2 tail with data",
            planted="%s, sector %d, byte %d = 0x%02x"
                    % (path, lba, FORM2_PLANT_AT, FORM2_PLANT_VALUE),
            clean=_describe(kit, None), after=_describe(got, exc),
            ok=kit.ok and isinstance(exc, KitUnreadable)))

        path, entry, kit = past
        fence = entry.lba + entry.sectors
        files = dict(image.files)
        files["/PLANTED.BIN"] = _FakeEntry(fence)   # _slot_end reads only .lba
        planted = _PlantedImage(image, files=files)
        got, exc = _read_kit_as(planted, path)
        out.append(DiscControl(
            name="next file at the ISO size",
            planted="%s, a file placed at sector %d (its ISO end)" % (path, fence),
            clean=_describe(kit, None), after=_describe(got, exc),
            ok=(kit.ok and exc is None and not got.ok
                and tex.NOTE_PAST_ISO_SIZE not in {n.kind for n in got.notes})))
        return tuple(out)
    finally:
        image.close()


@dataclass(frozen=True)
class _FakeEntry:
    lba: int

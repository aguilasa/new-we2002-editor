"""Read one kit container (`TEX_<tag>.BIN`) behind a guard of form.

PLAN-KITS-PY.md section 2.1: a kit can come from anywhere -- another disc,
a patch, a file WETex just wrote -- so it is not checked against a digest
but against its form.  The guard is:

* 11 image/palette records, in the rectangles and widths of section 1.1
  (`EXPECTED_SHAPE`);
* every image's LZSS stream ends inside the file and decompresses to the
  size its rectangle asks for (`plain_size`);
* every palette's 256 entries are inside the file.

What fails is not raised at once: it is collected in `Kit.problems`, one
sentence per record that failed, so a diagnostic view can list them all.
`Kit.require()` is the refusal, for a caller that needs the kit whole.

This module is also the one place the rectangles of a kit container live.
They are addresses, and section 3.1 puts addresses in the `looks` layout;
they stay here because `tools/looks/` is only changed by the two tasks of
phase 5 (section 2), and `looks` itself never reads them -- it samples the
kit by VRAM point.  `survey` and `source` import them from here.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Optional

_TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
for _sub in ("pes2", "looks"):
    _path = os.path.normpath(os.path.join(_TOOLS, _sub))
    if _path not in sys.path:
        sys.path.insert(0, _path)

import bin_archive  # noqa: E402  (tools/pes2, after the path insert)
import lzss  # noqa: E402

from .errors import KitRefused  # noqa: E402

KIND_IMAGE = "image"
KIND_CLUT = "clut"

EXPECTED_SHAPE = (
    (KIND_IMAGE, 576, 256, 64, 128),   # 0 uniform, first set
    (KIND_IMAGE, 576, 384, 64, 128),   # 1 sleeves, first set
    (KIND_CLUT, 0, 486, 256, 1),       # 2 player palette, first set
    (KIND_CLUT, 0, 488, 256, 1),       # 3 goalkeeper palette, first set
    (KIND_IMAGE, 576, 256, 64, 128),   # 4 uniform, second set
    (KIND_IMAGE, 576, 384, 64, 128),   # 5 sleeves, second set
    (KIND_CLUT, 0, 486, 256, 1),       # 6 player palette, second set
    (KIND_CLUT, 0, 488, 256, 1),       # 7 goalkeeper palette, second set
    (KIND_IMAGE, 704, 256, 64, 64),    # 8 flag
    (KIND_CLUT, 256, 480, 256, 1),     # 9 flag palette
    (KIND_IMAGE, 768, 384, 64, 128),   # 10 referee
)
"""(kind, x, y, w, h) of every record, in file order, as section 1.1 measured."""

RECORD_NAMES = (
    "uniform, first set", "sleeves, first set",
    "player palette, first set", "goalkeeper palette, first set",
    "uniform, second set", "sleeves, second set",
    "player palette, second set", "goalkeeper palette, second set",
    "flag", "flag palette", "referee",
)

IMAGE_RECORDS = tuple(i for i, r in enumerate(EXPECTED_SHAPE) if r[0] == KIND_IMAGE)
PALETTE_RECORDS = tuple(i for i, r in enumerate(EXPECTED_SHAPE) if r[0] == KIND_CLUT)


def plain_size(record: int) -> int:
    """How many bytes the image of *record* decompresses to.

    The rectangle's halfwords, twice over for the flag: its record declares
    64x64 and every stream on the four measured discs holds twice that, the
    second half filler (section 1.1; `bin_archive.KNOWN_DOUBLE`).
    """
    _kind, x, y, w, h = EXPECTED_SHAPE[record]
    size = w * h * 2
    return size * 2 if (x, y, w, h) == bin_archive.KNOWN_DOUBLE else size


def shape_of(records) -> tuple:
    """(kind, x, y, w, h) of each record of `bin_archive.entries`."""
    out = []
    for e in records:
        kind = KIND_IMAGE if e.is_image else KIND_CLUT if e.is_clut else "kind %d" % e.kind
        out.append((kind, e.x, e.y, e.w, e.h))
    return tuple(out)


def shape_problem(records) -> Optional[str]:
    """None if *records* have the kit container shape, else the first thing that differs."""
    shape = shape_of(records)
    if shape == EXPECTED_SHAPE:
        return None
    if not shape:
        return "it holds no image or palette record list"
    if len(shape) != len(EXPECTED_SHAPE):
        return ("it has %d image/palette records where a kit container has %d"
                % (len(shape), len(EXPECTED_SHAPE)))
    for i, (got, want) in enumerate(zip(shape, EXPECTED_SHAPE)):
        if got != want:
            return ("record %d is %s at (%d,%d) %dx%d where a kit container has "
                    "%s at (%d,%d) %dx%d" % ((i,) + got + want))
    return "its records differ from a kit container's"  # unreachable: shapes differ


HEADER_TAG = 0x800F
LIST_END = b"\x0f\x80\xff\x00"
"""The tag of a list's last record followed by its 0x00FF end halfword."""


def declared_extent(data: bytes) -> Optional[int]:
    """Where the container ends by its own header, or None if it has none.

    A kit container opens with a table of 32-bit words, each the offset of
    one record list in its low halfword and the 0x800F tag in its high one
    (a zero word stands for an empty slot).  The container ends with the
    list the largest offset points to: its `LIST_END` plus the end halfword.
    None when the table is absent or that list's end is not in *data*.
    """
    offsets, p = [], 0
    while p + 4 <= len(data):
        lo, hi = data[p] | data[p + 1] << 8, data[p + 2] | data[p + 3] << 8
        if hi == HEADER_TAG:
            offsets.append(lo)
        elif lo or hi:
            break
        p += 4
    if not offsets:
        return None
    end = data.find(LIST_END, max(offsets))
    return None if end < 0 else end + len(LIST_END)


NOTE_PAST_ISO_SIZE = "past-iso-size"
NOTE_FORM2_TAIL = "form2-tail"


@dataclass(frozen=True)
class Note:
    """How a kit was read when it was not the plain way; `str()` is the sentence."""

    kind: str
    """`NOTE_PAST_ISO_SIZE` or `NOTE_FORM2_TAIL`."""
    text: str

    def __str__(self) -> str:
        return self.text


@dataclass(frozen=True)
class Image:
    """One decompressed image record: 8-bit indices, `width` x `height`.

    The rectangle's pixels only: the flag's filler half (`plain_size`) is
    checked by the guard and not kept."""

    record: int
    name: str
    width: int
    height: int
    indices: bytes


@dataclass(frozen=True)
class Palette:
    """One CLUT record: its 256 BGR555 halfwords as they are in the file."""

    record: int
    name: str
    raw: bytes


@dataclass(frozen=True)
class Kit:
    """A kit container read behind the guard of form.

    `problems` is empty when the container passed; otherwise one sentence
    per record that failed, naming it.  `notes` says how it was read when
    that was not the plain way (the Form 2 tail of section 2.1).  `images`
    and `palettes` hold only the records that passed.
    """

    label: str
    size: int
    problems: tuple
    notes: tuple = ()
    images: tuple = ()
    palettes: tuple = ()
    data: bytes = field(default=b"", repr=False, compare=False)
    """The container bytes as read (after the Form 2 tail, if any)."""

    @property
    def ok(self) -> bool:
        return not self.problems

    def require(self) -> "Kit":
        """This kit, or `KitRefused` with every problem in the message."""
        if self.problems:
            raise KitRefused("%s is refused: %s." % (self.label, "; ".join(self.problems)))
        return self


def _record_problem(record: int, why: str) -> str:
    return "record %d (%s) %s" % (record, RECORD_NAMES[record], why)


def read_kit(data: bytes, label: str = "the kit container", notes=()) -> Kit:
    """Read *data* as a kit container.  Never raises for a malformed one:
    what is wrong goes in `Kit.problems`, so one bad record does not hide
    the others."""
    data = bytes(data)
    records = bin_archive.entries(data)
    why = shape_problem(records)
    if why is not None:
        return Kit(label=label, size=len(data), problems=(why,), notes=tuple(notes),
                   data=data)

    problems, images, palettes = [], [], []
    for i in IMAGE_RECORDS:
        e, want = records[i], plain_size(i)
        if e.offset >= len(data):
            problems.append(_record_problem(
                i, "starts at byte %d, past the end of the %d-byte file"
                % (e.offset, len(data))))
            continue
        try:
            plain, _used = lzss.decompress(data, e.offset, cap=want)
        except lzss.LzssError as exc:
            problems.append(_record_problem(i, "has an LZSS stream that does not decode: %s"
                                            % exc))
            continue
        if len(plain) != want:
            problems.append(_record_problem(
                i, "decompresses to %d bytes where its rectangle asks for %d"
                % (len(plain), want)))
            continue
        width = e.w * 2                       # 8 bpp: two pixels per halfword
        images.append(Image(record=i, name=RECORD_NAMES[i], width=width, height=e.h,
                            indices=plain[:width * e.h]))
    for i in PALETTE_RECORDS:
        e = records[i]
        want = e.colours * 2
        raw = data[e.offset:e.offset + want]
        if len(raw) != want:
            problems.append(_record_problem(
                i, "wants %d bytes at byte %d and the file has %d there"
                % (want, e.offset, len(raw))))
            continue
        palettes.append(Palette(record=i, name=RECORD_NAMES[i], raw=raw))
    return Kit(label=label, size=len(data), problems=tuple(problems), notes=tuple(notes),
               images=tuple(images), palettes=tuple(palettes), data=data)


# -- the guard, seen refusing ---------------------------------------------
#
# Section 5, control 4: one byte changed in the LZSS stream of a sound kit
# has to be refused, with the sentence that names the record.

STREAM_CONTROL_RECORD = 0
STREAM_CONTROL_AT = 0
"""Byte, counted from the start of the record's stream, that the control
replaces: the first flag byte, which says literal or command for the next
eight tokens.  A changed literal byte is not a defect of form -- the stream
still decodes to the right size -- and the guard cannot see it (measured:
byte +1 of TEX_00 on the Japanese disc, 0x00 -> 0xff, passes)."""


@dataclass(frozen=True)
class StreamControl:
    """A sound kit, the byte planted in it, and what the guard said."""

    label: str
    offset: int
    """Where record 0's stream starts."""
    at: int
    before: int
    after: int
    clean: Kit
    planted: Kit

    @property
    def ok(self) -> bool:
        """The clean kit passed and the planted one failed on that record."""
        name = "record %d (" % STREAM_CONTROL_RECORD
        return (self.clean.ok and not self.planted.ok
                and any(p.startswith(name) for p in self.planted.problems))


def stream_control(data: bytes, label: str = "the kit container") -> StreamControl:
    """Plant one byte in the stream of record 0 and read both."""
    clean = read_kit(data, label)
    records = bin_archive.entries(data)
    offset = records[STREAM_CONTROL_RECORD].offset
    at = offset + STREAM_CONTROL_AT
    planted = bytearray(data)
    before = planted[at]
    planted[at] = before ^ 0xFF
    return StreamControl(label=label, offset=offset, at=at, before=before, after=planted[at],
                         clean=clean, planted=read_kit(bytes(planted), label))

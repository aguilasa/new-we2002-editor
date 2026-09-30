"""Survey of the kit containers (`/BIN/TEX_<tag>.BIN`) of one disc image.

This is the measurement behind the table of PLAN-KITS-PY.md section 1.1,
promoted from a throwaway script to a function that returns data.  Nothing
here prints: `tools/kits/cli.py survey` is the one that shows the result.

What a kit container holds, in file order (11 records):

    uniform image (576,256), sleeves image (576,384),
    player CLUT (0,486), goalkeeper CLUT (0,488)      -- first set
    the same four again                                -- second set
    flag image (704,256), flag CLUT (256,480),
    referee image (768,384)

`survey_files()` is the pure half: it takes the container bytes by tag and
measures them, which is also what lets a caller plant a defect in memory and
see the counts move.  `survey_image()` opens a disc and feeds it.
"""

from __future__ import annotations

import hashlib
import os
import sys
from dataclasses import dataclass
from typing import Mapping, Optional

_TOOLS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
for _sub in ("pes2", "looks"):
    _path = os.path.normpath(os.path.join(_TOOLS, _sub))
    if _path not in sys.path:
        sys.path.insert(0, _path)

import bin_archive  # noqa: E402  (tools/pes2, after the path insert)
import iso  # noqa: E402
import lzss  # noqa: E402
import layout  # noqa: E402  (tools/looks: where the kit files are named)


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

FIRST_IMAGES = (0, 1)
SECOND_IMAGES = (4, 5)
FIRST_PALETTES = (2, 3)
SECOND_PALETTES = (6, 7)
FLAG = 8
REFEREE = 10


class SurveyError(Exception):
    """The survey could not run; the message is what a UI would show."""


class NoKitsFound(SurveyError):
    """The image opened but holds no kit container."""


@dataclass(frozen=True)
class KitFacts:
    """What was measured on one container."""

    tag: str
    size: int
    shape: tuple
    shape_ok: bool
    problem: Optional[str] = None
    images_equal: Optional[bool] = None
    palettes_equal: Optional[bool] = None
    player_equals_keeper: Optional[bool] = None
    flag_size: Optional[int] = None
    flag_declared: Optional[int] = None
    flag_tail_values: Optional[frozenset] = None
    referee_digest: Optional[str] = None

    @property
    def measured(self) -> bool:
        """Whether every field past the shape was measured."""
        return self.shape_ok and self.problem is None

    @property
    def sets_equal(self) -> bool:
        return bool(self.measured and self.images_equal and self.palettes_equal)

    @property
    def only_palettes_differ(self) -> bool:
        return bool(self.measured and self.images_equal and not self.palettes_equal)


@dataclass(frozen=True)
class Survey:
    """The whole survey, and the counts section 1.1 reports."""

    source: str
    kits: tuple

    @property
    def total(self) -> int:
        return len(self.kits)

    @property
    def shape_ok(self) -> tuple:
        return tuple(k.tag for k in self.kits if k.shape_ok)

    @property
    def shape_off(self) -> tuple:
        return tuple(k.tag for k in self.kits if not k.shape_ok)

    @property
    def distinct_shapes(self) -> int:
        return len({k.shape for k in self.kits})

    @property
    def problems(self) -> tuple:
        return tuple((k.tag, k.problem) for k in self.kits if k.problem)

    @property
    def measured(self) -> tuple:
        return tuple(k for k in self.kits if k.measured)

    @property
    def sets_equal(self) -> tuple:
        return tuple(k.tag for k in self.measured if k.sets_equal)

    @property
    def images_differ(self) -> tuple:
        return tuple(k.tag for k in self.measured if not k.images_equal)

    @property
    def only_palettes_differ(self) -> tuple:
        return tuple(k.tag for k in self.measured if k.only_palettes_differ)

    @property
    def player_equals_keeper(self) -> tuple:
        return tuple(k.tag for k in self.measured if k.player_equals_keeper)

    @property
    def flag_sizes(self) -> tuple:
        return tuple(sorted({k.flag_size for k in self.measured}))

    @property
    def flag_declared(self) -> tuple:
        return tuple(sorted({k.flag_declared for k in self.measured}))

    @property
    def flag_tail_single(self) -> tuple:
        """Tags whose decompressed flag has one byte value in its second half."""
        return tuple(k.tag for k in self.measured if len(k.flag_tail_values) == 1)

    @property
    def flag_tail_values(self) -> tuple:
        values = set()
        for k in self.measured:
            values |= k.flag_tail_values
        return tuple(sorted(values))

    @property
    def flag_tail_split(self) -> tuple:
        """((byte value, how many containers), ...) over the single-valued tails."""
        split = {}
        for k in self.measured:
            if len(k.flag_tail_values) == 1:
                (v,) = k.flag_tail_values
                split[v] = split.get(v, 0) + 1
        return tuple(sorted(split.items()))

    @property
    def referee_variants(self) -> int:
        return len({k.referee_digest for k in self.measured})

    @property
    def size_range(self) -> tuple:
        sizes = [k.size for k in self.kits]
        return (min(sizes), max(sizes)) if sizes else (0, 0)


def _shape_of(records) -> tuple:
    out = []
    for e in records:
        kind = KIND_IMAGE if e.is_image else KIND_CLUT if e.is_clut else "kind %d" % e.kind
        out.append((kind, e.x, e.y, e.w, e.h))
    return tuple(out)


def _clut_bytes(data: bytes, entry) -> bytes:
    return bytes(data[entry.offset:entry.offset + entry.colours * 2])


def measure_kit(tag: str, data: bytes) -> KitFacts:
    """Measure one container.  Never raises for a malformed container: what
    went wrong is carried in `problem`, so one bad file does not hide 104."""
    records = bin_archive.entries(data)
    shape = _shape_of(records)
    if shape != EXPECTED_SHAPE:
        return KitFacts(tag=tag, size=len(data), shape=shape, shape_ok=False)
    try:
        images = {i: bin_archive.read_image(data, records[i])[0]
                  for i, rec in enumerate(EXPECTED_SHAPE) if rec[0] == KIND_IMAGE}
    except (lzss.LzssError, ValueError) as exc:
        return KitFacts(tag=tag, size=len(data), shape=shape, shape_ok=True,
                        problem="an image does not decompress: %s" % exc)
    cluts = {i: _clut_bytes(data, records[i])
             for i, rec in enumerate(EXPECTED_SHAPE) if rec[0] == KIND_CLUT}

    flag = bytes(images[FLAG])
    return KitFacts(
        tag=tag,
        size=len(data),
        shape=shape,
        shape_ok=True,
        images_equal=all(images[a] == images[b]
                         for a, b in zip(FIRST_IMAGES, SECOND_IMAGES)),
        palettes_equal=all(cluts[a] == cluts[b]
                           for a, b in zip(FIRST_PALETTES, SECOND_PALETTES)),
        player_equals_keeper=cluts[FIRST_PALETTES[0]] == cluts[FIRST_PALETTES[1]],
        flag_size=len(flag),
        flag_declared=records[FLAG].expected,
        flag_tail_values=frozenset(flag[len(flag) // 2:]),
        referee_digest=hashlib.sha256(bytes(images[REFEREE])).hexdigest(),
    )


def survey_files(files: Mapping[str, bytes], source: str = "") -> Survey:
    """Measure containers given as {tag: bytes}.  Pure: no I/O."""
    if not files:
        raise NoKitsFound("No kit container (%s<tag>%s) was found in %s."
                          % (layout.KIT_PREFIX, layout.KIT_SUFFIX, source or "the input"))
    kits = tuple(measure_kit(tag, files[tag]) for tag in sorted(files))
    return Survey(source=source, kits=kits)


def kit_paths(image) -> list:
    """The kit container paths of an opened `iso.Image`, sorted."""
    head = layout.KIT_DIR + layout.KIT_PREFIX
    return sorted(p for p in image.files
                  if p.startswith(head) and p.endswith(layout.KIT_SUFFIX))


def tag_of(path: str) -> str:
    return path[len(layout.KIT_DIR + layout.KIT_PREFIX):-len(layout.KIT_SUFFIX)]


def read_kits(image_path: str) -> dict:
    """{tag: bytes} of every kit container on the disc at *image_path*."""
    try:
        image = iso.Image(image_path)
    except OSError as exc:
        raise SurveyError("Could not open %s: %s" % (image_path, exc.strerror or exc)) from exc
    except ValueError as exc:
        raise SurveyError("%s is not a readable data track: %s" % (image_path, exc)) from exc
    try:
        out = {}
        for path in kit_paths(image):
            try:
                out[tag_of(path)] = image.read_file(path)
            except (iso.Form2Sector, iso.OutsideTrack) as exc:
                raise SurveyError("%s on %s cannot be read as Form 1: %s"
                                  % (path, image_path, exc)) from exc
        return out
    finally:
        image.close()


def survey_image(image_path: str) -> Survey:
    """Survey every kit container of the disc at *image_path*."""
    return survey_files(read_kits(image_path), source=image_path)

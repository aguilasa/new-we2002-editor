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
from types import MappingProxyType
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


# -- negative controls ---------------------------------------------------
#
# Each control plants one defect in a copy of the containers and names the
# survey figure that has to move.  They live here, next to what they break,
# so the red is reproducible from HEAD instead of from a throwaway probe.

@dataclass(frozen=True)
class ControlResult:
    """One planted defect and the figure it had to move."""

    name: str
    planted: str
    figure: str
    clean: object
    after: object

    @property
    def red(self) -> bool:
        return self.clean != self.after


def _flip_clut_bit(data: bytes, record: int) -> bytes:
    entry = bin_archive.entries(data)[record]
    out = bytearray(data)
    out[entry.offset] ^= 0x01
    return bytes(out)


def _flip_stream_bit(data: bytes, record: int, at: int = 3) -> bytes:
    entry = bin_archive.entries(data)[record]
    out = bytearray(data)
    out[entry.offset + at] ^= 0x01
    return bytes(out)


def _shift_rect_x(data: bytes, record: int) -> bytes:
    entry = bin_archive.entries(data)[record]
    out = bytearray(data)
    out[entry.pos + 2:entry.pos + 4] = (entry.x + 1).to_bytes(2, "little")
    return bytes(out)


NEGATIVE_CONTROLS = (
    ("A4 player CLUT, second set", "A4", lambda d: _flip_clut_bit(d, SECOND_PALETTES[0]),
     "first set == second set", lambda s: s.sets_equal),
    ("A4 goalkeeper CLUT, first set", "A4", lambda d: _flip_clut_bit(d, FIRST_PALETTES[1]),
     "player palette == keeper palette", lambda s: s.player_equals_keeper),
    ("00 referee LZSS stream, +3", "00", lambda d: _flip_stream_bit(d, REFEREE),
     "referee variants / problems", lambda s: (s.referee_variants, s.problems)),
    ("00 referee rect x + 1", "00", lambda d: _shift_rect_x(d, REFEREE),
     "shape ok", lambda s: len(s.shape_ok)),
)
"""(name, tag, plant, figure, measure): the defects of KITS-TASK-01's Log."""


def negative_controls(files: Mapping[str, bytes], source: str = "") -> tuple:
    """Plant each defect of NEGATIVE_CONTROLS on its own and measure again.
    Pure: *files* is not modified."""
    clean = survey_files(files, source)
    out = []
    for name, tag, plant, figure, measure in NEGATIVE_CONTROLS:
        if tag not in files:
            raise SurveyError("The control '%s' needs TEX_%s, which %s does not hold."
                              % (name, tag, source or "the input"))
        planted = dict(files)
        planted[tag] = plant(files[tag])
        out.append(ControlResult(name=name, planted="TEX_" + tag, figure=figure,
                                 clean=measure(clean),
                                 after=measure(survey_files(planted, source))))
    return tuple(out)


def negative_controls_image(image_path: str) -> tuple:
    """negative_controls() over every kit container of a disc."""
    return negative_controls(read_kits(image_path), source=image_path)


# -- who owns a VRAM point -------------------------------------------------
#
# PLAN-KITS-PY.md section 4.4: which record of which file on the disc covers
# a VRAM point, and whether it starts there.  A point named in a note may be
# the origin of a record or only a sample inside one; this tells the two apart.

@dataclass(frozen=True)
class Owner:
    """One record of one file that covers a VRAM point."""

    path: str
    kind: str
    x: int
    y: int
    w: int
    h: int

    def starts_at(self, point) -> bool:
        return (self.x, self.y) == tuple(point)

    @property
    def shape(self) -> tuple:
        return (self.kind, self.x, self.y, self.w, self.h)


@dataclass(frozen=True)
class PointOwners:
    """Every record on the disc that covers one VRAM point."""

    point: tuple
    owners: tuple

    @property
    def files(self) -> tuple:
        return tuple(sorted({o.path for o in self.owners}))

    @property
    def starters(self) -> tuple:
        return tuple(o for o in self.owners if o.starts_at(self.point))

    def grouped(self) -> tuple:
        """((shape, (paths sorted)), ...) -- one line per record shape,
        sorted by how many files own it (most first), then by shape."""
        groups = {}
        for o in self.owners:
            groups.setdefault(o.shape, set()).add(o.path)
        return tuple(sorted(((s, tuple(sorted(p))) for s, p in groups.items()),
                            key=lambda g: (-len(g[1]), g[0])))


@dataclass(frozen=True)
class RectsReport:
    """The answer for every point asked, over every readable file."""

    source: str
    points: tuple
    scanned: int
    with_records: int
    skipped: tuple


def _kind_name(e) -> str:
    return KIND_IMAGE if e.is_image else KIND_CLUT if e.is_clut else "kind %d" % e.kind


def covers(entry, point) -> bool:
    """x in [rx, rx+w) and y in [ry, ry+h), in the halfword units the record stores."""
    px, py = point
    return entry.x <= px < entry.x + entry.w and entry.y <= py < entry.y + entry.h


def owners_of(files: Mapping[str, bytes], points, source: str = "",
              skipped=()) -> RectsReport:
    """For each VRAM point, every record in *files* ({path: bytes}) covering it.
    Pure: no I/O.  *skipped* is carried through for the caller to report."""
    points = tuple(tuple(p) for p in points)
    found = {p: [] for p in points}
    with_records = 0
    for path in sorted(files):
        records = bin_archive.entries(files[path])
        with_records += bool(records)
        for e in records:
            for p in points:
                if covers(e, p):
                    found[p].append(Owner(path=path, kind=_kind_name(e),
                                          x=e.x, y=e.y, w=e.w, h=e.h))
    return RectsReport(
        source=source,
        points=tuple(PointOwners(point=p, owners=tuple(found[p])) for p in points),
        scanned=len(files),
        with_records=with_records,
        skipped=tuple(skipped),
    )


def read_all_files(image_path: str) -> tuple:
    """({path: bytes} of every readable file on the disc, ((path, reason), ...)
    of the ones that could not be read as Form 1 inside the track)."""
    try:
        image = iso.Image(image_path)
    except OSError as exc:
        raise SurveyError("Could not open %s: %s" % (image_path, exc.strerror or exc)) from exc
    except ValueError as exc:
        raise SurveyError("%s is not a readable data track: %s" % (image_path, exc)) from exc
    try:
        out, skipped = {}, []
        for path in sorted(image.files):
            try:
                out[path] = image.read_file(path)
            except iso.Form2Sector:
                skipped.append((path, "Form 2"))
            except iso.OutsideTrack:
                skipped.append((path, "outside the track"))
        return out, tuple(skipped)
    finally:
        image.close()


def parse_point(text: str) -> tuple:
    """'608,256' -> (608, 256); a malformed point raises SurveyError."""
    try:
        x, y = (int(v, 0) for v in text.split(","))
    except ValueError as exc:
        raise SurveyError("'%s' is not a VRAM point X,Y" % text) from exc
    return (x, y)


def rects_image(image_path: str, points) -> RectsReport:
    """owners_of() over every readable file of the disc at *image_path*."""
    files, skipped = read_all_files(image_path)
    return owners_of(files, points, source=image_path, skipped=skipped)


# -- negative control of the owner search --------------------------------
#
# Shift the uniform origins of one kit container out of (576,256) and the
# owner counts of a point inside that rectangle have to drop by that file.

RECTS_CONTROL_TAG = "A4"
RECTS_CONTROL_FROM = (576, 256)
RECTS_CONTROL_TO_X = 640


def rects_control_path() -> str:
    return layout.KIT_DIR + layout.KIT_PREFIX + RECTS_CONTROL_TAG + layout.KIT_SUFFIX


def _shift_origins(data: bytes, origin, to_x: int) -> tuple:
    """(new bytes, how many records moved): every image record at *origin*
    gets x = *to_x*."""
    out = bytearray(data)
    moved = 0
    for e in bin_archive.entries(data):
        if e.is_image and (e.x, e.y) == tuple(origin):
            out[e.pos + 2:e.pos + 4] = to_x.to_bytes(2, "little")
            moved += 1
    return bytes(out), moved


@dataclass(frozen=True)
class RectsControl:
    """One point measured on the clean files and on the planted ones."""

    point: tuple
    planted: str
    moved: int
    files: tuple      # (clean, planted) number of owner files
    records: tuple    # (clean, planted) number of owner records
    planted_owns: tuple  # (clean, planted): does the planted file own the point

    @property
    def red(self) -> bool:
        return self.files[0] != self.files[1] or self.records[0] != self.records[1]


def rects_negative(files: Mapping[str, bytes], points, source: str = "") -> tuple:
    """Plant the origin shift of RECTS_CONTROL_TAG and compare owners_of()
    before and after, point by point.  Pure: *files* is not modified."""
    path = rects_control_path()
    if path not in files:
        raise SurveyError("The rects control needs %s, which %s does not hold."
                          % (path, source or "the input"))
    planted = dict(files)
    planted[path], moved = _shift_origins(files[path], RECTS_CONTROL_FROM, RECTS_CONTROL_TO_X)
    clean = owners_of(files, points, source)
    after = owners_of(planted, points, source)
    return tuple(
        RectsControl(point=a.point, planted=path, moved=moved,
                     files=(len(a.files), len(b.files)),
                     records=(len(a.owners), len(b.owners)),
                     planted_owns=(path in a.files, path in b.files))
        for a, b in zip(clean.points, after.points))


def rects_negative_image(image_path: str, points) -> tuple:
    """rects_negative() over every readable file of the disc at *image_path*."""
    files, _ = read_all_files(image_path)
    return rects_negative(files, points, source=image_path)


# -- which primitive samples which kit record ----------------------------
#
# PLAN-KITS-PY.md section 4.3: for each figure of the LOOKS SET, how many
# primitives sample each rectangle of the kit container, read through the
# draw list of `tools/looks` and never remapped here.  Two counts per role,
# because the draw list resolves only the FIRST record covering the FIRST
# corner (section 1.2): "first" is that resolution, "touch" is every kit
# record any of the four corners falls in.

KIT_ROLES = MappingProxyType({
    (576, 256): "uniform",
    (576, 384): "sleeves",
    (704, 256): "flag",
    (768, 384): "referee",
})
"""Role of a kit image record by its VRAM origin, as section 1.1 measured."""

ROLE_ORDER = ("uniform", "sleeves", "flag", "referee")
SLEEVES = (576, 384)
PRIMS_FIGURES = (0, 1)
PRIMS_TUPLE = "A-A1-A-A-A"
"""The tuple the figures are drawn in: the reference `assembly --check-image`
walks.  The tuple picks the head and its colours; the body's pieces, which
sample the kit, are the figure's own."""

CONTAINER_DAT2D = "DAT2D"
CONTAINER_KIT = "kit"
CONTAINER_NONE = "nothing"
CONTAINER_ORDER = (CONTAINER_DAT2D, CONTAINER_KIT, CONTAINER_NONE)


def role_of(x: int, y: int) -> str:
    """The role of a kit image record at origin (x, y); an unknown origin is
    named by it, so a container of another shape shows up instead of hiding."""
    return KIT_ROLES.get((x, y), "other (%d,%d)" % (x, y))


@dataclass(frozen=True)
class FigurePrims:
    """What one figure's primitives sample, for one kit."""

    figure: int
    total: int
    sections: int
    containers: tuple      # ((container label, primitives), ...)
    first: tuple           # ((role, primitives), ...) by the draw list's resolution
    touch: tuple           # ((role, primitives), ...) by any of the four corners
    touch_dat2d: int       # primitives with a corner in a DAT2D image record
    touch_none: int        # primitives with a corner in no record of either file
    disagree: int          # primitives whose corners touch a kit role the first missed
    kit_box: Optional[tuple]  # (x0, y0, x1, y1) of the corners in kit records, inclusive

    def first_of(self, role: str) -> int:
        return dict(self.first).get(role, 0)

    def touch_of(self, role: str) -> int:
        return dict(self.touch).get(role, 0)

    @property
    def sleeves(self) -> int:
        """Primitives sampling the sleeves image, by either count."""
        return max(self.first_of("sleeves"), self.touch_of("sleeves"))


@dataclass(frozen=True)
class PrimsReport:
    source: str
    kit: str
    tuple_text: str
    figures: tuple


def _ordered(counts: dict, order) -> tuple:
    keys = [k for k in order if k in counts] + sorted(k for k in counts if k not in order)
    return tuple((k, counts[k]) for k in keys)


def _corners_of(entry, primitive) -> list:
    """The four VRAM texels of one draw-list entry, with the tuple's band --
    the same texcoords the draw list and scene.py sample."""
    import atlas

    if entry["texcoords"] is not None:
        coords = entry["texcoords"]
    else:
        coords = [(u, v + entry["band"]) for u, v in primitive.texcoords]
    return [atlas.texel(primitive, u, v) for u, v in coords]


def _covering(records, point) -> list:
    return [r for r in records if covers(r, point)]


def _drawn(files: Mapping[str, bytes], values, figure: int, kit: str) -> list:
    """[(draw-list entry, primitive), ...] of one figure: the draw list of
    `tools/looks/assembly.py`, each entry paired with the primitive its
    section scan holds.  Shared by the primitive count and the UV rects, so
    both read the same geometry the same way."""
    import assembly
    import section

    try:
        parts = assembly.draw_list(files, values, figure, kit)
    except assembly.BadAssembly as exc:
        raise SurveyError("The draw list of figure %d refused: %s" % (figure, exc)) from exc
    scans = {}
    out = []
    for entry in parts:
        name = entry["file"]
        if name not in scans:
            scans[name] = section.scan(files[name], layout.GEOMETRY_START[name])
        out.append((entry, scans[name].sections[entry["section"]].primitives[entry["primitive"]]))
    return out


def _tuple_values(tuple_text: str):
    import looks

    try:
        return looks.parse_tuple(tuple_text)
    except looks.BadLooks as exc:
        raise SurveyError("The tuple %s is refused: %s" % (tuple_text, exc)) from exc


def figure_prims(files: Mapping[str, bytes], values, figure: int, kit: str) -> FigurePrims:
    """Count one figure's primitives per container and per kit role.
    Pure: *files* is {disc path: bytes} and is not modified."""
    import texture

    kit_path = layout.kit_path(kit)
    kit_images = texture.images(files[kit_path])
    dat_images = texture.images(files[layout.DAT2D])
    by_offset = {r.offset: r for r in kit_images}
    drawn = _drawn(files, values, figure, kit)
    parts = [entry for entry, _ in drawn]

    containers, first, touch = {}, {}, {}
    touch_dat2d = touch_none = disagree = 0
    kit_points = []
    for entry, primitive in drawn:
        if entry["container"] is None:
            label, first_role = CONTAINER_NONE, None
        elif entry["container"] == kit_path:
            rec = by_offset[entry["image"]]
            label, first_role = CONTAINER_KIT, role_of(rec.x, rec.y)
        elif entry["container"] == layout.DAT2D:
            label, first_role = CONTAINER_DAT2D, None
        else:
            label, first_role = entry["container"], None
        containers[label] = containers.get(label, 0) + 1
        if first_role is not None:
            first[first_role] = first.get(first_role, 0) + 1

        roles, in_dat2d, nowhere = set(), False, False
        for point in _corners_of(entry, primitive):
            kit_hit = _covering(kit_images, point)
            dat_hit = _covering(dat_images, point)
            roles.update(role_of(r.x, r.y) for r in kit_hit)
            if kit_hit:
                kit_points.append(point)
            in_dat2d = in_dat2d or bool(dat_hit)
            nowhere = nowhere or not (kit_hit or dat_hit)
        for role in roles:
            touch[role] = touch.get(role, 0) + 1
        touch_dat2d += in_dat2d
        touch_none += nowhere
        disagree += bool(roles - {first_role})

    return FigurePrims(
        figure=figure, total=len(parts),
        sections=len({(p["file"], p["section"]) for p in parts}),
        containers=_ordered(containers, CONTAINER_ORDER),
        first=_ordered(first, ROLE_ORDER),
        touch=_ordered(touch, ROLE_ORDER),
        touch_dat2d=touch_dat2d, touch_none=touch_none, disagree=disagree,
        kit_box=(min(x for x, _ in kit_points), min(y for _, y in kit_points),
                 max(x for x, _ in kit_points), max(y for _, y in kit_points))
        if kit_points else None)


def prims_files(files: Mapping[str, bytes], kit: str = layout.KIT_ON_SCREEN,
                tuple_text: str = PRIMS_TUPLE, source: str = "") -> PrimsReport:
    """figure_prims() for both figures.  Pure: no I/O."""
    values = _tuple_values(tuple_text)
    return PrimsReport(source=source, kit=kit, tuple_text=tuple_text,
                       figures=tuple(figure_prims(files, values, f, kit)
                                     for f in PRIMS_FIGURES))


def read_prims_files(image_path: str, kit: str) -> dict:
    """The four files the draw list reads, through the looks disc guard."""
    if kit not in layout.KIT_TAGS:
        raise SurveyError("TEX_%s is not one of the %d kit containers."
                          % (kit, len(layout.KIT_TAGS)))
    return _read_disc_files(image_path, (layout.EDT_MOD, layout.MODEL, layout.DAT2D,
                                         layout.kit_path(kit)))


def read_prims_all_kits(image_path: str) -> dict:
    """The three model files and every kit container, in one disc open."""
    return _read_disc_files(image_path, (layout.EDT_MOD, layout.MODEL, layout.DAT2D)
                            + tuple(layout.kit_path(k) for k in layout.KIT_TAGS))


def _read_disc_files(image_path: str, paths) -> dict:
    import iso_source

    try:
        with iso_source.open_disc(image_path) as disc:
            return {p: disc.read(p) for p in paths}
    except OSError as exc:
        raise SurveyError("Could not open %s: %s" % (image_path, exc.strerror or exc)) from exc
    except layout.WrongDisc as exc:
        raise SurveyError(str(exc)) from exc
    except ValueError as exc:
        raise SurveyError("%s is not a readable data track: %s" % (image_path, exc)) from exc


def prims_image(image_path: str, kit: str = layout.KIT_ON_SCREEN,
                tuple_text: str = PRIMS_TUPLE) -> PrimsReport:
    """prims_files() over the disc at *image_path*."""
    return prims_files(read_prims_files(image_path, kit), kit, tuple_text, source=image_path)


# -- the same count over every kit, and over several tuples ---------------
#
# PLAN-KITS-PY.md section 4.3 says the count is the same in the 105 kits and
# does not depend on the tuple beyond the head.  These two sweeps are what
# that sentence rests on.

@dataclass(frozen=True)
class KitsSweep:
    """prims_files() over every kit, grouped by identical result."""

    source: str
    tuple_text: str
    groups: tuple   # ((figures, (kit tags sorted)), ...), most kits first

    @property
    def kits(self) -> int:
        return sum(len(tags) for _, tags in self.groups)


def prims_all_kits(files: Mapping[str, bytes], tuple_text: str = PRIMS_TUPLE,
                   source: str = "") -> KitsSweep:
    """Count the primitives with every kit container of *files* and group
    the kits whose two figures come out the same.  Pure: no I/O."""
    tags = [k for k in layout.KIT_TAGS if layout.kit_path(k) in files]
    if not tags:
        raise NoKitsFound("No kit container was found in %s." % (source or "the input"))
    groups = {}
    for tag in tags:
        figures = prims_files(files, tag, tuple_text, source).figures
        groups.setdefault(figures, []).append(tag)
    return KitsSweep(source=source, tuple_text=tuple_text,
                     groups=tuple(sorted(((f, tuple(t)) for f, t in groups.items()),
                                         key=lambda g: (-len(g[1]), g[1]))))


def prims_all_kits_image(image_path: str, tuple_text: str = PRIMS_TUPLE) -> KitsSweep:
    """prims_all_kits() over the disc at *image_path*."""
    return prims_all_kits(read_prims_all_kits(image_path), tuple_text, source=image_path)


def kit_roles_of(report: PrimsReport) -> tuple:
    """What a tuple sweep compares: per figure, the kit roles by both counts --
    the part of the result the body decides and the head does not."""
    return tuple((f.figure, f.first, f.touch) for f in report.figures)


def prims_tuples(files: Mapping[str, bytes], kit: str, tuple_texts,
                 source: str = "") -> tuple:
    """prims_files() once per tuple.  Pure: no I/O."""
    return tuple(prims_files(files, kit, t, source) for t in tuple_texts)


def prims_tuples_image(image_path: str, kit: str, tuple_texts) -> tuple:
    """prims_tuples() over the disc at *image_path*."""
    return prims_tuples(read_prims_files(image_path, kit), kit, tuple_texts, source=image_path)


# -- negative controls of the primitive count ----------------------------

PRIMS_AWAY = (0, 0)
"""Where a planted record is moved so no primitive can sample it: the display
area at the top-left of VRAM, which no texture page of the figures names."""


def _move_images(data: bytes, origin, to) -> tuple:
    """(new bytes, how many records moved): every image record at *origin*
    gets origin *to*."""
    out = bytearray(data)
    moved = 0
    for e in bin_archive.entries(data):
        if e.is_image and (e.x, e.y) == tuple(origin):
            out[e.pos + 2:e.pos + 4] = to[0].to_bytes(2, "little")
            out[e.pos + 4:e.pos + 6] = to[1].to_bytes(2, "little")
            moved += 1
    return bytes(out), moved


@dataclass(frozen=True)
class PrimsControl:
    """One planted move, the count it had to move, and whether it did."""

    name: str
    moved: int
    figure: int
    count: str
    clean: int
    after: int
    expect: str

    @property
    def ok(self) -> bool:
        if self.expect == EXPECT_ZERO:
            return self.after == 0
        if self.expect == EXPECT_DROP:
            return self.clean > 0 and self.after == 0
        return self.after > 0


PRIMS_OVERLAP = (560, 256)
"""Where the positive control puts the sleeves: 16 halfwords left of the
uniform, so its rect covers the uniform's columns 576..623 from behind."""

EXPECT_ZERO = "stays zero"
EXPECT_DROP = "drops to zero"
EXPECT_RISE = "rises above zero"

PRIMS_CONTROLS = (
    ("sleeves moved to (0,0)", SLEEVES, PRIMS_AWAY,
     (("sleeves", "first", EXPECT_ZERO), ("sleeves", "touch", EXPECT_ZERO))),
    ("uniform moved to (0,0)", (576, 256), PRIMS_AWAY,
     (("uniform", "first", EXPECT_DROP), ("uniform", "touch", EXPECT_DROP))),
    ("sleeves moved to (560,256)", SLEEVES, PRIMS_OVERLAP,
     ((role_of(*PRIMS_OVERLAP), "touch", EXPECT_RISE),
      (role_of(*PRIMS_OVERLAP), "first", EXPECT_ZERO),
      ("", "disagree", EXPECT_RISE))),
)
"""(name, origin, to, ((role, count, expectation), ...)).  The third is the
positive control of the any-corner count: the sleeves records, moved to
overlap the uniform rect from behind it in file order, are never the draw
list's first match -- and have to be counted all the same.  It is moved to
(560,256) and not onto (576,256) because the role is read off the origin: a
record lying exactly on the uniform's origin is named "uniform"."""


def _count_of(fig: FigurePrims, role: str, count: str) -> int:
    if count == "first":
        return fig.first_of(role)
    if count == "touch":
        return fig.touch_of(role)
    return fig.disagree


def prims_negative(files: Mapping[str, bytes], kit: str = layout.KIT_ON_SCREEN,
                   source: str = "") -> tuple:
    """Plant each move of PRIMS_CONTROLS in the kit and measure again.
    Pure: *files* is not modified."""
    path = layout.kit_path(kit)
    clean = prims_files(files, kit, source=source)
    out = []
    for name, origin, to, checks in PRIMS_CONTROLS:
        planted = dict(files)
        planted[path], moved = _move_images(files[path], origin, to)
        after = prims_files(planted, kit, source=source)
        for a, b in zip(clean.figures, after.figures):
            for role, count, expect in checks:
                out.append(PrimsControl(name=name, moved=moved, figure=a.figure,
                                        count=" ".join(t for t in (role, count) if t),
                                        clean=_count_of(a, role, count),
                                        after=_count_of(b, role, count),
                                        expect=expect))
    return tuple(out)


def prims_negative_image(image_path: str, kit: str = layout.KIT_ON_SCREEN) -> tuple:
    """prims_negative() over the disc at *image_path*."""
    return prims_negative(read_prims_files(image_path, kit), kit, source=image_path)


@dataclass(frozen=True)
class SweepControl:
    """The every-kit sweep and the tuple comparison, clean and with one kit's
    uniform moved away: the two checks behind section 4.3, seen failing."""

    kit: str
    moved: int
    clean: KitsSweep
    planted: KitsSweep
    roles_distinct: int   # kit_roles_of() of the kit, clean vs planted

    @property
    def red(self) -> bool:
        alone = any(tags == (self.kit,) for _, tags in self.planted.groups)
        return (len(self.clean.groups) == 1 and len(self.planted.groups) == 2
                and alone and self.roles_distinct == 2)


def prims_all_kits_negative(files: Mapping[str, bytes], kit: str = layout.KIT_ON_SCREEN,
                            tuple_text: str = PRIMS_TUPLE, source: str = "") -> SweepControl:
    """Move *kit*'s uniform records to PRIMS_AWAY and run both sweeps' checks
    again.  Pure: *files* is not modified."""
    path = layout.kit_path(kit)
    if path not in files:
        raise SurveyError("The sweep control needs %s, which %s does not hold."
                          % (path, source or "the input"))
    planted = dict(files)
    planted[path], moved = _move_images(files[path], (576, 256), PRIMS_AWAY)
    roles = {kit_roles_of(prims_files(f, kit, tuple_text, source)) for f in (files, planted)}
    return SweepControl(kit=kit, moved=moved,
                        clean=prims_all_kits(files, tuple_text, source),
                        planted=prims_all_kits(planted, tuple_text, source),
                        roles_distinct=len(roles))


def prims_all_kits_negative_image(image_path: str, kit: str = layout.KIT_ON_SCREEN,
                                  tuple_text: str = PRIMS_TUPLE) -> SweepControl:
    """prims_all_kits_negative() over the disc at *image_path*."""
    return prims_all_kits_negative(read_prims_all_kits(image_path), kit, tuple_text,
                                   source=image_path)


# -- the UV rects in the work bitmap -------------------------------------
#
# PLAN-KITS-PY.md section 4.6 crosses the community's zone map against the
# geometry, and the zone map is drawn on the 256x128 WORK BITMAP
# (SUPERPACK-UNIFORMES.md section 2): the uniform image (128x128 pixels) on
# the left, the long-sleeves image (128x128) on the right.  This turns each
# kit primitive of the figures into the rect of bitmap pixels it samples.
#
# A corner's pixel is computed in PIXELS from the primitive's page and its
# u,v -- column = (page_x - record_x) * texels_per_halfword + u -- and never
# through the halfword VRAM x that atlas.texel returns: at 8 bits one
# halfword is two pixels, and rounding through it loses the odd column.

BITMAP_W = 256
BITMAP_H = 128
BITMAP_X = MappingProxyType({"uniform": 0, "sleeves": 128})
"""Left edge, in the work bitmap, of each kit role that lives in it."""

UV_OUTSIDE_ROLE = "not uniform or sleeves"
UV_OUTSIDE_SPLIT = "corners in two images"
UV_OUTSIDE_EDGE = "rect leaves 256x128"


@dataclass(frozen=True)
class UvRect:
    """One kit primitive and the bitmap pixels its corners bound, inclusive."""

    file: str
    section: int
    primitive: int
    role: str
    rect: Optional[tuple]    # (x0, y0, x1, y1) in bitmap pixels, or None if outside
    outside: str             # "" when mapped, else why it is not


@dataclass(frozen=True)
class FigureUv:
    figure: int
    rects: tuple             # UvRect, in draw-list order

    @property
    def mapped(self) -> tuple:
        return tuple(r for r in self.rects if not r.outside)

    @property
    def outside(self) -> tuple:
        return tuple(r for r in self.rects if r.outside)

    @property
    def union(self) -> Optional[tuple]:
        rs = [r.rect for r in self.mapped]
        if not rs:
            return None
        return (min(r[0] for r in rs), min(r[1] for r in rs),
                max(r[2] for r in rs), max(r[3] for r in rs))

    @property
    def pixels(self) -> int:
        """Distinct bitmap pixels inside the axis-aligned rects: bounding-rect
        coverage, not a rasterisation of the triangles."""
        seen = set()
        for r in self.mapped:
            x0, y0, x1, y1 = r.rect
            for y in range(y0, y1 + 1):
                seen.update((x, y) for x in range(x0, x1 + 1))
        return len(seen)


@dataclass(frozen=True)
class UvReport:
    source: str
    kit: str
    tuple_text: str
    figures: tuple

    def canonical(self) -> dict:
        """The geometry only -- no source path, no kit tag -- so the digest
        names the rects and nothing else."""
        return {"bitmap": [BITMAP_W, BITMAP_H], "tuple": self.tuple_text,
                "figures": [{"figure": f.figure,
                             "rects": [{"file": r.file, "section": r.section,
                                        "primitive": r.primitive, "role": r.role,
                                        "rect": list(r.rect) if r.rect else None,
                                        "outside": r.outside}
                                       for r in f.rects]}
                            for f in self.figures]}

    def canonical_json(self) -> str:
        import json

        return json.dumps(self.canonical(), sort_keys=True, separators=(",", ":"))

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.canonical_json().encode("ascii")).hexdigest()


def bitmap_pixel(primitive, u: int, v: int, record) -> tuple:
    """(column, row) of texel (u, v) of *primitive* inside the image *record*,
    in pixels: the page's halfword offset from the record times the texels a
    halfword holds at the primitive's depth, plus u."""
    import atlas

    page_x, page_y = primitive.tpage_vram
    per = atlas.texels_per_unit(primitive.tpage_depth)
    return ((page_x - record.x) * per + u, page_y + v - record.y)


def _texcoords_of(entry, primitive) -> list:
    """The (u, v) of the four corners, with the tuple's band -- the same
    coordinates _corners_of() turns into VRAM texels."""
    if entry["texcoords"] is not None:
        return list(entry["texcoords"])
    return [(u, v + entry["band"]) for u, v in primitive.texcoords]


def figure_uv(files: Mapping[str, bytes], values, figure: int, kit: str,
              roles: Mapping = KIT_ROLES) -> FigureUv:
    """The bitmap rect of every primitive of one figure with a corner in a kit
    image record (the any-corner rule of figure_prims).  *roles* names a
    record by its origin; a planted control passes its own.  Pure."""
    import atlas
    import texture

    kit_images = texture.images(files[layout.kit_path(kit)])
    out = []
    for entry, primitive in _drawn(files, values, figure, kit):
        corners = []
        for u, v in _texcoords_of(entry, primitive):
            hits = _covering(kit_images, atlas.texel(primitive, u, v))
            corners.append((u, v, hits[0] if hits else None))
        if not any(rec is not None for _, _, rec in corners):
            continue
        named = {roles.get((rec.x, rec.y), role_of(rec.x, rec.y))
                 if rec is not None else None for _, _, rec in corners}
        key = dict(file=entry["file"], section=entry["section"],
                   primitive=entry["primitive"])
        if len(named) != 1:
            out.append(UvRect(role="+".join(sorted(r or "no kit record" for r in named)),
                              rect=None, outside=UV_OUTSIDE_SPLIT, **key))
            continue
        role = named.pop()
        if role not in BITMAP_X:
            out.append(UvRect(role=role, rect=None, outside=UV_OUTSIDE_ROLE, **key))
            continue
        pts = [bitmap_pixel(primitive, u, v, rec) for u, v, rec in corners]
        left = BITMAP_X[role]
        rect = (left + min(x for x, _ in pts), min(y for _, y in pts),
                left + max(x for x, _ in pts), max(y for _, y in pts))
        inside = (left <= rect[0] and rect[2] < left + BITMAP_W // 2
                  and 0 <= rect[1] and rect[3] < BITMAP_H)
        out.append(UvRect(role=role, rect=rect,
                          outside="" if inside else UV_OUTSIDE_EDGE, **key))
    return FigureUv(figure=figure, rects=tuple(out))


def uv_files(files: Mapping[str, bytes], kit: str = layout.KIT_ON_SCREEN,
             tuple_text: str = PRIMS_TUPLE, source: str = "",
             roles: Mapping = KIT_ROLES) -> UvReport:
    """figure_uv() for both figures.  Pure: no I/O."""
    values = _tuple_values(tuple_text)
    return UvReport(source=source, kit=kit, tuple_text=tuple_text,
                    figures=tuple(figure_uv(files, values, f, kit, roles)
                                  for f in PRIMS_FIGURES))


def uv_image(image_path: str, kit: str = layout.KIT_ON_SCREEN) -> UvReport:
    """uv_files() over the disc at *image_path*."""
    return uv_files(read_prims_files(image_path, kit), kit, source=image_path)


# -- negative controls of the UV rects -----------------------------------

UNIFORM = (576, 256)
UV_SHIFT = (577, 256)
"""The uniform record moved one halfword right: at 8 bits every pixel the
figures sample is then two columns further left in the image.  The control
still names the moved record "uniform" -- the role is keyed by origin, and
without that every rect would just fall outside instead of moving.  Corners
on the uniform's first halfword column fall out of the moved record, so the
primitives that touch it leave the mapped set; the others must move."""


@dataclass(frozen=True)
class UvControl:
    """One planted move, one figure (-1: both), and what it did to the rects."""

    name: str
    moved: int
    figure: int
    measure: str
    clean: str
    after: str
    ok: bool


def _key(r: UvRect) -> tuple:
    return (r.file, r.section, r.primitive)


def uv_negative(files: Mapping[str, bytes], kit: str = layout.KIT_ON_SCREEN,
                source: str = "") -> tuple:
    """Plant (a) the uniform shifted by +1 halfword and (b) the uniform moved
    to PRIMS_AWAY, and check what each has to do.  Pure."""
    path = layout.kit_path(kit)
    clean = uv_files(files, kit, source=source)
    out = []

    planted = dict(files)
    planted[path], moved = _move_images(files[path], UNIFORM, UV_SHIFT)
    after = uv_files(planted, kit, source=source,
                     roles=MappingProxyType({**KIT_ROLES, UV_SHIFT: "uniform"}))
    name = "uniform moved to (%d,%d)" % UV_SHIFT
    out.append(UvControl(name, moved, -1, "digest changes", clean.digest[:16],
                         after.digest[:16], clean.digest != after.digest))
    for a, b in zip(clean.figures, after.figures):
        before = {_key(r): r.rect for r in a.mapped}
        common = [(before[_key(r)], r.rect) for r in b.mapped if _key(r) in before]
        shifted = sum(1 for c, d in common if d == (c[0] - 2, c[1], c[2] - 2, c[3]))
        out.append(UvControl(name, moved, a.figure, "rects move -2 px in x",
                             "%d mapped" % len(a.mapped),
                             "%d of %d still mapped moved" % (shifted, len(common)),
                             bool(common) and shifted == len(common)))
        ua, ub = a.union, b.union
        out.append(UvControl(name, moved, a.figure, "union x1 moves -2 px",
                             "%r" % (ua,), "%r" % (ub,),
                             ua is not None and ub is not None and ub[2] == ua[2] - 2))

    planted = dict(files)
    planted[path], moved = _move_images(files[path], UNIFORM, PRIMS_AWAY)
    after = uv_files(planted, kit, source=source)
    name = "uniform moved to (%d,%d)" % PRIMS_AWAY
    for a, b in zip(clean.figures, after.figures):
        out.append(UvControl(name, moved, a.figure, "mapped count drops to 0",
                             str(len(a.mapped)), str(len(b.mapped)),
                             len(a.mapped) > 0 and len(b.mapped) == 0))
    return tuple(out)


def uv_negative_image(image_path: str, kit: str = layout.KIT_ON_SCREEN) -> tuple:
    """uv_negative() over the disc at *image_path*."""
    return uv_negative(read_prims_files(image_path, kit), kit, source=image_path)

"""The reader of a replay capture: what `oracle.py --replay` and
`--replay-field` keep, read back with no emulator (PLAN-KITS-REPLAY section 2.1).

A capture is the JSON `oracle.py --replay SLOT [--focus K]` writes to
`work/kits-oracle/replay-<slot>[-<focus>].json` -- the paused replay up close,
before and after the turn -- or the one `--replay-field SLOT` writes to
`replay-field-<slot>-capture.json`, the walk over the 22 on the pitch.
`Capture.load` reads either, puts back the tuples the JSON round trip turned
into lists, refuses one that lacks a key the analysis reads, and migrates the
implicit schema of the captures kept so far (v0) to v1: the fixed keys
`schema`, `kind`, `slot`, `focus`, `button` and `taps`.

`Frame` is one whole frame of a capture, `Figure` one figure of it -- a list of
pieces, head first, so every function that took a figure as a list of pieces
still takes one -- and `Walk` the table of the walk.  `judge` and `judge_walk`
are the judges of G8 over them; the expectations they are given, and the
plants, stay with the oracle.

No emulator, no `tools/looks/oracle`: what the analysis needs of the disc --
the MODEL.BIN index (`oracle.model_index`) and the uniform record's width --
is passed in.
"""

from __future__ import annotations

import json
import math
import os
import re

from . import raster
from . import tex  # noqa: F401  (tex puts tools/pes2 and tools/looks on sys.path)
from .errors import KitsError
from .figure import BACK_COPY, GLYPH_W, KEEPER_ARMBAND, SLEEVE_LENGTHS
from .zones import GAPS, ZONES

import layout  # noqa: E402  (tools/looks)

SCHEMA = 1
"""The capture schema `Capture.load` gives: v0, the files kept before this
module, have no `schema` key and are migrated."""
KIND_CLOSE = "close"
"""A `--replay` capture: one figure up close, before and after the turn."""
KIND_WALK = "walk"
"""A `--replay-field` capture: one capture per tap of the walk."""
WALK_BUTTON = "L2"
"""The button `--replay --focus K` taps K times to reach a player
(`oracle.REPLAY_FIELD_BUTTONS[0]`)."""
CLOSE_KEYS = ("front", "back", "front_frames", "back_frames", "turn_frames", "rotate",
              "yaws", "turned", "hits", "pages", "buffer", "texture")
"""Keys a close capture has to hold: the ones `oracle.py --replay` reads back."""
WALK_KEYS = ("slot", "button", "foci", "pages")
"""Keys a walk capture has to hold."""
POSE_KEYS = ("events", "lists", "offsets")
"""Keys every `pose_capture` inside a capture has to hold."""
FOCUS_KEYS = ("k", "moves", "refused")
"""Keys every focus of a walk has to hold; one not refused also `FOCUS_TAKEN`."""
FOCUS_TAKEN = ("frames", "capture", "followed")
"""Keys a focus of the walk the tap reached has to hold."""
_CLOSE_NAME = re.compile(r"^replay-(\d+)(?:-(\d+))?\.json$")
"""`replay-<slot>[-<focus>].json`: a v0 close capture names its slot only here."""

VRAM_W = 1024
"""Halfwords across VRAM."""
KIT_PAGES = tuple((x, 256) for x in range(512, VRAM_W, 64))
"""Every page a kit can sit in, in a match (`oracle.KIT_PAGES`)."""
KIT_CLUTS = tuple((0, y) for y in range(486, 494))
"""The kit palettes' VRAM rows (`oracle.KIT_CLUTS`)."""
KIT_BITS = 8
"""A kit page's depth."""
IMAGE_HEIGHT = 128
"""Rows of the uniform image; the sleeves image lies below it on the page."""
TEXTURE_HALFWORDS = 128
"""Halfwords across an 8-bit texture page: 256 texels."""
NEUTRAL = 128
"""The colour a modulated texel is drawn unchanged under: the GPU multiplies
by colour / 128."""
ROOTS = (2, 56, 13)
"""The sections a figure opens at, the piece after its head: outfield (2), the
goalkeeper of the selection screen (56) and the one of a match (13)."""
FAMILIES = {2: "outfield", 13: "goalkeeper"}
"""Root -> family; any other root is "other"."""
POSE_MARGIN = 16
"""Pixels around a figure's projected vertices within which the frame's
textured quads are taken as that figure's."""
TORSO_MARGIN = 2
"""Pixels around the torso's own projected vertices within which a quad is
taken as drawn on it: behind a player the box of the whole figure takes in
the back of a neighbour a score of pixels off the axis (slot 10)."""
PANEL_W, PANEL_H = 20, 24
"""A back panel: the torso gap's size (core/zones.py GAPS)."""
PLAYER_PALETTE = {1: 2, 2: 6}
"""Set -> the record of its player palette."""
UNIFORM_WIDTH = tex.EXPECTED_SHAPE[0][3]
"""Halfwords across the uniform image (record 0 of a kit, section 1.1): the
row width `field_number` and `Figure.panel` read a uniform page with."""
ARMBAND_REPLACES = {SLEEVE_LENGTHS["short"]["armband"]: SLEEVE_LENGTHS["short"]["replaced"],
                    SLEEVE_LENGTHS["long"]["armband"]: SLEEVE_LENGTHS["long"]["replaced"],
                    KEEPER_ARMBAND: 15}
"""Armband -> the arm section it is drawn in place of: 90 for 4 on the short
sleeve, 93 for 97 on the long one (`core.figure.SLEEVE_LENGTHS`), 92 for 15
on the goalkeeper of family 13 (KITS-REPLAYS-9-10 items 3 and 4)."""
REPLAY_STILL = 0
"""The most a followed figure's matrices may differ between the last two
frames of a capture: the replay is paused."""
REPLAY_FOLLOW_DEPTH = 5000
"""Depth under which the figure on the axis is the one the camera follows."""
REPLAY_FOLLOW_OFF = 8.0
"""Pixels off the axis within which a figure is the followed one."""
REPLAY_FOCUS_MARGIN = (8.0, 1000)
"""The next figure has to lie this many pixels farther off the axis, or this
far apart in depth, for the followed one to be unambiguous."""
REPLAY_ARMBANDS = (90, 93, 92, 91, 94)
"""MODEL.BIN sections that draw a captain's armband: 90 on a short sleeve, 93
on a long one, 92 on the goalkeeper of family 13, 91 and 94 on family 56."""
OUTFIELD_ARMBANDS = (90, 93)
"""The two armbands of an outfield captain."""
SHORT_SLEEVES = (3, 4, 5, 6)
"""The short sleeves of family 2."""
LONG_SLEEVES = (95, 96, 97, 98)
"""The long sleeves of family 2."""
REPLAY_SHARED_CELL = (0, 0, 80)
"""The panel cell every outfield back of a page samples beside its own."""


class ReplayError(KitsError):
    """A replay capture that cannot be read: missing, not JSON, or lacking a
    key the analysis reads."""


# -- the capture -------------------------------------------------------------

def restore_samples(capture) -> None:
    """The tuples a JSON round trip turned into lists, put back, in every
    primitive of a `pose_capture`."""
    if capture is None:
        return
    for one in capture["lists"].values():
        for s in one:
            s.update(page=tuple(s["page"]), clut=tuple(s["clut"]),
                     uv=[tuple(t) for t in s["uv"]], xy=[tuple(t) for t in s["xy"]],
                     rgb=[tuple(c) for c in s["rgb"]] if s.get("rgb") else None)


def _require(data: dict, keys, where: str) -> None:
    for key in keys:
        if key not in data:
            raise ReplayError("%s lacks the key %r" % (where, key))


def _pose(data, where: str) -> None:
    if data is None:
        return
    if not isinstance(data, dict):
        raise ReplayError("%s is not a pose capture" % where)
    _require(data, POSE_KEYS, where)


class Capture:
    """One replay capture, migrated to schema v1.  `data` is the whole
    migrated dict; the fixed keys are also attributes."""

    def __init__(self, data: dict, path: str = None):
        self.data = data
        self.path = path
        self.schema = data["schema"]
        self.kind = data["kind"]
        self.slot = data["slot"]
        self.focus = data["focus"]
        self.button = data["button"]
        self.taps = data["taps"]

    @classmethod
    def load(cls, path: str, slot: int = None) -> "Capture":
        """Read *path*; *slot* is needed only for a v0 close capture whose
        file name does not say it."""
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except OSError as exc:
            raise ReplayError("%s cannot be read: %s" % (path, exc)) from exc
        except ValueError as exc:
            raise ReplayError("%s is not JSON: %s" % (path, exc)) from exc
        return cls.from_dict(data, os.path.basename(path), slot, path)

    @classmethod
    def from_dict(cls, data, name: str = "the capture", slot: int = None,
                  path: str = None) -> "Capture":
        """`load` on a dict already read; *name* is the file name, which a
        v0 close capture takes its slot and focus from."""
        if not isinstance(data, dict):
            raise ReplayError("%s is not a JSON object" % name)
        if data.get("schema", 0) not in (0, SCHEMA):
            raise ReplayError("%s has schema %r, this reader knows 0 and %d"
                              % (name, data.get("schema"), SCHEMA))
        if "foci" in data:
            _require(data, WALK_KEYS, name)
            for focus in data["foci"]:
                where = "%s focus %s" % (name, focus.get("k"))
                _require(focus, FOCUS_KEYS, where)
                if not focus["refused"]:
                    _require(focus, FOCUS_TAKEN, where)
                    _pose(focus["capture"], where + " capture")
                    restore_samples(focus["capture"])
            taken = [f["k"] for f in data["foci"]]
            data.update(schema=SCHEMA, kind=KIND_WALK, focus=None,
                        taps=max(taken) if taken else 0)
            return cls(data, path)
        _require(data, CLOSE_KEYS, name)
        _pose(data["front"], name + " front")
        _pose(data["back"], name + " back")
        found = _CLOSE_NAME.match(name)
        focus = data.get("focus")
        if focus is None:
            focus = int(found.group(2)) if found and found.group(2) else 0
        if "slot" in data:
            slot = data["slot"]
        elif slot is None:
            if not found:
                raise ReplayError("%s lacks the key 'slot', and its name does not say it"
                                  % name)
            slot = int(found.group(1))
        restore_samples(data["front"])
        restore_samples(data["back"])
        data["hits"] = [(tag, index, [tuple(a) for a in at], flat, shared)
                        for tag, index, at, flat, shared in data["hits"]]
        if data["buffer"] is not None:
            data["buffer"].update(origin=tuple(data["buffer"]["origin"]),
                                  offset=tuple(data["buffer"]["offset"]),
                                  rows=[[tuple(p) for p in row]
                                        for row in data["buffer"]["rows"]])
        if data["texture"]:
            data["texture"]["cluts"] = {k: [tuple(c) for c in v]
                                        for k, v in data["texture"]["cluts"].items()}
        data.update(schema=SCHEMA, kind=KIND_CLOSE, slot=slot, focus=focus,
                    button=WALK_BUTTON if focus else None, taps=focus)
        return cls(data, path)

    def frames(self, side: str = "front") -> list:
        """The `Frame`s of the close capture's *side*, "front" (the first
        capture) or "back" (the turned one); [] when there is none."""
        if self.kind != KIND_CLOSE:
            raise ReplayError("frames() reads a close capture; a walk is read by Walk")
        return capture_frames(self.data[side])


# -- frames, figures ---------------------------------------------------------

def is_figure(sample) -> bool:
    """A primitive of a kit: 8 bits, a kit CLUT, a kit page."""
    return kit_image_of(sample) is not None


def kit_image_of(sample) -> str:
    """Which kit image a primitive samples: "uniform", "sleeves", "both" or
    None when its page is not the kit's."""
    if (sample["page"] not in KIT_PAGES or sample["bits"] != KIT_BITS
            or sample["clut"] not in KIT_CLUTS):
        return None
    halves = {"uniform" if v < IMAGE_HEIGHT else "sleeves" for _u, v in sample["uv"]}
    return halves.pop() if len(halves) == 1 else "both"


def work_point(u: int, v: int) -> tuple:
    """A texel of the kit page in work-bitmap pixels: the uniform on the left,
    the sleeves image on the right (core/flat.py)."""
    return (u, v) if v < IMAGE_HEIGHT else (IMAGE_HEIGHT + u, v - IMAGE_HEIGHT)


def sample_zones(sample) -> set:
    """The names of the zones the texel box of one primitive touches."""
    points = [work_point(u, v) for u, v in sample["uv"]]
    x0, y0 = min(p[0] for p in points), min(p[1] for p in points)
    x1, y1 = max(p[0] for p in points), max(p[1] for p in points)
    return {z.name for z in ZONES
            if z.x <= x1 and x0 < z.x + z.w and z.y <= y1 and y0 < z.y + z.h}


def matrix_pieces(stops, lag: int = 1) -> list:
    """The stops turned into drawn pieces: the matrix of stop k belongs to the
    section the pointers name *lag* stops later, each as {"section",
    "matrix"}; a stop naming no section, or several, is a None section."""
    out = []
    for k in range(len(stops) - lag):
        named = stops[k + lag]["named"]
        out.append({"section": named[0][1] if len(named) == 1 else None,
                    "matrix": (tuple(stops[k]["rotation"]), tuple(stops[k]["translation"]))})
    return out


def pose_frames(capture: dict) -> list:
    """The frames of a capture: for each submit of a list with figure
    primitives, the matrix stops since the previous such submit.  The first
    is left out, its stops having begun mid-frame."""
    blocks, current, out = [], [], []
    for one in capture["events"]:
        if one["kind"] == "matrix":
            current.append(one)
            continue
        samples = capture["lists"].get("%d" % one["head"])
        if not samples or not any(is_figure(s) for s in samples):
            continue
        blocks.append((one["head"], current))
        current = []
    for k, (head, stops) in enumerate(blocks):
        if k == 0:
            continue        # its stops began mid-frame
        out.append({"head": head, "stops": stops})
    return out


def pose_project(rotation, translation, projection, vertex):
    """A model vertex through one piece's GTE matrix and the projection:
    RTPS, `SX = OFX + H * X / Z`, rotation in 4.12."""
    x, y, z = vertex
    r = rotation
    cx = (r[0] * x + r[1] * y + r[2] * z) / 4096.0 + translation[0]
    cy = (r[3] * x + r[4] * y + r[5] * z) / 4096.0 + translation[1]
    cz = (r[6] * x + r[7] * y + r[8] * z) / 4096.0 + translation[2]
    if cz <= 0:
        return None
    h = projection["H"]
    return (projection["OFX"] + h * cx / cz, projection["OFY"] + h * cy / cz)


PAIRINGS = ("indices", "corners")
"""How a primitive's texels are paired with its vertices: `indices`, the
stored order, is the one the game uses; `corners` is what `--pair-by
corners` shows it is not (CORR-KITS-083)."""


def piece_error(piece, projection, sec, group, pair: str = "indices") -> tuple:
    """(mean pixel distance, primitives matched) of one piece: each primitive
    of its section projected with the piece's matrix and matched, by its four
    texels, to the nearest primitive of *group* that carries them.  *pair*
    says which vertex each texel goes with (`PAIRINGS`)."""
    by_uv = {}
    for one in group:
        if len(one["uv"]) == 4:
            by_uv.setdefault(tuple(tuple(t) for t in one["uv"]), []).append(one)
    total, corners, matched = 0.0, 0, 0
    rotation, translation = piece["matrix"]
    for prim in sec.primitives:
        drawn = by_uv.get(tuple(tuple(t) for t in prim.texcoords))
        if not drawn:
            continue        # culled, or a texel quad the frame does not draw
        points = {}
        # texcoords follow the STORED order, not `corners`: `--pair-by
        # corners` prints what the other pairing gives
        order = prim.indices if pair == "indices" else prim.corners
        for vi, texel in zip(order, prim.texcoords):
            v = sec.vertices[vi]
            points[tuple(texel)] = pose_project(rotation, translation, projection,
                                                (v.x, v.y, v.z))
        if None in points.values() or len(points) != 4:
            continue        # behind the eye, or a quad two corners of which share a texel
        best = min(sum(((points[uv][0] - xy[0]) ** 2 + (points[uv][1] - xy[1]) ** 2) ** 0.5
                       for uv, xy in zip(one["uv"], one["xy"])) for one in drawn)
        total += best
        corners += len(points)
        matched += 1
    return ((total / corners) if corners else None, matched)


class Figure(list):
    """One figure of a frame: its pieces, head first, each {"section",
    "matrix", "projection"}; `samples` are the frame's textured primitives."""

    samples: list = None

    @property
    def pieces(self) -> list:
        """The pieces as a plain list, head first: the figure itself."""
        return list(self)

    @property
    def order(self) -> list:
        return [p["section"] for p in self]

    @property
    def head(self):
        return self[0]["section"] if self else None

    @property
    def root(self):
        return self[1]["section"] if len(self) > 1 else None

    @property
    def family(self) -> str:
        return FAMILIES.get(self.root, "other")

    @property
    def sleeves(self):
        return sleeves_of(self.order)

    @property
    def armband(self):
        return armband_of(self.order)

    @property
    def replaces(self):
        """The arm section the figure's armband stands in for, or None."""
        return ARMBAND_REPLACES.get(self.armband)

    @property
    def depth(self) -> float:
        return figure_depth(self)

    @property
    def off_axis(self) -> float:
        return figure_off_axis(self)

    def pose(self) -> dict:
        """The pose as `work/kits-pose/` keeps it: the projection and each
        piece's rotation and translation."""
        return {"projection": self[0]["projection"],
                "pieces": [{"section": p["section"], "rotation": list(p["matrix"][0]),
                            "translation": list(p["matrix"][1])} for p in self]}

    def group(self, index) -> tuple:
        """(quads, fit) of `figure_group` over the frame's samples."""
        return figure_group(self, self.samples or [], index)

    def box(self, index):
        """The figure's screen box, grown by `POSE_MARGIN`; None if no
        vertex projects."""
        _group, fit = self.group(index)
        return fit["box"] if fit else None

    def sections(self, index, buffer=None, texture=None) -> dict:
        """Section -> what the GPU is told for it (`shading_of`), the zones
        its kit quads touch, its pixel error and matches, and with the frame
        buffer the mean distances of the game's pixels to the bare texel
        ("far") and to the modulated one ("far_shaded")."""
        group, fit = self.group(index)
        if group is None:
            return {}
        found = {p["section"]: section_samples(group, index, p["section"])
                 for p in self if p["section"] is not None}
        errors = {r["section"]: r for r in fit["rows"]}
        colours = (colour_confront(group, buffer, texture, found)
                   if buffer is not None and texture is not None else {})
        out = {}
        for section, samples in found.items():
            row = shading_of(samples)
            row["zones"] = sorted({z for one in samples for z in sample_zones(one)
                                   if kit_image_of(one)})
            row["error"] = errors[section]["error"]
            row["matched"] = errors[section]["matched"]
            c = colours.get(section)
            row["far"] = c["texel_far"] if c else None
            row["far_shaded"] = c["shaded_far"] if c else None
            out[section] = row
        return out

    def panel(self, index, pages: dict = None, width: int = UNIFORM_WIDTH,
              on_torso: bool = False) -> dict:
        """The back panel the figure samples: the cells (cell -> quads), the
        figure's own cell (`panel_cell`, the shared one taken away when
        *on_torso*: behind a player), its page, and with the uniform pages
        the number in it and that panel as `read_panels` reads it ("read":
        digits and unexplained pixels)."""
        group, _fit = self.group(index)
        group = group or []
        if on_torso and len(self) > 1:
            torso = piece_box(self[1], index)
            group = [one for one in group if torso is not None and all(
                torso[0] <= x <= torso[2] and torso[1] <= y <= torso[3] for x, y in one["xy"])]
        cells = panel_samples(group)
        out = {"cells": {cell: len(found) for cell, found in cells.items()}, "own": None,
               "page": None, "panel": None, "number": None, "read": None}
        if cells:
            cell = panel_cell(cells, on_torso)
            out["own"] = cell
            out["page"] = cells[cell][0]["page"][0]
            out["panel"] = (out["page"],) + cell[1:]
            words = (pages or {}).get("%d" % out["page"])
            if words is not None:
                shown = [one for one in read_panels(words, width) if one["cell"][1:] == cell[1:]]
                if shown:
                    out["read"] = shown[0]
                    out["number"] = shown[0]["number"]
        return out


class Frame:
    """One whole frame of a capture: its figures, the head of the GPU list
    they are drawn in, its primitives and its drawing offset."""

    def __init__(self, head: int, figures: list, samples: list, offset):
        self.head = head
        self.figures = figures
        self.samples = samples
        self.offset = offset
        for figure in figures:
            figure.samples = samples

    def focus(self, nth: int = 0, on_axis: bool = False):
        """The followed figure: the *nth* nearest (`replay_focus`), or with
        *on_axis* the *nth* nearest the camera's axis (`field_focus`)."""
        return (field_focus if on_axis else replay_focus)(self.figures, nth)


def capture_frames(capture) -> list:
    """The `Frame`s of a `pose_capture`, the pieces named one stop late."""
    if capture is None:
        return []
    out = []
    for frame in pose_frames(capture):
        pieces = matrix_pieces(frame["stops"], 1)
        for piece, stop in zip(pieces, frame["stops"]):
            piece["projection"] = stop["projection"]
        offset = capture["offsets"].get("%d" % frame["head"])
        out.append(Frame(frame["head"], replay_figures(pieces),
                         capture["lists"].get("%d" % frame["head"], []),
                         tuple(offset) if offset is not None else None))
    return out


def replay_figures(pieces, roots=ROOTS) -> list:
    """One frame's pieces cut into `Figure`s: each opens at a root and takes
    the piece before it, its head, up to the head of the next.  The last piece
    of the frame is the one the draw lag leaves unnamed, so the last figure is
    one piece short."""
    starts = [k for k, p in enumerate(pieces) if p["section"] in roots and k > 0]
    out = []
    for at, start in enumerate(starts):
        end = starts[at + 1] - 1 if at + 1 < len(starts) else len(pieces)
        out.append(Figure(pieces[start - 1:end]))
    return out


def figure_depth(figure) -> float:
    """The median z of a figure's translations: the view's depth of it."""
    zs = sorted(p["matrix"][1][2] for p in figure)
    return zs[len(zs) // 2]


def figure_off_axis(figure) -> float:
    """Pixels the root of *figure* lies off the screen's centre, across: the
    camera's axis."""
    root = figure[1] if len(figure) > 1 else figure[0]
    x, _y, z = root["matrix"][1]
    return abs(root["projection"]["H"] * x / z) if z > 0 else float("inf")


def replay_focus(figures, nth: int = 0):
    """The *nth* nearest figure by `figure_depth` (0, the one the replay as
    saved follows).  None if there is not that many."""
    ranked = sorted(figures, key=figure_depth)
    return ranked[nth] if nth < len(ranked) else None


def field_focus(figures, nth: int = 0):
    """The figure the camera follows behind a player: the *nth* nearest the
    camera's axis.  None if there is not that many."""
    ranked = sorted(figures, key=figure_off_axis)
    return ranked[nth] if nth < len(ranked) else None


def pose_change(one, other) -> int:
    """The largest difference, entry by entry, between two figures' matrices;
    None when they are not the same pieces."""
    if [p["section"] for p in one] != [p["section"] for p in other]:
        return None
    return max(abs(a - b) for p, q in zip(one, other)
               for a, b in zip(p["matrix"][0] + p["matrix"][1], q["matrix"][0] + q["matrix"][1]))


def sleeves_of(order) -> str:
    """"long" if a figure's sections hold a long sleeve, "short" if a short
    one, else None."""
    if any(s in LONG_SLEEVES for s in order):
        return "long"
    if any(s in SHORT_SLEEVES for s in order):
        return "short"
    return None


def armband_of(order):
    """The armband section a figure draws, or None."""
    return next((s for s in order if s in REPLAY_ARMBANDS), None)


def piece_box(piece, index):
    """The screen box of one piece's MODEL.BIN vertices through its matrix,
    grown by `TORSO_MARGIN`; None if the section has none."""
    sec = index["sections"].get((layout.MODEL, piece["section"]))
    points = [at for v in (sec.vertices if sec else [])
              for at in [pose_project(piece["matrix"][0], piece["matrix"][1],
                                      piece["projection"], (v.x, v.y, v.z))] if at is not None]
    if not points:
        return None
    return (min(p[0] for p in points) - TORSO_MARGIN, min(p[1] for p in points) - TORSO_MARGIN,
            max(p[0] for p in points) + TORSO_MARGIN, max(p[1] for p in points) + TORSO_MARGIN)


def figure_group(figure, samples, index):
    """The textured quads of a frame that fall inside the screen box of
    *figure*'s own vertices, each through its piece's matrix, grown by
    `POSE_MARGIN`; and each piece's mean pixel error there (`piece_error`)."""
    if figure is None:
        return None, None
    projection = figure[0]["projection"]
    points = []
    for piece in figure:
        sec = index["sections"].get((layout.MODEL, piece["section"]))
        for v in (sec.vertices if sec else []):
            at = pose_project(piece["matrix"][0], piece["matrix"][1], projection, (v.x, v.y, v.z))
            if at is not None:
                points.append(at)
    if not points:
        return None, None
    box = (min(p[0] for p in points) - POSE_MARGIN, min(p[1] for p in points) - POSE_MARGIN,
           max(p[0] for p in points) + POSE_MARGIN, max(p[1] for p in points) + POSE_MARGIN)
    group = [one for one in samples if len(one["uv"]) == 4 and all(
        box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])]
    rows = []
    for piece in figure:
        sec = index["sections"].get((layout.MODEL, piece["section"]))
        error, matched = (piece_error(piece, projection, sec, group) if sec else (None, 0))
        rows.append({"section": piece["section"], "error": error, "matched": matched})
    return group, {"box": box, "rows": rows}


def section_samples(group, index, section: int) -> list:
    """The primitives of a player group whose four texels are a primitive of
    MODEL.BIN section *section* on the disc."""
    sec = index["sections"].get((layout.MODEL, section))
    if sec is None:
        return []
    held = {tuple(tuple(t) for t in prim.texcoords) for prim in sec.primitives}
    return [one for one in group if tuple(tuple(t) for t in one["uv"]) in held]


def shading_of(samples) -> dict:
    """What the GPU is told to do with the texels of *samples*: how many are
    shaded per corner, how many raw (texture not modulated), the CLUTs and
    pages, and the range of the corner colours."""
    colours = [c for one in samples for c in (one.get("rgb") or [])]
    return {"n": len(samples),
            "shaded": sum(1 for one in samples if one["code"] & 16),
            "raw": sum(1 for one in samples if one["code"] & 1),
            "semi": sum(1 for one in samples if one["code"] & 2),
            "cluts": sorted({tuple(one["clut"]) for one in samples}),
            "pages": sorted({tuple(one["page"]) for one in samples}),
            "low": tuple(min(c[i] for c in colours) for i in range(3)) if colours else None,
            "high": tuple(max(c[i] for c in colours) for i in range(3)) if colours else None}


def triangle_pixels(xy, uv, rgb):
    """[(x, y, u, v, (r, g, b))] of the pixel centres inside one triangle, with
    texel and colour interpolated the way `core/raster.py` interpolates UV."""
    (x0, y0), (x1, y1), (x2, y2) = xy
    area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
    if area == 0:
        return []
    out = []
    for py in range(min(y0, y1, y2), max(y0, y1, y2) + 1):
        for px in range(min(x0, x1, x2), max(x0, x1, x2) + 1):
            sx, sy = px + 0.5, py + 0.5
            a = ((x1 - sx) * (y2 - sy) - (x2 - sx) * (y1 - sy)) / area
            b = ((x2 - sx) * (y0 - sy) - (x0 - sx) * (y2 - sy)) / area
            g = 1.0 - a - b
            if a < 0 or b < 0 or g < 0:
                continue
            u = a * uv[0][0] + b * uv[1][0] + g * uv[2][0]
            v = a * uv[0][1] + b * uv[1][1] + g * uv[2][1]
            colour = tuple(a * rgb[0][i] + b * rgb[1][i] + g * rgb[2][i] for i in range(3))
            out.append((px, py, int(u), int(v), colour))
    return out


def sample_pixels(one) -> list:
    """`triangle_pixels` of a quad as the GPU splits it, (0 1 2) and (1 2 3)."""
    rgb = one.get("rgb") or [(NEUTRAL,) * 3] * len(one["xy"])
    out = triangle_pixels(one["xy"][:3], one["uv"][:3], rgb[:3])
    if len(one["xy"]) == 4:
        out += triangle_pixels(one["xy"][1:], one["uv"][1:], rgb[1:])
    return out


def texel_colour(texture: dict, page, clut, u: int, v: int):
    """The 15-bit texel at (u, v) of an 8-bit page, through its CLUT, as five-
    bit (r, g, b); None if the capture did not keep that page or CLUT.  Odd
    texels lose bit 7 on the way through the PNG."""
    words = texture["pages"].get("%d,%d,%d" % (tuple(page) + (KIT_BITS,)))
    row = texture["cluts"].get("%d,%d" % tuple(clut))
    if words is None or row is None:
        return None
    half = words[v * TEXTURE_HALFWORDS + u // 2]
    index = (half >> (8 * (u & 1))) & 0xFF
    if u & 1:
        index &= 0x7F
    return row[index] if index < len(row) else None


def colour_confront(group, buffer, texture: dict, sections: dict) -> dict:
    """Section -> the game's drawn pixels against the texels they sample:
    the mean frame-buffer colour, the mean texel, the mean texel times the
    corner colour / 128, and the mean distance of the game's to each.  A pixel
    counts for the primitive of the group drawn last over it."""
    owners = {}
    for k, one in enumerate(group):
        for px, py, _u, _v, _c in sample_pixels(one):
            owners[(px, py)] = k
    x0, y0 = buffer["origin"]
    out = {}
    for section, samples in sections.items():
        rows = []
        for one in samples:
            if one["bits"] != KIT_BITS:
                continue        # only 8-bit pages are kept
            k = next(i for i, g in enumerate(group) if g is one)
            for px, py, u, v, colour in sample_pixels(one):
                if owners.get((px, py)) != k:
                    continue
                by, bx = py - y0, px - x0
                if not (0 <= by < len(buffer["rows"]) and 0 <= bx < len(buffer["rows"][0])):
                    continue
                texel = texel_colour(texture, one["page"], one["clut"], u, v)
                if texel is None:
                    continue
                game = buffer["rows"][by][bx]
                shaded = tuple(min(31, int(t * c / NEUTRAL)) for t, c in zip(texel, colour))
                rows.append((game, texel, shaded))
        if not rows:
            out[section] = None
            continue
        mean = lambda i: tuple(sum(r[i][c] for r in rows) / len(rows) for c in range(3))  # noqa: E731
        far = lambda i: sum(abs(r[0][c] - r[i][c]) for r in rows for c in range(3)) / (3.0 * len(rows))  # noqa: E731
        out[section] = {"pixels": len(rows), "game": mean(0), "texel": mean(1),
                        "shaded": mean(2), "texel_far": far(1), "shaded_far": far(2)}
    return out



# -- the figure drawn in the captured pose -----------------------------------

class _Picture:
    """What `raster.draw` reads of a looks Scene: parts, notes and a centre."""

    def __init__(self, parts, fit):
        self.parts = parts
        self.notes = {raster.FIT: fit}

    def centre(self):
        return tuple(sum(p[i] for p in self.notes[raster.FIT]) / 4.0 for i in range(3))


class _Part:
    """One quad for `raster.draw`: four points, four (u, v), a surface."""

    def __init__(self, points, uvs, surface):
        self.points, self.uvs, self.surface = points, uvs, surface


class _Surface:
    """One 256x256 texture page read through one CLUT, as RGBA bytes; a
    texel whose colour is 0 is transparent, as the GPU leaves it."""

    def __init__(self, texture: dict, page, clut):
        self.width = self.height = 256
        out = bytearray(256 * 256 * 4)
        for v in range(256):
            for u in range(256):
                texel = texel_colour(texture, page, clut, u, v)
                if texel is None or tuple(texel[:3]) == (0, 0, 0):
                    continue
                k = (v * 256 + u) * 4
                out[k:k + 4] = bytes((texel[0] << 3, texel[1] << 3, texel[2] << 3, 255))
        self.rgba = bytes(out)


def section_source(group, index, section: int):
    """(page, clut) the game draws *section* with in *group*: the commonest
    of the quads that carry its texels; None if none does."""
    tally = {}
    for one in section_samples(group, index, section):
        key = (tuple(one["page"]), tuple(one["clut"]))
        tally[key] = tally.get(key, 0) + 1
    return max(tally, key=tally.get) if tally else None


def pose_picture(figure, index, texture: dict, box, only=None) -> tuple:
    """(width, height, rgba) of *figure* drawn by `core/raster` in its
    captured pose: every MODEL.BIN section of it through its piece's matrix
    and the projection, on the screen pixels of *box* (x0, y0, x1, y1) --
    the frame buffer the capture kept -- so the two pictures line up pixel
    for pixel.  Each section is textured from the page and CLUT the game's
    own quads of it sample, when the capture kept them; else it is drawn
    untextured.  *only* draws one section."""
    group, _fit = figure_group(figure, figure.samples or [], index)
    surfaces, parts = {}, []
    for piece in figure:
        if piece["section"] is None or (only is not None and piece["section"] != only):
            continue
        sec = index["sections"].get((layout.MODEL, piece["section"]))
        if sec is None:
            continue
        source = section_source(group or [], index, piece["section"])
        surface = None
        if source is not None and texture is not None \
                and texel_colour(texture, source[0], source[1], 0, 0) is not None:
            surface = surfaces.get(source) or surfaces.setdefault(
                source, _Surface(texture, source[0], source[1]))
        rotation, translation = piece["matrix"]
        for prim in sec.primitives:
            points = []
            for vi in prim.indices:
                v = sec.vertices[vi]
                r = rotation
                cz = (r[6] * v.x + r[7] * v.y + r[8] * v.z) / 4096.0 + translation[2]
                at = pose_project(rotation, translation, figure[0]["projection"],
                                  (v.x, v.y, v.z))
                if at is None:
                    break
                # raster.draw's orthographic view: screen x is minus model x,
                # screen y minus model y, and the nearest has the largest z
                points.append((-at[0], -at[1], -cz))
            if len(points) != len(prim.indices):
                continue
            parts.append(_Part(points, [(u / 256.0, v / 256.0) for u, v in prim.texcoords],
                               surface))
    x0, y0, x1, y1 = box
    w, h = int(x1 - x0) + 1, int(y1 - y0) + 1
    if not parts:
        return w, h, bytes(w * h * 4)
    # a square target whose fit leaves scale 1: the box's span is its drawn size
    span = max(w, h)
    side = int(math.ceil(span / (1.0 - 2 * raster.MARGIN))) + 2
    fit = [(-x0, -y0, 0.0), (-(x0 + span), -y0, 0.0), (-x0, -(y0 + span), 0.0),
           (-(x0 + span), -(y0 + span), 0.0)]
    drawn = raster.draw(_Picture(parts, fit), 0.0, 0.0, side, side, ((0, 1, 2), (1, 2, 3)))
    # raster.draw puts screen pixel x at side/2 + (x + 0.5 - span/2) * scale
    scale = side * (1.0 - 2 * raster.MARGIN) / span
    origin = side / 2.0 - span * scale / 2.0
    out = bytearray(w * h * 4)
    for y in range(h):
        for x in range(w):
            sx, sy = int(origin + (x + 0.5) * scale), int(origin + (y + 0.5) * scale)
            if 0 <= sx < side and 0 <= sy < side:
                k = (sy * side + sx) * 4
                out[(y * w + x) * 4:(y * w + x) * 4 + 4] = drawn.rgba[k:k + 4]
    return w, h, bytes(out)


# -- the back panel ----------------------------------------------------------

def panel_cells() -> list:
    """(figure, x, y) of every 20x24 cell under the map: the two torso gaps
    start the two rows, and the rows run on to the right in steps of 20."""
    out = []
    for gap in GAPS:
        if not gap.name.startswith("torso"):
            continue
        if gap.figure == 0:
            for row in range(2):
                for k in range(5):
                    out.append((0, gap.x + k * gap.w, gap.y + row * gap.h))
        else:
            out.append((1, gap.x, gap.y))
    return out


def panel_samples(group) -> dict:
    """Panel cell -> the primitives of *group* whose four texels lie in it:
    which back panel of the page the figure's torso shows."""
    out = {}
    for one in group:
        if kit_image_of(one) != "uniform":
            continue
        for figure, cx, cy in panel_cells():
            if all(cx <= u < cx + PANEL_W and cy <= v < cy + PANEL_H for u, v in one["uv"]):
                out.setdefault((figure, cx, cy), []).append(one)
    return out


def panel_cell(cells: dict, outfield: bool):
    """The panel cell a figure's back shows, of the cells its torso samples:
    the one with the most quads -- or, for an outfield player, the one left
    once `REPLAY_SHARED_CELL` is taken away, when exactly one is."""
    own = [c for c in cells if c != REPLAY_SHARED_CELL] if outfield else []
    return own[0] if len(own) == 1 else max(cells, key=lambda c: len(cells[c]))


def pixel_index(words, width: int, x: int, y: int) -> int:
    """The 8-bit index of pixel (x, y) of an 8 bpp page held as 15-bit
    halfwords, *width* halfwords a row; an odd pixel keeps seven bits."""
    word = words[y * width + x // 2] & 0x7FFF
    return word & 0xFF if x % 2 == 0 else word >> 8


def back_indices(words, width: int, rect) -> list:
    """The rows of indices of one rectangle of an 8 bpp page."""
    x0, y0, w, h = rect
    return [[pixel_index(words, width, x0 + x, y0 + y) for x in range(w)] for y in range(h)]


def glyphs(words, width: int) -> tuple:
    """The ten digit glyphs of the numbers zone as rows of 7-bit indices, and
    the zone's background index (its commonest value)."""
    zone = next(z for z in ZONES if z.name == "numbers 0-9")
    rows = back_indices(words, width, (zone.x, zone.y, zone.w, zone.h))
    tally = {}
    for row in rows:
        for v in row:
            tally[v & 0x7F] = tally.get(v & 0x7F, 0) + 1
    ground = max(tally, key=tally.get)
    out = [[[v & 0x7F for v in row[d * GLYPH_W:(d + 1) * GLYPH_W]] for row in rows]
           for d in range(zone.w // GLYPH_W)]
    return out, ground


def read_panel(words, width: int, cell, back, glyph_set, ground) -> dict:
    """One panel against the rule: the figure's shirt back underneath, digits
    of the numbers zone on top.  Says which digit sits where, how many pixels
    neither explains."""
    _figure, cx, cy = cell
    panel = [[v & 0x7F for v in row]
             for row in back_indices(words, width, (cx, cy, PANEL_W, PANEL_H))]
    found = []
    for gy in range(PANEL_H - len(glyph_set[0]) + 1):
        for gx in range(PANEL_W - GLYPH_W + 1):
            for digit, glyph in enumerate(glyph_set):
                ink = [(x, y) for y, row in enumerate(glyph) for x, v in enumerate(row)
                       if v != ground]
                if ink and all(panel[gy + y][gx + x] == glyph[y][x] for x, y in ink):
                    found.append((gx, gy, digit, len(ink)))
    # a narrow glyph (the 1) also fits inside wider ones: keep the placements
    # whose ink no other placement covers more of
    found.sort(key=lambda f: -f[3])
    kept, covered = [], set()
    for gx, gy, digit, n in found:
        ink = {(gx + x, gy + y) for y, row in enumerate(glyph_set[digit])
               for x, v in enumerate(row) if v != ground}
        if ink & covered:
            continue
        kept.append((gx, gy, digit))
        covered |= ink
    kept.sort()
    unexplained = sum(1 for y in range(PANEL_H) for x in range(PANEL_W)
                      if (x, y) not in covered and panel[y][x] != back[y][x])
    return {"cell": cell, "digits": kept, "unexplained": unexplained,
            "number": int("".join(str(d) for _x, _y, d in kept)) if kept else None}


def read_panels(words, width: int, shift: int = 0) -> list:
    """Every back panel of a match page, read against the rule; *shift*
    moves every cell that many rows (negative is up), which only a plant does."""
    glyph_set, ground = glyphs(words, width)
    out = []
    for figure, x, y in panel_cells():
        cell = (figure, x, y + shift)
        sx, sy = BACK_COPY[cell[0]]
        back = [[v & 0x7F for v in row]
                for row in back_indices(words, width, (sx, sy, PANEL_W, PANEL_H))]
        out.append(read_panel(words, width, cell, back, glyph_set, ground))
    return out


def model_index(image_path: str) -> dict:
    """{"sections": {(MODEL.BIN, i): Section}} of the Japanese disc at
    *image_path*, read through the looks disc guard (`core.figure`): what
    `figure_group`, `piece_box` and `section_samples` look sections up in."""
    import section

    from .figure import read_geometry

    data = read_geometry(image_path)[layout.MODEL]
    return {"sections": {(layout.MODEL, i): sec for i, sec in
                         enumerate(section.scan(data, layout.MODEL_GEOMETRY_START).sections)}}


def field_number(pages: dict, panel, width: int, shift: int = 0):
    """The number in *panel* (page x, cell x, cell y) of the uniform pages
    read off the emulator, *width* halfwords a row; *shift* moves every cell
    that many rows, which only a plant does.  None if the page was not read."""
    if panel is None or "%d" % panel[0] not in pages:
        return None
    for one in read_panels(pages["%d" % panel[0]], width, shift):
        if (one["cell"][1], one["cell"][2] - shift) == tuple(panel[1:]):
            return one["number"]
    return None


def field_panels(rows: list) -> dict:
    """Page x -> the cells every followed outfield figure of that page samples;
    a figure's panel is the cell left once the shared one is taken away, or
    the shared one when nothing is left (its owner).  Sets each row's
    "panel"."""
    shared = {}
    for r in rows:
        if r.get("follows") and r.get("cells") and r["root"] != 13:
            held = set(r["cells"])
            shared[r["page"]] = held if r["page"] not in shared else shared[r["page"]] & held
    for r in rows:
        r["panel"] = None
        if not r.get("cells"):
            continue
        own = sorted(set(r["cells"]) - shared.get(r["page"], set())) or sorted(r["cells"])
        if len(own) == 1:
            r["panel"] = (r["page"],) + tuple(int(v) for v in own[0].split(",")[1:])
    return shared


def figure_tag(hits, cluts):
    """(tag, set) of the kit whose player palette sits at one of *cluts*, of
    the hits the capture found; (None, None) if none does."""
    for tag, index, at, flat, shared in hits or []:
        for kit_set, record in PLAYER_PALETTE.items():
            if index == record and any(tuple(a) in cluts for a in at):
                return tag, kit_set
    return None, None


# -- the walk ----------------------------------------------------------------

def field_row(capture: dict, index, nth: int = 0) -> dict:
    """What one focus of the walk shows: the followed figure of the last
    frame (the *nth* nearest the axis), its depth and the next one's, its
    root, head, sleeves and armband, and the panel cells its torso samples."""
    frames = capture_frames(capture)
    if not frames:
        return {"figures": 0, "focus": None, "order": [], "depth": None, "off": None,
                "next": None, "head": None, "root": None, "sleeves": None, "armband": None,
                "still": None, "cells": {}, "panel": None, "figure_cell": None, "whole": 0}
    last = frames[-1]
    ranked = sorted(last.figures, key=figure_off_axis)
    focus = last.focus(nth, on_axis=True)
    order = focus.order if focus is not None else []
    row = {"figures": len(ranked), "focus": focus, "order": order, "whole": len(frames),
           "depth": figure_depth(focus) if focus is not None else None,
           "off": figure_off_axis(focus) if focus is not None else None,
           "next": figure_off_axis(ranked[nth + 1]) if len(ranked) > nth + 1 else None,
           "next_depth": figure_depth(ranked[nth + 1]) if len(ranked) > nth + 1 else None}
    row["head"] = order[0] if order else None
    row["root"] = order[1] if len(order) > 1 else None
    row["sleeves"] = sleeves_of(order)
    row["armband"] = armband_of(order)
    before = frames[-2].focus(nth, on_axis=True) if len(frames) >= 2 else None
    row["still"] = pose_change(before, focus) if before is not None and focus else None
    group, _fit = figure_group(focus, last.samples, index)
    torso = piece_box(focus[1], index) if focus is not None and len(focus) > 1 else None
    on_torso = [one for one in (group or []) if torso is not None and all(
        torso[0] <= x <= torso[2] and torso[1] <= y <= torso[3] for x, y in one["xy"])]
    cells = panel_samples(on_torso)
    row["cells"] = {"%d,%d,%d" % cell: len(found) for cell, found in cells.items()}
    row["page"] = next((found[0]["page"][0] for found in cells.values()), None)
    row["panel"] = None
    return row


class Walk:
    """The table of a walk: one row per tap, the panels set, and with the
    uniform record's width the number of each."""

    def __init__(self, capture: Capture, rows: list, shared: dict):
        self.capture = capture
        self.slot = capture.slot
        self.button = capture.button
        self.rows = rows
        self.shared = shared

    @classmethod
    def load(cls, path: str, index, width: int = UNIFORM_WIDTH, nth: int = 0,
             shift: int = 0) -> "Walk":
        """Read a `replay-field-*-capture.json` into its table; *nth* and
        *shift* are the plant's (the next figure off the axis, every panel a
        row off)."""
        return cls.of(Capture.load(path), index, width, nth, shift)

    @classmethod
    def of(cls, capture: Capture, index, width: int = UNIFORM_WIDTH, nth: int = 0,
           shift: int = 0) -> "Walk":
        if capture.kind != KIND_WALK:
            raise ReplayError("%s is not a walk capture" % (capture.path or "the capture"))
        rows = []
        for focus in capture.data["foci"]:
            if focus.get("refused"):
                rows.append({"k": focus["k"], "end": "refused", "root": None,
                             "moves": focus["moves"], "refused": focus["refused"]})
                continue
            row = field_row(focus["capture"], index, nth)
            row.update(k=focus["k"], moves=focus["moves"], frames=focus["frames"],
                       follows=bool(focus["followed"]) and focus["k"] > 0)
            if not focus["followed"] and focus["k"] > 1:
                row["end"] = "ball"
            rows.append(row)
        shared = field_panels(rows)
        for row in rows:
            if not row.get("refused"):
                row["number"] = (field_number(capture.data["pages"], row["panel"], width, shift)
                                 if width is not None else None)
        return cls(capture, rows, shared)


# -- the judges --------------------------------------------------------------

def judge(report: dict, expect: dict, plant_root: int = None) -> list:
    """Failures of a close capture against its expectation: the followed
    figure opens at the expected root (*plant_root* in its place, for the
    plant) with the expected head, draws the armband and not the arm it
    replaces, holds one still pose, turned its back, shows the expected panel
    and number there, and every capture stayed under the replay's idle."""
    out = []
    focus = report["focus"]
    order = [p["section"] for p in focus] if focus is not None else []
    root = plant_root if plant_root is not None else expect["root"]
    if focus is None:
        out.append("no %s figure in the frame" % ("second" if plant_root is not None
                                                 else "followed"))
    elif len(order) < 2 or order[1] != root:
        out.append("the followed figure opens at %s, not at section %d"
                   % (order[1] if len(order) > 1 else None, root))
    if focus is not None and order[0] != expect["head"]:
        out.append("the followed figure's head is section %s, not %d" % (order[0], expect["head"]))
    if focus is not None and expect["armband"] is not None and expect["armband"] not in order:
        out.append("the followed figure does not draw section %d" % expect["armband"])
    if focus is not None and expect["armband"] is None and armband_of(order) is not None:
        out.append("the followed figure draws armband %d, none expected" % armband_of(order))
    if expect["replaced"] is not None and expect["replaced"] in order:
        out.append("the followed figure draws section %d beside the armband" % expect["replaced"])
    if expect.get("sleeves") and sleeves_of(order) != expect["sleeves"]:
        out.append("the followed figure's sleeves are %s, not %s"
                   % (sleeves_of(order), expect["sleeves"]))
    if report["still"] is None or report["still"] > REPLAY_STILL:
        out.append("the pose changed by %s between two frames, over %d"
                   % (report["still"], REPLAY_STILL))
    if report["turned"] != "back":
        out.append("the back was not reached: %s" % report["turned"])
    if report["panel"] != expect["panel"]:
        out.append("the back samples panel %s, not %s" % (report["panel"], expect["panel"]))
    if report["number"] != expect["number"]:
        out.append("the panel holds %s, not %d" % (report["number"], expect["number"]))
    out += ["panel %s: %s" % (report["panel"], line) for line in report["panel_failures"]]
    idle = report["idle"]
    for what in ("front_frames", "back_frames"):
        if idle is None or report[what] >= idle:
            out.append("%s %d, not under the replay's idle %s" % (what, report[what], idle))
    return out


def judge_walk(rows: list, expect: dict, idle) -> list:
    """Failures of a walk's table against its expectation: every focus that
    follows a player has it on the camera's axis, the next figure
    `REPLAY_FOCUS_MARGIN` apart, under `REPLAY_FOLLOW_DEPTH`; the camera came
    back to the ball; the outfield armband is the expected one, on the player
    wearing the expected number; the figure the replay opens on is the
    goalkeeper with his armband; the walk follows the expected outfield
    players and goalkeepers and no other figure; every capture holds one
    still pose over its last two frames; and every capture stayed under the
    idle."""
    out = []
    followed = [r for r in rows if r.get("follows")]
    if not followed:
        out.append("no tap moved the camera to a player")
    for r in followed:
        if r["depth"] is None or r["depth"] >= REPLAY_FOLLOW_DEPTH:
            out.append("focus %d: the followed figure lies at depth %s, not under %d"
                       % (r["k"], r["depth"], REPLAY_FOLLOW_DEPTH))
        if r["off"] is None or r["off"] > REPLAY_FOLLOW_OFF:
            out.append("focus %d: the followed figure lies %s px off the axis, over %.0f"
                       % (r["k"], r["off"], REPLAY_FOLLOW_OFF))
        if r["off"] is not None and r["next"] is not None \
                and r["next"] - r["off"] < REPLAY_FOCUS_MARGIN[0] \
                and abs(r["next_depth"] - r["depth"]) < REPLAY_FOCUS_MARGIN[1]:
            out.append("focus %d: the next figure lies %.1f px farther off the axis and %.0f "
                       "apart in depth, under the margin %.0f px or %d"
                       % ((r["k"], r["next"] - r["off"], abs(r["next_depth"] - r["depth"]))
                          + REPLAY_FOCUS_MARGIN))
    if not rows or rows[-1].get("end") != "ball":
        out.append("the camera did not come back to the ball: %s"
                   % (rows[-1].get("end") if rows else "no focus"))
    captain = expect["captain"]
    banded = [r for r in followed if r["armband"] in OUTFIELD_ARMBANDS]
    if len(banded) != 1:
        out.append("%d focus(es) draw an outfield armband, not 1" % len(banded))
    for r in banded:
        if r["armband"] != captain["armband"]:
            out.append("focus %d draws armband %d, not %d"
                       % (r["k"], r["armband"], captain["armband"]))
        if r["number"] != captain["number"]:
            out.append("focus %d, the outfield captain, holds number %s, not %d"
                       % (r["k"], r["number"], captain["number"]))
    players = expect.get("players")
    if players:
        outfield = sum(r["root"] == 2 for r in followed)
        keepers = sum(r["root"] == 13 for r in followed)
        others = len(followed) - outfield - keepers
        if (outfield, keepers, others) != (players["outfield"], players["keepers"], 0):
            out.append("the walk follows %d outfield player(s), %d goalkeeper(s) and %d other "
                       "figure(s), not %d, %d and 0"
                       % (outfield, keepers, others, players["outfield"], players["keepers"]))
    keeper = expect["keeper"]
    opening = next((r for r in rows if r["k"] == keeper["k"]), None)
    if opening is None or opening["root"] != keeper["root"] \
            or opening["armband"] != keeper["armband"]:
        out.append("focus %d opens at %s with armband %s, not family %d with %d"
                   % (keeper["k"], opening and opening["root"], opening and opening["armband"],
                      keeper["root"], keeper["armband"]))
    for r in rows:
        if r.get("frames") is not None and (r.get("still") is None or r["still"] > REPLAY_STILL):
            out.append("focus %d: the figure's matrices differ by %s between the last two "
                       "frames, not within %d" % (r["k"], r.get("still"), REPLAY_STILL))
        if r.get("frames") is not None and (idle is None or r["frames"] >= idle):
            out.append("focus %d: %d frame(s) from the last tap, not under the replay's idle %s"
                       % (r["k"], r["frames"], idle))
    return out


# -- the head ----------------------------------------------------------------

HEAD_CLUT_STEP = layout.HAIR_MATRIX_KIND_STEP // 2
"""CLUT x per column of a skin record: 16 entries (32 bytes, two per entry),
the window `skin.grid` calls a column."""

HEAD_SKINS = len(layout.SKIN_PALETTES)
"""The skin records, VRAM rows `layout.CLUT_ROW_FIRST` onwards, one per value
of `skin_colour`."""

HEAD_HAIRS = layout.HAIR_MATRIX_KINDS
"""Columns `layout.HAIR_COLUMN` onwards: one per value of `hair_colour`."""

HEAD_BEARDS = 7
"""Columns `layout.BEARD_COLUMN` onwards: the seven values of `beard_colour`
the LOOKS SET reaches (`layout.BEARD_COLUMN`'s docstring)."""


def head_samples(figure, samples, index) -> list:
    """The primitives of *figure*'s head section, of the frame's *samples*,
    that lie inside the head piece's own screen box (`piece_box`): the box of
    the whole figure takes in a neighbour's head (slot 10, focus 8)."""
    if figure is None or not figure:
        return []
    group, _fit = figure_group(figure, samples, index)
    box = piece_box(figure[0], index)
    if group is None or box is None:
        return []
    return [one for one in section_samples(group, index, figure.head)
            if all(box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])]


def head_styles(section: int) -> tuple:
    """(the HAIR letters whose style draws *section*, whether it is the twin
    beard F and G draw instead): `assembly.HAIR_MAP` and `FACE_TWINS`."""
    import assembly  # noqa: E402  (tools/looks)
    import looks  # noqa: E402  (tools/looks)
    twins = {twin: base for base, twin in assembly.FACE_TWINS[assembly.HEAD_FIGURE].items()}
    base = twins.get(section, section)
    letters = sorted({looks.HAIR_STYLES[value][0]
                      for value, (drawn, _bands) in enumerate(assembly.HAIR_MAP)
                      if drawn == base})
    return tuple(letters), section in twins


def head_reading(section, cluts) -> dict:
    """What a head's CLUTs say by the LOOKS SET rule (KITS-REPLAYS-9-10 item
    (a)): the row is the skin, column `layout.HAIR_COLUMN` + n the hair colour
    n, column `layout.BEARD_COLUMN` + n the beard colour n; and the section the
    style (`head_styles`).  A CLUT off the skin records or in another column
    is `stray`; two skins, two hairs or two beards are kept as read."""
    import looks  # noqa: E402  (tools/looks)
    skins, hairs, beards, stray = set(), set(), set(), []
    for clut in cluts:
        x, y = clut
        row, column = y - layout.CLUT_ROW_FIRST, x // HEAD_CLUT_STEP
        if x % HEAD_CLUT_STEP or not 0 <= row < HEAD_SKINS:
            stray.append(tuple(clut))
            continue
        skins.add(row)
        if layout.HAIR_COLUMN <= column < layout.HAIR_COLUMN + HEAD_HAIRS:
            hairs.add(column - layout.HAIR_COLUMN)
        elif layout.BEARD_COLUMN <= column < layout.BEARD_COLUMN + HEAD_BEARDS:
            beards.add(column - layout.BEARD_COLUMN)
        else:
            stray.append(tuple(clut))
    styles, twin = head_styles(section) if section is not None else ((), False)
    letter = lambda values: [looks.LETTERS[v] for v in sorted(values)]  # noqa: E731
    return {"section": section, "styles": list(styles), "twin": twin,
            "cluts": sorted(tuple(c) for c in cluts), "skin": letter(skins),
            "hair": letter(hairs), "beard": letter(beards), "stray": sorted(stray)}


def head_expected(values: dict) -> dict:
    """The head a player record says the game draws: the section of his HAIR
    style (`assembly.HAIR_MAP`), its twin when his beard is F or G
    (`FACE_TWINS`, from `FACE_TWIN_FROM`), and his skin, hair colour and beard
    colour as letters."""
    import assembly  # noqa: E402  (tools/looks)
    import looks  # noqa: E402  (tools/looks)
    section = assembly.HAIR_MAP[values["hair_style"]][0]
    if values["beard_style"] >= assembly.FACE_TWIN_FROM:
        section = assembly.FACE_TWINS[assembly.HEAD_FIGURE][section]
    return {"section": section, "skin": looks.LETTERS[values["skin_colour"]],
            "hair": looks.LETTERS[values["hair_colour"]],
            "beard": looks.LETTERS[values["beard_colour"]]}


def head_judge(reading: dict, expected: dict) -> list:
    """What of *reading* the record *expected* does not say: the section, the
    one skin, the one hair colour, and the beard colour when the head shows
    one (a beardless view samples no beard column: Bokšić, slots 9 and 10);
    and any stray CLUT."""
    out = []
    if reading["section"] != expected["section"]:
        out.append("head section %s, not %d" % (reading["section"], expected["section"]))
    if reading["skin"] != [expected["skin"]]:
        out.append("skin %s, not %s" % ("/".join(reading["skin"]) or "none", expected["skin"]))
    if reading["hair"] != [expected["hair"]]:
        out.append("hair colour %s, not %s"
                   % ("/".join(reading["hair"]) or "none", expected["hair"]))
    if reading["beard"] and reading["beard"] != [expected["beard"]]:
        out.append("beard colour %s, not %s" % ("/".join(reading["beard"]), expected["beard"]))
    if reading["stray"]:
        out.append("CLUT(s) %s fit no skin, hair or beard column" % reading["stray"])
    return out

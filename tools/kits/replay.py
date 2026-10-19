#!/usr/bin/env python3
"""Command line of the replay reader: a kept replay capture read with no
emulator (PLAN-KITS-REPLAY section 2.3).  It prints; `core/replay.py` reads.

Every reader takes `--json`, which prints one object with
`"schema": "kits-replay/1"` and fixed keys -- the contract with an agent: a key
that does not apply is null, never missing.  Without it the output is short
and for a person.

Usage:
    python tools/kits/replay.py describe <capture.json> [--json]
    python tools/kits/replay.py figures <capture.json> [--side front|back] [--frame N] [--json]
    python tools/kits/replay.py figure <capture.json> [--on-axis | --nearest] [--nth N]
                                       [--section S] [--json]
    python tools/kits/replay.py panel <capture.json> [--on-axis | --nearest] [--nth N] [--json]
    python tools/kits/replay.py walk <replay-field-*-capture.json> [--json]
    python tools/kits/replay.py head <capture.json> [--player all|RECORD]
                                     [--plant-hair-column] [--drawn] [--json]
    python tools/kits/replay.py show <capture.json> --png out.png [--section S | --box]
    python tools/kits/replay.py confront <capture.json> [--section S] [--json]
    python tools/kits/replay.py confront <capture.json> --tab [--player] [--out DIR] [--json]
    python tools/kits/replay.py capture --slot S [--focus K] [--turn R1|L1] [--walk L2|R2]
                                        [--out DIR] [--cue CUE]   # boots the emulator
    python tools/kits/replay.py check [<folder>] [--plant-hair-column]  # the kits_replay gate

The geometry comes from `WE2002_LOOKS_IMAGE`, the Japanese data track.
`check` reads `WE2002_KITS_REPLAY_DIR` when no folder is given, and exits 77
without either.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

KITS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, KITS_DIR)

from core import replay  # noqa: E402

SCHEMA = "kits-replay/1"
"""The schema of every `--json` object this command prints."""
IMAGE_VARIABLE = "WE2002_LOOKS_IMAGE"
REPLAY_DIR_VARIABLE = "WE2002_KITS_REPLAY_DIR"
SKIP = 77
CAPTURES = {
    "replay-9.json": "125ff69bf1fedc188a12ee933ec431c6d9fbd4f79c7488966c08304b87551b1d",
    "replay-9-3.json": "f34717387cc1f706ad9921c65fc5473fa9cd7ab53cecdfa938c2de680bddb5a8",
    "replay-10.json": "8dde786284f499c52ef58480a2dea963fa982259f320a7ad50bcf3229009811a",
    "replay-10-2.json": "e9b785b2a6cf80029293fbbd20fc873eeeeebe919d6e08cc11ef03e0928d2a7b",
    "replay-10-3.json": "d362901327da8d5efba910f6f456cbb357fb19eb53807751751a401c1fe6ace8",
    "replay-field-9-capture.json":
        "efb8e1e4b1b7e62411faf5224eb80265843af43a5e3290bc39c9ba74d9426971",
    "replay-field-10-capture.json":
        "57e8f52326f6e9f03503223bd38874a58314b6754f5d0825cae082956341d8f4",
}
"""The captures `check` reads, with the sha256 each was kept with (KRP-TASK-01
Log): five up close (`oracle.py --replay SLOT [--focus K]`) and the two walks
(`--replay-field SLOT`).  A capture that differs is another capture, and what
the judges assert of it means nothing."""


# -- reading -----------------------------------------------------------------

def sha256_of(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def digest_problem(path: str, want: str):
    """None if *path* holds the capture *want* names, else why not."""
    if not os.path.isfile(path):
        return "no capture at %s" % path
    got = sha256_of(path)
    if got != want:
        return "%s has sha256 %s, not the %s it was kept with" % (path, got, want)
    return None


def _index():
    image = os.environ.get(IMAGE_VARIABLE)
    if not image:
        raise SystemExit("replay.py: set %s to the Japanese data track (.bin): the figure's "
                         "geometry comes from it" % IMAGE_VARIABLE)
    return replay.model_index(image)


def _pair(value):
    return list(value) if value is not None else None


def _capture_doc(capture) -> dict:
    return {"path": capture.path, "sha256": sha256_of(capture.path), "kind": capture.kind,
            "slot": capture.slot, "focus": capture.focus, "button": capture.button,
            "taps": capture.taps}


def figure_doc(figure) -> dict:
    """The fixed keys of one figure."""
    if figure is None:
        return None
    return {"order": figure.order, "head": figure.head, "root": figure.root,
            "family": figure.family, "sleeves": figure.sleeves, "armband": figure.armband,
            "replaces": figure.replaces, "depth": figure.depth,
            "off_axis": figure.off_axis if figure.off_axis != float("inf") else None}


def followed(capture, side: str, on_axis: bool, nth: int):
    """(frames of *side*, the followed figure of the last one)."""
    frames = capture.frames(side)
    return frames, (frames[-1].focus(nth, on_axis) if frames else None)


def default_axis(capture, args) -> bool:
    """The pick `oracle.py --replay` makes: the nearest in the replay as saved,
    the one on the camera's axis once L2 has moved it to a player."""
    if args.on_axis:
        return True
    if args.nearest:
        return False
    return bool(capture.focus)


def panel_of(capture, index, on_axis: bool, nth: int) -> dict:
    """The panel the followed figure's back shows, read as `oracle.py
    --replay` reads it: the turned capture of the replay as saved; the first
    capture, then the turned one, behind a player, inside his torso's box."""
    behind = bool(capture.focus)
    sides = ("front", "back") if behind else ("back",)
    for side in sides:
        _frames, figure = followed(capture, side, on_axis, nth)
        if figure is None:
            continue
        found = figure.panel(index, capture.data["pages"], on_torso=behind)
        if found["cells"]:
            break
    else:
        return {"side": None, "cells": {}, "panel": None, "number": None, "read": None}
    read = found["read"]
    return {"side": side,
            "cells": {"%d,%d,%d" % cell: n for cell, n in sorted(found["cells"].items())},
            "panel": _pair(found["panel"]), "number": found["number"],
            "read": None if read is None else {
                "digits": [list(d) for d in read["digits"]],
                "unexplained": read["unexplained"]}}


def section_doc(figure, index, section: int, capture) -> dict:
    found = figure.sections(index, capture.data.get("buffer"), capture.data.get("texture"))
    row = found.get(section)
    if row is None:
        return None
    return {"section": section, "n": row["n"], "shaded": row["shaded"], "raw": row["raw"],
            "semi": row["semi"], "cluts": [list(c) for c in row["cluts"]],
            "pages": [list(p) for p in row["pages"]], "zones": row["zones"],
            "error": row["error"], "matched": row["matched"], "far": row["far"],
            "far_shaded": row["far_shaded"]}


def figure_report(capture, index, on_axis: bool, nth: int = 0, section: int = None) -> dict:
    frames, figure = followed(capture, "front", on_axis, nth)
    still = None
    if len(frames) >= 2 and figure is not None:
        before = frames[-2].focus(nth, on_axis)
        still = replay.pose_change(before, figure) if before is not None else None
    return {"schema": SCHEMA, "capture": _capture_doc(capture),
            "pick": "on_axis" if on_axis else "nearest", "nth": nth, "frames": len(frames),
            "figure": figure_doc(figure), "still": still,
            "box": _pair(figure.box(index)) if figure is not None else None,
            "panel": panel_of(capture, index, on_axis, nth),
            "turned": capture.data["turned"], "front_frames": capture.data["front_frames"],
            "back_frames": capture.data["back_frames"],
            "section": section_doc(figure, index, section, capture)
            if figure is not None and section is not None else None}


def walk_report(capture, index) -> dict:
    walk = replay.Walk.of(capture, index)
    rows = []
    for r in walk.rows:
        rows.append({key: r.get(key) for key in (
            "k", "follows", "end", "refused", "head", "root", "sleeves", "armband", "number",
            "still", "depth", "off", "next", "next_depth", "frames", "figures", "whole")})
        rows[-1]["panel"] = _pair(r.get("panel"))
    followed_rows = [r for r in walk.rows if r.get("follows")]
    return {"schema": SCHEMA, "capture": _capture_doc(capture), "foci": len(rows),
            "follows": {"outfield": sum(r["root"] == 2 for r in followed_rows),
                        "goalkeeper": sum(r["root"] == 13 for r in followed_rows),
                        "other": sum(r["root"] not in (2, 13) for r in followed_rows)},
            "shared": {"%d" % page: sorted(cells) for page, cells in sorted(walk.shared.items())},
            "rows": rows}


def describe_report(capture) -> dict:
    doc = {"schema": SCHEMA, "capture": _capture_doc(capture), "front": None, "back": None,
           "turned": None, "rotate": None, "front_frames": None, "back_frames": None,
           "turn_frames": None, "foci": None}
    if capture.kind == replay.KIND_WALK:
        doc["foci"] = len(capture.data["foci"])
        return doc
    for side in ("front", "back"):
        frames = capture.frames(side)
        doc[side] = {"frames": len(frames),
                     "figures": [len(f.figures) for f in frames]} if capture.data[side] else None
    for key in ("turned", "rotate", "front_frames", "back_frames", "turn_frames"):
        doc[key] = capture.data[key]
    return doc


def figures_report(capture, side: str, frame: int) -> dict:
    frames = capture.frames(side)
    one = frames[frame] if frames and -len(frames) <= frame < len(frames) else None
    return {"schema": SCHEMA, "capture": _capture_doc(capture), "side": side,
            "frame": frame, "frames": len(frames),
            "head": one.head if one else None,
            "offset": _pair(one.offset) if one else None,
            "figures": [figure_doc(f) for f in sorted(one.figures, key=replay.figure_depth)]
            if one else []}


# -- show and confront -------------------------------------------------------

SHOW_SCALE = 4
"""Each frame-buffer pixel is a SHOW_SCALE x SHOW_SCALE block in `show`'s PNG,
as `oracle.save_buffer` writes the crop."""
SHOW_GAP = 4
"""Pixels of black between the game's half and the drawn one, before scaling."""
BOX_COLOUR = (255, 255, 0)
"""The outline `show --box` draws round a piece's screen box."""


def write_png(path: str, width: int, height: int, rgb: bytes) -> None:
    """An RGB PNG, stdlib only."""
    import struct
    import zlib

    raw = bytearray()
    for y in range(height):
        raw.append(0)
        raw += rgb[y * width * 3:(y + 1) * width * 3]

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

    with open(path, "wb") as fh:
        fh.write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height,
                                                                     8, 2, 0, 0, 0))
                 + chunk(b"IDAT", zlib.compress(bytes(raw))) + chunk(b"IEND", b""))


def show_picture(capture, index, section: int = None, box: bool = False) -> dict:
    """The game's frame-buffer crop under the followed figure (left) beside
    the figure `core/raster` draws in the captured pose on the same pixels
    (right): {"width", "height", "rgb", "drawn", "box"}, at SHOW_SCALE."""
    figure = followed(capture, "front", default_axis_of(capture), 0)[1]
    buffer = capture.data.get("buffer")
    if figure is None or buffer is None:
        raise SystemExit("replay.py: %s has no followed figure or no frame buffer under it"
                         % capture.path)
    rows = buffer["rows"]
    h, w = len(rows), len(rows[0])
    x0, y0 = buffer["origin"]
    dw, dh, rgba = replay.pose_picture(figure, index, capture.data.get("texture"),
                                       (x0, y0, x0 + w - 1, y0 + h - 1), section)
    full_w = 2 * w + SHOW_GAP
    pixels = [[(0, 0, 0)] * full_w for _ in range(h)]
    drawn = 0
    for y in range(h):
        for x in range(w):
            pixels[y][x] = tuple(v << 3 for v in rows[y][x][:3])
            k = (y * dw + x) * 4
            if rgba[k + 3]:
                pixels[y][w + SHOW_GAP + x] = tuple(rgba[k:k + 3])
                drawn += 1
    outline = None
    if box:
        target = next((p for p in figure if p["section"] == section), None) \
            if section is not None else (figure[1] if len(figure) > 1 else None)
        found = replay.piece_box(target, index) if target is not None else None
        if found is not None:
            outline = [int(round(found[0])) - x0, int(round(found[1])) - y0,
                       int(round(found[2])) - x0, int(round(found[3])) - y0]
            for half in (0, w + SHOW_GAP):
                for x in range(outline[0], outline[2] + 1):
                    for y in (outline[1], outline[3]):
                        if 0 <= x < w and 0 <= y < h:
                            pixels[y][half + x] = BOX_COLOUR
                for y in range(outline[1], outline[3] + 1):
                    for x in (outline[0], outline[2]):
                        if 0 <= x < w and 0 <= y < h:
                            pixels[y][half + x] = BOX_COLOUR
    out = bytearray()
    for y in range(h * SHOW_SCALE):
        row = pixels[y // SHOW_SCALE]
        for x in range(full_w * SHOW_SCALE):
            out += bytes(row[x // SHOW_SCALE])
    return {"width": full_w * SHOW_SCALE, "height": h * SHOW_SCALE, "rgb": bytes(out),
            "drawn": drawn, "box": outline}


def default_axis_of(capture) -> bool:
    """`default_axis` with no flags: the nearest as saved, the axis behind a player."""
    return bool(capture.focus)


def confront_report(capture, index, section: int = None) -> dict:
    """Per section of the followed figure, the game's pixels against the bare
    texel and the modulated one (`colour_confront`)."""
    figure = followed(capture, "front", default_axis_of(capture), 0)[1]
    group, _fit = figure.group(index) if figure is not None else (None, None)
    rows = []
    buffer, texture = capture.data.get("buffer"), capture.data.get("texture")
    if group is not None and buffer is not None and texture is not None:
        found = {p["section"]: replay.section_samples(group, index, p["section"])
                 for p in figure if p["section"] is not None
                 and (section is None or p["section"] == section)}
        for sec, c in replay.colour_confront(group, buffer, texture, found).items():
            rows.append({"section": sec, "pixels": c["pixels"] if c else 0,
                         "game": list(c["game"]) if c else None,
                         "texel": list(c["texel"]) if c else None,
                         "shaded": list(c["shaded"]) if c else None,
                         "far": c["texel_far"] if c else None,
                         "far_shaded": c["shaded_far"] if c else None})
    return {"schema": SCHEMA, "capture": _capture_doc(capture),
            "figure": figure_doc(figure), "section": section, "sections": rows}


# -- the tab against the game: confront --tab --------------------------------

TAB_SIDES = ("front", "back")
"""The two views `confront --tab` compares, each against the same view of
the game."""


def game_side(side: str, focus: int) -> str:
    """The capture of a close capture ("front": the first, "back": the turned
    one) that holds the game's *side* ("front" or "back") of its figure.  The
    replay as saved faces the goalkeeper, so its first capture is his front;
    behind a player (*focus*) the first capture is his back, and his front is
    the turned one (PLAN-KITS-REPLAY section 2.4, CORR-K3D-034)."""
    if not focus:
        return side
    return "back" if side == "front" else "front"


def _kits_confront():
    """tools/kits/confront.py, by path (the looks one has the same name)."""
    import importlib.util

    if "kits_confront" not in sys.modules:
        spec = importlib.util.spec_from_file_location("kits_confront",
                                                      os.path.join(KITS_DIR, "confront.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    return sys.modules["kits_confront"]


def game_pixels(capture, index, which: str, on_axis: bool):
    """The game's pixels (eight bits a channel) under the quads of the
    followed figure of capture *which*, read off its frame buffer; None when
    the capture kept no frame buffer for it."""
    buffer = capture.data.get("buffer" if which == "front" else "back_buffer")
    frames = capture.frames(which)
    figure = frames[-1].focus(0, on_axis) if frames else None
    if buffer is None or figure is None:
        return None
    group, _fit = figure.group(index)
    owners = set()
    for one in group or []:
        for px, py, _u, _v, _c in replay.sample_pixels(one):
            owners.add((px, py))
    x0, y0 = buffer["origin"]
    rows = buffer["rows"]
    return [tuple(v << 3 for v in rows[py - y0][px - x0][:3]) for (px, py) in sorted(owners)
            if 0 <= py - y0 < len(rows) and 0 <= px - x0 < len(rows[0])]


def tab_args(capture, index, player: bool = False) -> dict:
    """What the tab is asked to draw for the capture's figure: the kit (the
    one whose player palette the figure samples, behind a player), figure 0
    or 1, the armband, the long sleeves and the number of the measured
    expectation (`oracle.REPLAY_EXPECT`); with *player*, the looks tuple of the
    player the panel names (`HEAD_TEAMS`, `HEAD_EXPECT`), for his head."""
    O = _kits_oracle()
    frames, figure = followed(capture, "front", bool(capture.focus), 0)
    tag, kit_set = capture.data.get("tag"), capture.data.get("set")
    if capture.focus and figure is not None:
        group, _fit = figure.group(index)
        cluts = {tuple(one["clut"]) for one in group or []
                 if replay.kit_image_of(one) == "uniform"}
        tag, kit_set = replay.figure_tag(capture.data.get("hits"), cluts)
    tag = "41" if tag is None else tag
    keeper = figure is not None and figure.root in (13, 56)
    expect = O.REPLAY_EXPECT.get((capture.slot, capture.focus), {})
    asked = {"tag": tag, "set": kit_set, "figure": 1 if keeper else 0,
             "armband": expect.get("armband", replay.KEEPER_ARMBAND) is not None,
             "long_sleeves": not keeper and capture.slot in O.REPLAY_LONG_SLOTS,
             "number": expect.get("number"), "player": None}
    if player:
        panel = expect.get("panel")
        asked["player"] = HEAD_EXPECT.get((HEAD_TEAMS.get(panel[0]) if panel else None,
                                           expect.get("number")))
    return asked


def confront_tab(capture, index, out_dir: str, player: bool = False) -> dict:
    """The tab's figure against the game's, front with front and back with
    back (`game_side`), by colour histogram: the intersection over all the
    game's colours and over the colours the tab draws.  It records; it asserts
    no limit."""
    import subprocess

    O = _kits_oracle()
    confront = _kits_confront()
    image = os.environ[IMAGE_VARIABLE]
    asked = tab_args(capture, index, player)
    python = confront.VENV_PYTHON
    if not os.path.isfile(python):
        raise SystemExit("replay.py: no venv python at %s (make looks-venv)" % python)
    os.makedirs(out_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(capture.path))[0] + ("-player" if player else "")
    sides = {}
    for side in TAB_SIDES:
        which = game_side(side, capture.focus)
        shown = game_pixels(capture, index, which, bool(capture.focus))
        out = os.path.join(out_dir, "%s-tab-%s.png" % (stem, side))
        args = [python, confront.APP, image, "--tag", asked["tag"], "--tab", "3d",
                "--figure", str(asked["figure"]), "--yaw", "%g" % O.REPLAY_TAB[side],
                "--export-3d", out]
        args += ["--kit-set", str(asked["set"])] if asked["set"] is not None else []
        args += ["--armband"] if asked["armband"] else []
        args += ["--long-sleeves"] if asked["long_sleeves"] else []
        args += ["--number", str(asked["number"])] if asked["number"] is not None else []
        args += ["--player-looks", asked["player"]] if asked["player"] else []
        if shown is None:
            sides[side] = {"game_capture": which, "game_pixels": 0, "intersection": None,
                           "intersection_tab_colours": None, "tab_png": None,
                           "yaw": O.REPLAY_TAB[side]}
            continue
        done = subprocess.run(args, env=confront.environment(), capture_output=True,
                              text=True, timeout=confront.TIMEOUT)
        if done.returncode or not os.path.isfile(out):
            raise SystemExit("replay.py: app.py exited %s: %s"
                             % (done.returncode, done.stderr[-300:]))
        game = confront.histogram(shown)
        ours = confront.histogram(confront.figure_pixels(confront.read_rgb(out)))
        sides[side] = {"game_capture": which, "game_pixels": len(shown),
                       "intersection": confront.intersection(game, ours),
                       "intersection_tab_colours": confront.intersection(
                           confront.restrict(game, set(ours)), ours),
                       "tab_png": out, "yaw": O.REPLAY_TAB[side]}
    return {"schema": SCHEMA, "capture": _capture_doc(capture), "tab": asked,
            "sides": sides}


# -- the capture (the only reader that boots the emulator) -------------------

DRIVE_VARIABLE = "WE2002_LOOKS_DRIVE_IMAGE"
"""The English cue the replay states were saved on."""
CAPTURE_DIR = os.path.join("work", "kits-replay")
"""Where `capture` writes by default: not `work/kits-oracle/`, whose captures
`check` holds to their digests."""
NOT_TURNED = "not asked"
"""`turned` of a capture taken without `--turn`."""


def replay_arrive(game, slot: int, focus: int, label: str) -> int:
    """Load *slot* and tap `REPLAY_FIELD_BUTTONS[0]` *focus* times, each a
    `press` that has to move the screen, then let the camera land
    (`REPLAY_FIELD_SETTLE`).  The frame counter at the last tap: the replay's
    idle starts again there."""
    O = _kits_oracle()
    O.load_slot(game, slot, label)
    for _tap in range(focus):
        game.press(O.REPLAY_FIELD_BUTTONS[0])
    tapped = O.frame_now(game)
    if focus:
        game.step(O.REPLAY_FIELD_SETTLE)
    return tapped


def frame_buffer(game, capture: dict, fit):
    """The frame buffer under a followed figure's screen box *fit* (from
    `figure_group`) of *capture*, read off VRAM at five bits a channel:
    {"origin", "offset", "rows"}; None without a figure or a drawing offset.
    The drawing offset rides in the one-node list submitted before each
    ordering table, not in the table the figure is in: the last one set."""
    import oracle as looks_oracle  # tools/looks

    offsets = [capture["offsets"].get("%d" % e["head"]) for e in capture["events"]
               if e["kind"] == "submit"]
    offset = next((o for o in reversed(offsets) if o is not None), None)
    if fit is None or offset is None:
        return None
    box = tuple(int(round(v)) for v in fit["box"])
    rows = looks_oracle.vram_region(game, offset[0] + box[0], offset[1] + box[1],
                                    box[2] - box[0] + 1, box[3] - box[1] + 1)
    return {"origin": box[:2], "offset": offset,
            "rows": [[looks_oracle._five_bits(p) for p in row] for row in rows]}


def replay_capture(game, maps, bodies: dict, index, slot: int, rotate: str,
                   focus: int = 0) -> dict:
    """Everything `--replay` reads from the paused replay: the first capture
    (`pose_capture`) with the frame buffer under the followed figure and the
    texture pages and CLUTs it samples; the kit pages; then, from the state
    reloaded, taps of *rotate* until the torso has turned `REPLAY_BACK`, and
    the turned capture.  With *focus* the camera is first moved K taps of L2
    to a player (`replay_arrive`), which it follows from behind: the first
    capture is then his back and the turned one his front.  Each run counts
    the frames it spends since its last tap, and the turn keeps in `tap_gaps`
    the frames between one tap of *rotate* and the next, the first from the
    reload's last L2 tap: each is an idle the replay has to outlast
    (CORR-KRP-008).  With *rotate* None there is
    no turn: the first capture alone, `turned` `NOT_TURNED`."""
    O = _kits_oracle()
    import oracle as looks_oracle  # tools/looks

    label = "replay-%d" % slot + ("-%d" % focus if focus else "")
    choose = O.replay_chooser(focus)
    submits = O.REPLAY_FIELD_SUBMITS if focus else O.REPLAY_SUBMITS
    start = replay_arrive(game, slot, focus, label)
    front = O.pose_capture(game, maps, submits)
    front_frames = O.frame_now(game) - start
    game.step(O.REPLAY_SETTLE)
    hits, tag, kit_set, page_x = O._edit_kit(game, bodies, label)
    frames = O.replay_frames(front, choose=choose)
    head = frames[-1]["head"] if frames else None
    samples = front["lists"].get("%d" % head, []) if head is not None else []
    figure, fit = O.figure_group(frames[-1]["focus"] if frames else None, samples, index)
    texture = {"pages": {}, "cluts": {}}
    buffer = frame_buffer(game, front, fit if figure else None)
    if buffer is not None:
        for page in sorted({tuple(one["page"]) for one in figure if one["bits"] == O.KIT_BITS}):
            rows = looks_oracle.vram_region(game, page[0], page[1], O.TEXTURE_HALFWORDS, 256)
            texture["pages"]["%d,%d,%d" % (page + (O.KIT_BITS,))] = [
                (p[0] >> 3) | (p[1] >> 3) << 5 | (p[2] >> 3) << 10 for row in rows for p in row]
        for clut in sorted({tuple(one["clut"]) for one in figure}):
            row = looks_oracle.vram_region(game, clut[0], clut[1], 256, 1)[0]
            texture["cluts"]["%d,%d" % clut] = [looks_oracle._five_bits(p) for p in row]
    pages = {}
    for x in sorted({one["page"][0] for one in samples if O.is_figure(one)}):
        pages["%d" % x] = O._edit_page(game, x)
    game.capture(label + "-front")
    if rotate is None:
        return {"focus": focus, "front": front, "back": None, "front_frames": front_frames,
                "back_frames": None, "turn_frames": None, "rotate": None, "yaws": [],
                "depths": [], "turned": NOT_TURNED, "hits": hits, "tag": tag, "set": kit_set,
                "page_x": page_x, "pages": pages, "buffer": buffer, "back_buffer": None,
                "texture": texture}
    start = replay_arrive(game, slot, focus, label + "-turn")
    yaws, depths, gaps, turned, tapped = [], [], [], None, start
    root = frames[-1]["focus"][1]["section"] if frames and frames[-1]["focus"] else None
    projection = frames[-1]["focus"][0]["projection"] if frames and frames[-1]["focus"] else None
    for _tap in range(O.REPLAY_ROTATE_MOST):
        try:
            now = O.frame_now(game)
            gaps.append(now - tapped)
            tapped = now
            game.press(rotate)
        except looks_oracle.NotArrived as exc:
            turned = "refused: %s" % exc
            break
        # the followed figure's own family: past the goal line the camera
        # sees another goalkeeper nearer than a cut-off frame's own one
        # behind a player the camera turns about him and keeps him on its
        # axis: the figure on the axis, within the depth it follows at
        followed = None
        for count in O.REPLAY_YAW_STOPS:
            stops = O.matrix_stops(game, maps, count, partial=True)
            pieces = O.matrix_pieces(stops, 1)
            for piece in pieces:
                # these stops do not read the GTE: the first capture's projection
                piece.setdefault("projection", projection)
            figures = O.replay_figures(pieces)
            if focus:
                followed = O.field_focus([f for f in figures
                                        if O.figure_depth(f) < O.REPLAY_FOLLOW_DEPTH
                                        and O.figure_off_axis(f) <= O.REPLAY_FOLLOW_OFF])
            else:
                followed = O.replay_focus([f for f in figures if f[1]["section"] == root])
            if followed is not None:
                break
        if followed is None:
            turned = "no figure in the stops after the tap"
            break
        yaws.append(O.piece_yaw(followed[1]["matrix"]))
        depths.append([followed[1]["section"], O.figure_depth(followed)])
        front_yaw = O.piece_yaw(frames[-1]["focus"][1]["matrix"]) if frames else yaws[0]
        if abs((yaws[-1] - front_yaw + 180.0) % 360.0 - 180.0) >= O.REPLAY_BACK:
            turned = "back"
            break
    back = O.pose_capture(game, maps, submits) if turned == "back" else None
    turn_frames = O.frame_now(game) - start
    back_frames = O.frame_now(game) - tapped
    back_samples, back_buffer = [], None
    if back is not None:
        back_frames_list = O.replay_frames(back, choose=choose)
        if back_frames_list:
            back_samples = back["lists"].get("%d" % back_frames_list[-1]["head"], [])
            back_figure, back_fit = O.figure_group(back_frames_list[-1]["focus"], back_samples,
                                                   index)
            back_buffer = frame_buffer(game, back, back_fit if back_figure else None)
        for x in sorted({one["page"][0] for one in back_samples if O.is_figure(one)}):
            pages.setdefault("%d" % x, O._edit_page(game, x))
    game.capture(label + "-back")
    return {"focus": focus, "front": front, "back": back, "front_frames": front_frames,
            "back_frames": back_frames, "turn_frames": turn_frames, "tap_gaps": gaps, "rotate": rotate, "yaws": yaws, "depths": depths, "turned": turned,
            "hits": hits, "tag": tag, "set": kit_set, "page_x": page_x, "pages": pages,
            "buffer": buffer, "back_buffer": back_buffer, "texture": texture}


def replay_field_capture(game, maps, slot: int, button: str = None) -> dict:
    """`--replay-field`'s reading of the emulator: for k taps of *button*,
    from 0 until a tap does not move the screen or the camera is back on the
    ball after a player, the state reloaded, the k taps (each a `press` that
    has to move the screen), `REPLAY_FIELD_SETTLE` frames, and a
    `pose_capture`; the uniform pages each focus samples, read once."""
    O = _kits_oracle()
    import oracle as looks_oracle  # tools/looks

    button = button or O.REPLAY_FIELD_BUTTONS[0]
    foci, pages = [], {}
    for k in range(O.REPLAY_FIELD_MOST + 1):
        label = "replay-field-%d-%d" % (slot, k)
        O.load_slot(game, slot, label)
        moves, refused = [], None
        for _tap in range(k):
            before = game.capture()
            try:
                after = game.press(button)
            except looks_oracle.NotArrived as exc:
                refused = str(exc)
                break
            moves.append(before.difference(after, looks_oracle.pixels(before, None)))
        if refused is not None:
            foci.append({"k": k, "moves": moves, "refused": refused})
            break
        tapped = O.frame_now(game)
        game.step(O.REPLAY_FIELD_SETTLE)
        game.capture(label)
        capture = O.pose_capture(game, maps, O.REPLAY_FIELD_SUBMITS)
        frames = O.frame_now(game) - tapped
        for x in sorted({one["page"][0] for v in capture["lists"].values() for one in v
                         if O.is_figure(one)}):
            if "%d" % x not in pages:
                pages["%d" % x] = O._edit_page(game, x)
        foci.append({"k": k, "moves": moves, "refused": None, "frames": frames,
                     "capture": capture})
        frames_now = O.replay_frames(capture)
        axis = O.field_focus(frames_now[-1]["figures"]) if frames_now else None
        followed = (axis is not None and O.figure_depth(axis) < O.REPLAY_FOLLOW_DEPTH
                    and O.figure_off_axis(axis) <= O.REPLAY_FOLLOW_OFF)
        if k > 1 and not followed and any(f.get("followed") for f in foci[:-1]):
            foci[-1]["followed"] = False
            break
        foci[-1]["followed"] = followed
    return {"slot": slot, "button": button, "foci": foci, "pages": pages}



def v1(data: dict, kind: str, slot: int, focus, button, taps) -> dict:
    """*data* with the fixed keys of schema v1 (`core.replay.Capture`)."""
    data.update(schema=replay.SCHEMA, kind=kind, slot=slot, focus=focus, button=button,
                taps=taps)
    return data


def sequences(data: dict) -> list:
    """(name, frames, judged) of every sequence of a capture.  A judged one
    counts from its last tap to the end of its capture -- the replay's idle,
    which every tap starts again, has to outlast it; the turn counts from the
    reload across all its taps, and is printed, not judged; its largest gap
    between two taps (`tap_gaps`, CORR-KRP-008) is judged as "turn gap".  A
    capture taken before `tap_gaps` existed has no gap to judge, and says so
    by leaving the sequence out."""
    if data.get("kind") == replay.KIND_WALK:
        return [("focus %d" % f["k"], f["frames"], True) for f in data["foci"]
                if not f.get("refused")]
    out = [("front", data["front_frames"], True)]
    if data.get("back_frames") is not None:
        out += [("turn", data["turn_frames"], False)]
        if data.get("tap_gaps"):
            out += [("turn gap", max(data["tap_gaps"]), True)]
        out += [("back", data["back_frames"], True)]
    return out


def timeout_failures(data: dict, idle) -> list:
    """The judged sequences that reached the replay's timeout *idle* (or any,
    when the slot has no measured timeout): past it the replay has left."""
    return ["%s: %s frame(s), not under the timeout %s" % (name, n, idle)
            for name, n, judged in sequences(data)
            if judged and (idle is None or n is None or n >= idle)]


def run_capture(slot: int, focus: int = 0, turn: str = None, walk: str = None,
                out: str = CAPTURE_DIR, cue: str = None) -> tuple:
    """Boot the fork on *cue* and capture: the walk (`walk`, L2 or R2) or the
    figure *focus* taps of L2 lead to, turned by *turn* when asked.  Refuses
    a plugged-in controller before booting (CORR-K3D-031).  Returns (path,
    data); the capture is written in schema v1."""
    import fork  # tools/pes2

    O = _kits_oracle()
    import oracle as looks_oracle  # tools/looks

    fork.refuse_joysticks()
    image = os.environ[IMAGE_VARIABLE]
    maps = looks_oracle.model_maps(image)
    with looks_oracle.Oracle(cue) as game:
        if walk:
            data = v1(replay_field_capture(game, maps, slot, walk), replay.KIND_WALK, slot,
                      None, walk, None)
            data["taps"] = max((f["k"] for f in data["foci"]), default=0)
        else:
            data = v1(replay_capture(game, maps, O.read_kits(image), O.model_index(image),
                                     slot, turn, focus),
                      replay.KIND_CLOSE, slot, focus, replay.WALK_BUTTON if focus else None,
                      focus)
    name = ("replay-field-%d-%s" % (slot, walk) if walk
            else "replay-%d" % slot + ("-%d" % focus if focus else "")
            + ("-%s" % turn if turn else ""))
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, name + ".json")
    with open(path, "w") as fh:
        json.dump(data, fh)
    return path, data


# -- the gate ----------------------------------------------------------------

# -- head: the head of each player against his disc record ---------------------

HEAD_TEAMS = {576: 41, 640: 22}
"""Uniform page -> team index (`core/teams.py`): Brazil wears the page at x
576 and Croatia the one at 640 in both replays (KITS-REPLAYS-9-10 item 7).
Constant per slot, never read from the capture (K1); the 22 of 22 below are
what confirms it, since the other way round no number lands on its player."""

HEAD_EXPECT = {
    (41, 1): "A-I1-B-A-B", (41, 2): "C-I1-A-A-A", (41, 3): "C-I1-A-A-A",
    (41, 4): "D-I1-A-A-A", (41, 5): "A-A1-B-A-A", (41, 6): "C-K1-B-A-A",
    (41, 7): "C-I1-A-A-B", (41, 9): "A-I1-A-A-A", (41, 10): "C-I1-A-A-A",
    (41, 11): "D-I3-A-A-A", (41, 16): "C-I1-A-B-A",
    (22, 1): "A-A1-B-A-A", (22, 2): "A-L3-B-A-A", (22, 3): "A-A1-B-A-A",
    (22, 4): "A-I2-B-A-B", (22, 5): "A-G1-B-A-B", (22, 7): "A-I1-B-A-B",
    (22, 8): "A-L3-H-F-C", (22, 10): "A-A1-B-A-A", (22, 11): "A-L3-H-A-A",
    (22, 14): "A-A1-B-A-A", (22, 20): "A-L3-B-A-B",
}
"""(team, shirt number) -> the five looks the disc records for him, as the
corpus tuple spells them (`looks.TUPLE_ORDER`): the 22 of the two replays.
The gate judges the captured heads against these constants (K1), and checks
that the disc still says them; `head --player all` is the measurement that
reads the disc instead (PLAN-KITS-REPLAY section 3.1)."""

HEAD_PLAYERS = 22
"""Players on the pitch in both replays: 20 outfield and 2 goalkeepers."""

SQUAD_NUMBERS_SIZE = 16
"""Bytes of one team's shirt numbers at `OFS_SQUAD_NUMBERS_NATIONAL`: 23 of
five bits, six to a little-endian word (`SquadNumbers` of Types.hpp)."""

SQUAD_PER_WORD = 6
SQUAD_BITS = 5
SQUAD_SIZE = 23
"""The `SquadNumbers` packing, and the 23 slots of a national team: player
record `team * 23 + slot` of `/SELECT.BIN` (`Database::Load`, PLAYERS_NC on)."""

RAW_SECTOR, SECTOR_HEADER, SECTOR_DATA = 2352, 24, 2048
"""A raw MODE2 sector: where its 2048 data bytes start and how many."""


def squad_numbers(image_path: str, team: int) -> list:
    """The shirt numbers of national *team*'s 23 slots, as `Database::Load`
    reads `OFS_SQUAD_NUMBERS_NATIONAL` (stored minus one) from the raw image."""
    import ofs_map  # noqa: E402  (tools/pes2: Offsets.hpp read, never typed here)

    offset = dict(ofs_map.read_offsets())["OFS_SQUAD_NUMBERS_NATIONAL"] \
        + team * SQUAD_NUMBERS_SIZE
    inside = offset % RAW_SECTOR
    if not SECTOR_HEADER <= inside <= SECTOR_HEADER + SECTOR_DATA - SQUAD_NUMBERS_SIZE:
        raise replay.ReplayError("team %d's shirt numbers cross a sector boundary" % team)
    with open(image_path, "rb") as fh:
        fh.seek(offset)
        raw = fh.read(SQUAD_NUMBERS_SIZE)
    words = [int.from_bytes(raw[i:i + 4], "little") for i in range(0, SQUAD_NUMBERS_SIZE, 4)]
    return [((words[s // SQUAD_PER_WORD] >> (SQUAD_BITS * (s % SQUAD_PER_WORD)))
             & ((1 << SQUAD_BITS) - 1)) + 1 for s in range(SQUAD_SIZE)]


def disc_records(image_path: str) -> list:
    """The 1,449 player records of `/SELECT.BIN`, decoded (`looks.decode`)."""
    import iso  # noqa: E402  (tools/pes2)
    import layout  # noqa: E402  (tools/looks)
    import looks  # noqa: E402  (tools/looks)

    data = iso.Image(image_path).read_file(layout.SELECT)
    return [looks.decode(raw) for raw in looks.records(data)]


def player_of(image_path: str, team: int, number: int):
    """(record index, slot) of the player of *team* wearing *number*, or
    (None, None)."""
    numbers = squad_numbers(image_path, team)
    if numbers.count(number) != 1:
        return None, None
    slot = numbers.index(number)
    return team * SQUAD_SIZE + slot, slot


def head_rows(capture, index) -> list:
    """One row per figure the capture follows: its k (None up close), the
    page and number of its back panel, and the head read off its CLUTs.  The
    walk's focus 0 shows no panel: it is the goalkeeper the replay opens on,
    whose panel the close capture of the same slot reads
    (`oracle.REPLAY_EXPECT[(slot, 0)]`, K1)."""
    rows = []
    if capture.kind == replay.KIND_WALK:
        walk = replay.Walk.of(capture, index)
        foci = {f["k"]: f for f in capture.data["foci"]}
        opening = _kits_oracle().REPLAY_EXPECT.get((capture.slot, 0), {})
        for r in walk.rows:
            if r.get("refused") or r.get("end") == "ball" or r.get("focus") is None:
                continue
            last = replay.capture_frames(foci[r["k"]]["capture"])[-1]
            panel, number = r.get("panel"), r.get("number")
            if panel is None and r["root"] == 13 and opening.get("panel"):
                panel, number = opening["panel"], opening.get("number")
            rows.append({"k": r["k"], "figure": r["focus"], "samples": last.samples,
                         "page": panel[0] if panel else None, "number": number})
    else:
        on_axis = bool(capture.focus)
        frames, figure = followed(capture, "front", on_axis, 0)
        p = panel_of(capture, index, on_axis, 0)
        rows.append({"k": None, "figure": figure, "samples": frames[-1].samples if frames else [],
                     "page": p["panel"][0] if p["panel"] else None, "number": p["number"]})
    return rows


def shifted_cluts(cluts, plant: bool) -> list:
    """The CLUTs as read, or with *plant* one column to the right: the plant
    that takes every hair colour to the next (K2)."""
    return [(x + replay.HEAD_CLUT_STEP, y) if plant else (x, y) for x, y in cluts]


HEAD_KIT = "41"
"""The kit `head --drawn` dresses the figure in: any kit would do, the head
textures come from DAT2D.BIN (`figure._model_banks`)."""


def drawn_head(figure, samples, index, tuple_text: str, geometry, kit) -> dict:
    """The head the window draws for *tuple_text* (`api.figure`, in the pose
    it opens with) against the game's, primitive by primitive: for every
    primitive of the game's head section the capture samples, the CLUT the
    game used and the one we draw it with.  `differ` lists the ones that do
    not agree; a drawn section other than the game's is `section`."""
    from core import api, figure as kits_figure

    drawn = api.figure(kit, 1, 0, frame=api.FIGURE_POSE, geometry=geometry, player=tuple_text)
    sec = index["sections"].get((kits_figure.layout.MODEL, figure.head))
    by_uv = {tuple(tuple(t) for t in p.texcoords): at for at, p in enumerate(sec.primitives)}
    game = {}
    for one in replay.head_samples(figure, samples, index):
        game[by_uv[tuple(tuple(t) for t in one["uv"])]] = tuple(one["clut"])
    section = drawn.notes["player head"]["section"]
    ours = {}
    for part in drawn.parts:
        if part.file == kits_figure.layout.MODEL and part.section == section:
            row, column = kits_figure.skin.grid(part.clut)
            ours[part.primitive] = (column * replay.HEAD_CLUT_STEP, row)
    differ = sorted([at, list(game[at]), list(ours[at]) if at in ours else None]
                    for at in game if section != figure.head or game[at] != ours.get(at))
    return {"section": section, "game_section": figure.head, "primitives": len(game),
            "differ": differ}


def head_report(capture, index, player=None, image_path=None, plant: bool = False,
                drawn: bool = False) -> dict:
    """`head`: per followed figure, its section, CLUTs and the head they read;
    with *player* "all" the record each locates by page and number, or with a
    record index that one record, decoded and judged; and the summary of how
    many distinct players match."""
    import looks  # noqa: E402  (tools/looks)

    records = disc_records(image_path) if player is not None else None
    geometry = kit = None
    if drawn:
        from core import api

        geometry = api.read_geometry(image_path)
        kit = api.open_source(image_path).kit(HEAD_KIT)
    out = []
    for row in head_rows(capture, index):
        samples = replay.head_samples(row["figure"], row["samples"], index)
        cluts = shifted_cluts(sorted({tuple(one["clut"]) for one in samples}), plant)
        reading = replay.head_reading(row["figure"].head if row["figure"] else None, cluts)
        team = HEAD_TEAMS.get(row["page"])
        doc = {"k": row["k"], "page": row["page"], "team": team, "number": row["number"],
               "primitives": len(samples), "reading": reading, "record": None, "slot": None,
               "disc": None, "expected": None, "failures": None, "drawn": None}
        if player is not None:
            if player == "all":
                record, slot = (player_of(image_path, team, row["number"])
                                if team is not None and row["number"] is not None
                                else (None, None))
            else:
                record, slot = int(player), None
            if record is not None:
                values = records[record]
                expected = replay.head_expected(values)
                doc.update(record=record, slot=slot, expected=expected,
                           disc=looks.format_tuple({k: values[k] for k in looks.TUPLE_ORDER}),
                           failures=replay.head_judge(reading, expected))
            else:
                doc["failures"] = ["no record for page %s number %s"
                                   % (row["page"], row["number"])]
        want = HEAD_EXPECT.get((team, row["number"]))
        if drawn and want is not None and row["figure"] is not None:
            doc["drawn"] = drawn_head(row["figure"], row["samples"], index, want, geometry, kit)
            doc["drawn"]["tuple"] = want
        out.append(doc)
    players = {}
    for doc in out:
        if doc["failures"] is not None:
            key = (doc["team"], doc["number"]) if doc["record"] is not None else ("k", doc["k"])
            players[key] = players.get(key, True) and not doc["failures"]
    drawn_rows = [doc for doc in out if doc["drawn"] is not None]
    return {"schema": SCHEMA, "capture": _capture_doc(capture), "player": player,
            "plant": plant, "rows": out, "players": len(players),
            "match": sum(players.values()) if players else None,
            "drawn": len(drawn_rows) if drawn else None,
            "drawn_agree": sum(not d["drawn"]["differ"] for d in drawn_rows) if drawn else None}


def head_constant_failures(image_path: str) -> list:
    """Where `HEAD_EXPECT` and the disc disagree: a constant the disc no
    longer says, or a player the disc no longer holds."""
    import looks  # noqa: E402  (tools/looks)

    records = disc_records(image_path)
    out = []
    for (team, number), want in sorted(HEAD_EXPECT.items()):
        record, _slot = player_of(image_path, team, number)
        if record is None:
            out.append("team %d has no single player wearing %d" % (team, number))
            continue
        have = looks.format_tuple({k: records[record][k] for k in looks.TUPLE_ORDER})
        if have != want:
            out.append("team %d number %d: the disc records %s, HEAD_EXPECT says %s"
                       % (team, number, have, want))
    return out


def head_gate_failures(capture, index, plant: bool = False) -> list:
    """The gate's head judgement: every followed figure whose page and number
    name a player of `HEAD_EXPECT` reads his head (K1)."""
    import looks  # noqa: E402  (tools/looks)

    out = []
    for doc in head_report(capture, index, plant=plant)["rows"]:
        want = HEAD_EXPECT.get((doc["team"], doc["number"]))
        if want is None:
            out.append("%s: page %s number %s is none of HEAD_EXPECT"
                       % ("focus %s" % doc["k"] if doc["k"] is not None else "up close",
                          doc["page"], doc["number"]))
            continue
        for line in replay.head_judge(doc["reading"],
                                      replay.head_expected(looks.parse_tuple(want))):
            out.append("%s, team %d number %d: %s"
                       % ("focus %s" % doc["k"] if doc["k"] is not None else "up close",
                          doc["team"], doc["number"], line))
    return out


# -- pose: the pose against ANIME.BIN (PLAN-KITS-REPLAY section 5.1) ----------

ANIME_EXPECT = {
    (9, 0): (0, 0), (10, 0): (0, 0),
    (9, 3): (146, 8), (10, 2): (134, 9), (10, 3): (4, 9),
}
"""(slot, focus) -> (animation, frame) of `/BIN/ANIME.BIN` the followed
figure's pose is read from: the first header entry of the block its pairs
are in (the goalkeepers' block is entries 0 and 1), and the frame there.
Measured by `pose --against-anime` on the five recaptured poses, 10 of 10
paired pieces explained in each (KRP-TASK-14).  Constant per (slot, focus),
never read from the capture (K1)."""

ANIME_POSES = {
    "anime/slot9-keeper-front.json":
        "18fbf3c345321b06762f5e2463c3da0a4e8761dbbf0961df321e396ac8faaca2",
    "anime/slot10-keeper-front.json":
        "a2d4e3bba073c704bcc66e7b2c68ca698e88ea9c162008062a86160ec7b032f7",
    "anime/slot9-focus3-first.json":
        "4f5221f9775fd73bde745c6cd2e7d50e53270617903ff1405c1c3d74e4cd2b9c",
    "anime/slot10-focus2-first.json":
        "27da64f776a881d90b6278deb8a3587ab13156e3f7a0ee4ff51c6234c6c2d683",
    "anime/slot10-focus3-first.json":
        "63c427bfac827f8efc87b6381c4ccd0a08140b943b892c0d00f0ae863e64dc4b",
}
"""The poses `check` judges against `ANIME_EXPECT`, in the folder of the kept
captures, with the sha256 each was kept with: the five up close recaptured
with the pair (`oracle.py --replay SLOT [--focus K] --pose-dir
<folder>/anime`, KRP-TASK-14)."""

ANIME_PLANT = 1
"""`--plant-anime`: the animation expected is moved this many entries on, so
the judge has to find every explained piece in another animation."""


def read_anime(image_path: str) -> bytes:
    """The whole of `/BIN/ANIME.BIN`, through the `looks` digest guard."""
    import anime  # tools/looks
    import iso_source  # tools/pes2

    with iso_source.open_disc(image_path) as disc:
        return anime.read(disc)


def load_pose(path: str) -> dict:
    """A pose, as `work/kits-pose/` keeps it ({"slot", "focus", "pieces"}),
    from a pose file or from a capture's followed figure."""
    with open(path) as fh:
        doc = json.load(fh)
    if "pieces" in doc:
        return doc
    capture = replay.Capture.load(path)
    figure = followed(capture, "front", bool(capture.focus), 0)[1]
    if figure is None:
        raise replay.ReplayError("%s follows no figure" % path)
    return dict(figure.pose(), slot=capture.slot, focus=capture.focus or 0)


def anime_report(pose: dict, data: bytes, plant: bool = False) -> dict:
    """The pose against the file (`replay.anime_reading`), judged against
    `ANIME_EXPECT` for its (slot, focus); with *plant* the expected animation
    is `ANIME_PLANT` entries on."""
    key = (pose["slot"], pose.get("focus") or 0)
    reading = replay.anime_reading(data, pose)
    expect = ANIME_EXPECT.get(key)
    if expect is not None and plant:
        expect = (expect[0] + ANIME_PLANT, expect[1])
    failures = (["no ANIME_EXPECT for slot %d focus %d" % key] if expect is None
                else replay.anime_judge(reading, expect))
    return dict(reading, slot=key[0], focus=key[1], expect=list(expect) if expect else None,
                plant=plant, failures=failures)


def anime_gate_failures(folder: str, data: bytes, plant: bool = False) -> list:
    """`check`'s part for the poses: each of `ANIME_POSES` holds its digest
    and reads the frame `ANIME_EXPECT` says."""
    out = []
    for name, want in ANIME_POSES.items():
        path = os.path.join(folder, name)
        problem = digest_problem(path, want)
        if problem:
            out.append(problem)
            continue
        doc = anime_report(load_pose(path), data, plant)
        out.extend("%s: %s" % (name, line) for line in doc["failures"])
    return out


def _kits_oracle():
    """tools/kits/oracle.py, by path: `import oracle` finds the looks one,
    which `core.tex` put first on sys.path.  Loaded once; when the oracle is
    the running script it registers itself here, and that one is used."""
    import importlib.util

    if "kits_oracle" in sys.modules:
        return sys.modules["kits_oracle"]
    spec = importlib.util.spec_from_file_location("kits_oracle",
                                                  os.path.join(KITS_DIR, "oracle.py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check(folder: str, verbose: bool = True, plant_head: bool = False,
          plant_anime: bool = False) -> int:
    """`kits_replay`: every capture of `CAPTURES` in *folder* holds its digest,
    and the readers' answer on it holds the oracle's judges against the
    measured expectations (`REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`).  Returns
    the failure count."""
    oracle = _kits_oracle()
    index = _index()
    failures = []
    for line in head_constant_failures(os.environ[IMAGE_VARIABLE]):
        failures.append("HEAD_EXPECT: %s" % line)
        print("  FAIL  HEAD_EXPECT: %s" % line)
    if not failures and verbose:
        print("  ok    HEAD_EXPECT: the disc records the %d players' looks it says"
              % len(HEAD_EXPECT))
    for name, want in CAPTURES.items():
        path = os.path.join(folder, name)
        problem = digest_problem(path, want)
        if problem:
            failures.append(problem)
            print("  FAIL  %s" % problem)
            continue
        capture = replay.Capture.load(path)
        if capture.kind == replay.KIND_WALK:
            doc = walk_report(capture, index)
            walk = replay.Walk.of(capture, index)
            got = replay.judge_walk(walk.rows, oracle.REPLAY_FIELD_EXPECT[capture.slot],
                                    oracle.REPLAY_IDLE.get(capture.slot))
            said = "%d foci, %d outfield, %d goalkeeper(s) followed" % (
                doc["foci"], doc["follows"]["outfield"], doc["follows"]["goalkeeper"])
        else:
            doc = figure_report(capture, index, bool(capture.focus))
            expect = oracle.REPLAY_EXPECT[(capture.slot, capture.focus)]
            read = doc["panel"]["read"]
            panel = tuple(doc["panel"]["panel"]) if doc["panel"]["panel"] else None
            panel_failures = oracle.panels_judge([{
                "cell": (0,) + panel[1:], "number": doc["panel"]["number"],
                "digits": [tuple(d) for d in read["digits"]],
                "unexplained": read["unexplained"]}]) if read else []
            figure = followed(capture, "front", bool(capture.focus), 0)[1]
            got = replay.judge({"focus": figure, "still": doc["still"],
                                "turned": doc["turned"], "panel": panel,
                                "number": doc["panel"]["number"],
                                "panel_failures": panel_failures,
                                "idle": oracle.REPLAY_IDLE.get(capture.slot),
                                "front_frames": doc["front_frames"],
                                "back_frames": doc["back_frames"]}, expect)
            f = doc["figure"]
            said = "root %s head %s armband %s for %s, still %s, panel %s number %s" % (
                f["root"], f["head"], f["armband"], f["replaces"], doc["still"],
                doc["panel"]["panel"], doc["panel"]["number"])
        heads = head_gate_failures(capture, index, plant_head)
        got = got + ["head of %s" % line for line in heads]
        said += "; every head reads its player's HEAD_EXPECT"
        for line in got:
            failures.append("%s: %s" % (name, line))
            print("  FAIL  %s: %s" % (name, line))
        if not got and verbose:
            print("  ok    %s: %s" % (name, said))
    anime = anime_gate_failures(folder, read_anime(os.environ[IMAGE_VARIABLE]), plant_anime)
    for line in anime:
        failures.append("ANIME_EXPECT: %s" % line)
        print("  FAIL  ANIME_EXPECT: %s" % line)
    if not anime and verbose:
        print("  ok    ANIME_EXPECT: the %d pose(s) up close read the animation and frame "
              "it says, every paired piece explained" % len(ANIME_POSES))
    print("kits_replay: %d failure(s)" % len(failures))
    return len(failures)


# -- printing ----------------------------------------------------------------

def _print_anime(doc) -> None:
    for row in doc["rows"]:
        if row is None:
            print("  piece with no pair")
            continue
        print("  %-4s pair %6d: animation %s frame %s slot %s, rules %s"
              % (row["section"], row["pair"], row["animations"], row["frame"], row["slot"],
                 ",".join(row["rules"]) or "none"))
    print("slot %d focus %d: %d of %d piece(s) carry a pair, %d explained; animation %s "
          "frame %s explains %d; expected %s%s"
          % (doc["slot"], doc["focus"], doc["linked"], doc["pieces"], doc["explained"],
             doc["animations"], doc["frame"], doc["explains"], doc["expect"],
             " (planted)" if doc["plant"] else ""))
    for line in doc["failures"]:
        print("  FAIL  %s" % line)


def _print_figure(doc) -> None:
    f = doc["figure"]
    if f is None:
        print("no followed figure")
        return
    print("%s, %s: %s %s, head %s, sleeves %s, armband %s%s; still %s; depth %.0f"
          % (doc["capture"]["path"], doc["pick"], f["family"], f["root"], f["head"],
             f["sleeves"], f["armband"],
             " for %s" % f["replaces"] if f["replaces"] else "", doc["still"], f["depth"]))
    print("  order %s" % " ".join(map(str, f["order"])))
    p = doc["panel"]
    print("  panel %s from the %s capture, number %s" % (p["panel"], p["side"], p["number"]))
    s = doc["section"]
    if s is not None:
        print("  section %d: %d prim(s), %d shaded, %d raw, %d semi; CLUT %s; page %s; error %s"
              % (s["section"], s["n"], s["shaded"], s["raw"], s["semi"], s["cluts"],
                 s["pages"], s["error"]))


def _print_head(doc) -> None:
    for r in doc["rows"]:
        h = r["reading"]
        print("  %-8s page %-4s team %-4s number %-4s section %-3s %s%s, %d prim(s), CLUT %s: "
              "skin %s hair %s beard %s%s" % (
                  "up close" if r["k"] is None else "focus %d" % r["k"], r["page"], r["team"],
                  r["number"], h["section"], "/".join(h["styles"]) or "-",
                  " twin" if h["twin"] else "", r["primitives"],
                  " ".join("(%d,%d)" % tuple(c) for c in h["cluts"]),
                  "/".join(h["skin"]) or "-", "/".join(h["hair"]) or "-",
                  "/".join(h["beard"]) or "-",
                  "; stray %s" % h["stray"] if h["stray"] else ""))
        if r["disc"] is not None:
            e = r["expected"]
            print("           record %s (slot %s) %s: section %d skin %s hair %s beard %s -- %s"
                  % (r["record"], r["slot"], r["disc"], e["section"], e["skin"], e["hair"],
                     e["beard"], "; ".join(r["failures"]) or "ok"))
        elif r["failures"]:
            print("           %s" % "; ".join(r["failures"]))
        if r["drawn"] is not None:
            d = r["drawn"]
            print("           drawn %s: section %d (the game's %d), %d primitive(s) the game "
                  "samples, %s" % (d["tuple"], d["section"], d["game_section"], d["primitives"],
                                   "%d differ: %s" % (len(d["differ"]), d["differ"])
                                   if d["differ"] else "every CLUT the game's"))
    if doc["drawn"] is not None:
        print("%s of %s drawn head(s) sample the game's CLUT on every primitive"
              % (doc["drawn_agree"], doc["drawn"]))
    if doc["player"] is not None:
        print("%s of %s distinct player(s) match their disc record%s" % (
            doc["match"], doc["players"], " (plant: every CLUT a column right)"
            if doc["plant"] else ""))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("describe", "figures", "figure", "panel", "walk"):
        one = sub.add_parser(name)
        one.add_argument("capture")
        one.add_argument("--json", action="store_true")
        if name in ("figure", "panel"):
            pick = one.add_mutually_exclusive_group()
            pick.add_argument("--on-axis", action="store_true")
            pick.add_argument("--nearest", action="store_true")
            one.add_argument("--nth", type=int, default=0)
        if name == "figure":
            one.add_argument("--section", type=int)
        if name == "figures":
            one.add_argument("--side", choices=("front", "back"), default="front")
            one.add_argument("--frame", type=int, default=-1)
    head = sub.add_parser("head")
    head.add_argument("capture")
    head.add_argument("--player")
    head.add_argument("--plant-hair-column", action="store_true")
    head.add_argument("--drawn", action="store_true")
    head.add_argument("--json", action="store_true")
    show = sub.add_parser("show")
    show.add_argument("capture")
    show.add_argument("--png", required=True)
    show.add_argument("--section", type=int)
    show.add_argument("--box", action="store_true")
    show.add_argument("--json", action="store_true")
    confront = sub.add_parser("confront")
    confront.add_argument("capture")
    confront.add_argument("--section", type=int)
    confront.add_argument("--tab", action="store_true")
    confront.add_argument("--player", action="store_true")
    confront.add_argument("--out", default=os.path.join("work", "kits-replay", "tab"))
    confront.add_argument("--json", action="store_true")
    take = sub.add_parser("capture")
    take.add_argument("--slot", type=int, required=True)
    take.add_argument("--focus", type=int, default=0)
    take.add_argument("--turn", choices=("R1", "L1"))
    take.add_argument("--walk", choices=("L2", "R2"))
    take.add_argument("--out", default=CAPTURE_DIR)
    take.add_argument("--cue")
    pose = sub.add_parser("pose")
    pose.add_argument("capture")
    pose.add_argument("--against-anime", action="store_true", required=True)
    pose.add_argument("--plant-anime", action="store_true")
    pose.add_argument("--json", action="store_true")
    gate = sub.add_parser("check")
    gate.add_argument("folder", nargs="?")
    gate.add_argument("--quiet", action="store_true")
    gate.add_argument("--plant-hair-column", action="store_true")
    gate.add_argument("--plant-anime", action="store_true")
    args = parser.parse_args(argv)

    if args.command == "capture":
        cue = args.cue or os.environ.get(DRIVE_VARIABLE)
        if not cue or not os.environ.get(IMAGE_VARIABLE):
            print("replay.py capture: needs %s (the Japanese data track) and --cue or %s "
                  "(the English cue the states were saved on)" % (IMAGE_VARIABLE,
                                                                  DRIVE_VARIABLE))
            return 1
        if args.walk and (args.focus or args.turn):
            print("replay.py capture: --walk takes neither --focus nor --turn")
            return 1
        path, data = run_capture(args.slot, args.focus, args.turn, args.walk, args.out, cue)
        idle = _kits_oracle().REPLAY_IDLE.get(args.slot)
        for name, n, judged in sequences(data):
            print("  %-9s %s frame(s) %s" % (
                name, n, "the largest between two taps of the turn; timeout %s" % idle
                if name == "turn gap" else
                "from its last tap to the end of its capture; timeout %s" % idle
                if judged else "from the reload, across its taps (each starts the idle "
                "again): not judged"))
        print("  capture kept at %s (schema v1, sha256 %s)" % (path, sha256_of(path)))
        failures = timeout_failures(data, idle)
        for line in failures:
            print("  FAIL  %s" % line)
        return 1 if failures else 0
    if args.command == "check":
        folder = args.folder or os.environ.get(REPLAY_DIR_VARIABLE)
        if not folder:
            print("kits_replay: skipped -- %s is not set (the folder of the kept captures, "
                  "work/kits-oracle)" % REPLAY_DIR_VARIABLE)
            return SKIP
        if not os.environ.get(IMAGE_VARIABLE):
            print("kits_replay: skipped -- %s is not set" % IMAGE_VARIABLE)
            return SKIP
        return 1 if check(folder, not args.quiet, args.plant_hair_column,
                          args.plant_anime) else 0
    if args.command == "pose":
        if not os.environ.get(IMAGE_VARIABLE):
            print("replay.py pose: needs %s (the Japanese data track)" % IMAGE_VARIABLE)
            return 1
        try:
            pose_doc = load_pose(args.capture)
        except replay.ReplayError as exc:
            print("replay.py: %s" % exc, file=sys.stderr)
            return 1
        doc = anime_report(pose_doc, read_anime(os.environ[IMAGE_VARIABLE]), args.plant_anime)
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        else:
            _print_anime(doc)
        return 1 if doc["failures"] else 0

    try:
        capture = replay.Capture.load(args.capture)
    except replay.ReplayError as exc:
        print("replay.py: %s" % exc, file=sys.stderr)
        return 1
    if args.command in ("show", "confront") and capture.kind != replay.KIND_CLOSE:
        print("replay.py: %s is a walk; show and confront read a close capture"
              % args.capture, file=sys.stderr)
        return 1
    if args.command == "head":
        if args.player not in (None, "all") and not args.player.isdigit():
            print("replay.py head: --player takes all or a record index", file=sys.stderr)
            return 1
        doc = head_report(capture, _index(), args.player, os.environ.get(IMAGE_VARIABLE),
                          args.plant_hair_column, args.drawn)
        for row in doc["rows"]:
            row["reading"]["cluts"] = [list(c) for c in row["reading"]["cluts"]]
            row["reading"]["stray"] = [list(c) for c in row["reading"]["stray"]]
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        else:
            _print_head(doc)
        failed = [r for r in doc["rows"] if r["failures"] or (r["drawn"] and r["drawn"]["differ"])]
        return 1 if failed else 0
    if args.command == "show":
        picture = show_picture(capture, _index(), args.section, args.box)
        write_png(args.png, picture["width"], picture["height"], picture["rgb"])
        doc = {"schema": SCHEMA, "capture": _capture_doc(capture), "png": args.png,
               "width": picture["width"], "height": picture["height"],
               "sha256": sha256_of(args.png), "drawn": picture["drawn"],
               "section": args.section, "box": picture["box"]}
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        else:
            print("%s: %dx%d, the game's frame left, the captured pose drawn right "
                  "(%d px drawn)" % (args.png, doc["width"], doc["height"], doc["drawn"]))
        return 0
    if args.command == "confront" and args.tab:
        doc = confront_tab(capture, _index(), args.out, args.player)
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        else:
            for side in TAB_SIDES:
                one = doc["sides"][side]
                print("  tab %s (yaw %g) against the game's %s capture: %s px, histogram "
                      "intersection %s, %s over the colours the tab draws" % (
                          side, one["yaw"], one["game_capture"], one["game_pixels"],
                          "%.3f" % one["intersection"] if one["intersection"] is not None
                          else "-",
                          "%.3f" % one["intersection_tab_colours"]
                          if one["intersection_tab_colours"] is not None else "-"))
        return 0
    if args.command == "confront":
        doc = confront_report(capture, _index(), args.section)
        if args.json:
            print(json.dumps(doc, indent=1, sort_keys=True))
        else:
            for r in doc["sections"]:
                print("  %3d: %4d px; far %s bare texel, %s modulated" % (
                    r["section"], r["pixels"],
                    "%.2f" % r["far"] if r["far"] is not None else "-",
                    "%.2f" % r["far_shaded"] if r["far_shaded"] is not None else "-"))
        return 0
    if args.command == "describe":
        doc = describe_report(capture)
    elif args.command == "figures":
        doc = figures_report(capture, args.side, args.frame)
    elif args.command == "walk":
        doc = walk_report(capture, _index())
    else:
        if capture.kind != replay.KIND_CLOSE:
            print("replay.py: %s is a walk; read it with `walk`" % args.capture, file=sys.stderr)
            return 1
        doc = figure_report(capture, _index(), default_axis(capture, args), args.nth,
                            getattr(args, "section", None))
        if args.command == "panel":
            doc = {"schema": SCHEMA, "capture": doc["capture"], "pick": doc["pick"],
                   "nth": doc["nth"], "panel": doc["panel"]}
    if args.json:
        print(json.dumps(doc, indent=1, sort_keys=True))
        return 0
    if args.command == "figure":
        _print_figure(doc)
    elif args.command == "panel":
        p = doc["panel"]
        print("panel %s from the %s capture, number %s; cells %s"
              % (p["panel"], p["side"], p["number"], p["cells"]))
    elif args.command == "walk":
        for r in doc["rows"]:
            print("  %2d  %-6s head %-4s root %-4s %-5s armband %-4s panel %-16s number %s"
                  % (r["k"], "follow" if r["follows"] else (r["end"] or "-"), r["head"],
                     r["root"], r["sleeves"], r["armband"], r["panel"], r["number"]))
        print("%d foci; followed %s" % (doc["foci"], doc["follows"]))
    elif args.command == "figures":
        for f in doc["figures"]:
            print("  depth %6.0f  off %s  %s %s: %s" % (
                f["depth"], "%.1f" % f["off_axis"] if f["off_axis"] is not None else "-",
                f["family"], f["root"], " ".join(map(str, f["order"]))))
        print("%s frame %d of %d, list head %s, %d figure(s)"
              % (doc["side"], doc["frame"], doc["frames"], doc["head"], len(doc["figures"])))
    else:
        c = doc["capture"]
        print("%s: %s capture, slot %s focus %s (%s x%s); front %s, back %s, turned %s"
              % (c["path"], c["kind"], c["slot"], c["focus"], c["button"], c["taps"],
                 doc["front"], doc["back"], doc["turned"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

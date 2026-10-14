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
    python tools/kits/replay.py show <capture.json> --png out.png [--section S | --box]
    python tools/kits/replay.py confront <capture.json> [--section S] [--json]
    python tools/kits/replay.py capture --slot S [--focus K] [--turn R1|L1] [--walk L2|R2]
                                        [--out DIR] [--cue CUE]   # boots the emulator
    python tools/kits/replay.py check [<folder>]        # the kits_replay gate

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


def replay_capture(game, maps, bodies: dict, index, slot: int, rotate: str,
                   focus: int = 0) -> dict:
    """Everything `--replay` reads from the paused replay: the first capture
    (`pose_capture`) with the frame buffer under the followed figure and the
    texture pages and CLUTs it samples; the kit pages; then, from the state
    reloaded, taps of *rotate* until the torso has turned `REPLAY_BACK`, and
    the turned capture.  With *focus* the camera is first moved K taps of L2
    to a player (`replay_arrive`), which it follows from behind: the first
    capture is then his back and the turned one his front.  Each run counts
    the frames it spends since its last tap.  With *rotate* None there is
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
    buffer, texture = None, {"pages": {}, "cluts": {}}
    # the drawing offset rides in the one-node list submitted before each
    # ordering table, not in the table the figure is in: the last one set
    offsets = [front["offsets"].get("%d" % e["head"]) for e in front["events"]
               if e["kind"] == "submit"]
    offset = next((o for o in reversed(offsets) if o is not None), None)
    if figure and offset is not None:
        box = tuple(int(round(v)) for v in fit["box"])
        rows = looks_oracle.vram_region(game, offset[0] + box[0], offset[1] + box[1],
                                        box[2] - box[0] + 1, box[3] - box[1] + 1)
        buffer = {"origin": box[:2], "offset": offset,
                  "rows": [[looks_oracle._five_bits(p) for p in row] for row in rows]}
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
                "page_x": page_x, "pages": pages, "buffer": buffer, "texture": texture}
    start = replay_arrive(game, slot, focus, label + "-turn")
    yaws, depths, turned, tapped = [], [], None, start
    root = frames[-1]["focus"][1]["section"] if frames and frames[-1]["focus"] else None
    projection = frames[-1]["focus"][0]["projection"] if frames and frames[-1]["focus"] else None
    for _tap in range(O.REPLAY_ROTATE_MOST):
        try:
            tapped = O.frame_now(game)
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
    back_samples = []
    if back is not None:
        back_frames_list = O.replay_frames(back, choose=choose)
        if back_frames_list:
            back_samples = back["lists"].get("%d" % back_frames_list[-1]["head"], [])
        for x in sorted({one["page"][0] for one in back_samples if O.is_figure(one)}):
            pages.setdefault("%d" % x, O._edit_page(game, x))
    game.capture(label + "-back")
    return {"focus": focus, "front": front, "back": back, "front_frames": front_frames,
            "back_frames": back_frames, "turn_frames": turn_frames, "rotate": rotate, "yaws": yaws, "depths": depths, "turned": turned,
            "hits": hits, "tag": tag, "set": kit_set, "page_x": page_x, "pages": pages,
            "buffer": buffer, "texture": texture}


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
    reload across all its taps, and is printed, not judged."""
    if data.get("kind") == replay.KIND_WALK:
        return [("focus %d" % f["k"], f["frames"], True) for f in data["foci"]
                if not f.get("refused")]
    out = [("front", data["front_frames"], True)]
    if data.get("back_frames") is not None:
        out += [("turn", data["turn_frames"], False), ("back", data["back_frames"], True)]
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


def check(folder: str, verbose: bool = True) -> int:
    """`kits_replay`: every capture of `CAPTURES` in *folder* holds its digest,
    and the readers' answer on it holds the oracle's judges against the
    measured expectations (`REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`).  Returns
    the failure count."""
    oracle = _kits_oracle()
    index = _index()
    failures = []
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
        for line in got:
            failures.append("%s: %s" % (name, line))
            print("  FAIL  %s: %s" % (name, line))
        if not got and verbose:
            print("  ok    %s: %s" % (name, said))
    print("kits_replay: %d failure(s)" % len(failures))
    return len(failures)


# -- printing ----------------------------------------------------------------

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
    show = sub.add_parser("show")
    show.add_argument("capture")
    show.add_argument("--png", required=True)
    show.add_argument("--section", type=int)
    show.add_argument("--box", action="store_true")
    show.add_argument("--json", action="store_true")
    confront = sub.add_parser("confront")
    confront.add_argument("capture")
    confront.add_argument("--section", type=int)
    confront.add_argument("--json", action="store_true")
    take = sub.add_parser("capture")
    take.add_argument("--slot", type=int, required=True)
    take.add_argument("--focus", type=int, default=0)
    take.add_argument("--turn", choices=("R1", "L1"))
    take.add_argument("--walk", choices=("L2", "R2"))
    take.add_argument("--out", default=CAPTURE_DIR)
    take.add_argument("--cue")
    gate = sub.add_parser("check")
    gate.add_argument("folder", nargs="?")
    gate.add_argument("--quiet", action="store_true")
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
                name, n, "from its last tap to the end of its capture; timeout %s" % idle
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
        return 1 if check(folder, not args.quiet) else 0

    try:
        capture = replay.Capture.load(args.capture)
    except replay.ReplayError as exc:
        print("replay.py: %s" % exc, file=sys.stderr)
        return 1
    if args.command in ("show", "confront") and capture.kind != replay.KIND_CLOSE:
        print("replay.py: %s is a walk; show and confront read a close capture"
              % args.capture, file=sys.stderr)
        return 1
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

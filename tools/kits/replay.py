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


# -- the gate ----------------------------------------------------------------

def _kits_oracle():
    """tools/kits/oracle.py, by path: `import oracle` finds the looks one,
    which `core.tex` put first on sys.path."""
    import importlib.util

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
    gate = sub.add_parser("check")
    gate.add_argument("folder", nargs="?")
    gate.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

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

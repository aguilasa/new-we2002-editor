#!/usr/bin/env python3
"""Confronts 2 and 3 of PLAN-KITS-PY.md section 5: the community and the game.

Confront 2, the community as an outside oracle, is the run with no option.

The 3D flags the community made (`.bin` beside `.tim`, mostly `*_BND`) are a lone
LZSS stream and the TIM it was compressed from.  Our decompression of the
`.bin` -- the decoder every kit record goes through, reached by the facade --
has to give the TIM's pixels byte for byte.  The TIM never passed through our
code: it is parsed here, by this file alone.

The pairs are read from WE2002_KITS_CORPUS, a folder of the user's (walked
recursively; a pair is a `.bin` and a `.tim` with the same stem, any case).
Nothing of it enters the repository.

Usage:
    python tools/kits/confront.py                 # every pair, exit 1 on any mismatch
    python tools/kits/confront.py --report        # what the corpus holds, counted
    python tools/kits/confront.py --negative [--scratch DIR]
        # copies one matching .tim, changes one pixel of the copy, and needs it refused
    python tools/kits/confront.py --score [--game PNG]
        # confront 3: our 3D of both teams against the game's own match frame
    python tools/kits/confront.py --score --negative
        # the same matrix with the two teams' renders swapped, which has to fail

Confront 3 is the colour histogram of the looks (`tools/looks/confront.py`,
histogram intersection at the console's 5 bits per channel, the frame restricted
to the colours our render draws) on the match of section 4.1: Scotland in its
first kit (`TEX_01`, set 1) against Denmark in its second (`TEX_13`, set 2).
The frame is the one `oracle.py --slot 3 --out work/kits-oracle/match-3`
writes beside its VRAM dumps, and the boxes are the six outfield players
measured on it.  Our side is the window's 3D tab, front and back, spawned with
the venv python on the :98 like `ui_check.py` does.  Each team's boxes have to
score its own render at least MARGIN over the other team's.
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib
from dataclasses import dataclass
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import api  # noqa: E402

SKIP = 77
CORPUS_VARIABLE = "WE2002_KITS_CORPUS"

TIM_MAGIC = 0x10
TIM_HAS_CLUT = 0x08


class TimError(ValueError):
    """The file is not a TIM this reader can take apart."""


def tim_pixels(data: bytes) -> tuple:
    """((x, y, w, h) of the image block, its pixel bytes) of a TIM.

    Layout: u32 magic 0x10, u32 flags (bit 3: a CLUT block follows), then
    each block as u32 length (itself included), u16 x, y, w, h, and data."""
    if len(data) < 8:
        raise TimError("%d bytes is shorter than a TIM header" % len(data))
    magic, flags = struct.unpack_from("<II", data, 0)
    if magic != TIM_MAGIC:
        raise TimError("magic 0x%x, not 0x10" % magic)
    p = 8
    if flags & TIM_HAS_CLUT:
        if p + 4 > len(data):
            raise TimError("the CLUT block is cut")
        p += struct.unpack_from("<I", data, p)[0]
    if p + 12 > len(data):
        raise TimError("no image block after byte %d" % p)
    length, x, y, w, h = struct.unpack_from("<IHHHH", data, p)
    pixels = data[p + 12:p + length]
    if len(pixels) != length - 12 or len(pixels) != w * h * 2:
        raise TimError("image block %dx%d says %d bytes and holds %d"
                       % (w, h, length - 12, len(pixels)))
    return (x, y, w, h), pixels


@dataclass(frozen=True)
class PairResult:
    stem: str
    bin_path: str
    tim_path: str
    status: str          # "match", "differ", "bin" (does not decode), "tim" (not a TIM)
    detail: str = ""

    @property
    def ok(self) -> bool:
        return self.status == "match"


def compare_pair(bin_data: bytes, tim_data: bytes, stem: str = "pair",
                 bin_path: str = "", tim_path: str = "") -> PairResult:
    """Decode the `.bin`, parse the `.tim`, and compare the pixels exactly."""
    def result(status, detail=""):
        return PairResult(stem, bin_path, tim_path, status, detail)
    try:
        rect, pixels = tim_pixels(tim_data)
    except TimError as exc:
        return result("tim", str(exc))
    try:
        plain = api.decompress_stream(bin_data, stem + ".bin")
    except api.StreamError as exc:
        return result("bin", str(exc))
    if plain == pixels:
        return result("match", "%d bytes at (%d,%d) %dx%d" % ((len(pixels),) + rect))
    if len(plain) != len(pixels):
        return result("differ", "the .bin gives %d bytes, the .tim holds %d"
                      % (len(plain), len(pixels)))
    first = next(i for i in range(len(plain)) if plain[i] != pixels[i])
    count = sum(1 for a, b in zip(plain, pixels) if a != b)
    return result("differ", "%d byte(s) differ, first at %d" % (count, first))


def find_pairs(folder: str) -> list:
    """[(stem, bin path, tim path)] under *folder*, sorted by path."""
    out = []
    for root, _dirs, files in os.walk(folder):
        by_stem = {}
        for name in files:
            stem, ext = os.path.splitext(name)
            by_stem.setdefault(stem.lower(), {})[ext.lower()] = os.path.join(root, name)
        for stem in sorted(by_stem):
            exts = by_stem[stem]
            if ".bin" in exts and ".tim" in exts:
                out.append((os.path.splitext(os.path.basename(exts[".bin"]))[0],
                            exts[".bin"], exts[".tim"]))
    return sorted(out, key=lambda t: t[1].lower())


def _read(path: str) -> bytes:
    with open(path, "rb") as fh:
        return fh.read()


def confront_folder(folder: str) -> list:
    return [compare_pair(_read(b), _read(t), stem, b, t) for stem, b, t in find_pairs(folder)]


def tim_shape(data: bytes) -> tuple:
    """(flags, CLUT block length or 0, (x, y, width in pixels, h)) of a TIM.
    Width in pixels: at 8 bits a halfword of the image block is two."""
    _magic, flags = struct.unpack_from("<II", data, 0)
    clut = struct.unpack_from("<I", data, 8)[0] if flags & TIM_HAS_CLUT else 0
    (x, y, w, h), _ = tim_pixels(data)
    return flags, clut, (x, y, w * 2 if flags & 7 == 1 else w, h)


NAMED_LIST = 10
"""A list of names this short or shorter is printed whole."""


def report(folder: str) -> list:
    """The lines of `--report`: what the corpus holds, counted -- the files
    per folder and the ones without a partner, how the pairs are named, and
    the TIM flags, CLUT length and image rectangle of every pair."""
    from collections import Counter

    lines = []
    for root, _dirs, files in sorted(os.walk(folder)):
        exts = Counter(os.path.splitext(f)[1].lower() for f in files)
        if not (exts[".bin"] or exts[".tim"]):
            continue
        stems = {}
        for f in files:
            stem, ext = os.path.splitext(f)
            if ext.lower() in (".bin", ".tim"):
                stems.setdefault(stem.lower(), {})[ext.lower()] = stem
        lone = {e: sorted(s[e] for s in stems.values() if set(s) == {e})
                for e in (".bin", ".tim")}
        lines.append("%s/: %d .bin, %d .tim, %d pair(s)"
                     % (os.path.relpath(root, folder), exts[".bin"], exts[".tim"],
                        sum(len(s) == 2 for s in stems.values())))
        for e in (".bin", ".tim"):
            if lone[e]:
                names = (", ".join(lone[e]) if len(lone[e]) <= NAMED_LIST
                         else "(%d, not listed)" % len(lone[e]))
                lines.append("  %d %s without a partner: %s" % (len(lone[e]), e, names))
    pairs = find_pairs(folder)
    odd = sorted(stem for stem, _b, _t in pairs if not stem.upper().endswith("_BND"))
    lines.append("pairs: %d, %d named *_BND, %d otherwise: %s"
                 % (len(pairs), len(pairs) - len(odd), len(odd), ", ".join(odd) or "none"))
    shapes = Counter()
    rects = Counter()
    for _stem, _b, tim in pairs:
        flags, clut, rect = tim_shape(_read(tim))
        shapes[(flags, clut)] += 1
        rects[rect] += 1
    for (flags, clut), n in sorted(shapes.items()):
        lines.append("  TIM flags %d, CLUT block %d bytes: %d" % (flags, clut, n))
    for rect, n in sorted(rects.items(), key=lambda kv: (-kv[1], kv[0])):
        lines.append("  image at (%d,%d) %dx%d px: %d" % (rect + (n,)))
    return lines


CONTROL_PIXEL = 1000
"""Pixel byte the negative control changes in its copy of a .tim."""


def negative(results: list, scratch: Optional[str]) -> int:
    sound = next((r for r in results if r.ok), None)
    if sound is None:
        print("confront 2: --negative needs a matching pair, and none matched")
        return 1
    own = scratch is None
    folder = tempfile.mkdtemp(prefix="kits-confront2-") if own else scratch
    try:
        os.makedirs(folder, exist_ok=True)
        copy = os.path.join(folder, os.path.basename(sound.tim_path))
        shutil.copyfile(sound.tim_path, copy)
        data = bytearray(_read(copy))
        rect_start = len(data) - len(tim_pixels(bytes(data))[1])
        at = rect_start + CONTROL_PIXEL
        data[at] ^= 0x01
        with open(copy, "wb") as fh:
            fh.write(data)
        planted = compare_pair(_read(sound.bin_path), _read(copy), sound.stem,
                               sound.bin_path, copy)
        held = planted.status == "differ" and ("first at %d" % CONTROL_PIXEL) in planted.detail
        print("control: %s.tim copied to %s, pixel byte %d (file byte %d) XOR 0x01"
              % (sound.stem, folder, CONTROL_PIXEL, at))
        print("  clean:   %s (%s)" % (sound.status, sound.detail))
        print("  planted: %s (%s)" % (planted.status, planted.detail))
        print("control %s" % ("held: the changed copy is refused" if held else "FAILED"))
        return 0 if held else 1
    finally:
        if own:
            shutil.rmtree(folder, ignore_errors=True)

# -- confront 3: the 3D against the game -----------------------------------

IMAGE_VARIABLE = "WE2002_LOOKS_IMAGE"
MATCH_FRAME = os.path.join("work", "kits-oracle", "match-3", "screen.png")
"""The frame `oracle.py --slot 3 --out work/kits-oracle/match-3` writes: slot 3
loaded, 32 frames stepped, the broadcast camera of Scotland x Denmark."""
TEAMS = (("01", 1, "Scotland, first kit"), ("13", 2, "Denmark, second kit"))
"""(tag, set the game wears, who) -- section 4.1, measured in VRAM."""
BOXES = {
    "01": ((255, 295, 295, 388), (65, 350, 106, 462), (760, 472, 800, 592)),
    "13": ((395, 328, 435, 430), (663, 208, 712, 294), (10, 510, 62, 626)),
}
"""(left, top, right, bottom) of each outfield player of a team in MATCH_FRAME
(800x655), measured off a 2x zoom with a 20-pixel grid.  The goalkeepers are
out of the frame, and Scotland's wears set 2's goalkeeper palette anyway."""
FRAME_SIZE = (800, 655)
FRAME_SHA256 = "ee1bfba6e7dc03af8276130f6f25d8b71493aefdd3635dc4c6069ac009e9d8a6"
"""MATCH_FRAME as two runs of `oracle.py --slot 3` wrote it, byte for byte the
same (2026-10-04).  BOXES hold for that picture only, so another one is refused."""
MARGIN = 0.05
"""The looks' KIT_CONTROL_MARGIN: how much better the right kit has to score
than another team's, in histogram intersection."""
RANK = 32
"""5 bits per channel, the console's colour depth (the looks' RANK)."""
YAWS = (180.0, 0.0)
"""Front and back: a player on the pitch shows either."""
BACKDROP_3D = (0x8C, 0x8C, 0x8C)
VENV_PYTHON = os.path.join("work", "venv-looks",
                           os.path.join("Scripts", "python.exe") if os.name == "nt"
                           else os.path.join("bin", "python"))
APP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ui", "app.py")
DISPLAY = ":98"
TIMEOUT = 180


class ScoreError(RuntimeError):
    """Confront 3 could not be measured."""


def read_rgb(path: str) -> tuple:
    """(width, height, [(r, g, b), ...]) of an 8-bit RGB or RGBA PNG without
    interlace, any row filter: both the fork's frame and the Qt capture."""
    with open(path, "rb") as fh:
        data = fh.read()
    p, chunks = 8, {}
    while p < len(data):
        n = struct.unpack_from(">I", data, p)[0]
        tag = data[p + 4:p + 8]
        chunks[tag] = chunks.get(tag, b"") + data[p + 8:p + 8 + n]
        p += 12 + n
    width, height, depth, kind, _, _, interlace = struct.unpack_from(">IIBBBBB", chunks[b"IHDR"])
    bpp = {2: 3, 6: 4}.get(kind)
    if depth != 8 or bpp is None or interlace:
        raise ScoreError("%s: not an 8-bit RGB or RGBA PNG without interlace" % path)
    raw = zlib.decompress(chunks[b"IDAT"])
    stride, prev, pixels = width * bpp, bytearray(width * bpp), []
    for r in range(height):
        f = raw[r * (stride + 1)]
        row = bytearray(raw[r * (stride + 1) + 1:(r + 1) * (stride + 1)])
        for i in range(stride):
            a = row[i - bpp] if i >= bpp else 0
            b = prev[i]
            c = prev[i - bpp] if i >= bpp else 0
            if f == 1:
                row[i] = (row[i] + a) & 0xFF
            elif f == 2:
                row[i] = (row[i] + b) & 0xFF
            elif f == 3:
                row[i] = (row[i] + (a + b) // 2) & 0xFF
            elif f == 4:
                pa, pb, pc = abs(b - c), abs(a - c), abs(a + b - 2 * c)
                row[i] = (row[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
        prev = row
        pixels.extend(tuple(row[x * bpp:x * bpp + 3]) for x in range(width))
    return width, height, pixels


def quantise(pixel) -> tuple:
    return tuple(v // (256 // RANK) for v in pixel)


def histogram(pixels) -> dict:
    out: dict = {}
    for pixel in pixels:
        colour = quantise(pixel)
        out[colour] = out.get(colour, 0) + 1
    return out


def box_pixels(shot: tuple, box: tuple) -> list:
    width = shot[0]
    return [shot[2][y * width + x] for y in range(box[1], box[3]) for x in range(box[0], box[2])]


def figure_pixels(shot: tuple) -> list:
    """The drawn pixels of a 3D capture: inside the box of the backdrop colour,
    the backdrop left out."""
    width, _, pixels = shot
    at = [i for i, p in enumerate(pixels) if p == BACKDROP_3D]
    if not at:
        raise ScoreError("the capture has no 3D view (no backdrop pixel)")
    xs, ys = [i % width for i in at], [i // width for i in at]
    return [p for y in range(min(ys), max(ys) + 1) for x in range(min(xs), max(xs) + 1)
            for p in (pixels[y * width + x],) if p != BACKDROP_3D]


def intersection(first: dict, second: dict) -> float:
    """Histogram intersection of two normalised histograms, 0..1 (the looks')."""
    total_a, total_b = sum(first.values()), sum(second.values())
    if not total_a or not total_b:
        return 0.0
    return sum(min(n / total_a, second.get(colour, 0) / total_b)
               for colour, n in first.items())


def restrict(counts: dict, palette) -> dict:
    return {colour: n for colour, n in counts.items() if colour in palette}


def environment() -> dict:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if os.name == "nt":
        return env
    env["DISPLAY"] = DISPLAY
    try:
        ps = subprocess.run(["ps", "-o", "args=", "-C", "Xvfb"], capture_output=True,
                            text=True).stdout
    except OSError:
        ps = ""
    auth = [line.split()[line.split().index("-auth") + 1] for line in ps.splitlines()
            if ("Xvfb %s " % DISPLAY) in line + " " and "-auth" in line]
    if auth:
        env["XAUTHORITY"] = auth[0]
    else:
        env.pop("XAUTHORITY", None)
    return env


def render(image: str, tag: str, kit_set: int, out_dir: str) -> dict:
    """The histogram of our 3D of *tag* in *kit_set*, front and back together."""
    if not os.path.isfile(VENV_PYTHON):
        raise ScoreError("no venv python at %s (make looks-venv)" % VENV_PYTHON)
    counts: dict = {}
    for yaw in YAWS:
        out = os.path.join(out_dir, "ours-%s-set%d-yaw%d.png" % (tag, kit_set, yaw))
        args = [VENV_PYTHON, APP, image, "--tag", tag, "--tab", "3d", "--kit-set",
                str(kit_set), "--figure", "0", "--yaw", "%g" % yaw, "--screenshot", out]
        try:
            done = subprocess.run(args, env=environment(), capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            raise ScoreError("app.py did not exit within %d s" % TIMEOUT)
        if done.returncode or not os.path.isfile(out):
            raise ScoreError("app.py exited %s on TEX_%s set %d: %s"
                             % (done.returncode, tag, kit_set,
                                (done.stdout + done.stderr).strip()[-300:]))
        for colour, n in histogram(figure_pixels(read_rgb(out))).items():
            counts[colour] = counts.get(colour, 0) + n
    return counts


def score_matrix(frame: tuple, ours: dict) -> dict:
    """{(team on the pitch, our render): (score, share of the boxes kept)}."""
    out = {}
    for team, _, _ in TEAMS:
        pixels = [p for box in BOXES[team] for p in box_pixels(frame, box)]
        game = histogram(pixels)
        for mine, hist in ours.items():
            kept = restrict(game, set(hist))
            out[(team, mine)] = (intersection(kept, hist),
                                 sum(kept.values()) / float(len(pixels)))
    return out


def leads(matrix: dict, swapped: bool = False) -> list:
    """[(team, right, wrong, lead)]: how far each team's players score the
    render they should match over the other one.  *swapped* hands each team
    the other team's render -- the control."""
    tags = [t for t, _, _ in TEAMS]
    out = []
    for team in tags:
        other = [t for t in tags if t != team][0]
        right, wrong = (other, team) if swapped else (team, other)
        out.append((team, right, wrong, matrix[(team, right)][0] - matrix[(team, wrong)][0]))
    return out


def score_verdict(matrix: dict, swapped: bool = False) -> list:
    """Failures: a team whose own render does not lead the other's by MARGIN."""
    bad = []
    for team, right, wrong, lead in leads(matrix, swapped):
        if lead < MARGIN:
            bad.append("the TEX_%s players score our TEX_%s %.3f, TEX_%s %.3f: a lead of "
                       "%.3f, under %.2f" % (team, right, matrix[(team, right)][0], wrong,
                                             matrix[(team, wrong)][0], lead, MARGIN))
    return bad


def score(game_path: str, negative_run: bool) -> int:
    image = os.environ.get(IMAGE_VARIABLE)
    if not image:
        print("confront 3: skipped -- %s is not set (the Japanese data track .bin)"
              % IMAGE_VARIABLE)
        return SKIP
    if not os.path.isfile(game_path):
        print("confront 3: skipped -- no frame at %s; make it with "
              "`python tools/kits/oracle.py --slot 3 --out %s`"
              % (game_path, os.path.dirname(game_path)))
        return SKIP
    import hashlib

    with open(game_path, "rb") as fh:
        digest = hashlib.sha256(fh.read()).hexdigest()
    if digest != FRAME_SHA256:
        print("confront 3: %s has sha256 %s, not the %s… BOXES were measured on"
              % (game_path, digest[:12], FRAME_SHA256[:12]))
        return 1
    frame = read_rgb(game_path)
    if frame[:2] != FRAME_SIZE:
        print("confront 3: %s is %dx%d, and BOXES were measured on %dx%d"
              % ((game_path,) + frame[:2] + FRAME_SIZE))
        return 1
    with tempfile.TemporaryDirectory(prefix="kits-score-") as tmp:
        ours = {tag: render(image, tag, kit_set, tmp) for tag, kit_set, _ in TEAMS}
    matrix = score_matrix(frame, ours)
    print("  frame: %s" % game_path)
    print("  %-28s %s" % ("players on the pitch", "  ".join(
        "ours TEX_%s set %d" % (t, s) for t, s, _ in TEAMS)))
    for team, _, who in TEAMS:
        print("  TEX_%s %-20s %s" % (team, who, "  ".join(
            "%.3f (%4.1f %% kept)" % (matrix[(team, t)][0], 100 * matrix[(team, t)][1])
            for t, _, _ in TEAMS)))
    if not negative_run:
        for team, right, wrong, lead in leads(matrix):
            print("  TEX_%s players: our TEX_%s leads our TEX_%s by %.3f" % (team, right, wrong, lead))
    bad = score_verdict(matrix, swapped=negative_run)
    for line in bad:
        print("  %s  %s" % ("red " if negative_run else "FAIL", line))
    if negative_run:
        print("confront 3 --negative: the swapped renders give %d failure(s) of %d -- %s"
              % (len(bad), len(TEAMS), "the control holds" if len(bad) == len(TEAMS)
                 else "THE CONTROL DOES NOT FAIL"))
        return 0 if len(bad) == len(TEAMS) else 1
    print("confront 3: %d of %d team(s) score their own kit %.2f over the other's"
          % (len(TEAMS) - len(bad), len(TEAMS), MARGIN))
    return 1 if bad else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--negative", action="store_true",
                        help="change one pixel of a copied .tim and require a mismatch")
    parser.add_argument("--scratch", help="where --negative puts its copy (default: a temp folder)")
    parser.add_argument("--report", action="store_true",
                        help="count what the corpus holds: files per folder, the unpaired, "
                             "the pair names, and each pair's TIM shape")
    parser.add_argument("--score", action="store_true",
                        help="confront 3: our 3D of both teams against the game's match frame")
    parser.add_argument("--game", default=MATCH_FRAME,
                        help="the game frame --score reads (default %(default)s)")
    args = parser.parse_args(argv)
    if args.score:
        return score(args.game, args.negative)

    folder = os.environ.get(CORPUS_VARIABLE)
    if not folder:
        print("confront 2: skipped -- %s is not set (a folder with the community's "
              ".bin / .tim flag pairs)" % CORPUS_VARIABLE)
        return SKIP
    if not os.path.isdir(folder):
        print("confront 2: %s points at %s, which is not a folder" % (CORPUS_VARIABLE, folder))
        return 1
    if args.report:
        for line in report(folder):
            print(line)
        return 0
    results = confront_folder(folder)
    if args.negative:
        return negative(results, args.scratch)
    for r in results:
        if not r.ok:
            print("  %-6s %s: %s" % (r.status.upper(), os.path.relpath(r.bin_path, folder),
                                     r.detail))
    matched = sum(r.ok for r in results)
    print("confront 2: %d pairs read, %d match byte for byte (%s)"
          % (len(results), matched, ", ".join(
              "%d %s" % (sum(r.status == s for r in results), s)
              for s in ("differ", "bin", "tim") if any(r.status == s for r in results))
             or "no mismatch"))
    return 0 if results and matched == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

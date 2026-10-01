#!/usr/bin/env python3
"""Confront 2 of PLAN-KITS-PY.md section 5: the community as an outside oracle.

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
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import sys
import tempfile
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--negative", action="store_true",
                        help="change one pixel of a copied .tim and require a mismatch")
    parser.add_argument("--scratch", help="where --negative puts its copy (default: a temp folder)")
    parser.add_argument("--report", action="store_true",
                        help="count what the corpus holds: files per folder, the unpaired, "
                             "the pair names, and each pair's TIM shape")
    args = parser.parse_args(argv)

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

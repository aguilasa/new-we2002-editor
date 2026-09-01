#!/usr/bin/env python3
"""The LZSS codec of the `BIN/*.BIN` containers -- phase 7.

Ported from `WECompress.cpp` of Maximiliano Ducoli's **WECompressor**
(<https://github.com/maxiducoli/WECompressor>), whose own comments are in
Italian and predate him. Credit and the non-commercial condition are in
[NOTICE.md](../../NOTICE.md); section 9 of `docs/PLAN-FEATURES.md` made
that a blocking requirement of this file existing at all.

Section 1.14 of `docs/PLAN-PES2-PSX.md` measured that PES2 and WE2002
share the container format: 2.070 bytes of compressed stream byte for byte
identical, and the same header-width histogram. This is the tool that
turns "the same decoder consumes the first 2 kB" into "the same decoder
consumes every stream on four discs".

## The format

A stream is a sequence of groups. Each group opens with a **flag byte**,
read low bit first, eight tokens per byte:

    flag bit 0   literal          one byte, copied out
    flag bit 1   command          one or two bytes:

      0x00..0x7F  two bytes: distance = next | (b & 3) << 8   (0..1023)
                              count    = (b >> 2) + 3         (3..34)
      0x80..0xBF  one byte:  distance = (b & 0x0F) + 1        (1..16)
                              count    = (b >> 4) - 6         (2..5)
      0xC0..0xFE  one byte:  a block of (b - 0xB8) literal bytes follows
      0xFF        end of stream

The copy is byte at a time and may overlap its own output, as LZ77's
always may. **`0xC0..0xFE` is read here and never written** -- the CARP
compressor leaves that branch commented out, and section 5(c) of
`PLAN-FEATURES` measured the consequence: recompressed output is never
byte-identical to Konami's, always 0,2%-2,0% smaller. That asymmetry is a
decision, not a defect, and it is why the round-trip asserted here is
`decompress(compress(x)) == x` and never the other direction.

Two details of the C that a careless port loses:

  `while (k3-- >= 0)` uses a **signed** `k3`, so the literal block is
  `k3 + 1` bytes, not `k3`. Making it unsigned changes the ceiling and
  breaks only the files that use the opcode.

  The flag register is `i = k | 0xFF00`, and the reload test is
  `(i & 0x100) == 0`. The 0xFF00 is a shift counter, not data: after
  eight `i >>= 1` it runs out and the next flag byte is read.

## Usage

    python3 tools/pes2/lzss.py <track1.bin>              # every BIN/*.BIN
    python3 tools/pes2/lzss.py <track1.bin> --file /BIN/DAT2D.BIN
    python3 tools/pes2/lzss.py <track1.bin> --check      # measured counts
    python3 tools/pes2/lzss.py <track1.bin> --roundtrip  # every block
"""

import argparse
import collections
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import Image                                        # noqa: E402

WINDOW = 1024           # N   -- the ring buffer, hence the largest distance
LOOKAHEAD = 34          # F   -- the largest match
THRESHOLD = 3           # the shortest match worth a two-byte command

# A PSX RAM pointer, which is what a container header is made of. The
# console has 2 MiB at 0x80000000; the headers seen here stay well inside.
RAM_LO = 0x80000000
RAM_HI = 0x80200000

BIN_DIR = "/BIN/"

# The largest block measured on these discs is 16.725 B -- japanese-shift-jis;
# 16.676 in both PES2 releases, 16.501 in the European Deluxe -- and five to
# seven blocks per disc pass 16 KiB. The 256 KiB here is deliberate slack over
# that, not a measurement: the cap exists for the resync scan, where a wrong
# offset can decode into a plausible-looking stream forever. `--sizes`
# reprints the distribution, so the next change to it need not be guessed.
#
# (This comment claimed "the largest block is 16 KiB" until 2026-09-01, which
# was never measured and is false by 341 bytes.)
PROBE_CAP = 1 << 18

# A decode shorter than this is not reported as a block. Three bytes of any
# file "decompress" to one byte somewhere, so the resync scan needs a floor
# -- but the floor is what separates the `none` verdict from `whole`, and it
# was chosen by plausibility. Measured 2026-09-01 over the four discs: the
# smallest real block is **1.152 B**, the same on all four, so the margin
# under this floor is **128 bytes**. A real 1 KiB block on a fifth disc would
# drop out of the count in silence and take its container to `none`.
MIN_BLOCK = 1024


# What each disc is measured to hold, keyed on its container count -- the
# cheapest thing a disc says about itself, and distinct across the four we
# have. A fifth disc that collided on the count would need a better key;
# the check says which disc it matched, so a wrong match is visible.
#
# These are the numbers section 1.14(e) of the plan publishes, remeasured
# 2026-09-01. The count *is* the assertion: the signed-`k3` porting bug the
# module docstring warns about takes (EsIt) from whole 172 to whole 41, and
# nothing weaker than a measured value notices.
EXPECT = {
    208: ("PES2 (EsIt)",
          {"whole": 172, "partial": 3, "none": 33, "blocks": 2153}),
    210: ("PES2 (EnFrDe)",
          {"whole": 174, "partial": 3, "none": 33, "blocks": 2195}),
    177: ("WE2002 European Deluxe",
          {"whole": 141, "partial": 3, "none": 33, "blocks": 1842}),
    195: ("WE2002 Japanese",
          {"whole": 159, "partial": 3, "none": 33, "blocks": 2027}),
}


class LzssError(Exception):
    """A stream that does not decode -- the reason names where it stopped."""


def decompress(data, start=0, cap=None):
    """(plain bytes, bytes consumed) for the stream that begins at `start`.

    Raises `LzssError` rather than returning a short read: a caller that
    is probing an offset needs "no" to be distinguishable from "yes, and
    it was empty".
    """
    out = bytearray()
    p = start
    n = len(data)
    flags = 0
    while True:
        if (flags & 0x100) == 0:
            if p >= n:
                raise LzssError(f"stream at {start}: input ended mid-flags at {p}")
            flags = data[p] | 0xFF00
            p += 1
        if p >= n:
            raise LzssError(f"stream at {start}: input ended mid-token at {p}")
        b = data[p]

        if (flags & 1) == 0:                       # literal
            out.append(b)
            p += 1
        else:
            if b & 0x80:
                p += 1
                if b & 0x40:                       # 0xC0..0xFF
                    if b == 0xFF:
                        break                      # end of stream
                    count = b - 0xB9 + 1           # signed k3, hence the +1
                    if p + count > n:
                        raise LzssError(
                            f"stream at {start}: literal block of {count} runs "
                            f"past the end at {p}")
                    out += data[p:p + count]
                    p += count
                    flags >>= 1
                    continue
                distance = (b & 0x0F) + 1
                count = (b >> 4) - 7 + 1
            else:                                  # 0x00..0x7F, two bytes
                if p + 1 >= n:
                    raise LzssError(
                        f"stream at {start}: two-byte command truncated at {p}")
                distance = data[p + 1] | ((b & 3) << 8)
                count = (b >> 2) + 2 + 1
                p += 2
            if distance == 0:
                raise LzssError(f"stream at {start}: distance 0 at {p}")
            if distance > len(out):
                raise LzssError(
                    f"stream at {start}: distance {distance} reaches before the "
                    f"start of {len(out)} bytes of output")
            for _ in range(count):
                out.append(out[-distance])
        if cap is not None and len(out) > cap:
            raise LzssError(f"stream at {start}: past the {cap}-byte cap")
        flags >>= 1
    return bytes(out), p - start


def compress(plain):
    """The CARP encoding of `plain`, minus the block-literal opcode.

    Not byte-compatible with Konami's compressor, and not meant to be --
    see the module docstring. What it guarantees is that `decompress`
    reproduces `plain` exactly.

    The match search is a hash of three-byte keys rather than the ring
    buffer and hash chain of the C. The output alphabet is the same; only
    the search is, and the encoder is free to pick any legal match.
    """
    out = bytearray()
    flags_at = None
    flag = 0
    bit = 0
    index = {}
    i = 0
    n = len(plain)

    def open_group():
        nonlocal flags_at, flag, bit
        flags_at = len(out)
        out.append(0)
        flag = 0
        bit = 0

    def close_group():
        out[flags_at] = flag

    open_group()
    while i < n:
        best_len = 0
        best_dist = 0
        key = bytes(plain[i:i + 3])
        if len(key) == 3:
            lo = i - WINDOW + 1
            for pos in reversed(index.get(key, ())):
                if pos < lo:
                    break
                length = 3
                limit = min(LOOKAHEAD, n - i)
                while length < limit and plain[pos + length] == plain[i + length]:
                    length += 1
                if length > best_len:
                    best_len, best_dist = length, i - pos
                    if length == limit:
                        break

        # The one-byte command reaches only 16 back but costs half as much,
        # so a short near match beats a short far one.
        near = None
        window = plain[max(0, i - 16):i]
        for length in range(min(5, n - i), 1, -1):
            at = window.rfind(plain[i:i + length])
            if at >= 0:
                near = (length, len(window) - at)
                break

        if near and (best_len < THRESHOLD or near[0] >= best_len):
            best_len, best_dist = near
            token = bytes([((best_len + 6) << 4) | (best_dist - 1)])
        elif best_len >= THRESHOLD:
            token = bytes([((best_len - 3) << 2) | (best_dist >> 8),
                           best_dist & 0xFF])
        else:
            best_len = 1
            token = None

        if token is None:
            out.append(plain[i])
        else:
            flag |= 1 << bit
            out += token

        for k in range(i, min(i + best_len, n - 2)):
            index.setdefault(bytes(plain[k:k + 3]), []).append(k)
        i += best_len

        bit += 1
        if bit == 8:
            close_group()
            open_group()

    flag |= 1 << bit
    out.append(0xFF)
    close_group()
    out.append(0x00)                 # the CARP terminator writes this too
    return bytes(out)


def check_block_literal():
    """Assert the `0xC0..0xFE` branch, on a stream built here.

    The expectation table above catches this too, but only on a disc it
    recognises; this holds on any disc and on none. It is the branch
    `compress()` never emits -- so `--roundtrip` cannot reach it either --
    and it is where the one porting bug the module docstring names lives:
    `while (k3-- >= 0)` is signed, so `0xC5` introduces `0xC5 - 0xB9 + 1`
    = 13 literal bytes, not 12.

    Returns a list of complaints, empty when the branch is right.
    """
    bad = []
    # Flag byte 0x03: **both** of the first two tokens are commands -- token
    # 0 the block literal of 13, token 1 the 0xFF that ends the stream. With
    # 0x01 the terminator is read as a literal and the stream runs off the
    # end, which is what the first draft of this assertion did.
    stream = bytes([0x03, 0xC5]) + b"0123456789abc" + bytes([0xFF])
    try:
        plain, used = decompress(stream, 0)
    except LzssError as exc:
        return [f"the block-literal opcode does not decode at all: {exc}"]
    if plain != b"0123456789abc":
        bad.append(f"0xC5 gave {plain!r}, expected b'0123456789abc' -- the "
                   f"literal block is k3 + 1 bytes, `k3` being signed")
    if used != len(stream):
        bad.append(f"0xC5 consumed {used} of {len(stream)} bytes")
    return bad


# ---- containers ------------------------------------------------------

def header_words(data):
    """The leading RAM pointers of a container, nulls included.

    Section 1.14 counted these to build the width histogram. A null word
    is *inside* the run, not the end of it: `TEX_*.BIN` has one at index 6
    on both discs and eleven real pointers around it.
    """
    words = []
    p = 0
    while p + 4 <= len(data):
        w = struct.unpack_from("<I", data, p)[0]
        if w == 0:
            words.append(w)
        elif RAM_LO <= w < RAM_HI:
            words.append(w)
        else:
            break
        p += 4
    while words and words[-1] == 0:      # a trailing null is padding, not a slot
        words.pop()
    return words


def stream_start(data):
    """Where the first compressed stream should begin, from the header."""
    return 4 * len(header_words(data))


def scan(data, start=None, minimum=MIN_BLOCK):
    """Every LZSS stream in a container, found by decoding and resyncing.

    Streams are 4-byte aligned and separated by gaps this task does not
    explain -- the per-entry headers are PES2-TASK-27's subject. So the
    scan decodes, then walks forward in words until the next stream
    decodes, and reports what it covered.

    `minimum` rejects the short accidental decodes: three bytes of any
    file will "decompress" to one byte somewhere. It also *defines* the
    `none` verdict -- see `MIN_BLOCK` for what the number is worth.
    """
    if start is None:
        start = stream_start(data)
    blocks = []
    p = start
    n = len(data)
    while p < n:
        q = (p + 3) & ~3
        found = None
        while q + 2 <= n:
            try:
                plain, used = decompress(data, q, cap=PROBE_CAP)
            except LzssError:
                q += 4
                continue
            if len(plain) >= minimum:
                found = (q, used, len(plain))
                break
            q += 4
        if found is None:
            break
        blocks.append(found)
        p = found[0] + found[1]
    return blocks


def containers(img):
    """Every Form 1 `/BIN/*.BIN` of one disc, in path order."""
    return [p for p in sorted(img.files)
            if p.startswith(BIN_DIR) and p.endswith(".BIN") and img.is_form1(p)]


def classify(data):
    """(verdict, blocks, leftover) for one container.

    The three verdicts are the ones PES2-TASK-26 asks for, sharpened by
    what the discs turned out to hold:

    - `whole`   -- a stream decodes at exactly the offset this container's
                   own header names. The codec reads the file, and the
                   header rule of section 1.14 finds the way in.
    - `partial` -- streams decode, but not at the header offset. The codec
                   is fine; the way in is something else.
    - `none`    -- nothing decodes anywhere. Not an LZSS container.

    **`leftover` is not failure.** A container ends with a table of
    16-byte entry records -- `0f 80 0a 00 20 02 80 01 …` -- and `DAT2D`
    carries 15.538 bytes of it after its last stream. Counting that as
    "stopped in the middle" would report a defect that is not there; what
    it really is, is PES2-TASK-27's subject. So it is measured and
    reported, never judged.
    """
    start = stream_start(data)
    blocks = scan(data, start)
    if not blocks:
        return "none", blocks, len(data)
    covered = sum(b[1] for b in blocks)
    leftover = len(data) - covered
    return ("whole" if blocks[0][0] == start else "partial"), blocks, leftover


# ---- commands --------------------------------------------------------

def cmd(args):
    """Every image on the command line, plus a total when there is more than one.

    The total is here rather than in prose because the plan quotes it: four
    discs, 790 containers, and a sum nobody should be adding by hand.
    """
    grand = {"whole": 0, "partial": 0, "none": 0, "files": 0,
             "blocks": 0, "comp": 0, "raw": 0, "bad": 0}
    for image in args.image:
        one(args, image, grand)
    if len(args.image) > 1:
        print(f"\nTOTAL over {len(args.image)} disc(s): {grand['files']} "
              f"container(s) -- whole {grand['whole']}, partial "
              f"{grand['partial']}, not LZSS {grand['none']}")
        print(f"  {grand['blocks']} block(s), {grand['comp']} B compressed -> "
              f"{grand['raw']} B plain")
    return 1 if grand["bad"] else 0


def one(args, image, grand):
    with Image(image) as img:
        paths = containers(img)
        if args.file:
            paths = [p for p in paths if p == args.file]
            if not paths:
                print(f"{args.file}: not a Form 1 /BIN/*.BIN of "
                      f"{os.path.basename(image)}", file=sys.stderr)
                grand["bad"] += 1
                return

        print(f"{os.path.basename(image)}   {len(paths)} container(s) "
              f"in {BIN_DIR}")
        tally = {"whole": 0, "partial": 0, "none": 0}
        blocks_total = raw_total = comp_total = 0
        sizes = []
        bad = 0
        for path in paths:
            data = img.read_file(path)
            words = header_words(data)
            verdict, blocks, leftover = classify(data)
            tally[verdict] += 1
            blocks_total += len(blocks)
            sizes += [b[2] for b in blocks]
            raw_total += sum(b[2] for b in blocks)
            comp_total += sum(b[1] for b in blocks)
            if args.file or args.verbose:
                print(f"  {path:22s} {len(data):8d} B  header {len(words):3d} w "
                      f"-> stream at {4 * len(words):5d}  {verdict}  "
                      f"{len(blocks)} block(s), {leftover} B outside")
                for off, used, raw in blocks:
                    print(f"      @{off:7d}  comp {used:7d}  raw {raw:7d}")
            elif verdict != "whole":
                print(f"  {path:22s} {verdict}: {len(blocks)} block(s), "
                      f"{leftover} B of {len(data)} outside any stream")

            if args.roundtrip:
                for off, used, raw in blocks:
                    plain, _ = decompress(data, off)
                    again, _ = decompress(compress(plain), 0)
                    if again != plain:
                        print(f"  ROUND-TRIP FAILED {path} @{off}")
                        bad += 1

        print(f"  whole {tally['whole']}   partial {tally['partial']}   "
              f"not LZSS {tally['none']}   (of {len(paths)})")
        print(f"  {blocks_total} block(s), {comp_total} B compressed -> "
              f"{raw_total} B plain")

        if args.sizes and sizes:
            counted = collections.Counter(sizes)
            print(f"  block sizes: min {min(sizes)}  max {max(sizes)}  "
                  f"over 16 KiB {sum(1 for x in sizes if x > 16384)}  "
                  f"(MIN_BLOCK {MIN_BLOCK}, margin {min(sizes) - MIN_BLOCK} B; "
                  f"PROBE_CAP {PROBE_CAP})")
            print("  most common: "
                  + ", ".join(f"{v}x{k}" for k, v in counted.most_common(6)))

        for key in ("whole", "partial", "none"):
            grand[key] += tally[key]
        grand["files"] += len(paths)
        grand["blocks"] += blocks_total
        grand["comp"] += comp_total
        grand["raw"] += raw_total
        if args.roundtrip:
            print("  round-trip: "
                  + ("FAILED" if bad else f"{blocks_total}/{blocks_total} OK"))

        if args.check:
            # Against **measured value**, not shape. The loop that used to
            # stand here re-decoded the blocks `scan` had just decoded, at
            # the same offsets, with the same deterministic function: it
            # could not disagree. What it left asserting was
            # `tally["whole"] > 0`, a floor only a completely dead decoder
            # reaches -- the signed-`k3` bug drops (EsIt) from 172 whole to
            # 41 and cleared it comfortably.
            for complaint in check_block_literal():
                print(f"CHECK FAILED: {complaint}", file=sys.stderr)
                bad += 1
            want = EXPECT.get(len(paths))
            if want is None:
                print(f"CHECK: {len(paths)} containers is no disc on record "
                      f"-- counts not asserted", file=sys.stderr)
            else:
                label, counts = want
                got = dict(tally, blocks=blocks_total)
                print(f"CHECK: recognised {label} by its {len(paths)} "
                      f"containers", file=sys.stderr)
                for key in ("whole", "partial", "none", "blocks"):
                    if got[key] != counts[key]:
                        print(f"CHECK FAILED: {label}: {key} is {got[key]}, "
                              f"measured {counts[key]}", file=sys.stderr)
                        bad += 1
            print("CHECK OK" if not bad else "CHECK FAILED", file=sys.stderr)
    grand["bad"] += bad


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", nargs="+",
                    help="the data track (.bin) of one or more discs")
    ap.add_argument("--file", metavar="PATH", help="one container, in detail")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--roundtrip", action="store_true",
                    help="assert decompress(compress(x)) == x on every block")
    ap.add_argument("--sizes", action="store_true",
                    help="print the block-size distribution, which is what "
                         "justifies MIN_BLOCK and PROBE_CAP")
    ap.add_argument("--check", action="store_true",
                    help="assert the block-literal opcode, and the measured "
                         "verdict and block counts of a disc on record")
    args = ap.parse_args(argv)
    return cmd(args)


if __name__ == "__main__":
    sys.exit(main())

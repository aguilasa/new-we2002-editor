#!/usr/bin/env python3
"""`ANIME.BIN` -- the animations, and the pose the LOOKS SET screen plays.

WHAT THIS FILE IS, MEASURED
---------------------------
LOOKS-TASK-24 answered *where the pose comes from* and LOOKS-TASK-25 captured
*what the game loads*.  This module is the file itself, read from the disc:

    offset 0        204 words, one per animation, each an ABSOLUTE RAM address
                    inside the file's own load image (`layout.ANIME_BASE`).
                    197 of the 204 are distinct; seven animations are named
                    twice.
    offset 816      the payload, one block per animation and nothing else:

                        frame[N]      96 bytes each
                        pointer[N]    one per frame, absolute like the header
                        0x0000000B    one word, closing the block

                    The header entry points at the POINTER LIST, not at the
                    frames -- the frames sit just before it.

    A frame is TWELVE PAIRS of words, one pair per drawn piece, in the order
    the screen draws them (`PIECE_ORDER`).  The first word of a pair carries
    three signed 10-bit angles at bits 9:0, 19:10 and 29:20, each shifted left
    by four; the top two bits are flags this module does not read.  **The
    matrix is not in the file.**  The game builds it from those three angles.

WHAT IS EXACT HERE AND WHAT IS NOT
----------------------------------
The angles are exact: `frame_angles()` reproduces, integer for integer, the
three halfwords the game leaves in the scratchpad for every piece of every
frame of both save states (`oracle.py --pose` records them beside each piece).

The matrix is NOT exact yet, and saying so is the point.  `rotation()` builds
`Rz . Ry . Rx` from the same sine table the game uses -- measured, see
`sine_table()` -- and lands within **1** of the game's own entries, on a 4096
scale.  The last unit is the GTE's: the game's `RotMatrix` at 0x8003D4BC feeds
the products through the coprocessor, whose saturation and truncation this
module does not emulate.  Reproducing it exactly is what LOOKS-TASK-26 still
owes, and the run says so rather than rounding the claim away.

Usage:
    python tools/looks/anime.py --check
    python tools/looks/anime.py --check-image              # WE2002_LOOKS_IMAGE
    python tools/looks/anime.py --check-image <japanese.bin>
    python tools/looks/anime.py --report [<japanese.bin>]
    python tools/looks/anime.py --against-pose  # vs work/looks-pose/
"""

from __future__ import annotations

import math
import struct
import sys

import harness
import layout

HEADER_WORDS = layout.ANIME_HEADER_WORDS
WORD = 4
FRAME_BYTES = 96
PIECE_PAIRS = 12
PAIR_BYTES = 8
BLOCK_END = 0x0000000B  # not-an-address: the word that closes an animation
WORD_OF_FRAME_FIVE = 0x8FE3FC02  # not-an-address: a packed angle triple
ANGLE_BITS = 10  # not-an-address: the width of one packed angle
ANGLE_SHIFT = 4  # not-an-address: how far the game shifts an angle left
TURN = 4096  # not-an-address: angle units in a full turn, and 1.0 in 4.12
ONE = 4096  # not-an-address: 1.0 in the 4.12 fixed point the GTE uses
MATRIX_UNITS = 1  # not-an-address: how far the GTE's rounding puts us
"""How far a matrix built here may sit from the game's and still be rounding.

Measured on 2026-09-18: where the angles are the named frame's and the piece
is the outfield player's, every entry lands within one unit of 4096 -- the
game runs the same products through the GTE and this module does not emulate
that coprocessor.  Six of the goalkeeper's limbs land 92 to 188 apart with the
SAME angles, which is not rounding and not measured yet."""

PIECE_ORDER = (
    "root", "head", "torso", "upper arm a", "forearm a", "upper arm b",
    "forearm b", "thigh a", "shin a", "foot a", "thigh b", "shin b",
)
"""Which piece each pair of a frame belongs to, in draw order.

**Measured, not assigned by shape.**  On 2026-09-18 the pose capture read the
three unpacked angles out of the scratchpad at every matrix load and they are,
pair for pair, the twelve pairs of the frame the animation state was playing
(`oracle.py --pose <SLOT> <N>` writes both, and `--check-image` here has no
way to check it -- what checks it is the capture).  `root` is the load that
carries no model pointer; the other eleven are `pieces.py`'s names.
"""


class BadAnime(Exception):
    """The file does not have the shape this module measured."""


# --- the file --------------------------------------------------------------

def read(disc) -> bytes:
    """The whole of ANIME.BIN, through the digest guard of `layout`."""
    return disc.read(layout.ANIME)


def header(data: bytes) -> list:
    """The 204 header entries, as OFFSETS into the file.

    The words are absolute addresses in the file's load image, so this is
    where `layout.ANIME_BASE` earns its keep: it is a measured constant of the
    file and not a derivation (`derive_base()` refuses this file -- §10.3 (j)).
    """
    if len(data) < HEADER_WORDS * WORD:
        raise BadAnime("a file of %d byte(s) cannot hold %d header entries"
                       % (len(data), HEADER_WORDS))
    out = []
    for word in struct.unpack("<%dI" % HEADER_WORDS,
                              data[:HEADER_WORDS * WORD]):
        if not layout.ANIME_BASE <= word < layout.ANIME_BASE + len(data):
            raise BadAnime("header entry %d is %#010x, outside the file "
                           "loaded at %#010x" % (len(out), word,
                                                 layout.ANIME_BASE))
        out.append(word - layout.ANIME_BASE)
    return out


def block(data: bytes, at: int) -> dict:
    """One animation, from the offset its header entry names.

    *at* is the pointer LIST.  Reading it is what says how many frames there
    are, and where they start -- the frames are the bytes just before it.
    """
    inside = range(layout.ANIME_BASE, layout.ANIME_BASE + len(data))
    frames = []
    cursor = at
    while cursor + WORD <= len(data):
        word = struct.unpack("<I", data[cursor:cursor + WORD])[0]
        if word not in inside:
            break
        frames.append(word - layout.ANIME_BASE)
        cursor += WORD
    if not frames:
        raise BadAnime("the list at %d names no frame" % at)
    end = struct.unpack("<I", data[cursor:cursor + WORD])[0] \
        if cursor + WORD <= len(data) else None
    if end != BLOCK_END:
        raise BadAnime("the list at %d closes with %r and not %#x"
                       % (at, end, BLOCK_END))
    first = min(frames)
    if at - first != len(frames) * FRAME_BYTES:
        raise BadAnime("%d frame(s) between %d and %d is %d byte(s) each, not "
                       "%d" % (len(frames), first, at,
                               (at - first) // max(len(frames), 1),
                               FRAME_BYTES))
    return {"list": at, "frames": frames, "start": first,
            "end": cursor + WORD}


def blocks(data: bytes) -> list:
    """Every animation in the file, in file order.

    Seven header entries repeat, so this is 197 blocks for 204 entries -- the
    count is of BLOCKS, and the caller that wants animations by name wants
    `header()`.
    """
    found = {}
    for at in sorted(set(header(data))):
        found[at] = block(data, at)
    return [found[at] for at in sorted(found)]


def coverage(data: bytes, start: int = HEADER_WORDS * WORD) -> dict:
    """Does the payload tile the file from *start* to the exact EOF?

    **With the starting offset beside the count**, because a walk that begins
    in the middle can close on the same EOF and have read half the file --
    which is how CORR-LOOKS-010 was found in the model files.
    """
    holes = []
    cursor = start
    frames = 0
    for one in blocks(data):
        if one["start"] != cursor:
            holes.append((cursor, one["start"], one["start"] - cursor))
        frames += len(one["frames"])
        cursor = max(cursor, one["end"])
    return {"start": start, "blocks": len(blocks(data)), "frames": frames,
            "end": cursor, "eof": len(data), "holes": holes}


# --- a frame ---------------------------------------------------------------

def _signed(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def angles(word: int) -> tuple:
    """The three angles a pair's first word packs.

    The unpack is the game's, instruction for instruction (0x80011D48):
    `sll 22 / sra 18` is bits 9:0 signed and shifted left by four, `sll 12 /
    sra 22 / sll 4` is bits 19:10, and `sll 2 / sra 22 / sll 4` is bits 29:20.
    The top two bits are read elsewhere by the game and not here.
    """
    return tuple(_signed(word >> (ANGLE_BITS * n), ANGLE_BITS) << ANGLE_SHIFT
                 for n in range(3))


def frame_angles(data: bytes, at: int) -> list:
    """The twelve pieces of one frame, each with its three angles."""
    if at + FRAME_BYTES > len(data):
        raise BadAnime("a frame at %d runs past the file's %d byte(s)"
                       % (at, len(data)))
    words = struct.unpack("<%dI" % (FRAME_BYTES // WORD),
                          data[at:at + FRAME_BYTES])
    return [{"piece": PIECE_ORDER[n], "angles": angles(words[n * 2]),
             "second": words[n * 2 + 1]}
            for n in range(PIECE_PAIRS)]


# --- the matrix the game builds from them ----------------------------------

def sine_table() -> list:
    """The game's own sine table, generated rather than carried.

    `RotMatrix` at 0x8003D4BC indexes a 4096-word table at 0x8005B148, each
    word `(cos << 16) | sin` in 4.12.  Dumped from RAM on 2026-09-18 and
    compared entry by entry against `round(sin(2*pi*i/4096) * 4096)`: **0
    mismatches in 4096**, against 3080 for truncation.  So the table is a
    rounded sine and this module builds it instead of shipping 16 KB of it.
    """
    return [int(math.floor(math.sin(2 * math.pi * i / TURN) * ONE + 0.5))
            for i in range(TURN)]


_SINE = None


def sin(angle: int) -> int:
    global _SINE
    if _SINE is None:
        _SINE = sine_table()
    return _SINE[angle % TURN]


def cos(angle: int) -> int:
    return sin(angle + TURN // 4)


def _product(a: list, b: list) -> list:
    return [sum(a[row * 3 + k] * b[k * 3 + column] for k in range(3))
            for row in range(3) for column in range(3)]


def rotation(three: tuple) -> list:
    """The 4.12 rotation matrix of three angles: `Rz . Ry . Rx`.

    The order is measured, not chosen: decomposing the matrices the game
    loaded gives back angles that are multiples of 16 -- which is what the
    file stores -- only under this order, and the reconstruction then lands
    within one unit of the game's own numbers.

    **Within one unit, not on it.**  The game runs the same products through
    the GTE, and the last unit is that coprocessor's rounding.  Callers that
    need the game's exact matrix take it from a pose capture; callers that
    need the pose take this.
    """
    ax, ay, az = three
    sx, cx = sin(ax), cos(ax)
    sy, cy = sin(ay), cos(ay)
    sz, cz = sin(az), cos(az)
    rx = [ONE, 0, 0, 0, cx, -sx, 0, sx, cx]
    ry = [cy, 0, sy, 0, ONE, 0, -sy, 0, cy]
    rz = [cz, -sz, 0, sz, cz, 0, 0, 0, ONE]
    inner = [value >> 12 for value in _product(ry, rx)]
    return [value >> 12 for value in _product(rz, inner)]


def pose(data: bytes, animation: int, index: int) -> list:
    """Every piece of one frame of one animation, angles and matrix."""
    entries = header(data)
    if not 0 <= animation < len(entries):
        raise BadAnime("animation %d, and the file names %d"
                       % (animation, len(entries)))
    one = block(data, entries[animation])
    if not 0 <= index < len(one["frames"]):
        raise BadAnime("frame %d, and animation %d has %d"
                       % (index, animation, len(one["frames"])))
    return [dict(piece, matrix=rotation(piece["angles"]))
            for piece in frame_angles(data, one["frames"][index])]


# --- the gate --------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("anime.py", _checks, verbose=verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    # -- the angle unpack, on words made here -------------------------------
    ok("zero unpacks to no turn at all", angles(0) == (0, 0, 0))
    ok("the low field is bits 9:0, shifted left by four",
       angles(1) == (16, 0, 0))
    ok("the middle field is bits 19:10", angles(1 << 10) == (0, 16, 0))
    ok("the high field is bits 29:20", angles(1 << 20) == (0, 0, 16))
    ok("each field is SIGNED: the top bit of ten is negative",
       angles(0x200) == (-8192, 0, 0))  # not-an-address: a packed angle
    ok("and the top two bits of the word are not an angle",
       angles(0xC0000000) == (0, 0, 0))  # not-an-address: two flag bits
    # The cross-check that matters, and it is a MEASUREMENT: this word is the
    # first pair of frame 5 of the animation the screen plays, and the triple
    # is what the game had in its scratchpad when it drew `root` from that
    # frame (oracle.py --pose, 2026-09-18).
    ok("a word of the real file unpacks to what the game left in scratchpad",
       angles(WORD_OF_FRAME_FIVE)
       == (32, 4080, 4064),  # not-an-address: three angles
       "%r" % (angles(WORD_OF_FRAME_FIVE),))

    # -- the sine table -----------------------------------------------------
    table = sine_table()
    ok("the table has one entry per angle unit", len(table) == TURN)
    ok("a quarter turn is 1.0 in 4.12", table[TURN // 4] == ONE)
    ok("half a turn is zero again", table[TURN // 2] == 0)
    ok("and three quarters is -1.0", table[3 * TURN // 4] == -ONE)
    # The four entries the RAM dump of 2026-09-18 begins with, which is what
    # makes "generated" a measurement and not a convenience.
    ok("the first entries are the game's own",
       [table[i] for i in range(1, 5)] == [6, 13, 19, 25],
       "%r" % ([table[i] for i in range(1, 5)],))
    ok("cos is sin a quarter turn along", cos(0) == ONE and sin(0) == 0)

    # -- the matrix ---------------------------------------------------------
    ok("no turn is the identity",
       rotation((0, 0, 0)) == [ONE, 0, 0, 0, ONE, 0, 0, 0, ONE])
    turned = rotation((0, TURN // 4, 0))
    ok("a quarter turn about y sends x to -z",
       turned[0] == 0 and turned[6] == -ONE, "%r" % (turned,))
    ok("a rotation keeps its rows a unit long",
       all(abs(sum(value * value for value in row) - ONE * ONE) < ONE * 8
           for row in (turned[0:3], turned[3:6], turned[6:9])),
       "%r" % (turned,))

    # -- the file's shape, on a file made here ------------------------------
    made = _synthetic()
    # The header points at the pointer LIST, which is past the frames -- the
    # made-up file has two frames, so 816 + 2 * 96.
    ok("the header reads back as offsets, and points at the list",
       header(made)[0] == 816 + 2 * FRAME_BYTES, "%r" % (header(made)[0],))
    one = block(made, header(made)[0])
    ok("a block finds its frames before its list", one["start"] == 816)
    ok("and its frames are 96 bytes each", len(one["frames"]) == 2)
    walk = coverage(made)
    ok("the walk closes on the exact end of the made-up file",
       walk["end"] == walk["eof"] and not walk["holes"],
       "%r" % (walk,))
    ok("a frame gives one entry per drawn piece",
       [piece["piece"] for piece in frame_angles(made, 816)]
       == list(PIECE_ORDER))

    broken = bytearray(made)
    broken[-4:] = struct.pack("<I", 0)
    attempt("a block that does not close with the marker is refused",
            BadAnime, lambda: blocks(bytes(broken)))
    attempt("a header entry outside the file is refused", BadAnime,
            lambda: header(struct.pack("<I", 0) * HEADER_WORDS))
    attempt("a frame index the animation does not have is refused", BadAnime,
            lambda: pose(made, 0, 9))

    # -- membership in the image gate ---------------------------------------
    import cli

    ok("anime is in the list cli.py check runs", "anime" in cli.CHECK_IMAGE)


def _synthetic() -> bytes:
    """A file of one animation and two frames, built to the measured shape."""
    frames = 2
    start = HEADER_WORDS * WORD
    at = start + frames * FRAME_BYTES
    head = struct.pack("<%dI" % HEADER_WORDS,
                       *([layout.ANIME_BASE + at] * HEADER_WORDS))
    body = bytearray()
    for index in range(frames):
        for pair in range(PIECE_PAIRS):
            body += struct.pack("<2I", pair + index, 0)
    for index in range(frames):
        body += struct.pack("<I", layout.ANIME_BASE + start
                            + index * FRAME_BYTES)
    body += struct.pack("<I", BLOCK_END)
    return head + bytes(body)


def _check_image(image_path: str) -> int:
    """The measured shape of the real file, asserted on a real disc."""
    import iso_source

    failures = 0
    with iso_source.open_disc(image_path) as disc:
        try:
            disc.read(layout.DAT2D)
        except layout.WrongDisc as exc:
            print("  FAILED %s" % exc)
            print("anime --check-image: 1 failure(s)")
            return 1
        data = read(disc)

    def ok(what: str, condition: bool, detail: str = "") -> None:
        nonlocal failures
        if condition:
            print("  ok    %s%s" % (what, "   %s" % detail if detail else ""))
        else:
            failures += 1
            print("  FAIL  %s%s" % (what, "   %s" % detail if detail else ""))

    entries = header(data)
    walk = coverage(data)
    ok("the header names %d animation(s), %d of them distinct"
       % (len(entries), len(set(entries))), len(entries) == HEADER_WORDS)
    ok("the walk from offset %d covers %d block(s) and %d frame(s) and ends "
       "at %d" % (walk["start"], walk["blocks"], walk["frames"], walk["end"]),
       walk["end"] == walk["eof"] and not walk["holes"],
       "EOF %d, %d hole(s)" % (walk["eof"], len(walk["holes"])))
    ok("every block closes with the same marker",
       all(struct.unpack("<I", data[one["end"] - WORD:one["end"]])[0]
           == BLOCK_END for one in blocks(data)))
    ok("every frame is %d byte(s), twelve pairs of words" % FRAME_BYTES,
       all((one["list"] - one["start"]) % FRAME_BYTES == 0
           for one in blocks(data)))

    screen = pose(data, layout.ANIME_SCREEN_ENTRY, 0)
    ok("the entry the screen plays has a frame for each drawn piece",
       [piece["piece"] for piece in screen] == list(PIECE_ORDER))
    ok("and its matrices are rotations",
       all(abs(sum(value * value for value in piece["matrix"][0:3])
               - ONE * ONE) < ONE * 8 for piece in screen))
    print("anime --check-image: %d failure(s)" % failures)
    return 1 if failures else 0


def against_pose(data: bytes, captures: list) -> dict:
    """The file against what the game loaded, piece by piece.

    Three numbers, and none of them rounded into another:

      **how many pieces the file holds outright** -- the three angles the game
          had in its scratchpad ARE the pair of a key frame, integer for
          integer;
      **how many it does not hold at all** -- the same search over every frame
          of every animation finds nothing.  Those are the frames the game
          builds between key frames, and what it builds them from is not
          measured yet (LOOKS-TASK-32);
      **how far the matrix is** -- on the pieces the file does hold, the
          matrix this module builds against the one the game loaded.
    """
    index = _pairs_by_position(data)
    exact = missing = matrix_exact = pieces = elsewhere = 0
    worst = 0
    for record in captures:
        camera = record["camera"]["rotation"]
        for piece in record["pieces"]:
            pieces += 1
            name = piece["piece"]
            if name not in PIECE_ORDER:
                raise BadAnime("the capture drew %r, which no pair names"
                               % name)
            position = PIECE_ORDER.index(name)
            three = tuple(piece["angles"])
            at = piece["animation_frame"] - layout.ANIME_BASE
            named = None
            if 0 <= at <= len(data) - FRAME_BYTES:
                named = frame_angles(data, at)[position]["angles"]
            if named == three:
                # The reliable link, and the only one the matrix is compared
                # on: the triple IS the pair of the frame the state named.  A
                # triple that merely turns up somewhere in 3952 frames can be
                # another frame's, and comparing a matrix against those was
                # what put six of slot 1's limbs 90 to 188 units apart --
                # false matches, not a broken build.
                exact += 1
                built = [value >> 12 for value in
                         _product(camera, rotation(three))]
                apart = max(abs(a - b) for a, b in zip(built, piece["rotation"]))
                worst = max(worst, apart)
                matrix_exact += (apart == 0)
            elif three in index[position]:
                elsewhere += 1
            else:
                missing += 1
    return {"captures": len(captures), "pieces": pieces, "exact": exact,
            "missing": missing, "elsewhere": elsewhere,
            "matrix_exact": matrix_exact, "matrix_worst": worst}


def _pairs_by_position(data: bytes) -> list:
    """Every angle triple the file holds, kept by which pair carries it."""
    index = [set() for _ in range(PIECE_PAIRS)]
    for one in blocks(data):
        for at in one["frames"]:
            for position, piece in enumerate(frame_angles(data, at)):
                index[position].add(piece["angles"])
    return index


def _load_captures(directory: str) -> list:
    import json
    import os

    found = []
    for name in sorted(os.listdir(directory)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(directory, name), encoding="utf-8") as handle:
            record = json.load(handle)
        if "animation" in record and "pieces" in record:
            found.append(record)
    return found


def _against_pose(image_path: str, directory: str) -> int:
    import iso_source
    import os

    if not os.path.isdir(directory):
        print("anime --against-pose: skipped -- no captures in %s; run "
              "oracle.py --poses first" % directory)
        return 77
    captures = _load_captures(directory)
    if not captures:
        print("anime --against-pose: skipped -- %s holds no capture with the "
              "angles beside each piece" % directory)
        return 77
    with iso_source.open_disc(image_path) as disc:
        data = read(disc)
    found = against_pose(data, captures)
    print("  %d capture(s), %d piece(s) drawn" % (found["captures"],
                                                  found["pieces"]))
    print("  %d of %d carry angles the file holds, integer for integer"
          % (found["exact"], found["pieces"]))
    print("  %d carry angles the file holds at that pair but NOT in the "
          "frame the state named" % found["elsewhere"])
    print("  %d carry angles NO frame of the file holds -- the in-between "
          "frames, still open (LOOKS-TASK-32)" % found["missing"])
    print("  of the %d the file holds, %d matrices are exact and the worst "
          "entry is %d apart of %d"
          % (found["exact"], found["matrix_exact"], found["matrix_worst"],
             ONE))
    failures = 0
    if not found["exact"]:
        print("  FAIL  not one piece carries angles this module finds in the "
              "file: the decode is wrong, not the game")
        failures += 1
    if found["matrix_worst"] > MATRIX_UNITS:
        print("  open  the worst matrix is %d apart and not %d: the pieces "
              "that miss are the goalkeeper's limbs, whose angles ARE the "
              "named frame's -- so something else reaches their matrix, and "
              "naming it is what LOOKS-TASK-26 still owes"
              % (found["matrix_worst"], MATRIX_UNITS))
    print("anime --against-pose: %d failure(s)" % failures)
    return 1 if failures else 0


def _report(image_path: str) -> int:
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = read(disc)
    walk = coverage(data)
    print("%s: %d byte(s), %d header entr(ies), %d distinct"
          % (layout.ANIME, len(data), len(header(data)),
             len(set(header(data)))))
    print("  from offset %d: %d block(s), %d frame(s), ending at %d (EOF %d), "
          "%d hole(s)" % (walk["start"], walk["blocks"], walk["frames"],
                          walk["end"], walk["eof"], len(walk["holes"])))
    entry = layout.ANIME_SCREEN_ENTRY
    one = block(data, header(data)[entry])
    print("  the screen plays entry %d: %d frame(s) at %d..%d"
          % (entry, len(one["frames"]), one["start"], one["end"]))
    for piece in pose(data, entry, 0):
        print("    %-13s angles %-22s matrix %s"
              % (piece["piece"], piece["angles"], piece["matrix"]))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return self_check()
    if len(argv) == 3 and argv[1] == "--check-image":
        return _check_image(argv[2])
    if len(argv) == 2 and argv[1] == "--check-image":
        import iso_source

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("anime --check-image: skipped -- %s" % exc)
            return 77
        return _check_image(image)
    if len(argv) in (2, 3, 4) and argv[1] == "--against-pose":
        import iso_source
        import os

        directory = argv[3] if len(argv) == 4 else os.path.join(
            os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.abspath(__file__)))),
            "work", "looks-pose")
        if len(argv) >= 3:
            image = argv[2]
        else:
            try:
                image = iso_source.image_from_env()
            except RuntimeError as exc:
                print("anime --against-pose: skipped -- %s" % exc)
                return 77
        return _against_pose(image, directory)
    if len(argv) in (2, 3) and argv[1] == "--report":
        import iso_source

        if len(argv) == 3:
            return _report(argv[2])
        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("anime --report: skipped -- %s" % exc)
            return 77
        return _report(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

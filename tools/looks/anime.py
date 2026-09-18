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

WHAT IS EXACT, AND WHAT THE GAME BLENDS
---------------------------------------
Both, and measured against the pose captures of both save states:

    96 of 96 pieces carry the angles the file holds at the pair the game was
    reading, integer for integer;
    90 of those 96 matrices come out EXACT -- every one of the nine
    halfwords -- and the other 6 are matrices the game BLENDED.

The link is the PAIR the game reads (`layout.ANIME_UNPACK`), not the frame the
animation state names: the state's frame is right for the outfield player and
wrong for the goalkeeper.

`rotation()` is the game's `RotMatrix` at 0x8003D4BC written out term by term,
not a rotation of the same name -- the order of its twelve shifts is what
makes it exact rather than one unit away.  The six that are not exact are the
game's own averaging path (`(a + b) >> 1` at 0x80011F90), and they are named
by a sweep of every pair in the file rather than by how far they missed:
`no_pair_explains()`.  What decides that blend is the animation state across
frames, which is LOOKS-TASK-32 and not this file.

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
WORD_OF_BOOT_PLACE = 0xFF1967F8  # not-an-address: a packed place
ANGLE_BITS = 10  # not-an-address: the width of one packed angle
ANGLE_SHIFT = 4  # not-an-address: how far the game shifts an angle left
ANGLE_STEP = 16  # not-an-address: the unit a stored angle is a multiple of
TURN = 4096  # not-an-address: angle units in a full turn, and 1.0 in 4.12
ONE = 4096  # not-an-address: 1.0 in the 4.12 fixed point the GTE uses
MATRIX_UNITS = 1  # not-an-address: the unit a wrong shift order costs
"""How far a matrix lands when the products are shifted in another order.

Kept because it is the measurement that found the right order: writing the
same nine terms with a single shift at the end, or composing `Rz . Ry . Rx`
with two shifts, lands ONE unit away on two thirds of the pieces -- 5 of 13
exact that way against 90 of 96 the game's way.  One unit of 4096 is invisible
in a drawing and total in a comparison."""

PIECE_ORDER = (
    "head", "torso", "upper arm a", "forearm a", "upper arm b", "forearm b",
    "thigh a", "shin a", "foot a", "thigh b", "shin b", "foot b",
)
"""Which piece each pair of a frame belongs to, in draw order.

**Measured, not assigned by shape.**  On 2026-09-18 the pose capture read the
three unpacked angles out of the scratchpad at every matrix load and they are,
pair for pair, the twelve pairs of the frame the animation state was playing
(`oracle.py --pose <SLOT> <N>` writes both, and `--check-image` here has no
way to check it -- what checks it is the capture).

**And this tuple was one place off until 2026-09-18, which is the whole of
LOOKS-TASK-27's blocker.**  The names come from the model pointer the game
holds when it loads a matrix, and that pointer is the piece it has just
DRAWN, not the one it is about to draw (`oracle.DRAW_LAG`): the matrix goes
in first and the piece's own pointers are armed after it.  Read one stop off,
the boot took the hip's matrix and the figure could not stand -- the boot came
out at thigh height with every piece individually plausible.  What settles it
is measured three ways and none of them is "it looks right":

    the ANKLE is rigid at this reading and at no other -- the boot's origin
    in the shin's own frame spreads 5 units across eight spread frames of
    both slots, against 156 one stop away (`oracle.py --pose-lag`);
    the a/b pairs become SYMMETRIC -- hips at -224 and -217, shoulders at
    -341 and -342, where the other reading puts one elbow above its own
    shoulder;
    the file's own places then stack the figure from the head at -420 to the
    boot at 0, which is the boot every other place is measured against.

**And the twelfth pair was called `root` until 2026-09-18** -- a piece that
draws nothing, whose only job was to be the origin (CORR-LOOKS-062).  It is
the SECOND BOOT, and the name was wrong because it is the one pair the capture
cannot name: the eleven others are named by the model pointer of the stop
after them, and the pass's first stop carries no pointer at all, so the piece
drawn by the twelfth matrix has nothing to name it.  Three measurements name
it, and the first is the same ankle the lag was settled by:

    in the FILE, over all seventeen frames of the screen's walk, the twelfth
    pair's place sits in shin b's own frame at a mean of (0.2, 69.1, -2.2)
    with a spread of at most 5.6 -- which is an ankle, and the same ankle
    shin a holds foot a at (0.3, 68.2, 3.3), spread at most 5.1.  Against
    shin a it spreads 356, and against the torso 229;
    in the CAPTURES, the twelfth stop's origin sits in shin b's own frame to
    within 4.8 units on slot 1 and 4.3 on slot 2, against 356.8 and 328.3
    against the other shin (`oracle.py --pose-lag`), and its rotation swings
    with the walk -- 4362 of spread across eight frames, tracking shin b's
    4074 -- where the camera is constant and different.  The docstring it replaces said that matrix
    "is the camera's to within a small turn", and it is not: the piece that
    barely moves is the torso, at 185;
    the arithmetic closes: twelve matrix loads a pass and twelve drawn
    sections (the head, plus 0..10 of the figure), eleven of them named by a
    pointer, and the one section no capture ever names is 10, the second boot.
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


POSITION_BITS = 11  # not-an-address: the width of the x and z fields
POSITION_Y_HIGH = 5  # not-an-address: bits 11..15 of the second word
POSITION_Y_LOW = 5  # not-an-address: bits 16..20, which come out lower


def position(word0: int, word1: int) -> tuple:
    """Where the piece sits, out of the pair's SECOND word.

    **The file carries the whole pose, angles and place.**  Measured on
    2026-09-18 against the captures of both save states: `x` is bits 10:0
    signed, `z` is bits 31:21 signed, and `y` is ten bits that the game
    reassembles SWAPPED -- bits 11..15 become the high five and bits 16..20 the
    low five -- with the top two bits of the FIRST word deciding its sign.

    That is the code at 0x80011F0C..0x80011F50 read back, and the check is the
    game's own translations: with the twelfth pair's place subtracted and the
    camera
    applied, they reproduce what the GTE was handed to within a few units.

    The places are relative to each other, not to the screen: what the figure
    is placed against is the twelfth pair's own place -- the second boot's,
    measured in CORR-LOOKS-062 -- and the camera carries the rest.
    """
    flags = word0 >> 30
    high = (word1 >> 6) & 0x3E0  # not-an-address: bits 11..15, moved up five
    low = (word1 >> 16) & 0x1F  # not-an-address: bits 16..20
    y = high | low
    y |= (flags - (flags & 2)) << 12
    if flags >> 1:
        y = -y
    return (_signed(word1, POSITION_BITS), y,
            _signed(word1 >> 21, POSITION_BITS))


def frame_angles(data: bytes, at: int) -> list:
    """The twelve pieces of one frame, each with its three angles."""
    if at + FRAME_BYTES > len(data):
        raise BadAnime("a frame at %d runs past the file's %d byte(s)"
                       % (at, len(data)))
    words = struct.unpack("<%dI" % (FRAME_BYTES // WORD),
                          data[at:at + FRAME_BYTES])
    return [{"piece": PIECE_ORDER[n], "angles": angles(words[n * 2]),
             "position": position(words[n * 2], words[n * 2 + 1]),
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


def _inverse(m: list):
    """The inverse of a 3x3, in floats -- only ever used to undo the camera."""
    det = (m[0] * (m[4] * m[8] - m[5] * m[7])
           - m[1] * (m[3] * m[8] - m[5] * m[6])
           + m[2] * (m[3] * m[7] - m[4] * m[6]))
    if not det:
        return None
    cofactors = [
        (m[4] * m[8] - m[5] * m[7]), -(m[1] * m[8] - m[2] * m[7]),
        (m[1] * m[5] - m[2] * m[4]),
        -(m[3] * m[8] - m[5] * m[6]), (m[0] * m[8] - m[2] * m[6]),
        -(m[0] * m[5] - m[2] * m[3]),
        (m[3] * m[7] - m[4] * m[6]), -(m[0] * m[7] - m[1] * m[6]),
        (m[0] * m[4] - m[1] * m[3]),
    ]
    return [value / det for value in cofactors]


def rotation(three: tuple) -> list:
    """The 4.12 rotation matrix of three angles, as the game builds it.

    **This is `RotMatrix` at 0x8003D4BC, not a rotation of the same name.**
    Disassembled on 2026-09-18 and written out term by term: the routine loads
    six table entries, then runs three `gpf sf` -- the GTE's interpolation,
    `IRn = (IR0 * IRn) >> 12` -- and assembles the nine halfwords out of the
    products, shifting by twelve at each step.  Writing the same products with
    a single shift at the end, or in another order, lands one unit away on
    two thirds of the pieces: measured, 5 of 13 exact that way against
    **90 of 96** this way.  The order of the shifts IS the answer.
    """
    ax, ay, az = three
    sx, cx = sin(ax), cos(ax)
    sy, cy = sin(ay), cos(ay)
    sz, cz = sin(az), cos(az)
    # The six products the first two `gpf` leave in IR1..IR3, each already
    # shifted -- t0..t5 in the routine's own registers.
    cx_sy = (cx * sy) >> 12
    cx_sz = (cx * sz) >> 12
    cx_cz = (cx * cz) >> 12
    sx_sy = (sx * sy) >> 12
    sx_sz = (sx * sz) >> 12
    sx_cz = (sx * cz) >> 12
    return [
        (cz * cy) >> 12, ((cz * sx_sy) >> 12) - cx_sz,
        ((cz * cx_sy) >> 12) + sx_sz,
        (sz * cy) >> 12, ((sz * sx_sy) >> 12) + cx_cz,
        ((sz * cx_sy) >> 12) - sx_cz,
        -sy, (cy * sx) >> 12, (cx * cy) >> 12,
    ]


def compose(camera: list, three: tuple) -> list:
    """The matrix the game hands the GTE for a piece: the camera over its turn.

    One shift of twelve at the end, arithmetic -- which is what the game does
    and what `(value + 2048) >> 12` is not: rounding here misses every piece.
    """
    return [value >> 12 for value in _product(camera, rotation(three))]


def no_pair_explains(data: bytes, camera: list, matrix: list) -> bool:
    """Is this matrix the turn of NO pair in the file, under this camera?

    The witness that a matrix is one the game BLENDED rather than one this
    module got wrong.  The game has a path that averages a fresh matrix with
    the one it kept (`(a + b) >> 1` at 0x80011F90), and the average of two
    turns is not the turn of anything stored.

    **It sweeps every pair of the file, and that is the point.**  The first
    witness tried was cheaper -- undo the camera, read the turn back, and call
    it a blend when the angles are not multiples of sixteen -- and it was
    wrong for one piece in six: the average of two triples 32 apart IS a
    multiple of sixteen, and that piece was reported as a defect.  A witness
    that can be fooled by arithmetic is not a witness.
    """
    for offset in range(HEADER_WORDS * WORD, len(data) - WORD, PAIR_BYTES):
        three = angles(struct.unpack("<I", data[offset:offset + WORD])[0])
        if compose(camera, three) == matrix:
            return False
    return True


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
    # is what the game had in its scratchpad when it drew `foot b` from that
    # frame (oracle.py --pose, 2026-09-18).
    ok("a word of the real file unpacks to what the game left in scratchpad",
       angles(WORD_OF_FRAME_FIVE)
       == (32, 4080, 4064),  # not-an-address: three angles
       "%r" % (angles(WORD_OF_FRAME_FIVE),))

    # -- the place, on words made here ---------------------------------
    ok("a second word of zero places the piece at the origin",
       position(0, 0) == (0, 0, 0))
    ok("x is the low eleven bits, signed", position(0, 1) == (1, 0, 0))
    ok("and it is signed",
       position(0, 1 << (POSITION_BITS - 1))
       == (-1024, 0, 0))  # not-an-address: a packed place
    ok("z is the top eleven bits, signed",
       position(0, 1 << 21) == (0, 0, 1))
    ok("y comes out of bits 11..20, swapped",
       position(0, 1 << 16) == (0, 1, 0), "%r" % (position(0, 1 << 16),))
    ok("and the high five of y are bits 11..15",
       position(0, 1 << 11) == (0, 32, 0), "%r" % (position(0, 1 << 11),))
    # The pair the capture read for the twelfth piece in frame 5 of the screen's
    # animation, and the place it put it at.
    ok("the real pair places the second boot where the game placed it",
       position(WORD_OF_FRAME_FIVE, WORD_OF_BOOT_PLACE) == (-8, -409, -8),
       "%r" % (position(WORD_OF_FRAME_FIVE, WORD_OF_BOOT_PLACE),))

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

    # -- what the run leaves out, and saying so (CORR-LOOKS-061) ------------
    def capture(slot, frame, paired):
        return {"slot": slot, "frame": frame, "unpacked": 12 if paired else 0,
                "pieces": [{"piece": "head", "pair": 3 if paired else None}]}

    made_captures = [capture(1, 0, True), capture(1, 40, False),
                     capture(2, 0, True), capture(2, 40, False)]
    judged, aside = split_captures(made_captures)
    ok("a capture with no pair on any piece is set aside, not judged",
       [capture_name(one) for one in judged] == ["slot1-frame0", "slot2-frame0"]
       and [capture_name(one) for one in aside] == ["slot1-frame40",
                                                    "slot2-frame40"],
       "%r / %r" % (judged, aside))
    ok("the floor sits under the measured half, so half judged passes",
       len(judged) >= JUDGED_FLOOR * len(made_captures))
    thin = [capture(1, 0, True)] + [capture(1, n, False)
                                    for n in range(1, 16)]
    ok("and the run the floor exists for -- one capture carrying the verdict "
       "-- falls under it",
       len(split_captures(thin)[0]) == 1
       and len(split_captures(thin)[0]) < JUDGED_FLOOR * len(thin))

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

    The link is the PAIR the game was reading -- `layout.ANIME_UNPACK_BASE` at
    the instruction that reads it -- and not the frame the animation state
    names.  The difference is not a nicety: the state's frame is right for the
    outfield player and wrong for the goalkeeper, whose angles then match
    nothing in 3952 frames (measured 2026-09-18, 80 of 96 pieces).  A pointer
    that says where the game IS reading beats one that says what it is playing.

    Two numbers come out and neither is rounded into the other: how many
    pieces carry the angles the file holds at that pair, and how far the
    matrix built from them lands from the one the game loaded.
    """
    exact = wrong = pieces = matrix_exact = unlinked = blended = 0
    worst = 0
    off = []
    for record in captures:
        camera = record["camera"]["rotation"]
        for piece in record["pieces"]:
            pieces += 1
            at = piece.get("pair")
            if at is None:
                # The first load of a pass can come before any unpack stop,
                # so the pair is not known for it.  It is one piece of twelve
                # and it is counted, not guessed at.
                unlinked += 1
                continue
            if not 0 <= at <= len(data) - PAIR_BYTES:
                raise BadAnime("a piece read a pair at %d, outside the %d "
                               "byte(s) of %s" % (at, len(data), layout.ANIME))
            three = angles(struct.unpack("<I", data[at:at + WORD])[0])
            if three != tuple(piece["angles"]):
                wrong += 1
                continue
            exact += 1
            built = compose(camera, three)
            apart = max(abs(a - b) for a, b in zip(built, piece["rotation"]))
            worst = max(worst, apart)
            if apart == 0:
                matrix_exact += 1
            elif no_pair_explains(data, camera, piece["rotation"]):
                blended += 1
            else:
                off.append((apart, record["slot"], record["frame"],
                            piece["id"]))
    return {"captures": len(captures), "pieces": pieces, "exact": exact,
            "wrong": wrong, "unlinked": unlinked, "blended": blended,
            "matrix_exact": matrix_exact, "matrix_worst": worst,
            "off": sorted(off, reverse=True)}


def _pairs_by_position(data: bytes) -> list:
    """Every angle triple the file holds, kept by which pair carries it."""
    index = [set() for _ in range(PIECE_PAIRS)]
    for one in blocks(data):
        for at in one["frames"]:
            for position, piece in enumerate(frame_angles(data, at)):
                index[position].add(piece["angles"])
    return index


JUDGED_FLOOR = 1.0 / 3.0
"""The share of captures that has to carry a pair for a run to mean anything.

A capture whose pass never stopped at the unpack routine has no pair beside any
piece, and the angles in it are whatever the scratchpad still held -- they are
NOT what that frame drew, so judging them would measure the leftovers.  Setting
them aside is right; doing it in silence is not, and until CORR-LOOKS-061 half
the captures left the run without a line saying so.

Measured on 2026-09-18, twice: **8 of 16** captures carry pairs, the same eight
frames both times.  The floor sits at a third, well under the measured half,
because a floor written AT the measurement turns ordinary variation into a red
(trap 49 of the profile).  What it has to catch is the run where the stop moves
and one or two captures carry the whole verdict.
"""


def split_captures(records: list) -> tuple:
    """(judged, set aside): a capture with no pair on any piece is set aside."""
    judged, aside = [], []
    for one in records:
        paired = sum(1 for piece in one["pieces"]
                     if piece.get("pair") is not None)
        (judged if paired else aside).append(one)
    return judged, aside


def capture_name(one: dict) -> str:
    return "slot%s-frame%s" % (one.get("slot"), one.get("frame"))


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
    records = _load_captures(directory)
    captures, aside = split_captures(records)
    if not captures:
        print("anime --against-pose: skipped -- %s holds no capture with the "
              "pair beside each piece" % directory)
        return 77
    with iso_source.open_disc(image_path) as disc:
        data = read(disc)
    found = against_pose(data, captures)
    print("  %d of %d capture(s) judged, %d piece(s) of %d drawn"
          % (len(captures), len(records), found["pieces"],
             sum(len(one["pieces"]) for one in records)))
    if aside:
        print("  %d set aside -- the pass never stopped at the unpack, so the "
              "angles beside each piece are the scratchpad's, not that "
              "frame's: %s" % (len(aside),
                               ", ".join(capture_name(one) for one in aside)))
    print("  %d of %d carry the angles the file holds at the pair the game "
          "read, integer for integer" % (found["exact"], found["pieces"]))
    print("  %d piece(s) drew before any unpack stop, so no pair names them"
          % found["unlinked"])
    print("  %d matrices of %d are EXACT, %d are blends the game made, and %d "
          "are neither" % (found["matrix_exact"], found["exact"],
                           found["blended"], len(found["off"])))
    failures = 0
    if len(captures) < JUDGED_FLOOR * len(records):
        print("  FAIL  only %d of %d capture(s) carry a pair, under the %.0f%% "
              "this run needs to mean anything -- the unpack stop moved, and "
              "a verdict drawn from what is left describes those frames, not "
              "the animation"
              % (len(captures), len(records), JUDGED_FLOOR * 100))
        failures += 1
    if found["wrong"]:
        print("  FAIL  %d piece(s) carry angles the pair does not hold -- the "
              "decode is wrong, not the game" % found["wrong"])
        failures += 1
    for apart, slot, frame, name in found["off"]:
        print("  FAIL  slot %d frame %d: %s is %d apart, and a pair of the "
              "file DOES reproduce it -- the pair this piece was given is "
              "the wrong one" % (slot, frame, name, apart))
        failures += 1
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

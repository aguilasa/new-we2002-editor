#!/usr/bin/env python3
"""What `HEIG` and `BODY` do to the drawing: a scale, per axis, in the camera.

Measured on 2026-09-18 (LOOKS-TASK-29), and the answer is neither "nothing" nor
"a scale in height".  The game keeps one scale vector for the figure,

    h = HEIG + 148
    x = z = (h << 12) / (table[BODY] + 10)
    y     = (h << 12) / 180

and applies it to the COLUMNS of the figure's own rotation, truncating toward
zero, before the view matrix is multiplied in.  So `HEIG` scales all three
axes -- a taller player is also a wider one -- and `BODY` scales only x and z,
the width and the depth, with `H TYPE` the one build as wide as it is tall.
The pose does not change: the scale is inside the camera the pose is composed
with, which is why every piece of a taller figure comes out taller with the
pose file untouched.

**Nothing of the rule is written here.**  The bias, the shift, the divisor of
the height, the ten added to the table and the table itself are read out of
`/SELECT8.BIN`, the overlay that runs the screen, by decoding the instructions
`layout.STATURE_*` names -- and each one is refused unless it is the
instruction it is said to be.  A rule copied out of a debugger session into a
constant would be right until the day it was not, and nothing would say so.

The chain, integer for integer as the hardware computes it:

    camera = (VIEW . trunc(ROT . diag(scale))) >> 12
    piece  = (camera . pose) >> 12

`oracle.py --stature` measures it against the game: 56 heights, 8 builds and
the pieces of the passes that carry a pair, both slots, exact.
"""

from __future__ import annotations

import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402

SKIP = 77

ONE = 4096  # not-an-address: 1.0 in 4.12
FRACTION = 12
"""Bits of fraction in every matrix and scale here."""

WORD = 4
HALF = (1 << 16) - 1
"""Mask of a 16-bit immediate.  A shift and not a hex literal: rule 1 reads
hex as an address, and what makes this not one is that it is a field width."""

WIDE = 1 << 32
"""The span of a 32-bit word, for the signed reading of the magic."""

ADDIU, LUI, ORI, LBU, SW = 9, 15, 13, 36, 43
SPECIAL_SLL, SPECIAL_SRA = 0, 3
"""The MIPS opcodes (and the two SPECIAL functions) the rule is made of."""

BUILDS = 8
"""`BODY` has eight values, A to H (`looks.FIELDS`)."""


class BadStature(Exception):
    """The overlay does not hold the rule where the rule was measured."""


# --- reading the rule off the disc ------------------------------------------

def _word(code: bytes, address: int) -> int:
    at = address - layout.SELECT8_BASE
    if not 0 <= at <= len(code) - WORD:
        raise BadStature("%s is outside the overlay's %d bytes"
                         % (hex(address), len(code)))
    return struct.unpack_from("<I", code, at)[0]


def _signed16(value: int) -> int:
    value &= HALF
    return value - (1 << 16) if value >= 1 << 15 else value


def _fields(word: int) -> dict:
    return {"op": word >> 26, "rs": (word >> 21) & 31, "rt": (word >> 16) & 31,
            "rd": (word >> 11) & 31, "sa": (word >> 6) & 31,
            "funct": word & 63, "imm": word & HALF}


def _expect(code: bytes, address: int, op: int, funct: int = None,
            what: str = "") -> dict:
    found = _fields(_word(code, address))
    if found["op"] != op or (funct is not None and found["funct"] != funct):
        raise BadStature("%s is not the %s the stature rule was read from "
                         "(opcode %d, function %d)"
                         % (hex(address), what, found["op"], found["funct"]))
    return found


def rule(code: bytes) -> dict:
    """The stature rule, decoded out of `/SELECT8.BIN`.

    {"bias", "shift", "height_divisor", "table", "extra"} -- and a refusal if
    any of the nine instructions is not what it was measured to be.
    """
    bias = _expect(code, layout.STATURE_HEIGHT_BIAS, ADDIU, what="addiu")
    shift = _expect(code, layout.STATURE_HEIGHT_SHIFT, 0, SPECIAL_SLL, "sll")
    load = _expect(code, layout.STATURE_TABLE_LOAD, LBU, what="lbu")
    extra = _expect(code, layout.STATURE_TABLE_EXTRA, ADDIU, what="addiu")
    high = _expect(code, layout.STATURE_MAGIC_HIGH, LUI, what="lui")
    low = _expect(code, layout.STATURE_MAGIC_LOW, ORI, what="ori")
    post = _expect(code, layout.STATURE_MAGIC_SHIFT, 0, SPECIAL_SRA, "sra")
    width = [_expect(code, one, SW, what="sw")
             for one in layout.STATURE_WIDTH_STORES]
    height = _expect(code, layout.STATURE_HEIGHT_STORE, SW, what="sw")

    # The table's address, as the `lbu` itself computes it: `at` holds the
    # upper half the code put there (0x800F0000) plus BODY, and the load adds
    # its signed offset.  Derived, and then held against the one layout names.
    upper = (layout.STATURE_TABLE >> 16) + 1
    derived = (upper << 16) + _signed16(load["imm"])
    if derived != layout.STATURE_TABLE:
        raise BadStature("the table load reads %s, and the table was measured "
                         "at %s" % (hex(derived), hex(layout.STATURE_TABLE)))
    at = layout.STATURE_TABLE - layout.SELECT8_BASE
    table = list(code[at:at + BUILDS])

    # The divisor behind the multiply: `hi = x * M >> 32` (M signed), then
    # `(hi + x) >> s`, is x * (1 + M / 2^32) / 2^s -- a division by
    # 2^(32 + s) / (2^32 + M).
    magic = (high["imm"] << 16) | low["imm"]
    if magic >= WIDE // 2:
        magic -= WIDE
    divisor = (1 << (32 + post["sa"])) / float(WIDE + magic)
    whole = int(round(divisor))
    if abs(divisor - whole) > 1e-3:
        raise BadStature("the magic %d with a shift of %d divides by %.4f, "
                         "not by a whole number" % (magic, post["sa"], divisor))
    # Which words the two results go to: x and z take the table's quotient,
    # y the magic's.  This is the fact that says which axis HEIG alone decides.
    axes = sorted(one["imm"] for one in width) + [height["imm"]]
    if not (axes[1] - axes[0] == 2 * WORD and axes[2] - axes[0] == WORD):
        raise BadStature("the stores go to offsets %r, which are not x and z "
                         "for the table and y for the height" % (axes,))
    return {"bias": _signed16(bias["imm"]), "shift": shift["sa"],
            "height_divisor": whole, "table": table,
            "extra": _signed16(extra["imm"])}


def _divide(numerator: int, denominator: int) -> int:
    """MIPS `div`: the quotient truncated toward zero."""
    quotient = abs(numerator) // abs(denominator)
    return quotient if (numerator >= 0) == (denominator > 0) else -quotient


def scale(found: dict, height: int, build: int) -> tuple:
    """(x, y, z) in 4.12 for a height in cm and a `BODY` index 0..7.

    *height* is what the screen writes (`175 cm`), which is the field plus the
    bias -- the same number `looks.py` decodes, so either may be passed here.
    """
    if not 0 <= build < len(found["table"]):
        raise BadStature("BODY %d, and the table has %d builds"
                         % (build, len(found["table"])))
    numerator = height << found["shift"]
    across = _divide(numerator, found["table"][build] + found["extra"])
    return (across, _divide(numerator, found["height_divisor"]), across)


# --- the chain ----------------------------------------------------------------

def scale_columns(matrix: list, vector) -> list:
    """`ScaleMatrix`: column j times vector[j], truncated toward zero.

    The truncation is the code's -- `bgez`, add 4095, `sra 12` -- and not the
    GTE's floor, and it matters: flooring lands one unit off on the negative
    terms.

    Columns, as the code indexes them -- and what can NOT be told from the
    game's numbers: with x and z scaled alike and the figure turned about y
    only, scaling the rows gives the same nine integers.  So a slip between
    the two is invisible on this screen, and no check here pretends to catch
    it; `camera` refuses any other turn, which is where it would start to show.
    """
    return [_divide(matrix[row * 3 + column] * vector[column], ONE)
            for row in range(3) for column in range(3)]


def gte_product(one: list, two: list) -> list:
    """`one . two` as the GTE's `mvmva sf` computes it: sum, then `>> 12`.

    An arithmetic shift, so negative results round toward minus infinity, and
    IR saturates at 16 bits.
    """
    out = []
    for row in range(3):
        for column in range(3):
            total = sum(one[row * 3 + k] * two[k * 3 + column]
                        for k in range(3)) >> FRACTION
            out.append(max(-(1 << 15), min((1 << 15) - 1, total)))
    return out


def gte_vector(matrix: list, vector, translation) -> list:
    """`mvmva sf` with a translation: T + (M . v) >> 12, the piece's place."""
    return [translation[row] + (sum(matrix[row * 3 + k] * vector[k]
                                    for k in range(3)) >> FRACTION)
            for row in range(3)]


def camera(chain: dict, vector) -> dict:
    """The camera the game hands the GTE, for one scale vector.

    *chain* is what `oracle.py --camera` read at `layout.CAMERA_BUILD`: the
    view's rotation and translation, and the figure's angles and place.  The
    figure's rotation is `anime.rotation` of the angles -- the pose's routine,
    which reproduced the measured loads exactly (the build itself calls a
    sibling at 0x8003D6BC that this cycle has not disassembled; with only a
    turn about y the two cannot disagree, and a chain that ever carries
    another angle is refused rather than trusted).
    """
    import anime

    angles = tuple(chain["angles"])
    if angles[0] or angles[2]:
        raise BadStature("the figure's angles %r turn about more than y, and "
                         "the routine the game uses for them is not the one "
                         "measured here" % (angles,))
    figure = scale_columns(anime.rotation(angles), vector)
    view = chain["view"]
    return {"rotation": gte_product(view["rotation"], figure),
            "translation": gte_vector(view["rotation"], chain["place"],
                                      view["translation"])}


def piece(matrix: dict, pose: list, place) -> tuple:
    """(rotation, translation) of one piece under *matrix*, as the GTE has it."""
    return (gte_product(matrix["rotation"], pose),
            gte_vector(matrix["rotation"], place, matrix["translation"]))


# --- self-check ---------------------------------------------------------------

def _encode(op: int, rs: int = 0, rt: int = 0, imm: int = 0, rd: int = 0,
            sa: int = 0, funct: int = 0) -> bytes:
    if op:
        word = (op << 26) | (rs << 21) | (rt << 16) | (imm & HALF)
    else:
        word = (rs << 21) | (rt << 16) | (rd << 11) | (sa << 6) | funct
    return struct.pack("<I", word)


def synthetic_overlay(table=(210, 200, 195, 190, 185, 180, 175, 170),
                      magic=(46603, 24759),  # not-an-address: lui/ori halves
                      post=7) -> bytearray:
    """An overlay with the rule's nine instructions where layout says.

    The words are the ones the real file holds, assembled here from their
    fields so that the check runs with no disc; `table`, the magic and the
    post-shift are arguments so that a red case can change one of them.
    """
    size = layout.STATURE_TABLE - layout.SELECT8_BASE + BUILDS
    code = bytearray(size)

    def put(address, raw):
        at = address - layout.SELECT8_BASE
        code[at:at + WORD] = raw

    put(layout.STATURE_HEIGHT_BIAS, _encode(ADDIU, 2, 2, 148))
    put(layout.STATURE_HEIGHT_SHIFT, _encode(0, 0, 2, rd=2, sa=12,
                                             funct=SPECIAL_SLL))
    put(layout.STATURE_TABLE_LOAD,
        _encode(LBU, 1, 3, layout.STATURE_TABLE
                - ((layout.STATURE_TABLE >> 16) + 1 << 16)))
    put(layout.STATURE_TABLE_EXTRA, _encode(ADDIU, 3, 3, 10))
    put(layout.STATURE_MAGIC_HIGH, _encode(LUI, 0, 5, magic[0]))
    put(layout.STATURE_MAGIC_LOW, _encode(ORI, 5, 5, magic[1]))
    put(layout.STATURE_MAGIC_SHIFT, _encode(0, 0, 3, rd=3, sa=post,
                                            funct=SPECIAL_SRA))
    put(layout.STATURE_WIDTH_STORES[0], _encode(SW, 6, 2, 40))
    put(layout.STATURE_WIDTH_STORES[1], _encode(SW, 6, 2, 48))
    put(layout.STATURE_HEIGHT_STORE, _encode(SW, 6, 3, 44))
    at = layout.STATURE_TABLE - layout.SELECT8_BASE
    code[at:at + BUILDS] = bytes(table)
    return code


MEASURED_CHAIN = {
    "view": {"rotation": [4096, 0, 0, 0, 2560, 171, 0, -275, 4096],  # not-an-address: 4.12 matrix
             "translation": [0, 128, 3072]},  # not-an-address: units
    "angles": [0, 128, 0],
    "place": [-480, 32, 1056],  # not-an-address: units
}
"""The chain as `oracle.py --camera` read it on 2026-09-18, identical in both
slots -- kept here as the check's fixture, so that the rule is held against
numbers the GAME produced without a disc or an emulator in the room."""

MEASURED_LOADS = (
    (175, 0, [3195, 0, 635, -27, 2488, 133, -635, -268, 3195]),  # not-an-address: 4.12
    (155, 0, [2829, 0, 562, -24, 2204, 118, -562, -237, 2829]),  # not-an-address: 4.12
    (210, 0, [3833, 0, 762, -32, 2986, 160, -762, -321, 3833]),  # not-an-address: 4.12
    (175, 7, [3905, 0, 776, -33, 2488, 163, -776, -268, 3905]),  # not-an-address: 4.12
)
"""(height, BODY, the camera `POSE_MATRIX` loaded) -- four loads read on
2026-09-18: the two ends of HEIG, the state's own value, and the widest BODY.
`oracle.py --stature` re-reads them with every other value of both rows."""


def self_check(verbose: bool = True) -> int:
    return harness.run("stature.py", _checks, verbose=verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    found = attempt("the rule decodes out of a synthetic overlay",
                    lambda: rule(bytes(synthetic_overlay())))
    if found is None:
        return
    ok("the bias is the one looks.py decodes HEIG with",
       found["bias"] == 148, "%r" % (found,))
    ok("the magic and the shift divide the height by a whole number",
       found["height_divisor"] == 180, "%r" % (found,))
    ok("the width divisor is the table plus ten",
       found["extra"] == 10 and found["table"][0] == 210, "%r" % (found,))

    # The scale vectors the game held, read at FIGURE_SCALE on 2026-09-18.
    ok("175 cm, A TYPE is (3258, 3982, 3258), the save states' own",
       scale(found, 175, 0) == (3258, 3982, 3258),  # not-an-address: 4.12
       "%r" % (scale(found, 175, 0),))
    ok("210 cm widens x and z with y (3909, 4778, 3909)",
       scale(found, 210, 0) == (3909, 4778, 3909))  # not-an-address: 4.12
    ok("H TYPE is as wide as it is tall (3982, 3982, 3982)",
       scale(found, 175, 7) == (3982, 3982, 3982))  # not-an-address: 4.12
    ok("the quotient truncates: 176 cm is 4004 in y, not the 4005 rounding "
       "gives", scale(found, 176, 0)[1] == 4004)  # not-an-address: 4.12

    for height, build, load in MEASURED_LOADS:
        got = camera(MEASURED_CHAIN, scale(found, height, build))
        ok("the chain reproduces the game's load at %d cm, BODY %d"
           % (height, build), got["rotation"] == load,
           "%r against %r" % (got["rotation"], load))
    ok("and the camera's translation does not move with the scale",
       camera(MEASURED_CHAIN, scale(found, 155, 0))["translation"]
       == camera(MEASURED_CHAIN, scale(found, 210, 7))["translation"]
       == [-480, 192, 4125])  # not-an-address: units

    # -- red: a rule that is not the one read must not pass for it --------
    halved = attempt("a post-shift of 6 still decodes",
                     lambda: rule(bytes(synthetic_overlay(post=6))))
    ok("and it decodes to the divisor it implies, 90, not to 180",
       halved is not None and halved["height_divisor"] == 90, "%r" % (halved,))
    broken = synthetic_overlay()
    at = layout.STATURE_MAGIC_HIGH - layout.SELECT8_BASE
    broken[at:at + WORD] = _encode(ADDIU, 0, 5, 1)
    try:
        rule(bytes(broken))
    except BadStature as exc:
        ok("an instruction that is not the lui is refused, by address",
           hex(layout.STATURE_MAGIC_HIGH) in str(exc), str(exc))
    else:
        ok("an instruction that is not the lui is refused", False)
    swapped = [scale(found, 210, 0)[1], scale(found, 210, 0)[0],
               scale(found, 210, 0)[1]]
    ok("height on the wrong axis does NOT reproduce the load",
       camera(MEASURED_CHAIN, swapped)["rotation"] != MEASURED_LOADS[2][2])
    try:
        camera(dict(MEASURED_CHAIN, angles=[16, 128, 0]), (ONE, ONE, ONE))
    except BadStature:
        ok("angles beyond y are refused, not trusted", True)
    else:
        ok("angles beyond y are refused, not trusted", False)


def _check_image(image: str) -> int:
    """`--check-image`: the rule off the real overlay, against the fixtures."""
    import iso_source

    with iso_source.open_disc(image) as disc:
        code = disc.read(layout.SELECT8)
    found = rule(code)
    print("stature: h = HEIG + %d; x = z = (h << %d) / (table[BODY] + %d); "
          "y = (h << %d) / %d" % (found["bias"], found["shift"],
                                  found["extra"], found["shift"],
                                  found["height_divisor"]))
    print("  table %s -> width divisors %s"
          % (found["table"], [one + found["extra"] for one in found["table"]]))
    failures = 0
    for height, build, load in MEASURED_LOADS:
        got = camera(MEASURED_CHAIN, scale(found, height, build))["rotation"]
        mark = "ok" if got == load else "DIFFERS"
        failures += got != load
        print("  %d cm, BODY %s: scale %s  camera %s"
              % (height, "ABCDEFGH"[build], scale(found, height, build), mark))
    print("stature --check-image: %d problem(s)" % failures)
    return 1 if failures else 0


def main(argv: list) -> int:
    if len(argv) >= 2 and argv[1] == "--check-image":
        import iso_source

        if len(argv) > 2:
            return _check_image(argv[2])
        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("stature --check-image: skipped -- %s" % exc)
            return SKIP
        return _check_image(image)
    return self_check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))

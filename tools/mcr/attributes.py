#!/usr/bin/env python3
"""The 12-byte player attribute codec, written twice on purpose.

Provenance (section 3.4 of the plan):

  container   --
  address     none of its own; the record's base and stride live in `layout.py`
  semantics   the upstream (field names and domains)
  codec       `src/core/Player.cpp` -- NORMATIVE

This is the only part of the port that is born with an oracle already in the
house, and section 1.4 of the plan says why: `Player.cpp` unpacks the same 12
bytes, and the upstream describes the same packing in a different shape. So the
expensive part here is not reverse engineering -- it is two implementations that
have to agree, and disagreeing is measurable without an emulator, without Wine
and without a disc.

TWO IMPLEMENTATIONS, AND WHY THEY ARE REALLY TWO:

  `decode_stream`/`encode_stream`  the upstream's shape: the 12 bytes as one
      96-bit little-endian stream, each field at a declared (offset, width).
      That is literally what its `algoritmo1`/`algoritmo2` do -- they sum
      pre-weighted values with a carry across byte boundaries.

  `decode_masks`/`encode_masks`    `Player.cpp` transcribed verbatim, mask by
      mask and shift by shift, including the order of the read-modify-write
      pairs, which is load-bearing (see the comment at the top of that file).

Neither is derived from the other. Agreement between a bit-offset table and a
pile of hand-written masks is evidence; agreement between two spellings of the
same expression would not be.

MEASURED, not assumed: the upstream stores each field's weight table as
`index << shift` in a hidden combo box, and all 21 of the stream fields' shifts
match `Player.cpp`. `--upstream-weights` re-measures that against the VB source
when the clone is present.

Usage:

    python3 tools/mcr/attributes.py <card.mcr>
    python3 tools/mcr/attributes.py <card.mcr> --player 0
    python3 tools/mcr/attributes.py --self-check
    python3 tools/mcr/attributes.py --upstream-weights work/easy-mcr
"""

import argparse
import dataclasses
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout                                            # noqa: E402
from card import Card                                    # noqa: E402

BLOB_BYTES = 12
BLOB_BITS = BLOB_BYTES * 8


class AttributeError_(Exception):
    """A value that does not fit the field, or a blob that is not 12 bytes."""


@dataclasses.dataclass(frozen=True)
class Field:
    """One field of the record, as a run of bits in the little-endian stream.

    `bias` is what the game adds on display: the sixteen skill attributes are
    stored 0..7 and shown 12..19, height is stored 0..63 and shown 148..211,
    age 0..31 shown 15..46, and the shirt number is stored one less than it is
    worn. Storing the bias here and not in the caller is what keeps the two
    implementations comparable -- both return the displayed value.
    """

    name: str
    offset: int          # absolute bit offset into the 96-bit stream
    width: int
    bias: int = 0

    @property
    def byte(self) -> int:
        return self.offset // 8

    @property
    def shift(self) -> int:
        return self.offset % 8

    @property
    def low(self) -> int:
        return self.bias

    @property
    def high(self) -> int:
        return self.bias + (1 << self.width) - 1


# The record, in stream order. Bytes 0..3 carry the identity and the shirt
# number; bytes 4..11 are the run the upstream builds with its carry algorithm.
FIELDS: tuple[Field, ...] = (
    Field("position", 0, 3),
    Field("hair_style", 4, 5),
    Field("hair_colour", 9, 3),
    Field("beard_style", 13, 3),
    Field("beard_colour", 17, 3),
    Field("height", 20, 6, bias=148),
    Field("number", 26, 5, bias=1),
    Field("out_of_position", 31, 1),
    Field("skin_colour", 32, 2),
    Field("build", 34, 3),
    Field("age", 37, 5, bias=15),
    Field("reflexes", 42, 3, bias=12),
    Field("strength", 46, 3, bias=12),
    Field("stamina", 49, 3, bias=12),
    Field("dribbling", 52, 3, bias=12),
    Field("speed", 55, 3, bias=12),
    Field("acceleration", 58, 3, bias=12),
    Field("attack", 61, 3, bias=12),
    Field("defence", 64, 3, bias=12),
    Field("shot_power", 67, 3, bias=12),
    Field("shot_accuracy", 70, 3, bias=12),
    Field("passing", 73, 3, bias=12),
    Field("technique", 76, 3, bias=12),
    Field("heading", 79, 3, bias=12),
    Field("jump", 82, 3, bias=12),
    Field("swerve", 85, 3, bias=12),
    Field("aggression", 88, 3, bias=12),
    Field("boots", 91, 3),
    Field("foot", 94, 2),
)

BY_NAME = {f.name: f for f in FIELDS}

# The bits no field claims. NOT padding to be zeroed: they are bits of a record
# nobody in either implementation decodes, and section 6 of the plan says the
# encoder preserves what it does not understand. Computed, so that editing
# FIELDS cannot leave this list lying about what it covers.
GAP_BITS = tuple(b for b in range(BLOB_BITS)
                 if not any(f.offset <= b < f.offset + f.width for f in FIELDS))


def _require_blob(blob: bytes) -> None:
    if len(blob) != BLOB_BYTES:
        raise AttributeError_(
            f"the attribute blob is {BLOB_BYTES} bytes, got {len(blob)}")


# --- implementation A: the stream (the upstream's shape) -------------------

def _read_bits(blob: bytes, offset: int, width: int) -> int:
    value = int.from_bytes(blob, "little")
    return (value >> offset) & ((1 << width) - 1)


def _write_bits(blob: bytearray, offset: int, width: int, raw: int) -> None:
    mask = ((1 << width) - 1) << offset
    value = int.from_bytes(blob, "little")
    value = (value & ~mask) | ((raw << offset) & mask)
    blob[:] = value.to_bytes(BLOB_BYTES, "little")


def decode_stream(blob: bytes) -> dict[str, int]:
    _require_blob(blob)
    return {f.name: _read_bits(blob, f.offset, f.width) + f.bias
            for f in FIELDS}


def encode_stream(values: dict[str, int], blob: bytes) -> bytes:
    """Read-modify-write. Every bit outside FIELDS comes through untouched."""
    _require_blob(blob)
    out = bytearray(blob)
    for f in FIELDS:
        if f.name not in values:
            continue
        raw = values[f.name] - f.bias
        if not 0 <= raw < (1 << f.width):
            raise AttributeError_(
                f"{f.name}={values[f.name]} is outside {f.low}..{f.high}")
        _write_bits(out, f.offset, f.width, raw)
    return bytes(out)


# --- implementation B: the masks (`Player.cpp`, verbatim) ------------------
# Transcribed from src/core/Player.cpp. The masks, the shifts and the ORDER of
# the read-modify-write pairs are unchanged -- Encode() there clears and sets
# overlapping bits in a specific sequence, and reordering two adjacent lines can
# change the result. It reads oddly in Python on purpose: this is a transcript,
# not a rewrite, and the point is for it to be wrong in different ways than the
# stream is if either is wrong at all.

def decode_masks(raw: bytes) -> dict[str, int]:
    _require_blob(raw)
    v = {}
    v["position"] = raw[0] & 0x07
    v["skin_colour"] = raw[4] & 0x03
    v["hair_style"] = ((raw[0] >> 4) & 0x0F) + ((raw[1] << 4) & 0x10)
    v["hair_colour"] = (raw[1] >> 1) & 0x07
    v["beard_style"] = (raw[1] >> 5) & 0x07
    v["beard_colour"] = (raw[2] >> 1) & 0x07
    v["height"] = 148 + ((raw[2] >> 4) & 0x0F) + ((raw[3] << 4) & 0x30)
    v["build"] = (raw[4] >> 2) & 0x07
    v["age"] = 15 + ((raw[4] >> 5) & 0x07) + ((raw[5] << 3) & 0x18)
    v["boots"] = (raw[11] >> 3) & 0x07
    v["foot"] = (raw[11] >> 6) & 0x03
    v["attack"] = 12 + ((raw[7] >> 5) & 0x07)
    v["defence"] = 12 + (raw[8] & 0x07)
    v["strength"] = 12 + ((raw[5] >> 6) & 0x03) + ((raw[6] << 2) & 0x04)
    v["stamina"] = 12 + ((raw[6] >> 1) & 0x07)
    v["speed"] = 12 + ((raw[6] >> 7) & 0x01) + ((raw[7] << 1) & 0x06)
    v["acceleration"] = 12 + ((raw[7] >> 2) & 0x07)
    v["passing"] = 12 + ((raw[9] >> 1) & 0x07)
    v["shot_power"] = 12 + ((raw[8] >> 3) & 0x07)
    v["shot_accuracy"] = 12 + ((raw[8] >> 6) & 0x03) + ((raw[9] << 2) & 0x04)
    v["jump"] = 12 + ((raw[10] >> 2) & 0x07)
    v["heading"] = 12 + ((raw[9] >> 7) & 0x01) + ((raw[10] << 1) & 0x06)
    v["technique"] = 12 + ((raw[9] >> 4) & 0x07)
    v["dribbling"] = 12 + ((raw[6] >> 4) & 0x07)
    v["swerve"] = 12 + ((raw[10] >> 5) & 0x07)
    v["aggression"] = 12 + (raw[11] & 0x07)
    v["reflexes"] = 12 + ((raw[5] >> 2) & 0x07)
    v["out_of_position"] = (raw[3] >> 7) & 0x01
    v["number"] = 1 + ((raw[3] >> 2) & 0x1F)
    return v


def encode_masks(v: dict[str, int], blob: bytes) -> bytes:
    _require_blob(blob)
    r = bytearray(blob)
    r[3] &= 0x01
    r[3] |= (v["number"] - 1) << 2
    r[3] &= 0x7F
    r[3] |= v["out_of_position"] << 7
    r[0] &= 0xF8
    r[0] |= v["position"]
    r[4] &= 0xFC
    r[4] |= v["skin_colour"]
    r[0] &= 0x0F
    r[0] |= (v["hair_style"] << 4) & 0xFF
    r[1] &= 0xFE
    r[1] |= v["hair_style"] >> 4
    r[1] &= 0xF1
    r[1] |= v["hair_colour"] << 1
    r[1] &= 0x1F
    r[1] |= (v["beard_style"] << 5) & 0xFF
    r[2] &= 0xF1
    r[2] |= v["beard_colour"] << 1
    r[2] &= 0x0F
    r[2] |= ((v["height"] - 148) << 4) & 0xFF
    r[3] &= 0xFC
    r[3] |= (v["height"] - 148) >> 4
    r[4] &= 0xE3
    r[4] |= v["build"] << 2
    r[4] &= 0x1F
    r[4] |= ((v["age"] - 15) << 5) & 0xFF
    r[5] &= 0xFC
    r[5] |= (v["age"] - 15) >> 3
    r[11] &= 0xC7
    r[11] |= v["boots"] << 3
    r[11] &= 0x3F
    r[11] |= (v["foot"] << 6) & 0xFF
    r[7] &= 0x1F
    r[7] |= ((v["attack"] - 12) << 5) & 0xFF
    r[8] &= 0xF8
    r[8] |= v["defence"] - 12
    r[5] &= 0x3F
    r[5] |= ((v["strength"] - 12) << 6) & 0xFF
    r[6] &= 0xFE
    r[6] |= (v["strength"] - 12) >> 2
    r[6] &= 0xF1
    r[6] |= (v["stamina"] - 12) << 1
    r[6] &= 0x7F
    r[6] |= ((v["speed"] - 12) << 7) & 0xFF
    r[7] &= 0xFC
    r[7] |= (v["speed"] - 12) >> 1
    r[7] &= 0xE3
    r[7] |= (v["acceleration"] - 12) << 2
    r[9] &= 0xF1
    r[9] |= (v["passing"] - 12) << 1
    r[8] &= 0xC7
    r[8] |= (v["shot_power"] - 12) << 3
    r[8] &= 0x3F
    r[8] |= ((v["shot_accuracy"] - 12) << 6) & 0xFF
    r[9] &= 0xFE
    r[9] |= (v["shot_accuracy"] - 12) >> 2
    r[10] &= 0xE3
    r[10] |= (v["jump"] - 12) << 2
    r[9] &= 0x7F
    r[9] |= ((v["heading"] - 12) << 7) & 0xFF
    r[10] &= 0xFC
    r[10] |= (v["heading"] - 12) >> 1
    r[9] &= 0x8F
    r[9] |= (v["technique"] - 12) << 4
    r[6] &= 0x8F
    r[6] |= (v["dribbling"] - 12) << 4
    r[10] &= 0x1F
    r[10] |= ((v["swerve"] - 12) << 5) & 0xFF
    r[11] &= 0xF8
    r[11] |= v["aggression"] - 12
    r[5] &= 0xE3
    r[5] |= (v["reflexes"] - 12) << 2
    return bytes(r)


# The pair the port uses. The stream is the one that ships, because it is the
# one whose field table a human can check against the measurement; the masks
# stay as the oracle it is checked against, every run.
decode = decode_stream
encode = encode_stream


# --- the record on a card --------------------------------------------------

def player_blob(card: Card, index: int) -> bytes:
    a = layout.player_attribute_address(index)
    return bytes(card.data[a:a + BLOB_BYTES])


def shirt_numbers_from_table(card: Card) -> list[int]:
    """The 23 shirt numbers off the 5-bit table, for the tripwire.

    `numbers.py` (MCR-TASK-07) owns this properly, domains and all. Six lines
    of it live here because the tripwire of section 1.5 is a completion
    criterion of THIS task: the number is stored twice, and the two readings
    disagreeing is the cheapest evidence that an encoder is wrong.
    """
    d = layout.SHIRT_NUMBERS
    raw = int.from_bytes(card.data[d.address:d.address + d.total_bytes],
                         "little")
    per = layout.SHIRT_NUMBERS_PER_GROUP
    out = []
    for j in range(layout.SQUAD_SIZE):
        group, within = divmod(j, per)
        # The offset inside the group is 5*within -- NOT the documented
        # `[0,5,2,7,4,1]`. That table is the shift INSIDE A BYTE, and it pairs
        # with a byte index: 5*within = 0,5,10,15,20,25 lands on byte
        # 0,0,1,1,2,3 at shift 0,5,2,7,4,1. Using the table as a group-wide
        # offset is what this reader did first, and it produced
        # `1 5 1 26 9 1 ...` -- numbers that look like shirt numbers and are
        # not. The tripwire caught it; nothing else would have.
        base = group * layout.SHIRT_NUMBER_GROUP_BYTES * 8
        out.append(1 + ((raw >> (base + 5 * within)) & 0x1F))
    return out


# --- the upstream's weight tables, re-measured -----------------------------

_ITEMS = re.compile(r"Me\.(id\w+)\.Items\.AddRange\(New Object\(\) \{([^}]*)\}")

# The upstream's hidden combo box for each stream field. Bytes 0..3 are absent
# on purpose: there it builds the byte by CONCATENATING hex digits as strings
# rather than summing weights, so there is no shift to compare.
UPSTREAM_COMBO = {
    "skin_colour": "idskincolor", "build": "idbody", "age": "idage",
    "reflexes": "idresponse", "strength": "idbodybalance",
    "stamina": "idstamina", "dribbling": "iddribble", "speed": "idspeed",
    "acceleration": "idaceleration", "attack": "idoffense",
    "defence": "iddeffense", "shot_power": "idshotpower",
    "shot_accuracy": "idshotacc", "passing": "idpass",
    "technique": "idtechnique", "heading": "idhead", "jump": "idjump",
    "swerve": "idcurve", "aggression": "idaggression", "boots": "idboots",
    "foot": "idfoot",
}


def upstream_weights(clone: str) -> dict[str, list[int]]:
    """`{combo: [weights]}` read out of the upstream's VB designer file.

    Only the `lite/` tree has these: the main tree folds the same screen into
    `Frmmcr.vb` and the newer version delegates to a DLL with no source.
    """
    path = os.path.join(clone, "lite", "fifatomcr", "Frmmcr.designer.vb")
    if not os.path.isfile(path):
        raise AttributeError_(
            f"{path} not found. The upstream clone is gitignored; "
            f"see MCR-TASK-02 for how it is fetched.")
    with open(path, encoding="utf-8", errors="replace") as fh:
        text = fh.read()
    out = {}
    for m in _ITEMS.finditer(text):
        values = [v.strip().strip('"') for v in m.group(2).split(",")]
        try:
            out[m.group(1)] = [int(v) for v in values]
        except ValueError:
            continue      # the hex-digit combos of bytes 0..3
    return out


def check_upstream_weights(clone: str, verbose: bool = True) -> list[str]:
    """Each weight list has to be `index << shift` for OUR declared shift."""
    tables = upstream_weights(clone)
    problems = []
    checked = 0
    for name, combo in sorted(UPSTREAM_COMBO.items()):
        if combo not in tables:
            problems.append(f"{name}: {combo} not found in the designer")
            continue
        f = BY_NAME[name]
        weights = tables[combo]
        expected = [i << f.shift for i in range(len(weights))]
        if weights != expected:
            problems.append(
                f"{name}: {combo} is {weights[:4]}..., expected "
                f"{expected[:4]}... for shift {f.shift}")
        checked += 1
    if verbose:
        print(f"attributes.py --upstream-weights: {checked - len(problems)}/"
              f"{len(UPSTREAM_COMBO)} weight tables are `index << shift` with "
              f"our shifts")
        for p in problems:
            print(f"  FAIL {p}")
    return problems


# --- self-check ------------------------------------------------------------

def self_check(card_path: str | None = None, verbose: bool = True) -> int:
    failures = []

    def ok(name, cond, detail=""):
        if cond:
            if verbose:
                print(f"  ok    {name}")
        else:
            failures.append(name)
            print(f"  FAIL  {name}  {detail}")

    def attempt(name, fn, default=None):
        try:
            return fn()
        except Exception as e:                        # noqa: BLE001
            failures.append(name)
            print(f"  FAIL  {name}: raised {type(e).__name__}: {e}")
            return default

    def refuses(name, fn, fragment, kind=AttributeError_):
        """Demands that `fn()` raise `kind` with `fragment` in the message.

        Hand-rolled `try/except SpecificError` around a refusal looks equivalent
        and is not: any OTHER exception walks straight past it and kills the
        run. Measured here -- the planted v4.2 swap made this block raise
        KeyError, the self-check died mid-way, and three checks never ran. It is
        the same fragility MCR-TASK-04 found, in the one place this module
        wrote by hand.
        """
        try:
            fn()
        except kind as e:
            if fragment in str(e):
                if verbose:
                    print(f"  ok    {name}")
            else:
                failures.append(name)
                print(f"  FAIL  {name}: refused without saying "
                      f"{fragment!r}: {e}")
        except Exception as e:                        # noqa: BLE001
            failures.append(name)
            print(f"  FAIL  {name}: raised {type(e).__name__}, "
                  f"expected {kind.__name__}: {e}")
        else:
            failures.append(name)
            print(f"  FAIL  {name}: did NOT refuse")

    print("attributes.py self-check")

    ok("29 fields", len(FIELDS) == 29, f"n={len(FIELDS)}")
    ok("no field name repeats", len(BY_NAME) == len(FIELDS))
    ok("fields do not overlap and stay inside 96 bits",
       all(f.offset + f.width <= BLOB_BITS for f in FIELDS)
       and len(GAP_BITS) + sum(f.width for f in FIELDS) == BLOB_BITS)
    ok("4 bits belong to no field", len(GAP_BITS) == 4, f"gaps={GAP_BITS}")
    ok("the gaps are where the measurement puts them",
       GAP_BITS == (3, 12, 16, 45), f"gaps={GAP_BITS}")

    # --- the two implementations, on 100,000 seeded blobs
    rng = random.Random(20260907)
    blobs = [bytes(rng.randrange(256) for _ in range(BLOB_BYTES))
             for _ in range(100_000)]

    def sweep():
        bad_decode = bad_stream_rt = bad_masks_rt = bad_cross = 0
        first = None
        for b in blobs:
            a_ = decode_stream(b)
            m_ = decode_masks(b)
            if a_ != m_:
                bad_decode += 1
                if first is None:
                    first = (b.hex(" "),
                             {k: (a_[k], m_[k]) for k in a_ if a_[k] != m_[k]})
            if encode_stream(a_, b) != b:
                bad_stream_rt += 1
            if encode_masks(m_, b) != b:
                bad_masks_rt += 1
            if encode_stream(a_, b) != encode_masks(m_, b):
                bad_cross += 1
        return bad_decode, bad_stream_rt, bad_masks_rt, bad_cross, first

    res = attempt("the 100,000-blob sweep runs", sweep,
                  default=(-1, -1, -1, -1, None))
    bad_decode, bad_stream_rt, bad_masks_rt, bad_cross, first = res
    ok("100,000 blobs: stream and masks decode the same", bad_decode == 0,
       f"differ={bad_decode} first={first}")
    ok("100,000 blobs: encode_stream(decode_stream(b)) == b",
       bad_stream_rt == 0, f"differ={bad_stream_rt}")
    ok("100,000 blobs: encode_masks(decode_masks(b)) == b",
       bad_masks_rt == 0, f"differ={bad_masks_rt}")
    ok("100,000 blobs: the two encoders agree byte for byte",
       bad_cross == 0, f"differ={bad_cross}")

    # --- the gap bits survive an edit
    b = bytes(rng.randrange(256) for _ in range(BLOB_BYTES))
    gap_mask = 0
    for g in GAP_BITS:
        gap_mask |= 1 << g
    v = decode_stream(b)
    v["speed"] = 19
    v["number"] = 7
    out = encode_stream(v, b)
    ok("an edit preserves every bit no field claims",
       (int.from_bytes(out, "little") & gap_mask)
       == (int.from_bytes(b, "little") & gap_mask))
    ok("and the edit actually landed",
       decode_stream(out)["speed"] == 19 and decode_stream(out)["number"] == 7)

    # --- domains
    ok("skills are shown 12..19 over a 3-bit field",
       BY_NAME["speed"].low == 12 and BY_NAME["speed"].high == 19)
    ok("height is 148..211", BY_NAME["height"].low == 148
       and BY_NAME["height"].high == 211)
    ok("age is 15..46", BY_NAME["age"].low == 15 and BY_NAME["age"].high == 46)
    ok("the shirt number is stored one less",
       BY_NAME["number"].low == 1 and BY_NAME["number"].high == 32)

    refuses("refuses a value outside the domain",
            lambda: encode_stream(dict(v, speed=20), b), "outside 12..19")
    refuses("refuses a blob that is not 12 bytes",
            lambda: decode_stream(b"\x00" * 11), "12 bytes, got 11")

    # --- the deliberate divergence: the v4.2 Speed/Dribble swap
    swapped = dict(v)
    swapped["speed"], swapped["dribbling"] = v["dribbling"], v["speed"]
    if v["speed"] != v["dribbling"]:
        ok("the v4.2 Speed/Dribble swap would be caught",
           encode_stream(swapped, b) != encode_stream(v, b))
    else:
        # A blob where the two happen to be equal cannot witness the swap.
        alt = dict(v)
        alt["speed"], alt["dribbling"] = 12, 19
        sw = dict(alt)
        sw["speed"], sw["dribbling"] = alt["dribbling"], alt["speed"]
        ok("the v4.2 Speed/Dribble swap would be caught",
           encode_stream(sw, b) != encode_stream(alt, b))

    # --- against the real card, if there is one
    card_path = card_path or os.environ.get("WE2002_MCR_CARD")
    if not card_path or not os.path.isfile(card_path):
        print("  skip  the 23 records of the fixture "
              "(no WE2002_MCR_CARD)")
    else:
        card = attempt("open the card", lambda: Card.from_file(card_path))
        if card is not None:
            diffs = []
            for i in range(layout.SQUAD_SIZE):
                blob = player_blob(card, i)
                if decode_stream(blob) != decode_masks(blob):
                    diffs.append(i)
            ok(f"the {layout.SQUAD_SIZE} records decode the same both ways",
               diffs == [], f"differ at {diffs}")

            rt = [i for i in range(layout.SQUAD_SIZE)
                  if encode_stream(decode_stream(player_blob(card, i)),
                                   player_blob(card, i))
                  != player_blob(card, i)]
            ok("and re-encode to the same bytes", rt == [], f"differ at {rt}")

            # The tripwire of section 1.5: the number is stored twice.
            table = attempt("read the shirt-number table",
                            lambda: shirt_numbers_from_table(card), default=[])
            from_record = [decode_stream(player_blob(card, i))["number"]
                           for i in range(layout.SQUAD_SIZE)]
            ok(f"tripwire: {layout.SQUAD_SIZE}/{layout.SQUAD_SIZE} shirt "
               f"numbers agree between the record and the table",
               table == from_record,
               f"table={table} record={from_record}")

    # --- the upstream's weights, if the clone is present
    clone = layout.find_upward(os.path.join("work", "easy-mcr"))
    if clone is None:
        print("  skip  the upstream weight tables (no work/easy-mcr)")
    else:
        w = attempt("the upstream weight check runs",
                    lambda: check_upstream_weights(clone, verbose=False),
                    default=None)
        ok(f"all {len(UPSTREAM_COMBO)} upstream weight tables are "
           f"`index << shift` with our shifts", w == [], f"problems={w}")

    print(f"attributes.py: {len(failures)} failure(s)")
    return len(failures)


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?", help="a .mcr to read")
    ap.add_argument("--player", type=int, default=None,
                    help="show one record instead of all 23")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("--upstream-weights", metavar="CLONE",
                    help="re-measure the weight tables in the VB source")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check(a.card) else 0

    if a.upstream_weights:
        try:
            return 1 if check_upstream_weights(a.upstream_weights) else 0
        except AttributeError_ as e:
            print(f"error: {e}", file=sys.stderr)
            return 2

    if not a.card:
        ap.error("give a .mcr, or use --self-check")

    try:
        card = Card.from_file(a.card)
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    indices = ([a.player] if a.player is not None
               else range(layout.SQUAD_SIZE))
    for i in indices:
        blob = player_blob(card, i)
        v = decode_stream(blob)
        agree = "" if v == decode_masks(blob) else "   <-- DISAGREES WITH Player.cpp"
        print(f"player {i:2d}  {blob.hex(' ')}{agree}")
        for f in FIELDS:
            print(f"    {f.name:<16} {v[f.name]:>4}   "
                  f"[{f.low}..{f.high}]  byte {f.byte} bit {f.shift} "
                  f"w{f.width}")
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())

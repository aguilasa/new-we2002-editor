#!/usr/bin/env python3
"""The 24 five-bit shirt numbers, and the tripwire they make possible.

Provenance (section 3.4 of the plan):

  container   --
  address     `layout.py` (which measures itself against `wte/re/mcr.md`)
  semantics   the upstream
  codec       ours -- section 1.5 of the plan

THE NUMBER IS STORED TWICE, and that is the cheapest guard in the whole port:
the 16-byte table here, and the 5 bits at `raw[3]` of each player record that
`attributes.py` decodes. Any off-by-one or bit-packing slip in a writer breaks
the pair on the first save, and checking costs a subtraction. Section 1.5 of
the plan measured 23/23 on the fixture; `--check` re-measures it.

THE CARD STORES THE NUMBER MINUS ONE. Reading adds 1 and writing subtracts 1 --
symmetrically. The upstream adds on read and does NOT subtract on write, and
section 6 of the plan calls that a defect to diverge from rather than a format
to reproduce: the symptom is "the number changed by itself".

Usage:

    python3 tools/mcr/numbers.py <card.mcr>
    python3 tools/mcr/numbers.py <card.mcr> --check
    python3 tools/mcr/numbers.py --self-check
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout                                            # noqa: E402
from card import Card                                    # noqa: E402
import harness                                           # noqa: E402

WIDTH = 5
SLOTS = 24                  # 4 groups x 6; the squad uses 23 of them
STORED_BIAS = 1             # the card holds the number minus one


class NumbersError(Exception):
    """A shirt number outside what five bits hold, or a table of the wrong size."""


def _group_and_offset(slot: int) -> tuple[int, int]:
    """`(group, bit offset inside the group)` for slot `slot`.

    THE OFFSET IS `5*within`, NOT the documented `[0,5,2,7,4,1]`.

    That table is real, and it is the shift INSIDE A BYTE -- it only means
    anything paired with a byte index. `5*within` = 0, 5, 10, 15, 20, 25 lands
    on bytes 0, 0, 1, 1, 2, 3 at exactly those shifts, which is why the two
    descriptions look interchangeable and are not. Using the table as a
    group-wide offset returns `1 5 1 26 9 1 6 11 18 ...` on the fixture:
    numbers that look like shirt numbers. Measured in MCR-TASK-06, where the
    tripwire caught it; `self_check` keeps both readings side by side so it
    cannot come back.
    """
    group, within = divmod(slot, layout.SHIRT_NUMBERS_PER_GROUP)
    return group, WIDTH * within


def decode_table(table: bytes) -> list[int]:
    """The 24 numbers held in the 16-byte table."""
    d = layout.SHIRT_NUMBERS
    if len(table) != d.total_bytes:
        raise NumbersError(
            f"the shirt-number table is {d.total_bytes} bytes, got {len(table)}")
    raw = int.from_bytes(table, "little")
    bits = layout.SHIRT_NUMBER_GROUP_BYTES * 8
    out = []
    for slot in range(SLOTS):
        group, offset = _group_and_offset(slot)
        out.append(STORED_BIAS
                   + ((raw >> (group * bits + offset)) & ((1 << WIDTH) - 1)))
    return out


def encode_table(numbers: list[int], table: bytes) -> bytes:
    """Read-modify-write of the slots given. Everything else survives.

    The 2 bits left over in each group -- 6 x 5 = 30 of 32 -- and any slot not
    in `numbers` come through untouched, which is what lets the round-trip be
    byte-identical.
    """
    d = layout.SHIRT_NUMBERS
    if len(table) != d.total_bytes:
        raise NumbersError(
            f"the shirt-number table is {d.total_bytes} bytes, got {len(table)}")
    if len(numbers) > SLOTS:
        raise NumbersError(f"{len(numbers)} numbers for {SLOTS} slots")
    raw = int.from_bytes(table, "little")
    bits = layout.SHIRT_NUMBER_GROUP_BYTES * 8
    for slot, number in enumerate(numbers):
        stored = number - STORED_BIAS
        if not 0 <= stored < (1 << WIDTH):
            raise NumbersError(
                f"slot {slot}: number {number} is outside "
                f"{STORED_BIAS}..{STORED_BIAS + (1 << WIDTH) - 1}")
        group, offset = _group_and_offset(slot)
        shift = group * bits + offset
        mask = ((1 << WIDTH) - 1) << shift
        raw = (raw & ~mask) | (stored << shift)
    return raw.to_bytes(d.total_bytes, "little")


def read(card: Card) -> list[int]:
    d = layout.SHIRT_NUMBERS
    return decode_table(bytes(card.data[d.address:d.address + d.total_bytes]))


def squad(card: Card) -> list[int]:
    """Only the 23 slots the squad uses. Slot 24 is not a player."""
    return read(card)[:layout.SQUAD_SIZE]


def write(card: Card, numbers: list[int]) -> None:
    d = layout.SHIRT_NUMBERS
    old = bytes(card.data[d.address:d.address + d.total_bytes])
    card.write(d.address, encode_table(numbers, old))


def cross_check(card: Card) -> list[tuple[int, int, int]]:
    """The tripwire: `(slot, from the table, from the record)` where they differ.

    Empty means the two independent copies of every shirt number agree.
    """
    import attributes
    from_table = squad(card)
    from_record = [attributes.decode(attributes.player_blob(card, i))["number"]
                   for i in range(layout.SQUAD_SIZE)]
    return [(i, t, r) for i, (t, r) in enumerate(zip(from_table, from_record))
            if t != r]


# --- self-check ------------------------------------------------------------

def self_check(card_path: str | None=None, verbose: bool=True) -> int:
    return harness.run("numbers.py", _checks, verbose, card_path=card_path)


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(NumbersError)
    size = layout.SHIRT_NUMBERS.total_bytes
    ok("24 slots of 5 bits in 16 bytes",
       SLOTS * WIDTH == 120 and size == 16 and SLOTS * WIDTH <= size * 8)
    ok("6 per group, 30 of 32 bits used",
       layout.SHIRT_NUMBERS_PER_GROUP * WIDTH == 30
       and layout.SHIRT_NUMBER_GROUP_BYTES * 8 == 32)

    # The two descriptions of the same offset, kept side by side.
    byte_local = []
    for w in range(layout.SHIRT_NUMBERS_PER_GROUP):
        _, off = _group_and_offset(w)
        byte_local.append(off % 8)
    ok("5*within lands on the documented byte-local shifts",
       tuple(byte_local) == layout.SHIRT_NUMBER_BIT_SHIFTS,
       f"got={byte_local} documented={layout.SHIRT_NUMBER_BIT_SHIFTS}")
    ok("and the two are NOT the same number",
       [o for _, o in (_group_and_offset(w)
                       for w in range(layout.SHIRT_NUMBERS_PER_GROUP))]
       != list(layout.SHIRT_NUMBER_BIT_SHIFTS))

    # Round-trip on a synthetic table.
    wanted = [(i % 32) + 1 for i in range(SLOTS)]
    blank = bytes(size)
    t = attempt("encode a full table", lambda: encode_table(wanted, blank),
                default=blank)
    ok("a full table round-trips", decode_table(t) == wanted,
       f"got={decode_table(t)}")

    # Every slot is independent: writing one must not disturb its neighbours.
    def one_at_a_time():
        out = []
        for slot in range(SLOTS):
            one = list(wanted)
            one[slot] = 32 if wanted[slot] != 32 else 1
            if decode_table(encode_table(one, t)) != one:
                out.append(slot)
        return out

    disturbed = attempt("change one slot at a time", one_at_a_time)
    ok("changing one slot leaves the other 23 alone", disturbed == [],
       f"disturbed={disturbed}")

    # The 8 bits no slot claims survive a write.
    spare_mask = 0
    for g in range(size * 8 // 32):
        for b in range(30, 32):
            spare_mask |= 1 << (g * 32 + b)
    noisy = (int.from_bytes(t, "little") | spare_mask).to_bytes(size, "little")
    out = attempt("write over a table with the spare bits set",
                  lambda: encode_table(wanted, noisy), default=bytes(size))
    ok("the 2 spare bits of each group survive a write",
       (int.from_bytes(out, "little") & spare_mask) == spare_mask)

    # Writing fewer slots leaves the rest alone -- slot 24 is not a player.
    partial = attempt("write only the 23 squad slots",
                      lambda: encode_table(wanted[:layout.SQUAD_SIZE], t),
                      default=t)
    ok("writing 23 slots leaves slot 24 untouched",
       decode_table(partial)[layout.SQUAD_SIZE] == wanted[layout.SQUAD_SIZE])

    one = attempt("encode number 1", lambda: encode_table([1], blank),
                  default=blank)
    ok("stored is one less than worn",
       decode_table(one)[0] == 1 and one[0] & 0x1F == 0)

    refuses("refuses number 0", lambda: encode_table([0], blank),
            "outside 1..32")
    refuses("refuses number 33", lambda: encode_table([33], blank),
            "outside 1..32")
    refuses("refuses a table of the wrong size",
            lambda: decode_table(b"\x00" * 15), "16 bytes, got 15")
    refuses("refuses more numbers than slots",
            lambda: encode_table([1] * 25, blank), "25 numbers for 24 slots")

    # --- against the real card
    card_path = card_path or os.environ.get("WE2002_MCR_CARD")
    if not card_path or not os.path.isfile(card_path):
        print("  skip  the fixture (no WE2002_MCR_CARD)")
    else:
        card = attempt("open the card", lambda: Card.from_file(card_path))
        if card is not None:
            got = attempt("read the table", lambda: read(card), default=[])
            ok("the fixture reads as the plan measured",
               got[:layout.SQUAD_SIZE]
               == [1, 5, 4, 3, 2, 7, 6, 11, 10, 9, 8, 16, 17, 13, 19, 22, 12,
                   18, 20, 14, 15, 21, 23],
               f"got={got[:layout.SQUAD_SIZE]}")
            ok("the unused 24th slot holds 0, which reads as 1",
               got[23] == 1, f"slot24={got[23]}")

            d = layout.SHIRT_NUMBERS
            original = bytes(card.data[d.address:d.address + d.total_bytes])
            ok("re-encoding the fixture table changes no byte",
               encode_table(got, original) == original)

            diffs = attempt("the tripwire runs", lambda: cross_check(card),
                            default=None)
            ok(f"tripwire: {layout.SQUAD_SIZE}/{layout.SQUAD_SIZE} agree with "
               f"the player records", diffs == [], f"differ={diffs}")


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?")
    ap.add_argument("--check", action="store_true",
                    help="run the tripwire against the player records")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check(a.card) else 0

    if not a.card:
        ap.error("give a .mcr, or use --self-check")

    try:
        card = Card.from_file(a.card)
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    if a.check:
        diffs = cross_check(card)
        if diffs:
            for slot, t, r in diffs:
                print(f"  FAIL slot {slot}: table says {t}, record says {r}")
        print(f"numbers.py --check: "
              f"{layout.SQUAD_SIZE - len(diffs)}/{layout.SQUAD_SIZE} shirt "
              f"numbers agree between the table and the player records")
        return 1 if diffs else 0

    values = read(card)
    print(f"slots 0..{layout.SQUAD_SIZE - 1} (the squad):")
    print("  " + " ".join(f"{n:2d}" for n in values[:layout.SQUAD_SIZE]))
    print(f"slot {layout.SQUAD_SIZE} (unused): {values[layout.SQUAD_SIZE]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

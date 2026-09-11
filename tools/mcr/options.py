#!/usr/bin/env python3
"""The option save's records, and the one byte that picks the camera.

Provenance (section 3.4 of the plan):

  container   `card.py` -- the directory names the block, and the PSX save
              header says how many icon frames stand in front of the data
  address     `layout.py`, the option section: MEASURED HERE on 2026-09-11 by
              diffing four option files saved from one session of the game with
              nothing changed but the camera. Not `wte/re/mcr.md`: the camera
              is none of the team save's 17 destinations, and
              `we-team-editor.exe` never writes it
  semantics   the nine camera names are the game's own, off its option screen
  codec       --

WHAT THIS MODULE IS NOT. It is not part of the team editor. `model.Save` reads
players, numbers, the formation and the kickers out of ABSOLUTE addresses the
upstream wrote; this reads two records out of the same save by resolving
offsets against the block the directory actually names. The two coexist and do
not share a byte: the camera lives at data offset 4, and the nearest
destination of the other measurement is thousands of bytes away.

THE CHECKSUM IS THE WHOLE RISK. Each record carries its own -- the payload's
bytes summed mod 256 -- and the game will not take a record whose sum does not
match. Writing the camera byte alone leaves a card the console loads and the
game rejects, which looks like "the edit did nothing" and is in fact a save the
game threw away. `write_camera` recomputes it; nothing else here writes.

Measured, four cards from one session:

    camera         byte      checksum
    normal-near      0          0xD8
    normal-mid       1          0xD9      (the clean one)
    normal-far       2          0xDA
    ov-far           8          0xE0

Patching those two bytes into the clean card reproduces each of the other three
byte for byte, outside the title padding -- which is uninitialised memory the
game leaves in the PSX save header and is not data. `--check` is that
measurement, run again.

Usage:

    python3 tools/mcr/options.py <card.mcr>
    python3 tools/mcr/options.py <card.mcr> --set normal-far --out <copy.mcr>
    python3 tools/mcr/options.py --check
    python3 tools/mcr/options.py --self-check
"""

import argparse
import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card as card_mod                                  # noqa: E402
import harness                                           # noqa: E402
import layout                                            # noqa: E402
import mcrio                                             # noqa: E402
from card import Card                                    # noqa: E402

# The nine views of the option screen, in the order the byte counts them. The
# four marked below were measured; the other five are the screen's order with
# the two ends pinned, and 8 landing exactly on the last name is what makes the
# ordering more than a guess.
CAMERA_NAMES = (
    "normal-near",      # 0   measured
    "normal-mid",       # 1   measured -- the clean card
    "normal-far",       # 2   measured
    "wide",             # 3
    "tv",               # 4
    "zoom",             # 5
    "ov-near",          # 6
    "ov-mid",           # 7
    "ov-far",           # 8   measured
)

MEASURED_CAMERAS = (0, 1, 2, 8)

# The environment variable that points at the four cards `--check` needs. A
# memory card is somebody's save and is not versioned -- same rule as roms/ --
# so the check SKIPS when the directory is not there, and says it skipped.
CAMERA_DIR_ENV = "WE2002_MCR_CAMERA_CARDS"

# The file names inside that directory, and the camera each was saved with.
# The clean card comes first: it is the one the other three are patched out of.
CAMERA_FIXTURES = (
    ("limpo", 1),
    ("camera-normal-near", 0),
    ("camera-normal-far", 2),
    ("camera-ov-far", 8),
)

# The PSX save header, at the top of the first block of the chain: "SC", then a
# byte whose low nibble counts the icon frames that follow the header.
SAVE_MAGIC = b"SC"
ICON_FRAMES_MASK = 0x0F
MAX_ICON_FRAMES = 3
TITLE_OFFSET = 4
TITLE_BYTES = 64


class OptionsError(Exception):
    """A save that is not shaped the way the measurement says."""


@dataclasses.dataclass(frozen=True)
class Record:
    """One record of the option save, already located in the card."""

    index: int
    header: int             # card address of the u16 size
    size: int               # as the file declares it, never as the table does
    stored_checksum: int
    computed_checksum: int

    @property
    def payload(self) -> int:
        return self.header + layout.OPTION_RECORD_HEADER_BYTES

    @property
    def checksum_ok(self) -> bool:
        return self.stored_checksum == self.computed_checksum


# --- locating the save ----------------------------------------------------

def save_start(card: Card) -> int:
    """The card address of the first block of the option save."""
    found = card.find_save()
    if found is None:
        raise OptionsError(
            f"{card.origin}: the directory has no entry matching "
            f"{card_mod.SAVE_NAME_RE.pattern} -- this card holds no WE2002 "
            f"option save, or the save was deleted and its directory entry "
            f"freed.")
    entry, blocks = found
    start = blocks[0] * card_mod.BLOCK_BYTES
    header = bytes(card.data[start:start + 4])
    if header[:len(SAVE_MAGIC)] != SAVE_MAGIC:
        raise OptionsError(
            f"{card.origin}: block {blocks[0]} is declared in use as "
            f"{entry.name!r} but does not start with "
            f"{SAVE_MAGIC.decode()} -- it starts with {header[:2].hex(' ')}. "
            f"The directory and the block disagree.")
    return start


def icon_frames(card: Card) -> int:
    """How many icon frames the save's own header declares: 1, 2 or 3."""
    count = card.data[save_start(card) + 2] & ICON_FRAMES_MASK
    if not 1 <= count <= MAX_ICON_FRAMES:
        raise OptionsError(
            f"{card.origin}: the save header declares {count} icon frames, "
            f"and a PSX save has 1 to {MAX_ICON_FRAMES}. Without that count "
            f"the first data byte cannot be found, and being wrong by one "
            f"frame decodes the icon as options.")
    return count


def data_offset(card: Card) -> int:
    """The card address of the save's first data byte.

    DERIVED, three ways over, and none of them a constant. The block comes from
    the directory, the frame size from the container, and the number of icon
    frames from the save's own header. Written as a constant this would be
    right for the cards on hand and wrong for a card whose save sits in another
    block -- trap 6 of the profile, and the reason the team save's absolute
    addresses cannot be reused here.
    """
    return save_start(card) + card_mod.FRAME_BYTES * (1 + icon_frames(card))


def record(card: Card, index: int) -> Record:
    """Record `index`, located and checksummed. Nothing is repaired."""
    base = data_offset(card) + layout.option_record_offset(index)
    size = int.from_bytes(card.data[base:base + 2], "little")
    stored = card.data[base + 2]
    payload = base + layout.OPTION_RECORD_HEADER_BYTES
    end = payload + size
    if size == 0 or end > card_mod.CARD_BYTES:
        why = "zero" if size == 0 else "past the end of the card"
        raise OptionsError(
            f"{card.origin}: record {index} at {base:#07x} declares a size of "
            f"{size}, which is {why}. The save is not the one this module "
            f"measured, or the block the directory names is not where the "
            f"save is.")
    return Record(
        index=index,
        header=base,
        size=size,
        stored_checksum=stored,
        computed_checksum=checksum(bytes(card.data[payload:end])),
    )


def records(card: Card) -> list[Record]:
    """Both records, in offset order.

    A LIST AND NOT A WALK. `offset + header + size` lands in the 119 zero bytes
    between record 0 and record 1, where the size reads as 0 and a walker
    concludes the save has one record -- measured, and it is why
    `layout.OPTION_RECORD_OFFSETS` is a table.
    """
    return [record(card, i)
            for i in range(len(layout.OPTION_RECORD_OFFSETS))]


def checksum(payload: bytes) -> int:
    """The byte in front of a record: its payload summed, mod 256."""
    return sum(payload) & 0xFF


def title_padding(card: Card) -> tuple[int, int]:
    """The span after the save title's terminator, inside the PSX save header.

    NOT DATA. The game leaves whatever was in memory there, so it differs
    between two saves of the same session, and a diff that does not know about
    it reports a dozen bytes of noise beside the two that matter. Returned as a
    span so `--check` can say how many of the differing bytes were noise
    instead of waving them away.
    """
    start = save_start(card) + TITLE_OFFSET
    title = bytes(card.data[start:start + TITLE_BYTES])
    end = title.find(b"\x00\x00")
    if end < 0:
        return (start + TITLE_BYTES, start + TITLE_BYTES)
    return (start + end, start + TITLE_BYTES)


# --- the camera -----------------------------------------------------------

def camera_address(card: Card) -> int:
    return record(card, layout.CAMERA.record).payload + layout.CAMERA.offset


def read_camera(card: Card) -> int:
    return card.data[camera_address(card)]


def camera_name(value: int) -> str:
    """The screen's name for a camera byte, or a label that says it is not one."""
    if 0 <= value < len(CAMERA_NAMES):
        return CAMERA_NAMES[value]
    return f"<unknown camera {value}>"


def parse_camera(text: str) -> int:
    """A name or a number from the command line, as a camera byte."""
    wanted = str(text).strip().lower()
    if wanted in CAMERA_NAMES:
        return CAMERA_NAMES.index(wanted)
    try:
        value = int(wanted, 0)
    except ValueError:
        raise OptionsError(
            f"{text!r} is not a camera. The nine are: "
            f"{', '.join(CAMERA_NAMES)}.") from None
    if not 0 <= value < len(CAMERA_NAMES):
        raise OptionsError(
            f"camera {value} outside 0..{len(CAMERA_NAMES) - 1} -- the game "
            f"has {len(CAMERA_NAMES)} views, and a tenth value is not one of "
            f"them.")
    return value


def write_camera(card: Card, value: int) -> list[int]:
    """Write the camera and repair its record's checksum; returns what moved.

    TWO BYTES, ALWAYS, and never one. The record in front of the camera carries
    the sum of its payload; leave it stale and the game drops the record, which
    reads on screen as an edit that did nothing. The write itself goes through
    `Card.write`, so the refusal below the directory still stands.
    """
    if not 0 <= value < len(CAMERA_NAMES):
        raise OptionsError(
            f"camera {value} outside 0..{len(CAMERA_NAMES) - 1}")
    rec = record(card, layout.CAMERA.record)
    if not rec.checksum_ok:
        raise OptionsError(
            f"{card.origin}: record {rec.index} already has a bad checksum "
            f"({rec.stored_checksum:#04x} stored, "
            f"{rec.computed_checksum:#04x} computed). Writing would replace "
            f"it with a correct one and hide whatever damaged the save. Find "
            f"out what did that first.")
    address = rec.payload + layout.CAMERA.offset
    card.write(address, bytes([value]))
    payload = bytes(card.data[rec.payload:rec.payload + rec.size])
    card.write(rec.header + 2, bytes([checksum(payload)]))
    return [address, rec.header + 2]


# --- the measurement, run again -------------------------------------------

def _fixture_dir(explicit: str | None = None) -> str | None:
    path = explicit or os.environ.get(CAMERA_DIR_ENV)
    return path if path and os.path.isdir(path) else None


def check(directory: str | None = None, verbose: bool = True) -> list[str]:
    """Re-runs the 2026-09-11 measurement. Empty is correct.

    For each of the three edited cards: take the CLEAN one, write that camera,
    and demand the result equal the card the game itself saved. The only bytes
    allowed to differ are the title padding -- and they are not excused
    silently, they are counted and named, because a difference reaching past
    that padding means the two cards differ in something real.
    """
    problems: list[str] = []
    path = _fixture_dir(directory)
    if path is None:
        if verbose:
            print(f"options.py --check: skipped, no {CAMERA_DIR_ENV} "
                  f"directory with the four measured cards")
        return problems

    def card_at(name):
        return Card.from_file(os.path.join(path, name + ".mcr"))

    missing = [n for n, _ in CAMERA_FIXTURES
               if not os.path.isfile(os.path.join(path, n + ".mcr"))]
    if missing:
        problems.append(f"{path}: missing {', '.join(missing)}")
        if verbose:
            for p in problems:
                print(f"  FAIL {p}")
        return problems

    for name, expected in CAMERA_FIXTURES:
        c = card_at(name)
        got = read_camera(c)
        if got != expected:
            problems.append(
                f"{name}: camera reads {got} ({camera_name(got)}), measured "
                f"{expected} ({camera_name(expected)})")
        for rec in records(c):
            if not rec.checksum_ok:
                problems.append(
                    f"{name}: record {rec.index} checksum "
                    f"{rec.stored_checksum:#04x}, computed "
                    f"{rec.computed_checksum:#04x}")
            measured = layout.OPTION_RECORD_MEASURED_SIZES[rec.index]
            if rec.size != measured:
                problems.append(
                    f"{name}: record {rec.index} declares {rec.size} bytes, "
                    f"measured {measured}")

    clean_name = CAMERA_FIXTURES[0][0]
    padding = title_padding(card_at(clean_name))
    for name, expected in CAMERA_FIXTURES[1:]:
        mine = card_at(clean_name)
        write_camera(mine, expected)
        real = card_at(name).to_bytes()
        moved = [i for i, (x, y) in enumerate(zip(real, mine.to_bytes()))
                 if x != y]
        outside = [i for i in moved if not padding[0] <= i < padding[1]]
        if outside:
            problems.append(
                f"{name}: patching the clean card leaves {len(outside)} "
                f"byte(s) differing outside the title padding, first at "
                f"{outside[0]:#07x}")
        elif verbose:
            print(f"  ok    {name}: two bytes reproduce the card the game "
                  f"saved ({len(moved)} in the title padding)")

    if verbose:
        print(f"options.py --check: {len(CAMERA_FIXTURES)} cards"
              + ("" if not problems else f", {len(problems)} problem(s)"))
        for p in problems:
            print(f"  FAIL {p}")
    return problems


# --- self-check -----------------------------------------------------------

def self_check(card_path: str | None = None, verbose: bool = True) -> int:
    return harness.run("options.py", _checks, verbose, card_path=card_path)


def _synthetic(camera: int = 1) -> Card:
    """A card whose block 1 holds an option save shaped like the measured one.

    Built here and not read from disk, so this self-check runs on a machine
    that has never seen a memory card -- the rule `selftest.py` is built on.
    """
    card = card_mod.synthetic_card(blocks=2)
    start = card_mod.BLOCK_BYTES
    header = bytearray(card_mod.FRAME_BYTES)
    header[0:2] = SAVE_MAGIC
    header[2] = 0x11                     # one icon frame
    header[3] = 0x02                     # two blocks
    header[TITLE_OFFSET:TITLE_OFFSET + 4] = b"WEW\x00"
    card.data[start:start + card_mod.FRAME_BYTES] = header
    data = start + card_mod.FRAME_BYTES * 2
    for index, size in enumerate(layout.OPTION_RECORD_MEASURED_SIZES):
        base = data + layout.option_record_offset(index)
        payload = bytearray(size)
        if index == layout.CAMERA.record:
            payload[layout.CAMERA.offset] = camera
        card.data[base:base + 2] = size.to_bytes(2, "little")
        card.data[base + 2] = checksum(bytes(payload))
        card.data[base + 3:base + 3 + size] = payload
    return card


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(OptionsError)

    ok("nine cameras", len(CAMERA_NAMES) == 9, f"n={len(CAMERA_NAMES)}")
    ok("the four fixtures carry the four measured values",
       tuple(v for _, v in CAMERA_FIXTURES) == (1, 0, 2, 8))
    ok("every measured value is a camera",
       all(0 <= v < len(CAMERA_NAMES) for v in MEASURED_CAMERAS))
    ok("the checksum of nothing is zero", checksum(b"") == 0)
    ok("the checksum wraps at 256", checksum(b"\xff\x02") == 1)

    card = attempt("build a synthetic option card", lambda: _synthetic(1))
    if card is None:
        return

    # The address is DERIVED, and that is the point: the synthetic save sits in
    # block 1 like the user's cards, so a hard-coded address would agree here
    # and disagree on a card whose save moved.
    where = attempt("locate the camera", lambda: camera_address(card))
    ok("the camera sits one byte into record 0's payload",
       where == data_offset(card) + layout.option_record_offset(0)
       + layout.OPTION_RECORD_HEADER_BYTES + layout.CAMERA.offset)
    ok("and reads back what was built", read_camera(card) == 1)
    ok("which the screen calls normal-mid", camera_name(1) == "normal-mid")

    recs = attempt("locate both records", lambda: records(card), default=[])
    ok("two records", len(recs) == 2, f"n={len(recs)}")
    ok("both checksums verify", all(r.checksum_ok for r in recs))
    ok("both sizes are the measured ones",
       [r.size for r in recs] == list(layout.OPTION_RECORD_MEASURED_SIZES))

    before = card.to_bytes()
    moved = attempt("write a camera", lambda: write_camera(card, 8), default=[])
    ok("the write moves exactly two bytes", len(moved) == 2, f"moved={moved}")
    actually = [i for i, (x, y) in enumerate(zip(before, card.to_bytes()))
                if x != y]
    ok("and the card agrees it was two", actually == sorted(moved),
       f"card={actually} returned={sorted(moved)}")
    ok("the camera reads back", read_camera(card) == 8)
    ok("the checksum was repaired, not left stale",
       record(card, 0).checksum_ok)

    # The red case for the checksum: writing the byte WITHOUT the repair has to
    # leave a record that fails. Without this, a `write_camera` that forgot the
    # checksum would pass every check above.
    stale = attempt("build another", lambda: _synthetic(1))
    if stale is not None:
        stale.data[camera_address(stale)] = 8
        ok("a camera written without the checksum fails verification",
           not record(stale, 0).checksum_ok)
        refuses("and writing over it refuses instead of hiding it",
                lambda: write_camera(stale, 2), "bad checksum")

    ok("a name parses", parse_camera("ov-far") == 8)
    ok("a number parses", parse_camera("3") == 3)
    refuses("refuses a name that is not a camera",
            lambda: parse_camera("helicopter"), "is not a camera")
    refuses("refuses a tenth camera", lambda: parse_camera("9"),
            "outside 0..8")
    refuses("refuses writing a tenth camera",
            lambda: write_camera(card, 9), "outside 0..8")

    # A card with no WE2002 save has to be NAMED, not decoded: the offsets mean
    # nothing without the directory entry that anchors them.
    blank = attempt(
        "build a card with no option save",
        lambda: card_mod.synthetic_card(save_name="BISLPM-00000ZZZ-XXX"))
    if blank is not None:
        refuses("refuses a card with no option save",
                lambda: read_camera(blank), "no entry matching")

    # A save header that lies about its icon frames moves the data by 128 bytes
    # per frame; guessing one decodes the icon as options.
    lying = attempt("build one more", lambda: _synthetic(1))
    if lying is not None:
        lying.data[card_mod.BLOCK_BYTES + 2] = 0x10
        refuses("refuses a save declaring no icon frames",
                lambda: read_camera(lying), "icon frames")

    # --- against the measured cards, when they are on this machine
    problems = attempt("the measurement runs again",
                       lambda: check(card_path, verbose=False), default=None)
    if _fixture_dir(card_path) is None:
        c.skip("the four measured cards", f"no {CAMERA_DIR_ENV}")
    else:
        ok("the four cards still measure as they did",
           problems == [], f"problems={problems}")


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?")
    ap.add_argument("--set", dest="camera",
                    help="a camera name or a number 0..8")
    ap.add_argument("--out", help="where to write; the default is a copy "
                                  "beside the card, never the card")
    ap.add_argument("--force", action="store_true",
                    help="write the card named by WE2002_MCR_CARD anyway")
    ap.add_argument("--check", action="store_true",
                    help="re-run the measurement against the four cards")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check(a.card) else 0
    if a.check:
        return 1 if check(a.card) else 0
    if not a.card:
        ap.error("give a .mcr, or use --check / --self-check")

    try:
        card = mcrio.check_card(mcrio.read_card(a.card))
        if a.camera is None:
            value = read_camera(card)
            print(f"camera: {value} ({camera_name(value)})")
            print(f"  at {camera_address(card):#07x}, save data at "
                  f"{data_offset(card):#07x}")
            for rec in records(card):
                state = "ok" if rec.checksum_ok else \
                    f"BAD, computed {rec.computed_checksum:#04x}"
                print(f"  record {rec.index}: {rec.size:6d} bytes at "
                      f"{rec.payload:#07x}, checksum "
                      f"{rec.stored_checksum:#04x} {state}")
            return 0

        wanted = parse_camera(a.camera)
        target = mcrio.check_destination(a.out or mcrio.copy_target(a.card),
                                         force=a.force)
        was = read_camera(card)
        moved = write_camera(card, wanted)
        written = mcrio.write_card(card, target, force=a.force)
        print(f"camera {was} ({camera_name(was)}) -> {wanted} "
              f"({camera_name(wanted)})")
        for offset in moved:
            print(f"  {offset:#07x}")
        print(f"written: {written}")
        return 0
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

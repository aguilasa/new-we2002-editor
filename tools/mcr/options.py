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

THE CHECKSUM IS THE WHOLE RISK, and the game is strict about it. Each record
carries its own -- the payload's bytes summed mod 256.

MEASURED on 2026-09-12, and it settled a guess this docstring had got wrong.
One byte was changed on DuckStation's card, from `wide` to `tv`, leaving the
sum at wide's `0xdb` instead of tv's `0xdc`. The game did not take the record,
did not fall back to a default, and did not quietly ignore the edit: it put
**ERROR** on screen while loading the option file, and refused to go on. The
prose here used to say it "looks like the edit did nothing", which was a
deduction, and the deduction was wrong -- it is loud, not silent.

It also did not touch the card. The file's digest after the refusal was the one
written before it, so a stale sum costs a failed load and nothing else; the
12,420-byte record of edited names beside it was never at risk.

`write_camera` recomputes the sum; nothing else here writes.

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

AND THE OTHER DIRECTION, which is the one that matters here. This module wrote
5 on 2026-09-11, then 3, 6 and 7 on 2026-09-12, over DuckStation's card -- two
bytes each time -- and the game came up with Zoom, Wide, OV Near and OV Mid
selected. The four cards above cannot establish that on their own: a card the
game saved is a card the game had already accepted, so reading it back proves
the decoder and says nothing about whether the checksum we compute is the one
the game validates. It is.

WITH THOSE FOUR, EVERY CAMERA HAS BEEN SEEN. Four read back from the game's own
saves, four written by us and shown on screen, and `tv` written by the game onto
a card we had edited. Until 2026-09-12 the last two rested on being fenced
between proven neighbours, which is an argument and not a sighting; a check
demands the three routes cover all nine and claim none twice.

THE BLOCK IS NOT THE SAVE'S ADDRESS, AND THAT IS MEASURED TOO. On 2026-09-12 the
save was moved from blocks 1-2 to blocks 3-4, directory and all, and the game
loaded it and showed the right camera without touching the card. The console
follows the directory, as it is supposed to, so a card from somebody else can
hold this save anywhere. That is why `data_offset` derives instead of
declaring: a constant would have been right for every card this repository has
seen and wrong for that one, reading the neighbouring block's fill and
reporting a camera nobody set. The self-check builds the same save in two
different blocks and demands the address follow.

AND THEN THE WRITE, which closed the last gap. With the save still in blocks
3-4, the camera was changed to `tv` ON THE GAME'S OWN SCREEN and the option
file saved. Three things came back, and all three matter:

  the save stayed in blocks 3-4          the game writes back into the chain
                                         it found; it does not normalise to
                                         the first free blocks

  the camera landed at data offset 4     the game wrote the byte this module
                                         derives, on a card this module had
                                         already edited

  the checksum it wrote was OURS         0xdc, which is what `checksum()`
                                         computes for that payload, accepted
                                         with no adjustment

The third is the one worth spelling out. Knowing the game REJECTS a wrong sum
(above) is not the same as knowing the sum it PRODUCES is ours: a validator
could accept our byte by coincidence and still generate a different one. It
does not. Same algorithm, both directions.

Sixteen bytes moved in total -- those three, and thirteen in the title padding,
which is the same noise `--check` already excuses. The 12,420-byte record of
names beside it was not touched, and that the padding varies between two of the
GAME'S OWN writes is what confirms it was never data.

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
# four unmarked ones are the screen's order with both ends pinned and the
# middle confirmed, which is what makes the ordering more than a guess.
CAMERA_NAMES = (
    "normal-near",      # 0   read back
    "normal-mid",       # 1   read back -- the clean card
    "normal-far",       # 2   read back
    "wide",             # 3   written, and the game showed it
    "tv",               # 4   the game wrote it on a card we had edited
    "zoom",             # 5   written, and the game showed it
    "ov-near",          # 6   written, and the game showed it
    "ov-mid",           # 7   written, and the game showed it
    "ov-far",           # 8   read back
)

# THREE KINDS OF EVIDENCE, AND THEY DO NOT POINT THE SAME WAY. Keeping them
# apart is the point of having three tuples, and between them they now cover
# all nine -- nothing here rests on being fenced between proven neighbours.
#
# READ_BACK: the game wrote the byte and we read it. That is what `--check`
# repeats, and it proves the decoder. It CANNOT prove writing: a card the game
# saved is a card the game already accepted, so reading it back says nothing
# about whether our checksum is the one it validates.
#
# WRITTEN_BACK: we wrote the byte and the game read it -- 5 on 2026-09-11, then
# 3, 6 and 7 on 2026-09-12, by replacing DuckStation's card and finding Zoom,
# Wide, OV Near and OV Mid selected on the option screen. This is the direction
# the module exists for.
#
# GAME_WROTE_OVER_OURS: 4, on 2026-09-12. The strongest of the three and the
# narrowest: the game saved the option file on a card this module had already
# edited, and put the byte where this module reads it, with the checksum this
# module computes. Both sides of the round trip, in one measurement.
READ_BACK_CAMERAS = (0, 1, 2, 8)
WRITTEN_BACK_CAMERAS = (3, 5, 6, 7)
GAME_WROTE_OVER_OURS = (4,)
MEASURED_CAMERAS = tuple(sorted(READ_BACK_CAMERAS + WRITTEN_BACK_CAMERAS
                                + GAME_WROTE_OVER_OURS))

# The environment variable that points at the cards `--check` needs. A
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

# A FIFTH CARD, AND IT IS OF A DIFFERENT KIND. The four above all hold the save
# in blocks 1-2 and were saved by the game before this module existed. This one
# the game wrote on 2026-09-12 AFTER we had moved the save to blocks 3-4 and
# edited it: the camera it set is `tv`, in a chain we relinked by hand.
#
# It is what keeps the derived address anchored to a real file instead of only
# to a synthetic one. A constant address reads the neighbouring block's fill
# here and reports a camera nobody set -- so this row is the one that fails
# first if somebody ever "simplifies" `data_offset`.
MOVED_FIXTURE = ("jogo-gravou-tv-bloco3", 4, [3, 4])

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
    the sum of its payload; leave it stale and the game puts ERROR on screen
    loading the option file and stops there -- measured, not deduced. The write
    itself goes through `Card.write`, so the refusal below the directory still
    stands.
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

    # The moved card, when it is there. It is checked SEPARATELY and not folded
    # into the loop above: that loop patches each card out of the clean one,
    # and the clean one's save is in another block, so a patch between the two
    # would be comparing different chains and would fail for the wrong reason.
    name, expected, blocks = MOVED_FIXTURE
    moved_path = os.path.join(path, name + ".mcr")
    counted = len(CAMERA_FIXTURES)
    if not os.path.isfile(moved_path):
        if verbose:
            print(f"  skip  {name}: the card the game wrote in block "
                  f"{blocks[0]} is not here")
    else:
        counted += 1
        c = Card.from_file(moved_path)
        found = c.find_save()
        where = list(found[1]) if found else None
        if where != blocks:
            problems.append(
                f"{name}: the save is in blocks {where}, and the measurement "
                f"put it in {blocks}")
        else:
            got = read_camera(c)
            if got != expected:
                problems.append(
                    f"{name}: camera reads {got} ({camera_name(got)}), the "
                    f"game set {expected} ({camera_name(expected)})")
            bad = [r.index for r in records(c) if not r.checksum_ok]
            if bad:
                problems.append(
                    f"{name}: record(s) {bad} have a checksum the game did "
                    f"not agree with -- the sum it writes is not the one "
                    f"`checksum()` computes")
            elif verbose:
                print(f"  ok    {name}: the game's own write, in blocks "
                      f"{where} -- camera {got} ({camera_name(got)}) at "
                      f"{camera_address(c):#07x}, its checksum is ours")

    if verbose:
        print(f"options.py --check: {counted} cards"
              + ("" if not problems else f", {len(problems)} problem(s)"))
        for p in problems:
            print(f"  FAIL {p}")
    return problems


# --- self-check -----------------------------------------------------------

def self_check(card_path: str | None = None, verbose: bool = True) -> int:
    return harness.run("options.py", _checks, verbose, card_path=card_path)


def _blank_card(first_block: int, blocks: int = 2,
                save_name: str = "BISLPM-86600WEW-OPT") -> Card:
    """A formatted card whose save chain starts at `first_block`.

    `card_mod.synthetic_card` always starts at block 1, which is the one
    arrangement this check must NOT be limited to. The directory is written the
    way a real one is: `link` is 0-BASED over the data blocks, so the frame
    that points at frame f stores f-1, and only the first entry carries the
    name -- copied from the real card, where the last entry has size 0 and an
    empty name.
    """
    data = bytearray(b"\x00" * card_mod.CARD_BYTES)
    data[0:2] = card_mod.MAGIC
    last = first_block + blocks - 1
    for i in range(1, card_mod.DIRECTORY_FRAMES + 1):
        q = bytearray(card_mod.FRAME_BYTES)
        if first_block <= i <= last:
            q[0] = 0x51 if i == first_block else (0x53 if i == last else 0x52)
            q[8:10] = (card_mod.CHAIN_END if i == last
                       else i).to_bytes(2, "little")
            if i == first_block:
                q[4:8] = (card_mod.BLOCK_BYTES * blocks).to_bytes(4, "little")
                q[10:10 + len(save_name)] = save_name.encode("ascii")
        else:
            q[0] = 0xA0
            q[8:10] = card_mod.CHAIN_END.to_bytes(2, "little")
        q[card_mod.FRAME_BYTES - 1] = card_mod.frame_checksum(bytes(q))
        data[i * card_mod.FRAME_BYTES:(i + 1) * card_mod.FRAME_BYTES] = q
    data[card_mod.FRAME_BYTES - 1] = card_mod.frame_checksum(
        bytes(data[0:card_mod.FRAME_BYTES]))
    return Card(bytes(data), origin=f"<synthetic block {first_block}>")


def _synthetic(camera: int = 1, first_block: int = 1) -> Card:
    """A card holding an option save shaped like the measured one.

    Built here and not read from disk, so this self-check runs on a machine
    that has never seen a memory card -- the rule `selftest.py` is built on.

    `first_block` is what makes this more than a fixture. The save does not
    have to live in block 1, and on 2026-09-12 the game was measured loading
    one from block 3: the directory is what says where it is, and the console
    follows it. So the self-check builds the same save in two places and
    demands the address follow, which a constant cannot do.
    """
    card = _blank_card(first_block, blocks=2)
    start = first_block * card_mod.BLOCK_BYTES
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
    ok("the kinds of evidence do not overlap",
       not (set(READ_BACK_CAMERAS) & set(WRITTEN_BACK_CAMERAS))
       and not (set(READ_BACK_CAMERAS) & set(GAME_WROTE_OVER_OURS))
       and not (set(WRITTEN_BACK_CAMERAS) & set(GAME_WROTE_OVER_OURS)))
    # The one the game accepted from us, and it is what pins the middle of the
    # list: both ends were already fixed, so a name at index 5 that the game
    # agrees with leaves the ordering no room to be off.
    # EVERY camera has been observed, by one of the three routes, and no route
    # claims the same one twice. Until 2026-09-12 two of them rested on being
    # fenced between proven neighbours, which is an argument and not a sighting.
    ok("the three kinds of evidence cover all nine cameras",
       MEASURED_CAMERAS == tuple(range(len(CAMERA_NAMES))),
       f"measured={MEASURED_CAMERAS}")
    ok("and no camera is claimed by two of them",
       len(READ_BACK_CAMERAS) + len(WRITTEN_BACK_CAMERAS)
       + len(GAME_WROTE_OVER_OURS) == len(CAMERA_NAMES))
    ok("the four we wrote and the game showed",
       [CAMERA_NAMES[v] for v in WRITTEN_BACK_CAMERAS]
       == ["wide", "zoom", "ov-near", "ov-mid"])
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
    # checksum would pass every check above -- and the game is the one that
    # would catch it, with ERROR on the option file's load screen.
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

    # THE SAME SAVE, IN ANOTHER BLOCK. Measured on 2026-09-12: the game loaded
    # an option save moved to block 3 and came up with the right camera, so the
    # directory -- not the block number -- is what says where the save is. A
    # constant address would read the neighbouring block's fill here and report
    # a camera nobody set.
    moved = attempt("build the same save in block 3",
                    lambda: _synthetic(camera=3, first_block=3))
    if moved is not None and card is not None:
        ok("the save is found where the directory puts it",
           moved.find_save()[1] == [3, 4], f"blocks={moved.find_save()[1]}")
        shift = attempt("locate the camera in the moved save",
                        lambda: camera_address(moved))
        ok("and the address moves with it, by whole blocks",
           shift is not None
           and shift - (data_offset(card) + layout.option_record_offset(0)
                        + layout.OPTION_RECORD_HEADER_BYTES
                        + layout.CAMERA.offset)
           == 2 * card_mod.BLOCK_BYTES,
           f"moved={shift:#07x}" if shift else "not located")
        ok("the camera still reads", read_camera(moved) == 3)
        ok("and both records still verify",
           all(r.checksum_ok for r in records(moved)))

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

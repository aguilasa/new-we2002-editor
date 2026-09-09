#!/usr/bin/env python3
"""The PSX memory card container -- directory, blocks, frames and the refusals.

Provenance (section 3.4 of the plan):

  container   the public nocash spec ("Memory Card Data Format"), and this
              repository's `wte/tools/dump_mcr.py`, which already implements it
  address     NONE. The save's 17 destinations live in `layout.py`, and only
              there (Rule 1 of section 3.3). This module's `0x800` is not one
              of them: it is DERIVED from the frame size and the directory
              frame count, and is therefore computed, not written
  semantics   --
  codec       --

What this module exists to prevent, and what the upstream does: treating the
card as a flat 131,072-byte binary. `Easy MCR` never mentions directory, frame,
block or state anywhere in its source, and the effect is threefold -- it only
works with a raw dump, it breaks silently if the save moves to another block,
and it writes IDs from a private database into bytes 0..137, which are the whole
`MC` header frame plus the `state`+`size`+`link` of entry 1. The result is a
card no console reads. See section 1.10 of the plan.

Usage:

    python3 tools/mcr/card.py <card.mcr>
    python3 tools/mcr/card.py <card.mcr> --json
    python3 tools/mcr/card.py --self-check
"""

import argparse
import dataclasses
import json
import os
import re
import sys
import harness                                           # noqa: E402

# --- the container --------------------------------------------------------
# Numbers from the public nocash spec, the same four `dump_mcr.py` already
# carries. There is nothing of WE2002 here: every PSX memory card is like this.

CARD_BYTES = 0x20000        # 131,072 = 16 blocks
BLOCK_BYTES = 8192
FRAME_BYTES = 128
DIRECTORY_FRAMES = 15       # frame 0 is the `MC` header; the next 15 describe
                            # blocks 1..15
MAGIC = b"MC"

# The first byte that belongs to DATA and not to structure. It is the `0x800`
# of section 1.10 of the plan, and it is derived on purpose: written as a
# constant it becomes one more magic number nobody knows the origin of, and the
# next person to change FRAME_BYTES leaves it behind.
HEADER_BYTES = FRAME_BYTES * (DIRECTORY_FRAMES + 1)   # 2048 = 0x800

# The eight frame states. The high nibble separates free from in use; the low
# one gives the position in the chain.
FRAME_STATES = {
    0x51: "in use, first block of the chain",
    0x52: "in use, middle block",
    0x53: "in use, last block of the chain",
    0xA0: "free (formatted)",
    0xA1: "free (was the first of a deleted chain)",
    0xA2: "free (was a middle one)",
    0xA3: "free (was the last one)",
    0xFF: "unused",
}

IN_USE_STATES = (0x51, 0x52, 0x53)
CHAIN_END = 0xFFFF

# The name of the WE2002 save, as it appears in the directory frame.
#
# MEASURED, and only one: `BISLPM-86600WEW-OPT`, in the Japanese fixture. The
# `B` is the PSX save header, the next letter is the region (I=Japan, E=Europe,
# A=America) and the rest is the product code plus the file name.
#
# The European and American variants are in the pattern BY FORM, not by
# measurement: no SLES or SLUS card has passed through here, and inventing their
# product number would be fabricating data. What identifies the save is the
# `WEW-OPT` suffix; that is what is matched, and the prefix only checks that the
# thing looks like a PSX save name.
SAVE_NAME_RE = re.compile(r"^B[A-Z]SL[A-Z]{2}-\d{5}WEW-OPT$")


class CardError(Exception):
    """A card that is not a card, or that is not the one asked for."""


class Refused(Exception):
    """A write this module does not perform, with the reason a human needs."""


def frame_checksum(frame: bytes) -> int:
    """The XOR of the first 127 bytes, which is what byte 127 holds."""
    x = 0
    for b in frame[:FRAME_BYTES - 1]:
        x ^= b
    return x


@dataclasses.dataclass
class DirectoryEntry:
    """One of the 15 directory frames, already read."""

    frame: int              # 1..15
    block: int              # the block it describes -- the same number
    state: int
    size: int               # declared size of the save, in bytes
    link: int               # next in the chain, 0-based, or 0xFFFF
    name: str
    stored_checksum: int
    computed_checksum: int

    @property
    def state_name(self) -> str:
        return FRAME_STATES.get(self.state, "unknown")

    @property
    def in_use(self) -> bool:
        return self.state in IN_USE_STATES

    @property
    def checksum_ok(self) -> bool:
        return self.stored_checksum == self.computed_checksum

    @property
    def next_frame(self) -> int | None:
        """The next frame in the chain, or `None` if this is the last one.

        The `link` is 0-BASED over the 15 data blocks, and the frame is
        1-based: link 1 means frame 2. Reading the link as a frame number makes
        the fixture's chain point at itself -- frame 1 has link 1 -- and a naive
        reader either loops forever or concludes "one-block chain" for a
        16,384-byte save. It is the declared size that breaks the tie, and that
        is how this was measured.
        """
        if self.link == CHAIN_END:
            return None
        return self.link + 1


class Card:
    """The 131,072 bytes of a card, with the directory on top.

    The raw bytes are normative (Rule 2 of section 3.3): this object holds the
    whole card and edits it by read-modify-write in place. Nothing is
    reassembled, and that is why a byte-identical round-trip is reachable.
    """

    def __init__(self, data: bytes, origin: str = "<memory>",
                 container: bytes | None = None):
        if len(data) != CARD_BYTES:
            raise CardError(
                f"{origin}: {len(data)} bytes, and a PSX memory card has "
                f"{CARD_BYTES} ({CARD_BYTES // BLOCK_BYTES} blocks of "
                f"{BLOCK_BYTES}). A file with a header in front of the card "
                f"-- a DexDrive .gme -- is opened by `gme.read_card`, which "
                f"takes the wrapper off and hands the card here. An emulator "
                f".mcd is already a raw dump and comes straight in.")
        if data[:len(MAGIC)] != MAGIC:
            raise CardError(
                f"{origin}: the first two bytes are "
                f"{data[:2].hex(' ')} and not {MAGIC.decode()} "
                f"({MAGIC.hex(' ')}). This is not a formatted memory card.")
        self.data = bytearray(data)
        self.origin = origin
        # The wrapper this card arrived in, when it arrived in one, kept whole
        # so that writing it back out is the same file and not a lookalike.
        # `gme.py` measured why: three of the eight committed containers have a
        # header of 3,904 zero bytes, and no synthesis reproduces that -- it
        # signs what it makes. `None` means the card came from a raw dump.
        self.container = bytes(container) if container is not None else None

    # -- reading ----------------------------------------------------------

    @classmethod
    def from_file(cls, path) -> "Card":
        with open(path, "rb") as fh:
            return cls(fh.read(), origin=str(path))

    def frame(self, index: int) -> bytes:
        return bytes(self.data[index * FRAME_BYTES:(index + 1) * FRAME_BYTES])

    def block(self, index: int) -> bytes:
        return bytes(self.data[index * BLOCK_BYTES:(index + 1) * BLOCK_BYTES])

    def header_checksum_ok(self) -> bool:
        """Frame 0 has a checksum too, and it is not repaired either."""
        q = self.frame(0)
        return q[FRAME_BYTES - 1] == frame_checksum(q)

    def directory(self) -> list[DirectoryEntry]:
        out = []
        for i in range(1, DIRECTORY_FRAMES + 1):
            q = self.frame(i)
            out.append(DirectoryEntry(
                frame=i,
                block=i,
                state=q[0],
                size=int.from_bytes(q[4:8], "little"),
                link=int.from_bytes(q[8:10], "little"),
                name=q[10:30].split(b"\0")[0].decode("ascii", "replace"),
                stored_checksum=q[FRAME_BYTES - 1],
                computed_checksum=frame_checksum(q),
            ))
        return out

    def stray_blocks(self) -> list[tuple[int, int, int]]:
        """Blocks holding data the directory does not declare: `(block, state, non_zero)`.

        MEASURED in the fixture: block 3 has 41 non-zero bytes and the directory
        marks it `0xA0`, free. It is not litter -- it is where the formation,
        the kickers and the tactic live. It is what makes "is this card valid
        for the console?" an open question (section 5.6 of the plan), and it is
        why this measurement is a command and not a stray script.
        """
        found = self.find_save()
        declared = set(found[1]) if found else set()
        out = []
        for b in range(1, DIRECTORY_FRAMES + 1):
            if b in declared:
                continue
            nz = sum(1 for x in self.block(b) if x)
            if nz:
                out.append((b, self.frame(b)[0], nz))
        return out

    def bad_checksums(self) -> list[int]:
        """The frames whose XOR does not match -- REPORTED, never repaired.

        Not recalculating the checksum is MEASURED behaviour of the original,
        and section 6 of the plan says to reproduce it for now: diverging with
        no oracle trades one unknown for another. Whoever wants to change that
        measures first, in MCR-TASK-13.
        """
        bad = [] if self.header_checksum_ok() else [0]
        bad += [d.frame for d in self.directory() if not d.checksum_ok]
        return bad

    def chain(self, start_frame: int) -> list[int]:
        """The frames of one chain, following `link` from `start_frame`."""
        seen: list[int] = []
        entries = {d.frame: d for d in self.directory()}
        cur = start_frame
        while cur is not None:
            if cur in seen:
                raise CardError(
                    f"{self.origin}: the chain starting at frame "
                    f"{start_frame} returns to frame {cur} -- corrupt "
                    f"directory, or the `link` was read as a frame number "
                    f"instead of a 0-based block index.")
            if cur not in entries:
                raise CardError(
                    f"{self.origin}: the chain starting at frame "
                    f"{start_frame} points to frame {cur}, outside "
                    f"1..{DIRECTORY_FRAMES}.")
            seen.append(cur)
            cur = entries[cur].next_frame
        return seen

    def find_save(self, pattern: re.Pattern = SAVE_NAME_RE):
        """The WE2002 save: the entry, and the blocks it actually occupies.

        Returns `(entry, [blocks])`, or `None` if there is none.

        NAMING THE BLOCK IS THE POINT. The upstream assumes where the save is
        and, if it is somewhere else, every address shifts by multiples of 8192
        and the result still looks plausible on screen -- that is trap 6 of the
        profile. Here the block is read from the directory and returned with it.
        """
        for d in self.directory():
            if d.in_use and d.state == 0x51 and pattern.match(d.name):
                return d, self.chain(d.frame)
        return None

    # -- writing ----------------------------------------------------------

    def write(self, offset: int, payload: bytes) -> None:
        """Writes `payload` at `offset`, or REFUSES with the reason.

        The refusal below `0x800` is not a courtesy comment: it is the negative
        control case of section 5.2 of the plan, and it exists because the
        upstream's `GrabarData` writes exactly there.
        """
        if offset < 0:
            raise Refused(f"negative offset: {offset}")
        end = offset + len(payload)
        if end > CARD_BYTES:
            raise Refused(
                f"a {len(payload)}-byte write at {offset:#07x} runs past the "
                f"end of the card ({CARD_BYTES:#07x}).")
        if offset < HEADER_BYTES:
            raise Refused(
                f"write at {offset:#07x}, below {HEADER_BYTES:#05x}: that is "
                f"where the `MC` header frame and the {DIRECTORY_FRAMES} "
                f"directory frames live -- state, size, link, name and "
                f"checksum of every block. A card with that overwritten is "
                f"read by no console. It is what the upstream does to bytes "
                f"0..137, and what the port does not do.")
        self.data[offset:end] = payload

    def to_bytes(self) -> bytes:
        return bytes(self.data)


# --- the synthetic card, for the self-check -------------------------------

def synthetic_card(save_name: str = "BISLPM-86600WEW-OPT",
                   blocks: int = 2) -> Card:
    """A valid card assembled in memory -- no fixture, no disk.

    It is what makes `mcr_selftest` run on any machine. The chain has `blocks`
    blocks so that the 0-based `link` test has something to exercise: with a
    single block, reading the link wrongly would go unnoticed.
    """
    data = bytearray(b"\x00" * CARD_BYTES)
    data[0:2] = MAGIC
    for i in range(1, DIRECTORY_FRAMES + 1):
        q = bytearray(b"\x00" * FRAME_BYTES)
        if i <= blocks:
            q[0] = 0x51 if i == 1 else (0x53 if i == blocks else 0x52)
            q[4:8] = (BLOCK_BYTES * blocks).to_bytes(4, "little")
            # 0-based link: frame i points to frame i+1 with the value i
            q[8:10] = (CHAIN_END if i == blocks else i).to_bytes(2, "little")
            if i == 1:
                q[10:10 + len(save_name)] = save_name.encode("ascii")
        else:
            q[0] = 0xA0
            q[8:10] = CHAIN_END.to_bytes(2, "little")
        q[FRAME_BYTES - 1] = frame_checksum(q)
        data[i * FRAME_BYTES:(i + 1) * FRAME_BYTES] = q
    data[127] = frame_checksum(data[0:FRAME_BYTES])
    return Card(bytes(data), origin="<synthetic>")


# --- self-check -----------------------------------------------------------

def self_check(verbose: bool=True) -> int:
    """Exercises the module against a synthetic card. Returns the failure count.

    Every refusal is a RED CASE: the test does not ask "does the module accept
    what is valid", it asks "does the module refuse what is invalid, and for the
    right reason". A guard that has never gone red is decoration -- the lesson
    of CORR-PES2-009 and -020.
    """
    return harness.run("card.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(Refused)
    c = synthetic_card()

    # --- what has to work
    ok("magic and size accepted", c.to_bytes()[:2] == MAGIC
       and len(c.to_bytes()) == CARD_BYTES)
    ok("header checksum matches", c.header_checksum_ok())
    ok("no bad checksum in the synthetic card", c.bad_checksums() == [],
       f"bad={c.bad_checksums()}")
    ok("15 directory frames", len(c.directory()) == DIRECTORY_FRAMES)

    d = c.directory()
    ok("frame 1 in use, first of the chain", d[0].state == 0x51 and d[0].in_use)
    ok("frame 1 names its state", d[0].state_name.startswith("in use"))
    ok("frame 3 free", d[2].state == 0xA0 and not d[2].in_use)

    found = attempt("finds the save by name", c.find_save)
    ok("finds the save by name", found is not None)
    if found:
        entry, blocks = found
        ok("says which blocks the save is in", blocks == [1, 2], f"blocks={blocks}")
        ok("declared size matches the chain",
           entry.size == len(blocks) * BLOCK_BYTES,
           f"size={entry.size} blocks={len(blocks)}")

    # The 0-based link, exercised head on: frame 1 has link 1 and points to
    # frame 2. Read as a frame number, it would point at itself.
    ok("0-based link becomes the next frame",
       d[0].link == 1 and d[0].next_frame == 2,
       f"link={d[0].link} next={d[0].next_frame}")
    ok("end of chain is None", d[1].next_frame is None)

    ok("HEADER_BYTES is derived and equals 0x800", HEADER_BYTES == 0x800)

    # valid write, into the data
    before = c.to_bytes()
    c.write(HEADER_BYTES, b"\xAA\xBB")
    ok("write at 0x800 is accepted", c.to_bytes()[0x800:0x802] == b"\xAA\xBB")
    ok("a valid write only touches what it asked for",
       sum(1 for a, b in zip(before, c.to_bytes()) if a != b) == 2)

    # --- the refusals: the red cases
    refuses("refuses a write at 0x0000",
            lambda: c.write(0, b"\x00" * 138), "below 0x800")
    refuses("refuses a write at the last directory byte",
            lambda: c.write(HEADER_BYTES - 1, b"\x00"), "below 0x800")
    refuses("refuses a write running past the end of the card",
            lambda: c.write(CARD_BYTES - 1, b"\x00\x00"), "past the end")
    refuses("refuses a negative offset",
            lambda: c.write(-1, b"\x00"), "negative")

    refuses("refuses a file truncated by 1 byte",
            lambda: Card(bytes(CARD_BYTES - 1), origin="<truncated>"),
            "bytes, and a PSX memory card", kind=CardError)
    refuses("refuses a file with no MC",
            lambda: Card(b"\x00" * CARD_BYTES, origin="<no magic>"),
            "not a formatted memory card", kind=CardError)

    # a diverging checksum is REPORTED, never repaired
    dirty = synthetic_card()
    dirty.data[3 * FRAME_BYTES + FRAME_BYTES - 1] ^= 0xFF
    ok("a diverging checksum is reported", dirty.bad_checksums() == [3],
       f"bad={dirty.bad_checksums()}")
    ok("a diverging checksum is NOT repaired",
       dirty.frame(3)[FRAME_BYTES - 1] != frame_checksum(dirty.frame(3)))

    stray = attempt("data outside the chain is computable", c.stray_blocks,
                    default=None)
    ok("the synthetic card has no data outside the chain", stray == [],
       f"stray={stray}")
    littered = synthetic_card()
    littered.write(3 * BLOCK_BYTES, b"\x01\x02\x03")
    found_stray = attempt("a free block with data is computable",
                          littered.stray_blocks)
    ok("data in a free block is denounced", found_stray == [(3, 0xA0, 3)],
       f"stray={found_stray}")

    # the negative of section 5.2: turning frame 1's state from 0x51 to 0xA0
    lost = synthetic_card()
    lost.data[1 * FRAME_BYTES] = 0xA0
    lost.data[1 * FRAME_BYTES + FRAME_BYTES - 1] = frame_checksum(
        lost.frame(1))
    ok("the save disappears when frame 1 turns 0xA0",
       attempt("find_save on a card with no save", lost.find_save, "?") is None)

    # a chain that comes back on itself -- the symptom of reading the link as a
    # frame number
    loop = synthetic_card()
    loop.data[1 * FRAME_BYTES + 8:1 * FRAME_BYTES + 10] = (0).to_bytes(2, "little")
    refuses("refuses a circular chain",
            lambda: loop.chain(1), "returns to frame", kind=CardError)


# --- CLI ------------------------------------------------------------------

def _report(card: Card) -> dict:
    found = card.find_save()
    return {
        "origin": card.origin,
        "bytes": CARD_BYTES,
        "magic_ok": True,
        "bad_checksums": card.bad_checksums(),
        "save": None if found is None else {
            "name": found[0].name,
            "blocks": found[1],
            "declared_size": found[0].size,
            "first_block_offset": found[1][0] * BLOCK_BYTES,
        },
        "blocks_outside_the_chain": [
            {"block": b, "state": f"{e:#04x}", "non_zero_bytes": n}
            for b, e, n in card.stray_blocks()
        ],
        "directory": [
            {"frame": d.frame, "state": f"{d.state:#04x}",
             "state_name": d.state_name, "size": d.size,
             "link": f"{d.link:#06x}", "next_frame": d.next_frame,
             "name": d.name, "checksum_ok": d.checksum_ok}
            for d in card.directory()
        ],
    }


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?", help="the .mcr to inspect")
    ap.add_argument("--json", action="store_true", help="output as JSON")
    ap.add_argument("--blocks", action="store_true",
                    help="non-zero bytes per block, and what falls outside "
                         "the chain")
    ap.add_argument("--self-check", action="store_true",
                    help="run the self-check, with no card at all")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0

    if not a.card:
        ap.error("give a .mcr, or use --self-check")

    try:
        card = Card.from_file(a.card)
    except (CardError, OSError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2

    if a.blocks:
        found = card.find_save()
        declared = set(found[1]) if found else set()
        d = {x.frame: x for x in card.directory()}
        print(" block  state  non-zero bytes")
        for b in range(1, DIRECTORY_FRAMES + 1):
            nz = sum(1 for x in card.block(b) if x)
            mark = "  <-- outside the declared chain" if nz and b not in declared else ""
            print(f"   {b:2d}   {d[b].state:#04x}   {nz:6d}{mark}")
        return 0

    rep = _report(card)
    if a.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        return 0

    print(f"{card.origin}: {CARD_BYTES} bytes, magic MC")
    bad = rep["bad_checksums"]
    print(f"frame checksums: "
          f"{'all match' if not bad else f'DIVERGE in frames {bad}'}"
          f"  (reported, never repaired)")
    if rep["save"]:
        s = rep["save"]
        print(f"WE2002 save: {s['name']!r} in blocks {s['blocks']}, "
              f"{s['declared_size']} bytes declared, "
              f"first block at {s['first_block_offset']:#07x}")
    else:
        print("WE2002 save: NOT found on this card")
    print()
    print("  f  state   as                                        size  link"
          "   name")
    for d in card.directory():
        print(f" {d.frame:2d}   {d.state:#04x}  {d.state_name:<40} "
              f"{d.size:>6}  {d.link:#06x}  {d.name}")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())

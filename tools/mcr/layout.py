#!/usr/bin/env python3
"""The save's 17 destinations -- THE SINGLE SOURCE OF ADDRESSES.

Provenance (section 3.4 of the plan):

  container   --
  address     `wte/re/mcr.md`, the 17 destinations measured out of
              `we-team-editor.exe`, both sides: the writer at `0x0040f150`
              (`grabar_memoryClick`) and the reader at `0x0040b9ec`
  semantics   the field names are ours; what X, Y, roles and the domains MEAN
              is the upstream's, and that lives in `formation.py`/`domains.py`
  codec       --

Rule 1 of section 3.3: no other module of `tools/mcr/` writes an address
constant. A decoder written against an unverified address produces a plausible
wrong field, and the symptom only shows up in the game -- which is why this
module ships a `--check` instead of a comment saying it was verified.

The check reads `wte/re/mcr.md`, the committed artifact, and not
`wte/tools/dump_mcr.py`. Two reasons: the markdown is versioned while
`we-team-editor.exe` is not, so the check runs on a clean clone; and the table
below is written independently of the tool that emits the markdown, so the two
agreeing means something. Importing the generator would be checking it against
itself.

Usage:

    python3 tools/mcr/layout.py
    python3 tools/mcr/layout.py --check
    python3 tools/mcr/layout.py --self-check
"""

import argparse
import dataclasses
import os
import re
import sys
import harness                                           # noqa: E402

_MEASUREMENT = os.path.join("wte", "re", "mcr.md")


def _find_measurement() -> str:
    """Walks up from this file looking for `wte/re/mcr.md`.

    Counting `dirname` hops looked equivalent and is not: copy the module
    anywhere -- which is what its own negative controls do -- and a fixed hop
    count points at a directory that does not exist, so `--check` dies with a
    path error instead of running. Every control run then reported three
    failures that had nothing to do with the planted defect, which is exactly
    how a control stops being readable. Walking up finds the repository from
    wherever the module actually sits, and the fallback keeps a nameable path
    in the error when there is no repository at all.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    while True:
        candidate = os.path.join(here, _MEASUREMENT)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            return os.path.join(here, _MEASUREMENT)
        here = parent


MCR_MD = _find_measurement()


def find_upward(relative: str) -> str | None:
    """Walks up from this file looking for `relative`; `None` if never found.

    The generalisation of `_find_measurement`, hoisted here after the same
    defect appeared twice more: `attributes.py` and `domains.py` each located
    the upstream clone by counting `dirname` hops from `__file__`, so a copy of
    the module one directory shallower -- which is what every negative control
    is -- pointed at a directory that does not exist. The check did not fail;
    it SKIPPED, and the control came out green with an invented label in place.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    while True:
        candidate = os.path.join(here, relative)
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent

BLOCK_BYTES = 8192      # only to derive the block number; the container is card.py


class LayoutError(Exception):
    """The written layout and the measured one disagree."""


@dataclasses.dataclass(frozen=True)
class Destination:
    """One measured destination.

    `total_bytes` is what the measurement counts: for a strided field it is
    `item_size * count`, NOT the span. The player record is the case that makes
    the difference matter -- 276 bytes of attributes live as 23 chunks of 12 at
    stride 32, so the span is 23*32 and reading `0x5904..0x5904+276` would walk
    straight through names and untouched bytes.
    """

    address: int
    total_bytes: int
    field: str
    reads_back: bool = True      # the writer and the reader are NOT symmetric
    item_size: int | None = None
    count: int | None = None
    stride: int | None = None

    @property
    def block(self) -> int:
        return self.address // BLOCK_BYTES

    @property
    def strided(self) -> bool:
        return self.stride is not None

    def item_address(self, index: int) -> int:
        """The address of item `index` of a strided destination."""
        if not self.strided:
            raise LayoutError(f"{self.field} is not strided")
        if not 0 <= index < self.count:
            raise LayoutError(
                f"{self.field}: index {index} outside 0..{self.count - 1}")
        return self.address + index * self.stride


# --- the 17 destinations ---------------------------------------------------
# Written from `wte/re/mcr.md`, and checked back against it by `--check`.
# The order is the address order of the markdown table, so a diff between the
# two reads straight.

SQUAD_SIZE = 23
PLAYER_STRIDE = 32

DESTINATIONS: tuple[Destination, ...] = (
    Destination(0x5404, 16, "shirt numbers, 23 x 5 bits"),
    Destination(0x5904, 12 * SQUAD_SIZE, "player j: 12 B of attributes",
                item_size=12, count=SQUAD_SIZE, stride=PLAYER_STRIDE),
    Destination(0x5910, 10 * SQUAD_SIZE, "player j: 10 B of name",
                item_size=10, count=SQUAD_SIZE, stride=PLAYER_STRIDE),
    # The six tactics destinations are written and NEVER read back by
    # `0x0040b9ec`. That asymmetry is measured, and it is why v1 passes tactics
    # through untouched (section 1.9 of the plan).
    Destination(0x6102, 1, "tactics byte 0, plus 50", reads_back=False),
    Destination(0x6113, 1, "kicker 3"),
    Destination(0x6122, 1, "kicker 2"),
    Destination(0x6131, 1, "kicker 4"),
    Destination(0x6140, 1, "kicker 1"),
    Destination(0x614F, 1, "kicker 0"),
    Destination(0x62A8, 20, "formation, bytes 10..29"),
    Destination(0x63D5, 10, "formation, bytes 0..9"),
    Destination(0x6479, 1, "tactics byte 1, high nibble", reads_back=False),
    Destination(0x6488, 1, "tactics byte 1, low nibble", reads_back=False),
    Destination(0x6497, 1, "tactics byte 2, low nibble", reads_back=False),
    Destination(0x64A6, 1, "tactics byte 2, high nibble", reads_back=False),
    Destination(0x64E2, 1, "tactics byte 0, raw", reads_back=False),
    Destination(0x6500, 1, "captain"),
)

BY_ADDRESS = {d.address: d for d in DESTINATIONS}


def _required(address: int, what: str) -> Destination:
    """A named view over a destination that has to be in the table.

    Bare `_required(0x63D5, "FORMATION_ROLES")` raises `KeyError: 25557` at import time when a row
    is deleted -- a decimal number, no file, no hint that a destination went
    missing. Measured while planting exactly that defect.
    """
    try:
        return BY_ADDRESS[address]
    except KeyError:
        raise LayoutError(
            f"{what} needs the destination {address:#06x}, which is not in "
            f"DESTINATIONS. A row was removed or its address was changed; "
            f"`--check` says which side disagrees with wte/re/mcr.md.") from None

# --- named views over the table -------------------------------------------
# Everything below is DERIVED. Nothing here introduces an address that is not
# already one of the 17 above.

SHIRT_NUMBERS = _required(0x5404, "SHIRT_NUMBERS")
PLAYER_ATTRIBUTES = _required(0x5904, "PLAYER_ATTRIBUTES")
PLAYER_NAME = _required(0x5910, "PLAYER_NAME")

# The five kickers in KICKER ORDER (0..4), which is not address order. The
# table is `0x614F, 0x6140, 0x6122, 0x6113, 0x6131`: it DECREASES, then jumps
# back up. Arithmetic in place of a table writes into the wrong field, and the
# result still looks like a formation.
KICKER_ADDRESSES = (0x614F, 0x6140, 0x6122, 0x6113, 0x6131)

# The captain. SETTLED IN MCR-TASK-13, and it was our reading that was wrong:
# section 1.8 of the plan had this as the captain by our RE of the `.exe` and a
# sixth kicker by the upstream. Three measurements agree it is the captain --
# the sixth column of the `estrategia` form's `malla2`, whose label's Hint is
# `Captain`; a driven experiment that put the six columns on six distinct rows
# and got 0,1,2,3,4 in the five kickers and 5 here; and the upstream's own
# source, where the value written to 25856 is a local called `CP`, beside
# `SF`, `LF`, `RC`, `LC` and `PK`. Nobody ever called it a sixth kicker: we
# read that off its POSITION, sixth in a group of six.
CAPTAIN = _required(0x6500, "CAPTAIN")

# The 20 bytes at `0x62A8` are ONE destination in the measurement, and the
# upstream reads them as two arrays of ten: X then Y. That split is semantics,
# not a new address, so it stays derived -- adding it to DESTINATIONS would make
# the count 18 and break the very check this module exists for.
FORMATION_XY = _required(0x62A8, "FORMATION_XY")
FORMATION_X_ADDRESS = FORMATION_XY.address            # 0x62A8, 10 bytes
FORMATION_Y_ADDRESS = FORMATION_XY.address + 10       # 0x62B2, 10 bytes
FORMATION_ROLES = _required(0x63D5, "FORMATION_ROLES")
OUTFIELD_COUNT = 10

TACTICS = tuple(d for d in DESTINATIONS if not d.reads_back)

# Bit shifts of the 5-bit shirt number: six values per 4-byte group, 30 bits
# used and 2 lost, four groups, 16 bytes. Same shape as `SquadNumbers` in
# `we2002_core`.
SHIRT_NUMBER_BIT_SHIFTS = (0, 5, 2, 7, 4, 1)
SHIRT_NUMBERS_PER_GROUP = 6
SHIRT_NUMBER_GROUP_BYTES = 4


def player_attribute_address(index: int) -> int:
    return PLAYER_ATTRIBUTES.item_address(index)


def player_name_address(index: int) -> int:
    return PLAYER_NAME.item_address(index)


def kicker_address(kicker: int) -> int:
    if not 0 <= kicker < len(KICKER_ADDRESSES):
        raise LayoutError(
            f"kicker {kicker} outside 0..{len(KICKER_ADDRESSES) - 1}")
    return KICKER_ADDRESSES[kicker]


# --- the option file's records --------------------------------------------
#
# A SECOND MEASUREMENT, AND A SEPARATE ONE. Everything above is the TEAM save:
# 17 destinations measured out of `we-team-editor.exe`, addresses absolute in
# the card, cross-checked against `wte/re/mcr.md`. Nothing below came from that
# binary and nothing below is in that markdown, so `--check` does not touch it
# and the count of 17 does not move.
#
# Provenance of this section:
#
#   container   card.py -- the block comes from the directory, and the PSX save
#               header says how many icon frames stand between the block start
#               and the first byte of data
#   address     MEASURED HERE on 2026-09-11, by diffing four option files saved
#               from one session of the game with nothing changed but the
#               camera. The camera moved one byte and the record checksum in
#               front of it; patching those two into the clean card reproduced
#               each of the other three BYTE FOR BYTE, outside the title
#               padding that the game leaves uninitialised
#   semantics   the nine camera names are the game's own, off its option screen
#   codec       --
#
# NOTHING HERE IS AN ABSOLUTE ADDRESS, and that is deliberate. The team save's
# 17 are absolute because the upstream wrote them that way, and trap 6 of the
# profile is what that costs: move the save to another block and every one of
# them lands 8,192 bytes off, still looking plausible. These are offsets INSIDE
# the save, and `options.py` resolves them against the block the directory
# actually names. The user's cards hold this save in block 1, where every
# absolute address above would be wrong by 8,192.


@dataclasses.dataclass(frozen=True)
class OptionField:
    """One field inside one record of the option save."""

    record: int             # index into OPTION_RECORD_OFFSETS
    offset: int             # from the first byte of the record's PAYLOAD
    size: int
    field: str


# Each record is `[u16 size, little endian][u8 checksum][payload]`, and the
# checksum is the payload's bytes summed mod 256. Both were measured the same
# way: the sum matches in all six cards on hand, and the two records of one
# card have independent checksums that each moved only when their own payload
# did.
OPTION_RECORD_HEADER_BYTES = 3

# Where each record starts, counted from the first byte of the save's data.
# THE RECORDS ARE NOT PACKED. Record 0 ends 119 bytes before record 1 begins,
# and the gap is zeros -- so walking the chain by `offset + 3 + size` reads a
# size of 0 and concludes the save has one record. Measured; the offsets are a
# table for that reason.
OPTION_RECORD_OFFSETS = (0x000, 0x100)

# What each record declared in all six cards. The reader takes the size from
# the file and never from here; this is what `options.py --check` holds the
# file up against, so a card with a different build of the save is NAMED
# instead of being decoded into plausible nonsense.
OPTION_RECORD_MEASURED_SIZES = (134, 12420)

# The one field measured so far. The rest of record 0 is 50 little-endian
# u16 pad masks -- the button configuration -- and 32 further bytes nobody has
# moved one at a time yet.
CAMERA = OptionField(record=0, offset=1, size=1, field="camera")

OPTION_FIELDS: tuple[OptionField, ...] = (CAMERA,)


def option_record_offset(index: int) -> int:
    """Where record `index` starts, from the first byte of the save's data."""
    if not 0 <= index < len(OPTION_RECORD_OFFSETS):
        raise LayoutError(
            f"option record {index} outside "
            f"0..{len(OPTION_RECORD_OFFSETS) - 1}")
    return OPTION_RECORD_OFFSETS[index]


# --- the cross-check against `wte/re/mcr.md` -------------------------------

_ROW = re.compile(
    r"^\|\s*`0x([0-9a-fA-F]+)`\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|")


def parse_mcr_md(path: str = MCR_MD) -> dict[int, tuple[int, int, str]]:
    """`{address: (block, total_bytes, field)}` from the measured table.

    Only rows whose first cell is a backticked hex address count, which is what
    separates the destination table from the directory table above it.
    """
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        raise LayoutError(f"cannot read the measurement at {path}: {e}") from e

    out: dict[int, tuple[int, int, str]] = {}
    for line in text.splitlines():
        m = _ROW.match(line)
        if not m:
            continue
        addr = int(m.group(1), 16)
        if addr in out:
            raise LayoutError(
                f"{path}: address {addr:#06x} appears twice in the table")
        out[addr] = (int(m.group(2)), int(m.group(3)), m.group(4))
    if not out:
        raise LayoutError(
            f"{path}: no destination row parsed. The table shape changed, and "
            f"a check that parses nothing passes for the wrong reason.")
    return out


def check(path: str = MCR_MD, verbose: bool = True) -> list[str]:
    """Compares this table with the measured one. Returns the complaints."""
    problems: list[str] = []
    measured = parse_mcr_md(path)
    ours = {d.address: d for d in DESTINATIONS}

    # Both directions: present on one side and absent on the other is a failure.
    only_ours = sorted(set(ours) - set(measured))
    only_theirs = sorted(set(measured) - set(ours))
    for a in only_ours:
        problems.append(
            f"{a:#06x} ({ours[a].field}) is in layout.py and NOT in the "
            f"measurement")
    for a in only_theirs:
        problems.append(
            f"{a:#06x} ({measured[a][2]}) is in the measurement and NOT in "
            f"layout.py")

    for a in sorted(set(ours) & set(measured)):
        block, total, field = measured[a]
        d = ours[a]
        if d.total_bytes != total:
            problems.append(
                f"{a:#06x} ({field}): {d.total_bytes} bytes here, {total} "
                f"measured")
        if d.block != block:
            problems.append(
                f"{a:#06x} ({field}): block {d.block} here, {block} measured")

    if verbose:
        n = len(set(ours) & set(measured))
        print(f"layout.py --check: {n}/{len(measured)} destinations agree with "
              f"{os.path.relpath(path)}"
              + ("" if not problems else f", {len(problems)} problem(s)"))
        for p in problems:
            print(f"  FAIL {p}")
    return problems


# --- Rule 1, enforced -----------------------------------------------------
# "Only layout.py has addresses" is worth nothing as prose. This is the sweep
# that can fail on it, and MCR-TASK-10 aggregates it into `selftest.py`.

MCR_DIR = os.path.dirname(os.path.abspath(__file__))

# The save's own address space. Every one of the 17 destinations falls inside
# it, and no container constant does: `card.py` carries 0x20000, 8192, 128 and
# the derived 0x800, all outside. Narrower than "any hex literal" on purpose --
# a sweep that flags 0x800 gets switched off within a week.
SAVE_SPACE = (0x4000, 0x8000)

_HEX = re.compile(r"0[xX][0-9a-fA-F]+")
_DEC = re.compile(r"(?<![\w.])\d{4,6}(?![\w.])")


def _code_lines(path: str):
    """`(lineno, source)` with comments and string literals removed.

    THE SWEEP MEASURES CODE, NOT PROSE. A module that operates on `0x62A8` has
    to be able to say so in its own docstring, and `formation.py` names eleven
    addresses in its documentation on purpose -- the open `0x6500` is a
    completion criterion of MCR-TASK-08. A textual sweep flagged all eleven,
    which would have left two bad options: gut the documentation, or switch the
    sweep off. Tokenising costs four lines and keeps both.

    String literals go too. A constant smuggled as `int("0x5904", 16)` would
    escape, which is a contrivance nobody writes by accident; forbidding a
    module to quote the address it documents is a cost paid every day.
    """
    import io
    import tokenize
    with open(path, "rb") as fh:
        source = fh.read()
    skip = {tokenize.COMMENT, tokenize.STRING, tokenize.NL, tokenize.NEWLINE,
            tokenize.INDENT, tokenize.DEDENT, tokenize.ENCODING,
            tokenize.ENDMARKER}
    # Python 3.12 split f-strings into their own token types, so the literal
    # text inside one is FSTRING_MIDDLE and NOT STRING. Without these three the
    # sweep reads the prose inside every f-string as code -- measured: a `print`
    # that names `0x6500` in its message was reported as a stray address.
    for extra in ("FSTRING_START", "FSTRING_MIDDLE", "FSTRING_END"):
        if hasattr(tokenize, extra):
            skip.add(getattr(tokenize, extra))
    lines: dict[int, list[str]] = {}
    try:
        for tok in tokenize.tokenize(io.BytesIO(source).readline):
            if tok.type in skip:
                continue
            lines.setdefault(tok.start[0], []).append(tok.string)
    except tokenize.TokenError as e:
        raise LayoutError(f"{path}: cannot be tokenised: {e}") from None
    return [(n, " ".join(parts)) for n, parts in sorted(lines.items())]


def address_monopoly(directory: str = MCR_DIR) -> list[str]:
    """Modules other than this one carrying a save address. Empty is correct.

    Both notations are swept, because the upstream writes them in decimal --
    22788 and 21508 read as ordinary numbers and would walk straight past a
    hex-only sweep.

    THE WALK IS THE POINT, and CORR-MCR-014 is why: this enumerated with
    `os.listdir`, which stops at the top, and `tools/mcr/ui/` -- the one place
    where a literal transcription of the upstream WinForms is most likely to
    carry a raw address -- was invisible to it. No skip, no change of count,
    three green gates. The criterion says `tools/mcr/**.py`, and `**` is
    recursive. Complaints name `rel`, not `name`: with the descent, `app.py`
    alone no longer identifies a file and `ui/app.py` does.
    """
    known = {d.address for d in DESTINATIONS} | set(KICKER_ADDRESSES) \
        | {FORMATION_Y_ADDRESS}
    complaints = []
    here = os.path.abspath(__file__)
    for root, dirs, names in os.walk(directory):
        dirs[:] = sorted(d for d in dirs if d != "__pycache__")
        for name in sorted(names):
            if not name.endswith(".py"):
                continue
            path = os.path.join(root, name)
            if os.path.abspath(path) == here:
                continue
            rel = os.path.relpath(path, directory)
            for lineno, text in _code_lines(path):
                for m in _HEX.finditer(text):
                    v = int(m.group(), 16)
                    if SAVE_SPACE[0] <= v < SAVE_SPACE[1]:
                        complaints.append(
                            f"{rel}:{lineno}: {m.group()} is in the save "
                            f"address space; addresses belong in layout.py")
                for m in _DEC.finditer(text):
                    if int(m.group()) in known:
                        complaints.append(
                            f"{rel}:{lineno}: {m.group()} is a save address in "
                            f"decimal; addresses belong in layout.py")
    return complaints


# --- self-check ------------------------------------------------------------

def self_check(verbose: bool=True) -> int:
    """Exercises the module. Returns the number of failures.

    The red case is the point: changing one address by hand has to make
    `--check` fail AND NAME IT. A check that only counts rows stays green when
    an address moves, which is the exact defect it exists to catch.
    """
    return harness.run("layout.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    import tempfile

    ok("17 destinations", len(DESTINATIONS) == 17, f"n={len(DESTINATIONS)}")
    ok("no duplicate address", len(BY_ADDRESS) == len(DESTINATIONS))
    ok("addresses in ascending order",
       list(BY_ADDRESS) == sorted(BY_ADDRESS))

    # The two assertions `mcr.md` already charges for.
    ok("the kicker table is NOT increasing",
       list(KICKER_ADDRESSES) != sorted(KICKER_ADDRESSES),
       f"table={[hex(a) for a in KICKER_ADDRESSES]}")
    ok("every kicker address is one of the 17",
       all(a in BY_ADDRESS for a in KICKER_ADDRESSES))
    ok("shirt bit shifts are (5*(j mod 6)) mod 8",
       SHIRT_NUMBER_BIT_SHIFTS
       == tuple((5 * (j % SHIRT_NUMBERS_PER_GROUP)) % 8
                for j in range(SHIRT_NUMBERS_PER_GROUP)),
       f"shifts={SHIRT_NUMBER_BIT_SHIFTS}")
    groups = SHIRT_NUMBERS.total_bytes // SHIRT_NUMBER_GROUP_BYTES
    ok("16 bytes = 4 groups of 4, holding 24 five-bit numbers",
       SHIRT_NUMBERS.total_bytes == 16 and groups == 4
       and groups * SHIRT_NUMBERS_PER_GROUP == 24
       and groups * SHIRT_NUMBERS_PER_GROUP > SQUAD_SIZE,
       f"bytes={SHIRT_NUMBERS.total_bytes} groups={groups}")

    # The strided player record -- the case where total_bytes is not a span.
    ok("attributes: 23 x 12 at stride 32",
       PLAYER_ATTRIBUTES.count == 23 and PLAYER_ATTRIBUTES.item_size == 12
       and PLAYER_ATTRIBUTES.stride == 32)
    ok("attributes total is 276, not the span",
       PLAYER_ATTRIBUTES.total_bytes == 276
       and PLAYER_ATTRIBUTES.total_bytes != 23 * 32)
    ok("name sits 12 bytes past the attributes, same record",
       PLAYER_NAME.address - PLAYER_ATTRIBUTES.address
       == PLAYER_ATTRIBUTES.item_size)
    ok("player 0 and player 22 addresses",
       player_attribute_address(0) == 0x5904
       and player_attribute_address(22) == 0x5904 + 22 * 32)
    ok("name of player 22", player_name_address(22) == 0x5910 + 22 * 32)

    c.refuses("refuses player index 23",
              lambda: player_attribute_address(23), "outside 0..22",
              kind=LayoutError)

    # The six tactics destinations, written and never read back.
    ok("6 tactics destinations, none read back", len(TACTICS) == 6)
    ok("tactics addresses match the measurement",
       tuple(d.address for d in TACTICS)
       == (0x6102, 0x6479, 0x6488, 0x6497, 0x64A6, 0x64E2))

    # Blocks: derived here, and checked against the measurement by --check.
    ok("shirt numbers and players are in block 2",
       SHIRT_NUMBERS.block == 2 and PLAYER_ATTRIBUTES.block == 2
       and PLAYER_NAME.block == 2)
    ok("formation, kickers and tactics are in block 3",
       all(_required(a, "kicker").block == 3 for a in KICKER_ADDRESSES)
       and FORMATION_XY.block == 3 and FORMATION_ROLES.block == 3
       and all(d.block == 3 for d in TACTICS)
       and CAPTAIN.block == 3)
    ok("14 of the 17 fall in block 3",
       sum(1 for d in DESTINATIONS if d.block == 3) == 14,
       f"n={sum(1 for d in DESTINATIONS if d.block == 3)}")

    # X and Y are derived, not extra entries.
    ok("X and Y live inside the 20 bytes of 0x62A8",
       FORMATION_X_ADDRESS == 0x62A8 and FORMATION_Y_ADDRESS == 0x62B2
       and FORMATION_XY.total_bytes == 2 * OUTFIELD_COUNT)
    ok("0x62B2 is NOT a separate destination", 0x62B2 not in BY_ADDRESS)

    # --- the cross-check itself
    problems = attempt("--check runs", lambda: check(verbose=False), default=None)
    ok("17/17 against wte/re/mcr.md", problems == [], f"problems={problems}")

    # --- the red case: a moved address has to be named
    saved = DESTINATIONS
    try:
        globals()["DESTINATIONS"] = tuple(
            dataclasses.replace(d, address=d.address + 1)
            if d.address == 0x5404 else d for d in saved)
        moved = attempt("--check with a moved address",
                        lambda: check(verbose=False), default=[])
        ok("a moved address makes --check fail", len(moved) >= 2,
           f"problems={moved}")
        ok("and it names both sides",
           any("0x5405" in p for p in moved) and any("0x5404" in p for p in moved),
           f"problems={moved}")
    finally:
        globals()["DESTINATIONS"] = saved

    # --- the red case: a wrong size
    try:
        globals()["DESTINATIONS"] = tuple(
            dataclasses.replace(d, total_bytes=d.total_bytes + 1)
            if d.address == 0x62A8 else d for d in saved)
        sized = attempt("--check with a wrong size",
                        lambda: check(verbose=False), default=[])
        ok("a wrong size makes --check fail",
           any("21 bytes here, 20 measured" in p for p in sized),
           f"problems={sized}")
    finally:
        globals()["DESTINATIONS"] = saved

    # --- Rule 1: no other module carries an address
    # --- the option file's records, the second measurement
    ok("one option field measured so far", len(OPTION_FIELDS) == 1,
       f"n={len(OPTION_FIELDS)}")
    ok("the camera is in record 0, one byte in",
       (CAMERA.record, CAMERA.offset, CAMERA.size) == (0, 1, 1),
       f"camera={CAMERA}")
    ok("two records, and record 0 starts at the first data byte",
       len(OPTION_RECORD_OFFSETS) == 2 and option_record_offset(0) == 0)
    ok("as many measured sizes as records",
       len(OPTION_RECORD_MEASURED_SIZES) == len(OPTION_RECORD_OFFSETS))
    # The gap is the point: packed records would make a chain walk correct, and
    # it is not. If a future measurement removes the gap, the walk in
    # `options.py` can be simplified -- and this check is what would say so.
    ok("record 0 ends before record 1 begins, with a gap",
       OPTION_RECORD_HEADER_BYTES + OPTION_RECORD_MEASURED_SIZES[0]
       < option_record_offset(1),
       f"end={OPTION_RECORD_HEADER_BYTES + OPTION_RECORD_MEASURED_SIZES[0]:#x} "
       f"next={option_record_offset(1):#x}")
    # These are offsets into the save, never card addresses. A value that fell
    # inside the team save's address space would mean somebody pasted an
    # absolute address in here, which is the whole defect this section avoids.
    ok("no option offset is a card address",
       not any(SAVE_SPACE[0] <= o < SAVE_SPACE[1]
               for o in OPTION_RECORD_OFFSETS))
    c.refuses("refuses an option record that does not exist",
              lambda: option_record_offset(len(OPTION_RECORD_OFFSETS)),
              "outside 0..", kind=LayoutError)

    monopoly = attempt("the address sweep runs", address_monopoly, default=None)
    ok("no other module of tools/mcr/ has a save address", monopoly == [],
       f"complaints={monopoly}")

    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "layout.py"), "w") as fh:
            fh.write("# stands in for this module; the sweep skips it\n")
        with open(os.path.join(d, "guilty.py"), "w") as fh:
            fh.write("BASE = 0x5904\nALSO = 21508\nFINE = 0x20000\n")
        caught = attempt("the sweep runs on a planted module",
                         lambda: address_monopoly(d), default=[])
        # The sweep skips the file it is defined in, which here is the real
        # layout.py, so the planted stand-in is swept too and stays quiet.
        ok("the sweep catches a planted hex address",
           any("0x5904" in c for c in caught), f"caught={caught}")
        ok("and a planted decimal one",
           any("21508" in c for c in caught), f"caught={caught}")
        ok("and leaves container constants alone",
           not any("0x20000" in c for c in caught), f"caught={caught}")

    # --- the red case: a table that parses nothing must not pass
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as fh:
        fh.write("# no table here\n")
        empty = fh.name
    try:
        c.refuses("refuses a table that parses nothing",
                  lambda: parse_mcr_md(empty), "no destination row parsed",
                  kind=LayoutError)
    finally:
        os.unlink(empty)


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true",
                    help="cross-check against wte/re/mcr.md")
    ap.add_argument("--self-check", action="store_true",
                    help="run the self-check, including the red cases")
    ap.add_argument("--rule1", action="store_true",
                    help="sweep tools/mcr/ for addresses outside layout.py")
    ap.add_argument("--mcr-md", default=MCR_MD,
                    help="path to the measurement (default: wte/re/mcr.md)")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0

    if a.rule1:
        found = address_monopoly()
        for c in found:
            print(f"  FAIL {c}")
        print(f"layout.py --rule1: {len(found)} address(es) outside layout.py")
        return 1 if found else 0

    if a.check:
        try:
            return 1 if check(a.mcr_md) else 0
        except LayoutError as e:
            print(f"error: {e}", file=sys.stderr)
            return 2

    print(f"{len(DESTINATIONS)} destinations, from wte/re/mcr.md\n")
    print(" address  block  bytes  reads back  field")
    for d in DESTINATIONS:
        print(f"  {d.address:#06x}      {d.block}  {d.total_bytes:5d}  "
              f"{'yes' if d.reads_back else 'NO ':<10}  {d.field}"
              + (f"  [{d.count} x {d.item_size} @ stride {d.stride}]"
                 if d.strided else ""))
    print()
    print(f"kickers, in kicker order: "
          f"{', '.join(f'{a:#06x}' for a in KICKER_ADDRESSES)}  (not increasing)")
    print(f"shirt-number bit shifts:  {SHIRT_NUMBER_BIT_SHIFTS}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

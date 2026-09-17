#!/usr/bin/env python3
"""The twelve rows of LOOKS SET: what each one holds, and what it is called.

Provenance (plan section 3.4):

    container   --
    address     layout.py, as always
    codec       IN HOUSE.  `src/core/Player.cpp` unpacks the same twelve bytes,
                and it is checked against `ed.exe` byte for byte by the golden
                tests.  This module is checked against IT, mechanically:
                `--check` re-reads the expressions out of that file and runs
                them beside these.
    semantics   third party.  What a `3` in `hair_style` LOOKS like is what
                four editors' combo boxes say it looks like.

**Ranges are asserted here; names never are.**  An index outside what the field
holds is a defect anyone can prove.  A wrong label is an opinion nobody here
can disprove, because nobody has put a PlayStation in front of every value --
the same line `tools/mcr/domains.py` draws, for the same reason.

## The twelve rows are not twelve stored fields

Ten of them are.  `DEFAUL` and `NAT` are not, and what they ARE was measured on
2026-09-17 by LOOKS-TASK-23, in the running game:

  `DEFAUL` is the screen's **confirm button**.  Its one value is `O.K.`, its
      help is `Confirm`, and Circle on it leaves LOOKS SET for the player-edit
      menu.  It applies NOTHING: the twelve rows and the twelve-byte record
      come out of the press unchanged, with the nation chosen or without.
  `NAT` chooses the player's **nationality**, which is stored as one byte
      outside the twelve (`layout.PLAYER_NATION`) and survives leaving the
      screen -- the edit menu shows it as `NAT. BRA`.  It moves no look row.

**This block said, until that measurement, that the two were "the two halves of
the game's own default look per nationality", over `data/defaultlook.txt`.**
That was inference from the column names and it is wrong twice: the game
applies no default from this screen, and that file is the EDITOR's table, keyed
by TEAM -- its own header says `TEAM;NAME;...` -- listing nations AND clubs
(`Inter`, `Bayern`, `Clas. Brazil`), which the game's list of nationalities is
not.  See `nation_lines()`.

Measured on 2026-09-15 by LOOKS-TASK-09 from the other side, and still true:
neither row moves a byte of either model file, and `AGE` moves four bytes in
all of RAM.

## The count in section 1.9 was third-party opinion, and it was wrong

`/SELECT.BIN` at **157,164** is right, and two witnesses say so that the
`Offsets We2002.txt` of the Superpack never met: `OFS_PLAYER_ATTR` of
`src/core/include/we2002/Offsets.hpp` resolves to exactly that byte of exactly
that file (`tools/pes2/ofs_map.py`), and it is an offset the golden tests
verify against `ed.exe`.

The **1,242 records** beside it are not.  The block holds **1,449** -- which is
`PLAYERS_TOTAL - PLAYERS_NC`, the count `Database::Load` reads -- and the disc
agrees without being told: every one of the first 1,449 decodes to a height
between 155 and 202, and record 1,449 is the first that is all zero.

Usage:
    python tools/looks/looks.py --check
    python tools/looks/looks.py --check-image
    python tools/looks/looks.py --report [<tuple>]
    python tools/looks/looks.py --corpus [<folder of renders>]
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402

SKIP = 77

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
PLAYER_CPP = os.path.join(REPO, "src", "core", "Player.cpp")
PLAYER_TYPES_HPP = os.path.join(REPO, "src", "core", "include", "we2002",
                                "Types.hpp")
DEFAULT_LOOK = os.path.join(REPO, "data", "defaultlook.txt")

UNNAMED = "?"
"""What `label()` answers for an index inside the field and outside the table.

Three fields hold more values than anyone has named, and the two cases are
different: out of the FIELD is a defect, out of the TABLE is a gap in somebody
else's naming.  Raising on the second would make this module refuse a disc the
game plays.
"""


class BadLooks(Exception):
    """A value outside what the field holds, or a tuple that does not parse."""


# ---- the bit pieces ------------------------------------------------------

class Piece:
    """One run of bits of one byte, spelled the way `Player.cpp` spells it.

    `shift` is the C++ shift with its sign kept: positive is `>>`, negative is
    `<<`.  The mask is applied AFTER the shift, as it is there, so the bits in
    the byte are `mask << shift` for a right shift and `mask >> -shift` for a
    left one.  Keeping the spelling is what lets the cross-check compare the
    two side by side instead of comparing two translations.
    """

    __slots__ = ("byte", "shift", "mask")

    def __init__(self, byte: int, shift: int, mask: int):
        self.byte = byte
        self.shift = shift
        self.mask = mask

    def get(self, raw) -> int:
        value = raw[self.byte]
        return ((value >> self.shift) if self.shift >= 0
                else (value << -self.shift)) & self.mask

    def byte_mask(self) -> int:
        """The bits of the byte this piece owns."""
        return ((self.mask << self.shift) if self.shift >= 0
                else (self.mask >> -self.shift))

    def put(self, raw: bytearray, value: int) -> None:
        bits = value & self.mask
        moved = (bits << self.shift) if self.shift >= 0 else (bits >> -self.shift)
        raw[self.byte] = (raw[self.byte] & ~self.byte_mask() & 0xFF) | moved  # not-an-address: a byte mask


class Field:
    """One stored field: where its bits are, what it is biased by, its labels."""

    __slots__ = ("name", "row", "pieces", "bias", "labels", "values")

    def __init__(self, name, row, pieces, bias=0, labels=(), values=None):
        self.name = name
        self.row = row
        self.pieces = pieces
        self.bias = bias
        self.labels = tuple(labels)
        self.values = values if values is not None else self.span()

    def span(self) -> int:
        """How many distinct values the bits can hold."""
        width = 0
        for piece in self.pieces:
            width |= piece.mask
        return width + 1

    def get(self, raw) -> int:
        return self.bias + sum(piece.get(raw) for piece in self.pieces)

    def put(self, raw: bytearray, value: int) -> None:
        if not self.bias <= value < self.bias + self.values:
            raise BadLooks("%s=%d is outside %d..%d"
                           % (self.name, value, self.bias,
                              self.bias + self.values - 1))
        for piece in self.pieces:
            piece.put(raw, value - self.bias)

    def label(self, value: int) -> str:
        if not self.bias <= value < self.bias + self.values:
            raise BadLooks("%s=%d is outside %d..%d"
                           % (self.name, value, self.bias,
                              self.bias + self.values - 1))
        index = value - self.bias
        if not self.labels:
            return str(value)
        return self.labels[index] if index < len(self.labels) else UNNAMED

    def index_of(self, text: str) -> int:
        for index, name in enumerate(self.labels):
            if name.upper() == text.upper():
                return self.bias + index
        raise BadLooks("%r is not a %s: %s"
                       % (text, self.name, ", ".join(self.labels)))


LETTERS = ("A", "B", "C", "D", "E", "F", "G", "H")

HAIR_STYLES = ("A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "C1",
               "C2", "D1", "D2", "E1", "E2", "F1", "F2", "F3", "G1", "H1",
               "I1", "I2", "I3", "J1", "K1", "L1", "L2", "L3", "M1", "N1",
               "O1", "P1")
"""Thirty-two, and not a pattern: the letters run A to P and the count per
letter is 3, 6, 2, 2, 2, 3, 1, 1, 3, 1, 1, 3, 1, 1, 1, 1.  Written out because
the .mcr cycle measured what guessing the pattern costs -- an invented
`C3, C4, ...` passes every range check and only a re-read of the source
catches it."""


FIELDS = (
    Field("skin_colour", "SKIN", (Piece(4, 0, 0x03),), labels=LETTERS[:4]),  # not-an-address: bit masks
    Field("hair_style", "HAIR",
          (Piece(0, 4, 0x0F), Piece(1, -4, 0x10)), labels=HAIR_STYLES),  # not-an-address: idem
    Field("hair_colour", "H.COL", (Piece(1, 1, 0x07),), labels=LETTERS),  # not-an-address: idem
    Field("beard_style", "FACE", (Piece(1, 5, 0x07),), labels=LETTERS[:7]),  # not-an-address: idem
    Field("beard_colour", "H.F.COL.", (Piece(2, 1, 0x07),), labels=LETTERS[:7]),  # not-an-address: idem
    Field("height", "HEIG",
          (Piece(2, 4, 0x0F), Piece(3, -4, 0x30)), bias=148),  # not-an-address: idem
    Field("build", "BODY", (Piece(4, 2, 0x07),), labels=LETTERS),  # not-an-address: idem
    Field("age", "AGE", (Piece(4, 5, 0x07), Piece(5, -3, 0x18)), bias=15),  # not-an-address: idem
    Field("boots", "BOOTS", (Piece(11, 3, 0x07),), labels=LETTERS),  # not-an-address: idem
    Field("foot", "FOOT", (Piece(11, 6, 0x03),),  # not-an-address: idem
          labels=("R", "L", "B")),
)
"""The ten rows of LOOKS SET that are stored in the player's twelve bytes.

Spelled piece for piece as `src/core/Player.cpp` spells them, and `--check`
proves that by running both over random blobs.  The labels are the third
party's: `en_we2000edit`, `src/app/Commands.cpp` and `tools/mcr/domains.py` all
carry the same lists, which is agreement and not proof.
"""

BY_NAME = {field.name: field for field in FIELDS}
BY_ROW = {field.row: field for field in FIELDS}

UNSTORED = {
    "DEFAUL": "the screen's confirm button: one value, `O.K.`, help `Confirm`, "
              "and Circle on it leaves LOOKS SET applying nothing -- measured "
              "in the game on 2026-09-17 (LOOKS-TASK-23)",
    "NAT": "chooses the player's nationality, kept in one byte outside the "
           "twelve (layout.PLAYER_NATION) and moving no look row.  Neither "
           "row is a field of the twelve bytes, and neither moves a byte of "
           "either model file",
}
"""The two rows of the screen that store none of the twelve bytes -- see the
module docstring, and note that `NAT` does store something, elsewhere."""

SCREEN = ("DEFAUL", "NAT", "SKIN", "HAIR", "H.COL", "FACE", "H.F.COL.",
          "HEIG", "BODY", "AGE", "BOOTS", "FOOT")
"""The rows top to bottom.  `--check` asserts this equals `oracle.ROWS`, which
is the list the emulator driver counts Down presses with: two lists of the same
screen that drift apart would take a measurement with them."""

TUPLE_ORDER = ("skin_colour", "hair_style", "hair_colour", "beard_style",
               "beard_colour")
"""The five fields of the corpus tuple, in the order the file names spell them.

`A-I3-A-F-A` is skin A, hair I3, hair colour A, beard F, beard colour A -- and
the same five, in the same order, are columns 3 to 7 of `defaultlook.txt`.
"""

TUPLE_SEPARATOR = "-"


# ---- the codec -----------------------------------------------------------

def decode(raw) -> dict:
    """The ten stored fields of one twelve-byte record."""
    if len(raw) != layout.PLAYER_RECORD_SIZE:
        raise BadLooks("a record is %d bytes and this is %d"
                       % (layout.PLAYER_RECORD_SIZE, len(raw)))
    return {field.name: field.get(raw) for field in FIELDS}


def encode(values: dict, raw=None) -> bytes:
    """*values* written back into *raw*, leaving every other bit alone.

    Deliberately not a mirror of `Player::Encode`, which rewrites the whole
    record including the skills: this cycle is a viewer, and a function that
    can only ever change what it was asked to change cannot quietly rewrite an
    attribute nobody mentioned.
    """
    out = bytearray(raw if raw is not None
                    else bytes(layout.PLAYER_RECORD_SIZE))
    if len(out) != layout.PLAYER_RECORD_SIZE:
        raise BadLooks("a record is %d bytes and this is %d"
                       % (layout.PLAYER_RECORD_SIZE, len(out)))
    for name, value in values.items():
        if name not in BY_NAME:
            raise BadLooks("%r is not one of the stored fields: %s"
                           % (name, ", ".join(sorted(BY_NAME))))
        BY_NAME[name].put(out, value)
    return bytes(out)


def labels(values: dict) -> dict:
    """The same record as the names a person reads on the screen."""
    return {name: BY_NAME[name].label(value)
            for name, value in values.items() if name in BY_NAME}


# ---- the corpus tuple ----------------------------------------------------

def parse_tuple(text: str) -> dict:
    """`A-I3-A-F-A` to the five fields it names."""
    parts = text.strip().split(TUPLE_SEPARATOR)
    if len(parts) != len(TUPLE_ORDER):
        raise BadLooks("%r has %d part(s) and a tuple has %d: %s"
                       % (text, len(parts), len(TUPLE_ORDER),
                          ", ".join(TUPLE_ORDER)))
    return {name: BY_NAME[name].index_of(part)
            for name, part in zip(TUPLE_ORDER, parts)}


def format_tuple(values: dict) -> str:
    """The inverse, for the five fields of `TUPLE_ORDER`."""
    return TUPLE_SEPARATOR.join(BY_NAME[name].label(values[name])
                                for name in TUPLE_ORDER)


CORPUS_SUFFIX = ".jpg"
"""What a render of the corpus is called.  The names are the measurement."""


def survey_tuples(names) -> dict:
    """Parse every name of *names* as a tuple, and say what came of it.

    The round trip is the half of the claim that is easy to skip: a parser can
    read `A-I3-A-F-A` correctly and a formatter can spell it back differently,
    and nothing downstream would notice until the corpus was compared against a
    render by name.  So it is counted, not assumed.
    """
    out = {"names": list(names), "parsed": [], "refused": [],
           "round_trip": 0,
           "coverage": {name: set() for name in TUPLE_ORDER}}
    for name in out["names"]:
        stem = name[:-len(CORPUS_SUFFIX)] if name.endswith(CORPUS_SUFFIX)             else name
        try:
            values = parse_tuple(stem)
        except BadLooks as exc:
            out["refused"].append((name, str(exc)))
            continue
        out["parsed"].append((name, values))
        if format_tuple(values) == stem:
            out["round_trip"] += 1
        for field, value in values.items():
            out["coverage"][field].add(value)
    return out


def say_survey(found: dict) -> None:
    """The survey as the task log spells it, printed by the tool this time."""
    for name, why in found["refused"]:
        print("   refused: %s -- %s" % (name, why))
    print("%d %s   parsed: %d   refused: %d   round-trip to its own name: %d"
          % (len(found["names"]), CORPUS_SUFFIX, len(found["parsed"]),
             len(found["refused"]), found["round_trip"]))
    for field in TUPLE_ORDER:
        print("   %-13s %2d of %2d value(s) covered"
              % (field, len(found["coverage"][field]),
                 BY_NAME[field].values))


def survey_problems(found: dict) -> list:
    """What makes a corpus survey worthless.  [] is good.

    The refusal is the one that matters and the one a reader would not think
    to ask for: with a permissive parser every name parses, the line reads
    `50 parsed, 0 refused`, and it looks BETTER than the true one.  A corpus
    whose names are all tuples cannot exercise that, so it is a problem here
    and not a silent pass.
    """
    problems = []
    if not found["names"]:
        problems.append("no %s in the folder: a survey of nothing passes "
                        "every count it prints" % CORPUS_SUFFIX)
    if not found["refused"]:
        problems.append("every name parsed as a tuple, so nothing here "
                        "exercised the refusal -- a parser that accepts any "
                        "number of parts would print exactly this")
    if found["round_trip"] != len(found["parsed"]):
        problems.append("%d of %d parsed name(s) format back to a different "
                        "name than the one they came from"
                        % (len(found["parsed"]) - found["round_trip"],
                           len(found["parsed"])))
    return problems


def corpus_names(folder: str) -> list:
    """The render file names of *folder*, sorted, without reading the images."""
    if not os.path.isdir(folder):
        raise BadLooks("%r is not a folder" % folder)
    return sorted(name for name in os.listdir(folder)
                  if name.lower().endswith(CORPUS_SUFFIX))


def default_looks(path: str = DEFAULT_LOOK) -> list:
    """The look table of `data/defaultlook.txt`, as (nation, values) pairs.

    Ninety-five nations with five columns each, and the columns are
    `TUPLE_ORDER`.  A field may be empty, which the editor reads as "leave this
    one alone"; those come back missing from the dict rather than as a made-up
    default.

    The file is cp1252 -- it carries one 0x92 curly apostrophe -- and nothing
    here decodes the two text columns, so it is read as Latin-1 and the bytes
    survive.
    """
    with open(path, encoding="latin-1") as handle:
        rows = [line.rstrip("\n") for line in handle if line.strip()]
    out = []
    for line in rows[1:]:
        cells = line.split(";")
        if len(cells) != 2 + len(TUPLE_ORDER):
            raise BadLooks("%r has %d column(s) and the table has %d"
                           % (line, len(cells), 2 + len(TUPLE_ORDER)))
        values = {}
        for name, cell in zip(TUPLE_ORDER, cells[2:]):
            if cell.strip():
                values[name] = BY_NAME[name].index_of(cell.strip())
        out.append((cells[1], values))
    return out


NATION_CODES = ((1, 54, -1), (55, 79, 40))
"""How a value of the `NAT` row maps to the byte the game stores, in runs.

`(first index, last index, what to add)`, and the two runs are the finding:
the row's values 1 to 54 store 0 to 53, and then the code **jumps 41** -- value
55 (`Iceland`) stores 95, and the row runs out at 119.  So codes 54 to 94, all
forty-one of them, name something the screen does not offer.

Measured on 2026-09-17 (LOOKS-TASK-23) by `oracle.py --default`, which walks
every value of the row and reads `layout.PLAYER_NATION` at each one -- and
re-walks it on every run, so this is a claim a command re-measures rather than
a number copied out of a session.  Value 0, `Unknown`, has no code: the two
copies of the byte do not even agree there until the first press.

Why it matters beyond bookkeeping: `Algeria` is value 65 and stores 105.  Any
pairing that treats the row's position as the game's number is wrong from
value 55 on, and wrong quietly.
"""

UNKNOWN_NATION = 0
"""The value of the row that names no nation, and stores no code."""


def nation_code(index: int) -> int:
    """The byte the game stores for value *index* of the `NAT` row."""
    for first, last, add in NATION_CODES:
        if first <= index <= last:
            return index + add
    raise BadLooks("value %d of NAT stores no nationality code; the row runs "
                   "%d..%d and %d is Unknown"
                   % (index, NATION_CODES[0][0], NATION_CODES[-1][1],
                      UNKNOWN_NATION))


def nation_index(code: int) -> int:
    """The inverse, for a code the row can reach."""
    for first, last, add in NATION_CODES:
        if first + add <= code <= last + add:
            return code - add
    raise BadLooks("no value of NAT stores %d; the row reaches %s"
                   % (code, ", ".join("%d..%d" % (first + add, last + add)
                                      for first, last, add in NATION_CODES)))


def nation_lines(nat_texts) -> dict:
    """The screen's `NAT` values against the lines of `data/defaultlook.txt`.

    **The two lists are not the same list, and that is the finding.**  The file
    is the EDITOR's table, keyed by TEAM: nations and clubs together
    (`Inter`, `Bayern`, `Clas. Brazil`, `Euro All Stars`).  The screen's row is
    the game's list of nationalities, which carries countries the file has not
    got (`Senegal`, `Uzbekistan`, `Trin y Tobago`) and spells the long ones
    short, because the cell is narrow: `Portuga`, `Netherl`, `Swi`, `Cze`.

    So the pairing is by NAME, never by index.  The first sixteen coincide in
    both order and position, which is exactly the trap: an index pairing looks
    right for a screenful and then applies another team's line -- a club's,
    further down.

    Returns `{"paired", "screen_only", "file_only", "truncated", "prefix_of"}`;
    every count a document quotes comes out of here.
    """
    file_rows = default_looks()
    by_name = {}
    for name, values in file_rows:
        by_name.setdefault(name, values)
    out = {"paired": {}, "screen_only": [], "file_only": [],
           "truncated": [], "prefix_of": {}}
    taken = set()
    for index, shown in enumerate(nat_texts):
        if shown in by_name:
            out["paired"][index] = (shown, by_name[shown])
            taken.add(shown)
            continue
        # A cell too narrow for the name: the game cuts it, so the file's name
        # starts with what the screen shows.  Only a UNIQUE completion counts;
        # two candidates would be a guess, and this module does not guess.
        starts = [name for name in by_name if name.startswith(shown)]
        if len(starts) == 1:
            out["paired"][index] = (starts[0], by_name[starts[0]])
            out["truncated"].append((shown, starts[0]))
            out["prefix_of"][shown] = starts[0]
            taken.add(starts[0])
        else:
            out["screen_only"].append((index, shown, len(starts)))
    out["file_only"] = [name for name, _v in file_rows if name not in taken]
    return out


def nation_by_index(nat_texts, skip: int = 0) -> dict:
    """The pairing this module refuses: value N of the row against line N of
    the file, optionally dropping the first *skip* values of the row.

    It exists so a check can show what it costs.  `skip=1` -- past `Unknown`,
    which no line of the file names -- is the version somebody would actually
    write, and it holds for a screenful before it starts naming other teams.
    """
    file_rows = default_looks()
    return {index + skip: file_rows[index][0]
            for index in range(min(len(nat_texts) - skip, len(file_rows)))}


# ---- the records on the disc ---------------------------------------------

def records(data: bytes, count: int | None = None) -> list:
    """The player records of `/SELECT.BIN`, as raw twelve-byte blobs."""
    count = layout.PLAYER_RECORD_COUNT if count is None else count
    first = layout.PLAYER_RECORD_OFFSET
    size = layout.PLAYER_RECORD_SIZE
    end = first + count * size
    if end > len(data):
        raise BadLooks("%d record(s) from %d need %d bytes and the file has %d"
                       % (count, first, end, len(data)))
    return [data[first + i * size:first + (i + 1) * size]
            for i in range(count)]


def out_of_table(values: dict) -> list:
    """Field names whose value is inside the bits and outside the labels."""
    return sorted(name for name, value in values.items()
                  if name in BY_NAME and BY_NAME[name].labels
                  and value - BY_NAME[name].bias >= len(BY_NAME[name].labels))


# ---- the cross-check against the in-house decoder ------------------------

_ASSIGN = re.compile(r"^\s*(\w+)\s*=\s*(.+?);\s*$", re.M)


def cpp_decoder(source: str) -> dict:
    """{field: python expression} lifted out of `Player::Decode`.

    Mechanical on purpose.  C and Python spell `>>`, `<<`, `&`, `+` and hex
    the same way, so the only edit is the name of the array -- which means what
    runs here is the other implementation's arithmetic and not a retyping of
    it.
    """
    start = source.find("void Player::Decode()")
    if start < 0:
        raise BadLooks("no Player::Decode() in this source")
    end = source.find("\nvoid ", start + 1)
    body = source[start:end if end > 0 else len(source)]
    out = {}
    for name, expr in _ASSIGN.findall(body):
        if "raw_attributes" not in expr:
            continue
        out[name] = expr.replace("raw_attributes[", "raw[")
    return out


_CONSTANT = re.compile(r"inline constexpr int (\w+)\s*=\s*(\d+)\s*;")


def core_player_count(path: str = PLAYER_TYPES_HPP) -> int:
    """How many records `Database::Load` reads from `OFS_PLAYER_ATTR`.

    `PLAYERS_TOTAL - PLAYERS_NC`, read out of the core's own header rather than
    copied from it, so the day somebody changes one the count here changes with
    it instead of silently disagreeing.  The loop that uses the two is
    `Database.cpp`'s `for(i=PLAYERS_NC;i<PLAYERS_TOTAL;i++)`.
    """
    with open(path, encoding="utf-8") as handle:
        found = dict(_CONSTANT.findall(handle.read()))
    missing = [n for n in ("PLAYERS_TOTAL", "PLAYERS_NC") if n not in found]
    if missing:
        raise BadLooks("%s does not declare %s" % (path, ", ".join(missing)))
    return int(found["PLAYERS_TOTAL"]) - int(found["PLAYERS_NC"])


def disagreements(source: str, blobs) -> list:
    """Every field where this module and the C++ differ on some blob."""
    expressions = cpp_decoder(source)
    problems = []
    for field in FIELDS:
        if field.name not in expressions:
            problems.append("%s: Player::Decode has no line for it"
                            % field.name)
            continue
        expr = expressions[field.name]
        for raw in blobs:
            theirs = eval(expr, {"__builtins__": {}}, {"raw": raw})  # noqa: S307
            mine = field.get(raw)
            if theirs != mine:
                problems.append(
                    "%s: %s gives %d and this module gives %d on %s"
                    % (field.name, expr, theirs, mine, raw.hex()))
                break
    return problems


def _blobs(count: int = 64):
    """Deterministic pseudo-random records -- the same set every run.

    A seeded generator rather than a fixed list, because a fixed list is a list
    somebody chose, and the bits it happens not to exercise are the bits a
    wrong mask hides in.
    """
    import random

    rng = random.Random(20260915)  # not-an-address: the date, as a seed
    return [bytes(rng.randrange(256) for _ in range(layout.PLAYER_RECORD_SIZE))
            for _ in range(count)]


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("looks.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(BadLooks)

    ok("the screen has twelve rows", len(SCREEN) == 12, "%d" % len(SCREEN))
    ok("ten of them are stored and two are not",
       len(FIELDS) + len(UNSTORED) == len(SCREEN))
    ok("every stored field names a row of the screen",
       all(field.row in SCREEN for field in FIELDS))
    ok("and the two unstored rows are the two the screen opens with",
       tuple(SCREEN[:2]) == ("DEFAUL", "NAT") and set(UNSTORED) == set(SCREEN[:2]))

    import oracle

    ok("this list of rows is the one the emulator driver counts with",
       SCREEN == oracle.ROWS, "%r vs %r" % (SCREEN, oracle.ROWS))

    # The domains, as bits and as names.  The gap between the two is the point.
    ok("the four skins fill their two bits",
       BY_NAME["skin_colour"].values == 4 == len(BY_NAME["skin_colour"].labels))
    ok("the thirty-two hair styles fill their five bits",
       BY_NAME["hair_style"].values == 32 == len(HAIR_STYLES))
    ok("hair colour names all eight of its values",
       len(BY_NAME["hair_colour"].labels) == BY_NAME["hair_colour"].values == 8)
    short = sorted(f.name for f in FIELDS
                   if f.labels and len(f.labels) < f.values)
    ok("three fields hold more values than anyone has named",
       short == ["beard_colour", "beard_style", "foot"], "%r" % (short,))
    ok("and the unnamed ones come back as a marker, not as a refusal",
       BY_NAME["beard_colour"].label(7) == UNNAMED)
    refuses("a value past the bits is refused, though",
            lambda: BY_NAME["beard_colour"].label(8), "outside 0..7")
    ok("height starts at 148 and age at 15",
       BY_NAME["height"].bias == 148 and BY_NAME["age"].bias == 15)
    ok("height spans the 64 its two pieces allow",
       BY_NAME["height"].values == 64)

    # The codec, against the other implementation.
    source = attempt("read src/core/Player.cpp",
                     lambda: open(PLAYER_CPP, encoding="utf-8").read())
    if source is not None:
        blobs = _blobs()
        found = attempt("run both decoders over 64 blobs",
                        lambda: disagreements(source, blobs), default=["raised"])
        ok("every field decodes exactly as Player::Decode does", found == [],
           "; ".join(found[:3]))
        # The red case for the cross-check itself: a comparison that cannot
        # disagree would pass the line above while proving nothing.
        bent = source.replace("hair_colour = (raw_attributes[1]>>1)&0x07;",
                              "hair_colour = (raw_attributes[1]>>2)&0x07;")
        ok("and a bent expression is caught",
           bent != source and [p for p in disagreements(bent, blobs)
                               if p.startswith("hair_colour")])

    # The count, against the core that reads the same block.  Here rather than
    # in --check-image because the header is always in the room and the disc
    # is not, and because a count nothing checks is a count that drifts: this
    # one arrived from a third party 207 short.
    count = attempt("read PLAYERS_TOTAL and PLAYERS_NC", core_player_count)
    ok("the record count is the one Database::Load reads",
       count == layout.PLAYER_RECORD_COUNT,
       "the core says %r and layout.py says %d"
       % (count, layout.PLAYER_RECORD_COUNT))
    ok("and the block fits inside /SELECT.BIN",
       layout.PLAYER_RECORD_OFFSET
       + layout.PLAYER_RECORD_COUNT * layout.PLAYER_RECORD_SIZE
       <= layout.SIZE[layout.SELECT])

    # Round trip, over the whole domain of every field rather than a sample.
    trouble = []
    for field in FIELDS:
        for value in range(field.bias, field.bias + field.values):
            raw = encode({field.name: value})
            if decode(raw)[field.name] != value:
                trouble.append("%s=%d" % (field.name, value))
    ok("every value of every field survives encode and decode",
       trouble == [], "%r" % (trouble[:5],))

    # Fields must not share bits: one field written must leave the others.
    overlap = []
    for i, one in enumerate(FIELDS):
        for two in FIELDS[i + 1:]:
            for a in one.pieces:
                for b in two.pieces:
                    if a.byte == b.byte and a.byte_mask() & b.byte_mask():
                        overlap.append("%s and %s share bits of byte %d"
                                       % (one.name, two.name, a.byte))
    ok("no two fields share a bit", overlap == [], "; ".join(overlap[:3]))

    # The tuple, both ways.
    text = "A-I3-A-F-A"
    parsed = attempt("parse a corpus tuple", lambda: parse_tuple(text))
    ok("a tuple parses to the five fields it names",
       parsed == {"skin_colour": 0, "hair_style": 22, "hair_colour": 0,
                  "beard_style": 5, "beard_colour": 0}, "%r" % (parsed,))
    ok("and formats back to itself", format_tuple(parsed) == text)
    refuses("a tuple with four parts is refused",
            lambda: parse_tuple("A-I3-A-F"), "part(s) and a tuple has 5")
    refuses("a label the field does not have is refused",
            lambda: parse_tuple("A-Z9-A-F-A"), "is not a hair_style")

    # The corpus rule, on synthetic names: the Superpack is the user's folder
    # and is not in this tree, but nothing about the rule needs it.
    made = attempt("survey five synthetic render names",
                   lambda: survey_tuples(["A-A1-A-A-A.jpg", "A-I3-A-F-A.jpg",
                                          "B-B2-C-D-A.jpg", "D-P1-H-G-B.jpg",
                                          "0.jpg"]))
    if made is not None:
        ok("four names parse and the fifth is refused",
           (len(made["parsed"]), len(made["refused"])) == (4, 1),
           "%d parsed, %d refused"
           % (len(made["parsed"]), len(made["refused"])))
        ok("and every one that parsed formats back to its own name",
           made["round_trip"] == len(made["parsed"]),
           "%d of %d" % (made["round_trip"], len(made["parsed"])))
        ok("the refusal says what is wrong with the name",
           "part(s) and a tuple has 5" in made["refused"][0][1],
           made["refused"][0][1])
        ok("coverage is counted per field",
           len(made["coverage"]["skin_colour"]) == 3
           and len(made["coverage"]["hair_style"]) == 4,
           "%r" % ({k: sorted(v) for k, v in made["coverage"].items()},))
        ok("a survey with nothing wrong in it has nothing to report",
           survey_problems(made) == [], "%r" % (survey_problems(made),))
        # The red case of the survey itself.  A corpus in which every name
        # parses is indistinguishable from a parser that accepts anything,
        # and the line it prints reads BETTER than the true one.
        ok("a survey where nothing was refused is a problem, not a better run",
           [p for p in survey_problems(survey_tuples(["A-A1-A-A-A.jpg"]))
            if "refus" in p])
        ok("and so is an empty folder",
           [p for p in survey_problems(survey_tuples([])) if "no .jpg" in p])

    # The 95 nations are a fixture this repository already ships, so this runs
    # with no disc and no Superpack in the room.
    table = attempt("read data/defaultlook.txt", lambda: default_looks())
    if table is not None:
        ok("the default-look table has 95 nations", len(table) == 95,
           "%d" % len(table))
        outside = [(nation, out_of_table(values)) for nation, values in table
                   if out_of_table(values)]
        ok("and every value in it is one the labels name", outside == [],
           "%r" % (outside[:3],))
        ok("its five look columns are the five of the corpus tuple",
           all(set(values) <= set(TUPLE_ORDER) for _n, values in table))
        _nation_checks(c)


# ---- the disc ------------------------------------------------------------

def _nation_checks(c) -> None:
    """`NAT` against the file, and what pairing them by index costs.

    Skipped where `screen.json` is not there: the row's values are a
    measurement of the game (LOOKS-TASK-21), and this module does not carry a
    copy of them.
    """
    import screen

    if not os.path.exists(screen.TABLE):
        c.skip("NAT against defaultlook.txt", "screen.json is not measured yet")
        return
    ok = c.ok
    nat = screen.load()["rows"]["NAT"]["texts"]
    found = nation_lines(nat)
    paired, only_screen = found["paired"], found["screen_only"]
    ok("the row and the file are not the same list",
       len(paired) < len(nat) and found["file_only"],
       "%d paired of %d, %d file line(s) unused"
       % (len(paired), len(nat), len(found["file_only"])))
    ok("the truncated names complete to one file name each and no more",
       all(short != full and full.startswith(short)
           for short, full in found["truncated"]), "%r" % found["truncated"])
    ok("a name two file lines could complete is left unpaired, not guessed",
       all(count != 1 for _i, _shown, count in only_screen))
    ok("Unknown pairs with nothing",
       any(shown == "Unknown" for _i, shown, _n in only_screen))

    # The red case, and it is the one somebody would actually write: drop
    # `Unknown` and pair by position.  It holds for sixteen values and then
    # starts handing nations the lines of CLUBS.
    by_index = nation_by_index(nat, 1)
    run = 1
    while (run < len(nat) and paired.get(run)
           and by_index.get(run) == paired[run][0]):
        run += 1
    ok("pairing by index holds for a screenful and then stops",
       run - 1 == 16 and by_index.get(run) != nat[run],
       "ends at index %d (%r), where the file line is %r"
       % (run - 1, nat[run - 1], by_index.get(run)))
    wrong = sum(1 for index in paired
                if by_index.get(index) not in (None, paired[index][0]))
    invented = sum(1 for index in by_index
                   if index not in paired)
    ok("and pairing by index gives a line to values that have none",
       wrong and invented, "%d wrong team(s), %d invented" % (wrong, invented))

    # The codes, which are the other half of the same lesson: the row's
    # position is not the game's number either.
    ok("the code runs with the index and then jumps",
       nation_code(1) == 0 and nation_code(54) == 53
       and nation_code(55) == 95 and nation_code(len(nat) - 1) == 119,
       "%d, %d, %d, %d" % (nation_code(1), nation_code(54), nation_code(55),
                           nation_code(len(nat) - 1)))
    ok("every value but Unknown has a code, and it round-trips",
       all(nation_index(nation_code(i)) == i for i in range(1, len(nat))))
    c.refuses("Unknown has no code, and is refused rather than given one",
              lambda: nation_code(UNKNOWN_NATION), "stores no nationality",
              BadLooks)
    c.refuses("and a code in the gap belongs to no value of the row",
              lambda: nation_index(54), "no value of NAT stores", BadLooks)
    ok("the gap is forty-one codes the screen cannot reach",
       nation_code(55) - nation_code(54) - 1 == 41)


def _check_image(image_path: str) -> int:
    """The record block: where it starts, how long it runs, what it holds."""
    import iso_source

    with iso_source.open_disc(image_path) as disc:
        data = disc.read(layout.SELECT)

    problems = []
    blobs = records(data)
    print("/SELECT.BIN: %d B, %d record(s) of %d from %d"
          % (len(data), len(blobs), layout.PLAYER_RECORD_SIZE,
             layout.PLAYER_RECORD_OFFSET))

    # Where the block ENDS is the measurement, and it is made without being
    # told the count: a real record decodes to a plausible height, and the
    # first one that does not is where the block stopped.
    size = layout.PLAYER_RECORD_SIZE
    first = layout.PLAYER_RECORD_OFFSET
    room = (len(data) - first) // size
    height = BY_NAME["height"]
    run = 0
    for index in range(room):
        raw = data[first + index * size:first + (index + 1) * size]
        if not PLAUSIBLE_HEIGHT[0] <= height.get(raw) <= PLAUSIBLE_HEIGHT[1]:
            break
        run += 1
    print("    the run of plausible heights stops after %d record(s); the "
          "file has room for %d" % (run, room))
    if run != layout.PLAYER_RECORD_COUNT:
        problems.append("the run stops after %d record(s) and layout.py says "
                        "%d" % (run, layout.PLAYER_RECORD_COUNT))

    decoded = [decode(raw) for raw in blobs]
    print("    every field of every record, as the labels name them")
    for field in FIELDS:
        seen = {}
        for one in decoded:
            seen[one[field.name]] = seen.get(one[field.name], 0) + 1
        lowest, highest = min(seen), max(seen)
        unnamed = sorted(v for v in seen
                         if field.labels
                         and v - field.bias >= len(field.labels))
        print("        %-13s %2d of %2d value(s) used, %d..%d%s"
              % (field.name, len(seen), field.values, lowest, highest,
                 "" if not unnamed
                 else "   USED AND UNNAMED: %s" % unnamed))
        if highest >= field.bias + field.values:
            problems.append("%s reaches %d, past the %d its bits hold"
                            % (field.name, highest, field.values))

    print("looks --check-image: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line)
    return 1 if problems else 0


PLAUSIBLE_HEIGHT = (150, 205)
"""The window a real footballer's height falls in, used to find where the
record block ends without being told where it ends.

Not a domain: the field holds 148 to 211.  This is the range that separates
1,449 records of people from the zeros after them -- measured, every one of the
first 1,449 lands in 155..202 and record 1,449 is all zero.
"""


def _check_corpus(folder: str) -> int:
    """The fifty renders, by name.  The half of the cross-check that was prose.

    LOOKS-TASK-13 claimed both witnesses of the tuple and only one of them was
    a command: the 95 nations of `data/defaultlook.txt` are asserted by
    `--check`, and the fifty file names were parsed by a throwaway script
    (CORR-LOOKS-027).  This is that script, with a red case and an exit code.
    """
    names = corpus_names(folder)
    print("the corpus of renders: %s" % folder)
    found = survey_tuples(names)
    say_survey(found)
    problems = survey_problems(found)
    print("looks --corpus: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line)
    return 1 if problems else 0


def corpus_from_env(argument: str | None = None) -> str:
    """The corpus folder, from the argument or the environment."""
    folder = argument or os.environ.get(layout.ENV_CORPUS)
    if not folder:
        raise RuntimeError("no corpus folder: pass one, or point %s at the "
                           "folder of renders named by tuple.  It is the "
                           "third party's and is not in this tree"
                           % layout.ENV_CORPUS)
    return folder


def _report(text: str | None = None) -> int:
    print("the twelve rows of LOOKS SET")
    for row in SCREEN:
        if row in UNSTORED:
            print("    %-9s not stored -- %s" % (row, UNSTORED[row]))
            continue
        field = BY_ROW[row]
        names = (", ".join(field.labels) if field.labels
                 else "%d..%d" % (field.bias, field.bias + field.values - 1))
        gap = ("" if not field.labels or len(field.labels) == field.values
               else "  (%d value(s) unnamed)"
                    % (field.values - len(field.labels)))
        print("    %-9s %-13s %2d value(s)%s" % (row, field.name,
                                                 field.values, gap))
        print("        %s" % names)
    if text:
        values = parse_tuple(text)
        print()
        print("%s is %s" % (text, ", ".join(
            "%s %s" % (name, BY_NAME[name].label(values[name]))
            for name in TUPLE_ORDER)))
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return self_check()
    if len(argv) >= 2 and argv[1] == "--report":
        return _report(argv[2] if len(argv) > 2 else None)
    if len(argv) >= 2 and argv[1] == "--corpus":
        try:
            folder = corpus_from_env(argv[2] if len(argv) > 2 else None)
        except RuntimeError as exc:
            print("looks: skipped -- %s" % exc)
            return SKIP
        return _check_corpus(folder)
    if len(argv) == 2 and argv[1] == "--check-image":
        import iso_source

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("looks: skipped -- %s" % exc)
            return SKIP
        return _check_image(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

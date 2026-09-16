#!/usr/bin/env python3
"""Where things are, and which disc may be read for what.

This is the module the drawing rules of the plan (section 3.3, rule 1) single
out: every address of the `looks` project lives here, and nowhere else.  It
knows no file format and imports no Qt.  Callers hand it bytes or digests and
it answers questions about them, which is what lets its self_check() run on a
machine with no disc image at all.

It does no I/O at all.  It held one exception for as long as the two-disc
guard had no caller -- `--check-discs` opened both real discs itself -- and
LOOKS-TASK-03 cleared that debt on 2026-09-14: the live demonstration now lives
in `iso_source.py --check-discs`, where reading a disc is the module's job.

What is an address, and what is a format?  The line this file draws: the KSEG0
pointer table at the head of a model file is ADDRESS material, so deriving the
load base from it belongs here.  The vertices and primitives those pointers aim
at are FORMAT, and they belong to section.py.  derive_base() reads the pointer
table and stops there; it never looks at a section.

THE RULE THIS FILE EXISTS FOR
-----------------------------
There are two discs and they are not interchangeable:

* the Japanese original is the truth about BYTES.  Textures and palettes are
  read from it and from nothing else;
* the English translation patch is the disc you DRIVE, because its menus are
  legible -- and its geometry is byte-for-byte the same, so driving it is free.

Reading a palette off the English disc is a silent error.  The offset is valid
there, the graphic appears, and it is the wrong graphic: `/BIN/DAT2D.BIN`
differs between the two, and it is exactly the file that holds hair, faces,
bodies, boots and the skin palettes.  Nothing raises, nothing warns.  That is
why the rule is a digest check in code and not a sentence in a document.

Usage:
    python tools/looks/layout.py --check
    python tools/looks/layout.py --sweep
"""

from __future__ import annotations

import hashlib
import io
import os
import re
import sys
import tokenize
import tempfile

# --- The two discs, and how a recipe names each one -----------------------
#
# Two variables because they are two different files, and the second is a
# .cue rather than a .bin: the emulator wants the sheet, the readers want the
# data track.  The PES2 tooling learned this the expensive way -- one family
# of variables for disc tools and another for emulator tools -- and the
# recipe that carried only the first left the one gate that boots the game
# reporting `skipped` in 0.01 s while the run printed `100% tests passed`.
ENV_IMAGE = "WE2002_LOOKS_IMAGE"
"""The Japanese data track (.bin).  The truth about bytes."""

ENV_DRIVE_IMAGE = "WE2002_LOOKS_DRIVE_IMAGE"
"""The English .cue.  The disc to drive the emulator with."""

ENV_CORPUS = "WE2002_LOOKS_CORPUS"
"""The folder of the fifty renders, whose names are corpus tuples.

Third party's, and not in the git tree (plan section 2), so it is named the
way every other external fixture of this repository is: by variable, and the
gate that reads it skips with 77 when it is not set.
"""

# --- Paths inside the disc ------------------------------------------------
EDT_MOD = "/BIN/EDT_MOD.BIN"
MODEL = "/BIN/MODEL.BIN"
DAT2D = "/BIN/DAT2D.BIN"
SELECT = "/SELECT.BIN"

# --- Identity of what may be read, measured 2026-09-14 --------------------
#
# sha256 of the FILE as read out of the disc, not of the disc.  Keying on the
# file is what makes the check say something: two dumps of the same release
# can differ in their tail and still hold identical assets, and a translation
# patch can leave the disc the same size while replacing exactly this file.
DIGEST = {
    # Identical on both discs -- this is why the English disc may be driven.
    EDT_MOD: "6ff56894e7ce94aa655047200143087afe85d70cda777e5aee30dedf9d427dd3",
    MODEL: "0b3814bb0d3b47f4ac3b13a1eb9f64ce9c50f8f08331790716827c618c0578cb",
    # Japanese only.  The English disc has
    # 4a4d6a4fe301b1169535c6e5acf7e31c584d725be1571e689ed6fb5696beef60 here,
    # and reading a palette out of that one is the silent error above.
    DAT2D: "0e914e584c889635f0c3a7a64d87ed5c773541c76b35455b6475c19c9f50de7b",
    SELECT: "86d14a66a3cd72b9363832260d4f3842e15d530c2f76eb0d6a3f6823cd603ce1",
}

TEXTURE_FILES = frozenset({DAT2D})
"""Files that may only ever be read from the Japanese disc."""

GEOMETRY_FILES = frozenset({EDT_MOD, MODEL})
"""Files proven identical on both discs, so either may supply them."""

RECORD_FILES = frozenset({SELECT})
"""Japanese-only too, but records rather than art -- so a hint of its own.

/SELECT.BIN is the second of the two files that differ between the discs, and
it holds the player records.  Folding it into TEXTURE_FILES would refuse it
with a sentence about palettes, which is the wrong thing to go looking at.
"""

# The whole-image digest of the Japanese dump, so a recipe can confirm it is
# pointed at the right dump before reading anything.  Both copies on this
# machine -- roms/japanese-shift-jis.bin and the we-2002-original-japao.bin
# under C:\games\ps1\roms\we2002\ -- are this same dump, 307,187,664 bytes,
# measured 2026-09-14.  The English one is 306,834,864 bytes.
IMAGE_DIGEST_JAPANESE = (
    "e853eb14f5bddd50a4a5e77a1da4d22c989a0d99ad5a4927e24e1dba7475abf3"
)
IMAGE_SIZE_JAPANESE = 307187664
IMAGE_SIZE_ENGLISH = 306834864


# --- Where each file sits on the disc -------------------------------------
#
# Measured 2026-09-14 from the directory of roms/japanese-shift-jis.bin, and
# identical on the English disc -- the translation patch replaces content
# in place and moves nothing.  Nothing here READS by LBA (iso.py resolves the
# path through the filesystem, which is what makes the tooling survive a
# different dump); these are recorded because the plan cites them and because
# a changed LBA is the first sign of a rebuilt image.
LBA = {
    EDT_MOD: 5000,
    MODEL: 8100,
    DAT2D: 5300,
    SELECT: 850,
}

SIZE = {
    EDT_MOD: 36072,
    MODEL: 64800,
    DAT2D: 81124,
    SELECT: 300648,
}

# --- Where each model file loads in RAM -----------------------------------
#
# KSEG0 addresses.  Both files are raw -- not LZSS, unlike DAT2D.BIN -- and
# the game copies them to these addresses untouched, which is why a pointer
# inside the file is an absolute RAM address and not a file offset.
#
# These are the constants derive_base() is checked AGAINST, never the source
# of the answer: see require_base().
BASE = {
    EDT_MOD: 0x8011C000,
    MODEL: 0x8016E800,
}

MODEL_GEOMETRY_START = 1816
"""Offset of the first MODEL.BIN section: 107 vertices, 88 primitives.

The number the `we3d` analysis reports for section 0, re-measured here.

EDT_MOD.BIN has no constant beside this one on purpose: its first section is
DERIVED, by geometry_start(), because deriving it is what would have caught
the scan that began at 15,704 and reported the file as read (CORR-LOOKS-010).
"""

# --- The BIN container's record model -------------------------------------
#
# A record list closes with the pair [bank word][RECORD_LIST_END], and every
# record of it carries that same bank word in field 7.  `tools/pes2/bin_archive.py`
# documents that word as "0x800f, a constant tag"; LOOKS-TASK-10 measured that
# it is the 64 KiB page of the 16-bit offset in field 6, biased so bank 0 reads
# 0x800f.  The four discs that project measured never needed the bank, because
# no payload of theirs sits past the first 64 KiB.  This one does: DAT2D.BIN's
# palettes are at bank 1 and DATSEL.BIN's images at bank 3.
RECORD_TAG_BASE = 0x800F  # not-an-address: field 7 when the payload is in bank 0
RECORD_BANK = 0x10000  # not-an-address: the 64 KiB page that field 7 counts
RECORD_LIST_END = 0x00FF  # not-an-address: the halfword that closes a list

VRAM_WIDTH = 1024  # not-an-address: PSX frame-buffer width in 16-bit units
VRAM_HEIGHT = 512  # not-an-address: PSX frame-buffer height in rows
CLUT_ROW_FIRST = 480
"""The first VRAM row a palette may live on.

The strip at the bottom of the frame buffer that PSX games keep CLUTs in, and
the rule `bin_archive.py` already states.  On this disc the four skin palettes
are rows 480 to 483, the boots row 484, and 256 narrow palettes fill 496..511.
"""

TEXTURE_EXPECTED = {
    # (image records, clut records, palettes of 16 entries, palettes of 256)
    DAT2D: (23, 267, 262, 5),
}

TEXTURE_BANK = {
    # (first byte of the palette payloads, first byte of the record list that
    # indexes them).  The payloads tile exactly between the two: 262 x 32 B
    # plus 5 x 512 B is 10,944 B, and 65,892 + 10,944 is 76,836.
    DAT2D: (65892, 76836),
}

HEAD_SECTION = 24
"""The MODEL.BIN section that is the head.

Named by LOOKS-TASK-09 -- it is the piece HAIR, FACE and SKIN share, and the
only one of the twelve that does not live in EDT_MOD.BIN.  `pieces.py` carries
the same number for the same reason; it is here as well because `atlas.py`
addresses the section by index and rule 1 owns indices into a named file.
"""

HAIR_PRIMITIVES = (1, 14)
"""The two primitives of HEAD_SECTION whose `v` the HAIR field walks.

Measured in RAM by LOOKS-TASK-08 with the game running: a step of HAIR adds
0x20 to the `v` of all four corners of these two and of nothing else.  They are
the whole evidence of section 1.8 -- their `u` is 176..199, past the halfway
mark of a 4-bit page, so what they sample is the SECOND image record of that
page and not the first.
"""

FACE_PRIMITIVES = (8, 13)
"""The two primitives of HEAD_SECTION whose `v` the FACE field walks.

Measured in RAM by LOOKS-TASK-11, both save states, a step of 0x10.  They were
nearly recorded as one primitive: `report_field` printed four hits, which is
exactly one textured quad, and the second of the pair was below the cut.
Their `u` is 152..174 -- past the halfway mark, like the hair's -- so FACE
samples the SAME image record the hair does.
"""

HAIR_IMAGE = 3568
"""The DAT2D.BIN image record hair, facial hair and face detail come from.

VRAM (544, 256), the second half of texture page 0x18.  The CARP table calls
this one "Caras" and calls 8 "Pelos"; the zeta tutorial sends the reader here
for hair.  LOOKS-TASK-11 measured that the tutorial is right -- both the two
primitives HAIR moves and the two FACE moves sample this record, and neither
field touches the one at 8.
"""

FLAG_IMAGE = 10248
"""The one other DAT2D.BIN image the geometry samples, at VRAM (672, 384).

136 primitives reach it, all of them from MODEL.BIN sections 0 and 1 -- none of
the twelve pieces LOOKS-TASK-09 named.  The CARP table calls it "Banderin
pelotas"; nothing here confirms that, and the measured claim is only that the
player is not what samples it.
"""

DAT2D_SCENE_LABELS = {
    # `Offsets WE2002 - CARP/Dat/DAT2D.BIN.txt`, transcribed 2026-09-15 so that
    # what the scene says and what the disc says can be compared row by row.
    # Opinion, not measurement: its other seventeen rows are blank or a
    # signature, and its line 20 misconverts its own hex D59C to 23,964
    # instead of 54,684.
    8: "Pelos Cuerpos y botines",
    3568: "Caras",
    7456: "Cuerpo",
    9296: "Redes del arco",
    10248: "Banderin pelotas",
    22200: "Banderitas del menu",
}

SKIN_IMAGE = 8
"""The DAT2D.BIN image record at VRAM (512, 256): bodies, boots and bare skin.

The first half of the same page, and by far the most sampled thing in the
container.  CARP's label for it, "Pelos Cuerpos y botines", is right about the
bodies and the boots and wrong about the hair.
"""

SKIN_PALETTES = (65892, 66404, 66916, 67428)
"""The four 256-entry palettes at VRAM (0, 480) to (0, 483), one per skin.

LOOKS-TASK-10 found them by tiling the palette bank; LOOKS-TASK-08 found which
one a figure uses by moving SKIN on the screen and watching the CLUT id walk
0x40 at a time, which is exactly one VRAM row.  The CARP table calls them
"Pieles A" to "Pieles D" and gets the fourth wrong -- it prints 67,248 where the
record says 67,428, two digits swapped in its own arithmetic.

They are a tuple and not four names because the index IS the field's value:
`skin_colour` is two bits in `src/core/Player.cpp`, and row = 480 + that.
"""

HAIR_MATRIX_FIRST = 65924
"""Where the eight hair colours of the first skin start: SKIN_PALETTES[0] + 32.

The offsets of the zeta tutorial's table, read out of the PDF in 2026-09-15
rather than summarised: `Tipo A` of `Raza Blanca` is 65,924, and the table walks
32 bytes per type and 512 per race.  **Thirty-two bytes past the skin palette's
own start**, which is the thing that makes it the FIRST hair colour and not the
zeroth -- LOOKS-TASK-12's own criterion wrote the matrix as
`65892 + race*512 + kind*32`, off by one column, and the disc says otherwise:
column 0 of each record is the bare-skin window, which no hair colour uses.
"""

HAIR_MATRIX_RACE_STEP = 512
"""512 B is 256 entries is one whole palette record, so one VRAM row."""

HAIR_MATRIX_KIND_STEP = 32
"""32 B is 16 entries is one 4-bit CLUT, so one step of x in the CLUT id."""

HAIR_MATRIX_KINDS = 8
"""Eight hair colours, `Tipo A` to `Tipo H` in the tutorial's own table.

The same eight `src/core/Player.cpp` packs into the three bits of
`hair_colour`, and the same eight for `beard_colour` beside it.  Two witnesses
that never met, agreeing on a count.
"""

BARE_SKIN_COLUMN = 0
"""Column 0 of a skin record: the window with no hair colour in it.

446 primitives name it -- the bare arms, legs and faces -- and it is the only
column whose sixteen entries look nothing like the other fifteen.
"""

HAIR_COLUMN = 1
"""The column `hair_colour` 0 selects.

Measured on the screen: the head's primitives carry column 1 on the disc, and
one step of H.COL takes byte 2 of the CLUT id from 1 to 2 on both save states.
The zeta table starts at the same place from the other side -- its `Tipo A` is
32 bytes past the record.
"""

BEARD_COLUMN = 9
"""The column `beard_colour` 0 selects.

Measured the same way: the two FACE primitives carry column 9 on the disc, and
one step of H.F.COL. takes them from 9 to 10, on both slots.

`src/core/Player.cpp` gives `beard_colour` three bits, and eight columns from 9
would need a column 16, which a 256-entry record does not have.  The screen
settles it: walked end to end by `oracle.py --palettes`, H.F.COL. reaches
**seven** values, columns 9 to 15, and the grid comes out exactly full.
"""

BOOT_SECTIONS = (9, 10)
"""The two EDT_MOD.BIN sections the BOOTS field rewrites, in both slots.

The only two sections the two figures share byte for byte, which is how
LOOKS-TASK-09 named them the feet before BOOTS was asked; `pieces.py` carries
the same pair as BOOTS_SECTIONS, per slot, and this is the file-level name
`oracle.py --assembly` addresses one of them by.
"""

HEAD_RUNS = ((24, 56), (74, 106))
"""The two runs of MODEL.BIN sections that are heads, as half-open ranges.

**Thirty-two sections each, byte for byte distinct** -- and that is a count of
SECTIONS, not of bodies.  Measured 2026-09-16, remeasured by CORR-LOOKS-029:
the first run holds **twelve** distinct vertex arrays and the second 24, and
fifteen of the first run's sixteen pairs share theirs byte for byte.  Thirty-two
is exactly what `hair_style` holds and two runs is exactly the two figures
EDT_MOD.BIN's two lists already showed, which is what makes the coincidence
worth refusing rather than reading.

All 32 of the first run sample HAIR_IMAGE and 16 of the second do, but **not
each with its own window**: the 32 take **fourteen** distinct windows on that
sheet, several shared -- 25, 26 and 27 take one between them -- and sections
32, 33, 36 and 37 take none at all.  `assembly.hair_windows` measures it and
`assembly.HEAD_RUN_WINDOWS` asserts it.

**The anchoring is measured, and it is not `24 + N`.**  On 2026-09-16
`oracle.py --patched HAIR` read the whole loaded file after every press and
found the row rewriting the **even** sections of the first run, one per LETTER
of the style's label: A is 24, B is 26, C 30, D 48, F 52, G 28, I 34, J 36,
K 32, L 46, O 44, P 50 -- and E in TWO, E1 in 48 which is D's and E2 in 54
which is its own, so thirteen sections for twelve whole letters and one split.
The digit picks a sixteen-row band of HAIR_IMAGE inside that section.  The table is `assembly.HAIR_MAP`, which also carries the
three values that rewrote nothing and the three even sections nobody named.

**And the goalkeeper's hair is the FIRST run too.**  Walked on slot 1
(CORR-LOOKS-047), the row rewrites the same even sections with the same bands,
and not one section of 74..105 moved at any press.  So "two runs, two figures"
is still the coincidence it was: what the second run is, nothing has measured.

The first run is therefore **sixteen pairs** rather than 32 independent heads:
`assembly.head_pairs` measures what separates a pair, and it is the beard.
"""

HAIR_QUADS = {
    24: (1, 14),
    26: (1, 3),
    34: (0, 1, 12),
    46: (0, 9, 17),
}
"""Which primitives of a head take the hair band, per MODEL.BIN section.

Measured 2026-09-16 by `oracle.py --writes`, which puts an EXECUTE breakpoint
on HAIR_QUAD_STORE and reads `a0` -- the primitive the game is writing -- at
every hit while the row is walked.  Four of the thirteen sections the row
visits came out this way; the other nine are written somewhere else, because
walking every value of the row never stopped that instruction with their
addresses in `a0`.

**So this is a measured four, not a rule for thirteen.**  The obvious rule --
"the primitives that sample the hair sheet in the hair colour's column" -- is
measured WRONG: section 30 has twelve of those and the game rewrites two.
"""

HAIR_QUAD_ROWS = (15, 1, 15, 1)
"""The row inside a band that the game writes into each corner's `v`.

Read off the store below: `v1 = band * 16 + 15` goes to bytes 0x1 and 0x9 of
the primitive -- corners 0 and 2 -- and `v0 = band * 16 + 1` to 0x5 and 0xd,
corners 1 and 3.  **An absolute value, not a displacement.**  The disc does not
hold these rows: section 24 keeps 14/1, 26 keeps 14 and 0 or 1, 34 keeps 15/2,
46 keeps 79/66.  Adding the band to the disc's `v` drew every hair quad a row
off -- measured in the game's own display list, where section 24's two quads
carry `v` 15 and the file 14 (CORR-LOOKS-042).
"""

HAIR_QUAD_STORE = 0x80011590
"""The instruction in the GAME that writes a hair quad's `v`.

Found on 2026-09-16 by a write watchpoint on section 24's own quad
(LOOKS-TASK-14), which stopped one instruction past it:

    0x80011580  andi  v0, a2, 0x00ff      the band, as the caller passed it
    0x80011584  sll   v0, v0, 4           ATLAS_BAND rows a band
    0x80011588  addiu v1, v0, 15
    0x8001158C  addiu v0, v0, 1
    0x80011590  sb v1, 0x1(a0)            <- this one
    0x80011594  sb v0, 0x5(a0)
    0x80011598  sb v1, 0x9(a0)
    0x8001159C  sb v0, 0xd(a0)

An **execute** breakpoint here is what turns "which bytes changed" into "which
primitive of which section, and with what band" -- `a0` is the primitive and
`a2` is the band -- and it sees a write even when the value written is the one
already there, which a memory diff cannot.

It is an address in the game's own code, not in a file this project reads, and
it is here for the same reason every other address is.
"""

ATLAS_BAND = 16
"""Rows of an image record that one step of HAIR or of FACE walks.

Measured 2026-09-15 by `oracle.py --assembly`, pressing each row from the
bottom of its range to the top: the `v` of the two primitives each owns moves
in blocks of sixteen rows of the record at HAIR_IMAGE, and never anything else.
"""

HAIR_COLOUR_PRIMITIVES = (0, 1, 4, 9, 14, 16, 17)
"""The HEAD_SECTION primitives whose CLUT id the H.COL field walks.

Seven, measured identically on both slots, and HAIR_PRIMITIVES is a subset:
the hair is two of them, and the other five are hair-coloured parts of the head
that the HAIR field does not reshape.  The whole hit list, not a sample.
"""

SKIN_COLOUR_PRIMITIVES = (0, 1, 8, 9, 13, 14, 16, 17)
"""The HEAD_SECTION primitives whose CLUT id the SKIN field walks.

Eight, measured identically on both slots (`oracle.py --fields SKIN`,
2026-09-15): a step adds 0x40 to byte 2, which is one whole 256-entry record --
the row of the grid, with the column left where it was.

It is here to be crossed with HAIR_COLOUR_PRIMITIVES, and the crossing is the
point: the union of the three colour fields is **nine** of the head's eighteen
primitives, and primitive 4 is in H.COL and NOT here -- the one place in the
head where "row x column" does not hold.  Recorded by
[`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md), which found it by
subtraction: what a field does not move is as measured as what it does.
"""

BOOTS_PALETTE = 67940
"""The palette the boots sample, at VRAM (0, 484).

The CARP table labels this offset "Botines".  What confirms it is not the label
but the geometry: the two EDT_MOD.BIN sections LOOKS-TASK-09 named the feet --
by mirroring and by being the only two both figures share -- sample this
palette and nothing else, and no other section samples it.
"""

PLAYER_RECORD_OFFSET = 157164
PLAYER_RECORD_COUNT = 1449
PLAYER_RECORD_SIZE = 12
"""The packed appearance/attribute records inside /SELECT.BIN.

1,449 x 12 B = 17,388 B ending at 174,552, inside the file's 300,648.

**The offset came from a third party and is now measured**, by two witnesses
that never met it: `OFS_PLAYER_ATTR` of `src/core/include/we2002/Offsets.hpp`
resolves to exactly this byte of exactly this file (`tools/pes2/ofs_map.py`),
and that offset is one the golden tests verify against `ed.exe`.

**The count came from the same third party and was wrong.**  It said 1,242
until 2026-09-15, when LOOKS-TASK-13 measured 1,449 twice over: it is
`PLAYERS_TOTAL - PLAYERS_NC` of `src/core/include/we2002/Types.hpp`, which is
what `Database::Load` reads, and the disc says the same without being asked --
the first 1,449 records decode to a height between 155 and 202, and record
1,449 is the first that is all zero.
"""


class WrongDisc(Exception):
    """Raised when a file is read from a disc that may not supply it."""


class BadPointerList(Exception):
    """Raised when a header pointer does not lead to a list of the known shape."""


class WrongBase(Exception):
    """Raised when the load address derived from a file is not the known one."""


def digest(data: bytes) -> str:
    """sha256 of *data*, hex, lowercase -- the one spelling used here."""
    return hashlib.sha256(data).hexdigest()


def is_trusted(disc_path: str, data_digest: str) -> bool:
    """Is *data_digest* the content this project expects at *disc_path*?

    Unknown paths answer False rather than True: a file nobody measured is
    not a file anybody may trust.
    """
    return DIGEST.get(disc_path) == data_digest


def _hint_for(disc_path: str) -> str:
    """The sentence that names the real problem behind a refusal at *disc_path*.

    Every path in DIGEST has to get one.  The families are not decoration: a
    mismatch means something different for each, and the reader is being told
    where to look.  self_check() walks DIGEST and demands a non-empty answer
    for every entry, because the way this went wrong the first time was by
    omission -- /SELECT.BIN belonged to no family and fell through to "",
    leaving the bare "digest mismatch" the docstring above calls the failure.
    """
    if disc_path in TEXTURE_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and textures and palettes may only "
            f"be read from the Japanese one.  Point {ENV_IMAGE} at it; "
            f"{ENV_DRIVE_IMAGE} is the disc you drive, not the disc you read."
        )
    if disc_path in RECORD_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and the player records are read from "
            f"the Japanese one.  Point {ENV_IMAGE} at it; {ENV_DRIVE_IMAGE} "
            f"is the disc you drive, not the disc you read."
        )
    if disc_path in GEOMETRY_FILES:
        return (
            f"  {disc_path} is identical on both known discs, so a mismatch "
            f"means a third disc -- another release, or a modified image."
        )
    return ""


def require(disc_path: str, data: bytes, image: str = "<unknown image>") -> bytes:
    """Return *data*, or refuse it with a message that names the real problem.

    The message matters as much as the refusal.  The mistake this guards is
    "you opened the English disc", and an exception that only says "digest
    mismatch" sends the reader looking at the parser instead.
    """
    got = digest(data)
    if is_trusted(disc_path, got):
        return data

    expected = DIGEST.get(disc_path)
    if expected is None:
        raise WrongDisc(
            f"{disc_path}: nothing measured for this path, so nothing to "
            f"trust it against (read from {image})"
        )

    hint = _hint_for(disc_path)

    raise WrongDisc(
        f"{disc_path}: read {got} from {image}, expected {expected}.{hint}"
    )


def derive_base(data: bytes) -> tuple[int, int]:
    """Derive the KSEG0 load address of a model file from its own header.

    Returns (header_words, base).

    The method, not the number, is what matters -- a constant nobody can
    re-derive is a constant nobody can check.  Both model files open with a
    run of KSEG0 pointers, and the run ends at the first word that is not one
    (a count, or the 0x000000FF terminator).  The lowest of those pointers
    aims at the first byte past the run, because that is where the record
    list begins.  So:

        base = min(header pointers) - 4 * (number of header words)

    Measured 2026-09-14, and it is one rule for both files even though their
    headers are very different sizes:

        EDT_MOD.BIN   2 words, min 0x8011C008, 0x8011C008 - 8  = 0x8011C000
        MODEL.BIN    18 words, min 0x8016E848, 0x8016E848 - 72 = 0x8016E800

    The 2 and the 18 are not guessed: `lzss.py -v` reports the same header
    lengths for these files ("header 2 w -> stream at 8"), from its own
    reading, which is a second witness to where the run ends.

    **Do not run this over the whole file.** Vertex and colour data is full of
    words with the top bit set -- 642 of them in EDT_MOD.BIN, 1,703 in
    MODEL.BIN -- and only a few dozen are pointers.  Reading those as an
    address table produces targets in the billions and a base that means
    nothing.  The run at the head is bounded precisely because it stops at the
    first non-pointer.
    """
    if len(data) < 8:
        raise WrongBase("file is %d bytes: too short to hold a header" % len(data))

    words = len(data) // 4
    header = 0
    while header < words:
        word = int.from_bytes(data[header * 4:header * 4 + 4], "little")
        if word < 0x80000000:
            break
        header += 1
    else:
        raise WrongBase("every word is a KSEG0 pointer: this is not a model file")

    if header == 0:
        raise WrongBase(
            "the file does not start with a KSEG0 pointer (first word is "
            "0x%08x), so it has no pointer table to derive a base from"
            % int.from_bytes(data[0:4], "little")
        )

    pointers = [
        int.from_bytes(data[i * 4:i * 4 + 4], "little") for i in range(header)
    ]
    base = min(pointers) - 4 * header

    # Every pointer in the run has to land inside the file under that base.
    # This is the cross-check that makes the answer an answer: a base derived
    # from a coincidence would send some of its own siblings out of range.
    for index, pointer in enumerate(pointers):
        target = pointer - base
        if not 0 <= target < len(data):
            raise WrongBase(
                "base 0x%08x puts header pointer %d (0x%08x) at %d, outside "
                "the file's %d bytes" % (base, index, pointer, target, len(data))
            )

    return header, base


def pointer_density(data: bytes, base: int) -> tuple[int, int]:
    """Count the words that look like pointers, and those that land inside.

    Returns (words with the top bit set, of those, how many fall inside the
    file under *base*).  This is the measurement behind derive_base()'s
    warning not to sweep the whole file: vertex and colour data is full of
    words with the top bit set, and only a few dozen of them are addresses.
    The docstring there carries the two pairs as prose; this is how a caller
    re-derives them instead of trusting the prose.

    It lives here rather than in the caller because 0x80000000 is an address,
    and rule 1 of the plan puts every address in this file -- a caller
    counting high-bit words itself would be caught by --sweep, correctly.
    """
    high = 0
    inside = 0
    for index in range(len(data) // 4):
        word = int.from_bytes(data[index * 4:index * 4 + 4], "little")
        if word < 0x80000000:
            continue
        high += 1
        if 0 <= word - base < len(data):
            inside += 1
    return high, inside


LIST_TERMINATOR = 0x000000FF  # not-an-address: the word that closes a pointer list


def read_pointer_list(data: bytes, offset: int, base: int) -> list[int]:
    """The targets of the record list at *offset*, as file offsets.

    Thin wrapper over read_pointer_entries(); most callers want only the
    offsets.  A caller that has to tell one kind of entry from another -- and
    is_derivable() does -- wants the tags too.
    """
    return [target for _tag, target in read_pointer_entries(data, offset, base)]


def read_pointer_entries(data: bytes, offset: int, base: int) -> list:
    """Read one record list at *offset* and return its (tag, offset) entries.

    The shape this reads, measured 2026-09-14 on EDT_MOD.BIN: pairs of (tag,
    KSEG0 pointer) closed by LIST_TERMINATOR.  Both of that file's lists carry
    a [count][pad] header before the pairs, and whether a list has one can be
    read off the file rather than assumed -- if the second word is a pointer,
    the pairs have already begun.

    **The variant MODEL.BIN uses, measured 2026-09-14 by LOOKS-TASK-05: a
    (0, 0) pair is an EMPTY SLOT, not the end.** The earlier reading called
    the list at 672 malformed -- "it closes with 0x00000000 at 736 rather than
    with LIST_TERMINATOR" -- and that was wrong twice over.  The word at 736 is
    entry 8 of a pair whose tag is also zero, and the list goes on to close
    with LIST_TERMINATOR at 768 like every other one.  Skipping the empty pair
    reads it as ten targets, and all six lists that were refused read cleanly.

    A zero pointer is skipped rather than kept because it is not an address:
    keeping it would put offset 0 -- the file header -- in a list of section
    starts, and a scan handed that walks into the pointer table.

    Every target is checked against the file's length.  A list that does not
    close, or that aims outside, raises: guessing here would produce a
    plausible list of offsets and a scan that walks into the middle of a
    section.
    """
    words = len(data) // 4

    def word(index):
        if not 0 <= index < words:
            raise BadPointerList(
                "pointer list at %d runs past the file's %d bytes"
                % (offset, len(data))
            )
        return int.from_bytes(data[index * 4:index * 4 + 4], "little")

    if offset % 4:
        raise BadPointerList("pointer list at %d is not word-aligned" % offset)

    index = offset // 4
    if word(index + 1) < 0x80000000:
        index += 2  # a [count][pad] header, as in EDT_MOD.BIN

    targets = []
    while True:
        tag = word(index)
        if tag == LIST_TERMINATOR:
            return targets
        pointer = word(index + 1)
        if tag == 0 and pointer == 0:
            index += 2  # an empty slot -- see the docstring
            continue
        if pointer < 0x80000000:
            raise BadPointerList(
                "pointer list at %d: entry %d holds 0x%08x, which is not a "
                "KSEG0 pointer and is not the terminator"
                % (offset, len(targets), pointer)
            )
        target = pointer - base
        if not 0 <= target < len(data):
            raise BadPointerList(
                "pointer list at %d: entry %d aims at %d, outside the file's "
                "%d bytes" % (offset, len(targets), target, len(data))
            )
        targets.append((tag, target))
        index += 2


def record_lists(data: bytes) -> list[list[int]]:
    """Every record list the header of *data* names, in header order.

    EDT_MOD.BIN has TWO, of eleven records each, sharing two of them.  Reading
    only one of the two is how a scan came to start 43% into the file and
    still close on an exact EOF -- the counts were right for what was read,
    and what was read was half the file (CORR-LOOKS-010).

    Raises BadPointerList on MODEL.BIN today: see read_pointer_list.
    """
    header, base = derive_base(data)
    pointers = [
        int.from_bytes(data[i * 4:i * 4 + 4], "little") for i in range(header)
    ]
    return [read_pointer_list(data, p - base, base) for p in pointers]


def geometry_start(data: bytes) -> int:
    """The offset of the first section: the lowest target of any header list.

    Derived rather than stored, which is the same choice derive_base() makes
    and for the same reason: a constant nobody re-derives is a constant nobody
    checks.  Here it is also the fix for a specific failure -- a scan handed a
    hand-picked start reported an exact EOF and looked complete.

    EDT_MOD.BIN answers 216.

    **MODEL.BIN must NOT use this, and the reason is measured rather than
    procedural.** Since the empty-slot variant was understood its header lists
    all read, so the obstacle is no longer parsing -- it is the answer.
    Sixteen of its eighteen header pointers lead to lists that open with an
    entry tagged 0x80, and those entries aim at one of TWO flat runs of bare
    KSEG0 pointers: twelve at offset 104, which is 64 pointers long, and four
    at offset 232, which is 32.  Neither run is a section, and neither is a
    shape this function reads.  min over all targets therefore answers 104,
    which would hand a scan a start inside a pointer table and fail in the
    exact way deriving the start was introduced to prevent.

    The other two header pointers lead to lists of ONE entry, tagged 0x02, and
    those do name sections: 1816 and 4792, the file's first two.  So the lists
    DO state the constant -- a derivation by lowest 0x02-tagged target answers
    1816, measured.  MODEL_GEOMETRY_START stays a constant because it is cheap
    and because that derivation has not been exercised on any second file, not
    because the information is absent (CORR-LOOKS-013 measured both claims:
    this docstring used to say every list aims at 104, and that 1816 was a
    fact the lists do not state).
    """
    if not is_derivable(data):
        raise BadPointerList(
            "this file's lists name a target that is not a section (the "
            "0x80-tagged entry), so the lowest target is not the start of "
            "geometry -- use the file's recorded constant instead"
        )
    targets = [t for one in record_lists(data) for t in one]
    if not targets:
        raise BadPointerList("the header names no record at all")
    return min(targets)


def require_base(disc_path: str, data: bytes) -> int:
    """Derive the load base of *data* and demand it match the known constant.

    The constant is in BASE and the answer comes from the file, so the two
    disagreeing is a real event: a different release, a modified image, or a
    file that is not the one its name says.
    """
    expected = BASE.get(disc_path)
    if expected is None:
        raise WrongBase("%s: no load address recorded for this file" % disc_path)

    _header, got = derive_base(data)
    if got != expected:
        raise WrongBase(
            "%s: header derives base 0x%08x, expected 0x%08x -- a different "
            "release, a modified image, or not this file at all"
            % (disc_path, got, expected)
        )
    return got


def self_check() -> None:
    """Exercise the guard on made-up bytes, including the case that must fail.

    Synthetic on purpose: this runs on a machine with no image, no venv and
    no display, which is the contract of the selftest gate.  The live
    demonstration against the two real discs is `--check-discs`.
    """
    # Green: the measured content passes, by construction.
    body = b"whatever"
    saved = DIGEST[DAT2D]
    try:
        DIGEST[DAT2D] = digest(body)
        assert require(DAT2D, body, "fake") is body
        assert is_trusted(DAT2D, digest(body))

        # Red 1: the wrong content is refused, and the message says which
        # disc problem it is rather than just "mismatch".
        try:
            require(DAT2D, b"english", "fake")
        except WrongDisc as exc:
            text = str(exc)
            assert "Japanese" in text, text
            assert ENV_IMAGE in text, text
        else:
            raise AssertionError("DAT2D guard accepted foreign content")
    finally:
        DIGEST[DAT2D] = saved

    # Red 2: a path nobody measured is refused rather than waved through.
    try:
        require("/BIN/NOSUCH.BIN", b"", "fake")
    except WrongDisc as exc:
        assert "nothing measured" in str(exc), str(exc)
    else:
        raise AssertionError("unmeasured path was trusted")

    # Red 3: geometry gets its own wording, because a mismatch there means a
    # third disc and not the English one.
    try:
        require(MODEL, b"not the model", "fake")
    except WrongDisc as exc:
        assert "third disc" in str(exc), str(exc)
    else:
        raise AssertionError("geometry guard accepted foreign content")

    # Red 4: EVERY measured path gets a hint, not just the three with a
    # family.  This one is a sweep rather than a case, on purpose: /SELECT.BIN
    # was refused with a bare "digest mismatch" for exactly as long as it
    # belonged to no family, and the next path added to DIGEST would inherit
    # that silence the same way -- by omission, which no single red case
    # catches.
    for measured in DIGEST:
        assert _hint_for(measured), "no hint for %s" % measured
        try:
            require(measured, b"content from the wrong disc", "fake")
        except WrongDisc as exc:
            text = str(exc)
            assert text.rstrip().endswith("."), text
            assert len(text) > len(
                "%s: read %s from fake, expected %s."
                % (measured, digest(b"x"), DIGEST[measured])
            ), text
        else:
            raise AssertionError("%s guard accepted foreign content" % measured)

    # And the two Japanese-only files say so by name, since "you opened the
    # English disc" is the overwhelmingly likely cause of either refusal.
    for japanese_only in TEXTURE_FILES | RECORD_FILES:
        assert ENV_IMAGE in _hint_for(japanese_only), japanese_only
        assert "Japanese" in _hint_for(japanese_only), japanese_only

    # The two disc variables are two different names.  They have been one
    # name before, in another project, and it cost twelve runs.
    assert ENV_IMAGE != ENV_DRIVE_IMAGE

    # -- derive_base, on a synthetic header shaped like the real ones -------
    #
    # Green: two header words whose lower pointer aims at offset 8.
    synthetic = (
        (0x8011C070).to_bytes(4, "little")
        + (0x8011C008).to_bytes(4, "little")
        + b"\x00" * 512
    )
    assert derive_base(synthetic) == (2, 0x8011C000), derive_base(synthetic)

    # Red 5: a base that would throw one of its own pointers out of the file
    # is refused rather than returned.  Same shape, but the high pointer now
    # aims far past the end.
    outside = (
        (0x8011C008).to_bytes(4, "little")
        + (0x8019C070).to_bytes(4, "little")
        + b"\x00" * 512
    )
    try:
        derive_base(outside)
    except WrongBase as exc:
        assert "outside the file" in str(exc), str(exc)
    else:
        raise AssertionError("derive_base accepted a base its own pointers deny")

    # Red 6: a file that does not begin with a pointer has no table to read,
    # and saying so beats returning a number computed from nothing.
    try:
        derive_base(b"\x02\x00\x00\x00" + b"\x00" * 32)
    except WrongBase as exc:
        assert "no pointer table" in str(exc), str(exc)
    else:
        raise AssertionError("derive_base invented a base for a headerless file")

    # Red 7: require_base reports the mismatch with both numbers, because
    # "wrong base" without the derived value says nothing about which disc.
    elsewhere = (
        (0x80200070).to_bytes(4, "little")
        + (0x80200008).to_bytes(4, "little")
        + b"\x00" * 512
    )
    assert derive_base(elsewhere) == (2, 0x80200000), derive_base(elsewhere)
    try:
        require_base(EDT_MOD, elsewhere)
    except WrongBase as exc:
        assert "expected 0x8011c000" in str(exc).lower(), str(exc)
    else:
        raise AssertionError("require_base accepted a foreign base")

    # pointer_density answers about the same synthetic vector: two header
    # pointers set the top bit, the 512 zero bytes do not, and both header
    # pointers land inside by construction -- which is what derive_base just
    # demanded.  The point of the function is the ratio it reports on a real
    # file, so the assertion here is only that it counts what it says.
    assert pointer_density(synthetic, 0x8011C000) == (2, 2), pointer_density(
        synthetic, 0x8011C000
    )
    assert pointer_density(bytes(64), 0x8011C000) == (0, 0)

    # -- the address tables agree with each other ---------------------------
    #
    # Every file with a digest has an LBA and a size; a path added to one map
    # and forgotten in the others is the omission this catches, the same way
    # red 4 catches a missing hint.
    for measured in DIGEST:
        assert measured in LBA, "no LBA for %s" % measured
        assert measured in SIZE, "no size for %s" % measured
    assert set(BASE) == GEOMETRY_FILES, (set(BASE), GEOMETRY_FILES)

    # The player records fit inside the file they are said to live in.
    span = PLAYER_RECORD_OFFSET + PLAYER_RECORD_COUNT * PLAYER_RECORD_SIZE
    assert span <= SIZE[SELECT], (span, SIZE[SELECT])

    # MODEL.BIN's geometry starts after its header, not inside it.
    assert MODEL_GEOMETRY_START > 18 * 4

    # -- record_lists and geometry_start, on a synthetic model file ---------
    #
    # Built in EDT_MOD.BIN's shape: a two-word header of pointers, each aiming
    # at a [count][pad] list of (tag, pointer) pairs closed by the terminator.
    # Two lists, and the answer is the LOWEST target of either -- which is the
    # whole point: reading one list and starting there is how nine sections
    # went unread while the scan still closed on an exact EOF.
    def _word(value):
        return value.to_bytes(4, "little")

    fake_base = 0x80100000
    #      0: -> list one at 8        4: -> list two at 40
    #
    # The lower header pointer aims at offset 8, the first byte past the
    # two-word run, because that is the rule derive_base() reads.
    model = _word(fake_base + 8) + _word(fake_base + 40)
    #      8: count, pad, then two records aiming at 200 and 120
    model += _word(3) + _word(0)
    model += _word(2) + _word(fake_base + 200)
    model += _word(2) + _word(fake_base + 120)
    model += _word(LIST_TERMINATOR)
    model += bytes(40 - len(model))
    #     40: a list with no [count][pad], aiming at 300 and 360, with an
    #         EMPTY SLOT between them -- a (0, 0) pair is not the end.
    #
    # The slot is in the MIDDLE and not at the front on purpose: a list that
    # opens with (0, 0) is swallowed by the [count][pad] heuristic above,
    # which reads any non-pointer second word as a preamble.  Planted at the
    # front, the branch this exercises never runs, and its negative control
    # comes out green -- measured.
    model += _word(2) + _word(fake_base + 300)
    model += _word(0) + _word(0)
    model += _word(2) + _word(fake_base + 360)
    model += _word(LIST_TERMINATOR)
    model += bytes(400 - len(model))

    assert derive_base(model) == (2, fake_base), derive_base(model)
    assert record_lists(model) == [[200, 120], [300, 360]], record_lists(model)
    assert geometry_start(model) == 120, geometry_start(model)

    # Red 11: the empty slot is SKIPPED, not stored and not treated as the
    # end.  Both wrong readings are silent -- storing it puts offset 0, the
    # file header, in a list of section starts; ending there hid six of
    # MODEL.BIN's eighteen lists behind "this list is malformed".  Without a
    # (0, 0) pair in the synthetic above, the branch that handles it never ran
    # and its negative control came out green.
    assert 0 not in record_lists(model)[1], record_lists(model)
    assert record_lists(model)[1] == [300, 360], record_lists(model)
    entries = read_pointer_entries(model, 40, fake_base)
    assert entries == [(2, 300), (2, 360)], entries

    # Red 9: a list that aims outside the file is refused, not returned.  A
    # plausible-looking offset here sends the scan into the middle of a
    # section, where it reads a vertex count out of colour data.
    far = model[:20] + _word(fake_base + 4000) + model[24:]  # the 200 pointer
    try:
        record_lists(far)
    except BadPointerList as exc:
        assert "outside the file" in str(exc), str(exc)
    else:
        raise AssertionError("a pointer list aiming past the file was accepted")

    # Red 10: a list that never reaches its terminator is refused rather than
    # read to the end of the file.
    unclosed = model.replace(_word(LIST_TERMINATOR), _word(2), 1)
    try:
        record_lists(unclosed)
    except BadPointerList as exc:
        assert "runs past the file" in str(exc) or "not a KSEG0" in str(exc), exc
    else:
        raise AssertionError("an unterminated pointer list was accepted")

    # -- the sweep itself, on a planted tree --------------------------------
    #
    # Red 8, and the reason it is here: --sweep is only ever run against the
    # real tree, which is clean, so it was only ever observed GREEN.  A sweep
    # that stopped matching .py, or blanked a line too eagerly, or resolved
    # its root to an empty directory, prints the same "no address outside
    # layout.py" and exits 0 -- the sentence a reader takes for proof.  The
    # tree below is built to be found in, so the sweep is watched working.
    planted = {
        "bad.py": ["BASE = 0x8011C000"],
        "ok.py": ["SHIRT = 0x1234  # not-an-address: a colour, not a pointer"],
        "above.py": ["# not-an-address: this annotation is on the wrong line",
                     "Y = 0x5678"],
        ADDRESS_OWNER: ["BASE = 0x8016E800"],
        os.path.join("ui", "deep.py"): ["OFFSET = 157164"],
        os.path.join("ui", ADDRESS_OWNER): ["BASE = 0x8016E800"],
    }
    with tempfile.TemporaryDirectory() as tmp:
        for name, body in planted.items():
            full = os.path.join(tmp, name)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "w", encoding="utf-8") as handle:
                for text in body:
                    print(text, file=handle)

        stats: dict = {}
        caught = {(where, number) for where, number, _ in
                  sweep_addresses(tmp, stats)}

        # A hex literal is found, and so is a four-digit decimal in a
        # SUBDIRECTORY -- which is what proves the walk descends.  os.listdir
        # would miss ui/ entirely, and the .mcr cycle lost a whole package
        # that way.
        assert ("bad.py", 1) in caught, caught
        assert (os.path.join("ui", "deep.py"), 1) in caught, caught

        # The escape works, and it works PER LINE: an annotation written on
        # the line above excuses nothing.
        assert not any(where == "ok.py" for where, _ in caught), caught
        assert ("above.py", 2) in caught, caught

        # The owner is exempt by path.  A same-named file in a subdirectory is
        # not the owner and does not inherit the exemption.
        assert not any(where == ADDRESS_OWNER for where, _ in caught), caught
        assert (os.path.join("ui", ADDRESS_OWNER), 1) in caught, caught

        # And the sweep says how much it read, so "swept nothing" stops
        # looking like "swept everything and found nothing".
        assert stats["files"] == len(planted) - 1, stats
        assert stats["lines"] == 6, stats

        empty_stats: dict = {}
        with tempfile.TemporaryDirectory() as nothing:
            assert sweep_addresses(nothing, empty_stats) == []
        assert empty_stats == {"files": 0, "lines": 0}, empty_stats

    print("layout: self_check ok")


def is_derivable(data: bytes) -> bool:
    """Can geometry_start() be trusted for this file?

    True when every entry of every header list is a plain section pointer.
    False when any entry carries the 0x80 tag, which MODEL.BIN uses for the
    entry that aims at its flat pointer array -- see geometry_start().

    **It reads the ENTRY tags, not the first word each header pointer lands
    on.** Those are the same word in MODEL.BIN, whose lists open straight into
    pairs, and different in EDT_MOD.BIN, whose lists carry a [count][pad]
    preamble.  A check that read the landing word answered correctly on both
    real files while comparing two different things, and a list that combined
    a preamble with a tagged entry walked past it.
    """
    try:
        header, base = derive_base(data)
        for index in range(header):
            pointer = int.from_bytes(data[index * 4:index * 4 + 4], "little")
            entries = read_pointer_entries(data, pointer - base, base)
            if any(tag == SUBLIST_TAG for tag, _target in entries):
                return False
    except (WrongBase, BadPointerList):
        return False
    return True


SUBLIST_TAG = 0x80  # not-an-address: the tag MODEL.BIN's lists open with

GEOMETRY_EXPECTED = {
    # (sections, vertices, primitives, end) for a scan from the file's start
    # of geometry.  Counts rather than addresses, but they belong here for the
    # same reason SIZE does: they are facts about one named file, and rule 1
    # keeps modelfile.py free of numbers it would otherwise have to carry.
    #
    # **Each one is only meaningful with the offset the scan began at**, which
    # is why GEOMETRY_START sits beside it.  A scan of EDT_MOD.BIN from 15,704
    # reports 11/690/611 and an exact EOF, looks complete, and is 43% of the
    # file (CORR-LOOKS-010).
    MODEL: (106, 2461, 1767, 64800),
    EDT_MOD: (20, 1218, 1074, 36072),
}

GEOMETRY_START = {
    MODEL: MODEL_GEOMETRY_START,
    EDT_MOD: 216,
}
"""Where a scan of each file begins.

EDT_MOD.BIN's entry is the answer geometry_start() derives, kept here so a
caller can compare the two; MODEL.BIN's is the constant, because its lists do
not state it.  self_check() demands the derived and the recorded agree.
"""


TMD_CLAIMED = (0x8016821C, 0x80168C0C, 0x8016A2C4, 0x8016A650)
"""The four textured TMDs section 1.6 of the plan records living in RAM.

Recorded there on 2026-09-13 as unknown (a) -- real Sony TMDs, already fixed by
`OpenTMD`, textured, with 92, 261, 30 and 18 vertices, belonging to neither
model file.  They are here because they are ADDRESSES and this module owns
addresses, and because what LOOKS-TASK-08 measured about them has to sit beside
them: **in both save states all four hold nothing but zeros**, and the TMDs that
really are in RAM on that screen are 29 small ones between 0x800C1678 and
0x800C4948, 4 to 54 vertices each, that no LOOKS field touches.  So the four
addresses are not reproducible from the states, and nothing in this cycle may
be built on them.
"""

TMD_MAGIC = 0x00000041
"""The first word of a Sony TMD."""

ADDRESS_OWNER = "layout.py"
"""The one module of tools/looks/ allowed to carry an address (plan 3.3, rule 1)."""

# What the sweep calls an address.  Anchored, because by the time they are
# applied the candidate is already a whole NUMBER token from tokenize -- there
# is nothing around it to search.
#
# They are module constants and not locals so there is ONE definition of each
# to edit.  The tokenize rewrite left an unanchored pair behind in
# sweep_addresses() under these same two names, dead but readable, and whoever
# went to loosen or tighten the rule would have found those first, edited them,
# changed nothing, and watched the gate stay green (CORR-LOOKS-011).
_HEX_LITERAL = re.compile(r"\A0[xX][0-9a-fA-F]+\Z")
_BIG_DECIMAL = re.compile(r"\A\d{4,}\Z")


def sweep_addresses(root: str | None = None,
                    stats: dict | None = None) -> list[tuple[str, int, str]]:
    """Find addresses written outside this file.  Returns the offending lines.

    *stats*, if given, is filled with how much was actually read -- "files" and
    "lines".  A sweep that opened nothing and a sweep that read everything and
    found nothing print the same sentence otherwise, and that sentence is the
    one a reader takes for "rule 1 is being kept".  Same failure superpack_count
    had, closed the same way (CORR-LOOKS-003, CORR-LOOKS-009).

    Rule 1 of the plan is what lets an offset move later without being hunted
    through the tree, and a rule nobody sweeps is a rule that decays one
    commit at a time.

    What counts as an address: a hexadecimal literal, or a decimal literal of
    four digits or more, **written as code**.  The escape is one line:

    * a line carrying `# not-an-address: <why>` is exempt.  The marker is
      spelled as the claim it makes -- an earlier spelling, `# address:`, read
      as the opposite of what the annotator meant, and a tripwire whose
      escape hatch reads backwards will be used wrongly.

    Strings and comments are not code, so a sha256 in a message and a date in
    a docstring are not addresses.  **That reading comes from `tokenize` and
    not from scanning for quote characters.** The hand-rolled stripper this
    replaced could not see triple quotes, so every prose paragraph in a module
    was swept as if it were code: `section.py` arrived with four dates in
    docstrings and the gate went red on 2026-09-14 over the word "2026".
    Annotating prose with `# not-an-address:` would have been the wrong repair
    -- it would train the exemption on text that was never a candidate, and
    the exemption is supposed to be rare enough to read.

    The walk uses os.walk and not os.listdir: `ui/` is a directory, and the
    .mcr cycle left one of those outside its own sweep exactly this way.
    """
    if root is None:
        root = os.path.dirname(os.path.abspath(__file__))

    findings = []
    files = 0
    lines = 0

    for parent, _dirs, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".py"):
                continue
            path = os.path.join(parent, name)
            # The owner is exempt by its PATH, not by its name: os.walk
            # descends, so a tools/looks/ui/layout.py would otherwise be
            # excused for free -- a whole directory outside the rule, which is
            # how the .mcr cycle lost one.
            if os.path.relpath(path, root) == ADDRESS_OWNER:
                continue
            files += 1
            with open(path, encoding="utf-8") as handle:
                source = handle.read()
            source_lines = source.splitlines()
            lines += len(source_lines)
            exempt = {
                number for number, line in enumerate(source_lines, 1)
                if "# not-an-address:" in line
            }
            for number in _address_lines(source, path):
                if number in exempt:
                    continue
                text = source_lines[number - 1] if number <= len(source_lines) else ""
                findings.append((os.path.relpath(path, root), number, text.rstrip()))
    if stats is not None:
        stats["files"] = files
        stats["lines"] = lines
    return findings


def _address_lines(source: str, path: str) -> set:
    """Line numbers of *source* holding a numeric literal that looks like an address.

    Uses `tokenize`, so a number is only a candidate when Python itself calls
    it a NUMBER token: text inside a string and text after a `#` are other
    token kinds and never reach the test.

    A file that will not tokenize -- a syntax error mid-edit -- is reported as
    one finding on line 1 rather than skipped.  Skipping would mean the sweep
    quietly stops covering a file at the exact moment somebody is changing it.
    """
    found = set()
    try:
        tokens = tokenize.generate_tokens(io.StringIO(source).readline)
        for kind, text, (row, _col), _end, _line in tokens:
            if kind != tokenize.NUMBER:
                continue
            body = text.replace("_", "")
            if _HEX_LITERAL.match(body) or _BIG_DECIMAL.match(body):
                found.add(row)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        found.add(1)
    return found


def _sweep(root: str | None = None) -> int:
    stats: dict = {}
    findings = sweep_addresses(root, stats)
    swept = " (%d file(s), %d line(s) swept)" % (stats["files"], stats["lines"])
    if not findings:
        print("layout --sweep: no address outside %s%s"
              % (ADDRESS_OWNER, swept))
        return 0
    for path, number, line in findings:
        print("  %s:%d: %s" % (path, number, line.strip()))
    print("layout --sweep: %d line(s) carrying an address outside %s%s"
          % (len(findings), ADDRESS_OWNER, swept))
    return 1


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        self_check()
        return 0
    if len(argv) == 2 and argv[1] == "--sweep":
        return _sweep()
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

"""Every address the kit2d tool reads or writes, in one module.

PLAN-KIT2D-PY.md section 1.1 (measured in SUPERPACK-UNIFORMES-2D.md, section
7 there): the 2D kit of a team is a palette, a sprite model and the radar
colours, and the model draws from three images.  No other file of
`tools/kit2d/` may spell one of these numbers; `selftest.py` sweeps for them.

The LBAs and sizes are the same on the three discs of `roms/` (section 2.1).
The team order is the original editor's: 95 teams, nations and all-stars
first (`teams[id-1]`), then the 32 Master League clubs.

The load base of the overlay is INFERRED, not measured: section 1.2 took it
from one run of in-range pointers, and section 4.1 (phase 0) measures it in
RAM.  Until then `LOAD_BASE_STATUS` says so, and no render enters a gate.
"""

from __future__ import annotations

TEAMS = 95
KIT_SETS = 2                    # first kit, second kit

# -- palette and model: /SELECT2.BIN ---------------------------------------

SELECT2_PATH = "/SELECT2.BIN"
SELECT2_LBA = 1050

PALETTE_OFFSET = 172096         # 64 bytes per team: first kit, second at +32
PALETTE_TEAM_STRIDE = 64
PALETTE_SECOND_KIT = 32
PALETTE_WORDS = 16              # BGR555
PALETTE_BYTES = PALETTE_WORDS * 2
PALETTE_WORD_0 = 0x0000         # on the 190 kits of the original discs
PALETTE_WORD_1 = 0x4208

MODEL_TABLE_OFFSET = 225808     # 95 x (first, second) RAM pointers
MODEL_POINTER_BYTES = 4
MODEL_TABLE_BYTES = TEAMS * KIT_SETS * MODEL_POINTER_BYTES     # 760
MODEL_DISTINCT = 190
MODEL_POINTER_LOW = 0x800FB8AC  # the range the 190 pointers fall in
MODEL_POINTER_HIGH = 0x8010000C

# -- the three images: /BIN/DATSEL.BIN --------------------------------------

DATSEL_PATH = "/BIN/DATSEL.BIN"
DATSEL_LBA = 6000
GRAPHICS_STREAMS = (            # (LZSS stream number, byte offset)
    (21, 126536),
    (22, 129208),
    (23, 132000),
)
GRAPHICS_WIDTH = 128
GRAPHICS_HEIGHT = 128
GRAPHICS_BPP = 4                # low nibble first

# -- the palette the polipoli viewer uses: /BIN/DAT2D.BIN -------------------
# Not the game's palette; kept only so nobody mistakes it for one.

DAT2D_PATH = "/BIN/DAT2D.BIN"
DAT2D_LBA = 5300
VIEWER_PALETTE_OFFSET = 68484

# -- the radar: /SELECT.BIN -------------------------------------------------

SELECT_PATH = "/SELECT.BIN"
SELECT_LBA = 850
RADAR_FIRST_OFFSET = 0x3F534    # 2 bytes per team
RADAR_SECOND_OFFSET = 0x3F634
RADAR_BYTES = 2
RADAR_COLOURS = 8               # valid colours (SimoSapo)

# -- the overlay load base: INFERRED (section 1.2), measured by section 4.1 --

LOAD_BASE = 0x800CA930
LOAD_BASE_STATUS = "inferred"   # becomes "measured" when phase 0 closes 4.1

ADDRESSES = (
    PALETTE_OFFSET, MODEL_TABLE_OFFSET,
    *(offset for _, offset in GRAPHICS_STREAMS),
    VIEWER_PALETTE_OFFSET, RADAR_FIRST_OFFSET, RADAR_SECOND_OFFSET,
    MODEL_POINTER_LOW, MODEL_POINTER_HIGH, LOAD_BASE,
)
"""The numbers no other file of tools/kit2d may spell.  The LBAs stay out:
850 or 1050 is as likely a window width as a sector, and the files are read
by path; a sweep that cries wolf gets switched off."""


def palette_offset(team: int, kit_set: int) -> int:
    """Byte offset in /SELECT2.BIN of the palette of *team* (0..94), *kit_set* (0, 1)."""
    return PALETTE_OFFSET + PALETTE_TEAM_STRIDE * team + PALETTE_SECOND_KIT * kit_set


def model_offset(team: int, kit_set: int) -> int:
    """Byte offset in /SELECT2.BIN of the model pointer of *team*, *kit_set*."""
    return MODEL_TABLE_OFFSET + MODEL_POINTER_BYTES * (KIT_SETS * team + kit_set)


def radar_offset(team: int, kit_set: int) -> int:
    """Byte offset in /SELECT.BIN of the radar colours of *team*, *kit_set*."""
    base = RADAR_SECOND_OFFSET if kit_set else RADAR_FIRST_OFFSET
    return base + RADAR_BYTES * team


def self_check() -> list:
    """Complaints about the table's own consistency; empty when it holds."""
    bad = []
    if MODEL_TABLE_BYTES != 760:
        bad.append("the model table is %d bytes, section 1.1 says 760" % MODEL_TABLE_BYTES)
    if palette_offset(TEAMS - 1, 1) + PALETTE_BYTES > MODEL_TABLE_OFFSET:
        bad.append("the last palette runs into the model table")
    if radar_offset(TEAMS - 1, 0) + RADAR_BYTES > RADAR_SECOND_OFFSET:
        bad.append("the first-kit radar runs into the second-kit one")
    offsets = [offset for _, offset in GRAPHICS_STREAMS]
    if offsets != sorted(set(offsets)):
        bad.append("the graphics streams are not in increasing order")
    if not MODEL_POINTER_LOW < MODEL_POINTER_HIGH:
        bad.append("the model pointer range is empty")
    if not LOAD_BASE < MODEL_POINTER_LOW:
        bad.append("the load base is above the models it should precede")
    if LOAD_BASE_STATUS not in ("inferred", "measured"):
        bad.append("LOAD_BASE_STATUS is %r" % LOAD_BASE_STATUS)
    if len(set(ADDRESSES)) != len(ADDRESSES):
        bad.append("ADDRESSES holds a duplicate")
    return bad

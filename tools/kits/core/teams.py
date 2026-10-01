"""The team list of a disc: the name the ROM holds, or the English table.

PLAN-KITS-PY.md section 3.3.  The rule:

* **on the Japanese disc** the names come from `TEAM_NAMES`, the English
  table of the original editor, by team index (`name_origin == "table"`);
* **on any other disc** they come from the ROM (`name_origin == "rom"`) --
  which is also what an unknown disc gets: the ROM is all there is.

"Japanese" is decided by the disc, never by the text: the boot executable
`/SLPM_870.56` has to have the digest the `looks` layout measured on the
Japanese release.  All three discs in `roms/` boot a file of that name, and
only the digest tells them apart; guessing from the name bytes would read a
Japanese name decoded to blanks as an empty English one.

The ROM name is the mixed-case one ("Inter", not "INTER"), read where
`Database::Load` reads `mixed_case_name`: `OFS_TEAM_MIXED_CASE_NAME`, the
32 Master League clubs first and backwards, then the 63 nations and
all-stars backwards, each `TEAM_MIXED_CASE_NAME_LEN[i]` bytes and cut at
the first NUL (the `strcpy` of the original).  Offsets and lengths come
from `generated/team_names.py`, never typed here.

The index is the original editor's combobox order: nations 0..53,
all-stars 54..62, Master League clubs 63..94.  It is not the kit tag;
`tag` stays None until section 4.2 links the two.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Optional

from . import tex  # noqa: F401  (puts tools/pes2 and tools/looks on sys.path)
from .errors import SourceUnreadable
from .generated import team_names as names

import iso  # noqa: E402  (tools/pes2)
import layout  # noqa: E402  (tools/looks: the boot file and its Japanese digest)

ORIGIN_TABLE = "table"
ORIGIN_ROM = "rom"

GROUP_NATIONAL = "national"
GROUP_ALLSTAR = "allstar"
GROUP_ML = "ml"

TEAM_COUNT = names.TEAMS_NATIONAL + names.TEAMS_ALLSTAR + names.TEAMS_ML
NATIONAL_ALLSTAR = names.TEAMS_NATIONAL + names.TEAMS_ALLSTAR


@dataclass(frozen=True)
class TeamEntry:
    """One team of the disc, in the original editor's combobox order."""

    index: int
    name: str
    name_origin: str        # ORIGIN_TABLE or ORIGIN_ROM
    tag: Optional[str] = None
    """The kit tag (`TEX_<tag>`), None until section 4.2 is closed."""

    @property
    def group(self) -> str:
        if self.index < names.TEAMS_NATIONAL:
            return GROUP_NATIONAL
        if self.index < NATIONAL_ALLSTAR:
            return GROUP_ALLSTAR
        return GROUP_ML


def is_japanese(image) -> bool:
    """Whether the opened `iso.Image` is the Japanese release, by the digest
    of its boot executable."""
    if layout.BOOT not in image.files:
        return False
    try:
        data = image.read_file(layout.BOOT)
    except (iso.Form2Sector, iso.OutsideTrack):
        return False
    return hashlib.sha256(data).hexdigest() == layout.expected_digest(layout.BOOT)


def _mixed_case_names(image_path: str) -> list:
    """The 95 mixed-case names as `Database::Load` reads them, by team index."""
    order = ([names.TEAMS_ML + NATIONAL_ALLSTAR - 1 - i for i in range(names.TEAMS_ML)]
             + [NATIONAL_ALLSTAR - 1 - i for i in range(NATIONAL_ALLSTAR)])
    sizes = [names.TEAM_MIXED_CASE_NAME_LEN[t] for t in order]
    try:
        with open(image_path, "rb") as fh:
            fh.seek(names.OFS_TEAM_MIXED_CASE_NAME)
            raw = fh.read(sum(sizes))
    except OSError as exc:
        raise SourceUnreadable("Could not read the team names of %s: %s"
                               % (image_path, exc.strerror or exc)) from exc
    if len(raw) != sum(sizes):
        raise SourceUnreadable("%s ends inside the team names (%d of %d bytes)"
                               % (image_path, len(raw), sum(sizes)))
    out = [""] * TEAM_COUNT
    p = 0
    for team, size in zip(order, sizes):
        field = raw[p:p + size]
        out[team] = field.split(b"\0", 1)[0].decode("latin-1")
        p += size
    return out


def read_teams(image_path: str, image) -> tuple:
    """The 95 `TeamEntry` of the disc at *image_path* (*image* is it opened)."""
    if is_japanese(image):
        return tuple(TeamEntry(i, names.TEAM_NAMES[i], ORIGIN_TABLE) for i in range(TEAM_COUNT))
    rom = _mixed_case_names(image_path)
    return tuple(TeamEntry(i, rom[i], ORIGIN_ROM) for i in range(TEAM_COUNT))

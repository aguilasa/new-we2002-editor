#!/usr/bin/env python3
"""The Italian-to-English rename applied across the port (phase 3.5).

The inherited code names everything in Italian. Phase 2 anglicised class and
file names but deliberately left members, offsets and tables alone: while the
golden tests were being built, being able to compare field for field against
legacy/mfc/edDlg.cpp was worth more than consistency. Phase 3 closed that, so
this is the sweep.

Two of the three consumers are generators -- tools/port_database.py and
tools/extract_legacy_data.py both re-derive their output from the legacy
source on every run, so the rename has to live here rather than in the
generated files. tools/apply_glossary.py applies the same map to the
hand-written sources.

Order matters only where one name is a prefix of another *without* an
intervening word character; \\b handles the rest (OFS_NOMI_SQ1 does not match
inside OFS_NOMI_SQ1_F, because `_` is a word character). Longest-first
ordering is enforced in rename_identifiers() anyway.

Two names in here are corrections, not translations:

  * `nome_m` was documented as "long name". It is not: `m` is *minuscolo*,
    and the field holds the mixed-case spelling of the team name ("Bayern",
    "Galatasaray") as opposed to the all-caps `nomi[]` slots ("INTER").
  * `OFS_NOMI_PML1/2` sit under a "player" prefix but load squad_ml[].nomi[6]
    and [7] -- they are the 7th and 8th *team* name slots of a Master League
    club.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Class members, free functions and the shared constants.
# ---------------------------------------------------------------------------

MEMBERS: dict[str, str] = {
    # --- Player -----------------------------------------------------------
    "nome": "name",
    "posizione": "position",
    "col_pelle": "skin_colour",
    "stile_capelli": "hair_style",
    "col_capelli": "hair_colour",
    "stile_barba": "beard_style",
    "col_barba": "beard_colour",
    "altezza": "height",
    "corporatura": "build",
    "eta": "age",
    "scarpe": "boots",
    "piede": "foot",
    "attacco": "attack",
    "difesa": "defence",
    "forza": "strength",
    "resistenza": "stamina",
    "velocita": "speed",
    "accel": "acceleration",
    "passaggio": "passing",
    "pot_tiro": "shot_power",
    "prec_tiro": "shot_accuracy",
    "salto": "jump",
    "testa": "heading",
    "tecnica": "technique",
    "effetto": "swerve",
    "aggress": "aggression",
    "riflessi": "reflexes",
    "fuori_ruolo": "out_of_position",
    "numero": "number",
    "costo": "cost",
    "str_carat": "raw_attributes",
    # --- Team / MlTeam ----------------------------------------------------
    "nomi": "names",
    "nome_m": "mixed_case_name",
    "nomi_a": "abbreviations",
    "nomek": "kanji_name",
    "nomekanji": "raw_kanji_name",
    "bar_attacco": "bar_attack",
    "bar_difesa": "bar_defence",
    "bar_potenza": "bar_power",
    "bar_velocita": "bar_speed",
    "bar_tecnica": "bar_technique",
    "kik_punl": "kick_long_fk",
    "kik_punc": "kick_short_fk",
    "kik_angsx": "kick_left_corner",
    "kik_angdx": "kick_right_corner",
    "kik_rigori": "kick_penalty",
    "kik_cap": "captain",
    "str_tattica": "raw_formation",
    "tat_ruolo": "slot_role",
    "tat_x": "slot_x",
    "tat_y": "slot_y",
    "stile_bandiera": "flag_shape",
    "col_bandiera": "flag_colours",
    "maglia1": "home_kit",
    "maglia2": "away_kit",
    "str_strategia": "raw_strategy",
    "stc_numeri": "squad_numbers",
    "str_numeri": "raw_numbers",
    # --- Formation --------------------------------------------------------
    "ruoli": "roles",
    # --- Database ---------------------------------------------------------
    "gioc": "players",
    "squad_nazall": "teams",
    "squad_ml": "ml_teams",
    "squad_defml": "ml_default",
    "tattpred": "preset_formations",
    "link_euroas": "link_euro_allstar",
    "link_worldas": "link_world_allstar",
    # --- functions --------------------------------------------------------
    "codifica_carat": "Decode",
    "decodifica": "Encode",
    "NomiAllStar": "CopyAllStarNames",
    "TrovaIdMl": "ResolveMlLink",
    "CalcolaCostoGiocatore": "ComputePlayerCost",
    # --- constants --------------------------------------------------------
    "PLAYERS_NAZALL": "PLAYERS_NATIONAL_ALLSTAR",
    "TEAMS_NAZALL": "TEAMS_NATIONAL_ALLSTAR",
    "TEAMS_NAZALL_SLOTS": "TEAMS_NATIONAL_ALLSTAR_SLOTS",
}

# ---------------------------------------------------------------------------
# Locals inside the generated Load()/Save(), lifted along with the bodies.
# ---------------------------------------------------------------------------

LOCALS: dict[str, str] = {
    "fil_ctrl": "image_file",
    "fil_url": "url_file",
    "auxstr": "buf",
    "auxstr1": "buf1",
    "auxcol": "colour_buf",
    "auxnome": "name_buf",
}

# ---------------------------------------------------------------------------
# Byte offsets. Suffix conventions after the rename:
#   _A / _B / _C  a continuation, because the read would cross a sector
#                 boundary and the original seeks over the 304 bytes of
#                 header + EDC/ECC by hand
#   _COPY_n       one of several identical copies the disc genuinely holds
#   _1 .. _n      distinct records, not continuations
# ---------------------------------------------------------------------------

OFFSETS: dict[str, str] = {
    # team names, six all-caps slots
    "OFS_NOMI_SQ1": "OFS_TEAM_NAME_1",
    "OFS_NOMI_SQ1_F": "OFS_TEAM_NAME_1_END",
    "OFS_NOMI_SQ1A": "OFS_TEAM_NAME_1_A",
    "OFS_NOMI_SQ2": "OFS_TEAM_NAME_2",
    "OFS_NOMI_SQ3": "OFS_TEAM_NAME_3",
    "OFS_NOMI_SQ4": "OFS_TEAM_NAME_4",
    "OFS_NOMI_SQ5": "OFS_TEAM_NAME_5",
    "OFS_NOMI_SQ5A": "OFS_TEAM_NAME_5_A",
    "OFS_NOMI_SQ6": "OFS_TEAM_NAME_6",
    "OFS_NOMI_SQ6A": "OFS_TEAM_NAME_6_A",
    "OFS_NOMI_SQ6B": "OFS_TEAM_NAME_6_B",
    # team names, other spellings
    "OFS_NOMI_SQK": "OFS_TEAM_NAME_KANJI",
    "OFS_NOMI_SQK1": "OFS_TEAM_NAME_KANJI_A",
    "OFS_NOMI_SQ_M": "OFS_TEAM_MIXED_CASE_NAME",
    "OFS_NOMI_SQ_AB1": "OFS_TEAM_ABBREV_1",
    "OFS_NOMI_SQ_AB2": "OFS_TEAM_ABBREV_2",
    "OFS_NOMI_SQ_AB3": "OFS_TEAM_ABBREV_3",
    # the 7th and 8th name slots, Master League clubs only
    "OFS_NOMI_PML1": "OFS_ML_TEAM_NAME_7",
    "OFS_NOMI_PML2": "OFS_ML_TEAM_NAME_8",
    "OFS_NOMI_PML2A": "OFS_ML_TEAM_NAME_8_A",
    # player names
    "OFS_NOMI_G": "OFS_PLAYER_NAME",
    "OFS_NOMI_G2": "OFS_PLAYER_NAME_2",
    "OFS_NOMI_G3": "OFS_PLAYER_NAME_3",
    "OFS_NOMI_G4": "OFS_PLAYER_NAME_4",
    "OFS_NOMI_G5": "OFS_PLAYER_NAME_5",
    "OFS_NOMI_G6": "OFS_PLAYER_NAME_6",
    "OFS_NOMI_G7": "OFS_PLAYER_NAME_7",
    "OFS_NOMI_G8": "OFS_PLAYER_NAME_8",
    "OFS_NOMI_GML": "OFS_ML_PLAYER_NAME",
    "OFS_NOMI_GML2": "OFS_ML_PLAYER_NAME_2",
    "OFS_NOMI_GML3": "OFS_ML_PLAYER_NAME_3",
    # player attributes
    "OFS_CARAT_G": "OFS_PLAYER_ATTR",
    "OFS_CARAT_G1": "OFS_PLAYER_ATTR_1",
    "OFS_CARAT_G2": "OFS_PLAYER_ATTR_2",
    "OFS_CARAT_G3": "OFS_PLAYER_ATTR_3",
    "OFS_CARAT_G4": "OFS_PLAYER_ATTR_4",
    "OFS_CARAT_G5": "OFS_PLAYER_ATTR_5",
    "OFS_CARAT_G6": "OFS_PLAYER_ATTR_6",
    "OFS_CARAT_G7": "OFS_PLAYER_ATTR_7",
    "OFS_CARAT_G8": "OFS_PLAYER_ATTR_8",
    "OFS_CARAT_G9": "OFS_PLAYER_ATTR_9",
    "OFS_CARAT_GML": "OFS_ML_PLAYER_ATTR",
    "OFS_CARAT_GML1": "OFS_ML_PLAYER_ATTR_1",
    "OFS_CARAT_GML2": "OFS_ML_PLAYER_ATTR_2",
    # transfer costs
    "OFS_COSTI_NAZ": "OFS_COST_NATIONAL",
    "OFS_COSTI_NC": "OFS_COST_NC",
    # team strength bars
    "OFS_BAR": "OFS_TEAM_BARS",
    "OFS_BAR1": "OFS_TEAM_BARS_A",
    # formations and squad numbers
    "OFS_TATTICHE": "OFS_FORMATIONS",
    "OFS_TATTICHEA": "OFS_FORMATIONS_A",
    "OFS_NUMERI_NAZ": "OFS_SQUAD_NUMBERS_NATIONAL",
    "OFS_NUMERI_ML": "OFS_SQUAD_NUMBERS_ML",
    # flags: the shape table is stored five times over, the colours once
    "OFS_BANDIERE_FORMA1": "OFS_FLAG_SHAPE_COPY_1",
    "OFS_BANDIERE_FORMA2": "OFS_FLAG_SHAPE_COPY_2",
    "OFS_BANDIERE_FORMA3": "OFS_FLAG_SHAPE_COPY_3",
    "OFS_BANDIERE_FORMA4": "OFS_FLAG_SHAPE_COPY_4",
    "OFS_BANDIERE_FORMA5": "OFS_FLAG_SHAPE_COPY_5",
    "OFS_BANDIERE_COLORE": "OFS_FLAG_COLOURS",
    "OFS_BANDIERE_COLORE1": "OFS_FLAG_COLOURS_A",
    "OFS_BANDIERE_COLORE2": "OFS_FLAG_COLOURS_B",
    "OFS_BANDIERE_COLORE_SEN": "OFS_FLAG_COLOURS_SENEGAL",
    # kit preview ("anteprima maglia")
    "OFS_ANT_MAGLIE": "OFS_KIT_PREVIEW",
    "OFS_ANT_MAGLIE1": "OFS_KIT_PREVIEW_A",
    "OFS_ANT_MAGLIE2": "OFS_KIT_PREVIEW_B",
    "OFS_ANT_MAGLIE3": "OFS_KIT_PREVIEW_C",
    # already English: OFS_KICKER, OFS_LINK_ML, OFS_LINK_ML1, OFS_LINK_ML2
}

# ---------------------------------------------------------------------------
# Constant tables.
# ---------------------------------------------------------------------------

TABLES: dict[str, str] = {
    "LUN_NOMI1": "TEAM_NAME_LEN_1",
    "LUN_NOMI2": "TEAM_NAME_LEN_2",
    "LUN_NOMI3": "TEAM_NAME_LEN_3",
    "LUN_NOMI4": "TEAM_NAME_LEN_4",
    "LUN_NOMI5": "TEAM_NAME_LEN_5",
    "LUN_NOMI6": "TEAM_NAME_LEN_6",
    "LUN_NOMI_MIN": "TEAM_MIXED_CASE_NAME_LEN",
    "LUN_NOMI_ADD1": "ML_TEAM_NAME_LEN_7",
    "LUN_NOMI_ADD2": "ML_TEAM_NAME_LEN_8",
    "LUN_NOMIK": "TEAM_NAME_KANJI_LEN",
    "NC_NAZ_SEQ": "NC_TEAM_CODE",
    "NC_NAZ_QT": "NC_PLAYER_COUNT",
    # already English: ROLE_NAMES, START_LINK, TEAM_NAMES, N_ROLES
}

IDENTIFIERS: dict[str, str] = {**MEMBERS, **LOCALS, **OFFSETS, **TABLES}

# ---------------------------------------------------------------------------
# Comments carried over verbatim with the lifted function bodies.
#
# Applied before the identifier pass, longest first, and matched
# case-insensitively on the comment text only. These are phrases rather than
# tokens, so they cannot go through the \b machinery.
# ---------------------------------------------------------------------------

COMMENTS: list[tuple[str, str]] = [
    ("nomi aggiuntivi ml - 1° lotto", "ml clubs, 7th name slot"),
    ("nomi aggiuntivi ml - 2° lotto", "ml clubs, 8th name slot"),
    ("ci sono nel mezzo le vecchie nazionali nord irlanda, giamaica, uae",
     "the retired national sides -- northern ireland, jamaica, uae -- sit in between"),
    ("le nuove nazionali non sono li...", "the new national sides are elsewhere"),
    ("salvare tattiche - vedere salto", "save formations -- mind the jump"),
    ("salvare abilita - decodifica", "save attributes -- repacked into the raw blob"),
    ("salvare bandiera, forma * 5", "save flags: the shape table five times over"),
    ("anteprima maglia", "kit preview"),
    ("giocatori non contact ml", "non-contract ml players"),
    ("giocatori nazionali-alls", "national and all-star players"),
    ("tattiche predefinite", "preset formations"),
    ("forma, la 1° (sono tutte ok e uguali)",
     "shape, 1st copy (all five copies agree)"),
    ("per squadre naz/all", "for national and all-star teams"),
    ("per squadre ml", "for ml clubs"),
    ("assegnare link ml", "assign ml links"),
    ("link delle all-star", "all-star links"),
    ("link nomi all-star", "all-star name links"),
    ("caricare bar forza", "load strength bars"),
    ("salvare bar forza", "save strength bars"),
    ("caricare costi ml", "load ml costs"),
    ("salvare costi ml", "save ml costs"),
    ("salvare stringa numeri", "save the squad-number blob"),
    ("caricare stringa numeri", "load the squad-number blob"),
    ("caricare caratteristiche", "load attributes"),
    ("caricare i nomi", "load names"),
    ("caricare bandiera", "load flags"),
    ("caricare tattiche", "load formations"),
    ("caricare numeri", "load squad numbers"),
    ("caricare maglia", "load kits"),
    ("caricare kik", "load set-piece takers"),
    ("salvare kik", "save set-piece takers"),
    ("salvare i nomi -", "save names"),
    ("salvare nomi", "save names"),
    ("caricare nomi", "load names"),
    ("lotto kanji - ml", "kanji batch, ml clubs"),
    ("minuscolo - naz/alls", "mixed case, national and all-star"),
    ("minuscolo - ml", "mixed case, ml clubs"),
    ("nazionali-allstar", "national and all-star"),
    ("naz/alls", "national and all-star"),
    ("naz/all", "national and all-star"),
    ("naz-all", "national and all-star"),
    ("tutte ml", "all ml clubs"),
    ("squadre", "teams"),
    ("giocatori", "players"),
    ("attaccante", "forward"),
    ("portiere", "goalkeeper"),
    ("difensore", "defender"),
    ("centrocampista", "midfielder"),
    ("bayern monaco", "bayern munich"),
    ("jugoslavia", "yugoslavia"),
    ("francia", "france"),
    ("lotto", "batch"),
    ("default ml", "ml default"),
    ("colori", "colours"),
]


def _ordinal(n: int) -> str:
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}{ {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th') }"


def rename_comments(text: str) -> tuple[str, int]:
    """Translate the Italian comment phrases, leaving code untouched."""
    total = 0

    def fix(match: re.Match) -> str:
        nonlocal total
        body = match.group(2)
        for italian, english in COMMENTS:
            body, n = re.subn(re.escape(italian), english, body, flags=re.IGNORECASE)
            total += n
        # "1°" is the Italian ordinal; spell it the English way.
        body, n = re.subn(r"(\d+)\s*°", lambda m: _ordinal(int(m.group(1))), body)
        total += n
        return match.group(1) + body

    # Only single-line // comments; the /// doc blocks are already English.
    text = re.sub(r"(//)([^\n]*)", fix, text)
    return text, total


# Spans the lower-case rename must not enter: string literals, and anything in
# backticks. A backticked span inside a doc comment is a quotation -- usually
# of the legacy source, as in "the original declared `squadra squad_nazall[63]`"
# -- and rewriting it would make the sentence claim something untrue.
PROTECTED = re.compile(r'"(?:[^"\\]|\\.)*"' r"|`[^`\n]*`")


def _sub_all(text: str, table: dict[str, str]) -> tuple[str, int]:
    """Word-boundary rename. Longest names first, so no name eats a prefix."""
    total = 0
    for old in sorted(table, key=len, reverse=True):
        text, n = re.subn(rf"\b{re.escape(old)}\b", table[old], text)
        total += n
    return text, total


def rename_identifiers(text: str, table: dict[str, str] | None = None) -> tuple[str, int]:
    """Rename, treating SHOUTY and lower_case names differently inside strings.

    An all-caps name appearing in a string literal is almost always a label
    echoing the identifier -- {"OFS_NOMI_SQ1", we2002::OFS_NOMI_SQ1} in the
    tests -- and wants renaming with it.

    A lower-case one is usually prose or a quotation. The test suite prints
    its progress in Portuguese, and a blanket rename turned "clubes ML com
    nome" into "clubes ML com name"; a doc comment quoting the legacy
    declaration lost the very name it was quoting. So the lower-case pass
    skips everything PROTECTED matches.
    """
    table = IDENTIFIERS if table is None else table
    shouty = {k: v for k, v in table.items() if k.isupper()}
    rest = {k: v for k, v in table.items() if not k.isupper()}

    text, total = _sub_all(text, shouty)

    out = []
    at = 0
    for m in PROTECTED.finditer(text):
        chunk, n = _sub_all(text[at:m.start()], rest)
        out.append(chunk)
        out.append(m.group(0))
        total += n
        at = m.end()
    chunk, n = _sub_all(text[at:], rest)
    out.append(chunk)
    total += n
    return "".join(out), total


def rename(text: str) -> tuple[str, int, int]:
    text, comments = rename_comments(text)
    text, identifiers = rename_identifiers(text)
    return text, identifiers, comments


# Anything still matching this after a sweep is a leftover.
LEFTOVER = re.compile(
    r"\b(" + "|".join(
        sorted((re.escape(k) for k in IDENTIFIERS), key=len, reverse=True)
    ) + r")\b"
)

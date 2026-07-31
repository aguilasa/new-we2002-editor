#pragma once

#include "we2002/Types.hpp"

namespace we2002 {

/// A national team or all-star side (63 of them).
class Team {
public:
    Team();

    /// Six all-caps spellings of the team name, of differing lengths; which
    /// one the game shows depends on the screen. TEAM_NAME_LEN_1..6 give the
    /// byte length of each slot per team.
    char names[6][20]{};
    /// The mixed-case spelling -- "Bayern", not "BAYERN". The original's name
    /// for it ended in _m, for *minuscolo*, and phase 2 mis-glossed that as
    /// "long name". It is not longer, it is the same name in mixed case.
    char mixed_case_name[20]{};
    char abbreviations[3][4]{};
    /// The Japanese name, decoded to ASCII by KanjiToAscii, and the raw
    /// two-byte-per-character form it was decoded from.
    char kanji_name[20]{};
    char raw_kanji_name[40]{};

    /// The five strength bars shown on the team screen.
    char bar_attack{}, bar_defence{}, bar_power{}, bar_speed{}, bar_technique{};

    /// Set-piece takers and the captain, each an index into the squad.
    char kick_long_fk{}, kick_short_fk{}, kick_left_corner{},
        kick_right_corner{}, kick_penalty{}, captain{};

    /// The formation, as the 30-byte blob the disc stores, plus the role and
    /// pitch position of each of the ten outfield slots.
    ///
    /// 31 and not 30: Load() reads the 30 bytes and then strcpy()s them here,
    /// so the terminator needs a byte of its own. The original declared 30 and
    /// wrote the NUL one past the end, into slot_role[0]; every -O2 build with
    /// _FORTIFY_SOURCE aborts on that. Save() writes a fixed 30 bytes, so the
    /// extra byte never reaches the disc. See docs/PLAN-LINUX.md phase 6.
    char raw_formation[31]{}, slot_role[10]{}, slot_x[10]{}, slot_y[10]{};

    char flag_shape{};
    unsigned short flag_colours[16]{};
    unsigned short home_kit[16]{};
    unsigned short away_kit[16]{};

    char raw_strategy[4]{};
    SquadNumbers squad_numbers{};
};

/// A Master League club (32 of them). Same shape as Team, but with eight name
/// slots instead of six, a link table, and squad numbers stored unpacked.
class MlTeam {
public:
    MlTeam();

    char names[8][20]{};
    char mixed_case_name[20]{};
    char abbreviations[3][4]{};
    char kanji_name[20]{};
    char raw_kanji_name[40]{};

    char bar_attack{}, bar_defence{}, bar_power{}, bar_speed{}, bar_technique{};

    char kick_long_fk{}, kick_short_fk{}, kick_left_corner{},
        kick_right_corner{}, kick_penalty{}, captain{};

    /// 31 for the same reason as Team::raw_formation.
    char raw_formation[31]{}, slot_role[10]{}, slot_x[10]{}, slot_y[10]{};

    char flag_shape{};
    unsigned short flag_colours[16]{};
    unsigned short home_kit[16]{};
    unsigned short away_kit[16]{};

    char raw_numbers[23]{};
    unsigned char link[46]{};
    char raw_strategy[4]{};
};

/// One of the 16 preset formations.
class Formation {
public:
    Formation();

    char name[7]{};
    char roles[11]{}, x[10]{}, y[10]{};
};

}  // namespace we2002

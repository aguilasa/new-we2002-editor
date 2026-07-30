#pragma once

#include "we2002/Types.hpp"

namespace we2002 {

// Member names stay Italian; see the note in Player.hpp.
//   nomi = names          nome_m = long name   nomi_a = abbreviations
//   nomek / nomekanji = Shift-JIS name, decoded / raw
//   bar_* = the five strength bars shown on the team screen
//   kik_* = set-piece takers (punl/punc = long/short free kick,
//           angsx/angdx = left/right corner, rigori = penalties, cap = captain)
//   tattica = formation    tat_ruolo/x/y = role and pitch position per slot
//   bandiera = flag        maglia1/2 = home/away kit colours
//   strategia = strategy   numeri = squad numbers

/// A national team or all-star side (63 of them).
class Team {
public:
    Team();

    char nomi[6][20]{};
    char nome_m[20]{};
    char nomi_a[3][4]{};
    char nomek[20]{};
    char nomekanji[40]{};

    char bar_attacco{}, bar_difesa{}, bar_potenza{}, bar_velocita{}, bar_tecnica{};

    char kik_punl{}, kik_punc{}, kik_angsx{}, kik_angdx{}, kik_rigori{}, kik_cap{};

    char str_tattica[30]{}, tat_ruolo[10]{}, tat_x[10]{}, tat_y[10]{};

    char stile_bandiera{};
    unsigned short col_bandiera[16]{};
    unsigned short maglia1[16]{};
    unsigned short maglia2[16]{};

    char str_strategia[4]{};
    SquadNumbers stc_numeri{};
};

/// A Master League club (32 of them). Same shape as Team, but with eight name
/// slots instead of six, a link table, and squad numbers stored unpacked.
class MlTeam {
public:
    MlTeam();

    char nomi[8][20]{};
    char nome_m[20]{};
    char nomi_a[3][4]{};
    char nomek[20]{};
    char nomekanji[40]{};

    char bar_attacco{}, bar_difesa{}, bar_potenza{}, bar_velocita{}, bar_tecnica{};

    char kik_punl{}, kik_punc{}, kik_angsx{}, kik_angdx{}, kik_rigori{}, kik_cap{};

    char str_tattica[30]{}, tat_ruolo[10]{}, tat_x[10]{}, tat_y[10]{};

    char stile_bandiera{};
    unsigned short col_bandiera[16]{};
    unsigned short maglia1[16]{};
    unsigned short maglia2[16]{};

    char str_numeri[23]{};
    unsigned char link[46]{};
    char str_strategia[4]{};
};

/// One of the 16 preset formations.
class Formation {
public:
    Formation();

    char nome[7]{};
    char ruoli[11]{}, x[10]{}, y[10]{};
};

}  // namespace we2002

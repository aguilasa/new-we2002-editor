#pragma once

#include <map>
#include <string>

namespace we2002 {

// NOTE ON NAMING
// Class and file names are anglicised, but *member* names stay in the
// original Italian. During the port the golden tests compare this code
// byte-for-byte against legacy/mfc/, and keeping the field names identical
// keeps that comparison readable. Renaming them is cheap to do later and
// pointless to do now.
//
//   attacco = attack      difesa = defence     forza = strength
//   resistenza = stamina  velocita = speed     accel = acceleration
//   passaggio = passing   pot_tiro = shot power
//   prec_tiro = shot accuracy                  salto = jump
//   testa = heading       tecnica = technique  effetto = swerve
//   aggress = aggression  riflessi = reflexes  fuori_ruolo = out of position
//   posizione = position  col_pelle = skin colour
//   stile_capelli = hair style                 col_capelli = hair colour
//   stile_barba = beard style                  col_barba = beard colour
//   altezza = height      corporatura = build  eta = age
//   scarpe = boots        piede = footedness   numero = shirt number
//   costo = transfer cost

/// A player as scraped from SoFIFA, before conversion to WE attributes.
class FifaPlayer {
public:
    int UpdatePlayerFromURL(const std::string& link);
    void SetPlayerToDummy();

    std::string name;
    std::string positions;
    int number[2]{};  // 0 = national team, 1 = club
    int weight{};
    int height{};
    int age{};
    char foot{};
    int weakFootSkill{};
    int skillMoves{};
    std::string offWeight;
    std::string defWeight;
    int* attributeValues{nullptr};
};

/// A player as stored on the CD image.
class Player {
public:
    Player();

    /// Unpack `str_carat` (12 packed bytes off the disc) into the members.
    void codifica_carat();
    /// Repack the members back into `str_carat`.
    void decodifica();

    char url[500]{};
    char nome[11]{};
    int posizione{};
    int col_pelle{};
    int stile_capelli{};
    int col_capelli{};
    int stile_barba{};
    int col_barba{};
    int altezza{};
    int corporatura{};
    int eta{};
    int scarpe{};
    int piede{};
    int attacco{};
    int difesa{};
    int forza{};
    int resistenza{};
    int velocita{};
    int accel{};
    int passaggio{};
    int pot_tiro{};
    int prec_tiro{};
    int salto{};
    int testa{};
    int tecnica{};
    int dribbling{};
    int effetto{};
    int aggress{};
    int riflessi{};
    int fuori_ruolo{};
    int numero{};
    int costo{};

    /// The 12 raw bytes as they appear on the disc.
    char str_carat[12]{};
};

}  // namespace we2002

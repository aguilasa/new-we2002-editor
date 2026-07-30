#pragma once

#include <map>
#include <string>

namespace we2002 {

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

    /// Unpack `raw_attributes` (12 packed bytes off the disc) into the members.
    ///
    /// The original spelled this pair backwards: its decoder was called
    /// "codifica_carat" and its encoder "decodifica". Decode/Encode here,
    /// matching the direction of travel.
    void Decode();
    /// Repack the members back into `raw_attributes`.
    void Encode();

    char url[500]{};
    char name[11]{};
    int position{};
    int skin_colour{};
    int hair_style{};
    int hair_colour{};
    int beard_style{};
    int beard_colour{};
    int height{};
    int build{};
    int age{};
    int boots{};
    int foot{};
    int attack{};
    int defence{};
    int strength{};
    int stamina{};
    int speed{};
    int acceleration{};
    int passing{};
    int shot_power{};
    int shot_accuracy{};
    int jump{};
    int heading{};
    int technique{};
    int dribbling{};
    int swerve{};
    int aggression{};
    int reflexes{};
    int out_of_position{};
    int number{};
    int cost{};

    /// The 12 raw bytes as they appear on the disc.
    char raw_attributes[12]{};
};

}  // namespace we2002

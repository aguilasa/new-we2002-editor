#pragma once

#include <map>
#include <string>
#include <vector>

namespace we2002 {

class SofifaRules;

/// A player as scraped from SoFIFA, before conversion to WE attributes.
class FifaPlayer {
public:
    /// Fetch and parse one SoFIFA player page. Returns 1 on success and 0 on
    /// anything else -- a URL that is not SoFIFA's, an empty response, or a
    /// page whose markup no longer matches. See Sofifa.hpp on why the last of
    /// those is now the usual outcome.
    ///
    /// `rules` supplies the attribute layout: which fields the page carries,
    /// in what order, and where each lands in `attribute_values`. The original
    /// reached for four globals here instead.
    int UpdatePlayerFromURL(const std::string& link, const SofifaRules& rules);

    /// A neutral stand-in, for filling out a club squad without a real page.
    /// Every attribute is 1, which converts to the lowest WE value.
    void SetPlayerToDummy(const SofifaRules& rules);

    std::string name;
    std::string positions;
    int number[2]{-1, -1};  // 0 = national team, 1 = club
    int weight{};
    int height{};
    int age{};
    char foot{};
    int weak_foot_skill{};
    int skill_moves{};
    std::string offensive_work_rate;
    std::string defensive_work_rate;
    /// One entry per field the rules file lists, in that file's order. The
    /// original carried a bare `int*` and delete[]/new[]'d it on every fetch.
    std::vector<int> attribute_values;
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

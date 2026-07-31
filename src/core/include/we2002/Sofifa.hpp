// The SoFIFA import: fetch a player's page, and convert FIFA's 0..99
// attributes into WE2002's 12..19 ones.
//
// This is the fork's addition, not Moriero's -- thyddralisk bolted it onto the
// 2002 editor in 2015. It lives in the core because it is data conversion, not
// UI, and because the app must stay free of parsing logic.
//
// Two things are worth knowing before relying on it.
//
// The scraper targets the SoFIFA of 2015: `http://sofifa.com/`, a specific
// nesting of <li class="active"> and "row attribute" markup, and the FIFA 15
// attribute set, which the rules file also hard-codes. The site has been
// rebuilt several times since; the parser is ported as it was, and against
// today's SoFIFA it will simply fail to find its anchors and return 0. Fixing
// that is a separate job from porting it.
//
// The conversion itself is table-driven, from two files read at startup:
// "SOFIFA attributes.txt" naming FIFA's fields in page order, and "WE
// attributes conversion rules.txt" giving, per WE attribute and per position,
// how to aggregate those fields and where to cut the result into 12..19.

#pragma once

#include <filesystem>
#include <map>
#include <string>
#include <vector>

#include "we2002/Database.hpp"
#include "we2002/Player.hpp"

namespace we2002 {

/// One WE attribute's recipe for one position group.
struct FieldConversion {
    /// 0 = weighted average, 1 = maximum, -1 = minimum. -999 means the rules
    /// file named something else, in which case no aggregation runs.
    int aggregation{-999};
    int field_count{0};
    int field_index[3]{};
    float field_weight[3]{};

    /// An extra term from one of the non-numeric fields: 1 = offensive work
    /// rate, 2 = defensive work rate, 3 = skill moves, 0 = none.
    int discrete_field{0};
    std::map<std::string, float> discrete_values;
    float discrete_weight{0};

    /// Seven cut points turning the aggregate into 12..19.
    float upper_bound[7]{};

    int Value(const FifaPlayer& player) const;
};

/// Everything the two rule files describe.
class SofifaRules {
public:
    /// Read "SOFIFA attributes.txt". Returns false if it cannot be opened.
    bool LoadFields(const std::filesystem::path& path);
    /// Read "WE attributes conversion rules.txt". Must run after LoadFields:
    /// the rules refer to fields by group and name, and the index they resolve
    /// to comes from the field file. Returns false if it cannot be opened.
    bool LoadConversions(const std::filesystem::path& path);

    /// How many attributes one player's page yields, for `version`.
    int FieldCount(const std::string& version) const;
    /// Group names in page order, and the fields within each group.
    const std::vector<std::string>& Groups(const std::string& version) const;
    const std::vector<std::string>& GroupFields(const std::string& version,
                                                const std::string& group) const;
    int FieldIndex(const std::string& version, const std::string& group,
                   const std::string& field) const;

    /// WE position 0..7 (GK, CB, SB, DH, SH, OH, CF, WG) for a FIFA position
    /// abbreviation. Unknown abbreviations map to 0, as in the original.
    int PositionFromFifa(const std::string& fifa_position) const;
    /// The converted value of one WE attribute, e.g. "Offense".
    int Value(const std::string& we_attribute, const FifaPlayer& player) const;

    bool ready() const { return !field_count_.empty(); }

private:
    std::map<std::string, int> field_count_;
    std::map<std::string, std::vector<std::string>> groups_;
    std::map<std::string, std::map<std::string, std::vector<std::string>>>
        group_fields_;
    std::map<std::string, std::map<std::string, std::map<std::string, int>>>
        field_index_;
    std::map<std::string, int> fifa_to_we_position_;
    /// WE attribute -> position (0..7) -> recipe.
    std::map<std::string, std::map<int, FieldConversion>> conversions_;
};

/// Copy a scraped player onto a disc player. The three flags are the
/// edit-options checkboxes.
void ApplyFifaToPlayer(Database& db, int player_index, const FifaPlayer& fifa,
                       const SofifaRules& rules, bool edit_name, bool edit_look,
                       bool edit_position_and_skills);

/// Put the shirt numbers SoFIFA reported into the squad lists that hold them:
/// `national` into the player's national squad slot, `club` into whichever
/// Master League club links to them. Either may be -1 for "not reported".
void SetPlayerNumbers(Database& db, int player_index, int national, int club);

/// Fetch a URL over HTTP and return the body, or "" on any failure.
std::string FetchUrl(const std::string& url);

}  // namespace we2002

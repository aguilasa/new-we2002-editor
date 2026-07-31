// Port of the SoFIFA import: legacy/mfc/giocatore.cpp's fifa_player methods
// and editFromFIFA, edDlg.cpp's carica_SOFIFAFields /
// carica_SOFIFAConversionRules / setPlayerNo, and myiotxt.cpp's curl wrapper
// and string helpers.

#include "we2002/Sofifa.hpp"

#include <curl/curl.h>

#include <algorithm>
#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "we2002/Tables.hpp"
#include "we2002/Types.hpp"

namespace we2002 {
namespace {

/// The only FIFA edition the scraper and the rules file know about. It was
/// hard-coded in three places in the original; it is hard-coded once here.
const char* const FIFA_VERSION = "15";
/// SetPlayerToDummy asked for a different key than everything else. Kept,
/// because a rules file may well define only one of the two and the original's
/// behaviour was to fall back to zero fields rather than to the "15" set.
const char* const DUMMY_VERSION = "15w";

const std::vector<std::string>& EmptyList() {
    static const std::vector<std::string> empty;
    return empty;
}

std::vector<std::string> Split(const std::string& s, char delim) {
    std::vector<std::string> out;
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, delim)) {
        out.push_back(item);
    }
    return out;
}

/// Collect the text that sits *between* markup: split on `open`, and throw
/// away everything up to the next `close`. myiotxt.cpp's
/// splitOutsideDelimitingChars, used to pull the contents out of a run of
/// <tag>value</tag>.
std::vector<std::string> SplitOutsideDelimiters(const std::string& s, char open,
                                                char close) {
    std::vector<std::string> out;
    std::stringstream ss(s);
    std::string item;
    while (std::getline(ss, item, open)) {
        out.push_back(item);
        std::getline(ss, item, close);
    }
    return out;
}

std::string Trim(const std::string& s) {
    std::size_t first = 0;
    while (first < s.size() && (s[first] == ' ' || s[first] == '\t')) {
        ++first;
    }
    std::size_t last = s.size();
    while (last > first && (s[last - 1] == ' ' || s[last - 1] == '\t')) {
        --last;
    }
    return s.substr(first, last - first);
}

/// stoi that returns 0 rather than throwing. The original called stoi on
/// whatever the page happened to contain; on a page that has since changed
/// shape that is an uncaught exception, so it is swallowed here.
int ToInt(const std::string& s) {
    try {
        return std::stoi(s);
    } catch (...) {
        return 0;
    }
}

float ToFloat(const std::string& s) {
    try {
        return std::stof(s);
    } catch (...) {
        return 0.0F;
    }
}

std::size_t WriteToString(void* data, std::size_t size, std::size_t nmemb,
                          void* user) {
    auto* out = static_cast<std::string*>(user);
    out->append(static_cast<char*>(data), size * nmemb);
    return size * nmemb;
}

}  // namespace

std::string FetchUrl(const std::string& url) {
    std::string body;
    CURL* curl = curl_easy_init();
    if (curl == nullptr) {
        return body;
    }
    curl_easy_setopt(curl, CURLOPT_URL, url.c_str());
    curl_easy_setopt(curl, CURLOPT_WRITEFUNCTION, &WriteToString);
    curl_easy_setopt(curl, CURLOPT_WRITEDATA, &body);
    curl_easy_setopt(curl, CURLOPT_NOPROGRESS, 1L);
    curl_easy_setopt(curl, CURLOPT_FOLLOWLOCATION, 1L);
    curl_easy_setopt(curl, CURLOPT_TIMEOUT, 30L);
    if (curl_easy_perform(curl) != CURLE_OK) {
        body.clear();
    }
    curl_easy_cleanup(curl);
    return body;
}

// ---------------------------------------------------------------------------
// FieldConversion
// ---------------------------------------------------------------------------

int FieldConversion::Value(const FifaPlayer& player) const {
    const auto at = [&player](int index) -> float {
        if (index < 0 || index >= static_cast<int>(player.attribute_values.size())) {
            return 0;
        }
        return static_cast<float>(player.attribute_values[index]);
    };

    float value = 0;
    switch (aggregation) {
        case 0: {
            float weight_sum = 0;
            for (int k = 0; k < field_count; ++k) {
                value += at(field_index[k]) * field_weight[k];
                weight_sum += field_weight[k];
            }
            if (weight_sum != 0) {
                value /= weight_sum;
            }
            break;
        }
        case 1:
            for (int k = 0; k < field_count; ++k) {
                value = std::max(value, at(field_index[k]));
            }
            break;
        case -1:
            value = 100;
            for (int k = 0; k < field_count; ++k) {
                value = std::min(value, at(field_index[k]));
            }
            break;
        default:
            // The rules file named an aggregation we do not implement. The
            // original left `resVal` uninitialised here and read it below;
            // zero at least makes the result reproducible.
            break;
    }

    if (discrete_field > 0) {
        std::string key;
        switch (discrete_field) {
            case 1: key = player.offensive_work_rate; break;
            case 2: key = player.defensive_work_rate; break;
            default: key = std::to_string(player.skill_moves); break;
        }
        const auto it = discrete_values.find(key);
        if (it != discrete_values.end()) {
            value += it->second * discrete_weight;
        }
    }

    for (int i = 0; i < 7; ++i) {
        if (value <= upper_bound[i]) {
            return 12 + i;
        }
    }
    return 19;
}

// ---------------------------------------------------------------------------
// SofifaRules
// ---------------------------------------------------------------------------

bool SofifaRules::LoadFields(const std::filesystem::path& path) {
    field_count_.clear();
    groups_.clear();
    group_fields_.clear();
    field_index_.clear();

    std::ifstream in(path);
    if (!in) {
        return false;
    }

    std::string line;
    std::getline(in, line);  // header: VERSION;GROUP;ATTRIBUTE
    while (std::getline(in, line) && !line.empty()) {
        const std::vector<std::string> fields = Split(line, ';');
        if (fields.size() < 3) {
            continue;
        }
        const std::string& version = fields[0];
        const std::string& group = fields[1];
        const std::string& attribute = fields[2];

        if (group_fields_[version].count(group) == 0) {
            if (groups_.count(version) == 0) {
                field_count_[version] = 0;
                groups_[version] = {};
            }
            groups_[version].push_back(group);
            group_fields_[version][group] = {};
        }
        group_fields_[version][group].push_back(attribute);
        // The index is the position in the whole flattened list, which is the
        // order the page presents them in.
        field_index_[version][group][attribute] = field_count_[version];
        ++field_count_[version];
    }
    return true;
}

int SofifaRules::FieldCount(const std::string& version) const {
    const auto it = field_count_.find(version);
    return (it == field_count_.end()) ? 0 : it->second;
}

const std::vector<std::string>& SofifaRules::Groups(
    const std::string& version) const {
    const auto it = groups_.find(version);
    return (it == groups_.end()) ? EmptyList() : it->second;
}

const std::vector<std::string>& SofifaRules::GroupFields(
    const std::string& version, const std::string& group) const {
    const auto v = group_fields_.find(version);
    if (v == group_fields_.end()) {
        return EmptyList();
    }
    const auto g = v->second.find(group);
    return (g == v->second.end()) ? EmptyList() : g->second;
}

int SofifaRules::FieldIndex(const std::string& version, const std::string& group,
                            const std::string& field) const {
    const auto v = field_index_.find(version);
    if (v == field_index_.end()) {
        return -1;
    }
    const auto g = v->second.find(group);
    if (g == v->second.end()) {
        return -1;
    }
    const auto f = g->second.find(field);
    return (f == g->second.end()) ? -1 : f->second;
}

int SofifaRules::PositionFromFifa(const std::string& fifa_position) const {
    const auto it = fifa_to_we_position_.find(fifa_position);
    return (it == fifa_to_we_position_.end()) ? 0 : it->second;
}

int SofifaRules::Value(const std::string& we_attribute,
                       const FifaPlayer& player) const {
    const auto fn = conversions_.find(we_attribute);
    if (fn == conversions_.end()) {
        return 12;
    }
    // A player's first listed position picks which recipe applies.
    std::string first = player.positions;
    const std::size_t comma = first.find(',');
    if (comma != std::string::npos) {
        first = first.substr(0, comma);
    }
    const auto sub = fn->second.find(PositionFromFifa(first));
    return (sub == fn->second.end()) ? 12 : sub->second.Value(player);
}

bool SofifaRules::LoadConversions(const std::filesystem::path& path) {
    static const char* const kWePositions[8] = {"GK", "CB", "SB", "DH",
                                                "SH", "OH", "CF", "WG"};
    std::map<std::string, int> we_position;
    for (int i = 0; i < 8; ++i) {
        we_position[kWePositions[i]] = i;
    }

    fifa_to_we_position_.clear();
    conversions_.clear();

    std::ifstream in(path);
    if (!in) {
        return false;
    }

    // The file is line-oriented and read strictly forwards; every loop below
    // mirrors one in carica_SOFIFAConversionRules. The eof guards are new --
    // the original would spin forever on a truncated file.
    std::string line;
    const auto next = [&in, &line]() -> bool {
        return static_cast<bool>(std::getline(in, line));
    };
    const auto seek_to = [&next, &line](const char* marker) -> bool {
        while (line != marker) {
            if (!next()) {
                return false;
            }
        }
        return true;
    };

    if (!next() || !seek_to("Position:{")) {
        return false;
    }
    // "WE:fifa1,fifa2,..." until "}"
    if (!next()) {
        return false;
    }
    while (line != "}") {
        const std::vector<std::string> mapping = Split(line, ':');
        if (mapping.size() >= 2) {
            for (const std::string& fifa : Split(mapping[1], ',')) {
                fifa_to_we_position_[fifa] = we_position[mapping[0]];
            }
        }
        if (!next()) {
            return false;
        }
    }

    if (!seek_to("$FIELDS:{") || !next()) {
        return false;
    }

    while (!line.empty()) {
        const std::string we_attribute = line.substr(0, line.find(':'));
        if (!next()) {
            break;
        }
        std::map<int, FieldConversion> per_position;

        while (line != "}") {
            const std::vector<std::string> positions =
                Split(line.substr(0, line.find(':')), ',');
            FieldConversion conv;

            if (!next() || !next()) {  // "Function:{", "Aggregation:{"
                return false;
            }
            if (!next()) {  // type:Avg / Max / Min
                return false;
            }
            const std::string type = line.substr(line.find(':') + 1, line.size() - 5);
            if (type == "Avg") {
                conv.aggregation = 0;
            } else if (type == "Max") {
                conv.aggregation = 1;
            } else if (type == "Min") {
                conv.aggregation = -1;
            }

            // Up to three source fields, named "<group>/<attribute>".
            for (int k = 0; k < 3; ++k) {
                if (!next()) {
                    return false;
                }
                if (line.size() > 8) {
                    const std::string group =
                        line.substr(line.find(':') + 1, line.find('/') - 7);
                    const std::string attribute = line.substr(line.find('/') + 1);
                    conv.field_index[conv.field_count] =
                        FieldIndex(FIFA_VERSION, group, attribute);
                    ++conv.field_count;
                }
            }
            for (int k = 0; k < 3; ++k) {
                if (!next()) {
                    return false;
                }
                if (line.size() > 8) {
                    conv.field_weight[k] = ToFloat(line.substr(line.find(':') + 1));
                }
            }

            if (!next() || !next()) {  // end Aggregation, "Discrete:{"
                return false;
            }
            if (!next()) {
                return false;
            }
            const std::string discrete = line.substr(line.find(':') + 1);
            if (discrete == "Offensive work rate") {
                conv.discrete_field = 1;
            } else if (discrete == "Defensive work rate") {
                conv.discrete_field = 2;
            } else if (discrete == "Skill moves") {
                conv.discrete_field = 3;
            }

            if (!next() || !next()) {  // "Values:{", first value
                return false;
            }
            while (line != "}") {
                const std::vector<std::string> entry = Split(line, ':');
                if (entry.size() >= 2) {
                    conv.discrete_values[entry[0]] = ToFloat(entry[1]);
                }
                if (!next()) {
                    return false;
                }
            }
            if (!next()) {
                return false;
            }
            if (line.size() > 7) {
                conv.discrete_weight = ToFloat(line.substr(line.find(':') + 1));
            }
            if (!next() || !next()) {  // end Discrete, end Function
                return false;
            }

            if (!next() || !next()) {  // "Range:{", first bound
                return false;
            }
            int bound = 0;
            while (line != "}") {
                const std::string value = line.substr(line.find(':') + 1);
                if (value != "-" && bound < 7) {
                    conv.upper_bound[bound] = ToFloat(value);
                    ++bound;
                }
                if (!next()) {
                    return false;
                }
            }

            if (!positions.empty() && positions[0] == "ALL") {
                for (int p = 0; p < 8; ++p) {
                    per_position[p] = conv;
                }
            } else {
                for (const std::string& p : positions) {
                    per_position[we_position[p]] = conv;
                }
            }

            if (!next() || !next()) {  // close sub-function, next sub-function
                return false;
            }
        }

        conversions_[we_attribute] = per_position;
        if (!next()) {  // blank line between attributes
            break;
        }
        if (!next()) {  // first line of the next attribute
            break;
        }
    }

    return true;
}

// ---------------------------------------------------------------------------
// FifaPlayer
// ---------------------------------------------------------------------------

void FifaPlayer::SetPlayerToDummy(const SofifaRules& rules) {
    name = "Dummy";
    positions = "CB";
    // Only clubs hold dummy players, so the national number is left alone.
    number[1] = 50;
    weight = 70;
    height = 170;
    age = 16;
    foot = 'R';
    weak_foot_skill = 1;
    skill_moves = 1;
    offensive_work_rate = "Medium";
    defensive_work_rate = "Medium";
    attribute_values.assign(rules.FieldCount(DUMMY_VERSION), 1);
}

int FifaPlayer::UpdatePlayerFromURL(const std::string& link,
                                    const SofifaRules& rules) {
    if (link.find("http://sofifa.com/") == std::string::npos) {
        return 0;
    }
    const int field_count = rules.FieldCount(FIFA_VERSION);
    if (field_count == 0) {
        return 0;
    }

    const std::vector<std::string> page = Split(FetchUrl(link), '\n');
    if (page.empty()) {
        return 0;
    }
    attribute_values.assign(field_count, 0);

    // The page is walked strictly forwards, anchor by anchor. `advance` is the
    // original's `do { r++; line = arr[r]; } while (not found)` with a bound
    // on r, so a page that no longer contains an anchor fails instead of
    // running off the end of the vector.
    std::size_t r = 0;
    const auto advance = [&page, &r](const char* needle) -> bool {
        while (++r < page.size()) {
            if (page[r].find(needle) != std::string::npos) {
                return true;
            }
        }
        return false;
    };

    // NAME
    const std::string name_anchor =
        "<li class=\"active\"><a href=\"javascript:void(0);\">";
    if (!advance(name_anchor.c_str())) {
        return 0;
    }
    {
        const std::size_t start = page[r].find(name_anchor) + name_anchor.size();
        const std::size_t end = page[r].size() - std::strlen("</a></li>");
        if (end <= start) {
            return 0;
        }
        name = Trim(page[r].substr(start, end - start));
    }

    // AGE / HEIGHT / WEIGHT all live in one <span>, space-separated.
    if (!advance("<span class=")) {
        return 0;
    }
    std::vector<std::string> outside = SplitOutsideDelimiters(page[r], '<', '>');
    if (outside.size() < 2) {
        return 0;
    }
    std::vector<std::string> words = Split(Trim(outside[outside.size() - 2]), ' ');

    std::size_t w = 0;
    const auto find_word = [&words, &w](const char* needle) -> bool {
        while (w < words.size()) {
            if (words[w].find(needle) != std::string::npos) {
                return true;
            }
            ++w;
        }
        return false;
    };
    if (!find_word("Age") || w + 1 >= words.size()) {
        return 0;
    }
    age = ToInt(words[w + 1]);
    ++w;
    if (!find_word("cm")) {
        return 0;
    }
    height = ToInt(words[w].substr(0, words[w].find("cm")));
    ++w;
    if (!find_word("kg")) {
        return 0;
    }
    weight = ToInt(words[w].substr(0, words[w].find("kg")));

    // POSITIONS: each <span class="pos ..."> is followed by its abbreviation.
    {
        const std::vector<std::string> by_gt = Split(page[r], '>');
        std::string list;
        for (std::size_t i = 0; i < by_gt.size(); ++i) {
            if (by_gt[i].find("<span class=\"pos ") != std::string::npos &&
                i + 1 < outside.size()) {
                list.append(",").append(outside[i + 1]);
            }
        }
        if (!list.empty()) {
            list.erase(list.begin());
        }
        positions = list;
    }

    if (!advance("Preferred Foot")) {
        return 0;
    }
    foot = (page[r].find("Left") != std::string::npos) ? 'L' : 'R';

    // Both of these are a star rating in the next line's title= attribute.
    const auto star_rating = [&page, &r, &advance](const char* anchor) -> int {
        if (!advance(anchor) || r + 1 >= page.size()) {
            return 0;
        }
        ++r;
        const std::size_t at = page[r].find("title=");
        if (at == std::string::npos || at + 7 >= page[r].size()) {
            return 0;
        }
        return ToInt(page[r].substr(at + 7, 1));
    };
    weak_foot_skill = star_rating("Weak Foot");
    skill_moves = star_rating("Skill Moves");

    if (!advance("Work Rate")) {
        return 0;
    }
    outside = SplitOutsideDelimiters(page[r], '<', '>');
    if (outside.size() >= 2) {
        const std::vector<std::string> rates = Split(outside[1], '/');
        if (rates.size() >= 2) {
            offensive_work_rate = Trim(rates[0]);
            defensive_work_rate = Trim(rates[1]);
        }
    }

    // SHIRT NUMBER. The page carries up to two -- a club number and a national
    // one -- in identically shaped blocks, so the original ran the same search
    // twice in a row. Kept as a loop of two rather than two copies.
    number[0] = -1;
    number[1] = -1;
    const char* const CHART = "<div id=\"chartdiv\"></div>";
    for (int pass = 0; pass < 2; ++pass) {
        if (r >= page.size() || page[r].find(CHART) != std::string::npos) {
            break;
        }
        bool found = false;
        while (++r < page.size()) {
            if (page[r].find("Player Number") != std::string::npos) {
                found = true;
                break;
            }
            if (page[r].find(CHART) != std::string::npos) {
                break;
            }
        }
        if (!found || r < 8) {
            break;
        }
        // The block's header sits eight lines back; "Free Agents" there means
        // the number belongs to nobody.
        r -= 8;
        if (page[r].find("Free Agents") != std::string::npos) {
            continue;
        }
        r += 7;
        if (r >= page.size()) {
            break;
        }
        const std::vector<std::string> cell =
            SplitOutsideDelimiters(page[r], '<', '>');
        const int value = (cell.size() >= 2) ? ToInt(cell[1]) : 0;

        // Seven lines on again: a contract date means this was the club block.
        r += 7;
        if (r >= page.size()) {
            break;
        }
        if (page[r].find("Contract Valid Until") == std::string::npos) {
            number[0] = value;
        } else {
            number[1] = value;
        }
        r -= 6;
    }

    // The attribute table: groups in order, fields in order within a group.
    if (!advance("row attribute")) {
        return 0;
    }
    for (const std::string& group : rules.Groups(FIFA_VERSION)) {
        if (!advance(group.c_str())) {
            return 0;
        }
        for (const std::string& field : rules.GroupFields(FIFA_VERSION, group)) {
            if (!advance(field.c_str())) {
                return 0;
            }
            const std::vector<std::string> cell =
                SplitOutsideDelimiters(page[r], '<', '>');
            const int index = rules.FieldIndex(FIFA_VERSION, group, field);
            if (index >= 0 && index < field_count && cell.size() >= 2) {
                attribute_values[index] = ToInt(cell[1]);
            }
        }
    }

    return 1;
}

// ---------------------------------------------------------------------------
// Applying a scraped player
// ---------------------------------------------------------------------------

void ApplyFifaToPlayer(Database& db, int player_index, const FifaPlayer& fifa,
                       const SofifaRules& rules, bool edit_name, bool edit_look,
                       bool edit_position_and_skills) {
    Player& p = db.players[player_index];

    if (edit_name) {
        // SoFIFA gives "L. Messi"; the disc has room for ten characters and
        // the game shows the surname, so anything up to the last ". " goes.
        std::string text = fifa.name;
        const std::size_t dot = text.rfind('.');
        if (dot != std::string::npos && dot + 2 <= text.size()) {
            text = text.substr(dot + 2);
        }
        std::memset(p.name, 0, sizeof(p.name));
        std::memcpy(p.name, text.data(), std::min<std::size_t>(text.size(), 10));
    }

    if (edit_position_and_skills) {
        const std::vector<std::string> positions = Split(fifa.positions, ',');
        if (!positions.empty()) {
            p.position = rules.PositionFromFifa(positions[0]);
        }
        // A player who covers more than one WE position is flagged as able to
        // play out of position.
        bool covered[8] = {};
        for (const std::string& pos : positions) {
            covered[rules.PositionFromFifa(pos)] = true;
        }
        int count = 0;
        for (bool c : covered) {
            count += c ? 1 : 0;
        }
        p.out_of_position = (count > 1) ? 1 : 0;
    }

    if (edit_look) {
        p.height = fifa.height;
        // Build from how heavy the player is for their height. The eight
        // brackets are the original's, and so is the 1..8 range -- note the
        // build combo is indexed from 0, so this never selects "A".
        const int ratio = fifa.weight - (fifa.height - 100);
        if (ratio <= -11) {
            p.build = 1;
        } else if (ratio <= -7) {
            p.build = 2;
        } else if (ratio <= -3) {
            p.build = 3;
        } else if (ratio <= 2) {
            p.build = 4;
        } else if (ratio <= 6) {
            p.build = 5;
        } else if (ratio <= 10) {
            p.build = 6;
        } else if (ratio <= 14) {
            p.build = 7;
        } else {
            p.build = 8;
        }
        p.age = fifa.age;
        // A five-star weak foot is two-footed; otherwise take the strong one.
        p.foot = (fifa.weak_foot_skill == 5) ? 2 : ((fifa.foot == 'L') ? 1 : 0);
    }

    if (edit_position_and_skills) {
        p.attack = rules.Value("Offense", fifa);
        p.defence = rules.Value("Defense", fifa);
        p.strength = rules.Value("Body Balance", fifa);
        p.stamina = rules.Value("Stamina", fifa);
        p.speed = rules.Value("Speed", fifa);
        p.acceleration = rules.Value("Acceleration", fifa);
        p.passing = rules.Value("Pass", fifa);
        p.shot_power = rules.Value("Shoot Power", fifa);
        p.shot_accuracy = rules.Value("Shoot Accuracy", fifa);
        p.jump = rules.Value("Jump", fifa);
        p.heading = rules.Value("Head accuracy", fifa);
        p.technique = rules.Value("Tecnique", fifa);
        p.dribbling = rules.Value("Dribble", fifa);
        p.swerve = rules.Value("Curve", fifa);
        p.aggression = rules.Value("Aggressive", fifa);
        p.reflexes = rules.Value("Response", fifa);

        // DIVERGENCE from the original, deliberate. editFromFIFA ended with
        //     costo = CalcolaCostoGiocatore(i);
        // where `i` was a loop counter left over from the position scan --
        // always 8 by the time control reached here. Every imported player was
        // therefore priced as player 8. This uses the player's own index,
        // which is plainly what was meant; the "upd. player cost" button
        // recomputes the same value for everybody anyway.
        p.cost = ComputePlayerCost(db, player_index);
    }
}

void SetPlayerNumbers(Database& db, int player_index, int national, int club) {
    if (player_index >= PLAYERS_NC) {
        const int team = (player_index - PLAYERS_NC) / 23;
        const int slot = (player_index - PLAYERS_NC) % 23;
        SetSquadNumberAt(db.teams[team].squad_numbers, slot,
                         static_cast<std::uint32_t>(national - 1));
    }
    // A player can only be in one club squad, so the search stops at the first
    // link that points at them.
    for (int c = 0; c < TEAMS_ML; ++c) {
        for (int slot = 0; slot < 23; ++slot) {
            if (ResolveMlLink(&db.ml_teams[c].link[slot * 2]) == player_index) {
                db.ml_teams[c].raw_numbers[slot] = static_cast<char>(club - 1);
                return;
            }
        }
    }
}

}  // namespace we2002

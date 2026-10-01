// Headless driver for the phase 3 golden tests.
//
// The point of these tests is to compare, byte for byte, what the original
// ed.exe writes into a CD image against what this port writes. ed.exe is
// driven through its GUI by tools/golden_run.sh; this tool is the other half,
// performing the same operations with nothing but we2002::core.
//
//   golden_tool roundtrip <image.bin>   load, then save straight back
//   golden_tool digest <image.bin>      print a stable summary of the load
//
// "roundtrip" is deliberately a no-op edit: open the image and press Write.
// If the oracle and the port disagree there, they disagree about the format
// itself, which is the thing worth knowing first.

#include <cstdio>
#include <cstring>
#include <iostream>
#include <string>

#include "we2002/Database.hpp"
#include "we2002/Offsets.hpp"
#include "we2002/Tables.hpp"

namespace {

void PrintReport(const std::string& message) {
    std::cout << "[report] " << message << "\n";
}

int Usage() {
    std::cerr << "usage: golden_tool <roundtrip|digest|names> <image.bin>\n";
    return 2;
}

// A cheap order-sensitive checksum. Not cryptographic -- it only has to change
// when the loaded state changes, so that "did the port read the same thing the
// oracle did" has a one-line answer.
struct Fnv {
    std::uint64_t h = 1469598103934665603ull;
    void Feed(const void* data, std::size_t n) {
        const auto* p = static_cast<const unsigned char*>(data);
        for (std::size_t i = 0; i < n; ++i) {
            h ^= p[i];
            h *= 1099511628211ull;
        }
    }
};

int Digest(const std::filesystem::path& image) {
    we2002::Database db;
    if (!db.Load(image, PrintReport)) {
        std::cerr << "golden_tool: cannot load " << image << "\n";
        return 1;
    }

    Fnv players;
    for (const auto& p : db.players) {
        players.Feed(p.name, sizeof(p.name));
        players.Feed(p.raw_attributes, sizeof(p.raw_attributes));
    }

    Fnv teams;
    for (const auto& t : db.teams) {
        teams.Feed(t.names, sizeof(t.names));
        teams.Feed(t.abbreviations, sizeof(t.abbreviations));
        teams.Feed(t.raw_formation, sizeof(t.raw_formation));
        teams.Feed(t.flag_colours, sizeof(t.flag_colours));
        teams.Feed(t.home_kit, sizeof(t.home_kit));
        teams.Feed(t.away_kit, sizeof(t.away_kit));
        teams.Feed(&t.squad_numbers, sizeof(t.squad_numbers));
    }

    Fnv ml;
    for (const auto& t : db.ml_teams) {
        ml.Feed(t.names, sizeof(t.names));
        ml.Feed(t.link, sizeof(t.link));
        ml.Feed(t.raw_numbers, sizeof(t.raw_numbers));
    }

    std::printf("players %016llx\n", static_cast<unsigned long long>(players.h));
    std::printf("teams   %016llx\n", static_cast<unsigned long long>(teams.h));
    std::printf("ml      %016llx\n", static_cast<unsigned long long>(ml.h));
    std::printf("team[0]   %s\n", db.teams[0].names[0]);
    std::printf("player[0] %s\n", db.players[0].name);
    return 0;
}

int Roundtrip(const std::filesystem::path& image) {
    we2002::Database db;
    if (!db.Load(image, PrintReport)) {
        std::cerr << "golden_tool: cannot load " << image << "\n";
        return 1;
    }
    if (!db.Save(image, PrintReport)) {
        std::cerr << "golden_tool: cannot save " << image << "\n";
        return 1;
    }
    return 0;
}

// Every team's name slots as Database::Load read them, one line per team
// index in the order of the original editor's team combobox (nations,
// all-stars, Master League): index, mixed-case name, first all-caps name.
// tools/kits/cli.py teams is checked against this (KITS-TASK-13).
int Names(const std::filesystem::path& image) {
    we2002::Database db;
    if (!db.Load(image, PrintReport)) {
        std::cerr << "golden_tool: cannot load " << image << "\n";
        return 1;
    }
    // teams[] has one slot more than there are teams (the 64th of
    // TEAMS_NATIONAL_ALLSTAR_SLOTS); only the 63 the editor lists are printed.
    int index = 0;
    for (int i = 0; i < we2002::TEAMS_NATIONAL_ALLSTAR; ++i)
        std::printf("%d\t%s\t%s\n", index++, db.teams[i].mixed_case_name, db.teams[i].names[0]);
    for (const auto& t : db.ml_teams)
        std::printf("%d\t%s\t%s\n", index++, t.mixed_case_name, t.names[0]);
    return 0;
}

}  // namespace

int main(int argc, char** argv) {
    if (argc != 3) return Usage();

    const std::string verb = argv[1];
    const std::filesystem::path image = argv[2];

    if (verb == "roundtrip") return Roundtrip(image);
    if (verb == "digest") return Digest(image);
    if (verb == "names") return Names(image);
    return Usage();
}

// The SoFIFA commands on the main dialog. The parsing and the conversion
// arithmetic are in we2002::SofifaRules (src/core/Sofifa.cpp); what is left
// here is reading the two rule files at startup, walking the player list, and
// the two text-file round trips.

#include <QCoreApplication>
#include <QMessageBox>
#include <QProgressDialog>

#include <cstring>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

#include "MainWindow.hpp"
#include "Sofifa.hpp"
#include "we2002/Sofifa.hpp"
#include "we2002/Tables.hpp"
#include "ui_MainDialog.h"

using we2002::PLAYERS_NC;
using we2002::PLAYERS_TOTAL;
using we2002::ResolveMlLink;
using we2002::TEAMS_ML;

namespace sofifa {

std::filesystem::path DataFile(const char* name) {
    const std::filesystem::path beside_binary =
        std::filesystem::path(QCoreApplication::applicationDirPath().toStdString()) /
        name;
    if (std::filesystem::exists(beside_binary)) {
        return beside_binary;
    }
#ifdef WE2002_SOURCE_DATA_DIR
    const std::filesystem::path in_source =
        std::filesystem::path(WE2002_SOURCE_DATA_DIR) / name;
    if (std::filesystem::exists(in_source)) {
        return in_source;
    }
#endif
    return name;
}

}  // namespace sofifa

namespace {

/// Where the scraped database is cached, beside the CD image.
std::filesystem::path SofifaDbPath(std::filesystem::path image) {
    if (image.extension() == ".bin") {
        image.replace_extension();
        image += "_SOFIFAdb.txt";
    } else {
        image += "_SOFIFAdb.txt";
    }
    return image;
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

int ToInt(const std::string& s) {
    try {
        return std::stoi(s);
    } catch (...) {
        return 0;
    }
}

}  // namespace

// ---------------------------------------------------------------------------

void MainWindow::LoadSofifaFields() {
    if (!sofifa_rules_.LoadFields(sofifa::DataFile("SOFIFA attributes.txt"))) {
        QMessageBox::warning(
            this, windowTitle(),
            QStringLiteral("Error ! Impossible to read SOFIFA attributes !"));
    }
}

void MainWindow::LoadSofifaConversionRules() {
    // Silent on failure, as in the original: without the rules the import
    // buttons simply produce nothing, and the editor is still usable.
    sofifa_rules_.LoadConversions(
        sofifa::DataFile("WE attributes conversion rules.txt"));
}

// ---------------------------------------------------------------------------

void MainWindow::OnImportSofifaWeb() {
    // One HTTP request per player with a URL. There are 1911 players, so this
    // takes a while; the original blocked with no feedback at all.
    QProgressDialog progress(QStringLiteral("Reading SoFIFA..."),
                             QStringLiteral("Stop"), 0, PLAYERS_TOTAL, this);
    progress.setWindowModality(Qt::WindowModal);

    for (int i = 0; i < PLAYERS_TOTAL; ++i) {
        progress.setValue(i);
        if (progress.wasCanceled()) {
            break;
        }
        const std::string link(db_.players[i].url);
        if (link == "dummy") {
            fifa_players_[i].SetPlayerToDummy(sofifa_rules_);
        } else if (!link.empty()) {
            fifa_players_[i].UpdatePlayerFromURL(link, sofifa_rules_);
        }
    }
    progress.setValue(PLAYERS_TOTAL);

    Report(QStringLiteral("Done. Results will now be written into text file."));

    // Cache what was fetched, so the slow pass need only happen once and the
    // "from txt" button can reload it.
    std::ofstream out(SofifaDbPath(image_), std::ios::trunc);
    out << "NO;NAME;POSITIONS;WEIGHT;HEIGHT;AGE;FOOT;WEAKFOOTSKILL;SKILLMOVES;"
           "OFFWEIGHT;DEFWEIGHT;NATIONALNO;CLUBNO;ATTRIBUTES...\n";
    for (int i = 0; i < PLAYERS_TOTAL; ++i) {
        out << i << ';';
        // Only rows that came from SoFIFA carry data; the rest are just an
        // index and a newline, which is what keeps the file line-aligned with
        // the player list on the way back in.
        if (std::string(db_.players[i].url).find("http://sofifa.com/") !=
            std::string::npos) {
            const we2002::FifaPlayer& f = fifa_players_[i];
            out << f.name << ';' << f.positions << ';' << f.weight << ';'
                << f.height << ';' << f.age << ';' << f.foot << ';'
                << f.weak_foot_skill << ';' << f.skill_moves << ';'
                << f.offensive_work_rate << ';' << f.defensive_work_rate << ';'
                << f.number[0] << ';' << f.number[1] << ';';
            for (int v : f.attribute_values) {
                out << v << ';';
            }
        }
        out << '\n';
    }
    out.close();

    Report(QStringLiteral("Done."));
}

void MainWindow::OnImportSofifaTxt() {
    std::ifstream in(SofifaDbPath(image_));
    if (!in) {
        return;
    }
    std::string line;
    std::getline(in, line);  // header
    for (int i = 0; i < PLAYERS_TOTAL && std::getline(in, line); ++i) {
        const std::vector<std::string> fields = Split(line, ';');
        if (fields.size() <= 12) {
            continue;  // an index-only row: this player was never fetched
        }
        we2002::FifaPlayer& f = fifa_players_[i];
        f.name = fields[1];
        f.positions = fields[2];
        f.weight = ToInt(fields[3]);
        f.height = ToInt(fields[4]);
        f.age = ToInt(fields[5]);
        f.foot = (fields[6] == "L") ? 'L' : 'R';
        f.weak_foot_skill = ToInt(fields[7]);
        f.skill_moves = ToInt(fields[8]);
        f.offensive_work_rate = fields[9];
        f.defensive_work_rate = fields[10];
        f.number[0] = ToInt(fields[11]);
        f.number[1] = ToInt(fields[12]);

        f.attribute_values.clear();
        for (std::size_t k = 13; k < fields.size(); ++k) {
            // The writer puts a ';' after every attribute, so the split leaves
            // a trailing empty field. Skip it rather than storing a zero.
            if (!fields[k].empty()) {
                f.attribute_values.push_back(ToInt(fields[k]));
            }
        }
    }
    Report(QStringLiteral("Done."));
}

void MainWindow::OnEditAllFromFifa() {
    // A height of zero means nothing was ever scraped for this player.
    for (int i = 0; i < PLAYERS_TOTAL; ++i) {
        if (fifa_players_[i].height > 0) {
            we2002::ApplyFifaToPlayer(db_, i, fifa_players_[i], sofifa_rules_,
                                      edit_opt_.names,
                                      edit_opt_.age_height_weight_foot,
                                      edit_opt_.characteristics);
        }
    }

    if (edit_opt_.shirt_numbers) {
        for (int t = 0; t < 54; ++t) {
            for (int k = 0; k < 23; ++k) {
                const int p = PLAYERS_NC + (t * 23) + k;
                if (fifa_players_[p].height > 0) {
                    we2002::SetSquadNumberAt(
                        db_.teams[t].squad_numbers, k,
                        static_cast<std::uint32_t>(fifa_players_[p].number[0] - 1));
                }
            }
        }
        for (int c = 0; c < TEAMS_ML; ++c) {
            for (int k = 0; k < 23; ++k) {
                const int p = ResolveMlLink(&db_.ml_teams[c].link[k * 2]);
                if (fifa_players_[p].height > 0) {
                    db_.ml_teams[c].raw_numbers[k] =
                        static_cast<char>(fifa_players_[p].number[1] - 1);
                }
            }
        }
    }

    OnTeamSelected();
    Report(QStringLiteral("Done."));
}

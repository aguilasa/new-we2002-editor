// The push-button commands: write, reload, and the bulk operations that walk
// every team or every player at once.

#include <QComboBox>
#include <QFile>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QTextStream>

#include <cstring>
#include <fstream>
#include <map>
#include <sstream>
#include <string>
#include <vector>

#include "FlagKitDialog.hpp"
#include "MainWindow.hpp"
#include "PlayerFields.hpp"
#include "Sofifa.hpp"
#include "we2002/Tables.hpp"
#include "ui_MainDialog.h"

using we2002::PLAYERS_NC;
using we2002::PLAYERS_TOTAL;
using we2002::ResolveMlLink;
using we2002::TEAMS_ML;

namespace {

/// The message the original used for every completed bulk operation.
const char* const DONE = "Operation done!";

}  // namespace

// ---------------------------------------------------------------------------

void MainWindow::OnWriteCd() {
    if (!db_.Save(image_, [this](const std::string& m) {
            Report(QString::fromStdString(m));
        })) {
        QMessageBox::critical(this, windowTitle(),
                              QStringLiteral("Could not write the CD image."));
        return;
    }
    // The URLs live in a sidecar file, not on the disc, so they are written
    // together with it. The original never saved them back at all -- it only
    // ever read the file, which meant a URL typed into the form was lost on
    // exit. Writing it is the one behaviour added here, and it cannot affect
    // the image or the golden tests.
    SaveUrls();
    Report(QStringLiteral("CD image edited !"));
}

void MainWindow::OnReload() {
    db_.Load(image_,
             [this](const std::string& m) { Report(QString::fromStdString(m)); });
    LoadUrls();
    OnTeamSelected();
}

void MainWindow::OnFlagKitPreview() {
    const int id = SelectedTeam();
    if (id > 0 && id < 64) {
        we2002::Team& t = db_.teams[id - 1];
        FlagKitDialog dlg(id, t.flag_shape, t.flag_colours, t.home_kit, t.away_kit,
                          this);
        dlg.exec();
    } else if (id > 63 && id < 96) {
        we2002::MlTeam& t = db_.ml_teams[id - 64];
        FlagKitDialog dlg(id, t.flag_shape, t.flag_colours, t.home_kit, t.away_kit,
                          this);
        dlg.exec();
    }
    // The Master League default (96) has no flag or kit, and the original
    // offered nothing for it either.
}

void MainWindow::OnDefaultNumbers() {
    // Push each national squad's number list down onto the player records, so
    // that a player's own shirt number matches the slot they occupy.
    for (int t = 0; t < we2002::TEAMS_NATIONAL_ALLSTAR_SLOTS; ++t) {
        for (int k = 0; k < 23; ++k) {
            db_.players[PLAYERS_NC + (t * 23) + k].number =
                static_cast<int>(
                    we2002::SquadNumberAt(db_.teams[t].squad_numbers, k)) +
                1;
        }
    }
    Report(QLatin1String(DONE));
}

void MainWindow::OnRecomputeCosts() {
    for (int i = 0; i < PLAYERS_TOTAL; ++i) {
        db_.players[i].cost = we2002::ComputePlayerCost(db_, i);
    }
    Report(QLatin1String(DONE));
}

// ---------------------------------------------------------------------------

void MainWindow::OnSortReserves() {
    const int id = SelectedTeam();

    // The twelve bench places, ordered by position code so the keeper ends up
    // last. Position 0 is GK, which would otherwise sort first, so it is
    // temporarily rewritten to 57 -- past every real position -- and put back
    // afterwards. If exactly one keeper turned up, the last two places are
    // swapped so the spare keeper is not the very last name.
    if (id > 0 && id < 64) {
        const int base = ((id - 1) * 23) + 11 + PLAYERS_NC;

        for (int i = 0; i < 12; ++i) {
            if (db_.players[base + i].position == 0) {
                db_.players[base + i].position = 57;
            }
        }
        // The original's bubble sort, kept as-is including its quirk: the
        // outer index also advances the base, so this is not quite a textbook
        // pass. Reproduced rather than corrected, because the resulting order
        // is what users' saves already contain.
        for (int i = 0; i < 12; ++i) {
            const int a = base + i;
            for (int j = 1; j < 12 - i; ++j) {
                if (db_.players[a].position > db_.players[a + j].position) {
                    we2002::Player spare;
                    // The bench sort does not carry the URL across, so the
                    // SoFIFA link stays with the slot rather than the player.
                    CopyPlayerFields(spare, db_.players[a], false);
                    CopyPlayerFields(db_.players[a], db_.players[a + j], false);
                    CopyPlayerFields(db_.players[a + j], spare, false);
                }
            }
        }

        int keepers = 0;
        for (int i = 0; i < 12; ++i) {
            if (db_.players[base + i].position == 57) {
                db_.players[base + i].position = 0;
                ++keepers;
            }
        }
        if (keepers == 1) {
            const int last = base + 11;
            we2002::Player spare;
            CopyPlayerFields(spare, db_.players[last], false);
            CopyPlayerFields(db_.players[last], db_.players[last - 1], false);
            CopyPlayerFields(db_.players[last - 1], spare, false);
        }
    } else if (id > 63) {
        // Link teams reorder the link bytes instead of the player records.
        unsigned char* links =
            (id < 96) ? db_.ml_teams[id - 64].link : db_.ml_default.link;

        int slot[12];
        for (int i = 0; i < 12; ++i) {
            slot[i] = ResolveMlLink(&links[22 + (i * 2)]);
        }
        for (int i = 0; i < 12; ++i) {
            if (db_.players[slot[i]].position == 0) {
                db_.players[slot[i]].position = 57;
            }
        }
        for (int i = 0; i < 12; ++i) {
            for (int j = 1; j < 12 - i; ++j) {
                if (db_.players[slot[i]].position >
                    db_.players[slot[i + j]].position) {
                    // The original wrote its two-byte scratch at indices 1 and
                    // 2 of a char[2] -- one past the end. std::swap does the
                    // same job without walking off the array.
                    std::swap(links[22 + (i * 2)], links[22 + ((i + j) * 2)]);
                    std::swap(links[22 + (i * 2) + 1],
                              links[22 + ((i + j) * 2) + 1]);
                }
            }
        }
        int keepers = 0;
        for (int i = 0; i < 12; ++i) {
            if (db_.players[slot[i]].position == 57) {
                db_.players[slot[i]].position = 0;
                ++keepers;
            }
        }
        if (keepers == 1) {
            std::swap(links[42], links[44]);
            std::swap(links[43], links[45]);
        }
    }

    Report(QLatin1String(DONE));
    OnTeamSelected();
}

// ---------------------------------------------------------------------------

void MainWindow::OnCopyTeamNames() {
    // Spread the first (longest) name across every other slot, truncated to
    // whatever each slot holds, and derive the mixed-case and Japanese
    // spellings from it.
    const int id = SelectedTeam();
    if (id <= 0 || id > 95) {
        return;
    }
    const bool is_ml = id > 63;
    const int t = id - 1;  // row in the per-team length tables, ML included

    char (*names)[20] = is_ml ? db_.ml_teams[id - 64].names : db_.teams[t].names;
    char (*abbrev)[4] =
        is_ml ? db_.ml_teams[id - 64].abbreviations : db_.teams[t].abbreviations;
    char* mixed = is_ml ? db_.ml_teams[id - 64].mixed_case_name
                        : db_.teams[t].mixed_case_name;
    char* kanji =
        is_ml ? db_.ml_teams[id - 64].kanji_name : db_.teams[t].kanji_name;

    const QString source = txt_team_name_[0]->text();
    const auto store = [](char* dest, std::size_t cap, const QString& s) {
        const QByteArray b = s.toLatin1();
        std::snprintf(dest, cap, "%s", b.constData());
    };

    store(names[0], sizeof(names[0]), source);

    const char lengths[6] = {0,
                             we2002::TEAM_NAME_LEN_2[t], we2002::TEAM_NAME_LEN_3[t],
                             we2002::TEAM_NAME_LEN_4[t], we2002::TEAM_NAME_LEN_5[t],
                             we2002::TEAM_NAME_LEN_6[t]};
    for (int i = 1; i < 6; ++i) {
        const QString cut = source.left(lengths[i] - 1);
        store(names[i], sizeof(names[i]), cut);
        txt_team_name_[i]->setText(cut);
    }

    const QString abbr = source.left(3);
    for (int i = 0; i < 3; ++i) {
        store(abbrev[i], sizeof(abbrev[i]), abbr);
        txt_abbrev_[i]->setText(abbr);
    }

    // "BAYERN" -> "Bayern": keep the first letter, lower-case the rest, then
    // trim to the slot's length.
    const auto title_case = [&source](int limit) {
        const QString tail = source.mid(1).toLower().left(limit - 2);
        return source.left(1) + tail;
    };

    const QString mixed_text = title_case(we2002::TEAM_MIXED_CASE_NAME_LEN[t]);
    store(mixed, 20, mixed_text);
    ui_->TXT_TEAM_NAME_MIXED->setText(mixed_text);

    // The Japanese slot's length is read at row id-64 for Master League clubs
    // but id-1 for everything else -- including the five other name slots just
    // above, which use id-1 for clubs as well. That inconsistency is the
    // original's; it makes the derived Japanese name a different length for a
    // club than the label above the box promises.
    const QString kanji_text =
        title_case(we2002::TEAM_NAME_KANJI_LEN[is_ml ? id - 64 : t]);
    store(kanji, 20, kanji_text);
    ui_->TXT_TEAM_NAME_KANJI->setText(kanji_text);

    if (is_ml) {
        const int c = id - 64;
        const QString extra1 = source.left(we2002::ML_TEAM_NAME_LEN_7[c] - 1);
        store(db_.ml_teams[c].names[6], 20, extra1);
        ui_->TXT_ML_EXTRA_NAME1->setText(extra1);

        const QString extra2 = source.left(we2002::ML_TEAM_NAME_LEN_8[c] - 1);
        store(db_.ml_teams[c].names[7], 20, extra2);
        ui_->TXT_ML_EXTRA_NAME2->setText(extra2);
    }
}

// ---------------------------------------------------------------------------

void MainWindow::OnEditAllPlayersLook() {
    // data/defaultlook.txt lists, per team, the skin tone / hair / beard the
    // whole squad should get. An empty field means "leave it alone".
    //
    // Note the file is cp1252, not UTF-8: it carries a 0x92 curly apostrophe
    // in "Costa d'Avorio". Only the two leading columns are text and neither
    // is parsed, so the bytes are read as Latin-1 and never decoded.
    const std::filesystem::path path = sofifa::DataFile("defaultlook.txt");
    std::ifstream in(path);
    if (!in) {
        QMessageBox::warning(
            this, windowTitle(),
            QStringLiteral("Failed to open file defaultlook.txt!"));
        return;
    }

    // Columns 3..7: skin, hair style, hair colour, beard style, beard colour,
    // each a label from the player-skills combos. -1 for "not specified".
    static const char* const kSkin[] = {"A", "B", "C", "D"};
    static const char* const kHair[] = {
        "A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2",
        "D1", "D2", "E1", "E2", "F1", "F2", "F3", "G1", "H1", "I1", "I2",
        "I3", "J1", "K1", "L1", "L2", "L3", "M1", "N1", "O1", "P1"};
    static const char* const kLetters[] = {"A", "B", "C", "D", "E", "F", "G", "H"};

    const auto index_of = [](const std::string& v, const char* const* table,
                             int count) {
        for (int i = 0; i < count; ++i) {
            if (v == table[i]) {
                return i;
            }
        }
        return -1;
    };

    int look[95][5];
    for (auto& row : look) {
        for (int& v : row) {
            v = -1;
        }
    }

    std::string line;
    std::getline(in, line);  // header
    for (int i = 0; i < 95 && std::getline(in, line); ++i) {
        std::vector<std::string> fields;
        std::stringstream ss(line);
        std::string field;
        while (std::getline(ss, field, ';')) {
            fields.push_back(field);
        }
        if (fields.size() != 7) {
            continue;
        }
        look[i][0] = index_of(fields[2], kSkin, 4);
        look[i][1] = index_of(fields[3], kHair, 32);
        look[i][2] = index_of(fields[4], kLetters, 8);
        look[i][3] = index_of(fields[5], kLetters, 7);
        look[i][4] = index_of(fields[6], kLetters, 7);
    }

    const auto apply = [](we2002::Player& p, const int (&row)[5]) {
        if (row[0] >= 0) p.skin_colour = row[0];
        if (row[1] >= 0) p.hair_style = row[1];
        if (row[2] >= 0) p.hair_colour = row[2];
        if (row[3] >= 0) p.beard_style = row[3];
        if (row[4] >= 0) p.beard_colour = row[4];
    };

    for (int t = 0; t < 54; ++t) {
        for (int k = 0; k < 23; ++k) {
            apply(db_.players[PLAYERS_NC + (t * 23) + k], look[t]);
        }
    }
    for (int t = 63; t < 95; ++t) {
        for (int j = 0; j < 46; j += 2) {
            const int p = ResolveMlLink(&db_.ml_teams[t - 63].link[j]);
            // Contracted players were already covered by the loop above; only
            // the free agents a club has signed still need doing.
            if (p < PLAYERS_NC) {
                apply(db_.players[p], look[t]);
            }
        }
    }

    Report(QStringLiteral("Done."));
}

void MainWindow::OnEditAllBars() {
    // Recompute the five strength bars from the starting eleven, as a
    // position-weighted mean of the relevant skill, shifted down by ten
    // because the bars run 0..9 while the skills run 12..19.
    static const int kWeights[5][8] = {
        // GK CB SB DH SH OH CF WG
        {0, 0, 0, 0, 1, 3, 5, 3},  // attack
        {5, 4, 2, 2, 0, 0, 0, 0},  // defence
        {3, 5, 1, 4, 1, 2, 4, 1},  // power
        {0, 1, 3, 1, 5, 2, 4, 5},  // speed
        {0, 0, 0, 3, 2, 5, 4, 2},  // technique
    };

    const auto skill = [](const we2002::Player& p, int bar) {
        switch (bar) {
            case 0: return p.attack;
            case 1: return p.defence;
            case 2: return p.strength;
            case 3: return p.speed;
            default: return p.technique;
        }
    };

    const auto accumulate = [&](const int* squad, int count, char* out[5]) {
        for (int bar = 0; bar < 5; ++bar) {
            double values = 0;
            double weights = 0;
            for (int i = 0; i < count; ++i) {
                const we2002::Player& p = db_.players[squad[i]];
                const int w = kWeights[bar][p.position];
                values += skill(p, bar) * w;
                weights += w;
            }
            *out[bar] = static_cast<char>(
                static_cast<int>(values / weights - 10 + 0.5));
        }
    };

    // 54 national teams and the first two all-star sides. The seven classic
    // sides (57..63) are left alone, as in the original.
    for (int t = 0; t < 56; ++t) {
        int squad[11];
        for (int i = 0; i < 11; ++i) {
            squad[i] = PLAYERS_NC + (t * 23) + i;
        }
        we2002::Team& team = db_.teams[t];
        char* out[5] = {&team.bar_attack, &team.bar_defence, &team.bar_power,
                        &team.bar_speed, &team.bar_technique};
        accumulate(squad, 11, out);
    }
    for (int c = 0; c < TEAMS_ML; ++c) {
        int squad[11];
        for (int i = 0; i < 11; ++i) {
            squad[i] = ResolveMlLink(&db_.ml_teams[c].link[i * 2]);
        }
        we2002::MlTeam& club = db_.ml_teams[c];
        char* out[5] = {&club.bar_attack, &club.bar_defence, &club.bar_power,
                        &club.bar_speed, &club.bar_technique};
        accumulate(squad, 11, out);
    }

    OnTeamSelected();
    Report(QStringLiteral("Done."));
}

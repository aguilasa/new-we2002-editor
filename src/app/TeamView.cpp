// The team view: everything that reads a team out of the database into the
// form, and everything that writes an edited field back.
//
// This is the port of OnSelezioneSquadraV (legacy/mfc/edDlg.cpp:2328-3360,
// 1030 lines) and of the killfocus families that hang off it. The original
// opened with the comment
//
//     //////////////////////////////////////////////////
//     // accidenti a non poter usare i vettori!!!!    //
//     //////////////////////////////////////////////////
//
// -- "damn not being able to use arrays" -- and then spelled out twenty-three
// copies of each line. The arrays exist now; the logic is unchanged.

#include <QComboBox>
#include <QLabel>
#include <QLineEdit>
#include <QSignalBlocker>

#include <cstring>

#include "MainWindow.hpp"
#include "PlayerSelectDialog.hpp"
#include "PlayerSkillsDialog.hpp"
#include "we2002/Tables.hpp"
#include "ui_MainDialog.h"

using we2002::PLAYERS_NC;
using we2002::ResolveMlLink;

namespace {

/// Copy a QString into one of the fixed char buffers on the disc structures.
/// The original used strcpy into char[20] and friends and simply trusted the
/// LimitText it had set on the edit box; this keeps the truncation but stops
/// it overrunning if a limit is ever missed.
template <std::size_t N>
void CopyInto(char (&dest)[N], const QString& text) {
    const QByteArray bytes = text.toLatin1();
    const std::size_t n = std::min<std::size_t>(bytes.size(), N - 1);
    std::memcpy(dest, bytes.constData(), n);
    dest[n] = '\0';
}

/// "(12)" -- the length hint the original built with _itoa + strcpy + strcat.
QString LengthHint(int stored_length) {
    return QStringLiteral("(%1)").arg(stored_length - 1);
}

}  // namespace

// ---------------------------------------------------------------------------
// Loading a team into the form
// ---------------------------------------------------------------------------

void MainWindow::OnTeamSelected() {
    const int id = SelectedTeam();

    for (QComboBox* kicker : cmb_kicker_) {
        const QSignalBlocker block(kicker);
        kicker->clear();
    }

    if (id > 0) {
        // Fields that every team has. The per-kind branches below may disable
        // or overwrite them again.
        for (int i = 0; i < 6; ++i) {
            txt_team_name_[i]->setEnabled(true);
        }
        for (int i = 0; i < 3; ++i) {
            txt_abbrev_[i]->setEnabled(true);
        }
        ui_->TXT_TEAM_NAME_KANJI->setEnabled(true);
        ui_->TXT_TEAM_NAME_MIXED->setEnabled(true);
        for (QLineEdit* bar : txt_bar_) {
            bar->setEnabled(true);
        }
        for (QLineEdit* url : txt_url_) {
            url->setEnabled(true);
        }
        // The two extra Master League name slots are hidden for everyone else.
        ui_->TXT_ML_EXTRA_NAME1->setVisible(false);
        ui_->TXT_ML_EXTRA_NAME2->setVisible(false);
        ui_->LAB_ML_EXTRA_NAMES->setVisible(false);
        ui_->LBL_ML_EXTRA_NAME1->setVisible(false);
        ui_->LBL_ML_EXTRA_NAME2->setVisible(false);

        // Name lengths are per team and fixed by the disc layout. Index id-1
        // spans national teams, all-stars and Master League clubs in disc
        // order, which is why the Master League branch also uses id-1 here.
        //
        // The Master League default (id 96) has no row in these tables. The
        // original read one past the end of all of them; the values were then
        // thrown away by the branch below, which blanks the labels. Skipping
        // the read is the only difference, and it is not observable.
        if (id < 96) {
            const int t = id - 1;
            const char lengths[6] = {
                we2002::TEAM_NAME_LEN_1[t], we2002::TEAM_NAME_LEN_2[t],
                we2002::TEAM_NAME_LEN_3[t], we2002::TEAM_NAME_LEN_4[t],
                we2002::TEAM_NAME_LEN_5[t], we2002::TEAM_NAME_LEN_6[t]};
            for (int i = 0; i < 6; ++i) {
                lab_team_name_[i]->setText(LengthHint(lengths[i]));
                txt_team_name_[i]->setMaxLength(lengths[i] - 1);
            }
            ui_->LAB_TEAM_NAME_KANJI->setText(LengthHint(we2002::TEAM_NAME_KANJI_LEN[t]));
            ui_->TXT_TEAM_NAME_KANJI->setMaxLength(we2002::TEAM_NAME_KANJI_LEN[t] - 1);
            ui_->LAB_TEAM_NAME_MIXED->setText(
                LengthHint(we2002::TEAM_MIXED_CASE_NAME_LEN[t]));
            ui_->TXT_TEAM_NAME_MIXED->setMaxLength(
                we2002::TEAM_MIXED_CASE_NAME_LEN[t] - 1);
        }

        if (id < 64) {
            ShowNationalOrAllStar(id);
        } else if (id < 96) {
            ShowMlClub(id);
        } else {
            ShowMlDefault();
        }
    } else {
        ClearTeamForm();
    }

    // The original ended by calling OnSelchangeTat2..11 and OnChangeTatx2 by
    // hand, because SetCurSel does not raise CBN_SELCHANGE. Qt's
    // currentIndexChanged does fire on setCurrentIndex, so the role captions
    // have already been repainted; only the pitch layout still needs a nudge,
    // and only for slots whose coordinate text did not change.
    for (int i = 0; i < 10; ++i) {
        OnSlotMoved(i);
    }
}

void MainWindow::ShowNationalOrAllStar(int id) {
    const we2002::Team& team = db_.teams[id - 1];
    const bool is_all_star = (id == 55 || id == 56);

    for (int i = 0; i < 6; ++i) {
        txt_team_name_[i]->setText(QLatin1String(team.names[i]));
    }
    for (int i = 0; i < 3; ++i) {
        txt_abbrev_[i]->setText(QLatin1String(team.abbreviations[i]));
    }
    ui_->TXT_TEAM_NAME_KANJI->setText(QLatin1String(team.kanji_name));
    ui_->TXT_TEAM_NAME_MIXED->setText(QLatin1String(team.mixed_case_name));

    const char bars[5] = {team.bar_attack, team.bar_defence, team.bar_power,
                          team.bar_speed, team.bar_technique};
    for (int i = 0; i < 5; ++i) {
        txt_bar_[i]->setText(QString::number(static_cast<int>(bars[i])));
    }

    for (int i = 0; i < 10; ++i) {
        const QSignalBlocker block(cmb_role_[i]);
        cmb_role_[i]->setCurrentIndex(team.raw_formation[i] - 2);
        // Blocking the combo suppressed the caption repaint, so do it here.
        OnRoleShown(i);
        txt_slot_x_[i]->setText(
            QString::number(static_cast<int>(team.raw_formation[10 + i])));
        txt_slot_y_[i]->setText(
            QString::number(static_cast<int>(team.raw_formation[20 + i])));
    }

    for (int k = 0; k < 23; ++k) {
        const int lk = SquadPlayer(id, k);
        txt_player_[k]->setText(QLatin1String(db_.players[lk].name));
        txt_url_[k]->setText(QLatin1String(db_.players[lk].url));
        // The all-star squads are assembled from links into other teams, so
        // there is no stable player record to hang a SoFIFA URL on.
        txt_url_[k]->setEnabled(!is_all_star);
    }

    // The kicker lists are filled by arithmetic even for the two all-star
    // sides, whose squads are actually reached through links. That is the
    // original's behaviour and it is why the all-star kicker dropdowns show
    // the names of whoever occupies those pool slots.
    for (int i = 0; i < 11; ++i) {
        const int lk = ((id - 1) * 23) + i + PLAYERS_NC;
        for (QComboBox* kicker : cmb_kicker_) {
            kicker->addItem(QLatin1String(db_.players[lk].name));
        }
    }
    const char chosen[6] = {team.kick_long_fk,      team.kick_short_fk,
                            team.kick_left_corner,  team.kick_right_corner,
                            team.kick_penalty,      team.captain};
    for (int i = 0; i < 6; ++i) {
        const QSignalBlocker block(cmb_kicker_[i]);
        cmb_kicker_[i]->setCurrentIndex(chosen[i]);
    }

    for (int k = 0; k < 23; ++k) {
        txt_number_[k]->setText(QString::number(
            static_cast<int>(we2002::SquadNumberAt(team.squad_numbers, k)) + 1));
    }
}

void MainWindow::ShowMlClub(int id) {
    const we2002::MlTeam& club = db_.ml_teams[id - 64];

    ui_->TXT_ML_EXTRA_NAME1->setVisible(true);
    ui_->TXT_ML_EXTRA_NAME2->setVisible(true);
    ui_->LAB_ML_EXTRA_NAMES->setVisible(true);
    ui_->LBL_ML_EXTRA_NAME1->setVisible(true);
    ui_->LBL_ML_EXTRA_NAME2->setVisible(true);

    for (int i = 0; i < 6; ++i) {
        txt_team_name_[i]->setText(QLatin1String(club.names[i]));
    }
    for (int i = 0; i < 3; ++i) {
        txt_abbrev_[i]->setText(QLatin1String(club.abbreviations[i]));
    }
    ui_->TXT_TEAM_NAME_KANJI->setText(QLatin1String(club.kanji_name));
    ui_->TXT_TEAM_NAME_MIXED->setText(QLatin1String(club.mixed_case_name));
    ui_->TXT_ML_EXTRA_NAME1->setText(QLatin1String(club.names[6]));
    ui_->TXT_ML_EXTRA_NAME2->setText(QLatin1String(club.names[7]));

    const int c = id - 64;
    ui_->LBL_ML_EXTRA_NAME1->setText(LengthHint(we2002::ML_TEAM_NAME_LEN_7[c]));
    ui_->TXT_ML_EXTRA_NAME1->setMaxLength(we2002::ML_TEAM_NAME_LEN_7[c] - 1);
    ui_->LBL_ML_EXTRA_NAME2->setText(LengthHint(we2002::ML_TEAM_NAME_LEN_8[c]));
    ui_->TXT_ML_EXTRA_NAME2->setMaxLength(we2002::ML_TEAM_NAME_LEN_8[c] - 1);

    const char bars[5] = {club.bar_attack, club.bar_defence, club.bar_power,
                          club.bar_speed, club.bar_technique};
    for (int i = 0; i < 5; ++i) {
        txt_bar_[i]->setText(QString::number(static_cast<int>(bars[i])));
    }

    for (int i = 0; i < 10; ++i) {
        const QSignalBlocker block(cmb_role_[i]);
        cmb_role_[i]->setCurrentIndex(club.raw_formation[i] - 2);
        OnRoleShown(i);
        txt_slot_x_[i]->setText(
            QString::number(static_cast<int>(club.raw_formation[10 + i])));
        txt_slot_y_[i]->setText(
            QString::number(static_cast<int>(club.raw_formation[20 + i])));
    }

    for (int k = 0; k < 23; ++k) {
        const int lk = ResolveMlLink(&club.link[k * 2]);
        txt_player_[k]->setText(QLatin1String(db_.players[lk].name));
        txt_url_[k]->setText(QLatin1String(db_.players[lk].url));
        // Only the eleven starters can take a set piece.
        if (k < 11) {
            for (QComboBox* kicker : cmb_kicker_) {
                kicker->addItem(QLatin1String(db_.players[lk].name));
            }
        }
    }
    const char chosen[6] = {club.kick_long_fk,     club.kick_short_fk,
                            club.kick_left_corner, club.kick_right_corner,
                            club.kick_penalty,     club.captain};
    for (int i = 0; i < 6; ++i) {
        const QSignalBlocker block(cmb_kicker_[i]);
        cmb_kicker_[i]->setCurrentIndex(chosen[i]);
    }

    for (int k = 0; k < 23; ++k) {
        txt_number_[k]->setText(
            QString::number(static_cast<int>(club.raw_numbers[k]) + 1));
    }
}

void MainWindow::ShowMlDefault() {
    const we2002::MlTeam& tpl = db_.ml_default;

    // The default template has no names and no strength bars: it is only a
    // squad and a formation. The original showed "---" and "-" and greyed the
    // fields out.
    for (int i = 0; i < 6; ++i) {
        txt_team_name_[i]->setText(QStringLiteral("---"));
        txt_team_name_[i]->setEnabled(false);
        lab_team_name_[i]->clear();
    }
    for (int i = 0; i < 3; ++i) {
        txt_abbrev_[i]->setText(QStringLiteral("---"));
        txt_abbrev_[i]->setEnabled(false);
    }
    ui_->TXT_TEAM_NAME_KANJI->setText(QStringLiteral("---"));
    ui_->TXT_TEAM_NAME_KANJI->setEnabled(false);
    ui_->TXT_TEAM_NAME_MIXED->setText(QStringLiteral("---"));
    ui_->TXT_TEAM_NAME_MIXED->setEnabled(false);
    ui_->LAB_TEAM_NAME_KANJI->clear();
    ui_->LAB_TEAM_NAME_MIXED->clear();
    for (QLineEdit* bar : txt_bar_) {
        bar->setText(QStringLiteral("-"));
        bar->setEnabled(false);
    }

    for (int i = 0; i < 10; ++i) {
        const QSignalBlocker block(cmb_role_[i]);
        cmb_role_[i]->setCurrentIndex(tpl.raw_formation[i] - 2);
        OnRoleShown(i);
        txt_slot_x_[i]->setText(
            QString::number(static_cast<int>(tpl.raw_formation[10 + i])));
        txt_slot_y_[i]->setText(
            QString::number(static_cast<int>(tpl.raw_formation[20 + i])));
    }

    for (int k = 0; k < 23; ++k) {
        const int lk = ResolveMlLink(&tpl.link[k * 2]);
        txt_player_[k]->setText(QLatin1String(db_.players[lk].name));
        // No URLs here: the template's players are shared with the clubs, and
        // editing one from this screen would be ambiguous.
        txt_url_[k]->clear();
        txt_url_[k]->setEnabled(false);
        if (k < 11) {
            for (QComboBox* kicker : cmb_kicker_) {
                kicker->addItem(QLatin1String(db_.players[lk].name));
            }
        }
    }
    const char chosen[6] = {tpl.kick_long_fk,     tpl.kick_short_fk,
                            tpl.kick_left_corner, tpl.kick_right_corner,
                            tpl.kick_penalty,     tpl.captain};
    for (int i = 0; i < 6; ++i) {
        const QSignalBlocker block(cmb_kicker_[i]);
        cmb_kicker_[i]->setCurrentIndex(chosen[i]);
    }

    for (int k = 0; k < 23; ++k) {
        txt_number_[k]->setText(
            QString::number(static_cast<int>(tpl.raw_numbers[k]) + 1));
    }
}

void MainWindow::ClearTeamForm() {
    for (int k = 0; k < 23; ++k) {
        txt_number_[k]->clear();
        txt_player_[k]->clear();
        txt_url_[k]->clear();
    }
    for (int i = 0; i < 6; ++i) {
        txt_team_name_[i]->clear();
        lab_team_name_[i]->clear();
    }
    for (int i = 0; i < 3; ++i) {
        txt_abbrev_[i]->clear();
    }
    ui_->LAB_TEAM_NAME_KANJI->clear();
    ui_->LAB_TEAM_NAME_MIXED->clear();
    ui_->TXT_TEAM_NAME_KANJI->clear();
    ui_->TXT_TEAM_NAME_MIXED->clear();
    for (QLineEdit* bar : txt_bar_) {
        bar->clear();
    }
    for (int i = 0; i < 10; ++i) {
        const QSignalBlocker block(cmb_role_[i]);
        cmb_role_[i]->setCurrentIndex(-1);
        OnRoleShown(i);
        txt_slot_x_[i]->clear();
        txt_slot_y_[i]->clear();
    }
}

// ---------------------------------------------------------------------------
// Writing edits back
// ---------------------------------------------------------------------------

void MainWindow::OnTeamNameEdited(int slot) {
    const int id = SelectedTeam();
    const QString text = txt_team_name_[slot]->text();
    if (id > 0 && id < 64) {
        CopyInto(db_.teams[id - 1].names[slot], text);
    } else if (id > 63 && id < 96) {
        CopyInto(db_.ml_teams[id - 64].names[slot], text);
    }
}

void MainWindow::OnMlExtraNameEdited(int slot) {
    const int id = SelectedTeam();
    if (id > 63 && id < 96) {
        QLineEdit* box = (slot == 0) ? ui_->TXT_ML_EXTRA_NAME1 : ui_->TXT_ML_EXTRA_NAME2;
        CopyInto(db_.ml_teams[id - 64].names[6 + slot], box->text());
    }
}

void MainWindow::OnKanjiNameEdited() {
    const int id = SelectedTeam();
    const QString text = ui_->TXT_TEAM_NAME_KANJI->text();
    if (id > 0 && id < 64) {
        CopyInto(db_.teams[id - 1].kanji_name, text);
    } else if (id > 63 && id < 96) {
        CopyInto(db_.ml_teams[id - 64].kanji_name, text);
    }
}

void MainWindow::OnMixedCaseNameEdited() {
    const int id = SelectedTeam();
    const QString text = ui_->TXT_TEAM_NAME_MIXED->text();
    if (id > 0 && id < 64) {
        CopyInto(db_.teams[id - 1].mixed_case_name, text);
    } else if (id > 63 && id < 96) {
        CopyInto(db_.ml_teams[id - 64].mixed_case_name, text);
    }
}

void MainWindow::OnAbbreviationEdited(int slot) {
    const int id = SelectedTeam();
    const QString text = txt_abbrev_[slot]->text();
    if (id > 0 && id < 64) {
        CopyInto(db_.teams[id - 1].abbreviations[slot], text);
    } else if (id > 63 && id < 96) {
        CopyInto(db_.ml_teams[id - 64].abbreviations[slot], text);
    }
}

void MainWindow::OnBarEdited(int bar) {
    const int id = SelectedTeam();
    const char value = static_cast<char>(txt_bar_[bar]->text().toInt());
    char* target = nullptr;
    if (id > 0 && id < 64) {
        we2002::Team& t = db_.teams[id - 1];
        char* const bars[5] = {&t.bar_attack, &t.bar_defence, &t.bar_power,
                               &t.bar_speed, &t.bar_technique};
        target = bars[bar];
    } else if (id > 63 && id < 96) {
        we2002::MlTeam& t = db_.ml_teams[id - 64];
        char* const bars[5] = {&t.bar_attack, &t.bar_defence, &t.bar_power,
                               &t.bar_speed, &t.bar_technique};
        target = bars[bar];
    }
    if (target != nullptr) {
        *target = value;
    }
}

void MainWindow::OnKickerChanged(int which) {
    const int id = SelectedTeam();
    const char value = static_cast<char>(cmb_kicker_[which]->currentIndex());
    char* target = nullptr;
    if (id > 0 && id < 64) {
        we2002::Team& t = db_.teams[id - 1];
        char* const targets[6] = {&t.kick_long_fk,      &t.kick_short_fk,
                                &t.kick_left_corner,  &t.kick_right_corner,
                                &t.kick_penalty,      &t.captain};
        target = targets[which];
    } else if (id > 63 && id < 96) {
        we2002::MlTeam& t = db_.ml_teams[id - 64];
        char* const targets[6] = {&t.kick_long_fk,      &t.kick_short_fk,
                                &t.kick_left_corner,  &t.kick_right_corner,
                                &t.kick_penalty,      &t.captain};
        target = targets[which];
    } else if (id == 96) {
        we2002::MlTeam& t = db_.ml_default;
        char* const targets[6] = {&t.kick_long_fk,      &t.kick_short_fk,
                                &t.kick_left_corner,  &t.kick_right_corner,
                                &t.kick_penalty,      &t.captain};
        target = targets[which];
    }
    if (target != nullptr) {
        *target = value;
    }
}

void MainWindow::OnSquadNumberEdited(int slot) {
    const int id = SelectedTeam();
    int value = txt_number_[slot]->text().toInt();
    if (id > 0 && id < 64) {
        // National squads pack the numbers into five bits each, so 32 is the
        // ceiling; the original clamped and rewrote the box.
        if (value > 32) {
            value = 32;
            txt_number_[slot]->setText(QStringLiteral("32"));
        }
        we2002::SetSquadNumberAt(db_.teams[id - 1].squad_numbers, slot,
                                 static_cast<std::uint32_t>(value - 1));
        // Keep the player's own shirt number in step with the team's list.
        db_.players[PLAYERS_NC + ((id - 1) * 23) + slot].number = value;
    } else if (id > 63 && id < 96) {
        db_.ml_teams[id - 64].raw_numbers[slot] = static_cast<char>(value - 1);
    } else if (id == 96) {
        db_.ml_default.raw_numbers[slot] = static_cast<char>(value - 1);
    }
}

void MainWindow::OnPlayerUrlEdited(int slot) {
    const int id = SelectedTeam();
    if (id <= 0 || id >= 96) {
        return;
    }
    // Note the asymmetry, kept from the original: the all-star sides (55, 56)
    // resolve their squad through links everywhere else, but here they fall
    // into the arithmetic branch along with the ordinary national teams. Their
    // URL boxes are disabled in that case, so the branch is unreachable.
    const int lk = (id < 64) ? ((id - 1) * 23) + slot + PLAYERS_NC
                             : ResolveMlLink(&db_.ml_teams[id - 64].link[slot * 2]);
    const QByteArray text = txt_url_[slot]->text().toLatin1();
    std::snprintf(db_.players[lk].url, sizeof(db_.players[lk].url), "%s",
                  text.constData());
}

void MainWindow::OnPlayerSkills(int slot) {
    const int id = SelectedTeam();
    if (id <= 0) {
        return;
    }
    const int player = SquadPlayer(id, slot);
    PlayerSkillsDialog dlg(db_, fifa_players_, sofifa_rules_, player, this);
    dlg.exec();
    OnTeamSelected();
}

void MainWindow::OnPlayerSwap(int slot) {
    const int id = SelectedTeam();
    if (id <= 0) {
        return;
    }

    // National teams own their squad outright: the dialog edits the player
    // record in place. Everything else holds a link table, and the swap
    // rewrites the two link bytes for this slot.
    if ((id > 0 && id < 55) || (id > 56 && id < 64)) {
        PlayerSelectDialog dlg(db_, SquadPlayer(id, slot), this);
        dlg.exec();
    } else {
        unsigned char* links = nullptr;
        if (id == 55) {
            links = db_.link_euro_allstar;
        } else if (id == 56) {
            links = db_.link_world_allstar;
        } else if (id < 96) {
            links = db_.ml_teams[id - 64].link;
        } else {
            links = db_.ml_default.link;
        }

        PlayerSelectDialog dlg(db_, ResolveMlLink(&links[slot * 2]), links,
                               slot * 2, this);
        dlg.exec();
        if (id == 55 || id == 56) {
            // The all-star squads are a view over other teams' players, so
            // their name copies have to be rebuilt after a swap.
            db_.CopyAllStarNames();
        }
    }
    OnTeamSelected();
}

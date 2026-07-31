#include "PlayerSelectDialog.hpp"

#include <QCheckBox>
#include <QComboBox>
#include <QLabel>
#include <QListWidget>
#include <QPushButton>

#include <cstring>
#include <string>

#include "PlayerFields.hpp"
#include "we2002/Tables.hpp"
#include "we2002/Types.hpp"
#include "ui_PlayerSelectDialog.h"

using we2002::PICKER_TEAM_NAMES;
using we2002::PLAYERS_NC;

namespace {

/// The "- ML (non contacted) " row: the 64th entry in the team list, holding
/// the whole free-agent pool rather than a 23-man squad.
constexpr int NON_CONTRACT_ROW = 63;

/// SoFIFA URLs look like .../player/12345-lionel-messi/230045/?units=..., and
/// the picker showed the slug between the first '-' and the '?' beside the
/// name so you can tell two players with the same short name apart.
QString UrlHint(const char* url) {
    const std::string s(url);
    const std::size_t dash = s.find('-');
    const std::size_t query = s.find('?');
    if (dash == std::string::npos || query == std::string::npos || query <= dash + 1) {
        return {};
    }
    return QString::fromLatin1(s.data() + dash + 1,
                               static_cast<int>(query - dash - 1));
}

}  // namespace

PlayerSelectDialog::PlayerSelectDialog(we2002::Database& db, int slot_player,
                                       QWidget* parent)
    : QDialog(parent), ui_(new Ui::PlayerSelectDialog), db_(db),
      slot_player_(slot_player) {
    Build();
}

PlayerSelectDialog::PlayerSelectDialog(we2002::Database& db, int slot_player,
                                       unsigned char* links, int link_pos,
                                       QWidget* parent)
    : QDialog(parent), ui_(new Ui::PlayerSelectDialog), db_(db),
      slot_player_(slot_player), links_(links), link_pos_(link_pos),
      link_mode_(true) {
    Build();
}

PlayerSelectDialog::~PlayerSelectDialog() {
    delete ui_;
}

void PlayerSelectDialog::Build() {
    ui_->setupUi(this);
    setFixedSize(size());

    for (int i = 0; i < 54; ++i) {
        ui_->LIST_TEAMS->addItem(QStringLiteral("National %1 - %2")
                                       .arg(i + 1)
                                       .arg(QLatin1String(PICKER_TEAM_NAMES[i])));
    }
    for (int i = 0; i < 9; ++i) {
        ui_->LIST_TEAMS->addItem(
            QStringLiteral("All-star %1 - %2")
                .arg(i + 1)
                .arg(QLatin1String(PICKER_TEAM_NAMES[i + 54])));
    }
    ui_->LIST_TEAMS->addItem(QStringLiteral("- ML (non contacted) "));

    connect(ui_->LIST_TEAMS, &QListWidget::currentRowChanged, this,
            &PlayerSelectDialog::OnTeamSelected);
    connect(ui_->LIST_PLAYERS, &QListWidget::currentRowChanged, this,
            &PlayerSelectDialog::OnPlayerSelected);
    connect(ui_->LIST_PLAYERS, &QListWidget::itemDoubleClicked, this,
            &PlayerSelectDialog::OnAccept);
    connect(ui_->IDC_BUTTON1, &QPushButton::clicked, this,
            &PlayerSelectDialog::OnAccept);
    connect(ui_->CHK_ML, &QCheckBox::clicked, this,
            &PlayerSelectDialog::OnLinkModeToggled);
    connect(ui_->CHK_COMPLETE_SWAP, &QCheckBox::clicked, this,
            &PlayerSelectDialog::OnSwapModeToggled);
    connect(ui_->CHK_LK_DEF, &QCheckBox::clicked, this,
            &PlayerSelectDialog::OnDefaultNationalityToggled);
    connect(ui_->CHK_LK_NDEF, &QCheckBox::clicked, this,
            &PlayerSelectDialog::OnChangeNationalityToggled);

    if (link_mode_) {
        // Link teams may still edit skills instead, so the checkbox is shown
        // and starts ticked; copy/swap teams never see it.
        ui_->CHK_ML->setVisible(true);
        ui_->CHK_COMPLETE_SWAP->setVisible(false);
        ui_->CHK_ML->setChecked(true);
    }
    OnLinkModeToggled();
}

// ---------------------------------------------------------------------------

void PlayerSelectDialog::OnTeamSelected() {
    const int id = ui_->LIST_TEAMS->currentRow();
    ui_->LIST_PLAYERS->clear();
    if (id < 0) {
        return;
    }

    const int count = (id == NON_CONTRACT_ROW) ? PLAYERS_NC : 23;
    for (int i = 0; i < count; ++i) {
        const int p = (id == NON_CONTRACT_ROW) ? i : (id * 23) + PLAYERS_NC + i;
        QString label = QLatin1String(db_.players[p].name);
        const QString hint = UrlHint(db_.players[p].url);
        if (!hint.isEmpty()) {
            label += QStringLiteral(" | ") + hint;
        }
        ui_->LIST_PLAYERS->addItem(label);
    }
    OnLinkModeToggled();
}

void PlayerSelectDialog::OnPlayerSelected() {
    if (ui_->LIST_TEAMS->currentRow() != NON_CONTRACT_ROW) {
        ui_->LBL_ML_NATIONALITY->clear();
        return;
    }
    const int id = ui_->LIST_PLAYERS->currentRow();
    if (id < 0) {
        ui_->LBL_ML_NATIONALITY->clear();
        return;
    }

    // Which run of the non-contract pool this index falls in, and therefore
    // which team the player nominally belongs to.
    int seen = 0;
    int run = 0;
    while (seen + we2002::NC_PLAYER_COUNT[run] - 1 < id) {
        seen += we2002::NC_PLAYER_COUNT[run];
        ++run;
    }
    const int team = we2002::NC_TEAM_CODE[run];
    ui_->LBL_ML_NATIONALITY->setText(QStringLiteral("%1° (nazionality %2 - %3 )")
                                .arg(id + 1)
                                .arg(team)
                                .arg(QLatin1String(PICKER_TEAM_NAMES[team])));

    // Every team whose run starts at or before this player and is within the
    // one-byte position field can address them. Offering the choice is what
    // lets a free agent be linked under a different flag.
    ui_->CMB_NATIONALITY->clear();
    int offered = 0;
    for (int i = 0; i < 120; ++i) {
        const int start = we2002::START_LINK[i];
        if (start != -1 && start <= id && id - start < 255) {
            ui_->CMB_NATIONALITY->addItem(QLatin1String(PICKER_TEAM_NAMES[i]));
            nationality_codes_[offered] = i;
            ++offered;
        }
    }
    ui_->CMB_NATIONALITY->setCurrentIndex(0);
}

void PlayerSelectDialog::OnLinkModeToggled() {
    const bool linking = ui_->CHK_ML->isChecked();
    const bool non_contract =
        ui_->LIST_TEAMS->currentRow() == NON_CONTRACT_ROW;

    if (linking) {
        ui_->CHK_ML->setText(QStringLiteral("link"));
        ui_->CHK_COMPLETE_SWAP->setVisible(false);
        if (non_contract) {
            ui_->LBL_ML_NATIONALITY->setVisible(true);
            ui_->CHK_LK_DEF->setVisible(true);
            ui_->CHK_LK_NDEF->setVisible(true);
            ui_->CMB_NATIONALITY->setVisible(true);
            ui_->CHK_LK_DEF->setChecked(true);
        }
    } else {
        ui_->CHK_ML->setText(QStringLiteral("skill"));
        ui_->CHK_COMPLETE_SWAP->setVisible(true);
        ui_->LBL_ML_NATIONALITY->setVisible(false);
        ui_->CHK_LK_DEF->setVisible(false);
        ui_->CHK_LK_NDEF->setVisible(false);
        ui_->CMB_NATIONALITY->setVisible(false);
    }
    if (!non_contract) {
        ui_->LBL_ML_NATIONALITY->setVisible(false);
        ui_->CHK_LK_DEF->setVisible(false);
        ui_->CHK_LK_NDEF->setVisible(false);
        ui_->CMB_NATIONALITY->setVisible(false);
        ui_->CHK_LK_DEF->setChecked(false);
    }
}

void PlayerSelectDialog::OnSwapModeToggled() {
    ui_->CHK_COMPLETE_SWAP->setText(ui_->CHK_COMPLETE_SWAP->isChecked()
                             ? QStringLiteral("complete substitution")
                             : QStringLiteral("incomplete substitution"));
}

void PlayerSelectDialog::OnDefaultNationalityToggled() {
    ui_->CHK_LK_NDEF->setChecked(!ui_->CHK_LK_DEF->isChecked());
}

void PlayerSelectDialog::OnChangeNationalityToggled() {
    ui_->CHK_LK_DEF->setChecked(!ui_->CHK_LK_NDEF->isChecked());
}

// ---------------------------------------------------------------------------

void PlayerSelectDialog::MakeLink(int player, unsigned char* out) const {
    if (player > PLAYERS_NC - 1) {
        // Contracted: the link is simply (team, position within the squad).
        out[0] = static_cast<unsigned char>((player - PLAYERS_NC) / 23);
        out[1] = static_cast<unsigned char>((player - PLAYERS_NC) % 23);
        return;
    }
    if (ui_->CHK_LK_DEF->isChecked()) {
        // The team the free agent is filed under on the disc.
        int seen = 0;
        int run = 0;
        while (seen + we2002::NC_PLAYER_COUNT[run] <= player) {
            seen += we2002::NC_PLAYER_COUNT[run];
            ++run;
        }
        out[0] = static_cast<unsigned char>(we2002::NC_TEAM_CODE[run]);
        out[1] = static_cast<unsigned char>(player - seen + 23);
    } else {
        // Whichever team the user picked in the nationality combo.
        const int code = nationality_codes_[ui_->CMB_NATIONALITY->currentIndex()];
        out[0] = static_cast<unsigned char>(code);
        out[1] = static_cast<unsigned char>(
            ui_->LIST_PLAYERS->currentRow() - we2002::START_LINK[code] + 23);
    }
}

void PlayerSelectDialog::OnAccept() {
    const int team_row = ui_->LIST_TEAMS->currentRow();
    int chosen = ui_->LIST_PLAYERS->currentRow();
    if (team_row < 0 || chosen < 0) {
        return;
    }
    if (team_row != NON_CONTRACT_ROW) {
        chosen = team_row * 23 + chosen + PLAYERS_NC;
    }

    if (!link_mode_ || !ui_->CHK_ML->isChecked()) {
        if (ui_->CHK_COMPLETE_SWAP->isChecked()) {
            // "Complete substitution": the two players trade places, so the
            // squad the chosen player came from gets the one being replaced.
            we2002::Player spare;
            CopyPlayerFields(spare, db_.players[chosen], true);
            CopyPlayerFields(db_.players[chosen], db_.players[slot_player_], true);
            CopyPlayerFields(db_.players[slot_player_], spare, true);
        } else {
            // "Incomplete": the chosen player is duplicated into the slot and
            // stays where they were as well.
            CopyPlayerFields(db_.players[slot_player_], db_.players[chosen], true);
        }
    } else {
        MakeLink(chosen, &links_[link_pos_]);
    }
    accept();
}

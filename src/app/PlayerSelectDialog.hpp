// Port of selezDlg (legacy/mfc/selezDlg.cpp).
//
// Picks a player out of the whole pool and puts them in a squad slot. It has
// two quite different jobs depending on which kind of team asked for it:
//
//   * A national squad owns its players outright, so the dialog copies the
//     chosen player's record over the slot's record -- or swaps the two, if
//     "complete substitution" is ticked.
//   * A Master League club, the default template and the two all-star sides
//     all hold a table of two-byte links, so the dialog rewrites the link for
//     that slot instead and leaves both player records alone.
//
// The link form is the fiddly one. A link is (team code, position); positions
// 0..22 are that team's own squad, and 23 upwards index into the non-contract
// pool through the team's run in NC_TEAM_CODE / NC_PLAYER_COUNT. A given
// non-contract player is reachable from more than one team code, which is what
// the "default" / "change nat." pair chooses between.

#pragma once

#include <QDialog>

#include "we2002/Database.hpp"

namespace Ui {
class PlayerSelectDialog;
}

class PlayerSelectDialog : public QDialog {
    Q_OBJECT

public:
    /// Copy-or-swap form, for national squads.
    PlayerSelectDialog(we2002::Database& db, int slot_player, QWidget* parent = nullptr);
    /// Link-rewriting form. `links` is the team's 46-byte table and `link_pos`
    /// the byte offset of the slot being replaced.
    PlayerSelectDialog(we2002::Database& db, int slot_player, unsigned char* links,
                       int link_pos, QWidget* parent = nullptr);
    ~PlayerSelectDialog() override;

private slots:
    void OnTeamSelected();
    void OnPlayerSelected();
    void OnAccept();  ///< the "ok" button and the list's double-click
    void OnLinkModeToggled();
    void OnSwapModeToggled();
    void OnDefaultNationalityToggled();
    void OnChangeNationalityToggled();

private:
    void Build();
    /// Turn a pool index into the two link bytes. Port of trovaLK().
    void MakeLink(int player, unsigned char* out) const;

    Ui::PlayerSelectDialog* ui_;
    we2002::Database& db_;
    int slot_player_;
    unsigned char* links_{nullptr};
    int link_pos_{0};
    bool link_mode_{false};

    /// Team codes offered in the nationality combo for the currently selected
    /// non-contract player, in combo order. Port of the file-scope applk[].
    int nationality_codes_[120]{};
};

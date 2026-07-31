// Port of carattDlg (legacy/mfc/carattDlg.cpp).
//
// One player's attributes: name, look, position, the eighteen 12..19 skills,
// shirt number and transfer value. Every field commits on focus-out straight
// into the Player record -- there is no OK/Cancel, and there was none in the
// original either.
//
// The thirty-two killfocus handlers reduce to two, because the original had
// already factored the bodies into exitTXT() and exitCMB(); all that was left
// duplicated was the pairing of a control with a field.

#pragma once

#include <QDialog>

#include <vector>

#include "we2002/Database.hpp"
#include "we2002/Player.hpp"
#include "we2002/Sofifa.hpp"

class QComboBox;
class QLineEdit;

namespace Ui {
class PlayerSkillsDialog;
}

class PlayerSkillsDialog : public QDialog {
    Q_OBJECT

public:
    PlayerSkillsDialog(we2002::Database& db, std::vector<we2002::FifaPlayer>& fifa,
                       const we2002::SofifaRules& rules, int player,
                       QWidget* parent = nullptr);
    ~PlayerSkillsDialog() override;

private slots:
    void OnImportFromUrl();

private:
    void Load();  ///< carica()
    /// A skill box: clamped to 12..19, the range the disc encodes.
    void BindSkill(QLineEdit* box, int we2002::Player::*field);
    /// A combo whose index is the stored value outright.
    void BindChoice(QComboBox* combo, int we2002::Player::*field);

    Ui::PlayerSkillsDialog* ui_;
    we2002::Database& db_;
    std::vector<we2002::FifaPlayer>& fifa_;
    const we2002::SofifaRules& rules_;
    int player_;
};

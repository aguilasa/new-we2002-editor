// The tactics panel: the ten outfield slots, their roles and pitch positions,
// and the sixteen preset formations.
//
// Port of OnSelchangeTat2..11, OnKillfocusTat2..11, OnChangeTatx/Taty2..11,
// OnKillfocusTatx/Taty2..11, muovitattica(), applica_tatt() and the sixteen
// On451a..On532b wrappers -- 106 methods in the original, all of them the same
// method with a different index baked in.
//
// The formation blob is 30 bytes: ten roles, then ten x, then ten y. Slot 1 is
// the keeper and is not represented; array index 0 here is the resource's slot
// 2, which is why the original's control names run TAT2..TAT11.

#include <QComboBox>
#include <QGroupBox>
#include <QLineEdit>
#include <QPushButton>

#include "MainWindow.hpp"
#include "ui_MainDialog.h"

void MainWindow::OnRoleShown(int slot) {
    // CBN_SELCHANGE: the pitch button wears the role's abbreviation.
    cmd_slot_[slot]->setText(cmb_role_[slot]->currentText());
}

void MainWindow::OnRoleCommitted(int slot) {
    // Stored roles start at 2; the combo starts at role 1 in index 0.
    char* formation = SelectedFormation();
    if (formation != nullptr) {
        formation[slot] = static_cast<char>(cmb_role_[slot]->currentIndex() + 2);
    }
}

void MainWindow::PitchPosition(float x, float y, int* out_x, int* out_y) const {
    // Map disc coordinates onto the pitch group box, then centre the button on
    // the result. TCORRX/TCORRY were the original's fudge for the group box's
    // border; keeping them keeps the markers where ed.exe puts them.
    const QRect pitch = ui_->CAMPO_->geometry();
    const float step_x =
        static_cast<float>(pitch.width()) / (PITCH_X_MAX - PITCH_X_MIN);
    const float step_y =
        static_cast<float>(pitch.height()) / (PITCH_Y_MAX - PITCH_Y_MIN);
    *out_x = pitch.left() + static_cast<int>(step_x * x) - SLOT_BUTTON_W / 2 +
             PITCH_NUDGE_X;
    *out_y = pitch.top() + static_cast<int>(step_y * y) - SLOT_BUTTON_H / 2 +
             PITCH_NUDGE_Y;
}

void MainWindow::OnSlotMoved(int slot) {
    const float x =
        static_cast<float>(txt_slot_x_[slot]->text().toInt() - PITCH_X_MIN);
    const float y =
        static_cast<float>(txt_slot_y_[slot]->text().toInt() - PITCH_Y_MIN);
    int px = 0;
    int py = 0;
    PitchPosition(x, y, &px, &py);
    // BTW/BTH, not the button's own size: the original overrode the .rc
    // geometry every time it moved a marker.
    cmd_slot_[slot]->setGeometry(px, py, SLOT_BUTTON_W, SLOT_BUTTON_H);
}

void MainWindow::OnSlotXCommitted(int slot) {
    int value = txt_slot_x_[slot]->text().toInt();
    if (value < PITCH_X_MIN) {
        value = PITCH_X_MIN;
        txt_slot_x_[slot]->setText(QString::number(value));
    }
    if (value > PITCH_X_MAX) {
        value = PITCH_X_MAX;
        txt_slot_x_[slot]->setText(QString::number(value));
    }
    char* formation = SelectedFormation();
    if (formation != nullptr) {
        formation[10 + slot] = static_cast<char>(value);
    }
}

void MainWindow::OnSlotYCommitted(int slot) {
    int value = txt_slot_y_[slot]->text().toInt();
    if (value < PITCH_Y_MIN) {
        value = PITCH_Y_MIN;
        txt_slot_y_[slot]->setText(QString::number(value));
    }
    if (value > PITCH_Y_MAX) {
        value = PITCH_Y_MAX;
        txt_slot_y_[slot]->setText(QString::number(value));
    }
    char* formation = SelectedFormation();
    if (formation != nullptr) {
        formation[20 + slot] = static_cast<char>(value);
    }
}

void MainWindow::ApplyPresetFormation(int k) {
    if (SelectedTeam() <= 0) {
        return;
    }
    char* formation = SelectedFormation();
    if (formation == nullptr) {
        return;
    }
    const we2002::Formation& preset = db_.preset_formations[k];
    for (int i = 0; i < 10; ++i) {
        // roles[0] is the keeper, which the ten editable slots skip.
        formation[i] = preset.roles[i + 1];
        formation[10 + i] = preset.x[i];
        formation[20 + i] = preset.y[i];
    }
    OnTeamSelected();
}

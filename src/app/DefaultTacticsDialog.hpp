// Port of tattDlg (legacy/mfc/tattDlg.cpp).
//
// Edits the sixteen preset formations that the main dialog's TACT1..16 buttons
// apply. Same pitch widget as the main dialog, one formation at a time, plus
// import/export of a single formation as a .t2002 file.

#pragma once

#include <QDialog>

#include "we2002/Team.hpp"

class QComboBox;
class QKeyEvent;
class QLineEdit;
class QPushButton;

namespace Ui {
class DefaultTacticsDialog;
}

class DefaultTacticsDialog : public QDialog {
    Q_OBJECT

public:
    DefaultTacticsDialog(we2002::Formation* formations, QWidget* parent = nullptr);
    ~DefaultTacticsDialog() override;

protected:
    void keyPressEvent(QKeyEvent* event) override;

private slots:
    void OnFormationSelected();
    void OnNameEdited();
    void OnImport();
    void OnExport();

private:
    void Load();
    void MoveMarker(int slot);
    int Current() const;

    Ui::DefaultTacticsDialog* ui_;
    we2002::Formation* formations_;

    QComboBox* cmb_role_[10]{};
    QLineEdit* txt_slot_x_[10]{};
    QLineEdit* txt_slot_y_[10]{};
    QPushButton* cmd_slot_[10]{};
};

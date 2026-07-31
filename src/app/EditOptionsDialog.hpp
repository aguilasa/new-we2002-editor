// Port of editOptForm (legacy/mfc/editOptForm.cpp).
//
// Four checkboxes deciding which fields the three "edit all" commands are
// allowed to touch. The original had no OK button: it wrote each flag back on
// click and the caller kept the dialog as a member, so the settings survived
// however the window was dismissed. Same here -- the caller reads the getters
// after exec() and ignores the result code.

#pragma once

#include <QDialog>

namespace Ui {
class EditOptionsDialog;
}

class EditOptionsDialog : public QDialog {
    Q_OBJECT

public:
    explicit EditOptionsDialog(QWidget* parent = nullptr);
    ~EditOptionsDialog() override;

    void SetOptions(bool names, bool age_height_weight_foot, bool characteristics,
                    bool shirt_numbers);

    bool EditNames() const;
    bool EditAgeHeightWeightFoot() const;
    bool EditCharacteristics() const;
    bool EditShirtNumbers() const;

private:
    Ui::EditOptionsDialog* ui_;
};

#include "EditOptionsDialog.hpp"

#include <QCheckBox>

#include "ui_EditOptionsDialog.h"

EditOptionsDialog::EditOptionsDialog(QWidget* parent)
    : QDialog(parent), ui_(new Ui::EditOptionsDialog) {
    ui_->setupUi(this);
    setFixedSize(size());
}

EditOptionsDialog::~EditOptionsDialog() {
    delete ui_;
}

void EditOptionsDialog::SetOptions(bool names, bool age_height_weight_foot,
                                   bool characteristics, bool shirt_numbers) {
    ui_->CHK_EDITNAME->setChecked(names);
    ui_->CHK_EDITLOOK->setChecked(age_height_weight_foot);
    ui_->CHK_EDITCHAR->setChecked(characteristics);
    ui_->CHK_EDITNUMS->setChecked(shirt_numbers);
}

bool EditOptionsDialog::EditNames() const {
    return ui_->CHK_EDITNAME->isChecked();
}

bool EditOptionsDialog::EditAgeHeightWeightFoot() const {
    return ui_->CHK_EDITLOOK->isChecked();
}

bool EditOptionsDialog::EditCharacteristics() const {
    return ui_->CHK_EDITCHAR->isChecked();
}

bool EditOptionsDialog::EditShirtNumbers() const {
    return ui_->CHK_EDITNUMS->isChecked();
}

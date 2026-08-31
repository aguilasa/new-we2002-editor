#include "DefaultTacticsDialog.hpp"

#include <QComboBox>
#include <QFile>
#include <QFileDialog>
#include <QGroupBox>
#include <QKeyEvent>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>
#include <QSignalBlocker>

#include <cstring>

#include "Bind.hpp"
#include "MainWindow.hpp"  // the pitch constants, shared with the main dialog
#include "we2002/Tables.hpp"
#include "ui_DefaultTacticsDialog.h"

namespace {

/// The .t2002 single-formation file: an eight-byte magic and a 44-byte record.
///
/// The record is a straight memory image of the original's `tattica` class as
/// 32-bit MSVC laid it out -- four bytes of vtable pointer (the class has a
/// virtual destructor), then the name (7 bytes), the eleven roles, the ten x
/// and the ten y, then two bytes of tail padding. The vptr is a process
/// address: it meant nothing in the file then and means nothing now, so it is
/// written as zero and skipped on read. Everything a reader cares about lands
/// at the byte it always did.
///
/// The 4 and the 44 are the 32-bit numbers, and they are the right ones: the
/// original's own importer validates the length against a literal 52
/// (legacy/mfc/tattDlg.cpp:701), which is 8 + sizeof(tattica) with a 4-byte
/// vptr. Debug/ed.exe is an x86-64 rebuild of that source, where the vptr
/// grows to 8 and sizeof(tattica) to 48, so it EXPORTS 56 bytes and then
/// refuses its own file -- while accepting the 52-byte one this code writes.
/// Do not "fix" these to 8 and 56: that would make the port emit the file the
/// original rejects. See CORR-WTE-132.
constexpr char MAGIC[8] = {'f', '.', 'm', '.', 't', 'a', 't', 't'};
constexpr int RECORD_BYTES = 44;
constexpr int FILE_BYTES = static_cast<int>(sizeof(MAGIC)) + RECORD_BYTES;
constexpr int VPTR_BYTES = 4;

}  // namespace

DefaultTacticsDialog::DefaultTacticsDialog(we2002::Formation* formations,
                                           QWidget* parent)
    : QDialog(parent), ui_(new Ui::DefaultTacticsDialog), formations_(formations) {
    ui_->setupUi(this);
    setFixedSize(size());

    // These were TCMB_TAT/TTXT_TATX/TTXT_TATY/TCMD_VT in ed.rc; the T kept
    // them out of the main dialog's way in one flat resource namespace, which
    // stopped mattering once each form became its own class.
    for (int i = 0; i < 10; ++i) {
        cmb_role_[i] = Bind<QComboBox>(this, "CMB_SLOT_ROLE%d", i + 2);
        txt_slot_x_[i] = Bind<QLineEdit>(this, "TXT_SLOT_X%d", i + 2);
        txt_slot_y_[i] = Bind<QLineEdit>(this, "TXT_SLOT_Y%d", i + 2);
        cmd_slot_[i] = Bind<QPushButton>(this, "CMD_SLOT%d", i + 1);

        for (int r = 1; r < we2002::N_ROLES; ++r) {
            cmb_role_[i]->addItem(QLatin1String(we2002::ROLE_NAMES[r]));
        }
        txt_slot_x_[i]->setMaxLength(2);
        txt_slot_y_[i]->setMaxLength(3);

        connect(cmb_role_[i], &QComboBox::currentIndexChanged, this,
                [this, i](int index) {
                    cmd_slot_[i]->setText(cmb_role_[i]->itemText(index));
                    if (cmb_role_[i]->hasFocus()) {
                        formations_[Current()].roles[i + 1] =
                            static_cast<char>(index + 2);
                    }
                });
        connect(txt_slot_x_[i], &QLineEdit::textChanged, this,
                [this, i] { MoveMarker(i); });
        connect(txt_slot_y_[i], &QLineEdit::textChanged, this,
                [this, i] { MoveMarker(i); });
        connect(txt_slot_x_[i], &QLineEdit::editingFinished, this, [this, i] {
            const int v = qBound(PITCH_X_MIN, txt_slot_x_[i]->text().toInt(),
                                 PITCH_X_MAX);
            txt_slot_x_[i]->setText(QString::number(v));
            formations_[Current()].x[i] = static_cast<char>(v);
        });
        connect(txt_slot_y_[i], &QLineEdit::editingFinished, this, [this, i] {
            const int v = qBound(PITCH_Y_MIN, txt_slot_y_[i]->text().toInt(),
                                 PITCH_Y_MAX);
            txt_slot_y_[i]->setText(QString::number(v));
            formations_[Current()].y[i] = static_cast<char>(v);
        });
    }

    ui_->TXT_FORMATION_NAME->setMaxLength(6);
    for (int i = 0; i < 16; ++i) {
        ui_->CMB_FORMATION->addItem(QLatin1String(formations_[i].name));
    }

    connect(ui_->CMB_FORMATION, &QComboBox::currentIndexChanged, this,
            &DefaultTacticsDialog::OnFormationSelected);
    connect(ui_->TXT_FORMATION_NAME, &QLineEdit::editingFinished, this,
            &DefaultTacticsDialog::OnNameEdited);
    connect(ui_->CMD_IMP, &QPushButton::clicked, this,
            &DefaultTacticsDialog::OnImport);
    connect(ui_->CMD_EXP, &QPushButton::clicked, this,
            &DefaultTacticsDialog::OnExport);
    connect(ui_->IDOK, &QPushButton::clicked, this, &QDialog::accept);

    ui_->CMB_FORMATION->setCurrentIndex(0);
    Load();
}

DefaultTacticsDialog::~DefaultTacticsDialog() {
    delete ui_;
}

void DefaultTacticsDialog::keyPressEvent(QKeyEvent* event) {
    // Return confirms the dialog, which is the only way out of it.
    //
    // ed.rc:627 declares the OK button NOT WS_VISIBLE, and rc2ui.py translates
    // that faithfully. In MFC an invisible DEFPUSHBUTTON is still the dialog's
    // default, so Return reaches IDOK and EndDialog runs; Qt skips a default
    // button that is not visible -- measured with setDefault(true) on this very
    // button, which changed nothing. Without a way out, exec() kept blocking
    // the main dialog and the write button could not be reached at all: the
    // preset edits, which are already committed field by field into
    // db_.preset_formations, never got a chance to be saved. See CORR-WTE-131.
    //
    // The key event only arrives here after the focused QLineEdit has ignored
    // it, and QLineEdit emits returnPressed/editingFinished first -- so the
    // field being typed into is committed before the dialog closes, which is
    // the order the original had too.
    if ((event->key() == Qt::Key_Return || event->key() == Qt::Key_Enter) &&
        (event->modifiers() & ~Qt::KeypadModifier) == Qt::NoModifier) {
        accept();
        return;
    }
    // Escape and everything else stay with QDialog, which rejects on Escape --
    // the same exit IDCANCEL gave in the original.
    QDialog::keyPressEvent(event);
}

int DefaultTacticsDialog::Current() const {
    return qMax(0, ui_->CMB_FORMATION->currentIndex());
}

void DefaultTacticsDialog::OnFormationSelected() {
    Load();
}

void DefaultTacticsDialog::Load() {
    const we2002::Formation& f = formations_[Current()];
    ui_->TXT_FORMATION_NAME->setText(QLatin1String(f.name));
    for (int i = 0; i < 10; ++i) {
        const QSignalBlocker block(cmb_role_[i]);
        cmb_role_[i]->setCurrentIndex(f.roles[i + 1] - 2);
        cmd_slot_[i]->setText(cmb_role_[i]->currentText());
        txt_slot_x_[i]->setText(QString::number(static_cast<int>(f.x[i])));
        txt_slot_y_[i]->setText(QString::number(static_cast<int>(f.y[i])));
    }
}

void DefaultTacticsDialog::OnNameEdited() {
    we2002::Formation& f = formations_[Current()];
    const QByteArray text = ui_->TXT_FORMATION_NAME->text().toLatin1();
    std::snprintf(f.name, sizeof(f.name), "%s", text.constData());
    // The combo names the formations, so it has to follow the rename.
    const QSignalBlocker block(ui_->CMB_FORMATION);
    ui_->CMB_FORMATION->setItemText(Current(), QLatin1String(f.name));
}

void DefaultTacticsDialog::MoveMarker(int slot) {
    const QRect pitch = ui_->PITCH->geometry();
    const float x =
        static_cast<float>(txt_slot_x_[slot]->text().toInt() - PITCH_X_MIN);
    const float y =
        static_cast<float>(txt_slot_y_[slot]->text().toInt() - PITCH_Y_MIN);
    const float step_x =
        static_cast<float>(pitch.width()) / (PITCH_X_MAX - PITCH_X_MIN);
    const float step_y =
        static_cast<float>(pitch.height()) / (PITCH_Y_MAX - PITCH_Y_MIN);
    cmd_slot_[slot]->setGeometry(
        pitch.left() + static_cast<int>(step_x * x) - SLOT_BUTTON_W / 2 +
            PITCH_NUDGE_X,
        pitch.top() + static_cast<int>(step_y * y) - SLOT_BUTTON_H / 2 +
            PITCH_NUDGE_Y,
        SLOT_BUTTON_W, SLOT_BUTTON_H);
}

// ---------------------------------------------------------------------------

void DefaultTacticsDialog::OnImport() {
    const QString path = QFileDialog::getOpenFileName(
        this, QStringLiteral("TACTIC FILE TO IMPORT"), QString(),
        QStringLiteral("tactic file MANIA 2002 (*.t2002)"));
    if (path.isEmpty()) {
        return;
    }
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly)) {
        QMessageBox::warning(this, windowTitle(), QStringLiteral("Not right file !"));
        return;
    }
    const QByteArray blob = file.readAll();
    if (blob.size() != FILE_BYTES ||
        std::memcmp(blob.constData(), MAGIC, sizeof(MAGIC)) != 0) {
        QMessageBox::warning(this, windowTitle(), QStringLiteral("Not right file !"));
        return;
    }

    const char* rec = blob.constData() + sizeof(MAGIC) + VPTR_BYTES;
    we2002::Formation& f = formations_[Current()];
    std::memcpy(f.name, rec, sizeof(f.name));
    std::memcpy(f.roles, rec + sizeof(f.name), sizeof(f.roles));
    std::memcpy(f.x, rec + sizeof(f.name) + sizeof(f.roles), sizeof(f.x));
    std::memcpy(f.y, rec + sizeof(f.name) + sizeof(f.roles) + sizeof(f.x),
                sizeof(f.y));

    Load();
    OnNameEdited();
    QMessageBox::information(this, windowTitle(),
                             QStringLiteral("Tactic imported !"));
}

void DefaultTacticsDialog::OnExport() {
    QString path = QFileDialog::getSaveFileName(
        this, QStringLiteral("TACTIC FILE TO EXPORT"), QString(),
        QStringLiteral("tactic file MANIA 2002 (*.t2002)"));
    if (path.isEmpty()) {
        return;
    }
    if (!path.endsWith(QLatin1String(".t2002"))) {
        path += QLatin1String(".t2002");
    }
    QFile file(path);
    if (!file.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        return;
    }

    const we2002::Formation& f = formations_[Current()];
    QByteArray blob(FILE_BYTES, '\0');
    char* out = blob.data();
    std::memcpy(out, MAGIC, sizeof(MAGIC));
    char* rec = out + sizeof(MAGIC) + VPTR_BYTES;
    std::memcpy(rec, f.name, sizeof(f.name));
    std::memcpy(rec + sizeof(f.name), f.roles, sizeof(f.roles));
    std::memcpy(rec + sizeof(f.name) + sizeof(f.roles), f.x, sizeof(f.x));
    std::memcpy(rec + sizeof(f.name) + sizeof(f.roles) + sizeof(f.x), f.y,
                sizeof(f.y));
    file.write(blob);

    QMessageBox::information(this, windowTitle(),
                             QStringLiteral("Tactic exported !"));
}

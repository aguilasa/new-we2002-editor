#include "FlagKitDialog.hpp"

#include <QFile>
#include <QFileDialog>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>

#include <cstring>

#include "ui_FlagKitPreviewDialog.h"

namespace {

/// .b2002: magic, one style byte, sixteen 16-bit colour words.
constexpr char FLAG_MAGIC[8] = {'f', '.', 'm', '.', 'b', 'a', 'n', 'd'};
constexpr int FLAG_FILE_BYTES = 8 + 1 + 32;
/// .m2002: magic and sixteen 16-bit colour words.
constexpr char KIT_MAGIC[8] = {'f', '.', 'm', '.', 'm', 'a', 'g', 'l'};
constexpr int KIT_FILE_BYTES = 8 + 32;

/// The palette words are stored little-endian on the disc and were written to
/// these files by memcpy on a little-endian machine, so the files are too.
void ReadWords(const char* src, unsigned short* dest, int count) {
    for (int i = 0; i < count; ++i) {
        dest[i] = static_cast<unsigned short>(
            static_cast<unsigned char>(src[i * 2]) |
            (static_cast<unsigned char>(src[i * 2 + 1]) << 8));
    }
}

void WriteWords(char* dest, const unsigned short* src, int count) {
    for (int i = 0; i < count; ++i) {
        dest[i * 2] = static_cast<char>(src[i] & 0xFF);
        dest[i * 2 + 1] = static_cast<char>((src[i] >> 8) & 0xFF);
    }
}

}  // namespace

FlagKitDialog::FlagKitDialog(int team_id, char& flag_shape,
                             unsigned short* flag_colours, unsigned short* home_kit,
                             unsigned short* away_kit, QWidget* parent)
    : QDialog(parent), ui_(new Ui::FlagKitPreviewDialog), team_id_(team_id),
      flag_shape_(flag_shape), flag_colours_(flag_colours) {
    ui_->setupUi(this);
    setFixedSize(size());
    kit_[0] = home_kit;
    kit_[1] = away_kit;

    for (int i = 0; i < 15; ++i) {
        txt_flag_[i] =
            findChild<QLineEdit*>(QString::asprintf("TXT_BAND_COL%d", i + 1));
        txt_flag_[i]->setMaxLength(5);  // 65535
        connect(txt_flag_[i], &QLineEdit::editingFinished, this, [this, i] {
            const int v = qMin(txt_flag_[i]->text().toInt(), 65535);
            if (v == 65535) {
                txt_flag_[i]->setText(QStringLiteral("65535"));
            }
            flag_colours_[i] = static_cast<unsigned short>(v);
        });
    }
    for (int k = 0; k < 2; ++k) {
        for (int i = 0; i < 14; ++i) {
            txt_kit_[k][i] = findChild<QLineEdit*>(
                QString::asprintf("TXT_%dMAG_COL%d", k + 1, i + 1));
            txt_kit_[k][i]->setMaxLength(5);
            connect(txt_kit_[k][i], &QLineEdit::editingFinished, this, [this, k, i] {
                const int v = qMin(txt_kit_[k][i]->text().toInt(), 65535);
                if (v == 65535) {
                    txt_kit_[k][i]->setText(QStringLiteral("65535"));
                }
                // Words 0 and 1 are not exposed, hence the +2.
                kit_[k][i + 2] = static_cast<unsigned short>(v);
            });
        }
    }

    ui_->TXT_BAND_STILE->setMaxLength(2);
    connect(ui_->TXT_BAND_STILE, &QLineEdit::editingFinished, this, [this] {
        flag_shape_ = static_cast<char>(ui_->TXT_BAND_STILE->text().toInt());
    });

    connect(ui_->IDC_BUTTONINB, &QPushButton::clicked, this,
            &FlagKitDialog::OnImportFlag);
    connect(ui_->IDC_BUTTONESB, &QPushButton::clicked, this,
            &FlagKitDialog::OnExportFlag);
    connect(ui_->IDC_BUTTON1IM, &QPushButton::clicked, this,
            [this] { ImportKit(0); });
    connect(ui_->IDC_BUTTON1EM, &QPushButton::clicked, this,
            [this] { ExportKit(0); });
    connect(ui_->IDC_BUTTON2IM, &QPushButton::clicked, this,
            [this] { ImportKit(1); });
    connect(ui_->IDC_BUTTON2EM, &QPushButton::clicked, this,
            [this] { ExportKit(1); });
    connect(ui_->IDOK, &QPushButton::clicked, this, &QDialog::accept);

    if (!HasOwnFlag()) {
        for (QLineEdit* box : txt_flag_) {
            box->setEnabled(false);
        }
    }
    Load();
}

FlagKitDialog::~FlagKitDialog() {
    delete ui_;
}

bool FlagKitDialog::HasOwnFlag() const {
    // Teams 57..63 are the classic sides; 69 is Newcastle and 86 is Parma.
    // The original's two guards for this disagree at the edges -- OnInitDialog
    // greys the boxes for id 57..63, while the flag import/export refuses for
    // 56..63. 56 is the World All-Stars, which has no flag of its own either,
    // so the wider test is the correct one and is used for both here.
    return team_id_ > 0 && team_id_ != 69 && team_id_ != 86 &&
           (team_id_ < 56 || team_id_ > 63);
}

void FlagKitDialog::Load() {
    ui_->TXT_BAND_STILE->setText(QString::number(static_cast<int>(flag_shape_)));
    for (int i = 0; i < 15; ++i) {
        txt_flag_[i]->setText(QString::number(flag_colours_[i]));
    }
    for (int k = 0; k < 2; ++k) {
        for (int i = 0; i < 14; ++i) {
            txt_kit_[k][i]->setText(QString::number(kit_[k][i + 2]));
        }
    }
}

// ---------------------------------------------------------------------------

void FlagKitDialog::OnImportFlag() {
    if (!HasOwnFlag()) {
        QMessageBox::warning(
            this, windowTitle(),
            QStringLiteral("Choose a team (that has \"indipendent\" flag too) !"));
        return;
    }
    const QString path = QFileDialog::getOpenFileName(
        this, QStringLiteral("FLAG FILE TO IMPORT"), QString(),
        QStringLiteral("flag file MANIA 2002 (*.b2002)"));
    if (path.isEmpty()) {
        return;
    }
    QFile file(path);
    QByteArray blob;
    if (file.open(QIODevice::ReadOnly)) {
        blob = file.readAll();
    }
    if (blob.size() != FLAG_FILE_BYTES ||
        std::memcmp(blob.constData(), FLAG_MAGIC, sizeof(FLAG_MAGIC)) != 0) {
        QMessageBox::warning(this, windowTitle(), QStringLiteral("Not right file !"));
        return;
    }
    flag_shape_ = blob[static_cast<int>(sizeof(FLAG_MAGIC))];
    ReadWords(blob.constData() + sizeof(FLAG_MAGIC) + 1, flag_colours_, 16);
    Load();
    QMessageBox::information(this, windowTitle(), QStringLiteral("Flag imported !"));
}

void FlagKitDialog::OnExportFlag() {
    if (!HasOwnFlag()) {
        QMessageBox::warning(
            this, windowTitle(),
            QStringLiteral("Choose a team (that has \"indipendent\" flag too) !"));
        return;
    }
    QString path = QFileDialog::getSaveFileName(
        this, QStringLiteral("FLAG FILE TO EXPORT"), QString(),
        QStringLiteral("flag file MANIA 2002 (*.b2002)"));
    if (path.isEmpty()) {
        return;
    }
    if (!path.endsWith(QLatin1String(".b2002"))) {
        path += QLatin1String(".b2002");
    }
    QByteArray blob(FLAG_FILE_BYTES, '\0');
    std::memcpy(blob.data(), FLAG_MAGIC, sizeof(FLAG_MAGIC));
    blob[static_cast<int>(sizeof(FLAG_MAGIC))] = flag_shape_;
    WriteWords(blob.data() + sizeof(FLAG_MAGIC) + 1, flag_colours_, 16);

    QFile file(path);
    if (file.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        file.write(blob);
        QMessageBox::information(this, windowTitle(),
                                 QStringLiteral("Flag exported !"));
    }
}

void FlagKitDialog::ImportKit(int which) {
    const QString path = QFileDialog::getOpenFileName(
        this, QStringLiteral("SHIRT FILE TO IMPORT"), QString(),
        QStringLiteral("shirt file MANIA 2002 (*.m2002)"));
    if (path.isEmpty()) {
        return;
    }
    QFile file(path);
    QByteArray blob;
    if (file.open(QIODevice::ReadOnly)) {
        blob = file.readAll();
    }
    if (blob.size() != KIT_FILE_BYTES ||
        std::memcmp(blob.constData(), KIT_MAGIC, sizeof(KIT_MAGIC)) != 0) {
        QMessageBox::warning(this, windowTitle(), QStringLiteral("Not right file!"));
        return;
    }
    ReadWords(blob.constData() + sizeof(KIT_MAGIC), kit_[which], 16);
    Load();
    QMessageBox::information(this, windowTitle(), QStringLiteral("Shirt imported !"));
}

void FlagKitDialog::ExportKit(int which) {
    QString path = QFileDialog::getSaveFileName(
        this, QStringLiteral("SHIRT FILE TO EXPORT"), QString(),
        QStringLiteral("shirt file MANIA 2002 (*.m2002)"));
    if (path.isEmpty()) {
        return;
    }
    if (!path.endsWith(QLatin1String(".m2002"))) {
        path += QLatin1String(".m2002");
    }
    QByteArray blob(KIT_FILE_BYTES, '\0');
    std::memcpy(blob.data(), KIT_MAGIC, sizeof(KIT_MAGIC));
    WriteWords(blob.data() + sizeof(KIT_MAGIC), kit_[which], 16);

    QFile file(path);
    if (file.open(QIODevice::WriteOnly | QIODevice::Truncate)) {
        file.write(blob);
        QMessageBox::information(this, windowTitle(),
                                 QStringLiteral("Shirt exported !"));
    }
}

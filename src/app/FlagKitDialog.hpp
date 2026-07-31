// Port of graf (legacy/mfc/graf.cpp).
//
// The flag and the two kits, as raw 16-bit palette words. No picture is drawn
// -- the original called this a "preview" but only ever showed the numbers,
// and reproducing the PSX texture format is well outside a port.
//
// The arrays are 16 words each. The flag uses words 0..14 (the fifteenth is
// not shown) and each kit uses words 2..15, so the kit boxes are offset by two
// against their index. That is the disc layout, not a mistake.

#pragma once

#include <QDialog>

class QLineEdit;

namespace Ui {
class FlagKitPreviewDialog;
}

class FlagKitDialog : public QDialog {
    Q_OBJECT

public:
    /// `team_id` is the main dialog's selection index; it decides whether the
    /// flag is editable at all.
    FlagKitDialog(int team_id, char& flag_shape, unsigned short* flag_colours,
                  unsigned short* home_kit, unsigned short* away_kit,
                  QWidget* parent = nullptr);
    ~FlagKitDialog() override;

private slots:
    void OnImportFlag();
    void OnExportFlag();

private:
    void Load();
    void ImportKit(int which);
    void ExportKit(int which);
    /// True when this team owns its flag. The nine classic sides share the
    /// modern nations' flags, and Newcastle (69) and Parma (86) borrow one
    /// too, so for those the colours are read-only.
    bool HasOwnFlag() const;

    Ui::FlagKitPreviewDialog* ui_;
    int team_id_;
    char& flag_shape_;
    unsigned short* flag_colours_;
    unsigned short* kit_[2]{};

    QLineEdit* txt_flag_[15]{};
    QLineEdit* txt_kit_[2][14]{};
};

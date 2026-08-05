// Construction, widget binding and the handlers that did not fit anywhere
// else. See MainWindow.hpp for the shape of the port.

#include "MainWindow.hpp"

#include <QComboBox>
#include <QEvent>
#include <QFileDialog>
#include <QFileInfo>
#include <QLabel>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>
#include <QRegularExpression>
#include <QRegularExpressionValidator>

#include <fstream>
#include <string>

#include "Bind.hpp"
#include "DefaultTacticsDialog.hpp"
#include "EditOptionsDialog.hpp"
#include "QtPath.hpp"
#include "we2002/Tables.hpp"
#include "we2002/Types.hpp"
#include "ui_MainDialog.h"

using we2002::PLAYERS_NC;
using we2002::PLAYERS_TOTAL;
using we2002::ROLE_NAMES;
using we2002::TEAM_NAMES;
using we2002::TEAMS_ALLSTAR;
using we2002::TEAMS_ML;
using we2002::TEAMS_NATIONAL;

namespace {

/// The original's file-size check. It only warns: ed.exe carries on and loads
/// the image anyway, and images that are not exactly this long still work if
/// the layout matches.
constexpr qint64 EXPECTED_IMAGE_BYTES = 474431328;

}  // namespace

MainWindow::MainWindow(QWidget* parent)
    : QDialog(parent), ui_(new Ui::MainDialog) {
    ui_->setupUi(this);
    // The form carries absolute geometry transcribed from ed.rc; it is not a
    // layout and must not be resized into one.
    setFixedSize(size());
    BindWidgets();
    ConnectSignals();
    InitLimits();
    FillRoleCombos();
}

MainWindow::~MainWindow() {
    delete ui_;
}

// ---------------------------------------------------------------------------
// Widget binding
// ---------------------------------------------------------------------------

void MainWindow::BindWidgets() {
    // objectNames come from tools/glossary.py's UI_CONTROLS, applied by
    // tools/rc2ui.py when it generates the forms. Each control's original
    // ed.rc symbol is still recorded in ui/controls.json as `id`, so a name
    // can be traced back to the resource script it came from.
    //
    // The families below were CMD_CARAT/CMD_SOST/CMB_TAT/TXT_TATX/TXT_TATY/
    // CMD_VT/TXT_GIOC/TXT_NSQUAD/LAB_NSQUAD/TXT_NSQUAD_A there.
    const auto edit = [this](const char* fmt, int n) {
        return Bind<QLineEdit>(this, fmt, n);
    };
    const auto button = [this](const char* fmt, int n) {
        return Bind<QPushButton>(this, fmt, n);
    };

    for (int i = 0; i < 23; ++i) {
        txt_player_[i] = edit("TXT_PLAYER%d", i + 1);
        txt_url_[i] = edit("TXT_URL%d", i + 1);
        txt_number_[i] = edit("TXT_NUM%d", i + 1);
        cmd_skills_[i] = button("CMD_SKILLS%d", i + 1);
        cmd_swap_[i] = button("CMD_SWAP%d", i + 1);
    }
    // Tactics slots are numbered 2..11 in the resource: slot 1 is the keeper,
    // whose position is not editable. Array index 0 is resource slot 2.
    for (int i = 0; i < 10; ++i) {
        cmb_role_[i] = Bind<QComboBox>(this, "CMB_SLOT_ROLE%d", i + 2);
        txt_slot_x_[i] = edit("TXT_SLOT_X%d", i + 2);
        txt_slot_y_[i] = edit("TXT_SLOT_Y%d", i + 2);
        cmd_slot_[i] = button("CMD_SLOT%d", i + 1);
    }
    for (int i = 0; i < 16; ++i) {
        cmd_preset_[i] = button("CMD_TACT%d", i + 1);
    }
    for (int i = 0; i < 6; ++i) {
        txt_team_name_[i] = edit("TXT_TEAM_NAME%d", i + 1);
        lab_team_name_[i] = Bind<QLabel>(this, "LAB_TEAM_NAME%d", i + 1);
    }
    for (int i = 0; i < 3; ++i) {
        txt_abbrev_[i] = edit("TXT_TEAM_ABBREV%d", i + 1);
    }

    static const char* const kBars[5] = {"TXT_BAR_OFF", "TXT_BAR_DEF", "TXT_BAR_POW",
                                         "TXT_BAR_SPE", "TXT_BAR_TEC"};
    for (int i = 0; i < 5; ++i) {
        txt_bar_[i] = Bind<QLineEdit>(this, QLatin1String(kBars[i]));
    }
    // Order matters: it is the order the commit handler switches on, and it
    // matches Team's kick_long_fk / kick_short_fk / kick_left_corner /
    // kick_right_corner / kick_penalty / captain.
    static const char* const kKickers[6] = {"CMB_KICK_LONG_FK",  "CMB_KICK_SHORT_FK",
                                            "CMB_KICK_LEFT_CORNER", "CMB_KICK_RIGHT_CORNER",
                                            "CMB_KICK_PENALTY",   "CMB_CAPTAIN"};
    for (int i = 0; i < 6; ++i) {
        cmb_kicker_[i] = Bind<QComboBox>(this, QLatin1String(kKickers[i]));
    }
}

void MainWindow::ConnectSignals() {
    connect(ui_->CMB_TEAM, &QComboBox::currentIndexChanged, this,
            &MainWindow::OnTeamSelected);

    for (int i = 0; i < 23; ++i) {
        // EN_CHANGE in the original, but only the user's edits matter here --
        // the load path writes the same value back, so textEdited is both
        // equivalent and cheaper.
        connect(txt_url_[i], &QLineEdit::textEdited, this,
                [this, i] { OnPlayerUrlEdited(i); });
        connect(txt_number_[i], &QLineEdit::editingFinished, this,
                [this, i] { OnSquadNumberEdited(i); });
        connect(cmd_skills_[i], &QPushButton::clicked, this,
                [this, i] { OnPlayerSkills(i); });
        connect(cmd_swap_[i], &QPushButton::clicked, this,
                [this, i] { OnPlayerSwap(i); });
    }

    for (int i = 0; i < 10; ++i) {
        // CBN_SELCHANGE: repaint the pitch button's caption. Unlike the
        // original this also fires on setCurrentIndex, which is exactly what
        // the explicit OnSelchangeTat2..11 calls at the end of
        // OnSelezioneSquadraV were there to do by hand.
        connect(cmb_role_[i], &QComboBox::currentIndexChanged, this,
                [this, i] { OnRoleShown(i); });
        cmb_role_[i]->installEventFilter(this);

        // EN_CHANGE: must fire on programmatic setText too, because that is
        // how the pitch redraws when a team is loaded.
        connect(txt_slot_x_[i], &QLineEdit::textChanged, this,
                [this, i] { OnSlotMoved(i); });
        connect(txt_slot_y_[i], &QLineEdit::textChanged, this,
                [this, i] { OnSlotMoved(i); });
        connect(txt_slot_x_[i], &QLineEdit::editingFinished, this,
                [this, i] { OnSlotXCommitted(i); });
        connect(txt_slot_y_[i], &QLineEdit::editingFinished, this,
                [this, i] { OnSlotYCommitted(i); });
    }

    for (int i = 0; i < 16; ++i) {
        connect(cmd_preset_[i], &QPushButton::clicked, this,
                [this, i] { ApplyPresetFormation(i); });
    }
    for (int i = 0; i < 6; ++i) {
        connect(txt_team_name_[i], &QLineEdit::editingFinished, this,
                [this, i] { OnTeamNameEdited(i); });
        cmb_kicker_[i]->installEventFilter(this);
    }
    for (int i = 0; i < 3; ++i) {
        connect(txt_abbrev_[i], &QLineEdit::editingFinished, this,
                [this, i] { OnAbbreviationEdited(i); });
    }
    for (int i = 0; i < 5; ++i) {
        connect(txt_bar_[i], &QLineEdit::editingFinished, this,
                [this, i] { OnBarEdited(i); });
    }

    connect(ui_->TXT_TEAM_NAME_KANJI, &QLineEdit::editingFinished, this,
            &MainWindow::OnKanjiNameEdited);
    connect(ui_->TXT_TEAM_NAME_MIXED, &QLineEdit::editingFinished, this,
            &MainWindow::OnMixedCaseNameEdited);
    connect(ui_->TXT_ML_EXTRA_NAME1, &QLineEdit::editingFinished, this,
            [this] { OnMlExtraNameEdited(0); });
    connect(ui_->TXT_ML_EXTRA_NAME2, &QLineEdit::editingFinished, this,
            [this] { OnMlExtraNameEdited(1); });

    connect(ui_->CMD_COPY_TEAM_NAMES, &QPushButton::clicked, this,
            &MainWindow::OnCopyTeamNames);
    connect(ui_->CMB_WRITE, &QPushButton::clicked, this, &MainWindow::OnWriteCd);
    connect(ui_->CMB_RELOAD, &QPushButton::clicked, this, &MainWindow::OnReload);
    connect(ui_->CMD_DEFAULT_NUMBERS, &QPushButton::clicked, this, &MainWindow::OnDefaultNumbers);
    connect(ui_->CMD_UPDATE_COSTS, &QPushButton::clicked, this,
            &MainWindow::OnRecomputeCosts);
    connect(ui_->CMD_SORT_RESERVES, &QPushButton::clicked, this,
            &MainWindow::OnSortReserves);
    connect(ui_->CMD_FLAG_KIT, &QPushButton::clicked, this,
            &MainWindow::OnFlagKitPreview);
    connect(ui_->CMD_EDIT_PRESETS, &QPushButton::clicked, this,
            &MainWindow::OnPresetTactics);
    connect(ui_->CMB_SHOWEDITOPT, &QPushButton::clicked, this,
            &MainWindow::OnEditOptions);
    connect(ui_->CMB_IMPFIFAWEB, &QPushButton::clicked, this,
            &MainWindow::OnImportSofifaWeb);
    connect(ui_->CMB_IMPFIFATXT, &QPushButton::clicked, this,
            &MainWindow::OnImportSofifaTxt);
    connect(ui_->CMB_EDITALLTXT, &QPushButton::clicked, this,
            &MainWindow::OnEditAllFromFifa);
    connect(ui_->CMB_EDITALLLOOK, &QPushButton::clicked, this,
            &MainWindow::OnEditAllPlayersLook);
    connect(ui_->CMB_EDITALLBARS, &QPushButton::clicked, this,
            &MainWindow::OnEditAllBars);
}

bool MainWindow::eventFilter(QObject* watched, QEvent* event) {
    if (event->type() == QEvent::FocusOut) {
        for (int i = 0; i < 10; ++i) {
            if (watched == cmb_role_[i]) {
                OnRoleCommitted(i);
                break;
            }
        }
        for (int i = 0; i < 6; ++i) {
            if (watched == cmb_kicker_[i]) {
                OnKickerChanged(i);
                break;
            }
        }
    }
    return QDialog::eventFilter(watched, event);
}

void MainWindow::InitLimits() {
    // Maximum lengths come from OnInitDialog's LimitText calls.
    //
    // The digits-only validator is ES_NUMBER, which ed.rc sets on exactly the
    // 48 controls below -- the five bars, the 23 squad numbers and the twenty
    // pitch coordinates. tools/rc2ui.py deliberately left it out of the .ui
    // and recorded it in ui/controls.json instead, because in Qt it is a
    // validator rather than a widget property.
    static const QRegularExpression digits(QStringLiteral("[0-9]*"));
    const auto digits_only = [](QLineEdit* e) {
        e->setValidator(new QRegularExpressionValidator(digits, e));
    };

    for (int i = 0; i < 23; ++i) {
        txt_player_[i]->setMaxLength(10);
        txt_number_[i]->setMaxLength(2);
        digits_only(txt_number_[i]);
    }
    for (int i = 0; i < 3; ++i) {
        txt_abbrev_[i]->setMaxLength(3);
    }
    for (int i = 0; i < 5; ++i) {
        txt_bar_[i]->setMaxLength(1);
        digits_only(txt_bar_[i]);
    }
    for (int i = 0; i < 10; ++i) {
        txt_slot_x_[i]->setMaxLength(2);
        txt_slot_y_[i]->setMaxLength(3);
        digits_only(txt_slot_x_[i]);
        digits_only(txt_slot_y_[i]);
    }
}

void MainWindow::FillRoleCombos() {
    // Role 0 is "no role"; the combos start at 1, so the stored role is the
    // index plus two -- hence the +2/-2 that every tactics handler carries.
    for (int i = 0; i < 10; ++i) {
        cmb_role_[i]->clear();
        for (int r = 1; r < we2002::N_ROLES; ++r) {
            cmb_role_[i]->addItem(QLatin1String(ROLE_NAMES[r]));
        }
        cmb_role_[i]->setCurrentIndex(-1);
    }
}

void MainWindow::FillTeamCombo() {
    QComboBox* combo = ui_->CMB_TEAM;
    const QSignalBlocker block(combo);
    combo->clear();
    combo->addItem(QStringLiteral("---"));
    for (int i = 0; i < TEAMS_NATIONAL; ++i) {
        combo->addItem(QStringLiteral("Nation %1 - %2")
                           .arg(i + 1)
                           .arg(QLatin1String(TEAM_NAMES[i])));
    }
    for (int i = 0; i < TEAMS_ALLSTAR; ++i) {
        combo->addItem(QStringLiteral("All-star %1 - %2")
                           .arg(i + 1)
                           .arg(QLatin1String(TEAM_NAMES[i + 54])));
    }
    for (int i = 0; i < TEAMS_ML; ++i) {
        combo->addItem(QStringLiteral("Master League %1 - %2")
                           .arg(i + 1)
                           .arg(QLatin1String(TEAM_NAMES[i + 63])));
    }
    combo->addItem(QStringLiteral("Master League (default)"));
    combo->setCurrentIndex(0);
}

void MainWindow::RefreshPresetButtons() {
    for (int i = 0; i < 16; ++i) {
        cmd_preset_[i]->setText(QLatin1String(db_.preset_formations[i].name));
    }
}

// ---------------------------------------------------------------------------
// Loading
// ---------------------------------------------------------------------------

bool MainWindow::OpenImage(const QString& preselected) {
    const QString chosen =
        preselected.isEmpty()
            ? QFileDialog::getOpenFileName(
                  this, QStringLiteral("IMAGE CD SELECTION"), QString(),
                  QStringLiteral("WE2002 CD Image (we2002.bin);;Binary file "
                                 "(*.bin);;All file (*.*)"))
            : preselected;
    if (chosen.isEmpty()) {
        QMessageBox::warning(this, windowTitle(),
                             QStringLiteral("Impossible editing without CD image !"));
        return false;
    }
    if (QFileInfo(chosen).size() != EXPECTED_IMAGE_BYTES) {
        // A warning only, exactly as in the original -- it loads anyway.
        QMessageBox::warning(this, windowTitle(),
                             QStringLiteral("Not WE2002 CD image (474.431.328 bytes)! "
                                            "Suggest to close the program !"));
    }
    image_ = app::PathFromQString(chosen);

    if (!db_.Load(image_, [this](const std::string& m) {
            Report(QString::fromStdString(m));
        })) {
        QMessageBox::critical(this, windowTitle(),
                              QStringLiteral("Could not read the CD image."));
        return false;
    }
    LoadUrls();
    LoadSofifaFields();
    LoadSofifaConversionRules();

    fifa_players_.assign(PLAYERS_TOTAL, we2002::FifaPlayer{});

    FillTeamCombo();
    RefreshPresetButtons();
    return true;
}

void MainWindow::LoadUrls() {
    // The URLs are the fork's addition and live beside the image, not in it:
    // <image>.bin -> <image>_url.txt, one line per player, in player order.
    std::filesystem::path url_file = image_;
    if (url_file.extension() == ".bin") {
        url_file.replace_extension();
        url_file += "_url.txt";
    } else {
        url_file += "_url.txt";
    }

    std::ifstream in(url_file);
    for (int i = 0; i < PLAYERS_TOTAL; ++i) {
        std::string line;
        if (in && std::getline(in, line)) {
            // The disc field is a fixed char[500]; keep the original's
            // truncation rather than silently growing it.
            if (line.size() >= sizeof(db_.players[i].url)) {
                line.resize(sizeof(db_.players[i].url) - 1);
            }
            std::snprintf(db_.players[i].url, sizeof(db_.players[i].url), "%s",
                          line.c_str());
        } else {
            db_.players[i].url[0] = '\0';
        }
    }
}

void MainWindow::SaveUrls() const {
    std::filesystem::path url_file = image_;
    if (url_file.extension() == ".bin") {
        url_file.replace_extension();
        url_file += "_url.txt";
    } else {
        url_file += "_url.txt";
    }
    std::ofstream out(url_file, std::ios::trunc);
    if (!out) {
        return;
    }
    for (int i = 0; i < PLAYERS_TOTAL; ++i) {
        out << db_.players[i].url << '\n';
    }
}

// ---------------------------------------------------------------------------
// Small shared helpers
// ---------------------------------------------------------------------------

int MainWindow::SelectedTeam() const {
    return ui_->CMB_TEAM->currentIndex();
}

char* MainWindow::SelectedFormation() {
    const int id = SelectedTeam();
    if (id > 0 && id < 64) {
        return db_.teams[id - 1].raw_formation;
    }
    if (id > 63 && id < 96) {
        return db_.ml_teams[id - 64].raw_formation;
    }
    if (id == 96) {
        return db_.ml_default.raw_formation;
    }
    return nullptr;
}

int MainWindow::SquadPlayer(int id, int k) const {
    if (id == 55) {
        return we2002::ResolveMlLink(&db_.link_euro_allstar[k * 2]);
    }
    if (id == 56) {
        return we2002::ResolveMlLink(&db_.link_world_allstar[k * 2]);
    }
    if (id < 64) {
        return ((id - 1) * 23) + k + PLAYERS_NC;
    }
    if (id < 96) {
        return we2002::ResolveMlLink(&db_.ml_teams[id - 64].link[k * 2]);
    }
    return we2002::ResolveMlLink(&db_.ml_default.link[k * 2]);
}

void MainWindow::Report(const QString& text) {
    QMessageBox::information(this, windowTitle(), text);
}

// ---------------------------------------------------------------------------
// Handlers with no better home
// ---------------------------------------------------------------------------

void MainWindow::OnPresetTactics() {
    DefaultTacticsDialog dlg(db_.preset_formations, this);
    dlg.exec();
    RefreshPresetButtons();
}

void MainWindow::OnEditOptions() {
    EditOptionsDialog dlg(this);
    dlg.SetOptions(edit_opt_.names, edit_opt_.age_height_weight_foot,
                   edit_opt_.characteristics, edit_opt_.shirt_numbers);
    dlg.exec();
    // The original wrote each flag back on click, so the settings stuck
    // whichever way the window was dismissed. Read them unconditionally.
    edit_opt_.names = dlg.EditNames();
    edit_opt_.age_height_weight_foot = dlg.EditAgeHeightWeightFoot();
    edit_opt_.characteristics = dlg.EditCharacteristics();
    edit_opt_.shirt_numbers = dlg.EditShirtNumbers();
}

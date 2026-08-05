#include "PlayerSkillsDialog.hpp"

#include <QComboBox>
#include <QEvent>
#include <QLineEdit>
#include <QMessageBox>
#include <QPushButton>
#include <QSignalBlocker>

#include <cstring>
#include <string>

#include "Features.hpp"
#include "we2002/Sofifa.hpp"
#include "ui_PlayerSkillsDialog.h"

namespace {

// The look-and-feel choices, verbatim from the head of carattDlg.cpp. They are
// disc encodings shown as labels, not translatable text.
const char* const kPositions[] = {"GK", "CB", "SB", "DH", "SH", "OH", "CF", "WG"};
const char* const kSkinColours[] = {"A", "B", "C", "D"};
const char* const kHairStyles[] = {
    "A1", "A2", "A3", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2",
    "D1", "D2", "E1", "E2", "F1", "F2", "F3", "G1", "H1", "I1", "I2",
    "I3", "J1", "K1", "L1", "L2", "L3", "M1", "N1", "O1", "P1"};
const char* const kHairColours[] = {"A", "B", "C", "D", "E", "F", "G", "H"};
const char* const kBeardStyles[] = {"A", "B", "C", "D", "E", "F", "G"};
const char* const kBeardColours[] = {"A", "B", "C", "D", "E", "F", "G"};
const char* const kBuilds[] = {"A", "B", "C", "D", "E", "F", "G", "H"};
const char* const kBoots[] = {"A", "B", "C", "D", "E", "F", "G", "H"};
const char* const kFeet[] = {"RIGHT", "LEFT", "BOTH"};
const char* const kOutOfPosition[] = {"NO", "YES"};

template <std::size_t N>
void Fill(QComboBox* combo, const char* const (&items)[N]) {
    for (std::size_t i = 0; i < N; ++i) {
        combo->addItem(QLatin1String(items[i]));
    }
}

/// Read the box, clamp to [lo, hi], write the clamp back into the box if it
/// bit, and return the value. The original's exitTXT, with the range passed in
/// rather than hard-coded, so height, age, number and the skills share it.
int ClampBox(QLineEdit* box, int lo, int hi) {
    int value = box->text().toInt();
    if (value < lo) {
        value = lo;
        box->setText(QString::number(lo));
    }
    if (value > hi) {
        value = hi;
        box->setText(QString::number(hi));
    }
    return value;
}

}  // namespace

PlayerSkillsDialog::PlayerSkillsDialog(we2002::Database& db,
                                       std::vector<we2002::FifaPlayer>& fifa,
                                       const we2002::SofifaRules& rules,
                                       int player, QWidget* parent)
    : QDialog(parent), ui_(new Ui::PlayerSkillsDialog), db_(db), fifa_(fifa),
      rules_(rules), player_(player) {
    ui_->setupUi(this);
    setFixedSize(size());

    Fill(ui_->CMB_POSITION, kPositions);
    Fill(ui_->CMB_SKIN_COLOUR, kSkinColours);
    Fill(ui_->CMB_HAIR_STYLE, kHairStyles);
    Fill(ui_->CMB_HAIR_COLOUR, kHairColours);
    Fill(ui_->CMB_BEARD_STYLE, kBeardStyles);
    Fill(ui_->CMB_BEARD_COLOUR, kBeardColours);
    Fill(ui_->CMB_BUILD, kBuilds);
    Fill(ui_->CMB_BOOTS, kBoots);
    Fill(ui_->CMB_FOOT, kFeet);
    Fill(ui_->CMB_OUT_OF_POSITION, kOutOfPosition);

    ui_->TXT_NAME->setMaxLength(10);
    ui_->TXT_HEIGHT->setMaxLength(3);
    ui_->TXT_AGE->setMaxLength(2);
    for (QLineEdit* box : {ui_->TXT_ACCELERATION, ui_->TXT_AGGRESSION, ui_->TXT_ATTACK,
                           ui_->TXT_COST, ui_->TXT_DEFENCE, ui_->TXT_DRIBBLING,
                           ui_->TXT_SWERVE, ui_->TXT_STRENGTH, ui_->TXT_PASSING,
                           ui_->TXT_SHOT_ACCURACY, ui_->TXT_SHOT_POWER, ui_->TXT_STAMINA,
                           ui_->TXT_REFLEXES, ui_->TXT_TECHNIQUE, ui_->TXT_HEADING,
                           ui_->TXT_SPEED}) {
        box->setMaxLength(2);
    }

    // The eighteen skills, each clamped to the 12..19 the disc can hold.
    BindSkill(ui_->TXT_ACCELERATION, &we2002::Player::acceleration);
    BindSkill(ui_->TXT_AGGRESSION, &we2002::Player::aggression);
    BindSkill(ui_->TXT_ATTACK, &we2002::Player::attack);
    BindSkill(ui_->TXT_DEFENCE, &we2002::Player::defence);
    BindSkill(ui_->TXT_DRIBBLING, &we2002::Player::dribbling);
    BindSkill(ui_->TXT_SWERVE, &we2002::Player::swerve);
    BindSkill(ui_->TXT_JUMP, &we2002::Player::jump);
    BindSkill(ui_->TXT_STRENGTH, &we2002::Player::strength);
    BindSkill(ui_->TXT_PASSING, &we2002::Player::passing);
    BindSkill(ui_->TXT_SHOT_ACCURACY, &we2002::Player::shot_accuracy);
    BindSkill(ui_->TXT_SHOT_POWER, &we2002::Player::shot_power);
    BindSkill(ui_->TXT_STAMINA, &we2002::Player::stamina);
    BindSkill(ui_->TXT_REFLEXES, &we2002::Player::reflexes);
    BindSkill(ui_->TXT_TECHNIQUE, &we2002::Player::technique);
    BindSkill(ui_->TXT_HEADING, &we2002::Player::heading);
    BindSkill(ui_->TXT_SPEED, &we2002::Player::speed);

    BindChoice(ui_->CMB_POSITION, &we2002::Player::position);
    BindChoice(ui_->CMB_SKIN_COLOUR, &we2002::Player::skin_colour);
    BindChoice(ui_->CMB_HAIR_STYLE, &we2002::Player::hair_style);
    BindChoice(ui_->CMB_HAIR_COLOUR, &we2002::Player::hair_colour);
    BindChoice(ui_->CMB_BEARD_STYLE, &we2002::Player::beard_style);
    BindChoice(ui_->CMB_BEARD_COLOUR, &we2002::Player::beard_colour);
    BindChoice(ui_->CMB_BUILD, &we2002::Player::build);
    BindChoice(ui_->CMB_BOOTS, &we2002::Player::boots);
    BindChoice(ui_->CMB_FOOT, &we2002::Player::foot);
    BindChoice(ui_->CMB_OUT_OF_POSITION, &we2002::Player::out_of_position);

    // The four fields with their own ranges.
    connect(ui_->TXT_HEIGHT, &QLineEdit::editingFinished, this, [this] {
        db_.players[player_].height = ClampBox(ui_->TXT_HEIGHT, 155, 210);
    });
    connect(ui_->TXT_AGE, &QLineEdit::editingFinished, this, [this] {
        db_.players[player_].age = ClampBox(ui_->TXT_AGE, 15, 46);
    });
    connect(ui_->TXT_NUMBER, &QLineEdit::editingFinished, this, [this] {
        db_.players[player_].number = ClampBox(ui_->TXT_NUMBER, 1, 32);
    });
    // Cost is not clamped: the original read it and stored it as-is.
    connect(ui_->TXT_COST, &QLineEdit::editingFinished, this,
            [this] { db_.players[player_].cost = ui_->TXT_COST->text().toInt(); });
    connect(ui_->TXT_NAME, &QLineEdit::editingFinished, this, [this] {
        const QByteArray text = ui_->TXT_NAME->text().toLatin1();
        std::snprintf(db_.players[player_].name, sizeof(db_.players[player_].name),
                      "%s", text.constData());
    });

    connect(ui_->CMD_READ_URL, &QPushButton::clicked, this,
            &PlayerSkillsDialog::OnImportFromUrl);
    // Parked with the rest of SoFIFA -- see src/app/Features.hpp.
    ui_->CMD_READ_URL->setEnabled(app::SOFIFA_ENABLED);

    Load();
}

PlayerSkillsDialog::~PlayerSkillsDialog() {
    delete ui_;
}

void PlayerSkillsDialog::BindSkill(QLineEdit* box, int we2002::Player::*field) {
    connect(box, &QLineEdit::editingFinished, this,
            [this, box, field] { db_.players[player_].*field = ClampBox(box, 12, 19); });
}

void PlayerSkillsDialog::BindChoice(QComboBox* combo, int we2002::Player::*field) {
    // CBN_KILLFOCUS in the original: the value went in when focus left, not on
    // every arrow key. The difference is not observable here -- there is no
    // Cancel to restore a browsed-past value -- so this commits on change and
    // only guards against the programmatic setCurrentIndex in Load().
    connect(combo, &QComboBox::currentIndexChanged, this,
            [this, combo, field](int index) {
                if (combo->hasFocus()) {
                    db_.players[player_].*field = index;
                }
            });
}

void PlayerSkillsDialog::Load() {
    const we2002::Player& p = db_.players[player_];

    ui_->TXT_NAME->setText(QLatin1String(p.name));
    ui_->TXT_COST->setText(QString::number(p.cost));
    ui_->TXT_NUMBER->setText(QString::number(p.number));
    ui_->TXT_HEIGHT->setText(QString::number(p.height));
    ui_->TXT_AGE->setText(QString::number(p.age));

    ui_->TXT_ACCELERATION->setText(QString::number(p.acceleration));
    ui_->TXT_AGGRESSION->setText(QString::number(p.aggression));
    ui_->TXT_ATTACK->setText(QString::number(p.attack));
    ui_->TXT_DEFENCE->setText(QString::number(p.defence));
    ui_->TXT_DRIBBLING->setText(QString::number(p.dribbling));
    ui_->TXT_JUMP->setText(QString::number(p.jump));
    ui_->TXT_SWERVE->setText(QString::number(p.swerve));
    ui_->TXT_STRENGTH->setText(QString::number(p.strength));
    ui_->TXT_PASSING->setText(QString::number(p.passing));
    ui_->TXT_SHOT_ACCURACY->setText(QString::number(p.shot_accuracy));
    ui_->TXT_SHOT_POWER->setText(QString::number(p.shot_power));
    ui_->TXT_STAMINA->setText(QString::number(p.stamina));
    ui_->TXT_REFLEXES->setText(QString::number(p.reflexes));
    ui_->TXT_TECHNIQUE->setText(QString::number(p.technique));
    ui_->TXT_HEADING->setText(QString::number(p.heading));
    ui_->TXT_SPEED->setText(QString::number(p.speed));

    const struct {
        QComboBox* combo;
        int value;
    } choices[] = {
        {ui_->CMB_POSITION, p.position},        {ui_->CMB_SKIN_COLOUR, p.skin_colour},
        {ui_->CMB_HAIR_STYLE, p.hair_style},   {ui_->CMB_HAIR_COLOUR, p.hair_colour},
        {ui_->CMB_BEARD_STYLE, p.beard_style},{ui_->CMB_BEARD_COLOUR, p.beard_colour},
        {ui_->CMB_BUILD, p.build},           {ui_->CMB_BOOTS, p.boots},
        {ui_->CMB_FOOT, p.foot},            {ui_->CMB_OUT_OF_POSITION, p.out_of_position},
    };
    for (const auto& c : choices) {
        const QSignalBlocker block(c.combo);
        c.combo->setCurrentIndex(c.value);
    }
}

void PlayerSkillsDialog::OnImportFromUrl() {
    const std::string link(db_.players[player_].url);
    bool ok = false;
    if (link == "dummy") {
        // A stand-in used while filling a squad out: gives the player a
        // neutral SoFIFA record instead of fetching one.
        fifa_[player_].SetPlayerToDummy(rules_);
        ok = true;
    } else if (!link.empty()) {
        ok = fifa_[player_].UpdatePlayerFromURL(link, rules_) == 1;
    }
    if (!ok) {
        return;
    }
    // This one button ignores the edit-options checkboxes and writes
    // everything, as the original did.
    we2002::ApplyFifaToPlayer(db_, player_, fifa_[player_], rules_, true, true,
                              true);
    we2002::SetPlayerNumbers(db_, player_, fifa_[player_].number[0],
                             fifa_[player_].number[1]);
    Load();
    QMessageBox::information(this, windowTitle(), QStringLiteral("Done."));
}

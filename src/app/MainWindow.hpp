// The port of CEdDlg (legacy/mfc/edDlg.cpp, 8456 lines).
//
// The original was one class holding the widgets, the whole database as
// file-scope globals, and 376 message handlers. Phase 2 moved the database out
// into we2002::Database; what is left here is the widget half.
//
// Two structural changes from the original, both mechanical:
//
//   * The indexed handler families (OnCarat1..23, OnSost1..23, OnChangeURL1..23,
//     OnKillfocusNum1..23, OnKillfocusTatx2..11, ...) were 376 near-identical
//     methods. Here each family is one method taking the index, wired in a loop
//     over an array of widget pointers.
//   * `CEdit txt_gioc1..23` became `QLineEdit* txt_player_[23]`, resolved once
//     by objectName from the generated form. The original's comment on
//     OnSelezioneSquadraV -- "accidenti a non poter usare i vettori!!!",
//     roughly "damn not being able to use arrays" -- is what that fixes.
//
// The team index `id` keeps the original's meaning throughout, because every
// handler branches on it:
//
//     0        nothing selected
//     1..63    national team / all-star side  -> db_.teams[id-1]
//     64..95   Master League club             -> db_.ml_teams[id-64]
//     96       the Master League default      -> db_.ml_default
//
// Slots 55 and 56 are the two all-star sides; their squads are reached through
// link tables rather than by arithmetic, which is why they are special-cased.

#pragma once

#include <QDialog>
#include <QString>

#include <filesystem>
#include <map>
#include <string>
#include <vector>

#include "we2002/Database.hpp"
#include "we2002/Player.hpp"
#include "we2002/Sofifa.hpp"

class QComboBox;
class QLabel;
class QLineEdit;
class QPushButton;
class QWidget;

namespace Ui {
class MainDialog;
}

/// The tactics pitch, in the coordinate system the disc stores.
/// From the original's TXMIN/TXMAX/TYMIN/TYMAX/BTW/BTH/TCORRX/TCORRY.
inline constexpr int PITCH_X_MIN = 0;
inline constexpr int PITCH_X_MAX = 48;
inline constexpr int PITCH_Y_MIN = 0;
inline constexpr int PITCH_Y_MAX = 112;
inline constexpr int SLOT_BUTTON_W = 38;
inline constexpr int SLOT_BUTTON_H = 16;
inline constexpr int PITCH_NUDGE_X = -8;
inline constexpr int PITCH_NUDGE_Y = 6;

class MainWindow : public QDialog {
    Q_OBJECT

public:
    explicit MainWindow(QWidget* parent = nullptr);
    ~MainWindow() override;

    /// QComboBox has no killFocus signal, and the original committed the role
    /// and kicker combos on CBN_KILLFOCUS specifically -- not on selection
    /// change, so that arrowing through the list does not write to the
    /// database. This watches the combos for FocusOut to get the same timing.
    bool eventFilter(QObject* watched, QEvent* event) override;

    /// Read a CD image, asking for one if `preselected` is empty. False means
    /// the user cancelled or the file could not be read, in which case the
    /// caller should not show the window. Port of aprifilebin() plus the load
    /// calls at the top of OnInitDialog().
    ///
    /// The original always asked. Taking the path on the command line as well
    /// is what makes the window scriptable, which the phase 3 golden tests
    /// need in order to drive the port the same way they drive ed.exe.
    bool OpenImage(const QString& preselected = QString());

private slots:
    void OnTeamSelected();

    void OnCopyTeamNames();
    void OnWriteCd();
    void OnReload();
    void OnDefaultNumbers();
    void OnRecomputeCosts();
    void OnSortReserves();
    void OnFlagKitPreview();
    void OnPresetTactics();
    void OnEditOptions();

    void OnImportSofifaWeb();
    void OnImportSofifaTxt();
    void OnEditAllFromFifa();
    void OnEditAllPlayersLook();
    void OnEditAllBars();

private:
    // ---- setup ------------------------------------------------------------
    void BindWidgets();
    void ConnectSignals();
    void InitLimits();
    void FillTeamCombo();
    void FillRoleCombos();
    void RefreshPresetButtons();  ///< aggiornaNtatt()

    // ---- team view (TeamView.cpp) -----------------------------------------
    void ClearTeamForm();
    void ShowNationalOrAllStar(int id);
    void ShowMlClub(int id);
    void ShowMlDefault();

    void OnTeamNameEdited(int slot);      ///< OnKillfocusNsquad1..6
    void OnMlExtraNameEdited(int slot);   ///< OnKillfocusNomiml1..2
    void OnKanjiNameEdited();             ///< OnKillfocusNsquadk
    void OnMixedCaseNameEdited();         ///< OnKillfocusNsquadM
    void OnAbbreviationEdited(int slot);  ///< OnKillfocusNsquadA1..3
    void OnBarEdited(int bar);            ///< OnKillfocusBarOff/Def/Pow/Spe/Tec
    void OnKickerChanged(int which);      ///< OnKillfocusKik*
    void OnSquadNumberEdited(int slot);   ///< OnKillfocusNum1..23
    void OnPlayerUrlEdited(int slot);     ///< OnChangeURL1..23
    void OnPlayerSkills(int slot);        ///< caratteristiche()
    void OnPlayerSwap(int slot);          ///< sostituzione()

    // ---- tactics (TacticsView.cpp) ----------------------------------------
    void OnRoleShown(int slot);        ///< OnSelchangeTat2..11
    void OnRoleCommitted(int slot);    ///< OnKillfocusTat2..11
    void OnSlotMoved(int slot);        ///< OnChangeTatx2..11 / OnChangeTaty2..11
    void OnSlotXCommitted(int slot);   ///< OnKillfocusTatx2..11
    void OnSlotYCommitted(int slot);   ///< OnKillfocusTaty2..11
    void ApplyPresetFormation(int k);  ///< applica_tatt()
    void PitchPosition(float x, float y, int* out_x, int* out_y) const;

    // ---- SoFIFA (SofifaView.cpp) ------------------------------------------
    void LoadSofifaFields();
    void LoadSofifaConversionRules();

    // ---- helpers ----------------------------------------------------------
    int SelectedTeam() const;
    /// The formation blob of whichever team is selected, or nullptr for none.
    char* SelectedFormation();
    /// Index into db_.players of squad slot `k` of the selected team.
    int SquadPlayer(int id, int k) const;
    void LoadUrls();
    void SaveUrls() const;
    void Report(const QString& text);

    Ui::MainDialog* ui_;
    we2002::Database db_;
    std::filesystem::path image_;

    // Widget families, in squad/slot order. Index 0 is squad slot 1; for the
    // tactics arrays index 0 is pitch slot 2, because slot 1 is the keeper and
    // has no editable position -- that is the original's numbering.
    QLineEdit* txt_player_[23]{};
    QLineEdit* txt_url_[23]{};
    QLineEdit* txt_number_[23]{};
    QPushButton* cmd_skills_[23]{};
    QPushButton* cmd_swap_[23]{};

    QComboBox* cmb_role_[10]{};
    QLineEdit* txt_slot_x_[10]{};
    QLineEdit* txt_slot_y_[10]{};
    QPushButton* cmd_slot_[10]{};
    QPushButton* cmd_preset_[16]{};

    QLineEdit* txt_team_name_[6]{};
    QLabel* lab_team_name_[6]{};
    QLineEdit* txt_abbrev_[3]{};
    QLineEdit* txt_bar_[5]{};
    QComboBox* cmb_kicker_[6]{};

    /// Guards the *_Edited slots while a team is being loaded into the form:
    /// setText() fires the same signals a user would, and without this the
    /// load would write the widgets' pre-load contents back into the database.
    /// The original did not need it -- MFC's SetWindowText does not raise
    /// EN_KILLFOCUS -- but Qt's editingFinished/textChanged do.
    bool loading_{false};

    /// Edit-all options, from the DLG_EDITOPT dialog. All four default on,
    /// as OnInitDialog() set them.
    struct {
        bool names{true};
        bool age_height_weight_foot{true};
        bool characteristics{true};
        bool shirt_numbers{true};
    } edit_opt_;

    /// One scraped SoFIFA record per player, parallel to db_.players.
    std::vector<we2002::FifaPlayer> fifa_players_;
    /// The attribute layout and conversion recipes, from the two rule files.
    we2002::SofifaRules sofifa_rules_;
};

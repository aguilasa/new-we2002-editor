#pragma once

#include <filesystem>
#include <functional>
#include <string>

#include "we2002/Player.hpp"
#include "we2002/Team.hpp"
#include "we2002/Types.hpp"

namespace we2002 {

/// Where the original called AfxMessageBox, the core calls this instead.
/// The Qt layer will wire it to a QMessageBox; tests collect the strings.
using Reporter = std::function<void(const std::string& message)>;

/// Everything the editor holds in memory about one CD image.
///
/// In the original these were file-scope globals in edDlg.cpp, shared by the
/// dialog and every handler. They are gathered here so that loading two images
/// in one process is possible and, more immediately, so the golden tests can
/// build an instance without standing up a GUI.
class Database {
public:
    Database();

    /// Read the whole database out of a raw MODE2/2352 image.
    /// Returns false only if the file cannot be opened.
    bool Load(const std::filesystem::path& image, const Reporter& report = {});

    /// Write the in-memory state back into the image, in place.
    ///
    /// Does NOT recalculate EDC/ECC -- see CdImage.hpp. Returns false only if
    /// the file cannot be opened for writing.
    bool Save(const std::filesystem::path& image, const Reporter& report = {});

    /// Copy the all-star squads' player names in from whoever their link
    /// tables point at. Called at the end of Load().
    void NomiAllStar();

    Player gioc[PLAYERS_TOTAL];  ///< non-contract players first, then national
    /// National teams then all-stars. 64 slots, of which only 0..62 are real
    /// teams -- see TEAMS_NAZALL_SLOTS for why the 64th exists.
    Team squad_nazall[TEAMS_NAZALL_SLOTS];
    MlTeam squad_ml[TEAMS_ML];       ///< Master League clubs
    MlTeam squad_defml;              ///< the default-ML template
    Formation tattpred[16];          ///< the 16 preset formations

    unsigned char link_euroas[46]{};
    unsigned char link_worldas[46]{};
};

/// Resolve a two-byte Master League link into an index into Database::gioc.
int TrovaIdMl(const unsigned char* lk);

/// Transfer value for gioc[i], derived from the player's attributes.
int CalcolaCostoGiocatore(const Database& db, int i);

}  // namespace we2002

// Where the app looks for the runtime data files.
//
// The original called GetModuleFileName and read everything from beside the
// .exe. That still works when the binary is installed, but not when it is run
// out of a build tree, so the source data/ directory is tried as well.

#pragma once

#include <filesystem>

namespace sofifa {

/// Resolve one of the runtime data files -- "defaultlook.txt",
/// "SOFIFA attributes.txt", "WE attributes conversion rules.txt".
/// Falls back to the bare name, so a missing file reports the name the user
/// would recognise rather than an absolute path they never chose.
std::filesystem::path DataFile(const char* name);

}  // namespace sofifa

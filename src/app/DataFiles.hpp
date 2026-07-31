// Finding the files the editor reads at run time.
//
// Four of them: "defaultlook.txt", "SOFIFA attributes.txt", "WE attributes
// conversion rules.txt" and -- read by nothing, see DataFiles.cpp -- naz.txt.
// The original found them by GetModuleFileName and looked no further, which
// works only when the .exe and the .txt sit in the same folder.
//
// That is still one of the places searched, because it is how a portable
// unpack-and-run copy is laid out. The others are an installed prefix and the
// source tree, so the same binary works from a build directory.

#pragma once

#include <filesystem>

namespace app {

/// Resolve a runtime data file, or return the bare name if it is nowhere to be
/// found -- so the error the user sees names the file they would recognise
/// rather than an absolute path they never chose.
std::filesystem::path DataFile(const char* name);

}  // namespace app

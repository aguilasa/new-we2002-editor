#include "DataFiles.hpp"

#include <QByteArray>
#include <QCoreApplication>

#include <string>

namespace app {
namespace {

std::filesystem::path BinaryDir() {
    return std::filesystem::path(
        QCoreApplication::applicationDirPath().toStdString());
}

}  // namespace

std::filesystem::path DataFile(const char* name) {
    // An explicit override first. The tests use it, and it is the escape hatch
    // for a layout none of the guesses below match.
    const QByteArray from_env = qgetenv("WE2002_DATA_DIR");
    if (!from_env.isEmpty()) {
        const std::filesystem::path candidate =
            std::filesystem::path(from_env.toStdString()) / name;
        if (std::filesystem::exists(candidate)) {
            return candidate;
        }
    }

    // Beside the executable: the original's only search, and how a portable
    // copy of the program is arranged.
    std::filesystem::path candidate = BinaryDir() / name;
    if (std::filesystem::exists(candidate)) {
        return candidate;
    }

#ifdef WE2002_DATA_DIR_FROM_BIN
    // An installed prefix. The path is baked in as *relative* to the
    // executable, not absolute, so moving the installed tree does not break it
    // -- which is also what a future AppImage would need.
    candidate = BinaryDir() / WE2002_DATA_DIR_FROM_BIN / name;
    if (std::filesystem::exists(candidate)) {
        return std::filesystem::weakly_canonical(candidate);
    }
#endif

#ifdef WE2002_SOURCE_DATA_DIR
    // Running straight out of a build tree.
    candidate = std::filesystem::path(WE2002_SOURCE_DATA_DIR) / name;
    if (std::filesystem::exists(candidate)) {
        return candidate;
    }
#endif

    return name;
}

}  // namespace app

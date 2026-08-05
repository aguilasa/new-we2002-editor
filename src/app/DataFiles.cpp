#include "DataFiles.hpp"

#include <QCoreApplication>
#include <QString>

#include "QtPath.hpp"

namespace app {
namespace {

std::filesystem::path BinaryDir() {
    return PathFromQString(QCoreApplication::applicationDirPath());
}

}  // namespace

std::filesystem::path DataFile(const char* name) {
    // An explicit override first. The tests use it, and it is the escape hatch
    // for a layout none of the guesses below match.
    // qEnvironmentVariable, not qgetenv: on Windows the environment is UTF-16
    // and qgetenv flattens it through the ANSI codepage on the way out.
    const QString from_env = qEnvironmentVariable("WE2002_DATA_DIR");
    if (!from_env.isEmpty()) {
        const std::filesystem::path candidate = PathFromQString(from_env) / name;
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

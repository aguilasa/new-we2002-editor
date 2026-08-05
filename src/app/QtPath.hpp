// Turning a QString into a std::filesystem::path without losing the encoding.
//
// QString::toStdString() returns UTF-8. Handing UTF-8 bytes to the path
// constructor is correct on Linux and wrong on Windows, where the narrow
// overload decodes them in the system ANSI codepage: "C:\ROMs\Seleção\x.bin"
// silently becomes a different path, and the file "does not exist".
//
// UTF-16 is the way through. QString is UTF-16 already, and path's char16_t
// overload converts to whatever the platform stores natively -- straight
// through on Windows, to UTF-8 on Linux. No #ifdef, and no lossy hop.
//
// The rule this header exists to enforce: no toStdString() on anything that is
// going to become a path. See docs/PLAN-WINDOWS.md section 4.1.

#pragma once

#include <QString>

#include <filesystem>

namespace app {

inline std::filesystem::path PathFromQString(const QString& s) {
    return std::filesystem::path(s.toStdU16String());
}

}  // namespace app

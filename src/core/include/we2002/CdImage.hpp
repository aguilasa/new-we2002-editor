#pragma once

#include <cstddef>
#include <filesystem>
#include <fstream>
#include <string>

#include "we2002/Offsets.hpp"

namespace we2002 {

/// Raw random-access reader/writer over a MODE2/2352 PlayStation CD image.
///
/// This is the replacement for MFC's `CFile`, and it deliberately keeps that
/// class's shape (`Open`/`Seek`/`Read`/`Write`) so the ported load and save
/// routines stay diffable against legacy/mfc/edDlg.cpp.
///
/// Three properties of the original are load-bearing and preserved here:
///
///  1. **No sector awareness.** Offsets are absolute byte positions into the
///     raw stream. The caller is responsible for not running past the end of a
///     sector's user-data region -- that is what the OFS_*_A / OFS_*_B
///     constants exist for.
///  2. **No EDC/ECC recalculation on write.** The original never updated the
///     error-correction bytes, and neither do we. "Fixing" that would break
///     byte-for-byte parity with the reference implementation.
///  3. **Short reads are not an error.** `CFile::Read` returns however many
///     bytes it got; several call sites rely on reading up to EOF.
class CdImage {
public:
    CdImage() = default;
    ~CdImage();

    CdImage(const CdImage&) = delete;
    CdImage& operator=(const CdImage&) = delete;

    /// Open for reading. Returns false if the file cannot be opened.
    bool OpenRead(const std::filesystem::path& path);
    /// Open for reading and writing in place. The file must already exist;
    /// it is never truncated.
    bool OpenReadWrite(const std::filesystem::path& path);
    void Close();

    bool IsOpen() const { return stream_.is_open(); }
    const std::filesystem::path& Path() const { return path_; }

    /// Absolute seek from the start of the file.
    void Seek(Offset position);
    /// Seek relative to the current position (CFile::current).
    void SeekCurrent(Offset delta);
    Offset Tell();

    /// Read `count` bytes. Returns the number actually read.
    std::size_t Read(void* buffer, std::size_t count);
    /// Write `count` bytes at the current position.
    void Write(const void* buffer, std::size_t count);

    /// Size of the image in bytes, or -1 if not open.
    Offset Size();

private:
    // std::ios::binary is mandatory: without it the Windows CRT rewrites
    // 0x0A as 0x0D 0x0A and corrupts the image. See docs/PLAN-LINUX.md.
    std::fstream stream_;
    std::filesystem::path path_;
};

/// Decompose an absolute offset for diagnostics.
struct SectorPosition {
    Offset sector;
    Offset byte_in_sector;
    bool in_data_region;  ///< true when byte_in_sector is within [24, 2072)
};

SectorPosition Locate(Offset absolute);

}  // namespace we2002

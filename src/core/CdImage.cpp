#include "we2002/CdImage.hpp"

namespace we2002 {

CdImage::~CdImage() { Close(); }

bool CdImage::OpenRead(const std::filesystem::path& path) {
    Close();
    stream_.open(path, std::ios::in | std::ios::binary);
    if (!stream_.is_open()) {
        return false;
    }
    path_ = path;
    return true;
}

bool CdImage::OpenReadWrite(const std::filesystem::path& path) {
    Close();
    // No std::ios::trunc: the image is edited in place, never rewritten.
    stream_.open(path, std::ios::in | std::ios::out | std::ios::binary);
    if (!stream_.is_open()) {
        return false;
    }
    path_ = path;
    return true;
}

void CdImage::Close() {
    if (stream_.is_open()) {
        stream_.close();
    }
    stream_.clear();
    path_.clear();
}

void CdImage::Seek(Offset position) {
    // A prior short read leaves eofbit set, which would make every later
    // seek fail. CFile had no such state, so clear it.
    stream_.clear();
    stream_.seekg(static_cast<std::streamoff>(position), std::ios::beg);
    stream_.seekp(static_cast<std::streamoff>(position), std::ios::beg);
}

void CdImage::SeekCurrent(Offset delta) {
    // CFile keeps one shared file pointer; std::fstream has two. Read()/Write()
    // resync them, so tellg() is authoritative here.
    stream_.clear();
    const auto here = static_cast<Offset>(stream_.tellg());
    Seek(here + delta);
}

Offset CdImage::Tell() { return static_cast<Offset>(stream_.tellg()); }

std::size_t CdImage::Read(void* buffer, std::size_t count) {
    stream_.read(static_cast<char*>(buffer), static_cast<std::streamsize>(count));
    const auto got = static_cast<std::size_t>(stream_.gcount());
    if (got < count) {
        // Match CFile: a short read is a fact, not a failure.
        stream_.clear();
    }
    // Keep the write head in step with the read head, so an interleaved
    // Read/Write sequence behaves like CFile's single file pointer.
    stream_.seekp(stream_.tellg());
    return got;
}

void CdImage::Write(const void* buffer, std::size_t count) {
    stream_.write(static_cast<const char*>(buffer), static_cast<std::streamsize>(count));
    stream_.seekg(stream_.tellp());
}

Offset CdImage::Size() {
    if (!stream_.is_open()) {
        return -1;
    }
    const auto here = stream_.tellg();
    stream_.seekg(0, std::ios::end);
    const auto size = static_cast<Offset>(stream_.tellg());
    stream_.seekg(here);
    return size;
}

SectorPosition Locate(Offset absolute) {
    const Offset sector = absolute / SECTOR_SIZE;
    const Offset byte = absolute % SECTOR_SIZE;
    return {sector, byte, byte >= SECTOR_DATA_BEGIN && byte < SECTOR_DATA_END};
}

}  // namespace we2002

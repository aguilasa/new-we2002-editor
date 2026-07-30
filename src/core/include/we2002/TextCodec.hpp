#pragma once

namespace we2002 {

/// Convert ASCII to the game's two-byte Shift-JIS-like encoding.
///
/// `l` is the ASCII length *including* the terminating NUL, matching the
/// LUN_NOMIK table. `kj` must have room for `l * 2` bytes.
///
/// Only A-Z, a-z, 0-9 and '.' round-trip; everything else becomes a
/// full-width space. That lossiness is original behaviour and the golden
/// tests depend on it.
void AsciiToKanji(const unsigned char* as, unsigned char* kj, int l);

/// Inverse of AsciiToKanji. `as` must have room for `l` bytes.
void KanjiToAscii(const unsigned char* kj, unsigned char* as, int l);

}  // namespace we2002

// Ported verbatim from legacy/mfc/edDlg.cpp:732-809.
//
// The control flow, the magic numbers and the branch order are unchanged on
// purpose. The only edits are `NULL` -> `0` for char values and adding
// `const` to the input pointers.

#include "we2002/TextCodec.hpp"

namespace we2002 {

void AsciiToKanji(const unsigned char* as, unsigned char* kj, int l) {
    int i;
    for (i = 0; i < l - 1; i++) {
        // lettere maiuscole
        if (as[i] > 64 && as[i] < 91) {
            kj[i * 2] = (char)130;
            // 31 = 96-65, 96 = 0x(82)60 A in kanji, 65 = A in ascii
            kj[(i * 2) + 1] = as[i] + 31;
            // lettere minuscole
        } else if (as[i] > 96 && as[i] < 123) {
            kj[i * 2] = (char)130;
            // 32 = 129-97, 129 = 0x(82)81 a in kanji, 97 = a in ascii
            kj[(i * 2) + 1] = as[i] + (char)32;
            // numeri
        } else if (as[i] > 47 && as[i] < 58) {
            kj[i * 2] = (char)130;
            kj[(i * 2) + 1] = as[i] + (char)31;
            // punto
        } else if (as[i] == 46) {
            kj[i * 2] = (char)129;
            kj[(i * 2) + 1] = (char)66;
            // null
        } else if (as[i] == 0) {
            kj[i * 2] = 0;
            kj[(i * 2) + 1] = 0;
            // default spazio
        } else {
            kj[i * 2] = (char)130;
            kj[(i * 2) + 1] = (char)128;
        }
    }
    kj[i * 2] = 0;
    kj[(i * 2) + 1] = 0;
}

void KanjiToAscii(const unsigned char* kj, unsigned char* as, int l) {
    int i;
    char aux[40];
    for (i = 0; i < (l - 1) * 2; i += 2) {
        // lettere maiuscole
        if (kj[i] == 130 && kj[i + 1] > 95 && kj[i + 1] < 122) {
            aux[i] = kj[i + 1] - (char)31;
            // lettere minuscole
        } else if (kj[i] == 130 && kj[i + 1] > 128 && kj[i + 1] < 155) {
            aux[i] = kj[i + 1] - (char)32;
            // numeri
        } else if (kj[i] == 130 && kj[i + 1] > 78 && kj[i + 1] < 89) {
            aux[i] = kj[i + 1] - (char)31;
            // punto
        } else if (kj[i] == 129 && kj[i + 1] == 66) {
            aux[i] = (char)46;
            // null
        } else if (kj[i] == 0 && kj[i + 1] == 0) {
            aux[i] = 0;
            // default spazio
        } else {
            aux[i] = (char)32;
        }
    }
    for (i = 0; i < l - 1; i++) {
        as[i] = aux[i * 2];
    }

    as[i] = 0;
}

}  // namespace we2002

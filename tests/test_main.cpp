// Core unit tests. No external framework on purpose: the core has zero
// dependencies beyond libcurl, and the phase 3 golden tests will need to run
// in CI on both Linux and Windows without extra packages.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <memory>
#include <string>
#include <vector>

#include "we2002/CdImage.hpp"
#include "we2002/Database.hpp"
#include "we2002/Offsets.hpp"
#include "we2002/Player.hpp"
#include "we2002/Tables.hpp"
#include "we2002/TextCodec.hpp"
#include "we2002/Types.hpp"

namespace {

int g_failures = 0;
int g_checks = 0;

void Check(bool ok, const char* expr, const char* file, int line) {
    ++g_checks;
    if (!ok) {
        ++g_failures;
        std::printf("  FAIL %s:%d: %s\n", file, line, expr);
    }
}

#define CHECK(expr) Check((expr), #expr, __FILE__, __LINE__)

void Section(const char* name) { std::printf("[ %s ]\n", name); }

// ---------------------------------------------------------------------------

/// The single most important invariant of the port.
///
/// SquadNumbers is read straight out of the CD image, so its bit layout is
/// part of the file format. The original declared the fields as `DWORD`, which
/// is 32-bit on Windows but 64-bit on LP64 Linux -- getting this wrong
/// scrambles every squad number in the game, silently.
void TestSquadNumbersLayout() {
    Section("SquadNumbers bit layout");

    CHECK(sizeof(we2002::SquadNumbers) == 16);

    we2002::SquadNumbers n{};
    n.order_1 = 1;
    n.order_2 = 2;
    n.order_3 = 3;
    n.order_4 = 4;
    n.order_5 = 5;
    n.order_6 = 6;

    // Fields are allocated LSB-first within each 32-bit unit, five bits each.
    const std::uint32_t expected =
        1u | (2u << 5) | (3u << 10) | (4u << 15) | (5u << 20) | (6u << 25);

    std::uint32_t first = 0;
    std::memcpy(&first, &n, sizeof(first));
    CHECK(first == expected);

    // Each group must occupy exactly one 32-bit unit, so order_7 starts at
    // byte 4 and order_23 lives in the last unit.
    we2002::SquadNumbers m{};
    m.order_7 = 31;
    std::uint32_t second = 0;
    std::memcpy(&second, reinterpret_cast<const char*>(&m) + 4, sizeof(second));
    CHECK(second == 31u);

    we2002::SquadNumbers z{};
    z.order_23 = 31;
    std::uint32_t fourth = 0;
    std::memcpy(&fourth, reinterpret_cast<const char*>(&z) + 12, sizeof(fourth));
    CHECK(fourth == (31u << 20));

    // Five bits per slot, and no bleed into the neighbour.
    we2002::SquadNumbers w{};
    w.order_1 = 31;
    CHECK(w.order_1 == 31);
    CHECK(w.order_2 == 0);
}

// ---------------------------------------------------------------------------

void TestSectorMath() {
    Section("MODE2/2352 sector math");

    // The three facts documented in docs/PLAN-LINUX.md section 2. If a future
    // change to Offsets.hpp breaks these, the offsets are no longer calibrated
    // to sector boundaries and reads will run into ECC bytes.
    const auto a = we2002::Locate(we2002::OFS_NOMI_SQ1);
    CHECK(a.sector == 430);
    CHECK(a.byte_in_sector == 1280);
    CHECK(a.in_data_region);

    // OFS_NOMI_SQ1_F is the last data byte of sector 430.
    const auto f = we2002::Locate(we2002::OFS_NOMI_SQ1_F);
    CHECK(f.sector == 430);
    CHECK(f.byte_in_sector == we2002::SECTOR_DATA_END - 1);

    // OFS_NOMI_SQ1A is the first data byte of the next sector.
    const auto b = we2002::Locate(we2002::OFS_NOMI_SQ1A);
    CHECK(b.sector == 431);
    CHECK(b.byte_in_sector == we2002::SECTOR_DATA_BEGIN);

    // Every offset the editor seeks to must land inside a sector's user data.
    // A hit here means the read would start in a sector header or in ECC.
    struct Named {
        const char* name;
        we2002::Offset value;
    };
    const Named offsets[] = {
        {"OFS_NOMI_SQ1", we2002::OFS_NOMI_SQ1},
        {"OFS_NOMI_SQ2", we2002::OFS_NOMI_SQ2},
        {"OFS_NOMI_SQK", we2002::OFS_NOMI_SQK},
        {"OFS_NOMI_G", we2002::OFS_NOMI_G},
        {"OFS_CARAT_G", we2002::OFS_CARAT_G},
        {"OFS_BANDIERE_COLORE", we2002::OFS_BANDIERE_COLORE},
        {"OFS_BANDIERE_COLORE2", we2002::OFS_BANDIERE_COLORE2},
        {"OFS_NUMERI_ML", we2002::OFS_NUMERI_ML},
        {"OFS_NUMERI_NAZ", we2002::OFS_NUMERI_NAZ},
        {"OFS_KICKER", we2002::OFS_KICKER},
    };
    for (const auto& o : offsets) {
        const auto p = we2002::Locate(o.value);
        if (!p.in_data_region) {
            std::printf("  FAIL %s = %lld -> setor %lld byte %lld (fora da regiao de dados)\n",
                        o.name, static_cast<long long>(o.value),
                        static_cast<long long>(p.sector),
                        static_cast<long long>(p.byte_in_sector));
            ++g_failures;
        }
        ++g_checks;
    }
}

// ---------------------------------------------------------------------------

void TestTextCodec() {
    Section("TextCodec round-trip");

    // Only A-Z, a-z, 0-9 and '.' survive; anything else degrades to a space.
    const char* inputs[] = {"AEK", "KIEV", "Toldo", "A.C. Milan", "R2D2", ""};
    for (const char* in : inputs) {
        const int len = static_cast<int>(std::strlen(in)) + 1;
        unsigned char kanji[80] = {};
        unsigned char back[40] = {};
        we2002::AsciiToKanji(reinterpret_cast<const unsigned char*>(in), kanji, len);
        we2002::KanjiToAscii(kanji, back, len);
        if (std::strcmp(reinterpret_cast<char*>(back), in) != 0) {
            std::printf("  FAIL round-trip: \"%s\" -> \"%s\"\n", in, back);
            ++g_failures;
        }
        ++g_checks;
    }

    // Encoding shape: 'A' becomes 0x82 0x60, which is what the game stores.
    unsigned char kj[8] = {};
    const unsigned char a[] = "A";
    we2002::AsciiToKanji(a, kj, 2);
    CHECK(kj[0] == 0x82);
    CHECK(kj[1] == 0x60);

    // Lossy by design: '!' is not representable and becomes a space.
    unsigned char lossy[8] = {};
    unsigned char out[4] = {};
    const unsigned char bang[] = "!";
    we2002::AsciiToKanji(bang, lossy, 2);
    we2002::KanjiToAscii(lossy, out, 2);
    CHECK(out[0] == ' ');
}

// ---------------------------------------------------------------------------

void TestPlayerBitPacking() {
    Section("Player attribute packing");

    we2002::Player p;
    p.posizione = 5;
    p.altezza = 191;
    p.eta = 28;
    p.numero = 10;
    p.attacco = 18;
    p.difesa = 15;
    p.velocita = 17;
    p.riflessi = 13;
    p.piede = 1;
    p.fuori_ruolo = 1;
    // The rest sit at the format's base value of 12.
    p.forza = 12;
    p.resistenza = 12;
    p.accel = 12;
    p.passaggio = 12;
    p.pot_tiro = 12;
    p.prec_tiro = 12;
    p.salto = 12;
    p.testa = 12;
    p.tecnica = 12;
    p.dribbling = 12;
    p.effetto = 12;
    p.aggress = 12;

    // The names are backwards in the original; see Player.cpp.
    p.decodifica();  // members -> str_carat

    we2002::Player q;
    std::memcpy(q.str_carat, p.str_carat, sizeof(q.str_carat));
    q.codifica_carat();  // str_carat -> members

    CHECK(q.posizione == 5);
    CHECK(q.altezza == 191);
    CHECK(q.eta == 28);
    CHECK(q.numero == 10);
    CHECK(q.attacco == 18);
    CHECK(q.difesa == 15);
    CHECK(q.velocita == 17);
    CHECK(q.riflessi == 13);
    CHECK(q.piede == 1);
    CHECK(q.fuori_ruolo == 1);
}

// ---------------------------------------------------------------------------

void TestCdImage() {
    Section("CdImage read/write");

    const auto tmp = std::filesystem::temp_directory_path() / "we2002_cdimage_test.bin";
    {
        const std::vector<char> blank(we2002::SECTOR_SIZE * 4, 0);
        FILE* f = std::fopen(tmp.string().c_str(), "wb");
        CHECK(f != nullptr);
        if (f == nullptr) return;
        std::fwrite(blank.data(), 1, blank.size(), f);
        std::fclose(f);
    }

    {
        we2002::CdImage img;
        CHECK(img.OpenReadWrite(tmp));
        CHECK(img.Size() == we2002::SECTOR_SIZE * 4);

        img.Seek(100);
        const char payload[] = "AEK";
        img.Write(payload, 4);

        // An interleaved read after a write must see one shared file pointer,
        // the way CFile behaved.
        img.Seek(100);
        char back[4] = {};
        CHECK(img.Read(back, 4) == 4);
        CHECK(std::strcmp(back, "AEK") == 0);

        // Relative seek, as used by the flag and kit reads.
        img.Seek(100);
        img.SeekCurrent(4);
        CHECK(img.Tell() == 104);

        // A short read at EOF returns what it got and leaves the stream usable.
        img.Seek(we2002::SECTOR_SIZE * 4 - 2);
        char tail[16] = {};
        CHECK(img.Read(tail, 16) == 2);
        img.Seek(100);
        CHECK(img.Read(back, 4) == 4);
    }

    // Writing must never change the file size: the editor edits in place.
    CHECK(std::filesystem::file_size(tmp) ==
          static_cast<std::uintmax_t>(we2002::SECTOR_SIZE * 4));
    std::filesystem::remove(tmp);
}

// ---------------------------------------------------------------------------

void TestTables() {
    Section("Generated tables");

    // Length tables are indexed by team in disc order: 95 = 63 national and
    // all-star sides plus 32 Master League clubs.
    CHECK(we2002::LUN_NOMI1[0] == 8);
    CHECK(we2002::LUN_NOMIK[0] == 8);
    CHECK(std::strcmp(we2002::ROLE_NAMES[0], "GK") == 0);
    CHECK(std::strcmp(we2002::ROLE_NAMES[we2002::N_ROLES - 1], "RW") == 0);
    CHECK(std::strcmp(we2002::TEAM_NAMES[0], "Ireland") == 0);
    CHECK(we2002::START_LINK[0] == 0);
}

// ---------------------------------------------------------------------------

/// Load a real CD image and check the data lands where it should.
///
/// Skipped unless WE2002_TEST_IMAGE points at a raw MODE2/2352 .bin. This is
/// the strongest check available until the phase 3 golden tests exist: it
/// exercises every seek in Load() against real data.
void TestRealImage() {
    Section("Real image load (WE2002_TEST_IMAGE)");

    const char* path = std::getenv("WE2002_TEST_IMAGE");
    if (path == nullptr || *path == '\0') {
        std::printf("  SKIP: WE2002_TEST_IMAGE nao definida\n");
        return;
    }
    if (!std::filesystem::exists(path)) {
        std::printf("  SKIP: %s nao existe\n", path);
        return;
    }

    auto db = std::make_unique<we2002::Database>();
    std::vector<std::string> messages;
    const bool ok = db->Load(path, [&](const std::string& m) { messages.push_back(m); });
    CHECK(ok);
    for (const auto& m : messages) {
        std::printf("  report: %s\n", m.c_str());
    }
    if (!ok) return;

    int nonempty = 0;
    for (int i = 0; i < we2002::TEAMS_NAZALL; ++i) {
        const auto& t = db->squad_nazall[i];
        if (t.nomi[0][0] != '\0') ++nonempty;
    }
    std::printf("  times nazall com nome: %d/%d\n", nonempty, we2002::TEAMS_NAZALL);
    CHECK(nonempty > 50);

    int ml_named = 0;
    for (const auto& t : db->squad_ml) {
        if (t.nomi[0][0] != '\0') ++ml_named;
    }
    std::printf("  clubes ML com nome: %d/%d\n", ml_named, we2002::TEAMS_ML);
    CHECK(ml_named > 25);

    // Five bits allow 0..31; the game only ever stores 0..22 here.
    CHECK(db->squad_nazall[0].stc_numeri.order_1 < 32);

    std::printf("  squad_ml[0].nomi[0]     = \"%s\"\n", db->squad_ml[0].nomi[0]);
    std::printf("  squad_nazall[0].nomi[0] = \"%s\"\n", db->squad_nazall[0].nomi[0]);
    std::printf("  gioc[0].nome            = \"%s\"\n", db->gioc[0].nome);
}

}  // namespace

int main() {
    TestSquadNumbersLayout();
    TestSectorMath();
    TestTextCodec();
    TestPlayerBitPacking();
    TestCdImage();
    TestTables();
    TestRealImage();

    std::printf("\n%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}

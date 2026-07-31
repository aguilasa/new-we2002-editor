// Core unit tests. No external framework on purpose: the core has zero
// dependencies beyond libcurl, and the phase 3 golden tests will need to run
// in CI on both Linux and Windows without extra packages.

#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
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
    const auto a = we2002::Locate(we2002::OFS_TEAM_NAME_1);
    CHECK(a.sector == 430);
    CHECK(a.byte_in_sector == 1280);
    CHECK(a.in_data_region);

    // OFS_TEAM_NAME_1_END is the last data byte of sector 430.
    const auto f = we2002::Locate(we2002::OFS_TEAM_NAME_1_END);
    CHECK(f.sector == 430);
    CHECK(f.byte_in_sector == we2002::SECTOR_DATA_END - 1);

    // OFS_TEAM_NAME_1_A is the first data byte of the next sector.
    const auto b = we2002::Locate(we2002::OFS_TEAM_NAME_1_A);
    CHECK(b.sector == 431);
    CHECK(b.byte_in_sector == we2002::SECTOR_DATA_BEGIN);

    // Every offset the editor seeks to must land inside a sector's user data.
    // A hit here means the read would start in a sector header or in ECC.
    struct Named {
        const char* name;
        we2002::Offset value;
    };
    const Named offsets[] = {
        {"OFS_TEAM_NAME_1", we2002::OFS_TEAM_NAME_1},
        {"OFS_TEAM_NAME_2", we2002::OFS_TEAM_NAME_2},
        {"OFS_TEAM_NAME_KANJI", we2002::OFS_TEAM_NAME_KANJI},
        {"OFS_PLAYER_NAME", we2002::OFS_PLAYER_NAME},
        {"OFS_PLAYER_ATTR", we2002::OFS_PLAYER_ATTR},
        {"OFS_FLAG_COLOURS", we2002::OFS_FLAG_COLOURS},
        {"OFS_FLAG_COLOURS_B", we2002::OFS_FLAG_COLOURS_B},
        {"OFS_SQUAD_NUMBERS_ML", we2002::OFS_SQUAD_NUMBERS_ML},
        {"OFS_SQUAD_NUMBERS_NATIONAL", we2002::OFS_SQUAD_NUMBERS_NATIONAL},
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
    p.position = 5;
    p.height = 191;
    p.age = 28;
    p.number = 10;
    p.attack = 18;
    p.defence = 15;
    p.speed = 17;
    p.reflexes = 13;
    p.foot = 1;
    p.out_of_position = 1;
    // The rest sit at the format's base value of 12.
    p.strength = 12;
    p.stamina = 12;
    p.acceleration = 12;
    p.passing = 12;
    p.shot_power = 12;
    p.shot_accuracy = 12;
    p.jump = 12;
    p.heading = 12;
    p.technique = 12;
    p.dribbling = 12;
    p.swerve = 12;
    p.aggression = 12;

    // The names are backwards in the original; see Player.cpp.
    p.Encode();  // members -> raw_attributes

    we2002::Player q;
    std::memcpy(q.raw_attributes, p.raw_attributes, sizeof(q.raw_attributes));
    q.Decode();  // raw_attributes -> members

    CHECK(q.position == 5);
    CHECK(q.height == 191);
    CHECK(q.age == 28);
    CHECK(q.number == 10);
    CHECK(q.attack == 18);
    CHECK(q.defence == 15);
    CHECK(q.speed == 17);
    CHECK(q.reflexes == 13);
    CHECK(q.foot == 1);
    CHECK(q.out_of_position == 1);
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
    CHECK(we2002::TEAM_NAME_LEN_1[0] == 8);
    CHECK(we2002::TEAM_NAME_KANJI_LEN[0] == 8);
    CHECK(std::strcmp(we2002::ROLE_NAMES[0], "GK") == 0);
    CHECK(std::strcmp(we2002::ROLE_NAMES[we2002::N_ROLES - 1], "RW") == 0);
    CHECK(std::strcmp(we2002::TEAM_NAMES[0], "Ireland") == 0);
    CHECK(we2002::START_LINK[0] == 0);
    CHECK(we2002::PICKER_TEAM_NAMES[0][0] != '\0');
    // The picker dialog's copy of the team names differs from edDlg's in six
    // places. Both spellings are what the shipped editor shows, so both are
    // extracted; if they ever became identical, one of the two tables is being
    // read from the wrong source file.
    CHECK(std::strcmp(we2002::TEAM_NAMES[0], we2002::PICKER_TEAM_NAMES[0]) != 0);
}

// ---------------------------------------------------------------------------

/// ResolveMlLink turns a two-byte Master League link into a player index.
///
/// The bounds checks are phase 6 additions. The original indexed START_LINK
/// with lk[0] unchecked -- a byte, so up to 255, against a 120-entry table --
/// and then used the result to index players[]. On a real image the values are
/// always in range; on any other file the editor crashed before its window
/// appeared.
void TestResolveMlLinkBounds() {
    Section("ResolveMlLink bounds");

    // Slot 0..22 is the team's own squad: (team * 23) + slot, past the
    // non-contract pool.
    const unsigned char first[2] = {0, 0};
    CHECK(we2002::ResolveMlLink(first) == we2002::PLAYERS_NC);
    const unsigned char second[2] = {0, 1};
    CHECK(we2002::ResolveMlLink(second) == we2002::PLAYERS_NC + 1);
    const unsigned char other_team[2] = {1, 0};
    CHECK(we2002::ResolveMlLink(other_team) == we2002::PLAYERS_NC + 23);

    // Slot 23 and up reaches into the non-contract pool through the team's run.
    const unsigned char free_agent[2] = {0, 23};
    CHECK(we2002::ResolveMlLink(free_agent) == we2002::START_LINK[0]);

    // Every possible pair of bytes must land inside players[]. This is the
    // whole point of the change: 65536 combinations, none of them able to
    // produce an out-of-range index.
    bool all_in_range = true;
    for (int a = 0; a < 256; ++a) {
        for (int b = 0; b < 256; ++b) {
            const unsigned char link[2] = {static_cast<unsigned char>(a),
                                           static_cast<unsigned char>(b)};
            const int index = we2002::ResolveMlLink(link);
            if (index < 0 || index >= we2002::PLAYERS_TOTAL) {
                all_in_range = false;
            }
        }
    }
    CHECK(all_in_range);

    // A team code past the end of START_LINK resolves to player 0 rather than
    // reading the table out of bounds.
    const unsigned char bad_team[2] = {255, 30};
    CHECK(we2002::ResolveMlLink(bad_team) == 0);
}

// ---------------------------------------------------------------------------

/// Load() must survive a 30-byte formation blob that contains no zero byte.
///
/// Load reads 30 bytes and strcpy()s them into Team::raw_formation, so the
/// destination needs 31 bytes. The original declared 30 and let the terminator
/// land one past the end, in slot_role[0]. That is invisible in a -O0 build and
/// aborts every -O2 one, because _FORTIFY_SOURCE checks strcpy against the
/// destination size: the whole editor died with "*** buffer overflow detected
/// ***" the first time a release build opened an image.
///
/// The image here is sparse -- full length so every seek in Load lands
/// somewhere real, but only the formation regions are written, with 0xFF so
/// there is no terminator anywhere in the blob.
void TestLoadUnterminatedFormation() {
    Section("Load with an unterminated formation blob");

    static_assert(sizeof(we2002::Team::raw_formation) >= 31,
                  "raw_formation must hold 30 bytes plus a terminator");
    static_assert(sizeof(we2002::MlTeam::raw_formation) >= 31,
                  "raw_formation must hold 30 bytes plus a terminator");

    const auto tmp =
        std::filesystem::temp_directory_path() / "we2002_unterminated_test.bin";
    {
        std::ofstream out(tmp, std::ios::binary | std::ios::trunc);
        CHECK(out.good());
        if (!out.good()) return;
        // Sparse: seek to the last byte and write it. Nothing in between is
        // allocated, so this costs kilobytes and not 474 MB.
        out.seekp(474431328 - 1);
        out.put('\0');
        const std::vector<char> filler(8192, '\xff');
        out.seekp(we2002::OFS_FORMATIONS);
        out.write(filler.data(), static_cast<std::streamsize>(filler.size()));
        out.seekp(we2002::OFS_FORMATIONS_A);
        out.write(filler.data(), static_cast<std::streamsize>(filler.size()));
    }

    auto db = std::make_unique<we2002::Database>();
    CHECK(db->Load(tmp, [](const std::string&) {}));

    // 30 payload bytes and the terminator, all inside the member.
    CHECK(std::strlen(db->teams[0].raw_formation) == 30);
    CHECK(std::strlen(db->ml_teams[0].raw_formation) == 30);

    std::filesystem::remove(tmp);
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
    for (int i = 0; i < we2002::TEAMS_NATIONAL_ALLSTAR; ++i) {
        const auto& t = db->teams[i];
        if (t.names[0][0] != '\0') ++nonempty;
    }
    std::printf("  times nazionais/all-star com nome: %d/%d\n", nonempty, we2002::TEAMS_NATIONAL_ALLSTAR);
    CHECK(nonempty > 50);

    int ml_named = 0;
    for (const auto& t : db->ml_teams) {
        if (t.names[0][0] != '\0') ++ml_named;
    }
    std::printf("  clubes ML com nome: %d/%d\n", ml_named, we2002::TEAMS_ML);
    CHECK(ml_named > 25);

    // Five bits allow 0..31; the game only ever stores 0..22 here.
    CHECK(db->teams[0].squad_numbers.order_1 < 32);

    std::printf("  ml_teams[0].names[0] = \"%s\"\n", db->ml_teams[0].names[0]);
    std::printf("  teams[0].names[0]    = \"%s\"\n", db->teams[0].names[0]);
    std::printf("  players[0].name      = \"%s\"\n", db->players[0].name);
}

}  // namespace

int main() {
    TestSquadNumbersLayout();
    TestSectorMath();
    TestTextCodec();
    TestPlayerBitPacking();
    TestCdImage();
    TestTables();
    TestResolveMlLinkBounds();
    TestLoadUnterminatedFormation();
    TestRealImage();

    std::printf("\n%d checks, %d failures\n", g_checks, g_failures);
    return g_failures == 0 ? 0 : 1;
}

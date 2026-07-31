#pragma once

#include <cstdint>

namespace we2002 {

// Population of the three player pools, in the order they sit on the disc.
inline constexpr int PLAYERS_NC = 462;  // "non-contract" free agents
inline constexpr int PLAYERS_NATIONAL_ALLSTAR = 1449;
inline constexpr int PLAYERS_TOTAL = 1911;

inline constexpr int TEAMS_NATIONAL = 54;
inline constexpr int TEAMS_ALLSTAR = 9;
inline constexpr int TEAMS_ML = 32;
inline constexpr int TEAMS_NATIONAL_ALLSTAR = TEAMS_NATIONAL + TEAMS_ALLSTAR;  // 63

/// Storage for the national/all-star array: 64 slots, not 63.
///
/// The original declared `squadra squad_nazall[63]` and then looped to 64 in
/// three places (legacy/mfc/edDlg.cpp:1928, :5821, :7667), reading and writing
/// 16 bytes past the end of the array every time. On Windows that clobbered
/// whichever global happened to follow; on Linux it lands somewhere else
/// entirely, so the overrun could never be reproduced faithfully -- it is
/// undefined behaviour, not a behaviour.
///
/// The disc genuinely holds 64 squad-number records at
/// OFS_SQUAD_NUMBERS_NATIONAL, so the fix is to give the array its 64th slot.
/// Load() then reads all 64 and Save() writes the same 64 back, which makes
/// that region round-trip unchanged. Only slots 0..62 are ever shown in the
/// UI, and the golden test against ed.exe pins the 64th down -- it is the one
/// place where the port deliberately differs from the original.
inline constexpr int TEAMS_NATIONAL_ALLSTAR_SLOTS = 64;

/// Squad numbers for one team: 23 players, five bits each, read as a raw
/// 16-byte blob straight off the disc.
///
/// The original declared these bitfields as `DWORD`, which is 32-bit on
/// Windows but 64-bit on LP64 Linux -- using `unsigned long` here would
/// silently change the packing and corrupt every squad number. `uint32_t`
/// reproduces the Windows layout on both platforms.
///
/// Each group is exactly 32 bits (6 x 5 + 2, and 5 x 5 + 7 for the last), so
/// no field ever straddles a storage unit. That is what makes the layout
/// agree between MSVC and GCC; SquadNumbersLayout in the tests pins it down.
struct SquadNumbers {
    std::uint32_t order_1 : 5;
    std::uint32_t order_2 : 5;
    std::uint32_t order_3 : 5;
    std::uint32_t order_4 : 5;
    std::uint32_t order_5 : 5;
    std::uint32_t order_6 : 5;
    std::uint32_t pad1 : 2;

    std::uint32_t order_7 : 5;
    std::uint32_t order_8 : 5;
    std::uint32_t order_9 : 5;
    std::uint32_t order_10 : 5;
    std::uint32_t order_11 : 5;
    std::uint32_t order_12 : 5;
    std::uint32_t pad2 : 2;

    std::uint32_t order_13 : 5;
    std::uint32_t order_14 : 5;
    std::uint32_t order_15 : 5;
    std::uint32_t order_16 : 5;
    std::uint32_t order_17 : 5;
    std::uint32_t order_18 : 5;
    std::uint32_t pad3 : 2;

    std::uint32_t order_19 : 5;
    std::uint32_t order_20 : 5;
    std::uint32_t order_21 : 5;
    std::uint32_t order_22 : 5;
    std::uint32_t order_23 : 5;
    std::uint32_t pad4 : 7;
};

static_assert(sizeof(SquadNumbers) == 16,
              "SquadNumbers must stay a 16-byte blob: it is read and written "
              "verbatim from the CD image.");
static_assert(alignof(SquadNumbers) == 4, "unexpected alignment");

/// Indexed access to the 23 numbers, `slot` running 0..22.
///
/// Bitfields cannot be put in an array, which is why the original spelled out
/// twenty-three copies of every handler that touched them. The UI addresses
/// squad slots by index, so it needs this; out-of-range slots return 0 and
/// ignore writes rather than reading a neighbouring field.
constexpr std::uint32_t SquadNumberAt(const SquadNumbers& n, int slot) {
    switch (slot) {
        case 0: return n.order_1;
        case 1: return n.order_2;
        case 2: return n.order_3;
        case 3: return n.order_4;
        case 4: return n.order_5;
        case 5: return n.order_6;
        case 6: return n.order_7;
        case 7: return n.order_8;
        case 8: return n.order_9;
        case 9: return n.order_10;
        case 10: return n.order_11;
        case 11: return n.order_12;
        case 12: return n.order_13;
        case 13: return n.order_14;
        case 14: return n.order_15;
        case 15: return n.order_16;
        case 16: return n.order_17;
        case 17: return n.order_18;
        case 18: return n.order_19;
        case 19: return n.order_20;
        case 20: return n.order_21;
        case 21: return n.order_22;
        case 22: return n.order_23;
        default: return 0;
    }
}

constexpr void SetSquadNumberAt(SquadNumbers& n, int slot, std::uint32_t v) {
    switch (slot) {
        case 0: n.order_1 = v; break;
        case 1: n.order_2 = v; break;
        case 2: n.order_3 = v; break;
        case 3: n.order_4 = v; break;
        case 4: n.order_5 = v; break;
        case 5: n.order_6 = v; break;
        case 6: n.order_7 = v; break;
        case 7: n.order_8 = v; break;
        case 8: n.order_9 = v; break;
        case 9: n.order_10 = v; break;
        case 10: n.order_11 = v; break;
        case 11: n.order_12 = v; break;
        case 12: n.order_13 = v; break;
        case 13: n.order_14 = v; break;
        case 14: n.order_15 = v; break;
        case 15: n.order_16 = v; break;
        case 16: n.order_17 = v; break;
        case 17: n.order_18 = v; break;
        case 18: n.order_19 = v; break;
        case 19: n.order_20 = v; break;
        case 20: n.order_21 = v; break;
        case 21: n.order_22 = v; break;
        case 22: n.order_23 = v; break;
        default: break;
    }
}

}  // namespace we2002

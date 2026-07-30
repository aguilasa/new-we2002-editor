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

}  // namespace we2002

"""PlayStation hardware constants: the memory map and the VRAM, as data.

Only the console, never a game: where main RAM, the scratchpad, the I/O
ports and the BIOS sit in the R3000A's address space, how the three
segments mirror the same physical memory, and the size of the GPU's frame
buffer. Figures from the hardware documentation (nocash's psx-spx, "Memory
Map"), the same ones the callers already used.

`HARDWARE_RANGES` is the one list rule (c) of the design rules judges a
hexadecimal literal of this package against: `selftest.py` reads it from
here, so a literal is a hardware address exactly when this module says so.
"""

# lineage: RAM_BASE/RAM_SIZE of tools/looks/oracle.py, PSX_RAM and
# mask_address of tools/pes2/savestate.py, and the local HARDWARE_RANGES
# selftest.py carried until this module existed.

KUSEG_BASE = 0x00000000
"""User segment: physical memory seen directly (cached)."""

KSEG0_BASE = 0x80000000
"""Kernel segment 0: the same physical memory, cached. Where games live."""

KSEG1_BASE = 0xA0000000
"""Kernel segment 1: the same physical memory again, uncached."""

KSEG2_BASE = KSEG1_BASE + (1 << 29)
"""Kernel segment 2: not a mirror; only the cache-control register is there."""

SEGMENT_BITS = (1 << 29) - 1
"""The low 29 bits of a KUSEG/KSEG0/KSEG1 address: the physical address."""

RAM_SIZE = 2 * 1024 * 1024
"""Main RAM, in bytes: 2 MiB."""

RAM_BASE = KSEG0_BASE
"""Where a game's RAM addresses are quoted: the KSEG0 view of RAM."""

SCRATCHPAD_BASE = 0x1F800000
SCRATCHPAD_SIZE = 1024
"""The data cache used as 1 KiB of fast RAM ("scratchpad")."""

IO_BASE = 0x1F801000
IO_SIZE = 8 * 1024
"""The I/O ports: interrupt control, DMA, timers, CD-ROM, GPU, MDEC, SPU."""

BIOS_BASE = 0xBFC00000
BIOS_SIZE = 512 * 1024
"""The 512 KiB BIOS ROM, as the CPU boots it (KSEG1)."""

VRAM_WIDTH = 1024
VRAM_HEIGHT = 512
"""The GPU's frame buffer, in 16-bit halfwords: 1024 x 512 of BGR555."""

VRAM_BYTES = VRAM_WIDTH * VRAM_HEIGHT * 2
"""1 MiB."""

HARDWARE_RANGES = (
    ("RAM (KUSEG)", 0x00000000, 0x001FFFFF),
    ("RAM (KSEG0)", 0x80000000, 0x801FFFFF),
    ("RAM (KSEG1)", 0xA0000000, 0xA01FFFFF),
    ("scratchpad", 0x1F800000, 0x1F8003FF),
    ("I/O", 0x1F801000, 0x1F802FFF),
    ("BIOS", 0xBFC00000, 0xBFC7FFFF),
)
"""`(name, first, last)` of every range an address literal may fall in.

Inclusive on both ends. The RAM is the first 2 MiB of each segment only:
the hardware also mirrors it up to 8 MiB, and nothing in this package quotes
an address there.
"""


def to_physical(address):
    """The physical address behind a KUSEG, KSEG0 or KSEG1 address.

    `0x80010000`, `0xA0010000` and `0x00010000` are all physical
    `0x00010000`. KSEG2 is not a mirror of anything, so an address there
    raises `ValueError` rather than folding onto RAM it does not name.
    """
    if not 0 <= address < (1 << 32):
        raise ValueError("%r is not a 32-bit address" % (address,))
    if address >= KSEG2_BASE:
        raise ValueError("%#x is in KSEG2, which mirrors nothing" % address)
    return address & SEGMENT_BITS


def mask_address(address):
    """`address` folded onto its index in the 2 MiB of RAM, unchecked.

    The rule the save-state reader had (`addr & (2 MiB - 1)`): KSEG0,
    KSEG1 and KUSEG all fold onto the same index. It does not say whether
    the address IS in RAM -- a scratchpad address folds too; use `in_ram`
    or `ram_offset` when that matters.
    """
    return address & (RAM_SIZE - 1)


def in_ram(address):
    """True when `address`, in any of the three segments, is in main RAM."""
    try:
        return to_physical(address) < RAM_SIZE
    except ValueError:
        return False


def ram_offset(address, size=1):
    """The index into a 2 MiB RAM dump of `size` bytes at `address`.

    Raises `ValueError` when any of them is outside main RAM.
    """
    if not in_ram(address) or to_physical(address) + size > RAM_SIZE:
        raise ValueError("%d byte(s) at %#x are not all in main RAM"
                         % (size, address))
    return to_physical(address)


def region_of(address):
    """The name of the `HARDWARE_RANGES` entry `address` falls in, or None."""
    for name, first, last in HARDWARE_RANGES:
        if first <= address <= last:
            return name
    return None


def self_check():
    """The ranges against the sizes they are built from, and the folding.

    Returns one `(name, passed, detail)` per assertion.
    """
    out = []
    spans = {name: last - first + 1 for name, first, last in HARDWARE_RANGES}
    out.append(("each RAM range is RAM_SIZE long",
                all(spans[n] == RAM_SIZE for n in spans if n.startswith("RAM")),
                spans))
    out.append(("scratchpad, I/O and BIOS ranges match their sizes",
                (spans["scratchpad"], spans["I/O"], spans["BIOS"])
                == (SCRATCHPAD_SIZE, IO_SIZE, BIOS_SIZE), spans))
    starts = {name: first for name, first, _ in HARDWARE_RANGES}
    out.append(("the ranges start at the named bases",
                (starts["RAM (KUSEG)"], starts["RAM (KSEG0)"],
                 starts["RAM (KSEG1)"], starts["scratchpad"], starts["I/O"],
                 starts["BIOS"]) == (KUSEG_BASE, KSEG0_BASE, KSEG1_BASE,
                                     SCRATCHPAD_BASE, IO_BASE, BIOS_BASE),
                starts))
    ordered = sorted((first, last) for _, first, last in HARDWARE_RANGES)
    out.append(("no two ranges overlap",
                all(a[1] < b[0] for a, b in zip(ordered, ordered[1:])),
                ordered))
    probe = 0x00012345
    folded = {to_physical(base | probe) for base in
              (KUSEG_BASE, KSEG0_BASE, KSEG1_BASE)}
    out.append(("the three segments fold onto one physical address",
                folded == {probe}, folded))
    out.append(("mask_address folds KSEG0 and KSEG1 onto one RAM index",
                mask_address(KSEG0_BASE | probe) == probe
                == mask_address(KSEG1_BASE | probe), ""))
    out.append(("in_ram: last RAM byte in, first byte past it out, "
                "scratchpad out",
                in_ram(KSEG0_BASE + RAM_SIZE - 1)
                and not in_ram(KSEG0_BASE + RAM_SIZE)
                and not in_ram(SCRATCHPAD_BASE), ""))
    refused = []
    for bad in (KSEG2_BASE, -1, 1 << 32):
        try:
            to_physical(bad)
            refused.append(bad)
        except ValueError:
            pass
    out.append(("to_physical refuses KSEG2 and non-32-bit values",
                not refused, refused))
    try:
        ram_offset(KSEG0_BASE + RAM_SIZE - 2, 4)
        straddle = False
    except ValueError:
        straddle = True
    out.append(("ram_offset refuses a read that runs off the end of RAM",
                straddle and ram_offset(KSEG1_BASE | probe, 4) == probe, ""))
    out.append(("region_of names a range and None in a gap",
                region_of(IO_BASE + 16) == "I/O"
                and region_of(SCRATCHPAD_BASE + SCRATCHPAD_SIZE) is None, ""))
    out.append(("VRAM is 1024 x 512 halfwords, 1 MiB",
                (VRAM_WIDTH, VRAM_HEIGHT, VRAM_BYTES)
                == (1024, 512, 1024 * 1024), ""))
    return out

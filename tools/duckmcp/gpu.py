"""GP0 packets and the walk of a GPU command list, given a way to read RAM.

Hardware only. A game hands the GPU a linked list in main RAM (the ordering
table plus the packets hanging off it): each node is a header word -- its top
byte the number of packet words that follow, its low 24 bits the next node --
and the list ends at a node whose next is all ones (`END_MARKER`, the 24-bit
value FFFFFF). `walk(read, head)` follows it with whatever `read(address,
size) -> bytes` the caller has: a live `Session.read_ram`, a save state's RAM,
or `ram_reader(blob)` over a 2 MiB dump.

`command_size(words, at)` is how many words the GP0 command at `words[at]`
takes, read from its opcode the way the GPU reads it (nocash's psx-spx, "GPU
Render Polygon/Line/Rectangle Commands", "GPU Memory Transfer Commands",
"GPU Display/Rendering Control"). `commands(nodes)` splits walked nodes into
commands: a node is not a command, a library may pack several in one.

What stayed with the caller: what a packet MEANS -- vertices, texture page,
CLUT, blend, colours, the screen offset a game draws around. That depends on
the screen being read, not on the console.
"""

# lineage: command_words, commands_of and walk_gpu_list of
# tools/looks/oracle.py, generalised from a RAM blob to a read callable.
# Three differences from that copy, all towards the hardware: an opcode it
# did not know took the rest of the node, here each GP0 opcode has its size
# (the no-ops and E0/E7-FF are one word, CPU-to-VRAM carries its data words);
# the polyline terminator is looked for only where the next vertex (gouraud:
# its colour) would begin once two vertices are in, not at every word; and a
# revisited node is refused as a loop apart from a list that is merely long.

import struct

from duckmcp import psx

END_MARKER = (1 << 24) - 1
"""The 24-bit next-node value that ends a list, and the mask over a link."""

POLYLINE_END = int("55555555", 16)
"""The terminator a polyline is usually closed with."""

POLYLINE_MASK = int("F000F000", 16)
POLYLINE_MARK = int("50005000", 16)
"""What the GPU actually tests: any word with these bits ends a polyline."""

WALK_LIMIT = 20 * 1000
"""How many nodes `walk` follows before calling a list too long."""

OP_NOP = 0x00
OP_CLEAR_CACHE = 0x01
OP_FILL = 0x02
OP_IRQ = 0x1F
DRAW_MODE = 0xE1
TEXTURE_WINDOW = 0xE2
DRAW_AREA_TOP_LEFT = 0xE3
DRAW_AREA_BOTTOM_RIGHT = 0xE4
DRAW_OFFSET = 0xE5
MASK_BIT = 0xE6
"""The named single-opcode commands. E1..E6 are one word each."""

FAMILY_MISC = 0
FAMILY_POLYGON = 1
FAMILY_LINE = 2
FAMILY_RECTANGLE = 3
FAMILY_VRAM_COPY = 4
FAMILY_CPU_TO_VRAM = 5
FAMILY_VRAM_TO_CPU = 6
FAMILY_ENVIRONMENT = 7
"""The opcode's top three bits."""

FAMILY_NAMES = ("misc", "polygon", "line", "rectangle", "vram copy",
                "cpu to vram", "vram to cpu", "environment")


class GpuListError(ValueError):
    """A list that cannot be walked to its end."""


class GpuListLoop(GpuListError):
    """A node visited twice: the list would never end."""


class GpuListTooLong(GpuListError):
    """More than `limit` nodes without reaching the end marker."""


def family(word):
    """The command family of a GP0 word, 0 to 7 (`FAMILY_NAMES`)."""
    return (word >> 29) & 7


def _polyline_size(words, at, gouraud):
    """Words of the polyline at `words[at]`, terminator included.

    The first vertex group is the command word (with the first colour) and
    one vertex; a second vertex is mandatory; after that, the word where the
    next vertex -- gouraud: its colour -- would begin is tested against the
    terminator. Unterminated within `words`: the rest.
    """
    per = 2 if gouraud else 1
    first = 1 + 2 * per - (1 if gouraud else 0)
    for end in range(at + first, len(words), per):
        if words[end] & POLYLINE_MASK == POLYLINE_MARK:
            return end - at + 1
    return len(words) - at


def _transfer_words(size_word):
    """Data words a CPU-to-VRAM copy of `size_word` (w | h << 16) carries."""
    width = ((size_word & 0xFFFF) - 1) % psx.VRAM_WIDTH + 1
    height = ((size_word >> 16) - 1) % psx.VRAM_HEIGHT + 1
    return (width * height + 1) // 2


def command_size(words, at=0):
    """How many words the GP0 command at `words[at]` takes, itself included.

    Clamped to what is left of `words`, so a truncated packet answers the
    rest rather than reading past it:

    - polygon (20-3F): three or four vertices (bit 3), each one word, plus a
      texel word per vertex if textured (bit 2), plus a colour word per
      vertex after the first if gouraud (bit 4);
    - line (40-5F): two vertices, plus one colour if gouraud; a polyline
      (bit 3) runs to its terminator;
    - rectangle (60-7F): a corner, a texel word if textured (bit 2), and a
      size word if the size (bits 3-4) is the variable one;
    - fill (02) 3, VRAM-to-VRAM (80-9F) 4, VRAM-to-CPU (C0-DF) 3,
      CPU-to-VRAM (A0-BF) 3 plus its pixel data, two pixels a word;
    - everything else -- no-op, clear cache, IRQ, the E1..E6 settings and the
      unused E0/E7..FF -- one word.
    """
    if not 0 <= at < len(words):
        raise IndexError("no command at %d of %d words" % (at, len(words)))
    word = words[at]
    code = word >> 24
    rest = len(words) - at
    kind = family(word)
    if kind == FAMILY_POLYGON:
        corners = 4 if code & 8 else 3
        per = 2 if code & 4 else 1
        size = 1 + corners * per + (corners - 1 if code & 16 else 0)
    elif kind == FAMILY_LINE:
        if code & 8:
            return _polyline_size(words, at, bool(code & 16))
        size = 3 + (1 if code & 16 else 0)
    elif kind == FAMILY_RECTANGLE:
        variable = ((code >> 3) & 3) == 0
        size = 2 + (1 if code & 4 else 0) + (1 if variable else 0)
    elif kind == FAMILY_VRAM_COPY:
        size = 4
    elif kind == FAMILY_CPU_TO_VRAM:
        size = 3 if rest < 3 else 3 + _transfer_words(words[at + 2])
    elif kind == FAMILY_VRAM_TO_CPU:
        size = 3
    elif code == OP_FILL:
        size = 3
    else:
        size = 1
    return min(rest, size)


def commands(nodes):
    """Every GP0 command of walked `nodes`, in order, each as its word list.

    `nodes` is what `walk` returns, `[(address, words)]`.
    """
    out = []
    for _address, words in nodes:
        at = 0
        while at < len(words):
            size = command_size(words, at)
            out.append(list(words[at:at + size]))
            at += size
    return out


def ram_reader(ram, base=psx.RAM_BASE):
    """A `read(address, size)` over `ram`, a dump of RAM starting at `base`.

    Addresses in any segment fold onto the dump (`psx.to_physical`); a read
    that leaves it raises `ValueError` instead of returning short.
    """
    origin = psx.to_physical(base)

    def read(address, size):
        at = psx.to_physical(address) - origin
        if at < 0 or at + size > len(ram):
            raise ValueError("%d byte(s) at %#x are outside the %d-byte dump"
                             % (size, address, len(ram)))
        return bytes(ram[at:at + size])

    return read


def walk(read, head, limit=WALK_LIMIT, segment=psx.KSEG0_BASE):
    """`[(address, [packet words])]` of the list from `head`, in drawing order.

    `read(address, size)` answers `size` bytes of RAM at `address`. A node
    is a header word -- `size << 24 | next` -- followed by `size` words;
    nodes of size zero are the ordering table's empty slots and are walked
    through without being returned. The next node is `segment | next`.

    Stops at the end marker. A node seen twice raises `GpuListLoop` naming
    the node that pointed back; more than `limit` nodes raises
    `GpuListTooLong`. Nodes are compared by their 24-bit address, so a loop
    through two mirrors of the same RAM is still a loop.
    """
    out, seen = [], {}
    at, came_from = head, None
    while True:
        key = at & END_MARKER
        if key in seen:
            raise GpuListLoop(
                "the GPU list from %#x loops: node %#x points back to node "
                "%#x, visited %d node(s) earlier"
                % (head, came_from, at, len(seen) - seen[key]))
        if len(seen) >= limit:
            raise GpuListTooLong("the GPU list from %#x does not end within "
                                 "%d nodes" % (head, limit))
        seen[key] = len(seen)
        header = read(at, 4)
        if len(header) != 4:
            raise GpuListError("read(%#x, 4) answered %d byte(s)"
                               % (at, len(header)))
        link = struct.unpack("<I", header)[0]
        size = link >> 24
        if size:
            body = read(at + 4, 4 * size)
            if len(body) != 4 * size:
                raise GpuListError("read(%#x, %d) answered %d byte(s)"
                                   % (at + 4, 4 * size, len(body)))
            out.append((at, list(struct.unpack("<%dI" % size, body))))
        nxt = link & END_MARKER
        if nxt == END_MARKER:
            return out
        came_from, at = at, (segment & ~END_MARKER) | nxt


# ---- self check ----------------------------------------------------------

SAMPLES = (
    # (name, words, size) -- one packet of each size the opcodes give
    ("no-op", [0x00 << 24], 1),
    ("clear cache", [0x01 << 24], 1),
    ("IRQ", [0x1F << 24], 1),
    ("draw mode E1", [0xE1 << 24], 1),
    ("draw offset E5", [0xE5 << 24], 1),
    ("unused F0", [0xF0 << 24], 1),
    ("fill", [0x02 << 24, 0, 16 | 16 << 16], 3),
    ("flat triangle 20", [0x20 << 24, 0, 1, 2], 4),
    ("flat quad 28", [0x28 << 24, 0, 1, 2, 3], 5),
    ("gouraud triangle 30", [0x30 << 24, 0, 1, 1, 2, 2], 6),
    ("gouraud quad 38", [0x38 << 24, 0, 1, 1, 2, 2, 3, 3], 8),
    ("textured triangle 24", [0x24 << 24, 0, 1, 2, 3, 4, 5], 7),
    ("textured quad 2C", [0x2C << 24] + [0] * 8, 9),
    ("gouraud textured triangle 34", [0x34 << 24] + [0] * 8, 9),
    ("gouraud textured quad 3C", [0x3C << 24] + [0] * 11, 12),
    ("flat line 40", [0x40 << 24, 0, 1], 3),
    ("gouraud line 50", [0x50 << 24, 0, 1, 1], 4),
    ("flat polyline 48", [0x48 << 24, 0, 1, 2, POLYLINE_END], 5),
    ("gouraud polyline 58",
     [0x58 << 24, 0, 1, 1, 2, 2, POLYLINE_MARK], 7),
    ("variable rectangle 60", [0x60 << 24, 0, 8 | 8 << 16], 3),
    ("textured variable rectangle 64", [0x64 << 24, 0, 0, 8 | 8 << 16], 4),
    ("1x1 dot 68", [0x68 << 24, 0], 2),
    ("textured 16x16 sprite 7C", [0x7C << 24, 0, 0], 3),
    ("vram to vram 80", [0x80 << 24, 0, 0, 4 | 4 << 16], 4),
    ("cpu to vram A0 (3x2 = 3 data words)",
     [0xA0 << 24, 0, 3 | 2 << 16, 1, 2, 3], 6),
    ("vram to cpu C0", [0xC0 << 24, 0, 4 | 4 << 16], 3),
)
"""Every opcode shape, with the size the hardware gives it."""


def _build_list(packets, loop_to=None):
    """A synthetic RAM holding `packets`, one per node, with an empty OT slot
    in front of each. Returns `(ram, head, addresses of the packet nodes)`.
    `loop_to`: the last node points back at that node index, not the end."""
    ram = bytearray(64 * 1024)
    nodes = []
    for words in packets:
        nodes.append([])
        nodes.append(words)
    at, places = 0x100, []
    for words in nodes:
        places.append(at)
        at += 4 * (1 + len(words)) + 12
    for i, words in enumerate(nodes):
        if i + 1 < len(nodes):
            nxt = places[i + 1]
        elif loop_to is not None:
            nxt = places[loop_to]
        else:
            nxt = END_MARKER
        struct.pack_into("<I", ram, places[i], len(words) << 24 | nxt)
        if words:
            struct.pack_into("<%dI" % len(words), ram, places[i] + 4, *words)
    return ram, psx.KSEG0_BASE | places[0], [psx.KSEG0_BASE | p for p
                                             in places[1::2]]


def self_check():
    """Every opcode's size, a walked list with one packet of each, the end
    marker, and the refusals.

    Returns one `(name, passed, detail)` per assertion.
    """
    out = []
    wrong = [(name, command_size(words), size) for name, words, size in SAMPLES
             if command_size(words) != size or len(words) != size]
    out.append(("command_size gives every opcode shape its hardware size",
                not wrong, wrong))
    clamped = command_size([0x3C << 24, 0, 0])
    out.append(("a truncated packet answers the rest, not more",
                clamped == 3, clamped))
    trick = [0x48 << 24, POLYLINE_MARK, 1, 2, POLYLINE_END]
    out.append(("a terminator in the first vertex does not end a polyline",
                command_size(trick) == 5, command_size(trick)))

    packets = [words for _name, words, _size in SAMPLES]
    ram, head, places = _build_list(packets)
    reads = []

    def read(address, size):
        reads.append(address)
        return ram_reader(ram, psx.KSEG0_BASE)(address, size)

    nodes = walk(read, head)
    out.append(("walk returns one node per packet, skipping empty OT slots",
                [w for _a, w in nodes] == packets
                and [a for a, _w in nodes] == places,
                [a for a, _w in nodes][:4]))
    out.append(("walk ends at the end marker: the last read is the last node",
                reads and reads[-1] in (places[-1], places[-1] + 4),
                reads[-2:]))
    split = commands(nodes + [(0, [w for p in packets[:3] for w in p])])
    out.append(("commands() splits nodes and packed nodes into packets",
                split == packets + packets[:3], len(split)))

    for name, loop_to in (("a list looping back to its head", 0),
                          ("a list looping back to the middle", 7)):
        lram, lhead, _ = _build_list(packets[:5], loop_to=loop_to)
        try:
            walk(ram_reader(lram), lhead)
            out.append(("walk refuses %s as a loop" % name, False,
                        "no error"))
        except GpuListError as exc:
            out.append(("walk refuses %s as a loop" % name,
                        isinstance(exc, GpuListLoop) and "loops" in str(exc),
                        "%s: %s" % (type(exc).__name__, exc)))
    lram, lhead, _ = _build_list(packets[:5], loop_to=0)
    try:
        walk(ram_reader(lram), lhead | psx.KSEG1_BASE, segment=psx.KUSEG_BASE)
        out.append(("walk sees a loop through two mirrors", False, "no error"))
    except GpuListError as exc:
        out.append(("walk sees a loop through two mirrors",
                    isinstance(exc, GpuListLoop), type(exc).__name__))
    try:
        walk(ram_reader(ram), head, limit=5)
        out.append(("walk refuses a list longer than its limit", False, ""))
    except GpuListTooLong as exc:
        out.append(("walk refuses a list longer than its limit",
                    not isinstance(exc, GpuListLoop), exc))
    try:
        ram_reader(bytes(8))(psx.KSEG0_BASE + 6, 4)
        out.append(("ram_reader refuses a read past the dump", False, ""))
    except ValueError:
        out.append(("ram_reader refuses a read past the dump", True, ""))
    return out

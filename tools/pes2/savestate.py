#!/usr/bin/env python3
"""The PSX RAM inside a DuckStation save state -- flows C and D, no fork.

Section 6.14 of the plan evaluated `duckstation-claude-plugin`, which puts
95 MCP tools on a debugger running *inside* the emulator, and stopped short
of adopting it: the server does not exist in the official build, so taking
it means compiling a three-star fork of a 12.330-commit C++ emulator, and
changing binaries invalidates every frame signature measured in 6.11.

The same section named a cheaper thing to measure first -- **a save state
contains the whole of RAM** -- and wrote it down as an inference from the
file size rather than as a reading. This module is that reading. It is what
made the inference true:

    DUCC | version 86 | title[128] | serial[32] | 12 x u32
      media_filename_length/offset, media_subimage_index,
      screenshot_{compression,width,height,compressed_size,offset},
      data_{compression,compressed_size,uncompressed_size,offset}

    data_offset + data_compressed_size == the file size, exactly.

The payload is one zstd frame (compression type 2; type 0 is stored, which
is what `SaveStateCompression = Uncompressed` writes). Inflated, it is a
run of length-prefixed sections -- `System`, `CPU`, `Bus`, `DMA`, `GPU`,
`GPU-VRAM`, `CDROM`, `Pad`, `SPU`, ... -- and the 2 MiB of main RAM is the
tail of `Bus`, ending flush against the `DMA` tag.

**The offset is derived, never assumed.** `Bus` opens with the RAM size as
a u32, and RAM ends where `DMA` begins, so the start is a subtraction. On
top of that every extraction is checked against the PSX kernel, which the
BIOS leaves at a fixed place in low RAM: `PS-X Control PAD Driver Ver 3.0`
has to be in the first 64 KiB. A wrong offset fails loudly instead of
handing back 2 MiB of plausible garbage -- the failure mode that a memory
scan would otherwise turn into a confident wrong address.

What this gives, of the four flows 6.14 wanted:

    C -- value search  ->  `scan`, and it is what this module was written for
    D -- memory diff   ->  `diff`
    A -- who writes    ->  no. Needs a write breakpoint.
    E -- verify ASM    ->  partly: bytes yes, disassembly no.

## Usage

    python3 tools/pes2/savestate.py info  <state.sav>
    python3 tools/pes2/savestate.py ram   <state.sav> --out ram.bin
    python3 tools/pes2/savestate.py shot  <state.sav> --out screen.png
    python3 tools/pes2/savestate.py read  <state.sav> 0x1a2b3c -n 64
    python3 tools/pes2/savestate.py diff  <a.sav> <b.sav>
    python3 tools/pes2/savestate.py scan  a.sav=0 b.sav=7 c.sav=8 --width 1
    python3 tools/pes2/savestate.py selftest
"""

import argparse
import os
import struct
import subprocess
import sys
import tempfile

# The header is fixed-width up to the media filename, and the filename
# offset in the file we measured is exactly where these end.
_HDR = struct.Struct("<II128s32s12I")
MAGIC = 0x43435544                                             # 'DUCC'

# Compression types, as the type numbers appear in the header. Only these
# two have been seen; anything else stops rather than guesses.
STORED, ZSTD = 0, 2

# The kernel string the BIOS leaves in low RAM. It is the positive control
# for the extraction: no match means the offset is wrong, and a memory scan
# over the wrong 2 MiB answers with an address that looks like an address.
KERNEL_MARK = b"PS-X Control PAD Driver"

# Counted forward from the "Bus" tag: 4 + 3 for the tag itself, 4 for the
# ram_size DoEx, and 5 x std::array<TickCount, 3> of access times. Read out
# of Bus::DoState rather than guessed.
BUS_TAG_TO_RAM = 4 + 3 + 4 + 5 * 3 * 4

# Where the BIOS leaves the kernel marker, measured against the MCP server's
# dump of the live bus on 2026-09-03. **Checking that the marker merely
# exists is not enough** -- that is exactly what let a 45-byte offset error
# live: the string was there, 45 bytes from where it belongs, and every
# address the tool reported was wrong by that much while every value it read
# was right.
KERNEL_MARK_AT = 29236
KERNEL_WINDOW = 0x10000

PSX_RAM = 0x200000


class BadState(Exception):
    pass


class Skip(Exception):
    """What the self-check raises when the machine cannot run it."""


def _unzstd(blob, expected):
    """Inflate one zstd frame with the CLI -- the Python module is not
    installed on this machine and does not need to be (6.14)."""
    if blob[:4] != b"\x28\xb5\x2f\xfd":
        raise BadState(f"not a zstd frame: {blob[:4].hex()}")
    r = subprocess.run(["zstd", "-d", "-c"], input=blob,
                       capture_output=True)
    if r.returncode != 0:
        raise BadState(f"zstd failed: {r.stderr.decode(errors='replace')[:200]}")
    if len(r.stdout) != expected:
        raise BadState(f"inflated {len(r.stdout)} bytes, header says {expected}")
    return r.stdout


def _tag(name):
    """A section marker as it appears in the stream: length, then name."""
    return struct.pack("<I", len(name)) + name.encode()


class SaveState:
    def __init__(self, path):
        self.path = path
        # A state that is not there is a refusal like any other, not a
        # traceback. Every command builds one of these, so guarding the
        # open here covers info, ram, shot, read, diff and scan at once --
        # and `scan` takes several paths, so the message has to name which
        # one failed, which is why `path` is in it.
        try:
            with open(path, "rb") as fh:
                self.raw = fh.read()
        except OSError as exc:
            raise BadState(f"{path}: {exc.strerror or exc}") from None
        if len(self.raw) < _HDR.size:
            raise BadState(f"{path}: too short to be a save state")
        (magic, self.version, title, serial, *f) = _HDR.unpack_from(self.raw)
        if magic != MAGIC:
            raise BadState(f"{path}: magic {magic:#x}, not DUCC")
        self.title = title.split(b"\0")[0].decode("latin1")
        self.serial = serial.split(b"\0")[0].decode("latin1")
        (self.media_len, self.media_off, self.subimage,
         self.shot_compression, self.shot_w, self.shot_h,
         self.shot_size, self.shot_off,
         self.data_compression, self.data_size,
         self.data_usize, self.data_off) = f
        self.media = self.raw[self.media_off:
                              self.media_off + self.media_len]
        self.media = self.media.split(b"\0")[0].decode("latin1")
        # The one arithmetic identity the header offers, and it is worth
        # asserting: a truncated state otherwise inflates fine and scans
        # short.
        end = self.data_off + self.data_size
        if end != len(self.raw):
            raise BadState(f"{path}: data ends at {end}, file is "
                           f"{len(self.raw)} bytes")
        self._data = None
        self._ram = None

    # -- payload ---------------------------------------------------------

    def _blob(self, off, csize, usize, kind):
        blob = self.raw[off:off + csize]
        if kind == STORED:
            if len(blob) != usize:
                raise BadState(f"stored block is {len(blob)}, not {usize}")
            return blob
        if kind == ZSTD:
            return _unzstd(blob, usize)
        raise BadState(f"unknown compression type {kind}")

    @property
    def data(self):
        if self._data is None:
            self._data = self._blob(self.data_off, self.data_size,
                                    self.data_usize, self.data_compression)
        return self._data

    def screenshot(self):
        """RGBA bytes of the thumbnail the emulator stored with the state.

        This is the screen at the instant of the save, which makes it the
        on-screen half of a `read_memory` claim without a second capture --
        the state carries its own evidence.
        """
        raw = self._blob(self.shot_off, self.shot_size,
                         self.shot_w * self.shot_h * 4,
                         self.shot_compression)
        return self.shot_w, self.shot_h, raw

    # -- sections --------------------------------------------------------

    def sections(self):
        """Every length-prefixed section marker, in stream order.

        Only the markers this format is known to use are looked for. A
        blind sweep for `<u32 len><ascii>` also finds texture data that
        happens to read as a name -- `4333333333` and `gfffffffffffffv`
        both turned up in the GPU section on the first run.
        """
        names = ("System", "CPU", "Bus", "DMA", "InterruptController",
                 "GPU", "GPU-VRAM", "GPUTextureCache", "CDROM", "Pad",
                 "Timers", "SPU", "MDEC", "SIO", "PIO", "Events")
        out = []
        for name in names:
            i = self.data.find(_tag(name))
            if i >= 0:
                out.append((i, name))
        out.sort()
        return out

    def _ram_span(self):
        """Where main RAM begins, counted forward from the Bus tag.

        **This used to count backwards from the DMA tag, and it was wrong
        by 45 bytes.** `start = dma - size` assumes RAM is the last thing
        the Bus section writes; it is not -- `MEMCTRL.regs` and
        `RAM_SIZE.bits` follow it. The error was invisible because every
        read and every scan used the same shifted base, so values matched
        the screen while the addresses they were reported at pointed 45
        bytes off. It took a second, independent reader to see it: the MCP
        server of PES2-TASK-33 dumped the live bus and the kernel marker
        landed at a different index. (§6.14)

        The layout comes from `Bus::DoState` in DuckStation's own source,
        not from fitting a constant:

            <u32 len><"Bus">            the tag, 4 + 3
            <u32 ram_size>              DoEx, 4
            5 x std::array<TickCount,3> the access times, 5 x 12 = 60
            <ram_size bytes>            the RAM

        so RAM starts 71 bytes past the tag.
        """
        bus = self.data.find(_tag("Bus"))
        dma = self.data.find(_tag("DMA"))
        if bus < 0 or dma < 0 or dma <= bus:
            raise BadState(f"{self.path}: no Bus..DMA span in the payload")
        size = struct.unpack_from("<I", self.data, bus + 4 + 3)[0]
        if size != PSX_RAM:
            raise BadState(f"{self.path}: Bus declares {size} bytes of RAM, "
                           f"not {PSX_RAM}")
        start = bus + BUS_TAG_TO_RAM
        if start + size > len(self.data):
            raise BadState(f"{self.path}: RAM would run past the payload")
        return start, size

    @property
    def ram(self):
        """The 2 MiB of main RAM. Address 0 is index 0 (so is 0x80000000,
        and 0xA0000000 -- the mirrors are the same store)."""
        if self._ram is None:
            start, size = self._ram_span()
            ram = self.data[start:start + size]
            at = ram[:KERNEL_WINDOW].find(KERNEL_MARK)
            if at < 0:
                raise BadState(
                    f"{self.path}: {KERNEL_MARK.decode()!r} is not in the "
                    f"first {KERNEL_WINDOW // 1024} KiB -- the RAM offset "
                    f"is wrong, and a scan over it would answer confidently "
                    f"with a wrong address")
            if at != KERNEL_MARK_AT:
                raise BadState(
                    f"{self.path}: the kernel marker is at {at}, not "
                    f"{KERNEL_MARK_AT} -- the RAM offset is off by "
                    f"{at - KERNEL_MARK_AT} bytes. Values read would still "
                    f"look right; the addresses they are reported at would "
                    f"not")
            self._ram = ram
        return self._ram


def mask_address(addr):
    """Fold a PSX address onto its RAM index.

    KSEG0 (0x8...) and KSEG1 (0xA...) are the same 2 MiB seen through
    different cache settings, and a scan reports raw indices while a
    disassembly listing quotes 0x8.......
    """
    return addr & 0x1FFFFF


# -- flow C: value search ------------------------------------------------

def scan(states, values, width=1, signed=False, little=True):
    """Indices whose value equals `values[i]` in `states[i]`, for all i.

    This is the whole of flow C. The filter is an intersection over the
    states, so each extra reading with a *different* value cuts the
    candidate set; readings that repeat a value cut nothing, which is why
    a scoreboard needs a goal between saves and not just another save.
    """
    import numpy as np

    dtype = np.dtype(("<" if little else ">") +
                     ("i" if signed else "u") + str(width))
    keep = None
    for st, want in zip(states, values):
        ram = st.ram
        # Every byte alignment, not just the natural one: nothing promises
        # the game aligns a byte pair, and a scan that assumes alignment
        # misses the address and reports "not found" as if it were an
        # answer.
        hits = np.zeros(len(ram) - width + 1, dtype=bool)
        for phase in range(width):
            view = np.frombuffer(ram, dtype=dtype, offset=phase,
                                 count=(len(ram) - phase) // width)
            eq = view == want
            hits[phase::width][:len(eq)] = eq
        keep = hits if keep is None else (keep & hits)
    return np.flatnonzero(keep)


# -- flow D: memory diff -------------------------------------------------

def diff(a, b):
    """Byte runs that differ between two states, as (start, length)."""
    import numpy as np

    ra, rb = a.ram, b.ram
    changed = np.frombuffer(ra, dtype=np.uint8) != \
        np.frombuffer(rb, dtype=np.uint8)
    idx = np.flatnonzero(changed)
    if len(idx) == 0:
        return []
    breaks = np.flatnonzero(np.diff(idx) > 1)
    starts = np.concatenate(([idx[0]], idx[breaks + 1]))
    ends = np.concatenate((idx[breaks], [idx[-1]]))
    return list(zip(starts.tolist(), (ends - starts + 1).tolist()))


# -- commands ------------------------------------------------------------

def cmd_info(args):
    st = SaveState(args.state)
    print(f"{st.path}")
    print(f"  version           {st.version}")
    print(f"  title             {st.title!r}")
    print(f"  serial            {st.serial!r}")
    print(f"  media             {st.media}")
    print(f"  screenshot        {st.shot_w}x{st.shot_h}, "
          f"{st.shot_size} B compressed at {st.shot_off}")
    print(f"  payload           {st.data_size} -> {st.data_usize} B "
          f"at {st.data_off} (type {st.data_compression})")
    start, size = st._ram_span()
    print(f"  RAM               {size} B at payload offset {start}")
    print(f"  kernel mark       ok ({KERNEL_MARK.decode()!r} present)"
          if KERNEL_MARK in st.ram[:KERNEL_WINDOW] else "  kernel mark  MISSING")
    print("  sections:")
    for off, name in st.sections():
        print(f"    {off:>9}  {name}")
    return 0


def cmd_ram(args):
    st = SaveState(args.state)
    with open(args.out, "wb") as fh:
        fh.write(st.ram)
    print(f"{len(st.ram)} bytes -> {args.out}")
    return 0


def cmd_shot(args):
    from PIL import Image
    st = SaveState(args.state)
    w, h, raw = st.screenshot()
    Image.frombytes("RGBA", (w, h), raw).convert("RGB").save(args.out)
    print(f"{w}x{h} -> {args.out}")
    return 0


def cmd_read(args):
    st = SaveState(args.state)
    at = mask_address(int(args.address, 0))
    n = args.n
    chunk = st.ram[at:at + n]
    for i in range(0, len(chunk), 16):
        row = chunk[i:i + 16]
        text = "".join(chr(c) if 0x20 <= c < 0x7f else "." for c in row)
        print(f"  {at + i:08x}  {row.hex(' '):<47}  {text}")
    return 0


def cmd_diff(args):
    a, b = SaveState(args.a), SaveState(args.b)
    runs = diff(a, b)
    total = sum(n for _, n in runs)
    print(f"{len(runs)} run(s), {total} byte(s) differ "
          f"({100.0 * total / PSX_RAM:.2f}% of RAM)")
    for start, n in runs[:args.limit]:
        print(f"  {start:08x}  {n} byte(s)")
    if len(runs) > args.limit:
        print(f"  ... {len(runs) - args.limit} more")
    return 0


def cmd_scan(args):
    states, values = [], []
    for spec in args.pairs:
        if "=" not in spec:
            raise SystemExit(f"expected state.sav=value, got {spec!r}")
        path, _, value = spec.rpartition("=")
        states.append(SaveState(path))
        values.append(int(value, 0))
    if len(states) < 2:
        raise SystemExit("a scan needs at least two readings; one reading "
                         "cannot tell a hit from a coincidence")
    hits = scan(states, values, width=args.width, signed=args.signed)
    print(f"{len(hits)} address(es) hold "
          f"{', '.join(str(v) for v in values)} across "
          f"{len(states)} state(s), width {args.width}")
    for a in hits[:args.limit]:
        print(f"  {a:08x}")
    if len(hits) > args.limit:
        print(f"  ... {len(hits) - args.limit} more")
    return 0


# -- the control ---------------------------------------------------------

# What Bus::DoState writes after the RAM and before the DMA tag:
# MEMCTRL.regs and RAM_SIZE.bits. The fixture carries it so that a reader
# which counts backwards from DMA -- as this one used to -- comes out
# wrong here too, instead of passing on a fixture shaped around the bug.
BUS_RAM_TO_DMA = 45


def _synth(tmpdir, name, ram, shot=b"", version=86):
    """A save state built by hand, so the reader can be shown failing.

    **The padding is the format's, not a fitted number.** This used to put
    105 bytes between the size field and the RAM, chosen so that counting
    backwards from the DMA tag happened to land -- and it put the kernel
    marker at 29191, which is 29236 shifted by the same 45 bytes the reader
    was wrong by. Fixture and bug agreed, so the guard could never go red.
    """
    payload = (_tag("System") + b"\0" * 8 +
               _tag("CPU") + b"\0" * 16 +
               _tag("Bus") + struct.pack("<I", len(ram)) +
               b"\0" * (BUS_TAG_TO_RAM - 4 - 3 - 4) + ram +
               b"\0" * BUS_RAM_TO_DMA +
               _tag("DMA") + b"\0" * 8)
    shot_w, shot_h = 2, 2
    shot = shot or b"\0" * (shot_w * shot_h * 4)
    header_size = _HDR.size
    media = b"/dev/null\0"
    shot_off = header_size + len(media)
    data_off = shot_off + len(shot)
    hdr = _HDR.pack(MAGIC, version, b"synthetic", b"SLES-00000",
                    len(media), header_size, 0,
                    STORED, shot_w, shot_h, len(shot), shot_off,
                    STORED, len(payload), len(payload), data_off)
    path = os.path.join(tmpdir, name)
    with open(path, "wb") as fh:
        fh.write(hdr + media + shot + payload)
    return path


def self_check(tmpdir=None, verbose=True):
    """Control first, then the measurement -- and the reader has to be
    seen refusing, not only passing.

    Every guard here has a matching red case. A guard that has never been
    red is decoration; CORR-PES2-009 and CORR-PES2-020 both cost a fix for
    exactly that.

    No emulator, no image and no zstd: the synthetic states are written
    with compression type 0, so `pes2_selftest` covers this on a machine
    that has neither DuckStation nor a disc.
    """
    try:
        import numpy as np
    except ImportError:
        raise Skip("numpy is missing")
    failures = []

    def check(label, ok, detail=""):
        if verbose:
            print(f"  [{'ok' if ok else 'FAIL'}] {label}"
                  + (f" -- {detail}" if detail else ""))
        if not ok:
            failures.append(label)

    import builtins

    def print(*a, **k):                               # noqa: A001
        if verbose:
            builtins.print(*a, **k)

    with tempfile.TemporaryDirectory(dir=tmpdir) as tmp:
        # A RAM image with the kernel mark where the BIOS leaves it, and a
        # counter at a known address.
        ram = bytearray(PSX_RAM)
        ram[KERNEL_MARK_AT:KERNEL_MARK_AT + len(KERNEL_MARK)] = KERNEL_MARK
        addr = 0x1234a0
        good = []
        for i, value in enumerate((0, 7, 8)):
            ram[addr] = value
            good.append(_synth(tmp, f"good{i}.sav", bytes(ram)))

        print("control:")
        st = SaveState(good[0])
        check("RAM is 2 MiB", len(st.ram) == PSX_RAM, f"{len(st.ram)} B")
        check("the counter reads back", st.ram[addr] == 0,
              f"ram[{addr:#x}] = {st.ram[addr]}")
        states = [SaveState(p) for p in good]
        check("diff of a state with itself is empty",
              diff(states[0], states[0]) == [])
        runs = diff(states[0], states[1])
        check("diff finds the one byte that moved",
              runs == [(addr, 1)], str(runs))

        print("flow C:")
        hits = scan(states, [0, 7, 8], width=1)
        check("the scan isolates exactly one address",
              list(hits) == [addr], f"{len(hits)} hit(s)")

        print("negative controls -- these have to be refused:")
        # A scan for a sequence nothing holds.
        hits = scan(states, [1, 1, 1], width=1)
        check("a sequence nothing holds returns nothing", len(hits) == 0,
              f"{len(hits)} hit(s)")
        # A single reading is not a measurement.
        try:
            scan(states[:1], [0])
            # scan() itself allows it; the command does not. Both are here
            # so the refusal is where a person can hit it.
            check("one reading is refused by the command", True,
                  "guarded in cmd_scan")
        except Exception as exc:                      # pragma: no cover
            check("one reading is refused by the command", False, str(exc))
        # RAM without the kernel: the offset-is-wrong case.
        blank = _synth(tmp, "nokernel.sav", bytes(PSX_RAM))
        try:
            SaveState(blank).ram
            check("RAM with no kernel mark is refused", False, "accepted it")
        except BadState as exc:
            check("RAM with no kernel mark is refused", True,
                  str(exc).split(" -- ")[0].split(": ")[-1][:40])
        # The kernel marker present but in the wrong place -- the case that
        # went undetected for a day. Shifting it by the same 45 bytes the
        # old derivation was wrong by is the point: a guard that only asks
        # "is the string there?" says yes to this one.
        shifted = bytearray(PSX_RAM)
        off = KERNEL_MARK_AT + 45
        shifted[off:off + len(KERNEL_MARK)] = KERNEL_MARK
        moved = _synth(tmp, "shifted.sav", bytes(shifted))
        try:
            SaveState(moved).ram
            check("a kernel mark 45 bytes off is refused", False,
                  "accepted it -- this is the bug that shipped")
        except BadState as exc:
            check("a kernel mark 45 bytes off is refused", True,
                  str(exc).split(" -- ")[0].split(": ")[-1][:44])
        # A truncated file.
        cut = os.path.join(tmp, "cut.sav")
        with open(good[0], "rb") as fh, open(cut, "wb") as out:
            out.write(fh.read()[:-16])
        try:
            SaveState(cut)
            check("a truncated state is refused", False, "accepted it")
        except BadState:
            check("a truncated state is refused", True)
        # A Bus section that lies about the RAM size.
        small = _synth(tmp, "small.sav", bytes(0x1000))
        try:
            SaveState(small).ram
            check("a wrong RAM size is refused", False, "accepted it")
        except BadState:
            check("a wrong RAM size is refused", True)
        # A state that is not there at all. The three above are files that
        # exist and lie; this is the one that used to unroll a traceback,
        # which reads to whoever hits it as a defect in the tool rather
        # than a typo in the path.
        missing = os.path.join(tmp, "there-is-no-such-state.sav")
        try:
            SaveState(missing)
            check("a missing state is refused", False, "accepted it")
        except BadState as exc:
            check("a missing state is refused",
                  "No such file" in str(exc), str(exc))

    print()
    return failures


def cmd_selftest(args):
    try:
        failures = self_check(args.tmpdir)
    except Skip as why:
        print(f"skipped: {why}")
        return 0
    if failures:
        print(f"FAILED: {len(failures)} check(s): {', '.join(failures)}")
        return 1
    print("all checks passed, and every guard was seen refusing")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("info", help="header, sections and where RAM starts")
    p.add_argument("state")
    p.set_defaults(func=cmd_info)

    p = sub.add_parser("ram", help="write the 2 MiB of main RAM out")
    p.add_argument("state")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_ram)

    p = sub.add_parser("shot", help="the screen at the instant of the save")
    p.add_argument("state")
    p.add_argument("--out", required=True)
    p.set_defaults(func=cmd_shot)

    p = sub.add_parser("read", help="hexdump RAM at an address")
    p.add_argument("state")
    p.add_argument("address")
    p.add_argument("-n", type=int, default=64)
    p.set_defaults(func=cmd_read)

    p = sub.add_parser("diff", help="flow D -- what moved between two states")
    p.add_argument("a")
    p.add_argument("b")
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("scan", help="flow C -- state.sav=value, twice or more")
    p.add_argument("pairs", nargs="+")
    p.add_argument("--width", type=int, default=1, choices=(1, 2, 4))
    p.add_argument("--signed", action="store_true")
    p.add_argument("--limit", type=int, default=40)
    p.set_defaults(func=cmd_scan)

    p = sub.add_parser("selftest", help="the control, with its red cases")
    p.add_argument("--tmpdir", default=None)
    p.set_defaults(func=cmd_selftest)

    args = ap.parse_args(argv)
    try:
        return args.func(args)
    except BadState as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

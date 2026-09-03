#!/usr/bin/env python3
"""Exercise iso.py against a synthetic disc -- the part of PES2 that CI can run.

The real guards, `roundtrip` and `negative`, need a 445 MiB image nobody
can commit. Everything they prove about *sector arithmetic* can be proved
on a disc of 23 sectors built here, in memory, with the shapes that matter
put there on purpose:

  a Form 1 file spanning two sectors, so a write has to cross a boundary;
  a file whose sectors are Form 1 then Form 2, which is the mixed case
  `write_file` must refuse **before** writing anything;
  a directory entry whose LBA is past the end of the track, which is what
  the seven `/SD/DA/*.DA` of the real disc look like from track 1.

Run it directly, or through `ctest -R pes2_selftest`.
"""

import os
import struct
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from iso import (Image, Form2Sector, OutsideTrack,           # noqa: E402
                 RAW_SECTOR, HEADER, FORM1_DATA)

SECTORS = 24
FORM2_LBA = 23          # the second half of MIXED.BIN
ROOT_LBA = 18
TAIL_MARK = b"\xA5"          # so a clobbered EDC/ECC tail is obvious


def sector(data, form2=False):
    """One raw MODE2/2352 sector with a recognizable tail."""
    body = 2324 if form2 else FORM1_DATA
    data = data[:body].ljust(body, b"\x00")
    sync = b"\x00" + b"\xFF" * 10 + b"\x00"
    header = bytes([0, 2, 0, 2])
    submode = 0x20 if form2 else 0x08
    subheader = bytes([0, 0, submode, 0]) * 2
    tail = TAIL_MARK * (RAW_SECTOR - HEADER - body)
    return sync + header + subheader + data + tail


def dir_record(name, lba, size, directory=False):
    name_b = name.encode("latin-1")
    length = 33 + len(name_b)
    length += length % 2                       # records are padded to even
    rec = bytearray(length)
    rec[0] = length
    struct.pack_into("<I", rec, 2, lba)
    struct.pack_into("<I", rec, 10, size)
    rec[25] = 0x02 if directory else 0
    rec[32] = len(name_b)
    rec[33:33 + len(name_b)] = name_b
    return bytes(rec)


def build(path):
    """A 24-sector disc with one of each interesting shape.

    LBA 16 PVD, 18 root, 19 SMALL, 20-21 SPAN, 22-23 MIXED (23 is Form 2),
    and a directory entry pointing at LBA 900, which the track never
    reaches.
    """
    files = {
        "SMALL.BIN;1": (19, 1000),
        "SPAN.BIN;1": (20, 3000),          # two sectors, crosses a boundary
        "MIXED.BIN;1": (22, 3000),         # sector 22 Form 1, sector 23 Form 2
        "GONE.BIN;1": (900, 2048),         # past the end of the track
    }
    payload = {
        19: b"SMALL" + bytes(range(256)) * 3,
        20: b"SPANA" + bytes(range(256)) * 7,
        21: b"SPANB" + bytes(range(256)) * 7,
        22: b"MIXED" + bytes(range(256)) * 7,
        23: b"FORM2" + bytes(range(256)) * 7,
    }

    root = dir_record("\x00", ROOT_LBA, FORM1_DATA, True) + \
        dir_record("\x01", ROOT_LBA, FORM1_DATA, True)
    for name, (lba, size) in files.items():
        root += dir_record(name, lba, size)

    pvd = bytearray(FORM1_DATA)
    pvd[0] = 1
    pvd[1:6] = b"CD001"
    pvd[40:72] = b"SYNTHETIC".ljust(32)
    pvd[156:190] = dir_record("\x00", ROOT_LBA, FORM1_DATA, True).ljust(34, b"\x00")

    with open(path, "wb") as fh:
        for lba in range(SECTORS):
            if lba == 16:
                fh.write(sector(bytes(pvd)))
            elif lba == ROOT_LBA:
                fh.write(sector(root))
            else:
                fh.write(sector(payload.get(lba, b""), form2=(lba == FORM2_LBA)))
    return files


def _points_at(fd, path):
    """Whether /proc/self/fd/<fd> is an open handle on `path`."""
    try:
        return os.readlink(f"/proc/self/fd/{fd}") == path
    except OSError:
        return False


def check(label, condition, detail=""):
    print(f"  {'ok  ' if condition else 'FAIL'} {label}"
          f"{'  -- ' + detail if detail and not condition else ''}")
    return 0 if condition else 1


def raises(exc, fn, *a):
    try:
        fn(*a)
    except exc:
        return True
    except Exception as other:                       # noqa: BLE001
        print(f"       raised {type(other).__name__}: {other}")
        return False
    return False


def main():
    bad = 0
    tmp = tempfile.mkdtemp(prefix="pes2-selftest-")
    path = os.path.join(tmp, "synthetic.bin")
    build(path)
    original = open(path, "rb").read()
    print(f"synthetic disc: {SECTORS} sectors, {len(original)} bytes")

    with Image(path) as img:
        bad += check("volume id read", img.volume_id == "SYNTHETIC", img.volume_id)
        bad += check("four files found", len(img.files) == 4, str(sorted(img.files)))
        bad += check("SMALL.BIN is form1", img.status("/SMALL.BIN") == "form1")
        bad += check("SPAN.BIN is form1", img.status("/SPAN.BIN") == "form1")
        bad += check("MIXED.BIN is form2", img.status("/MIXED.BIN") == "form2",
                     img.status("/MIXED.BIN"))
        bad += check("GONE.BIN is outside", img.status("/GONE.BIN") == "outside",
                     img.status("/GONE.BIN"))
        bad += check("SPAN.BIN reads 3000 bytes",
                     len(img.read_file("/SPAN.BIN")) == 3000)
        bad += check("SPAN.BIN spans two sectors",
                     img.read_file("/SPAN.BIN")[:5] == b"SPANA"
                     and img.read_file("/SPAN.BIN")[FORM1_DATA:FORM1_DATA + 5]
                     == b"SPANB")
        bad += check("reading a Form 2 sector raises",
                     raises(Form2Sector, img.read_sector, FORM2_LBA))
        bad += check("reading past the track raises",
                     raises(OutsideTrack, img.read_sector, SECTORS))

    # A same-size rewrite is the identity, tail included.
    with Image(path, writable=True) as img:
        img.write_file("/SPAN.BIN", img.read_file("/SPAN.BIN"))
    bad += check("rewriting a file is the identity",
                 open(path, "rb").read() == original)

    # A real edit moves exactly the bytes it should, and nothing in the tail.
    with Image(path, writable=True) as img:
        data = bytearray(img.read_file("/SPAN.BIN"))
        data[FORM1_DATA + 1] = ord("X")              # in the second sector
        img.write_file("/SPAN.BIN", bytes(data))
    now = open(path, "rb").read()
    moved = [i for i, (a, b) in enumerate(zip(original, now)) if a != b]
    bad += check("a one-byte edit moves one byte", len(moved) == 1, str(moved))
    expected = (20 + 1) * RAW_SECTOR + HEADER + 1
    bad += check("and it lands where the arithmetic says",
                 moved == [expected], f"{moved} != [{expected}]")
    # put it back before the refusal tests
    with Image(path, writable=True) as img:
        data = bytearray(img.read_file("/SPAN.BIN"))
        data[FORM1_DATA + 1] = original[(20 + 1) * RAW_SECTOR + HEADER + 1]
        img.write_file("/SPAN.BIN", bytes(data))
    bad += check("and it can be put back",
                 open(path, "rb").read() == original)

    # The three refusals, each of which must leave the image untouched.
    with Image(path, writable=True) as img:
        bad += check("growing a file is refused",
                     raises(ValueError, img.write_file, "/SPAN.BIN",
                            b"x" * 3001))
        bad += check("a mixed Form 1 / Form 2 file is refused",
                     raises(Form2Sector, img.write_file, "/MIXED.BIN",
                            b"x" * 3000))
        bad += check("a file outside the track is refused",
                     raises(OutsideTrack, img.write_file, "/GONE.BIN",
                            b"x" * 2048))
    bad += check("and none of the three wrote a byte",
                 open(path, "rb").read() == original)

    # A failed open must not leave the descriptor behind.
    #
    # Getting this to actually test something took a second try. Simply
    # calling Image() on a bad file and counting descriptors afterwards
    # stays green either way: the unbound file object has no reference
    # left once the exception unwinds, so CPython closes it for us and the
    # explicit close in Image.__init__ never shows. Keeping the traceback
    # alive keeps the frame alive, and the frame is what holds `self` --
    # so with the traceback in hand the descriptor is still open if
    # nothing closed it on purpose.
    truncated = os.path.join(tmp, "truncated.bin")
    with open(truncated, "wb") as fh:
        fh.write(b"\x00" * (RAW_SECTOR + 7))

    def open_bad_keeping_traceback():
        try:
            Image(truncated)
        except ValueError:
            return sys.exc_info()[2]        # frames stay alive with it
        return None

    tb = open_bad_keeping_traceback()
    bad += check("a bad image raises", tb is not None)
    # Scan by target path, not by fd number. Diffing the set of numbers
    # before and against after misses it: the leaked descriptor lands on a
    # low number that was already in use earlier in this run, so the set
    # difference is empty while the file is still open.
    leaked = [fd for fd in os.listdir("/proc/self/fd")
              if _points_at(fd, truncated)]
    bad += check("and closes the descriptor even with the frames alive",
                 not leaked, f"still open: {leaked}")
    del tb

    # The frame comparison the emulator driver is built on, exercised with
    # no emulator in sight -- which is exactly what the shell version it
    # replaced could not do, and why the region comparison that finally
    # told two screens apart had no test behind it for a day.
    try:
        import drive                                          # noqa: E402
        drive.self_check()
        bad += check("drive.py frame logic", True)
    except drive.Skip as why:                                 # noqa: F821
        print(f"  ..   drive.py frame logic skipped: {why}")
    except Exception as exc:                                  # noqa: BLE001
        bad += check("drive.py frame logic", False,
                     f"{type(exc).__name__}: {exc}")

    # The save-state reader, on states built here. It needs neither an
    # emulator nor a disc nor zstd -- the synthetic states are stored
    # uncompressed -- so the only thing that can hold it back is numpy.
    try:
        import savestate                                      # noqa: E402
        failures = savestate.self_check(verbose=False)
        bad += check("savestate.py reader, scan and guards", not failures,
                     ", ".join(failures))
    except savestate.Skip as why:                             # noqa: F821
        print(f"  ..   savestate.py skipped: {why}")
    except Exception as exc:                                  # noqa: BLE001
        bad += check("savestate.py reader, scan and guards", False,
                     f"{type(exc).__name__}: {exc}")

    # The MCP client, its launcher and the routes written on them. All
    # three run with no emulator: what they can prove here is the decoding,
    # the thresholds and the red cases -- including the one that matters
    # most day to day, that an absent server says "the fork is not running"
    # instead of unrolling a urllib traceback.
    for name, what in (("mcp", "mcp.py client, decoding and red cases"),
                       ("fork", "fork.py paths, kill list and refusals"),
                       ("mcp_drive", "mcp_drive.py routes and thresholds")):
        try:
            module = __import__(name)
            failures = module.self_check(verbose=False)
            bad += check(what, not failures, ", ".join(failures))
        except Exception as exc:                              # noqa: BLE001
            bad += check(what, False, f"{type(exc).__name__}: {exc}")

    os.remove(path)
    os.remove(truncated)
    os.rmdir(tmp)
    print("FAILED" if bad else "OK")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())

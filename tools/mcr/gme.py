#!/usr/bin/env python3
"""The DexDrive `.gme` container: a 3,904-byte header in front of a raw card.

Provenance (section 3.4 of the plan):

  container   MEASURED, on the eight cards committed under `mcr/`. No public
              spec was consulted and none is claimed -- what is written below
              is what those files say, and what they do not say is called out
              as unknown
  address     NONE of the save's. The save's 17 destinations live in
              `layout.py` and only there (Rule 1 of section 3.3). The three
              numbers here -- the header length, where the directory mirror
              starts, how long it is -- belong to the wrapper, the same way
              `card.py`'s derived `0x800` belongs to the card
  semantics   --
  codec       --

WHAT WAS MEASURED, 2026-09-09, over `mcr/*.gme`:

  * 134,976 bytes each = 3,904 of header plus the 131,072 of a raw card
  * the card's `MC` sits at 3904 in all eight, without exception
  * `123-456-STD` opens the header in FIVE of the eight; the other three carry
    3,904 zero bytes and hold a perfectly valid card
  * bytes 0x16..0x24 are the fifteen directory states of frames 1..15, byte for
    byte, in all five signed ones -- a mirror of the card that follows
  * 0x12, 0x14 and 0x15 are 0x01, 0x01 and 0x4D; 0x25..0x26 are 00 01
  * from 0x35 to the end of the header: zero in all eight. The comment area a
    DexDrive can fill is empty in every card we have

TWO CONSEQUENCES, and they are the whole design:

1. UNWRAPPING IS LOSSLESS AND IS A CUT. `data[3904:]` is the card, including
   for the three zero-header files -- which a reader that checked the signature
   first would have refused. Detection is by CONTENT (the size, and `MC` at
   3904), never by the name of the file.

2. WRAPPING IS ONLY LOSSLESS IF THE ORIGINAL HEADER COMES BACK. Synthesizing
   one produces the signed form, and three of the eight do not have it. Worse,
   even among the signed five the bytes after the mirror are NOT understood:
   0x27..0x34 is 0xFF except for a 0x03/0x05/0x07 here and there, and
   `synthesize()` writing 0xFF throughout reproduces exactly TWO of those five
   headers. So a card opened from a `.gme` carries its header along and gets it
   back; a card that came from a raw dump gets a synthesized one, and that is
   said out loud rather than pretended to be the same thing.

THE MIRROR IS CHECKED ON THE WAY OUT, not only written. A header whose fifteen
states disagree with the directory of the card beside it would make a DexDrive
list saves that are not there. The check applies to SIGNED headers only: a
zeroed header states nothing, so there is nothing for it to disagree with.

Usage:

    python3 tools/mcr/gme.py <file.gme|file.mcr>
    python3 tools/mcr/gme.py --check mcr/
    python3 tools/mcr/gme.py --self-check
"""

import argparse
import glob
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import card as card_mod                                  # noqa: E402
import harness                                           # noqa: E402
from card import Card, CardError                         # noqa: E402

# --- the wrapper ----------------------------------------------------------

HEADER_BYTES = 3904
SIGNATURE = b"123-456-STD"

# Where the fifteen directory states are echoed, and how many there are. The
# count is DERIVED from the card's directory rather than written again: the two
# have to be the same fifteen, and a mirror that outlived a change to the
# directory would be the one bug this module exists to prevent.
MIRROR_AT = 0x16
MIRROR_BYTES = card_mod.DIRECTORY_FRAMES

# The three fixed bytes before the mirror, and the two after it. Their meaning
# is unknown; they are reproduced because every signed header we have carries
# them, and inventing a different value would be inventing data.
FIXED = {0x12: 0x01, 0x14: 0x01, 0x15: 0x4D}
AFTER_MIRROR = bytes([0x00, 0x01])
# 0x27..0x34, all `0xFF` in two of the five signed headers and MOSTLY 0xFF in
# the other three. See the note above: this is why a preserved header wins.
TAIL_AT = 0x27
TAIL_BYTES = 14
TAIL_FILL = 0xFF

WRAPPED_BYTES = HEADER_BYTES + card_mod.CARD_BYTES

RAW = "raw"
GME = "gme"
# What a name suggests. It decides what is WRITTEN and never what is read.
EXTENSIONS = {".gme": GME, ".mcr": RAW, ".mcd": RAW}


class GmeError(Exception):
    """A container that is not one, or a wrap this module will not perform."""


def looks_wrapped(data: bytes) -> bool:
    """Content, not name: the size, and the card's magic where it must be."""
    return (len(data) == WRAPPED_BYTES
            and data[HEADER_BYTES:HEADER_BYTES + len(card_mod.MAGIC)]
            == card_mod.MAGIC)


def unwrap(data: bytes, origin: str = "<memory>") -> tuple[bytes, bytes]:
    """`.gme` bytes -> (the card, the header). Raises if this is not one."""
    if not looks_wrapped(data):
        raise GmeError(
            f"{origin}: {len(data)} bytes, and a DexDrive .gme has "
            f"{WRAPPED_BYTES} ({HEADER_BYTES} of header plus the "
            f"{card_mod.CARD_BYTES} of a card) with the card's "
            f"{card_mod.MAGIC.decode()} at {HEADER_BYTES}. What is at "
            f"{HEADER_BYTES} here is "
            f"{data[HEADER_BYTES:HEADER_BYTES + 2].hex(' ') or '(nothing)'}.")
    return bytes(data[HEADER_BYTES:]), bytes(data[:HEADER_BYTES])


def mirror(card_bytes: bytes) -> bytes:
    """The fifteen directory states of the card, in frame order."""
    return bytes(card_bytes[(i + 1) * card_mod.FRAME_BYTES]
                 for i in range(MIRROR_BYTES))


def signed(header: bytes) -> bool:
    return header[:len(SIGNATURE)] == SIGNATURE


def mirror_ok(header: bytes, card_bytes: bytes) -> bool:
    """Does the header's mirror agree with the card's directory?

    An unsigned header states nothing -- three of the eight measured files are
    3,904 zero bytes -- so there is nothing to disagree with, and it passes.
    """
    if not signed(header):
        return True
    return header[MIRROR_AT:MIRROR_AT + MIRROR_BYTES] == mirror(card_bytes)


def synthesize(card_bytes: bytes) -> bytes:
    """A signed header for a card that arrived without one."""
    h = bytearray(HEADER_BYTES)
    h[:len(SIGNATURE)] = SIGNATURE
    for at, value in FIXED.items():
        h[at] = value
    h[MIRROR_AT:MIRROR_AT + MIRROR_BYTES] = mirror(card_bytes)
    h[MIRROR_AT + MIRROR_BYTES:MIRROR_AT + MIRROR_BYTES + len(AFTER_MIRROR)] \
        = AFTER_MIRROR
    h[TAIL_AT:TAIL_AT + TAIL_BYTES] = bytes([TAIL_FILL]) * TAIL_BYTES
    return bytes(h)


def wrap(card_bytes: bytes, header: bytes | None = None) -> bytes:
    """card (+ the header it came with) -> `.gme` bytes."""
    if len(card_bytes) != card_mod.CARD_BYTES:
        raise GmeError(
            f"a .gme wraps a whole card of {card_mod.CARD_BYTES} bytes, and "
            f"this is {len(card_bytes)}.")
    if header is None:
        header = synthesize(card_bytes)
    if len(header) != HEADER_BYTES:
        raise GmeError(
            f"the header is {len(header)} bytes and a .gme header is "
            f"{HEADER_BYTES}.")
    if not mirror_ok(header, card_bytes):
        raise GmeError(
            f"the header's directory mirror at {MIRROR_AT:#x} says "
            f"{header[MIRROR_AT:MIRROR_AT + MIRROR_BYTES].hex(' ')} and the "
            f"card's directory says {mirror(card_bytes).hex(' ')}. Writing "
            f"that would make a DexDrive list saves the card does not have.")
    return bytes(header) + bytes(card_bytes)


# --- the file doors -------------------------------------------------------

def read_card(path) -> Card:
    """Open a card from any of the three containers, by content.

    The extension is not consulted, and that is deliberate: nothing makes a
    `.gme` be named `.gme`, and the emulator's `.mcd` is a raw dump under
    another name. What decides is the size and where `MC` sits.
    """
    with open(path, "rb") as fh:
        data = fh.read()
    if looks_wrapped(data):
        card_bytes, header = unwrap(data, origin=str(path))
        return Card(card_bytes, origin=str(path), container=header)
    return Card(data, origin=str(path))


def format_for(path, explicit: str | None = None) -> str:
    """What to WRITE at this path: the explicit choice, else the extension."""
    if explicit is not None:
        if explicit not in (RAW, GME):
            raise GmeError(f"unknown format {explicit!r}; "
                           f"it is {RAW!r} or {GME!r}.")
        return explicit
    return EXTENSIONS.get(os.path.splitext(str(path))[1].lower(), RAW)


def file_bytes(card: Card, fmt: str) -> bytes:
    """The bytes to put on disk, in the format asked for."""
    raw = card.to_bytes()
    if fmt == RAW:
        return raw
    return wrap(raw, card.container)


# --- self-check -----------------------------------------------------------

def self_check(card_path: str | None = None, verbose: bool = True) -> int:
    return harness.run("gme.py", _checks, verbose, card_path=card_path)


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(GmeError)

    synth = card_mod.synthetic_card().to_bytes()

    # --- the shape of the wrapper, with no file anywhere
    made = attempt("wrap a synthetic card", lambda: wrap(synth))
    ok("a wrapped card is header + card",
       made is not None and len(made) == WRAPPED_BYTES,
       f"len={len(made) if made else None}")
    ok("and it is recognised by content", made is not None
       and looks_wrapped(made))
    back = attempt("unwrap it again", lambda: unwrap(made),
                   default=(b"", b""))
    ok("unwrapping gives the card back byte for byte", back[0] == synth)
    ok("the synthesized header is signed", signed(back[1]))
    ok("its mirror is the card's directory", mirror_ok(back[1], synth))

    # THE CONTROL FOR THE PRESERVE PATH, and it needs no fixture. A header of
    # 3,904 zero bytes is what three of the eight measured files carry, and it
    # is the one shape a regenerated header CANNOT reproduce: regeneration
    # signs it. So this is what goes red when `wrap` stops preserving.
    zeroed = bytes(HEADER_BYTES)
    kept = attempt("wrap with a header of zeros",
                   lambda: wrap(synth, zeroed))
    ok("an unsigned header is preserved, not replaced",
       kept is not None and kept[:HEADER_BYTES] == zeroed,
       "a regenerated header would be signed, and three of the eight "
       "measured cards are not")
    ok("and the round-trip of such a file is byte-identical",
       kept is not None and unwrap(kept)[0] == synth
       and wrap(unwrap(kept)[0], unwrap(kept)[1]) == kept)

    # THE CONTROL FOR CONTENT-DETECTION, also with no fixture: the same bytes
    # under a name that says raw. A reader that trusted the extension would
    # hand 134,976 bytes to `Card` and refuse them.
    ok("a wrapped blob is recognised whatever the name says",
       looks_wrapped(made))
    ok("and a raw card is not mistaken for a wrapped one",
       not looks_wrapped(synth))
    with tempfile.TemporaryDirectory() as tmp:
        # THE NAME LIES ON PURPOSE. Nothing makes a container be called `.gme`,
        # and a reader that asked the name instead of the bytes would hand
        # 134,976 bytes to `Card` and refuse a perfectly good card.
        misnamed = os.path.join(tmp, "wrapped-but-called.mcr")
        with open(misnamed, "wb") as fh:
            fh.write(made)
        got = attempt("open a container named .mcr",
                      lambda: read_card(misnamed))
        ok("the name does not decide what is READ",
           got is not None and got.to_bytes() == synth)
        ok("and the wrapper is kept even so",
           got is not None and got.container is not None)

    # --- the refusals
    refuses("refuses to unwrap a raw card",
            lambda: unwrap(synth, origin="<raw>"), "of header plus the")
    refuses("refuses to wrap something that is not a card",
            lambda: wrap(synth[:-1]), "wraps a whole card")
    refuses("refuses a header of the wrong length",
            lambda: wrap(synth, b"\x00" * 10), "is 10 bytes")
    bad = bytearray(synthesize(synth))
    bad[MIRROR_AT] ^= 0xFF
    refuses("refuses a header whose mirror disagrees with the card",
            lambda: wrap(synth, bytes(bad)), "would make a DexDrive list")

    # --- what the name decides, and what it does not
    ok("the extension decides what is written",
       format_for("x.gme") == GME and format_for("x.mcr") == RAW
       and format_for("x.mcd") == RAW)
    ok("an explicit format wins over the extension",
       format_for("x.mcr", GME) == GME)
    ok("an unknown extension writes raw", format_for("x.bin") == RAW)
    refuses("refuses a format that is not one",
            lambda: format_for("x.mcr", "vgs"), "it is 'raw' or 'gme'")

    # --- against the committed cards, when they are there
    root = _repo_root()
    files = sorted(glob.glob(os.path.join(root, "mcr", "*.gme"))) if root \
        else []
    if not files:
        c.skip("the committed cards", "no mcr/*.gme beside this checkout")
        return

    signed_count = 0
    reproduced = 0
    for path in files:
        name = os.path.basename(path)
        with open(path, "rb") as fh:
            data = fh.read()
        ok(f"{name}: is a container by content", looks_wrapped(data),
           f"len={len(data)}")
        if not looks_wrapped(data):
            continue
        card_bytes, header = unwrap(data, origin=path)
        ok(f"{name}: the header's mirror agrees with the directory",
           mirror_ok(header, card_bytes))
        ok(f"{name}: gme -> card -> gme is byte-identical",
           wrap(card_bytes, header) == data)
        if signed(header):
            signed_count += 1
            if synthesize(card_bytes) == header:
                reproduced += 1
        opened = attempt(f"{name}: opens as a card",
                         lambda p=path: read_card(p))
        ok(f"{name}: the opened card carries its header",
           opened is not None and opened.container == header)

    ok(f"five of the {len(files)} committed cards are signed",
       signed_count == 5, f"signed={signed_count}")
    ok("and synthesis reproduces two of those five exactly",
       reproduced == 2,
       f"reproduced={reproduced} -- the bytes after the mirror are not "
       f"understood, which is why a preserved header wins")


def _repo_root() -> str | None:
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(os.path.dirname(here))
    return root if os.path.isdir(os.path.join(root, "docs")) else None


# --- CLI ------------------------------------------------------------------

SKIP = 77


def _check_dir(where: str) -> int:
    files = sorted(glob.glob(os.path.join(where, "*.gme")))
    if not files:
        print(f"gme.py --check: no .gme under {where}", file=sys.stderr)
        return SKIP
    bad = 0
    for path in files:
        with open(path, "rb") as fh:
            data = fh.read()
        try:
            card_bytes, header = unwrap(data, origin=path)
            same = wrap(card_bytes, header) == data
            state = "signed" if signed(header) else "zero header"
            mirrored = "mirror ok" if mirror_ok(header, card_bytes) \
                else "MIRROR DISAGREES"
            print(f"  {'ok  ' if same else 'FAIL'} "
                  f"{os.path.basename(path)}  {state}, {mirrored}")
            bad += 0 if same else 1
        except (GmeError, CardError) as e:
            print(f"  FAIL {os.path.basename(path)}: {e}")
            bad += 1
    print(f"gme.py --check: {len(files) - bad}/{len(files)} containers "
          f"round-trip byte-identical")
    return 1 if bad else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("path", nargs="?", help="a .gme, .mcr or .mcd to inspect")
    ap.add_argument("--check", metavar="DIR", nargs="?", const="",
                    help="round-trip every .gme in DIR (default: mcr/)")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0

    if a.check is not None:
        where = a.check
        if not where:
            root = _repo_root()
            if root is None:
                print("error: no repository root found; give --check DIR",
                      file=sys.stderr)
                return 2
            where = os.path.join(root, "mcr")
        return _check_dir(where)

    if not a.path:
        ap.error("give a file, or use --check / --self-check")

    with open(a.path, "rb") as fh:
        data = fh.read()
    if looks_wrapped(data):
        card_bytes, header = unwrap(data, origin=a.path)
        print(f"file       {a.path}")
        print(f"container  .gme, {HEADER_BYTES} bytes of header + "
              f"{len(card_bytes)} of card")
        print(f"header     {'signed' if signed(header) else 'all zeros'}"
              f"{' (' + SIGNATURE.decode() + ')' if signed(header) else ''}")
        print(f"mirror     {header[MIRROR_AT:MIRROR_AT + MIRROR_BYTES].hex(' ')}")
        print(f"directory  {mirror(card_bytes).hex(' ')}")
        print(f"agree      {'yes' if mirror_ok(header, card_bytes) else 'NO'}")
    else:
        print(f"file       {a.path}")
        print(f"container  raw, {len(data)} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())

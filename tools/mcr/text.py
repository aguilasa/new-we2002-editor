#!/usr/bin/env python3
"""The 10-byte player name -- cp932, and NOT a NUL-terminated string.

Provenance (section 3.4 of the plan):

  container   --
  address     `layout.py`
  semantics   measured (section 1.6 of the plan)
  codec       ours -- `we2002_core`'s `TextCodec` DOES NOT SERVE, see below

WHY `TextCodec` IS THE WRONG TOOL HERE, and it is not a matter of taste.
`KanjiToAscii` reads the field TWO BYTES AT A TIME and only recognises pairs
that begin with 0x82 (letters and digits) or the pair 0x81 0x42 (the full stop).
Everything else falls to its default branch, which emits a space. This field is
a MIXTURE: single-byte halfwidth katakana (0xA1..0xDF) next to two-byte
Shift-JIS. Feed it slot 0 and every pair misses, so ten bytes of a real name
come back as five spaces -- silently, with no error anywhere.

`TextCodec` is not broken. It is right for what it was written for: the team
name on the CD image, which really is stored as 0x82-pairs. It is simply a
different encoding of a different field, and `self_check` runs a transcription
of it against slot 0 so the claim above is a MEASUREMENT and not a story.

The upstream has the same bug and one more on top: it assumes ASCII and runs
`Regex.Replace(text, "[^a-zA-Z.]", "")` before writing, which deletes every
Japanese name outright.

AND THE FIELD IS NOT NUL-TERMINATED. Slot 20 of the fixture uses all ten bytes
with no terminator. Padding is NUL when there is room, so decoding strips
trailing NULs and encoding pads with them -- but a reader that stops at the
first NUL is right 22 times out of 23 and wrong on the one that matters.

Usage:

    python3 tools/mcr/text.py <card.mcr>
    python3 tools/mcr/text.py <card.mcr> --check
    python3 tools/mcr/text.py --self-check
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout                                            # noqa: E402
from card import Card                                    # noqa: E402
import harness                                           # noqa: E402

ENCODING = "cp932"
NAME_BYTES = 10
PAD = 0x00


class TextError(Exception):
    """A name that does not fit ten bytes, or bytes that are not cp932."""


def decode_name(raw: bytes) -> str:
    """Ten bytes -> str. Trailing NUL padding is dropped; nothing else is."""
    if len(raw) != NAME_BYTES:
        raise TextError(f"a name is {NAME_BYTES} bytes, got {len(raw)}")
    trimmed = raw.rstrip(bytes([PAD]))
    try:
        return trimmed.decode(ENCODING)
    except UnicodeDecodeError as e:
        raise TextError(
            f"{raw.hex(' ')} is not {ENCODING}: {e}. This field is a mixture "
            f"of ASCII, halfwidth katakana and two-byte Shift-JIS; a card "
            f"written by a tool that assumed ASCII can hold a broken pair."
        ) from None


def encode_name(name: str) -> bytes:
    """str -> ten bytes, NUL-padded. Refuses rather than truncating."""
    try:
        raw = name.encode(ENCODING)
    except UnicodeEncodeError as e:
        raise TextError(f"{name!r} has no {ENCODING} form: {e}") from None
    if len(raw) > NAME_BYTES:
        raise TextError(
            f"{name!r} needs {len(raw)} bytes in {ENCODING} and the field "
            f"holds {NAME_BYTES}. Truncating would cut a two-byte character "
            f"in half, so this refuses instead.")
    return raw + bytes([PAD]) * (NAME_BYTES - len(raw))


def read(card: Card, index: int) -> str:
    a = layout.player_name_address(index)
    return decode_name(bytes(card.data[a:a + NAME_BYTES]))


def read_all(card: Card) -> list[str]:
    return [read(card, i) for i in range(layout.SQUAD_SIZE)]


def write(card: Card, index: int, name: str) -> None:
    card.write(layout.player_name_address(index), encode_name(name))


# --- the transcription of `KanjiToAscii`, kept only to be shown failing -----

def kanji_to_ascii(kj: bytes, length: int = 6) -> str:
    """`src/core/TextCodec.cpp`'s `KanjiToAscii`, transcribed.

    It is here for one reason: so that "TextCodec does not serve this field"
    is something `self_check` demonstrates rather than something this module
    asserts. Nothing in the port calls it.
    """
    out = []
    for i in range(0, (length - 1) * 2, 2):
        hi, lo = kj[i], kj[i + 1]
        if hi == 130 and 95 < lo < 122:
            out.append(chr(lo - 31))
        elif hi == 130 and 128 < lo < 155:
            out.append(chr(lo - 32))
        elif hi == 130 and 78 < lo < 89:
            out.append(chr(lo - 31))
        elif hi == 129 and lo == 66:
            out.append(".")
        elif hi == 0 and lo == 0:
            out.append("\0")
        else:
            out.append(" ")
    return "".join(out)


# --- self-check ------------------------------------------------------------

def self_check(card_path: str | None=None, verbose: bool=True) -> int:
    return harness.run("text.py", _checks, verbose, card_path=card_path)


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(TextError)
    # The two slots section 1.6 measured, carried here as literals so the
    # module is checkable with no card at all.
    SLOT0 = bytes.fromhex("50a58357aeb0d9835900")
    SLOT20 = bytes.fromhex("834bd8bda5db836fb0bd")

    n0 = attempt("slot 0 decodes", lambda: decode_name(SLOT0))
    n20 = attempt("slot 20 decodes", lambda: decode_name(SLOT20))
    ok("slot 0 decodes to the measured name", n0 == "P･ジｮｰﾙズ", repr(n0))
    ok("slot 20 decodes to the measured name", n20 == "ガﾘｽ･ﾛバｰｽ", repr(n20))
    ok("slot 20 fills all ten bytes with no terminator",
       len(SLOT20.rstrip(b"\x00")) == NAME_BYTES)

    # The case that tells "strip trailing NULs" apart from "stop at the first
    # NUL". NO NAME IN THE FIXTURE HAS AN INTERIOR NUL, so without this every
    # check here passes with either reading -- measured: planting
    # `split(b"\0")[0]` left the whole self-check green. The field is not a
    # C string, so an interior NUL is data and has to survive.
    INTERIOR = b"AB\x00CD\x00\x00\x00\x00\x00"
    ok("an interior NUL is data, not a terminator",
       attempt("decode an interior NUL",
               lambda: decode_name(INTERIOR)) == "AB\x00CD")
    ok("and it round-trips to the same ten bytes",
       attempt("re-encode an interior NUL",
               lambda: encode_name("AB\x00CD")) == INTERIOR)
    ok("slot 0 round-trips",
       attempt("re-encode slot 0", lambda: encode_name(n0)) == SLOT0)
    ok("slot 20 round-trips",
       attempt("re-encode slot 20", lambda: encode_name(n20)) == SLOT20)

    # The demonstration: TextCodec on the same ten bytes.
    via_textcodec = kanji_to_ascii(SLOT0)
    ok("KanjiToAscii turns slot 0 into five spaces",
       via_textcodec == "     ", repr(via_textcodec))
    ok("and it loses a name that cp932 reads fine",
       via_textcodec.strip() == "" and (n0 or "").strip() != "")

    # ASCII still works, which is why the bug is easy to miss.
    ok("a plain ASCII name round-trips",
       attempt("encode SMITH", lambda: encode_name("SMITH"))
       == b"SMITH\x00\x00\x00\x00\x00"
       and attempt("decode SMITH",
                   lambda: decode_name(b"SMITH\x00\x00\x00\x00\x00")) == "SMITH")
    ok("an empty name is ten NULs",
       attempt("encode empty", lambda: encode_name("")) == bytes(NAME_BYTES)
       and attempt("decode empty",
                   lambda: decode_name(bytes(NAME_BYTES))) == "")

    # Ten bytes exactly, in two shapes. Routed through `attempt` because a
    # defect here raises rather than returning something wrong, and an `ok()`
    # whose expression raises kills the run -- measured, twice, in this cycle.
    ten_ascii = attempt("ten ASCII bytes fit",
                        lambda: len(encode_name("ABCDEFGHIJ")))
    ok("ten ASCII bytes fit", ten_ascii == NAME_BYTES, f"got={ten_ascii}")
    five_wide = attempt("five two-byte characters fit",
                        lambda: len(encode_name("ジョンソン")))
    ok("five two-byte characters fit", five_wide == NAME_BYTES,
       f"got={five_wide}")

    refuses("refuses an eleventh ASCII byte",
            lambda: encode_name("ABCDEFGHIJK"), "needs 11 bytes")
    refuses("refuses a name that overflows in two-byte characters",
            lambda: encode_name("ジョンソンズ"), "needs 12 bytes")
    refuses("refuses a field of the wrong size",
            lambda: decode_name(b"\x00" * 9), "10 bytes, got 9")
    refuses("refuses a character cp932 has no form for",
            lambda: encode_name("€"), "no cp932 form")
    refuses("refuses bytes that are not cp932",
            lambda: decode_name(bytes.fromhex("83ff00000000000000 00".replace(" ", ""))),
            "is not cp932")

    # --- against the real card
    card_path = card_path or os.environ.get("WE2002_MCR_CARD")
    if not card_path or not os.path.isfile(card_path):
        print("  skip  the 23 names of the fixture (no WE2002_MCR_CARD)")
    else:
        card = attempt("open the card", lambda: Card.from_file(card_path))
        if card is not None:
            names = attempt("decode the 23 names", lambda: read_all(card),
                            default=None)
            ok(f"all {layout.SQUAD_SIZE} names decode without an exception",
               names is not None and len(names) == layout.SQUAD_SIZE)
            if names:
                def roundtrip_all():
                    out = []
                    for i in range(layout.SQUAD_SIZE):
                        a = layout.player_name_address(i)
                        raw = bytes(card.data[a:a + NAME_BYTES])
                        if encode_name(decode_name(raw)) != raw:
                            out.append(i)
                    return out

                bad = attempt("round-trip the 23 names", roundtrip_all)
                ok(f"encode(decode(b)) == b on all {layout.SQUAD_SIZE}",
                   bad == [], f"differ at {bad}")

                full = [i for i in range(layout.SQUAD_SIZE)
                        if len(bytes(card.data[
                            layout.player_name_address(i):
                            layout.player_name_address(i) + NAME_BYTES
                        ]).rstrip(b"\x00")) == NAME_BYTES]
                ok("at least one name fills all ten bytes",
                   full != [], f"full={full}")

                # `kanji_to_ascii` emits "\0" for a NUL pair, and `str.strip()`
                # does NOT remove it -- stripping only whitespace counted 5 of
                # 23 here and made the codec look partly usable. It is not:
                # with the NULs stripped too, every name comes back blank.
                def via(i):
                    a = layout.player_name_address(i)
                    return kanji_to_ascii(
                        bytes(card.data[a:a + NAME_BYTES])).strip("\0 ")

                lost = [i for i in range(layout.SQUAD_SIZE)
                        if via(i) == "" and names[i].strip() != ""]
                kept = [i for i in range(layout.SQUAD_SIZE)
                        if via(i) == names[i].strip()]
                ok(f"TextCodec blanks all {layout.SQUAD_SIZE} names",
                   len(lost) == layout.SQUAD_SIZE, f"survived={sorted(set(range(layout.SQUAD_SIZE)) - set(lost))}")
                ok("and reproduces none of them", kept == [], f"kept={kept}")


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?")
    ap.add_argument("--check", action="store_true",
                    help="round-trip every name and report byte differences")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check(a.card) else 0

    if not a.card:
        ap.error("give a .mcr, or use --self-check")

    try:
        card = Card.from_file(a.card)
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    bad = []
    for i in range(layout.SQUAD_SIZE):
        addr = layout.player_name_address(i)
        raw = bytes(card.data[addr:addr + NAME_BYTES])
        try:
            name = decode_name(raw)
        except TextError as e:
            print(f"{i:2d}  {raw.hex(' ')}  ERROR: {e}")
            bad.append(i)
            continue
        if a.check and encode_name(name) != raw:
            bad.append(i)
        marker = "  <-- fills all ten bytes" if len(raw.rstrip(b"\x00")) == NAME_BYTES else ""
        print(f"{i:2d}  {raw.hex(' ')}  {name!r}{marker}")

    if a.check:
        print(f"\ntext.py --check: "
              f"{layout.SQUAD_SIZE - len(bad)}/{layout.SQUAD_SIZE} names "
              f"re-encode to the same bytes")
        return 1 if bad else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())

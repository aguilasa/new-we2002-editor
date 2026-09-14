#!/usr/bin/env python3
"""Where things are, and which disc may be read for what.

This is the module the drawing rules of the plan (section 3.3, rule 1) single
out: every address of the `looks` project lives here, and nowhere else.  It
knows no file format and imports no Qt.  Callers hand it bytes or digests and
it answers questions about them, which is what lets its self_check() run on a
machine with no disc image at all.

It does no I/O at all.  It held one exception for as long as the two-disc
guard had no caller -- `--check-discs` opened both real discs itself -- and
LOOKS-TASK-03 cleared that debt on 2026-09-14: the live demonstration now lives
in `iso_source.py --check-discs`, where reading a disc is the module's job.

What is an address, and what is a format?  The line this file draws: the KSEG0
pointer table at the head of a model file is ADDRESS material, so deriving the
load base from it belongs here.  The vertices and primitives those pointers aim
at are FORMAT, and they belong to section.py.  derive_base() reads the pointer
table and stops there; it never looks at a section.

THE RULE THIS FILE EXISTS FOR
-----------------------------
There are two discs and they are not interchangeable:

* the Japanese original is the truth about BYTES.  Textures and palettes are
  read from it and from nothing else;
* the English translation patch is the disc you DRIVE, because its menus are
  legible -- and its geometry is byte-for-byte the same, so driving it is free.

Reading a palette off the English disc is a silent error.  The offset is valid
there, the graphic appears, and it is the wrong graphic: `/BIN/DAT2D.BIN`
differs between the two, and it is exactly the file that holds hair, faces,
bodies, boots and the skin palettes.  Nothing raises, nothing warns.  That is
why the rule is a digest check in code and not a sentence in a document.

Usage:
    python tools/looks/layout.py --check
    python tools/looks/layout.py --sweep
"""

from __future__ import annotations

import hashlib
import os
import re
import sys

# --- The two discs, and how a recipe names each one -----------------------
#
# Two variables because they are two different files, and the second is a
# .cue rather than a .bin: the emulator wants the sheet, the readers want the
# data track.  The PES2 tooling learned this the expensive way -- one family
# of variables for disc tools and another for emulator tools -- and the
# recipe that carried only the first left the one gate that boots the game
# reporting `skipped` in 0.01 s while the run printed `100% tests passed`.
ENV_IMAGE = "WE2002_LOOKS_IMAGE"
"""The Japanese data track (.bin).  The truth about bytes."""

ENV_DRIVE_IMAGE = "WE2002_LOOKS_DRIVE_IMAGE"
"""The English .cue.  The disc to drive the emulator with."""

# --- Paths inside the disc ------------------------------------------------
EDT_MOD = "/BIN/EDT_MOD.BIN"
MODEL = "/BIN/MODEL.BIN"
DAT2D = "/BIN/DAT2D.BIN"
SELECT = "/SELECT.BIN"

# --- Identity of what may be read, measured 2026-09-14 --------------------
#
# sha256 of the FILE as read out of the disc, not of the disc.  Keying on the
# file is what makes the check say something: two dumps of the same release
# can differ in their tail and still hold identical assets, and a translation
# patch can leave the disc the same size while replacing exactly this file.
DIGEST = {
    # Identical on both discs -- this is why the English disc may be driven.
    EDT_MOD: "6ff56894e7ce94aa655047200143087afe85d70cda777e5aee30dedf9d427dd3",
    MODEL: "0b3814bb0d3b47f4ac3b13a1eb9f64ce9c50f8f08331790716827c618c0578cb",
    # Japanese only.  The English disc has
    # 4a4d6a4fe301b1169535c6e5acf7e31c584d725be1571e689ed6fb5696beef60 here,
    # and reading a palette out of that one is the silent error above.
    DAT2D: "0e914e584c889635f0c3a7a64d87ed5c773541c76b35455b6475c19c9f50de7b",
    SELECT: "86d14a66a3cd72b9363832260d4f3842e15d530c2f76eb0d6a3f6823cd603ce1",
}

TEXTURE_FILES = frozenset({DAT2D})
"""Files that may only ever be read from the Japanese disc."""

GEOMETRY_FILES = frozenset({EDT_MOD, MODEL})
"""Files proven identical on both discs, so either may supply them."""

RECORD_FILES = frozenset({SELECT})
"""Japanese-only too, but records rather than art -- so a hint of its own.

/SELECT.BIN is the second of the two files that differ between the discs, and
it holds the player records.  Folding it into TEXTURE_FILES would refuse it
with a sentence about palettes, which is the wrong thing to go looking at.
"""

# The whole-image digest of the Japanese dump, so a recipe can confirm it is
# pointed at the right dump before reading anything.  Both copies on this
# machine -- roms/japanese-shift-jis.bin and the we-2002-original-japao.bin
# under C:\games\ps1\roms\we2002\ -- are this same dump, 307,187,664 bytes,
# measured 2026-09-14.  The English one is 306,834,864 bytes.
IMAGE_DIGEST_JAPANESE = (
    "e853eb14f5bddd50a4a5e77a1da4d22c989a0d99ad5a4927e24e1dba7475abf3"
)
IMAGE_SIZE_JAPANESE = 307187664
IMAGE_SIZE_ENGLISH = 306834864


# --- Where each file sits on the disc -------------------------------------
#
# Measured 2026-09-14 from the directory of roms/japanese-shift-jis.bin, and
# identical on the English disc -- the translation patch replaces content
# in place and moves nothing.  Nothing here READS by LBA (iso.py resolves the
# path through the filesystem, which is what makes the tooling survive a
# different dump); these are recorded because the plan cites them and because
# a changed LBA is the first sign of a rebuilt image.
LBA = {
    EDT_MOD: 5000,
    MODEL: 8100,
    DAT2D: 5300,
    SELECT: 850,
}

SIZE = {
    EDT_MOD: 36072,
    MODEL: 64800,
    DAT2D: 81124,
    SELECT: 300648,
}

# --- Where each model file loads in RAM -----------------------------------
#
# KSEG0 addresses.  Both files are raw -- not LZSS, unlike DAT2D.BIN -- and
# the game copies them to these addresses untouched, which is why a pointer
# inside the file is an absolute RAM address and not a file offset.
#
# These are the constants derive_base() is checked AGAINST, never the source
# of the answer: see require_base().
BASE = {
    EDT_MOD: 0x8011C000,
    MODEL: 0x8016E800,
}

MODEL_GEOMETRY_START = 1816
"""Offset of the first MODEL.BIN section: 107 vertices, 88 primitives.

The number the `we3d` analysis reports for section 0, re-measured here.
"""

PLAYER_RECORD_OFFSET = 157164
PLAYER_RECORD_COUNT = 1242
PLAYER_RECORD_SIZE = 12
"""The packed appearance/attribute records inside /SELECT.BIN.

1,242 x 12 B = 14,904 B ending at 172,068, inside the file's 300,648.  The
offset is third-party opinion (the `Offsets We2002.txt` of the en_we2000edit
sources) and LOOKS-TASK-13 is what confirms the contents; what is checked here
is only that the span fits, which is cheap and catches a typo.
"""


class WrongDisc(Exception):
    """Raised when a file is read from a disc that may not supply it."""


class WrongBase(Exception):
    """Raised when the load address derived from a file is not the known one."""


def digest(data: bytes) -> str:
    """sha256 of *data*, hex, lowercase -- the one spelling used here."""
    return hashlib.sha256(data).hexdigest()


def is_trusted(disc_path: str, data_digest: str) -> bool:
    """Is *data_digest* the content this project expects at *disc_path*?

    Unknown paths answer False rather than True: a file nobody measured is
    not a file anybody may trust.
    """
    return DIGEST.get(disc_path) == data_digest


def _hint_for(disc_path: str) -> str:
    """The sentence that names the real problem behind a refusal at *disc_path*.

    Every path in DIGEST has to get one.  The families are not decoration: a
    mismatch means something different for each, and the reader is being told
    where to look.  self_check() walks DIGEST and demands a non-empty answer
    for every entry, because the way this went wrong the first time was by
    omission -- /SELECT.BIN belonged to no family and fell through to "",
    leaving the bare "digest mismatch" the docstring above calls the failure.
    """
    if disc_path in TEXTURE_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and textures and palettes may only "
            f"be read from the Japanese one.  Point {ENV_IMAGE} at it; "
            f"{ENV_DRIVE_IMAGE} is the disc you drive, not the disc you read."
        )
    if disc_path in RECORD_FILES:
        return (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and the player records are read from "
            f"the Japanese one.  Point {ENV_IMAGE} at it; {ENV_DRIVE_IMAGE} "
            f"is the disc you drive, not the disc you read."
        )
    if disc_path in GEOMETRY_FILES:
        return (
            f"  {disc_path} is identical on both known discs, so a mismatch "
            f"means a third disc -- another release, or a modified image."
        )
    return ""


def require(disc_path: str, data: bytes, image: str = "<unknown image>") -> bytes:
    """Return *data*, or refuse it with a message that names the real problem.

    The message matters as much as the refusal.  The mistake this guards is
    "you opened the English disc", and an exception that only says "digest
    mismatch" sends the reader looking at the parser instead.
    """
    got = digest(data)
    if is_trusted(disc_path, got):
        return data

    expected = DIGEST.get(disc_path)
    if expected is None:
        raise WrongDisc(
            f"{disc_path}: nothing measured for this path, so nothing to "
            f"trust it against (read from {image})"
        )

    hint = _hint_for(disc_path)

    raise WrongDisc(
        f"{disc_path}: read {got} from {image}, expected {expected}.{hint}"
    )


def derive_base(data: bytes) -> tuple[int, int]:
    """Derive the KSEG0 load address of a model file from its own header.

    Returns (header_words, base).

    The method, not the number, is what matters -- a constant nobody can
    re-derive is a constant nobody can check.  Both model files open with a
    run of KSEG0 pointers, and the run ends at the first word that is not one
    (a count, or the 0x000000FF terminator).  The lowest of those pointers
    aims at the first byte past the run, because that is where the record
    list begins.  So:

        base = min(header pointers) - 4 * (number of header words)

    Measured 2026-09-14, and it is one rule for both files even though their
    headers are very different sizes:

        EDT_MOD.BIN   2 words, min 0x8011C008, 0x8011C008 - 8  = 0x8011C000
        MODEL.BIN    18 words, min 0x8016E848, 0x8016E848 - 72 = 0x8016E800

    The 2 and the 18 are not guessed: `lzss.py -v` reports the same header
    lengths for these files ("header 2 w -> stream at 8"), from its own
    reading, which is a second witness to where the run ends.

    **Do not run this over the whole file.** Vertex and colour data is full of
    words with the top bit set -- 642 of them in EDT_MOD.BIN, 1,703 in
    MODEL.BIN -- and only a few dozen are pointers.  Reading those as an
    address table produces targets in the billions and a base that means
    nothing.  The run at the head is bounded precisely because it stops at the
    first non-pointer.
    """
    if len(data) < 8:
        raise WrongBase("file is %d bytes: too short to hold a header" % len(data))

    words = len(data) // 4
    header = 0
    while header < words:
        word = int.from_bytes(data[header * 4:header * 4 + 4], "little")
        if word < 0x80000000:
            break
        header += 1
    else:
        raise WrongBase("every word is a KSEG0 pointer: this is not a model file")

    if header == 0:
        raise WrongBase(
            "the file does not start with a KSEG0 pointer (first word is "
            "0x%08x), so it has no pointer table to derive a base from"
            % int.from_bytes(data[0:4], "little")
        )

    pointers = [
        int.from_bytes(data[i * 4:i * 4 + 4], "little") for i in range(header)
    ]
    base = min(pointers) - 4 * header

    # Every pointer in the run has to land inside the file under that base.
    # This is the cross-check that makes the answer an answer: a base derived
    # from a coincidence would send some of its own siblings out of range.
    for index, pointer in enumerate(pointers):
        target = pointer - base
        if not 0 <= target < len(data):
            raise WrongBase(
                "base 0x%08x puts header pointer %d (0x%08x) at %d, outside "
                "the file's %d bytes" % (base, index, pointer, target, len(data))
            )

    return header, base


def require_base(disc_path: str, data: bytes) -> int:
    """Derive the load base of *data* and demand it match the known constant.

    The constant is in BASE and the answer comes from the file, so the two
    disagreeing is a real event: a different release, a modified image, or a
    file that is not the one its name says.
    """
    expected = BASE.get(disc_path)
    if expected is None:
        raise WrongBase("%s: no load address recorded for this file" % disc_path)

    _header, got = derive_base(data)
    if got != expected:
        raise WrongBase(
            "%s: header derives base 0x%08x, expected 0x%08x -- a different "
            "release, a modified image, or not this file at all"
            % (disc_path, got, expected)
        )
    return got


def self_check() -> None:
    """Exercise the guard on made-up bytes, including the case that must fail.

    Synthetic on purpose: this runs on a machine with no image, no venv and
    no display, which is the contract of the selftest gate.  The live
    demonstration against the two real discs is `--check-discs`.
    """
    # Green: the measured content passes, by construction.
    body = b"whatever"
    saved = DIGEST[DAT2D]
    try:
        DIGEST[DAT2D] = digest(body)
        assert require(DAT2D, body, "fake") is body
        assert is_trusted(DAT2D, digest(body))

        # Red 1: the wrong content is refused, and the message says which
        # disc problem it is rather than just "mismatch".
        try:
            require(DAT2D, b"english", "fake")
        except WrongDisc as exc:
            text = str(exc)
            assert "Japanese" in text, text
            assert ENV_IMAGE in text, text
        else:
            raise AssertionError("DAT2D guard accepted foreign content")
    finally:
        DIGEST[DAT2D] = saved

    # Red 2: a path nobody measured is refused rather than waved through.
    try:
        require("/BIN/NOSUCH.BIN", b"", "fake")
    except WrongDisc as exc:
        assert "nothing measured" in str(exc), str(exc)
    else:
        raise AssertionError("unmeasured path was trusted")

    # Red 3: geometry gets its own wording, because a mismatch there means a
    # third disc and not the English one.
    try:
        require(MODEL, b"not the model", "fake")
    except WrongDisc as exc:
        assert "third disc" in str(exc), str(exc)
    else:
        raise AssertionError("geometry guard accepted foreign content")

    # Red 4: EVERY measured path gets a hint, not just the three with a
    # family.  This one is a sweep rather than a case, on purpose: /SELECT.BIN
    # was refused with a bare "digest mismatch" for exactly as long as it
    # belonged to no family, and the next path added to DIGEST would inherit
    # that silence the same way -- by omission, which no single red case
    # catches.
    for measured in DIGEST:
        assert _hint_for(measured), "no hint for %s" % measured
        try:
            require(measured, b"content from the wrong disc", "fake")
        except WrongDisc as exc:
            text = str(exc)
            assert text.rstrip().endswith("."), text
            assert len(text) > len(
                "%s: read %s from fake, expected %s."
                % (measured, digest(b"x"), DIGEST[measured])
            ), text
        else:
            raise AssertionError("%s guard accepted foreign content" % measured)

    # And the two Japanese-only files say so by name, since "you opened the
    # English disc" is the overwhelmingly likely cause of either refusal.
    for japanese_only in TEXTURE_FILES | RECORD_FILES:
        assert ENV_IMAGE in _hint_for(japanese_only), japanese_only
        assert "Japanese" in _hint_for(japanese_only), japanese_only

    # The two disc variables are two different names.  They have been one
    # name before, in another project, and it cost twelve runs.
    assert ENV_IMAGE != ENV_DRIVE_IMAGE

    # -- derive_base, on a synthetic header shaped like the real ones -------
    #
    # Green: two header words whose lower pointer aims at offset 8.
    synthetic = (
        (0x8011C070).to_bytes(4, "little")
        + (0x8011C008).to_bytes(4, "little")
        + b"\x00" * 512
    )
    assert derive_base(synthetic) == (2, 0x8011C000), derive_base(synthetic)

    # Red 5: a base that would throw one of its own pointers out of the file
    # is refused rather than returned.  Same shape, but the high pointer now
    # aims far past the end.
    outside = (
        (0x8011C008).to_bytes(4, "little")
        + (0x8019C070).to_bytes(4, "little")
        + b"\x00" * 512
    )
    try:
        derive_base(outside)
    except WrongBase as exc:
        assert "outside the file" in str(exc), str(exc)
    else:
        raise AssertionError("derive_base accepted a base its own pointers deny")

    # Red 6: a file that does not begin with a pointer has no table to read,
    # and saying so beats returning a number computed from nothing.
    try:
        derive_base(b"\x02\x00\x00\x00" + b"\x00" * 32)
    except WrongBase as exc:
        assert "no pointer table" in str(exc), str(exc)
    else:
        raise AssertionError("derive_base invented a base for a headerless file")

    # Red 7: require_base reports the mismatch with both numbers, because
    # "wrong base" without the derived value says nothing about which disc.
    elsewhere = (
        (0x80200070).to_bytes(4, "little")
        + (0x80200008).to_bytes(4, "little")
        + b"\x00" * 512
    )
    assert derive_base(elsewhere) == (2, 0x80200000), derive_base(elsewhere)
    try:
        require_base(EDT_MOD, elsewhere)
    except WrongBase as exc:
        assert "expected 0x8011c000" in str(exc).lower(), str(exc)
    else:
        raise AssertionError("require_base accepted a foreign base")

    # -- the address tables agree with each other ---------------------------
    #
    # Every file with a digest has an LBA and a size; a path added to one map
    # and forgotten in the others is the omission this catches, the same way
    # red 4 catches a missing hint.
    for measured in DIGEST:
        assert measured in LBA, "no LBA for %s" % measured
        assert measured in SIZE, "no size for %s" % measured
    assert set(BASE) == GEOMETRY_FILES, (set(BASE), GEOMETRY_FILES)

    # The player records fit inside the file they are said to live in.
    span = PLAYER_RECORD_OFFSET + PLAYER_RECORD_COUNT * PLAYER_RECORD_SIZE
    assert span <= SIZE[SELECT], (span, SIZE[SELECT])

    # MODEL.BIN's geometry starts after its header, not inside it.
    assert MODEL_GEOMETRY_START > 18 * 4

    print("layout: self_check ok")


ADDRESS_OWNER = "layout.py"
"""The one module of tools/looks/ allowed to carry an address (plan 3.3, rule 1)."""


def sweep_addresses(root: str | None = None) -> list[tuple[str, int, str]]:
    """Find addresses written outside this file.  Returns the offending lines.

    Rule 1 of the plan is what lets an offset move later without being hunted
    through the tree, and a rule nobody sweeps is a rule that decays one
    commit at a time.

    What counts as an address: a hexadecimal literal, or a decimal literal of
    four digits or more.  Both are crude on purpose -- this is a tripwire, not
    a parser -- so two escapes exist, and both have to be written down at the
    site rather than assumed:

    * a line carrying `# not-an-address: <why>` is exempt.  The marker is
      spelled as the claim it makes -- an earlier spelling, `# address:`, read
      as the opposite of what the annotator meant, and a tripwire whose
      escape hatch reads backwards will be used wrongly;
    * digits inside a string are not addresses, so a sha256 in a docstring or
      a message does not trip it.

    The walk uses os.walk and not os.listdir: `ui/` is a directory, and the
    .mcr cycle left one of those outside its own sweep exactly this way.
    """
    if root is None:
        root = os.path.dirname(os.path.abspath(__file__))

    hex_literal = re.compile(r"0[xX][0-9a-fA-F]+")
    big_decimal = re.compile(r"(?<![\w.])\d{4,}(?![\w.])")
    findings = []

    for parent, _dirs, names in os.walk(root):
        for name in sorted(names):
            if not name.endswith(".py") or name == ADDRESS_OWNER:
                continue
            path = os.path.join(parent, name)
            with open(path, encoding="utf-8") as handle:
                for number, line in enumerate(handle, 1):
                    code = _strip_strings_and_comments(line)
                    if "# not-an-address:" in line:
                        continue
                    if hex_literal.search(code) or big_decimal.search(code):
                        findings.append(
                            (os.path.relpath(path, root), number, line.rstrip())
                        )
    return findings


def _strip_strings_and_comments(line: str) -> str:
    """Blank out quoted runs and trailing comments, so only code digits remain.

    Deliberately simple: it does not understand triple quotes or escapes, and
    it does not need to.  A digit that survives inside a docstring is a false
    positive a reader can dismiss; a digit hidden from the sweep is the
    failure that matters, and blanking only closed quote pairs cannot hide one
    that is written as bare code.
    """
    out = []
    quote = None
    for char in line:
        if quote:
            out.append(" ")
            if char == quote:
                quote = None
            continue
        if char in "\"'":
            quote = char
            out.append(" ")
            continue
        if char == "#":
            break
        out.append(char)
    return "".join(out)


def _sweep(root: str | None = None) -> int:
    findings = sweep_addresses(root)
    if not findings:
        print("layout --sweep: no address outside %s" % ADDRESS_OWNER)
        return 0
    for path, number, line in findings:
        print("  %s:%d: %s" % (path, number, line.strip()))
    print("layout --sweep: %d line(s) carrying an address outside %s"
          % (len(findings), ADDRESS_OWNER))
    return 1


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        self_check()
        return 0
    if len(argv) == 2 and argv[1] == "--sweep":
        return _sweep()
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

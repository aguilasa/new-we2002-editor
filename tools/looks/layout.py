#!/usr/bin/env python3
"""Where things are, and which disc may be read for what.

This is the module the drawing rules of the plan (section 3.3, rule 1) single
out: every address of the `looks` project lives here, and nowhere else.  It
knows no file format and imports no Qt.  It also does no I/O -- callers hand it
bytes or digests and it answers questions about them, which is what lets its
self_check() run on a machine with no disc image at all.

Today it carries the two-disc rule and nothing more.  LOOKS-TASK-03 adds the
LBAs, the two RAM base addresses and the player-record offset; this file is the
place they go.

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
    python tools/looks/layout.py --check-discs <japanese.bin> <english.bin>
"""

from __future__ import annotations

import hashlib
import os
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


class WrongDisc(Exception):
    """Raised when a file is read from a disc that may not supply it."""


def digest(data: bytes) -> str:
    """sha256 of *data*, hex, lowercase -- the one spelling used here."""
    return hashlib.sha256(data).hexdigest()


def is_trusted(disc_path: str, data_digest: str) -> bool:
    """Is *data_digest* the content this project expects at *disc_path*?

    Unknown paths answer False rather than True: a file nobody measured is
    not a file anybody may trust.
    """
    return DIGEST.get(disc_path) == data_digest


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

    hint = ""
    if disc_path in TEXTURE_FILES:
        hint = (
            f"  {disc_path} differs between the Japanese original and the "
            f"English translation patch, and textures and palettes may only "
            f"be read from the Japanese one.  Point {ENV_IMAGE} at it; "
            f"{ENV_DRIVE_IMAGE} is the disc you drive, not the disc you read."
        )
    elif disc_path in GEOMETRY_FILES:
        hint = (
            f"  {disc_path} is identical on both known discs, so a mismatch "
            f"means a third disc -- another release, or a modified image."
        )

    raise WrongDisc(
        f"{disc_path}: read {got} from {image}, expected {expected}.{hint}"
    )


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

    # The two disc variables are two different names.  They have been one
    # name before, in another project, and it cost twelve runs.
    assert ENV_IMAGE != ENV_DRIVE_IMAGE

    print("layout: self_check ok")


def _check_discs(japanese: str, english: str) -> int:
    """Read the four files off both real discs and show the guard working.

    This reaches for tools/pes2/iso.py directly.  That is temporary: the disc
    facade is LOOKS-TASK-03's `iso_source.py`, and this function moves behind
    it when that exists.  It is here now because a guard nobody has seen go
    red on the real thing is a guard nobody has tested.
    """
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "pes2"))
    import iso  # noqa: E402  (deliberately late -- see the docstring)

    paths = [EDT_MOD, MODEL, DAT2D, SELECT]
    failures = 0

    print("Japanese disc -- everything must be accepted")
    with iso.Image(japanese) as image:
        for path in paths:
            try:
                require(path, image.read_file(path), japanese)
                print("  accepted %s" % path)
            except WrongDisc as exc:
                failures += 1
                print("  REFUSED  %s: %s" % (path, exc))

    print("English disc -- geometry accepted, texture refused")
    with iso.Image(english) as image:
        for path in paths:
            try:
                require(path, image.read_file(path), english)
                verdict = "accepted"
            except WrongDisc:
                verdict = "refused"
            want = "accepted" if path in GEOMETRY_FILES else "refused"
            mark = "ok" if verdict == want else "WRONG"
            if mark == "WRONG":
                failures += 1
            print("  %-8s %-20s (wanted %s) %s" % (verdict, path, want, mark))

    if failures:
        print("layout --check-discs: %d unexpected result(s)" % failures)
        return 1
    print("layout --check-discs: ok")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        self_check()
        return 0
    if len(argv) == 4 and argv[1] == "--check-discs":
        return _check_discs(argv[2], argv[3])
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

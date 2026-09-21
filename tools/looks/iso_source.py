#!/usr/bin/env python3
"""The disc facade: open an image, hand back the bytes of a file inside it.

No ISO reader is written here.  `tools/pes2/iso.py` already reads this image on
this machine, Windows included, and this module wraps it rather than growing a
second one.  What it adds is the thing a bare reader cannot have: **every read
goes through layout.require()**, so a file whose content is not what this
project measured never becomes bytes in anybody's hand.

That is the whole point, and it is worth stating plainly.  The mistake being
guarded is reading a palette off the English translation disc: the offset is
valid there, the graphic appears, and it is the wrong graphic.  A guard that
the caller may or may not invoke does not stop that -- so the checked read is
the ordinary one, and the unchecked read is a separate function with a name
that shows up in a grep.

Usage:
    python tools/looks/iso_source.py --check
    python tools/looks/iso_source.py --check-discs <japanese.bin> <english.bin>
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "pes2"))

import iso  # noqa: E402  (after the path insert, deliberately)

import layout  # noqa: E402


class Disc:
    """One opened disc image, read-only, with the two-disc guard in the path.

    Wraps `iso.Image`.  It deliberately does NOT subclass it: inheriting would
    expose `read_file()` unguarded under the same name the checked read wants,
    and the one thing this class exists to make impossible is an accidental
    unchecked read.
    """

    def __init__(self, path: str):
        self.path = path
        self._image = iso.Image(path)

    # -- the ordinary read ------------------------------------------------
    def read(self, disc_path: str) -> bytes:
        """Bytes of *disc_path*, refused unless they are what we measured.

        Raises layout.WrongDisc when the content does not match, with a
        message that names the likely cause rather than just the mismatch.
        """
        return layout.require(disc_path, self._image.read_file(disc_path), self.path)

    # -- the named escape hatch -------------------------------------------
    def read_unchecked(self, disc_path: str) -> bytes:
        """Bytes of *disc_path* with NO guard.  Two legitimate callers only.

        Comparing two discs is the honest one: you cannot compare against the
        English disc through a guard whose job is to refuse it.  Surveying an
        unmeasured image is the other.  Anything else wants read().

        The name is the point.  `grep -rn read_unchecked tools/looks` lists
        every place the rule is stepped around, which a keyword argument on
        read() would not.
        """
        return self._image.read_file(disc_path)

    def entry(self, disc_path: str):
        """The directory entry (lba, size) -- metadata, so no content to check."""
        return self._image.entry(disc_path)

    def form_of(self, disc_path: str) -> str:
        """"form1", "form2" or "outside" -- metadata too, and what says whether
        a file can be read here at all.  The 105 kit containers are form 1 on
        both discs, and the European dump has 18 of them in form 2 (section 8),
        so it is measured per disc rather than assumed."""
        return self._image.status(disc_path)

    def close(self) -> None:
        self._image.close()

    def __enter__(self) -> "Disc":
        return self

    def __exit__(self, *exc) -> None:
        self.close()


def open_disc(path: str) -> Disc:
    """Open *path* as a data track.  Use as a context manager."""
    return Disc(path)


def read_file(image_path: str, disc_path: str) -> bytes:
    """Open, read one checked file, close.  For a caller that wants only one."""
    with open_disc(image_path) as disc:
        return disc.read(disc_path)


def image_from_env() -> str:
    """The Japanese image named by the environment, or a message saying so.

    Raises RuntimeError naming BOTH variables, because pointing the drive
    variable here is exactly the confusion the two names exist to prevent.
    """
    value = os.environ.get(layout.ENV_IMAGE)
    if not value:
        raise RuntimeError(
            "%s is not set: it names the Japanese data track (.bin), which is "
            "what every read comes from.  %s is the English .cue you drive the "
            "emulator with, and it is not a substitute."
            % (layout.ENV_IMAGE, layout.ENV_DRIVE_IMAGE)
        )
    return value


class _StubImage:
    """An iso.Image-shaped object over a dict, for self_check().

    The gate runs with no disc image, so the red case cannot use a real one.
    What is being tested is this module's own contract -- that read() refuses
    and read_unchecked() does not -- and that needs a reader, not a disc.
    """

    def __init__(self, files: dict):
        self.files = files
        self.closed = False

    def read_file(self, path: str) -> bytes:
        return self.files[path]

    def close(self) -> None:
        self.closed = True


def self_check() -> None:
    """The checked read refuses what the unchecked read returns."""
    good = b"the measured bytes"
    saved = layout.DIGEST[layout.MODEL]
    try:
        layout.DIGEST[layout.MODEL] = layout.digest(good)

        disc = Disc.__new__(Disc)
        disc.path = "stub.bin"
        disc._image = _StubImage({layout.MODEL: good, layout.DAT2D: b"from the wrong disc"})

        # Green: measured content passes through untouched.
        assert disc.read(layout.MODEL) == good

        # Red 1: content that is not what we measured never reaches the caller.
        try:
            disc.read(layout.DAT2D)
        except layout.WrongDisc as exc:
            assert layout.ENV_IMAGE in str(exc), str(exc)
        else:
            raise AssertionError("iso_source.read() returned unmeasured content")

        # Red 2 -- the one that matters most: the escape hatch DOES return it.
        # If this ever raises too, the checked/unchecked pair has collapsed
        # into one behaviour and the guard is no longer the thing being
        # tested by red 1.
        assert disc.read_unchecked(layout.DAT2D) == b"from the wrong disc"

        # Closing goes through to the wrapped image; a leaked descriptor on
        # Windows keeps a 300 MB file locked and the next run fails on open.
        disc.close()
        assert disc._image.closed
    finally:
        layout.DIGEST[layout.MODEL] = saved

    # Red 3: the environment helper names both variables, so the reader is
    # told which of the two is wanted rather than just that one is missing.
    keep = os.environ.pop(layout.ENV_IMAGE, None)
    try:
        try:
            image_from_env()
        except RuntimeError as exc:
            assert layout.ENV_IMAGE in str(exc) and layout.ENV_DRIVE_IMAGE in str(exc)
        else:
            raise AssertionError("image_from_env() accepted an unset variable")
    finally:
        if keep is not None:
            os.environ[layout.ENV_IMAGE] = keep

    # Rule 1 of the plan: this module carries no address.  It names files by
    # the constants of layout.py and never by a number of its own.
    assert layout.MODEL.startswith("/"), layout.MODEL

    print("iso_source: self_check ok")


def _report_bases(disc, paths, seen: dict) -> int:
    """Derive each file's load base from its own header and print the verdict.

    *seen* carries the bases derived on an earlier disc: a path already in it
    must derive the same number here, which is the assertion that geometry is
    interchangeable between the two discs rather than merely claimed to be.

    Returns the number of failures, so the caller can add it to its own.
    """
    failures = 0
    for path in paths:
        data = disc.read_unchecked(path)
        try:
            header, base = layout.derive_base(data)
            layout.require_base(path, data)
        except layout.WrongBase as exc:
            failures += 1
            print("  BASE     %s: %s" % (path, exc))
            continue

        high, inside = layout.pointer_density(data, base)
        before = seen.get(path)
        if before is not None and before != base:
            failures += 1
            mark = "DIFFERS from 0x%08x on the other disc" % before
        else:
            seen[path] = base
            mark = "ok"
        print("  base     %-20s %2d words -> 0x%08x (constant 0x%08x) %s"
              % (path, header, base, layout.BASE[path], mark))
        print("           %d word(s) with the top bit set, %d of them inside "
              "the file under that base" % (high, inside))
    return failures


def _report_kits(disc, kits) -> int:
    """The 105 kit containers through the guard, as one line and a count.

    One line, not 105: they are a set, and what a reader needs from them is
    that every one was accepted and how big the set is.  A refusal names the
    file -- that is the case worth a line of its own.
    """
    refused = []
    forms = {}
    for path in kits:
        forms[disc.form_of(path)] = forms.get(disc.form_of(path), 0) + 1
        try:
            disc.read(path)
        except layout.WrongDisc as exc:
            refused.append((path, exc))
    print("  %d of %d kit container(s) accepted, %s"
          % (len(kits) - len(refused), len(kits),
             ", ".join("%d %s" % (n, kind) for kind, n in sorted(forms.items()))))
    for path, exc in refused:
        print("  REFUSED  %s: %s" % (path, exc))
    return len(refused)


def _check_discs(japanese: str, english: str) -> int:
    """Read the measured files off both real discs and show the guard working.

    This is the live half of the two-disc rule, and it is here rather than in
    layout.py because reading a disc is this module's job -- layout.py does no
    I/O.  It uses read_unchecked() on purpose for the English side: the point
    is to show what would have been returned, and then that read() refuses it.
    """
    paths = sorted(layout.DIGEST)
    kits = sorted(layout.KIT_FILES)
    # What "accepted on the English disc" means: this project measured the
    # file identical on both dumps.  It is not the same set as the geometry --
    # ANIME.BIN and the 105 kits are identical too, and reading only the
    # geometry into that expectation made the command report ANIME.BIN as an
    # unexpected result on every run (found 2026-09-20, LOOKS-TASK-30).
    shared = (layout.GEOMETRY_FILES | layout.ANIMATION_FILES
              | layout.SCREEN_ART_FILES | layout.KIT_FILES)
    geometry = sorted(layout.GEOMETRY_FILES)
    failures = 0
    derived = {}

    print("Japanese disc -- everything must be accepted")
    with open_disc(japanese) as disc:
        for path in paths:
            try:
                disc.read(path)
                print("  accepted %s" % path)
            except layout.WrongDisc as exc:
                failures += 1
                print("  REFUSED  %s: %s" % (path, exc))
        failures += _report_kits(disc, kits)

        # The load base is derived from the file rather than read from the
        # table, every time this command runs.  Without this the two BASE
        # constants are nailed down in practice: derive_base() is exercised
        # only on synthetic vectors built to match the algorithm, so a
        # regression in it would keep --check green and surface in phase 2,
        # far from here.
        failures += _report_bases(disc, geometry, derived)

    print("English disc -- what is identical accepted, the rest refused")
    with open_disc(english) as disc:
        for path in paths:
            try:
                disc.read(path)
                verdict = "accepted"
            except layout.WrongDisc:
                verdict = "refused"
            want = "accepted" if path in shared else "refused"
            mark = "ok" if verdict == want else "WRONG"
            if mark == "WRONG":
                failures += 1
            print("  %-8s %-20s (wanted %s) %s" % (verdict, path, want, mark))

            # And the escape hatch still hands the bytes over, which is what
            # makes the refusal above a decision rather than a read failure.
            assert disc.read_unchecked(path), path

        failures += _report_kits(disc, kits)

        # Geometry is byte-for-byte identical on both discs, so the base
        # derived here has to equal the one derived there.  Free assertion on
        # bytes this command has already read, and it is the reason driving
        # the English disc is allowed at all.
        failures += _report_bases(disc, geometry, derived)

    if failures:
        print("iso_source --check-discs: %d unexpected result(s)" % failures)
        return 1
    print("iso_source --check-discs: ok")
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

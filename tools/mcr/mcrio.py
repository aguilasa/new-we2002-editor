#!/usr/bin/env python3
"""Load, validate, refuse, write -- and the two round-trips that prove it.

Provenance (section 3.4 of the plan):

  container   `card.py`
  address     `layout.py`
  semantics   --
  codec       --

WHY THIS FILE IS NOT CALLED `io.py`. Section 3.2 of the plan names it `io.py`,
and that name does not work: every module here puts `tools/mcr` at the front of
`sys.path`, and `io` is a stdlib module that CPython has already imported and
cached before any of our code runs. `import io` therefore returns the stdlib
one, always -- measured, `io.__file__` comes back as the interpreter's own.
A file called `io.py` here would be runnable as a script and IMPORTABLE BY
NOBODY, which is fatal for the aggregator of MCR-TASK-10. Renaming costs one
line in the plan; discovering it from inside `selftest.py` costs an afternoon.

THE TWO ROUND-TRIPS (section 5.1 of the plan):

  form 1   read the file, write it out. Proves the I/O and nothing else.
  form 2   read it, decode the 23 records into the model, re-encode ALL of
           them, write. This is the one that puts the encoder under test --
           the swapped `speed`/`dribbling` of the upstream's v4.2 shows up
           here and only here.

`cmp` = 0 bytes on both.

THE REFUSALS. Writing is where a tool destroys work, so this module refuses
three things before it starts: the file named by WE2002_MCR_CARD (the fixture
the whole cycle measures against -- shared with the `wte/` cycle, and anchored
by a digest), anything under a `roms/` directory, and any card that is not a
card. `--force` lifts only the first, and says so.

Usage:

    python3 tools/mcr/mcrio.py <card.mcr>
    python3 tools/mcr/mcrio.py <card.mcr> --roundtrip
    python3 tools/mcr/mcrio.py <card.mcr> --edit-probe 0 technique 12
    python3 tools/mcr/mcrio.py --negative
    python3 tools/mcr/mcrio.py --self-check
"""

import argparse
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attributes                                        # noqa: E402
import formation as formation_mod                        # noqa: E402
import layout                                            # noqa: E402
import numbers as numbers_mod                            # noqa: E402
from card import (Card, CardError, FRAME_BYTES, Refused,   # noqa: E402
                  synthetic_card)
from model import Formation, Save                        # noqa: E402
import harness                                           # noqa: E402

CARD_ENV = "WE2002_MCR_CARD"
READ_ONLY_DIR = "roms"


class IoRefused(Exception):
    """A destination this module will not write to."""


# --- reading ---------------------------------------------------------------

def check_card(card: Card) -> Card:
    """The card holds a WE2002 save, or this raises saying what is missing.

    The state byte is the whole of it: an entry flipped from `0x51` to `0xA0`
    still has its name, its size and its link, and a reader that matched on the
    name alone would sail past it into a block the directory says is free.
    That is injection 4 of section 5.2, and this is the guard it lights.
    """
    found = card.find_save()
    if found is None:
        names = [d.name for d in card.directory() if d.name]
        raise CardError(
            f"{card.origin}: no WE2002 save in the directory. The 15 entries "
            f"in use or not are named {names or ['(none)']}; what is looked "
            f"for is a first-block entry whose name ends in WEW-OPT. An entry "
            f"whose state is not 0x51 is not a first block, however right the "
            f"name looks.")
    return card


def load(path) -> Save:
    """File -> validated card -> model. Size, magic and directory, in order."""
    return Save.read(check_card(Card.from_file(path)))


# --- writing ---------------------------------------------------------------

def check_destination(path, force: bool = False) -> str:
    """The path this module agrees to write, or a refusal naming the reason."""
    target = os.path.realpath(str(path))
    parts = target.split(os.sep)
    if READ_ONLY_DIR in parts:
        raise IoRefused(
            f"{target} is under a {READ_ONLY_DIR}/ directory, which holds the "
            f"originals and is never a tool's target. Copy into work/ and "
            f"point at the copy. --force does not lift this one.")
    fixture = os.environ.get(CARD_ENV)
    if fixture and os.path.exists(fixture) \
            and os.path.realpath(fixture) == target:
        if not force:
            raise IoRefused(
                f"{target} is the card named by {CARD_ENV}. It is the fixture "
                f"every measurement in this cycle is anchored to, by digest, "
                f"and the wte/ cycle uses the same file. Write a copy, or pass "
                f"--force if overwriting it is really what you mean.")
    return target


EDITED_SUFFIX = "-edited"


def copy_target(path) -> str:
    """Where a write goes by DEFAULT: a copy beside the card, never the card.

    This is the whole of the copy-first policy, in one place so that it can be
    measured. The only irreversible thing this port does is write over a memory
    card, and a card is a save nobody can re-earn -- every other refusal in
    this file exists for that reason. So the screen's Save lands here, and
    overwriting the file that was opened is a separate action that asks first.

    An already-derived name comes back unchanged, so saving twice in one
    session does not grow `x-edited-edited.mcr`.
    """
    base, ext = os.path.splitext(os.path.abspath(str(path)))
    if base.endswith(EDITED_SUFFIX):
        return base + (ext or ".mcr")
    return base + EDITED_SUFFIX + (ext or ".mcr")


def write_card(card: Card, path, force: bool = False) -> str:
    target = check_destination(path, force=force)
    with open(target, "wb") as fh:
        fh.write(card.to_bytes())
    return target


def store(save: Save, path, force: bool = False) -> str:
    """Model -> card (read-modify-write) -> file."""
    save.write()
    return write_card(save.card, path, force=force)


# --- the round-trips -------------------------------------------------------

def differing(a: bytes, b: bytes) -> list[int]:
    return [i for i, (x, y) in enumerate(zip(a, b)) if x != y]


def roundtrip(path, form: int = 2) -> list[int]:
    """The offsets that changed. Empty is the pass.

    Both forms go through a real file, because "the I/O" is what form 1 is
    about; comparing two buffers in memory would skip the part under test.
    """
    with open(path, "rb") as fh:
        original = fh.read()
    card = check_card(Card(original, origin=str(path)))
    if form == 2:
        Save.read(card).write()
    elif form != 1:
        raise ValueError(f"form {form}: there are two, 1 and 2")
    with tempfile.TemporaryDirectory() as tmp:
        out = write_card(card, os.path.join(tmp, "roundtrip.mcr"))
        with open(out, "rb") as fh:
            written = fh.read()
    if len(written) != len(original):
        raise CardError(
            f"{path}: {len(original)} bytes in, {len(written)} out")
    return differing(original, written)


def edit_probe(path, index: int, field: str, value: int) -> list[int]:
    """Change one field of one player; return the offsets that moved.

    The end-to-end measurement of this task: an edit has to move exactly the
    bytes it names and no others, and this reports them rather than asserting
    them, so the number in the log comes out of a versioned tool.
    """
    with open(path, "rb") as fh:
        original = fh.read()
    card = check_card(Card(original, origin=str(path)))
    save = Save.read(card)
    if field == "number":
        save.set_number(index, value)
    else:
        if field not in attributes.BY_NAME:
            raise ValueError(f"no attribute called {field!r}")
        save.players[index].attributes[field] = value
    save.write_player(index)
    return differing(original, card.to_bytes())


# --- the five injections of section 5.2 ------------------------------------

def _planted_card() -> Card:
    """A synthetic card with a formation on it, so it can be written back."""
    c = synthetic_card()
    formation_mod.write(c, Formation(
        x=list(range(10, 20)), y=list(range(30, 40)),
        role=[0, 1, 4, 5, 6, 8, 12, 14, 15, 17],
        kickers=[7, 7, 8, 7, 7], open_slot_byte=0))
    return c


def negative(verbose: bool = True) -> list[tuple[str, str, bool]]:
    """`(injection, guard, did the guard fire)` for the five of section 5.2.

    Five reds is the pass. A green case is a bug in the guard, not in the
    test -- "a guard that has never been red is decoration".

    The injections are applied to DATA and BEHAVIOUR, not by editing this
    file: each one reproduces what the defect would do, and then asks the
    guard that owns it. The source-substitution controls, which prove the
    guards themselves can go red, live in the task's log.
    """
    out = []

    # 1. Swap speed and dribbling on the way out -- the upstream's v4.2 bug.
    #    Guard: form 2 of the round-trip.
    c = _planted_card()
    s = Save.read(c)
    s.players[0].attributes["speed"] = attributes.BY_NAME["speed"].high
    s.players[0].attributes["dribbling"] = attributes.BY_NAME["dribbling"].low
    s.write()
    before = c.to_bytes()
    buggy = Save.read(c)
    for p in buggy.players:
        a = p.attributes
        a["speed"], a["dribbling"] = a["dribbling"], a["speed"]
    buggy.write()
    out.append(("swap speed and dribbling in the encoder",
                "form 2 of the round-trip", c.to_bytes() != before))

    # 2. Drop the -1 from the shirt-number write. Writing `n + STORED_BIAS`
    #    stores `n`, which is exactly what a missing bias does.
    #    Guard: the cross-check of the two independent copies.
    c2 = _planted_card()
    s2 = Save.read(c2)
    s2.set_number(0, 10)
    s2.write_player(0)
    d = layout.SHIRT_NUMBERS
    table = list(numbers_mod.read(c2))
    table[0] = 10 + numbers_mod.STORED_BIAS
    c2.write(d.address, numbers_mod.encode_table(
        table, bytes(c2.data[d.address:d.address + d.total_bytes])))
    out.append(("drop the -1 from the shirt-number write",
                "the cross-check of the two encoders",
                numbers_mod.cross_check(c2) != []))

    # 3. Write 138 bytes at 0x0000 -- what the upstream's GrabarData does.
    #    Guard: the refusal below the end of the directory.
    c3 = _planted_card()
    fired = False
    try:
        c3.write(0, bytes(138))
    except Refused:
        fired = True
    out.append(("write 138 bytes at offset 0",
                "the refusal below the directory", fired))

    # 4. Flip the state of frame 1 from in-use to free.
    #    Guard: the directory validation on load.
    c4 = _planted_card()
    entry = c4.find_save()[0]
    c4.data[entry.frame * FRAME_BYTES] = 0xA0
    fired = False
    try:
        check_card(c4)
    except CardError:
        fired = True
    out.append(("flip the state of frame 1 to free",
                "the directory validation", fired))

    # 5. Truncate the file by one byte. Guard: the size validation.
    fired = False
    try:
        Card(_planted_card().to_bytes()[:-1], origin="<truncated>")
    except CardError:
        fired = True
    out.append(("truncate the card by one byte",
                "the size validation", fired))

    if verbose:
        for injection, guard, red in out:
            print(f"  {'RED ' if red else 'GREEN'}  {injection}"
                  f"  ->  {guard}")
        print(f"negative control: {sum(1 for _, _, r in out if r)} of "
              f"{len(out)} guards fired")
    return out


# --- self-check ------------------------------------------------------------

def self_check(card_path: str | None=None, verbose: bool=True) -> int:
    return harness.run("mcrio.py", _checks, verbose, card_path=card_path)


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(IoRefused)
    ok("no Qt in the I/O", "PySide6" not in sys.modules)
    # Why this file is not `io.py`: with `tools/mcr` first on `sys.path`,
    # `import io` still resolves to the interpreter's own, because CPython
    # cached it before any of this ran. Asserted, not asserted-in-prose.
    import io as _stdlib_io
    ok("a file called io.py here would be unreachable by import",
       os.path.dirname(os.path.abspath(_stdlib_io.__file__))
       != os.path.dirname(os.path.abspath(__file__)),
       f"io came from {_stdlib_io.__file__}")

    # The refusals, on paths that need no card to exist.
    refuses("refuses to write under roms/",
            lambda: check_destination(os.path.join("roms", "x.mcr")),
            "never a tool's target")
    refuses("--force does not lift the roms/ refusal",
            lambda: check_destination(os.path.join("roms", "x.mcr"),
                                      force=True),
            "--force does not lift this one")

    with tempfile.TemporaryDirectory() as tmp:
        fixture = os.path.join(tmp, "entrada.mcr")
        with open(fixture, "wb") as fh:
            fh.write(_planted_card().to_bytes())
        old = os.environ.get(CARD_ENV)
        os.environ[CARD_ENV] = fixture
        try:
            refuses("refuses to overwrite the card named by the variable",
                    lambda: check_destination(fixture), CARD_ENV)
            ok("--force lifts that one",
               attempt("force the fixture path",
                       lambda: check_destination(fixture, force=True))
               == os.path.realpath(fixture))
            ok("a sibling path is fine",
               attempt("a normal destination",
                       lambda: check_destination(
                           os.path.join(tmp, "copy.mcr"))) is not None)

            # The copy-first policy. The default destination of a write is
            # never the card that was opened -- that is what makes the
            # screen's Save safe without a dialog, and the overwrite a
            # separate act.
            ok("the default destination is never the card that was opened",
               copy_target(fixture) != os.path.abspath(fixture),
               f"copy_target({fixture}) = {copy_target(fixture)}")
            ok("and it is a destination this module agrees to write",
               attempt("the default destination of the fixture",
                       lambda: check_destination(copy_target(fixture)))
               is not None)
            ok("deriving twice does not grow the name",
               copy_target(copy_target(fixture)) == copy_target(fixture),
               f"{copy_target(copy_target(fixture))}")

            # Both round-trips, through real files, on a card that is not the
            # fixture.
            work = os.path.join(tmp, "copy.mcr")
            with open(work, "wb") as fh:
                fh.write(_planted_card().to_bytes())
            ok("form 1 of the round-trip changes no byte",
               attempt("form 1", lambda: roundtrip(work, form=1), [None]) == [],
               "")
            ok("form 2 of the round-trip changes no byte",
               attempt("form 2", lambda: roundtrip(work, form=2), [None]) == [],
               "")

            # The end-to-end edit: one field, one record.
            moved = attempt("edit probe", lambda: edit_probe(
                work, 0, "technique",
                attributes.BY_NAME["technique"].low + 5), [])
            base = layout.player_attribute_address(0)
            ok("one attribute moves only bytes of that player's record",
               moved and all(base <= i < base + attributes.BLOB_BYTES
                             for i in moved),
               f"moved={moved[:8]}")

            # A number moves two places, and the probe shows both.
            moved2 = attempt("number probe",
                             lambda: edit_probe(work, 0, "number", 30), [])
            n = layout.SHIRT_NUMBERS
            ok("a shirt number moves the record and the table, "
               "and nothing else",
               any(base <= i < base + attributes.BLOB_BYTES for i in moved2)
               and any(n.address <= i < n.address + n.total_bytes
                       for i in moved2)
               and all(base <= i < base + attributes.BLOB_BYTES
                       or n.address <= i < n.address + n.total_bytes
                       for i in moved2),
               f"moved={[hex(i) for i in moved2]}")

            # The truncated file, through the real path.
            short = os.path.join(tmp, "short.mcr")
            with open(short, "wb") as fh:
                fh.write(_planted_card().to_bytes()[:-1])
            refuses("refuses a file one byte short", lambda: load(short),
                    "bytes, and a PSX memory card", kind=CardError)

            # A card with no save in the directory.
            blind = os.path.join(tmp, "blind.mcr")
            c = _planted_card()
            c.data[c.find_save()[0].frame * FRAME_BYTES] = 0xA0
            with open(blind, "wb") as fh:
                fh.write(c.to_bytes())
            refuses("refuses a card whose save entry is marked free",
                    lambda: load(blind), "no WE2002 save in the directory",
                    kind=CardError)
        finally:
            if old is None:
                os.environ.pop(CARD_ENV, None)
            else:
                os.environ[CARD_ENV] = old

    # The five injections.
    cases = attempt("the five injections", lambda: negative(verbose=False), [])
    ok("all five guards fire", len(cases) == 5
       and all(red for _, _, red in cases),
       f"green={[i for i, _, r in cases if not r]}")

    # --- against the real card
    card_path = card_path or os.environ.get(CARD_ENV)
    if not card_path or not os.path.isfile(card_path):
        print("  skip  the fixture (no WE2002_MCR_CARD)")
    else:
        before = os.path.getmtime(card_path)
        ok("form 1 on the fixture changes no byte",
           attempt("form 1 on the fixture",
                   lambda: roundtrip(card_path, form=1), [None]) == [])
        ok("form 2 on the fixture changes no byte",
           attempt("form 2 on the fixture",
                   lambda: roundtrip(card_path, form=2), [None]) == [])
        ok("and the fixture itself was not written",
           os.path.getmtime(card_path) == before)


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?")
    ap.add_argument("--roundtrip", action="store_true",
                    help="both forms, byte-identical or the offsets that moved")
    ap.add_argument("--edit-probe", nargs=3,
                    metavar=("SLOT", "FIELD", "VALUE"),
                    help="change one field and report the bytes that moved")
    ap.add_argument("--negative", action="store_true",
                    help="the five injections of section 5.2")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check(a.card) else 0
    if a.negative:
        cases = negative()
        return 0 if all(red for _, _, red in cases) else 1

    if not a.card:
        ap.error("give a .mcr, or use --negative / --self-check")

    try:
        if a.roundtrip:
            rc = 0
            for form in (1, 2):
                moved = roundtrip(a.card, form=form)
                print(f"form {form}: {len(moved)} byte(s) differ"
                      + (f" -- first at {moved[0]:#07x}" if moved else ""))
                rc |= 1 if moved else 0
            return rc
        if a.edit_probe:
            slot, field, value = a.edit_probe
            moved = edit_probe(a.card, int(slot), field, int(value))
            print(f"{field}={value} on slot {slot}: {len(moved)} byte(s) moved")
            for i in moved:
                print(f"  {i:#07x}")
            return 0
        save = load(a.card)
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    entry, blocks = save.card.find_save()
    print(f"{a.card}: {entry.name} in blocks {blocks}")
    print(f"players: {len(save.players)}   "
          f"shirt numbers disagreeing: {len(save.disagreements())}")
    print(f"bad frame checksums: {save.card.bad_checksums() or 'none'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

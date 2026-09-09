#!/usr/bin/env python3
"""One command line over the whole port: info, dump, get, set, roundtrip, ...

Provenance (section 3.4 of the plan): none of the four columns. Every number
this prints comes from a module that owns it.

Subcommands:

    info <card>                      the container and where the save lives
    dump <card>                      the 23 players, the numbers, the formation
    get <card> <slot> [field]        one player, or one field of one player
    set <card> <slot> <field> <v>    write it -- on a COPY, never the fixture
    roundtrip <card>                 both forms of section 5.1
    convert <in> <out>               between .gme, .mcr and .mcd
    negative [--plant]               the five injections; --plant adds the
                                     source-level controls (controls.py
                                     prints how many, and of which kind)
    check [card]                     the fixture gate; exits 77 with no card

`check` IS THE `mcr_card` TARGET, and 77 is not an error: it is what tells
ctest the test skipped. Same convention as the golden tests and `pes2_image`.
A machine with no memory card and no venv sees `2 passed, 2 skipped` and not
a red run -- the second pass is `mcr_container`, whose input is committed.

WRITING IS THE ONE DANGEROUS VERB, so `set` goes through `mcrio.check_destination`
like everything else: it refuses the card named by WE2002_MCR_CARD without
--force, and refuses anything under roms/ with or without it.

Usage:

    python3 tools/mcr/cli.py info work/mcr-entrada.mcr
    python3 tools/mcr/cli.py check
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attributes                                        # noqa: E402
import card as card_mod                                  # noqa: E402
import gme                                               # noqa: E402
import domains                                           # noqa: E402
import formation as formation_mod                        # noqa: E402
import layout                                            # noqa: E402
import mcrio                                             # noqa: E402
import numbers as numbers_mod                            # noqa: E402
from model import Save                                   # noqa: E402

SKIP = 77
CARD_ENV = mcrio.CARD_ENV


def _open(path):
    return mcrio.check_card(mcrio.read_card(path))


def cmd_info(a) -> int:
    c = _open(a.card)
    entry, blocks = c.find_save()
    print(f"file            {a.card}")
    print(f"size            {len(c.to_bytes())} bytes, magic "
          f"{c.to_bytes()[:2].decode('ascii')}")
    print(f"save            {entry.name}")
    print(f"blocks          {blocks}")
    print(f"declared size   {entry.size} bytes")
    bad = c.bad_checksums()
    print(f"bad checksums   {bad if bad else 'none'}")
    for block, state, non_zero in c.stray_blocks():
        print(f"outside chain   block {block}, state {state:#04x}, "
              f"{non_zero} non-zero bytes")
    return 0


def cmd_dump(a) -> int:
    save = Save.read(_open(a.card))
    print("slot  no  name        pos  hgt  age  spd  tec  sta  str")
    for p in save.players:
        v = p.attributes
        print(f" {p.index:3d} {p.shirt_number:3d}  {p.name:<11.11} "
              f"{p.label('position'):>3}  {v['height']:3d}  {v['age']:3d}  "
              f"{v['speed']:3d}  {v['technique']:3d}  {v['stamina']:3d}  "
              f"{v['strength']:3d}")
    bad = save.disagreements()
    print()
    print(f"shirt numbers   the two copies agree on "
          f"{layout.SQUAD_SIZE - len(bad)} of {layout.SQUAD_SIZE}")
    f = save.formation
    print(f"formation X     {f.x}")
    print(f"formation Y     {f.y}")
    print(f"roles           {f.role_labels()}")
    print(f"kickers         {f.kickers}")
    print(f"captain         {f.captain}  (0x6500; measured in MCR-TASK-13, "
          f"domain 0..10 -- the starting eleven)")
    return 0


def cmd_get(a) -> int:
    save = Save.read(_open(a.card))
    p = save.players[a.slot]
    if a.field:
        if a.field not in p.attributes:
            print(f"error: no field called {a.field!r}", file=sys.stderr)
            return 2
        value = p.attributes[a.field]
        label = (f"  {domains.label(a.field, value)}"
                 if a.field in domains.FOR_FIELD else "")
        print(f"{value}{label}")
        return 0
    print(f"slot            {p.index}")
    print(f"name            {p.name!r}")
    print(f"shirt number    {p.shirt_number} (table), "
          f"{p.attributes['number']} (record)")
    for field in sorted(p.attributes):
        value = p.attributes[field]
        label = (f"  {domains.label(field, value)}"
                 if field in domains.FOR_FIELD else "")
        print(f"  {field:<16} {value:3d}{label}")
    return 0


def cmd_set(a) -> int:
    target = mcrio.check_destination(a.card, force=a.force)
    before = open(target, "rb").read()
    save = Save.read(mcrio.check_card(card_mod.Card(before, origin=target)))
    if a.field == "name":
        save.players[a.slot].name = a.value
    elif a.field == "number":
        save.set_number(a.slot, int(a.value))
    elif a.field in attributes.BY_NAME:
        save.players[a.slot].attributes[a.field] = int(a.value)
    else:
        print(f"error: no field called {a.field!r}", file=sys.stderr)
        return 2
    save.write_player(a.slot)
    mcrio.write_card(save.card, target, force=a.force)
    moved = mcrio.differing(before, save.card.to_bytes())
    print(f"{a.field}={a.value} on slot {a.slot}: {len(moved)} byte(s) moved")
    for offset in moved:
        print(f"  {offset:#07x}")
    return 0


def cmd_roundtrip(a) -> int:
    rc = 0
    for form in (1, 2):
        moved = mcrio.roundtrip(a.card, form=form)
        print(f"form {form}: {len(moved)} byte(s) differ"
              + (f" -- first at {moved[0]:#07x}" if moved else ""))
        rc |= 1 if moved else 0
    return rc


def cmd_convert(a) -> int:
    """Between the three containers. The card inside never changes.

    This does NOT go through `check_card`: a container is not a save, and four
    of the eight committed `.gme` are PES2 cards while a fifth has no option
    file at all. Refusing to convert them would be answering a question nobody
    asked -- whether the save inside is one this editor can open is what
    `info` and `dump` are for.
    """
    source = mcrio.read_card(a.source)
    fmt = gme.format_for(a.target, a.format)
    written = mcrio.write_card(source, a.target, force=a.force, fmt=fmt)
    print(f"{a.source} -> {written} ({fmt}, {os.path.getsize(written)} bytes)")
    if fmt == gme.GME and source.container is None:
        print("note: the card had no wrapper, so the header was synthesized. "
              "The bytes after the directory mirror are not understood, and "
              "two of the five signed headers measured reproduce exactly.")
    return 0


def cmd_negative(a) -> int:
    cases = mcrio.negative()
    rc = 0 if all(red for _, _, red in cases) else 1
    if a.plant:
        import controls
        print()
        results = controls.run_all(card_path=os.environ.get(CARD_ENV))
        rc |= 0 if all(r.good for r in results) else 1
    return rc


def cmd_check(a) -> int:
    """The fixture gate. Skips with 77 when there is no card to measure."""
    path = a.card or os.environ.get(CARD_ENV)
    if not path or not os.path.isfile(path):
        print(f"skipped: no memory card. Point {CARD_ENV} at a .mcr, or pass "
              f"one as an argument.")
        return SKIP
    import harness

    def body(c) -> None:
        ok, attempt = c.ok, c.attempt
        digest_before = attempt("read the card", lambda: open(path, "rb").read())
        save = attempt("load the card", lambda: mcrio.load(path))
        ok("the card holds a WE2002 save", save is not None)
        if save is None:
            return
        ok("23 players decoded", len(save.players) == layout.SQUAD_SIZE)
        ok("the two copies of every shirt number agree",
           save.disagreements() == [], f"{save.disagreements()}")
        ok("the shirt-number tripwire is quiet",
           numbers_mod.cross_check(save.card) == [])
        ok("no frame checksum is broken", save.card.bad_checksums() == [])
        for form in (1, 2):
            moved = attempt(f"round-trip form {form}",
                            lambda f=form: mcrio.roundtrip(path, form=f),
                            default=None)
            ok(f"round-trip form {form} changes no byte", moved == [],
               f"{moved[:8] if moved else moved}")
        cases = attempt("the five injections",
                        lambda: mcrio.negative(verbose=False), default=[])
        ok("all five guards fire on the real card",
           len(cases) == 5 and all(red for _, _, red in cases))
        # Every cross-check that has an oracle on disk.
        problems = attempt("layout --check",
                           lambda: layout.check(verbose=False), default=None)
        ok("17/17 destinations agree with the measurement", problems == [],
           f"{problems}")
        clone = layout.find_upward(os.path.join("work", "easy-mcr"))
        if not clone:
            c.skip("the upstream cross-checks (no work/easy-mcr)")
        else:
            ok("14/14 label tables match the upstream",
               attempt("domains --check",
                       lambda: domains.check(clone, verbose=False),
                       default=None) == [])
            ok("21/21 upstream weight tables match our shifts",
               attempt("attributes --upstream-weights",
                       lambda: attributes.check_upstream_weights(
                           clone, verbose=False), default=None) == [])
        ok("the card on disk was not written",
           open(path, "rb").read() == digest_before)

    return 1 if harness.run("mcr_card", body) else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="command", required=True)

    p = sub.add_parser("info", help="the container and where the save lives")
    p.add_argument("card")
    p.set_defaults(fn=cmd_info)

    p = sub.add_parser("dump", help="the squad, the numbers, the formation")
    p.add_argument("card")
    p.set_defaults(fn=cmd_dump)

    p = sub.add_parser("get", help="one player, or one field of one player")
    p.add_argument("card")
    p.add_argument("slot", type=int)
    p.add_argument("field", nargs="?")
    p.set_defaults(fn=cmd_get)

    p = sub.add_parser("set", help="write one field -- on a copy")
    p.add_argument("card")
    p.add_argument("slot", type=int)
    p.add_argument("field")
    p.add_argument("value")
    p.add_argument("--force", action="store_true",
                   help="allow writing the card named by the variable")
    p.set_defaults(fn=cmd_set)

    p = sub.add_parser("roundtrip", help="both forms of section 5.1")
    p.add_argument("card")
    p.set_defaults(fn=cmd_roundtrip)

    p = sub.add_parser("convert", help="between .gme, .mcr and .mcd")
    p.add_argument("source")
    p.add_argument("target")
    p.add_argument("--format", choices=(gme.RAW, gme.GME),
                   help="override what the target's extension says")
    p.add_argument("--force", action="store_true",
                   help="allow writing the card named by the variable")
    p.set_defaults(fn=cmd_convert)

    p = sub.add_parser("negative", help="the injections, and the controls")
    p.add_argument("--plant", action="store_true",
                   help="also plant the source-level controls")
    p.set_defaults(fn=cmd_negative)

    p = sub.add_parser("check", help="the fixture gate; 77 when there is none")
    p.add_argument("card", nargs="?")
    p.set_defaults(fn=cmd_check)

    a = ap.parse_args(argv)
    try:
        return a.fn(a)
    except (card_mod.CardError, gme.GmeError, mcrio.IoRefused) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())

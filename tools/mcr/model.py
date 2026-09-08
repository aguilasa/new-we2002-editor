#!/usr/bin/env python3
"""The model: 23 players and one formation, as a VIEW over the raw card.

Provenance (section 3.4 of the plan):

  container   `card.py`
  address     `layout.py` -- and nowhere else, this file included
  semantics   the modules underneath (`attributes`, `numbers`, `text`,
              `formation`, `domains`)
  codec       theirs; this module owns none

RULE 2 IS THE WHOLE DESIGN OF THIS FILE. The card's bytes stay in `card.Card`
and are edited by read-modify-write in the field. What lives here is a VIEW:
reading it builds dataclasses, writing it puts each field back where it came
from and touches nothing else. That is what carries the ten untouched bytes at
the end of every 32-byte record, the slack in the block, the directory and the
six tactics bytes through a round-trip unchanged.

The counter-example is the upstream, which reassembles the file from its own
buffers -- and that is exactly why it can write over the header.

TWO COPIES OF THE SHIRT NUMBER, AND THIS MODULE KEEPS THEM APART. The number
is in the 12-byte record AND in the 5-bit table, and the fixture has all 23
agreeing. `Player.attributes["number"]` is the record's copy and
`Player.shirt_number` is the table's; `write()` puts each back where it was
read from, so a card that arrives disagreeing leaves disagreeing. Reconciling
silently would burn the best tripwire this port has (section 1.5 of the plan).
Whoever wants both changed calls `set_number()`, which says so.

Usage:

    python3 tools/mcr/model.py <card.mcr>
    python3 tools/mcr/model.py --self-check
"""

import argparse
import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import attributes                                        # noqa: E402
import domains                                           # noqa: E402
import formation as formation_mod                        # noqa: E402
import layout                                            # noqa: E402
import numbers as numbers_mod                            # noqa: E402
import text                                              # noqa: E402
from card import Card                                    # noqa: E402
from formation import Formation                          # noqa: E402
import harness                                           # noqa: E402

SQUAD_SIZE = layout.SQUAD_SIZE


class ModelError(Exception):
    """A slot index, a field name or a value the card cannot hold."""


@dataclasses.dataclass
class Player:
    """One squad slot: the record, the name, and the table's shirt number."""

    index: int
    name: str
    attributes: dict[str, int]
    shirt_number: int

    @property
    def number_agrees(self) -> bool:
        """The tripwire, per player. False means an encoder is wrong."""
        return self.attributes["number"] == self.shirt_number

    def label(self, field: str) -> str:
        """The upstream's name for a coded field. Third-party label."""
        return domains.label(field, self.attributes[field])

    def set_number(self, number: int) -> None:
        """Change BOTH copies of the shirt number, and say so by name.

        The card stores it in the 12-byte record and in the 5-bit table, and
        moving one is how a card starts disagreeing with itself. Whoever wants
        both changed calls this; whoever sets `attributes["number"]` alone gets
        reported by the cross-check, which is the point of having two.
        """
        self.attributes["number"] = number
        self.shirt_number = number

    def set_name(self, name: str) -> None:
        """The only supported way to change the name -- it refuses what will
        not fit rather than truncating.

        Ten bytes of cp932, and a two-byte character straddling the tenth is
        why `text.encode_name` refuses. The check belongs here and not on the
        screen: a line edit holds any string at all, and the field does not.
        """
        text.encode_name(name)
        self.name = name


@dataclasses.dataclass
class Save:
    """The card, plus the decoded view of it.

    `card` is not a copy: it is the object the writes go to. Holding it here
    is what makes `write()` a read-modify-write instead of a rebuild.
    """

    card: Card
    players: list[Player]
    formation: Formation

    # -- reading ----------------------------------------------------------

    @classmethod
    def read(cls, card: Card) -> "Save":
        table = numbers_mod.squad(card)
        players = [
            Player(
                index=i,
                name=text.read(card, i),
                attributes=attributes.decode(attributes.player_blob(card, i)),
                shirt_number=table[i],
            )
            for i in range(SQUAD_SIZE)
        ]
        return cls(card=card, players=players,
                   formation=formation_mod.read(card))

    def disagreements(self) -> list[tuple[int, int, int]]:
        """`(slot, table, record)` where the two copies of the number differ."""
        return [(p.index, p.shirt_number, p.attributes["number"])
                for p in self.players if not p.number_agrees]

    # -- writing ----------------------------------------------------------

    def write_player(self, index: int) -> None:
        """One slot back to the card, field by field.

        Three writes: the 12-byte record (read-modify-write, so the four gap
        bits survive), the 10-byte name, and the slot's 5 bits in the table.
        The ten bytes after the name are never addressed and therefore never
        change.
        """
        if not 0 <= index < SQUAD_SIZE:
            raise ModelError(
                f"slot {index} is outside 0..{SQUAD_SIZE - 1}")
        p = self.players[index]
        old = attributes.player_blob(self.card, index)
        self.card.write(layout.player_attribute_address(index),
                        attributes.encode(p.attributes, old))
        text.write(self.card, index, p.name)
        self._write_number(index, p.shirt_number)

    def _write_number(self, index: int, number: int) -> None:
        d = layout.SHIRT_NUMBERS
        table = list(numbers_mod.read(self.card))
        table[index] = number
        self.card.write(
            d.address,
            numbers_mod.encode_table(
                table,
                bytes(self.card.data[d.address:d.address + d.total_bytes])))

    def set_number(self, index: int, number: int) -> None:
        """Change BOTH copies of a shirt number, and say so by name.

        The only supported way to change a number. Setting
        `attributes["number"]` alone leaves the table behind, and the
        cross-check will report it -- which is the point of having two.
        """
        self.players[index].set_number(number)

    def write(self) -> None:
        """Every player and the formation back to the card.

        This is form 2 of the round-trip (section 5.1 of the plan): decoding
        the 23 records and re-encoding all of them is what puts the encoder
        under test. Form 1 -- read the file and write it out -- only proves
        the I/O.
        """
        for i in range(SQUAD_SIZE):
            self.write_player(i)
        formation_mod.write(self.card, self.formation)


# --- the door the UI is allowed to open -------------------------------------

def load(path) -> Save:
    """Open a card and return the model. THE UI'S ONLY WAY IN.

    Rule 3 forbids `tools/mcr/ui/*.py` from importing `layout`, `card` or
    `mcrio`, and the selftest sweeps for it -- so the window needs a door that
    is not one of those three. This is it: one function, no address, no
    container, no path policy of its own.

    The import is DEFERRED on purpose and not a style tic: `mcrio` imports this
    module at its top, so importing it back here at module scope is a cycle.
    Inside the function it runs after both modules exist. The validation is
    still `mcrio`'s -- size, magic and the directory entry -- because writing a
    second, weaker loader for the UI is exactly how a screen ends up reading a
    card the gate would have refused.
    """
    import mcrio
    return mcrio.load(path)


def store(save: Save, path, force: bool = False) -> str:
    """Flush the model into the card and write it out. THE UI'S ONLY WAY OUT.

    The mirror of `load()`, deferred for the same reason, and delegating for a
    stronger one: `mcrio.store` keeps the three refusals -- `roms/`, the
    fixture named by the variable, and a destination that is not writable --
    and calls `Save.write()` before the file is opened. A window that wrote the
    file itself would be a second writer with none of that, and it would be the
    one running when it matters.

    `force` is passed through and the UI never sets it: lifting the fixture
    refusal is a decision for whoever typed the command, not for a screen.
    """
    import mcrio
    return mcrio.store(save, path, force=force)


def copy_target(path) -> str:
    """Where a write goes by default: a copy, never the card that was opened.

    The policy is `mcrio`'s; this is the door, because Rule 3 keeps the screen
    out of that module.
    """
    import mcrio
    return mcrio.copy_target(path)


# --- self-check ------------------------------------------------------------

def self_check(card_path: str | None=None, verbose: bool=True) -> int:
    return harness.run("model.py", _checks, verbose, card_path=card_path)


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(ModelError)
    ok("the squad is 23 slots", SQUAD_SIZE == 23)
    ok("no Qt in the model", "PySide6" not in sys.modules)

    from card import synthetic_card
    c = synthetic_card()
    s = attempt("read a synthetic card", lambda: Save.read(c))
    ok("23 players come out", s is not None and len(s.players) == SQUAD_SIZE)
    ok("each player knows its own slot",
       s is not None and [p.index for p in s.players] == list(range(SQUAD_SIZE)))
    ok("the formation comes out too",
       s is not None and isinstance(s.formation, Formation))

    # A blank card has every number stored as zero, which decodes to 1 in both
    # copies -- so they agree, and the tripwire is silent for the right reason.
    ok("the two copies agree on a blank card",
       s is not None and s.disagreements() == [])

    # A synthetic card has a formation region of zeros, and the role is stored
    # as index + 2 -- so it reads back as -2 and `formation.write` refuses it,
    # rightly: there is no formation there to preserve. Plant one, so that what
    # this check measures is the round-trip and not the blank card.
    attempt("plant a formation on the synthetic card",
            lambda: formation_mod.write(c, Formation(
                x=list(range(10, 20)), y=list(range(30, 40)),
                role=[0, 1, 4, 5, 6, 8, 12, 14, 15, 17],
                kickers=[7, 7, 8, 7, 7], open_slot_byte=0)))
    s = attempt("read it again", lambda: Save.read(c), s)
    refuses("a zeroed formation region refuses to be written back",
            lambda: formation_mod.write(
                c, dataclasses.replace(s.formation, role=[-2] * 10)),
            "always reads as -2", kind=formation_mod.FormationError)

    # Write the whole squad back: nothing may move.
    before = c.to_bytes()
    attempt("write the whole squad back", lambda: s.write())
    ok("re-encoding all 23 changes no byte on a synthetic card",
       c.to_bytes() == before,
       f"differ at "
       f"{[i for i, (a, b) in enumerate(zip(c.to_bytes(), before)) if a != b][:8]}")

    # `write()` has to reach the card. Measured as a control in MCR-TASK-09:
    # with its loop cut to `range(0)` every "changes no byte" check above
    # stayed green, because writing nobody changes nothing. Only mcrio.py's
    # injection caught it. A round-trip check needs a companion that proves
    # the writer ran.
    s.players[SQUAD_SIZE - 1].attributes["stamina"] = \
        attributes.BY_NAME["stamina"].low + 4
    attempt("write the squad after an edit", lambda: s.write())
    back = attempt("read the squad back", lambda: Save.read(c))
    ok("write() reaches the card -- it is not a loop over nobody",
       back is not None
       and back.players[SQUAD_SIZE - 1].attributes["stamina"]
       == attributes.BY_NAME["stamina"].low + 4,
       f"stamina={back.players[SQUAD_SIZE - 1].attributes['stamina'] if back else None}")
    before = c.to_bytes()

    # One field, one place. `technique` is not stored twice, unlike `number`.
    s.players[0].attributes["technique"] = \
        attributes.BY_NAME["technique"].low + 3
    attempt("write slot 0", lambda: s.write_player(0))
    moved = [i for i, (a, b) in enumerate(zip(c.to_bytes(), before)) if a != b]
    base = layout.player_attribute_address(0)
    ok("editing one attribute stays inside that player's 12-byte record",
       moved and all(base <= i < base + attributes.BLOB_BYTES for i in moved),
       f"moved={moved[:8]}")

    # Both copies of the number, changed the only supported way.
    before2 = c.to_bytes()
    attempt("set a number", lambda: s.set_number(1, 30))
    attempt("write slot 1", lambda: s.write_player(1))
    reread = attempt("read the card again", lambda: Save.read(c))
    ok("set_number moves both copies",
       reread is not None and reread.players[1].shirt_number == 30
       and reread.players[1].attributes["number"] == 30,
       f"table={reread.players[1].shirt_number if reread else None} "
       f"record={reread.players[1].attributes['number'] if reread else None}")
    ok("and the tripwire stays quiet",
       reread is not None and reread.disagreements() == [])
    moved_n = [i for i, (a, b) in enumerate(zip(c.to_bytes(), before2))
               if a != b]
    rec1 = layout.player_attribute_address(1)
    tab = layout.SHIRT_NUMBERS
    ok("a number touches the record and the table, and nothing else",
       any(rec1 <= i < rec1 + attributes.BLOB_BYTES for i in moved_n)
       and any(tab.address <= i < tab.address + tab.total_bytes
               for i in moved_n)
       and all(rec1 <= i < rec1 + attributes.BLOB_BYTES
               or tab.address <= i < tab.address + tab.total_bytes
               for i in moved_n),
       f"moved={[hex(i) for i in moved_n]}")

    # Changing only the record's copy must be VISIBLE, not repaired.
    s2 = attempt("read once more", lambda: Save.read(c))
    if s2 is not None:
        s2.players[2].attributes["number"] = 17
        attempt("write slot 2", lambda: s2.write_player(2))
        s3 = attempt("read after the half edit", lambda: Save.read(c))
        ok("half an edit is reported, not silently reconciled",
           s3 is not None and [d[0] for d in s3.disagreements()] == [2],
           f"disagreements={s3.disagreements() if s3 else None}")

    # The write door, end to end. `store()` is what the screen calls, and the
    # failure it has to be able to report is the one MCR-TASK-09 measured on
    # `Save.write` -- a path that opens the file without flushing the model
    # writes a card with none of the edits in it, and every "no byte moved"
    # check stays green. So: edit, store, re-read from DISK, demand the value.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        s4 = attempt("read for the store probe", lambda: Save.read(c))
        if s4 is not None:
            s4.players[3].attributes["heading"] = \
                attributes.BY_NAME["heading"].low + 6
            s4.players[3].set_number(19)
            out = os.path.join(tmp, "stored.mcr")
            written = attempt("store the model", lambda: store(s4, out))
            ok("store() writes the file it names", written is not None
               and os.path.isfile(out))
            reread = attempt("read the stored file back",
                             lambda: Save.read(Card.from_file(out)))
            ok("store() flushes the model -- the edit survives the file",
               reread is not None
               and reread.players[3].attributes["heading"]
               == attributes.BY_NAME["heading"].low + 6
               and reread.players[3].shirt_number == 19,
               f"heading={reread.players[3].attributes['heading'] if reread else None} "
               f"number={reread.players[3].shirt_number if reread else None}")
            ok("the default destination is a copy, not the file opened",
               copy_target(out) != os.path.abspath(out))

    refuses("refuses a name that does not fit ten bytes",
            lambda: s.players[0].set_name("A" * 11), "holds 10",
            kind=text.TextError)
    refuses("refuses a slot past the squad",
            lambda: s.write_player(SQUAD_SIZE), "outside 0..22")
    refuses("refuses a negative slot",
            lambda: s.write_player(-1), "outside 0..22")

    # --- against the real card
    card_path = card_path or os.environ.get("WE2002_MCR_CARD")
    if not card_path or not os.path.isfile(card_path):
        print("  skip  the fixture (no WE2002_MCR_CARD)")
    else:
        real = attempt("open the card", lambda: Card.from_file(card_path))
        if real is not None:
            original = real.to_bytes()
            live = attempt("read the fixture", lambda: Save.read(real))
            ok("23 names decoded",
               live is not None and len(live.players) == SQUAD_SIZE)
            ok("the two copies of the number agree 23 of 23",
               live is not None and live.disagreements() == [],
               f"differ={live.disagreements() if live else None}")
            # Form 2 on a COPY in memory. The fixture is never written.
            copy = Card(original, origin="<copy>")
            view = attempt("read the copy", lambda: Save.read(copy))
            attempt("re-encode all 23 and the formation",
                    lambda: view.write())
            ok("form 2 of the round-trip changes no byte",
               copy.to_bytes() == original,
               f"differ at "
               f"{[i for i, (a, b) in enumerate(zip(copy.to_bytes(), original)) if a != b][:8]}")


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("card", nargs="?")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check(a.card) else 0

    if not a.card:
        ap.error("give a .mcr, or use --self-check")

    try:
        save = Save.read(Card.from_file(a.card))
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    print(" slot  no  name         pos  spd  tec  sta")
    for p in save.players:
        v = p.attributes
        print(f"  {p.index:2d}  {p.shirt_number:3d}  {p.name:<11.11}  "
              f"{p.label('position'):>3}  {v['speed']:3d}  "
              f"{v['technique']:3d}  {v['stamina']:3d}")
    bad = save.disagreements()
    print()
    print(f"shirt numbers: the two copies agree on "
          f"{SQUAD_SIZE - len(bad)} of {SQUAD_SIZE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

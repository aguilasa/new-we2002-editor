#!/usr/bin/env python3
"""The formation: X[10], Y[10], the ten roles, the five kickers, the open byte.

Provenance (section 3.4 of the plan):

  container   --
  address     `layout.py`
  semantics   THE UPSTREAM (section 1.7) -- this is where it genuinely adds
  codec       ours

Our reverse engineering had `0x62A8` (20 B) and `0x63D5` (10 B) as opaque
ranges. Zetaprog says they are the X and Y of the ten outfield players and
their positional role, and nothing in the fixture contradicts him -- but
nothing in the fixture confirms the MEANING either, so the field names here are
his and are marked as such.

THREE THINGS THAT ARE EASY TO GET WRONG, all of them measured:

  the role is stored as INDEX + 2, over the 20 labels in `domains.ROLE`;

  the kickers live in a table that DECREASES and then jumps back up --
  0x614F, 0x6140, 0x6122, 0x6113, 0x6131. Arithmetic in place of the table
  writes into the wrong field and the result still looks like a formation;

  `X*7` and `Y*2` are SCREEN factors, not format. They scale the pitch widget
  in the upstream's window. They are not in this module and must not be: put
  them in and the round-trip dies.

THE CAPTAIN, AND IT WAS OUR READING THAT WAS WRONG. `0x6500` was carried as
`open_slot_byte` while section 1.8 of the plan had it as the captain by our RE
of the `.exe` and a sixth kicker by the upstream. MCR-TASK-13 settled it, and
the two third parties never disagreed:

  the Obocaman editor's `estrategia` form puts six markers on one grid, and
  the sixth one's label reads `Hint = 'Captain'`, `Caption = 'CP'`;
  driving that grid -- six columns on six distinct rows -- puts 0, 1, 2, 3, 4
  in the five kicker addresses and **5 here**, so this byte is written by that
  sixth column and by nothing else;
  the upstream writes 25856 from a local called `CP`, beside `SF`, `LF`, `RC`,
  `LC` and `PK`.

"Sixth kicker" was read off its POSITION -- sixth in a group of six -- and not
off any label. The byte is now written like every other field.

THE MEASURED DOMAIN IS 0..10, because the grid has eleven rows: the starting
eleven, not the twenty-three squad slots. The write below still accepts any
byte, because refusing a value this port merely does not understand would
destroy a card it was only asked to carry; the domain lives on the screen,
where it is a choice offered rather than a rule enforced.

Usage:

    python3 tools/mcr/formation.py <card.mcr>
    python3 tools/mcr/formation.py --self-check
"""

import argparse
import dataclasses
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import domains                                           # noqa: E402
import layout                                            # noqa: E402
from card import Card                                    # noqa: E402
import harness                                           # noqa: E402

OUTFIELD = layout.OUTFIELD_COUNT      # 10 -- the goalkeeper has no X/Y here
ROLE_BIAS = 2                         # the role is stored as index + 2
KICKERS = len(layout.KICKER_ADDRESSES)


class FormationError(Exception):
    """A coordinate, role or slot index outside what the field holds."""


@dataclasses.dataclass
class Formation:
    """What the card holds, in the card's own units.

    `x`, `y` and `role` are ten long. `kickers` is five slot indices in KICKER
    ORDER, which is not address order. `captain` is `0x6500`, measured in
    MCR-TASK-13; its domain is the eleven starters, 0..10.
    """

    x: list[int]
    y: list[int]
    role: list[int]
    kickers: list[int]
    captain: int

    def role_labels(self) -> list[str]:
        """The upstream's names. Third-party labels, no oracle."""
        return [domains.ROLE[r] if 0 <= r < len(domains.ROLE)
                else domains.UNNAMED for r in self.role]


def _slice(card: Card, dest) -> bytes:
    return bytes(card.data[dest.address:dest.address + dest.total_bytes])


def read(card: Card) -> Formation:
    xy = _slice(card, layout.FORMATION_XY)
    roles = _slice(card, layout.FORMATION_ROLES)
    return Formation(
        x=list(xy[:OUTFIELD]),
        y=list(xy[OUTFIELD:]),
        role=[b - ROLE_BIAS for b in roles],
        kickers=[card.data[a] for a in layout.KICKER_ADDRESSES],
        captain=card.data[layout.CAPTAIN.address],
    )


def _check_lengths(f: Formation) -> None:
    for name, seq, n in (("x", f.x, OUTFIELD), ("y", f.y, OUTFIELD),
                         ("role", f.role, OUTFIELD),
                         ("kickers", f.kickers, KICKERS)):
        if len(seq) != n:
            raise FormationError(f"{name} has {len(seq)} entries, expected {n}")


def write(card: Card, f: Formation) -> None:
    """Read-modify-write, field by field. Nothing else on the card is touched.

    `captain` IS written back, and has been since MCR-TASK-13 measured what it
    is. It was not before: writing a byte whose meaning is unsettled is how a
    round-trip stops being evidence, and until the verdict the port carried it
    through untouched.
    """
    _check_lengths(f)
    for i, v in enumerate(f.x):
        if not 0 <= v <= 0xFF:
            raise FormationError(f"x[{i}]={v} does not fit a byte")
    for i, v in enumerate(f.y):
        if not 0 <= v <= 0xFF:
            raise FormationError(f"y[{i}]={v} does not fit a byte")
    for i, r in enumerate(f.role):
        if not 0 <= r < len(domains.ROLE):
            extra = ""
            if r < 0:
                # MEASURED in MCR-TASK-09: the role is stored as index + 2, so
                # a byte of 0 reads back as -2. A card whose formation region
                # was never written -- a blank card, the synthetic one -- comes
                # out of `read()` like this and cannot be written back. That is
                # correct and not a round-trip failure: there is no formation
                # there to preserve. Without this clause the message is just
                # "-2", and the reader looks for a decoder bug.
                extra = (f" -- the stored byte is {r + ROLE_BIAS}, and a "
                         f"formation region of zeros always reads as "
                         f"{-ROLE_BIAS}")
            raise FormationError(
                f"role[{i}]={r} is outside 0..{len(domains.ROLE) - 1}{extra}")
    for k, slot in enumerate(f.kickers):
        if not 0 <= slot <= 0xFF:
            raise FormationError(f"kicker {k}={slot} does not fit a byte")
    if not 0 <= f.captain <= 0xFF:
        raise FormationError(f"captain={f.captain} does not fit a byte")

    card.write(layout.FORMATION_XY.address, bytes(f.x) + bytes(f.y))
    card.write(layout.FORMATION_ROLES.address,
               bytes(r + ROLE_BIAS for r in f.role))
    for k, slot in enumerate(f.kickers):
        card.write(layout.kicker_address(k), bytes([slot]))
    card.write(layout.CAPTAIN.address, bytes([f.captain]))


# --- self-check ------------------------------------------------------------

def self_check(card_path: str | None=None, verbose: bool=True) -> int:
    return harness.run("formation.py", _checks, verbose, card_path=card_path)


def _checks(c, card_path: str | None = None) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(FormationError)
    ok("ten outfield players", OUTFIELD == 10)
    ok("five kickers", KICKERS == 5)
    ok("the kicker table is not increasing",
       list(layout.KICKER_ADDRESSES) != sorted(layout.KICKER_ADDRESSES))
    ok("the 20 bytes of 0x62A8 are exactly X then Y",
       layout.FORMATION_XY.total_bytes == 2 * OUTFIELD)
    ok("the roles are ten bytes",
       layout.FORMATION_ROLES.total_bytes == OUTFIELD)

    # A synthetic card, so this runs with no fixture.
    from card import synthetic_card
    c = synthetic_card()

    # The screen factors must not be here (section 1.7): X*7 and Y*2 scale the
    # upstream's pitch widget. Asserted BEHAVIOURALLY -- an earlier version of
    # this check grepped the module's own source for "* 7" and "* 2" and went
    # red on the arithmetic inside the self-check itself. A lint against your
    # own file measures the file, not the behaviour.
    probe = Formation(x=[7] * OUTFIELD, y=[2] * OUTFIELD, role=[0] * OUTFIELD,
                      kickers=[0] * KICKERS, captain=0)
    attempt("write the scaling probe", lambda: write(c, probe))
    ok("X reaches the card unscaled",
       c.data[layout.FORMATION_X_ADDRESS] == 7,
       f"byte={c.data[layout.FORMATION_X_ADDRESS]} (49 would mean X*7)")
    ok("Y reaches the card unscaled",
       c.data[layout.FORMATION_Y_ADDRESS] == 2,
       f"byte={c.data[layout.FORMATION_Y_ADDRESS]} (4 would mean Y*2)")
    wanted = Formation(
        x=list(range(10, 20)),
        y=list(range(30, 40)),
        role=[0, 1, 4, 5, 6, 8, 12, 14, 15, 19],
        kickers=[1, 2, 3, 4, 5],
        captain=0,
    )
    attempt("write a formation to a synthetic card", lambda: write(c, wanted))
    got = attempt("read it back", lambda: read(c))
    ok("X, Y and the roles survive the round-trip",
       got is not None and got.x == wanted.x and got.y == wanted.y
       and got.role == wanted.role, f"got={got}")
    ok("the kickers survive, in kicker order",
       got is not None and got.kickers == wanted.kickers,
       f"got={got.kickers if got else None}")
    ok("the role went to the card as index + 2",
       c.data[layout.FORMATION_ROLES.address] == wanted.role[0] + ROLE_BIAS,
       f"byte={c.data[layout.FORMATION_ROLES.address]}")
    ok("kicker 0 went to the highest address of the table",
       c.data[layout.KICKER_ADDRESSES[0]] == 1
       and layout.KICKER_ADDRESSES[0] == max(layout.KICKER_ADDRESSES))
    ok("role labels come out of the third-party table",
       got is not None and got.role_labels()[0] == "CB-L"
       and got.role_labels()[-1] == "RW", f"labels={got.role_labels() if got else None}")

    # The captain goes both ways since MCR-TASK-13. Read first...
    c.data[layout.CAPTAIN.address] = 0x2A
    reread = attempt("read after poking the captain", lambda: read(c))
    ok("the captain is read", reread is not None and reread.captain == 0x2A)
    # ...and then written, which is the half that did not exist before the
    # verdict. A writer that skips one field leaves every round-trip check
    # green, so the check demands the byte MOVE to what the model says.
    attempt("write a captain",
            lambda: write(c, dataclasses.replace(wanted, captain=6)))
    ok("write() puts the captain on the card",
       c.data[layout.CAPTAIN.address] == 6,
       f"captain={c.data[layout.CAPTAIN.address]}")
    attempt("write the original back", lambda: write(c, wanted))

    # Writing the formation must not touch the tactics bytes next door.
    tactics_before = {t.address: c.data[t.address] for t in layout.TACTICS}
    attempt("write once more", lambda: write(c, wanted))
    ok("the six tactics bytes are untouched",
       all(c.data[a] == v for a, v in tactics_before.items()))

    refuses("refuses a role past the 20 labels",
            lambda: write(c, dataclasses.replace(wanted, role=[20] * 10)),
            "outside 0..19")
    refuses("refuses nine roles",
            lambda: write(c, dataclasses.replace(wanted, role=[0] * 9)),
            "role has 9 entries")
    refuses("refuses four kickers",
            lambda: write(c, dataclasses.replace(wanted, kickers=[1] * 4)),
            "kickers has 4 entries")
    refuses("refuses an X that does not fit a byte",
            lambda: write(c, dataclasses.replace(wanted, x=[256] + [0] * 9)),
            "does not fit a byte")

    # --- against the real card
    card_path = card_path or os.environ.get("WE2002_MCR_CARD")
    if not card_path or not os.path.isfile(card_path):
        print("  skip  the fixture (no WE2002_MCR_CARD)")
    else:
        real = attempt("open the card", lambda: Card.from_file(card_path))
        if real is not None:
            f = attempt("read the fixture formation", lambda: read(real))
            ok("X matches the measurement",
               f is not None and f.x == [0x0b, 0x0b, 0x0b, 0x0f, 0x0f, 0x14,
                                         0x1f, 0x1f, 0x2c, 0x29],
               f"x={f.x if f else None}")
            ok("Y matches the measurement",
               f is not None and f.y == [0x20, 0x34, 0x48, 0x11, 0x57, 0x32,
                                         0x1e, 0x3e, 0x2a, 0x3e],
               f"y={f.y if f else None}")
            ok("the roles match the measurement",
               f is not None and f.role == [0, 1, 4, 5, 6, 8, 12, 14, 15, 17],
               f"role={f.role if f else None}")
            ok("the kickers are [7, 7, 8, 7, 7]",
               f is not None and f.kickers == [7, 7, 8, 7, 7],
               f"kickers={f.kickers if f else None}")
            ok("the captain is 8, inside the measured domain 0..10",
               f is not None and f.captain == 8 and 0 <= f.captain <= 10,
               f"captain={f.captain if f else None}")

            # Round-trip on a COPY in memory; the fixture is never written.
            copy = Card(real.to_bytes(), origin="<copy>")
            attempt("rewrite the fixture formation", lambda: write(copy, f))
            ok("reading and rewriting the fixture changes no byte",
               copy.to_bytes() == real.to_bytes(),
               f"differ at "
               f"{[i for i, (a, b) in enumerate(zip(copy.to_bytes(), real.to_bytes())) if a != b][:8]}")


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
        card = Card.from_file(a.card)
    except Exception as e:                            # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2

    f = read(card)
    print(" slot   X    Y   role")
    for i in range(OUTFIELD):
        print(f"  {i:2d}   {f.x[i]:3d}  {f.y[i]:3d}   "
              f"{f.role[i]:2d} {f.role_labels()[i]}")
    print()
    print(f"kickers (kicker order): {f.kickers}")
    print(f"captain (0x6500) = {f.captain}  -- measured in MCR-TASK-13; "
          f"the domain is the eleven starters, 0..10")
    return 0


if __name__ == "__main__":
    sys.exit(main())

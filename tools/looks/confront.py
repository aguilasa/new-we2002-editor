#!/usr/bin/env python3
"""The confrontation: the game's frame against ours, on the same tuple.

Plan section 5.3.  The loop is `load_state`, the tuple chosen ON THE GAME'S
SCREEN by `press_button`, `take_screenshot` on a frame counted from the state,
our viewer drawing the same tuple, and a number.

**The number cannot be a pixel difference, and the reason is measured.**  Our
render is a shelf of pieces under a free camera; the game's is a posed figure
under its own framing, animated.  Two pictures of the same head in different
places differ in almost every pixel, so a pixel metric would measure the pose
and the camera and nothing about the tuple.  What survives pose, camera and
resolution is WHICH COLOURS are drawn and in what proportion -- and on this
screen that is the whole tuple: the skin row, the hair colour and the beard
colour are CLUT windows (LOOKS-TASK-12), and the hair style and the beard pick
texels and meshes.  Measured before any of this was written: the fourteen
15-bit colours of our A-A1-A-A-A head all appear, EXACTLY, in the game's frame
-- the PSX draws these quads unmodulated, so a texel's colour on screen is the
palette entry itself.

So the metric is **colour-histogram intersection over 15-bit colours** (Swain
and Ballard's colour indexing): for a game frame and one of our renders,
`sum(min(h_game[c], h_ours[c]))` over the colours our renders can draw, both
histograms normalised.  1.0 is the same colour distribution, 0.0 is no colour
in common.  **And it is never read alone** -- trap 26 of the profile: every
game frame is scored against ALL of our renders of the slot, so beside each
number stands the score of the wrong tuples.  The verdict is whether the right
tuple wins its row.

Usage:
    python tools/looks/confront.py --check
    python tools/looks/confront.py --run            # both slots, ~40 min
    python tools/looks/confront.py --run 2          # one slot
    python tools/looks/confront.py --score          # re-judge the last run
    python tools/looks/confront.py --reach FACE     # how far a row walks
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import looks  # noqa: E402

SKIP = 77

START = "A-A1-A-A-A"
"""The tuple both save states restore.

Read off the screen on 2026-09-16, both slots: every one of the five rows says
ATYPE / A1TYPE.  The route is built as presses AWAY from this tuple, so a state
re-recorded on another player would move every route by an unknown amount --
which is why `--run` checks the reference frame before anything else.
"""

TUPLES = (
    "A-A1-A-A-A",
    "B-A1-A-A-A",
    "A-A1-C-A-A",
    "A-I3-A-A-A",
    "A-A1-A-B-E",
    "A-H1-A-A-A",
)
"""The tuples confronted, and what each one exercises.

* the reference, which costs no press and anchors the rest;
* `B` skin -- a CLUT row, the largest colour change the screen has;
* `C` hair colour -- a CLUT column over the hair's six entries;
* `I3` hair style -- another head section, 34, and another mesh;
* `B` beard in colour `E` -- a band and a column on two quads, the smallest
  change here, which is what says how fine the metric can see;
* `H1` -- a style the assembly table REFUSES.  It is routed and captured like
  the others, and on our side it must come back as a refusal, not a score.
"""

SLOT_FIGURE = {2: 0, 1: 1}
"""Which of EDT_MOD.BIN's two lists each save state shows.

List 0 is the outfield player and list 1 the goalkeeper, measured by
LOOKS-TASK-08 from which sections SKIN moved in each state.
"""

SHOT_ROW = "HAIR"
"""Where the cursor rests for the picture.  On SKIN and HAIR the game frames the
face; on the other rows it shows the whole figure, and a whole figure is mostly
kit -- which our side cannot draw (LOOKS-TASK-15)."""

SHOT_FRAMES = 30
"""Frames stepped after the last press and before the picture.  Counted, never
waited: the whole route is a fixed number of frames from `load_state`."""

PANEL = (0.040, 0.270, 0.310, 0.780)
"""The portrait panel, as fractions of the frame.  Measured off 864x655
captures of both slots: the blue box under the position plate."""

RENDER_SIZE = (640, 640)
PIECE = "head"

RANK = 32
"""Colour depth per channel on the PSX: 5 bits, so a colour is value // 8."""

MARGIN = 0.02
"""How far the right tuple must beat the best wrong one to count as a win.

Two renders of nearly the same colours score within a hair of each other, and a
win by 0.001 is a coin toss dressed as a verdict.  The beard tuple is the case
that decides whether this can be met; a miss there is the metric's resolution,
and it is printed as such rather than hidden by a smaller margin.
"""

GOALKEEPER_HEAD = ("the goalkeeper's head: HAIR_MAP was measured on the "
                   "outfield player only, so figure 1 draws the disc's section "
                   "24 whatever the style -- and draws it without refusing "
                   "(CORR-LOOKS-043)")
"""Kept as the record of the residue it named.  Since CORR-LOOKS-043 figure 1
REFUSES those styles, our side of the matrix drops them the way slot 2 drops
H1, and EXPECTED has nothing left to excuse."""

EXPECTED = {}
"""Misses that are a named residue and not a finding.  Anything else that loses
its row is unexplained, and the run fails."""


class ConfrontError(Exception):
    """A confrontation that could not be measured, or measured wrong."""


# ---- the route -----------------------------------------------------------

def rows_of(text: str) -> dict:
    """{screen row: steps from START} for one tuple -- negative is Left."""
    want = looks.parse_tuple(text)
    base = looks.parse_tuple(START)
    return {looks.BY_NAME[name].row: want[name] - base[name]
            for name in looks.TUPLE_ORDER}


def plan(text: str, rows: tuple, start_row: str) -> list:
    """[(row, button, count)] in screen order, then the move to SHOT_ROW.

    Screen order and not tuple order: the cursor walks down the list once, and
    a route that jumps back and forth is a route with more presses to lose.
    The last entry moves the cursor with no value press, so the picture is
    always taken on the same row.
    """
    steps = rows_of(text)
    out = []
    for row in sorted(steps, key=rows.index):
        count = steps[row]
        if count:
            out.append((row, "Right" if count > 0 else "Left", abs(count)))
    out.append((SHOT_ROW, None, 0))
    if start_row not in rows:
        raise ConfrontError("the cursor starts on %r, which is not a row"
                            % start_row)
    return out


def moves(rows: tuple, here: str, there: str) -> tuple:
    """(button, count) that takes the cursor from one row to another."""
    delta = rows.index(there) - rows.index(here)
    return ("Down" if delta > 0 else "Up", abs(delta))


# ---- the metric ----------------------------------------------------------

def quantise(pixel) -> tuple:
    return (pixel[0] // (256 // RANK), pixel[1] // (256 // RANK),
            pixel[2] // (256 // RANK))


def histogram(shot, box=None, drop=None) -> dict:
    """{15-bit colour: count} over a picture, or a box of it.

    `drop` is one colour left out -- our render's background, which is not a
    drawn pixel.  The game frame keeps everything; it is restricted later, to
    the colours our side can draw.
    """
    width, height, channels, rows = shot
    x0, y0, x1, y1 = (0, 0, width, height) if box is None else (
        int(box[0] * width), int(box[1] * height),
        int(box[2] * width), int(box[3] * height))
    out: dict = {}
    for y in range(y0, y1):
        row = rows[y]
        for x in range(x0, x1):
            colour = quantise(row[x * channels:x * channels + 3])
            if colour == drop:
                continue
            out[colour] = out.get(colour, 0) + 1
    return out


def restrict(counts: dict, palette) -> dict:
    return {colour: n for colour, n in counts.items() if colour in palette}


def intersection(first: dict, second: dict) -> float:
    """Histogram intersection of two normalised histograms, 0..1."""
    total_a, total_b = sum(first.values()), sum(second.values())
    if not total_a or not total_b:
        return 0.0
    return sum(min(n / total_a, second.get(colour, 0) / total_b)
               for colour, n in first.items())


def verdict(scores: dict, slot: int, alike: dict | None = None,
            expected: dict | None = None) -> dict:
    """{tuple: (outcome, why)} over one slot's matrix.

    `scores[(game tuple, our tuple)]` is the intersection, and `alike[(ours,
    other)]` how alike OUR OWN two renders are.  Three outcomes:

    * **win** -- the right render leads every other one by MARGIN;
    * **ranked** -- it leads every other one, and some lead is under MARGIN;
    * **unexplained** -- some other render scores at least as high.  A failure.
    * and **expected** -- a named residue in EXPECTED, which is not judged.

    **Why `ranked` exists, and it was added after the first run was read --
    said so, because a rule written after the data is the kind that fits it.**
    The reason is not the data but a bound: for normalised histograms,
    `I(g, a) - I(g, b) <= 1 - I(a, b)`, since `min(g, a) - min(g, b)` never
    exceeds `max(a - b, 0)`.  So no game frame, however right the table, can
    lead by more than our own two renders are apart.  Measured on 2026-09-16:
    our reference and our `A-A1-A-B-E` are 0.961 alike -- the beard moves 2.39%
    of the head (CORR-LOOKS-038) -- so the most either can lead the other by is
    0.039, and a MARGIN of 0.02 asks for half the ceiling from frames that score
    0.77 of a perfect match.  A lead under MARGIN is therefore printed with that
    ceiling beside it, and does not fail; ranking second does.

    Two renders IDENTICAL on our side (alike 1.0) say nothing about each other,
    so a twin is left out of the comparison -- when EXPECTED names it.  An
    unnamed twin is our side drawing two tuples the same, and it fails.
    """
    alike = alike or {}
    expected = EXPECTED if expected is None else expected
    ours = sorted({mine for _game, mine in scores})
    out = {}
    for game in sorted({g for g, _mine in scores}):
        if game not in ours:
            continue
        if (slot, game) in expected:
            out[game] = ("expected", expected[(slot, game)])
            continue
        twins = [o for o in ours if o != game and alike.get((game, o)) == 1.0]
        if any((slot, o) not in expected for o in twins):
            out[game] = ("unexplained", "our render of it is identical to %s"
                         % ", ".join(twins))
            continue
        right = scores[(game, game)]
        rivals = [o for o in ours if o != game and o not in twins]
        if not rivals:
            out[game] = ("unexplained", "nothing to be compared against")
            continue
        best = max(rivals, key=lambda o: scores[(game, o)])
        wrong = scores[(game, best)]
        if right - wrong >= MARGIN:
            out[game] = ("win", "by %.3f over %s" % (right - wrong, best))
        elif right > wrong:
            out[game] = ("ranked", "first by %.3f over %s, whose render ours "
                                   "is %.3f apart from -- the most any lead "
                                   "can be" % (right - wrong, best,
                                               1.0 - alike.get((game, best),
                                                               0.0)))
        else:
            out[game] = ("unexplained", "%.3f, and %s scores %.3f"
                         % (right, best, wrong))
    return out


# ---- the diagonal --------------------------------------------------------

QUAD_UV_WORDS = {9: (2, 4, 6, 8), 12: (2, 5, 8, 11)}
"""Where the four (u, v) sit in a textured quad packet, by packet length.

Flat-shaded (nine words): colour+command, then vertex and texcoord alternating.
Gouraud (twelve): colour, vertex and texcoord per corner.  The GPU draws a quad
as the triangles (0, 1, 2) and (1, 2, 3) of THIS order, which is what makes the
packet the judge of the diagonal.
"""

UNTANGLED = (1, 0, 3, 2)
"""`section.Primitive.corners` as a permutation of the stored order."""


def packet_texcoords(data: bytes, commands: dict) -> list:
    """[(clut, ((u, v) x 4))] of every textured quad node in a band."""
    import struct

    out = []
    for start in range(0, len(data) - 8, 4):
        word = struct.unpack_from("<I", data, start)[0]
        length = word >> 24
        code = data[start + 7]
        if code not in commands or commands[code][1] != length:
            continue
        if "textured quad" not in commands[code][0] or length not in \
                QUAD_UV_WORDS:
            continue
        if start + 4 + 4 * length > len(data):
            continue
        body = start + 4
        uvs = tuple((data[body + 4 * w], data[body + 4 * w + 1])
                    for w in QUAD_UV_WORDS[length])
        clut = struct.unpack_from("<H", data, body + 4 * QUAD_UV_WORDS[length][0]
                                  + 2)[0]
        out.append((clut, uvs))
    return out


ROW_SLACK = 1
"""How far a `v` may sit from the file's and still be the same corner.

Measured on 2026-09-16: the game draws the two hair quads of section 24 with
`v` 15 where the file holds 14 -- the store at `layout.HAIR_QUAD_STORE` writes
`band * 16 + 15`, and the file does not.  An exact match would call those two
quads absent; a slack of one row finds them, and says it did.

**Since CORR-LOOKS-042 the diagonal compares against what we DRAW**, and the
hair quads are drawn with the store's rows (`assembly.hair_texcoords`), so the
same capture now reads `stored 7` and `stored, one row off 0`.  The slack stays:
a nonzero "one row off" is exactly how a drawn `v` drifting from the game's
would show up again, and it is printed rather than hidden.
"""


def _near(one, two) -> bool:
    return all(a[0] == b[0] and abs(a[1] - b[1]) <= ROW_SLACK
               for a, b in zip(one, two))


def diagonal(stored: list, packets: list) -> dict:
    """How the game orders each of our primitives' texcoords.

    `stored` is [(clut, ((u, v) x 4))] in the file's own order.  Outcomes:

    * `stored` / `untangled` -- a packet with the primitive's CLUT carries its
      four pairs in that order, exactly;
    * `stored, one row off` / `untangled, one row off` -- the same within
      ROW_SLACK on `v`, which is what the game's hair store does;
    * `twin` -- another primitive of the list has the same CLUT and the same
      SET of pairs, so a packet cannot say which of the two it is.  Measured:
      sections mirror halves this way, and counting a twin would count one
      packet twice, possibly in the wrong order;
    * `ambiguous` -- both orders appear, or the two orders are the same;
    * `absent` -- neither order, within the slack.
    """
    by_set: dict = {}
    for clut, uvs in stored:
        key = (clut, frozenset(uvs))
        by_set[key] = by_set.get(key, 0) + 1
    names = ("stored", "untangled", "stored, one row off",
             "untangled, one row off", "twin", "ambiguous", "absent")
    out = {name: 0 for name in names}
    for clut, uvs in stored:
        other = tuple(uvs[i] for i in UNTANGLED)
        if by_set[(clut, frozenset(uvs))] > 1:
            out["twin"] += 1
            continue
        here = [p for c, p in packets if c == clut]
        a, b = uvs in here, other in here
        if uvs == other or (a and b):
            out["ambiguous"] += 1
        elif a:
            out["stored"] += 1
        elif b:
            out["untangled"] += 1
        else:
            near_a = any(_near(uvs, p) for p in here)
            near_b = any(_near(other, p) for p in here)
            if near_a and not near_b:
                out["stored, one row off"] += 1
            elif near_b and not near_a:
                out["untangled, one row off"] += 1
            elif near_a and near_b:
                out["ambiguous"] += 1
            else:
                out["absent"] += 1
    return out


def diagonal_verdict(found: dict) -> str | None:
    """"stored", "untangled", or None when the packets decide nothing."""
    stored = found["stored"] + found["stored, one row off"]
    untangled = found["untangled"] + found["untangled, one row off"]
    if stored and not untangled:
        return "stored"
    if untangled and not stored:
        return "untangled"
    return None


# ---- the gate ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("confront.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    import oracle

    rows = oracle.ROWS
    start = oracle.CURSOR_STARTS_ON

    ok("the reference tuple is the start, so it costs no press",
       plan(START, rows, start) == [(SHOT_ROW, None, 0)],
       "%r" % (plan(START, rows, start),))
    skin = attempt("plan the skin tuple",
                   lambda: plan("B-A1-A-A-A", rows, start), default=[])
    ok("one Right on SKIN, then the shot row", skin == [
        ("SKIN", "Right", 1), (SHOT_ROW, None, 0)], "%r" % (skin,))
    both = attempt("plan a two-row tuple",
                   lambda: plan("A-A1-A-B-E", rows, start), default=[])
    ok("rows come in screen order, and the count is the label's distance",
       [entry[0] for entry in both] == ["FACE", "H.F.COL.", SHOT_ROW]
       and both[0][2] == 1 and both[1][2] == 4, "%r" % (both,))
    ok("the five rows of a tuple are the five the route may press",
       set(rows_of(START)) == {"SKIN", "HAIR", "H.COL", "FACE", "H.F.COL."},
       "%r" % (sorted(rows_of(START)),))
    c.refusing(looks.BadLooks)("a tuple that does not parse refuses",
                               lambda: plan("A-Z9-A-A-A", rows, start),
                               "Z9")
    ok("the cursor moves the shortest way",
       moves(rows, "H.F.COL.", "HAIR") == ("Up", 3)
       and moves(rows, "NAT", "SKIN") == ("Down", 1))
    ok("every tuple of the confrontation parses", all(
        looks.parse_tuple(one) for one in TUPLES))
    ok("the confrontation covers two slots and at least three tuples",
       len(SLOT_FIGURE) == 2 and len(TUPLES) - 1 >= 3)

    # The metric, on synthetic pictures.
    def shot(pixels, width):
        rows_ = [bytes(v for p in pixels[i:i + width] for v in p)
                 for i in range(0, len(pixels), width)]
        return (width, len(rows_), 3, rows_)

    skin_a = (200, 160, 112)
    skin_b = (152, 104, 56)
    hair = (16, 16, 16)
    back = (32, 40, 48)
    game_a = shot([skin_a] * 6 + [hair] * 2, 4)
    ours_a = shot([skin_a] * 5 + [hair] * 2 + [back], 4)
    ours_b = shot([skin_b] * 5 + [hair] * 2 + [back], 4)
    h_game = histogram(game_a)
    h_a = histogram(ours_a, drop=quantise(back))
    h_b = histogram(ours_b, drop=quantise(back))
    ok("the background of our render is not counted",
       quantise(back) not in h_a)
    ok("the same colours in different proportions score high",
       intersection(h_game, h_a) > 0.9, "%.3f" % intersection(h_game, h_a))
    ok("a different skin scores low against the same frame",
       intersection(h_game, h_b) < 0.5, "%.3f" % intersection(h_game, h_b))
    ok("intersection is symmetric and bounded",
       abs(intersection(h_a, h_b) - intersection(h_b, h_a)) < 1e-9
       and 0.0 <= intersection(h_a, h_b) <= 1.0)
    ok("an empty histogram scores zero, not a division by zero",
       intersection({}, h_a) == 0.0)
    ok("a box crops before counting",
       sum(histogram(game_a, box=(0.0, 0.0, 0.5, 0.5)).values()) == 2)

    scores = {("A", "A"): 0.9, ("A", "B"): 0.3, ("B", "B"): 0.8,
              ("B", "A"): 0.79}
    seen = verdict(scores, 2, {("A", "B"): 0.99, ("B", "A"): 0.99})
    ok("a lead of MARGIN or more is a win", seen["A"][0] == "win",
       "%r" % (seen,))
    ok("a lead under MARGIN is ranked, not won",
       seen["B"][0] == "ranked", "%r" % (seen,))
    ok("and the ranked verdict prints the ceiling our renders allow",
       "0.010" in seen["B"][1], "%r" % (seen["B"],))
    lost = verdict({("A", "A"): 0.78, ("A", "B"): 0.79, ("B", "B"): 0.9,
                    ("B", "A"): 0.1}, 2)
    ok("scoring second is a failure", lost["A"][0] == "unexplained",
       "%r" % (lost,))
    tie = verdict({("A", "A"): 0.8, ("A", "B"): 0.8, ("B", "B"): 0.9,
                   ("B", "A"): 0.1}, 2)
    ok("and so is a tie", tie["A"][0] == "unexplained", "%r" % (tie,))
    twin = verdict({("A", "A"): 0.8, ("A", "B"): 0.8, ("B", "B"): 0.8,
                    ("B", "A"): 0.8}, 2, {("A", "B"): 1.0, ("B", "A"): 1.0})
    ok("two identical renders fail unless a residue names them",
       twin["A"][0] == "unexplained" and twin["B"][0] == "unexplained",
       "%r" % (twin,))
    gk = verdict({("A-A1-A-A-A", "A-A1-A-A-A"): 0.75,
                  ("A-A1-A-A-A", "A-I3-A-A-A"): 0.75,
                  ("A-A1-A-A-A", "B-A1-A-A-A"): 0.1,
                  ("A-I3-A-A-A", "A-I3-A-A-A"): 0.74,
                  ("A-I3-A-A-A", "A-A1-A-A-A"): 0.74,
                  ("A-I3-A-A-A", "B-A1-A-A-A"): 0.1,
                  ("B-A1-A-A-A", "B-A1-A-A-A"): 0.7,
                  ("B-A1-A-A-A", "A-A1-A-A-A"): 0.1,
                  ("B-A1-A-A-A", "A-I3-A-A-A"): 0.1},
                 1, {("A-A1-A-A-A", "A-I3-A-A-A"): 1.0,
                     ("A-I3-A-A-A", "A-A1-A-A-A"): 1.0},
                 {(1, "A-I3-A-A-A"): GOALKEEPER_HEAD})
    # A synthetic residue, because the real EXPECTED is empty since
    # CORR-LOOKS-043 -- and a mechanism nothing exercises is not a mechanism.
    ok("a named residue is expected, and its twin is judged without it",
       gk["A-I3-A-A-A"][0] == "expected" and gk["A-A1-A-A-A"][0] == "win",
       "%r" % (gk,))
    ok("the bound the ranked verdict leans on holds: a lead never exceeds how "
       "far apart the two renders are",
       intersection(h_game, h_a) - intersection(h_game, h_b)
       <= 1.0 - intersection(h_a, h_b) + 1e-9)

    # The diagonal, on packets built by hand.
    uvs = ((0, 0), (16, 0), (0, 16), (16, 16))
    other = tuple(uvs[i] for i in UNTANGLED)
    ok("a packet in stored order is read as stored",
       diagonal([(5, uvs)], [(5, uvs)])["stored"] == 1)
    ok("a packet in the untangled order is read as untangled",
       diagonal([(5, uvs)], [(5, other)])["untangled"] == 1)
    ok("a packet with another CLUT does not count",
       diagonal([(5, uvs)], [(6, uvs)])["absent"] == 1)
    ok("a quad that reads the same both ways decides nothing",
       diagonal([(5, ((0, 0),) * 4)], [(5, ((0, 0),) * 4)])["ambiguous"] == 1)
    mirrored = tuple(uvs[i] for i in (2, 3, 0, 1))
    twins = diagonal([(5, uvs), (5, mirrored)], [(5, uvs)])
    ok("two primitives with the same set of pairs are twins, not two votes",
       twins["twin"] == 2 and twins["stored"] == 0, "%r" % (twins,))
    lower = tuple((u, v + 1 if v else v) for u, v in uvs)
    ok("a v one row lower is the same corner, and is said to be",
       diagonal([(5, uvs)], [(5, lower)])["stored, one row off"] == 1)
    ok("two rows off is not",
       diagonal([(5, uvs)], [(5, tuple((u, v + 2) for u, v in uvs))])
       ["absent"] == 1)
    ok("the verdict needs one order and not the other",
       diagonal_verdict(dict(twins, stored=3)) == "stored"
       and diagonal_verdict(dict(twins, stored=3, untangled=1)) is None)

    lavender, yellow, teal = (170, 170, 255), (255, 230, 50), (20, 60, 60)
    plain = shot([teal, lavender, teal, teal], 4)
    blinked = shot([yellow, lavender, teal, teal], 4)
    other = shot([teal, teal, lavender, teal], 4)
    whole = (0.0, 0.0, 1.0, 1.0)
    ok("the glyph mask ignores the yellow cursor box",
       glyph_mask(plain, whole) == glyph_mask(blinked, whole))
    ok("and sees a letter that moved",
       glyph_mask(plain, whole) != glyph_mask(other, whole))

    import struct

    commands = {code: spec for code, spec in oracle.GPU_COMMANDS.items()
                if "textured quad" in spec[0]}
    flat = next(code for code, spec in commands.items() if spec[1] == 9)
    body = bytearray(4 * 10)
    struct.pack_into("<I", body, 0, (9 << 24) | 64)
    body[7] = flat
    for corner, word in enumerate(QUAD_UV_WORDS[9]):
        at = 4 + 4 * word
        body[at], body[at + 1] = uvs[corner]
        struct.pack_into("<H", body, at + 2, 5)
    found = attempt("parse a synthetic packet",
                    lambda: packet_texcoords(bytes(body) + bytes(8),
                                             oracle.GPU_COMMANDS), default=[])
    ok("the packet reader finds the quad, its CLUT and its four pairs",
       (5, uvs) in found, "%r" % (found,))


# ---- the live run --------------------------------------------------------

def _python_and_app():
    import ui_check

    python = ui_check.venv_python()
    if python is None:
        raise ConfrontError("no venv python under work/venv-looks")
    return python, ui_check.APP


def render(text: str, figure: int, out: str):
    """(picture, None) or (None, the refusal) for one tuple on our side."""
    import ui_check

    python, app = _python_and_app()
    code, output = ui_check.run_app(
        python, app, ["--looks", text, "--figure", str(figure), "--piece",
                      PIECE, "--size", "%dx%d" % RENDER_SIZE,
                      "--screenshot", out], ui_check.environment())
    if code == 2:
        return (None, output.strip().splitlines()[-1])
    if code or not os.path.isfile(out):
        raise ConfrontError("the viewer failed on %s (exit %s): %s"
                            % (text, code, output.strip()[-400:]))
    return (ui_check.picture(out), None)


def route(game, text: str, oracle) -> int:
    """Put one tuple on the game's screen.  Returns frames since load_state."""
    frames = oracle.LOAD_FRAMES
    press = oracle.CONFIRM_FRAMES + oracle.SETTLE_FRAMES
    here = oracle.CURSOR_STARTS_ON
    for row, button, count in plan(text, oracle.ROWS, here):
        way, distance = moves(oracle.ROWS, here, row)
        for _ in range(distance):
            game.press(way, box=oracle.FOOTER, least=oracle.ROW_MOVED)
            frames += press
        here = row
        cell = oracle.row_value(oracle.ROWS.index(row))
        for _ in range(count):
            game.press(button, box=cell, least=oracle.VALUE_MOVED)
            frames += press
    game.step(SHOT_FRAMES)
    return frames + SHOT_FRAMES


OUT_DIR = os.path.join("work", "looks-confront")
"""Where every capture, render and band of a run is kept -- and read back from
by `--score`, which re-judges a run without the emulator."""

BANDS = ("band-a.bin", "band-b.bin")


def out_dir() -> str:
    import oracle

    return os.path.join(oracle.ROOT, OUT_DIR)


def run(slots=(2, 1), verbose=True) -> int:
    import iso_source
    import oracle

    ready = oracle.preflight()
    _python_and_app()
    where = out_dir()
    os.makedirs(where, exist_ok=True)

    for slot in slots:
        for text in TUPLES:
            path = os.path.join(where, "ours-%d-%s.png" % (slot, text))
            if os.path.exists(path):
                os.remove(path)
            picture, why = render(text, SLOT_FIGURE[slot], path)
            if picture is None:
                with open(path + ".refused", "w", encoding="utf-8") as handle:
                    handle.write(why + "\n")

    failures = 0
    with oracle.Oracle(ready["cue"], out_dir=where, verbose=verbose) as game:
        for slot in sorted(oracle.SLOTS):
            oracle.restore_state(slot, verbose=verbose)
        for slot in slots:
            for text in TUPLES:
                game.load_looks(slot)
                count = route(game, text, oracle)
                game.capture("game-%d-%s" % (slot, text))
                print("  slot %d %s: captured on frame %d after load_state"
                      % (slot, text, count))
            # Repeatability, measured and not assumed: the reference route
            # again, from a fresh load, must give the same panel to the pixel.
            game.load_looks(slot)
            route(game, TUPLES[0], oracle)
            game.capture("game-%d-repeat" % slot)
            if slot == 2:
                # The bands are read on the reference frame, the tuple the
                # file's own texcoords describe with no band and no edit.
                game.load_looks(slot)
                route(game, START, oracle)
                for base, name in zip(oracle.BUFFER_BANDS, BANDS):
                    game.read_ram(base, oracle.BUFFER_SIZE,
                                  os.path.join(where, name))
    failures += score(slots, ready["image"])
    return 1 if failures else 0


def score(slots=(2, 1), image=None) -> int:
    """Judge the captures a run left behind.  No emulator."""
    import iso_source
    import layout
    import oracle
    import section

    import ui_check

    where = out_dir()
    failures = 0
    for slot in slots:
        games, ours, refused = {}, {}, {}
        for text in TUPLES:
            games[text] = ui_check.picture(
                os.path.join(where, "game-%d-%s.png" % (slot, text)))
            path = os.path.join(where, "ours-%d-%s.png" % (slot, text))
            if os.path.exists(path + ".refused"):
                with open(path + ".refused", encoding="utf-8") as handle:
                    refused[text] = handle.read().strip()
            else:
                ours[text] = ui_check.picture(path)
        again = ui_check.picture(os.path.join(where, "game-%d-repeat.png"
                                              % slot))
        same = histogram(again, box=PANEL) == histogram(games[TUPLES[0]],
                                                        box=PANEL)
        diff = ui_check.differing(again, games[TUPLES[0]])
        print("  slot %d: the reference route repeated differs in %d pixel(s) "
              "of the whole frame -- %s" % (slot, diff,
                                            "repeatable" if not diff
                                            else "NOT repeatable"))
        if diff or not same:
            failures += 1
        for text, why in sorted(refused.items()):
            print("  slot %d %s: our side refuses -- %s" % (slot, text, why))
        failures += _score(slot, games, ours)

    if 2 in slots:
        image = image or iso_source.image_from_env()
        packets = []
        for name in BANDS:
            with open(os.path.join(where, name), "rb") as handle:
                packets += packet_texcoords(handle.read(),
                                            oracle.GPU_COMMANDS)
        with iso_source.open_disc(image) as disc:
            data = disc.read(layout.MODEL)
        head = section.scan(data, layout.GEOMETRY_START[layout.MODEL]) \
            .sections[layout.HEAD_SECTION]
        import assembly

        # What we DRAW for the reference tuple, which is band 0: the hair
        # quads carry the rows the game's store writes, not the file's.
        quads = layout.HAIR_QUADS.get(layout.HEAD_SECTION, ())
        stored = [(one.clut,
                   assembly.hair_texcoords(one.texcoords, 0) if at in quads
                   else tuple(one.texcoords))
                  for at, one in enumerate(head.primitives)]
        found = diagonal(stored, packets)
        answer = diagonal_verdict(found)
        print("  the diagonal: %d textured quad packet(s) in the two bands, "
              "and the head's %d primitive(s):" % (len(packets), len(stored)))
        for name, count in found.items():
            print("      %-24s %d" % (name, count))
        print("      verdict: %s" % ("the game draws the %s order"
                                     % answer.upper() if answer
                                     else "NONE -- the packets decide nothing"))
        if answer is None:
            failures += 1
    print("confront: %s" % ("ok" if not failures else
                            "%d failure(s)" % failures))
    return failures


def _score(slot, games, ours) -> int:
    backs = {text: quantise(pic[3][0][0:3]) for text, pic in ours.items()}
    hists = {text: histogram(pic, drop=backs[text])
             for text, pic in ours.items()}
    palette = set()
    for one in hists.values():
        palette |= set(one)
    alike = {(a, b): (1.0 if hists[a] == hists[b]
                      else intersection(hists[a], hists[b]))
             for a in hists for b in hists if a != b}
    scores = {}
    columns = sorted(hists)
    print("  slot %d, figure %d: histogram intersection over the %d colour(s) "
          "our side draws -- rows the game, columns ours"
          % (slot, SLOT_FIGURE[slot], len(palette)))
    print("      %-12s %s" % ("", " ".join("%-11s" % t for t in columns)))
    for text in TUPLES:
        panel = restrict(histogram(games[text], box=PANEL), palette)
        line = []
        for other in columns:
            scores[(text, other)] = intersection(panel, hists[other])
            line.append("%-11.3f" % scores[(text, other)])
        print("      %-12s %s%s" % (text, " ".join(line),
                                    "" if text in hists else "  (refused)"))
    print("      our own renders, pairwise: %s" % ", ".join(
        "%s~%s %.3f" % (a, b, v) for (a, b), v in sorted(alike.items())
        if a < b))
    judged = verdict(scores, slot, alike)
    bad = 0
    for text in TUPLES:
        if text not in judged:
            continue
        outcome, why = judged[text]
        print("      %-12s %-11s %s" % (text, outcome.upper(), why))
        bad += outcome == "unexplained"
    print("  slot %d: %s" % (slot, ", ".join(
        "%d %s" % (sum(1 for o, _w in judged.values() if o == kind), kind)
        for kind in ("win", "ranked", "expected", "unexplained"))))
    return bad


GLYPH_LEFT = 0.770
"""Where a value cell's glyphs start, as a fraction of the frame.

Right of the left end-of-range arrow, which sits at 0.756 and appears and
disappears as the value leaves and reaches the bottom of its range -- inside
`oracle.row_value`'s box, which is why that box cannot count values."""

GLYPH_BLUE = 192
"""A glyph pixel: the lavender of the value text, blue at least this, and more
blue than red.  The cursor box that blinks over the cell is yellow and the row
is dark teal, so neither passes, and the blink leaves the mask alone."""


def glyph_mask(shot, box) -> frozenset:
    """The set of glyph pixels inside a box -- what the LABEL is, blink-free.

    Measured on 2026-09-16, and the reason this exists: the raw difference of
    the value cell counted eight values on a row that shows seven, because the
    cursor box pulses between two brightnesses and one pulse outweighed the
    idle floor.  The letters do not pulse.
    """
    width, height, channels, rows = shot
    x0, y0 = int(box[0] * width), int(box[1] * height)
    x1, y1 = int(box[2] * width), int(box[3] * height)
    out = set()
    for y in range(y0, y1):
        row = rows[y]
        for x in range(x0, x1):
            r, _g, b = row[x * channels:x * channels + 3]
            if b >= GLYPH_BLUE and b > r:
                out.add((x - x0, y - y0))
    return frozenset(out)


def reach(row: str, slots=(2, 1), verbose=True) -> int:
    """How many values a row walks on each slot, read off its label.

    Right until the glyphs stop changing.  **The control comes first:** two
    pictures with no press between them, the same number of frames apart as a
    press takes, must give the same mask -- otherwise the mask is reading the
    blink and the count below means nothing.  And every press leaves a picture
    named by its count, because the label is the witness.
    """
    import oracle
    import ui_check

    ready = oracle.preflight()
    field = looks.BY_ROW[row]
    tag = row.replace(".", "")
    failures = 0
    with oracle.Oracle(ready["cue"], verbose=verbose) as game:
        for slot in sorted(oracle.SLOTS):
            oracle.restore_state(slot, verbose=verbose)
        for slot in slots:
            game.load_looks(slot)
            game.select_row(row)
            cell = oracle.row_value(oracle.ROWS.index(row))
            box = (GLYPH_LEFT, cell[1], cell[2], cell[3])

            def mask(label):
                game.capture(label)
                return glyph_mask(ui_check.picture(
                    os.path.join(game.out_dir, "%s.png" % label)), box)

            idle = mask("reach-%d-%s-idle-a" % (slot, tag))
            game.step(oracle.CONFIRM_FRAMES + oracle.SETTLE_FRAMES)
            if mask("reach-%d-%s-idle-b" % (slot, tag)) != idle:
                print("  %s on slot %d: the label's mask moved with nothing "
                      "pressed, so it cannot count values" % (row, slot))
                failures += 1
                continue
            if not idle:
                print("  %s on slot %d: no glyph in the cell box" % (row, slot))
                failures += 1
                continue
            previous, moved = idle, 0
            for press in range(1, field.values + 1):
                game.press("Right", expect_change=False)
                current = mask("reach-%d-%s-%d" % (slot, tag, press))
                if current == previous:
                    break
                moved += 1
                previous = current
            print("  %s on slot %d: %d glyph pixel(s) at rest, still with "
                  "nothing pressed; %d Right(s) changed the label, so the "
                  "screen reaches %d of the %d value(s) the field holds"
                  % (row, slot, len(idle), moved, moved + 1, field.values))
    return 1 if failures else 0


def main(argv: list[str]) -> int:
    if len(argv) == 2 and argv[1] == "--check":
        return 1 if self_check() else 0
    try:
        import oracle

        if len(argv) >= 2 and argv[1] in ("--run", "--score"):
            slots = tuple(int(a) for a in argv[2:]) or (2, 1)
            if argv[1] == "--score":
                return 1 if score(slots) else 0
            return run(slots)
        if len(argv) == 3 and argv[1] == "--reach":
            return reach(argv[2])
    except oracle.Unavailable as exc:
        print("confront: skipped -- %s" % exc)
        return SKIP
    except (ConfrontError, oracle.OracleError) as exc:
        print("confront FAILED: %s" % exc, file=sys.stderr)
        return 1
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

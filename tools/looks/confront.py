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
    python tools/looks/confront.py --render         # our side again, no game
    python tools/looks/confront.py --score          # re-judge the last run
    python tools/looks/confront.py --reach FACE     # how far a row walks
    python tools/looks/confront.py --silhouette [SLOT]          # the pose, by shape
    python tools/looks/confront.py --silhouette-styles [SLOT]   # hair, in the close-up
    python tools/looks/confront.py --silhouette-stature [SLOT]  # HEIG and BODY, by shape
    python tools/looks/confront.py --kit-control    # another team's uniform scores worse
    python tools/looks/confront.py --outside [SLOT]  # our screen against the game's, outside the figure
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
"""Kept as the record of the residue it named.  CORR-LOOKS-043 made figure 1
REFUSE those styles, and CORR-LOOKS-047 measured the goalkeeper's map, so
figure 1 draws them again -- with the head its own walk names, and refusing
only H1, the way slot 2 does.  EXPECTED has nothing left to excuse."""

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
    ceiling beside it, and does not fail -- **but only where the ceiling is what
    made MARGIN unreachable**: a ceiling under `2 * MARGIN`, so that MARGIN asks
    for more than half of the most any lead can be.  Under a wide ceiling a lead
    below MARGIN is a coin toss the bound does not excuse, and it fails as
    unexplained.  The rule used to be `right > wrong`, which accepted a lead of
    0.001 under a ceiling of 0.5 and printed the 0.5 beside it
    (CORR-LOOKS-045).  Ranking second fails either way.

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
        ceiling = 1.0 - alike.get((game, best), 0.0)
        if right - wrong >= MARGIN:
            out[game] = ("win", "by %.3f over %s" % (right - wrong, best))
        elif right > wrong and ceiling < 2 * MARGIN:
            out[game] = ("ranked", "first by %.3f over %s, whose render ours "
                                   "is %.3f apart from -- the most any lead "
                                   "can be" % (right - wrong, best, ceiling))
        elif right > wrong:
            out[game] = ("unexplained",
                         "first by only %.3f over %s, and our two renders are "
                         "%.3f apart, so the bound does not explain the margin "
                         "being missed" % (right - wrong, best, ceiling))
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

    # -- the close-up verdict, on the numbers of 2026-09-18 --------------
    #
    # Slot 2's A1 photograph is the tightest the gate has met: our I3 scores
    # 274 against the right 202, 1.36x.  CORR-LOOKS-063 is about the verdict
    # that stayed green on a bare minimum, so the red cases are the ones a
    # minimum lets through.
    right = {"A-A1-A-A-A": 202, "A-C1-A-A-A": 357, "A-I3-A-A-A": 274}
    ink = 2379  # not-an-address: the game's head-band pixels, that photograph
    ratio, share, wrong = closeup_verdict(2, "A-A1-A-A-A", right, ink)
    ok("the close-up of 2026-09-18 passes, at the ratio it printed",
       wrong == [] and round(ratio, 2) == 1.36, "%r %r" % (ratio, wrong))
    hair = dict(right, **{"A-I3-A-A-A": 210})
    ok("a right style that wins by a hair is refused, though it is the minimum",
       closeup_verdict(2, "A-A1-A-A-A", hair, ink)[2])
    swapped = dict(right, **{"A-I3-A-A-A": 150})
    ok("a swapped style is refused, and the message names it",
       "I3" in "".join(closeup_verdict(2, "A-A1-A-A-A", swapped, ink)[2]))
    far = {"A-A1-A-A-A": ink // 3, "A-C1-A-A-A": ink, "A-I3-A-A-A": ink}
    ok("a right style far from the game's head is refused, though it wins",
       closeup_verdict(2, "A-A1-A-A-A", far, ink)[2])

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
    # Under a NARROW ceiling, which is the only place a thin lead ranks --
    # without it the tie would fail for the ceiling's sake and a control that
    # lets ties rank would stay green (CORR-LOOKS-045 moved the branch).
    tie = verdict({("A", "A"): 0.8, ("A", "B"): 0.8, ("B", "B"): 0.9,
                   ("B", "A"): 0.1}, 2, {("A", "B"): 0.99, ("B", "A"): 0.99})
    ok("and so is a tie, even under a ceiling narrow enough to rank",
       tie["A"][0] == "unexplained", "%r" % (tie,))
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
    # A thin lead under a WIDE ceiling is a coin toss, and the bound does not
    # excuse it (CORR-LOOKS-045).  The two real `ranked` of LOOKS-TASK-17 sit
    # under a ceiling of 0.039 and must keep passing.
    wide = verdict({("X", "X"): 0.500, ("X", "Y"): 0.499,
                    ("Y", "Y"): 0.900, ("Y", "X"): 0.100},
                   2, {("X", "Y"): 0.5, ("Y", "X"): 0.5})
    ok("a lead of 0.001 under a ceiling of 0.5 is unexplained, not ranked",
       wide["X"][0] == "unexplained", "%r" % (wide,))
    narrow = verdict({("A", "A"): 0.770, ("A", "B"): 0.754,
                      ("B", "B"): 0.760, ("B", "A"): 0.750},
                     2, {("A", "B"): 0.961, ("B", "A"): 0.961})
    ok("and the real pair, 0.016 and 0.010 under a ceiling of 0.039, ranks",
       narrow["A"][0] == "ranked" and narrow["B"][0] == "ranked",
       "%r" % (narrow,))

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

    # Our side of a run, on a scratch directory and a fake viewer: a tuple
    # that refused last time and draws now (CORR-LOOKS-046).
    import tempfile

    with tempfile.TemporaryDirectory() as where:
        def draws(text, figure, out):
            with open(out, "wb") as handle:
                handle.write(b"png")
            return ("picture", None)

        def refuses(text, figure, out):
            return (None, "no")

        path = ours_path(where, 2, TUPLES[0])
        with open(path + REFUSED, "w", encoding="utf-8") as handle:
            handle.write("an old refusal\n")
        render_ours((2,), where, draws, verbose=False)
        ok("a re-render that draws removes the old refusal",
           not os.path.exists(path + REFUSED) and os.path.exists(path))
        ok("and the tuple is then read as drawn",
           attempt("read our side", lambda: ours_side(where, 2, TUPLES[0]),
                   default=(None,))[0] == "drawn")
        render_ours((2,), where, refuses, verbose=False)
        ok("a re-render that refuses removes the old picture",
           not os.path.exists(path) and os.path.exists(path + REFUSED))
        with open(path, "wb") as handle:
            handle.write(b"png")
        c.refusing(ConfrontError)(
            "a picture beside a refusal is a failure naming the tuple, not a "
            "refusal", lambda: ours_side(where, 2, TUPLES[0]), TUPLES[0])
        os.remove(path)
        os.remove(path + REFUSED)
        c.refusing(ConfrontError)(
            "a tuple with neither file is a failure",
            lambda: ours_side(where, 2, TUPLES[0]), TUPLES[0])


# ---- the live run --------------------------------------------------------

def _python_and_app():
    import ui_check

    python = ui_check.venv_python()
    if python is None:
        raise ConfrontError("no venv python under work/venv-looks")
    return python, ui_check.APP


def render(text: str, figure: int, out: str, kit: str = None,
           piece: str = None):
    """(picture, None) or (None, the refusal) for one tuple on our side.

    *kit* names another team's container, which is how the kit control draws
    the same tuple in the wrong strip, and *piece* overrides the head-only
    default the colour run is made of -- a uniform is not on the head.
    """
    import ui_check

    python, app = _python_and_app()
    code, output = ui_check.run_app(
        python, app, ["--looks", text, "--figure", str(figure), "--piece",
                      piece or PIECE, "--size", "%dx%d" % RENDER_SIZE,
                      "--screenshot", out]
        + ([] if kit is None else ["--kit", kit]), ui_check.environment())
    if code == 2:
        return (None, output.strip().splitlines()[-1])
    if code or not os.path.isfile(out):
        raise ConfrontError("the viewer failed on %s (exit %s): %s"
                            % (text, code, output.strip()[-400:]))
    return (ui_check.picture(out), None)


WRONG_KITS = ("00", "50")
"""Two other teams' containers, for the control below.

Two and not one: a single wrong kit that happened to be close would make the
control a coin toss, and the pair are far apart on the disc -- one from each
end of the 105.
"""

KIT_CONTROL_MARGIN = 0.05
"""How much better the kit the screen wears must score than another team's.

In histogram intersection, where 1.0 is the same colour distribution.
Measured 2026-09-20 over both slots and both wrong kits: **0.218, 0.218,
0.148 and 0.063**, and the floor is written under the smallest of the four
rather than over the average of them.
"""


def check_kit_control(slots=(2, 1), verbose=True) -> int:
    """`--kit-control`: another team's uniform has to score worse.  No emulator.

    The kit is chosen by measurement (`oracle.py --kit`, off VRAM), and this is
    the other half of that claim: the choice has to MATTER to the picture.  Our
    reference tuple is drawn again in two other teams' strips and scored
    against the game's own capture of that tuple, by the same histogram
    intersection `--score` judges with -- so a run that dressed the figure in
    any container at all and called it the uniform comes back red here.
    """
    import ui_check

    where = out_dir()
    _python_and_app()
    problems = []
    for slot in slots:
        figure = SLOT_FIGURE[slot]
        game = os.path.join(where, "game-%d-%s.png" % (slot, START))
        if not os.path.isfile(game):
            print("  no capture at %s -- run --run first" % game)
            return SKIP
        panel = histogram(ui_check.picture(game), box=PANEL)
        # The WHOLE figure, not the head the colour run renders (`PIECE`): a
        # uniform is not on the head, and scored head-only the three kits come
        # back to the third decimal identical -- measured, which is how this
        # control was written wrong the first time.
        mine = os.path.join(where, "ours-%d-%s-whole.png" % (slot, START))
        picture, refusal = render(START, figure, mine, None, "all")
        if picture is None:
            problems.append("slot %d: our side refuses %s -- %s"
                            % (slot, START, refusal))
            continue
        back = quantise(picture[3][0][0:3])
        hist = histogram(picture, drop=back)
        right = intersection(restrict(panel, set(hist)), hist)
        print("  slot %d, %s whole, in the measured kit TEX_%s: %.3f"
              % (slot, START, layout_kit(), right))
        for tag in WRONG_KITS:
            out = os.path.join(where, "ours-%d-%s-kit%s.png" % (slot, START,
                                                                tag))
            picture, refusal = render(START, figure, out, tag, "all")
            if picture is None:
                problems.append("slot %d: the viewer refused TEX_%s -- %s"
                                % (slot, tag, refusal))
                continue
            wrong_back = quantise(picture[3][0][0:3])
            wrong_hist = histogram(picture, drop=wrong_back)
            wrong = intersection(restrict(panel, set(wrong_hist)), wrong_hist)
            print("      in TEX_%s: %.3f (%.3f worse)"
                  % (tag, wrong, right - wrong))
            if right - wrong < KIT_CONTROL_MARGIN:
                problems.append(
                    "slot %d: TEX_%s scores %.3f against the measured kit's "
                    "%.3f -- under the %.2f that says the kit decides the "
                    "picture" % (slot, tag, wrong, right, KIT_CONTROL_MARGIN))
    for line in problems:
        print("  FAIL  %s" % line)
    print("confront --kit-control: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def layout_kit() -> str:
    """The tag the window draws with, read from `layout` (rule 3 keeps the
    import inside the function, like every other one in this file)."""
    import layout

    return layout.KIT_ON_SCREEN


def press_value(game, button: str, row: str, oracle) -> None:
    """One press on a row's value, proved by the label's glyphs.

    Not by the raw difference of the value cell, which is trap 28 of the
    profile: E to F on FACE moves that cell by 0.0029, under the 0.004 that
    counts as unchanged -- F is E without its bottom bar -- and the route died
    on a press that had registered (CORR-LOOKS-049).  The glyph mask does not
    read the blink, and any letter that changes changes it.
    """
    import ui_check

    cell = oracle.row_value(oracle.ROWS.index(row))
    box = (GLYPH_LEFT, cell[1], cell[2], cell[3])

    def mask(frame_path):
        return glyph_mask(ui_check.picture(frame_path), box)

    game.capture()
    scratch = os.path.join(game.out_dir, "scratch.png")
    before = mask(scratch)
    game.press(button, expect_change=False)
    game.capture()
    if mask(scratch) == before:
        raise ConfrontError("%s on %s did not change the label -- the press "
                            "did not register" % (button, row))


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
        for _ in range(count):
            press_value(game, button, row, oracle)
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


REFUSED = ".refused"
"""The suffix of the file our side leaves instead of a PNG when it refuses."""


def ours_path(where: str, slot: int, text: str) -> str:
    return os.path.join(where, "ours-%d-%s.png" % (slot, text))


def ours_side(where: str, slot: int, text: str) -> tuple:
    """('drawn', the PNG) or ('refused', the reason) for one tuple of a run.

    **Both files present is a failure, not a refusal.**  It is an old run mixed
    with a new one, and reading the refusal first took out of the matrix the
    very tuple a measurement had just made draw -- the gate then printed `ok`
    over a tuple it never judged (CORR-LOOKS-046).
    """
    path = ours_path(where, slot, text)
    drawn = os.path.exists(path)
    refused = os.path.exists(path + REFUSED)
    if drawn and refused:
        raise ConfrontError(
            "slot %d %s has both a render and a refusal -- an old run mixed "
            "with a new one; re-render our side with --render" % (slot, text))
    if refused:
        with open(path + REFUSED, encoding="utf-8") as handle:
            return ("refused", handle.read().strip())
    if not drawn:
        raise ConfrontError("slot %d %s has neither a render nor a refusal "
                            "under %s" % (slot, text, where))
    return ("drawn", path)


def render_ours(slots=(2, 1), where=None, renderer=None, verbose=True) -> None:
    """Our side of every tuple, into the run's directory.  No emulator.

    What was there before goes first, BOTH files: a tuple that refused last
    time and draws now must not keep its old refusal beside the new picture.
    This is what `--render` runs, so a measurement that turns a refusal into a
    drawing is re-judged by `--render` and `--score` with no game at all.
    """
    where = where or out_dir()
    renderer = renderer or render
    os.makedirs(where, exist_ok=True)
    for slot in slots:
        for text in TUPLES:
            path = ours_path(where, slot, text)
            for stale in (path, path + REFUSED):
                if os.path.exists(stale):
                    os.remove(stale)
            picture, why = renderer(text, SLOT_FIGURE[slot], path)
            if picture is None:
                with open(path + REFUSED, "w", encoding="utf-8") as handle:
                    handle.write(why + "\n")
            if verbose:
                print("  slot %d %s: %s" % (slot, text, "drawn" if picture
                                             is not None else "refused"))


def run(slots=(2, 1), verbose=True) -> int:
    import iso_source
    import oracle

    ready = oracle.preflight()
    _python_and_app()
    where = out_dir()
    render_ours(slots, where)

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
            kind, what = ours_side(where, slot, text)
            if kind == "refused":
                refused[text] = what
            else:
                ours[text] = ui_check.picture(what)
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


# ---- the silhouette, which is the witness colour could not be --------------

PANEL_INSET = 3
"""Pixels of the panel's own border left out of every mask.

The panel is drawn with a light edge, and the row-by-row background rule below
reads that edge as figure -- measured: with the border in, the figure's box is
the whole 146x120 panel.  Three is the border, not a margin chosen to make a
number come out.
"""

PANEL_APART = 24
"""How far a pixel must sit from its row's background to count as figure.

Sum of the three channels' distance.  The panel's background is a GRADIENT --
339 distinct colours in one panel -- so the background is taken per ROW, where
it is nearly flat, and not as one colour for the whole box.
"""

SILHOUETTE_FRAMES = (60, 80, 100)
"""Counted frames a silhouette is taken at, and they are not any three.

**They start at 60 because the screen is still settling before it.**  Measured
2026-09-18: at counted frame 20 the panel carries 2726 pixels of ink against
the 2383 to 2532 of every later frame, and NO frame of the walk matches it
better than 3570 -- worse than the ink itself.  From 60 on every capture has a
sharp minimum at 198 to 399.

And 120 is deliberately not among them: it photographs the same phase of the
walk as 60, to the pixel (the control measures 0 between them), so it would
make the "a different frame differs" control pass on two others and fail on it.
"""

WALK_LAG = 2
"""How many frames of the walk the PICTURE may trail the draw in progress.

The dump is taken with the CPU stopped inside the draw of one frame, so what
is on screen is the frame finished before it.  That is one EMULATOR frame, and
a frame of the walk lasts about three and a half of them -- 17 frames over the
60 the cycle takes -- so the same one-frame lag lands 0, 1 or 2 frames back
depending on where in the walk it falls.  Measured: 0, 2, 1 and 0 over the four
captures of 2026-09-18.

It is a bound and not a constant, and saying so is the point: an offset that
had to be one number came out as four different ones and looked like no bridge
at all, when what it is is a lag with a known ceiling.
"""

MATCH_SHARE = 0.25
"""The most of the game's own ink the best match may differ by.

Measured over the four captures: 399 of 2383, 300 of 2454, 198 of 2532 and 399
of 2383 -- 8% to 17%.  The ceiling is written with room above the worst, and
what it has to catch is a figure of the wrong SHAPE, which the controls price
at 603 to 1483 pixels for a wrong frame of the same walk.
"""

STYLE_SWAP = ("A1", "I3")
"""The two hair styles a comparison is re-run between, and why it is printed
and NOT asserted on the full figure.

**This docstring claimed the opposite until LOOKS-TASK-28's fourth session,
and the claim was an artifact.**  The numbers below -- 656 and 783 pixels
between styles -- were measured while `pose()` posed only the reference head:
C1's and I3's heads sat at the file's origin, off the neck, and the "control"
was scoring a floating head.  With every head posed (`scene.place_for`), at
the full figure's size our A1 and I3 differ by a few tens of pixels, the
game's own A1 and I3 photographs by 15 and C1 by 29, and our I3 matches the
game's A1 picture at 378 against our A1's 399.  The full-body silhouette does
not separate hair styles, and asserting that it did is what this used to do.
It is still run and printed; what asserts hair styles is `--silhouette-styles`,
and it does so in the CLOSE-UP, where it passes 6 of 6 (`STYLE_TUPLES`).
Until CORR-LOOKS-064 this line had the styles gate asserting it and
failing: true of the full-figure version, which is gone.
The rest of what this said, measured before the fix, follows as it was:

Hair, because it is the field that changes the MESH: measured 2026-09-18 on
the panel's own size, `A-I3` differs from `A-A1` in 656 of 2686 silhouette
pixels and `A-C1` in 783, while `B-A1` -- a skin colour, which is a palette and
no geometry at all -- differs in **0**.  That zero is the reason the control is
a style and not a colour: a witness of FORM has to be blind to colour, and
this one is, measurably.
"""


def swapped_style(text: str) -> str:
    """The same tuple wearing the OTHER of `STYLE_SWAP`."""
    parts = text.split("-")
    parts[1] = (STYLE_SWAP[1] if parts[1] == STYLE_SWAP[0]
                else STYLE_SWAP[0])
    return "-".join(parts)

STYLE_MARGIN = 1.5
"""How much worse the wrong style must score than the right one."""

MATCH_MARGIN = 2.5
"""How much better the best candidate must be than the worst of the sweep.

Measured: 4.0x, 4.4x and 8.3x.  A sweep with no minimum -- every frame equally
far -- is the shape of a comparison that is not comparing figures at all, and
it is what the capture at counted frame 20 did.
"""

NEIGHBOURS = 8
"""How far either side of the named frame the match is looked for.

The point is not to find the best fit: it is to ask whether the frame the
game's own pair NAMES is the one whose silhouette matches, and a sweep that
only looked at that frame could not tell a match from the only thing offered.

**Eight, so the sweep covers the whole walk** -- the screen's animation is 17
frames, and a sweep of two came back with its best AT THE EDGE in both
directions on the first run, which says nothing about where the minimum is.
A window that the answer leans against is not a window.
"""


def panel_mask(frame, box, inset: int = PANEL_INSET,
               apart: int = PANEL_APART) -> bytearray:
    """The figure's mask out of one native frame, one byte per pixel.

    *frame* is a list of rows of (r, g, b), native 512x240, and *box* the
    panel's own rectangle out of `screen.json` -- never a rectangle written
    here, because the screen measured it.
    """
    left, top, right, bottom = box
    width, height = right - left + 1, bottom - top + 1
    mask = bytearray(width * height)
    for y in range(top + inset, bottom + 1 - inset):
        line = [tuple(frame[y][x])[:3] for x in range(left, right + 1)]
        counts: dict = {}
        for pixel in line:
            counts[pixel] = counts.get(pixel, 0) + 1
        background = max(counts, key=counts.get)
        for x in range(inset, width - inset):
            if sum(abs(a - b) for a, b in zip(line[x], background)) > apart:
                mask[(y - top) * width + x] = 1
    return mask


BUFFERS = (0, 240)
"""VRAM rows the two frame buffers of this screen start at.

The game draws into one and shows the other, so which one a dump holds
alternates; it is decided per dump by the boxes the screen's own border rule
finds, never assumed to be the top one -- which is the reading that made one
dump in four come back with no box at all.

**240 and not 256, and the difference is sixteen rows of somebody else's
picture.**  With 256 the second buffer's content arrives shifted up by
sixteen, which puts the help box's `Visual` inside the panel's own rectangle:
the mask then carries the white of the text as if it were the figure, 2618
pixels of ink against 2376, and no frame of the walk matches it.  The screen is
240 lines tall -- `screen.json` says so -- and the second buffer starts where
the first one ends.
"""


def still_frame(game, display, oracle, screen):
    """The finished frame buffer, dumped with the CPU STOPPED.

    Nothing is stepped here, and that is the whole point: `screen_frames`
    steps a frame per sample, so the walk moves between reading which pair the
    game is on and photographing it -- which is exactly what left LOOKS-TASK-28
    with two different offsets and no bridge.
    """
    import atlas

    width, height = display
    path = os.path.join(game.out_dir, "still.png")
    if os.path.exists(path):
        os.remove(path)
    game.client.call("dump_vram", path=path, format="png")
    if not os.path.exists(path):
        raise ConfrontError("dump_vram reported %s and there is no file there"
                            % path)
    _width, _height, rows = atlas.read_png(path)
    best, found = None, -1
    for origin in BUFFERS:
        frame = [row[:width] for row in rows[origin:origin + height]]
        if len(frame) < height:
            continue
        count = len(screen.boxes(frame, width, height))
        if count > found:
            best, found = frame, count
    if best is None or not found:
        raise ConfrontError("neither buffer at VRAM rows %s holds a box, so "
                            "neither is a finished picture of this screen"
                            % (BUFFERS,))
    return best


def game_at(game, slot, counted, oracle, anime, data, entry, table,
            steps=()):
    """(the ANIME frame being drawn, the panel's mask) at counted *counted*.

    *steps* walks rows first -- `((row, text), ...)`, as `oracle.py
    --stature` walks them -- and *counted* is then counted from the last press.

    **One run, and no frame stepped between the two halves.**  The pair says
    which frame of the file the game is drawing; the dump, taken at that same
    stop, holds the frame it finished just before.  Read in two runs -- which
    is how this started -- the walk advances in between by however many frames
    the photograph costs, and the offset between the two answers stops being
    the same number twice.
    """
    import layout
    import who_writes

    oracle.restore_state(slot, verbose=False)
    game.load_looks(slot, label="silhouette-%d-%d" % (slot, counted))
    if steps:
        oracle._stature_walk(game, slot, steps, table)
    game.step(counted)
    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.ANIME_UNPACK))
    try:
        client.call("continue")
        if not oracle._wait_for_hit(game, oracle.WATCH_SECONDS):
            raise ConfrontError("the unpack at %s never ran at frame %d"
                                % (who_writes.hx(layout.ANIME_UNPACK),
                                   counted))
        registers = client.call("read_registers", group="gpr")
        pair = (who_writes.register_value(registers,
                                          layout.ANIME_UNPACK_BASE)
                - layout.ANIME_BASE)
    finally:
        try:
            client.call("breakpoint", action="clear")
        except Exception:  # noqa: BLE001
            pass
    import screen as screen_module

    # One frame, and it is what makes the picture a FINISHED one: stopped
    # inside the draw, the buffer the dump would catch is the one being
    # written, which holds part of this figure over part of the last -- more
    # ink than either and matching neither.  Measured: two of six captures came
    # back that way, at 2618 and 2726 pixels of ink against the 2376 to 2532 of
    # the good ones, with a flat sweep.  Letting the frame finish costs about a
    # third of a frame of the walk, which is inside `WALK_LAG`.
    game.step(1)
    frame = still_frame(game, table["display"], oracle, screen_module)
    box = table["regions"]["panel"]["native"]
    return (anime.frame_of_pair(data, entry, pair), panel_mask(frame, box))


STYLE_TUPLES = ("A-A1-A-A-A", "A-C1-A-A-A", "A-I3-A-A-A")
"""Three hair styles walked ON THE GAME, and why three and why these.

**What it measured, twice, and the second time is the one that holds.**  The
first run found the game's C1 and I3 pictures matching OUR A1 -- and the cause
was ours: `pose()` posed only the reference head, so our C1 and I3 drew their
heads at the file's origin (`scene.place_for` fixes it, and `--check-image`
now guards it).  With every head posed, at the full figure's size, each style
matches its own by a few percent -- C1 402 against A1's 430, I3 391 against
412 -- but the game's A1 picture matches our I3 (378) better than our A1 (399).
The game's own three photographs differ by only 15 and 29 pixels: at this size
a hair style is a handful of pixels, and the silhouette does not separate them.
`--silhouette` does not assert it.  Where a style IS big is the close-up the
game shows with a head row under the cursor, and that is where
`--silhouette-styles` asks: with photograph and camera from the same stop
(`closeup_at_tuple`), each of the game's six photographs picks its own style,
by 1.36x to 4.10x against the nearest wrong one.  It read "2 of 3, A1 being
the one it misses" -- the first close-up, with a camera from another moment --
and had the gate asserting it and failing, until CORR-LOOKS-064.

Three because one is an anchor and two is a pair: what has to hold is that the
silhouette follows the mesh the SCREEN is showing, in every style the screen
can reach, and not only in the one the save state happens to load with.  These
three because the assembly table draws all of them and they move the outline
by 656 and 783 pixels of 2686 against each other -- measured on the panel's own
size, so they are distinguishable at the size the comparison is made at.
"""

def route_row(text: str, oracle) -> str:
    """The row `route` leaves the cursor on for *text*: the last one it edits."""
    here = oracle.CURSOR_STARTS_ON
    for row, _button, _count in plan(text, oracle.ROWS, here):
        here = row
    return here


def our_silhouette(data, text, figure, frame, camera, size, centre):
    """Our own mask for one tuple at one frame of the walk."""
    import scene

    drawn = scene.build(data, looks.parse_tuple(text), figure, frame)
    return scene.silhouette(drawn, camera, size, centre)


def fit_centre(theirs, projected, size):
    """The one translation the comparison needs, from the two boxes.

    The GTE's offsets are ZERO on this screen -- measured -- so where the
    figure's own screen frame sits inside the panel is the GPU's draw offset,
    and our places are relative to one piece -- the second boot
    (CORR-LOOKS-062) -- rather than to the game's world.  Both fold into ONE
    translation, of about 170 pixels.  *projected* is
    the UNCLIPPED box our points land in: a rasterised mask cannot be measured
    from, because with no translation the figure lands outside the picture
    entirely and the mask comes back empty.

    **It is measured per comparison, which makes the comparison translation
    free on purpose.**  One translation held across every comparison sounded
    stricter and was worse: fitted on one pose and applied to a photograph of
    another, it moved the whole figure and every candidate scored badly --
    measured, the best match went from 13% of the ink to 72%.  What this
    comparison judges is therefore SHAPE and SIZE, not where the figure sits in
    the panel; where it sits is the GPU's draw offset, which nothing here
    measures and which this says rather than implying.
    """
    import scene

    yours = scene.mask_box(theirs, size)
    if yours is None:
        raise ConfrontError("the game's mask is empty, so no centre can be "
                            "measured from it")
    return ((yours[0] + yours[2] - projected[0] - projected[2]) / 2.0,
            (yours[1] + yours[3] - projected[1] - projected[3]) / 2.0)


def _judged(label, theirs, named, cycle, data, text, figure, camera, size,
            scene, offsets, key, style_control=False) -> list:
    """One picture against the whole walk.  The problems, and it prints the row.

    It is a function because the frame captures and the style captures ask the
    same four questions of the same numbers, and two copies of four thresholds
    is two things to keep right.
    """
    scores = {}
    for step in range(-NEIGHBOURS, NEIGHBOURS + 1):
        at = (named + step) % cycle
        drawn = scene.build(data, looks.parse_tuple(text), figure, at)
        centre = fit_centre(theirs, scene.projected_box(drawn, camera), size)
        ours = our_silhouette(data, text, figure, at, camera, size, centre)
        scores[at] = scene.masks_differ(theirs, ours)
    best = min(scores, key=scores.get)
    # The control of the whole comparison: our side drawn at the same frame
    # with a hair the screen is not showing.  It has to score WORSE, or this
    # is not seeing the mesh -- which is exactly what section 6 (h) says
    # colour could not do.
    wrong_text = swapped_style(text)
    wrong_drawn = scene.build(data, looks.parse_tuple(wrong_text), figure, best)
    wrong = our_silhouette(
        data, wrong_text, figure, best, camera, size,
        fit_centre(theirs, scene.projected_box(wrong_drawn, camera), size))
    wrong_score = scene.masks_differ(theirs, wrong)
    behind = (named - best) % cycle
    offsets[key] = behind
    ink = sum(theirs)
    problems = []
    if behind > WALK_LAG:
        problems.append(
            "%s: the game's pair names walk frame %d and the picture matches "
            "frame %d, %d behind -- over the %d a one-frame lag can be"
            % (label, named, best, behind, WALK_LAG))
    if scores[best] > ink * MATCH_SHARE:
        problems.append(
            "%s: the best silhouette is %d pixel(s) from the game's %d of ink "
            "(%.0f%%), over the %.0f%% a matching figure takes"
            % (label, scores[best], ink, 100.0 * scores[best] / ink,
               100.0 * MATCH_SHARE))
    if style_control and wrong_score < scores[best] * STYLE_MARGIN:
        problems.append(
            "%s: %s scores %d and %s scores %d -- a style the screen is not "
            "showing has to be at least %.1fx worse, or the silhouette is not "
            "seeing the mesh"
            % (label, text, scores[best], wrong_text, wrong_score,
               STYLE_MARGIN))
    if scores[best] * MATCH_MARGIN > max(scores.values()):
        problems.append(
            "%s: the best of the sweep beats the worst by only %.1fx, under "
            "the %.1fx a real minimum takes -- a sweep with no minimum is not "
            "comparing figures"
            % (label, max(scores.values()) / float(scores[best] or 1),
               MATCH_MARGIN))
    print("    %-22s pair names walk frame %2d; best at %2d, %d behind, %d of "
          "%d (%.0f%%); %s scores %d"
          % (label, named, best, behind, scores[best], ink,
             100.0 * scores[best] / ink, wrong_text, wrong_score))
    return problems


HEAD_BAND = 40
"""Rows from the top of the game's ink that a close-up is judged on.

The HEAD, and only the head: below it the game's dark kit sits on a dark
background and the row-by-row mask loses it -- measured, the masks' boxes sit
3 pixels apart while the body scores half the ink.  A style is a head, so the
band is where the question is.  Measured at 30, 40 and 50 rows on the first
close-ups and the verdict did not move between them.
"""

CLOSE_UP_ROW = "HAIR"
"""The row the cursor sits on for a close-up -- the one whose value moves."""

CLOSEUP_MARGIN = 1.2
"""How much worse the nearest WRONG style must score than the right one, in
the close-up.

Measured 2026-09-18 over the six photographs of both slots (CORR-LOOKS-063):
the nearest wrong style scores **1.36x** the right one at the tightest -- slot
2's A1 photograph against our I3 -- and 4.10x at the widest (slot 2, C1), and
the ceiling is written below the smallest (pitfall 49).  The nearest, not the
worst: against the worst the widest is 4.73x, and a verdict is only as safe
as the style it almost picked.  It is NOT
`STYLE_MARGIN`'s 1.5, and on purpose: that one was written for the full
figure, where it was never met, and at 1.5 the correct run of today would
fail on its tightest photograph.  What this catches is the verdict that is
right only by a hair -- two styles the head band cannot tell apart, which a
bare minimum passes as long as the order does not flip.
"""

CLOSEUP_SHARE = 0.25
"""The most of the game's head-band ink the right style may differ by.

The close-up's own `MATCH_SHARE`: without it the right style passes at any
score, as long as the two wrong ones score worse.  Measured 2026-09-18 over
the six photographs of both slots: **6% to 8%** -- 119 of 2120 to 202 of 2379
-- so the ceiling sits at three times the worst, which is the room
`MATCH_SHARE` leaves over its own 8% to 17%.
"""


def closeup_at_tuple(game, slot, text, oracle, anime, adata, entry, table,
                     maps, names):
    """(walk frame, the panel's mask, the camera) of one close-up, ONE stop.

    **The camera is derived from the pieces of this very pass**
    (`oracle.camera_from_pieces`), not read off the camera load: the figure
    TURNS in the close-up, by a different angle at every capture -- 18.3,
    -16.9 and 16.9 degrees on the first three -- and the load does not carry
    the turn.  A photograph and a camera from two different moments would be
    comparing a turned head with an unturned one, which is what made the first
    close-up verdict "2 of 3".
    """
    oracle.restore_state(slot, verbose=False)
    game.load_looks(slot, label="closeup-%d-%s" % (slot, text))
    route(game, text, oracle)
    here = route_row(text, oracle)
    way, distance = moves(oracle.ROWS, here, CLOSE_UP_ROW)
    for _ in range(distance):
        game.press(way, box=oracle.FOOTER, least=oracle.ROW_MOVED)
    game.step(oracle.CLOSE_UP_SETTLE)
    pieces = oracle._pose_cycle(game, maps, names)
    import screen as screen_module

    frame = still_frame(game, table["display"], oracle, screen_module)
    box = table["regions"]["panel"]["native"]
    camera = oracle.camera_from_pieces(pieces, adata)
    head = [one for one in pieces if one.get("pair") is not None][0]
    return (anime.frame_of_pair(adata, entry, head["pair"]),
            panel_mask(frame, box), camera)


def closeup_verdict(slot, shown, scores, ink) -> tuple:
    """(ratio, share, problems) for one close-up photograph.

    *scores* is {our tuple: pixels apart in the head band}, *shown* the tuple
    the game was walked to, *ink* the game's own head-band pixels.  Pure, so
    that the self check can hand it made-up numbers and a planted control can
    break it without an emulator (CORR-LOOKS-063).
    """
    problems = []
    best = min(scores, key=scores.get)
    nearest = min(score for ours, score in scores.items() if ours != shown)
    ratio = nearest / float(scores[shown] or 1)
    share = scores[shown] / float(ink or 1)
    if best != shown:
        problems.append(
            "slot %d: the game shows %s and its head matches our %s better "
            "(%d against %d)" % (slot, shown, best, scores[best],
                                 scores[shown]))
    elif ratio < CLOSEUP_MARGIN:
        problems.append(
            "slot %d: the game shows %s and the nearest wrong style scores "
            "only %.2fx its own, under the %.1fx that tells two heads apart"
            % (slot, shown, ratio, CLOSEUP_MARGIN))
    if share > CLOSEUP_SHARE:
        problems.append(
            "slot %d: the game shows %s and our %s still differs in %d of %d "
            "head-band pixel(s) (%.0f%%), over the %.0f%% a match takes"
            % (slot, shown, shown, scores[shown], ink, 100.0 * share,
               100.0 * CLOSEUP_SHARE))
    return ratio, share, problems


def check_closeup_styles(slots=(2, 1), verbose=True) -> int:
    """`--silhouette-styles [SLOT]`: three hair styles, in the close-up.

    The full figure cannot answer it -- a style is 15 to 29 pixels of it, in
    the game's own photographs -- so this walks the game to each style, puts
    the cursor on HAIR, and compares HEADS: each game photograph against our
    three styles, drawn with the camera of that same stop.  What is asserted
    is that every photograph picks its own style, in both slots.

    Since CORR-LOOKS-063 the question is asked the way `--silhouette` asks
    its own: a **control** first -- the same close-up twice, which has to come
    back identical -- and then not only "is the minimum the right one" but by
    how much (`CLOSEUP_MARGIN`, against the nearest wrong style) and how close
    the right one is at all (`CLOSEUP_SHARE`).  A bare minimum over three
    candidates catches a swapped style and nothing else.
    """
    import anime
    import iso_source
    import layout
    import oracle
    import scene
    import screen

    ready = oracle.preflight()
    table = screen.load()
    with iso_source.open_disc(ready["image"]) as disc:
        data = {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D,
                             layout.ANIME)}
    entry = anime.header(data[layout.ANIME])[layout.ANIME_SCREEN_ENTRY]
    block = anime.block(data[layout.ANIME], entry)
    box = table["regions"]["panel"]["native"]
    size = (box[2] - box[0] + 1, box[3] - box[1] + 1)
    width = size[0]
    # Where the camera's axis falls inside the panel: the screen's own middle,
    # because the GTE's offsets are zero -- measured, the two masks' boxes land
    # 3 pixels apart with nothing fitted.
    centre = (table["display"][0] / 2.0 - box[0],
              table["display"][1] / 2.0 - box[1])
    maps = oracle.model_maps(ready["image"])
    names, _orders = oracle.piece_names(ready["image"])
    problems = []
    with oracle.Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, oracle.SLOTS[slot]))
            figure = scene.screen_state(slot).figure()
            focal = scene.load_camera(slot)["projection"]
            # The control, before any comparison (CORR-LOOKS-063): the same
            # close-up twice has to come back the same -- walk frame, mask
            # and derived camera -- or the photographs below are measuring
            # the emulator's mood.  The close-up is deterministic, so the
            # expected difference is zero, not "small".
            first = closeup_at_tuple(game, slot, STYLE_TUPLES[0], oracle,
                                     anime, data[layout.ANIME], entry, table,
                                     maps, names)
            again = closeup_at_tuple(game, slot, STYLE_TUPLES[0], oracle,
                                     anime, data[layout.ANIME], entry, table,
                                     maps, names)
            apart = sum(1 for a, b in zip(first[1], again[1]) if a != b)
            same_camera = first[2]["rotation"] == again[2]["rotation"]
            print("    control: %s close-up captured twice, walk frame %d and "
                  "%d, %d pixel(s) apart, camera %s"
                  % (STYLE_TUPLES[0], first[0], again[0], apart,
                     "identical" if same_camera else "DIFFERENT"))
            if apart or first[0] != again[0] or not same_camera:
                problems.append(
                    "slot %d: the same close-up twice differs (%d pixel(s), "
                    "walk %d and %d, camera %s), so no photograph of this "
                    "slot is judged" % (slot, apart, first[0], again[0],
                                        "same" if same_camera else "not"))
                continue
            for shown in STYLE_TUPLES:
                if shown == STYLE_TUPLES[0]:
                    walk, theirs, derived = again
                else:
                    walk, theirs, derived = closeup_at_tuple(
                        game, slot, shown, oracle, anime, data[layout.ANIME],
                        entry, table, maps, names)
                reference = {one["piece"]: one for one in anime.frame_angles(
                    data[layout.ANIME], block["frames"][walk])}[
                        scene.REFERENCE_PIECE]["position"]
                rotation = derived["rotation"]
                camera = {"rotation": rotation, "projection": focal,
                          "translation": [
                              derived["translation"][axis]
                              + sum(rotation[axis * 3 + k] * reference[k]
                                    for k in range(3)) / float(scene.ONE)
                              for axis in range(3)]}
                top = scene.mask_box(theirs, size)[1]
                scores = {}
                for ours in STYLE_TUPLES:
                    drawn = scene.build(data, looks.parse_tuple(ours), figure,
                                        walk)
                    mask = scene.silhouette(drawn, camera, size, centre)
                    scores[ours] = sum(
                        1 for index, (a, b) in enumerate(zip(theirs, mask))
                        if a != b and top <= index // width < top + HEAD_BAND)
                best = min(scores, key=scores.get)
                ink = sum(1 for index, a in enumerate(theirs)
                          if a and top <= index // width < top + HEAD_BAND)
                ratio, share, wrong = closeup_verdict(slot, shown, scores, ink)
                print("    game %s: camera spread %.1f / %.2f, walk frame %d; "
                      "head band %s; nearest wrong %.2fx, right %d of %d "
                      "(%.0f%%)"
                      % (shown, derived["rotation_spread"],
                         derived["translation_spread"], walk,
                         "  ".join("%s %d%s" % (ours[2:4], scores[ours],
                                                "*" if ours == best else "")
                                   for ours in STYLE_TUPLES),
                         ratio, scores[shown], ink, 100.0 * share))
                problems += wrong
    for line in problems:
        print("  FAIL  %s" % line)
    print("confront --silhouette-styles: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def check_silhouette(slots=(2, 1), frames=SILHOUETTE_FRAMES,
                     verbose=True) -> int:
    """`--silhouette [SLOT]`: our shape against the game's, with the camera.

    The measurement colour could not make (section 6 (h)): a histogram tells
    skin from skin and says nothing about which MESH was drawn.  A silhouette
    does, and it only means anything once the projection is the game's -- which
    is what `oracle.py --camera` measured and this reads off disc.

    Two controls, both before any comparison:

      **the same counted frame twice** -- the panel's mask has to come back
          identical, or the picture is measuring the emulator's mood;
      **a different counted frame** -- it has to differ, or the capture is
          reading a constant and the first control passes perfectly.

    And what is asserted is not "the difference is small".  It is that the
    frame of ANIME.BIN the game's OWN pair names is the frame whose silhouette
    matches best, at the same offset every time: the sweep looks NEIGHBOURS
    frames either side, and a bridge that named the wrong frame would show up
    as a different winner here and there rather than as one constant.
    """
    import anime
    import iso_source
    import layout
    import oracle
    import scene
    import screen

    ready = oracle.preflight()
    table = screen.load()
    with iso_source.open_disc(ready["image"]) as disc:
        data = {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D,
                             layout.ANIME)}
    entry = anime.header(data[layout.ANIME])[layout.ANIME_SCREEN_ENTRY]
    # The walk is a CYCLE, so the sweep wraps: a window that ran off the end
    # of the block raised instead of looking at the frame the game would play
    # next, which is the frame either side of the join.
    cycle = len(anime.block(data[layout.ANIME], entry)["frames"])
    box = table["regions"]["panel"]["native"]
    size = (box[2] - box[0] + 1, box[3] - box[1] + 1)
    print("  the panel is %dx%d native pixels, from screen.json" % size)

    problems = []
    offsets = {}
    with oracle.Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, oracle.SLOTS[slot]))
            camera = scene.load_camera(slot)
            state = scene.screen_state(slot)
            text, figure = state.tuple_text(), state.figure()
            print("    the state shows %s, figure %d; H %d px"
                  % (text, figure, camera["projection"]["H"]))

            theirs, plays = {}, {}
            named, first = game_at(game, slot, frames[0], oracle, anime,
                                   data[layout.ANIME], entry, table)
            twice, again = game_at(game, slot, frames[0], oracle, anime,
                                   data[layout.ANIME], entry, table)
            apart = scene.masks_differ(first, again)
            if named != twice:
                problems.append(
                    "slot %d: frame %d read ANIME frame %d once and %d the "
                    "next time, so the run is not repeatable"
                    % (slot, frames[0], named, twice))
                continue
            if apart:
                problems.append(
                    "slot %d: the panel at frame %d differs from itself in %d "
                    "pixel(s), so no difference below means anything"
                    % (slot, frames[0], apart))
                continue
            print("    control: frame %d captured twice, %d pixel(s) of ink, "
                  "identical" % (frames[0], sum(first)))
            theirs[frames[0]], plays[frames[0]] = first, named
            for counted in frames[1:]:
                plays[counted], theirs[counted] = game_at(
                    game, slot, counted, oracle, anime, data[layout.ANIME],
                    entry, table)
            moved = {counted: scene.masks_differ(first, theirs[counted])
                     for counted in frames[1:]}
            if not any(moved.values()):
                problems.append(
                    "slot %d: frames %s draw the same panel as frame %d -- the "
                    "capture is reading a constant"
                    % (slot, list(frames[1:]), frames[0]))
                continue
            print("    control: frame(s) %s differ from it by %s pixel(s)"
                  % (list(frames[1:]),
                     [moved[counted] for counted in frames[1:]]))

            for counted in frames:
                problems += _judged(
                    "slot %d frame %d" % (slot, counted), theirs[counted],
                    plays[counted], cycle, data, text, figure, camera, size,
                    scene, offsets, (slot, counted))

    if offsets:
        print("  the picture trails the draw by %s frame(s) of the walk over "
              "%d comparison(s), and the bound is %d"
              % (sorted(set(offsets.values())), len(offsets), WALK_LAG))
    for line in problems:
        print("  FAIL  %s" % line)
    print("confront --silhouette: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


STATURE_SHOWN = (
    ("155 cm", (("HEIG", "155 cm"),)),
    ("210 cm", (("HEIG", "210 cm"),)),
    ("D TYPE", (("BODY", "D TYPE"),)),
    ("H TYPE", (("BODY", "H TYPE"),)),
)
"""The statures `--silhouette-stature` walks the game to: the two ends of
`HEIG`, and two `BODY` -- the middle of the table and its widest end.  The
state's own 175 cm and `A TYPE` is the control each one is held against."""

STATURE_FRAME = 60
"""Counted frames after the last press before the photograph: the first of
`SILHOUETTE_FRAMES`, so the sweep starts where `--silhouette` settled."""


def check_silhouette_stature(slots=(2, 1), verbose=True) -> int:
    """`--silhouette-stature [SLOT]`: HEIG and BODY against the game's shape.

    The same judgement as `--silhouette` -- the sweep around the frame the
    game's own pair names, `MATCH_SHARE`, `WALK_LAG` and `MATCH_MARGIN`, the
    thresholds LOOKS-TASK-28 measured -- on the game walked to another stature,
    and our figure drawn with the camera `scene.load_camera` composes for it.

    Controls, before and beside:

      **the state photographed twice** -- identical, or no pixel below means
          anything;
      **the statures move the game's picture** -- every walked photograph has
          to differ from the state's, or the walk reached nothing;
      **the state's own stature on our side** -- our figure at 175 cm and
          `A TYPE`, fitted the same way, has to score WORSE than the stature
          the rows show.  The comparison is translation free, so what is left
          to tell them apart is size and shape, which is what HEIG and BODY
          change -- and only where the game's own photograph moved by MORE
          than our best match misses by.  Under that the ranking is noise and
          is printed as such, not asserted either way (pitfall 76).
    """
    import anime
    import iso_source
    import layout
    import oracle
    import scene
    import screen
    import stature

    ready = oracle.preflight()
    table = screen.load()
    with iso_source.open_disc(ready["image"]) as disc:
        data = {name: disc.read(name)
                for name in (layout.EDT_MOD, layout.MODEL, layout.DAT2D,
                             layout.ANIME, layout.SELECT8)}
    found = stature.rule(data[layout.SELECT8])
    entry = anime.header(data[layout.ANIME])[layout.ANIME_SCREEN_ENTRY]
    cycle = len(anime.block(data[layout.ANIME], entry)["frames"])
    box = table["regions"]["panel"]["native"]
    size = (box[2] - box[0] + 1, box[3] - box[1] + 1)
    problems = []
    offsets = {}
    with oracle.Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, oracle.SLOTS[slot]))
            state = scene.screen_state(slot)
            text, figure = state.tuple_text(), state.figure()
            own = state.values()
            base = scene.load_camera(slot)
            named, first = game_at(game, slot, STATURE_FRAME, oracle, anime,
                                   data[layout.ANIME], entry, table)
            twice, again = game_at(game, slot, STATURE_FRAME, oracle, anime,
                                   data[layout.ANIME], entry, table)
            if (named, first) != (twice, again):
                problems.append("slot %d: the state photographed twice "
                                "differs, so nothing below is a measurement"
                                % slot)
                continue
            print("    control: the state (%d cm, %s TYPE) photographed "
                  "twice, identical, %d pixel(s) of ink"
                  % (own["height"], "ABCDEFGH"[own["build"]], sum(first)))
            for name, steps in STATURE_SHOWN:
                plays, theirs = game_at(game, slot, STATURE_FRAME, oracle,
                                        anime, data[layout.ANIME], entry,
                                        table, steps)
                moved = scene.masks_differ(first, theirs)
                if not moved:
                    problems.append("slot %d, %s: the game's picture is the "
                                    "state's -- the walk reached nothing"
                                    % (slot, name))
                    continue
                values = dict(own)
                walked = scene.screen_state(slot)
                for row, value in steps:
                    walked.indices[row] = screen.index_of(table, row, value)
                values.update(walked.values())
                camera = scene.load_camera(slot, stature.scale(
                    found, values["height"], values["build"]))
                label = "slot %d %s" % (slot, name)
                problems += _judged(label, theirs, plays, cycle, data, text,
                                    figure, camera, size, scene, offsets,
                                    (slot, name))
                behind = offsets[(slot, name)]
                at = (plays - behind) % cycle
                right = _stature_score(data, text, figure, at, camera, size,
                                       theirs, scene)
                wrong = _stature_score(data, text, figure, at, base, size,
                                       theirs, scene)
                print("      the game's picture moved %d pixel(s) off the "
                      "state's; at frame %d our %s scores %d and the state's "
                      "own stature %d" % (moved, at, name, right, wrong))
                if moved <= right:
                    # Under the silhouette's resolution, and said so: the
                    # game's OWN two pictures differ by less than our best
                    # match already misses by, so no ranking of statures is
                    # a measurement here (pitfall 76).  `D TYPE` is 10% wider
                    # than the state and lands here in both slots.
                    print("      below the silhouette's resolution: the game's "
                          "own pictures differ by %d, under the %d our match "
                          "misses by -- not ranked" % (moved, right))
                elif wrong <= right:
                    problems.append(
                        "slot %d, %s: our figure at the state's stature scores "
                        "%d against the %d of the stature on screen -- the "
                        "comparison does not see HEIG and BODY"
                        % (slot, name, wrong, right))
    for line in problems:
        print("  FAIL  %s" % line)
    print("confront --silhouette-stature: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def _stature_score(data, text, figure, frame, camera, size, theirs, scene):
    """Pixels apart, our figure at *frame* under *camera*, fitted as usual."""
    drawn = scene.build(data, looks.parse_tuple(text), figure, frame)
    centre = fit_centre(theirs, scene.projected_box(drawn, camera), size)
    return scene.masks_differ(theirs, scene.silhouette(drawn, camera, size,
                                                       centre))


OUTSIDE_FRAME = 60
"""Counted frames after the state loads before the game's picture is taken."""

OUTSIDE_SLACK = 16
"""How far our region's ground may sit from the game's, per channel.

Five bits a channel in the frame buffer is steps of eight; two steps is what a
gradient's own banding moves between two renderers.  A region painted with a
colour chosen by eye misses by far more: the help box's grey border colour,
which the v2 filled it with, is 142 away.
"""

OUTSIDE_REGIONS = ("panel", "rows", "help", "title band", "ground below",
                   "ground left", "title", "icon", "shirt boxes", "plate",
                   "labels", "values")
"""The regions whose ground colour this cycle has MEASURED (`oracle.py
--scenery`), and so the ones this comparison asserts.  The rest of the screen
-- the cursor box -- is printed beside them and not asserted, because nothing
measured says what it should be yet."""

FURNITURE_REGIONS = {
    "title band": (192, 20, 480, 32),
    "ground below": (0, 223, 511, 239),
    "ground left": (0, 66, 15, 185),
}
"""Boxes of furniture `screen.json` does not name, in native pixels: the teal
band of the title where no letter falls, and two pieces of the background.
Their packets are the ones `oracle.py --scenery` walks off the list the frame
hands the GPU -- the title band three additive gradients, the background
eight opaque ones (2026-09-21)."""


SPRITE_REGION_GROUPS = ("title", "icon", "shirt boxes", "plate")
"""The static sprites whose box is a region of the comparison (LOOKS-TASK-36).

The bar is not one: every texel of it is transparent, so its box is the
shirt box under it and would be counted twice."""


def sprite_regions(slot):
    """{group: (left, top, right, bottom)} of the static sprites of *slot*.

    The union of each group's sprites, inclusive, off the table
    `oracle.py --scenery --write` measured -- not off the code that draws them.
    """
    import scene
    import sprites

    boxes = {}
    for one in scene.load_sprites(slot):
        name = sprites.group_of(one)
        if name not in SPRITE_REGION_GROUPS:
            continue
        (x, y), (w, h) = one["point"], one["size"]
        box = (x, y, x + w - 1, y + h - 1)
        old = boxes.get(name, box)
        boxes[name] = (min(old[0], box[0]), min(old[1], box[1]),
                       max(old[2], box[2]), max(old[3], box[3]))
    return boxes


HELP_INSET = 2
"""Pixels taken off the help box before its text is compared: the border of
the box is furniture, measured and asserted by its own region."""


def text_regions(table):
    """{labels, values, help: box} -- the text of the screen, in three boxes.

    Off `screen.json` and nothing else: the labels from their object's x to
    the left edge of the leftmost value box, the values from there to the
    right edge of the widest one, both over the twelve lines (LOOKS-TASK-37);
    and the inside of the help box (LOOKS-TASK-39).
    """
    width, height = table["display"]
    x0 = table["initial"]["2"]["anchors"]["labels"][0] + width // 2
    top = table["row0_y"] + height // 2
    bottom = top + table["pitch"] * len(table["order_of_rows"]) - 1
    boxes = [table["rows"][name]["cursor"] for name in table["order_of_rows"]]
    left = min(box[0] for box in boxes)
    right = max(box[2] for box in boxes)
    box = table["regions"]["help"]["native"]
    return {"labels": (x0, top, left - 1, bottom),
            "values": (left, top, right, bottom),
            "help": (box[0] + HELP_INSET, box[1] + HELP_INSET,
                     box[2] - HELP_INSET, box[3] - HELP_INSET)}


TEXT_INK_SLACK = {"labels": 0, "values": 0}
"""Pixels of each text column allowed to differ from the game's frame.

The help box is measured and NOT in here, which is the whole of what
LOOKS-TASK-39 found: the game draws that text with the console's own character
ROM (`oracle.py --help-box`), which is not on the disc and not this
repository's to ship, so the window draws it with a stand-in and the pixels
cannot agree.  The line is printed with its floor and its shifted control, so
what it costs is on the record rather than hidden by leaving the box out.
"""


def _area(box):
    return (box[2] - box[0] + 1) * (box[3] - box[1] + 1)


def ink_differences(one, two, box, skip=frozenset()):
    """Pixels of *box* where the two frames differ past `OUTSIDE_SLACK`,
    leaving out the pixels in *skip*."""
    left, top, right, bottom = box
    return sum(1 for y in range(top, bottom + 1)
               for x in range(left, right + 1)
               if (x, y) not in skip
               and colour_distance(one[y][x], two[y][x]) > OUTSIDE_SLACK)


def ground_colour(frame, box, skip=None):
    """The ground of a region: the median of each channel, figure left out.

    The median and not the commonest colour, and it was the commonest first:
    on a GRADIENT the commonest shade is decided by ties and by the console's
    dithering -- the help box's came out (8, 64, 96) in the game and
    (0, 40, 64) in our window, with both gradients running from the same
    colour to the same colour.  The median of a gradient is its middle, on
    either side, and the letters on it are too few to move it.  *skip* is a
    mask the size of the box, 1 where the figure is.
    """
    left, top, right, bottom = box
    width = right - left + 1
    channels = ([], [], [])
    for y in range(top, bottom + 1):
        for x in range(left, right + 1):
            if skip is not None and skip[(y - top) * width + (x - left)]:
                continue
            for index, value in enumerate(frame[y][x][:3]):
                channels[index].append(value)
    if not channels[0]:
        return None
    middle = len(channels[0]) // 2
    return tuple(sorted(one)[middle] for one in channels)


def colour_distance(one, two):
    return max(abs(a - b) for a, b in zip(one, two))


def check_outside(slots=(2, 1), verbose=True) -> int:
    """`--outside [SLOT]`: our screen against the game's, outside the figure.

    What LOOKS-TASK-31 asks of the furniture: the same picture as the game's
    where the figure is not.  For each region `screen.json` names, the ground
    colour -- the commonest, with the figure's own pixels left out -- of the
    game's frame and of our window at native size.

    **The control first:** the game photographed twice at the same counted
    frame has to give the same ground everywhere, or no distance below means
    anything.  The regions whose colours were measured (`OUTSIDE_REGIONS`) are
    asserted within `OUTSIDE_SLACK`; the rest of the screen is printed, so
    what is still drawn by eye says so.
    """
    import oracle
    import screen
    import ui_check

    ready = oracle.preflight()
    table = screen.load()
    display = table["display"]
    box = table["regions"]["panel"]["native"]
    python, app = _python_and_app()
    problems = []
    theirs = {}
    with oracle.Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            frames = []
            for _ in range(2):
                oracle.restore_state(slot, verbose=False)
                game.load_looks(slot, label="outside-%d" % slot)
                game.step(OUTSIDE_FRAME)
                frames.append(still_frame(game, display, oracle, screen))
            theirs[slot] = frames
    for slot in slots:
        print("  -- slot %d --" % slot)
        first, again = theirs[slot]
        figure = panel_mask(first, box)
        regions = dict((name, table["regions"][name]["native"])
                       for name in table["regions"])
        regions.update(FURNITURE_REGIONS)
        regions.update(sprite_regions(slot))
        regions.update(text_regions(table))
        control = [name for name in sorted(regions)
                   if ground_colour(first, regions[name])
                   != ground_colour(again, regions[name])]
        if control:
            problems.append("slot %d: the game photographed twice has another "
                            "ground in %s, so nothing below is measured"
                            % (slot, ", ".join(control)))
            continue
        print("    control: the game photographed twice, the same ground in "
              "all %d region(s)" % len(regions))
        out = os.path.join(out_dir(), "ours-outside-%d.png" % slot)
        code, output = ui_check.run_app(
            python, app, ["--state", str(slot), "--scale", "1",
                          "--screenshot", out], ui_check.environment())
        if code or not os.path.isfile(out):
            problems.append("slot %d: our window did not draw -- %s"
                            % (slot, output.strip()[-300:]))
            continue
        shot = ui_check.picture(out)
        width, height, channels, rows = shot
        ours = [[tuple(row[x * channels:x * channels + 3])
                 for x in range(width)] for row in rows]
        # The labels are left-aligned where their object says, so they are
        # the one text that can be held pixel by pixel, within
        # `OUTSIDE_SLACK` per channel: the pixels of the column whose largest
        # channel distance passes that slack, the game's frame against the
        # same frame photographed again as the floor. Without the slack
        # 11839 of 16416 differ, because our band's ground sits ~6 from the
        # game's (CORR-LOOKS-072).
        # The cursor box pulses in the game (trap 36) and is a fixed colour in
        # our window: its outline is not text, and is left out of the columns.
        cursor = table["rows"][table["cursor_on_load"]]["cursor"]
        outline = {(x, y) for x in range(cursor[0], cursor[2] + 1)
                   for y in range(cursor[1], cursor[3] + 1)
                   if x in (cursor[0], cursor[2]) or y in (cursor[1],
                                                           cursor[3])}
        for column, box in sorted(text_regions(table).items()):
            floor = ink_differences(first, again, box, outline)
            apart = ink_differences(first, ours, box, outline)
            shifted = [row[1:] + row[:1] for row in first]
            control = ink_differences(shifted, ours, box, outline)
            print("    %s, pixel for pixel within %d per channel: %d of %d "
                  "differ (the game against itself: %d; the game one pixel "
                  "off: %d)%s" % (column, OUTSIDE_SLACK, apart, _area(box),
                                  floor, control,
                                  "" if column in TEXT_INK_SLACK
                                  else "  (the console's font, not ours to "
                                       "draw: not asserted)"))
            if not control:
                problems.append("slot %d: the %s one pixel off do not differ "
                                "either, so equal says nothing"
                                % (slot, column))
            if floor:
                problems.append("slot %d: the %s differ from themselves in %d "
                                "pixel(s), so the comparison has no floor"
                                % (slot, column, floor))
            elif column not in TEXT_INK_SLACK:
                continue
            elif apart > TEXT_INK_SLACK[column]:
                problems.append("slot %d: %d pixel(s) of the %s differ from "
                                "the game's, over the %d allowed"
                                % (slot, apart, column,
                                   TEXT_INK_SLACK[column]))
        for name in sorted(regions):
            region = regions[name]
            skip = figure if name == "panel" else None
            game_ground = ground_colour(first, region, skip)
            our_ground = ground_colour(ours, region, skip)
            gap = colour_distance(game_ground, our_ground)
            asserted = name in OUTSIDE_REGIONS
            print("    %-12s game %-15s ours %-15s %3d apart%s"
                  % (name, game_ground, our_ground, gap,
                     "" if asserted else "  (not measured, not asserted)"))
            if asserted and gap > OUTSIDE_SLACK:
                problems.append("slot %d, %s: our ground is %d from the "
                                "game's, over the %d a measured colour takes"
                                % (slot, name, gap, OUTSIDE_SLACK))
    for line in problems:
        print("  FAIL  %s" % line)
    print("confront --outside: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


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

        if len(argv) >= 2 and argv[1] in ("--run", "--score", "--render"):
            slots = tuple(int(a) for a in argv[2:]) or (2, 1)
            if argv[1] == "--score":
                return 1 if score(slots) else 0
            if argv[1] == "--render":
                _python_and_app()
                render_ours(slots)
                return 0
            return run(slots)
        if len(argv) >= 2 and argv[1] in ("--silhouette",
                                           "--silhouette-styles",
                                           "--silhouette-stature"):
            # Two commands and not one flag inside a green gate: the styles
            # walked on the game DISAGREE today (LOOKS-TASK-28), and a
            # comparison that fails for a reason nobody has measured must not
            # ride inside the one that passes -- nor be quietly turned into a
            # note that passes with it.
            chosen = (int(argv[2]),) if len(argv) > 2 else (2, 1)
            if argv[1] == "--silhouette-styles":
                return check_closeup_styles(chosen)
            if argv[1] == "--silhouette-stature":
                return check_silhouette_stature(chosen)
            return check_silhouette(chosen)
        if len(argv) >= 2 and argv[1] == "--outside":
            return check_outside(tuple(int(a) for a in argv[2:]) or (2, 1))
        if len(argv) >= 2 and argv[1] == "--kit-control":
            return check_kit_control(tuple(int(a) for a in argv[2:]) or (2, 1))
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

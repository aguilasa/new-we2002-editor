#!/usr/bin/env python3
"""Which piece is which -- and, beside every name, how it was known.

Eleven sections make one player.  Naming them by vertex count is a guess, and
the plan says so: five of the pairs have identical counts, and the two models
differ by eight vertices in places that mean nothing on their own.  This module
names them from three facts that were measured, and then checks the answer
against a fourth that came from the running game.

    1. THE MIRROR PAIRS.  Nine of the twenty sections have a partner whose
       vertices are the same set with **z** negated -- exactly, as sets, not as
       bounding boxes.  What is left over in each list is one section: the
       torso.  (`mirror_axis`, and the axis is measured rather than assumed --
       x would be the guess, and x is not it.)

    2. THE LIST ORDER.  A header list is a chain, not a bag:

           list 0:  0 | 1 3 | 2 4 | 5 7 9 | 6 8 10
           list 1: 11 | 12 14 | 13 15 | 16 18 9 | 17 19 10

       Torso first, then one limb, then its mirror, and inside a limb the order
       runs from the body outwards.  `limbs()` cuts it at the point where the
       side flips, which needs no knowledge of what a limb is.

    3. WHAT THE TWO LISTS SHARE.  Sections 9 and 10 belong to both models and
       are byte-identical -- the goalkeeper and the outfield player wear the
       same boots.  A limb that ends in a shared section is a leg; the others
       are arms.  So the chain of three is thigh, shin, foot, and the chain of
       two is upper arm, forearm.

    4. AND THE GAME AGREES.  `oracle.py --fields SKIN` rewrote the CLUT of
       exactly the bare-skin sections: on the outfield player the forearm and
       not the upper arm -- a short sleeve -- and on the goalkeeper neither arm,
       which is a long sleeve; the legs on both; the feet on neither, because
       of the boots.  That is an independent witness for the two names that
       rule 2 alone would have had to take on trust, and it is the one the
       cycle profile demands: the option was changed in the game and the answer
       was read off what moved.

    5. AND BOOTS AGREES TOO, WITHOUT BEING ASKED.  `--fields BOOTS` rewrote the
       CLUT of sections 9 and 10 and of nothing else, in both slots.  Rule 3
       reached those two from the other end -- they are what the two lists
       share -- so the two arguments meet on the same pair without either
       having been fitted to the other.

Usage:
    python tools/looks/pieces.py --check
    python tools/looks/pieces.py --check-image           # takes WE2002_LOOKS_IMAGE
    python tools/looks/pieces.py --check-image <japanese.bin>
"""

from __future__ import annotations

import sys

import harness
import layout
import modelfile
import section

TORSO = "torso"
UPPER_ARM = "upper arm"
FOREARM = "forearm"
THIGH = "thigh"
SHIN = "shin"
FOOT = "foot"

ARM_CHAIN = (UPPER_ARM, FOREARM)
LEG_CHAIN = (THIGH, SHIN, FOOT)

HEAD = "head"
"""Not in EDT_MOD.BIN at all: the head is MODEL.BIN's section 24.

Named by the game and by nothing else -- HAIR, FACE and SKIN all write there
and nowhere else inside MODEL.BIN (LOOKS-TASK-08).  It is recorded here so the
eleven-plus-one is in one place, and `HEAD_SECTION` is the index a caller wants.
"""

HEAD_SECTION = 24

SKIN_SECTIONS = {
    1: (11, 16, 17, 18, 19),
    2: (0, 3, 4, 5, 6, 7, 8),
}
"""EDT_MOD.BIN sections whose CLUT one step of SKIN rewrote, per save-state slot.

Measured by `python tools/looks/oracle.py --fields SKIN` on 2026-09-14; slot 1
is the goalkeeper and slot 2 the outfield player.  Kept here because it is the
witness rule 4 uses, and a witness quoted from a session nobody can re-run is
not a witness -- the command that produces it is in the docstring above.
"""


BOOTS_SECTIONS = {1: (9, 10), 2: (9, 10)}
"""EDT_MOD.BIN sections one step of BOOTS rewrote, per slot.

The same measurement as SKIN_SECTIONS, one field over -- `oracle.py --fields
BOOTS`, 2026-09-15 -- and it is a **separate** witness rather than more of the
same one: rule 3 calls a limb a leg because it ends in a section both lists
share, and then calls that shared section a foot.  BOOTS says so from the other
direction, without being asked to: the only two sections it touches are exactly
those two, in both slots, and the boots are indeed the piece the two players
have in common.
"""


class BadPieces(Exception):
    """The file does not have the shape the naming rules need."""


class Piece:
    """One named section, and the reason it carries that name."""

    __slots__ = ("index", "name", "side", "models", "partner", "why")

    def __init__(self, index, name, side, models, partner, why):
        self.index = index
        self.name = name
        self.side = side
        """Which of a mirrored pair this is: "a", "b", or None when unpaired."""
        self.models = models
        """The header lists that name it.  Two means both players share it."""
        self.partner = partner
        self.why = why

    def __repr__(self):
        return "Piece(%d, %r, side=%r)" % (self.index, self.name, self.side)

    @property
    def full_name(self):
        return self.name if self.side is None else "%s %s" % (self.name,
                                                              self.side)


# --- the three measurements ------------------------------------------------

def mirror_axis(one, other):
    """The axis on which *other* is *one* reflected, or None.

    Compared as **sets of vertices**, which is the whole strength of the test:
    two pieces can share a bounding box and be different meshes, and the pairs
    here match vertex for vertex.  The axis is searched for rather than assumed
    -- the obvious guess is x, and this model mirrors in z.
    """
    if len(one.vertices) != len(other.vertices):
        return None
    theirs = sorted((v.x, v.y, v.z) for v in other.vertices)
    for axis in range(3):
        flipped = sorted(
            tuple(-value if index == axis else value
                  for index, value in enumerate((v.x, v.y, v.z)))
            for v in one.vertices
        )
        if flipped == theirs:
            return "xyz"[axis]
    return None


def mirror_candidates(sections):
    """index -> EVERY section that is this one reflected, not just the first.

    Kept separate from `mirrors()` because the interesting fact about this file
    is the plural: four sections have two candidates each, and a search that
    stopped at the first would never be able to say so.
    """
    out = {}
    for i, one in enumerate(sections):
        for j, other in enumerate(sections):
            if i == j:
                continue
            axis = mirror_axis(one, other)
            if axis is not None:
                out.setdefault(i, []).append((j, axis))
    return out


def _together(i, j, groups):
    """Do these two sections appear in the same header list?"""
    return any(i in group and j in group for group in groups)


def mirrors(sections, groups=None):
    """index -> (partner index, axis), for every section that has one.

    **A partner is not unique in this file, and the first draft assumed it
    was.**  The two players share the shin mesh vertex for vertex, so the left
    shin of one is a mirror of the right shin of BOTH -- four sections with two
    candidates each.  The old loop took the first and broke, and got the right
    answer only because 8 comes before 19 in file order.  Handed the same
    sections in the order 7, 19, 8, 18 it paired ACROSS the two players, with
    nothing in the output saying a choice had been made (CORR-LOOKS-020).

    *groups* are the header lists as sets of section indices.  A mirror pair is
    left-and-right OF THE SAME FIGURE, so a candidate only counts if the two
    share a list; the sections both lists own stay partners of each other.
    Given none, every section is a candidate for every other -- which is what
    the synthetic self-check wants, and what the red case exercises.

    Ambiguity that survives the filter is **refused**, not resolved.
    """
    candidates = mirror_candidates(sections)
    found = {}
    for i in sorted(candidates):
        eligible = [(j, axis) for j, axis in candidates[i]
                    if groups is None or _together(i, j, groups)]
        if not eligible:
            continue
        if len(eligible) > 1:
            raise BadPieces(
                "section %d has %d mirror partners in its own list -- %s -- "
                "and picking one of them is a guess, not a measurement"
                % (i, len(eligible),
                   ", ".join("%d in %s" % pair for pair in eligible))
            )
        found[i] = eligible[0]
    return found


def limbs(order, partner_of):
    """Cut a list's order into torso and limbs, by where the side flips.

    The rule needs no idea of what a limb is.  Walking the order after the
    torso, each section belongs to the side its pair was FIRST seen on; a run
    ends when that side changes.  On this file it cuts
    `[1, 3, 2, 4, 5, 7, 9, 6, 8, 10]` into `[1, 3] [2, 4] [5, 7, 9] [6, 8, 10]`.
    """
    runs, seen, current, current_side = [], set(), [], None
    for index in order:
        partner = partner_of.get(index)
        if partner is None:
            raise BadPieces(
                "section %d has no mirror partner, so it is a second torso "
                "and the chain cannot be cut" % index
            )
        # The first of a pair to appear is side "a" and its partner is "b".
        side = "b" if partner in seen else "a"
        seen.add(index)
        if current_side is not None and side != current_side:
            runs.append(current)
            current = []
        current.append(index)
        current_side = side
    if current:
        runs.append(current)
    return runs


def name_pieces(data):
    """Every section of EDT_MOD.BIN, named, with the rule that named it."""
    scan = section.scan(data, layout.GEOMETRY_START[layout.EDT_MOD])
    index_of = {one.offset: i for i, one in enumerate(scan.sections)}

    # The lists come FIRST, because the pairing needs them: a mirror pair is
    # left and right of the same figure, and without that this file has four
    # sections with two partners each.
    models = modelfile.read_models(data)
    owners = {}
    orders = {}
    for model in models:
        order = [index_of[target] for target in model.targets]
        orders[model.index] = order
        for index in order:
            owners.setdefault(index, []).append(model.index)

    paired = mirrors(scan.sections,
                     [set(order) for order in orders.values()])
    partner_of = {i: pair[0] for i, pair in paired.items()}

    shared = {i for i, lists in owners.items() if len(lists) > 1}
    if not shared:
        raise BadPieces("the two lists share no section, so nothing says which "
                        "limb is a leg")

    pieces = {}
    for list_index, order in sorted(orders.items()):
        torso = order[0]
        if torso in partner_of:
            raise BadPieces(
                "section %d opens list %d and has a mirror partner -- the "
                "torso is the unpaired one, so this file is not shaped the way "
                "these rules assume" % (torso, list_index)
            )
        pieces.setdefault(torso, Piece(
            torso, TORSO, None, owners[torso], None,
            "unpaired, and first in list %d" % list_index))

        for run in limbs(order[1:], partner_of):
            is_leg = bool(set(run) & shared)
            chain = LEG_CHAIN if is_leg else ARM_CHAIN
            if len(run) != len(chain):
                raise BadPieces(
                    "limb %s has %d section(s) and the %s chain has %d"
                    % (run, len(run), "leg" if is_leg else "arm", len(chain))
                )
            why = ("ends in a section both lists share -- the boots"
                   if is_leg else "no shared section, and the two models "
                   "differ here")
            for position, index in enumerate(run):
                first = index < partner_of[index]
                pieces.setdefault(index, Piece(
                    index, chain[position], "a" if first else "b",
                    owners[index], partner_of[index],
                    "%s; %d of %d outwards from the body"
                    % (why, position + 1, len(chain))))
    return pieces, orders, paired


# --- the two figures, compared piece by piece -------------------------------

def compare_lists(data, orders, sections):
    """Position by position, how the two lists' sections differ.

    A row per position: the two section indices, whether they are the SAME
    section, whether the sizes match, and -- when they do -- how many bytes
    differ and how many of those are vertex bytes rather than texture ones.

    **This exists because a sentence about it went wrong and nothing could
    catch it.**  The task's summary put the torso among the pieces of
    different size (it is not), gave the torso's two vertex bytes as if they
    described the thighs and shins too (22 and 0), and concluded "same mesh,
    different kit" for all eleven (CORR-LOOKS-021).  A renderer reading that
    loads one mesh and swaps the palette, and draws the goalkeeper with the
    outfield player's arm.  As a computation it cannot drift.
    """
    lists = [order for _index, order in sorted(orders.items())]
    if len(lists) != 2:
        raise BadPieces("comparing the figures needs exactly two lists, not %d"
                        % len(lists))
    rows = []
    for position, (i, j) in enumerate(zip(*lists)):
        one, other = sections[i], sections[j]
        row = {"position": position, "a": i, "b": j, "same_section": i == j,
               "verts": (len(one.vertices), len(other.vertices)),
               "prims": (len(one.primitives), len(other.primitives)),
               "sizes": (one.end - one.offset, other.end - other.offset),
               "differ": None, "vertex_bytes": None}
        if i != j and row["sizes"][0] == row["sizes"][1]:
            left = data[one.offset:one.end]
            right = data[other.offset:other.end]
            first_vertex = (section.HEADER_SIZE
                            + len(one.primitives) * section.PRIMITIVE_SIZE)
            differ = [k for k in range(len(left)) if left[k] != right[k]]
            row["differ"] = len(differ)
            row["vertex_bytes"] = sum(1 for k in differ if k >= first_vertex)
        rows.append(row)
    return rows


def mesh_agrees(rows, pieces):
    """Do the pieces whose MESH differs between the figures carry arm names?

    The measurement and the naming are independent, and this makes them check
    each other.  Where the two figures differ in mesh is the arm chain -- long
    sleeve against short -- and nowhere else: torso and thigh have the same
    vertex and primitive counts, the shin is identical byte for byte in the
    vertex block, and the feet are literally the same section.  A run where
    some other piece came out a different mesh means the names and the bytes
    have stopped agreeing, and one of them is wrong.

    The local is spelled `disagreements` rather than `problems` so the control
    that blinds `agrees_with_the_game()` keeps matching exactly one line --
    same reason `section.scan()` carries its own spelling (LOOKS-TASK-06).
    """
    disagreements = []
    for row in rows:
        if row["same_section"]:
            continue
        differs = row["sizes"][0] != row["sizes"][1]
        for index in (row["a"], row["b"]):
            if index not in pieces:
                continue
            name = pieces[index].name
            if differs and name not in ARM_CHAIN:
                disagreements.append(
                    "section %d is named %r and has a different mesh in the "
                    "other list -- only the arm chain should"
                    % (index, name))
            elif not differs and name in ARM_CHAIN:
                disagreements.append(
                    "section %d is named %r and has the same mesh in both "
                    "lists -- the arm chain is where they differ"
                    % (index, name))
    return disagreements


def say_comparison(rows):
    """The comparison as lines, for the report."""
    out = []
    for row in rows:
        if row["same_section"]:
            out.append("      pos %2d: section %d is SHARED by both lists"
                       % (row["position"], row["a"]))
        elif row["sizes"][0] != row["sizes"][1]:
            out.append("      pos %2d: %2d vs %2d  DIFFERENT MESH  %d/%d vs "
                       "%d/%d vert/prim, %d vs %d byte(s)"
                       % (row["position"], row["a"], row["b"],
                          row["verts"][0], row["prims"][0],
                          row["verts"][1], row["prims"][1],
                          row["sizes"][0], row["sizes"][1]))
        else:
            out.append("      pos %2d: %2d vs %2d  same size, %d of %d byte(s) "
                       "differ, %d of them vertex"
                       % (row["position"], row["a"], row["b"], row["differ"],
                          row["sizes"][0], row["vertex_bytes"]))
    return out


# --- the fourth witness ----------------------------------------------------

def bare_skin(pieces, slot):
    """The names the game's SKIN step rewrote, for one slot."""
    return sorted(pieces[i].full_name for i in SKIN_SECTIONS[slot]
                  if i in pieces)


def agrees_with_the_game(pieces, orders):
    """Does the skin map say what the names say?  Returns the disagreements.

    Two claims, and both are about ARMS, which is where rule 2 alone would be
    taking the chain order on trust:

    * the outfield player shows skin on the forearm and not on the upper arm
      -- a short sleeve;
    * the goalkeeper shows it on neither -- a long sleeve.

    Everything else is a consistency check: legs on both players, feet on
    neither.
    """
    problems = []
    outfield, goalkeeper = SKIN_SECTIONS[2], SKIN_SECTIONS[1]
    for slot, touched, label in ((2, outfield, "the outfield player"),
                                 (1, goalkeeper, "the goalkeeper")):
        owned = set(orders[0] if slot == 2 else orders[1])
        for index in touched:
            if index not in owned:
                problems.append(
                    "%s: SKIN touched section %d, which is not in that "
                    "model's list" % (label, index))
        names = {pieces[i].name for i in touched if i in pieces}
        if FOOT in names:
            problems.append("%s: SKIN touched a foot, and boots are not skin"
                            % label)
        if THIGH not in names or SHIN not in names:
            problems.append("%s: SKIN touched no thigh or no shin" % label)
        if UPPER_ARM in names:
            problems.append(
                "%s: SKIN touched an upper arm, which no sleeve in this game "
                "leaves bare" % label)
    if FOREARM not in {pieces[i].name for i in outfield if i in pieces}:
        problems.append("the outfield player: SKIN touched no forearm, so the "
                        "short sleeve is not visible in the measurement")
    if FOREARM in {pieces[i].name for i in goalkeeper if i in pieces}:
        problems.append("the goalkeeper: SKIN touched a forearm, and the long "
                        "sleeve covers it")

    # BOOTS, the other witness: it has to name the feet and nothing else.
    for slot, touched in sorted(BOOTS_SECTIONS.items()):
        names = {pieces[i].name for i in touched if i in pieces}
        if names != {FOOT}:
            problems.append(
                "slot %d: BOOTS touched %s, and boots are worn on feet"
                % (slot, ", ".join(sorted(names)) or "nothing named"))
        feet = {i for i, piece in pieces.items() if piece.name == FOOT}
        if set(touched) != feet:
            problems.append(
                "slot %d: BOOTS touched %s and the feet are %s -- the two have "
                "to be the same set" % (slot, sorted(touched), sorted(feet)))
    return problems


# --- reporting -------------------------------------------------------------

def bounds(one):
    """(x, y, z) extents of a section, as (min, max) pairs."""
    xs = [v.x for v in one.vertices]
    ys = [v.y for v in one.vertices]
    zs = [v.z for v in one.vertices]
    return ((min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs)))


def report(data, verbose=True):
    pieces, orders, paired = name_pieces(data)
    scan = section.scan(data, layout.GEOMETRY_START[layout.EDT_MOD])
    if verbose:
        print("  list order, as the header states it:")
        for index, order in sorted(orders.items()):
            print("      list %d: %s" % (index, order))
        print("  section  piece            side  lists  mirror  "
              "extent x,y,z      how it was known")
        for index in sorted(pieces):
            one = scan.sections[index]
            (x0, x1), (y0, y1), (z0, z1) = bounds(one)
            piece = pieces[index]
            print("      %2d     %-14s   %-4s  %-5s  %-6s  %4d,%4d,%4d    %s"
                  % (index, piece.name, piece.side or "-",
                     ",".join(map(str, piece.models)),
                     ("%s in %s" % (piece.partner, paired[index][1]))
                     if piece.partner is not None else "-",
                     x1 - x0, y1 - y0, z1 - z0, piece.why))
        print("  the two figures, one list against the other:")
        for line in say_comparison(compare_lists(data, orders, scan.sections)):
            print(line)
        groups = [set(order) for order in orders.values()]
        across = {}
        for index, candidates in mirror_candidates(scan.sections).items():
            other = [j for j, _axis in candidates
                     if not _together(index, j, groups)]
            if other:
                across[index] = other
        if across:
            # Said out loud because it is the interesting fact about this file,
            # and because it is what makes the pairing a decision rather than a
            # lookup: these sections would pair OUTSIDE their own list too.
            print("  also mirrored across the two lists: %s"
                  % ", ".join("%d~%s" % (i, v) for i, v in sorted(across.items())))
            print("      the two figures carry the same shin mesh, so the "
                  "pairing is confined to one list on purpose")
        for slot in sorted(SKIN_SECTIONS):
            print("  SKIN on slot %d rewrote: %s"
                  % (slot, ", ".join(bare_skin(pieces, slot))))
        for slot in sorted(BOOTS_SECTIONS):
            print("  BOOTS on slot %d rewrote: %s"
                  % (slot, ", ".join(sorted(
                      pieces[i].full_name for i in BOOTS_SECTIONS[slot]
                      if i in pieces))))
    return pieces, orders


def _check_image(path):
    import iso_source

    with iso_source.open_disc(path) as disc:
        data = disc.read(layout.EDT_MOD)
    pieces, orders = report(data)
    scan = section.scan(data, layout.GEOMETRY_START[layout.EDT_MOD])
    problems = agrees_with_the_game(pieces, orders)
    problems += mesh_agrees(compare_lists(data, orders, scan.sections), pieces)
    for line in problems:
        print("  FAIL  %s" % line)
    print("pieces --check-image: %s"
          % ("ok" if not problems else "%d disagreement(s)" % len(problems)))
    return 1 if problems else 0


# --- self-check ------------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("pieces.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses = c.refusing(BadPieces)

    # A mirror is a mirror of the VERTEX SET, and the axis is found, not
    # assumed.  Built rather than fixtured: the gate runs with no disc.
    body = section.build_section(3, 1)
    one = section.read_section(body, 0)

    class Flipped:
        def __init__(self, vertices):
            self.vertices = vertices

    class V:
        __slots__ = ("x", "y", "z")

        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    def flip(axis):
        return Flipped([V(*(-value if index == axis else value
                            for index, value in enumerate((v.x, v.y, v.z))))
                        for v in one.vertices])

    for axis, letter in enumerate("xyz"):
        ok("a set flipped in %s is recognised as mirrored in %s"
           % (letter, letter), mirror_axis(one, flip(axis)) == letter,
           "%s" % mirror_axis(one, flip(axis)))

    moved = Flipped([V(v.x + 1, v.y, v.z) for v in one.vertices])
    ok("a translated copy is not a mirror", mirror_axis(one, moved) is None)
    ok("a different length is not a mirror",
       mirror_axis(one, Flipped(list(one.vertices)[:-1])) is None)

    # -- two right answers, which is the case the real file has ------------
    #
    # Two copies of one mirrored pair: every section is then a mirror of two
    # others, and the three negative cases above -- translation, wrong length,
    # wrong axis -- say nothing about it.  This is what CORR-LOOKS-020 opened:
    # the old search took the first candidate and broke.
    twice = [one, flip(2), one, flip(2)]
    counted = attempt("count the candidates",
                      lambda: mirror_candidates(twice), default={})
    ok("every section of two identical pairs has two candidates",
       sorted(len(v) for v in counted.values()) == [2, 2, 2, 2],
       "%s" % {k: len(v) for k, v in sorted(counted.items())})

    refuses("an unconfined pairing refuses rather than picks",
            lambda: mirrors(twice), "picking one of them is a guess")

    # Confined to a list, each copy pairs within itself -- and, crucially, the
    # SAME answer whichever order the sections arrive in.  The old code got
    # file order right by luck: 8 comes before 19.
    within = attempt("pair within the lists",
                     lambda: mirrors(twice, [{0, 1}, {2, 3}]), default={})
    ok("confined to a list, each copy pairs inside itself",
       {k: v[0] for k, v in within.items()} == {0: 1, 1: 0, 2: 3, 3: 2},
       "%s" % within)

    # The real file's own trap, in miniature: sections 7, 19, 8, 18 handed over
    # in that order.  7 and 18 are the same mesh, 8 and 19 are its mirror, and
    # the lists are {7, 8} and {18, 19} -- so a pairing that ignored the lists
    # would cross the two figures here.
    shuffled = [one, flip(2), flip(2), one]
    other = attempt("pair the same sections in another order",
                    lambda: mirrors(shuffled, [{0, 2}, {1, 3}]), default={})
    ok("and the answer does not depend on the order they arrive in",
       {k: v[0] for k, v in other.items()} == {0: 2, 2: 0, 1: 3, 3: 1},
       "%s" % other)

    # The chain is cut where the side flips, and the cut is what names the
    # pieces.  Driven with the real file's order, spelled out here so the rule
    # is exercised with no disc in sight.
    partner_of = {1: 2, 2: 1, 3: 4, 4: 3, 5: 6, 6: 5, 7: 8, 8: 7, 9: 10,
                  10: 9}
    order = [1, 3, 2, 4, 5, 7, 9, 6, 8, 10]
    ok("the chain cuts into four limbs",
       limbs(order, partner_of) == [[1, 3], [2, 4], [5, 7, 9], [6, 8, 10]],
       "%s" % limbs(order, partner_of))

    # Red: a section with no partner inside the tail is a second torso, and
    # the cut has nothing to go on.
    refuses("an unpaired section in the tail is refused",
            lambda: limbs([1, 3, 99], partner_of), "no mirror partner")

    # And the fourth witness has to be able to DISAGREE.  Driven against a
    # naming where the arms are swapped, which is exactly the mistake rule 2
    # would make on its own if the list ran distal to proximal.
    def naming(upper, fore):
        made = {}
        for index in (0, 11):
            made[index] = Piece(index, TORSO, None, [0], None, "t")
        for index in (5, 6, 16, 17):
            made[index] = Piece(index, THIGH, "a", [0], None, "t")
        for index in (7, 8, 18, 19):
            made[index] = Piece(index, SHIN, "a", [0], None, "s")
        for index in (9, 10):
            made[index] = Piece(index, FOOT, "a", [0, 1], None, "f")
        for index in (1, 2, 12, 13):
            made[index] = Piece(index, upper, "a", [0], None, "u")
        for index in (3, 4, 14, 15):
            made[index] = Piece(index, fore, "a", [0], None, "f")
        return made

    orders = {0: [0, 1, 3, 2, 4, 5, 7, 9, 6, 8, 10],
              1: [11, 12, 14, 13, 15, 16, 18, 9, 17, 19, 10]}
    ok("the game agrees with the naming",
       agrees_with_the_game(naming(UPPER_ARM, FOREARM), orders) == [],
       "%s" % agrees_with_the_game(naming(UPPER_ARM, FOREARM), orders))
    swapped = agrees_with_the_game(naming(FOREARM, UPPER_ARM), orders)
    ok("and disagrees when the two arm names are swapped", len(swapped) >= 2,
       "%s" % swapped)

    # And the BOOTS witness has to bite on its own.  Driven by moving the foot
    # name onto the shins, which is the mistake a chain read the wrong way
    # round would produce.
    mislaid = naming(UPPER_ARM, FOREARM)
    for index in (9, 10):
        mislaid[index] = Piece(index, SHIN, "a", [0, 1], None, "s")
    for index in (7, 8):
        mislaid[index] = Piece(index, FOOT, "a", [0], None, "f")
    boots = agrees_with_the_game(mislaid, orders)
    ok("and disagrees when the foot name is on the wrong section",
       any("BOOTS" in line for line in boots), "%s" % boots)

    # -- the two figures differ in mesh at the arms, and only there ---------
    #
    # Synthetic, because the gate has no disc: rows in the shape compare_lists
    # produces, and a naming to check them against.  The sentence this replaces
    # put the torso among the pieces of different size and generalised one
    # piece's two vertex bytes to all eleven (CORR-LOOKS-021); a computation
    # cannot drift that way, but only if something demands the two agree.
    named = naming(UPPER_ARM, FOREARM)

    def row(a, b, same_section=False, same_size=True):
        return {"position": 0, "a": a, "b": b, "same_section": same_section,
                "verts": (1, 1), "prims": (1, 1),
                "sizes": (100, 100 if same_size else 200),
                "differ": 3, "vertex_bytes": 1}

    real = [row(0, 11), row(1, 12, same_size=False),
            row(3, 14, same_size=False), row(5, 16), row(7, 18),
            row(9, 9, same_section=True)]
    ok("the arms differ in mesh and nothing else does",
       mesh_agrees(real, named) == [], "%s" % mesh_agrees(real, named))

    # Red, both ways round: a torso that differs, and an arm that does not.
    bad_torso = mesh_agrees([row(0, 11, same_size=False)], named)
    ok("a torso with a different mesh is a disagreement",
       len(bad_torso) == 2, "%s" % bad_torso)
    bad_arm = mesh_agrees([row(1, 12)], named)
    ok("and so is an arm with the same mesh", len(bad_arm) == 2,
       "%s" % bad_arm)

    # The head is not in this file, and saying so is the point of the constant.
    ok("the head is recorded as MODEL.BIN's section, not EDT_MOD.BIN's",
       HEAD_SECTION == 24 and HEAD not in (TORSO, UPPER_ARM, FOREARM))

    ok("every chain name is distinct",
       len(set(ARM_CHAIN + LEG_CHAIN)) == len(ARM_CHAIN) + len(LEG_CHAIN))


# --- entry point -----------------------------------------------------------

def main(argv):
    if len(argv) == 2 and argv[1] == "--check":
        return self_check()
    if len(argv) == 3 and argv[1] == "--check-image":
        return _check_image(argv[2])
    if len(argv) == 2 and argv[1] == "--check-image":
        import iso_source

        try:
            image = iso_source.image_from_env()
        except RuntimeError as exc:
            print("pieces --check-image: skipped -- %s" % exc)
            return 77
        return _check_image(image)
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

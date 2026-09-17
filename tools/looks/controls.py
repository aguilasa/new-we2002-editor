#!/usr/bin/env python3
"""The negative controls, planted by command instead of described in prose.

Provenance (plan section 3.4): none of the four columns.  This module knows
nothing about a disc.  It knows how to break the reader on purpose.

*A guard that has never gone red is decoration.*  Section 5.5 names the first
controls, and the reason they are a COMMAND and not a table in a task log is
measured in the .mcr cycle: two of five counts did not reproduce from prose,
because "swap two fields in the encoder" has more than one reading and a line
that appears twice needs its function named to be found at all.  The repository
already applies the opposite rule to the golden tests -- `tools/par/` keeps the
edit script, because without a versioned stimulus a green run is not
repeatable.

Each control is a LITERAL SUBSTITUTION: a file, the function it lives in, the
exact source line, and what it becomes.  The engine copies the tree into a
sandbox, substitutes, and demands the named modules go red.  A substitution
matching zero times or more than once is a BROKEN control, not a red one -- a
literal that does not match leaves the copy intact and the run comes out green
for the wrong reason.

Usage:
    python tools/looks/controls.py
    python tools/looks/controls.py --list
    python tools/looks/controls.py --only section-primitive-size
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import shutil
import subprocess
import sys
import tempfile

LOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(LOOKS_DIR)


@dataclasses.dataclass(frozen=True)
class Control:
    """One planted defect, and the modules whose self-check must go red."""

    id: str
    module: str
    function: str
    old: str
    new: str
    expect_red: tuple
    why: str


CONTROLS = (
    Control(
        "section-primitive-size", "section.py", "module constant",
        "PRIMITIVE_SIZE = 24",
        "PRIMITIVE_SIZE = 20",
        ("section", "modelfile"),
        "the 24 the whole format hangs on; section 5.5 names it first",
    ),
    Control(
        "section-gap-fixed", "section.py", "skip_gap",
        "    while offset + 4 <= len(data):",
        "    for _once in range(2):",
        ("section", "modelfile"),
        "the gap is a RUN of zero words; a fixed eight bytes lands 4 bytes "
        "inside EDT_MOD.BIN's next header",
    ),
    Control(
        "section-separator-is-eof", "section.py", "walk",
        "        if is_separator(data, offset):",
        "        if False:",
        ("section",),
        "treating 0/0 as end-of-file is the stop at section 55 that looked "
        "like a wrong format",
    ),
    Control(
        "modelfile-list-order", "modelfile.py", "read_models",
        "    for index, targets in enumerate(layout.record_lists(data)):",
        "    for index, targets in enumerate(sorted(map(sorted, layout.record_lists(data)))):",
        ("modelfile",),
        "list order is not file order; sorting shuffles a body with no visible "
        "symptom -- section 5.5's second control",
    ),
    Control(
        "layout-disc-guard", "layout.py", "require",
        "    if is_trusted(disc_path, got):",
        "    if True:",
        ("layout",),
        "the two-disc guard: with it open, a palette read off the English "
        "disc returns the wrong graphic and nothing says so",
    ),
    Control(
        "layout-empty-slot", "layout.py", "read_pointer_entries",
        "        if tag == 0 and pointer == 0:",
        "        if False:",
        ("layout",),
        "a (0, 0) pair is an empty slot; calling it malformed is what hid "
        "six of MODEL.BIN's eighteen lists",
    ),
    Control(
        "layout-sweep-blind", "layout.py", "sweep_addresses",
        "                findings.append((os.path.relpath(path, root), number, text.rstrip()))",
        "                pass",
        ("layout",),
        "rule 1's sweep reporting nothing is indistinguishable from a clean "
        "tree unless the sweep itself has a red case",
    ),
    Control(
        "harness-counts-nothing", "harness.py", "Checker.ok",
        "            self.fail(name, detail)",
        "            pass",
        ("harness",),
        "a blind ok() approves its own blindness; only the bare raise in "
        "harness._checks reaches a path ok() is not on",
    ),
    Control(
        "oracle-any-screen", "oracle.py", "module constant",
        "BADGE_TOL = 0.004",
        "BADGE_TOL = 0.5",
        ("oracle",),
        "with the plate's tolerance opened up, load_looks accepts the other "
        "state as the one it asked for -- and every later diff would then be "
        "measuring two players instead of one field",
    ),
    Control(
        "section-primitive-is-colours", "section.py", "read_primitive",
        '    clut = struct.unpack_from("<H", data, offset + CLUT_IN_PRIMITIVE)[0]',
        "    clut = data[offset + 3]",
        ("section",),
        "the reading this module carried until LOOKS-TASK-08: byte 3 as a mode "
        "byte instead of the high half of the CLUT id, which is the half of "
        "the claim that says where the texture comes from",
    ),
    Control(
        "oracle-session-never-renewed", "oracle.py", "OneSession.call",
        "            if SESSION_LOST not in str(exc):",
        "            if True:",
        ("oracle",),
        "a session taken by another client on the fork's port, not handshaken "
        "again: the run dies at its first call, red for no cause in the "
        "tool, and whoever reads it learns to rerun until green "
        "(CORR-LOOKS-051)",
    ),
    Control(
        "oracle-preflight-late", "oracle.py", "PREREQUISITES",
        '    ("image", image_to_read),',
        '    # ("image", image_to_read),',
        ("oracle",),
        "a prerequisite asked for at its point of use instead of in the "
        "preflight: --check-live booted the emulator and died in a traceback "
        "thirty seconds later, neither measuring nor skipping",
    ),
    Control(
        "pieces-mirror-x-only", "pieces.py", "mirror_axis",
        "    for axis in range(3):",
        "    for axis in range(1):",
        ("pieces",),
        "this model mirrors in z and x is the obvious guess; a search that "
        "only tries x finds no pair at all, and every name downstream rests "
        "on the pairs",
    ),
    Control(
        "pieces-witness-blind", "pieces.py", "agrees_with_the_game",
        "    problems = []",
        "    problems = []; return problems",
        ("pieces",),
        "the emulator is the only witness that tells the upper arm from the "
        "forearm; with it blind, a naming that swaps the two passes",
    ),
    Control(
        "oracle-list-walk-lax", "oracle.py", "walk_packets",
        "        if code not in GPU_COMMANDS or GPU_COMMANDS[code][1] != length:",
        "        if code not in GPU_COMMANDS:",
        ("oracle",),
        "the agreement between a node's declared length and its command's real "
        "length is what makes the walk evidence and not a byte histogram; "
        "without it any region with a 0x2C in it starts counting as drawn "
        "geometry",
    ),
    Control(
        "oracle-tmd-span-short", "oracle.py", "tmd_spans",
        "            if walked is not None:",
        "            if False:",
        ("oracle",),
        "a TMD span that stops before its variable-length primitives puts "
        "real bytes in the residue bucket, and the negative half of unknown "
        "(a) -- no field touches a TMD -- would then read zero for free",
    ),
    Control(
        "texture-bank-ignored", "texture.py", "Record.__init__",
        "        self.offset = fields[6] + bank * layout.RECORD_BANK",
        "        self.offset = fields[6]",
        ("texture",),
        "field 7 is the 64 KiB bank of a 16-bit offset, not a tag; with it "
        "dropped every palette of DAT2D.BIN is read 65,536 bytes early -- "
        "inside the compressed images, where the bytes are still bytes and "
        "still make colours",
    ),
    Control(
        "texture-clut-any-record", "texture.py", "covering",
        "    hits = [r for r in records if r.is_clut and r.covers(x, y, colours)]",
        "    hits = [r for r in records if r.is_clut]",
        ("texture",),
        "this is the swap the task asks for: with the span ignored, every "
        "piece resolves to the first palette in the file, the render still "
        "draws, and the boots come out the colour of the skin",
    ),
    Control(
        "atlas-page-is-one-record", "atlas.py", "image_at",
        "        if rec.x <= x < rec.x + rec.w and rec.y <= y < rec.y + rec.h:",
        "        if rec.y <= y < rec.y + rec.h:",
        ("atlas",),
        "a 4-bit texture page is 256 texels wide and every image record of "
        "DAT2D.BIN is 128, so the page holds TWO of them; with the column "
        "ignored both halves resolve to the first record on the row, the hair "
        "and the bodies become the same sheet, and the CARP label that section "
        "1.8 disproved would read as confirmed",
    ),
    Control(
        "atlas-depth-fixed-at-four", "atlas.py", "texel",
        "    return (page_x + u // texels_per_unit(primitive.tpage_depth), page_y + v)",
        "    return (page_x + u // 4, page_y + v)",
        ("atlas",),
        "the page depth is the primitive's, not the image's, and at 8 bits a "
        "halfword is two texels and not four; fixing it at four puts the 1,039 "
        "kit primitives a whole page to the left, where DAT2D.BIN does have "
        "records -- so the sweep for what is missing comes back empty and the "
        "kits look like they live here",
    ),
    Control(
        "pieces-mirror-unconfined", "pieces.py", "mirrors",
        "                    if groups is None or _together(i, j, groups)]",
        "                    if True]",
        ("pieces",),
        "with the pairing free to look outside the figure's own list, four "
        "sections have two partners each and the left shin of one player "
        "mirrors the right shin of the OTHER -- which renames every limb",
    ),
    Control(
        "assembly-table-off-by-one", "assembly.py", "check_step",
        "    step = value - effect.field.bias",
        "    step = value - effect.field.bias + 1",
        ("assembly",),
        "the table shifted by one index, which is what the task asks for: the "
        "bottom of every field is the state the disc already holds, so a "
        "shifted table asks for an edit where the game asks for none -- and "
        "every piece still draws",
    ),
    Control(
        "assembly-effects-do-not-compose", "assembly.py", "combine",
        "        clut, band = apply_to(clut, band, effect, step)",
        "        clut, band = apply_to(primitive.clut, 0, effect, step)",
        ("assembly",),
        "each field applied to the DISC's value instead of the running one: "
        "six of the head's primitives are owned by two fields, so the second "
        "undoes the first and SKIN A to D comes out moving nothing",
    ),
    Control(
        "corpus-ties-to-palette", "corpus.py", "snapped_histogram",
        "                    if far is None or d < far:",
        "                    if far is None or d <= far:",
        ("corpus",),
        "a JPEG pixel exactly as near the background as a head colour is not "
        "evidence about the head; handing ties to the palette counts noise",
    ),
    Control(
        "corpus-beard-colour-always-seen", "corpus.py", "visible",
        "        return values[\"beard_style\"] != base",
        "        return True",
        ("corpus",),
        "with no beard the beard's quads sample none of the entries a beard "
        "colour moves (CORR-LOOKS-038); judging it there fails two renders "
        "for a colour that is not in the picture",
    ),
    Control(
        "corpus-shape-judged", "corpus.py", "field_failures",
        "            for field in COLOUR_FIELDS if verdicts[field] == \"DISAGREE\"]",
        "            for field in COLOUR_FIELDS + SHAPE_FIELDS if verdicts[field] == \"DISAGREE\"]",
        ("corpus",),
        "the emulator's own frames rank their true hair style third and "
        "fourth; judging shape by colour fails the metric, not the render",
    ),
    Control(
        "confront-margin-ignored", "confront.py", "verdict",
        "        if right - wrong >= MARGIN:",
        "        if right - wrong >= -1.0:",
        ("confront",),
        "a win by nothing is a coin toss; without the margin every tuple "
        "whose colours nearly match another's is called a hit",
    ),
    Control(
        "confront-tie-passes", "confront.py", "verdict",
        "        elif right > wrong and ceiling < 2 * MARGIN:",
        "        elif right >= wrong and ceiling < 2 * MARGIN:",
        ("confront",),
        "a tie between the right render and a wrong one is no verdict; "
        "letting it rank first calls a coincidence a hit",
    ),
    Control(
        "confront-background-counted", "confront.py", "histogram",
        "            if colour == drop:",
        "            if False:",
        ("confront",),
        "our render's background counted as a drawn colour dilutes every "
        "score by the same amount and makes the wrong tuples look close",
    ),
    Control(
        "confront-diagonal-any-clut", "confront.py", "diagonal",
        "        here = [p for c, p in packets if c == clut]",
        "        here = [p for c, p in packets]",
        ("confront",),
        "matching texcoords across every CLUT finds the hair's order in the "
        "face's packets, and the diagonal verdict reads somebody else's quad",
    ),
    Control(
        "confront-mask-sees-blink", "confront.py", "glyph_mask",
        "            if b >= GLYPH_BLUE and b > r:",
        "            if b >= GLYPH_BLUE or r >= GLYPH_BLUE:",
        ("confront",),
        "a mask that takes the yellow cursor box counts its blink as a value; "
        "that is how a seven-label row was counted as eight",
    ),
    Control(
        "confront-twins-vote", "confront.py", "diagonal",
        "        if by_set[(clut, frozenset(uvs))] > 1:",
        "        if False:",
        ("confront",),
        "two mirrored primitives share one set of texcoords, so one packet "
        "answers for both; letting each vote counts it twice, and one of the "
        "two votes is in the other order",
    ),
    Control(
        "scene-texel-in-halfwords", "scene.py", "local_texel",
        "    x = (page_x - record.x) * per + u",
        "    x = (page_x - record.x) + u",
        ("scene",),
        "the page offset counted in halfwords instead of texels: the picture "
        "stays seamless and samples a quarter of the sheet",
    ),
    Control(
        "scene-up-is-down", "scene.py", "module constant",
        "UP = -1",
        "UP = 1",
        ("scene",),
        "the model's y grows downward; with the flip gone the figure draws "
        "upside down and every part still looks like a part",
    ),
    Control(
        "scene-shelf-stacks", "scene.py", "shelf",
        "        at += (high_x - low_x) + SHELF_GAP",
        "        at += 0.0",
        ("scene",),
        "the shelf exists because the files carry no placement; with the step "
        "gone every piece lands on the origin, which is the pile this task "
        "measured and named",
    ),
    Control(
        "texture-window-at-record-start", "texture.py", "window_for",
        "    return (record, x - record.x)",
        "    return (record, 0)",
        ("texture", "scene"),
        "a 4-bit id inside a 256-entry record names one of sixteen windows; "
        "reading from the record's start returns window zero -- sixteen "
        "colours that draw perfectly and are somebody else's",
    ),
    Control(
        "assembly-hair-quads-guessed", "layout.py", "module constant",
        "    24: (1, 14),",
        "    24: (1, 15),",
        ("assembly",),
        "one of the four quad pairs the breakpoint named replaced by its "
        "neighbour: the band would land on a primitive the game never writes, "
        "and the head would draw with a stripe of somebody else's hair",
    ),
    Control(
        "assembly-hair-map-defaults", "assembly.py", "head_of",
        "    if found is None:",
        "    if found is None and False:",
        ("assembly",),
        "the three styles the map could not place handed back family A's head "
        "instead of a refusal: each of them would draw perfectly, wearing "
        "somebody else's hair",
    ),
    Control(
        "assembly-hair-map-is-one-section", "assembly.py", "module constant",
        "    (34, (0,)), (34, (2,)), (34, (1,)),",
        "    (34, (0,)), (36, (2,)), (34, (1,)),",
        ("assembly",),
        "one variant of a letter moved into its neighbour's section -- what "
        "the walk measured is that a letter IS a section, and a table that "
        "does not hold that is a table nobody measured",
    ),
    Control(
        "looks-cross-check-blind", "looks.py", "disagreements",
        "            if theirs != mine:",
        "            if False:",
        ("looks",),
        "the cross-check against src/core/Player.cpp is the whole evidence "
        "that this codec is the one ed.exe is measured against; unable to "
        "disagree, it approves any mask at all",
    ),
    Control(
        "looks-record-count", "layout.py", "module constant",
        "PLAYER_RECORD_COUNT = 1449",
        "PLAYER_RECORD_COUNT = 1242",
        ("looks",),
        "the third party's count, which was short by 207: with it the block "
        "stops inside the players and every later coverage figure is taken "
        "over six sevenths of the disc's squad",
    ),
    Control(
        "skin-matrix-at-the-record", "layout.py", "module constant",
        "HAIR_MATRIX_FIRST = 65924",
        "HAIR_MATRIX_FIRST = 65892",
        ("skin",),
        "section 5.5's third control -- one palette for another -- in the "
        "exact shape it nearly took: the hair colours start one 16-entry "
        "window PAST the skin record, and starting at the record itself gives "
        "type A the bare-skin window and every other type its neighbour's.  "
        "LOOKS-TASK-12's own criterion wrote the matrix this way",
    ),
    Control(
        "skin-window-unaligned-ok", "skin.py", "column_of",
        "    if inside % (texture.NARROW * 2):",
        "    if False:",
        ("skin",),
        "an offset that is not a whole window rounded down instead of "
        "refused: the sixteen entries it returns straddle two colours, and "
        "they still draw",
    ),
    Control(
        "confront-render-keeps-refusal", "confront.py", "render_ours",
        "            for stale in (path, path + REFUSED):",
        "            for stale in (path,):",
        ("confront",),
        "the re-render back to removing only the PNG: a tuple that refused "
        "last time and draws now keeps its old refusal beside the new picture, "
        "and the score drops from the matrix the tuple a measurement just "
        "unlocked -- green, over a tuple it never judged (CORR-LOOKS-046)",
    ),
    Control(
        "confront-score-prefers-refusal", "confront.py", "ours_side",
        "    if drawn and refused:",
        "    if False:",
        ("confront",),
        "a picture beside a refusal read as the refusal: the same silent skip, "
        "reached from a directory some other hand left mixed",
    ),
    Control(
        "pieces-mesh-check-blind", "pieces.py", "mesh_agrees",
        "            if differs and name not in ARM_CHAIN:",
        "            if False:",
        ("pieces",),
        "with the mesh comparison unable to disagree, 'same mesh, different "
        "kit' can be written about all eleven pieces again -- and a renderer "
        "reading that draws the goalkeeper with the outfield player's arm",
    ),
    Control(
        "skin-union-of-one-field", "skin.py", "moved_by_colour",
        "        out |= set(field.primitives or ())",
        "        out = set(field.primitives or ())",
        ("skin",),
        "the union of the three colour fields taken as the last one's list: "
        "with it, nothing says which of the head's primitives keep the pale "
        "skin's window whatever the screen says -- four of section 24's "
        "eighteen since CORR-LOOKS-049, nine as CORR-LOOKS-026 first read it",
    ),
    Control(
        "confront-ranked-ignores-ceiling", "confront.py", "verdict",
        "        elif right > wrong and ceiling < 2 * MARGIN:",
        "        elif right > wrong:",
        ("confront",),
        "the ranked verdict back to any lead above zero: a lead of 0.001 "
        "under a ceiling of 0.5 passes, and prints the 0.5 that says it "
        "should not have -- the case confront-margin-ignored does not reach, "
        "because that one turns losses into wins and reddens for that",
    ),
    Control(
        "assembly-unmeasured-as-unreached", "assembly.py", "check_step",
        "    if step >= effect.known:",
        "    if False:",
        ("assembly",),
        "a value the screen offers and nobody measured, applied anyway: F and "
        "G on FACE became bands 5 and 6 of a sheet whose beard bands stop at "
        "4, and the figure drew a beard nobody had seen -- which is how they "
        "were before CORR-LOOKS-048 measured the twin",
    ),
    Control(
        "assembly-face-twin-ignored", "assembly.py", "worn_head",
        "    drawn = twin_of(chosen, figure) if wears_twin(values) else chosen",
        "    drawn = chosen",
        ("assembly",),
        "beard F and G drawn on the head HAIR picked instead of its twin: the "
        "even section's beard quads get the twin's band, a head the game never "
        "shows for F or G, drawing perfectly (CORR-LOOKS-048)",
    ),
    Control(
        "assembly-goalkeeper-unmapped", "assembly.py", "HAIR_MAPS",
        "    1: HAIR_MAP_GOALKEEPER,",
        "",
        ("assembly",),
        "figure 1 back to having no map: every goalkeeper refuses, I3 "
        "included, which is where CORR-LOOKS-043 left it and 136 of the "
        "disc's 179 goalkeepers with it -- the walk on slot 1 is what took "
        "them back (CORR-LOOKS-047)",
    ),
    Control(
        "assembly-hair-v-from-disc", "assembly.py", "hair_texcoords",
        "    return tuple((u, rows + row)",
        "    return tuple((u, rows + _v)",
        ("assembly",),
        "the hair quad drawn from the file's v plus the band, instead of the "
        "absolute rows the game's store writes: every hair quad a texel row "
        "off, on all four heads whose quads are known, and the picture looks "
        "fine",
    ),
    Control(
        "ui-whole-figure-unjudged", "ui_check.py", "judge_whole",
        "        if counts.get(name, 0) < floor:",
        "        if False:",
        ("ui_check",),
        "the counts app.py --smoke prints, read and then not judged: the "
        "colour pairs draw --piece head, so with this blind a figure missing "
        "eleven of its twelve pieces passes the gate that is the only one to "
        "put the window up",
    ),
    Control(
        "scene-texel-window-ignored", "scene.py", "indices_in_quad",
        "    points = [local_texel(primitive, record, u, v + band)",
        "    points = [local_texel(primitive, record, u, v)",
        ("scene",),
        "the band dropped when reading which indices a quad samples: every "
        "FACE band then reports band 0's texels, the beardless face, and the "
        "measurement that says H.F.COL. paints nothing there -- and paints on "
        "the other four -- comes back saying it paints nowhere",
    ),
    Control(
        "assembly-colour-stays-on-24", "assembly.py", "edits",
        "                key = where_head",
        "                key = HEAD",
        ("assembly",),
        "the colour rows addressed to the head they were MEASURED on instead "
        "of the head the tuple wears: for the 29 styles that are not an A the "
        "plan comes back empty, and SKIN, H.COL, H.F.COL. and FACE move "
        "nothing while the figure draws perfectly",
    ),
    Control(
        "assembly-colour-borrowed-from-24", "assembly.py", "colour_primitives",
        "    return table[head]",
        "    return table[layout.HEAD_SECTION]",
        ("assembly",),
        "section 24's indices applied to every head, which is what the corpus "
        "measured: a skin that is not A on the forehead only, and the beard "
        "missing, on twelve heads drawing perfectly (CORR-LOOKS-049)",
    ),
    Control(
        "assembly-plan-key-drops-a-row", "assembly.py", "edits",
        "            out[key][(effect.row, primitives)] = (effect, step)",
        "            out[key][primitives] = (effect, step)",
        ("assembly",),
        "the plan keyed by primitives alone: H.F.COL. and FACE both own the "
        "beard's two, so the second replaces the first and the beard colour "
        "moves nothing on any head at all",
    ),
    Control(
        "assembly-band-choice-silent", "assembly.py", "unmeasured_bands",
        "    if not layout.HAIR_QUADS.get(chosen) or len(bands) < 2:",
        "    if True:",
        ("assembly",),
        "the band dropped when a style landed in two: with nothing reporting "
        "it, B1 draws with bands[0] and the draw list says `band +0` like "
        "every other line -- a pairing nobody measured, wearing the look of "
        "one that was",
    ),
    Control(
        "corpus-groups-unjudged", "corpus.py", "group_failures",
        "        if sum(values) / len(values) < floors[key]:",
        "        if False:",
        ("corpus",),
        "the self-score groups printed and never judged: skin_colour 47/47 "
        "passes beside twelve skins drawn on the forehead only, and the "
        "corpus run says ok over the error it exists to find (CORR-LOOKS-050)",
    ),
    Control(
        "corpus-residue-never-expires", "corpus.py", "group_failures",
        "        if key not in outliers:",
        "        if False:",
        ("corpus",),
        "a residue that keeps exempting its group after the group recovered: "
        "the exemption outlives the fix, and a later regression of that group "
        "comes back green -- a hole with a date",
    ),
    Control(
        "looks-tuple-any-length", "looks.py", "parse_tuple",
        "    if len(parts) != len(TUPLE_ORDER):",
        "    if False:",
        ("looks",),
        "a parser that takes any number of parts: the corpus survey then "
        "reports 50 of 50 parsed and 0 refused, which reads BETTER than the "
        "true line -- the exact shape of green-for-the-wrong-reason this "
        "cycle keeps meeting",
    ),
    Control(
        "cli-check-forgets-a-module", "cli.py", "module constant",
        "    \"scene\",\n)",
        ")",
        ("cli",),
        "the disc gate running seven of the eight --check-image: green, and "
        "blind to the one left out -- the shape looks_image had for five "
        "tasks, when it ran modelfile alone",
    ),
    Control(
        "cli-guard-read-left-out", "cli.py", "module constant",
        "    \"modelfile\",\n",
        "",
        ("cli",),
        "modelfile out of the check: the Japanese-only read through the guard "
        "leaves the image gate, and pointed at the English disc the run leans "
        "on the others to notice. Its POSITION in the list was guarded here "
        "until CORR-LOOKS-052, and moving it changes no verdict",
    ),
    Control(
        "cli-partial-skip-passes", "cli.py", "combine",
        "    if all(code == 0 for code in codes):",
        "    if all(code in (0, SKIP) for code in codes):",
        ("cli",),
        "a module skipping while the others ran means it lacks something the "
        "rest have; calling that green passes a gate that measured less than "
        "it says",
    ),
    Control(
        "screen-skips-unknown-control", "screen.py", "decode",
        "            raise BadScreen(\"byte %#04x at %d of %r is not a character and not \"",
        "            at += 1\n            continue\n            raise BadScreen(\"byte %#04x at %d of %r is not a character and not \"",
        ("screen",),
        "a decoder that steps over a byte it does not know: the value block "
        "still decodes, and a code the screen has not shown yet turns into a "
        "letter missing from the text with nothing to say so",
    ),
    Control(
        "screen-help-not-a-witness", "screen.py", "validate",
        "    if len(set(helps)) != len(helps):",
        "    if False:",
        ("screen",),
        "two rows sharing a help pass: the help is what the walk reads to know "
        "which row the cursor is on, so a shared one lets a Down that did not "
        "register measure the neighbouring row under this row's name",
    ),
    Control(
        "screen-glyph-keeps-measuring-pass", "screen.py", "glyph_strings",
        "        if measuring:\n            current = None\n            continue\n",
        "        if measuring:\n            current = None\n",
        ("screen",),
        "the width-measuring pass kept as if drawn: every word comes out twice "
        "at one x, and the control that checks decoding against the glyphs "
        "would be comparing against a text the screen never shows",
    ),
)

BY_ID = {c.id: c for c in CONTROLS}


@dataclasses.dataclass
class Result:
    control: Control
    matched: int
    red: list
    green: list

    @property
    def good(self) -> bool:
        return self.matched == 1 and not self.green


def _sandbox(tmp: str) -> str:
    """A copy of tools/looks plus the one tree its modules reach for.

    `tools/pes2/` comes along because iso_source.py wraps its ISO reader, and
    a sandbox without it would fail to import for a reason that has nothing to
    do with the planted defect -- a red for the wrong cause is as useless as a
    green for the wrong cause.
    """
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    shutil.copytree(LOOKS_DIR, os.path.join(tmp, "tools", "looks"),
                    ignore=ignore)
    pes2 = os.path.join(TOOLS_DIR, "pes2")
    if os.path.isdir(pes2):
        shutil.copytree(pes2, os.path.join(tmp, "tools", "pes2"), ignore=ignore)
    return os.path.join(tmp, "tools", "looks")


def plant(control: Control) -> Result:
    """Copy the tree, substitute once, and run the modules that must fail."""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = _sandbox(tmp)
        path = os.path.join(sandbox, control.module)
        with open(path, encoding="utf-8") as handle:
            text = handle.read()

        matched = text.count(control.old)
        if matched == 1:
            with open(path, "w", encoding="utf-8", newline="") as handle:
                handle.write(text.replace(control.old, control.new))

        env = dict(os.environ, PYTHONPATH=sandbox)
        # The image variable is dropped: a control must be judged by what the
        # substitution did, not by whether this machine has a disc.
        env.pop("WE2002_LOOKS_IMAGE", None)

        red, green = [], []
        for module in control.expect_red:
            proc = subprocess.run(
                [sys.executable, os.path.join(sandbox, module + ".py"),
                 "--check"],
                env=env, capture_output=True, text=True, cwd=sandbox)
            (red if proc.returncode else green).append(module)
        return Result(control, matched, red, green)


def run_all(only: str | None = None, verbose: bool = True) -> list:
    wanted = [BY_ID[only]] if only else list(CONTROLS)
    out = []
    for control in wanted:
        result = plant(control)
        out.append(result)
        if verbose:
            mark = "RED  " if result.good else "GREEN"
            note = ""
            if result.matched != 1:
                note = "  -- BROKEN CONTROL: matched %dx" % result.matched
            elif result.green:
                note = "  -- did NOT go red: %s" % ", ".join(result.green)
            print("  %s  %-26s %s :: %s%s"
                  % (mark, control.id, control.module, control.function, note))
    if verbose:
        good = sum(1 for r in out if r.good)
        # REPORTED, never written in prose.  A count that lives as a number in
        # a document is a count that disagrees with the tool the first time
        # somebody adds one.
        print("controls: %d of %d red (%d substitution%s)"
              % (good, len(out), len(out), "" if len(out) == 1 else "s"))
    return out


# --- self-check ------------------------------------------------------------

def _checks(c) -> None:
    ok = c.ok

    ok("every control has a distinct id", len(BY_ID) == len(CONTROLS))
    ok("every control names at least one module to go red",
       all(one.expect_red for one in CONTROLS))
    ok("every control says why it exists", all(one.why for one in CONTROLS))
    ok("no control replaces a line with itself",
       all(one.old != one.new for one in CONTROLS))

    # The literal has to be findable in the live tree, and findable ONCE.
    # This is the cheap half of "a broken control is not a red one": it costs
    # no sandbox and catches the substitution that rotted when a module was
    # edited, which is the way these decay.
    for control in CONTROLS:
        path = os.path.join(LOOKS_DIR, control.module)
        if not os.path.isfile(path):
            c.fail("%s: %s does not exist" % (control.id, control.module))
            continue
        with open(path, encoding="utf-8") as handle:
            hits = handle.read().count(control.old)
        ok("%s matches exactly once in %s" % (control.id, control.module),
           hits == 1, "matched %d time(s)" % hits)


def self_check(verbose: bool = True) -> int:
    import harness
    return harness.run("controls.py", _checks, verbose)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--only")
    parser.add_argument("--check", action="store_true",
                        help="check the catalogue without planting anything")
    args = parser.parse_args(argv)

    if args.check:
        return 1 if self_check() else 0
    if args.list:
        for control in CONTROLS:
            print("  %-26s %s :: %s" % (control.id, control.module,
                                        control.function))
            print("      %s" % control.why)
        print("controls: %d catalogued" % len(CONTROLS))
        return 0

    results = run_all(args.only)
    return 0 if all(r.good for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

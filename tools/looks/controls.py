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
        "assembly-table-off-by-one", "assembly.py", "edits",
        "        step = values[name] - effect.field.bias",
        "        step = values[name] - effect.field.bias + 1",
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
        "with it, nothing says nine of the head's eighteen primitives keep "
        "the pale skin's window whatever the screen says, and the nine that "
        "are not skin go back to being invisible -- which is the state "
        "CORR-LOOKS-026 found",
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

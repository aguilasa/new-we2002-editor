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
        '    clut = struct.unpack_from("<H", data, offset + 2)[0]',
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
        "pieces-mirror-unconfined", "pieces.py", "mirrors",
        "                    if groups is None or _together(i, j, groups)]",
        "                    if True]",
        ("pieces",),
        "with the pairing free to look outside the figure's own list, four "
        "sections have two partners each and the left shin of one player "
        "mirrors the right shin of the OTHER -- which renames every limb",
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

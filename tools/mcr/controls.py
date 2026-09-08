#!/usr/bin/env python3
"""The negative controls, planted by command instead of described in prose.

Provenance (section 3.4 of the plan): none of the four columns -- this module
knows nothing about the card. It knows how to break the port on purpose.

WHY THIS IS A COMMAND. Until now the stimulus of every negative control lived
as prose in a table in a task log, and CORR-MCR-009 measured what that costs:
two of the five counts of MCR-TASK-06 did not reproduce from the description,
because "swap two fields in the encoder" has more than one reading, and a line
that appears twice in a file needs its function to be identified at all. The
repository already applies the opposite rule to the golden tests -- `tools/par/`
keeps the edit script, because without a versioned stimulus a green run is not
repeatable. This is that rule, for the controls.

Each control is a LITERAL SUBSTITUTION: a file, the function it lives in, the
exact source line, and what it becomes. The engine copies the tree into a
sandbox, substitutes, and demands the named modules go red. A substitution that
matches zero times, or more than once, is reported as a broken control and not
as a red one -- a literal that does not match leaves the copy intact and the
run comes out green for the wrong reason.

TWO THINGS THE SANDBOX MUST CARRY, both measured in MCR-TASK-08: `wte/re/mcr.md`
and the upstream clone. Without them the checks that would catch the defect
SKIP, the module reports zero failures, and "0 failure(s)" reads as approval.
Matching the substitution is not enough -- the check the defect should trip has
to have run.

Usage:

    python3 tools/mcr/controls.py            # plant all of them
    python3 tools/mcr/controls.py --list
    python3 tools/mcr/controls.py --only card-write-guard
"""

import argparse
import dataclasses
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout                                            # noqa: E402

MCR_DIR = os.path.dirname(os.path.abspath(__file__))


@dataclasses.dataclass(frozen=True)
class Control:
    """One planted defect, and the modules whose self-check must go red."""

    id: str
    module: str
    function: str
    old: str
    new: str
    expect_red: tuple[str, ...]
    why: str
    creates: bool = False
    """`module` is a file that does NOT exist, and `new` is its whole content.

    One control needs this: the defect is a file appearing in a directory the
    sweep does not descend into, and no substitution in an existing module can
    express that. `old` stays empty, and "matched once" means the path was free
    and got written -- a path that already exists is a BROKEN control, exactly
    as a literal matching twice is.
    """


def _ui_probe() -> str:
    """The content of the file the descent control plants.

    THE WORDS COME FROM THE DICTIONARY, not from literals here. Written out,
    the two Spanish nouns would make THIS file trip the very sweep the control
    exists to exercise -- measured, two complaints on `controls.py` itself. The
    alternative, skipping `controls.py` the way `glossary.py` skips itself,
    would leave a real leak in the catalogue unwatched. Reading the live
    dictionary also keeps the control planting something the sweep must catch
    if the dictionary is ever rewritten. The accented vowel is an escape for
    the same reason: an escape in the source, the letter in the file written.
    """
    import glossary
    player = next(k for k, v in glossary.SPANISH.items() if v == "player")
    pitch = next(k for k, v in glossary.SPANISH.items() if v == "pitch")
    return (f"# el {player} y su posici\u00f3n en la {pitch}\n"
            f"{player.upper()}_X = 0x62A8\n"
            f"{pitch.upper()}_Y = 25266\n")


CONTROLS = (
    Control("card-write-guard", "card.py", "Card.write",
            "        if offset < HEADER_BYTES:", "        if False:",
            ("card",),
            "the refusal below the directory -- what the upstream does"),
    Control("card-size-guard", "card.py", "Card.__init__",
            "        if len(data) != CARD_BYTES:", "        if False:",
            ("card",),
            "the size validation; a truncated card must not be opened"),
    Control("card-link-base", "card.py", "DirectoryEntry.next_frame",
            "        return self.link + 1", "        return self.link",
            ("card",),
            "the link is 0-based over the data blocks, not a frame number"),
    Control("attributes-bit-write", "attributes.py", "encode_stream",
            "        _write_bits(out, f.offset, f.width, raw)",
            "        _write_bits(out, f.offset, f.width, raw ^ 1)",
            ("attributes",),
            "the stream encoder against the Player.cpp masks"),
    Control("numbers-bias", "numbers.py", "encode_table",
            "        stored = number - STORED_BIAS", "        stored = number",
            ("numbers",),
            "the -1 the card stores; the cross-check of the two copies"),
    Control("text-interior-nul", "text.py", "decode_name",
            "    trimmed = raw.rstrip(bytes([PAD]))",
            "    trimmed = raw.split(bytes([PAD]))[0]",
            ("text",),
            "stopping at the first NUL loses what comes after it"),
    Control("formation-screen-factor", "formation.py", "write",
            "    card.write(layout.FORMATION_XY.address, bytes(f.x) + bytes(f.y))",
            "    card.write(layout.FORMATION_XY.address,\n"
            "               bytes(v * 7 for v in f.x) + bytes(f.y))",
            ("formation",),
            "X*7 is a screen factor; in the core it kills the round-trip"),
    Control("domains-invented-label", "domains.py", "HAIR_STYLE",
            'HAIR_STYLE = ("a1", "a2", "a3", "b1", "b2", "b3", "b4", "b5", "b6", "c1",',
            'HAIR_STYLE = ("zz", "a2", "a3", "b1", "b2", "b3", "b4", "b5", "b6", "c1",',
            ("domains",),
            "a third party's table is copied, not inferred"),
    Control("layout-stray-address", "formation.py", "module scope",
            "OUTFIELD = layout.OUTFIELD_COUNT      # 10 -- the goalkeeper has no X/Y here",
            "OUTFIELD = layout.OUTFIELD_COUNT      # 10\nSNEAKY = 0x62A8",
            ("layout",),
            "Rule 1: only layout.py carries an address"),
    Control("model-write-nobody", "model.py", "Save.write",
            "        for i in range(SQUAD_SIZE):", "        for i in range(0):",
            ("model", "mcrio"),
            "a writer that writes nobody leaves every round-trip check green"),
    Control("model-half-number", "model.py", "Player.set_number",
            "        self.shirt_number = number", "        pass",
            ("model",),
            "the shirt number is stored twice and both copies must move"),
    Control("mcrio-directory-guard", "mcrio.py", "check_card",
            "    if found is None:", "    if False:",
            ("mcrio",),
            "a save entry marked free is not a save"),
    Control("mcrio-readonly-guard", "mcrio.py", "check_destination",
            "    if READ_ONLY_DIR in parts:", "    if False:",
            ("mcrio",),
            "roms/ is never a tool's target"),
    Control("harness-counts-nothing", "harness.py", "Checker.ok",
            "            self.fail(name, detail)", "            pass",
            ("harness",),
            "if a false check counts as a pass, EVERY module reports zero"),
    Control("ui-imports-an-address", os.path.join("ui", "main_window.py"),
            "module scope",
            "import model                                             # noqa: E402",
            "import model                                             # noqa: E402\n"
            "import mcrio                                             # noqa: E402",
            ("selftest",),
            "Rule 3: the window may not reach a module that knows an address"),
    Control("formation-captain-not-written", "formation.py", "write",
            "    card.write(layout.CAPTAIN.address, bytes([f.captain]))",
            "    pass",
            ("formation",),
            "the captain was read and never written until MCR-TASK-13 "
            "measured what it is; a writer that skips one field leaves every "
            "round-trip check green"),
    Control("ui-writes-from-two-places", os.path.join("ui", "squad_view.py"),
            "SquadView._select",
            "        self.form.show_player(self._save.players[row])",
            "        self.form.show_player(self._save.players[row])\n"
            "        model.store(self._save, \"autosave.mcr\")",
            ("selftest",),
            "the UI has one write door; a second one is how a screen writes "
            "a card nobody asked it to"),
    Control("model-store-skips-the-model", "model.py", "store",
            "    return mcrio.store(save, path, force=force)",
            "    return mcrio.write_card(save.card, path, force=force)",
            ("model",),
            "a write door that does not flush the model writes a file with "
            "none of the edits in it"),
    Control("mcrio-copy-target-is-the-original", "mcrio.py", "copy_target",
            "    if base.endswith(EDITED_SUFFIX):", "    if True:",
            ("mcrio",),
            "the default destination is a copy; the card that was opened is "
            "never written without being asked for"),
    Control("ui-below-the-sweep", os.path.join("ui", "_probe.py"),
            "a new file, one directory down", "",
            _ui_probe(),
            ("layout", "glossary"),
            "both sweeps have to DESCEND: ui/ is where the upstream's WinForms "
            "is transcribed, and it is a directory",
            creates=True),
)

# ONE CONTROL OF THIS CYCLE DOES NOT LIVE HERE, and saying so is the point.
# The drag's way back from pitch pixels to the card's units -- `to_card_x` and
# `to_card_y` of `ui/formation_view.py` -- is planted by `ui_check.py` instead
# (its `BREAKS`), in the same literal-substitution form. The engine below runs
# `<module>.py --self-check` under whatever interpreter started it, and the
# module that catches that defect needs PySide6, the venv and a display; a
# control here would plant it and measure nothing. CORR-MCR-018 is where that
# gap was found, by planting it and watching every gate stay green.
BY_ID = {c.id: c for c in CONTROLS}


def _repo_root() -> str | None:
    wte = layout.find_upward("wte")
    return os.path.dirname(wte) if wte else None


def _sandbox(root: str, tmp: str) -> str:
    """A copy of the tree with what the modules reach for outside it."""
    shutil.copytree(MCR_DIR, os.path.join(tmp, "tools", "mcr"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    if root:
        measurement = os.path.join(root, "wte", "re", "mcr.md")
        if os.path.isfile(measurement):
            os.makedirs(os.path.join(tmp, "wte", "re"), exist_ok=True)
            shutil.copy(measurement, os.path.join(tmp, "wte", "re", "mcr.md"))
        clone = os.path.join(root, "work", "easy-mcr")
        if os.path.isdir(clone):
            os.makedirs(os.path.join(tmp, "work"), exist_ok=True)
            os.symlink(clone, os.path.join(tmp, "work", "easy-mcr"))
    return os.path.join(tmp, "tools", "mcr")


@dataclasses.dataclass
class Result:
    control: Control
    matched: int
    red: list[str]
    green: list[str]
    skipped_checks: dict[str, int]

    @property
    def good(self) -> bool:
        return self.matched == 1 and not self.green


def plant(control: Control, card_path: str | None = None) -> Result:
    """Copies the tree, substitutes once, and runs the modules that must fail."""
    root = _repo_root()
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = _sandbox(root, tmp)
        path = os.path.join(sandbox, control.module)
        if control.creates:
            matched = 0 if os.path.exists(path) else 1
            if matched == 1:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(control.new)
        else:
            with open(path) as fh:
                text = fh.read()
            matched = text.count(control.old)
            if matched == 1:
                with open(path, "w") as fh:
                    fh.write(text.replace(control.old, control.new))
        env = dict(os.environ, PYTHONPATH=sandbox)
        if card_path:
            env["WE2002_MCR_CARD"] = card_path
        red, green, skipped = [], [], {}
        for module in control.expect_red:
            proc = subprocess.run(
                [sys.executable, os.path.join(sandbox, module + ".py"),
                 "--self-check"],
                env=env, capture_output=True, text=True)
            (red if proc.returncode else green).append(module)
            n = sum(1 for line in proc.stdout.splitlines()
                    if line.startswith("  skip"))
            if n:
                skipped[module] = n
        return Result(control, matched, red, green, skipped)


def run_all(only: str | None = None, card_path: str | None = None,
            verbose: bool = True) -> list[Result]:
    wanted = [BY_ID[only]] if only else list(CONTROLS)
    out = []
    for control in wanted:
        r = plant(control, card_path)
        out.append(r)
        if verbose:
            mark = "RED  " if r.good else "GREEN"
            note = ""
            if r.matched != 1:
                note = f"  -- BROKEN CONTROL: matched {r.matched}x"
            elif r.green:
                note = f"  -- did NOT go red: {', '.join(r.green)}"
            elif r.skipped_checks:
                note = f"  (skips: {r.skipped_checks})"
            print(f"  {mark}  {control.id:<26} {control.module} :: "
                  f"{control.function}{note}")
    if verbose:
        good = sum(1 for r in out if r.good)
        # The breakdown by kind is REPORTED, not asserted in prose somewhere
        # else: CORR-MCR-017 measured what the other way costs. The total lived
        # as a number in perfil-mcr.md, MCR-TASK-11 added the sixteenth, and
        # the file the commands read before running anything still said
        # fifteen -- while progresso.md, edited by the same task, said sixteen.
        # Same choice as --edit-probe in MCR-TASK-09: report it, do not claim it.
        made = sum(1 for r in out if r.control.creates)
        subs = len(out) - made
        print(f"controls: {good} of {len(out)} red "
              f"({subs} substitution{'' if subs == 1 else 's'}, "
              f"{made} new file{'' if made == 1 else 's'})")
    return out


# --- self-check ------------------------------------------------------------

def _checks(c) -> None:
    ok = c.ok

    ok("every control has a unique id", len(BY_ID) == len(CONTROLS))
    subs = [k for k in CONTROLS if not k.creates]
    ok("every control names a module that exists",
       all(os.path.isfile(os.path.join(MCR_DIR, k.module)) for k in subs))
    ok("every substitution matches exactly once in the real tree",
       all(open(os.path.join(MCR_DIR, k.module)).read().count(k.old) == 1
           for k in subs),
       str([k.id for k in subs
            if open(os.path.join(MCR_DIR, k.module)).read().count(k.old) != 1]))
    ok("no substitution is a no-op", all(k.old != k.new for k in subs))
    # The creating control is the mirror image: its path must be FREE, or the
    # plant would overwrite somebody's file and the run would measure that.
    ok("every creating control names a path that is free",
       all(not os.path.exists(os.path.join(MCR_DIR, k.module))
           and k.new and not k.old
           for k in CONTROLS if k.creates),
       str([k.id for k in CONTROLS if k.creates
            and os.path.exists(os.path.join(MCR_DIR, k.module))]))
    ok("the repository is found from wherever this runs",
       _repo_root() is not None)


def self_check(verbose: bool = True) -> int:
    import harness
    return harness.run("controls.py", _checks, verbose)


# --- CLI -------------------------------------------------------------------

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--only", metavar="ID")
    ap.add_argument("--card")
    ap.add_argument("--self-check", action="store_true")
    a = ap.parse_args(argv)

    if a.self_check:
        return 1 if self_check() else 0
    if a.list:
        for k in CONTROLS:
            print(f"{k.id:<26} {k.module} :: {k.function}")
            print(f"    - {k.old.strip() or '(the file does not exist)'}")
            print(f"    + {k.new.strip()}")
            print(f"    guards: {k.why}")
        return 0
    if a.only and a.only not in BY_ID:
        print(f"error: no control called {a.only!r}", file=sys.stderr)
        return 2

    card = a.card or os.environ.get("WE2002_MCR_CARD")
    results = run_all(only=a.only, card_path=card)
    return 0 if all(r.good for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())

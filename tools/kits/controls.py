#!/usr/bin/env python3
"""The negative controls of the kits gate, planted by command.

*A guard that has never gone red is decoration.*  Each control is a literal
substitution -- a file, the function it lives in, the exact source line and
what it becomes -- planted in a copy of `tools/kits/` (with the `tools/looks/`
and `tools/pes2/` it imports beside it).  The copy's `selftest.py --no-plant`
then has to exit non-zero AND print the check the control aims at: a red for
another reason is as useless as a green.  A literal that matches zero times or
more than once is a broken control, not a red one.

Usage:
    python tools/kits/controls.py
    python tools/kits/controls.py --list
    python tools/kits/controls.py --only tex-size-check
"""

from __future__ import annotations

import argparse
import dataclasses
import os
import shutil
import subprocess
import sys
import tempfile

KITS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(KITS_DIR)
REPO_DIR = os.path.dirname(TOOLS_DIR)
COPIED = ("tools/kits", "tools/looks", "tools/pes2", "src/core", "data")
"""What the sandbox holds, at the same paths as in the repository: the kits
tree, the two it imports, and what the looks self-checks read from the
repository root (the C++ core and data/defaultlook.txt)."""


@dataclasses.dataclass(frozen=True)
class Control:
    """One planted defect, and the failing check it has to show."""

    id: str
    path: str           # relative to tools/
    function: str
    old: str
    new: str
    expect: str         # a piece of the FAIL line the selftest must print
    why: str


CONTROLS = (
    Control(
        "tex-shape-referee", "kits/core/tex.py", "EXPECTED_SHAPE",
        "    (KIND_IMAGE, 768, 384, 64, 128),   # 10 referee",
        "    (KIND_IMAGE, 768, 385, 64, 128),   # 10 referee",
        "FAIL  a well-formed container passes the guard",
        "the rectangles are the guard of section 2.1; one off by a line must refuse "
        "every real kit",
    ),
    Control(
        "tex-flag-double", "kits/core/tex.py", "plain_size",
        "    return size * 2 if (x, y, w, h) == bin_archive.KNOWN_DOUBLE else size",
        "    return size",
        "FAIL  a well-formed container passes the guard",
        "the flag stream holds twice its rectangle (section 1.1); taking the "
        "rectangle at its word refuses all 105",
    ),
    Control(
        "tex-size-check", "kits/core/tex.py", "read_kit",
        "        if len(plain) != want:",
        "        if False:",
        "FAIL  a stream one byte short is refused on its record",
        "a stream that decodes to the wrong size is the second half of the guard",
    ),
    Control(
        "tex-stream-control-literal", "kits/core/tex.py", "module constant",
        "STREAM_CONTROL_AT = 0",
        "STREAM_CONTROL_AT = 1",
        "FAIL  section 5 control 4",
        "a changed literal byte still decodes to the right size: control 4 has to "
        "change the flag byte, or it plants nothing the guard can see",
    ),
    Control(
        "tex-header-extent", "kits/core/tex.py", "declared_extent",
        "    return None if end < 0 else end + len(LIST_END)",
        "    return None if end < 0 else end",
        "FAIL  the header extent is the end of the record list",
        "four bytes short of the end halfword, the read past the ISO size cuts the "
        "list it was reading for",
    ),
    Control(
        "source-form2-tail", "kits/core/source.py", "_sector_data",
        "    if any(raw[FORM2_TAIL]):",
        "    if False:",
        "FAIL  a sector marked Form 2 with data in its tail is refused",
        "the Form 2 bit is overruled only when the bytes prove the Form 1 layout",
    ),
    Control(
        "source-next-file", "kits/core/source.py", "_slot_end",
        "    later = [e.lba for e in image.files.values() if e.lba > entry.lba]",
        "    later = []",
        "FAIL  a file starting at the ISO end stops the read there",
        "reading past the ISO size stops at the next file, or it reads someone "
        "else's sectors",
    ),
    Control(
        "core-prints", "kits/core/errors.py", "KitsError",
        '    """Base of every error the kits core raises on purpose."""',
        '    """Base of every error the kits core raises on purpose."""\n'
        '    print("planted")',
        "FAIL  core/ has no print, exit, input or Qt",
        "section 3.1: the core returns data and never prints",
    ),
    Control(
        "looks-layout-empty-slot", "looks/layout.py", "the pointer-list walk",
        "        if tag == 0 and pointer == 0:",
        "        if False:",
        "FAIL  looks layout.self_check()",
        "section 6, coupling: a looks module the kits code imports breaks, and "
        "this gate has to say so.  The literal is the looks catalogue's own "
        "`layout-empty-slot`, which its self-check is known to catch; a constant "
        "no looks self-check reads (texture's KIND_IMAGE) stayed green",
    ),
    Control(
        "looks-skin-union", "looks/skin.py", "the union of a field's primitives",
        "        out |= set(field.primitives or ())",
        "        out = set(field.primitives or ())",
        "FAIL  looks skin.self_check()",
        "section 6, coupling, two imports away: no kits file imports skin, "
        "assembly does.  The looks catalogue's own `skin-union-of-one-field`; "
        "before CORR-KITS-017 the gate scanned only the kits imports and "
        "stayed green on it",
    ),
    Control(
        "cli-imports-survey", "kits/cli.py", "the imports",
        "from core import api  # noqa: E402\n",
        "from core import api  # noqa: E402\nfrom core import survey  # noqa: E402\n",
        "FAIL  cli.py and confront.py import only core.api",
        "section 3.1: the CLI is the second client of the facade and the proof it "
        "is enough; before CORR-KITS-018 it imported core.survey and the gate "
        "stayed green",
    ),
    Control(
        "confront2-blind", "kits/confront.py", "compare_pair",
        "    if plain == pixels:",
        "    if True:",
        "FAIL  confront 2: one pixel changed in the .tim is a mismatch",
        "section 5, confront 2: an oracle whose comparison cannot fail says "
        "nothing about the decoder",
    ),
    Control(
        "ui-imports-core", "kits/ui/app.py", "module imports",
        "from core import api  # noqa: E402",
        "from core import api, zones  # noqa: E402",
        "FAIL  ui/ imports only PySide6, core.api and the standard library",
        "section 3.1: the window draws what the facade returns; reaching past it "
        "is the coupling the facade exists to stop",
    ),
    Control(
        "zones-front-moved", "kits/core/zones.py", "ZONES",
        '    _z("shirt front", PLAYER, 12, 8, 20, 22),',
        '    _z("shirt front", PLAYER, 13, 8, 20, 22),',
        "FAIL  zones.self_check() reports no failure",
        "the map is a partition of polipoli's picture; one row moved 1 px has to "
        "overlap its neighbour (section 5, control 4 on the disc is `cli.py zones "
        "--negative`)",
    ),
    Control(
        "zones-quiet-unexplained", "kits/core/zones.py", "Confrontation.unsampled_unexplained",
        "        return tuple(z for z, n in self.sampled if not n and not z.unsampled)",
        "        return ()",
        "FAIL  a zone nobody samples, with no reason, fails section 4.6",
        "section 4.6: a quiet zone has to say why (CORR-KITS-031)",
    ),
    Control(
        "zones-excused-sampled", "kits/core/zones.py", "Confrontation.sampled_but_excused",
        "        return tuple(z for z, n in self.sampled if n and z.unsampled)",
        "        return ()",
        "FAIL  a zone excused from sampling, and sampled, fails section 4.6",
        "section 4.6: a reason for silence on a zone that is sampled is a wrong "
        "reason (CORR-KITS-031)",
    ),
    Control(
        "zones-gap-unused", "kits/core/zones.py", "Confrontation.gaps_unused",
        "        return tuple(g for g in self.gaps if (g.name, g.figure) not in used)",
        "        return ()",
        "FAIL  a declared gap nobody samples fails section 4.6",
        "section 4.6: a gap is declared because the game samples it; one that "
        "nobody samples is stale (CORR-KITS-031)",
    ),
)
BY_ID = {c.id: c for c in CONTROLS}


@dataclasses.dataclass
class Result:
    control: Control
    matched: int
    exit_code: int
    shown: bool         # the expected FAIL line was printed

    @property
    def good(self) -> bool:
        return self.matched == 1 and self.exit_code != 0 and self.shown


def _sandbox(tmp: str) -> str:
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for sub in COPIED:
        shutil.copytree(os.path.join(REPO_DIR, sub), os.path.join(tmp, sub), ignore=ignore)
    return tmp


def _selftest(root: str):
    env = dict(os.environ)
    env.pop("WE2002_LOOKS_IMAGE", None)
    return subprocess.run(
        [sys.executable, os.path.join(root, "tools", "kits", "selftest.py"), "--no-plant",
         "--quiet"],
        env=env, capture_output=True, text=True, cwd=root)


def baseline() -> tuple:
    """(exit code, output) of the selftest in an unplanted sandbox.  It has to
    be 0: otherwise every control is red for the sandbox, not for its plant."""
    with tempfile.TemporaryDirectory(prefix="kits-control-") as tmp:
        proc = _selftest(_sandbox(tmp))
        return proc.returncode, proc.stdout


def plant(control: Control) -> Result:
    """Copy the trees, substitute once, run the copy's selftest."""
    with tempfile.TemporaryDirectory(prefix="kits-control-") as tmp:
        root = _sandbox(tmp)
        path = os.path.join(root, "tools", control.path)
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
        matched = text.count(control.old)
        if matched == 1:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(text.replace(control.old, control.new))
        proc = _selftest(root)
        return Result(control, matched, proc.returncode, control.expect in proc.stdout)


def run_all(only=None, verbose: bool = True) -> list:
    """Every control's Result.  Raises RuntimeError when the unplanted sandbox
    is not green, since then no red below would mean anything."""
    code, output = baseline()
    if code != 0:
        fails = [l for l in output.splitlines() if "FAIL" in l]
        raise RuntimeError("the unplanted sandbox is not green (exit %d): %s"
                           % (code, "; ".join(fails[:5])))
    if verbose:
        print("  base   unplanted sandbox            selftest exit 0")
    out = []
    for control in ([BY_ID[only]] if only else CONTROLS):
        result = plant(control)
        out.append(result)
        if verbose:
            note = ""
            if result.matched != 1:
                note = "  -- BROKEN CONTROL: matched %dx" % result.matched
            elif result.exit_code == 0:
                note = "  -- did NOT go red"
            elif not result.shown:
                note = "  -- red, but not on %r" % control.expect
            print("  %s  %-28s %s :: %s%s" % ("RED  " if result.good else "GREEN",
                                             control.id, control.path, control.function, note))
    if verbose:
        print("controls: %d of %d red" % (sum(r.good for r in out), len(out)))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--only", choices=sorted(BY_ID))
    args = parser.parse_args(argv)
    if args.list:
        for c in CONTROLS:
            print("  %-28s %s :: %s\n      %s" % (c.id, c.path, c.function, c.why))
        print("controls: %d catalogued" % len(CONTROLS))
        return 0
    try:
        results = run_all(args.only)
    except RuntimeError as exc:
        print("controls: %s" % exc)
        return 1
    return 0 if all(r.good for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())

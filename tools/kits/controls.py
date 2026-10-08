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
        "FAIL  ui/ imports only PySide6, core.api, its own modules and the standard library",
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
    Control(
        "figure-swap-noop", "kits/core/figure.py", "swapped_palettes",
        "    return bytes(out)\n",
        "    return bytes(data)\n",
        "FAIL  set 1: the swap puts 488 where 486 was",
        "control 4 of section 5 has to swap something: a swap that returns the "
        "kit untouched passes TEX_A4 on the disc, whose two palettes are equal "
        "(KITS-TASK-24)",
    ),
    Control(
        "geometry-env-ignored", "kits/core/figure.py", "geometry_path_for",
        "    path = path or os.environ.get(GEOMETRY_ENV)\n",
        "    path = path\n",
        "FAIL  lone TEX: with no geometry path, the figure takes",
        "a lone TEX has no disc of its own, and the figure's geometry has to "
        "come from WE2002_LOOKS_IMAGE; ignoring it leaves every TEX opened "
        "outside the disc without a 3D figure (CORR-KITS-044)",
    ),
    Control(
        "oracle-sets-swapped", "kits/oracle.py", "SETS",
        "SETS = {0: 1, 1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 2}\n",
        "SETS = {0: 2, 1: 2, 2: 2, 3: 2, 4: 1, 5: 1, 6: 1, 7: 1}\n",
        "FAIL  oracle --expect: set 1 written, 00=1 holds",
        "oracle.py has to assert the set it reports: with the record-to-set "
        "map swapped it named Scotland's set 2 and exited 0 (CORR-KITS-047)",
    ),
    Control(
        "oracle-back-byte-order", "kits/oracle.py", "pixel_index",
        "    return word & 0xFF if x % 2 == 0 else word >> 8\n",
        "    return word >> 8 if x % 2 == 0 else word & 0xFF\n",
        "FAIL  oracle --back: the copy is found at (44,6), inside the shirt back",
        "the 8 bpp page packs the even pixel in the low byte; with the halves "
        "swapped --back finds no copy and its --expect-back fails (KITS-TASK-38, "
        "CORR-KITS-067)",
    ),
    Control(
        "oracle-pose-texel-order", "kits/oracle.py", "piece_error",
        '        order = prim.indices if pair == "indices" else prim.corners\n',
        "        order = prim.corners\n",
        "FAIL  oracle --match-pose: a piece's own matrix lands within the limit, paired by texel",
        "a texel belongs to the vertex Primitive.indices names, not to the corner "
        "order; paired by corners the measured pose misses (KITS-TASK-45, "
        "CORR-KITS-084)",
    ),
    Control(
        "oracle-matrix-share-blind", "kits/oracle.py", "matrix_report",
        '                        if q is not p and q["matrix"] == p["matrix"]]\n',
        '                        if False]\n',
        "FAIL  oracle --attach-matrix: a long sleeve given section 7's matrix shares it",
        "the whole answer of KITS-TASK-44 is 'own matrix'; a comparison that "
        "never finds a share prints the same verdict (CORR-KITS-076)",
    ),
    Control(
        "oracle-sleeves-long-first", "kits/oracle.py", "sleeves_kind",
        '    return ("armband" if any(n.startswith("armband") for n in names)\n'
        '            else "long sleeve" if any(n.startswith("long sleeve") for n in names)\n',
        '    return ("long sleeve" if any(n.startswith("long sleeve") for n in names)\n'
        '            else "armband" if any(n.startswith("armband") for n in names)\n',
        "FAIL  oracle --sleeves: a quad across captain and armband is the armband, once",
        "an armband quad also touches the captain's long-sleeve rows; counted "
        "long sleeve first, the 8 armband primitives vanish into the 88 "
        "(CORR-KITS-068)",
    ),
    Control(
        "cli-kit-swapped", "kits/cli.py", "module constant",
        'KIT_NAMES = {"home": 1, "away": 2}',
        'KIT_NAMES = {"home": 2, "away": 1}',
        "FAIL  cli.py figure --kit home is --set 1 and --kit away is --set 2",
        "kit 1 is home and kit 2 away by football's convention (G1 of "
        "KITS-AJUSTES-3D.md); --kit swapped draws the other uniform under the "
        "right name, with nothing else to show it (K3D-TASK-01)",
    ),
    Control(
        "holes-alpha-ignored", "kits/core/raster.py", "draw",
        "                    if data[k + 3]:\n",
        "                    if True:\n",
        "FAIL  hole count: a transparent texel in the uniform raises the count",
        "a count that takes every texel as opaque never sees the torso gap or a "
        "new one, and prints a clean figure at every turn (K3D-TASK-04)",
    ),
    Control(
        "raster-skips-flat-uv", "kits/core/raster.py", "draw",
        "            unmapped = skip_degenerate and \\\n",
        "            unmapped = True and \\\n",
        "FAIL  the drawing paints a triangle with no UV area",
        "a triangle whose UV has no area left out is what opened the shorts at the "
        "back (G6, K3D-TASK-13)",
    ),
    Control(
        "raster-mean-order", "kits/core/raster.py", "draw",
        "                if order == MEAN or here is None or depth >= here[0] - DEPTH_TIE:\n",
        "                if True:\n",
        "FAIL  crossing quads: at every pixel the nearest wins",
        "painting in order regardless of depth is the old order by mean depth, which "
        "put the leg over the shorts (G6, K3D-TASK-13)",
    ),
    Control(
        "scene-outside-figure", "kits/core/teams.py", "module imports",
        "import layout  # noqa: E402  (tools/looks: the boot file and its Japanese digest)\n",
        "import layout  # noqa: E402  (tools/looks: the boot file and its Japanese digest)\n"
        "import scene  # noqa: E402,F401\n",
        "FAIL  only core/figure.py imports the looks scene",
        "a second module asking the looks for a scene is a second bridge, which "
        "section 3.1 forbids (KITS-TASK-24)",
    ),
    Control(
        "i18n-key-missing", "kits/ui/i18n.py", "CATALOG",
        '        "zone_none": "nenhuma",\n',
        "",
        "FAIL  en-US and pt-BR have the same keys",
        "a key one language lacks shows a KeyError the day someone picks that "
        "language, and no gate in English sees it (KITS-TASK-36)",
    ),
    Control(
        "i18n-field-renamed", "kits/ui/i18n.py", "CATALOG",
        '        "status_exported": "exportado: {path}",',
        '        "status_exported": "exportado: {caminho}",',
        "FAIL  en-US and pt-BR have the same keys and the same fields",
        "a field renamed in one translation raises KeyError on format, only in "
        "that language (KITS-TASK-36)",
    ),
    Control(
        "ui-literal-text", "kits/ui/app.py", "Window.retranslate",
        '        self.export_button.setText(tr("export_png"))',
        '        self.export_button.setText("Exportar PNG")',
        "FAIL  ui/app.py shows no text outside tr()",
        "a literal in a setText is window text that no language switch reaches: "
        "the AST sweep is the only thing that says so (KITS-TASK-36)",
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

#!/usr/bin/env python3
"""The negative controls of the kits gate, planted by command.

*A guard that has never gone red is decoration.*  Each control is a literal
substitution -- a file, the function it lives in, the exact source line and
what it becomes -- planted in a copy of `tools/kits/` (with the `tools/looks/`
and `tools/pes2/` it imports beside it, and the `tools/duckmcp/` the
`tools/pes2/mcp.py` shim imports).  The copy's `selftest.py --no-plant`
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
COPIED = ("tools/kits", "tools/looks", "tools/pes2", "tools/duckmcp", "src/core", "data")
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
        "oracle-back-byte-order", "kits/core/replay.py", "pixel_index",
        "    return word & 0xFF if x % 2 == 0 else word >> 8\n",
        "    return word >> 8 if x % 2 == 0 else word & 0xFF\n",
        "FAIL  oracle --back: the copy is found at (44,6), inside the shirt back",
        "the 8 bpp page packs the even pixel in the low byte; with the halves "
        "swapped --back finds no copy and its --expect-back fails (KITS-TASK-38, "
        "CORR-KITS-067)",
    ),
    Control(
        "oracle-pose-texel-order", "kits/core/replay.py", "piece_error",
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
        "figure-long-sleeves-short-arms", "kits/core/figure.py", "arm_dress",
        '    out = {ARM_PIECES[s]: s for s in LONG_TO_SHORT} if sleeves == "long" else {}',
        '    out = {ARM_PIECES[s]: s for s in LONG_TO_SHORT.values()} if sleeves == "long" else {}',
        "FAIL  arm_dress: armband False, long sleeves",
        "the long sleeves are MODEL.BIN's 95 96 97 98 on the arm pieces (G3, "
        "K3D-TASK-10); dressed with the short arms they stand for, the box draws "
        "the figure it was ticked on",
    ),
    Control(
        "figure-keeper-armband-on-the-player-arm", "kits/core/figure.py", "arm_dress",
        "        return {ARM_PIECES[KEEPER_ARMBAND]: KEEPER_ARMBAND} if armband else {}",
        "        return {ARM_PIECES[KEEPER_ARMBAND]: SLEEVE_LENGTHS[\"long\"][\"armband\"]} "
        "if armband else {}",
        "FAIL  arm_dress: the goalkeeper, armband True",
        "the goalkeeper's armband is section 92, measured in slot 7 (G4, K3D-TASK-08 "
        "and 11); the player's 93 in its place draws a band the game never put on him",
    ),
    Control(
        "oracle-keeper-armband-unasked", "kits/oracle.py", "keeper_armband_judge",
        "    if not captains:\n        out.append(\"no figure opened at section %d draws section %d\" % (root, armband))",
        "    if False:\n        out.append(\"no figure opened at section %d draws section %d\" % (root, armband))",
        "FAIL  oracle --keeper-armband: no goalkeeper drawing the armband fails",
        "the armband is the claim of G4 (K3D-TASK-08); a judge that never asks "
        "for it passes any section with 15's vertices, 103 as well as 92",
    ),
    Control(
        "oracle-edit-number-head-unasked", "kits/oracle.py", "edit_number_judge",
        "    if not any(f[\"head\"] == head for f in report[\"figures\"]):\n"
        "        out.append(\"no figure opened at section %d\" % head)",
        "    if False:\n"
        "        out.append(\"no figure opened at section %d\" % head)",
        "FAIL  oracle --edit-number: no figure opened at the head fails",
        "which section the EDIT PL. NUM figure opens with is the first claim of G7 "
        "(K3D-TASK-16); a judge that never asks for it passes the plant's 103",
    ),
    Control(
        "oracle-edit-number-family-blind", "kits/oracle.py", "edit_number_judge",
        '            for f in report["figures"] if f["family"] == "neither"]',
        '            for f in report["figures"] if False]',
        "FAIL  oracle --edit-number: a figure of no family fails",
        "a figure whose sections belong to neither list is no EDT_MOD.BIN figure; "
        "the check was never seen red before CORR-K3D-020",
    ),
    Control(
        "oracle-edit-number-number-unasked", "kits/oracle.py", "edit_number_judge",
        '        if numbers and numbers != [expect["number"]]:',
        '        if False:',
        "FAIL  oracle --edit-number: another number on the measured panel fails",
        "the number on the back is what G7 measured (1 for Marcos, 5 for Edmilson); "
        "until CORR-K3D-020 any number the rule read passed",
    ),
    Control(
        "replay-focus-unasked", "kits/core/replay.py", "replay_focus",
        "    ranked = sorted(figures, key=figure_depth)",
        "    ranked = list(figures)",
        "FAIL  core/replay: the followed figure is the nearest, the plant the next",
        "the replay's camera follows one player, and the nearest figure is the one it "
        "follows (G8, K3D-TASK-17); taking the frame's first figure measures another",
    ),
    Control(
        "oracle-replay-colour-unread", "kits/oracle.py", "textured_samples",
        "            rgb = [looks_oracle._packet_colour(words[per * i] if code & 16 else words[0])",
        "            rgb = [looks_oracle._packet_colour(words[0])",
        "FAIL  oracle --replay: a shaded quad keeps its four corner colours, a flat one its one",
        "whether the GPU shades the figure is read off each quad's corner colours (G8, "
        "K3D-TASK-17); reading only the first would call every quad flat",
    ),
    Control(
        "replay-modulation-ignored", "kits/core/replay.py", "colour_confront",
        "                shaded = tuple(min(31, int(t * c / NEUTRAL)) for t, c in zip(texel, colour))",
        "                shaded = texel",
        "FAIL  core/replay: a pixel drawn at half colour is the modulated texel, not the bare one",
        "the confront says whether the GPU's modulation is what the 3D tab lacks (G8, "
        "K3D-TASK-17); a modulated column equal to the bare texel cannot tell",
    ),
    Control(
        "replay-field-margin-unasked", "kits/core/replay.py", "judge_walk",
        '                and abs(r["next_depth"] - r["depth"]) < REPLAY_FOCUS_MARGIN[1]:',
        "                and False:",
        "FAIL  core/replay: a second figure inside the margin fails",
        "behind a player the frame holds a dozen figures, and the one on the camera's axis "
        "is the followed one only if the next lies a margin off it (G8, K3D-TASK-18, "
        "CORR-K3D-024)",
    ),
    Control(
        "replay-field-still-unasked", "kits/core/replay.py", "judge_walk",
        '        if r.get("frames") is not None and (r.get("still") is None or r["still"] > REPLAY_STILL):',
        "        if False:",
        "FAIL  core/replay: a focus with no still pose, or one that moved, fails",
        "the table asks each focus for the still pose of the paused replay; a capture of "
        "one whole frame prints None there, and nothing judged it (G8, CORR-K3D-026)",
    ),
    Control(
        "replay-field-players-unasked", "kits/core/replay.py", "judge_walk",
        '        if (outfield, keepers, others) != (players["outfield"], players["keepers"], 0):',
        "        if False:",
        "FAIL  core/replay: a walk cut short or onto another figure fails",
        "a tap that lands the camera on another figure off the axis reads as the ball, and "
        "the walk ends early with an ok (G8, CORR-K3D-030)",
    ),
    Control(
        "fork-joystick-let-through", "pes2/fork.py", "refuse_joysticks",
        "    if found:\n        raise Fail(\"a game controller is plugged in",
        "    if False:\n        raise Fail(\"a game controller is plugged in",
        "FAIL  live runs: a plugged-in controller refuses the run",
        "the fork reads SDL-0, and a controller in use elsewhere presses buttons in the "
        "game under test (CORR-K3D-031)",
    ),
    Control(
        "looks-oracle-joystick-unasked", "looks/oracle.py", "Oracle.__enter__",
        "        fork.refuse_joysticks()\n",
        "",
        "FAIL  live runs: the oracle refuses before it boots the fork",
        "the guard has to run before the fork boots, in the one place every live "
        "measurement enters (CORR-K3D-031)",
    ),
    Control(
        "replay-field-shared-panel", "kits/core/replay.py", "field_panels",
        '        own = sorted(set(r["cells"]) - shared.get(r["page"], set())) or sorted(r["cells"])',
        '        own = sorted(r["cells"])',
        "FAIL  core/replay: the panel is the cell left once the shared one is taken away",
        "every outfield back also samples one cell all of a page share (G8, K3D-TASK-18); "
        "keeping every cell names no single panel for the player",
    ),
    Control(
        "replay-field-nearest-followed", "kits/core/replay.py", "field_focus",
        "    ranked = sorted(figures, key=figure_off_axis)",
        "    ranked = sorted(figures, key=figure_depth)",
        "FAIL  core/replay: the followed figure is on the axis, not the nearest",
        "behind a player a figure running between him and the camera lies nearer than he "
        "does; the camera keeps the followed one on its axis (G8, K3D-TASK-18)",
    ),
    Control(
        "oracle-replay-focus-nearest", "kits/oracle.py", "replay_chooser",
        "    return replay_focus if not focus else field_focus",
        "    return replay_focus",
        "FAIL  oracle --replay --focus: the replay as saved follows the nearest, a focus the axis",
        "behind a player a neighbour can lie nearer than the one the camera follows "
        "(K3D-TASK-18); --replay --focus takes the figure on the axis (G8, K3D-TASK-19)",
    ),
    Control(
        "replay-shared-cell-kept", "kits/core/replay.py", "panel_cell",
        "    own = [c for c in cells if c != REPLAY_SHARED_CELL] if outfield else []",
        "    own = []",
        "FAIL  core/replay: an outfield back shows the cell beside the shared one",
        "an outfield back samples the shared cell as much as its own (two quads each); "
        "the most quads names no single panel (G8, K3D-TASK-19)",
    ),
    Control(
        "replay-sleeves-unjudged", "kits/core/replay.py", "judge",
        '    if expect.get("sleeves") and sleeves_of(order) != expect["sleeves"]:',
        "    if False:",
        "FAIL  core/replay: an armband where none is expected, and long sleeves, fail",
        "the sleeves are per slot -- short in 9, long in 10 -- and the judge holds the "
        "followed player to them (G8, K3D-TASK-19)",
    ),
    Control(
        "oracle-arm-side-flipped", "kits/oracle.py", "arm_side",
        '    return "a" if sum(p[2] for p in points) / len(points) < 0 else "b"',
        '    return "a" if sum(p[2] for p in points) / len(points) > 0 else "b"',
        "FAIL  oracle --edt-arms: a sleeve goes on its own piece, in its frame",
        "the side of an arm is the sign of its mean z (K3D-TASK-07); read the "
        "other way, the armband lands on the other arm and nothing else differs",
    ),
    Control(
        "oracle-arm-frame-blind", "kits/oracle.py", "frame_offset",
        "    for _ in range(steps):",
        "    for _ in range(0):",
        "FAIL  oracle --edt-arms: a sleeve moved out of its frame fails",
        "an offset that never iterates is 0 for any arm, and the rule that the "
        "MODEL.BIN section shares its EDT_MOD.BIN piece's frame asserts nothing",
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
    Control(
        "replay-key-check", "kits/core/replay.py", "_require",
        "        if key not in data:\n",
        "        if False:\n",
        "FAIL  core/replay: a capture lacking a key is refused, naming the key",
        "a capture without a key the analysis reads has to be refused on that key, not "
        "fail three calls later on a KeyError (KRP-TASK-01)",
    ),
    Control(
        "replay-v0-slot", "kits/core/replay.py", "Capture.from_dict",
        "            slot = int(found.group(1))\n",
        "            slot = int(found.group(1)) - 1\n",
        "FAIL  core/replay: a v0 close capture comes back as v1, slot and focus off its name",
        "a v0 close capture says its slot only in its file name; the migration to v1 "
        "is what puts it in the capture (KRP-TASK-01)",
    ),
    Control(
        "replay-copy-in-oracle", "kits/oracle.py", "module constant",
        "PLANT_REPLAY_ROOT = 103\n",
        "PLANT_REPLAY_ROOT = 103\n\n\ndef figure_depth(figure):\n    return 0\n",
        "FAIL  oracle.py defines none of the analysis core/replay.py holds",
        "the analysis moved to core/replay.py by move, not copy; a second figure_depth "
        "in the oracle is the copy section 2.2 forbids (KRP-TASK-02)",
    ),
    Control(
        "replay-digest-unasked", "kits/replay.py", "digest_problem",
        "    if got != want:\n",
        "    if False:\n",
        "FAIL  replay.py: a capture with another digest is refused",
        "kits_replay judges the captures it was given by their bytes; one with another "
        "digest is another capture, and its ok means nothing (KRP-TASK-04)",
    ),
    Control(
        "replay-figure-key-dropped", "kits/replay.py", "figure_report",
        '            "turned": capture.data["turned"], "front_frames": '
        'capture.data["front_frames"],\n',
        '            "front_frames": capture.data["front_frames"],\n',
        "FAIL  replay.py: figure --json carries the kits-replay/1 schema and its fixed keys",
        "the --json keys are the contract with an agent: a key that does not apply is "
        "null, never missing (CORR-KRP-004)",
    ),
    Control(
        "replay-figures-schema-dropped", "kits/replay.py", "figures_report",
        '    return {"schema": SCHEMA, "capture": _capture_doc(capture), "side": side,\n',
        '    return {"capture": _capture_doc(capture), "side": side,\n',
        "FAIL  replay.py: figures --json carries the kits-replay/1 schema and its fixed keys",
        "an object without the schema is one an agent cannot tell from another "
        "command's (CORR-KRP-004)",
    ),
    Control(
        "replay-walk-key-dropped", "kits/replay.py", "walk_report",
        '            "shared": {"%d" % page: sorted(cells) for page, cells in '
        'sorted(walk.shared.items())},\n',
        "",
        "FAIL  replay.py: walk --json carries the kits-replay/1 schema and its fixed keys",
        "the walk's shared cells are a fixed key of its --json; dropping it breaks the "
        "contract with no judge seeing it (CORR-KRP-004)",
    ),
    Control(
        "replay-panel-key-dropped", "kits/replay.py", "main",
        '                   "nth": doc["nth"], "panel": doc["panel"]}\n',
        '                   "panel": doc["panel"]}\n',
        "FAIL  replay.py: panel --json carries the kits-replay/1 schema and its fixed keys",
        "the panel document is built in main, apart from every report; its keys need "
        "their own check (CORR-KRP-004)",
    ),
    Control(
        "replay-behind-inverted", "kits/replay.py", "panel_of",
        "    behind = bool(capture.focus)\n",
        "    behind = not bool(capture.focus)\n",
        "FAIL  replay.py: behind a player the panel is read off the first capture's torso",
        "the gate reads the panel through panel_of; behind a player it is the first "
        "capture's torso, and the inversion sends kits_replay to 6 failures on the kept "
        "captures (CORR-KRP-004)",
    ),
    Control(
        "replay-show-unposed", "kits/core/replay.py", "pose_picture",
        '        rotation, translation = piece["matrix"]\n        for prim in sec.primitives:\n',
        "        rotation, translation = (4096, 0, 0, 0, 4096, 0, 0, 0, 4096), (0, 0, 0)\n"
        "        for prim in sec.primitives:\n",
        "FAIL  show draws the figure in its captured pose, on the frame buffer's pixels",
        "show puts the drawn figure beside the game's frame to compare the two; drawn "
        "without the captured matrices it lands elsewhere, or nowhere (KRP-TASK-05)",
    ),
    Control(
        "replay-show-mirrored", "kits/core/replay.py", "pose_picture",
        "                points.append((-at[0], -at[1], -cz))\n",
        "                points.append((at[0], at[1], -cz))\n",
        "FAIL  show draws the figure in its captured pose, on the frame buffer's pixels",
        "raster.draw's view negates x and y, and pose_picture negates them back; without "
        "that the figure is drawn turned half round about the box's centre, and on "
        "replay-9-3 drawn goes from 2349 to 136 px (CORR-KRP-006)",
    ),
    Control(
        "replay-show-unrotated", "kits/core/replay.py", "pose_picture",
        '        rotation, translation = piece["matrix"]\n        for prim in sec.primitives:\n',
        '        rotation, translation = (4096, 0, 0, 0, 4096, 0, 0, 0, 4096), '
        'piece["matrix"][1]\n        for prim in sec.primitives:\n',
        "FAIL  show draws the figure in its captured pose, on the frame buffer's pixels",
        "the captured translation alone puts each piece in place but not turned; on "
        "replay-9-3 drawn goes from 2349 to 2636 px (CORR-KRP-006)",
    ),
    Control(
        "replay-capture-joystick-late", "kits/replay.py", "run_capture",
        "    fork.refuse_joysticks()\n    image = os.environ[IMAGE_VARIABLE]\n",
        "    image = os.environ[IMAGE_VARIABLE]\n",
        "FAIL  replay.py capture refuses a plugged-in controller before it reads or boots anything",
        "the controller guard has to run before the capture reads the disc or boots the "
        "fork; left to the Oracle it still refuses, but only after the work it was meant to "
        "spare (CORR-K3D-031, KRP-TASK-07)",
    ),
    Control(
        "replay-capture-timeout-unasked", "kits/replay.py", "timeout_failures",
        "            if judged and (idle is None or n is None or n >= idle)]\n",
        "            if judged and (idle is None or n is None)]\n",
        "FAIL  replay.py capture: a sequence that reaches the replay's timeout fails",
        "past 390 frames the paused replay leaves by itself, and what the capture read is "
        "another screen (PLAN-KITS-REPLAY section 2.5)",
    ),
    Control(
        "replay-capture-tap-gap-unjudged", "kits/replay.py", "sequences",
        '            out += [("turn gap", max(data["tap_gaps"]), True)]\n',
        '            out += [("turn gap", max(data["tap_gaps"]), False)]\n',
        "FAIL  replay.py capture: a gap between two taps of the turn that reaches the "
        "replay's timeout fails",
        "every tap of the turn starts the replay's idle again, so what has to stay under 390 "
        "frames is the gap between two taps; left unjudged, the turn's claim rests on an "
        "average (CORR-KRP-008, PLAN-KITS-REPLAY section 2.5)",
    ),
    Control(
        "replay-tab-sides-crossed", "kits/replay.py", "game_side",
        '    return "back" if side == "front" else "front"\n',
        "    return side\n",
        "FAIL  confront --tab compares the tab's front with the game's front, back with back",
        "behind a player the first capture is his back: taking it as his front compares the "
        "tab's front with the game's back, the gap CORR-K3D-034 left (KRP-TASK-06)",
    ),
    Control(
        "replay-tab-buffer-crossed", "kits/replay.py", "game_pixels",
        '    buffer = capture.data.get("buffer" if which == "front" else "back_buffer")\n',
        '    buffer = capture.data.get("buffer")\n',
        "FAIL  confront --tab reads the first capture's buffer, and the second's back_buffer",
        "the second capture's pixels live in back_buffer: reading the first capture's buffer "
        "for both sides compares the tab's back with the game's front, in silence "
        "(CORR-KRP-010)",
    ),
    Control(
        "replay-head-hair-column", "kits/core/replay.py", "head_reading",
        "            hairs.add(column - layout.HAIR_COLUMN)\n",
        "            hairs.add(column - layout.HAIR_COLUMN + 1)\n",
        "FAIL  replay.py head: the CLUT column 1 + n reads hair colour n",
        "a hair colour read one column off still names a letter, and every head of the walk "
        "would carry the next player's colour without a stray CLUT to show it "
        "(KRP-TASK-09, PLAN-KITS-REPLAY section 3.1)",
    ),
    Control(
        "replay-head-twin-unasked", "kits/core/figure.py", "player_head_section",
        '    if values["beard_style"] >= assembly.FACE_TWIN_FROM:\n',
        '    if values["beard_style"] > assembly.FACE_TWIN_FROM:\n',
        "FAIL  replay.py head: head_expected draws the twin for beard F",
        "beard F draws the twin (47 for 46) as G does (`assembly.FACE_TWINS`); an off-by-one "
        "there sends Croatia's 8 to the plain head (KRP-TASK-09)",
    ),
    Control(
        "replay-head-squad-unbiased", "kits/replay.py", "squad_numbers",
        "             & ((1 << SQUAD_BITS) - 1)) + 1 for s in range(SQUAD_SIZE)]\n",
        "             & ((1 << SQUAD_BITS) - 1)) for s in range(SQUAD_SIZE)]\n",
        "FAIL  replay.py head: shirt numbers unpack five bits per slot, stored minus one",
        "the disc stores each shirt number minus one (`TeamView.cpp`); read raw, every panel "
        "names the player one slot over, and his head is judged against another's record "
        "(KRP-TASK-09)",
    ),
    Control(
        "replay-head-piece-box", "kits/core/replay.py", "head_samples",
        '            if all(box[0] <= x <= box[2] and box[1] <= y <= box[3] for x, y in one["xy"])]\n',
        "            ]\n",
        "FAIL  replay.py head: head_samples keeps the head piece's box, not a neighbour's head",
        "the box of the whole figure takes in a neighbour's head: on slot 10, focus 8 reads "
        "CLUT (16,482) (32,480) and Croatia's 4 is judged skin A/C (CORR-KRP-016, "
        "PLAN-KITS-REPLAY section 3.1)",
    ),
    Control(
        "replay-anime-rule-ignored", "kits/core/replay.py", "anime_piece",
        "             if anime.compose(camera, anime.WALK_RULES[name](three)) == rotation]\n",
        "             if anime.compose(camera, three) == rotation]\n",
        "FAIL  replay.py pose: each piece is explained by the rule that built its rotation",
        "the angles taken as the file stores them explain only the pieces the game unpacks "
        "plain: on the replay's mirrored side every limb flips, and the pose would be read "
        "as no pair at all (KRP-TASK-14, PLAN-KITS-REPLAY section 5.1)",
    ),
    Control(
        "replay-anime-pair-slot", "kits/core/replay.py", "anime_piece",
        "    found = [(numbers, index, (pair - start) // anime.PAIR_BYTES)\n",
        "    found = [(numbers, index, (pair - start) // anime.FRAME_BYTES)\n",
        "FAIL  replay.py pose: each paired piece is placed in the frame its pair is in",
        "the pair's slot counted in frames is 0 for every piece, and which piece of the "
        "frame each section reads would be lost (KRP-TASK-14)",
    ),
    Control(
        "replay-anime-pose-drops-pair", "kits/core/replay.py", "pose_piece",
        "        if piece.get(key) is not None:\n",
        "        if False:\n",
        "FAIL  replay.py pose: a pose piece keeps the pair and camera",
        "the pose file `--replay --pose-dir` writes would lose the pair, and `pose "
        "--against-anime` could judge no piece of it (KRP-TASK-14)",
    ),
    Control(
        "replay-anime-ram-base-shifted", "kits/replay.py", "anime_ram_report",
        "    base = layout.ANIME_BASE & RAM_MASK\n",
        "    base = (layout.ANIME_BASE + 1) & RAM_MASK\n",
        "FAIL  replay.py anime-ram: the file read at ANIME_BASE matches byte for byte",
        "the RAM read one byte past ANIME_BASE is not the file: the probe that says ANIME.BIN "
        "sits whole in the replay's RAM has to see that (CORR-KRP-029, PLAN-KITS-REPLAY "
        "section 5.1)",
    ),
    Control(
        "replay-anime-ram-word-unjudged", "kits/replay.py", "anime_ram_report",
        "    if word != ANIME_BUILD_WORD:\n",
        "    if False:\n",
        "FAIL  replay.py anime-ram: another word at ANIME_BUILD fails",
        "a word printed and never compared: a state whose ANIME_BUILD is another instruction "
        "would pass, and the breakpoint there would stop on something else (CORR-KRP-029)",
    ),
    Control(
        "replay-same-pose-section-only", "kits/replay.py", "module constant",
        'SAME_POSE_FIELDS = ("section", "rotation", "translation")\n',
        'SAME_POSE_FIELDS = ("section",)\n',
        "FAIL  replay.py pose --same-as: a piece whose rotation differs fails",
        "comparing sections alone, any pose of the same figure is 'the same': the recapture "
        "would reproduce the old poses by construction (CORR-KRP-029)",
    ),
    Control(
        "api-player-tuple-drops-a-field", "kits/core/api.py", "player_tuple",
        "    return _figure.looks.format_tuple(values)\n",
        "    return _figure.looks.format_tuple(dict(values, hair_colour=0))\n",
        "FAIL  api.py: player_tuple names back the tuple player_fields read",
        "the head panel's hair colour combo would draw every player with hair colour A: "
        "the tuple the window builds from its combos loses the field (KRP-TASK-22, "
        "PLAN-KITS-REPLAY section 3.3)",
    ),
    Control(
        "figure-player-hair-unmoved", "kits/core/figure.py", "player_head_clut",
        '        column += values["hair_colour"]\n',
        "        column += 0\n",
        "FAIL  figure.py: the player's hair column moves to his hair colour",
        "every head keeps the disc's hair column: Bokšić's blond and Balaban's brown both "
        "draw as hair colour A (KRP-TASK-10, PLAN-KITS-REPLAY section 3.2)",
    ),
    Control(
        "figure-player-skin-unmoved", "kits/core/figure.py", "player_head_clut",
        '    return skin.clut_id(layout.CLUT_ROW_FIRST + values["skin_colour"], column)\n',
        "    return skin.clut_id(row, column)\n",
        "FAIL  figure.py: the player's skin is the CLUT row 480 + skin_colour",
        "the head keeps the disc's row 480, skin A: Brazil's 10 and 11 (skins C and D) "
        "would draw as Croatia's (KRP-TASK-10)",
    ),
    Control(
        "figure-player-beard-unmoved", "kits/core/figure.py", "player_head_clut",
        '        column += values["beard_colour"]\n',
        "        column += 0\n",
        "FAIL  figure.py: the player's beard column moves to his beard colour",
        "every head keeps the disc's beard column: a beard B would draw as beard A "
        "(CORR-KRP-018, PLAN-KITS-REPLAY section 3.2)",
    ),
    Control(
        "figure-player-off-skin-moved", "kits/core/figure.py", "player_head_clut",
        "    if not layout.CLUT_ROW_FIRST <= row < layout.CLUT_ROW_FIRST"
        " + len(layout.SKIN_PALETTES):\n",
        "    if False:\n",
        "FAIL  figure.py: a head CLUT in no hair or beard column, or off the skin records, "
        "is the disc's",
        "a head CLUT off the skin records, row 486 the kit's, would be moved onto a skin "
        "row as if it were the hair's (CORR-KRP-018)",
    ),
    Control(
        "figure-match-player-clut", "kits/core/figure.py", "match_scene",
        "            if values is not None and number == order[0][0]:\n",
        "            if values is not None and number == -1:\n",
        "FAIL  figure.py: match_scene with a player draws his head with his CLUTs",
        "the match figure draws the player's section in the disc's CLUTs: Balaban's "
        "hair B would show as hair A in the match tab (CORR-KRP-018)",
    ),
    Control(
        "figure-match-player-section", "kits/core/figure.py", "match_scene",
        "        order = [(player_head_section(values), rotation, translation)] + order[1:]\n",
        "        order = list(order)\n",
        "FAIL  figure.py: match_scene with a player draws his section where the head was",
        "the match figure keeps the measured head's section whatever the player: every "
        "head would be the pose's (CORR-KRP-018)",
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

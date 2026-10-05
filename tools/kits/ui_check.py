#!/usr/bin/env python3
"""The `kits_ui` gate: the kit viewer's window judged from its pictures.

PLAN-KITS-PY.md section 3.4.  This file runs `tools/kits/ui/app.py` as a
separate process, reads the PNGs it writes with a decoder of its own (zlib and
struct of the standard library) and judges them.  It imports nothing of the
code under test: a gate that asked the window how its picture came out would
be the window agreeing with itself.

WHAT CAN BE MISSING, and then it exits 77 (ctest's skip):

  the venv with PySide6 (`work/venv-looks`, the looks one);
  `WE2002_LOOKS_IMAGE`, the Japanese data track -- unset skips, set and
      pointing at no file FAILS, because the run asked for the gate;
  a display on Linux: `:98`, with the XAUTHORITY rule of `CLAUDE.md`.  On
      Windows there is no display to need: the app parks the window at -32000.

WHAT IT JUDGES:

  the window comes up off the user's screen and writes a picture;
  the picture is not blank -- many colours, none covering it;
  **the look is the fixed one**: the window colour of the fixed palette and
      the tab pane Fusion paints from it each cover a share of the picture.
      Both were measured on 2026-10-02: without `setPalette` the window colour
      is gone (the system's comes instead), and with the `Windows` style in
      place of Fusion the pane is gone.  On Windows removing the
      `setStyle("Fusion")` line alone already loses it (the native style
      paints it white); on Linux it does not, see the plants below;
  the same state twice is the same picture, and another kit is another one;
  a tag the disc does not have exits 2 and writes no file;
  **the kit selector** -- `app.py --list-kits` -- lists the 105 items in game
      order: Ireland first, the ML default after the 95 teams, TEX_A3 last;
  **the reading under the mouse** -- `app.py --hover X,Y`, a real mouse move
      through the canvas -- names the index and the colour that
      `cli.py export --work-bitmap` writes for that pixel in its indexed PNG,
      another process whose file is read here; a point off the image exits 1;
  and the plants, each in a copy of the tree: the window without Fusion and
      without the fixed palette (section 3.4) FAIL the style judge, and the
      readout reading the pixel to the right FAILS the hover judge; the 3D
      tab drawing set 1 for both sets FAILS the 3D judge, and the tab left on
      with no geometry, or a Plan widget that changes with no geometry, FAIL
      the 3D off judge; the kit selector labelled with bare tags FAILS the
      selector judge; the Diagnosis tab without its problem rows FAILS the
      Diagnosis judge, and without its note rows FAILS it only with
      WE2002_KITS_ED_IMAGE set -- without it that plant prints "not judged",
      because only the European Deluxe TEX_13 has a note row.  A plant that passes is a red gate.  "Without Fusion" is planted as
      `setStyle("Windows")`, not as the line taken out: on Linux Qt's default
      style already is Fusion (measured on :98, 2026-10-02), so removing the
      line changed nothing there and the plant passed.  "Windows" is the one
      other style Qt draws itself on both systems.

`--compare A.png B.png` is the cross-platform half (KITS-TASK-19): the same
state captured on Windows and on Linux, compared here, pixel by pixel.  It
FAILS above `CROSS_LIMIT` of the picture, or when either capture loses the
fixed look; the control is another kit in place of the same state.

Usage:
    python tools/kits/ui_check.py
    python tools/kits/ui_check.py --compare windows.png linux.png
    ctest -R kits_ui
"""

from __future__ import annotations

import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

SKIP = 77
IMAGE_VARIABLE = "WE2002_LOOKS_IMAGE"
DISPLAY = ":98"
VENV = os.path.join("work", "venv-looks")
VENV_PYTHON = os.path.join("Scripts", "python.exe") if os.name == "nt" else os.path.join("bin", "python")
TIMEOUT = 180

KITS_DIR = os.path.dirname(os.path.abspath(__file__))
TOOLS_DIR = os.path.dirname(KITS_DIR)
APP = os.path.join(KITS_DIR, "ui", "app.py")
COPIED = ("kits", "looks", "pes2")
"""What a planted copy holds under tools/: the window, the core, and the two
trees the core imports."""

STATE = ["--tag", "00", "--image", "work1", "--palette", "2", "--zoom", "3", "--zones"]
"""The state the gate captures, and the one KITS-TASK-19 compares across systems."""
OTHER = ["--tag", "A4", "--image", "work1", "--palette", "2", "--zoom", "3", "--zones"]
MISSING_TAG = ["--tag", "ZZ"]
FIGURE_TAG = "00"
"""The 3D tag: one of the 103 whose two sets differ in their images (section 1.1)."""
FIGURE_COMBOS = ((1, 0), (2, 0), (1, 1), (2, 1))
"""(set, figure) of the four 3D captures: first and second set, player and goalkeeper."""
BACKDROP_3D = (0x8C, 0x8C, 0x8C)
"""The 3D view's backdrop, `figure_view.BACKDROP`; written here, not read from it."""
FIGURE_FLOOR = 5.0
"""The figure covers at least this percentage of a 3D capture."""
NOTE_ROWS = 60
"""Bottom rows of a capture that hold the status and the 3D note."""
TAB_LABEL = (40, 20, 80)
"""(width, height, lowest row) the greyed 3D tab label fits in.  The geometry
variable may change the Plan capture in the note rows and in that label, and
nowhere else; measured 2026-10-03, the label is x 71-87, y 48-56."""

WINDOW_COLOUR = (0xEC, 0xEC, 0xEC)
"""`QPalette.Window` of the fixed palette."""
FUSION_PANE = (0xEB, 0xEB, 0xEB)
"""The tab pane Fusion paints from that window colour (measured: 18.8 % of the
state's picture on Windows, 18.7 % on Linux; gone under the `Windows` style)."""
STYLE_SHARE = 10.0
"""Each of the two covers at least this percentage of the picture (measured by
the gate, which opens the disc by absolute path: 22.8 % and 18.8 % on Windows,
22.2 % and 18.7 % on Linux; 0 when its plant is in)."""
MIN_COLOURS = 50
MAX_SHARE = 60.0
"""Not blank: at least this many colours, and none above this percentage."""
OTHER_FLOOR = 1.0
"""Another kit changes at least this percentage of the picture."""
CROSS_LIMIT = 5.0
"""`--compare` fails above this percentage of differing pixels.  Measured on
2026-10-02, the gate's state captured on Windows and on Linux: 12224 of 627200
px (1.95 %), all of it text rasterisation -- same palette, same Fusion pane,
bitmap, grid and zones untouched.  Another kit against the same state: 47.9 %
to 49.5 %.  The limit sits between the two, with room for fonts that differ
a little more."""

HOVER_TAG = "00"
HOVER_POINTS = ((15, 10), (100, 40), (40, 70), (5, 90))
"""Work-bitmap pixels of the first set, player palette, that --hover reads:
shirt front, goalkeeper socks, short sleeve, and the torso gap under the
map (index 0, transparent in this kit)."""
OFF_IMAGE = (9999, 0)
HOVER_PNG = "TEX_%s_set1_player.png" % HOVER_TAG
"""What `cli.py export --work-bitmap` names that bitmap."""

STYLE, HOVER, FIGURE, OFF, SELECTOR, DIAG, DIAG_NOTE, RESET = (
    "style", "hover", "3D", "3D off", "selector", "diagnosis", "diagnosis note", "reset")
"""DIAG_NOTE is the Diagnosis judge on the note rows: only the European
Deluxe TEX_13 makes one, so its plant is judged only with ED_VARIABLE set
and says it was not judged otherwise (CORR-KITS-061)."""
RESET_TURN = ("--yaw", "0", "--pitch", "30")
"""A turn away from the opening one, which --reset and --double-click have to undo
(KITS-TASK-37, CORR-KITS-064)."""
ED_VARIABLE = "WE2002_KITS_ED_IMAGE"
"""The European Deluxe disc, whose TEX_48 and TEX_70 the guard refuses and
whose TEX_13 is read past its ISO size (section 2.1); the Diagnosis judge
runs those three only when it is set, and says so when it is not."""
ED_DIAG = (("48", "Refused: record 0 ("), ("70", "Refused: record 4 ("),
           ("13", "Note: its ISO size is"))
"""(tag, the start of a row its Diagnosis tab has to show) on that disc."""
LIST_TEXT = (0x60, 0x60, 0x60)
"""A pixel this dark or darker inside the Diagnosis list is text."""

KIT_ITEMS = 105
"""Items of the kit selector on the disc: the 95 teams, the ML default, the 9 unreached."""
KIT_ITEM_WANT = {0: "Ireland — TEX_00", 95: "Master League default — TEX_A4",
                 KIT_ITEMS - 1: "TEX_A3"}
"""What `app.py --list-kits` has to print at those items, in en-US (KITS-TASK-31,
CORR-KITS-058): the first team in game order, the ML default after the teams,
and the last of the tags no team wears."""
PLANTS = (
    ("reset to the wrong yaw", RESET,
     "        self.turn_to(DEFAULT_YAW, DEFAULT_PITCH)\n",
     "        self.turn_to(DEFAULT_YAW + 90, DEFAULT_PITCH)  # planted\n", "figure_view.py"),
    ("double-click does nothing", RESET,
     "        self.drag = None\n        self.reset()\n",
     "        self.drag = None  # planted: the double click does nothing\n", "figure_view.py"),
    ("diagnosis rows never added", DIAG,
     '            self.diag_list.addItem(tr("diag_problem", text=text))\n',
     "            pass  # planted: no problem row\n"),
    ("diagnosis note rows never added", DIAG_NOTE,
     '            self.diag_list.addItem(tr("diag_note", text=text))\n',
     "            pass  # planted: no note row\n"),
    ("no Fusion", STYLE, '    app.setStyle("Fusion")\n',
     '    app.setStyle("Windows")  # planted: no Fusion\n'),
    ("no fixed palette", STYLE, "    app.setPalette(fixed_palette())\n",
     "    pass  # planted: no fixed palette\n"),
    ("readout one pixel right", HOVER,
     "        index = self.picture.indices[y * self.picture.width + x]\n",
     "        index = self.picture.indices[y * self.picture.width + x + 1]\n"),
    ("3D set ignored", FIGURE,
     "            scene = api.figure(self.kit, self.set_box.currentData(), "
     "self.figure_box.currentData(),\n",
     "            scene = api.figure(self.kit, 1, self.figure_box.currentData(),\n"),
    ("3D tab never off", OFF,
     "        self.tabs.setTabEnabled(1, self.geometry is not None)\n",
     "        self.tabs.setTabEnabled(1, True)\n"),
    ("kit labels bare tags", SELECTOR,
     '                labels[tag] = tr("kit_team", team=team.name, tag=tag)\n',
     '                labels[tag] = tr("kit_tag", tag=tag)  # planted: bare tags\n'),
    ("Plan changes without geometry", OFF,
     "        self.tabs.setTabEnabled(1, self.geometry is not None)\n",
     "        self.tabs.setTabEnabled(1, self.geometry is not None)\n"
     "        self.zones_box.setEnabled(self.geometry is not None)  # planted: Plan changes\n"),
)


class BadPicture(Exception):
    pass


# -- the PNG, read here -----------------------------------------------------------

def read_png(data: bytes) -> tuple:
    """(width, height, [(r, g, b), ...], indices or None) of an 8-bit RGB,
    RGBA or indexed PNG; raises on anything else rather than read it wrong."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise BadPicture("not a PNG")
    at, head, parts, plte = 8, None, [], b""
    while at + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[at:at + 8])
        body = data[at + 8:at + 8 + length]
        if kind == b"IHDR":
            head = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            parts.append(body)
        elif kind == b"PLTE":
            plte = body
        at += 12 + length
    if head is None or not parts:
        raise BadPicture("no IHDR or no IDAT")
    width, height, depth, colour, _, _, interlace = head
    if depth != 8 or colour not in (2, 3, 6) or interlace:
        raise BadPicture("depth %d, colour type %d, interlace %d: only 8-bit RGB/RGBA/indexed"
                         % (depth, colour, interlace))
    channels = {2: 3, 3: 1, 6: 4}[colour]
    raw = zlib.decompress(b"".join(parts))
    stride = width * channels
    if len(raw) != (stride + 1) * height:
        raise BadPicture("%d bytes of pixels for %dx%d" % (len(raw), width, height))
    pixels, indices, previous, at = [], [], bytearray(stride), 0
    for _ in range(height):
        kind = raw[at]
        line = bytearray(raw[at + 1:at + 1 + stride])
        at += stride + 1
        for i in range(stride):
            a = line[i - channels] if i >= channels else 0
            b = previous[i]
            c = previous[i - channels] if i >= channels else 0
            if kind == 1:
                line[i] = (line[i] + a) & 0xFF
            elif kind == 2:
                line[i] = (line[i] + b) & 0xFF
            elif kind == 3:
                line[i] = (line[i] + (a + b) // 2) & 0xFF
            elif kind == 4:
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                line[i] = (line[i] + (a if pa <= pb and pa <= pc else b if pb <= pc else c)) & 0xFF
            elif kind:
                raise BadPicture("filter type %d" % kind)
        if colour == 3:
            indices.extend(line)
            pixels.extend(tuple(plte[3 * k:3 * k + 3]) for k in line)
        else:
            pixels.extend(tuple(line[x * channels:x * channels + 3]) for x in range(width))
        previous = line
    return width, height, pixels, (indices if colour == 3 else None)


def picture(path: str) -> tuple:
    with open(path, "rb") as fh:
        return read_png(fh.read())


def share(shot: tuple, colour: tuple) -> float:
    return 100.0 * sum(1 for p in shot[2] if p == colour) / (shot[0] * shot[1])


def expected_readout(shot: tuple, point) -> tuple:
    """(index, (r, g, b)) of *point* in an indexed picture."""
    i = point[1] * shot[0] + point[0]
    return shot[3][i], shot[2][i]


INDEX_WORD = {"en-US": "index", "pt-BR": "índice"}
"""How the readout names a palette index, by language: written here and not
read from ui/i18n.py, so the window is judged from outside its own catalog
(KITS-TASK-36)."""
DEFAULT_LANG = "en-US"


def judge_hover(output: str, code, point, want, lang: str = DEFAULT_LANG) -> list:
    """Failures of one `--hover` run against the index and colour expected, in
    *lang*: its word for the index has to be there, every other language's not."""
    index, rgb = want
    readout = next((ln.split("readout:", 1)[1].strip() for ln in output.splitlines()
                    if "readout:" in ln), "")
    marked = next((ln.split("marked:", 1)[1].strip() for ln in output.splitlines()
                   if "marked:" in ln), "")
    bad = []
    if code != 0:
        bad.append("exit %s" % code)
    for piece in ("x %d, y %d" % point, "%s %d " % (INDEX_WORD[lang], index),
                  "RGB %d,%d,%d" % rgb):
        if piece not in readout + " ":
            bad.append("%r not in the readout %r" % (piece.strip(), readout))
    for other, word in INDEX_WORD.items():
        if other != lang and word + " " in readout:
            bad.append("%r, the %s word, in the %s readout %r" % (word, other, lang, readout))
    if marked != str(index):
        bad.append("the grid marks %r, not %d" % (marked, index))
    return bad


def differing(one: tuple, two: tuple) -> int:
    if one[:2] != two[:2]:
        raise BadPicture("%dx%d against %dx%d" % (one[0], one[1], two[0], two[1]))
    return sum(1 for a, b in zip(one[2], two[2]) if a != b)


# -- the judges -------------------------------------------------------------------

def judge_frame(shot: tuple) -> list:
    """Failures of a picture that has to show something."""
    counts = {}
    for p in shot[2]:
        counts[p] = counts.get(p, 0) + 1
    top = max(counts.values()) * 100.0 / len(shot[2])
    bad = []
    if len(counts) < MIN_COLOURS:
        bad.append("%d colour(s), fewer than %d: a blank frame" % (len(counts), MIN_COLOURS))
    if top > MAX_SHARE:
        bad.append("one colour covers %.1f %% of the picture" % top)
    return bad


def judge_style(shot: tuple) -> list:
    """Failures of the fixed look: the palette's window colour and Fusion's pane."""
    bad = []
    for what, colour in (("the fixed palette's window colour", WINDOW_COLOUR),
                         ("Fusion's tab pane", FUSION_PANE)):
        got = share(shot, colour)
        if got < STYLE_SHARE:
            bad.append("%s #%02x%02x%02x covers %.1f %%, under %.0f %%"
                       % ((what,) + colour + (got, STYLE_SHARE)))
    return bad


# -- running the window -----------------------------------------------------------

def find_upward(relative: str):
    here = KITS_DIR
    while True:
        candidate = os.path.join(here, relative)
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def xauthority() -> str:
    """The Xvfb's cookie, or "" when it runs without -auth (CLAUDE.md)."""
    try:
        out = subprocess.run(["ps", "-o", "args=", "-C", "Xvfb"],
                             capture_output=True, text=True).stdout
    except OSError:
        return ""
    for line in out.splitlines():
        if ("Xvfb %s " % DISPLAY) in line + " " and "-auth" in line:
            parts = line.split()
            return parts[parts.index("-auth") + 1]
    return ""


def environment() -> dict:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if os.name == "nt":
        return env           # the app parks the window at -32000 itself
    env["DISPLAY"] = DISPLAY
    auth = xauthority()
    if auth:
        env["XAUTHORITY"] = auth
    else:
        env.pop("XAUTHORITY", None)
    return env


def run_app(python: str, app: str, args: list, env: dict) -> tuple:
    try:
        done = subprocess.run([python, app] + args, env=env, capture_output=True,
                              text=True, encoding="utf-8", errors="replace",
                              timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, "did not exit within %d s" % TIMEOUT
    return done.returncode, done.stdout + done.stderr


def no_display(output: str) -> bool:
    return "could not connect to display" in output or "cannot open display" in output


def capture(python, app, image, args, out, env) -> tuple:
    """(picture or None, failures, output) of one --screenshot run."""
    code, output = run_app(python, app, [image] + args + ["--screenshot", out], env)
    if code != 0:
        return None, ["app.py exited %s: %s" % (code, output.strip()[-300:])], output
    bad = []
    if os.name == "nt" and "at -32000,-32000" not in output:
        bad.append("the window was not parked off the desktop: %s" % output.strip()[-200:])
    try:
        return picture(out), bad, output
    except (OSError, BadPicture, zlib.error) as exc:
        return None, bad + ["the picture does not read: %s" % exc], output


def hover_judge(python, app, image, env, want, lang=None, points=HOVER_POINTS) -> list:
    """Every one of *points* through --hover, judged against *want*
    {point: (index, rgb)}; with *lang*, the run passes `--lang` and the
    readout is judged in it, without it the default language is."""
    bad = []
    for point in points:
        args = [image, "--tag", HOVER_TAG, "--hover", "%d,%d" % point]
        if lang:
            args += ["--lang", lang]
        code, output = run_app(python, app, args, env)
        bad += ["%s: %s" % (point, b)
                for b in judge_hover(output, code, point, want[point], lang or DEFAULT_LANG)]
    return bad


def selector_judge(python, app, image, env) -> tuple:
    """(failures, items) of `app.py --list-kits`: KIT_ITEMS items, and
    KIT_ITEM_WANT at its indices."""
    code, output = run_app(python, app, [image, "--list-kits"], env)
    items = {}
    for line in output.splitlines():
        head, sep, text = line.strip().partition(": ")
        if sep and head.startswith("kit ") and head[4:].isdigit():
            items[int(head[4:])] = text
    bad = [] if code == 0 else ["--list-kits exited %s: %s" % (code, output.strip()[-200:])]
    if len(items) != KIT_ITEMS:
        bad.append("%d item(s), not %d" % (len(items), KIT_ITEMS))
    bad += ["item %d is %r, not %r" % (i, items.get(i), want)
            for i, want in sorted(KIT_ITEM_WANT.items()) if items.get(i) != want]
    return bad, items


def diagnosis(python, app, path, args, env) -> tuple:
    """(exit, summary, [rows]) of `app.py <path> <args> --list-diagnosis`."""
    code, output = run_app(python, app, [path] + args + ["--list-diagnosis"], env)
    summary, rows = None, []
    for line in output.splitlines():
        head, sep, text = line.strip().partition(": ")
        if sep and head == "diagnosis":
            summary = text
        elif sep and head.startswith("row ") and head[4:].isdigit():
            rows.append(text)
    return code, summary, rows


def text_in_list(shot: tuple) -> int:
    """Dark pixels inside the Diagnosis list: the biggest white box of the capture."""
    w, h, pixels = shot[0], shot[1], shot[2]
    white = [i for i, p in enumerate(pixels) if p == (255, 255, 255)]
    if not white:
        return -1
    xs, ys = [i % w for i in white], [i // w for i in white]
    return sum(1 for y in range(min(ys), max(ys) + 1) for x in range(min(xs), max(xs) + 1)
               if all(c <= d for c, d in zip(pixels[y * w + x], LIST_TEXT)))


def diag_judge(python, image, env, tmp, app=APP) -> tuple:
    """(failures, what was seen) of the Diagnosis tab: a sound lone TEX lists
    nothing, its copy with the byte `cli.py tex --negative` plants lists the
    refusal of record 0, and on the European Deluxe (ED_VARIABLE) TEX_48,
    TEX_70 and TEX_13 show their own row."""
    sound = os.path.join(tmp, "TEX_%s.BIN" % FIGURE_TAG)
    if not os.path.isfile(sound):
        done = subprocess.run([sys.executable, os.path.join(TOOLS_DIR, "pes2", "iso.py"),
                               "extract", image, "/BIN/TEX_%s.BIN" % FIGURE_TAG, "-o", sound],
                              capture_output=True, text=True)
        if done.returncode:
            return ["iso.py extract exited %d: %s" % (done.returncode, done.stderr.strip())], []
    bad, seen = [], []
    code, summary, rows = diagnosis(python, app, sound, [], env)
    seen.append("sound %d row(s)" % len(rows))
    if code != 0 or summary is None or rows:
        bad.append("the sound TEX_%s: exit %s, %r, rows %s" % (FIGURE_TAG, code, summary, rows))
    shot, more, _ = capture(python, app, sound, ["--tab", "diag"],
                            os.path.join(tmp, "diag-sound.png"), env)
    bad += more
    if shot is not None:
        dark = text_in_list(shot)
        seen.append("%d text px in its list" % dark)
        if dark != 0:
            bad.append("the sound TEX's list has %d text pixel(s)" % dark)
    done = subprocess.run([sys.executable, os.path.join(KITS_DIR, "cli.py"), "tex",
                           "--negative", sound], capture_output=True, text=True)
    first = done.stdout.splitlines()[0] if done.stdout else ""
    try:
        at = int(first.split("byte ", 1)[1].split()[0])
        after = int(first.split("-> ", 1)[1].split()[0], 16)
    except (IndexError, ValueError):
        return bad + ["cli.py tex --negative said %r" % first], seen
    with open(sound, "rb") as fh:
        data = bytearray(fh.read())
    data[at] = after
    planted = os.path.join(tmp, "TEX_%s_planted.BIN" % FIGURE_TAG)
    with open(planted, "wb") as fh:
        fh.write(bytes(data))
    code, summary, rows = diagnosis(python, app, planted, [], env)
    seen.append("planted %d row(s)" % len(rows))
    if code != 0 or not any(r.startswith("Refused: record 0 (") for r in rows):
        bad.append("byte %d planted: exit %s, %r, rows %s" % (at, code, summary, rows))
    shot, more, _ = capture(python, app, planted, ["--tab", "diag"],
                            os.path.join(tmp, "diag-planted.png"), env)
    bad += more
    if shot is not None and text_in_list(shot) <= 0:
        bad.append("the refused TEX's list draws no text")
    ed = os.environ.get(ED_VARIABLE)
    if ed:
        for tag, want in ED_DIAG:
            code, summary, rows = diagnosis(python, app, ed, ["--tag", tag], env)
            seen.append("ED TEX_%s %d row(s)" % (tag, len(rows)))
            if code != 0 or not any(r.startswith(want) for r in rows):
                bad.append("ED TEX_%s: exit %s, no row starting %r in %s"
                           % (tag, code, want, rows))
    else:
        seen.append("ED not checked, %s unset" % ED_VARIABLE)
    return bad, seen


def reset_judge(python, image, env, tmp, app=APP) -> tuple:
    """(failures, digests): the 3D turned away and reset -- by the button
    (--reset) or by a double click on the view (--double-click,
    CORR-KITS-064) -- is the 3D as it opens, and the same turn without
    either is not (the control)."""
    import hashlib

    base = ["--tag", FIGURE_TAG, "--tab", "3d"]
    runs = {"reset": base + list(RESET_TURN) + ["--reset"], "opened": base,
            "turned": base + list(RESET_TURN),
            "double-click": base + list(RESET_TURN) + ["--double-click"]}
    bad, digests = [], {}
    for name, args in runs.items():
        out = os.path.join(tmp, "reset-%s.png" % name)
        shot, more, _ = capture(python, app, image, args, out, env)
        bad += ["%s: %s" % (name, m) for m in more]
        if shot is None:
            return bad + ["%s: no picture" % name], digests
        with open(out, "rb") as fh:
            digests[name] = hashlib.sha256(fh.read()).hexdigest()
    if digests["reset"] != digests["opened"]:
        bad.append("reset gives %s, the opened view %s"
                   % (digests["reset"][:12], digests["opened"][:12]))
    if digests["double-click"] != digests["opened"]:
        bad.append("the double click gives %s, the opened view %s"
                   % (digests["double-click"][:12], digests["opened"][:12]))
    if digests["turned"] == digests["opened"]:
        bad.append("the turn without reset draws the opened view: the control measures nothing")
    return bad, digests


def cli_export(image: str, out: str) -> tuple:
    """The work bitmap HOVER_TAG as the CLI writes it, decoded here."""
    done = subprocess.run([sys.executable, os.path.join(KITS_DIR, "cli.py"), "export",
                           "--work-bitmap", "--tag", HOVER_TAG, "--out", out, image],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if done.returncode:
        raise BadPicture("cli.py export exited %d: %s" % (done.returncode, done.stderr.strip()))
    shot = picture(os.path.join(out, HOVER_PNG))
    if shot[3] is None:
        raise BadPicture("%s is not indexed" % HOVER_PNG)
    return shot


def sandbox(tmp: str, old: str, new: str, target: str = "app.py") -> str:
    """A copy of tools/{kits,looks,pes2} with *old* replaced once in
    tools/kits/ui/*target*; returns the copied app."""
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    for sub in COPIED:
        shutil.copytree(os.path.join(TOOLS_DIR, sub), os.path.join(tmp, "tools", sub),
                        ignore=ignore)
    app = os.path.join(tmp, "tools", "kits", "ui", "app.py")
    path = os.path.join(tmp, "tools", "kits", "ui", target)
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    if text.count(old) != 1:
        raise BadPicture("the plant %r matches %d time(s) in %s, not once"
                         % (old.strip(), text.count(old), target))
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(text.replace(old, new))
    return app


def view_box(shot: tuple):
    """(left, top, right, bottom) of the 3D view: the box of its backdrop colour."""
    w = shot[0]
    at = [i for i, p in enumerate(shot[2]) if p == BACKDROP_3D]
    if not at:
        return None
    xs, ys = [i % w for i in at], [i // w for i in at]
    return min(xs), min(ys), max(xs), max(ys)


def differing_in_view(one: tuple, two: tuple) -> int:
    """Pixels that differ inside the 3D view of *one*: the selectors above it
    name the set, so the whole capture differs even when the figure does not."""
    box = view_box(one)
    if box is None or one[:2] != two[:2]:
        return -1
    w = one[0]
    return sum(1 for y in range(box[1], box[3] + 1) for x in range(box[0], box[2] + 1)
               if one[2][y * w + x] != two[2][y * w + x])


def figure_judge(python, image, env, tmp, app=APP) -> tuple:
    """(failures, {(set, figure): sha256 of the capture}) of the four 3D captures."""
    import hashlib

    bad, shots, digests = [], {}, {}
    for kit_set, figure in FIGURE_COMBOS:
        out = os.path.join(tmp, "3d-%d-%d.png" % (kit_set, figure))
        shot, more, _ = capture(python, app, image, ["--tag", FIGURE_TAG, "--tab", "3d",
                                                     "--kit-set", str(kit_set),
                                                     "--figure", str(figure)], out, env)
        bad += ["set %d figure %d: %s" % (kit_set, figure, m) for m in more]
        if shot is None:
            continue
        with open(out, "rb") as fh:
            digests[(kit_set, figure)] = hashlib.sha256(fh.read()).hexdigest()
        cover = 100.0 - share(shot, BACKDROP_3D) - share(shot, WINDOW_COLOUR) \
            - share(shot, FUSION_PANE)
        if share(shot, BACKDROP_3D) < 10.0 or cover < FIGURE_FLOOR:
            bad.append("set %d figure %d: backdrop %.1f %%, the rest %.1f %%: no 3D view"
                       % (kit_set, figure, share(shot, BACKDROP_3D), cover))
        shots[(kit_set, figure)] = shot
    for figure in (0, 1):
        one, two = shots.get((1, figure)), shots.get((2, figure))
        if one is not None and two is not None and differing_in_view(one, two) <= 0:
            bad.append("figure %d: set 2 draws the same figure as set 1" % figure)
    return bad, digests


def off_judge(python, image, env, tmp, app=APP) -> list:
    """A lone TEX with WE2002_LOOKS_IMAGE unset: the 3D tab refuses with the
    sentence, and the Plan capture differs from the one with the variable only
    in the note rows at the bottom and in the 3D tab's label, which greys."""
    lone = os.path.join(tmp, "TEX_%s.BIN" % FIGURE_TAG)
    done = subprocess.run([sys.executable, os.path.join(TOOLS_DIR, "pes2", "iso.py"), "extract",
                           image, "/BIN/TEX_%s.BIN" % FIGURE_TAG, "-o", lone],
                          capture_output=True, text=True)
    if done.returncode:
        return ["iso.py extract exited %d: %s" % (done.returncode, done.stderr.strip())]
    bare = dict(env)
    bare.pop(IMAGE_VARIABLE, None)
    bad = []
    code, output = run_app(python, app, [lone, "--tab", "3d", "--screenshot",
                                         os.path.join(tmp, "off.png")], bare)
    if code != 3 or "WE2002_LOOKS_IMAGE" not in output or os.path.exists(os.path.join(tmp, "off.png")):
        bad.append("--tab 3d with no geometry: exit %s, %r" % (code, output.strip()[-200:]))
    without, more, _ = capture(python, app, lone, [], os.path.join(tmp, "plan-off.png"), bare)
    with_, more2, _ = capture(python, app, lone, [], os.path.join(tmp, "plan-on.png"), env)
    bad += more + more2
    if without is not None and with_ is not None:
        if without[:2] != with_[:2]:
            bad.append("the Plan tab changes size: %dx%d against %dx%d"
                       % (without[0], without[1], with_[0], with_[1]))
        else:
            w, h = without[0], without[1]
            above = [(i % w, i // w) for i, (a, b) in enumerate(zip(without[2], with_[2]))
                     if a != b and i // w < h - NOTE_ROWS]
            if not above:
                bad.append("the 3D tab's label does not grey")
            else:
                xs, ys = [p[0] for p in above], [p[1] for p in above]
                box = (max(xs) - min(xs) + 1, max(ys) - min(ys) + 1, max(ys))
                if box[0] > TAB_LABEL[0] or box[1] > TAB_LABEL[1] or box[2] > TAB_LABEL[2]:
                    bad.append("%d pixel(s) differ above the note rows, in a %dx%d box down to "
                               "row %d: more than the tab label" % ((len(above),) + box))
            if differing(without, with_) == 0:
                bad.append("the note does not change with the geometry: the sentence is not shown")
    return bad


class Tally:
    def __init__(self) -> None:
        self.failures = 0

    def ok(self, what: str, bad: list) -> None:
        print("  %s  %s" % ("ok  " if not bad else "FAIL", what))
        for b in bad:
            print("        %s" % b)
        self.failures += bool(bad)


def run(python: str, image: str) -> int:
    env = environment()
    t = Tally()
    with tempfile.TemporaryDirectory(prefix="kits-ui-") as tmp:
        first, bad, output = capture(python, APP, image, STATE, os.path.join(tmp, "a.png"), env)
        if first is None and no_display(output):
            print("kits_ui: skipped -- no display %s (Xvfb %s -screen 0 1280x1024x24 "
                  "-nolisten tcp &)" % (DISPLAY, DISPLAY))
            return SKIP
        t.ok("the window comes up off the desktop and writes a picture", bad)
        if first is None:
            print("kits_ui: %d failure(s)" % t.failures)
            return 1
        print("        %dx%d" % (first[0], first[1]))
        t.ok("the picture shows something", judge_frame(first))
        t.ok("the look is the fixed one: palette window colour %.1f %%, Fusion pane %.1f %%"
             % (share(first, WINDOW_COLOUR), share(first, FUSION_PANE)), judge_style(first))

        again, bad, _ = capture(python, APP, image, STATE, os.path.join(tmp, "b.png"), env)
        n = differing(first, again) if again is not None and again[:2] == first[:2] else -1
        t.ok("the same state twice is the same picture (%d px differ)" % n,
             bad + ([] if n == 0 else ["%d pixel(s) differ" % n]))

        told, bad, _ = capture(python, APP, image, STATE + ["--lang", "pt-BR"],
                               os.path.join(tmp, "pt.png"), env)
        switched, more, _ = capture(python, APP, image, STATE + ["--switch-to", "pt-BR"],
                                    os.path.join(tmp, "sw.png"), env)
        bad += more
        n = differing(told, switched) if told and switched and told[:2] == switched[:2] else -1
        m = differing(first, told) if told and told[:2] == first[:2] else -1
        t.ok("pt-BR picked in the window's selector is the window opened in pt-BR "
             "(%d px differ), and another picture than en-US (%d px)" % (n, m),
             bad + ([] if n == 0 else ["%d pixel(s) differ" % n])
             + ([] if m > 0 else ["pt-BR draws the same as en-US"]))

        other, bad, _ = capture(python, APP, image, OTHER, os.path.join(tmp, "c.png"), env)
        n = differing(first, other) if other is not None and other[:2] == first[:2] else -1
        pct = 100.0 * n / (first[0] * first[1]) if n >= 0 else -1.0
        t.ok("another kit is another picture (%d px, %.1f %%)" % (n, pct),
             bad + ([] if pct >= OTHER_FLOOR else ["under %.1f %%" % OTHER_FLOOR]))

        out = os.path.join(tmp, "missing.png")
        code, output = run_app(python, APP, [image] + MISSING_TAG + ["--screenshot", out], env)
        t.ok("a tag the disc does not have exits 2 and writes nothing (exit %s)" % code,
             [] if code == 2 and not os.path.exists(out)
             else ["exit %s, file %s" % (code, "written" if os.path.exists(out) else "absent")])

        want = {}
        try:
            ref = cli_export(image, os.path.join(tmp, "cli"))
            want = {p: expected_readout(ref, p) for p in HOVER_POINTS}
            bad = hover_judge(python, APP, image, env, want)
        except BadPicture as exc:
            bad = [str(exc)]
        t.ok("the reading under the mouse names the index and colour cli.py export writes, "
             "at %d point(s): %s" % (len(HOVER_POINTS), ", ".join(
                 "%s=%d" % (p, want[p][0]) for p in HOVER_POINTS) if want else "-"), bad)
        if want:
            bad = hover_judge(python, APP, image, env, want, "pt-BR", HOVER_POINTS[:1])
            wrong = judge_hover("  readout: x %d, y %d · index %d · RGB %d,%d,%d\n  marked: %d\n"
                                % (HOVER_POINTS[0] + (want[HOVER_POINTS[0]][0],)
                                   + want[HOVER_POINTS[0]][1] + (want[HOVER_POINTS[0]][0],)),
                                0, HOVER_POINTS[0], want[HOVER_POINTS[0]], "pt-BR")
            t.ok("with --lang pt-BR the readout says 'índice', and the judge refuses an "
                 "English one (%s)" % "; ".join(wrong)[:120],
                 bad + ([] if wrong else ["the judge took 'index' for pt-BR"]))
        code, output = run_app(python, APP, [image, "--tag", HOVER_TAG, "--hover",
                                             "%d,%d" % OFF_IMAGE], env)
        t.ok("a point off the image reads blank and exits 1 (exit %s)" % code,
             [] if code == 1 and "(blank)" in output else [output.strip()[-200:]])

        bad, items = selector_judge(python, APP, image, env)
        t.ok("the kit selector lists teams in game order: %d items, %s"
             % (len(items), "; ".join("%d %r" % (i, items.get(i)) for i in sorted(KIT_ITEM_WANT))),
             bad)

        bad, digests = figure_judge(python, image, env, tmp)
        t.ok("3D TEX_%s: the four combinations draw a figure, and set 1 is not set 2 for "
             "either figure (%s)" % (FIGURE_TAG, ", ".join(
                 "set %d fig %d %s" % (k[0], k[1], v[:12]) for k, v in sorted(digests.items()))),
             bad)
        t.ok("with no geometry disc the 3D tab is off with the sentence, and Plan is the same",
             off_judge(python, image, env, tmp))
        bad, digests = reset_judge(python, image, env, tmp)
        t.ok("Reset view and a double click after %s are the 3D as it opens, and the "
             "turn alone is not (%s)"
             % (" ".join(RESET_TURN), ", ".join("%s %s" % (k, v[:12])
                                                for k, v in sorted(digests.items()))), bad)
        bad, seen = diag_judge(python, image, env, tmp)
        t.ok("the Diagnosis tab lists the guard's refusal and the reading notes, and "
             "nothing for a sound kit (%s)" % ", ".join(seen), bad)
        if os.environ.get(ED_VARIABLE) is None:
            print("        note: %s is not set, so TEX_48, TEX_70 and TEX_13 of the "
                  "European Deluxe were not judged" % ED_VARIABLE)

        for name, judge, old, new, *target in PLANTS:
            if judge == DIAG_NOTE and os.environ.get(ED_VARIABLE) is None:
                print("        plant '%s': not judged, %s is not set and only its TEX_13 "
                      "has a note row" % (name, ED_VARIABLE))
                continue
            with tempfile.TemporaryDirectory(prefix="kits-ui-plant-") as box:
                try:
                    app = sandbox(box, old, new, *target)
                except BadPicture as exc:
                    t.ok("plant '%s'" % name, [str(exc)])
                    continue
                if judge == STYLE:
                    shot, bad, _ = capture(python, app, image, STATE,
                                           os.path.join(box, "p.png"), env)
                    red = judge_style(shot) if shot is not None else ["no picture"]
                elif judge == FIGURE:
                    red, _ = figure_judge(python, image, env, box, app)
                    bad = []
                elif judge == OFF:
                    red, bad = off_judge(python, image, env, box, app), []
                elif judge == SELECTOR:
                    red, bad = selector_judge(python, app, image, env)[0], []
                elif judge == RESET:
                    red, bad = reset_judge(python, image, env, box, app)[0], []
                elif judge in (DIAG, DIAG_NOTE):
                    red, bad = diag_judge(python, image, env, box, app)[0], []
                else:
                    bad, red = [], hover_judge(python, app, image, env, want) if want else []
                print("        plant '%s': %s" % (name, "; ".join(red)[:300] or "judge passed"))
                t.ok("plant '%s' fails the %s judge" % (name, judge),
                     bad + ([] if red else ["the window with it passed: the judge is blind"]))
    print("kits_ui: %d failure(s)" % t.failures)
    return 1 if t.failures else 0


def compare(a: str, b: str) -> int:
    """The cross-platform comparison: pixels that differ between two captures."""
    try:
        one, two = picture(a), picture(b)
    except (OSError, BadPicture, zlib.error) as exc:
        print("compare: %s" % exc, file=sys.stderr)
        return 1
    print("%s: %dx%d, window colour %.1f %%, Fusion pane %.1f %%"
          % (os.path.basename(a), one[0], one[1], share(one, WINDOW_COLOUR), share(one, FUSION_PANE)))
    print("%s: %dx%d, window colour %.1f %%, Fusion pane %.1f %%"
          % (os.path.basename(b), two[0], two[1], share(two, WINDOW_COLOUR), share(two, FUSION_PANE)))
    if one[:2] != two[:2]:
        print("different sizes: %dx%d against %dx%d" % (one[0], one[1], two[0], two[1]))
        return 1
    n = differing(one, two)
    pct = 100.0 * n / (one[0] * one[1])
    print("%d of %d pixels differ (%.2f %%)" % (n, one[0] * one[1], pct))
    red = ["%s loses the fixed look: %s" % (os.path.basename(name), "; ".join(why))
           for name, shot in ((a, one), (b, two)) for why in [judge_style(shot)] if why]
    if pct > CROSS_LIMIT:
        red.append("%.2f %% differ, above the %.1f %% limit" % (pct, CROSS_LIMIT))
    for line in red:
        print("FAIL  %s" % line)
    if not red:
        print("ok    within %.1f %%, both with the fixed look" % CROSS_LIMIT)
    return 1 if red else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--compare", nargs=2, metavar="PNG",
                        help="count the pixels that differ between two captures; "
                             "fails above %.1f %%%%" % CROSS_LIMIT)
    args = parser.parse_args(argv)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if args.compare:
        return compare(*args.compare)
    python = find_upward(os.path.join(VENV, VENV_PYTHON))
    if python is None:
        print("kits_ui: skipped -- no venv at %s (python -m venv %s; pip install PySide6)"
              % (VENV, VENV))
        return SKIP
    if subprocess.run([python, "-c", "import PySide6"], capture_output=True).returncode:
        print("kits_ui: skipped -- the venv at %s has no PySide6" % VENV)
        return SKIP
    image = os.environ.get(IMAGE_VARIABLE)
    if not image:
        print("kits_ui: skipped -- %s is not set (the Japanese data track .bin)" % IMAGE_VARIABLE)
        return SKIP
    if not os.path.isfile(image):
        print("  FAIL  %s points at a file  %s is not one" % (IMAGE_VARIABLE, image))
        print("kits_ui: 1 failure(s)")
        return 1
    return run(python, os.path.abspath(image))


if __name__ == "__main__":
    raise SystemExit(main())

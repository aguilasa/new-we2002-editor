#!/usr/bin/env python3
"""The `looks_ui` gate: the window drew something, or the test skips with 77.

FOUR THINGS CAN BE MISSING, and none of them is a failure:

  the venv with PySide6 in `work/venv-looks` -- there is no make target
      for it on this machine, and section 4.1 of the plan carries the two
      lines that build it;
  `tools/looks/ui/app.py`, which was LOOKS-TASK-15;
  `WE2002_LOOKS_IMAGE`, because a viewer with no disc has nothing to draw;
  a reachable display -- `:98` on Linux; on Windows the window parks at -32000.

Any of those exits 77, which is what tells ctest the test skipped.

**AND THERE IS NO FIFTH PATH.**  Either this file judged a picture or it
skipped: it never prints a `note:` about what it could not measure and passes
anyway.  That is the exact shape the `mcr_ui` target had -- green with the
window alone whenever the fixture was missing, and a line nobody read -- and
section 4.4 of the plan names it as the thing this gate must not repeat.

WHAT IT JUDGES, and the order matters:

  `--smoke` comes up, paints, reports counts and exits 0;
  `--screenshot` writes a PNG of the size asked for;
  the PNG is **not a blank frame** -- more than one colour, and the background
      does not cover the whole picture;
  the same tuple twice is **byte-identical**, which is what makes the next
      line mean anything;
  two tuples that differ in one field produce **different pictures**, by at
      least the floor measured on 2026-09-16;
  a tuple the assembly table refuses exits **2** and writes no file.

IT DECODES THE PNG ITSELF, in the standard library, and that is the whole
point of the file.  `app.py --compare` exists and is run -- its answer has to
agree with this one to the pixel -- but it is the code under test, and a gate
that asks the subject how different its own two pictures are is the defect
CORR-MCR-018 measured in the other cycle: the judge was comparing the
conversion against itself, and removing the arithmetic left the run green.
Here the pixels are counted twice, by two pieces of code that share nothing,
and the two counts have to match.

THE DISPLAY RULE HAS TWO HALVES, one per platform, and `CLAUDE.md` carries
both.  On Linux every GUI run goes to `:98` -- `:1` is the user's real session
-- and the server runs without `-auth`, so an EMPTY `XAUTHORITY` is the correct
value; this file resolves it the way `make run-98` does.  On Windows there is
no Xvfb and the window is parked off the desktop at -32000 by `app.py` itself,
which this gate then confirms out of the app's own report.

Usage:
    python tools/looks/ui_check.py
    ctest -R looks_ui
"""

from __future__ import annotations

import ast
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import harness  # noqa: E402
import layout  # noqa: E402
import screen  # noqa: E402

SKIP = 77
LOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
APP = os.path.join(LOOKS_DIR, "ui", "app.py")
DISPLAY = ":98"
TIMEOUT = 300

VENV = os.path.join("work", "venv-looks")
VENV_PYTHON = (os.path.join("Scripts", "python.exe") if os.name == "nt"
               else os.path.join("bin", "python"))

PARKED = -32000  # not-an-address: the parking spot CLAUDE.md names, in pixels
"""Where the window has to be, and the gate reads it back out of the report.

Windows has no Xvfb, so this number IS the rule there: a window that came up
anywhere else opened on the user's screen.
"""

SIZE = (640, 640)
"""The picture the gate asks for, and then insists on getting.

Both halves matter: a viewer that ignored `--size` would still write a PNG, and
`grabFramebuffer` returns whatever the widget happens to be, so the size is
read back out of the file rather than assumed.
"""

REFERENCE = "A-A1-A-A-A"
"""The tuple drawn twice, to prove the viewer does not wobble between runs."""

PAIRS = (
    ("A-A1-A-A-A", "B-A1-A-A-A", "SKIN", 40.0),
    ("A-A1-A-A-A", "A-A1-C-A-A", "H.COL", 12.0),
    ("A-I3-A-A-A", "B-I3-A-A-A", "SKIN", 10.0),
)
"""(the tuple to start from, the tuple to compare, the row, the floor in %).

Measured with `--piece head` at 640x640.  On 2026-09-16: `B-A1-A-A-A` differs
from `A-A1-A-A-A` in **47.13%** of the pixels and `A-A1-C-A-A` in **17.17%**.
The floors sit under those and well over nothing, because what they have to
catch is a viewer that draws the same boneco for every tuple -- which answers
0.00%, not 39%.  They are not a tolerance on the rendering: this gate does not
own what the picture looks like, only that the tuple reached it.

**Each pair carries its own base, and that is why the third exists.**  The
first two are family A, which wears MODEL.BIN section 24 -- the only head the
colour rows reached until CORR-LOOKS-034, so this gate ran green through that
whole defect while `scene --check-image` went red on it.  A gate whose sample
avoids the broken region is not a weaker gate; it is one that does not cover
what it says it covers.  `B-I3-A-A-A` against `A-I3-A-A-A` wears section 34 and
moves **14.54%** of the pixels, measured the same day, and its floor is its
own: the I3 head answers a skin change with less of the picture than A1 does,
so copying A1's 40% would have failed a working viewer.

**Remeasured after CORR-LOOKS-042**, which moved every hair quad a texel row to
where the game's store puts it: 48.29%, 15.81% and 13.66%.  The three floors
hold with the same room, and the figures above stay as what that day's tree
measured.
"""

POSED_FRAME = 0
"""The frame of the screen's walk the assembled figure is judged on.

Frame 0 of `scene.REFERENCE_FRAME`, spelled here rather than imported: the
gate judges the window from outside, and a floor that read its number out of
the code under test would move with it.
"""

REFUSED = "A-H1-A-A-A"
"""A tuple the assembly table refuses, and the exit code is the contract.

`HAIR=H1` wrote nothing to either model file when the map was walked, on both
figures, so which head it draws is not known and the table raises instead of
drawing somebody else's.  This was `A-A1-A-F-A` until CORR-LOOKS-048 measured
what beard F draws -- a refusal tuple has to be one the table still refuses,
or the gate reddens a working viewer.  The gate demands
exit 2 and NO file: a refusal that still writes a picture would be drawn from
something, and that something would be invented.
"""

REFUSED_TEXT = "H1 TYPE"
"""What the game writes for the hair style the table refuses.

The text, not the label: `REFUSED` above is a tuple this gate spells, and this
is what the SCREEN shows for the same style -- measured, and the difference
between the two is the whole reason `screen.json` exists.
"""

PIECE = "head"
"""The head alone, which is the piece every tuple of this gate changes.

The whole figure draws too, and the differences would be diluted by the eleven
sections no LOOKS row touches -- the floors above would then be measuring the
body's share of the frame rather than the field's effect.
"""

BLANK_COLOURS = 2
"""How many distinct colours make a picture not-blank, at the least.

One colour is the clear colour and nothing else: `paintGL` returning early
before it draws writes exactly that, and the file saves without complaint at
very nearly the same size.  Measured on the real shots: 15 to 19 colours, and
the background covers 38.47%.
"""

BACKGROUND_CEILING = 95.0
"""The most of a picture the single commonest colour may cover.

The 38.47% measured leaves this a long way off; it is here for the frame that
draws one stray triangle and is otherwise the clear colour, which passes the
colour count above and is still nothing to look at.
"""


BYTE = 0xFF  # not-an-address: the width of a PNG sample, in the filter
"""What a filtered sample wraps at.

Named once so the five places the PNG filters use it do not each read as
an address to rule 1's sweep -- and because a literal that appears five
times is a literal somebody will change in four of them.
"""


class BadPicture(Exception):
    """A PNG this gate will not pretend to have read."""


# ---- the picture, decoded here and not by the code under test -------------

def read_png(data: bytes) -> tuple:
    """(width, height, channels, [row bytes]) out of 8-bit RGB or RGBA.

    The standard library reaches all of it -- zlib for the stream, struct for
    the chunks, and the five filters of the spec by hand -- so the gate needs
    neither PIL nor Qt to say what is in the file.  Anything it does not
    recognise RAISES: an interlaced or 16-bit PNG read as if it were this one
    would come back as pixels, and they would be wrong quietly.
    """
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise BadPicture("not a PNG: the signature is %r" % data[:8])
    at, parts, head = 8, [], None
    while at + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[at:at + 8])
        body = data[at + 8:at + 8 + length]
        if len(body) != length:
            raise BadPicture("the %s chunk is short: %d of %d byte(s)"
                             % (kind.decode("ascii", "replace"), len(body),
                                length))
        if kind == b"IHDR":
            head = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            parts.append(body)
        at += 12 + length
    if head is None:
        raise BadPicture("the file has no IHDR")
    width, height, depth, colour, _compression, _filter, interlace = head
    if depth != 8 or colour not in (2, 6) or interlace:
        raise BadPicture("depth %d, colour type %d, interlace %d -- this "
                         "reader does 8-bit RGB and RGBA only"
                         % (depth, colour, interlace))
    if not parts:
        raise BadPicture("the file has no IDAT")

    channels = 3 if colour == 2 else 4
    raw = zlib.decompress(b"".join(parts))
    stride = width * channels
    if len(raw) != (stride + 1) * height:
        raise BadPicture("the pixels unpack to %d byte(s) and %dx%d needs %d"
                         % (len(raw), width, height, (stride + 1) * height))

    rows, previous, at = [], bytearray(stride), 0
    for _ in range(height):
        kind = raw[at]
        at += 1
        line = bytearray(raw[at:at + stride])
        at += stride
        if kind:
            _unfilter(kind, line, previous, channels, stride)
        rows.append(bytes(line))
        previous = line
    return (width, height, channels, rows)


def _unfilter(kind: int, line: bytearray, previous: bytearray,
              channels: int, stride: int) -> None:
    """One scanline, in place.  The five filters of the PNG spec."""
    if kind > 4:
        raise BadPicture("filter type %d is not one of the five" % kind)
    for i in range(stride):
        left = line[i - channels] if i >= channels else 0
        up = previous[i]
        upleft = previous[i - channels] if i >= channels else 0
        if kind == 1:
            line[i] = (line[i] + left) & BYTE
        elif kind == 2:
            line[i] = (line[i] + up) & BYTE
        elif kind == 3:
            line[i] = (line[i] + (left + up) // 2) & BYTE
        elif kind == 4:
            guess = left + up - upleft
            da, db, dc = (abs(guess - left), abs(guess - up),
                          abs(guess - upleft))
            nearest = left if (da <= db and da <= dc) else (up if db <= dc
                                                            else upleft)
            line[i] = (line[i] + nearest) & BYTE


def picture(path: str) -> tuple:
    with open(path, "rb") as handle:
        return read_png(handle.read())


def colours(shot: tuple) -> dict:
    """{pixel: how many}, the alpha included, over one picture."""
    width, _height, channels, rows = shot
    seen: dict = {}
    for row in rows:
        for x in range(width):
            key = row[x * channels:(x + 1) * channels]
            seen[key] = seen.get(key, 0) + 1
    return seen


def differing(one: tuple, two: tuple) -> int:
    """How many pixels differ.  Raises when the two are not the same shape."""
    if one[:3] != two[:3]:
        raise BadPicture("%dx%d with %d channel(s) against %dx%d with %d"
                         % (one[0], one[1], one[2], two[0], two[1], two[2]))
    width, _height, channels, rows = one
    return sum(1 for row, other in zip(rows, two[3])
               for x in range(width)
               if row[x * channels:(x + 1) * channels]
               != other[x * channels:(x + 1) * channels])


def percent(count: int, shot: tuple) -> float:
    return 100.0 * count / (shot[0] * shot[1])


# ---- the judges, which the planted runs below use unchanged ---------------

def judge_frame(name: str, shot: tuple) -> list:
    """Everything wrong with one picture.  Empty is the pass."""
    bad = []
    if (shot[0], shot[1]) != SIZE:
        bad.append("%s came out %dx%d and the gate asked for %dx%d"
                   % (name, shot[0], shot[1], SIZE[0], SIZE[1]))
    seen = colours(shot)
    if len(seen) < BLANK_COLOURS:
        bad.append("%s is one flat colour -- a blank frame, not a drawing"
                   % name)
    top = max(seen.values())
    if percent(top, shot) > BACKGROUND_CEILING:
        bad.append("%s is %.2f%% one colour, over the %.1f%% ceiling"
                   % (name, percent(top, shot), BACKGROUND_CEILING))
    return bad


def judge_pairs(shots: dict, theirs: dict) -> list:
    """The pictures against each other, and against `--compare`'s answer.

    `shots` is {tuple: picture} and `theirs` {tuple: what app.py --compare
    counted}.  Both halves are judged here so that the planted runs below get
    exactly this verdict and not a second implementation of it.
    """
    bad = []
    for start, name, row, floor in PAIRS:
        base = shots[start]
        count = differing(base, shots[name])
        share = percent(count, base)
        if share < floor:
            bad.append("%s moves %s and differs from %s in %.2f%% of the "
                       "pixels, under the %.1f%% floor -- the tuple did not "
                       "reach the picture" % (name, row, start, share, floor))
        if name in theirs and theirs[name] != count:
            bad.append("the gate counted %d differing pixel(s) between %s and "
                       "%s and app.py --compare counted %d"
                       % (count, start, name, theirs[name]))
    return bad


STANDING = 1.8
"""How much taller than wide the POSED figure's ink has to be.

Measured 2026-09-18 at 640x640 on `A-A1-A-A-A`: the assembled figure's ink box
is 187x521, a ratio of 2.79; the shelf's is 520x136, a ratio of 0.26; and the
PILE -- every piece at its own origin -- is 292x511, a ratio of 1.75.

**And it is said here what this floor does not catch.**  A pose read one piece
off still draws something tall, so the ratio separates a figure from a pile and
from a shelf and nothing finer; what says the pieces are in the right ORDER is
`scene.standing`, against the disc, in `scene.py --check-image`.  A gate that
claimed the ratio for that would be claiming a coverage it does not have.
"""

LYING = 0.6
"""And how much wider than tall the SHELF has to stay.

The shelf is the other half of the same judgement: without it a viewer that
ignored `--frame` entirely would draw the same picture twice and clear any
floor written about one of them.
"""


def ink_box(shot: tuple) -> tuple:
    """(width, height, pixels) of everything that is not the background.

    The background is the commonest colour, which is how the rest of this file
    already reads a picture -- there is no agreement with the viewer about
    what it paints behind the figure, and there should not be.
    """
    width, _height, channels, rows = shot
    back = max(colours(shot).items(), key=lambda one: one[1])[0]
    left = top = None
    right = bottom = -1
    drawn = 0
    for y, row in enumerate(rows):
        for x in range(width):
            if row[x * channels:(x + 1) * channels] == back:
                continue
            drawn += 1
            left = x if left is None else min(left, x)
            right = max(right, x)
            top = y if top is None else min(top, y)
            bottom = max(bottom, y)
    if not drawn:
        return (0, 0, 0)
    return (right - left + 1, bottom - top + 1, drawn)


def judge_posed(posed: tuple, shelved: tuple, piled: tuple = None) -> list:
    """The assembled figure against the two pictures it is not.  [] is a pass.

    Three things it must not be, and the third is the one that matters: the
    SHELF (pieces in a row), the PILE (every piece at its own origin, which is
    what neither model file says where to put -- pitfall 24), and a picture
    lying on its side.  The pile is drawn on purpose rather than reasoned
    about, because a pose that reached nothing draws exactly it -- and its ink
    is 1.75 tall for one wide against the standing figure's 2.70, which is far
    too close a call to leave to a ratio.
    """
    bad = []
    wide, tall, drawn = ink_box(posed)
    if not drawn:
        return ["the posed figure drew nothing at all"]
    ratio = tall / float(wide)
    if ratio < STANDING:
        bad.append("the posed figure's ink is %dx%d, %.2f tall for one wide, "
                   "under the %.1f a standing figure takes -- this is what a "
                   "pose read one piece off looks like"
                   % (wide, tall, ratio, STANDING))
    shelf_wide, shelf_tall, shelf_drawn = ink_box(shelved)
    if not shelf_drawn:
        return bad + ["the shelf drew nothing at all"]
    shelf_ratio = shelf_tall / float(shelf_wide)
    if shelf_ratio > LYING:
        bad.append("the shelf's ink is %dx%d, %.2f tall for one wide, over "
                   "the %.1f it takes for a row of pieces -- the shelf and "
                   "the pose are not telling apart"
                   % (shelf_wide, shelf_tall, shelf_ratio, LYING))
    if not differing(posed, shelved):
        bad.append("the posed figure and the shelf are the same picture, so "
                   "--frame reached nothing")
    if piled is not None and not differing(posed, piled):
        bad.append("the posed figure is the PILE -- every piece at its own "
                   "origin, which is where neither model file puts it -- so "
                   "the pose reached no point")
    return bad


def measure_posed(python: str, app: str, where: str, env: dict) -> tuple:
    """The whole figure and the same figure POSED.  `(bad, broke, shots)`.

    It is a function and not four lines inside `main` for the reason the
    first run of this gate wrote down: the planted trees run what this file
    calls, so a judgement that lives only in `main` is one no control can
    redden -- and a control that cannot go red is the thing this whole file
    exists to refuse.
    """
    entire, output = draw(python, app, REFERENCE,
                          os.path.join(where, "whole.png"), env, piece="all")
    if entire is None:
        return ([], "the whole figure did not draw: %s" % output.rstrip(),
                None)
    posed, output = draw(python, app, REFERENCE,
                         os.path.join(where, "posed.png"), env,
                         piece="all", frame=POSED_FRAME)
    if posed is None:
        return ([], "the posed figure did not draw: %s" % output.rstrip(),
                None)
    piled, output = draw(python, app, REFERENCE,
                         os.path.join(where, "piled.png"), env,
                         piece="all", shelf=False)
    if piled is None:
        return ([], "the pile did not draw: %s" % output.rstrip(), None)
    bad = (judge_frame("the whole figure", entire)
           + judge_frame("the posed figure", posed)
           + judge_posed(posed, entire, piled))
    return (bad, "", (entire, posed))


def judge_repeat(first: tuple, again: tuple) -> list:
    """The same tuple drawn twice.  Anything but identical is a finding.

    It is not a nicety: every floor above is a difference between two runs of
    the same program, so a viewer that wobbled frame to frame would clear them
    while proving nothing about the tuple.
    """
    count = differing(first, again)
    if count:
        return ["%s drawn twice differs from itself in %d pixel(s) (%.2f%%), "
                "so a difference between two tuples proves nothing"
                % (REFERENCE, count, percent(count, first))]
    return []


# ---- running the app ------------------------------------------------------

def find_upward(relative: str) -> str | None:
    """Walks up from this file looking for `relative`; `None` if never found.

    Upward and not a fixed number of `dirname` hops, for the reason the .mcr
    cycle wrote down: every planted copy of the tree below sits at a different
    depth, and a counted path would send it to a directory that does not
    exist -- which reads as "no venv", skips, and turns a control green.
    """
    here = os.path.dirname(os.path.abspath(__file__))
    while True:
        candidate = os.path.join(here, relative)
        if os.path.exists(candidate):
            return candidate
        parent = os.path.dirname(here)
        if parent == here:
            return None
        here = parent


def venv_python() -> str | None:
    found = find_upward(os.path.join(VENV, VENV_PYTHON))
    return found if found and os.access(found, os.X_OK) else None


def xauthority() -> str:
    """The Xvfb's own cookie, or the empty string when it has none.

    Empty is the ANSWER and not a failure: the server of `CLAUDE.md` runs
    without `-auth`, and inheriting the desktop's cookie is what breaks Qt with
    `Invalid MIT-MAGIC-COOKIE-1 key`.
    """
    try:
        out = subprocess.run(["ps", "-o", "args=", "-C", "Xvfb"],
                             capture_output=True, text=True).stdout
    except OSError:
        return ""
    for line in out.splitlines():
        if "Xvfb %s " % DISPLAY in line + " " and "-auth" in line:
            parts = line.split()
            return parts[parts.index("-auth") + 1]
    return ""


def environment() -> dict:
    """The environment the app runs in, which is where the display rule lives."""
    env = dict(os.environ)
    if os.name == "nt":
        # No Xvfb here, and no DISPLAY to set: app.py parks the window at
        # -32000 before showing it, which is the Windows half of the rule.
        return env
    env["DISPLAY"] = DISPLAY
    auth = xauthority()
    if auth:
        env["XAUTHORITY"] = auth
    else:
        env.pop("XAUTHORITY", None)
    return env


def run_app(python: str, app: str, args: list, env: dict):
    """(exit code, output) of one app run, or (None, output) when it hung.

    Decoded as UTF-8 and not by the console's own codec: the help of a row
    carries the button glyph, this machine's default is cp1252, and a gate that
    died reading its subject's output would be red for the one cause that says
    nothing about the window (CORR-LOOKS-055).
    """
    try:
        done = subprocess.run([python, app] + args, env=env,
                              capture_output=True, text=True, timeout=TIMEOUT,
                              encoding="utf-8", errors="replace")
    except subprocess.TimeoutExpired:
        return (None, "did not exit within %ds" % TIMEOUT)
    return (done.returncode, done.stdout + done.stderr)


def draw(python: str, app: str, name: str, out: str, env: dict,
         piece: str = None, frame: int = None, shelf: bool = True):
    """One tuple to one PNG.  `(picture, output)`; picture None on failure."""
    code, output = run_app(python, app,
                           ["--looks", name, "--piece", piece or PIECE,
                            "--size", "%dx%d" % SIZE, "--screenshot", out]
                           + ([] if frame is None
                              else ["--frame", str(frame)])
                           + ([] if shelf else ["--no-shelf"]),
                           env)
    if code or not os.path.isfile(out):
        return (None, output)
    return (picture(out), output)


WHOLE = {"primitives": 100, "sections": 2, "textured": 1}
"""The floors the WHOLE FIGURE has to clear, in the `--smoke` report.

Not the head's numbers and not the disc's: the smallest statement that
separates a figure from one piece of it.  The head alone is 18 primitives in
one section and the figure the viewer draws is 593 in twelve, so a body that
vanished comes back as 18 and 1 and trips these.

They exist because `--piece head` is right for the colour pairs -- the head is
the piece those tuples change -- and it left eleven of the twelve pieces
outside every judgement this file makes.  The `--smoke` line already printed
these counts and the gate threw them away (CORR-LOOKS-040).
"""


def _counted(output: str) -> dict:
    """The counts out of `app.py --smoke`, as a dict, or {} if the line is gone.

    Parsed rather than trusted: the numbers are the app's own report, so this
    gate reads them the way it reads a PNG -- evidence produced by the code
    under test, checked against a floor it does not get to choose.
    """
    found = {}
    for line in output.splitlines():
        if "primitive(s)" in line and "textured" in line:
            words = line.replace(",", " ").split()
            for index, word in enumerate(words):
                if index and word.startswith("primitive("):
                    found["primitives"] = int(words[index - 1])
                elif word == "textured":
                    found["textured"] = int(words[index - 1])
        if line.strip().startswith("sections "):
            found["sections"] = int(line.split()[1].rstrip(","))
    return found


def judge_whole(counts: dict) -> list:
    """The figure the smoke run drew, by its own counts.  [] is the pass."""
    bad = []
    if not counts:
        return ["app.py --smoke printed no counts, so nothing says the figure "
                "it drew is a figure and not one piece of it"]
    for name, floor in sorted(WHOLE.items()):
        if counts.get(name, 0) < floor:
            bad.append("the whole figure came out with %s %s and the floor is "
                       "%d -- eleven of the twelve pieces are the body, and a "
                       "body that did not draw looks exactly like this"
                       % (name, counts.get(name, "missing"), floor))
    # And DRESSED: every primitive textured, not merely more than one.  The
    # body's pages are in the kit container (LOOKS-TASK-30), and a figure that
    # lost it draws 237 of its 593 primitives grey while clearing every floor
    # above.
    if counts.get("textured") != counts.get("primitives"):
        bad.append("the whole figure drew %s primitive(s) and textured %s of "
                   "them -- the ones left over are the body, and they are grey "
                   "when the kit container did not reach the draw list"
                   % (counts.get("primitives"), counts.get("textured")))
    return bad


def _compared(output: str) -> int | None:
    """The pixel count out of `app.py --compare`'s line, or None."""
    for line in output.splitlines():
        if "pixel(s) differ" in line:
            words = line.split()
            for index, word in enumerate(words):
                if word == "of" and index:
                    try:
                        return int(words[index - 1])
                    except ValueError:
                        return None
    return None


def measure(python: str, app: str, where: str, env: dict) -> tuple:
    """Draw everything this gate judges.  `(shots, theirs, problems, broke)`.

    `broke` is separate from `problems` on purpose, and it is what the planted
    runs below read: a tree that does not run at all fails every judgement
    without any of them having measured anything, and reading that as "the
    control went red" proves nothing.  Measured the first time this gate ran --
    all three controls reported red, and all three had died at `import lzss`.
    """
    shots, theirs, bad = {}, {}, []
    wanted = [REFERENCE]
    for start, name, _row, _floor in PAIRS:
        wanted += [one for one in (start, name) if one not in wanted]
    for name in wanted:
        shot, output = draw(python, app, name,
                            os.path.join(where, "%s.png" % name), env)
        if shot is None:
            return (shots, theirs, bad,
                    "%s did not draw: %s" % (name, output.rstrip()))
        shots[name] = shot
        bad += judge_frame(name, shot)

    again, output = draw(python, app, REFERENCE,
                         os.path.join(where, "again.png"), env)
    if again is None:
        return (shots, theirs, bad,
                "%s did not draw a second time: %s"
                % (REFERENCE, output.rstrip()))
    bad += judge_repeat(shots[REFERENCE], again)

    for start, name, _row, _floor in PAIRS:
        code, output = run_app(
            python, app,
            ["--compare", os.path.join(where, "%s.png" % start),
             os.path.join(where, "%s.png" % name)], env)
        counted = _compared(output) if code == 0 else None
        if counted is None:
            bad.append("app.py --compare %s did not report a pixel count: %s"
                       % (name, output.rstrip()))
        else:
            theirs[name] = counted

    bad += judge_pairs(shots, theirs)
    return (shots, theirs, bad, "")


# ---- the screen, judged by key --------------------------------------------

TUPLE_ROWS = ("SKIN", "HAIR", "H.COL", "FACE", "H.F.COL.")
"""The five rows a press of which has to reach the figure.

They are the five of `looks.TUPLE_ORDER`, and the gate spells them here rather
than importing that list so that a row silently dropped from the tuple shows up
as a disagreement instead of as two files agreeing with each other.
"""


def read_screen(output: str) -> dict:
    """The screen's report out of `app.py`, as a dict, or {} if it is not there.

    Parsed, never reconstructed: these are the window's own words about what it
    draws, and the whole judgement below is that they agree with `screen.py`.
    """
    seen: dict = {"rows": {}}
    for line in output.splitlines():
        text = line.strip()
        if text.startswith("screen: slot "):
            # Cut at the two field names and not by splitting on ", ": the
            # help box carries the refusal sentence when there is one, commas
            # and all, and a split ate it the first time this ran.
            head, _, rest = text[len("screen: slot "):].partition(", cursor ")
            seen["slot"] = head
            where, _, helped = rest.partition(", help ")
            seen["cursor"] = where
            if helped:
                seen["help"] = ast.literal_eval(helped)
        elif text.startswith("row "):
            name, _, value = text[len("row "):].partition(" = ")
            seen["rows"][name.strip()] = ast.literal_eval(value)
        elif text.startswith("tuple "):
            head, _, built = text[len("tuple "):].partition(", scene built ")
            seen["tuple"] = head
            seen["builds"] = int(built.split()[0]) if built else None
        elif text.startswith("presses "):
            seen["presses"] = text[len("presses "):]
        elif text.startswith("refused: "):
            seen["refused"] = text[len("refused: "):]
        elif text.startswith("plate "):
            parts = text.split(", ")
            seen["plate"] = parts[0][len("plate "):]
            for part in parts[1:]:
                if part.startswith("title "):
                    seen["title"] = ast.literal_eval(part[len("title "):])
    return seen


def expected(table: dict, slot: int, buttons: list) -> dict:
    """The same presses through `screen.py`, which is what the window is
    judged against."""
    state = screen.State(table, slot)
    moved = state.press_all(buttons)
    return {"slot": str(slot), "cursor": state.row, "help": state.help_text(),
            "rows": state.texts(), "tuple": state.tuple_text(),
            "presses": "".join("+" if one else "." for one in moved),
            "plate": state.plate(), "title": state.title()}


def judge_walk(python: str, app: str, env: dict, table: dict, slot: int,
               buttons: list, what: str) -> list:
    """One key sequence into the window, against the same one into `screen.py`."""
    code, output = run_app(python, app,
                           ["--state", str(slot), "--keys", ",".join(buttons),
                            "--smoke"], env)
    if code != 0:
        return ["%s: app.py exited %s -- %s" % (what, code, output.rstrip())]
    seen = read_screen(output)
    if not seen.get("rows"):
        return ["%s: app.py printed no screen report" % what]
    want = expected(table, slot, buttons)
    bad = []
    for name in ("cursor", "help", "tuple", "presses", "plate", "title"):
        if seen.get(name) != want[name]:
            bad.append("%s: the window says %s %r and screen.py says %r"
                       % (what, name, seen.get(name), want[name]))
    for name, text in sorted(want["rows"].items()):
        if seen["rows"].get(name) != text:
            bad.append("%s: the window shows %s as %r and the game writes %r"
                       % (what, name, seen["rows"].get(name), text))
    return bad


def judge_keys(python: str, app: str, env: dict) -> list:
    """Every row walked to both ends, by key, against the measured table.

    This is the judgement LOOKS-TASK-22 exists for, and it is stronger than
    "the window did not crash" in one specific way: the window prints what it
    DRAWS -- its own state, its own text, its own count of figures built -- and
    every line of it is compared with a walk of `screen.py` that shares no code
    with the widget.  A window that did its own arithmetic about where a press
    lands would agree with itself and disagree here.
    """
    table = screen.load()
    bad = []
    for slot in (2, 1):
        for name in table["order_of_rows"]:
            index = table["order_of_rows"].index(name)
            start = table["order_of_rows"].index(table["cursor_on_load"])
            steps = (index - start) % len(table["order_of_rows"])
            to_row = ["Down"] * steps
            # Left to one end and Right to the other, one press further than
            # the row is long: the extra press is what tells a lock from a
            # wrap, and it is the press this gate is here for.
            walk = (to_row + screen.walk_to_end(table, name, "Left")
                    + screen.walk_to_end(table, name, "Right"))
            bad += judge_walk(python, app, env, table, slot, walk,
                              "slot %d, %s to both ends" % (slot, name))
            if slot == 2 and name in TUPLE_ROWS:
                bad += judge_figure(python, app, env, table, name, to_row)
    # The cursor's own two ends, which wrap where the rows lock.
    rows = len(table["order_of_rows"])
    for button in ("Up", "Down"):
        bad += judge_walk(python, app, env, table, 2, [button] * (rows + 1),
                          "the cursor all the way %s and one more" % button)
    return bad


def judge_figure(python: str, app: str, env: dict, table: dict, name: str,
                 to_row: list) -> list:
    """A press on a row of the tuple has to reach the figure.

    The count of scenes built is the witness: the window builds one on the way
    up and one per change after that, so a row that moved the text without
    moving the tuple comes back as a build that did not happen -- which is
    exactly the window whose rows are a picture of a screen rather than the
    screen.
    """
    code, output = run_app(python, app,
                           ["--keys", ",".join(to_row + ["Right"]), "--smoke"],
                           env)
    if code != 0:
        return ["%s: app.py exited %s pressing Right on it -- %s"
                % (name, code, output.rstrip())]
    seen = read_screen(output)
    want = expected(table, 2, to_row + ["Right"])
    bad = []
    if seen.get("tuple") != want["tuple"]:
        bad.append("%s: one Right leaves the window's tuple %r and screen.py "
                   "says %r" % (name, seen.get("tuple"), want["tuple"]))
    if seen.get("builds") != 2:
        bad.append("%s: one Right built %s figure(s) and the window builds one "
                   "on the way up and one per change, so this row did not "
                   "reach the scene" % (name, seen.get("builds")))
    return bad


SLOTS = (2, 1)
"""The two save states, outfield first.  Both are walked: the plate is the one
thing they differ in, and a screen that ignored the slot would pass on one."""


def judge_screen_refusal(python: str, app: str, env: dict,
                         table: dict) -> list:
    """The refused style, reached BY KEY, shown and not drawn.

    The viewer's own refusal (`judge_refusal`) is an exit code; this is the
    other half, and the one the task is about: on the screen the row still
    shows what the game shows, the help box carries the table's sentence, and
    no figure is built for it.  A window that fell back to another head would
    pass the exit-code check and fail here.
    """
    order = table["order_of_rows"]
    start = order.index(table["cursor_on_load"])
    keys = ["Down"] * ((order.index("HAIR") - start) % len(order))
    keys += ["Right"] * screen.index_of(table, "HAIR", REFUSED_TEXT)
    code, output = run_app(python, app,
                           ["--keys", ",".join(keys), "--smoke"], env)
    if code != 0:
        return ["walking HAIR to %s: app.py exited %s -- %s"
                % (REFUSED_TEXT, code, output.rstrip())]
    seen = read_screen(output)
    bad = []
    if seen.get("rows", {}).get("HAIR") != REFUSED_TEXT:
        bad.append("the row the table refuses shows %r and the game writes "
                   "%r -- a refusal may not change what the screen says"
                   % (seen.get("rows", {}).get("HAIR"), REFUSED_TEXT))
    if not seen.get("refused"):
        bad.append("%s was reached by key and the window said nothing about "
                   "refusing it" % REFUSED_TEXT)
    elif seen.get("help") != seen["refused"]:
        bad.append("the refusal is not what the help box shows: help %r, "
                   "refusal %r" % (seen.get("help"), seen["refused"]))
    want = expected(table, 2, keys)
    if seen.get("tuple") != want["tuple"]:
        bad.append("the refused tuple reads %r and screen.py says %r"
                   % (seen.get("tuple"), want["tuple"]))
    if not bad:
        print("  %s is refused on the screen: the row keeps the game's text, "
              "the help box carries the table's sentence, and the panel draws "
              "nothing" % REFUSED_TEXT)
    return bad


def judge_refusal(python: str, app: str, where: str, env: dict) -> list:
    """A tuple the table refuses: exit 2, the table's words, and no file."""
    out = os.path.join(where, "refused.png")
    code, output = run_app(python, app,
                           ["--looks", REFUSED, "--piece", PIECE,
                            "--screenshot", out], env)
    bad = []
    if code != 2:
        bad.append("%s is refused by the assembly table and app.py exited %s, "
                   "not 2 -- the gate cannot tell a refusal from a crash"
                   % (REFUSED, code))
    if "refuses" not in output:
        bad.append("%s exited %s without saying what refused it: %s"
                   % (REFUSED, code, output.rstrip()))
    if os.path.isfile(out):
        bad.append("%s was refused and a picture was written anyway" % REFUSED)
    return bad


# ---- the negative controls ------------------------------------------------

# They live here and not in `controls.py` for the reason the .mcr cycle wrote
# down: that engine plants a copy of the tree and runs `<module>.py
# --self-check` under the SYSTEM interpreter, and these three are only visible
# to a judge that has a venv, a display and a disc.  A red case lives where it
# can run.
BREAKS = (
    ("the tuple reaching the scene", os.path.join("ui", "app.py"),
     "        drawn = core.from_image(image, args.looks, args.figure,",
     "        drawn = core.from_image(image, DEFAULT_TUPLE, args.figure,"),
    ("the triangles being drawn", os.path.join("ui", "viewer.py"),
     "                functions.glDrawArrays(GL_TRIANGLES, first, count)",
     "                functions.glDrawArrays(GL_TRIANGLES, first, 0)"),
    ("app.py --compare counting pixels", os.path.join("ui", "app.py"),
     "            if one.pixel(x, y) != two.pixel(x, y):",
     "            if False:"),
    ("the kit reaching the body", "assembly.py",
     "    if kit is not None:",
     "    if False:"),
    ("the pose reaching the points", "scene.py",
     "        out.append(moved)",
     "        out.append(part)"),
)
"""(name, file, the exact line, what it becomes) -- one defect each.

The first draws the same boneco whatever the tuple says, which is the failure
the floors exist for.  The second paints the clear colour and saves it, which
is the failure `judge_frame` exists for.  The third leaves `--compare`
answering zero for two pictures that differ, which is the failure the
agreement between the two counts exists for -- and it is the one that would
otherwise be invisible, because `--compare` is the code under test.  The
fourth leaves every piece where the file puts it, which is the shelf wearing
the pose's name -- and it is what `judge_posed` exists for.
"""

KEY_ROW = "SKIN"
"""The row the planted trees are walked on: four values, so a walk to its end
and one press past it is five presses rather than eighty."""

KEY_BREAKS = (
    ("the arrows reaching the screen", os.path.join("ui", "looks_set.py"),
     "        self.press(button)\n        event.accept()",
     "        event.accept()"),
    ("the figure following the rows", os.path.join("ui", "looks_set.py"),
     "        if self.state.tuple_text() != before:",
     "        if False:"),
    ("the row's own text", os.path.join("ui", "looks_set.py"),
     '            "rows": {name: self.state.text_of(name)',
     '            "rows": {name: name'),
)
"""(name, file, the exact line, what it becomes) -- one defect each, and all
three are invisible to the picture judgement above.

The first leaves a window that draws the right figure and answers no key.  The
second leaves the rows moving and the figure frozen on the tuple it opened
with -- the screen this task exists to avoid, where the twelve rows are a
picture of a screen.  The third has the window report the row's NAME instead of
the game's text, which is what a window that invented its texts would look like
from outside.
"""

PLANTED: list = []


def _sandbox(tmp: str, name: str, where: str, old: str, new: str) -> tuple:
    """A copy of tools/looks with one substitution applied.  `(path, why not)`.

    `tools/pes2/` comes along, exactly as `controls.py` copies it and for the
    same measured reason: `atlas.py` reaches sideways for `lzss`, so a sandbox
    holding only this directory dies at import with `No module named 'lzss'`.
    That IS a red, and it is a red for the wrong cause -- the first run of this
    gate reported all three controls red without any of them having drawn a
    single frame.

    The literal has to match EXACTLY ONCE.  A substitution that matches nothing
    leaves the copy intact, the run comes out green, and the green is read as
    "the guard held" -- the same rule `controls.py` enforces, for the same
    reason.
    """
    ignore = shutil.ignore_patterns("__pycache__", "*.pyc")
    sandbox = os.path.join(tmp, "tools", "looks")
    shutil.copytree(LOOKS_DIR, sandbox, ignore=ignore)
    pes2 = os.path.join(os.path.dirname(LOOKS_DIR), "pes2")
    if os.path.isdir(pes2):
        shutil.copytree(pes2, os.path.join(tmp, "tools", "pes2"),
                        ignore=ignore)
    broken = os.path.join(sandbox, where)
    with open(broken, encoding="utf-8") as handle:
        text = handle.read()
    if text.count(old) != 1:
        return (None, "the substitution for %s matched %d time(s), not once"
                % (name, text.count(old)))
    with open(broken, "w", encoding="utf-8") as handle:
        handle.write(text.replace(old, new))
    return (sandbox, "")


def plant(python: str, env: dict, name: str, where: str, old: str,
          new: str) -> tuple:
    """One defect in a copy of the tree.  `(did the gate redden, why)`."""
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, where, old, new)
        if sandbox is None:
            return (False, why)
        app = os.path.join(sandbox, "ui", "app.py")
        shots = os.path.join(tmp, "shots")
        os.makedirs(shots)
        # The smoke counts first, and they are part of the judgement here and
        # not only in `main`: a defect that leaves the body grey draws every
        # picture below perfectly, and the control for it came back GREEN
        # until this line existed (measured 2026-09-20, LOOKS-TASK-30).
        code, output = run_app(python, app, ["--smoke"], env)
        if code != 0:
            return (False, "the planted tree for %s did not run, so nothing "
                           "was proved: %s" % (name, output.rstrip()))
        bad = judge_whole(_counted(output))
        _shots, _theirs, more, broke = measure(python, app, shots, env)
        bad += more
        if broke:
            return (False, "the planted tree for %s did not run, so nothing "
                           "was proved: %s" % (name, broke))
        more, broke, _posed = measure_posed(python, app, shots, env)
        if broke:
            return (False, "the planted tree for %s did not draw the figure, "
                           "so nothing was proved: %s" % (name, broke))
        bad += more
        if not bad:
            return (False, "%s :: %s was broken (%s -> %s) and the gate still "
                           "passed" % (where, name, old.strip(), new.strip()))
        return (True, bad[0])


def plant_keys(python: str, env: dict, name: str, where: str, old: str,
               new: str) -> tuple:
    """The same, for the judgement that walks the screen by key.

    A separate path because `plant` runs the PICTURE judgement, and a screen
    whose arrows do nothing draws the starting tuple perfectly well: the three
    controls above would all stay green on it.  A judgement with no red case of
    its own is a judgement nobody has seen fail.

    The walk is cut to one row and the two cursor ends -- twenty-four rows per
    planted tree would be four minutes of the gate to prove what one row
    proves.
    """
    table = screen.load()
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, where, old, new)
        if sandbox is None:
            return (False, why)
        app = os.path.join(sandbox, "ui", "app.py")
        code, output = run_app(python, app, ["--smoke"], env)
        if code != 0 or not read_screen(output).get("rows"):
            return (False, "the planted tree for %s did not run, so nothing "
                           "was proved: %s" % (name, output.rstrip()))
        order = table["order_of_rows"]
        start = order.index(table["cursor_on_load"])
        to_row = ["Down"] * ((order.index(KEY_ROW) - start) % len(order))
        bad = judge_walk(python, app, env, table, 2,
                         to_row + screen.walk_to_end(table, KEY_ROW, "Right"),
                         "planted: %s to its right end" % KEY_ROW)
        bad += judge_figure(python, app, env, table, KEY_ROW, to_row)
        if not bad:
            return (False, "%s :: %s was broken (%s -> %s) and the walk still "
                           "passed" % (where, name, old.strip(), new.strip()))
        return (True, bad[0])


# ---- HEIG and BODY in the drawing (LOOKS-TASK-29) --------------------------

STATURE_SHOTS = (
    ("175 cm, A TYPE", (), 175, 0),
    ("155 cm", (("HEIG", "Left", 20),), 155, 0),
    ("210 cm", (("HEIG", "Right", 35),), 210, 0),
    ("H TYPE", (("BODY", "Right", 7),), 175, 7),
)
"""(name, [(row, button, presses)], height, BODY) -- the stature ends.

From the state's own 175 cm and `A TYPE`, which `screen.json` measured on both
states: twenty Lefts to 155, thirty-five Rights to 210, seven to `H TYPE`.
"""

SCREEN_SCALE = 2
"""Window pixels per game pixel in screen mode: `looks_set.SCALE`, the app's
default `--scale`.  Written here because this gate may not import the widget
(it needs no Qt), and it only ever runs the app with the default."""

STATURE_SLACK = 0.06
"""How far the ink's ratio may sit from the rule's before the window is wrong.

The rule's ratios are exact (`stature.scale`); the ink is not, because the
figure is rasterised at the panel's native size, doubled, and a row of pixels
at either end of the figure is about 0.01 of it.  The slack is a few such rows
each side; a height applied on the wrong axis -- the failure this exists for --
misses by far more.
"""


def stature_keys(table: dict, steps) -> list:
    """The presses of one `STATURE_SHOTS` entry, from the cursor on load."""
    order = table["order_of_rows"]
    here = order.index(table["cursor_on_load"])
    out = []
    for row, button, count in steps:
        there = order.index(row)
        out += ["Down" if there > here else "Up"] * abs(there - here)
        here = there
        out += [button] * count
    return out


PANEL_BORDER = 2
"""Native pixels of frame each side of the panel: the game draws two one-pixel
lines a side (`oracle.py --scenery`, LOOKS-TASK-31), and the window paints
them since."""

PANEL_INK_APART = 24
"""How far a pixel of the panel has to sit from its ROW's ground to be figure.

Per row, because the panel's ground is the game's vertical gradient since
LOOKS-TASK-31: one ground colour for the whole panel -- what `ink_box` takes --
made every row of the gradient "ink", and the stature ratios all came out
1.000."""


def panel_ink(shot: tuple, box, scale: int) -> tuple:
    """(width, height, pixels) of the figure inside the panel.

    The ground is taken per row -- the commonest colour of that row of the
    panel -- so a vertical gradient behind the figure is ground everywhere and
    the figure is what differs from it.
    """
    _width, _height, channels, rows = shot
    # Inside the border: the game draws the panel's frame as two one-pixel
    # lines a side, and a frame is ink on every row and every column.
    left, top, right, bottom = [(one + PANEL_BORDER * way) * scale
                                for one, way in zip(box, (1, 0, -1, 0))]
    first = last = None
    low = high = None
    drawn = 0
    for y in range(top, bottom + scale):
        line = [tuple(rows[y][x * channels:x * channels + 3])
                for x in range(left, right + scale)]
        counts: dict = {}
        for pixel in line:
            counts[pixel] = counts.get(pixel, 0) + 1
        ground = max(counts, key=counts.get)
        for x, pixel in enumerate(line):
            if max(abs(a - b) for a, b in zip(pixel, ground)) <= PANEL_INK_APART:
                continue
            drawn += 1
            first = x if first is None else min(first, x)
            last = x if last is None else max(last, x)
            low = y if low is None else min(low, y)
            high = y if high is None else max(high, y)
    if not drawn:
        return (0, 0, 0)
    return (last - first + 1, high - low + 1, drawn)


def measure_stature(python: str, app: str, where: str, env: dict) -> tuple:
    """The panel at the stature ends.  `(bad, broke, inks)`.

    What is judged is the window's PICTURE, not its code: the ink of the panel
    has to grow with `HEIG` in both directions and with `BODY` only across, by
    the ratios `stature` computes for the game's own scale vectors.  With no
    measured camera on disc the window draws the v1 orbit, where the stature
    does not reach by design; `inks` comes back None and the caller says so
    instead of judging.
    """
    import iso_source
    import layout
    import stature

    table = screen.load()
    box = table["regions"]["panel"]["native"]
    inks = {}
    for name, steps, _height, _build in STATURE_SHOTS:
        out = os.path.join(where, "stature-%s.png" % name.split()[0])
        keys = stature_keys(table, steps)
        code, output = run_app(python, app,
                               ["--state", "2"]
                               + (["--keys", ",".join(keys)] if keys else [])
                               + ["--screenshot", out], env)
        if code != 0 or not os.path.isfile(out):
            return ([], "the screen at %s did not draw: %s"
                    % (name, output.rstrip()), None)
        if "game's own camera" not in output:
            return ([], "", None)
        inks[name] = panel_ink(picture(out), box, SCREEN_SCALE)
    with iso_source.open_disc(env[layout.ENV_IMAGE]) as disc:
        found = stature.rule(disc.read(layout.SELECT8))
    scales = {name: stature.scale(found, height, build)
              for name, _steps, height, build in STATURE_SHOTS}
    bad = []

    def near(what, got, want):
        if abs(got - want) > STATURE_SLACK:
            bad.append("%s: the ink says %.3f and the game's scale %.3f"
                       % (what, got, want))

    base, low = inks["175 cm, A TYPE"], inks["155 cm"]
    tall, wide = inks["210 cm"], inks["H TYPE"]
    near("210 cm against 155 cm, height", tall[1] / float(low[1]),
         scales["210 cm"][1] / float(scales["155 cm"][1]))
    near("210 cm against 175 cm, width", tall[0] / float(base[0]),
         scales["210 cm"][0] / float(scales["175 cm, A TYPE"][0]))
    near("H TYPE against A TYPE, width", wide[0] / float(base[0]),
         scales["H TYPE"][0] / float(scales["175 cm, A TYPE"][0]))
    near("H TYPE against A TYPE, height", wide[1] / float(base[1]),
         scales["H TYPE"][1] / float(scales["175 cm, A TYPE"][1]))
    return (bad, "", inks)


def plant_stature(python: str, env: dict, name: str, where: str, old: str,
                  new: str) -> tuple:
    """A defect in a copy of the tree, judged by `measure_stature` alone.

    The measured camera comes along into the copy: `scene` finds it beside the
    tree, and a sandbox without it draws the orbit, where no stature judgement
    runs -- a green that proved nothing.
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, where, old, new)
        if sandbox is None:
            return (False, why)
        cameras = os.path.join(os.path.dirname(os.path.dirname(LOOKS_DIR)),
                               "work", "looks-camera")
        shutil.copytree(cameras, os.path.join(tmp, "work", "looks-camera"))
        shots = os.path.join(tmp, "shots")
        os.makedirs(shots)
        app = os.path.join(sandbox, "ui", "app.py")
        bad, broke, inks = measure_stature(python, app, shots, env)
        if broke or inks is None:
            return (False, "the planted tree for %s did not judge the "
                           "stature, so nothing was proved: %s"
                    % (name, broke or "no game camera in the copy"))
        if not bad:
            return (False, "%s :: %s was broken (%s -> %s) and the stature "
                           "still passed" % (where, name, old.strip(),
                                             new.strip()))
        return (True, bad[0])


STATURE_BREAKS = (
    ("the stature reaching the camera", os.path.join("ui", "looks_set.py"),
     '        elif (now.get("height"), now.get("build")) != stature:',
     "        elif False:"),
    ("the height on its own axis", "stature.py",
     '    return (across, _divide(numerator, found["height_divisor"]), across)',
     '    return (_divide(numerator, found["height_divisor"]), across,\n'
     '            _divide(numerator, found["height_divisor"]))'),
)
"""The window whose rows stop at the text, and the rule with the height on the
wrong axis -- the negative control LOOKS-TASK-29 asks for, judged by the
picture the window draws."""


# ---- the screen's furniture (LOOKS-TASK-31) --------------------------------

SCENERY_INSET = 3
"""How far inside a packet's top-left corner the window is sampled, in native
pixels: past the edge the neighbour's colour bleeds in, and before the text of
a row, which starts further in."""

SCENERY_SLACK = 16
"""How far the window's pixel may sit from the colour the table measured.

The window paints eight bits a channel and the table holds what the game's
packet declared; two five-bit steps is the room confront.py --outside needed
between the two renderers."""


def measure_scenery(python: str, app: str, where: str, env: dict) -> tuple:
    """The window's furniture against the table it was drawn from.

    `(bad, broke, sampled)`; sampled is None when there is no measured table
    on disc, and the caller says so instead of judging.  What is judged is the
    PICTURE: each packet of `work/looks-scenery/slot2.json` is sampled just
    inside its top-left corner, and the pixel has to be the packet's colour at
    that row -- the top colour, or the gradient a few rows down.
    """
    import json

    table_path = os.path.join(os.path.dirname(os.path.dirname(LOOKS_DIR)),
                              "work", "looks-scenery", "slot2.json")
    if not os.path.isfile(table_path):
        return ([], "", None)
    with open(table_path, encoding="utf-8") as handle:
        packets = json.load(handle)["packets"]
    out = os.path.join(where, "scenery.png")
    code, output = run_app(python, app, ["--state", "2", "--scale", "1",
                                         "--screenshot", out], env)
    if code != 0 or not os.path.isfile(out):
        return ([], "the screen did not draw: %s" % output.rstrip(), None)
    width, height, channels, rows = picture(out)
    boxes = []
    for packet in packets:
        xs = [one[0] for one in packet["points"]]
        ys = [one[1] for one in packet["points"]]
        boxes.append((min(xs), min(ys), max(xs), max(ys)))
    bad, sampled = [], 0
    for index, packet in enumerate(packets):
        left, top, right, bottom = boxes[index]
        if packet.get("semi") or packet.get("line"):
            # A blended packet's pixel is its colour mixed with what is under
            # it, and a line is one pixel wide: neither has a colour of its own
            # to hold the window to.
            continue
        if bottom - top <= 2 * SCENERY_INSET:
            continue
        x, y = max(left, 0) + SCENERY_INSET, max(top, 0) + SCENERY_INSET
        if x >= width or y >= height or any(
                one[0] <= x <= one[2] and one[1] <= y <= one[3]
                and not later.get("line")
                for one, later in zip(boxes[index + 1:], packets[index + 1:])):
            # Off the screen, or drawn over by a later packet -- a polyline's
            # box is not what it covers, only its edge is.
            continue
        colours = packet["colours"]
        corners = packet["points"]
        high = colours[min(range(len(corners)), key=lambda i: corners[i][1])]
        low = colours[max(range(len(corners)), key=lambda i: corners[i][1])]
        share = (y - top) / float(bottom - top) if packet["gradient"] else 0
        want = [a + (b - a) * share for a, b in zip(high, low)]
        got = rows[y][x * channels:x * channels + 3]
        sampled += 1
        gap = max(abs(a - b) for a, b in zip(want, got))
        if gap > SCENERY_SLACK:
            bad.append("the packet at (%d,%d)-(%d,%d) is %s in the table and "
                       "the window paints %s there, %d apart"
                       % (left, top, right, bottom,
                          tuple(int(v) for v in want), tuple(got), gap))
    return (bad, "", sampled)


def plant_scenery(python: str, env: dict, name: str, where: str, old: str,
                  new: str) -> tuple:
    """A defect in a copy of the tree, judged by `measure_scenery` alone.

    The measured table comes along into the copy, like the camera does for the
    stature controls: without it the window paints no furniture and the
    judgement does not run -- a green that proved nothing.
    """
    with tempfile.TemporaryDirectory() as tmp:
        sandbox, why = _sandbox(tmp, name, where, old, new)
        if sandbox is None:
            return (False, why)
        tables = os.path.join(os.path.dirname(os.path.dirname(LOOKS_DIR)),
                              "work", "looks-scenery")
        shutil.copytree(tables, os.path.join(tmp, "work", "looks-scenery"))
        shots = os.path.join(tmp, "shots")
        os.makedirs(shots)
        app = os.path.join(sandbox, "ui", "app.py")
        bad, broke, sampled = measure_scenery(python, app, shots, env)
        if broke or sampled is None:
            return (False, "the planted tree for %s did not judge the "
                           "furniture, so nothing was proved: %s"
                    % (name, broke or "no table in the copy"))
        if not bad:
            return (False, "%s :: %s was broken (%s -> %s) and the furniture "
                           "still passed" % (where, name, old.strip(),
                                             new.strip()))
        return (True, bad[0])


SCENERY_BREAKS = (
    ("the measured furniture reaching the window",
     os.path.join("ui", "looks_set.py"),
     "        self._paint_scenery(painter)\n",
     "        pass\n"),
    ("the panel's piece of the furniture reaching the viewer",
     os.path.join("ui", "viewer.py"),
     "        painter.drawImage(self.rect(), self.clear_image)\n",
     "        pass\n"),
)
"""The window that measured its furniture and painted its own colours anyway
-- the defect this judgement exists for."""


# ---- the gate itself ------------------------------------------------------

def skip(why: str) -> int:
    print("skipped: %s" % why)
    return SKIP


def main(argv: list | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    if argv and argv[0] in ("--check", "--self-check"):
        return self_check()
    if argv:
        print(__doc__)
        return 2

    python = venv_python()
    if python is None:
        return skip("no venv at %s -- the window needs PySide6 of its own, "
                    "and `python -m venv %s` then `pip install PySide6` "
                    "is the whole recipe"
                    % (os.path.join(VENV, VENV_PYTHON), VENV))
    probe = subprocess.run([python, "-c", "import PySide6"],
                           capture_output=True, text=True)
    if probe.returncode:
        return skip("the venv at %s has no PySide6" % VENV)
    if not os.path.isfile(APP):
        return skip("%s does not exist yet (LOOKS-TASK-15)" % APP)
    if not os.environ.get(layout.ENV_IMAGE):
        return skip("%s is not set, and a viewer with no disc has nothing to "
                    "draw -- it names the Japanese data track"
                    % layout.ENV_IMAGE)

    env = environment()
    code, output = run_app(python, APP, ["--smoke"], env)
    if "could not connect to display" in output or "cannot open display" in output:
        return skip("no X server on %s -- `Xvfb %s -screen 0 1280x1024x24 "
                    "-nolisten tcp &`" % (DISPLAY, DISPLAY))
    if code == SKIP:
        return skip("app.py skipped itself: %s" % output.strip())
    print(output.rstrip())
    if code != 0:
        print("FAIL: app.py --smoke exited %s" % code)
        return 1
    if "window up" not in output:
        print("FAIL: app.py --smoke did not report a window")
        return 1
    if "off the desktop at %d,%d" % (PARKED, PARKED) not in output:
        print("FAIL: the window is not parked off the desktop, and the rule "
              "of CLAUDE.md is that nothing opens on the user's screen")
        return 1
    whole = judge_whole(_counted(output))
    if whole:
        for line in whole:
            print("FAIL: %s" % line)
        return 1

    with tempfile.TemporaryDirectory() as tmp:
        shots, theirs, bad, broke = measure(python, APP, tmp, env)
        if broke:
            print("FAIL: %s" % broke)
            return 1
        for name in sorted(shots):
            shot = shots[name]
            seen = colours(shot)
            print("  %s: %dx%d, %d colour(s), the commonest covers %.2f%%"
                  % (name, shot[0], shot[1], len(seen),
                     percent(max(seen.values()), shot)))
        for start, name, row, floor in PAIRS:
            base = shots.get(start)
            if base is None or name not in shots:
                continue
            count = differing(base, shots[name])
            print("  %s vs %s (%s): %d of %d pixel(s) differ (%.2f%%), floor "
                  "%.1f%%, and app.py --compare says %s"
                  % (start, name, row, count, shot[0] * shot[1],
                     percent(count, base), floor, theirs.get(name, "nothing")))
        # The colour pairs are `--piece head` for a measured reason, and that
        # leaves the other eleven pieces out of every picture judged above.
        # Two more: the whole figure, and the whole figure ASSEMBLED, which is
        # what LOOKS-TASK-27 delivers.
        more, broke, shots = measure_posed(python, APP, tmp, env)
        if broke:
            print("FAIL: %s" % broke)
            return 1
        entire, posed = shots
        bad += more
        seen = colours(entire)
        print("  the whole figure: %dx%d, %d colour(s), the commonest covers "
              "%.2f%%" % (entire[0], entire[1], len(seen),
                          percent(max(seen.values()), entire)))
        wide, tall, drawn = ink_box(posed)
        shelf_wide, shelf_tall, _shelf = ink_box(entire)
        print("  the figure posed on frame %d: ink %dx%d (%.2f tall for one "
              "wide, floor %.1f) against the shelf's %dx%d (%.2f, ceiling "
              "%.1f)" % (POSED_FRAME, wide, tall, tall / float(wide),
                         STANDING, shelf_wide, shelf_tall,
                         shelf_tall / float(shelf_wide), LYING))

        bad += judge_refusal(python, APP, tmp, env)
        if bad:
            for line in bad:
                print("FAIL: %s" % line)
            return 1
        print("  %s is refused by the table, exits 2 and writes no picture"
              % REFUSED)

    table = screen.load()
    bad = judge_screen_refusal(python, APP, env, table)
    walked = 0
    if not bad:
        bad = judge_keys(python, APP, env)
        walked = len(table["order_of_rows"]) * len(SLOTS)
    if bad:
        for line in bad:
            print("FAIL: %s" % line)
        return 1
    print("  the screen walked by key: %d row(s) to both ends across %d "
          "state(s), the cursor past both ends, and every text, help, plate "
          "and title is what screen.json measured off the game"
          % (walked, len(SLOTS)))

    with tempfile.TemporaryDirectory() as tmp:
        bad, broke, inks = measure_stature(python, APP, tmp, env)
    if broke:
        print("FAIL: %s" % broke)
        return 1
    if bad:
        for line in bad:
            print("FAIL: %s" % line)
        return 1
    judged_stature = inks is not None
    if judged_stature:
        print("  HEIG and BODY reach the panel, ink wide x tall: %s" % ", ".join(
            "%s %dx%d" % (name, one[0], one[1]) for name, one in inks.items()))
    else:
        print("  HEIG and BODY not judged: the window has no game camera "
              "(oracle.py --camera), and the v1 orbit carries no stature")

    with tempfile.TemporaryDirectory() as tmp:
        bad, broke, sampled = measure_scenery(python, APP, tmp, env)
    if broke:
        print("FAIL: %s" % broke)
        return 1
    if bad:
        for line in bad:
            print("FAIL: %s" % line)
        return 1
    judged_scenery = sampled is not None
    if judged_scenery:
        print("  the furniture the window paints is the measured table's: %d "
              "packet(s) sampled, every one within %d"
              % (sampled, SCENERY_SLACK))
    else:
        print("  the furniture not judged: no work/looks-scenery/ table "
              "(oracle.py --scenery --write)")

    failed = 0
    if judged_scenery:
        for name, where, old, new in SCENERY_BREAKS:
            red, why = plant_scenery(python, env, name, where, old, new)
            if red:
                print("negative: breaking %s reddens the furniture -- %s"
                      % (name, why))
                PLANTED.append(name)
            else:
                print("FAIL: %s" % why)
                failed += 1
    if judged_stature:
        for name, where, old, new in STATURE_BREAKS:
            red, why = plant_stature(python, env, name, where, old, new)
            if red:
                print("negative: breaking %s reddens the stature -- %s"
                      % (name, why))
                PLANTED.append(name)
            else:
                print("FAIL: %s" % why)
                failed += 1
    for name, where, old, new in BREAKS:
        red, why = plant(python, env, name, where, old, new)
        if red:
            print("negative: breaking %s reddens the gate -- %s" % (name, why))
            PLANTED.append(name)
        else:
            print("FAIL: %s" % why)
            failed += 1
    for name, where, old, new in KEY_BREAKS:
        red, why = plant_keys(python, env, name, where, old, new)
        if red:
            print("negative: breaking %s reddens the walk -- %s" % (name, why))
            PLANTED.append(name)
        else:
            print("FAIL: %s" % why)
            failed += 1
    if failed:
        return 1
    print("looks_ui: %d of %d negative control(s) red, and the window drew "
          "every tuple it was asked for and answered every key with what the "
          "game shows" % (len(PLANTED), len(BREAKS) + len(KEY_BREAKS)
                          + (len(STATURE_BREAKS) if judged_stature else 0)
                          + (len(SCENERY_BREAKS) if judged_scenery else 0)))
    return 0


# ---- the self-check, which needs no venv, no display and no disc ----------

def _png(width: int, height: int, pixels, channels: int = 4,
         filters=None) -> bytes:
    """A PNG built here, so the decoder above has something known to read."""
    lines = [bytearray(b"".join(bytes(pixels(x, y)) for x in range(width)))
             for y in range(height)]
    raw = bytearray()
    for y, line in enumerate(lines):
        kind = 0 if filters is None else filters[y]
        raw.append(kind)
        if kind == 2 and y:
            above = lines[y - 1]
            raw += bytes((line[i] - above[i]) & BYTE for i in range(len(line)))
        else:
            raw += bytes(line)

    def chunk(kind: bytes, body: bytes) -> bytes:
        return (struct.pack(">I", len(body)) + kind + body
                + struct.pack(">I", zlib.crc32(kind + body)))

    head = struct.pack(">IIBBBBB", width, height, 8,
                       6 if channels == 4 else 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", head)
            + chunk(b"IDAT", zlib.compress(bytes(raw)))
            + chunk(b"IEND", b""))


def _checks(c) -> None:
    ok = c.ok
    refuses = c.refusing(BadPicture)

    flat = read_png(_png(4, 3, lambda x, y: (1, 2, 3, 255)))
    ok("a PNG reads back at the size it was written",
       flat[:3] == (4, 3, 4), "%r" % (flat[:3],))
    ok("and every pixel of a flat picture is the one written",
       set(colours(flat)) == {bytes((1, 2, 3, 255))}, "%r" % colours(flat))

    filtered = read_png(_png(4, 3, lambda x, y: (x * 9, y * 7, 3, 255),
                             filters=[0, 2, 2]))
    plain = read_png(_png(4, 3, lambda x, y: (x * 9, y * 7, 3, 255)))
    ok("a filtered scanline decodes to the same pixels as an unfiltered one",
       filtered[3] == plain[3])

    three = read_png(_png(2, 2, lambda x, y: (x * 5, y * 5, 7), channels=3))
    ok("RGB reads as three channels", three[2] == 3, "%r" % (three[2],))

    refuses("a file that is not a PNG", lambda: read_png(b"not a png at all"),
            "signature")
    refuses("a file whose chunk runs off the end",
            lambda: read_png(_png(64, 64, lambda x, y: (x, y, 3, 255))[:60]),
            "short")
    refuses("a 16-bit PNG, rather than reading it as 8-bit",
            lambda: read_png(
                b"\x89PNG\r\n\x1a\n"
                + struct.pack(">I", 13) + b"IHDR"
                + struct.pack(">IIBBBBB", 1, 1, 16, 6, 0, 0, 0)
                + struct.pack(">I", 0)),
            "16")

    # The judges, on pictures built to be judged.
    blank = read_png(_png(SIZE[0], SIZE[1], lambda x, y: (31, 33, 41, 255)))
    drawn = read_png(_png(SIZE[0], SIZE[1],
                          lambda x, y: (31, 33, 41, 255) if x > 60
                          else (200, 40, 40, 255)))
    other = read_png(_png(SIZE[0], SIZE[1],
                          lambda x, y: (31, 33, 41, 255) if x > 400
                          else (40, 200, 40, 255)))
    ok("a drawn frame passes the frame judge", judge_frame("drawn", drawn) == [],
       "%s" % judge_frame("drawn", drawn))
    ok("a blank frame does NOT", judge_frame("blank", blank) != [])
    small = read_png(_png(8, 8, lambda x, y: (x, y, 3, 255)))
    ok("and neither does a picture of the wrong size",
       judge_frame("small", small) != [])

    ok("two pictures of the same thing are caught repeating",
       judge_repeat(drawn, drawn) == [])
    ok("a viewer that wobbles between runs is caught",
       judge_repeat(drawn, other) != [])

    shots = {start: drawn for start, _n, _r, _f in PAIRS}
    shots.update({name: other for _s, name, _r, _f in PAIRS})
    counts = {name: differing(drawn, other) for _s, name, _r, _f in PAIRS}
    ok("pictures that differ by more than the floor pass the pair judge",
       judge_pairs(shots, counts) == [], "%s" % judge_pairs(shots, counts))
    same = {one: drawn for pair in PAIRS for one in (pair[0], pair[1])}
    ok("a viewer that ignores the tuple is caught",
       judge_pairs(same, {name: 0 for _s, name, _r, _f in PAIRS}) != [])
    ok("and a --compare that disagrees with this file is caught",
       judge_pairs(shots, {name: counts[name] + 1
                           for _s, name, _r, _f in PAIRS}) != [])
    ok("every pair says which tuple it starts from",
       all(len(pair) == 4 and pair[0] in shots for pair in PAIRS))
    ok("and at least one of them starts from a head that is not section 24's",
       any(not pair[0].split("-")[1].startswith("A") for pair in PAIRS),
       "%r" % ([pair[0] for pair in PAIRS],))

    # The whole figure, by the counts the app prints.  The colour pairs are
    # `--piece head` for a measured reason, and this is what keeps the other
    # eleven pieces inside a judgement (CORR-LOOKS-040).
    figure = ("  A-A1-A-A-A, figure 0: 593 primitive(s), 593 textured, "
              "5 surface(s), 1186 triangle(s)\n"
              "  sections 12, shelf on, wireframe off, camera yaw 180 "
              "pitch 0")
    ok("the counts are read out of the app's own line",
       _counted(figure) == {"primitives": 593, "textured": 593,
                            "sections": 12},
       "%r" % (_counted(figure),))
    ok("and a whole DRESSED figure passes the floors",
       judge_whole(_counted(figure)) == [],
       "%s" % judge_whole(_counted(figure)))
    # Red: the same figure with the body grey -- 356 textured of 593, which is
    # what the app printed until the kit container reached the draw list
    # (LOOKS-TASK-30).  It clears every floor above and is not a dressed
    # figure, which is why the floors alone were not enough.
    undressed = figure.replace("593 textured", "356 textured")
    ok("a figure with its body untextured does not",
       judge_whole(_counted(undressed)) != [],
       "%s" % judge_whole(_counted(undressed)))
    alone = ("  A-A1-A-A-A, figure 0: 18 primitive(s), 18 textured, "
             "3 surface(s), 36 triangle(s)\n"
             "  sections 1, shelf on, wireframe off, camera yaw 180 "
             "pitch 0")
    ok("a body that did not draw is caught by them",
       len(judge_whole(_counted(alone))) == 2,
       "%s" % judge_whole(_counted(alone)))
    ok("and a report with no counts at all is caught too",
       judge_whole(_counted("window up")) != [])

    refuses("two pictures of different sizes, rather than counting anyway",
            lambda: differing(drawn, small), "channel")

    # The substitutions have to name lines that exist, or the planted runs
    # below are green for the wrong reason -- the same rule `_sandbox`
    # enforces at run time, checked here where it costs nothing.
    for name, where, old, _new in BREAKS:
        path = os.path.join(LOOKS_DIR, where)
        if not os.path.isfile(path):
            c.skip("the break for %s: %s is not here yet" % (name, where))
            continue
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
        ok("the break for %s matches its line exactly once" % name,
           text.count(old) == 1, "matched %d time(s)" % text.count(old))

    ok("the venv is looked for upward, not at a counted depth",
       find_upward(os.path.join("tools", "looks", "ui_check.py")) is not None)


def self_check(verbose: bool = True) -> int:
    return harness.run("ui_check.py", _checks, verbose)


if __name__ == "__main__":
    raise SystemExit(main())

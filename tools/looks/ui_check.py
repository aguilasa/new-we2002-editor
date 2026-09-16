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
"""

REFUSED = "A-A1-A-F-A"
"""A tuple the assembly table refuses, and the exit code is the contract.

`FACE=F` is value 5 of a row the screen was measured to reach 5 of, so the
table raises instead of drawing a beard nobody measured.  The gate demands
exit 2 and NO file: a refusal that still writes a picture would be drawn from
something, and that something would be invented.
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
    """(exit code, output) of one app run, or (None, output) when it hung."""
    try:
        done = subprocess.run([python, app] + args, env=env,
                              capture_output=True, text=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return (None, "did not exit within %ds" % TIMEOUT)
    return (done.returncode, done.stdout + done.stderr)


def draw(python: str, app: str, name: str, out: str, env: dict):
    """One tuple to one PNG.  `(picture, output)`; picture None on failure."""
    code, output = run_app(python, app,
                           ["--looks", name, "--piece", PIECE,
                            "--size", "%dx%d" % SIZE, "--screenshot", out],
                           env)
    if code or not os.path.isfile(out):
        return (None, output)
    return (picture(out), output)


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
     "        drawn = core.from_image(image, args.looks, args.figure)",
     "        drawn = core.from_image(image, DEFAULT_TUPLE, args.figure)"),
    ("the triangles being drawn", os.path.join("ui", "viewer.py"),
     "                functions.glDrawArrays(GL_TRIANGLES, first, count)",
     "                functions.glDrawArrays(GL_TRIANGLES, first, 0)"),
    ("app.py --compare counting pixels", os.path.join("ui", "app.py"),
     "            if one.pixel(x, y) != two.pixel(x, y):",
     "            if False:"),
)
"""(name, file, the exact line, what it becomes) -- one defect each.

The first draws the same boneco whatever the tuple says, which is the failure
the floors exist for.  The second paints the clear colour and saves it, which
is the failure `judge_frame` exists for.  The third leaves `--compare`
answering zero for two pictures that differ, which is the failure the
agreement between the two counts exists for -- and it is the one that would
otherwise be invisible, because `--compare` is the code under test.
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
        _shots, _theirs, bad, broke = measure(python, app, shots, env)
        if broke:
            return (False, "the planted tree for %s did not run, so nothing "
                           "was proved: %s" % (name, broke))
        if not bad:
            return (False, "%s :: %s was broken (%s -> %s) and the gate still "
                           "passed" % (where, name, old.strip(), new.strip()))
        return (True, bad[0])


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
        bad += judge_refusal(python, APP, tmp, env)
        if bad:
            for line in bad:
                print("FAIL: %s" % line)
            return 1
        print("  %s is refused by the table, exits 2 and writes no picture"
              % REFUSED)

    failed = 0
    for name, where, old, new in BREAKS:
        red, why = plant(python, env, name, where, old, new)
        if red:
            print("negative: breaking %s reddens the gate -- %s" % (name, why))
            PLANTED.append(name)
        else:
            print("FAIL: %s" % why)
            failed += 1
    if failed:
        return 1
    print("looks_ui: %d of %d negative control(s) red, and the window drew "
          "every tuple it was asked for" % (len(PLANTED), len(BREAKS)))
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

#!/usr/bin/env python3
"""Drive PES2 under DuckStation to a named screen, and capture it.

`run_duckstation.sh` boots the game and `boot_check.sh` proves it booted.
This is the third step section 3.4 of the plan asks for: getting *to* a
screen, because without an oracle the screen is the oracle (section 4.1)
and a field is only mapped when a poke changes what it shows.

This replaced `drive.sh` on 2026-09-02. The shell version was inherited
rather than chosen -- `run_duckstation.sh` was already shell and the driver
grew onto it -- and it cost three things that are gone here: bash re-reads a
script by *byte offset*, so editing the file mid-run corrupted a run; every
poll shelled out to `identify -format` and got a string back; and a route
was a space-separated string that no test could exercise without an
emulator. What stayed in shell is what is shell-pure: the launcher, whose
`--kill` carries the `pgrep`/`fusermount` traps.

Usage:

    python3 tools/pes2/drive.py <copy.cue> --screen main-menu --out-dir DIR
    python3 tools/pes2/drive.py <copy.cue> --list
    python3 tools/pes2/drive.py --self-check     # no emulator needed

Exits 77 -- ctest reads it as skipped -- when the machine cannot run it.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SKIP = 77

try:
    from PIL import Image as PILImage
except ImportError:                                          # pragma: no cover
    PILImage = None


class Skip(Exception):
    """The machine cannot run this; ctest should read it as skipped."""


class Fail(Exception):
    """The run reached a state the route did not allow."""


# --- the pad -----------------------------------------------------------
#
# **The bindings are read from the emulator's own configuration, not
# declared here.** The launcher used to write a `[Pad1]` section that
# DuckStation never read -- the AppImage resolves its data directory from
# $HOME, not from XDG_DATA_HOME -- and twelve boots went into pressing keys
# bound to nothing before that was measured. The user's call on 2026-09-02
# was to stop isolating: this machine's DuckStation is for this project, so
# its configuration is the one that runs and the launcher writes none.
#
# Reading it rather than declaring it is what makes that work, and it has a
# side benefit: remapping a button in the DuckStation GUI is all it takes,
# with nothing to change here. Falls back to DuckStation's defaults if
# there is no file to read.
#
# The two namespaces disagree, which is the other half of the trap: the
# value in the configuration is DuckStation's name, and what xdotool needs
# is an X keysym. `UpArrow` against `Up`, `Enter` against `Return`.
KEYSYM = {
    "UpArrow": "Up", "DownArrow": "Down",
    "LeftArrow": "Left", "RightArrow": "Right",
    "Enter": "Return", "Space": "space", "Backspace": "BackSpace",
    "Escape": "Escape", "Tab": "Tab",
}

DEFAULT_PAD = {
    "cross": "m", "circle": "k", "square": "j", "triangle": "i",
    "start": "Return", "select": "space", "l1": "f", "r1": "g",
    "up": "Up", "down": "Down", "left": "Left", "right": "Right",
}


def _keysym(name):
    """One DuckStation key name as the keysym xdotool sends."""
    if name in KEYSYM:
        return KEYSYM[name]
    if len(name) == 1 and name.isalpha():
        # Lowercase on purpose: the capital keysym is produced by holding
        # Shift, and the binding never asked for a modifier.
        return name.lower()
    return name


def load_pad(path=None):
    """The [Pad1] bindings actually in force, as xdotool keysyms."""
    path = path or os.path.expanduser(
        "~/.local/share/duckstation/settings.ini")
    pad = dict(DEFAULT_PAD)
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            section = None
            for line in fh:
                line = line.strip()
                if line.startswith("["):
                    section = line.strip("[]")
                    continue
                if section != "Pad1" or "=" not in line:
                    continue
                key, _, value = (x.strip() for x in line.partition("="))
                if not value.startswith("Keyboard/"):
                    continue
                button = key.lower()
                if button in pad:
                    pad[button] = _keysym(value.split("/", 1)[1])
    except OSError:
        pass
    return pad


PAD = load_pad()

HOTKEY = {
    "fast-forward": "Tab", "save-state": "F2", "load-state": "F1",
    "pause": "space",
}

# **The press has to be held.** `xdotool key X` presses and releases in the
# same instant and the game never sees the button down: measured on the
# title screen, three taps -- plain, with windowfocus, with
# --clearmodifiers -- left the frame identical to six decimal places, while
# a keydown / 1 s / keyup went straight through. A PSX game polls the pad
# once a frame; a tap can fall entirely between two polls. 0.4 s was not
# enough on the title screen.
HOLD = float(os.environ.get("PES2_HOLD", "1.0"))

# The title screen's signature, measured over five runs of the shell driver
# it replaced: means 0.5502..0.5528, standard deviations 0.3397..0.3411.
# The spread is the sparkle animation, an order of magnitude inside the
# tolerance.
TITLE = (0.550, 0.341)

# The main menu, measured over three consecutive runs on 2026-09-02:
# means 0.140639, 0.140682, 0.140679; standard deviations 0.212488,
# 0.212449, 0.212435.
MAIN_MENU = (0.1407, 0.2124)


# --- frames ------------------------------------------------------------

class Frame:
    """One capture of the game window, compared by region rather than by
    a single number over the whole picture.

    The shell version waited on the mean and standard deviation of the
    entire frame, and that is why the route into the menu never closed:
    two different screens can share a mean. A region is what tells them
    apart.
    """

    def __init__(self, path):
        self.path = path
        with PILImage.open(path) as im:
            self.image = im.convert("RGB").copy()
        self.size = self.image.size

    def stats(self, box=None):
        """(mean, standard deviation) over `box`, normalised to 0..1."""
        im = self.image.crop(box) if box else self.image
        n = im.width * im.height * 3
        if n == 0:
            return 0.0, 0.0
        data = im.tobytes()
        total = sum(data)
        mean = total / n
        var = sum((b - mean) ** 2 for b in data) / n
        return mean / 255.0, (var ** 0.5) / 255.0

    def difference(self, other, box=None):
        """Mean absolute difference per channel, 0..1. The primitive the
        whole driver is built on: `settle` waits for it to fall, `changed`
        waits for it to rise."""
        a = self.image.crop(box) if box else self.image
        b = other.image.crop(box) if box else other.image
        if a.size != b.size:
            return 1.0
        da, db = a.tobytes(), b.tobytes()
        if not da:
            return 0.0
        return sum(abs(x - y) for x, y in zip(da, db)) / (len(da) * 255.0)

    def is_black(self, tol=0.01):
        mean, sd = self.stats()
        return mean < tol and sd < tol


# --- the session -------------------------------------------------------

class Session:
    """A booted emulator plus the window it draws into."""

    def __init__(self, cue, out_dir, display=None, pad_type=None,
                 verbose=True):
        self.cue = cue
        self.out_dir = out_dir
        self.display = display or os.environ.get("PES2_DISPLAY", ":98")
        self.pad_type = pad_type
        self.verbose = verbose
        self.window = None
        self.shots = []
        self._tmp = None

    # -- lifecycle --

    def __enter__(self):
        env = dict(os.environ, PES2_IMAGE=self.cue,
                   PES2_DISPLAY=self.display)
        if self.pad_type:
            env["PES2_PAD_TYPE"] = self.pad_type
        launcher = os.path.join(HERE, "run_duckstation.sh")
        out = subprocess.run([launcher], env=env, capture_output=True,
                             text=True)
        if out.returncode != 0:
            raise Fail("the launcher failed:\n" + (out.stderr or out.stdout))
        for line in out.stdout.splitlines():
            if line.startswith("WINDOW="):
                self.window = line.split("=", 1)[1].strip()
        if not self.window:
            raise Fail("no window id from the launcher")
        self._tmp = tempfile.mkdtemp(prefix="pes2-frames-")
        self.say(f"window {self.window} on {self.display}")
        return self

    def __exit__(self, *exc):
        subprocess.run([os.path.join(HERE, "run_duckstation.sh"), "--kill"],
                       capture_output=True)
        if self._tmp:
            shutil.rmtree(self._tmp, ignore_errors=True)
        return False

    def say(self, msg):
        if self.verbose:
            print(f"  {msg}", flush=True)

    # -- input --
    #
    # Keyboard focus follows the pointer on a bare Xvfb -- there is no
    # window manager to hand it over -- and `xdotool key --window` goes
    # through XSendEvent, which DuckStation ignores. Move the pointer in,
    # then press without --window.

    def _xdotool(self, *args):
        env = dict(os.environ, DISPLAY=self.display, XAUTHORITY="")
        return subprocess.run(["xdotool", *args], env=env,
                              capture_output=True, text=True)

    def _aim(self):
        self._xdotool("windowfocus", self.window)
        self._xdotool("mousemove", "--window", self.window, "20", "20")

    def press(self, button, hold=HOLD):
        """Hold a pad button down for `hold` seconds, then release."""
        key = PAD.get(button, HOTKEY.get(button, button))
        self._aim()
        self._xdotool("keydown", key)
        time.sleep(hold)
        self._xdotool("keyup", key)
        self.say(f"press {button}")

    def hold(self, button, seconds):
        """Hold a hotkey down for a stretch. Fast forward is a *hold* in
        DuckStation, not a toggle, so a tap on Tab does nothing useful."""
        key = PAD.get(button, HOTKEY.get(button, button))
        self._aim()
        self._xdotool("keydown", key)
        time.sleep(seconds)
        self._xdotool("keyup", key)
        self.say(f"held {button} for {seconds}s")

    def wait_for_stats(self, mean, sd, tol=0.02, timeout=120, poll=0.0,
                       box=None):
        """Wait until the frame's mean and standard deviation both land
        within `tol` of the given pair, and return that frame.

        This is how a screen is recognised rather than merely waited for,
        and it is the only wait that works on the title: the attract loop
        never rests, so `settle` cannot find it -- holding fast forward for
        180 s never brought the picture still even once -- and the title is
        only motionless for a few seconds before handing itself to the demo.

        `poll` defaults to zero because a capture already costs a couple of
        tenths of a second, and every one of those spent sleeping is a
        chance to miss the screen.
        """
        deadline = time.time() + timeout
        best = None
        while time.time() < deadline:
            frame = self.capture()
            m, s = frame.stats(box)
            near = abs(m - mean) + abs(s - sd)
            if best is None or near < best[0]:
                best = (near, m, s)
            if abs(m - mean) <= tol and abs(s - sd) <= tol:
                self.say(f"recognised  mean={m:.6f} sd={s:.6f}")
                return frame
            if poll:
                time.sleep(poll)
        raise Fail(f"no frame matched mean={mean} sd={sd} (+-{tol}) within "
                   f"{timeout}s; closest was mean={best[1]:.6f} "
                   f"sd={best[2]:.6f}")

    # -- output --

    def capture(self, label=None):
        """Grab the window. Unlabelled captures are scratch frames used for
        waiting and are deleted with the session; labelled ones are the
        deliverable and land in out_dir."""
        if label:
            path = os.path.join(self.out_dir, f"{label}.png")
        else:
            path = os.path.join(self._tmp, f"f{time.time():.3f}.png")
        env = dict(os.environ, DISPLAY=self.display, XAUTHORITY="")
        r = subprocess.run(["import", "-window", self.window, path],
                           env=env, capture_output=True, text=True)
        if r.returncode != 0 or not os.path.exists(path):
            raise Fail(f"capture failed: {r.stderr.strip()}")
        frame = Frame(path)
        if label:
            mean, sd = frame.stats()
            self.say(f"shot {label}  mean={mean:.6f} sd={sd:.6f}  {path}")
            self.shots.append(path)
        return frame

    # -- waiting --
    #
    # Every wait is expressed against the frame, never against the clock.
    # The intro is about two minutes of FMV whose length varies with disc
    # read speed and with fast forward, and a fixed sleep either overshoots
    # into the attract demo or stops short.

    def settle(self, tol=0.004, stable_for=2, timeout=60, box=None,
               poll=1.0, allow_black=False):
        """Wait until the picture stops moving: `stable_for` consecutive
        polls whose difference from the previous one is under `tol`.

        **A black screen is still, and that is not what a route wants.**
        Loading between screens is black, so the first version of this
        returned the moment the title faded out and the step that followed
        pressed Down into a loading screen. Black does not count as settled
        unless the caller says it does.
        """
        deadline = time.time() + timeout
        previous = self.capture()
        run = 0
        d = 1.0
        while time.time() < deadline:
            time.sleep(poll)
            current = self.capture()
            d = current.difference(previous, box)
            previous = current
            if not allow_black and current.is_black():
                run = 0
                continue
            run = run + 1 if d < tol else 0
            if run >= stable_for:
                mean, sd = current.stats()
                self.say(f"settled  mean={mean:.6f} sd={sd:.6f}")
                return current
        raise Fail(f"the picture never settled within {timeout}s "
                   f"(last difference {d:.6f})")

    def changed(self, reference, tol=0.02, timeout=60, box=None, poll=1.0):
        """Wait until the picture differs from `reference` by more than
        `tol`. This is how a route knows a button was accepted."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            time.sleep(poll)
            current = self.capture()
            d = current.difference(reference, box)
            if d > tol:
                self.say(f"changed by {d:.6f}")
                return current
        raise Fail(f"the picture did not change within {timeout}s "
                   f"(last difference {d:.6f})")

    def nudge(self, button, tol=0.001, tries=6, settle_for=1.2):
        """Press until *something* changes, however small.

        A highlight moving one row is a difference of about 0.006 over the
        whole frame, and confirming a choice about 0.02 -- both far below
        what `advance` looks for. And the press does not always take on the
        first try: a screen that has just faded in swallows it, measured on
        the language screen, where the same Down registered in one run and
        not in the next. So press again rather than declaring the button
        broken.
        """
        before = self.capture()
        for attempt in range(1, tries + 1):
            self.press(button)
            time.sleep(settle_for)
            after = self.capture()
            d = after.difference(before)
            if d > tol:
                self.say(f"{button} took on try {attempt} (diff {d:.5f})")
                return after
        raise Fail(f"{tries} presses of {button} changed nothing at all")

    def advance(self, button="cross", tol=0.02, timeout=45, tries=4,
                box=None, allow_black=False):
        """Press until the picture changes, then wait for it to settle.

        The routine the whole happy path is made of. A single press is not
        reliable on these screens -- the title wants the button down across
        several polls, and a press landing during a fade is swallowed -- so
        this presses again rather than failing, and says how many it took.
        """
        before = self.capture()
        for attempt in range(1, tries + 1):
            self.press(button)
            try:
                self.changed(before, tol=tol, timeout=timeout // tries or 8,
                             box=box)
            except Fail:
                continue
            return self.settle(timeout=timeout, box=box,
                               allow_black=allow_black)
        raise Fail(f"{tries} presses of {button} left the picture unchanged")


# --- the routes --------------------------------------------------------
#
# A route is a function taking a Session. Naming them here rather than
# encoding them as strings is half the point of the rewrite: a route can
# branch, retry and assert.

def route_title(s):
    """Fast forward through the intro FMV and stop on the title.

    **Cross does not skip this video.** Twenty-four presses over eighty
    seconds left the FMV running, measured on 2026-09-02. Fast forward is
    what gets past it, and this recipe -- 25 s held, then wait for the
    title's signature -- matched five times out of five.

    The wait is by signature and not by stillness: holding fast forward for
    180 s never once brought the picture to rest, because the attract loop
    that follows the title is as animated as the movie before it.
    """
    time.sleep(6)
    s.hold("fast-forward", 25)
    frame = s.wait_for_stats(*TITLE, tol=0.02, timeout=120)
    s.capture("title")
    return frame


def route_main_menu(s):
    """The happy path from boot to the main menu.

    Walked by hand by the user on 2026-09-02 and measured here step by
    step. The buttons are not all the same one, which is what took a dozen
    boots to see:

      1. Get past the opening video -- by fast forward. Cross does not skip
         it, and neither does anything else that was tried.
      2. The title takes **Start**, not Cross. Five Crosses on it changed
         nothing at all, and the black frame that followed was the screen
         timing out into the attract demo on its own.
      3. `Seleziona Lingua`: Italiano and Spagnolo. Down, then Cross.
      4. A Si / No confirmation. Up to land on Si, then Cross.
      5. The memory-card slot screen, options 1 and 2. Cross.
      6. The main menu.
    """
    s.say("step 1: fast forward, then wait for the title")
    time.sleep(6)
    s.hold("fast-forward", 25)
    s.wait_for_stats(*TITLE, tol=0.02, timeout=120)

    # No capture between recognising the title and pressing. The title
    # hands itself to the attract demo within seconds -- one `import` in
    # between was enough to lose it, measured: the frame went 0.550 to
    # 0.197 across a single capture.
    s.say("step 2: Start on the title")
    s.press("start")
    s.settle(tol=0.006, timeout=45)
    language = s.settle(tol=0.006, timeout=45)
    s.capture("language")

    s.say("step 3: choosing Spagnolo")
    s.nudge("down")
    s.capture("language-chosen")
    s.nudge("cross")
    confirm = s.capture("confirm")

    s.say("step 4: answering Si")
    s.nudge("up")
    s.capture("confirm-chosen")
    s.press("cross")
    frame = s.settle(tol=0.006, timeout=60)
    if frame.difference(confirm) < 0.05:
        raise Fail("Cross on the Si/No box did not leave the language screen")
    s.capture("memory-card")

    s.say("step 5: past the memory-card slot")
    frame = s.advance("cross", tol=0.05, timeout=60)

    s.capture("main-menu")
    if frame.is_black():
        raise Fail("the main menu came out black -- the route landed "
                   "somewhere else")
    return frame


def route_team_select(s):
    raise Fail("the route past the main menu is not established -- "
               "see PES2-TASK-03")


ROUTES = {
    "title": route_title,
    "main-menu": route_main_menu,
    "team-select": route_team_select,
}


# --- self-check --------------------------------------------------------
#
# What the shell version could not have: the frame logic exercised without
# an emulator, so `pes2_selftest` covers it and a broken comparison is
# caught on a machine with no DuckStation at all.

def self_check():
    if PILImage is None:
        raise Skip("PIL is missing")
    tmp = tempfile.mkdtemp(prefix="pes2-drive-selfcheck-")
    try:
        def write(name, colour, size=(64, 48)):
            path = os.path.join(tmp, name)
            PILImage.new("RGB", size, colour).save(path)
            return Frame(path)

        black = write("black.png", (0, 0, 0))
        white = write("white.png", (255, 255, 255))
        grey = write("grey.png", (128, 128, 128))

        assert black.is_black(), "a black frame must read as black"
        assert not grey.is_black(), "a grey frame must not read as black"

        mean, sd = black.stats()
        assert mean == 0.0 and sd == 0.0, f"black stats were {mean}, {sd}"
        mean, sd = white.stats()
        assert abs(mean - 1.0) < 1e-9, f"white mean was {mean}"

        assert black.difference(black) == 0.0, "a frame differs from itself"
        assert abs(black.difference(white) - 1.0) < 1e-9, \
            "black against white must be a full difference"
        assert abs(black.difference(grey) - 128 / 255) < 1e-6, \
            "grey is half way"

        # A region tells apart two frames a whole-frame mean cannot. This
        # is the failure that kept the menu route from closing.
        left = PILImage.new("RGB", (64, 48), (0, 0, 0))
        left.paste(PILImage.new("RGB", (32, 48), (255, 255, 255)), (0, 0))
        right = PILImage.new("RGB", (64, 48), (0, 0, 0))
        right.paste(PILImage.new("RGB", (32, 48), (255, 255, 255)), (32, 0))
        lp = os.path.join(tmp, "left.png")
        rp = os.path.join(tmp, "right.png")
        left.save(lp)
        right.save(rp)
        lf, rf = Frame(lp), Frame(rp)
        assert abs(lf.stats()[0] - rf.stats()[0]) < 1e-9, \
            "the two halves must share a whole-frame mean"
        assert lf.difference(rf, box=(0, 0, 32, 48)) > 0.9, \
            "a region must tell them apart"

        # Different sizes are a full difference, not a crash.
        small = write("small.png", (0, 0, 0), size=(8, 8))
        assert small.difference(black) == 1.0, \
            "mismatched sizes must read as fully different"

        for name in ("title", "main-menu", "team-select"):
            assert name in ROUTES, f"route {name} went missing"
        for button in ("cross", "down", "up", "start"):
            assert button in PAD, f"pad button {button} went missing"

        print("SELF-CHECK OK: frame comparison, regions, routes, pad map")
        return 0
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


# --- entry point -------------------------------------------------------

def preflight(cue, display):
    if PILImage is None:
        raise Skip("PIL is missing")
    if not cue:
        raise Fail("usage: drive.py <copy.cue> --screen NAME --out-dir DIR")
    if "/roms/" in os.path.abspath(cue):
        raise Fail("refusing to boot roms/ -- copy first")
    if not os.path.isfile(cue):
        raise Skip(f"no image at {cue}")
    appimage = os.environ.get(
        "PES2_DUCKSTATION",
        os.path.expanduser("~/Applications/DuckStation-x64.AppImage"))
    if not os.path.isfile(appimage):
        raise Skip("no DuckStation AppImage")
    for binary in ("import", "xdotool"):
        if shutil.which(binary) is None:
            raise Skip(f"{binary} is missing")
    env = dict(os.environ, DISPLAY=display, XAUTHORITY="")
    if subprocess.run(["xdotool", "getdisplaygeometry"], env=env,
                      capture_output=True).returncode != 0:
        raise Skip(f"no X server on {display}")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", nargs="?", help=".cue of a working copy")
    ap.add_argument("--screen", default=os.environ.get("PES2_SCREEN"))
    ap.add_argument("--out-dir", default=os.environ.get("PES2_OUTDIR"))
    ap.add_argument("--display", default=os.environ.get("PES2_DISPLAY", ":98"))
    ap.add_argument("--pad-type", default=os.environ.get("PES2_PAD_TYPE"),
                    help="AnalogController (default) or DigitalController")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for name in ROUTES:
            print(f"  {name}")
        return 0

    try:
        if args.self_check:
            return self_check()

        cue = args.image or os.environ.get("PES2_IMAGE")
        preflight(cue, args.display)
        if not args.screen:
            raise Fail("give --screen NAME (see --list)")
        if args.screen not in ROUTES:
            raise Fail(f"no route named {args.screen}")

        out_dir = args.out_dir or tempfile.mkdtemp(prefix="pes2-drive-")
        os.makedirs(out_dir, exist_ok=True)
        print(f"route: {args.screen} -> {out_dir}")

        with Session(cue, out_dir, display=args.display,
                     pad_type=args.pad_type) as s:
            ROUTES[args.screen](s)
        print(f"DRIVE OK: {out_dir}")
        return 0
    except Skip as e:
        print(f"skipping: {e}")
        return SKIP
    except Fail as e:
        print(f"DRIVE FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

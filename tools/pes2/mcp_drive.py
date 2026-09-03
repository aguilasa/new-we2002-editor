#!/usr/bin/env python3
"""Drive PES2 to a named screen through the emulator's MCP server.

The same four routes as `drive.py`, driven by calls instead of by `xdotool`.
What changes is not speed but **determinism**: with the emulator paused
between one button and the next, five presses are five rows, and the route
can say so as an assertion instead of hoping.

    python3 tools/pes2/mcp_drive.py <copy.cue> --screen edit --out-dir DIR
    python3 tools/pes2/mcp_drive.py <copy.cue> --screen main-menu --save-state
    python3 tools/pes2/mcp_drive.py --measure-menu     # against a live game
    python3 tools/pes2/mcp_drive.py --self-check       # no emulator needed

Exits 77 -- ctest reads it as skipped -- when the machine cannot run it.

WHY THE FRAME SIGNATURES ARE MOSTLY GONE
----------------------------------------
`drive.py` recognises a screen by the mean **and standard deviation** of the
whole picture, and PES2-TASK-34 had to answer whether those survive the
change of binary. They were measured on 2026-09-03 against what section 6.11
recorded on 2026-09-02, and the answer split:

    screen         recorded (mean/sd)   fork          AppImage, today
    title          0.5502..0.5528 /     0.550140..    0.555093 /
                   0.3397..0.3411       0.552796 /    0.358742
                                        0.359942..
                                        0.360497
    main menu      0.140639..0.140682   0.140514..    (not re-run)
                                        0.140611
    flag grid      0.1685 / 0.2488      0.168337..
                                        0.168602 /
                                        0.248755..
                                        0.249048

**Every mean reproduced. The title's standard deviation did not, and it did
not under either binary.** That last clause is the finding, and it took
three wrong guesses to get to:

* it is not the fork -- the *AppImage* is byte-identical to the one that
  produced 0.341 (29 Aug, untouched) and gives 0.3587 today;
* it is not the capture path -- the same paused frame through MCP and
  through `import -window` agrees to 0.002245;
* it is not the resolution scale -- forced to 1x and back to 4x through
  `set_setting`, the title read 0.360384 and 0.360408;
* it is not the crop -- insetting the frame moves mean and standard
  deviation *together*, and the mean did not move.

What did change is unidentified. That is precisely why the pair is
**retired as the criterion**: a number that cannot be reproduced or
explained a day later, on the same binary, is not a criterion -- and it had
0.0006 of margin left inside the old +-0.02 tolerance, so it was one small
drift from failing anyway.

The means stay, because they reproduced across a binary change, a settings
change and a day. Everything else a route needs to know it now asserts
by counting, which is what `frame_step` is for.

HOW A ROW IS COUNTED
--------------------
Measured on the main menu, nine captures over a region holding just the
list, on 2026-09-03:

    the same row again      0.0002 .. 0.0005
    any two different rows  0.0082 .. 0.0125

Twenty times apart, so `SAME_ROW = 0.003` sits clear of both. The list has
**seven** rows, and that count is measured here rather than declared: the
walk wraps at r0==r7 and r1==r8. `menu_pick` uses this twice -- every press
must move, and no press may land on a row already visited -- which makes
"one key too many" a failure instead of a silent overshoot. That is the
assertion `drive.menu_pick` could not make: on a display without a window
manager a press that was merely slow to draw is indistinguishable from one
that was dropped, so it counted how many *seemed* to register.

The region matters. Over the whole frame, the same row twice differs by
0.0003 while the animated ball behind the menu moves by more than the
highlight does; crop to the list and the two separate cleanly.

WHERE STILLNESS WORKS AND WHERE IT DOES NOT
-------------------------------------------
Stepping the emulator makes a *truly* static screen bit-identical from one
look to the next, which is worth having: the opening's blue boxes settle at
a tolerance of exactly zero, where `drive.settle` needed 0.004, 0.006 and
0.012 guessed per screen.

**It stops there, and every screen past the opening proved it.** The main
menu rotates a ball; Modo Editar walks a player; the pad assignment blinks
between two pictures 0.000346 apart; the flag grid blinks a cursor. On all
four, whether two looks come out identical depends on where the slice lands
in the animation -- at two-second slices Modo Editar aligned and at
one-second slices it never did, which is a coin toss dressed as a criterion.

So those four are recognised by their **mean**, measured here, and the
assertions that carry weight are the counted ones. Stillness is for the
screens that really are still.
"""

import argparse
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import fork                                                   # noqa: E402
from drive import Frame, Fail, Skip, SKIP, PILImage           # noqa: E402
from mcp import NotRunning, ToolError                         # noqa: E402

# --- what a screen looks like ------------------------------------------

# The seven main-menu items, and nothing else -- see the module note.
MENU_LIST = (45, 85, 375, 345)
# The submenu that Cross opens over the right of the menu.
SUBMENU = (370, 95, 760, 255)

# Below this, two captures are the same menu row; above it, two different
# rows. Measured 0.0005 against 0.0082 on 2026-09-03.
SAME_ROW = 0.003

# The title never rests -- the attract loop is as animated as the movie
# before it -- so it is the one screen that cannot be recognised by
# stillness. Mean only: 0.550116..0.555093 over both binaries on
# 2026-09-03, against 0.5502..0.5528 recorded the day before. The standard
# deviation is not part of this any more; see the module note.
TITLE_MEAN = 0.5526
TITLE_TOL = 0.010

# The main menu, for the one check a route still makes by signature: that
# `from_main_menu` landed where it thinks. 0.140514..0.140611 under the
# fork, 0.140639..0.140682 under the AppImage.
MAIN_MENU_MEAN = 0.1406
MAIN_MENU_TOL = 0.010

# The Modo Editar menu -- Crear, Cambiar, Borrar and four more. It cycles
# something slowly, so consecutive looks are bit-identical for a few seconds
# at a time and `still` does settle on it. 0.154324..0.155040 measured.
EDIT_MEAN = 0.1547
EDIT_TOL = 0.010

# The pad-assignment screen between the submenu and the grid, and the flag
# grid itself. Neither ever goes bit-identical -- both blink a cursor -- so
# both are recognised by mean. 0.188149..0.188408 and 0.168337..0.168602
# measured under the fork; the grid's AppImage reading was 0.1685.
PAD_ASSIGN_MEAN = 0.1883
TEAM_SELECT_MEAN = 0.1685
SCREEN_TOL = 0.010

# Below this a frame is a loading screen, not a destination. The way into
# Modo Editar goes splash (0.0042), black (0.0000), screen (0.1549); the
# darkest real screen of the four routes is the language one at 0.043.
LIT = 0.02

SERIAL = "SLES-03957"
STATE_DIR = os.path.expanduser("~/.local/share/duckstation/savestates")

# A press has to be down long enough for the game to poll it, and then the
# game needs frames to act on it. Three down and seventeen after was
# measured to move exactly one menu row, every time, over the walks of
# 2026-09-03. Under `pause` these are exact frames, not a wall-clock guess:
# this is the number `drive.HOLD` and `drive.TAP` were approximating.
PRESS_FRAMES = 3
AFTER_FRAMES = 17


def state_path(slot=1):
    return os.path.join(STATE_DIR, f"{SERIAL}_{slot}.sav")


# --- the session -------------------------------------------------------

class McpSession:
    """A booted fork, its window, and an MCP session against it.

    Same shape as `drive.Session` where the routes need it -- `capture`,
    `press`, `save_state` -- so that the two can be read side by side. What
    it adds is `step`, `run` and the assertions those make possible.
    """

    def __init__(self, cue, out_dir, display=None, verbose=True):
        self.cue = cue
        self.out_dir = out_dir
        self.display = display or os.environ.get("PES2_DISPLAY", ":98")
        self.verbose = verbose
        self.client = None
        self.window = None
        self.pid = None
        self.shots = []
        self.presses = 0
        self.steps = 0
        self._tmp = None
        self._own = True

    # -- lifecycle --

    def __enter__(self):
        if PILImage is None:
            raise Skip("PIL is missing")
        self.pid, self.window, self.client = fork.launch(
            self.cue, display=self.display, verbose=self.verbose)
        self._tmp = tempfile.mkdtemp(prefix="pes2-mcp-frames-")
        self.pause()
        return self

    def __exit__(self, *exc):
        if self._own:
            fork.kill(verbose=False)
        if self._tmp:
            shutil.rmtree(self._tmp, ignore_errors=True)
        return False

    @classmethod
    def attach(cls, out_dir, display=None, verbose=True):
        """Talk to an emulator someone else started, and leave it running.

        This is what `pad.py` is: the user has the game up in front of them
        and wants one action sent to it.
        """
        from mcp import Client
        s = cls(None, out_dir, display=display, verbose=verbose)
        s.client = Client()
        s.client.initialize()
        s._own = False
        s._tmp = tempfile.mkdtemp(prefix="pes2-mcp-frames-")
        return s

    def say(self, msg):
        if self.verbose:
            print(f"  {msg}", flush=True)

    # -- the emulator clock --

    def pause(self):
        self.client.call("pause")

    def resume(self):
        self.client.call("continue")

    def frame(self):
        return self.client.call("get_status")["frame_number"]

    def step(self, n=1):
        """Advance exactly `n` frames and stay paused.

        Costs about 57 ms a frame over the wire, so it is for precision --
        a button and its consequence -- and `run` is for distance.
        """
        for _ in range(n):
            self.client.call("frame_step")
        self.steps += n

    def run(self, seconds, fast=False):
        """Let it run for a stretch of wall clock, then pause again.

        Loading screens are hundreds of frames long and stepping through
        them one call at a time costs three times real time. Fast forward
        makes the distance cheaper still; it is a hold in DuckStation, not
        a toggle, which is why it is set and cleared rather than tapped.
        """
        if fast:
            self.client.call("set_speed", fast_forward=True)
        self.resume()
        time.sleep(seconds)
        self.pause()
        if fast:
            self.client.call("set_speed", fast_forward=False)

    # -- input --

    def press(self, button, frames=PRESS_FRAMES, after=AFTER_FRAMES):
        """Hold a pad button for `frames` frames, then let the game act.

        `duration_frames` releases it on the emulator's own clock, so
        neither the hold nor the gap depends on how fast this script is
        talking to it. There is no pointer to aim, no focus to steal and no
        auto-repeat to outrun -- the three things section 6.11 calibrated
        by trial.
        """
        self.client.call("press_button", button=button.capitalize()
                         if button.islower() else button,
                         duration_frames=frames)
        self.step(frames + after)
        self.presses += 1

    # -- output --

    def capture(self, label=None):
        """Grab the emulator's own frame buffer.

        Not `import -window`: the picture comes out of the emulator, so a
        modal sitting on top of the game window cannot get into it, and the
        game does not have to be on a mapped, unobscured window at all.
        """
        if label:
            path = os.path.join(self.out_dir, f"{label}.png")
        else:
            path = os.path.join(self._tmp, "scratch.png")
        self.client.call("take_screenshot", path=path)
        if not os.path.exists(path):
            raise Fail(f"the emulator reported a screenshot at {path} and "
                       f"there is no file there")
        frame = Frame(path)
        if label:
            mean, sd = frame.stats()
            self.say(f"shot {label}  mean={mean:.6f} sd={sd:.6f}  {path}")
            self.shots.append(path)
        return frame

    # -- waiting --

    def still(self, box=None, tol=1e-6, stable_for=2, slice_seconds=0.25,
              budget=90, allow_black=False):
        """Let it run in slices until the picture stops changing.

        `tol` is *exact equality* by default, which is a thing this driver
        can afford and the `xdotool` one could not: with the emulator
        stopped when the picture is taken, a static screen is bit-identical
        from one look to the next, and the tolerances `drive.settle` had to
        guess at -- 0.004, 0.006, 0.012 per screen -- become one number that
        needs no calibration.

        The advance is by clock rather than by `step`, and deliberately: a
        round trip costs about 57 ms, so ten frames stepped is 570 ms
        against 310 ms for the same distance run. Frames are for precision,
        seconds are for distance. `press` is where the exactness has to be.

        A black screen is still and is never the destination, so it does not
        count unless the caller says it does.
        """
        previous = None
        run = 0
        for _ in range(budget):
            self.run(slice_seconds)
            current = self.capture()
            if not allow_black and current.is_black():
                run, previous = 0, current
                continue
            if previous is not None and not previous.is_black() \
                    and current.difference(previous, box) <= tol:
                run += 1
            else:
                run = 0
            previous = current
            if run >= stable_for:
                mean, sd = current.stats()
                self.say(f"still  mean={mean:.6f} sd={sd:.6f}")
                return current
        raise Fail(f"the picture never settled within "
                   f"{budget * slice_seconds:.0f}s of running")

    def wait_for_mean(self, mean, tol, budget=90, seconds=1.0, fast=True):
        """Let it run in slices until the frame's mean lands near `mean`.

        The one wait left that is by signature, and it is a mean only: the
        title is never still and never differs from a known frame, so
        neither `still` nor a difference can find it. See the module note
        on why the standard deviation is no longer part of this.
        """
        best = None
        for _ in range(budget):
            self.run(seconds, fast=fast)
            m, _sd = self.capture().stats()
            if best is None or abs(m - mean) < abs(best - mean):
                best = m
            if abs(m - mean) <= tol:
                self.say(f"recognised  mean={m:.6f}")
                return self.capture()
        raise Fail(f"no frame reached mean={mean} (+-{tol}) in "
                   f"{budget} slices; the closest was {best:.6f}")

    def until_changed(self, reference, box=None, tol=SAME_ROW, batch=10,
                      budget=60):
        """Step until the picture differs from `reference`."""
        for _ in range(budget):
            self.step(batch)
            current = self.capture()
            d = current.difference(reference, box)
            if d > tol:
                return current
        raise Fail(f"the picture did not change within {budget * batch} "
                   f"frames")

    def until_lit(self, min_mean=LIT, seconds=1.0, budget=40, label=None):
        """Let it run until there is a real picture, not just a lit one.

        **A route that returns a black frame has not failed loudly enough.**
        Loading between screens is black, so a fixed wait that is a second
        short lands on it, and every downstream check -- a poke read off the
        screen, a signature, a diff -- then measures nothing while reporting
        success. `route_edit` did exactly that on its first run: five rows
        asserted, the right item confirmed, and `mean=0.000000` in the
        output.

        The threshold is a mean and not `is_black`, because **"not black" is
        not the same as "arrived"**: the way into Modo Editar is splash,
        then true black, then the screen -- 0.0042, 0.0000, 0.1549 -- and a
        black test stops on the splash, which is the second way the same
        route came back with nothing on it.
        """
        for _ in range(budget):
            frame = self.capture()
            if frame.stats()[0] >= min_mean:
                return frame
            self.run(seconds)
        raise Fail(f"nothing brighter than mean={min_mean} appeared in "
                   f"{budget * seconds:.0f}s"
                   + (f" on the way to {label}" if label else ""))

    # -- menus, counted --

    def menu_rows(self, box=MENU_LIST, limit=16):
        """How many rows this list has, measured by walking it until it
        wraps. Returns the count and leaves the cursor where it started.

        The main menu came out as 7, which is what is on screen.
        """
        seen = [self.capture()]
        for i in range(1, limit + 1):
            self.press("Down")
            current = self.capture()
            for j, earlier in enumerate(seen):
                if current.difference(earlier, box) <= SAME_ROW:
                    self.say(f"the list wraps: row {i} is row {j} again "
                             f"-> {i - j} rows")
                    return i - j
            seen.append(current)
        raise Fail(f"the list did not wrap within {limit} presses -- either "
                   f"it is longer than that, or {box} is the wrong region")

    def menu_pick(self, index, label, box=MENU_LIST, confirm=True):
        """Move `index` rows down and confirm, asserting every step.

        Two assertions, both of which `drive.menu_pick` wanted and could not
        have. Each press must move the highlight, and no press may land on
        a row the walk has already been on -- which is what catches a press
        too many, because the list wraps rather than stopping at the end.
        Confirming after a wrap is how the earlier driver picked Modo Copa
        when the route asked for Modo Editar.
        """
        seen = [self.capture()]
        for row in range(1, index + 1):
            self.press("Down")
            current = self.capture()
            moved = current.difference(seen[-1], box)
            if moved <= SAME_ROW:
                raise Fail(f"press {row} of {index} did not move the "
                           f"highlight (difference {moved:.6f} <= "
                           f"{SAME_ROW}) -- the list is shorter than asked, "
                           f"or the region is wrong")
            for j, earlier in enumerate(seen):
                if current.difference(earlier, box) <= SAME_ROW:
                    raise Fail(
                        f"press {row} of {index} landed back on row {j} -- "
                        f"the list has wrapped, so confirming here would "
                        f"pick the wrong item")
            seen.append(current)
        self.say(f"{index} rows down, every one of them measured")
        frame = self.capture(f"menu-{label}")
        if confirm:
            before = self.capture()
            self.press("Cross")
            frame = self.until_changed(before, tol=SAME_ROW)
        return frame

    # -- save states --

    def save_state(self, slot=1):
        """Save through MCP and check the file really moved.

        Pressing a hotkey and hoping is what made a previous session
        conclude "F2 wrote nothing" while looking in a directory DuckStation
        was not using.
        """
        path = state_path(slot)
        before = os.path.getmtime(path) if os.path.exists(path) else 0
        self.client.call("save_state", slot=slot)
        for _ in range(20):
            time.sleep(0.5)
            if os.path.exists(path) and os.path.getmtime(path) > before:
                self.say(f"saved slot {slot}  "
                         f"{os.path.getsize(path)} B  {path}")
                return path
        raise Fail(f"no save state appeared at {path}")

    def load_state(self, slot=1):
        if not os.path.exists(state_path(slot)):
            raise Fail(f"no save state at {state_path(slot)} -- make one "
                       f"with --save-state on a route that reaches a screen")
        self.client.call("load_state", slot=slot)
        self.step(2)
        self.say(f"loaded slot {slot}")


# --- the routes --------------------------------------------------------

def route_title(s):
    """Fast forward through the intro and stop on the title.

    Cross does not skip the opening video -- twenty-four presses over eighty
    seconds left it running, measured under the AppImage and unchanged here.
    Fast forward is what gets past it, and under the fork the title arrives
    about seven seconds in rather than the twenty-five the shell recipe
    held for.
    """
    frame = s.wait_for_mean(TITLE_MEAN, TITLE_TOL, budget=90, seconds=2.0)
    s.capture("title")
    return frame


def route_main_menu(s):
    """Boot to the main menu.

    The steps are the ones walked by hand on 2026-09-02 and re-walked
    through MCP on 2026-09-03. Two of them are not what a first guess would
    be: the title takes **Start**, not Cross, and there are two Crosses
    after the memory-card slot, not one -- a `Comprobando la MEMORY CARD`
    screen and an `Auto-Cargar completado` one, both of which are perfectly
    still and so fool a wait that looks for stillness alone.
    """
    s.say("through the intro to the title")
    route_title(s)

    s.say("Start on the title")
    s.press("Start")
    language = s.still(budget=120)
    s.capture("language")

    s.say("Spagnolo")
    s.press("Down")
    s.capture("language-chosen")
    s.press("Cross")
    confirm = s.still(budget=60)
    s.capture("confirm")
    if confirm.difference(language) < 0.001:
        raise Fail("Cross on the language did not open the confirmation")

    s.say("answering Si")
    s.press("Up")
    s.press("Cross")
    s.still(budget=90)
    s.capture("memory-card")

    # **Three still screens stand between the slot and the menu**, not one:
    # `Comprobando la MEMORY CARD`, `Auto-Cargar completado`, and the slot
    # screen itself. Each is perfectly motionless, so `still` recognises all
    # three equally and a fixed number of Crosses lands on whichever the
    # timing gives -- the first version of this asked for two and stopped on
    # the auto-load. One of them also advances on its own when the card
    # check finishes, so a Cross into it is swallowed.
    #
    # And **the destination is the one screen here that never goes still**:
    # a ball rotates behind the main menu, so a `still` on the way out of
    # this loop waits for ever. That is the limit of exact-equality
    # stillness, found by hitting it -- press, let it run, and judge by the
    # one signature that says the menu is the menu.
    s.say("past the memory card, its check and the auto-load")
    mean = None
    for _ in range(8):
        mean = s.capture().stats()[0]
        if abs(mean - MAIN_MENU_MEAN) <= MAIN_MENU_TOL:
            break
        s.press("Cross")
        s.run(4)
    else:
        raise Fail(f"eight Crosses after the memory-card slot and this is "
                   f"still not the main menu: mean={mean:.6f}, wanted "
                   f"{MAIN_MENU_MEAN} +-{MAIN_MENU_TOL}")

    frame = s.capture("main-menu")
    mean = frame.stats()[0]
    if abs(mean - MAIN_MENU_MEAN) > MAIN_MENU_TOL:
        raise Fail(f"this is not the main menu: mean={mean:.6f}, wanted "
                   f"{MAIN_MENU_MEAN} +-{MAIN_MENU_TOL}")
    return frame


def from_main_menu(s, slot=1):
    """Be at the main menu, by whatever is cheaper.

    A state parked there turns two and a half minutes of opening into a
    load. Either way it *verifies* rather than assumes: loading a state
    parked somewhere else is a silent way to shoot the wrong screen.
    """
    if os.path.exists(state_path(slot)):
        s.run(6)
        s.load_state(slot)
        s.run(2)
        frame = s.capture()
        if abs(frame.stats()[0] - MAIN_MENU_MEAN) <= MAIN_MENU_TOL:
            s.say("the state was on the main menu")
            return frame
        s.say("the state was parked elsewhere -- walking the opening")
    return route_main_menu(s)


def route_team_select(s):
    """Main menu -> Modo Partido -> Partido de exhibicion -> the flag grid.

    The grid is the screen PES2-TASK-04 needs: the name above it comes out
    of `SELECT.BIN` @3128, so a poke into that table changes what is
    captured here.
    """
    from_main_menu(s)

    s.say("Modo Partido")
    before = s.capture()
    s.press("Cross")
    s.until_changed(before, box=SUBMENU)
    s.capture("match-submenu")

    # **Neither of the next two screens is ever still**, and finding that
    # out cost a run each: the pad assignment blinks between two pictures
    # 0.000346 apart for ever, and the grid's cursor never rests either. So
    # neither is waited for by stillness -- that primitive belongs to the
    # flat blue boxes of the opening, which really are motionless. Here the
    # mean is the criterion, and it is the screen's own measured mean rather
    # than a tolerance guessed per screen.
    s.say("Partido de exhibicion")
    before = s.capture()
    s.press("Cross")
    s.until_changed(before, tol=0.02)
    s.until_lit(label="the pad assignment")
    s.wait_for_mean(PAD_ASSIGN_MEAN, SCREEN_TOL, budget=30, seconds=1.0,
                    fast=False)
    s.capture("pad-assignment")

    s.say("past the pad assignment")
    before = s.capture()
    s.press("Cross")
    s.until_changed(before, tol=0.02)
    s.until_lit(label="the flag grid")
    frame = s.wait_for_mean(TEAM_SELECT_MEAN, SCREEN_TOL, budget=30,
                            seconds=1.0, fast=False)
    s.capture("team-select")
    return frame


def route_edit(s):
    """Main menu -> Modo Editar, the sixth row.

    This is the route the frame counting is for. `Modo Editar` is five rows
    below `Modo Partido` on a list of seven, and the old driver reached it
    by pressing and looking; here every one of the five is asserted, and a
    sixth would be caught by the wrap rather than confirmed.
    """
    from_main_menu(s)
    s.say("five rows down to Modo Editar")
    s.menu_pick(5, "edit")
    # No `still` here: this screen renders an animated player beside the
    # list, so it never goes bit-identical, and the assertion that matters
    # was already made -- `menu_pick` measured all five rows and confirmed
    # the sixth. What is left is to wait out the load, and to *say* it
    # waited: four seconds was not enough and the route came back with a
    # black frame it was perfectly happy about.
    #
    # **Not `still`.** The screen has a player animating beside the list, so
    # whether two consecutive looks come out bit-identical depends on where
    # the slice lands in his walk cycle: at two-second slices it happened to
    # align and at one-second slices it never did, which is a coin toss
    # dressed as a criterion. Wait for the screen's own mean instead -- it
    # is the destination that is being asserted, not the stillness.
    s.until_lit(label="Modo Editar")
    frame = s.wait_for_mean(EDIT_MEAN, EDIT_TOL, budget=30, seconds=1.0,
                            fast=False)
    s.capture("edit")
    return frame


ROUTES = {
    "title": route_title,
    "main-menu": route_main_menu,
    "team-select": route_team_select,
    "edit": route_edit,
}


# --- the red case, against a live game ---------------------------------

def measure_menu(s):
    """Measure the main menu's length, and prove the assertion bites.

    Run against an emulator already on the main menu. It reports the row
    count it measured and then asks for one row too many, which **must**
    fail: that is the check `drive.py` could not write, and a green that
    was never able to go red is decoration.
    """
    rows = s.menu_rows()
    print(f"the main menu has {rows} rows (measured, not declared)")

    # Where the cursor is left does not matter: a walk of `rows` rows wraps
    # onto its own starting row from anywhere on a list of that length.
    try:
        s.menu_pick(rows, "one-too-many", confirm=False)
    except Fail as e:
        print(f"RED CASE OK: asking for {rows} rows failed -- {e}")
        return rows
    raise Fail(f"asking for {rows} rows on a {rows}-row list was accepted; "
               f"the wrap check is not working")


# --- self-check --------------------------------------------------------

def self_check(verbose=True):
    """What can be proved with no emulator: the thresholds and the routes."""
    bad = []

    def check(what, ok, detail=""):
        if verbose:
            print(f"  {'ok' if ok else 'FAIL'}   {what}"
                  + (f"  ({detail})" if detail and not ok else ""))
        if not ok:
            bad.append(f"{what}{': ' + detail if detail else ''}")

    for name in ("title", "main-menu", "team-select", "edit"):
        check(f"route {name} exists", name in ROUTES)
    check("the routes match drive.py's",
          set(ROUTES) == {"title", "main-menu", "team-select", "edit"})

    # The threshold has to sit between what was measured, with room on both
    # sides. Same row 0.0002..0.0005, different row 0.0082..0.0125.
    check("SAME_ROW is above the worst same-row reading",
          SAME_ROW > 0.0005, f"{SAME_ROW}")
    check("SAME_ROW is below the best different-row reading",
          SAME_ROW < 0.0082, f"{SAME_ROW}")

    # The menu region must be inside the frame the emulator hands over.
    x0, y0, x1, y1 = MENU_LIST
    check("the menu region is inside an 800x655 frame",
          0 <= x0 < x1 <= 800 and 0 <= y0 < y1 <= 655)
    x0, y0, x1, y1 = SUBMENU
    check("the submenu region is inside an 800x655 frame",
          0 <= x0 < x1 <= 800 and 0 <= y0 < y1 <= 655)

    # The title tolerance must still admit both binaries' means, because
    # that is the claim the module note makes.
    # Every title mean measured on either binary, on either day, has to
    # fall inside the one tolerance -- that is the claim the module note
    # makes, and it is the reason the mean survived and the sd did not.
    for reading in (0.550116, 0.550140, 0.552796, 0.555093, 0.5502, 0.5528):
        check(f"the title mean {reading} is recognised",
              abs(reading - TITLE_MEAN) <= TITLE_TOL)
    # And it must not admit the main menu, or the two screens are one.
    check("the title tolerance excludes the main menu",
          abs(MAIN_MENU_MEAN - TITLE_MEAN) > TITLE_TOL)
    for reading in (0.140514, 0.140682):
        check(f"the main-menu mean {reading} is recognised",
              abs(reading - MAIN_MENU_MEAN) <= MAIN_MENU_TOL)

    # The standard deviation really did move, on both binaries, which is
    # the reason it is gone: the old pair at +-0.02 had 0.0006 of margin.
    for reading, who in ((0.360497, "the fork"), (0.358742, "the AppImage")):
        check(f"the title sd under {who} outran the old tolerance",
              abs(reading - 0.341) > 0.017, f"{abs(reading - 0.341):.6f}")
    check("and the two binaries agree with each other on it",
          abs(0.360497 - 0.358742) < 0.003)

    check("a press is expressed in frames, not seconds",
          isinstance(PRESS_FRAMES, int) and isinstance(AFTER_FRAMES, int))

    if verbose:
        print("SELF-CHECK " + ("FAILED" if bad else
                               "OK: routes, thresholds, regions, signatures"))
    return bad


# --- entry point -------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", nargs="?", help=".cue of a working copy")
    ap.add_argument("--screen", default=os.environ.get("PES2_SCREEN"))
    ap.add_argument("--out-dir", default=os.environ.get("PES2_OUTDIR"))
    ap.add_argument("--display", default=os.environ.get("PES2_DISPLAY", ":98"))
    ap.add_argument("--save-state", type=int, metavar="SLOT", nargs="?",
                    const=1, default=None)
    ap.add_argument("--measure-menu", action="store_true",
                    help="against a running game already on the main menu")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.list:
        for name in ROUTES:
            print(f"  {name}")
        return 0
    if args.self_check:
        return 1 if self_check() else 0

    out_dir = args.out_dir or tempfile.mkdtemp(prefix="pes2-mcp-")
    os.makedirs(out_dir, exist_ok=True)

    try:
        if args.measure_menu:
            s = McpSession.attach(out_dir, display=args.display)
            s.pause()
            measure_menu(s)
            return 0

        cue = args.image or os.environ.get("PES2_IMAGE")
        if not args.screen:
            raise Fail("give --screen NAME (see --list)")
        if args.screen not in ROUTES:
            raise Fail(f"no route named {args.screen}")
        print(f"route: {args.screen} -> {out_dir}")
        started = time.time()
        with McpSession(cue, out_dir, display=args.display) as s:
            ROUTES[args.screen](s)
            if args.save_state is not None:
                s.save_state(args.save_state)
            print(f"MCP DRIVE OK: {out_dir}  "
                  f"{time.time() - started:.1f}s, {s.presses} presses, "
                  f"{s.steps} frames stepped")
        return 0
    except Skip as e:
        print(f"skipping: {e}")
        return SKIP
    except fork.Skip as e:
        print(f"skipping: {e}")
        return SKIP
    except NotRunning as e:
        print(f"skipping: {e}")
        return SKIP
    except (Fail, fork.Fail, ToolError) as e:
        print(f"MCP DRIVE FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

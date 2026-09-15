#!/usr/bin/env python3
"""The running game as the live oracle, and the way back to the LOOKS SET screen.

This project is privileged: the thing it is reverse-engineering can be asked.
The emulator is the fork with an MCP server -- the same one PES2 uses -- and
what it buys is not speed but a baseline.  `load_state` puts the machine back
in a state that is **bit-identical** every time, so a diff taken after changing
one field measures that field and nothing else.  Measured: two loads of slot 1,
four frames apart, differ by exactly 0.000000 over the whole picture.

Two save states stand in for a route.  The user recorded them on 2026-09-14
with the game already on LOOKS SET:

    slot 1 -- a goalkeeper       slot 2 -- an outfield player

Both were recorded on the ENGLISH disc, and the file name does not say so:
DuckStation names a state after the serial, and both the European and the
Japanese release boot `SLPM_870.56`.  A state made on the Japanese disc would
carry exactly the same name and bring unreadable menus with it, so what this
module trusts is the `media` field from **inside** the file.

Provenance (plan section 3.4): this module reads the emulator, not the disc.
It holds no address of its own -- the two load addresses come from
`layout.BASE`, like every other address in this tree.

Usage:
    python tools/looks/oracle.py --check          # no emulator, no states
    python tools/looks/oracle.py --check-states   # the two .sav, no emulator
    python tools/looks/oracle.py --adopt-states   # copy them into the project
    python tools/looks/oracle.py --check-live     # boots the game and measures
    python tools/looks/oracle.py --fields HAIR SKIN
    python tools/looks/oracle.py --tmds          # unknown (a), the other half
    python tools/looks/oracle.py --buffers       # what the residue bands are
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import shutil
import sys

import harness
import layout
import section

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PES2 = os.path.join(ROOT, "tools", "pes2")
if PES2 not in sys.path:
    sys.path.insert(0, PES2)

SKIP = 77
WINDOWS = os.name == "nt"


# --- what the environment names -------------------------------------------

RAM_BASE = 0x80000000  # not-an-address: the console's own RAM window, not a datum
RAM_SIZE = 2 * 1024 * 1024  # not-an-address: a size, in bytes
SANE_COUNT = 4 * 1024  # not-an-address: the ceiling a TMD count has to be under

OT_POINTER = 0x00FFFFFF  # not-an-address: the mask over an OT link, not a link
BUFFER_BANDS = (0x80153000, 0x80162000)  # not-an-address: RAM, not the disc
BUFFER_SIZE = 0x5000  # not-an-address: how much of each band is read
"""The two bands every LOOKS field writes into, outside both model files.

Measured by `--fields` (LOOKS-TASK-08): each field moves 130 to 320 bytes that
are in neither EDT_MOD.BIN nor MODEL.BIN nor any TMD, and they cluster here.
Not disc addresses and so not layout.py's -- they are where this build of this
game happens to put a working buffer, and `--buffers` says what it is.
"""
"""All of PSX main RAM.  Not a disc address, so not layout.py's business."""

ENV_STATES = "WE2002_LOOKS_STATES"
"""Where this project keeps its own copy of the two save states.

They have to be copied, and the reason is not tidiness.  DuckStation keeps one
data directory for the whole machine, so the states of this cycle sit in the
same folder as the PES2 work, under a bare slot number that anything may
overwrite -- and re-recording them costs a hand-driven navigation no tool here
can reproduce.  The project copy is the master; the emulator's slot is a
scratch position restored from it.
"""

SERIAL = "SLPM-87056"
"""The serial DuckStation names a state after.

Japanese, and the English disc boots it too -- which is exactly why the file
name is not evidence about which disc a state came from.
"""

SLOTS = {1: "goalkeeper", 2: "outfield player"}
"""What each slot shows.  Registered here, and captured in the task's log."""


# --- the pad --------------------------------------------------------------

CONFIRM_FRAMES = 8
"""How long a button is held.

**Circle confirms, and three frames is not enough.**  With `duration_frames: 3`
the game does not register the press at all: the screen stays exactly as it
was, which reads as the wrong button rather than as a press that was too
short.  Eight registers.  Measured during the investigation session of
2026-09-14 and kept here as code, not as a note somebody has to remember.
"""

SETTLE_FRAMES = 20
"""Frames to let the game act on a press before looking at the screen.

One press, then look.  **Never a loop of confirmations** -- the repository
rule, earned in the `wte/` cycle: the extra key, sent while the first box is
still closing, closes the box behind it.  There is no helper in this module
that presses more than once, and that absence is the design.
"""

LOAD_FRAMES = 4
"""Frames to step after `load_state` before the picture is worth reading."""


# --- what the screen looks like -------------------------------------------
#
# Boxes are FRACTIONS of the frame, not pixels.  DuckStation renders at
# whatever resolution scale its own configuration says, and this cycle does not
# configure the emulator (the decision of 2026-09-02, inherited from PES2), so
# a pixel box is a box that stops meaning anything the day somebody drags that
# slider.  Measured against an 864x655 capture.

BADGE = (0.025, 0.200, 0.135, 0.265)
"""The little plate under the shirt name: `GK` in one state, `CB` in the other.

This is the region that says WHICH state loaded.  The whole frame does not:
the two states differ by 0.003015 over the picture, which is the size of the
animation's own wobble, while over this plate they differ by **0.119963**.
"""

ROW_FIRST = 0.153
ROW_HEIGHT = 0.0528
"""Where the first row's cell starts, and how far apart the twelve rows sit.

Measured off an 864x655 capture: the rows are 34.6 px apart, which is 0.0528 of
the height, and DEFAUL's cell opens at 0.153.
"""


def row_value(index):
    """The value cell of row *index*, as a fraction of the frame.

    Per row and not one fixed box, because a value change has to be measured
    ON the row that changed: over the whole picture one step of HAIR moves
    0.005265, which is under the 0.02 that counts as movement and is the same
    size as the model's own animation.  Over its own cell it moves 0.09.
    """
    return (0.660, ROW_FIRST + index * ROW_HEIGHT + 0.012,
            0.920, ROW_FIRST + (index + 1) * ROW_HEIGHT - 0.012)


ROW_VALUE = (0.600, 0.205, 0.960, 0.260)
"""The value cell of the row the cursor sits on when a state loads -- NAT."""

BADGE_MEAN = {1: 0.291686, 2: 0.299999}
"""The plate's mean per slot, measured 2026-09-14.

Exact, and that is not a figure of speech: a state reloaded gives a picture
that differs from the first load by 0.000000, so these reproduce to every digit
printed.  The tolerance below is therefore about the emulator's settings
changing, not about noise.
"""

BADGE_TOL = 0.004
"""Fifteen times the measured spread of nothing, and thirty times below the
0.12 that separates the two slots."""

BADGE_APART = 0.05
"""How far apart the two slots' plates must be for the pair to mean anything.

Asserted rather than assumed: if both states ever came to show the same
player, every later "the goalkeeper differs from the outfield player" reading
would be measuring noise, and nothing else in the cycle would notice.
"""

SCREEN_MEAN = 0.1828
SCREEN_TOL = 0.006
"""The LOOKS SET screen as a whole: 0.182425 and 0.183158 on the two slots,
drifting to 0.183844 as the model animates."""

MOVED = 0.02
"""Above this, a region changed.  One Right on the top row moved its value cell
by 0.097842; the same cell without a press moves by 0.000000."""

FOOTER = (0.020, 0.800, 0.990, 0.900)
"""The strip that names the selected field -- "Kind of Hair", "Visual".

This is what tells one ROW from the next, and the whole frame is not: walking
the twelve rows moves the whole picture by 0.0068 to 0.0215, which overlaps
what the model's own animation does to it over the same 28 frames.  Over this
strip the same ten presses move 0.0086 to 0.0548 and an idle pair moves
0.000000.
"""

ROW_MOVED = 0.004
"""Half the smallest measured row move, and above an idle difference of zero."""

VALUE_MOVED = 0.004
IDLE_MARGIN = 3
"""Above this, a value cell changed.

Lower than MOVED because a value step is often ONE CHARACTER -- A1TYPE to
A2TYPE moves its cell by 0.016759, where NAT's whole word moved 0.097842.

**It was 0.010 until the numeric rows were measured.**  A letter is not the
smallest thing a value step changes: `175 cm` to `174 cm` moves one DIGIT, and
its cell by 0.009463, which the old floor rejected as "the press did not
register".

**And a single constant cannot do it**, which the next run showed: the cursor
box blinks over the whole cell, so the idle drift depends on how much of the
cell the value fills -- 0.000455 on `A1TYPE`, 0.002033 on `23`.  A floor of
0.002 then refused AGE, correctly, for being under its own blink.  So the floor
is the LARGER of this constant and `IDLE_MARGIN` times the drift `field_diff`
measures on that row, and a press that cannot beat three times its own row's
blink is a press this cannot testify about.

**And the cell is not perfectly still**: the selected row wears a blinking
cursor box with an arrow at each end, which moved the first, wider cell by
0.005682 with nothing pressed.  Two things answer that, and both are needed:
the box was narrowed to the value glyphs, away from the border and the arrows;
and `field_diff` MEASURES the idle drift before trusting this floor, refusing
rather than measuring if the cell turns out to move on its own by more.  A
threshold between two numbers that were both measured is a threshold; one
chosen because it looked safe is a guess.
"""

ROWS = ("DEFAUL", "NAT", "SKIN", "HAIR", "H.COL", "FACE", "H.F.COL.",
        "HEIG", "BODY", "AGE", "BOOTS", "FOOT")
"""The rows of the LOOKS SET screen, top to bottom, as the screen spells them.

**Positions, not semantics.**  What each field MEANS, what its domain is and
what the labels expand to is LOOKS-TASK-13's subject, measured against
`src/core/Player.cpp`.  All this list is for is knowing how many times to press
Down: a save state restores the cursor on NAT, so a row is `index - 1` presses
away.
"""

CURSOR_STARTS_ON = "NAT"
"""Where both save states leave the cursor.  Asserted, not assumed: if a state
were ever re-recorded elsewhere every row offset below would silently shift."""

CHURN_PASSES = 3
"""How many idle passes go into the churn set.

The model on this screen is animated, so a byte can come back to its old value
just by the animation coming round again -- which is why A/B/A alone called
4.248 bytes "the field's" on the first run.  One pass samples one phase of the
animation; three sample three.
"""


# --- refusals -------------------------------------------------------------

class OracleError(Exception):
    """Something measurable went wrong."""


class NotArrived(OracleError):
    """The screen is not the one the state was supposed to restore."""


class WrongDisc(OracleError):
    """A save state that was not recorded on the disc we drive."""


class RamMismatch(OracleError):
    """What is loaded at a model file's address is not that model file."""


class Unavailable(Exception):
    """The machine cannot run this.  Reported as a skip, never as a failure."""


# --- the save states ------------------------------------------------------

def states_dir() -> str:
    """This project's own copy of the states."""
    return os.environ.get(ENV_STATES) or os.path.join(ROOT, "work",
                                                      "looks-states")


def project_state(slot: int) -> str:
    return os.path.join(states_dir(), "%s_%d.sav" % (SERIAL, slot))


def emulator_states_dir() -> str:
    """Where DuckStation itself keeps save states on this machine.

    Windows runs the fork out of its own folder, so its data directory is that
    folder; on Linux it is the user's shared one, which is what
    `tools/pes2/mcp_drive.py` records.  Derived from `fork.FORK_HOME` rather
    than imported from `mcp_drive`, because that module pulls in PIL at import
    time and asking where a file lives should not need an image library.
    """
    import fork

    if WINDOWS:
        # Read from the environment each time rather than from the constant
        # fork.py resolved at import: `PES2_FORK` is how make.ps1 says where
        # the fork lives, and a value set after this module loaded would
        # otherwise be ignored in silence.
        return os.path.join(os.path.expanduser(
            os.environ.get("PES2_FORK", fork.FORK_HOME)), "savestates")
    return os.path.expanduser("~/.local/share/duckstation/savestates")


def emulator_state(slot: int) -> str:
    """The slot file itself, which is the only place `load_state` reads from:
    it takes a slot number, not a path."""
    return os.path.join(emulator_states_dir(), "%s_%d.sav" % (SERIAL, slot))


def digest(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def media_of(path: str) -> str:
    """The disc image a save state was recorded on, read from inside it.

    The header is plain -- only the payload is zstd -- so this works on a
    machine with no decompressor, which this one is.
    """
    import savestate

    return savestate.SaveState(path).media


def drive_image() -> str:
    """The .cue this cycle drives, named by the environment."""
    value = os.environ.get(layout.ENV_DRIVE_IMAGE)
    if not value:
        raise Unavailable(
            "%s is not set: it names the English .cue the emulator boots.  %s "
            "is the Japanese data track every disc read comes from, and it is "
            "not a substitute." % (layout.ENV_DRIVE_IMAGE, layout.ENV_IMAGE)
        )
    return value


def require_media(path: str, cue: str) -> str:
    """Refuse a state recorded on another disc, and say why the name did not
    give it away."""
    got = media_of(path)
    if os.path.normcase(os.path.abspath(got)) != \
            os.path.normcase(os.path.abspath(cue)):
        raise WrongDisc(
            "%s was recorded on %r, and this cycle drives %r.  The file name "
            "cannot tell you this: both releases boot the serial %s, so a "
            "state made on the Japanese disc carries the same name and brings "
            "unreadable menus with it." % (os.path.basename(path), got, cue,
                                           SERIAL)
        )
    return got


def adopt_states(verbose: bool = True) -> int:
    """Copy the emulator's two slots into the project, once.

    Deliberately explicit.  The emulator's slot is overwritable by anything
    that touches that shared directory, so the copy is the master -- and a
    command that silently refreshed the master from the scratch position would
    destroy the fixture the first time something else wrote there.
    """
    target = states_dir()
    os.makedirs(target, exist_ok=True)
    cue = drive_image()
    for slot in sorted(SLOTS):
        source = emulator_state(slot)
        if not os.path.exists(source):
            raise Unavailable("no save state at %s" % source)
        require_media(source, cue)
        shutil.copy2(source, project_state(slot))
        if verbose:
            print("  adopted slot %d (%s)  %s" % (slot, SLOTS[slot],
                                                  project_state(slot)))
    return 0


def restore_state(slot: int, verbose: bool = True) -> bool:
    """Put the project's copy back in the emulator's slot if it is not there.

    Returns whether anything was written.  Loud on purpose: a restore means
    something else had overwritten the slot, and that is worth seeing.
    """
    master = project_state(slot)
    if not os.path.exists(master):
        raise Unavailable(
            "no project copy at %s -- run --adopt-states once, with the two "
            "states in the emulator's own directory" % master
        )
    live = emulator_state(slot)
    existed = os.path.exists(live)
    if existed and digest(live) == digest(master):
        return False
    # The directory is DuckStation's own, and this never makes one.  Creating
    # it would mean the path is wrong -- a mistyped PES2_FORK, say -- and the
    # copy would land in a folder nothing ever reads, which reads as success.
    if not os.path.isdir(os.path.dirname(live)):
        raise Unavailable(
            "no save-state directory at %s -- that is where DuckStation keeps "
            "them, and this does not create it"
            % os.path.dirname(live)
        )
    shutil.copy2(master, live)
    if verbose:
        print("  restored slot %d from the project copy (the emulator's was "
              "%s)" % (slot, "different" if existed else "absent"))
    return True


def check_states(verbose: bool = True) -> int:
    """The two states, without an emulator: they exist, and they are ours."""
    cue = drive_image()
    for slot in sorted(SLOTS):
        path = project_state(slot)
        if not os.path.exists(path):
            raise Unavailable(
                "no project copy of slot %d at %s -- run --adopt-states"
                % (slot, path)
            )
        media = require_media(path, cue)
        if verbose:
            print("  slot %d (%s)  %d B  sha256 %s\n      media %s"
                  % (slot, SLOTS[slot], os.path.getsize(path),
                     digest(path)[:16], media))
    return 0


# --- what has to be there before anything is launched ---------------------

def image_to_read() -> str:
    """The Japanese track, as an Unavailable rather than a RuntimeError.

    The same conversion `modelfile.py --check-image` makes, and for the same
    reason: an unset variable is something to skip on, not a defect in this
    module.  It lives here so the preflight can ask for the track BEFORE the
    emulator goes up -- `verify_load()` asks for it far too late, with the
    fork running and three states already restored (CORR-LOOKS-017).
    """
    import iso_source

    try:
        return iso_source.image_from_env()
    except RuntimeError as exc:
        raise Unavailable(str(exc)) from None


PREREQUISITES = (
    ("cue", drive_image),
    ("image", image_to_read),
    ("states", lambda: check_states(verbose=False)),
)
"""Everything `--check-live` needs before it may launch anything.

**The list is the point.**  The Japanese track was not on it, and was asked
for at its point of use instead -- so a run without it booted the emulator,
hid the window, restored three states, passed five checks and only then died
in a traceback: neither measured nor skipped, which is exactly what the cycle
profile forbids.  A check that comes to need something new adds it HERE.

The fork is deliberately not on the list: only the launch proves it is
installed where this thinks, and `Oracle.__enter__` already turns `fork.Skip`
into `Unavailable`.  Everything that can be known WITHOUT starting a process
is known first.
"""


def preflight() -> dict:
    """Every prerequisite, in order, before anything is launched.

    Each one raises `Unavailable`, which `main()` reports as 77 -- so a
    machine missing any of them is told what is missing, in seconds, with no
    emulator started.
    """
    return {key: need() for key, need in PREREQUISITES}


# --- the window -----------------------------------------------------------

def hide_window(handle) -> bool:
    """Move the emulator off the visible desktop, and do it at once.

    The repository rule has no Xvfb to lean on here: on Windows the editors and
    the emulator are moved to -32000 instead, which keeps them drawing (unlike
    `SW_HIDE`, which blanks the capture) while keeping them off the screen the
    user is working on.  Captures come out of the emulator's own frame buffer
    anyway, so nothing downstream cares where the window is.
    """
    if not WINDOWS or not handle:
        return False
    off = -32000  # not-an-address: the off-screen coordinate of CLAUDE.md
    flags = 0x0001 | 0x0004 | 0x0010  # not-an-address: NOSIZE|NOZORDER|NOACTIVATE
    return bool(ctypes.windll.user32.SetWindowPos(int(handle), 0, off, off,
                                                  0, 0, flags))


# --- the session ----------------------------------------------------------

class Oracle:
    """A booted game, paused, with an MCP session against it.

    Use as a context manager.  It owns the emulator it started and kills it on
    the way out -- DuckStation keeps one data directory, so one instance at a
    time is the rule for the whole repository, and leaving one up would take
    the PES2 tooling down with it.
    """

    def __init__(self, cue=None, out_dir=None, verbose=True):
        self.cue = cue
        self.out_dir = out_dir or os.path.join(ROOT, "work", "looks-shots")
        self.verbose = verbose
        self.client = None
        self.window = None
        self.pid = None
        self.shots = []

    def say(self, message):
        if self.verbose:
            print("  %s" % message, flush=True)

    def __enter__(self):
        import fork

        cue = self.cue or drive_image()
        if not os.path.isfile(cue):
            raise Unavailable("no disc image at %s" % cue)
        try:
            self.pid, self.window, self.client = fork.launch(
                cue, verbose=self.verbose, match=fork.ANY_WINDOW)
        except fork.Skip as exc:
            raise Unavailable(str(exc)) from None
        if hide_window(self.window):
            self.say("window moved off the visible desktop")
        os.makedirs(self.out_dir, exist_ok=True)
        self.pause()
        return self

    def __exit__(self, *exc):
        import fork

        fork.kill(verbose=False)
        return False

    # -- the clock --

    def pause(self):
        self.client.call("pause")

    def step(self, frames=1):
        for _ in range(frames):
            self.client.call("frame_step")

    # -- input --

    def press(self, button, box=None, expect_change=True, least=None):
        """One button, held CONFIRM_FRAMES, then look.

        There is no variant that presses twice.  What the caller gets instead
        is an assertion: unless it says otherwise, the region it names has to
        have moved, so a press the game ignored is a refusal rather than a
        silent no-op -- which is the failure three frames of Circle produced.
        """
        before = self.capture() if expect_change else None
        self.client.call("press_button", button=button,
                         duration_frames=CONFIRM_FRAMES)
        self.step(CONFIRM_FRAMES + SETTLE_FRAMES)
        after = self.capture()
        if expect_change:
            floor = MOVED if least is None else least
            moved = before.difference(after, pixels(before, box))
            if moved <= floor:
                raise NotArrived(
                    "%s moved the screen by %.6f, which is no more than the "
                    "%.6f that counts as unchanged -- the press did not "
                    "register, or the region is the wrong one"
                    % (button, moved, floor)
                )
            self.say("%s moved it by %.6f" % (button, moved))
        return after

    # -- output --

    def capture(self, label=None):
        from drive import Frame

        name = "%s.png" % (label or "scratch")
        path = os.path.join(self.out_dir, name)
        self.client.call("take_screenshot", path=path)
        if not os.path.exists(path):
            raise OracleError("the emulator reported a screenshot at %s and "
                              "there is no file there" % path)
        frame = Frame(path)
        if label:
            mean, sd = frame.stats()
            self.say("shot %s  mean=%.6f sd=%.6f  %s"
                     % (label, mean, sd, path))
            self.shots.append(path)
        return frame

    def read_ram(self, address, size, path):
        """Raw bytes out of the live machine.

        By MCP, and that is not a preference.  `tools/pes2/savestate.py` reads
        a state's header and stops: the payload is one zstd frame, the `zstd`
        CLI is not on this machine's PATH and the `zstandard` module is not
        installed either, so it prints the header and then raises
        `FileNotFoundError [WinError 2]` -- a message that never mentions zstd.
        The state is the starting position; the memory comes from the running
        emulator.
        """
        self.client.call("read_memory", address=address, size=size, path=path)
        with open(path, "rb") as handle:
            data = handle.read()
        if len(data) != size:
            raise OracleError("asked for %d bytes at %#x and got %d"
                              % (size, address, len(data)))
        return data

    # -- the screen --

    def load_looks(self, slot, label=None):
        """Restore one state and prove the screen it restored is the right one.

        By the picture, never by the clock: the emulator is stepped a fixed
        number of frames and then the frame is *read*, which is what makes
        this an assertion rather than a wait.
        """
        if slot not in SLOTS:
            raise OracleError("slot %r is not one of this cycle's two" % slot)
        self.pause()
        self.client.call("load_state", slot=slot)
        self.step(LOAD_FRAMES)
        frame = self.capture(label)
        self.require_looks(frame, slot)
        self.say("slot %d restored: the %s, on LOOKS SET"
                 % (slot, SLOTS[slot]))
        return frame

    def require_looks(self, frame, slot):
        """The three things that together say the right state is on screen."""
        if frame.is_black():
            raise NotArrived(
                "the frame is black -- the state did not restore, or it "
                "restored into a load"
            )
        mean, _sd = frame.stats()
        if abs(mean - SCREEN_MEAN) > SCREEN_TOL:
            raise NotArrived(
                "the frame's mean is %.6f, not the %.6f (+-%.6f) of the LOOKS "
                "SET screen" % (mean, SCREEN_MEAN, SCREEN_TOL)
            )
        badge, _ = frame.stats(pixels(frame, BADGE))
        want = BADGE_MEAN[slot]
        if abs(badge - want) > BADGE_TOL:
            raise NotArrived(
                "the position plate reads %.6f and slot %d (the %s) reads "
                "%.6f (+-%.6f) -- this is some other state, or the emulator's "
                "resolution scale has moved"
                % (badge, slot, SLOTS[slot], want, BADGE_TOL)
            )

    # -- rows, and what moving one does to memory --

    def select_row(self, row):
        """Put the cursor on a named row, counting the presses.

        Each Down is asserted to move the picture, so a press the game dropped
        is a refusal instead of an off-by-one that lands on a neighbouring
        field and measures it instead.
        """
        if row not in ROWS:
            raise OracleError("%r is not a row of this screen: %s"
                              % (row, ", ".join(ROWS)))
        for _ in range(ROWS.index(row) - ROWS.index(CURSOR_STARTS_ON)):
            self.press("Down", box=FOOTER, least=ROW_MOVED)
        # Captured under the row's name, because the footer of this screen
        # spells out the selected field ("Kind of Hair") and the code cannot
        # read it.  The presses are asserted to move; that the row they land
        # on is the one named is checked by looking at the picture, and the
        # picture is kept for that.
        return self.capture("row-%s" % row.replace(".", ""))

    def snapshot(self, tag):
        """All of main RAM, as bytes."""
        path = os.path.join(self.out_dir, "ram-%s.bin" % tag)
        return self.read_ram(RAM_BASE, RAM_SIZE, path)

    def churn(self, passes=CHURN_PASSES):
        """Every byte that moves while the game merely runs.

        Taken where the measurement will be taken -- same screen, same row --
        because what churns depends on what is being drawn.
        """
        seen = set()
        previous = self.snapshot("churn-0")
        for index in range(passes):
            self.step(CONFIRM_FRAMES + SETTLE_FRAMES)
            current = self.snapshot("churn-%d" % (index + 1))
            seen |= {i for i in range(len(previous))
                     if previous[i] != current[i]}
            previous = current
        self.say("churn over %d pass(es): %d byte(s)" % (passes, len(seen)))
        return seen

    def field_diff(self, slot, row):
        """What changing one field moves, with the animation filtered out.

        Three filters, and each one is there because the two before it were not
        enough:

        1. **changed by Right** -- 20.150 bytes, nearly all of it the game
           being alive;
        2. **and put back by Left** -- 4.248, because the field returns to its
           old value and so does anything that depends on it.  Still far too
           many: the model is animated and a periodic byte comes back on its
           own;
        3. **and not in the churn set** -- 132.  That is the field's.

        Returns the offsets, as offsets into RAM.
        """
        self.load_looks(slot)
        cell = row_value(ROWS.index(row))
        quiet = self.select_row(row)
        noise = self.churn()
        # The control for the threshold below: the cell this measurement
        # watches must be still when nothing is pressed.  Without it, a floor
        # of 0.004 would be a guess about a region that might be animated.
        drift = quiet.difference(self.capture(), pixels(quiet, cell))
        floor = max(VALUE_MOVED, drift * IDLE_MARGIN)
        self.say("the %s cell drifts %.6f while idle, so a press has to beat "
                 "%.6f" % (row, drift, floor))

        self.load_looks(slot)
        self.select_row(row)
        before = self.snapshot("before")
        self.press("Right", box=cell, least=floor)
        after = self.snapshot("after")
        self.press("Left", box=cell, least=floor)
        back = self.snapshot("back")

        moved = {i for i in range(len(before)) if before[i] != after[i]}
        restored = {i for i in moved if back[i] == before[i]}
        mine = sorted(restored - noise)
        self.say("%s on slot %d: %d moved, %d put back, %d of them not churn"
                 % (row, slot, len(moved), len(restored), len(mine)))
        return mine, before, after

    # -- the amount of the file that is really loaded --

    def verify_load(self, image=None, verbose=True):
        """Compare RAM at each model file's load address against the disc.

        **Not byte for byte, and the difference is the point.**  Section 5.2 of
        the plan claimed the two are identical; measured on the LOOKS SET
        screen they are not, and what differs is a gift rather than a problem:
        203 single bytes in EDT_MOD.BIN and 20 in MODEL.BIN, every one of them
        inside a section body and none in the header or the pointer lists.

        So what this asserts is what holds: the header region is identical --
        which is what proves the file is loaded at this address at all -- and
        every differing byte lies inside a walked section.  A wrong address
        fails both.  The differing bytes themselves are reported, because they
        are the lead LOOKS-TASK-08 opens with.
        """
        import iso_source

        image = image or iso_source.image_from_env()
        report = {}
        with iso_source.open_disc(image) as disc:
            for name in sorted(layout.BASE):
                want = disc.read(name)
                path = os.path.join(self.out_dir,
                                    "ram-%s" % os.path.basename(name))
                got = self.read_ram(layout.BASE[name], len(want), path)
                report[name] = _compare(name, want, got)
                if verbose:
                    _say_comparison(name, report[name])
        return report


def _compare(name, want, got, start=None):
    """Where the live copy of a model file differs from the disc's."""
    start = layout.GEOMETRY_START[name] if start is None else start
    if want[:start] != got[:start]:
        raise RamMismatch(
            "%s: the %d bytes before the first section differ between the disc "
            "and %#x, so what is loaded there is not this file"
            % (name, start, layout.BASE[name])
        )
    scan = section.scan(want, start)
    offsets = [i for i in range(len(want)) if want[i] != got[i]]

    per_section = {}
    in_primitive = set()
    outside = []
    for i in offsets:
        home = next((one for one in scan.sections
                     if one.offset <= i < one.end), None)
        if home is None:
            outside.append(i)
            continue
        place = i - home.offset - section.HEADER_SIZE
        per_section.setdefault(scan.sections.index(home), []).append(place)
        # The body is the primitives and then the vertices, so a byte is in a
        # primitive only while it is inside that first run.
        if 0 <= place < len(home.primitives) * section.PRIMITIVE_SIZE:
            in_primitive.add(place % section.PRIMITIVE_SIZE)
    if outside:
        raise RamMismatch(
            "%s: %d byte(s) differ outside every section, the first at +%d -- "
            "the game rewrites primitives, not headers, so this is the wrong "
            "address or the wrong file" % (name, len(outside), outside[0])
        )
    return {
        "bytes": len(want),
        "differing": offsets,
        "sections": per_section,
        "in_primitive": sorted(in_primitive),
    }


def _say_comparison(name, found):
    total, differ = found["bytes"], len(found["differing"])
    print("  %s at %#x: %d of %d byte(s) differ (%.2f%% equal), in section(s) "
          "%s" % (name, layout.BASE[name], differ, total,
                  100.0 * (total - differ) / total,
                  ", ".join(str(i) for i in sorted(found["sections"]))
                  or "none"))
    if differ:
        print("      every one of them at byte %s of a %d-byte primitive"
              % (found["in_primitive"], section.PRIMITIVE_SIZE))


def spans(image):
    """Every span a changed byte can be attributed to, from the disc itself.

    Built from the files rather than declared, so a section index in the output
    is the same index `modelfile` prints and not a second numbering.
    """
    import iso_source

    out = {}
    with iso_source.open_disc(image) as disc:
        for name in sorted(layout.BASE):
            data = disc.read(name)
            scan = section.scan(data, layout.GEOMETRY_START[name])
            out[layout.BASE[name]] = (name, len(data), scan.sections)
    return out


def attribute(address, maps):
    """Where one address falls: file, section, primitive or vertex, and byte."""
    for base, (name, size, sections) in maps.items():
        if not base <= address < base + size:
            continue
        offset = address - base
        for index, one in enumerate(sections):
            if not one.offset <= offset < one.end:
                continue
            inner = offset - one.offset - section.HEADER_SIZE
            if inner < 0:
                return (name, index, "header", offset, None)
            primitives = len(one.primitives) * section.PRIMITIVE_SIZE
            if inner < primitives:
                return (name, index, "primitive %d" % (inner // 24),
                        offset, inner % 24)
            vertex = inner - primitives
            return (name, index, "vertex %d" % (vertex // 8), offset,
                    vertex % 8)
        return (name, None, "outside every section", offset, None)
    return None


TMD_HEADER_SIZE = 12
TMD_OBJECT_SIZE = 28


def _tmd_pointer(value, flags, table):
    """One of a TMD object's three pointers, as an offset into main RAM.

    Bit 0 of the file flags is Sony's FIXP: set, the pointers were resolved to
    real addresses when the file was loaded; clear, they are offsets from the
    start of the object table.  Both spellings appear in this console's files,
    and reading one as the other lands the span somewhere plausible and wrong.

    **The mask is not decoration.**  A resolved pointer is a KSEG0 address with
    the top bit set, and the object table is read as signed words -- so it
    arrives NEGATIVE.  Subtracting the RAM base from it gives a negative
    offset, every span collapses to header-plus-table, and every TMD comes out
    exactly 40 bytes long.  Measured that way here first: 29 TMDs of 4 to 54
    vertices, all "40 bytes".  It was the printed extent that gave it away.
    """
    if flags & 1:
        return (value & 0xFFFFFFFF) - RAM_BASE  # not-an-address: a width mask
    return table + value


def _walk_tmd_primitives(data, at, count):
    """The end of *count* TMD packets starting at *at*, or None if they run out.

    TMD primitives are variable length -- byte 1 of each packet header is its
    payload in words -- so the only way to know where they end is to walk them.
    Assuming a fixed size is how a span comes out short, and a span that comes
    out short puts real bytes in the residue bucket.
    """
    if at is None:
        return None
    for _ in range(count):
        if at < 0 or at + 4 > len(data):
            return None
        at += 4 + data[at + 1] * 4
    return at if at <= len(data) else None


def tmd_spans(data):
    """(start, end, verts, prims) of every TMD in *data*, walked to its end.

    The header alone gives the counts; where the object ENDS takes reading the
    object table and walking the primitive packets.  This exists so a byte a
    field moved can be attributed to a TMD instead of only to "not in a model
    file" -- the two are different claims, and only the second was ever printed
    (CORR-LOOKS-019).
    """
    import struct

    out = []
    for address, verts, prims in _tmd_headers(data):
        at = address - RAM_BASE
        flags, objects = struct.unpack_from("<2I", data, at + 4)
        table = at + TMD_HEADER_SIZE
        end = table + objects * TMD_OBJECT_SIZE
        for index in range(objects):
            here = table + index * TMD_OBJECT_SIZE
            if here + TMD_OBJECT_SIZE > len(data):
                break
            (vert_top, n_vert, norm_top, n_norm,
             prim_top, n_prim, _scale) = struct.unpack_from("<7i", data, here)
            for top, count in ((vert_top, n_vert), (norm_top, n_norm)):
                start = _tmd_pointer(top, flags, table)
                if 0 <= start <= len(data):
                    end = max(end, min(len(data), start + count * 8))
            walked = _walk_tmd_primitives(
                data, _tmd_pointer(prim_top, flags, table), n_prim)
            if walked is not None:
                end = max(end, walked)
        out.append((RAM_BASE + at, RAM_BASE + end, verts, prims))
    return out


def attribute_tmd(address, spans):
    """Which TMD of *spans* an address falls in, or None."""
    for index, (start, end, _verts, _prims) in enumerate(spans):
        if start <= address < end:
            return index
    return None


def lists_touched(name, indices, image):
    """Which of a file's header lists own these section indices.

    EDT_MOD.BIN holds two eleven-piece lists sharing two sections, and the
    question of whether they are the goalkeeper and the outfield player is the
    one the two save states were made to answer.  Answered by set membership
    here rather than by eye, because "sections 11 and 16 to 19" and "the second
    list" are the same claim only if something checks.
    """
    import iso_source
    import modelfile

    with iso_source.open_disc(image) as disc:
        data = disc.read(name)
        scan = section.scan(data, layout.GEOMETRY_START[name])
        where = {one.offset: i for i, one in enumerate(scan.sections)}
        out = {}
        try:
            models = modelfile.read_models(data)
        except layout.BadPointerList:
            # MODEL.BIN's header lists aim at flat pointer runs, not sections,
            # so it has no readable model list yet and there is nothing to
            # attribute to.  Not an error here: the file this question is
            # about is EDT_MOD.BIN.
            return None
        for model in models:
            owned = {where[target] for target in model.targets}
            hit = sorted(set(indices) & owned)
            if hit:
                out[model.index] = hit
    return out


def report_field(found, before, after, maps, tmds=(), image=None,
                 verbose=True):
    """Group what a field moved by file and section, and say what is untouched.

    **Three buckets, not two.**  Model file, TMD, and neither -- because "not
    in a model file" and "not in a TMD" are different claims, and the verdict
    of unknown (a) rests on the second one.  Until CORR-LOOKS-019 only the
    first was printed, and the negative half of the verdict was two reports
    read side by side rather than one measurement.

    The count of bytes that landed in NEITHER is printed too, and that is
    deliberate: "nothing outside" and "nothing measured" print the same when
    only the hits are listed.
    """
    inside, elsewhere = {}, 0
    in_tmd = {}
    for offset in found:
        where = attribute(RAM_BASE + offset, maps)
        if where is None:
            which = attribute_tmd(RAM_BASE + offset, tmds)
            if which is None:
                elsewhere += 1
            else:
                in_tmd[which] = in_tmd.get(which, 0) + 1
            continue
        name, index, part, at, byte = where
        inside.setdefault((name, index), []).append((at, part, byte,
                                                     before[offset],
                                                     after[offset]))
    for key in sorted(inside):
        name, index = key
        hits = inside[key]
        bytes_in = sorted({b for _, _, b, _, _ in hits if b is not None})
        if verbose:
            print("      %s section %s: %d byte(s), at byte %s of the "
                  "primitive" % (name, index, len(hits), bytes_in))
            # Every hit, not a sample.  Four lines is EXACTLY one textured
            # quad, so a field that moves two primitives printed one of them
            # and the reader had to infer the other -- which is how FACE was
            # nearly recorded against a primitive nobody had seen move
            # (LOOKS-TASK-11).  A section this field touched is small by
            # construction; listing it whole costs nothing.
            for at, part, _byte, old, new in hits:
                print("          +%d %s: %d -> %d" % (at, part, old, new))
    print("      in a TMD: %d byte(s)%s"
          % (sum(in_tmd.values()),
             "" if not in_tmd
             else "  " + ", ".join("TMD %d: %d" % (k, v)
                                   for k, v in sorted(in_tmd.items()))))
    print("      in neither: %d byte(s)" % elsewhere)
    if image:
        for name in sorted({key[0] for key in inside}):
            indices = [key[1] for key in inside if key[0] == name]
            owners = lists_touched(name, indices, image)
            if owners:
                print("      %s: %s" % (name, "; ".join(
                    "list %d owns section(s) %s" % (k, v)
                    for k, v in sorted(owners.items()))))
    return inside, elsewhere


def pixels(frame, frac):
    """A fractional box as pixels of this frame."""
    if frac is None:
        return None
    width, height = frame.size
    return (int(frac[0] * width), int(frac[1] * height),
            int(frac[2] * width), int(frac[3] * height))


# --- the live check -------------------------------------------------------

def check_live(verbose=True):
    """Everything this module claims, against a running game.

    Skips rather than fails when the machine has no emulator or no states --
    77, this repository's code across all five projects.  Everything it needs
    is named by PREREQUISITES and asked for here, before the launch.
    """
    ready = preflight()
    cue = ready["cue"]

    failures = []

    def ok(what, condition, detail=""):
        print("  %s  %s%s" % ("ok  " if condition else "FAIL", what,
                              "  (%s)" % detail if detail and not condition
                              else ""))
        if not condition:
            failures.append(what)

    with Oracle(cue, verbose=verbose) as game:
        # Inside the context, and not before it: the launch is what proves the
        # emulator is installed where this thinks, and putting a state back
        # into a directory that turned out not to be DuckStation's is a copy
        # nothing will ever read.
        for slot in sorted(SLOTS):
            restore_state(slot, verbose=verbose)

        first = game.load_looks(1, "slot1-goalkeeper")
        again = game.load_looks(1, "slot1-again")
        ok("a reloaded state is the same picture to the last bit",
           first.difference(again) == 0.0,
           "%.6f" % first.difference(again))

        second = game.load_looks(2, "slot2-outfield")
        apart = first.difference(second, pixels(first, BADGE))
        ok("the two slots show different players", apart >= BADGE_APART,
           "the position plate differs by %.6f, under %.6f" % (apart,
                                                              BADGE_APART))
        print("      the plate differs by %.6f between the slots" % apart)

        # The wrong slot must be refused, and it is the assertion that makes
        # the other two mean anything: without it `load_looks` would accept
        # any LOOKS SET screen as any state.
        try:
            game.require_looks(second, 1)
            ok("slot 2's picture is refused as slot 1", False, "it accepted")
        except NotArrived as exc:
            ok("slot 2's picture is refused as slot 1", True)
            print("      %s" % str(exc).split(" -- ")[0])

        game.load_looks(1)
        report = game.verify_load(ready["image"])
        ok("both model files are loaded where layout.py says",
           set(report) == set(layout.BASE))

        moved = game.press("Right", box=ROW_VALUE)
        ok("one press changes the field under the cursor",
           moved.difference(first, pixels(first, ROW_VALUE)) > MOVED)

    print("oracle --check-live: %d failure(s)" % len(failures))
    return 1 if failures else 0


def check_fields(rows=None, slots=(1, 2), verbose=True):
    """Measure what each named field moves, on both states.

    This is the measurement LOOKS-TASK-08 exists for, kept as a command so the
    numbers in the plan come out of a script and not out of a session.
    """
    ready = preflight()
    maps = spans(ready["image"])
    rows = rows or ("HAIR", "SKIN", "FACE", "BODY")

    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in sorted(SLOTS):
            restore_state(slot, verbose=verbose)
        for row in rows:
            for slot in slots:
                found, before, after = game.field_diff(slot, row)
                print("  %s, slot %d (%s): %d byte(s)"
                      % (row, slot, SLOTS[slot], len(found)))
                # Built from the SAME snapshot the diff came from: a TMD map
                # taken at another moment would be a map of another RAM.
                report_field(found, before, after, maps, tmd_spans(before),
                             image=ready["image"], verbose=verbose)
    return 0


_PACKETS = (
    ("20", "flat triangle", 4), ("22", "flat triangle, semi", 4),
    ("24", "textured triangle", 7), ("25", "textured triangle, raw", 7),
    ("28", "flat quad", 5), ("2A", "flat quad, semi", 5),
    ("2C", "textured quad", 9), ("2D", "textured quad, raw", 9),
    ("2E", "textured quad, semi", 9), ("2F", "textured quad, semi raw", 9),
    ("30", "gouraud triangle", 6), ("34", "gouraud textured triangle", 9),
    ("38", "gouraud quad", 8), ("3C", "gouraud textured quad", 12),
    ("3D", "gouraud textured quad, raw", 12),
    ("E1", "draw mode", 1), ("E3", "draw area top-left", 1),
    ("E4", "draw area bottom-right", 1), ("E5", "draw offset", 1),
)

GPU_COMMANDS = {int(code, 16): (name, words) for code, name, words in _PACKETS}
"""The GPU packet codes this screen could plausibly hold, and their lengths.

Only what a player model needs plus the state commands around it.  The point is
not a complete table -- it is that a buffer of DRAWN geometry is almost all of
these and a buffer of anything else is almost none.

**Written as codes and not as hex literals**, and not to dodge the rule-1
sweep: the sweep flagged all eleven lines and was right by its own terms.  A
GPU command is an opcode, the same kind of thing as a mnemonic, and eleven
`# not-an-address:` comments would have silenced the sweep while teaching
nothing about why these numbers are not addresses.
"""


def walk_packets(data, base=None):
    """Count the PSX display-list nodes in *data*.

    A node is `[link][packet...]`: one word whose low 24 bits point at the next
    node and whose TOP byte is how many words of packet follow, and then the
    packet itself, which opens with its command in the top byte of its first
    word.

    The test is the agreement of those two numbers.  A command code alone is a
    one-byte coincidence and a histogram of them proves nothing; a link whose
    declared length is exactly the length the hardware gives that command,
    hundreds of times over, is not a coincidence.

    **The first version required the link to point back INSIDE the band and
    counted zero.** It does not: the band holds the nodes and the chain runs on
    to other regions -- the first node of the band points at 0x0006B53C, which
    is nowhere near it. Asking whether the region is self-contained is a
    different question from asking whether it is a display list, and the answer
    to the first was being read as the answer to the second.
    """
    import struct

    codes, nodes = {}, 0
    for start in range(0, len(data) - 8, 4):
        word = struct.unpack_from("<I", data, start)[0]
        target = word & OT_POINTER  # the low 24 bits are the next node
        length = word >> 24
        if not 0 < target < RAM_SIZE:
            continue
        code = data[start + 7]
        if code not in GPU_COMMANDS or GPU_COMMANDS[code][1] != length:
            continue
        nodes += 1
        name = GPU_COMMANDS[code][0]
        codes[name] = codes.get(name, 0) + 1
    return nodes, codes


def check_buffers(verbose=True):
    """What the two bands every field writes into actually are.

    Every LOOKS field moves 130 to 320 bytes that fall in NEITHER model file
    (LOOKS-TASK-08), and they cluster in two bands 0xF000 apart.  Naming them is
    what separates "the geometry the game loaded" from "the geometry the GPU
    drew", and the answer decides where a later render has to look.
    """
    ready = preflight()
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in sorted(SLOTS):
            restore_state(slot, verbose=verbose)
        game.load_looks(1)
        for base in BUFFER_BANDS:
            path = os.path.join(game.out_dir, "band-%08x.bin" % base)
            data = game.read_ram(base, BUFFER_SIZE, path)
            nodes, codes = walk_packets(data)
            filled = sum(1 for b in data if b)
            print("  %#010x  %d of %d byte(s) non-zero; %d display-list "
                  "node(s)" % (base, filled, len(data), nodes))
            for name in sorted(codes, key=lambda k: -codes[k]):
                print("      %-28s %d" % (name, codes[name]))
        first = game.read_ram(BUFFER_BANDS[0], BUFFER_SIZE,
                              os.path.join(game.out_dir, "band-a.bin"))
        second = game.read_ram(BUFFER_BANDS[1], BUFFER_SIZE,
                               os.path.join(game.out_dir, "band-b.bin"))
        same = sum(1 for a, b in zip(first, second) if a == b)
        print("  the two bands are %#x apart and %d of %d byte(s) equal "
              "(%.1f%%)" % (BUFFER_BANDS[1] - BUFFER_BANDS[0], same,
                            len(first), 100.0 * same / len(first)))
    return 0


def check_tmds(rows=(("HAIR", 1), ("SKIN", 2)), verbose=True):
    """Are the four TMDs of plan section 1.6 in RAM, and does any field move one?

    The answer decides unknown (a) as much as the field diffs do, and it has to
    come from a command: "I looked and they were zero" is exactly the kind of
    claim this cycle keeps turning into a script.

    **The second half used to be missing**, and this docstring promised it
    anyway: the command printed the four addresses and the TMDs it found, and
    never pressed a key.  "No field moves one" was then two reports read side
    by side.  It now measures the crossing for *rows* -- (field, slot) pairs,
    the two of the plan's own evidence by default -- and prints the count
    (CORR-LOOKS-019).
    """
    ready = preflight()
    maps = spans(ready["image"])
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in sorted(SLOTS):
            restore_state(slot, verbose=verbose)
        for slot in sorted(SLOTS):
            game.load_looks(slot)
            data = game.snapshot("tmd-slot%d" % slot)
            print("  slot %d (%s):" % (slot, SLOTS[slot]))
            for address in layout.TMD_CLAIMED:
                chunk = data[address - RAM_BASE:address - RAM_BASE + 32]
                print("      %#010x  %s%s" % (address, chunk[:12].hex(),
                                              "   ALL ZERO"
                                              if not any(chunk) else ""))
            found = _tmd_headers(data)
            print("      TMDs actually in RAM: %d" % len(found))
            if found:
                lo, hi = found[0], found[-1]
                print("          from %#010x to %#010x, %s vertices"
                      % (lo[0], hi[0],
                         "%d..%d" % (min(v for _, v, _ in found),
                                     max(v for _, v, _ in found))))
                walked = tmd_spans(data)
                print("          walked to their ends: %d..%d byte(s) each, "
                      "%d byte(s) of RAM in all"
                      % (min(e - s for s, e, _v, _p in walked),
                         max(e - s for s, e, _v, _p in walked),
                         sum(e - s for s, e, _v, _p in walked)))

        for row, slot in rows:
            found, before, after = game.field_diff(slot, row)
            print("  %s, slot %d (%s): %d byte(s)"
                  % (row, slot, SLOTS[slot], len(found)))
            report_field(found, before, after, maps, tmd_spans(before),
                         image=ready["image"], verbose=verbose)
    return 0


def _tmd_headers(data):
    """Every word-aligned Sony TMD header in *data*, as (address, verts, prims).

    A magic word alone is a four-byte coincidence, so the object table behind
    it has to be sane too -- that is what keeps this from reporting hundreds of
    hits in a 2 MiB scan.
    """
    import struct

    out = []
    magic = struct.pack("<I", layout.TMD_MAGIC)
    at = data.find(magic)
    while at != -1:
        if at % 4 == 0 and at + 40 <= len(data):
            flags, objects = struct.unpack_from("<2I", data, at + 4)
            if flags in (0, 1) and 0 < objects < 64:
                _vt, verts, _nt, _norms, _pt, prims, _scale = \
                    struct.unpack_from("<7i", data, at + 12)
                if (0 < verts < SANE_COUNT
                        and 0 < prims < SANE_COUNT):
                    out.append((RAM_BASE + at, verts, prims))
        at = data.find(magic, at + 1)
    return out


# --- self-check -----------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("oracle.py", _checks, verbose)


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt
    refuses_disc = c.refusing(WrongDisc)
    refuses_screen = c.refusing(NotArrived)
    refuses_ram = c.refusing(RamMismatch)

    import tempfile

    # -- the boxes are fractions, and resolving them is arithmetic ----------
    class Fake:
        def __init__(self, size):
            self.size = size

    small, large = Fake((320, 240)), Fake((960, 720))

    def covers(frame, frac):
        """The share of the frame a resolved box actually takes."""
        width, height = frame.size
        got = pixels(frame, frac)
        return (got[0] / width, got[1] / height, got[2] / width,
                got[3] / height)

    # The same share of the picture whatever the resolution scale is set to --
    # which is the whole reason the boxes are fractions.  Compared as shares
    # and not as multiplied pixels: truncation puts the four corners up to a
    # pixel apart, and a check that demands exact multiples fails on rounding
    # while saying nothing about the property.
    ok("a fractional box takes the same share of any frame",
       all(abs(a - b) <= 1.0 / min(small.size)
           for a, b in zip(covers(small, BADGE), covers(large, BADGE))),
       "%s vs %s" % (covers(small, BADGE), covers(large, BADGE)))
    ok("no box is given to a caller that asked for none",
       pixels(small, None) is None)
    ok("every box lies inside the frame",
       all(0.0 <= v <= 1.0 for box in (BADGE, ROW_VALUE) for v in box))

    # -- the two slots have to be far enough apart to be told apart ---------
    ok("the two slots' plates are further apart than the tolerance",
       abs(BADGE_MEAN[1] - BADGE_MEAN[2]) > BADGE_TOL,
       "%.6f apart, tolerance %.6f" % (abs(BADGE_MEAN[1] - BADGE_MEAN[2]),
                                       BADGE_TOL))
    ok("both slots are named", set(SLOTS) == set(BADGE_MEAN))

    # -- a press is held long enough for the game to see it -----------------
    # Three frames is the measured failure, so the constant is asserted
    # against it rather than merely commented.
    ok("a press is held longer than the three frames that failed",
       CONFIRM_FRAMES >= 8)

    # -- the screen gate refuses what is not the screen ---------------------
    class Picture:
        """A frame-shaped object, so the gate can be driven with no emulator."""

        def __init__(self, whole, badge, size=(320, 240)):
            self.size = size
            self._whole = whole
            self._badge = badge

        def is_black(self):
            return self._whole < 0.01

        def stats(self, box=None):
            return ((self._badge, 0.0) if box else (self._whole, 0.0))

        def difference(self, other, box=None):
            return abs((self._badge if box else self._whole)
                       - (other._badge if box else other._whole))

    game = Oracle.__new__(Oracle)
    good = Picture(SCREEN_MEAN, BADGE_MEAN[1])
    ok("the real screen passes", attempt(
        "check a good frame", lambda: game.require_looks(good, 1) or True)
       is True)
    refuses_screen("a black frame is not an arrival",
                   lambda: game.require_looks(Picture(0.0, 0.0), 1), "black")
    refuses_screen("another screen with the right plate is refused",
                   lambda: game.require_looks(Picture(0.5, BADGE_MEAN[1]), 1),
                   "mean")
    refuses_screen("the other slot's plate is refused",
                   lambda: game.require_looks(Picture(SCREEN_MEAN,
                                                      BADGE_MEAN[2]), 1),
                   "position plate")
    c.refuses("a slot this cycle does not have is refused",
              lambda: game.load_looks(3), "not one of this cycle's two",
              OracleError)

    # -- the state's media, read from inside the file -----------------------
    with tempfile.TemporaryDirectory() as tmp:
        import savestate

        state = savestate._synth(tmp, "synthetic.sav", b"\0" * 64)
        ok("the media field is read without a decompressor",
           media_of(state) == "/dev/null", media_of(state))
        refuses_disc("a state from another disc is refused",
                     lambda: require_media(state, "we2002-english.cue"),
                     "cannot tell you this")
        ok("and the right disc is accepted",
           require_media(state, "/dev/null") == "/dev/null")

        # The red case the file name cannot catch: same name, other disc.
        japanese = os.path.join(tmp, "%s_1.sav" % SERIAL)
        shutil.copy2(state, japanese)
        refuses_disc("a state named for the right serial is still refused",
                     lambda: require_media(japanese, "we2002-english.cue"),
                     SERIAL)

        # Restoring into a directory that is not DuckStation's has to refuse
        # rather than create one.  This is not hypothetical: an earlier draft
        # made the folder, and a mistyped fork path put both fixtures in
        # C:\nowhere\savestates while printing that it had restored them.
        saved = {name: os.environ.get(name)
                 for name in (ENV_STATES, "PES2_FORK")}
        os.environ[ENV_STATES] = tmp
        os.environ["PES2_FORK"] = os.path.join(tmp, "no-such-fork")
        try:
            shutil.copy2(state, project_state(1))
            c.refuses("restoring into a directory that is not there refuses",
                      lambda: restore_state(1, verbose=False),
                      "does not create it", Unavailable)
            ok("and it made no directory doing so",
               not os.path.exists(os.path.join(tmp, "no-such-fork")))
        finally:
            for name, was in saved.items():
                if was is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = was

    # -- a TMD is walked to its end, and a byte inside one is named --------
    #
    # Built rather than fixtured: the gate has no emulator, so the TMD is
    # forged.  It is the third bucket of report_field that this makes possible,
    # and without it the count of bytes "in a TMD" prints 0 forever whether or
    # not anything was measured (CORR-LOOKS-019).
    import struct

    at = 64
    forged = bytearray(256)
    struct.pack_into("<3I", forged, at, layout.TMD_MAGIC, 0, 1)  # id, flags, 1 object
    # Pointers are offsets from the object table (FIXP clear).  Vertices right
    # after the table, then one primitive packet of three payload words.
    scale = 4096  # not-an-address: a TMD's fixed-point scale
    struct.pack_into("<7i", forged, at + 12, 28, 3, 0, 0, 52, 1, scale)
    forged[at + 12 + 52 + 1] = 3            # the packet's ilen, in words
    forged[at + 12 + 52 + 3] = 0x2D  # not-an-address: a TMD mode byte

    heads = attempt("find the forged TMD", lambda: _tmd_headers(bytes(forged)),
                    default=[])
    ok("a forged TMD is found where it was put",
       heads == [(RAM_BASE + at, 3, 1)], "%s" % heads)

    walked = attempt("walk the forged TMD", lambda: tmd_spans(bytes(forged)),
                     default=[])
    ok("and it is walked past its variable-length primitives",
       walked == [(RAM_BASE + at, RAM_BASE + at + 80, 3, 1)], "%s" % walked)

    # The byte at +70 is INSIDE the primitive packet, which only the walk
    # reaches: a span that stopped at the vertex block would miss it and call
    # it residue.
    ok("a byte inside the packets belongs to the TMD",
       attribute_tmd(RAM_BASE + at + 70, walked) == 0)
    ok("a byte one past the end does not",
       attribute_tmd(RAM_BASE + at + 80, walked) is None)
    ok("and neither does one before the header",
       attribute_tmd(RAM_BASE + at - 4, walked) is None)

    # The SAME object with FIXP set, which is how every TMD in this game's RAM
    # is actually written.  It has to walk to the same end: read as a signed
    # word a resolved KSEG0 pointer is negative, and a span built from that
    # collapses to header-plus-table -- 40 bytes for every TMD, whatever its
    # size.  The synthetic one with FIXP clear passed happily while the real
    # ones did exactly that.
    fixp = bytearray(forged)
    struct.pack_into("<I", fixp, at + 4, 1)          # not-an-address: the FIXP flag
    struct.pack_into("<i", fixp, at + 12, RAM_BASE + at + 12 + 28 - (1 << 32))
    struct.pack_into("<i", fixp, at + 12 + 16, RAM_BASE + at + 12 + 52 - (1 << 32))
    resolved = attempt("walk a FIXP TMD", lambda: tmd_spans(bytes(fixp)),
                       default=[])
    ok("a resolved TMD walks to the same end as the relative one",
       resolved == walked, "%s vs %s" % (resolved, walked))

    # And the bucket the whole correction is about: with no model file to
    # attribute to, a byte in the TMD has to leave the residue count.
    import contextlib
    import io

    quiet = io.StringIO()  # report_field prints its buckets; this is a check
    with contextlib.redirect_stdout(quiet):
        counted = attempt(
            "report one byte that lands in a TMD",
            lambda: report_field([at + 70], forged, forged, {}, walked,
                                 verbose=False),
            default=None)
    ok("and the report says so out loud", "in a TMD: 1 byte(s)"
       in quiet.getvalue(), quiet.getvalue().strip())
    ok("a byte in a TMD is not counted as residue",
       counted is not None and counted[1] == 0, "%s" % (counted,))

    # -- the preflight, and the order that makes it worth having -----------
    #
    # The red case of CORR-LOOKS-017.  What went wrong was not the check but
    # WHEN it ran, so this is about when: with the Japanese track missing,
    # check_live has to refuse without ever constructing an Oracle.  Driving
    # it needs no emulator precisely because it must not get that far.
    ok("the Japanese track is on the prerequisite list",
       "image" in dict(PREREQUISITES))

    calls = []
    kept = globals()["PREREQUISITES"]
    globals()["PREREQUISITES"] = tuple(
        (key, (lambda k=key: calls.append(k) or k)) for key in "abc")
    try:
        walked = attempt("walk the prerequisite list", preflight, default=None)
    finally:
        globals()["PREREQUISITES"] = kept
    ok("the preflight runs every prerequisite on the list",
       calls == ["a", "b", "c"] and walked == {"a": "a", "b": "b", "c": "c"},
       "ran %s" % calls)

    saved = {name: os.environ.pop(name, None)
             for name in (layout.ENV_IMAGE, layout.ENV_DRIVE_IMAGE)}
    launched = []

    class NeverLaunches:
        """An Oracle that cannot be built -- constructing one is the failure."""

        def __init__(self, *args, **kwargs):
            launched.append(args)
            raise AssertionError("the emulator was launched anyway")

    was_oracle = globals()["Oracle"]
    globals()["Oracle"] = NeverLaunches
    # A .cue that does not exist: the point is that the run never gets far
    # enough to open it.  Without it the refusal would come from the FIRST
    # prerequisite and say nothing about the fourth.
    os.environ[layout.ENV_DRIVE_IMAGE] = "no-such-disc.cue"
    try:
        c.refuses("an unset Japanese track is a skip, not a RuntimeError",
                  image_to_read, layout.ENV_DRIVE_IMAGE, Unavailable)
        c.refuses("--check-live refuses when only the drive image is set",
                  lambda: check_live(verbose=False), "is not set", Unavailable)
        ok("and it refused before launching anything", not launched)
    finally:
        globals()["Oracle"] = was_oracle
        os.environ.pop(layout.ENV_DRIVE_IMAGE, None)
        for name, value in saved.items():
            if value is not None:
                os.environ[name] = value

    # -- the display-list walk ----------------------------------------------
    #
    # Built here, because the gate has no emulator: one node the way the band
    # really holds them, and then the two ways it can be wrong.
    import struct

    def node(length, code, words=None):
        """One [link][packet] node: the link declares `length` words."""
        out = struct.pack("<I", (length << 24) | 0x0006B53C)  # not-an-address: a link
        out += struct.pack("<I", (code << 24) | 0x7F7F7F)  # not-an-address: a colour
        return out + b"\x00" * 4 * ((words if words is not None else length) - 1)

    good = node(9, 0x2C)  # not-an-address: the textured-quad command
    counted, codes = attempt("walk one real node",
                             lambda: walk_packets(good), default=(0, {}))
    ok("a node whose declared length matches its command counts",
       counted == 1 and codes.get("textured quad") == 1,
       "%s %s" % (counted, codes))

    # The length is what makes this more than a byte coincidence: the same
    # command with the wrong declared length must NOT count.
    wrong = node(5, 0x2C, words=9)  # not-an-address: the same command, lying
    ok("a node whose length disagrees with its command does not count",
       walk_packets(wrong)[0] == 0, "%s" % (walk_packets(wrong),))
    ok("a word that is not a command does not count",
       walk_packets(node(9, 0x11))[0] == 0,  # not-an-address: not a GPU command
       "%s" % (walk_packets(node(9, 0x11))[0],))  # not-an-address: idem
    ok("and an empty region counts nothing",
       walk_packets(b"\x00" * 64) == (0, {}))

    # -- the RAM comparison -------------------------------------------------
    #
    # Built rather than fixtured, like every other self-check here: the gate
    # runs with no disc and no emulator, so the thing being compared has to be
    # a file this tree can make.
    import modelfile

    name = layout.EDT_MOD
    groups = [[("trunk", (7, 5)), ("left", (3, 2))],
              [("trunk", (7, 5)), ("boot", (4, 3))]]
    built = attempt(
        "build a synthetic model file",
        lambda: modelfile._build_file(groups,
                                      0x80010000,  # not-an-address: synthetic
                                      start_pad=12),
        default=None)
    if built is None:
        c.skip("the RAM comparison", "no synthetic file to compare")
        return
    body, placed = built
    start = min(placed.values())

    ok("a file compared with itself shows no difference", attempt(
        "compare with itself",
        lambda: len(_compare(name, body, body, start)["differing"]),
        default=-1) == 0)

    scan = section.scan(body, start)
    colour = scan.sections[0].offset + section.HEADER_SIZE + 2
    touched = bytearray(body)
    touched[colour] ^= 0xFF  # not-an-address: one colour byte of a primitive
    inside = attempt("compare with a rewritten primitive",
                     lambda: _compare(name, body, bytes(touched), start),
                     default=None)
    ok("a byte rewritten inside a section is reported, not refused",
       inside is not None and inside["differing"] == [colour],
       "%s" % (inside and inside["differing"]))
    ok("and it is placed within the primitive it belongs to",
       inside is not None and inside["in_primitive"] == [2],
       "%s" % (inside and inside["in_primitive"]))

    broken = bytearray(body)
    broken[4] ^= 0xFF  # not-an-address: a byte of the header
    refuses_ram("a difference before the first section means another file",
                lambda: _compare(name, body, bytes(broken), start),
                "not this file")

    # The other half of the same rule: a byte that falls in the gap BETWEEN
    # two sections is outside every section, and the game does not write
    # there.  This is the case that separates "the file is loaded here and the
    # game edits it" from "something else is loaded here".
    gap = scan.sections[0].end
    if gap < scan.sections[1].offset:
        strayed = bytearray(body)
        strayed[gap] ^= 0xFF  # not-an-address: a byte of the gap
        refuses_ram("a difference in the gap between sections is refused",
                    lambda: _compare(name, body, bytes(strayed), start),
                    "outside every section")
    else:
        c.skip("a difference in the gap between sections",
               "the synthetic file has no gap to plant one in")


# --- entry point ----------------------------------------------------------

def main(argv):
    try:
        if len(argv) == 2 and argv[1] == "--check":
            return self_check()
        if len(argv) == 2 and argv[1] == "--check-states":
            return check_states()
        if len(argv) == 2 and argv[1] == "--adopt-states":
            return adopt_states()
        if len(argv) == 2 and argv[1] == "--check-live":
            return check_live()
        if len(argv) == 2 and argv[1] == "--buffers":
            return check_buffers()
        if len(argv) == 2 and argv[1] == "--tmds":
            return check_tmds()
        if len(argv) >= 2 and argv[1] == "--fields":
            return check_fields(rows=tuple(argv[2:]) or None)
    except Unavailable as exc:
        print("oracle: skipped -- %s" % exc)
        return SKIP
    except OracleError as exc:
        print("oracle FAILED: %s" % exc, file=sys.stderr)
        return 1
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

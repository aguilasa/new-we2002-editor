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
    python tools/looks/oracle.py --palettes      # unknown (d), from the GPU side
    python tools/looks/oracle.py --kit [SLOT]    # which TEX_*.BIN the screen wears, off VRAM
    python tools/looks/oracle.py --scenery [SLOT] [--write]  # what draws the screen's furniture, off the display list
    python tools/looks/oracle.py --repaint [SLOT]  # which parts of the screen the game redraws every frame
    python tools/looks/oracle.py --pages [SLOT]    # what on the screen is drawn from each VRAM page
    python tools/looks/oracle.py --assembly [HAIR ...]  # every value of a field
    python tools/looks/oracle.py --where [HAIR]  # where a field goes when the file does not move
    python tools/looks/oracle.py --hair          # who writes the hair window, and from where
    python tools/looks/oracle.py --patched [HAIR [SLOT [TUPLE ...]]]  # which sections the game has edited, value by value
    python tools/looks/oracle.py --colour SKIN [SLOT [TUPLE ...]]  # which primitives of each head a colour row moves
    python tools/looks/oracle.py --writes [HAIR [SLOT]]  # every quad the game writes, value by value
    python tools/looks/oracle.py --screen [--write]  # LOOKS SET measured: every text, help, cursor and box; --write makes screen.json
    python tools/looks/oracle.py --keys [SEQUENCE [SLOT]]  # the same presses in the game, in screen.json and in our window; a repetition is written Right x41
    python tools/looks/oracle.py --glyphs [SLOT]  # the font rule of glyphs.py against every font sprite the frame drew
    python tools/looks/oracle.py --help-box [SLOT]  # who writes the help page, and that its glyphs are the console's, not the disc's
    python tools/looks/oracle.py --default [SLOT]  # what NAT and DEFAUL do: the nationality byte, and the default that is not applied
    python tools/looks/oracle.py --pose [SLOT]  # where the pose comes from: ANIME.BIN in RAM, the entry the screen plays, and the GTE matrix load
    python tools/looks/oracle.py --pose <SLOT> <N> [N ...]  # the pose ITSELF: the matrix and translation of every piece of frame N, and the hierarchy
    python tools/looks/oracle.py --poses [SLOT [N ...]]  # the same over both slots and the eight spread frames
    python tools/looks/oracle.py --stature [SLOT]
    python tools/looks/oracle.py --closeups [SLOT]  # which rows zoom the panel onto the head, and the camera of each  # what HEIG and BODY do: the scale, the camera and the pieces, against stature.py
"""

from __future__ import annotations

import ctypes
import hashlib
import os
import shutil
import struct
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

SESSION_LOST = "invalid MCP-Session-Id"
"""What the fork answers when the session this client holds is no longer its.

**The server keeps one session.**  Measured 2026-09-17, three runs of three:
a second client's `initialize` on the same port makes the first client's next
call fail with exactly this, and every call after it (CORR-LOOKS-051).  This
repository registers the fork in `.mcp.json`, so the editor is a second client
on port 2346, and one `looks_live` run in fourteen lost its session at the first
`pause` that way."""


class OneSession:
    """The fork's MCP client, handshaken again ONCE when its session is taken.

    Once per loss, and said every time, never silently: a call refused for a
    lost session was refused before it ran, so repeating it after a new
    `initialize` is the same call and not a second one.  A loss right after
    the new handshake raises -- two clients fighting over the port is a
    machine to fix, not a run to repeat until it passes.
    """

    def __init__(self, client):
        self._client = client
        self.renewed = 0

    def call(self, name, **arguments):
        import mcp

        try:
            return self._client.call(name, **arguments)
        except mcp.ToolError as exc:
            if SESSION_LOST not in str(exc):
                raise
        self._client.session = None
        self._client.server = None
        self._client.initialize()
        self.renewed += 1
        print("  MCP session taken by another client on the port -- "
              "initialised again before %s (%d time(s) this run)"
              % (name, self.renewed), flush=True)
        return self._client.call(name, **arguments)

    def __getattr__(self, attribute):
        return getattr(self._client, attribute)


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
        self.client = OneSession(self.client)
        # From here on the emulator is up, and `__exit__` does not run for an
        # exception raised inside `__enter__`.  The first `looks_live` run
        # under ctest lost its MCP session at this `pause()` and left the
        # emulator running with nobody to kill it (LOOKS-TASK-19).
        try:
            if hide_window(self.window):
                self.say("window moved off the visible desktop")
            os.makedirs(self.out_dir, exist_ok=True)
            self.pause()
        except BaseException:
            fork.kill(verbose=False)
            raise
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


WALK_LIMIT = 32
"""How many presses a field walk may take before it is called a runaway.

Twice the sixteen windows a 256-entry record holds, so a field with a domain
this cycle has not met yet still comes back with its whole cycle instead of a
refusal -- and a field that never returns to where it started still stops.
"""


def clut_address(image, name, index, primitive):
    """Where one primitive's CLUT id lives in main RAM.

    Derived from the disc and the load address, never written down: the file is
    loaded whole at `layout.BASE`, so the offset a scan gives is the offset in
    RAM.  `verify_load()` is what earns that.
    """
    import iso_source

    with iso_source.open_disc(image) as disc:
        data = disc.read(name)
    scan = section.scan(data, layout.GEOMETRY_START[name])
    one = scan.sections[index]
    return (layout.BASE[name] + one.offset + section.HEADER_SIZE
            + primitive * section.PRIMITIVE_SIZE + section.CLUT_IN_PRIMITIVE)


def section_address(image, name, index):
    """(first byte, length) of one whole section's BODY in main RAM.

    Primitives **and** vertices, and the second half is not padding: a hair
    style is a different shape, so it moves the mesh as well as the band of the
    atlas it samples.  Watching only the primitives is what turned a 32-value
    HAIR walk into three -- two styles that share a `v` band have identical
    primitive blocks, and the walk read the repeat as the end of the range.
    """
    import iso_source

    with iso_source.open_disc(image) as disc:
        data = disc.read(name)
    scan = section.scan(data, layout.GEOMETRY_START[name])
    one = scan.sections[index]
    return (layout.BASE[name] + one.offset + section.HEADER_SIZE,
            len(one.primitives) * section.PRIMITIVE_SIZE
            + len(one.vertices) * section.VERTEX_SIZE)


WATCH_SECONDS = 90
"""How long a write watchpoint is given before silence is called a failure.

A watchpoint that never fires is a **result only if it was waited for**: the
`who_writes.py` of the PES2 tree says the same thing, and the reason is that an
address nothing writes and an emulator that stopped stepping are the same
silence.
"""

IDLE_SECONDS = 5
"""How long the watchpoint runs with NOTHING pressed, before the press.

The control for the measurement below.  If the byte is written while the game
merely animates, then a hit after a press says nothing about the press, and
every reading built on it would be about the renderer's own housekeeping.
"""

WINDOW_BEFORE = 8
WINDOW_AFTER = 4
CALLER_BEFORE = 12
"""How much disassembly is read around the stop.

The fork stops on the instruction AFTER the store on this build -- measured by
PES2 in 2026-09-03 and the reason `who_writes.split_store` scans a window
instead of one line.
"""

INSTRUCTION_SIZE = 4


SETTLE_TRIES = 8
"""How many extra looks a sample gets before it is called settled.

**The game rewrites a section's primitives over MORE THAN ONE FRAME**, and the
28 frames a press already waits are not always enough.  Measured 2026-09-15 on
the first walk of BOOTS: one press left 34 of the 42 primitives it moves on the
new CLUT and 8 still on the old, in the same read.  Two consequences, and the
second is what makes this a guard rather than a comfort:

* a half-written block is a state that never existed, and a table built from
  one describes a frame the game never drew;
* a sample taken before the write STARTS equals the one before it, which the
  walk reads as the end of the range.  That is what turned a 32-value HAIR walk
  into three values and an 8-value BOOTS walk into nine.
"""


def texcoord_address(image, name, index, primitive, corner=0):
    """Where one corner's `v` byte of one primitive lives in main RAM.

    Same derivation as `clut_address`: the disc says the offset, `layout.BASE`
    says where the file is loaded, and `verify_load()` is what earns the sum.
    """
    import iso_source

    with iso_source.open_disc(image) as disc:
        data = disc.read(name)
    scan = section.scan(data, layout.GEOMETRY_START[name])
    one = scan.sections[index]
    return (layout.BASE[name] + one.offset + section.HEADER_SIZE
            + primitive * section.PRIMITIVE_SIZE
            + corner * section.TEXCOORD_STRIDE + section.V_IN_TEXCOORD)


def _wait_for_hit(game, seconds):
    """True if the armed watchpoint fired within *seconds*, False if it did not.

    No exception either way: this is used once as a CONTROL, where not firing
    is the good answer, and once as the measurement, where firing is.  Which
    silence is a failure is the caller's to say.
    """
    import time

    import who_writes

    deadline = time.time() + seconds
    while time.time() < deadline:
        if who_writes.is_paused(game.client.call("wait_for_pause")):
            return True
    return False


def catch_write(game, address, seconds=WATCH_SECONDS, presses=0,
                button="Right"):
    """Arm a write watchpoint on one byte and come back with the hit.

    `presses` is how many times *button* may be pressed while waiting: zero
    means the byte is expected to be written by the game on its own, which is
    what the head's scratch copy turned out to do -- it is rewritten every
    frame whether or not anything is pressed (measured 2026-09-16), and that is
    why this does not insist on a press being the cause.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="write",
                address=who_writes.hx(address))
    try:
        client.call("continue")
        # The press comes FIRST when there is one.  This byte is not written
        # every frame -- measured: 90s of free running at one value of the
        # field and nothing touched it -- so waiting before pressing spends
        # the whole budget on a machine that has nothing to say.
        hit = False
        for _ in range(max(1, presses)):
            if presses:
                client.call("press_button", button=button,
                            duration_frames=CONFIRM_FRAMES)
            hit = _wait_for_hit(game, max(1, seconds // max(1, presses)))
            if hit:
                break
        if not hit:
            raise OracleError(
                "nothing wrote %s in %ds%s: either the address is not what "
                "this thinks it is, or the emulator stopped stepping -- "
                "silence is not an answer here"
                % (who_writes.hx(address), seconds,
                   " and %d press(es) of %s" % (presses, button)
                   if presses else ""))
        registers = client.call("read_registers", group="gpr")
        pc = who_writes.register_value(registers, "pc")
        if pc is None:
            raise OracleError("the register read gave no pc: %r"
                              % (str(registers)[:200],))
        window = client.call(
            "disassemble",
            address=who_writes.hx(pc - WINDOW_BEFORE * INSTRUCTION_SIZE),
            count=WINDOW_BEFORE + WINDOW_AFTER)
        rows = window if isinstance(window, list) else []
        store = None
        for row in rows:
            text = row.get("instruction") if isinstance(row, dict) else str(row)
            parts = who_writes.split_store(text)
            if not parts:
                continue
            _mnemonic, _source, offset, base = parts
            value = who_writes.register_value(registers, base)
            if value is not None and value + offset == address:
                store = (row, parts, value)
                break
        caller = []
        ra = who_writes.register_value(registers, "ra")
        if ra is not None:
            reply = client.call(
                "disassemble",
                address=who_writes.hx(ra - CALLER_BEFORE * INSTRUCTION_SIZE),
                count=CALLER_BEFORE + WINDOW_AFTER)
            caller = reply if isinstance(reply, list) else []
        return {"pc": pc, "registers": registers, "rows": rows,
                "store": store, "caller": caller}
    finally:
        try:
            client.call("breakpoint", action="clear")
        except Exception:  # noqa: BLE001
            pass


def _flat_registers(registers):
    """(name, value) for every register in whatever shape the fork answers in."""
    import who_writes

    out = []
    stack = [registers]
    while stack:
        item = stack.pop()
        if not isinstance(item, dict):
            continue
        for key, value in item.items():
            if isinstance(value, dict):
                stack.append(value)
                continue
            if not isinstance(value, (str, int)):
                continue
            try:
                out.append((key, who_writes.parse_address(value)))
            except who_writes.Fail:
                # A register file can carry a name, a flag word or a status
                # string beside the numbers; one of those is not a failure of
                # this sweep, it is simply not an address.
                continue
    return sorted(set(out))


def model_maps(image):
    """{load address: (name, size, sections)} for both model files.

    What `attribute()` needs to say which SECTION a live pointer is inside --
    which is the whole question this task is missing an answer to.
    """
    import iso_source

    maps = {}
    with iso_source.open_disc(image) as disc:
        for name in sorted(layout.BASE):
            data = disc.read(name)
            scan = section.scan(data, layout.GEOMETRY_START[name])
            maps[layout.BASE[name]] = (name, len(data), scan.sections)
    return maps


def pointers_into_models(registers, maps):
    """Every register that lands inside a model file, with where it lands."""
    found = []
    for name, value in _flat_registers(registers):
        if name in ("pc", "ra"):
            continue
        where = attribute(value, maps)
        if where:
            found.append((name, value, where))
    return found


def _say_writer(found, address, maps=None):
    """The reading of one watchpoint hit, printed."""
    import who_writes

    print("      stopped at %s, watching %s"
          % (who_writes.hx(found["pc"]), who_writes.hx(address)))
    if found["store"]:
        row, (mnemonic, source, offset, base), value = found["store"]
        print("      written by %s  %s %s, %s(%s)   [%s = %s]"
              % (row.get("address"), mnemonic, source,
                 who_writes.hx(offset), base, base, who_writes.hx(value)))
        held = who_writes.register_value(found["registers"], source)
        if held is not None:
            print("      and the value stored is %s = %s"
                  % (source, who_writes.hx(held)))
    else:
        print("      no instruction in the window resolves to that byte -- "
              "read the disassembly below", flush=True)
    ra = who_writes.register_value(found["registers"], "ra")
    if ra is not None:
        print("      called from ra = %s" % who_writes.hx(ra), flush=True)
        for row in found.get("caller") or ():
            if isinstance(row, dict):
                print("        caller  %s  %s"
                      % (row.get("address"), row.get("instruction")))
    if maps:
        for name, value, where in pointers_into_models(found["registers"],
                                                       maps):
            print("      %-4s = %s  ->  %s section %s, %s"
                  % (name, who_writes.hx(value), where[0], where[1], where[2]))
    for row in found["rows"]:
        if isinstance(row, dict):
            mark = " <--" if found["store"] and row is found["store"][0] else ""
            print("        %s  %s%s"
                  % (row.get("address"), row.get("instruction"), mark))


def steady(game, sample):
    """*sample()* read until two looks in a row agree.

    Refuses rather than returning the last look: a block that will not settle
    is either animated -- in which case it is the wrong thing to watch -- or
    the emulator is not paused, and both make every value after it fiction.
    """
    previous = sample()
    for _ in range(SETTLE_TRIES):
        game.step(SETTLE_FRAMES)
        current = sample()
        if current == previous:
            return current
        previous = current
    raise OracleError(
        "what this is watching never settled in %d x %d frame(s): it is being "
        "written every frame, or the emulator is not paused"
        % (SETTLE_TRIES, SETTLE_FRAMES))


def walk(game, slot, row, sample, verbose=True):
    """Every state one field reaches, from one end of its range to the other.

    `sample()` answers whatever the caller wants watched -- a CLUT id, a whole
    block of primitives -- and has to answer something comparable, because a
    repeat is how the end of the range is found.

    **These fields clamp; they do not wrap.**  Measured 2026-09-15: a fourth
    Right on SKIN leaves the id exactly where the third put it.  So the walk is
    Left until the sample stops moving, then Right until it stops moving, which
    comes back with the whole domain in order.
    """
    game.load_looks(slot)
    game.select_row(row)

    def to_the_end(button):
        seen = []
        for _ in range(WALK_LIMIT):
            previous = steady(game, sample)
            game.press(button, expect_change=False)
            value = steady(game, sample)
            if value == previous:
                return seen
            seen.append(value)
        raise OracleError(
            "%s on slot %d kept moving for %d presses of %s"
            % (row, slot, WALK_LIMIT, button))

    start = steady(game, sample)
    to_the_end("Left")
    values = [steady(game, sample)] + to_the_end("Right")
    if start not in values:
        raise OracleError(
            "%s started at a state the walk never came back to" % row)
    if verbose:
        game.say("%s reaches %d value(s)" % (row, len(values)))
    return values, values.index(start)


def walk_field(game, slot, row, address, verbose=True):
    """Every CLUT id one field reaches, in the order it reaches them.

    The assertion is the RAM and not the picture: the id says which palette the
    next frame will read, where the value cell only says that the label
    changed.  `walk()` does the walking; this says what to watch.
    """
    import struct

    path = os.path.join(game.out_dir, "clut.bin")

    def read():
        return struct.unpack("<H", game.read_ram(address, 2, path))[0]

    values, _start = walk(game, slot, row, read, verbose=False)
    if verbose:
        game.say("%s reaches %d value(s): %s"
                 % (row, len(values), ", ".join("%#06x" % v for v in values)))
    return values


def vram_region(game, x, y, width, height):
    """One rectangle of the GPU's own frame buffer, as rows of (r, g, b).

    The fork answers `read_vram_region` with a **PNG file**, not with
    halfwords, so this is as close to the raw VRAM as the server gets.  The
    comparison downstream is made at five bits a channel, which is what the
    hardware stores and what survives the trip either way.
    """
    import atlas

    reply = game.client.call("read_vram_region", x=x, y=y,
                             width=width, height=height)
    path = reply.get("output_path")
    if not path or not os.path.exists(path):
        raise OracleError("read_vram_region reported %r and there is no file "
                          "there" % path)
    got_w, got_h, rows = atlas.read_png(path)
    if (got_w, got_h) != (width, height):
        raise OracleError("asked VRAM for %dx%d at (%d, %d) and the PNG is "
                          "%dx%d" % (width, height, x, y, got_w, got_h))
    return rows


def _five_bits(pixel):
    """An 8-bit PNG pixel back down to the five bits the hardware holds."""
    return tuple(channel >> 3 for channel in pixel[:3])


def _disc_five_bits(value):
    """The same three channels out of one BGR555 halfword on the disc."""
    return (value & 0x1F, (value >> 5) & 0x1F, (value >> 10) & 0x1F)  # not-an-address: the BGR555 fields


def check_palettes(slot=2, verbose=True):
    """Unknown (d), from the GPU's side: the palettes are the disc's, and static.

    Three things, and the third is the one that makes the first two worth
    having:

    1. the palette strip in VRAM **is** what `DAT2D.BIN` holds, entry for
       entry, resolved by the same rule a renderer will use -- so the file a
       renderer reads is the file the console draws with.  The rule is
       `texture.covering`, narrower record wins, and row 484 is what makes
       that a test rather than a formality: six 16-entry records sit on top of
       a 256-entry one there, and VRAM holds the narrow ones;
    2. stepping a colour field does **not** write to that strip -- the palettes
       do not move, the id that points at them does;
    3. each field's whole cycle of CLUT ids, read out of RAM after every press,
       which says which windows of the grid it can reach.
    """
    import struct

    import iso_source
    import skin
    import texture

    ready = preflight()
    address = clut_address(ready["image"], layout.MODEL, layout.HEAD_SECTION,
                           layout.HAIR_PRIMITIVES[0])
    beard = clut_address(ready["image"], layout.MODEL, layout.HEAD_SECTION,
                         layout.FACE_PRIMITIVES[0])
    with iso_source.open_disc(ready["image"]) as disc:
        data = disc.read(layout.DAT2D)
    records = texture.palettes(data)
    wide = sorted((r for r in records if r.colours == texture.WIDE),
                  key=lambda r: r.offset)
    # How far across each CLUT row to compare: the width of a wide record,
    # which is as far as this container's own records reach.  Past it the row
    # belongs to whatever else the frame buffer is holding -- on row 480 that
    # is a kit palette out of a TEX_*.BIN, and it is not this file's to check.
    span = texture.WIDE

    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        game.load_looks(slot)

        print("  every CLUT row of /BIN/DAT2D.BIN against VRAM, resolved the "
              "way a renderer resolves it", flush=True)
        for y in sorted({r.y for r in records}):
            got = vram_region(game, 0, y, span, 1)[0]
            differ, unresolved = [], 0
            for x in range(span):
                try:
                    record = texture.covering(records, x, y, 1)
                except texture.NoPalette:
                    unresolved += 1
                    continue
                want = struct.unpack_from(
                    "<H", data, record.offset + 2 * (x - record.x))[0]
                if _five_bits(got[x]) != _disc_five_bits(want):
                    differ.append(x)
            print("      row %d: %d of %d entr(y/ies) differ, %d that no "
                  "record covers" % (y, len(differ), span - unresolved,
                                     unresolved))
            if differ:
                problems.append("VRAM row %d differs from the disc at %d "
                                "entr(y/ies), first at x=%d"
                                % (y, len(differ), differ[0]))

        first = wide[0]
        before = vram_region(game, first.x, first.y, first.colours, 1)
        game.select_row("H.COL")
        game.press("Right", expect_change=False)
        after = vram_region(game, first.x, first.y, first.colours, 1)
        moved = sum(1 for i in range(first.colours) if before[0][i] != after[0][i])
        print("  one step of H.COL moved %d of the %d entries of the palette "
              "in VRAM" % (moved, first.colours), flush=True)
        if moved:
            problems.append("stepping H.COL rewrote %d palette entr(y/ies) in "
                            "VRAM: the field is not only choosing a window"
                            % moved)

        print("  the windows each field reaches, read out of RAM per press", flush=True)
        for row, at in (("SKIN", address), ("H.COL", address),
                        ("H.F.COL.", beard)):
            seen = walk_field(game, slot, row, at, verbose=verbose)
            cells = [skin.grid(v) for v in seen]
            print("      %-9s %d value(s): %s"
                  % (row, len(seen),
                     ", ".join("row %d col %d" % cell for cell in cells)))
            if len({cell[0] for cell in cells}) > 1 and \
                    len({cell[1] for cell in cells}) > 1:
                problems.append("%s moved both coordinates of the grid, and "
                                "each field was measured to move one" % row)

    print("oracle --palettes: %s"
          % ("ok" if not problems else "%d problem(s)" % len(problems)))
    for line in problems:
        print("    %s" % line, flush=True)
    return 1 if problems else 0


KIT_EXACT = "a page and a palette"
"""What a container has to reproduce before it is called the kit on screen.

Both, and halfword for halfword.  One alone would be a coincidence to argue
about with 105 candidates in the room; the two together are the pixels of the
body and the colours they are drawn in, which is the whole of what a kit is.
Measured 2026-09-20 on both states: TEX_A4 reproduces one page and two
palettes exactly and no other container reproduces any of the three.
"""


def _kit_records(body):
    """The records of one kit container, images and palettes alike."""
    import texture

    return [record for table in texture.tables(body) for record in table.records]


def _vram_words(game, records, seen):
    """{(x, y, w, h): rows of five-bit VRAM}, read once per distinct rect."""
    for record in records:
        key = (record.x, record.y, record.w, record.h)
        if key not in seen:
            seen[key] = [[_five_bits(pixel) for pixel in row]
                         for row in vram_region(game, *key)]
    return seen


def _kit_payload(body, record):
    """The halfwords one record holds, palette or page.

    A palette is stored plain and a page is an LZSS stream -- the same split
    `texture.read_palette` and `atlas.read_image` make, and the reason this
    reads bytes rather than calling them is that the comparison downstream is
    against RAW VRAM: indices decoded into texels would be a second reading of
    the same bytes, and a mismatch in it would not say which of the two was
    wrong.  One page's stream gives more than its rect declares (the 64x64 at
    (704, 256) hands back 16384 B for 8192), so the rect is what is read.
    """
    import lzss

    if record.is_clut:
        raw = body[record.offset:record.offset + record.size]
    else:
        plain, _used = lzss.decompress(body, record.offset)
        raw = bytes(plain[:record.size])
    if len(raw) < record.size:
        raise OracleError("the record at %d holds %d B and declares %d"
                          % (record.offset, len(raw), record.size))
    return struct.unpack("<%dH" % (record.size // 2), raw)


def _record_difference(body, record, rows):
    """Halfwords of one record that differ from the VRAM rows it declares."""
    stored = _kit_payload(body, record)
    differ = 0
    for row in range(record.h):
        line = rows[row]
        base = record.w * row
        differ += sum(1 for at in range(record.w)
                      if _disc_five_bits(stored[base + at]) != line[at])
    return differ


def _kit_difference(body, records, seen):
    """{rect: the best this container does on it} against what VRAM holds.

    **The best of the file's own candidates for that rectangle, not the sum
    over its records.**  A kit container holds the strip TWICE -- two pages
    and two palettes at the same VRAM coordinates, which is the home kit and
    the away one -- and the console uploads ONE of them.  Summing both made
    every container differ by thousands and the winner by 12,618, close enough
    to the runner-up that the measurement decided nothing (measured
    2026-09-20, before this).
    """
    out = {}
    for record in records:
        key = (record.x, record.y, record.w, record.h)
        differ = _record_difference(body, record, seen[key])
        out[key] = min(out[key], differ) if key in out else differ
    return out


def check_kit(slots=(2, 1), verbose=True):
    """`--kit [SLOT]`: which `TEX_*.BIN` the screen is wearing, read off VRAM.

    The uniform is per team and lives in 105 containers of identical shape
    (section 1.8), so the file a renderer must read cannot be chosen by name:
    it is chosen by asking the console which one it uploaded.  Every record of
    every container is compared, halfword for halfword, against the VRAM
    rectangle it declares -- the same five bits the hardware keeps, the same
    comparison `--palettes` makes for `DAT2D.BIN`.

    The controls, before the answer:

      **the same slot twice** -- VRAM read again after a second `load_state`
          has to give the same rectangles, or the reading is the emulator's
          mood;
      **the runner-up** -- no other container may fit those rectangles at
          all, and how far the nearest one is off is printed, because "closest
          of 105" and "the one" are not the same claim;
      **the other slot** -- printed beside it, because the two states are two
          different teams and are the cheapest wrong answer available.
    """
    import iso_source

    ready = preflight()
    with iso_source.open_disc(ready["image"]) as disc:
        bodies = {tag: disc.read(layout.kit_path(tag))
                  for tag in layout.KIT_TAGS}
    records = {tag: _kit_records(body) for tag, body in bodies.items()}
    shapes = {tuple(sorted((r.x, r.y, r.w, r.h) for r in one))
              for one in records.values()}
    print("  %d kit container(s), %d distinct set(s) of rectangles"
          % (len(bodies), len(shapes)))

    problems = []
    found = {}
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, SLOTS[slot]))
            restore_state(slot, verbose=False)
            game.load_looks(slot, label="kit-%d" % slot)
            seen = {}
            for tag in layout.KIT_TAGS:
                _vram_words(game, records[tag], seen)
            restore_state(slot, verbose=False)
            game.load_looks(slot, label="kit-%d-again" % slot)
            again = {}
            for tag in layout.KIT_TAGS:
                _vram_words(game, records[tag], again)
            if again != seen:
                problems.append("slot %d: VRAM read twice gives two different "
                                "pictures, so no container below is measured "
                                "against anything" % slot)
                continue
            print("    control: %d rectangle(s) of VRAM read twice, identical"
                  % len(seen))
            apart = {tag: _kit_difference(bodies[tag], records[tag], seen)
                     for tag in layout.KIT_TAGS}
            whole = {tag: sum(one.values()) for tag, one in apart.items()}
            # What names the kit is an EXACT rectangle, and not the smallest
            # total: of the seven rectangles a container declares, the screen
            # uploads three -- the other four hold whatever else the frame
            # buffer has there, and they differ by thousands for EVERY
            # container, which drowns the answer (measured 2026-09-20: 12,138
            # against 13,274 over all seven, which decides nothing).
            exact = {key: sorted(tag for tag in layout.KIT_TAGS
                                 if apart[tag][key] == 0)
                     for key in sorted(seen)}
            worn = [key for key in sorted(exact) if exact[key]]
            claimed = {tag for key in worn for tag in exact[key]}
            for key in sorted(seen):
                owners = exact[key]
                print("      (%4d,%4d) %3dx%-3d  exact in %-28s"
                      % (key[:2] + (key[2], key[3],
                                    ", ".join("TEX_" + one for one in owners)
                                    or "no container")))
            if not worn:
                problems.append("slot %d: no container reproduces any "
                                "rectangle of VRAM exactly" % slot)
                continue
            if len(claimed) > 1 or any(len(exact[key]) > 1 for key in worn):
                problems.append(
                    "slot %d: %s reproduce a rectangle exactly, so the kit is "
                    "not named" % (slot, ", ".join("TEX_" + one for one
                                                   in sorted(claimed))))
                continue
            best = claimed.pop()
            found[slot] = best
            pages = [key for key in worn if key[3] > 1]
            palettes = [key for key in worn if key[3] == 1]
            others = {tag: sum(apart[tag][key] for key in worn)
                      for tag in layout.KIT_TAGS if tag != best}
            runner = min(others, key=others.get)
            print("    the screen wears TEX_%s: %d page(s) and %d palette(s) "
                  "halfword for halfword, and the nearest other container, "
                  "TEX_%s, differs in %d of them"
                  % (best, len(pages), len(palettes), runner, others[runner]))
            print("    (over all %d rectangles, including the %d the screen "
                  "does not upload, TEX_%s differs by %d and the next by %d "
                  "-- which is why the exact rectangle is what decides)"
                  % (len(seen), len(seen) - len(worn), best, whole[best],
                     sorted(whole.values())[1]))
            if not pages or not palettes:
                problems.append(
                    "slot %d: TEX_%s is exact on %d page(s) and %d palette(s) "
                    "-- a kit is both, and one of them alone is a coincidence "
                    "with 105 candidates"
                    % (slot, best, len(pages), len(palettes)))
            if not others[runner]:
                problems.append("slot %d: TEX_%s is not the only container "
                                "that fits those rectangles" % (slot, best))
    if len(found) == len(slots) and len(set(found.values())) == 1:
        print("  both states wear the same kit, TEX_%s" % found[slots[0]])
    elif len(found) == len(slots):
        print("  the two states wear different kits: %s"
              % ", ".join("slot %d TEX_%s" % (k, v)
                          for k, v in sorted(found.items())))
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --kit: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


SCENERY_CENTRE = (256, 120)
"""The draw offset the screen's packets are written around.

Every vertex in the band is signed and small -- the row stripes run from -79 to
+65 -- because the game sets the GPU's drawing offset to the middle of the
512x240 display and writes the furniture around it.  The same centre
`screen.json` stores its text anchors in (LOOKS-TASK-21), which is what says
this is the screen's own frame and not a coincidence.
"""

_FURNITURE = (("28", 5, False, 4), ("2A", 5, False, 4), ("38", 8, True, 4),
              ("3A", 8, True, 4), ("20", 4, False, 3), ("22", 4, False, 3),
              ("30", 6, True, 3), ("32", 6, True, 3))
SCENERY_QUADS = {int(code, 16): (words, gradient, corners)
                 for code, words, gradient, corners in _FURNITURE}
"""The untextured packet codes, as (words, gradient, corners).

Flat and gouraud, quads and triangles: what a 2D screen paints a panel, a
stripe and a band with.  Written as codes and read back with `int`, like
`_PACKETS` above and for its reason: a GPU opcode is not an address, and a
`# not-an-address:` on each line would silence the sweep while teaching
nothing.
"""

_SPRITES = (("64", 4, None), ("65", 4, None), ("66", 4, None),
            ("67", 4, None), ("6C", 3, 1), ("6D", 3, 1), ("6E", 3, 1),
            ("6F", 3, 1), ("74", 3, 8), ("75", 3, 8), ("76", 3, 8),
            ("77", 3, 8), ("7C", 3, 16), ("7D", 3, 16), ("7E", 3, 16),
            ("7F", 3, 16))
SPRITE_CODES = {int(code, 16): (words, size) for code, words, size in _SPRITES}
"""The textured RECTANGLE codes, as (words, fixed size or None).

A sprite carries a corner and, for the variable form, a size; the page comes
from the draw mode in force rather than from the packet.  This screen's text,
the plate and the arrows are all sprites, and each rides in ONE node behind the
E1 that sets its page -- so a reader that classifies a node by its first word
calls the whole node a draw-mode change and never sees the sprite
(LOOKS-TASK-31, 2026-09-21).  `commands_of` is what splits the node.
"""

_TEXTURED = (("2C", 9), ("2D", 9), ("2E", 9), ("2F", 9), ("24", 7), ("25", 7),
             ("34", 9), ("3C", 12))
TEXTURED_QUADS = {int(code, 16): words for code, words in _TEXTURED}
"""The textured quad codes, by length: the figure, and anything else cut from
a page in VRAM."""

SCENERY_DIR = os.path.join(ROOT, "work", "looks-scenery")
"""Where `--scenery` writes what it measured, one JSON per slot."""


def _signed_vertex(word):
    """One GPU vertex word as (x, y), both signed 16-bit."""
    x, y = word & 0xFFFF, (word >> 16) & 0xFFFF  # not-an-address: two halves
    return (x - (1 << 16) if x >> 15 else x, y - (1 << 16) if y >> 15 else y)


def _packet_colour(word):
    """One GPU colour word as (r, g, b)."""
    return (word & 0xFF, (word >> 8) & 0xFF, (word >> 16) & 0xFF)  # not-an-address: three channels


def scenery_pages(data, display):
    """The textured QUADS of a band, grouped by the VRAM page they sample.

    Sprites are left to `sprites_of`: they take their page from the draw mode
    in force, which a scan of packets one at a time does not know.

    A textured quad carries its page in the second half of the `uv1` word and
    its CLUT in the second half of `uv0`, which is where the hardware reads
    them from.  What comes back is {(page, clut): (count, box on screen)} --
    the question section 10.3 (o) asks about the title band, the plate and the
    glyphs: they are images, and this says which page they are cut from.
    """
    out = {}
    for at in range(0, len(data) - 40, 4):
        link = struct.unpack_from("<I", data, at)[0]
        length, code = link >> 24, data[at + 7]
        if code in TEXTURED_QUADS and TEXTURED_QUADS[code] == length:
            points = [_signed_vertex(struct.unpack_from(
                "<I", data, at + 8 + 8 * i)[0]) for i in range(4)]
            clut = struct.unpack_from("<H", data, at + 14)[0]
            page = struct.unpack_from("<H", data, at + 22)[0]
        else:
            continue
        points = [(x + SCENERY_CENTRE[0], y + SCENERY_CENTRE[1])
                  for x, y in points]
        if not _inside(points, display):
            continue
        xs = [x for x, _y in points]
        ys = [y for _x, y in points]
        key = (page, clut)
        count, box = out.get(key, (0, None))
        here = (min(xs), min(ys), max(xs), max(ys))
        if box is not None:
            here = (min(box[0], here[0]), min(box[1], here[1]),
                    max(box[2], here[2]), max(box[3], here[3]))
        out[key] = (count + 1, here)
    return out


def page_vram(page):
    """(x, y, bits) the page word names in VRAM."""
    return ((page & 0x0F) * 64, ((page >> 4) & 1) * 256,  # not-an-address: page fields
            (4, 8, 16, 16)[(page >> 7) & 3])


def clut_vram(clut):
    """(x, y) the CLUT word names in VRAM."""
    return ((clut & 0x3F) * 16, (clut >> 6) & 0x1FF)  # not-an-address: clut fields


def _inside(points, display):
    return all(0 <= x <= display[0] and 0 <= y <= display[1]
               for x, y in points)


def check_scenery(slots=(2, 1), write=False, verbose=True):
    """`--scenery [SLOT]`: what draws the screen's furniture, off the band.

    The question of section 10.3 (o): is the panel's gradient, the row
    stripes, the title band and the help box an IMAGE off the disc or a
    polygon of the GPU?  The answer is read where the game writes it -- the
    display list in RAM -- and then held against the picture:

      **the packet has to be on screen** -- its colours are compared with the
          pixels the frame shows inside its own rectangle, and a packet that
          misses is not this screen's.  The bands hold the previous screen's
          list as well (its rows are 9 pixels apart where this screen's are
          12), and geometry alone cannot tell the two apart;
      **the control** -- the same slot loaded twice has to give the same
          furniture, or the reading is the emulator's mood.

    `--write` leaves `work/looks-scenery/slotN.json` for the window to draw
    from, the way `--camera` leaves the camera.
    """
    import confront
    import screen

    ready = preflight()
    table = screen.load()
    display = table["display"]
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, SLOTS[slot]))
            found, pages, sprites = _scenery_of(game, slot, table, display,
                                                confront, screen)
            again, _pages, sprites_again = _scenery_of(
                game, slot, table, display, confront, screen)
            if [one["points"] for one in found] != [one["points"]
                                                    for one in again]:
                problems.append("slot %d: the furniture read twice is not the "
                                "same, so nothing below is a measurement"
                                % slot)
                continue
            if sprites != sprites_again:
                problems.append("slot %d: the sprites read twice are not the "
                                "same, so nothing below is a measurement"
                                % slot)
                continue
            print("    control: the screen loaded twice draws the same %d "
                  "packet(s) and the same %d sprite(s)"
                  % (len(found), len(sprites)))
            _say_scenery(found, table)
            _say_pages(pages, table)
            problems += ["slot %d: %s" % (slot, line) for line in
                         _say_sprites(game, sprites, ready["image"])]
            _say_provenance(provenance_map(game, display, confront, screen),
                            table, display)
            samples = _static_samples(game, sprites, display, ready["image"],
                                      confront, screen)
            _say_static_samples(sprites, samples)
            arrows, arrow_problems = _arrow_samples(game, slot, display,
                                                    ready["image"], confront,
                                                    screen)
            problems += ["slot %d: %s" % (slot, line)
                         for line in arrow_problems]
            if write:
                print("    wrote %s"
                      % write_scenery(slot, found, display, sprites, samples,
                                      arrows))
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --scenery: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


GPU_LIST_STOPS = 6
"""Stops at `layout.GPU_LIST_SUBMIT` read before the frame's lists are called
seen.  Measured: three per frame -- a one-node list twice and the ordering
table once -- so six covers two frames, and the table of the SECOND is the one
walked, after the screen has settled."""

GPU_LIST_LIMIT = 20 * 1000  # not-an-address: a count of nodes
"""Nodes a walk may take before a list that does not end is refused."""

POLYLINE_END = 0x55555555  # not-an-address: the GPU's own polyline terminator

_FURNITURE_LINES = (("48", False), ("4A", True))
POLYLINE_CODES = {int(code, 16): semi for code, semi in _FURNITURE_LINES}
"""Monochrome polylines, and whether each is semi-transparent: the border
around the panel is four of them."""


_DRAW_MODE = ("E1", "E2", "E3", "E4", "E5", "E6")
DRAW_MODE_CODES = {int(code, 16) for code in _DRAW_MODE}
DRAW_MODE_SET = int("E1", 16)
DRAW_MODE_BITS = (1 << 9) - 1
"""The GPU's draw-mode commands, and the nine bits of the texture page word:
page x, page y, the blend of semi-transparent drawing, and the colour depth."""

BLEND_SHIFT = 5
"""Where the blend sits in the page word: two bits, 0 to 3 -- half and half,
back plus front, back minus front, back plus a quarter of front."""

_PAGE_WORD = (("24", 4), ("25", 4), ("26", 4), ("27", 4), ("2C", 4),
              ("2D", 4), ("2E", 4), ("2F", 4), ("34", 5), ("35", 5),
              ("36", 5), ("37", 5), ("3C", 5), ("3D", 5), ("3E", 5),
              ("3F", 5))
PAGE_WORD = {int(code, 16): index for code, index in _PAGE_WORD}
"""Textured polygons, by the index of the word whose upper half is the page:
drawing one sets the page -- and the blend -- as an E1 would."""


_COMMAND_WORDS = (("00", 1), ("02", 3), ("80", 4), ("C0", 3))
COMMAND_WORDS = {int(code, 16): words for code, words in _COMMAND_WORDS}
"""The fixed-length GP0 commands that are not polygons, lines or rectangles:
no-op, fill, VRAM copy, VRAM read.  The draw-mode ones are a word each."""

POLYLINE_MASK = 0xF000F000  # not-an-address: the bits a polyline end is tested on
POLYLINE_MARK = 0x50005000  # not-an-address: and what they have to read


def command_words(words, at):
    """How many words the GP0 command at *words[at]* takes, itself included.

    The length is in the code's bits, the way the GPU reads it: a polygon has
    three or four vertices, each one word, plus a texel word if textured and a
    colour word per vertex after the first if gouraud; a rectangle is a corner,
    a texel word if textured and a size word if its size is not fixed; a
    polyline runs to its terminator.  A code this does not know takes the rest
    of the node, which is the honest answer when the node is not understood.
    """
    code = words[at] >> 24
    rest = len(words) - at
    if code in COMMAND_WORDS:
        return min(rest, COMMAND_WORDS[code])
    if code in DRAW_MODE_CODES:
        return 1
    family = code >> 5
    if family == 1:
        corners = 4 if code & 8 else 3
        per = 2 if code & 4 else 1
        return min(rest, 1 + corners * per + (corners - 1 if code & 16 else 0))
    if family == 2:
        if code & 8:
            for end in range(at + 1, len(words)):
                if words[end] & POLYLINE_MASK == POLYLINE_MARK:
                    return end - at + 1
            return rest
        return min(rest, 3 + (1 if code & 16 else 0))
    if family == 3:
        size = (code >> 3) & 3
        return min(rest, 2 + (1 if code & 4 else 0) + (0 if size else 1))
    return rest


def commands_of(nodes):
    """Every GP0 command of a walked list, in order, each as its word list.

    A node is not a command: libgs packs a sprite behind the E1 that sets its
    page in one node, so reading a node by its first word sees a draw-mode
    change and nothing else.  That is how every sprite of this screen -- the
    text, the plate, the arrows -- stayed out of the first four readings.
    """
    out = []
    for _at, words in nodes:
        at = 0
        while at < len(words):
            size = command_words(words, at)
            out.append(words[at:at + size])
            at += size
    return out


def sprites_of(commands):
    """The textured rectangles of a list, with the page each is cut from.

    Each as `{"point", "size", "uv", "clut", "page", "bits", "colour", "raw",
    "semi", "blend"}`: screen pixels, the texel corner, the CLUT and page in
    VRAM coordinates, and the page's colour depth.  The page and blend are the
    draw mode in force -- the last E1, or the last textured polygon, before it.
    """
    out, mode = [], 0
    for words in commands:
        code = words[0] >> 24
        if code == DRAW_MODE_SET:
            mode = words[0] & DRAW_MODE_BITS
            continue
        if code in PAGE_WORD and len(words) > PAGE_WORD[code]:
            mode = (words[PAGE_WORD[code]] >> 16) & DRAW_MODE_BITS
            continue
        if code not in SPRITE_CODES:
            continue
        _words, fixed = SPRITE_CODES[code]
        x, y = _signed_vertex(words[1])
        if fixed is None:
            size = (words[3] & 0xFFFF, words[3] >> 16)  # not-an-address: two halves
        else:
            size = (fixed, fixed)
        page = page_vram(mode)
        out.append({"point": (x + SCENERY_CENTRE[0], y + SCENERY_CENTRE[1]),
                    "size": size,
                    "uv": (words[2] & 0xFF, (words[2] >> 8) & 0xFF),  # not-an-address: two bytes
                    "clut": clut_vram(words[2] >> 16),
                    "page": page[:2], "bits": page[2],
                    "colour": _packet_colour(words[0]),
                    "raw": bool(code & 1), "semi": bool(code & 2),
                    "blend": (mode >> BLEND_SHIFT) & 3})
    return out


def gpu_list_heads(game):
    """The heads the frame submits to the GPU, in the order it submits them."""
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.GPU_LIST_SUBMIT))
    heads = []
    try:
        for _ in range(GPU_LIST_STOPS):
            client.call("continue")
            if not _wait_for_hit(game, WATCH_SECONDS):
                raise OracleError("%s never ran, so no list reached the GPU"
                                  % who_writes.hx(layout.GPU_LIST_SUBMIT))
            registers = client.call("read_registers", group="gpr")
            heads.append(who_writes.register_value(registers,
                                                   layout.GPU_LIST_HEAD))
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    return heads


def walk_gpu_list(ram, head):
    """[(address, [packet words])] of one GPU list, in drawing order.

    *ram* is all of main memory from `RAM_BASE`.  A node is a link word -- its
    top byte the packet's length, the rest the next node -- followed by that
    many words; nodes of length zero are the ordering table's own empty slots
    and are walked through.
    """
    mask = OT_POINTER
    out, seen, at = [], set(), head
    while True:
        if at in seen or len(seen) > GPU_LIST_LIMIT:
            raise OracleError("the list from %#x does not end within %d "
                              "nodes" % (head, GPU_LIST_LIMIT))
        seen.add(at)
        offset = (at & mask) - (RAM_BASE & mask)
        link = struct.unpack_from("<I", ram, offset)[0]
        length = link >> 24
        if length:
            out.append((at, list(struct.unpack_from("<%dI" % length, ram,
                                                    offset + 4))))
        nxt = link & mask
        if nxt == mask:
            return out
        at = (RAM_BASE & ~mask) | nxt


def furniture_of(nodes):
    """The untextured packets of a list: quads, gradients and polylines.

    What the screen's furniture is made of, in the order it is drawn, each as
    `{"points", "colours", "gradient", "semi", "line"}` in screen pixels.
    Textured packets are the figure and are left to `scenery_pages`.
    """
    out, mode = [], None
    for words in commands_of(nodes):
        code = words[0] >> 24
        if code in DRAW_MODE_CODES:
            # Each word of a draw-mode packet is a command of its own; only
            # the one that sets the texture page carries the blend.
            for one in words:
                if one >> 24 == DRAW_MODE_SET:
                    mode = one & DRAW_MODE_BITS
            continue
        if code in PAGE_WORD:
            mode = (words[PAGE_WORD[code]] >> 16) & DRAW_MODE_BITS
            continue
        if code in SCENERY_QUADS:
            _words, gradient, corners = SCENERY_QUADS[code]
            if gradient:
                colours = [_packet_colour(words[2 * i]) for i in range(corners)]
                points = [_signed_vertex(words[2 * i + 1])
                          for i in range(corners)]
            else:
                colours = [_packet_colour(words[0])] * corners
                points = [_signed_vertex(words[1 + i]) for i in range(corners)]
            semi = bool(code & 2)
            line = False
        elif code in POLYLINE_CODES:
            points = [_signed_vertex(one) for one in words[1:]
                      if one != POLYLINE_END]
            colours = [_packet_colour(words[0])] * len(points)
            gradient, semi, line = False, POLYLINE_CODES[code], True
        else:
            continue
        out.append({"points": [(x + SCENERY_CENTRE[0], y + SCENERY_CENTRE[1])
                               for x, y in points],
                    "colours": colours, "gradient": gradient,
                    "semi": semi, "line": line,
                    "blend": (None if not semi or mode is None
                              else (mode >> BLEND_SHIFT) & 3)})
    return out


def _scenery_of(game, slot, table, display, confront, screen):
    """(furniture, pages) of the list one load of *slot* hands the GPU.

    Walked from the head the game submits (`layout.GPU_LIST_SUBMIT`), not
    swept out of memory: the list says which packets this frame DRAWS and in
    which order, which a sweep of RAM cannot, and it carries the
    semi-transparent ones -- the title band is three -- that no colour test
    against the frame can find, because the frame shows their blend.
    """
    restore_state(slot, verbose=False)
    game.load_looks(slot, label="scenery-%d" % slot)
    game.step(SCENERY_SETTLE)
    heads = gpu_list_heads(game)
    first, size, step = layout.SCENERY_SWEEP
    ram = b"".join(game.read_ram(base, step, os.path.join(
        game.out_dir, "scenery-%08x.bin" % base))
        for base in range(first, first + size, step))
    nodes = []
    for head in dict.fromkeys(heads[len(heads) // 2:]):
        nodes += walk_gpu_list(ram, head)
    # The walked commands laid back out one per node, so the page reader that
    # scans a band reads exactly this frame's list and nothing stale.
    commands = commands_of(nodes)
    pages = scenery_pages(b"".join(
        struct.pack("<I", len(words) << 24) +
        struct.pack("<%dI" % len(words), *words) for words in commands),
        display)
    furniture = [one for one in furniture_of(nodes)
                 if _inside_screen(one["points"], display)]
    sprites = [one for one in sprites_of(commands)
               if _inside_screen([one["point"],
                                  (one["point"][0] + one["size"][0],
                                   one["point"][1] + one["size"][1])],
                                 display)]
    return furniture, pages, sprites


def _inside_screen(points, display):
    """Any part of the packet on screen -- the background runs off the edges."""
    xs = [x for x, _y in points]
    ys = [y for _x, y in points]
    return (max(xs) >= 0 and min(xs) <= display[0]
            and max(ys) >= 0 and min(ys) <= display[1])


def _say_pages(pages, table):
    """Print the textured packets grouped by the VRAM page they sample.

    What they answer for section 10.3 (o) is the other half of the question:
    everything that is NOT one of the flat rectangles above is cut from a page
    in VRAM, and this says which page, how many packets, and whether
    `DAT2D.BIN` -- the only 2D container this cycle reads -- holds it.
    """
    import atlas
    import iso_source
    import texture

    ready = preflight()
    with iso_source.open_disc(ready["image"]) as disc:
        records = texture.images(disc.read(layout.DAT2D))
    print("    the textured packets by page, and what holds that page:")
    for (page, clut), (count, box) in sorted(pages.items(),
                                             key=lambda one: -one[1][0]):
        cx, cy = clut_vram(clut)
        x, y, bits = page_vram(page)
        held = atlas.image_at(records, x, y)
        print("        page %04x (%3d,%3d) %2d-bit, clut (%3d,%3d): %3d "
              "packet(s) over (%3d,%3d)-(%3d,%3d); %s"
              % (page, x, y, bits, cx, cy, count, box[0], box[1], box[2],
                 box[3], "in DAT2D.BIN" if held else "in no DAT2D record"))


def _gpu_name(code):
    """The name of a GPU command code, for a report line."""
    return GPU_COMMANDS.get(code, ("%#04x" % code,))[0]


SCENERY_SETTLE = 8
"""Frames let run after the state loads, before the band and the frame are
read together.  The screen is static; this is for the load itself to finish."""


def _say_scenery(found, table):
    """Print the furniture grouped by the region of the screen it lands in."""
    regions = {name: box for name, box in
               ((one, table["regions"][one]["native"])
                for one in table["regions"])}
    groups = {}
    for node in found:
        xs = [x for x, _y in node["points"]]
        ys = [y for _x, y in node["points"]]
        box = (min(xs), min(ys), max(xs), max(ys))
        where = "elsewhere"
        for name, region in regions.items():
            if (box[0] >= region[0] - 1 and box[1] >= region[1] - 1
                    and box[2] <= region[2] + 1 and box[3] <= region[3] + 1):
                where = name
                break
        groups.setdefault(where, []).append((box, node))
    for where in sorted(groups):
        items = groups[where]
        lines = [one for _box, one in items if one["line"]]
        grads = [one for _box, one in items if one["gradient"]]
        semis = [one for _box, one in items if one["semi"]]
        print("    %-10s %3d packet(s): %d gradient, %d line, %d "
              "semi-transparent"
              % (where, len(items), len(grads), len(lines), len(semis)))
        for box, node in items[:14]:
            colours = node["colours"]
            kind = ("line" if node["line"] else
                    "gradient" if node["gradient"] else "flat")
            print("        (%4d,%4d)-(%4d,%4d) %-8s%s %s%s"
                  % (box[0], box[1], box[2], box[3], kind,
                     " semi%s" % node["blend"] if node["semi"] else "      ",
                     colours[0],
                     " -> %s" % (colours[-1],) if node["gradient"] else ""))
        if len(items) > 14:
            print("        ... and %d more" % (len(items) - 14))


SPRITE_FILES = ("EDT_2D", "DAT2D")
"""The containers a sprite's texels are looked for in, by `layout` name.

`EDT_2D.BIN` holds the screen's own art -- the font the text is cut from --
and `DAT2D.BIN` the rest; both were found by decoding every record of every
2D container on the disc against the VRAM of LOOKS SET (2026-09-21)."""

SPRITE_CONTROL_SHIFT = 3
"""Rows the control reads VRAM off by.

The same comparison against VRAM three rows lower has to disagree somewhere,
or equal would not have meant anything: a page of zeros matches a page of
zeros.  Three and not one, because a glyph's top and bottom rows are blank."""

COLOUR_BITS = (1 << 15) - 1
"""The fifteen bits of a halfword a VRAM read survives: the fork hands VRAM
back as a PNG, and the top bit -- the mask bit, or the high bit of a 4-bit
page's fourth texel -- does not make the trip."""

TEXELS_PER_HALFWORD = {4: 4, 8: 2, 16: 1}
"""How many texels one VRAM halfword holds, by the page's colour depth."""


def _halfword(pixel):
    """One (r, g, b) of a VRAM read back as the halfword's low 15 bits."""
    r, g, b = pixel[:3]
    return (r >> 3) | ((g >> 3) << 5) | ((b >> 3) << 10)


def sprite_texels(sprite):
    """The VRAM halfwords one sprite samples, as a set of (x, y)."""
    per = TEXELS_PER_HALFWORD[sprite["bits"]]
    (px, py), (u, v), (w, h) = sprite["page"], sprite["uv"], sprite["size"]
    return {(px + t // per, py + row) for t in range(u, u + w)
            for row in range(v, v + h)}


def _disc_halfwords(disc):
    """({(x, y): halfword}, {(x, y): file}, {file: images}) of `SPRITE_FILES`.

    Read through the guard off the Japanese disc.  Where two records cover a
    halfword the first file in `SPRITE_FILES` wins, which never happens on this
    disc: the two files hold disjoint parts of VRAM.
    """
    import lzss
    import texture

    held, owner, counts = {}, {}, {}
    for name in SPRITE_FILES:
        data = disc.read(getattr(layout, name))
        counts[name] = len(texture.images(data))
        for record in texture.images(data):
            plain, _used = lzss.decompress(data, record.offset)
            for row in range(record.h):
                for col in range(record.w):
                    at = 2 * (row * record.w + col)
                    key = (record.x + col, record.y + row)
                    if key in held or at + 1 >= len(plain):
                        continue
                    held[key] = (plain[at] | plain[at + 1] << 8) & COLOUR_BITS
                    owner[key] = name
    return held, owner, counts


def _clut_from_disc(disc, x, y, colours):
    """The CLUT's halfwords (low 15 bits) from DAT2D.BIN's palettes, or None."""
    import texture

    data = disc.read(layout.DAT2D)
    try:
        record, first = texture.window_for(texture.palettes(data), x, y,
                                           colours)
    except texture.NoPalette:
        return None
    at = record.offset + 2 * first
    return [struct.unpack_from("<H", data, at + 2 * i)[0] & COLOUR_BITS
            for i in range(colours)]


def _vram_halfwords(game, keys, below=0):
    """{(x, y): halfword} of VRAM over the box of *keys*, *below* rows more."""
    xs = [x for x, _y in keys]
    ys = [y for _x, y in keys]
    x0, y0 = min(xs), min(ys)
    rows = vram_region(game, x0, y0, max(xs) - x0 + 1,
                       max(ys) - y0 + 1 + below)
    return {(x0 + col, y0 + row): _halfword(pixel)
            for row, line in enumerate(rows) for col, pixel in enumerate(line)}


def _say_sprites(game, sprites, image):
    """Print the sprites by page and hold their texels against the disc.

    What section 10.3 (o) asks of the text, the plate and the arrows: which
    image each is cut from.  Every group's sampled halfwords are decoded off
    the disc and compared with what VRAM holds while the screen is up, with a
    control read a few rows off that has to disagree -- over all the groups,
    since one flat bar reads the same shifted.  Returns the problems: texels
    held on the disc that differ from VRAM, a CLUT that differs, a control
    that cannot tell anywhere.  Texels held by NO image are a finding, not a
    problem -- the game may write them at run time.
    """
    import iso_source

    groups = {}
    for one in sprites:
        key = (one["page"], one["bits"], one["clut"])
        groups.setdefault(key, []).append(one)
    problems, compared, told = [], 0, 0
    with iso_source.open_disc(image) as disc:
        held, owner, counts = _disc_halfwords(disc)
        print("    the sprites by page, and where their texels come from (%s):"
              % ", ".join("%s.BIN %d image(s)" % (name, counts[name])
                          for name in SPRITE_FILES))
        for (page, bits, clut), items in sorted(groups.items(),
                                                key=lambda one: -len(one[1])):
            xs = [one["point"][0] for one in items]
            ys = [one["point"][1] for one in items]
            box = (min(xs), min(ys),
                   max(one["point"][0] + one["size"][0] for one in items),
                   max(one["point"][1] + one["size"][1] for one in items))
            keys = set()
            for one in items:
                keys |= sprite_texels(one)
            vram = _vram_halfwords(game, keys, SPRITE_CONTROL_SHIFT)
            mine = sorted(key for key in keys if key in held)
            files = sorted({owner[key] for key in mine})
            same = sum(1 for key in mine if held[key] == vram[key])
            control = sum(1 for (x, y) in mine
                          if held[(x, y)] == vram[(x, y + SPRITE_CONTROL_SHIFT)])
            print("        page (%3d,%3d) %2d-bit, clut (%3d,%3d): %3d "
                  "sprite(s) over (%3d,%3d)-(%3d,%3d)"
                  % (page[0], page[1], bits, clut[0], clut[1], len(items),
                     box[0], box[1], box[2], box[3]))
            if not mine:
                print("            texels: %d halfword(s), held by no image on "
                      "the disc" % len(keys))
            else:
                print("            texels: %d of %d halfword(s) in %s, %d of "
                      "them equal to VRAM; control %d rows down: %d equal"
                      % (len(mine), len(keys), " + ".join(
                          "%s.BIN" % name for name in files), same,
                         SPRITE_CONTROL_SHIFT, control))
                if same != len(mine):
                    problems.append("page (%d,%d): %d texel(s) on the disc "
                                    "differ from VRAM"
                                    % (page[0], page[1], len(mine) - same))
                if control == len(mine):
                    # A flat image reads the same shifted; it is the whole
                    # comparison that has to be able to tell, not each group.
                    print("            the control cannot tell here: the "
                          "texels are flat")
                compared += len(mine)
                told += len(mine) - control
            colours = 1 << bits if bits < 16 else 0
            if not colours:
                continue
            want = _clut_from_disc(disc, clut[0], clut[1], colours)
            got = [vram_halfword for vram_halfword in
                   (_halfword(pixel) for pixel in
                    vram_region(game, clut[0], clut[1], colours, 1)[0])]
            if want is None:
                print("            clut: no palette of DAT2D.BIN covers it")
                continue
            equal = sum(1 for a, b in zip(want, got) if a == b)
            print("            clut: DAT2D.BIN, %d of %d entries equal to VRAM"
                  % (equal, colours))
            if equal != colours:
                problems.append("clut (%d,%d): %d entr(ies) of DAT2D.BIN "
                                "differ from VRAM"
                                % (clut[0], clut[1], colours - equal))
    print("    control: %d of %d compared texel(s) differ %d rows off"
          % (told, compared, SPRITE_CONTROL_SHIFT))
    if compared and not told:
        problems.append("the control rows read the same as the disc "
                        "everywhere, so equal says nothing")
    return problems


STATIC_SAMPLES = 32
"""Pixels kept per static sprite, spread evenly over its opaque texels."""


def _static_samples(game, sprites, display, image, confront, screen):
    """{sprite index: [[x, y, [r, g, b]], ...]} for the static sprites.

    What `ui_check.py` holds the window's sprites to, and why it is written by
    THIS tool: the colour of each sample is the game's, read off the frame
    buffer with the CPU stopped, not what `sprites.py` decodes -- a judge that
    asked the code under test what the answer is would agree with it however
    wrong it was.  The disc says only WHERE to look: a texel whose CLUT entry
    is transparent shows the furniture, and a pixel a later sprite covers
    shows that one, so neither is a sample of this sprite.
    """
    import iso_source
    import sprites as art_module

    frame = confront.still_frame(game, display, sys.modules[__name__], screen)
    with iso_source.open_disc(image) as disc:
        art = art_module.Art(art_module.containers_of(disc))
    boxes = [(one["point"][0], one["point"][1],
              one["point"][0] + one["size"][0], one["point"][1] + one["size"][1])
             for one in sprites]
    out = {}
    for index, one in enumerate(sprites):
        if art_module.group_of(one) is None:
            continue
        rgba = art.image(one)
        width, height = one["size"]
        spots = []
        for row in range(height):
            for col in range(width):
                if not rgba[4 * (row * width + col) + 3]:
                    continue
                x, y = one["point"][0] + col, one["point"][1] + row
                if not (0 <= x < display[0] and 0 <= y < display[1]):
                    continue
                if any(box[0] <= x < box[2] and box[1] <= y < box[3]
                       for box in boxes[index + 1:]):
                    continue
                spots.append((x, y))
        step = max(1, len(spots) // STATIC_SAMPLES)
        out[index] = [[x, y, list(frame[y][x][:3])]
                      for x, y in spots[::step][:STATIC_SAMPLES]]
    return out


def _say_static_samples(sprites, samples):
    """Print how many static sprites gave a sample, and name those that gave none.

    The count is of the sprites that HAVE samples, not of the static sprites
    found (CORR-LOOKS-069): the bar is transparent over its whole cut
    (armadilha 91), so it is static and gives no pixel to judge.
    """
    import sprites as art_module

    sampled = [index for index, one in samples.items() if one]
    empty = [index for index, one in samples.items() if not one]
    print("    the static sprites sampled: %d pixel(s) of %d sprite(s), "
          "each the colour the game's frame shows there"
          % (sum(len(one) for one in samples.values()), len(sampled)))
    for index in empty:
        one = sprites[index]
        print("    not sampled: the %s at %s, %s -- no opaque texel on screen"
              % (art_module.group_of(one), one["point"], one["size"]))


ARROW_WALKS = ((), ("Up",))
"""The presses after a load that put each arrow on screen: the load leaves the
cursor on NAT with the right arrow beside its value, and one `Up` takes it to
DEFAUL, whose value shows the left arrow alone (`screen.json`)."""


def _arrow_samples(game, slot, display, image, confront, screen):
    """`(arrows, problems)`: the arrows each of `ARROW_WALKS` shows, sampled.

    What `ui_check.py` holds the window's ARROWS to (CORR-LOOKS-068), written
    by this tool for the reason `_static_samples` gives: the colour of each
    sample is the game's frame, not what `sprites.py` decodes.  Each entry is
    `{"keys", "side", "point", "uv", "clut", "colour", "samples"}`, with the
    uv, the CLUT and the colour the GAME's list carries.  The disc says only
    WHERE to look -- the opaque texels of the sprite cut with the game's own
    uv and CLUT, never `sprites.ARROW_CLUT`.

    The colour is the list's, and it is not the frame's to the unit: the arrow
    pulses a few steps a frame, and the list read is the frame being built
    (measured 2026-09-21: a list colour of 96 over a frame of 24/19 in five
    bits, which is 100).  The judge allows for it; nothing here pretends.

    The control is the same walk twice: the same arrows, at the same points,
    from the same uv and CLUT -- the colour is left out, because it pulses.
    """
    import iso_source
    import sprites as art_module

    with iso_source.open_disc(image) as disc:
        art = art_module.Art(art_module.containers_of(disc))
    out, problems, sides = [], [], set()
    for keys in ARROW_WALKS:
        seen = []
        for _attempt in range(2):
            restore_state(slot, verbose=False)
            game.load_looks(slot, label="arrows-%d" % slot)
            for button in keys:
                tap(game, button)
            listed = [one for one in sprites_of(frame_commands(game))
                      if tuple(one["page"]) == layout.ARROW_PAGE]
            frame = confront.still_frame(game, display,
                                         sys.modules[__name__], screen)
            seen.append((listed, frame))
        shape = [[(tuple(one["point"]), tuple(one["uv"]), tuple(one["clut"]))
                  for one in listed] for listed, _frame in seen]
        if shape[0] != shape[1]:
            problems.append("the arrows after %s read twice are not the same "
                            "(%r, then %r), so nothing below is a measurement"
                            % (",".join(keys) or "the load", shape[0], shape[1]))
            continue
        listed, frame = seen[0]
        by_uv = {tuple(uv): side for side, uv in art_module.ARROWS.items()}
        for one in listed:
            side = by_uv.get(tuple(one["uv"]))
            if side is None:
                problems.append("a sprite on the arrows' page at %r samples uv "
                                "%r, which is neither arrow"
                                % (one["point"], one["uv"]))
                continue
            rgba = art.image(dict(one, colour=[art_module.NEUTRAL] * 3))
            width, height = one["size"]
            spots = []
            for row in range(height):
                for col in range(width):
                    if not rgba[4 * (row * width + col) + 3]:
                        continue
                    x, y = one["point"][0] + col, one["point"][1] + row
                    if 0 <= x < display[0] and 0 <= y < display[1]:
                        spots.append([x, y, list(frame[y][x][:3])])
            sides.add(side)
            out.append({"keys": list(keys), "side": side,
                        "point": list(one["point"]), "uv": list(one["uv"]),
                        "clut": list(one["clut"]),
                        "colour": list(one["colour"]), "samples": spots})
            print("    arrows after %s: %s at %r, uv %r, CLUT %r, colour %r; "
                  "%d opaque texel(s) sampled"
                  % (",".join(keys) or "the load",
                     {"left": "<", "right": ">"}[side], tuple(one["point"]),
                     tuple(one["uv"]), tuple(one["clut"]),
                     tuple(one["colour"]), len(spots)))
            if tuple(one["clut"]) != tuple(art_module.ARROW_CLUT):
                problems.append("the %s arrow at %r is drawn from CLUT %r, and "
                                "the window cuts it from sprites.ARROW_CLUT %r"
                                % (side, tuple(one["point"]),
                                   tuple(one["clut"]),
                                   tuple(art_module.ARROW_CLUT)))
    missing = sorted(set(art_module.ARROWS) - sides)
    if missing:
        problems.append("the walks %r showed no %s arrow, so its pixels are "
                        "not sampled" % (ARROW_WALKS, " and ".join(missing)))
    print("    control: each walk read twice shows the same arrows from the "
          "same uv and CLUT" if not problems else
          "    the arrows: %d problem(s)" % len(problems))
    return out, problems


def write_scenery(slot, found, display, sprites=(), samples=None, arrows=None):
    """One JSON per slot, in `work/looks-scenery/`."""
    import json

    os.makedirs(SCENERY_DIR, exist_ok=True)
    path = os.path.join(SCENERY_DIR, "slot%d.json" % slot)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"slot": slot, "display": list(display),
                   "centre": list(SCENERY_CENTRE),
                   "packets": [{"points": one["points"],
                                "colours": one["colours"],
                                "gradient": one["gradient"],
                                "semi": one["semi"],
                                "blend": one["blend"],
                                "line": one["line"]}
                               for one in found],
                   "sprites": [dict(one, point=list(one["point"]),
                                    size=list(one["size"]),
                                    uv=list(one["uv"]),
                                    clut=list(one["clut"]),
                                    page=list(one["page"]),
                                    colour=list(one["colour"]),
                                    **({"samples": samples[index]}
                                       if samples and index in samples
                                       else {}))
                               for index, one in enumerate(sprites)],
                   "arrows": list(arrows or [])},
                  handle, indent=1)
        handle.write("\n")
    return path


REPAINT_TILE = (32, 30)
"""The tile the repaint map is read at, in screen pixels.

Sixteen across and eight down over a 512x240 screen.  Small enough that the
panel, the rows and the help box land in tiles of their own; big enough that
one glyph's worth of ink does not decide a tile.
"""

REPAINT_COLOUR = ((1 << 15) - 1) ^ (0x1F << 5)  # not-an-address: a BGR555 colour
"""The halfword written over the screen: magenta, full red and blue, no green.

A colour the screen does not hold anywhere -- the furniture is teal, dark blue
and black -- so "came back" and "stayed" are the same question as "is this
pixel magenta".
"""

REPAINT_FRAMES = 8
"""Frames let run after the damage, before the buffers are read again.

Both buffers are damaged and the console flips between them, so a rectangle
the game redraws every frame is back in both within two flips; eight is four
times that.
"""

REPAINT_BACK = 0.98
"""How much of a tile has to come back before it is called redrawn."""


PROVENANCE_TILE = 16
"""The square the provenance map is read at, in screen pixels.

Sixteen: the side a PSX texture page is cut into and the side this screen's
glyphs are drawn at.  Smaller would find the blank corner of one page in every
other page.
"""

PROVENANCE_STRIDE = 8
"""How far apart the VRAM blocks the map searches are taken.

Half a tile, so a source that is not tile-aligned is still found.  Whole VRAM
at this stride is 8,128 blocks, which a dictionary swallows.
"""

PROVENANCE_PLAIN = 4
"""How many colours a tile may hold before it counts as picture, not fill.

A tile of the panel's gradient holds two or three; a tile of text or of the
title band holds a dozen.  Flat tiles are left out: a filled rectangle matches
every other rectangle of that colour in VRAM, and counting those as "found
elsewhere" would call the whole screen an image.
"""


def provenance_map(game, display, confront, screen):
    """Which tiles of the screen exist somewhere ELSE in VRAM.

    The question section 10.3 (o) asks about the title band, the plate and the
    shirt box, for which there is no packet in RAM to read: a rectangle whose
    pixels are also sitting in a page of VRAM was BLITTED from that page --
    it is an image -- and one that exists only in the frame buffer was drawn
    there.

    Flat tiles are skipped (`PROVENANCE_PLAIN`), because a rectangle of one
    colour is found everywhere and would answer "image" for the whole screen.
    """
    import atlas

    frame = confront.still_frame(game, display, oracle_module(), screen)
    path = os.path.join(game.out_dir, "vram-provenance.png")
    if os.path.exists(path):
        os.remove(path)
    game.client.call("dump_vram", path=path, format="png")
    width, height, rows = atlas.read_png(path)
    tile = PROVENANCE_TILE
    # Every block of VRAM OUTSIDE the two frame buffers, by its pixels.
    buffers = set()
    for origin in confront.BUFFERS:
        buffers.update(range(origin, origin + display[1]))
    blocks = {}
    for y in range(0, height - tile, PROVENANCE_STRIDE):
        if y in buffers or (y + tile - 1) in buffers:
            continue
        for x in range(0, width - tile, PROVENANCE_STRIDE):
            key = tuple(tuple(rows[y + dy][x + dx][:3]) for dy in range(tile)
                        for dx in range(tile))
            blocks.setdefault(key, (x, y))
    out = {}
    for ty in range(0, display[1] - tile + 1, tile):
        for tx in range(0, display[0] - tile + 1, tile):
            pixels = tuple(tuple(frame[ty + dy][tx + dx][:3])
                           for dy in range(tile) for dx in range(tile))
            colours = len(set(pixels))
            if colours <= PROVENANCE_PLAIN:
                out[(tx, ty)] = ("flat", colours, None)
                continue
            where = blocks.get(pixels)
            out[(tx, ty)] = ("image" if where else "drawn", colours, where)
    return out


def _say_provenance(found, table, display):
    """Print the provenance map, and what it says region by region."""
    tile = PROVENANCE_TILE
    mark = {"image": "I", "drawn": "d", "flat": "."}
    print("    where the pixels come from, %dx%d tiles -- I also in a VRAM "
          "page, d only in the frame buffer, . flat fill"
          % (display[0] // tile, display[1] // tile))
    for ty in range(0, display[1] - tile + 1, tile):
        print("        %3d  %s" % (ty, "".join(
            mark[found[(tx, ty)][0]]
            for tx in range(0, display[0] - tile + 1, tile))))
    sources = {}
    for (tx, ty), (kind, _colours, where) in sorted(found.items()):
        if kind == "image" and where:
            sources.setdefault(where[1] // 64 * 64, set()).add(where[0] // 64 * 64)
    for row in sorted(sources):
        print("        tiles found in VRAM rows %d..%d, page columns %s"
              % (row, row + 63, sorted(sources[row])))


def check_repaint(slots=(2, 1), verbose=True):
    """`--repaint [SLOT]`: which parts of the screen the game draws per frame.

    The other half of section 10.3 (o), and the one the display list cannot
    answer: `--scenery` finds the panel, the help box and the row stripes as
    polygons in the band and finds **nothing** for the title band, the plate,
    the shirt box or the text -- so either they are drawn by a path that
    leaves no list in main RAM, or they are painted once and left.

    This asks the console.  Both frame buffers are overwritten with a colour
    the screen does not use, the game is let run, and the buffers are read
    again: what comes back is redrawn every frame; what stays magenta was
    painted once.  The control is the same map twice.
    """
    import confront
    import screen

    ready = preflight()
    table = screen.load()
    width, height = table["display"]
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, SLOTS[slot]))
            first = _repaint_map(game, slot, width, height, confront, screen)
            again = _repaint_map(game, slot, width, height, confront, screen)
            if first != again:
                problems.append("slot %d: the repaint map read twice differs, "
                                "so it is not a measurement" % slot)
                continue
            print("    control: the map read twice is the same")
            _say_repaint(first, table, width, height)
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --repaint: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def _repaint_map(game, slot, width, height, confront, screen):
    """{tile: 'redrawn' | 'painted once' | 'part'} for one load of a slot."""
    restore_state(slot, verbose=False)
    game.load_looks(slot, label="repaint-%d" % slot)
    game.step(SCENERY_SETTLE)
    before = confront.still_frame(game, (width, height), oracle_module(),
                                  screen)
    path = os.path.join(game.out_dir, "magenta.bin")
    with open(path, "wb") as handle:
        handle.write(struct.pack("<H", REPAINT_COLOUR) * (width * height))
    for origin in confront.BUFFERS:
        game.client.call("write_vram_region", x=0, y=origin, width=width,
                         height=height, input_path=path, format="raw")
    game.step(REPAINT_FRAMES)
    after = confront.still_frame(game, (width, height), oracle_module(),
                                 screen)
    across, down = REPAINT_TILE
    out = {}
    for ty in range(0, height, down):
        for tx in range(0, width, across):
            same = total = 0
            for y in range(ty, min(ty + down, height)):
                for x in range(tx, min(tx + across, width)):
                    total += 1
                    same += tuple(after[y][x][:3]) == tuple(before[y][x][:3])
            share = same / float(total or 1)
            out[(tx, ty)] = ("redrawn" if share >= REPAINT_BACK
                             else "part" if share > 1 - REPAINT_BACK
                             else "painted once")
    return out


def _say_repaint(found, table, width, height):
    """Print the repaint map as the screen's own shape, and name the regions."""
    across, down = REPAINT_TILE
    mark = {"redrawn": "#", "part": "+", "painted once": "."}
    print("    the screen, %dx%d tiles of %dx%d -- # redrawn every frame, "
          "+ partly, . painted once"
          % (width // across, height // down, across, down))
    for ty in range(0, height, down):
        line = "".join(mark[found[(tx, ty)]]
                       for tx in range(0, width, across))
        print("        %3d  %s" % (ty, line))
    for name in sorted(table["regions"]):
        box = table["regions"][name]["native"]
        kinds = {}
        for (tx, ty), kind in found.items():
            if (tx + across > box[0] and tx <= box[2]
                    and ty + down > box[1] and ty <= box[3]):
                kinds[kind] = kinds.get(kind, 0) + 1
        print("        %-8s %s" % (name, ", ".join(
            "%d %s" % (n, kind) for kind, n in sorted(kinds.items()))))


PAGE_SIZE = (64, 256)
"""The width and height of one PSX texture page, in VRAM halfwords."""

PAGE_CANDIDATES = ((704, 0), (512, 256), (576, 256), (640, 256), (768, 0),
                   (832, 0))
"""The pages this screen is known or suspected to draw from.

The first is the font (`--scenery` reads it off the GPU at the glyph routine's
drawing pass), the second and third are the head's and the kit's
(LOOKS-TASK-30), and the rest are their neighbours -- a page nothing draws
from comes back with nothing changed, which is the control this list carries
inside it.
"""

PAGE_FRAMES = 6
"""Frames let run after a page is damaged, before the screen is read again."""


def check_pages(slots=(2, 1), verbose=True):
    """`--pages [SLOT]`: what on the screen is drawn from each VRAM page.

    The question section 10.3 (o) leaves open after `--scenery`: the title
    band, the plate, the shirt box and the arrows leave no packet in RAM, and
    their pixels are in no other page of VRAM either -- so are they images at
    all?  This asks the console directly.  One page of VRAM is overwritten
    with a colour the screen does not use, the game is let run, and the screen
    is compared with itself: **what changes is drawn from that page**.

    The control is in the list -- pages nothing samples have to come back with
    nothing changed -- and the state is reloaded between pages, so the damage
    of one is never read as the damage of the next.
    """
    import confront
    import screen

    ready = preflight()
    table = screen.load()
    display = table["display"]
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, SLOTS[slot]))
            quiet = []
            clean = _page_frame(game, slot, display, confront, screen)
            twice = _page_frame(game, slot, display, confront, screen)
            if [row[:] for row in clean] != [row[:] for row in twice]:
                problems.append("slot %d: two undamaged runs of the same "
                                "length differ, so the damage below cannot "
                                "be told from the walk" % slot)
                continue
            print("    control: two undamaged runs give the same screen")
            for page in PAGE_CANDIDATES:
                changed, boxes = _damage_page(game, slot, page, display,
                                              confront, screen, clean)
                if not changed:
                    quiet.append(page)
                    continue
                print("    page (%3d,%3d): %d tile(s) of the screen change, "
                      "over %s" % (page[0], page[1], changed,
                                   ", ".join(_name_boxes(boxes, table))))
            print("    and nothing on screen comes from %s -- the control "
                  "this list carries"
                  % (", ".join("(%d,%d)" % one for one in quiet) or "no page"))
            if not quiet:
                problems.append("slot %d: every page tried changed the "
                                "screen, so the damage is not local and the "
                                "attribution means nothing" % slot)
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --pages: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def _page_frame(game, slot, display, confront, screen, page=None):
    """The screen after `PAGE_FRAMES`, with one page damaged or with none.

    **Two runs from the same state, and not one run before and after.** The
    figure walks: a frame taken before the damage and one taken after differ
    in every tile the walk touched, which is how the first version of this
    reported the same 48 tiles for every page, including the ones nothing
    samples (measured 2026-09-21).
    """
    restore_state(slot, verbose=False)
    game.load_looks(slot, label="pages-%d" % slot)
    game.step(SCENERY_SETTLE)
    if page is not None:
        path = os.path.join(game.out_dir, "page-magenta.bin")
        with open(path, "wb") as handle:
            handle.write(struct.pack("<H", REPAINT_COLOUR)
                         * (PAGE_SIZE[0] * PAGE_SIZE[1]))
        game.client.call("write_vram_region", x=page[0], y=page[1],
                         width=PAGE_SIZE[0], height=PAGE_SIZE[1],
                         input_path=path, format="raw")
    game.step(PAGE_FRAMES)
    return confront.still_frame(game, display, oracle_module(), screen)


def _damage_page(game, slot, page, display, confront, screen, before=None):
    """(tiles changed, their boxes) after one VRAM page is overwritten."""
    if before is None:
        before = _page_frame(game, slot, display, confront, screen)
    after = _page_frame(game, slot, display, confront, screen, page)
    tile = PROVENANCE_TILE
    changed, boxes = 0, []
    for ty in range(0, display[1] - tile + 1, tile):
        for tx in range(0, display[0] - tile + 1, tile):
            for dy in range(tile):
                row_a, row_b = before[ty + dy], after[ty + dy]
                if any(tuple(row_a[tx + dx][:3]) != tuple(row_b[tx + dx][:3])
                       for dx in range(tile)):
                    changed += 1
                    boxes.append((tx, ty))
                    break
    return changed, boxes


def _name_boxes(boxes, table):
    """The regions of the screen a list of tiles falls in."""
    tile = PROVENANCE_TILE
    names = []
    for name in sorted(table["regions"]):
        box = table["regions"][name]["native"]
        if any(tx + tile > box[0] and tx <= box[2] and ty + tile > box[1]
               and ty <= box[3] for tx, ty in boxes):
            names.append(name)
    top = min(ty for _tx, ty in boxes)
    if top < min(table["regions"][one]["native"][1]
                 for one in table["regions"]):
        names.append("above them all (the title band)")
    return names or ["nowhere this cycle has named"]


def check_assembly(rows=None, slot=2, verbose=True):
    """What every value of a field does to the primitives it owns.

    The measurement LOOKS-TASK-14 is built on, and the reason it is a walk
    rather than one step: LOOKS-TASK-08 stepped HAIR ONCE and recorded "+0x20
    to v", which is true of the first step and says nothing about the
    thirty-second.  A field is walked end to end and every value it reaches is
    printed with the whole primitive beside it.

    What is watched is the section's **primitive block**, not one witness:
    which primitives a field moves is part of the answer, and picking the
    witness first would decide it in advance.
    """
    import iso_source
    import looks

    ready = preflight()
    rows = rows or tuple(ASSEMBLY_ROWS)
    with iso_source.open_disc(ready["image"]) as disc:
        discs = {name: disc.read(name) for name in layout.BASE}

    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        for row in rows:
            if row not in ASSEMBLY_ROWS:
                raise OracleError("%r is not a row this measures: %s"
                                  % (row, ", ".join(ASSEMBLY_ROWS)))
            name, index = ASSEMBLY_ROWS[row]
            base, length = section_address(ready["image"], name, index)
            path = os.path.join(game.out_dir, "prims.bin")

            def read(base=base, length=length, path=path):
                return game.read_ram(base, length, path)

            # Down to the bottom of the range FIRST, so that index 0 of what
            # comes back is the field's lowest value and not wherever the save
            # state happened to leave it.  An anchored table is the difference
            # between "these bands exist" and "band 0 is hair style A1".
            count = looks.BY_ROW[row].values
            game.load_looks(slot)
            game.select_row(row)
            started = steady(game, read)
            for _ in range(count):
                game.press("Left", expect_change=False)
            values = [steady(game, read)]
            for _ in range(count):
                game.press("Right", expect_change=False)
                values.append(steady(game, read))
            distinct = len({bytes(v) for v in values})
            print("  %s on slot %d: %d press(es) of Left then %d of Right; "
                  "%d distinct state(s) in %d value(s); the state the disc "
                  "holds is %s"
                  % (row, slot, count, count, distinct, len(values),
                     "number %d" % values.index(started)
                     if started in values else "NOT among them"))
            _say_primitives(row, name, index, values,
                            values.index(started) if started in values else -1,
                            discs[name])
    return 0


ASSEMBLY_ROWS = {
    "HAIR": (layout.MODEL, layout.HEAD_SECTION),
    "FACE": (layout.MODEL, layout.HEAD_SECTION),
    "H.COL": (layout.MODEL, layout.HEAD_SECTION),
    "H.F.COL.": (layout.MODEL, layout.HEAD_SECTION),
    "SKIN": (layout.MODEL, layout.HEAD_SECTION),
    "BOOTS": (layout.EDT_MOD, layout.BOOT_SECTIONS[0]),
}
"""Which section to watch while a row is walked.

One section each, and the section is the piece the field was already measured
to touch -- LOOKS-TASK-08 for the head, LOOKS-TASK-09 for the boots.  A field
that turned out to move something else would show up as a section that never
changes, which is a refusal this prints rather than hides.
"""


def _say_primitives(row, name, index, values, at, disc_data):
    """Print what changed, primitive by primitive, value by value."""
    scan = section.scan(disc_data, layout.GEOMETRY_START[name])
    prim_bytes = len(scan.sections[index].primitives) * section.PRIMITIVE_SIZE
    first = values[0]
    moved = set()
    vertices = 0
    for block in values[1:]:
        for i in range(0, prim_bytes, section.PRIMITIVE_SIZE):
            if block[i:i + section.PRIMITIVE_SIZE] != \
                    first[i:i + section.PRIMITIVE_SIZE]:
                moved.add(i // section.PRIMITIVE_SIZE)
        vertices = max(vertices, sum(
            1 for i in range(prim_bytes, len(first), section.VERTEX_SIZE)
            if block[i:i + section.VERTEX_SIZE]
            != first[i:i + section.VERTEX_SIZE]))
    if not moved and not vertices:
        print("      nothing in %s section %d moved -- this row does not own "
              "this section" % (name, index), flush=True)
        return
    print("      %s section %d: %d primitive(s) move: %s"
          % (name, index, len(moved), sorted(moved)))
    if vertices:
        print("      and up to %d vertex(es) move with them -- this row "
              "changes the MESH, not only what it samples" % vertices, flush=True)

    else:
        # Does the row SWAP a body in?  `MODEL.BIN` holds two runs of 32 head
        # sections, which is exactly what `hair_style` holds, so "the row picks
        # a section" is the obvious reading -- and an obvious reading is the
        # kind this cycle measures instead of believing.  The vertices answer
        # it: a swapped body brings another section's mesh with it, and not one
        # vertex moved across every value walked.
        print("      and NO vertex moves in any of the %d value(s): the mesh "
              "in this slot is the disc's throughout, so the row does not swap "
              "another section's body in" % len(values), flush=True)
    # One line per value, and the SHAPE of the change rather than every
    # primitive: what a field does to forty-two primitives at once is one fact,
    # and printing it forty-two times buries it.  The whole list is above.
    for step, block in enumerate(values):
        prims = [section.read_primitive(block, w * section.PRIMITIVE_SIZE)
                 for w in sorted(moved or {0})]
        cluts = sorted({p.clut for p in prims})
        pages = sorted({p.tpage for p in prims})
        us = sorted({u for p in prims for u, _v in p.texcoords})
        vs = sorted({v for p in prims for _u, v in p.texcoords})
        print("        %2d%s  clut %s  page %s  u %d..%d  v %d..%d"
              % (step, " <-- the disc" if step == at else "     ",
                 ", ".join("%#06x" % c for c in cluts),
                 ", ".join("%#06x" % p for p in pages),
                 us[0], us[-1], vs[0], vs[-1]))


BURST_SECONDS = 6
BURST_LIMIT = 64
"""How long one press's burst of writes is collected, and how many hits it may
hold.

The game rewrites a head in a burst of calls, not one, so the end of a press is
silence rather than a count -- and the limit is what stops a routine that turns
out to run every frame from becoming an infinite loop instead of a measurement.
"""


def check_writes(row="HAIR", slot=2, verbose=True):
    """Every hair quad the game writes at each value of a field, with the band.

    The instrument the other two commands were missing.  `--patched` compares
    the file against the disc, so a write that puts back the byte that is
    already there is **invisible** to it -- which is exactly what three of
    HAIR's 32 values did, and why `assembly.HAIR_MAP` has three empty rows.

    An **execute** breakpoint on `layout.HAIR_QUAD_STORE` sees the write
    itself: `a0` is the primitive being written and `a2` the band, so one hit
    names the section, the primitive index and the band together.  That also
    answers the other open half -- which primitives of a head take the band --
    for every section the row visits, and not only for the one whose pair
    LOOKS-TASK-08 named.
    """
    import looks
    import who_writes

    ready = preflight()
    count = looks.BY_ROW[row].values
    maps = model_maps(ready["image"])
    out = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        game.load_looks(slot)
        game.select_row(row)
        cell = row_value(ROWS.index(row))
        quiet = game.capture()
        drift = quiet.difference(game.capture(), pixels(quiet, cell))
        floor = max(VALUE_MOVED, drift * IDLE_MARGIN)
        for _ in range(count):
            game.press("Left", expect_change=False)
        before = game.capture()
        for step in range(1, count):
            hits = _burst(game, maps, press="Right")
            # **The press has to be proved, because it is made while the CPU
            # is free-running and stopping at a breakpoint.**  A press the
            # game never read would put every write after it under the wrong
            # label, which is worse than a gap.
            after = game.capture()
            moved = after.difference(before, pixels(after, cell)) > floor
            before = after
            out.append((step, moved, hits))
            print("      %-4s %s%s"
                  % (looks.BY_ROW[row].label(step), _say_burst(hits),
                     "" if moved else "   [the value cell did not move]"),
                  flush=True)
    landed = [one for one in out if one[1]]
    print("  %s on slot %d: %d of %d press(es) registered, and %d of those "
          "wrote a quad"
          % (row, slot, len(landed), len(out),
             sum(1 for one in landed if one[2])), flush=True)
    sections = sorted({where[1] for _s, _m, hits in out for _band, where in hits})
    print("      the sections it wrote: %s" % sections, flush=True)
    quads = {}
    for _s, _m, hits in out:
        for _band, where in hits:
            quads.setdefault(where[1], set()).add(where[2])
    for index in sorted(quads):
        print("      section %d: %s" % (index, ", ".join(sorted(quads[index]))),
              flush=True)
    return 0


def _burst(game, maps, press=None):
    """[(band, where)] for every write the game makes after one press.

    Collected until the writes stop, not counted: a head is rebuilt in a burst
    whose length is the game's business.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.HAIR_QUAD_STORE))
    hits = []
    try:
        client.call("continue")
        if press:
            client.call("press_button", button=press,
                        duration_frames=CONFIRM_FRAMES)
        for _ in range(BURST_LIMIT):
            if not _wait_for_hit(game, BURST_SECONDS):
                break
            registers = client.call("read_registers", group="gpr")
            target = who_writes.register_value(registers, "a0")
            value = who_writes.register_value(registers, "v1")
            if target is not None and value is not None:
                where = attribute(target, maps)
                if where:
                    hits.append(((value - BAND_TOP) // layout.ATLAS_BAND,
                                 where))
            client.call("continue")
    finally:
        try:
            client.call("breakpoint", action="clear")
        except Exception:  # noqa: BLE001
            pass
    return hits


def _say_burst(hits):
    """One press's writes, folded to one line."""
    if not hits:
        return "wrote nothing"
    folded = {}
    for band, where in hits:
        folded.setdefault((where[0], where[1]), []).append(
            (where[2], band))
    return "; ".join(
        "%s section %d: %s" % (name, index,
                               ", ".join("%s band %d" % (what, band)
                                         for what, band in sorted(set(parts))))
        for (name, index), parts in sorted(folded.items(), key=lambda kv: kv[0][1]))


def check_patched(row="HAIR", slot=2, starts=(), verbose=True):
    """Which sections of a model file differ from the DISC at every value.

    The walk this task was built on watched **one** section, the head, because
    that is the section LOOKS-TASK-08 saw move.  A field that stops writing
    there and starts writing somewhere else looks, through that window, exactly
    like a field that stopped doing anything -- and `MODEL.BIN` holds two runs
    of 32 head sections, so "somewhere else" has 31 candidates.

    So this reads the whole loaded file after every press and says which
    sections the live copy no longer matches.  A style that picks another
    section shows up as that section's index; a style that changes nothing in
    the file at all shows up as an empty line, which is also an answer.

    *starts* are tuples to put on the screen first, one walk each from a fresh
    `load_state`: a row whose effect depends on another row -- FACE on the head
    HAIR picked -- is measured on each of them and not only on the state's own
    A1 (CORR-LOOKS-048).  Every changed primitive is printed with the corners
    it was left with, because "section 25 changed" does not say which quads.
    """
    import confront
    import iso_source
    import looks

    ready = preflight()
    count = looks.BY_ROW[row].values
    for start in starts:
        looks.parse_tuple(start)
    with iso_source.open_disc(ready["image"]) as disc:
        data = disc.read(layout.MODEL)
    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    walks = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        path = os.path.join(game.out_dir, "model.bin")

        def read():
            return game.read_ram(layout.BASE[layout.MODEL], len(data), path)

        for start in starts or (None,):
            game.load_looks(slot)
            if start is None:
                game.select_row(row)
            else:
                confront.route(game, start, sys.modules[__name__])
                way, distance = confront.moves(ROWS, confront.SHOT_ROW, row)
                for _ in range(distance):
                    game.press(way, box=FOOTER, least=ROW_MOVED)
            before = steady(game, read)
            for _ in range(count):
                game.press("Left", expect_change=False)
            states = [steady(game, read)]
            for _ in range(count):
                game.press("Right", expect_change=False)
                states.append(steady(game, read))
            walks.append((start, before, states))

    for start, before, states in walks:
        print("  %s on slot %d%s: %d value(s); what CHANGED at each press, and "
              "what the live %s no longer matches on the disc"
              % (row, slot, "" if start is None else " from %s" % start,
                 len(states), layout.MODEL), flush=True)
        for step, live in enumerate(states):
            old = states[step - 1] if step else (data if start is None
                                                 else before)
            changed = _sections_touched(old, live, scan, data)
            against = _sections_touched(data, live, scan, data)
            print("      %2d  changed: %s   |   differs from the disc in: %s"
                  % (step,
                     ", ".join("section %d (%d byte(s), band(s) %s)"
                               % (index, many, bands)
                               for index, many, bands in changed) or "nothing",
                     ", ".join(str(index) for index, _c, _b in against)
                     or "nothing"), flush=True)
            for index, _many, _bands in changed:
                one = scan.sections[index]
                first = one.offset + section.HEADER_SIZE
                for at in range(len(one.primitives)):
                    offset = first + at * section.PRIMITIVE_SIZE
                    if old[offset:offset + section.PRIMITIVE_SIZE] ==                             live[offset:offset + section.PRIMITIVE_SIZE]:
                        continue
                    prim = section.read_primitive(live, offset)
                    print("            section %d primitive %d: clut 0x%04x, "
                          "(u, v) %s" % (index, at, prim.clut,
                                         list(prim.texcoords)), flush=True)
    return 0


COLOUR_SETTLE_FRAMES = 300
"""Frames between the two reads that must agree at each end of a colour walk.

Not SETTLE_FRAMES: walked press by press with reads 20 frames apart, SKIN on
section 24 came back with primitive 7 moved once and never again, and the
press past the end of the range still writing -- the rewrite of a head's CLUT
ids runs longer than two reads 20 frames apart can see (CORR-LOOKS-049)."""


def check_colour(row="SKIN", slot=2, starts=(), verbose=True):
    """Which primitives of each head a colour row moves, from its two ends.

    For each start tuple: the row walked to the bottom, then to the top, and at
    each end the loaded MODEL.BIN is read until two reads COLOUR_SETTLE_FRAMES
    apart agree.  A primitive belongs to the row where its CLUT id differs
    between the two ends.  Ends and not steps, because what a step reads can be
    a state the game is still in the middle of writing (trap 18).
    """
    import confront
    import iso_source
    import looks

    import assembly

    ready = preflight()
    count = looks.BY_ROW[row].values
    # FACE moves the `v` of its quads, and past E it draws another section:
    # its top end is E, and what differs is the texcoords (CORR-LOOKS-048).
    up = assembly.FACE_TWIN_FROM - 1 if row == "FACE" else count
    for start in starts:
        looks.parse_tuple(start)
    with iso_source.open_disc(ready["image"]) as disc:
        data = disc.read(layout.MODEL)
    scan = section.scan(data, layout.GEOMETRY_START[layout.MODEL])
    out = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        path = os.path.join(game.out_dir, "model.bin")

        def settled():
            first = game.read_ram(layout.BASE[layout.MODEL], len(data), path)
            for _ in range(SETTLE_TRIES):
                game.step(COLOUR_SETTLE_FRAMES)
                again = game.read_ram(layout.BASE[layout.MODEL], len(data),
                                      path)
                if again == first:
                    return again
                first = again
            raise OracleError("MODEL.BIN never settled at an end of %s" % row)

        for start in starts or (None,):
            game.load_looks(slot)
            if start is None:
                game.select_row(row)
            else:
                confront.route(game, start, sys.modules[__name__])
                way, distance = confront.moves(ROWS, confront.SHOT_ROW, row)
                for _ in range(distance):
                    game.press(way, box=FOOTER, least=ROW_MOVED)
            for _ in range(count):
                game.press("Left", expect_change=False)
            bottom = settled()
            for _ in range(up):
                game.press("Right", expect_change=False)
            top = settled()
            moved = {}
            for index, one in enumerate(scan.sections):
                first = one.offset + section.HEADER_SIZE
                for at in range(len(one.primitives)):
                    offset = first + at * section.PRIMITIVE_SIZE
                    low = section.read_primitive(bottom, offset)
                    high = section.read_primitive(top, offset)
                    if (low.clut, low.texcoords) != (high.clut,
                                                     high.texcoords):
                        moved.setdefault(index, []).append(
                            (at, low.clut, high.clut))
            out.append((start, moved))

    for start, moved in out:
        print("  %s on slot %d from %s: primitives whose CLUT id or texcoords "
              "differ between the two settled ends" % (row, slot, start),
              flush=True)
        if not moved:
            print("      nothing", flush=True)
        for index in sorted(moved):
            print("      section %d: %s" % (index, tuple(at for at, _l, _h
                                                     in moved[index])),
                  flush=True)
            print("          %s" % ", ".join("%d 0x%04x->0x%04x" % one
                                             for one in moved[index]),
                  flush=True)
    return 0


def _sections_touched(before, after, scan, disc_data):
    """[(section, bytes that differ, the bands its differing primitives sit in)].

    The band is `v // ATLAS_BAND` of every corner of every primitive that
    differs, read out of *after* -- which is what turns "this section was
    rewritten" into "this section was pointed at band 3 of the hair sheet".
    """
    out = []
    for index, one in enumerate(scan.sections):
        differ = [offset for offset in range(one.offset, one.end)
                  if before[offset] != after[offset]]
        if not differ:
            continue
        bands = set()
        first = one.offset + section.HEADER_SIZE
        for offset in differ:
            inner = offset - first
            if not 0 <= inner < len(one.primitives) * section.PRIMITIVE_SIZE:
                continue
            at = first + (inner // section.PRIMITIVE_SIZE)                 * section.PRIMITIVE_SIZE
            live = section.read_primitive(after, at)
            bands |= {v // layout.ATLAS_BAND for _u, v in live.texcoords}
        out.append((index, len(differ), sorted(bands)))
    return out


def check_hair(slot=2, verbose=True):
    """The anchor of the hair map, asked twice in one session.

    **First, whether the SCREEN moves at all where the section does not.**  The
    walk of LOOKS-TASK-14 pressed 32 times and read the file's section, and got
    three states out of it; what it never asserted is that the row's own value
    cell was moving under those presses.  A field whose value cell stops moving
    after three presses and a field whose value cell walks 32 values while the
    section holds still are different findings with the same section reading,
    and only one of them means the styles are somewhere else.

    **Then, who writes the window.**  A write watchpoint on the `v` byte of the
    first hair primitive, with the control before it -- the same watchpoint
    armed over free running with nothing pressed -- so that a hit is about the
    press.  What it buys is the instruction, the register it stores and where
    that register was loaded from, which is the table this task is missing.
    """
    import looks

    ready = preflight()
    row = "HAIR"
    count = looks.BY_ROW[row].values
    name, index = ASSEMBLY_ROWS[row]
    base, length = section_address(ready["image"], name, index)
    witness = texcoord_address(ready["image"], name, index,
                               layout.HAIR_PRIMITIVES[0])
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        game.load_looks(slot)
        cell = row_value(ROWS.index(row))
        quiet = game.select_row(row)
        drift = quiet.difference(game.capture(), pixels(quiet, cell))
        floor = max(VALUE_MOVED, drift * IDLE_MARGIN)
        game.say("the %s cell drifts %.6f while idle, so a press has to beat "
                 "%.6f" % (row, drift, floor))
        path = os.path.join(game.out_dir, "hair.bin")

        def read():
            return game.read_ram(base, length, path)

        for _ in range(count):
            game.press("Left", expect_change=False)
        previous = game.capture()
        blocks = [steady(game, read)]
        cells = 0
        for _ in range(count):
            game.press("Right", expect_change=False)
            frame = game.capture()
            if frame.difference(previous, pixels(frame, cell)) > floor:
                cells += 1
            previous = frame
            blocks.append(steady(game, read))
        print("  %s on slot %d: the value cell moved on %d of %d press(es) "
              "of Right, and %s section %d reached %d distinct state(s) in "
              "%d value(s)"
              % (row, slot, cells, count, name, index,
                 len({bytes(b) for b in blocks}), len(blocks)))

        # Back to the bottom, so that the samples below walk the domain
        # upward from the field's lowest value instead of from wherever the
        # first half of this left it.
        for _ in range(count):
            game.press("Left", expect_change=False)
        maps = model_maps(ready["image"])
        game.say("watching the `v` of primitive %d of %s section %d, at %#010x"
                 % (layout.HAIR_PRIMITIVES[0], name, index, witness))
        bands, said = [], False
        for step in range(1, count + 1):
            found = catch_write(game, witness, seconds=BAND_SECONDS,
                                presses=1, button="Right", required=False)
            if found and not said:
                _say_writer(found, witness, maps)
                said = True
            bands.append(band_of(found) if found else None)
        if not said:
            raise OracleError(
                "%d press(es) of Right and not one of them wrote %#010x: the "
                "byte, the row or the address is wrong" % (count, witness))
        print("  %s: what each press writes to the hair quad, from the bottom "
              "of the row up -- `-` is a press that wrote nothing"
              % row, flush=True)
        print("      %s" % ", ".join(
            "%s=%s" % (looks.BY_ROW[row].label(step),
                       "-" if band is None else band)
            for step, band in enumerate(bands, 1)), flush=True)
        print("      %d of %d press(es) wrote the quad, over %d distinct "
              "band(s): %s"
              % (sum(1 for b in bands if b is not None), count,
                 len({b for b in bands if b is not None}),
                 sorted({b for b in bands if b is not None})), flush=True)
    return 0


BAND_SECONDS = 8
"""How long one value of the field is given to write the hair quad.

Short on purpose: most values write nothing, and the sweep is 32 of them.  The
budget is what makes the difference between "this value does not write it" and
"we did not wait", so it is named rather than inlined -- and it is generous
against a press that takes 28 frames to land.
"""


def band_of(found):
    """Which 16-row band one hit wrote, out of the value it stored.

    The routine is four stores of the same two bytes -- `v = band * 16 + 1` on
    two corners and `+ 15` on the other two -- so the band comes back out of
    either of them by arithmetic, and no table of ours is involved:

        andi  v0, a2, 0x00ff      the band, as the caller passed it
        sll   v0, v0, 4           sixteen rows a band
        addiu v1, v0, 15
        sb    v1, 0x1(a0)         the `v` of corner 0

    Measured 2026-09-16 on the LOOKS SET screen.
    """
    import who_writes

    if not found["store"]:
        return None
    _row, (_mnemonic, source, _offset, _base), _value = found["store"]
    held = who_writes.register_value(found["registers"], source)
    if held is None:
        return None
    return (held - BAND_TOP) // layout.ATLAS_BAND


BAND_TOP = 15
"""The `+15` the routine adds for the bottom corners of the quad.

One less than the band's sixteen rows: the quad covers rows 1..15 of its band,
not 0..15, which is what keeps it off the seam with the band above.
"""


def check_where(row="HAIR", slot=2, verbose=True):
    """Where a field's values go when the geometry does not show them.

    LOOKS-TASK-14 measured that `MODEL.BIN` section 24 shows **three** states
    while `hair_style` holds 32.  This is the other half of that question: the
    field is pressed through its whole domain and what is watched is the two
    working bands -- the display list the GPU is actually fed -- instead of the
    file.  If the styles are in there, the count comes out of this; if they are
    not, the answer is that they are nowhere this cycle has looked, which is
    also worth knowing and is what "a named hole" would then mean.
    """
    import looks

    ready = preflight()
    count = looks.BY_ROW[row].values
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in sorted(SLOTS):
            restore_state(one, verbose=verbose)
        game.load_looks(slot)
        game.select_row(row)
        path = os.path.join(game.out_dir, "bands.bin")

        def read():
            return b"".join(game.read_ram(base, BUFFER_SIZE, path)
                            for base in BUFFER_BANDS)

        for _ in range(count):
            game.press("Left", expect_change=False)
        states = [steady(game, read)]
        for _ in range(count):
            game.press("Right", expect_change=False)
            states.append(steady(game, read))

    seen, order = {}, []
    for state in states:
        key = bytes(state)
        if key not in seen:
            seen[key] = len(seen)
            order.append(key)
        else:
            order.append(key)
    print("  %s over %d value(s): %d distinct state(s) in the two bands"
          % (row, len(states), len(seen)))
    print("      the order they appear in: %s"
          % ", ".join(str(seen[k]) for k in order))
    if len(seen) > 1:
        first, second = order[0], next(k for k in order if k != order[0])
        differ = [i for i in range(len(first)) if first[i] != second[i]]
        print("      the first two differ at %d byte(s), from %#010x"
              % (len(differ), _band_address(differ[0])))
        print("      %s" % _say_runs(differ))
    return 0


def _band_address(offset):
    """A byte of the joined bands, back as a RAM address."""
    if offset < BUFFER_SIZE:
        return BUFFER_BANDS[0] + offset
    return BUFFER_BANDS[1] + offset - BUFFER_SIZE


def _say_runs(offsets, most=6):
    """The differing bytes as runs, which is how a display list differs."""
    runs, start, last = [], None, None
    for offset in offsets:
        if start is None:
            start, last = offset, offset
        elif offset == last + 1:
            last = offset
        else:
            runs.append((start, last))
            start, last = offset, offset
    if start is not None:
        runs.append((start, last))
    shown = ", ".join("%#010x+%d" % (_band_address(a), b - a + 1)
                      for a, b in runs[:most])
    return ("%d run(s): %s%s"
            % (len(runs), shown, " ..." if len(runs) > most else ""))


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


# --- the LOOKS SET screen, measured (LOOKS-TASK-21) ------------------------
#
# What the window of LOOKS-TASK-22 may draw, read off the game and never off
# a label: the text of every value of every row, the help of each row, how
# the cursor and the values move, the initial values of both states, and where
# the boxes are.  `--screen --write` writes screen.json; `--screen` walks it
# all again and fails on any difference.

OBJECT_SIZE = 20
"""The bytes of a text object that layout.SCREEN_PRINT documents -- the
sixteen it lists, and the colour after them (LOOKS-TASK-37)."""

STRING_READ = 256
"""How much of a string is read before its terminating zero is looked for.
The longest string this screen prints -- the twelve labels -- is 71 bytes."""

OBJECT_REPEAT = 2
GLYPH_REPEAT = 8
"""How many stops have to come round again before a frame counts as seen.

One is not enough for glyphs: the measuring pass puts every letter of a word at
the same x and y, so `BOOTS` alone repeats `O` at one key, and a cycle that
began on that `O` would close after one stop.  Eight distinct stops in the same
order again is a frame."""

OBJECT_LIMIT = 64
GLYPH_LIMIT = 1024  # not-an-address: a count of stops
"""A frame that has not come round by then is refused.  Measured: 8 objects
and 268 glyphs per frame on LOOKS SET."""

CYCLE_SECONDS = 120
"""The wall clock a frame of stops may take before the breakpoint is presumed
to be somewhere the game no longer goes."""

SCREEN_WALK_LIMIT = 160
"""Presses in one direction before a walk that neither locked nor came round
is refused.  The longest measured row, HEIG, walks 64."""

DUMP_SAMPLES = 6
"""VRAM dumps per picture, a frame apart, of which the finished ones must
agree."""

ASCII_KINDS = (32, 33)
"""The `kind` bytes of the two ASCII fonts this screen prints with."""


def _signed16(value):
    value &= 0xFFFF  # not-an-address: a halfword mask
    return value - 0x10000 if value & 0x8000 else value  # not-an-address: the sign bit of a halfword


def _stops(game, address, read, repeat, limit):
    """What *read* makes of each stop at an execute breakpoint, one frame of them.

    *address* is one address or a tuple of them; with several armed at once
    the stops come in the order the game runs them, and *read* tells them
    apart by the `pc` in the registers (CORR-LOOKS-071).

    The frame is closed by repetition, not by the clock: the first *repeat*
    stops coming round again in the same order.  The emulator is left paused.
    """
    import time

    import who_writes

    addresses = address if isinstance(address, tuple) else (address,)
    address = addresses[0]
    client = game.client
    client.call("breakpoint", action="clear")
    for one in addresses:
        client.call("breakpoint", action="add", type="execute",
                    address=who_writes.hx(one))
    out = []
    deadline = time.time() + CYCLE_SECONDS
    try:
        client.call("continue")
        while True:
            if time.time() > deadline:
                raise OracleError("%s stopped %d time(s) in %ds and never came "
                                  "round -- the screen is not drawing"
                                  % (who_writes.hx(address), len(out),
                                     CYCLE_SECONDS))
            if not who_writes.is_paused(client.call("wait_for_pause")):
                continue
            out.append(read(client.call("read_registers", group="gpr")))
            if (len(out) >= 2 * repeat
                    and out[-repeat:] == out[:repeat]):
                del out[-repeat:]
                return out
            if len(out) > limit:
                raise OracleError("%s stopped %d times without a frame coming "
                                  "round" % (who_writes.hx(address), limit))
            client.call("continue")
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass


def _cstring(game, address, size=STRING_READ):
    size = min(size, RAM_BASE + RAM_SIZE - address)
    path = os.path.join(game.out_dir, "string.bin")
    return game.read_ram(address, size, path).split(b"\0")[0]


def screen_objects(game):
    """Every text object the print routine is handed in one frame."""
    import struct

    import screen
    import who_writes

    path = os.path.join(game.out_dir, "object.bin")

    def read(registers):
        at = who_writes.register_value(registers, "a0")
        raw = game.read_ram(at, OBJECT_SIZE, path)
        pointer = struct.unpack_from("<I", raw, 8)[0]
        text = (_cstring(game, pointer)
                if RAM_BASE <= pointer < RAM_BASE + RAM_SIZE else b"")
        return (at, raw, text)

    out = []
    for at, raw, text in _stops(game, layout.SCREEN_PRINT, read,
                                OBJECT_REPEAT, OBJECT_LIMIT):
        x, y = struct.unpack_from("<hh", raw, 0)
        kind = raw[12]
        out.append({"at": at, "x": x, "y": y,
                    "width": struct.unpack_from("<H", raw, 6)[0],
                    "kind": kind, "raw": text,
                    "style": text_style(raw),
                    "lines": (screen.decode(text) if kind in ASCII_KINDS
                              else None)})
    return out


TEXT_ALIGN, TEXT_SPACING, TEXT_COLOUR = 13, 14, 16
"""Where a text object keeps how it is written, past the kind at byte 12.

Read on 2026-09-22 (LOOKS-TASK-37) off the eight objects of both states:
byte 14 is the SPACING the pen adds after every glyph -- 2 for the labels, 1
for `Unknown`, 0 for `SHIRT N` and the digits, and exactly the gap between
two glyphs the draw pass reports, inside a run: a `\\t` puts the pen at its
own column, so `A1` is two runs with 1 px between them at spacing 0 --
`check_glyphs` holds `Font.run` to it per run (CORR-LOOKS-071) --; bytes 16 to 18 are the COLOUR every glyph
of the object is modulated by, (128, 128, 128) for the labels, the plate and
the shirt and (112, 112, 240) for the values; byte 13 takes 0, 2 and 3 and
is the alignment inside the box -- left, right, centred -- measured against
the draw calls by LOOKS-TASK-38 (`glyphs.ALIGNMENTS`)."""


def text_style(raw):
    """{spacing, colour, align} of one text object's bytes."""
    return {"spacing": raw[TEXT_SPACING],
            "colour": list(raw[TEXT_COLOUR:TEXT_COLOUR + 3]),
            "align": raw[TEXT_ALIGN]}


def value_layout(reading, name, orders, display, shown):
    """The pieces *name*'s value is written in, as the game lays them.

    `[{box, align, spacing, colour, tokens}]`, left to right in the measured
    order: one per text object that writes a line on this row -- `A TYPE` is
    the `A` of one object, centred in its box, and the `TYPE` of another,
    against the right edge of its own.  `box` is the object's (x, y, width)
    in native pixels with y the line's; `tokens` are the line's
    `screen.line_tokens`, tabs and trailing blanks included, since both move
    the pen.  The boxes change with the value -- NAT's object sits 24 pixels
    left once it holds a nation -- which is why this is read on every value
    and not once (LOOKS-TASK-38).
    """
    import looks
    import screen

    origin = (display[0] // 2, display[1] // 2)
    index = looks.SCREEN.index(name)
    by_key = {obj["at"]: obj for obj in reading.objects}
    pieces = []
    for key in orders[name]:
        if key not in reading.pieces[name]:
            continue
        obj = by_key[key]
        lines = screen.line_tokens(obj["raw"])
        number = next(n for n in range(len(lines))
                      if screen.row_of(obj["y"] + n * reading.geometry["pitch"],
                                       reading.geometry["row0_y"],
                                       reading.geometry["pitch"]) == index)
        pieces.append({"box": [obj["x"] + origin[0],
                               obj["y"] + number * reading.geometry["pitch"]
                               + origin[1], obj["width"]],
                       "align": obj["style"]["align"],
                       "spacing": obj["style"]["spacing"],
                       "colour": screen.colour_at(lines, number,
                                                  obj["style"]["colour"]),
                       "tokens": lines[number]})
    joined = " ".join(screen.tokens_text(piece["tokens"]).strip()
                      for piece in pieces)
    if joined != shown:
        raise OracleError("%s: the pieces spell %r and the row reads %r"
                          % (name, joined, shown))
    return pieces


def placed_style(obj, display):
    """An object outside the rows as the window needs it: its style, its box
    in native pixels and its one line's tokens."""
    import screen

    lines = screen.line_tokens(obj["raw"])
    return dict(obj["style"],
                box=[obj["x"] + display[0] // 2, obj["y"] + display[1] // 2,
                     obj["width"]],
                tokens=lines[0])


def text_styles(reading, orders, labels, display):
    """How each text of the screen is written: the labels, the plate, the
    shirt, and each row's value.

    A value can be put together from more than one object -- `A1 TYPE` is the
    `A1` of one and the `TYPE` of another, with spacings 0 and 2 -- and which
    objects make it up changes with the value.  What is kept per row is the
    style of the object that writes its LAST piece.  Splitting a value by
    object, and where each piece starts, is `value_layout`, read per value by
    the walk (LOOKS-TASK-38).
    """
    import looks

    by_key = {obj["at"]: obj for obj in reading.objects}
    outside = reading.outside()
    out = {"labels": labels["style"],
           "plate": placed_style(outside["plate"], display),
           "shirt": placed_style(outside["shirt"], display), "values": {}}
    for name in looks.SCREEN:
        keys = [key for key in orders[name] if key in reading.pieces[name]]
        if not keys:
            raise OracleError("row %s shows no piece, so it has no style" % name)
        out["values"][name] = by_key[keys[-1]]["style"]
    return out


def screen_glyphs(game):
    """(x, y, text) of every string the glyph routine draws in one frame."""
    import screen
    import who_writes

    def read(registers):
        value = lambda name: who_writes.register_value(registers, name)
        return (value("a0"), _signed16(value("a1")), _signed16(value("a2")),
                value("a3"))

    return screen.glyph_strings(_stops(game, layout.SCREEN_GLYPH, read,
                                       GLYPH_REPEAT, GLYPH_LIMIT))


def screen_help(game):
    """The help box's text, through the pointer its setter keeps."""
    import struct

    import screen

    path = os.path.join(game.out_dir, "help.bin")
    pointer = struct.unpack("<I", game.read_ram(layout.SCREEN_HELP, 4, path))[0]
    if not RAM_BASE <= pointer < RAM_BASE + RAM_SIZE:
        raise OracleError("the help pointer holds %#x, which is not RAM"
                          % pointer)
    return screen.help_text(_cstring(game, pointer))


def screen_record(game):
    """The ten stored fields of the player on screen, from both live copies."""
    import looks

    path = os.path.join(game.out_dir, "record.bin")
    copies = [game.read_ram(at, layout.PLAYER_RECORD_SIZE, path)
              for at in layout.PLAYER_RAM]
    if len(set(copies)) != 1:
        raise OracleError("the two live copies of the player disagree: %s"
                          % " / ".join(c.hex() for c in copies))
    return looks.decode(copies[0])


def screen_frames(game, display):
    """The finished frame buffers of the next few frames, and their boxes.

    From `dump_vram`: one call, the whole 1024x512 VRAM at its own resolution,
    in exact 15-bit colours.  The first runs blamed `read_vram_region` for a
    missing rows box; the cause was the display size asked for before the
    load (see `measure_screen`), and `read_vram_region` was never re-tried.

    **And one dump is not a picture.**  The game draws into one buffer while it
    shows the other: measured, one of four dumps a frame apart held no box at
    all, and a PNG of a different size.  So this dumps DUMP_SAMPLES times and
    keeps the dumps holding the most boxes; at least two have to agree box for
    box.

    **Only the TOP buffer, at VRAM row 0**, whose origin is the display's: the
    label object's x=-56 lands on native column 200 and its y=-79 on row 41.
    """
    import atlas
    import screen

    width, height = display
    seen, per_dump = [], []
    for sample in range(DUMP_SAMPLES):
        game.step(1)
        # A name per dump, removed first: a file left by an earlier dump under
        # the same name would be read as this one if the emulator did not
        # write, and nothing would say so.
        path = os.path.join(game.out_dir, "vram-%d.png" % sample)
        if os.path.exists(path):
            os.remove(path)
        game.client.call("dump_vram", path=path, format="png")
        if not os.path.exists(path):
            raise OracleError("dump_vram reported %s and there is no file "
                              "there" % path)
        _, _, rows = atlas.read_png(path)
        frame = [row[:width] for row in rows[:height]]
        boxes = screen.boxes(frame, width, height)
        seen.append((frame, boxes))
        per_dump.append(len(boxes))
    most = max(len(boxes) for _, boxes in seen)
    kept = [(frame, boxes) for frame, boxes in seen if len(boxes) == most]
    if len(kept) < 2 or any(boxes != kept[0][1] for _, boxes in kept):
        raise OracleError("over %d dumps no two finished buffers agree on the "
                          "boxes: %r, boxes per dump %r"
                          % (DUMP_SAMPLES,
                             sorted({tuple(b) for _, b in seen}), per_dump))
    return [frame for frame, _ in kept], kept[0][1]


def tap(game, button):
    """One press, the same length the rest of the oracle uses, and no picture."""
    game.client.call("press_button", button=button,
                     duration_frames=CONFIRM_FRAMES)
    game.step(CONFIRM_FRAMES + SETTLE_FRAMES)


class ScreenReading:
    """One reading of the screen: objects, rows, and what sits left of the rows."""

    def __init__(self, geometry, objects):
        import screen

        self.objects = objects
        self.pieces = screen.pieces(
            [o for o in objects if o["lines"] is not None],
            geometry["row0_y"], geometry["pitch"], geometry["left"],
            geometry["top"])
        self.geometry = geometry

    def rows(self, orders):
        import looks
        import screen

        return {name: screen.compose(self.pieces[name], orders[name])
                for name in looks.SCREEN}

    def outside(self):
        """{title, shirt, plate: the object}: the kind-33 one, and the two left
        of the rows box, upper then lower."""
        import screen

        left = sorted((o for o in self.objects
                       if not screen.in_rows(o, self.geometry["left"],
                                             self.geometry["top"])
                       and o["kind"] == ASCII_KINDS[0]),
                      key=lambda o: o["y"])
        titles = [o for o in self.objects if o["kind"] == ASCII_KINDS[1]]
        if len(left) != 2 or len(titles) != 1:
            raise OracleError("expected a title and two strings left of the "
                              "rows box, and got %d and %d"
                              % (len(titles), len(left)))
        return {"title": titles[0], "shirt": left[0], "plate": left[1]}


def object_text(obj):
    """The one line an object outside the rows box holds."""
    return " ".join(line.strip() for line in obj["lines"]).strip()


def outside_control(reading, glyphs, frames, origin):
    """The three texts outside the rows box, each against what the frame shows.

    The rows are checked decode-against-glyph on every run, and until
    CORR-LOOKS-054 these three were not -- which is how a title nobody had
    compared came to be stored as the string its object holds.

    The shirt name and the position plate DO go through the glyph routine, so
    they are compared string for string, the way a row is.  The title does not:
    it is printed with the second font (`ASCII_KINDS[1]`), and measured, that
    one draws nothing the glyph routine reports.  So what is checked there is
    what its band holds -- one run of white per letter its font has a glyph
    for, counted off the finished frames (`screen.TITLE_FONT`).
    """
    import screen

    objects = reading.outside()
    # Left of the rows box, and only there: the plate shares its line with NAT,
    # whose label and value are drawn on the same y and belong to the row.
    left_of_rows = reading.geometry["left"]
    for name in ("shirt", "plate"):
        obj = objects[name]
        held = object_text(obj)
        drawn = [text.strip() for x, y, text in glyphs
                 if y == obj["y"] and x < left_of_rows]
        if drawn != [held]:
            raise OracleError("the %s object holds %r and the glyph routine "
                              "drew %r left of the rows box on its line"
                              % (name, held, drawn))
    title = objects["title"]
    held = object_text(title)
    if any(y == title["y"] for _, y, _ in glyphs):
        raise OracleError("the title's line goes through the glyph routine "
                          "now, and this counts its letters off the frame "
                          "because it did not")
    band = screen.title_band((title["x"], title["y"]), title["width"], origin)
    want = len(screen.title_drawn(held).replace(" ", ""))
    # A finished buffer with an empty band is the blink the cursor also has:
    # measured, one dump in eight held the boxes and no title.  A buffer
    # holding a DIFFERENT number of letters is a difference, and refused.
    counted = sorted({len(screen.ink_runs(frame, band)) for frame in frames})
    if want not in counted or any(n not in (0, want) for n in counted):
        raise OracleError("the title object holds %r, whose font draws %r -- "
                          "%d letter(s) -- and the band %r holds %r over %d "
                          "finished dump(s)"
                          % (held, screen.title_drawn(held), want, band,
                             counted, len(frames)))
    return {"title": screen.title_drawn(held), "title_object": held,
            "title_skipped": screen.title_skipped(held),
            "shirt": object_text(objects["shirt"]),
            "plate": object_text(objects["plate"]),
            "anchors": {name: [obj["x"], obj["y"]]
                        for name, obj in objects.items()}}


def _line_grid(glyphs, labels):
    """(row0_y, pitch), measured on the drawn labels: each on its own line,
    evenly apart."""
    import looks

    ys = []
    for name in looks.SCREEN:
        found = [y for x, y, text in glyphs
                 if x == labels["x"] and text.strip() == name]
        if len(found) != 1:
            raise OracleError("the label %r was drawn %d time(s) at x=%d"
                              % (name, len(found), labels["x"]))
        ys.append(found[0])
    steps = {b - a for a, b in zip(ys, ys[1:])}
    if len(steps) != 1 or ys[0] != labels["y"]:
        raise OracleError("the labels are not on an even grid from the "
                          "object's own y: %r" % ys)
    return ys[0], steps.pop()


def _named_boxes(found, anchor):
    """The three boxes by where they sit: the one holding the labels, the one
    left of it, the one under it."""
    rows = [b for b in found
            if b[0] <= anchor[0] <= b[2] and b[1] <= anchor[1] <= b[3]]
    if len(rows) != 1:
        raise OracleError("%d box(es) hold the labels: %r" % (len(rows), found))
    rows = rows[0]
    panel = [b for b in found if b[2] < rows[0]]
    helps = [b for b in found if b[1] > rows[3]]
    if len(panel) != 1 or len(helps) != 1 or len(found) != 3:
        raise OracleError("expected the rows box, one box left of it and one "
                          "under it, and found %r" % (found,))
    return {"rows": rows, "panel": panel[0], "help": helps[0]}


def _orders(reading, glyphs):
    """Left to right, per row: which object each drawn piece came from."""
    import looks
    import screen

    geometry = reading.geometry
    orders, problems = {}, []
    for index, name in enumerate(looks.SCREEN):
        line_y = geometry["row0_y"] + index * geometry["pitch"]
        drawn = sorted((x, text.strip()) for x, y, text in glyphs
                       if y == line_y and x >= geometry["left"]
                       and text.strip() and text.strip() != name)
        pieces = reading.pieces[name]
        if sorted(t for _, t in drawn) != sorted(pieces.values()):
            problems.append("%s: drawn %r, decoded %r"
                            % (name, [t for _, t in drawn],
                               sorted(pieces.values())))
            continue
        keys, used = [], set()
        for _, text in drawn:
            key = next(k for k, v in sorted(pieces.items())
                       if v == text and k not in used)
            used.add(key)
            keys.append(key)
        orders[name] = keys
    if problems:
        raise OracleError("the decoded strings are not what the game drew: %s"
                          % "; ".join(problems))
    return orders


def _control(game, reading, orders):
    """The glyphs drawn NOW against the rows the objects compose NOW."""
    glyphs = screen_glyphs(game)
    again = _orders(reading, glyphs)
    for name, keys in again.items():
        if keys != orders[name]:
            raise OracleError("%s draws its pieces in the order %r here and "
                              "%r on load" % (name, keys, orders[name]))
    return len(glyphs)


def _cursor_row(frames, regions, geometry, origin):
    """The row the yellow box sits on, the same in every finished buffer."""
    import looks
    import screen

    # A frame with no cursor at all is the blink, not a disagreement: measured,
    # one dump in six held the three boxes and no yellow pixel.
    shown = [screen.cursor(frame, regions["rows"]) for frame in frames]
    boxes = {box for box in shown if box is not None}
    if len(boxes) != 1 or sum(box is not None for box in shown) < 2:
        raise OracleError("the cursor box reads %r over %d finished dump(s)"
                          % (shown, len(frames)))
    box = boxes.pop()
    hits = [index for index in range(len(looks.SCREEN))
            if box[1] <= geometry["row0_y"] + index * geometry["pitch"]
            + origin[1] <= box[3]]
    if len(hits) != 1:
        raise OracleError("the cursor box %r covers %d row line(s)"
                          % (box, len(hits)))
    return hits[0], box


def measure_screen(game, verbose=True):
    """Everything screen.json holds, measured on the running game."""
    import time

    import looks
    import screen

    started = time.time()
    table = {"order_of_rows": list(looks.SCREEN),
             "initial": {}, "rows": {name: {} for name in looks.SCREEN}}
    orders, geometry, regions, display = None, None, None, None

    for slot in sorted(SLOTS):
        game.load_looks(slot)
        # AFTER the load, never before: asked of a freshly booted emulator the
        # GPU answers 256x239, the boot screen's mode, and a frame cut to 256
        # columns holds the panel and no rows box.  Four runs of this
        # measurement failed on exactly that, and were first taken for a
        # screen caught mid-draw.
        gpu = game.client.call("get_gpu_state")
        here_display = (int(gpu["display_width"]),
                        int(gpu["display_height"]))
        if display not in (None, here_display):
            raise OracleError("slot %d displays %r and the other %r"
                              % (slot, here_display, display))
        display = here_display
        origin = (display[0] // 2, display[1] // 2)
        table["display"] = list(display)
        objects = screen_objects(game)
        labels = screen.labels_object(objects)
        glyphs = screen_glyphs(game)
        row0_y, pitch = _line_grid(glyphs, labels)
        frames, found = screen_frames(game, display)
        named = _named_boxes(found, (labels["x"] + origin[0],
                                     labels["y"] + origin[1]))
        here = {"row0_y": row0_y, "pitch": pitch,
                "left": named["rows"][0] - origin[0],
                "top": named["rows"][1] - origin[1]}
        if geometry not in (None, here) or regions not in (None, named):
            raise OracleError("slot %d lays the screen out differently: %r %r"
                              % (slot, here, named))
        geometry, regions = here, named
        reading = ScreenReading(geometry, objects)
        slot_orders = _orders(reading, glyphs)
        if orders not in (None, slot_orders):
            raise OracleError("slot %d draws its pieces in another order"
                              % slot)
        orders = slot_orders
        outside = outside_control(reading, glyphs, frames, origin)
        cursor_row, cursor_box = _cursor_row(frames, regions, geometry, origin)
        record = screen_record(game)
        plate = outside["plate"]
        outside["anchors"]["labels"] = [labels["x"], labels["y"]]
        table["initial"][str(slot)] = dict(
            outside, rows=reading.rows(orders),
            help=screen_help(game), cursor=looks.SCREEN[cursor_row],
            record=record, styles=text_styles(reading, slot_orders, labels,
                                              display))
        say = print if verbose else (lambda *a: None)
        say("  slot %d on load: %s, plate %s, cursor on %s, help %r; %d "
            "glyph string(s) checked against %d object(s); the title object "
            "holds %r and the band draws %r"
            % (slot, SLOTS[slot], plate, looks.SCREEN[cursor_row],
               table["initial"][str(slot)]["help"], len(glyphs),
               len(objects), outside["title_object"], outside["title"]))
        if slot == min(SLOTS):
            table["cursor_box_on_load"] = list(cursor_box)

    first = table["initial"][str(min(SLOTS))]
    for slot, state in table["initial"].items():
        for key in ("help", "cursor"):
            if state[key] != first[key]:
                raise OracleError("the states differ in %s: %r and %r"
                                  % (key, first[key], state[key]))
    table["help_on_load"] = first["help"]
    table["cursor_on_load"] = first["cursor"]
    table["row0_y"], table["pitch"] = geometry["row0_y"], geometry["pitch"]
    table["rows_left"] = geometry["left"]
    table["rows_top"] = geometry["top"]
    table["orders"] = orders

    walk_slot = max(SLOTS)
    helps, vertical, boxes_by_row = _walk_cursor(game, walk_slot, display,
                                                 regions, geometry, origin,
                                                 verbose)
    table["vertical"] = vertical
    for name in looks.SCREEN:
        table["rows"][name]["help"] = helps[name]

    for index, name in enumerate(looks.SCREEN):
        table["rows"][name].update(
            _walk_row(game, walk_slot, name, table, geometry, orders,
                      verbose, regions, display))
        # Two walks read the same box: the cursor walk on arrival from the
        # row above or below, and the row walk on arrival and at both ends.
        if table["rows"][name]["cursor"] != list(boxes_by_row[name]):
            raise OracleError("%s: the cursor walk read the box %r and the "
                              "row walk %r" % (name, list(boxes_by_row[name]),
                                               table["rows"][name]["cursor"]))

    table["regions"] = {}
    for name, box in sorted(regions.items()):
        table["regions"][name] = {"native": list(box),
                                  "fraction": screen.fraction(box, display)}
    top = boxes_by_row[looks.SCREEN[0]]
    bottom = boxes_by_row[looks.SCREEN[-1]]
    table["regions"]["cursor"] = {
        "native": list(boxes_by_row[table["cursor_on_load"]]),
        "fraction": screen.fraction(boxes_by_row[table["cursor_on_load"]],
                                    display),
        "row": table["cursor_on_load"],
        "step": (bottom[1] - top[1]) // (len(looks.SCREEN) - 1)}
    for slot, state in table["initial"].items():
        _require_initial(table, slot, state)
    if verbose:
        print("  screen measured in %.0fs" % (time.time() - started))
    return table


def _walk_cursor(game, slot, display, regions, geometry, origin, verbose):
    """Up past the top and Down past the bottom, the cursor read off VRAM."""
    import looks

    game.load_looks(slot)
    helps, boxes = {}, {}

    def where():
        frames, _ = screen_frames(game, display)
        row, box = _cursor_row(frames, regions, geometry, origin)
        return row, box

    def press(button, expect):
        for attempt in range(2):
            tap(game, button)
            row, box = where()
            if row == expect or attempt:
                return row, box
        return row, box

    row, box = where()
    row, box = press("Up", row - 1)
    helps[looks.SCREEN[row]] = screen_help(game)
    boxes[looks.SCREEN[row]] = box
    last = len(looks.SCREEN) - 1
    after_up, _ = press("Up", last)
    vertical = {"up": "wraps" if after_up == last else
                "locks" if after_up == 0 else "moves to %d" % after_up}
    if after_up != last:
        row = after_up
        while row != last:
            row, box = press("Down", row + 1)
            helps.setdefault(looks.SCREEN[row], screen_help(game))
            boxes.setdefault(looks.SCREEN[row], box)
    else:
        helps.setdefault(looks.SCREEN[last], screen_help(game))
        row, box = press("Down", 0)
        if row != 0:
            raise OracleError("Down from the bottom after Up wrapped went to "
                              "row %d" % row)
        while row != last:
            row, box = press("Down", row + 1)
            helps.setdefault(looks.SCREEN[row], screen_help(game))
            boxes.setdefault(looks.SCREEN[row], box)
    after_down, _ = press("Down", 0)
    vertical["down"] = ("wraps" if after_down == 0 else
                        "locks" if after_down == last else
                        "moves to %d" % after_down)
    for name in looks.SCREEN:
        if name not in helps:
            raise OracleError("the cursor never reached %s" % name)
    if verbose:
        print("  cursor: Up past the top %s, Down past the bottom %s"
              % (vertical["up"], vertical["down"]))
    return helps, vertical, boxes


def _walk_row(game, slot, name, table, geometry, orders, verbose, regions,
              display):
    """Every value one row walks, both ends, and what moves beside it.

    A lock is judged by the text, the help AND the arrows: a press that
    leaves all three where they were moved nothing.  DEFAUL is why -- Left
    from its one value keeps `O.K.` and takes the cursor box to the row's
    name, the help to `Undo` and the arrow to the other side, and a walk that
    looked at the text alone wrote that down as a lock (CORR-LOOKS-067).  The
    position it reaches is measured by `_walk_label` as the row's `label`.
    """
    import looks

    game.load_looks(slot)
    here = looks.SCREEN.index(table["cursor_on_load"])
    target = looks.SCREEN.index(name)
    button = "Down" if target > here else "Up"
    for _ in range(abs(target - here)):
        tap(game, button)
    # With no press the help still reads what it read on load ("Visual"), and
    # the witness is the cursor box, which the load already read off VRAM.
    want = (table["rows"][name]["help"] if target != here
            else table["help_on_load"])
    if screen_help(game) != want:
        raise OracleError("pressed %s %d time(s) to reach %s and the help "
                          "reads %r" % (button, abs(target - here), name,
                                        screen_help(game)))
    field = looks.BY_ROW.get(name)
    origin = (display[0] // 2, display[1] // 2)

    def value_box(where):
        """The cursor box off VRAM, on this row's value: per row, because
        the game sizes it per row -- x 314 on NAT, 396 on DEFAUL
        (CORR-LOOKS-070) -- and the same on every value of it, which the
        three readings below assert rather than assume."""
        frames, _ = screen_frames(game, display)
        row, box = _cursor_row(frames, regions, geometry, origin)
        if row != target:
            raise OracleError("%s: %s the cursor box is on row %s"
                              % (name, where, looks.SCREEN[row]))
        return list(box)

    arrows_now = []
    help_now = [None]
    layout_now = []

    def read():
        reading = ScreenReading(geometry, screen_objects(game))
        rows = reading.rows(orders)
        value = screen_record(game)[field.name] if field else None
        arrows_now[:] = frame_arrows(game)
        help_now[0] = screen_help(game)
        layout_now[:] = value_layout(reading, name, orders, display,
                                     rows[name])
        return rows, value

    def rest():
        return (help_now[0], list(arrows_now))

    rows, value = read()
    initial = dict(rows)
    arrival = list(arrows_now)
    cursor = value_box("on arrival")
    # On the row the state loads on the help still reads "Visual" (trap 35),
    # and the first press makes it say the row whatever else it does -- so
    # that change is no evidence of anything, and the baseline is the row's.
    help_now[0] = table["rows"][name]["help"]
    moved, dropped = set(), 0
    # The arrows of every value the Right walk reaches, end included.
    between = []
    # The arrows on the value the cursor stood on when a Left took it to the
    # row's label, if one did.
    entered = []

    def go(direction, texts, values):
        nonlocal dropped
        for _ in range(SCREEN_WALK_LIMIT):
            before = rest()
            tap(game, direction)
            rows, value = read()
            if rows[name] == texts[-1] and rest() != before:
                # The text held and the help or the arrows moved: the cursor
                # left the value without changing it.
                if direction != "Left":
                    raise OracleError(
                        "%s: %s kept the text %r and moved the help or the "
                        "arrows (%r to %r), which only Left into a label is "
                        "modelled to do" % (name, direction, texts[-1],
                                            before, rest()))
                entered[:] = before[1]
                return "label"
            if rows[name] == texts[-1]:
                tap(game, direction)
                rows, value = read()
                if rows[name] == texts[-1] and rest() == before:
                    return "locks"
                if rows[name] == texts[-1]:
                    raise OracleError(
                        "%s: a second %s kept the text %r and moved the help "
                        "or the arrows (%r to %r)" % (name, direction,
                                                      texts[-1], before,
                                                      rest()))
                dropped += 1
            moved.update(other for other in looks.SCREEN
                         if other != name and rows[other] != initial[other])
            if rows[name] in texts:
                return "wraps"
            texts.append(rows[name])
            values.append(value)
            if direction == "Right":
                between.append((rows[name], list(arrows_now)))
                layouts.append(list(layout_now))
        raise OracleError("%s walked %s %d times without an end"
                          % (name, direction, SCREEN_WALK_LIMIT))

    left_texts, left_values = [rows[name]], [value]
    left = go("Left", left_texts, left_values)
    if left == "wraps":
        raise OracleError("%s wraps going Left; a wrapping row is not "
                          "modelled, and the walk says so rather than guess"
                          % name)
    label = None
    if left == "label":
        label = _walk_label(game, name, table, geometry, regions, display,
                            left_texts[-1], entered, read, rest)
        left = "locks"
        left_end = list(entered)
    else:
        left_end = list(arrows_now)
    # After the label, if there was one: _walk_label ends back on the value.
    cursor_ends = [value_box("at the left end")]
    # The left end's pieces, read on the value itself -- after a label, the
    # last reading was taken on the row's name.
    rows, _value = read()
    if rows[name] != left_texts[-1]:
        raise OracleError("%s: back from the left end the row reads %r, not "
                          "%r" % (name, rows[name], left_texts[-1]))
    layouts = [list(layout_now)]
    texts, values = [left_texts[-1]], [left_values[-1]]
    right = go("Right", texts, values)
    if right == "wraps":
        raise OracleError("%s wraps going Right after locking going Left"
                          % name)
    right_end = list(arrows_now)
    cursor_ends.append(value_box("at the right end"))
    if any(box != cursor for box in cursor_ends):
        raise OracleError("%s: the cursor box moved along the row: %r on "
                          "arrival, %r at the left end and %r at the right "
                          "end; one box per row is all the table can say"
                          % (name, cursor, cursor_ends[0], cursor_ends[1]))
    if list(reversed(left_texts)) != texts[:len(left_texts)]:
        raise OracleError("%s: Left walked %r and Right came back %r"
                          % (name, left_texts, texts))
    inner = [one for text, one in between if text != texts[-1]]
    if any(one != inner[0] for one in inner):
        raise OracleError("%s: the arrows between the two ends are not the "
                          "same on every value: %r" % (name, between))
    glyphs = _control(game, ScreenReading(geometry, screen_objects(game)),
                      orders)
    out = {"texts": texts, "left": left, "right": right,
           "stored": field.name if field else None,
           "label": label,
           "cursor": cursor,
           "moves_beside": sorted(moved, key=looks.SCREEN.index),
           "layouts": layouts,
           "arrows": {"arrival": arrival, "left_end": left_end,
                      "between": inner[0] if inner else None,
                      "right_end": right_end}}
    if field:
        if values != list(range(values[0], values[0] + len(values))):
            raise OracleError("%s: the stored value did not step by one with "
                              "the text: %r" % (name, values))
        out["values"] = values
    if verbose:
        print("            arrows: on arrival %s, at the left end %s, between "
              "%s, at the right end %s"
              % tuple(_say_arrows(out["arrows"][key]) for key in
                      ("arrival", "left_end", "between", "right_end")))
        print("            cursor on the value: %s, the same on arrival and "
              "at both ends" % cursor)
        if label is not None:
            print("            label: Left from the first value, help %r, "
                  "arrows %s, cursor %s; there Left %s, Up %s, Down %s, and "
                  "Right back" % (label["help"], _say_arrows(label["arrows"]),
                                  label["cursor"], label["left"], label["up"],
                                  label["down"]))
        shown = texts if len(texts) <= 6 else texts[:3] + ["..."] + texts[-2:]
        print("  %-9s %3d value(s), Left %s, Right %s%s%s; end checked "
              "against %d drawn string(s)%s"
              % (name, len(texts), left, right,
                 ", stored %d..%d" % (values[0], values[-1]) if field else "",
                 ", moves %s" % out["moves_beside"] if moved else "",
                 glyphs, ", %d press(es) dropped" % dropped if dropped else ""))
        print("            %s" % " | ".join(shown))
    return out


def _walk_label(game, name, table, geometry, regions, display, text,
                entered, read, rest):
    """The row's label position, which a Left from its first value reached.

    Measured, not assumed: the help and the arrows there, the cursor box off
    VRAM, and each of Left, Up and Down pressed twice -- two presses that move
    nothing are a lock, the way `go` judges one.  Anything else is refused,
    because `screen.LABEL_MOVES` is the only shape the table can say.  Right
    last, and it has to put the value's own help and arrows back.
    """
    import looks

    origin = (display[0] // 2, display[1] // 2)
    here = rest()
    frames, _ = screen_frames(game, display)
    row, box = _cursor_row(frames, regions, geometry, origin)
    if row != looks.SCREEN.index(name):
        raise OracleError("%s: Left took the cursor box to row %s"
                          % (name, looks.SCREEN[row]))
    label = {"help": here[0], "arrows": here[1], "cursor": list(box),
             "enter": "Left"}
    for button in ("Left", "Up", "Down"):
        for _ in range(2):
            tap(game, button)
            rows, _value = read()
            if rows[name] != text or rest() != here:
                raise OracleError(
                    "%s: %s on the label moved the screen (text %r, help and "
                    "arrows %r), which is not modelled"
                    % (name, button, rows[name], rest()))
        label[button.lower()] = "locks"
    frames, _ = screen_frames(game, display)
    if _cursor_row(frames, regions, geometry, origin)[1] != box:
        raise OracleError("%s: the cursor box left the label on a press that "
                          "moved nothing else" % name)
    back = (table["rows"][name]["help"], list(entered))
    for _attempt in range(2):
        tap(game, "Right")
        rows, _value = read()
        if rows[name] == text and rest() == back:
            break
    else:
        raise OracleError("%s: Right from the label shows text %r and %r, "
                          "not the value's %r" % (name, rows[name], rest(),
                                                   back))
    label["leave"] = "Right"
    return label


def _require_initial(table, slot, state):
    """Each stored row shows the text of the value the record holds."""
    import looks

    for name, field in looks.BY_ROW.items():
        row = table["rows"][name]
        want = row["texts"][row["values"].index(state["record"][field.name])]
        if state["rows"][name] != want:
            raise OracleError("slot %s holds %s=%d, which is %r on the walk, "
                              "and the screen showed %r"
                              % (slot, field.name, state["record"][field.name],
                                 want, state["rows"][name]))


def check_screen(write=False, verbose=True):
    """`--screen`: measure the screen and compare with, or write, screen.json."""
    import json

    import screen

    ready = preflight()
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in sorted(SLOTS):
            restore_state(slot, verbose=verbose)
        measured = measure_screen(game, verbose)
    measured = json.loads(json.dumps(measured))
    problems = screen.validate(measured)
    if problems:
        for problem in problems:
            print("  FAIL  %s" % problem)
        print("oracle --screen: the measurement does not hold together")
        return 1
    if write:
        screen.write(measured)
        print("oracle --screen --write: wrote %s" % screen.TABLE)
        return 0
    _say_arrow_cluts()
    table = screen.load()
    differences = _differences(table, measured)
    for path, want, got in differences:
        print("  FAIL  %s: screen.json has %r, the game shows %r"
              % (path, want, got))
    print("oracle --screen: %d difference(s) from screen.json"
          % len(differences))
    return 1 if differences else 0


KEY_SEQUENCE = ("Down,Right,Right,Down,Right,Down,Down,Left,Down,Right,"
                "Up,Up,Right,Down,Down,Down,Right,Right,Right")
"""The sequence `--keys` presses when nobody names one.

Chosen to be awkward on purpose: it leaves the row it loads on, walks a row up
as well as down, presses Left where the row is already at its left end -- a
press the game ignores and a window might not -- and ends on a row three
values along.  Nineteen presses, because the comparison is worth having only
where a disagreement has somewhere to hide.
"""


def frame_commands(game):
    """The GP0 commands of the frame on screen, walked off the list it hands
    the GPU (`layout.GPU_LIST_SUBMIT`), the way `_scenery_of` walks them.

    Cheap enough to ask after every press: the heads cost two frames of
    execution and all of RAM reads in a third of a second (measured
    2026-09-21, LOOKS-TASK-36)."""
    heads = gpu_list_heads(game)
    first, size, step = layout.SCENERY_SWEEP
    ram = b"".join(game.read_ram(base, step, os.path.join(
        game.out_dir, "frame-%08x.bin" % base))
        for base in range(first, first + size, step))
    nodes = []
    for head in dict.fromkeys(heads[len(heads) // 2:]):
        nodes += walk_gpu_list(ram, head)
    return commands_of(nodes)


def frame_glyphs(game):
    """The font glyphs of the frame on screen, `[(x, y, u, v)]` sorted.

    Every one the game can put a pixel with (`font_sprites`): the rows'
    names and values, the plate and the shirt.  Where each starts is what
    LOOKS-TASK-38 holds the window to, and the `uv` says which glyph it is."""
    return sorted((one["point"][0], one["point"][1], one["uv"][0],
                   one["uv"][1])
                  for one in font_sprites(sprites_of(frame_commands(game))))


def _glyphs_only_here(mine, theirs):
    """The glyphs of *mine* the other side does not draw too, sorted.

    A difference of multisets and not of sets: the same glyph twice on a line
    is two glyphs, and a value that lost one of a repeated pair differs by
    that one.
    """
    left = list(theirs)
    out = []
    for one in mine:
        if one in left:
            left.remove(one)
        else:
            out.append(one)
    return sorted(out)


def _glyph_differences(game, window):
    """What differs between the game's glyphs and the window's, by line.

    Empty when the two lists are the same glyph for glyph.  Otherwise one
    sentence per line of the screen that differs, naming the first glyph each
    side draws that the other does not -- the start of a misplaced value is
    the thing to read.

    **The first glyph OF THE LINE is not that** (CORR-LOOKS-078).  Until this
    the sentence printed `theirs[:1]` and `ours[:1]`, and a row whose label
    sits left of its value -- which is every row on this screen -- had the
    unchanged label as the leftmost glyph on both sides: the two halves of
    the sentence printed the same tuple and said nothing about the value that
    had moved.  It read as informative in LOOKS-TASK-38 only because the
    planted defect happened to move a value to the LEFT of its label.

    A line is reported when one side has a glyph the other does not, which is
    what the sentence names.  Both sides arrive sorted (`frame_glyphs`,
    `ui_check.read_screen`), so that is the same set of lines the old
    element-by-element comparison reported -- minus the one case it could
    only have reported with nothing to say.
    """
    game = [tuple(one) for one in game]
    window = [tuple(one) for one in window]
    lines = sorted({one[1] for one in game} | {one[1] for one in window})
    out = []
    for y in lines:
        theirs = [one for one in game if one[1] == y]
        ours = [one for one in window if one[1] == y]
        only_theirs = _glyphs_only_here(theirs, ours)
        only_ours = _glyphs_only_here(ours, theirs)
        if only_theirs or only_ours:
            out.append("the glyphs on line y %d: the game draws %d, the "
                       "first the window lacks %s; our window %d, the first "
                       "the game lacks %s"
                       % (y, len(theirs), only_theirs[:1], len(ours),
                          only_ours[:1]))
    return out


def frame_arrows(game):
    """The arrows beside the cursor's value in the frame on screen.

    `[{"side": "left" or "right", "point": [x, y]}]`, sorted: the sprites of
    `layout.ARROW_PAGE`, told apart by their `uv`.  Their colour pulses and is
    not part of the answer (LOOKS-TASK-36).  A sprite on that page with a
    `uv` that is neither arrow is refused -- it would be something this screen
    was never measured to draw.

    **And an arrow drawn from a CLUT other than `sprites.ARROW_CLUT` is
    refused** (CORR-LOOKS-068).  The window cuts both arrows from that one
    CLUT, and until this check it had been measured for the right arrow only:
    a wrong one passed every gate that runs without the emulator.  Every walk
    that reads the arrows now measures the CLUT of each one it sees -- the
    left arrow's is `(80, 497)` too, measured 2026-09-21 on DEFAUL in both
    slots.  The CLUTs seen are kept in `ARROW_CLUTS_SEEN`, by side.
    """
    import sprites as art

    sides = {tuple(uv): side for side, uv in art.ARROWS.items()}
    out = []
    for one in sprites_of(frame_commands(game)):
        if tuple(one["page"]) != layout.ARROW_PAGE:
            continue
        side = sides.get(tuple(one["uv"]))
        if side is None:
            raise OracleError("a sprite on the arrows' page at %r samples uv "
                              "%r, which is neither arrow"
                              % (one["point"], one["uv"]))
        clut = tuple(one["clut"])
        ARROW_CLUTS_SEEN.setdefault(side, set()).add(clut)
        if clut != tuple(art.ARROW_CLUT):
            raise OracleError("the %s arrow at %r is drawn from CLUT %r, and "
                              "the window cuts it from sprites.ARROW_CLUT %r"
                              % (side, tuple(one["point"]), clut,
                                 tuple(art.ARROW_CLUT)))
        out.append({"side": side, "point": list(one["point"])})
    return sorted(out, key=lambda one: (one["side"], one["point"]))


ARROW_CLUTS_SEEN: dict = {}
"""{side: {clut, ...}} of every arrow `frame_arrows` has read in this run."""


def _say_arrow_cluts():
    """One line naming the CLUT each arrow side was drawn from, or none seen."""
    if not ARROW_CLUTS_SEEN:
        print("  the arrows' CLUT: no arrow was on screen in this run")
        return
    print("  the arrows' CLUT, read off the list: %s" % ", ".join(
        "%s %s" % ({"left": "<", "right": ">"}[side],
                   " ".join("(%d,%d)" % one for one in sorted(cluts)))
        for side, cluts in sorted(ARROW_CLUTS_SEEN.items())))


def _say_arrows(arrows):
    if arrows is None:
        return "-"
    if not arrows:
        return "none"
    return " ".join("%s(%d,%d)" % ({"left": "<", "right": ">"}[one["side"]],
                                    one["point"][0], one["point"][1])
                    for one in arrows)


GLYPH_CONTROL = 1
"""Pairs the control reads the glyph table off by: the whole comparison
against the frame redone with each code taking its neighbour's pair has to
fail, or matching said nothing."""

PEN_CONTROLS = (0, 2)
"""Spacings the pen check is redone with, for EVERY object, as its control.

Each has to fail somewhere: 0 proves an object with a gap was measured, and 2
-- the labels' gap, which is what a pen ignoring the object's byte 14 would
use -- proves one with a gap of 0 or 1 was (CORR-LOOKS-071)."""


def pen_runs(raw):
    """The character codes of a string, in runs the pen lays without a jump.

    A run ends where the string opens a line (`\n`) or moves the pen with a
    tab (`\t` and its byte): `\t\x12A\t\x1e1` is two runs, `A` and `1`,
    each put at its own column (measured: the `1` lands one pixel past `A`'s
    width plus the object's spacing 0).  Where a run STARTS is the alignment
    and the tab (`glyphs.Font.place`, LOOKS-TASK-38); how the pen moves
    inside one is what the spacing byte says.  The colour
    code moves nothing and does not end a run.
    """
    import screen

    screen.decode(raw)  # refuses a byte that is none of the three codes
    runs, current, at = [], [], 0
    while at < len(raw):
        byte = raw[at]
        if byte in (screen.NEWLINE, screen.TAB):
            runs.append(current)
            current = []
            at += 1 + (screen.TAB_ARGUMENTS if byte == screen.TAB else 0)
        elif byte == screen.COLOUR:
            at += 1 + screen.COLOUR_ARGUMENTS
        else:
            current.append(byte)
            at += 1
    runs.append(current)
    return [run for run in runs if run]


def glyph_objects(stream):
    """[{at, spacing, text, runs, problem}] out of one frame of stops.

    *stream* is the frame in the order the game ran it: `("object", at,
    spacing, string)` where `SCREEN_PRINT` is entered, `("glyph", code, x, y,
    measuring)` where `SCREEN_GLYPH` is.  The glyphs after an object's stop
    are that object's, up to the next one.  The frame is a cycle that began
    wherever the breakpoints first caught it, so it is turned to start at an
    object: the glyphs ahead of the first object stop are the last object's.

    Only the draw pass is kept, and it is cut into the runs of the object's
    own string (`pen_runs`) -- not by where the pen went, which is the thing
    under test.  An object whose draw pass is not its string's characters in
    order gets a `problem` instead of runs.
    """
    first = next((index for index, stop in enumerate(stream)
                  if stop[0] == "object"), None)
    if first is None:
        return []
    out, current = [], None
    for stop in stream[first:] + stream[:first]:
        if stop[0] == "object":
            current = {"at": stop[1], "spacing": stop[2], "text": stop[3],
                       "draws": [], "runs": [], "problem": None}
            out.append(current)
            continue
        _kind, code, x, y, measuring = stop
        if not measuring:
            current["draws"].append((code, x, y))
    for obj in out:
        draws = obj.pop("draws")
        if not draws:
            continue
        try:
            runs = pen_runs(obj["text"])
        except Exception as exc:  # noqa: BLE001 -- screen.BadScreen, reported
            obj["problem"] = "its string does not decode: %s" % exc
            continue
        codes = [code for run in runs for code in run]
        if codes != [code for code, _x, _y in draws]:
            obj["problem"] = ("it drew %r and its string holds %r"
                              % ("".join(chr(c) for c, _x, _y in draws),
                                 "".join(chr(c) for c in codes)))
            continue
        at = 0
        for run in runs:
            obj["runs"].append(draws[at:at + len(run)])
            at += len(run)
    return out


def pen_problems(font, objects, spacing=None):
    """(advances checked, [what differs]) of `Font.run` against the game.

    Each run of each object is laid out by the rule from the point where the
    game drew its first glyph -- where a run STARTS is the alignment, held
    by `--keys` since LOOKS-TASK-38 -- with the object's own spacing, or with *spacing* for
    every object when it is given (the control).  Every drawn glyph after the
    first has to land on the point the game's draw call gave it.
    """
    import who_writes

    checked, wrong = 0, []
    for obj in objects:
        gap = obj["spacing"] if spacing is None else spacing
        if obj["problem"]:
            wrong.append("object %s: %s" % (who_writes.hx(obj["at"]),
                                            obj["problem"]))
        for line in obj["runs"]:
            text = "".join(chr(code) for code, _x, _y in line)
            laid = [tuple(one["point"]) for one in
                    font.run(text, (line[0][1], line[0][2]), gap, (128,) * 3)]
            game = [(x, y) for code, x, y in line
                    if code != ord(" ") and font.glyph(code)[2]]
            checked += max(len(game) - 1, 0)
            if laid != game:
                at = next((index for index, pair in enumerate(zip(laid, game))
                           if pair[0] != pair[1]), min(len(laid), len(game)))
                wrong.append("object %s, %r at spacing %d: glyph %d laid at "
                             "%r, the game drew it at %r"
                             % (who_writes.hx(obj["at"]), text, gap, at,
                                laid[at] if at < len(laid) else None,
                                game[at] if at < len(game) else None))
    return checked, wrong


def measured_gaps(font, obj):
    """The gaps the game left inside one object: each draw call's x minus the
    previous one's x plus that glyph's width, over every run."""
    gaps = set()
    for line in obj["runs"]:
        for (code, x, _y), (_after, then, _y2) in zip(line, line[1:]):
            gaps.add(then - x - font.glyph(code)[2])
    return sorted(gaps)


def font_sprites(sprites):
    """The sprites of a frame that are font glyphs with something to draw.

    On the font's page, and wider than 0.  The game's draw pass skips the
    `GsSortSprite` (0x8003E8BC) for the space alone (the branch at
    0x8010C93C), so a code whose width is 0 -- `@`, `^` and `~` in this font
    -- still hands the GPU a sprite 0 texels wide, which draws nothing.
    `Font.run` leaves it out, as it leaves the space out, and this is where
    the game's side drops it to match (CORR-LOOKS-074): a count of font
    sprites is a count of glyphs that can put a pixel on screen.
    """
    return [one for one in sprites
            if tuple(one["page"]) == layout.GLYPH_PAGE and one["size"][0]]


def check_glyphs(slots=(2, 1), verbose=True):
    """`--glyphs [SLOT]`: the font rule against what the frame drew.

    For every glyph the draw pass reports -- code, x, y -- the rule of
    `glyphs.py`, read off the Japanese disc, says the `uv` and the size, and
    the frame's own list has to hold a sprite at that point with exactly
    those, on the font's page and in its CLUT.  Spaces draw nothing and have
    to have NO sprite.  Every font sprite of the frame has to be claimed by a
    glyph.  And the control: the same comparison with the table read one
    pair off must fail, which is what gives "all equal" its weight.

    And the pen (CORR-LOOKS-071): the print and the glyph routine are caught
    in one stream, so every glyph is known to belong to a text object and to
    that object's spacing byte; `Font.run` lays each line out from its first
    glyph, and every following glyph has to land where the game drew it.  The
    same layout with the spacing forced to each of `PEN_CONTROLS` for every
    object has to fail somewhere.
    """
    import glyphs
    import iso_source
    import who_writes

    ready = preflight()
    with iso_source.open_disc(ready["image"]) as disc:
        table = glyphs.table_of(disc.read(layout.SELECTC))
    font = glyphs.Font(table)
    shifted = glyphs.Font(table[2 * GLYPH_CONTROL:]
                          + table[:2 * GLYPH_CONTROL])
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        object_path = os.path.join(game.out_dir, "object.bin")
        for slot in slots:
            restore_state(slot, verbose=False)
            game.load_looks(slot)
            game.step(SCENERY_SETTLE)

            def read(registers):
                value = lambda name: who_writes.register_value(registers, name)
                if value("pc") == layout.SCREEN_PRINT:
                    raw = game.read_ram(value("a0"), OBJECT_SIZE, object_path)
                    pointer = struct.unpack_from("<I", raw, 8)[0]
                    text = (_cstring(game, pointer)
                            if RAM_BASE <= pointer < RAM_BASE + RAM_SIZE
                            else b"")
                    return ("object", value("a0"), raw[TEXT_SPACING], text)
                return ("glyph", value("a0"), _signed16(value("a1")),
                        _signed16(value("a2")), value("a3"))

            stream = _stops(game, (layout.SCREEN_GLYPH, layout.SCREEN_PRINT),
                            read, GLYPH_REPEAT, GLYPH_LIMIT + OBJECT_LIMIT)
            calls = [stop[1:] for stop in stream if stop[0] == "glyph"]
            objects = glyph_objects(stream)
            drawn = font_sprites(sprites_of(frame_commands(game)))
            at = {tuple(one["point"]): one for one in drawn}
            draws = [(code, x, y) for code, x, y, passing in calls
                     if not passing]
            equal, spaces, wrong, claimed = 0, 0, [], set()
            control, empty = 0, 0
            for code, x, y in draws:
                point = (x + SCENERY_CENTRE[0], y + SCENERY_CENTRE[1])
                u, v, width = font.glyph(code)
                found = at.get(point)
                if code == ord(" "):
                    spaces += 1
                    if found is not None:
                        wrong.append("a space at %r has a sprite" % (point,))
                    continue
                if not width:
                    # Its 0-wide sprite was dropped by `font_sprites`, and
                    # `Font.run` emits none (CORR-LOOKS-074).
                    empty += 1
                    continue
                if found is None:
                    wrong.append("%r at %r has no sprite" % (chr(code), point))
                    continue
                claimed.add(point)
                if (found["uv"] == (u, v) and found["size"] == (width,
                                                              layout.GLYPH_HEIGHT)
                        and tuple(found["clut"]) == layout.GLYPH_CLUT):
                    equal += 1
                else:
                    wrong.append("%r at %r: the rule says uv %r size %r and "
                                 "the frame drew uv %r size %r"
                                 % (chr(code), point, (u, v),
                                    (width, layout.GLYPH_HEIGHT),
                                    found["uv"], found["size"]))
                su, sv, swidth = shifted.glyph(code)
                control += (found["uv"] == (su, sv)
                            and found["size"][0] == swidth)
            unclaimed = [one["point"] for one in drawn
                         if tuple(one["point"]) not in claimed]
            print("  -- slot %d --" % slot)
            print("    %d glyph(s) drawn, %d space(s), %d of width 0; %d of %d "
                  "font sprite(s) equal to the rule in uv, size and CLUT, %d "
                  "unclaimed" % (len(draws), spaces, empty, equal, len(drawn),
                                 len(unclaimed)))
            print("    control: the table read %d pair(s) off matches %d of "
                  "them" % (GLYPH_CONTROL, control))
            problems += ["slot %d: %s" % (slot, line) for line in wrong]
            if unclaimed:
                problems.append("slot %d: %d font sprite(s) no glyph claims, "
                                "the first at %r" % (slot, len(unclaimed),
                                                     unclaimed[0]))
            if control == equal:
                problems.append("slot %d: the shifted table matches as often "
                                "as the real one, so equal says nothing"
                                % slot)
            checked, pen_wrong = pen_problems(font, objects)
            print("    pen: %d object(s), %d advance(s) laid by Font.run from "
                  "each run's first glyph, %d run(s) off"
                  % (len(objects), checked, len(pen_wrong)))
            for obj in objects:
                first = ("".join(chr(code) for code, _x, _y in obj["runs"][0])
                         if obj["runs"] else "")
                more = len(obj["runs"]) - 1
                print("      object %s  spacing byte %d  gaps drawn %s  %r%s"
                      % (who_writes.hx(obj["at"]), obj["spacing"],
                         measured_gaps(font, obj), first[:24],
                         " (+%d run(s))" % more if more > 0 else ""))
            problems += ["slot %d: pen: %s" % (slot, line)
                         for line in pen_wrong]
            if not checked:
                problems.append("slot %d: pen: no advance to check -- the "
                                "stream held no object with two glyphs" % slot)
            for forced in PEN_CONTROLS:
                _checked, off = pen_problems(font, objects, forced)
                print("    control: every object at spacing %d puts %d run(s) "
                      "off" % (forced, len(off)))
                if not off:
                    problems.append("slot %d: pen: spacing %d for every object "
                                    "fits as well as the objects' own, so the "
                                    "pen check says nothing" % (slot, forced))
    for line in problems[:20]:
        print("  FAIL  %s" % line)
    print("oracle --glyphs: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


# --- The help box: who writes its page, and where the texels come from ----

HELP_CONTROL_SECONDS = 6
"""Seconds the page is watched with NOTHING pressed before it is called still.

The control of the whole measurement: the page is written when the help text
changes, not every frame, so a hit here would mean the watchpoint is answering
about something else.  The frame cuts sprites from the page every frame; the
page's texels are not rewritten (2026-09-22)."""

HELP_FIRST_SECONDS = 12
HELP_NEXT_SECONDS = 4
"""How long the glyph lookup is waited for: the first stop after the press, and
each one after it.  A run of stops ends by SILENCE -- the string is rendered
once per press, so there is no repetition to close a frame with."""

HELP_STOP_LIMIT = 64
"""Stops taken before a run is refused.  The longest help string this screen
shows is 26 characters."""

JAL, ADDIU, ORI, JR_FUNCT = 3, 9, 13, 8
"""The instruction forms the chain below is decoded with: `jal`, `addiu`,
`ori`, and the function field of `jr`."""

HELP_TILES = 16
"""Tiles of the help page this watches and reads: the strip a help string is
rendered into, as wide as the longest string this screen shows."""

HELP_SPACE = 0x20  # not-an-address: the one-byte space of a help string
SJIS_FIRST = 0x8100  # not-an-address: the first two-byte Shift-JIS code

T1, T2, ZERO = 9, 10, 0
"""Register numbers of `t1`, `t2` and `zero`, for the BIOS stub."""

REGISTER_FIELD = 0x1F  # not-an-address: five bits of a register number
IMMEDIATE_FIELD = 0xFFFF  # not-an-address: sixteen bits of an immediate
JUMP_FIELD = 0x03FFFFFF  # not-an-address: twenty-six bits of a jal
FUNCT_FIELD = 0x3F  # not-an-address: six bits of a special instruction


def boot_code():
    """The boot executable's text segment and its load base, through the guard.

    The base is READ OUT OF THE FILE and checked against `layout.BOOT_BASE`,
    not taken from it: every address below becomes a file offset through it,
    and a header that said something else would make each of them point at the
    wrong bytes in silence.
    """
    import iso_source
    import who_writes

    ready = preflight()
    with iso_source.open_disc(ready["image"]) as disc:
        data = disc.read(layout.BOOT)
    if data[:len(layout.BOOT_MAGIC)] != layout.BOOT_MAGIC:
        raise OracleError("%s does not open with %r, so it is not the boot "
                          "executable" % (layout.BOOT, layout.BOOT_MAGIC))
    base = struct.unpack_from("<I", data, layout.BOOT_LOAD_FIELD)[0]
    size = struct.unpack_from("<I", data, layout.BOOT_SIZE_FIELD)[0]
    if base != layout.BOOT_BASE:
        raise OracleError("%s says it loads at %s and this cycle's addresses "
                          "are read against %s"
                          % (layout.BOOT, who_writes.hx(base),
                             who_writes.hx(layout.BOOT_BASE)))
    return data[layout.BOOT_HEADER:layout.BOOT_HEADER + size], base


def boot_word(code, base, address):
    """The instruction at *address*, out of the file's text segment."""
    import who_writes

    at = address - base
    if not 0 <= at <= len(code) - INSTRUCTION_SIZE:
        raise OracleError("%s is outside the boot executable's %d byte(s)"
                          % (who_writes.hx(address), len(code)))
    return struct.unpack_from("<I", code, at)[0]


def _jal_target(word):
    """Where a `jal` goes, or None if the word is not one."""
    if word >> 26 != JAL:
        return None
    return (word & JUMP_FIELD) << 2 | RAM_BASE


def _addiu(word):
    """(rt, rs, immediate) of an `addiu`, or None if the word is not one."""
    if word >> 26 != ADDIU:
        return None
    return ((word >> 16) & REGISTER_FIELD, (word >> 21) & REGISTER_FIELD,
            word & IMMEDIATE_FIELD)


def help_chain(code, base):
    """The instructions that make the help box's glyphs the console's.

    Decoded out of `/SLPM_870.56`, each one refused unless it is what `layout`
    says it is.  What the chain says, in order:

      * `HELP_GLYPH_CALL` is a `jal` to `HELP_GLYPH_LOOKUP`, and the answer
        comes back at `HELP_GLYPH_RETURN`, two instructions later -- the delay
        slot between them is what finishes the Shift-JIS code;
      * the lookup reaches `KROM_STUB`, once per range of codes it accepts;
      * the stub is a BIOS call -- `t2` the kernel's jump vector `KROM_TABLE`,
        `t1` the function number `KROM_FUNCTION`.

    Returns what was found, for the report to print.
    """
    import who_writes

    call = boot_word(code, base, layout.HELP_GLYPH_CALL)
    target = _jal_target(call)
    if target != layout.HELP_GLYPH_LOOKUP:
        raise OracleError("%s is not a jal to %s: %#010x"
                          % (who_writes.hx(layout.HELP_GLYPH_CALL),
                             who_writes.hx(layout.HELP_GLYPH_LOOKUP), call))
    if layout.HELP_GLYPH_RETURN != layout.HELP_GLYPH_CALL + 2 * INSTRUCTION_SIZE:
        raise OracleError("%s is not the instruction after the call's delay "
                          "slot" % who_writes.hx(layout.HELP_GLYPH_RETURN))
    calls = [at for at in range(layout.HELP_GLYPH_LOOKUP,
                                layout.HELP_GLYPH_LOOKUP
                                + layout.HELP_LOOKUP_WORDS * INSTRUCTION_SIZE,
                                INSTRUCTION_SIZE)
             if _jal_target(boot_word(code, base, at)) == layout.KROM_STUB]
    if not calls:
        raise OracleError("%s never reaches %s in its first %d instruction(s)"
                          % (who_writes.hx(layout.HELP_GLYPH_LOOKUP),
                             who_writes.hx(layout.KROM_STUB),
                             layout.HELP_LOOKUP_WORDS))
    vector = _addiu(boot_word(code, base, layout.KROM_STUB))
    jump = boot_word(code, base, layout.KROM_STUB + INSTRUCTION_SIZE)
    number = _addiu(boot_word(code, base,
                              layout.KROM_STUB + 2 * INSTRUCTION_SIZE))
    if vector != (T2, ZERO, layout.KROM_TABLE):
        raise OracleError("%s does not load %s into t2: %r"
                          % (who_writes.hx(layout.KROM_STUB),
                             who_writes.hx(layout.KROM_TABLE), vector))
    if (jump >> 26 or jump & FUNCT_FIELD != JR_FUNCT
            or (jump >> 21) & REGISTER_FIELD != T2):
        raise OracleError("the word after %s is not `jr t2`: %#010x"
                          % (who_writes.hx(layout.KROM_STUB), jump))
    if number != (T1, ZERO, layout.KROM_FUNCTION):
        raise OracleError("%s does not load %#x into t1: %r"
                          % (who_writes.hx(layout.KROM_STUB
                                           + 2 * INSTRUCTION_SIZE),
                             layout.KROM_FUNCTION, number))
    return {"lookup": layout.HELP_GLYPH_LOOKUP, "calls": calls,
            "table": layout.KROM_TABLE, "function": layout.KROM_FUNCTION}


def help_special_codes(code, base):
    """The character codes the renderer draws from VRAM instead of rendering.

    Read out of the dispatch itself (`layout.HELP_SPECIAL_SPAN`): every
    `ori v0, zero, <code>` in it whose immediate is a two-byte Shift-JIS code.
    Refused unless there are as many as `layout.HELP_SPECIAL_COUNT` -- a span
    that stopped naming them would otherwise turn "not asked of the ROM" into
    a silent miss instead of a measurement.
    """
    import who_writes

    out = []
    for at in range(layout.HELP_SPECIAL_SPAN[0], layout.HELP_SPECIAL_SPAN[1],
                    INSTRUCTION_SIZE):
        word = boot_word(code, base, at)
        if word >> 26 != ORI or (word >> 21) & REGISTER_FIELD != ZERO:
            continue
        immediate = word & IMMEDIATE_FIELD
        if immediate >= SJIS_FIRST and immediate not in out:
            out.append(immediate)
    if len(out) != layout.HELP_SPECIAL_COUNT:
        raise OracleError("%s to %s names %d code(s) and this cycle measured "
                          "%d: %s"
                          % (who_writes.hx(layout.HELP_SPECIAL_SPAN[0]),
                             who_writes.hx(layout.HELP_SPECIAL_SPAN[1]),
                             len(out), layout.HELP_SPECIAL_COUNT,
                             ["%#06x" % one for one in out]))
    return sorted(out)


def krom_ink(raw):
    """The set pixels of one character of the console's ROM.

    Thirty bytes, fifteen rows of sixteen bits, each row a BIG-endian halfword
    -- which is why the game byte-swaps every row on its way to the
    scratchpad.
    """
    if len(raw) < layout.HELP_GLYPH_BYTES:
        raise OracleError("a glyph is %d bytes and this is %d"
                          % (layout.HELP_GLYPH_BYTES, len(raw)))
    width, height = layout.HELP_GLYPH_SIZE
    return {(x, y) for y in range(height) for x in range(width)
            if struct.unpack_from(">H", raw, 2 * y)[0] & (1 << (width - 1 - x))}


def tile_ink(rows, bits=4):
    """The texels of one tile of a page that are not the transparent index.

    *rows* are VRAM halfwords, as `_halfword` reads them: the fork hands VRAM
    back as a PNG, so the top bit of each halfword does not survive
    (`COLOUR_BITS`).  That is enough here and only here -- what is asked of a
    texel is whether it is zero, and the two indices this page is drawn with
    are 15 and 3, of which 15 in the top nibble reads back as 7, still ink.
    """
    per = TEXELS_PER_HALFWORD[bits]
    out = set()
    for y, row in enumerate(rows):
        for index, value in enumerate(row):
            for texel in range(per):
                if (value >> (bits * texel)) & ((1 << bits) - 1):
                    out.add((per * index + texel, y))
    return out


def _dilated(ink):
    """*ink* grown by one pixel in every direction -- the outline the game
    smears around a glyph before it uploads the tile."""
    return {(x + dx, y + dy) for x, y in ink
            for dx in (-1, 0, 1) for dy in (-1, 0, 1)}


def glyph_in_tile(bitmap, ink):
    """What separates the tile the game uploaded from the ROM's bitmap.

    `(missing, extra)`: pixels the ROM sets that the tile has no texel for, and
    texels outside the bitmap grown by one.  The game draws the glyph in one
    index and smears a one-pixel outline in another, so the tile's ink is the
    bitmap plus at most that ring.
    """
    return sorted(bitmap - ink), sorted(ink - _dilated(bitmap))


def help_tiles(game, count):
    """The first *count* tiles of the help page, each as its set of ink."""
    x, y = layout.HELP_PAGE
    per = TEXELS_PER_HALFWORD[4]
    wide = layout.HELP_TILE // per
    out = []
    for index in range(count):
        rows = vram_region(game, x + wide * index, y, wide, layout.HELP_TILE)
        out.append(tile_ink([[_halfword(pixel) for pixel in row]
                             for row in rows]))
    return out


def help_page_sprites(game):
    """The sprites of the frame that are cut from the help page."""
    heads = gpu_list_heads(game)
    first, size, step = layout.SCENERY_SWEEP
    ram = b"".join(game.read_ram(base, step, os.path.join(
        game.out_dir, "help-%08x.bin" % base))
        for base in range(first, first + size, step))
    nodes = []
    for head in dict.fromkeys(heads[len(heads) // 2:]):
        nodes += walk_gpu_list(ram, head)
    return [one for one in sprites_of(commands_of(nodes))
            if tuple(one["page"]) == layout.HELP_PAGE]


def _page_still(game):
    """True if nothing wrote the help page while nothing was pressed."""
    game.client.call("continue")
    return not _wait_for_hit(game, HELP_CONTROL_SECONDS)



def krom_answers(game, button="Down"):
    """(string pointer, glyph address) at every glyph lookup one press makes.

    Ends in SILENCE: the string is rendered once, when the help text changes,
    so there is no frame coming round to close the run with.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.HELP_GLYPH_RETURN))
    out = []
    try:
        client.call("continue")
        client.call("press_button", button=button,
                    duration_frames=CONFIRM_FRAMES)
        while True:
            if not _wait_for_hit(game, HELP_FIRST_SECONDS if not out
                                 else HELP_NEXT_SECONDS):
                return out
            registers = client.call("read_registers", group="gpr")
            out.append((who_writes.register_value(registers, "s3"),
                        who_writes.register_value(registers, "v0")))
            if len(out) > HELP_STOP_LIMIT:
                raise OracleError(
                    "%s stopped more than %d time(s) for one press"
                    % (who_writes.hx(layout.HELP_GLYPH_RETURN),
                       HELP_STOP_LIMIT))
            client.call("continue")
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass


def _in_bios(address):
    base, size = layout.BIOS_ROM
    return base <= address < base + size


def _help_writes(game):
    """Every write to the help page one press causes: (rect, pc) each.

    The rectangle is the measurement; the pc beside it is NOT.  The copy is a
    DMA, so the program counter at the moment the GPU touches VRAM is wherever
    the CPU has got to by then -- it read 0x8003A950 twice in a row while this
    was being written and then 0x8003F2F4 and 0x8010A910 on the next two runs,
    which is what a number with no meaning looks like when it is stable.

    The run ends in silence, and one press gives ONE hit: the watch reports
    the last write of the batch rather than every one of them, so what this
    says is the shape of the write and which tile it landed in, never how
    many tiles the press wrote.
    """
    import who_writes

    client = game.client
    client.call("press_button", button="Down", duration_frames=CONFIRM_FRAMES)
    out = []
    while _wait_for_hit(game, HELP_FIRST_SECONDS if not out
                        else HELP_NEXT_SECONDS):
        hit = client.call("vram_watch", action="last_hit")
        out.append(((hit.get("x"), hit.get("y"), hit.get("width"),
                     hit.get("height")), hit.get("pc")))
        if len(out) > HELP_STOP_LIMIT:
            raise OracleError("the page was written more than %d time(s) for "
                              "one press" % HELP_STOP_LIMIT)
        client.call("continue")
    if not out:
        raise OracleError("Down wrote nothing to the page at %r in %ds, so "
                          "the watchpoint has nothing to say"
                          % (layout.HELP_PAGE, HELP_FIRST_SECONDS))
    return out


def help_bytes(game):
    """The help box's string as the overlay holds it: Shift-JIS, with the
    single-byte spaces that move the pen without drawing."""
    path = os.path.join(game.out_dir, "help-string.bin")
    pointer = struct.unpack("<I", game.read_ram(layout.SCREEN_HELP, 4,
                                                path))[0]
    if not RAM_BASE <= pointer < RAM_BASE + RAM_SIZE:
        raise OracleError("the help pointer holds %#x, which is not RAM"
                          % pointer)
    return _cstring(game, pointer)


def help_pieces(raw, special):
    """[(code, from the ROM?)] for the characters of a help string that draw.

    A single-byte space moves the pen and draws nothing, so it takes no tile.
    Every other character is two bytes, big-endian, and takes one -- asked of
    the console's ROM unless its code is one of *special*, the handful the
    renderer draws from VRAM instead.
    """
    out, at = [], 0
    while at < len(raw):
        if raw[at] == HELP_SPACE:
            at += 1
            continue
        if at + 1 >= len(raw):
            raise OracleError("the help string ends inside a character: %r"
                              % raw[-4:])
        code = raw[at] << 8 | raw[at + 1]
        out.append((code, code not in special))
        at += 2
    return out


def check_help_box(slots=(2, 1), verbose=True):
    """`--help-box [SLOT]`: who writes the help page, and where from.

    The question of section 10.3 (o) about the help box, and the answer is
    that the disc has nothing to do with it.  What is measured, each with its
    control:

      **the page is still** unless the help text changes -- a VRAM write
          watchpoint over it hears nothing with nothing pressed;
      **one press writes it** one 16x16 tile at a time -- four halfwords by
          sixteen rows of a 4-bit page, inside the strip.  How MANY tiles is
          not read off the watchpoint: it reports one hit for the press, the
          last of the batch, and the count comes from the lookups and the
          sprites below, which are exact;
      **every letter comes from the console's ROM** -- the address the lookup
          answers with is inside `layout.BIOS_ROM` for every character asked
          of it, and the characters NOT asked are exactly the codes the
          dispatch names (`help_special_codes`), of which `■` is one;
      **the ROM's bitmap IS the tile** -- the 16x15 bits at that address are
          the tile's ink up to the one-pixel outline the game smears around
          them, and the next character's bitmap is not.
    """
    import screen
    import who_writes

    table = screen.load()
    code, base = boot_code()
    chain = help_chain(code, base)
    special = help_special_codes(code, base)
    row = ROWS[ROWS.index(CURSOR_STARTS_ON) + 1]
    wide = layout.HELP_TILE // TEXELS_PER_HALFWORD[4]
    print("  the chain, decoded from %s (%d bytes of code):"
          % (layout.BOOT, len(code)))
    print("    %s jal %s, which calls %s at %s -- the BIOS vector %s, "
          "function %#x"
          % (who_writes.hx(layout.HELP_GLYPH_CALL),
             who_writes.hx(chain["lookup"]), who_writes.hx(layout.KROM_STUB),
             ", ".join(who_writes.hx(one) for one in chain["calls"]),
             who_writes.hx(chain["table"]), chain["function"]))
    print("    and %d code(s) the dispatch draws from VRAM instead: %s"
          % (len(special), ", ".join("%#06x" % one for one in special)))
    problems = []
    ready = preflight()
    with Oracle(ready["cue"], verbose=verbose) as game:
        client = game.client
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, SLOTS[slot]))
            restore_state(slot, verbose=False)
            game.load_looks(slot, label="help-%d" % slot)
            game.step(SCENERY_SETTLE)
            client.call("breakpoint", action="clear")
            watch = client.call("vram_watch", action="add",
                                x=layout.HELP_PAGE[0], y=layout.HELP_PAGE[1],
                                width=wide * HELP_TILES,
                                height=layout.HELP_TILE)
            try:
                still = _page_still(game)
                print("    control: with nothing pressed, nothing wrote the "
                      "page in %ds: %s"
                      % (HELP_CONTROL_SECONDS,
                         "still" if still else "IT FIRED"))
                if not still:
                    problems.append("slot %d: the page is written with "
                                    "nothing pressed, so the press below "
                                    "proves nothing" % slot)
                writes = _help_writes(game)
            finally:
                client.call("vram_watch", action="remove",
                            id=watch.get("id", 1))
            shapes = {one[0][2:] for one in writes}
            tiles_written = sorted({(one[0][0] - layout.HELP_PAGE[0]) // wide
                                    for one in writes})
            print("    one Down wrote the page: %d hit(s), %s, tile(s) %s "
                  "of the strip"
                  % (len(writes),
                     ", ".join("%sx%s" % one for one in sorted(shapes)),
                     ",".join("%d" % one for one in tiles_written)))
            print("      (the pc at each: %s -- printed, not asserted: the "
                  "copy is a DMA, and the watch reports one hit for the "
                  "press, not one per tile)"
                  % ", ".join(sorted({str(one[1]) for one in writes})))
            if shapes != {(wide, layout.HELP_TILE)}:
                problems.append("slot %d: the page was written in %s, not in "
                                "%dx%d tiles of a 4-bit page"
                                % (slot, sorted(shapes), wide,
                                   layout.HELP_TILE))
            if any(one < 0 or one >= HELP_TILES for one in tiles_written):
                problems.append("slot %d: the press wrote tile(s) %s, outside "
                                "the %d of the strip"
                                % (slot, tiles_written, HELP_TILES))
            answers, pieces = None, None
            runs = []
            for _ in range(2):
                restore_state(slot, verbose=False)
                game.load_looks(slot)
                game.step(SCENERY_SETTLE)
                runs.append(krom_answers(game))
            if runs[0] != runs[1]:
                problems.append("slot %d: the same press read twice asks for "
                                "%d and %d glyph(s), so nothing below is "
                                "measured"
                                % (slot, len(runs[0]), len(runs[1])))
                continue
            answers = runs[0]
            print("    control: the same press twice asks for the same %d "
                  "glyph(s)" % len(answers))
            game.step(SCENERY_SETTLE)
            raw = help_bytes(game)
            text = screen.help_text(raw)
            pieces = help_pieces(raw, special)
            asked = [one for one in pieces if one[1]]
            print("    the box now shows the %s help, %r: %d character(s) "
                  "that draw, %d of them asked of the ROM and %d drawn from "
                  "VRAM (%s)"
                  % (row, text, len(pieces), len(asked),
                     len(pieces) - len(asked),
                     ", ".join("%#06x" % one for one, ask in pieces
                               if not ask) or "none"))
            if text != table["rows"][row]["help"]:
                problems.append("slot %d: the box shows %r and the table says "
                                "%r" % (slot, text,
                                        table["rows"][row]["help"]))
            outside = [one for _at, one in answers if not _in_bios(one)]
            print("    %d lookup(s), %d answer(s) outside the console's ROM "
                  "at %s+%#x; the first %s -> %s, the last %s -> %s"
                  % (len(answers), len(outside),
                     who_writes.hx(layout.BIOS_ROM[0]), layout.BIOS_ROM[1],
                     who_writes.hx(answers[0][0]),
                     who_writes.hx(answers[0][1]),
                     who_writes.hx(answers[-1][0]),
                     who_writes.hx(answers[-1][1])))
            if outside:
                problems.append("slot %d: %d glyph address(es) are not in the "
                                "console's ROM, the first %s"
                                % (slot, len(outside),
                                   who_writes.hx(outside[0])))
            if len(answers) != len(asked):
                problems.append("slot %d: %d lookup(s) for the %d character(s)"
                                " of the %s help that are not a special code"
                                % (slot, len(answers), len(asked), row))
                continue
            drawn = help_page_sprites(game)
            print("    the frame cuts %d sprite(s) from the page, %d of them "
                  "on the CLUT %r"
                  % (len(drawn), sum(1 for one in drawn
                                     if tuple(one["clut"])
                                     == layout.HELP_CLUT),
                     list(layout.HELP_CLUT)))
            if len(drawn) != len(pieces):
                problems.append("slot %d: %d sprite(s) off the page against "
                                "%d character(s) that draw"
                                % (slot, len(drawn), len(pieces)))
            tiles = help_tiles(game, len(pieces))
            bitmaps, waiting = {}, list(answers)
            for index, (_code, ask) in enumerate(pieces):
                if ask:
                    _at, address = waiting.pop(0)
                    bitmaps[index] = krom_ink(game.read_ram(
                        address, layout.HELP_GLYPH_BYTES,
                        os.path.join(game.out_dir, "help-glyph.bin")))
            same, off, control = 0, [], 0
            for index, bitmap in sorted(bitmaps.items()):
                missing, extra = glyph_in_tile(bitmap, tiles[index])
                if not missing and not extra:
                    same += 1
                else:
                    off.append("tile %d: %d pixel(s) of the ROM's glyph are "
                               "not in it, and %d texel(s) fall outside that "
                               "glyph's outline"
                               % (index, len(missing), len(extra)))
                if index + 1 < len(tiles) and index + 1 in bitmaps:
                    control += not any(glyph_in_tile(bitmap,
                                                     tiles[index + 1]))
            print("    %d of %d tile(s) are the ROM's bitmap plus its "
                  "one-pixel outline; control: the NEXT character's tile "
                  "takes %d of those bitmaps" % (same, len(bitmaps), control))
            problems += ["slot %d: %s" % (slot, line) for line in off]
            if control:
                problems.append("slot %d: %d bitmap(s) fit the next "
                                "character's tile as well, so equal says "
                                "nothing" % (slot, control))
    for line in problems[:20]:
        print("  FAIL  %s" % line)
    print("oracle --help-box: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0



def _screen_geometry(table):
    """The four numbers `ScreenReading` needs, out of the measured table."""
    return {"row0_y": table["row0_y"], "pitch": table["pitch"],
            "left": table["rows_left"], "top": table["rows_top"]}


def _press_sequence(game, slot, buttons, geometry, orders, table):
    """*buttons* from a fresh `load_state`, and what the screen then shows --
    the cursor box included, read off VRAM (CORR-LOOKS-070)."""
    game.load_looks(slot)
    for button in buttons:
        tap(game, button)
    reading = ScreenReading(geometry, screen_objects(game))
    display = tuple(table["display"])
    regions = {name: box["native"] for name, box in table["regions"].items()}
    frames, _ = screen_frames(game, display)
    _row, box = _cursor_row(frames, regions, geometry,
                            (display[0] // 2, display[1] // 2))
    return {"rows": reading.rows(orders), "help": screen_help(game),
            "arrows": frame_arrows(game), "cursor": list(box),
            "glyphs": frame_glyphs(game)}


def window_cursor(rows, width, table):
    """The yellow box in a picture of OUR window, in the game's native pixels.

    Read off the picture the window wrote, never asked of the window: its
    report says which row the cursor is on, not where it drew the box, and
    the box is what CORR-LOOKS-070 found wrong.  The picture is the display
    times the window's scale, so the scale is the width over the display's
    and has to divide it; the box is looked for inside the rows box, the way
    `_cursor_row` looks for the game's.
    """
    import screen

    native_width, _native_height = table["display"]
    if width % native_width:
        raise OracleError("the window's picture is %d wide, which is not a "
                          "whole multiple of the display's %d"
                          % (width, native_width))
    scale = width // native_width
    x0, y0, x1, y1 = table["regions"]["rows"]["native"]
    found = screen.cursor(rows, (x0 * scale, y0 * scale,
                                 (x1 + 1) * scale - 1, (y1 + 1) * scale - 1))
    if found is None:
        return None
    return [found[0] // scale, found[1] // scale,
            found[2] // scale, found[3] // scale]


def _window_sequence(slot, buttons, verbose=True, shot=None):
    """The same buttons into OUR window, or None if the venv is not here.

    Spawned rather than imported: the window needs PySide6, which lives in
    `work/venv-looks` and not in the interpreter that drives the emulator.
    """
    import subprocess

    import ui_check

    python = ui_check.venv_python()
    if python is None or not os.path.isfile(ui_check.APP):
        return None
    arguments = ["--state", str(slot), "--keys", ",".join(buttons)]
    arguments += ["--screenshot", shot] if shot else ["--smoke"]
    code, output = ui_check.run_app(python, ui_check.APP, arguments,
                                    ui_check.environment())
    if code != 0:
        raise OracleError("the window exited %s on the same keys: %s"
                          % (code, output.rstrip()))
    seen = ui_check.read_screen(output)
    if not seen.get("rows"):
        raise OracleError("the window printed no screen report")
    if verbose:
        print("  the window answered the same %d press(es)" % len(buttons))
    return seen


def check_keys(sequence=None, slot=2, verbose=True):
    """`--keys`: the same presses in the game and in our window, text by text.

    This is comparison (1) of section 10.4 of the plan, and the shape of it is
    the point:

      the CONTROL comes first -- the same sequence twice in the GAME, from
          `load_state` both times, and the twelve rows have to come back
          identical.  Without it a disagreement below says nothing about the
          window, because nothing has shown the game answers a sequence the
          same way twice;
      then the game against `screen.py`, which is what the table claims a
          press does;
      then the game against OUR WINDOW, which is what the task delivers.

    Every text is read by tool on both sides: the game's off the objects it
    prints, the window's off its own report.  Nothing here is transcribed.
    """
    import screen

    table = screen.load()
    buttons = screen.parse_keys(sequence) if sequence else screen.parse_keys(
        KEY_SEQUENCE)
    geometry = _screen_geometry(table)
    orders = table["orders"]

    ready = preflight()
    with Oracle(ready["cue"], verbose=verbose) as game:
        restore_state(slot, verbose=verbose)
        if verbose:
            print("  pressing %d button(s) in slot %d: %s"
                  % (len(buttons), slot, ",".join(buttons)))
        first = _press_sequence(game, slot, buttons, geometry, orders, table)
        again = _press_sequence(game, slot, buttons, geometry, orders, table)
        # The pair a person looks at, both written by tool: the game's frame
        # after the presses, and ours after the same ones.
        theirs = game.capture("keys-slot%d" % slot)
        ours_shot = os.path.join(game.out_dir, "keys-slot%d-window.png" % slot)

    control = [(name, first["rows"][name], again["rows"][name])
               for name in table["order_of_rows"]
               if first["rows"][name] != again["rows"][name]]
    if first["help"] != again["help"]:
        control.append(("help", first["help"], again["help"]))
    if first["arrows"] != again["arrows"]:
        control.append(("arrows", first["arrows"], again["arrows"]))
    if first["glyphs"] != again["glyphs"]:
        control.append(("glyphs", len(first["glyphs"]), len(again["glyphs"])))
    if first["cursor"] != again["cursor"]:
        control.append(("the cursor box", first["cursor"], again["cursor"]))
    for name, one, two in control:
        print("  FAIL  control: the game answered the same sequence with %s "
              "%r and then %r" % (name, one, two))
    if control:
        print("oracle --keys: the control failed, so nothing the window does "
              "would mean anything")
        return 1
    print("  control: the same sequence twice in the game gives the same "
          "twelve rows, the same help, the same arrows, the same cursor "
          "box and the same %d glyph(s)" % len(first["glyphs"]))

    state = screen.State(table, slot)
    state.press_all(buttons)
    ours = {"rows": state.texts(), "help": state.help_text(),
            "arrows": state.arrows(), "cursor": state.cursor_box()}
    window = _window_sequence(slot, buttons, verbose, ours_shot)
    if window is not None:
        import atlas

        print("  the pair to look at: the game %s, our window %s"
              % (theirs.path, ours_shot))
        width, _height, pixels = atlas.read_png(ours_shot)
        window["cursor"] = window_cursor(pixels, width, table)

    bad = []
    for name in table["order_of_rows"]:
        played = first["rows"][name]
        if ours["rows"][name] != played:
            bad.append("%s: the game shows %r and screen.json says a press "
                       "leaves %r" % (name, played, ours["rows"][name]))
        if window is not None and window["rows"].get(name) != played:
            bad.append("%s: the game shows %r and our window shows %r"
                       % (name, played, window["rows"].get(name)))
    if ours["help"] != first["help"]:
        bad.append("the help: the game shows %r and screen.json says %r"
                   % (first["help"], ours["help"]))
    if window is not None and window.get("help") != first["help"]:
        bad.append("the help: the game shows %r and our window shows %r"
                   % (first["help"], window.get("help")))
    if ours["arrows"] != first["arrows"]:
        bad.append("the arrows: the game draws %s and screen.json says %s"
                   % (_say_arrows(first["arrows"]), _say_arrows(ours["arrows"])))
    if window is not None and window.get("arrows") != first["arrows"]:
        bad.append("the arrows: the game draws %s and our window draws %s"
                   % (_say_arrows(first["arrows"]),
                      _say_arrows(window.get("arrows"))))
    if window is not None:
        bad += _glyph_differences(first["glyphs"], window.get("glyphs") or [])
    if ours["cursor"] != first["cursor"]:
        bad.append("the cursor box: the game draws %r and screen.json says %r"
                   % (first["cursor"], ours["cursor"]))
    if window is not None and window.get("cursor") != first["cursor"]:
        bad.append("the cursor box: the game draws %r and our window draws %r"
                   % (first["cursor"], window.get("cursor")))
    for line in bad:
        print("  FAIL  %s" % line)
    if verbose and not bad:
        for name in table["order_of_rows"]:
            print("    %-9s %r" % (name, first["rows"][name]))
        print("    help      %r" % first["help"])
        print("    arrows    %s" % _say_arrows(first["arrows"]))
        print("    cursor    %r" % (first["cursor"],))
    _say_arrow_cluts()
    print("oracle --keys: %d difference(s) after %d press(es), across the "
          "game, screen.json and %s"
          % (len(bad), len(buttons),
             "our window" if window is not None else "no window (no venv)"))
    return 1 if bad else 0


CTC2_MASK = 0xFFE00000  # not-an-address: the opcode field of an instruction
CTC2_OPCODE = 0x48C00000  # not-an-address: COP2 + CT, an instruction
"""`ctc2 rt, rd` -- a write into a GTE CONTROL register.

Not an address, and the sweep is right that it is a number: it is an opcode,
like the GPU commands above.  COP2 is 010010 in the top six bits and CT is
00110 in the next five, which is what these two constants spell.
"""

MATRIX_REGISTER = 0
"""GTE control register 0, the first word of the rotation matrix (R11R12).

A `ctc2` into it is the start of a matrix load, which is why the scan looks
for that one register rather than for every `ctc2`: 261 of those are in RAM
and 30 write this one.
"""

POSE_FRAMES = 4
"""Frames watched at the matrix instruction, so the count per frame is a
count and not a sample."""

WATCH_LIMIT = 8
"""Seconds a read watchpoint is given before silence counts as silence."""


def _ctc2_matrix_loads(ram):
    """Every instruction in RAM that writes the GTE's first matrix word."""
    out = []
    # `len(ram) - 3` and not `- 4`: the last whole word is a word like any
    # other, and stopping short of it left a four-byte input with nothing to
    # scan -- which is exactly what the self-check below hands it.
    for offset in range(0, len(ram) - 3, 4):
        word = int.from_bytes(ram[offset:offset + 4], "little")
        if (word & CTC2_MASK) != CTC2_OPCODE:
            continue
        if ((word >> 11) & 0x1F) == MATRIX_REGISTER:  # not-an-address: rd field
            out.append(RAM_BASE + offset)
    return out


NATIONS = ("Ireland", "Sweden", "Brazil", "Japan", "Nigeria", "Algeria")
"""The nations `--default` walks to: spread across the row, and one of them --
`Brazil`, skin B -- has a file line that is not all `A`, which is what tells
"the default was applied" from "nothing happened to a look that was already
the default".  `Algeria` is there because the index pairing puts a CLUB's line
on it (`looks.nation_by_index`), so a run that silently paired by index would
have to disagree with the game somewhere visible."""

LOOK_ROWS = ("SKIN", "HAIR", "H.COL", "FACE", "H.F.COL.")
"""The five the file has a column for, and the five a default would move."""

CONFIRM_SETTLE = 120
"""Frames given to the fade after Circle on `DEFAUL`.  The screen leaves, and
a frame read before the fade is over is black and says nothing."""


def _nation_byte(game, slot=None):
    """The two copies of the nationality, as the machine holds them now."""
    path = os.path.join(game.out_dir, "nation.bin")
    return [game.read_ram(address, 1, path)[0]
            for address in layout.PLAYER_NATION]


def _anime_in_ram(game, image, verbose=True):
    """The whole of ANIME.BIN against RAM at `layout.ANIME_BASE`."""
    import iso_source

    with iso_source.open_disc(image) as disc:
        want = disc.read(layout.ANIME)
    path = os.path.join(game.out_dir, "ram-anime.bin")
    got = game.read_ram(layout.ANIME_BASE, len(want), path)
    same = sum(1 for a, b in zip(want, got) if a == b)
    if verbose:
        print("  %s at %#010x: %d of %d byte(s) equal"
              % (layout.ANIME, layout.ANIME_BASE, same, len(want)))
    return want, same


def _watch_reads(game, addresses, seconds=WATCH_LIMIT, stops=1):
    """Arm a read watchpoint on each of *addresses* and run.

    Returns `(hits, pcs)`: the watches that fired with their counts, and the
    program counters that were sitting on them.  **All of them at once**: a
    sample of four of this file's 204 header entries read as silence, and the
    one entry the game does read is the sixth.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    for address in addresses:
        client.call("breakpoint", action="add", type="read",
                    address=who_writes.hx(address))
    pcs = {}
    try:
        for _ in range(stops):
            client.call("continue")
            if not _wait_for_hit(game, seconds):
                break
            pc = who_writes.register_value(
                client.call("read_registers", group="all"), "pc")
            pcs[pc] = pcs.get(pc, 0) + 1
        listed = client.call("breakpoint", action="list")
        hits = [(int(w["address"], 16), w["hit_count"]) for w in listed
                if w["hit_count"]]
    finally:
        try:
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
        client.call("breakpoint", action="clear")
    return hits, pcs


def check_pose(slot=None, verbose=True):
    """`--pose`: where the pose on the LOOKS SET screen comes from.

    The incognita this answers is the riskiest of the v2, and the shape of the
    run is the argument:

      **is the file even there** -- the whole of ANIME.BIN against RAM at
          `layout.ANIME_BASE`, byte for byte, on both states;
      **is it read** -- a read watchpoint on every one of the 204 header
          entries at once, and the entry that fires named.  The control for
          the instrument comes first: a read watchpoint on a text object the
          print routine is handed has to fire, or silence over the file would
          mean nothing;
      **where the matrix reaches the GTE** -- every `ctc2` in RAM that writes
          the matrix's first control register, armed together, and the one
          that fires on this screen;
      **how many pieces pass through it** in one frame.
    """
    import who_writes

    ready = preflight()
    slots = (slot,) if slot else tuple(sorted(SLOTS))
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in slots:
            restore_state(one, verbose=verbose)
            game.load_looks(one)
            print("  -- slot %d (%s) --" % (one, SLOTS[one]))

            want, same = _anime_in_ram(game, ready["image"], verbose)
            if same != len(want):
                problems.append("slot %d: %d of %d bytes of %s differ at "
                                "%#010x" % (one, len(want) - same, len(want),
                                            layout.ANIME, layout.ANIME_BASE))

            # The control for the instrument, before the silence is read as an
            # answer: a text object the print routine is handed every frame.
            objects = screen_objects(game)
            control, _pcs = _watch_reads(game, [objects[0]["at"]])
            if not control:
                problems.append("slot %d: a read watchpoint on the text object "
                                "at %#010x never fired, so this build cannot "
                                "tell 'not read' from 'not watched'"
                                % (one, objects[0]["at"]))
                continue
            print("    control: the text object at %s is read, so a read "
                  "watchpoint fires on this build"
                  % who_writes.hx(objects[0]["at"]))

            header = [layout.ANIME_BASE + 4 * word
                      for word in range(layout.ANIME_HEADER_WORDS)]
            hits, pcs = _watch_reads(game, header, stops=3)
            if not hits:
                problems.append("slot %d: none of the %d header entries of %s "
                                "was read" % (one, len(header), layout.ANIME))
            else:
                for address, count in hits:
                    entry = (address - layout.ANIME_BASE) // 4
                    print("    header entry %d (%s) read %d time(s), by %s"
                          % (entry, who_writes.hx(address), count,
                             ", ".join(who_writes.hx(pc) for pc in pcs)))

            # From the entry to the numbers: the state holds the frame list
            # and the frame being played, and whoever reads that frame is
            # what turns ANIME.BIN into angles.
            path = os.path.join(game.out_dir, "anime-state.bin")
            raw = game.read_ram(layout.ANIME_STATE + layout.ANIME_STATE_LIST,
                                8, path)
            frame_list = int.from_bytes(raw[0:4], "little")
            frame = int.from_bytes(raw[4:8], "little")
            print("    the state at %s plays list %s, frame %s"
                  % (who_writes.hx(layout.ANIME_STATE),
                     who_writes.hx(frame_list), who_writes.hx(frame)))
            end = layout.ANIME_BASE + layout.SIZE[layout.ANIME]
            for what, pointer in (("frame list", frame_list),
                                  ("frame", frame)):
                if not layout.ANIME_BASE <= pointer < end:
                    problems.append("slot %d: the %s is %s, outside %s in RAM "
                                    "(%s..%s) -- the pose would be coming "
                                    "from somewhere else"
                                    % (one, what, who_writes.hx(pointer),
                                       layout.ANIME,
                                       who_writes.hx(layout.ANIME_BASE),
                                       who_writes.hx(end)))
            inside = layout.ANIME_BASE <= frame_list < end
            if not inside:
                pass
            elif RAM_BASE <= frame < RAM_BASE + RAM_SIZE:
                words = [frame + 4 * word for word in range(16)]
                hits, readers = _watch_reads(game, words, stops=4)
                print("    the frame is read by %s, on %d of its words"
                      % (", ".join(who_writes.hx(pc) for pc in readers)
                         or "nobody", len(hits)))
                if not hits:
                    problems.append("slot %d: nothing read the frame at %s"
                                    % (one, who_writes.hx(frame)))

            ram = game.snapshot("pose")
            loads = _ctc2_matrix_loads(ram)
            fired = _fired_among(game, loads)
            print("    %d instruction(s) write the GTE's first matrix word; "
                  "%d run on this screen: %s"
                  % (len(loads), len(fired),
                     ", ".join("%s x%d" % (who_writes.hx(a), n)
                               for a, n in fired) or "none"))
            if layout.POSE_MATRIX not in [a for a, _n in fired]:
                problems.append("slot %d: layout.POSE_MATRIX is %s and it did "
                                "not run; what did is %r"
                                % (one, who_writes.hx(layout.POSE_MATRIX),
                                   [who_writes.hx(a) for a, _n in fired]))
                continue
            if layout.POSE_MATRIX_SECOND not in [a for a, _n in fired]:
                problems.append("slot %d: %s is recorded as the other matrix "
                                "load and it did not run"
                                % (one, who_writes.hx(
                                    layout.POSE_MATRIX_SECOND)))
            cycle = _matrix_stops(game)
            print("    %s: %d stop(s) before the sequence repeated -- the "
                  "number moves between runs, and the frame-accurate count "
                  "with a piece on each is LOOKS-TASK-25"
                  % (who_writes.hx(layout.POSE_MATRIX), cycle))
            if not cycle:
                problems.append("slot %d: the matrix instruction never came "
                                "round" % one)

    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --pose: %d problem(s)" % len(problems))
    return 1 if problems else 0


FIRED_STOPS = 40
"""How many times a run of armed breakpoints is let go before it is counted.

**The emulator BREAKS on the first hit and stays there**, so one `continue`
and a sleep answers "which fired FIRST", not "which fire".  Measured on
2026-09-17: the same thirty instructions, armed the same way, named
0x80012168 in one run and 0x80010E38 in the next -- two right answers to a
question nobody meant to ask.  Letting it go forty times is what turns it
into a count.
"""


def _fired_among(game, addresses, stops=FIRED_STOPS, seconds=4):
    """Arm an execute breakpoint on each and report which ones run, and how
    often, over *stops* stops."""
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    for address in addresses:
        client.call("breakpoint", action="add", type="execute",
                    address=who_writes.hx(address))
    try:
        for _ in range(stops):
            client.call("continue")
            if not _wait_for_hit(game, seconds):
                break
        listed = client.call("breakpoint", action="list")
        return sorted(((int(w["address"], 16), w["hit_count"])
                       for w in listed if w["hit_count"]),
                      key=lambda pair: -pair[1])
    finally:
        try:
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
        client.call("breakpoint", action="clear")


def _matrix_stops(game):
    """Stops at the matrix instruction before the sequence comes round.

    **A cycle, and this task does not claim it is a frame.**  The repetition
    that closes it is the same one the screen's objects are counted by, but
    there the objects are eight and here the stops are in the hundreds, and
    nothing yet says a piece is one stop.  Attributing loads to pieces is
    LOOKS-TASK-25, which counts the frame from `load_state` and names them.
    """
    import who_writes

    def read(registers):
        return tuple(who_writes.register_value(registers, name)
                     for name in ("a0", "a1", "s0"))

    return len(_stops(game, layout.POSE_MATRIX, read, OBJECT_REPEAT,
                      GLYPH_LIMIT))



# --- the reference pose: which matrix belongs to which piece ---------------

POSE_DIR = os.path.join(ROOT, "work", "looks-pose")
"""Where `--pose <SLOT> <N>` writes one JSON per captured frame."""

POSE_CAPTURE_FRAMES = (0, 20, 40, 60, 80, 100, 120, 140)
"""The frames captured when none are named, counted from `load_state`.

**Spread, and that is the whole point.**  Frames close together move the
figure so little that every piece looks rigidly attached to every other one.
Measured on 2026-09-18, all three on slot 2: ten CONSECUTIVE frames name the
winner by 1.0x to 8.6x and are worthless; 0..24 in fours puts the two knees at
11x and 13x but leaves the shoulder at 3.3x; these eight put every joint that
IS a joint at 4.7x or better and every pair that is not under 1.6x.
"""

MATRIX_STRUCT = 32
"""Bytes of the matrix the game hands the GTE: nine 4.12 halfwords, two of
padding, then three 32-bit translations.  The shape is not assumed -- it is
what the `lw`/`ctc2` pairs at `layout.POSE_PIECE_MATRIX` read, offsets 0 to
0x10 for the rotation and 0x14 to 0x1C for the translation."""

POSE_CYCLE_LIMIT = 40
"""Stops allowed before a draw pass is declared not to come round."""

CAMERA_READS = 3
"""Times the camera load is read before it is called constant."""

MATRIX_TOLERANCE = 0.02
"""How far `M x Mt` may sit from `C x Ct`, as a fraction of the largest entry.

`M = C x R` with `R` a true rotation in 4.12 gives `M x Mt = C x Ct` exactly in
real arithmetic; what the game stores is rounded to whole halfwords, so the
equality is approximate and the size of the slack is a measurement, not a
taste.  Measured on 2026-09-18 over both slots and eight frames each, the
worst piece of a pass sits at **0.0071** -- this threshold is not quite three
times that.  It is wide for rounding and hopeless as a hiding place: a matrix
that is NOT the camera composed with a rotation misses by orders of
magnitude, and the identity against this camera reads **0.99**.

The first threshold written here was 0.006, from a slot-2 run whose worst was
0.0013, and slot 1 came in at 0.0071 and failed it.  A bound fitted to one
slot is a bound fitted to one sample.
"""

HIERARCHY_GAP = 3.0
"""How much better the chosen parent must be than the runner-up.

A ratio and not a distance: the spreads themselves are in model units and a
piece that swings far from every candidate would pass a fixed bound just by
standing still.  Measured over the eight spread frames; ten consecutive ones
do not reach it, which is the point of `POSE_CAPTURE_FRAMES`.
"""


def _matrix_struct(game, base, path):
    """The matrix at *base*, as the game stores it: 9 rotation, 3 translation."""
    raw = game.read_ram(base, MATRIX_STRUCT, path)
    return (list(struct.unpack("<9h", raw[:18])),
            list(struct.unpack("<3i", raw[20:32])))


def piece_names(image):
    """{(file, section): name} for every piece either figure draws.

    The names are `pieces.py`'s, and the head is MODEL.BIN's section 24 --
    the eleven-plus-one of LOOKS-TASK-09, not a naming invented here.
    """
    import iso_source
    import pieces

    with iso_source.open_disc(image) as disc:
        data = disc.read(layout.EDT_MOD)
    named, orders, _paired = pieces.name_pieces(data)
    out = {(layout.MODEL, pieces.HEAD_SECTION): pieces.HEAD}
    for index, piece in named.items():
        out[(layout.EDT_MOD, index)] = piece.full_name
    return out, orders


def _drawn_section(registers, maps):
    """Which section the live pointers are inside, or None when none are.

    One section or nothing: every register that lands in a model file has to
    land in the SAME one, because the piece this matrix belongs to is what the
    caller is about to name.  Two different sections at one stop would mean
    the pointer is not the witness it is being used as, and that is a refusal
    rather than a pick.
    """
    seen = {(where[0], where[1])
            for _name, _value, where in pointers_into_models(registers, maps)
            if where[1] is not None}
    if len(seen) > 1:
        raise OracleError("one matrix load points into %d sections at once "
                          "(%s) -- the pointer does not name the piece"
                          % (len(seen), sorted(seen)))
    return seen.pop() if seen else None


def _pose_cycle(game, maps, names):
    """One draw pass of the per-piece matrix load, in the order it happens.

    **The pass is closed by the sequence REPEATING, not by a piece coming
    round a second time and not by the frame counter.**  Both of the easy
    rules are wrong here, and each was measured wrong on 2026-09-18:

      `internal_frame_number` ticks in the MIDDLE of a pass -- between the
      last leg and the head -- so cutting on it splits one figure across two
      frames and hands the first capture five pieces instead of thirteen;

      cutting at the first piece that appears twice would lose the last load
      of a pass that draws one section twice.  This screen does not -- the
      period is 12 and every section appears once -- but the rule costs
      nothing and the alternative is a silent truncation.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    # Two breakpoints, and the pair matters: the unpack names WHERE in
    # ANIME.BIN the angles came from, and the matrix load names which piece
    # they were for.  Neither alone is the bridge.
    for address in (layout.ANIME_UNPACK, layout.POSE_PIECE_MATRIX):
        client.call("breakpoint", action="add", type="execute",
                    address=who_writes.hx(address))
    path = os.path.join(game.out_dir, "piece-matrix.bin")
    out = []
    keys = []
    pair = None
    try:
        while True:
            client.call("continue")
            if not _wait_for_hit(game, WATCH_SECONDS):
                raise OracleError(
                    "%s stopped %d time(s) and then stopped stopping -- the "
                    "screen is not drawing"
                    % (who_writes.hx(layout.POSE_PIECE_MATRIX), len(out)))
            registers = client.call("read_registers", group="gpr")
            if who_writes.register_value(registers, "pc")                     == layout.ANIME_UNPACK:
                pair = (who_writes.register_value(
                    registers, layout.ANIME_UNPACK_BASE) - layout.ANIME_BASE)
                continue
            where = _drawn_section(registers, maps)
            base = who_writes.register_value(registers,
                                             layout.POSE_PIECE_MATRIX_BASE)
            rotation, translation = _matrix_struct(game, base, path)
            # The three angles the game unpacked for THIS piece, still in the
            # scratchpad when the matrix built from them is loaded.  They are
            # the bridge between the capture and ANIME.BIN: the file holds
            # these numbers and nothing else of the pose (LOOKS-TASK-26).
            angles = list(struct.unpack(
                "<3h", game.read_ram(layout.POSE_ANGLES, 6, path)))
            # And WHICH animation frame those angles came out of, read at this
            # stop and not at the end of the pass: measured 2026-09-18, the
            # animation advances IN THE MIDDLE of a draw pass -- the first
            # five pieces of a pass came from one frame of ANIME.BIN and the
            # rest from the next.  One frame pointer for the whole pass names
            # the wrong file bytes for half the pieces.
            playing = struct.unpack("<I", game.read_ram(
                layout.ANIME_STATE + layout.ANIME_STATE_FRAME, 4, path))[0]
            keys.append(where)
            out.append({
                "order": None,
                "file": where[0] if where else None,
                "section": where[1] if where else None,
                "piece": names.get(where) if where else UNPOINTED_PIECE,
                "rotation": rotation,
                "translation": translation,
                "angles": angles,
                "animation_frame": playing,
                "pair": pair,
            })
            # Consumed: the next piece gets its own pair or none at all.  Ten
            # unpack variants share the dispatch at 0x80011DA0 and only one is
            # the instruction watched here, so a piece that took another one
            # leaves no stop -- and inheriting the previous piece's pair would
            # name the wrong bytes with a straight face.
            pair = None
            period = _repeating_period(keys)
            if period:
                return _named_pass(out[-period:])
            if len(out) > POSE_CYCLE_LIMIT:
                raise OracleError("%d matrix loads and the draw order never "
                                  "repeated" % POSE_CYCLE_LIMIT)
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass


def _repeating_period(keys):
    """The length of the pass, once it has been seen twice, or None.

    Two whole turns, never one: a sequence that happens to end the way it
    began has a period of one by that reading, and this one draws the same
    section twice inside a single pass.
    """
    for period in range(2, len(keys) // 2 + 1):
        if keys[-period:] == keys[-2 * period:-period]:
            return period
    return None


DRAW_LAG = 1
"""How many stops the model pointer trails the matrix it belongs to.

**The pointer at a matrix load names the piece the game has just DRAWN**, not
the one the matrix is for: the matrix goes into the GTE first and the piece's
own pointers are armed after it, so by the time the next load stops the
emulator the registers hold the piece that was finished in between.  One, and
measured -- `draw_lag()` re-measures it from any pass and refuses a pass where
another lag wins.

It cost LOOKS-TASK-27 a whole pass: read at lag 0 the boot took the hip's
matrix, and the assembled figure put a boot at thigh height with every piece
individually plausible and no number anywhere out of range.
"""


def _named_pass(found):
    """The pass with each load numbered and named uniquely, at `DRAW_LAG`.

    A section drawn twice would be two loads and two pieces, and the second is
    not the first -- `foot a` and `foot a #2`.  This screen never does it, and
    the numbering is here so that a pass which does is not quietly collapsed
    into one piece.

    What was OBSERVED is kept beside what it names: `pointer_piece` and
    `pointer_section` are the registers as read at that stop, and `piece` and
    `section` are the piece the matrix is for.  Keeping both is what lets
    `draw_lag()` re-measure the shift instead of inheriting it.
    """
    count = len(found)
    for one in found:
        one["pointer_file"] = one.get("file")
        one["pointer_section"] = one.get("section")
        one["pointer_piece"] = one["piece"]
    for order, one in enumerate(found):
        drawn = found[(order + DRAW_LAG) % count]
        one["file"] = drawn["pointer_file"]
        one["section"] = drawn["pointer_section"]
        one["piece"] = drawn["pointer_piece"]
    seen = {}
    for order, one in enumerate(found):
        one["order"] = order
        name = one["piece"]
        seen[name] = seen.get(name, 0) + 1
        one["instance"] = seen[name]
        one["id"] = name if seen[name] == 1 else "%s #%d" % (name, seen[name])
    return found


UNPOINTED_PIECE = "foot b"
"""The one load of a pass that carries no model pointer, and which piece it is.

Measured on 2026-09-18: at that stop the three pointer registers the other
eleven loads carry the piece in are all zero.  It is named here rather than
left blank because the pass is counted by its pieces coming round, and an
unnamed member of that count is a hole in the count.

**It was named `root` -- a piece that draws nothing -- until CORR-LOOKS-062.**
The pointer cannot name it, so what names it is elimination and the joint: a
pass loads twelve matrices and draws twelve sections, eleven of them named by
the pointer of the stop after them, and section 10 -- the second boot -- is
the one no capture ever names.  Against `shin b` this stop's origin holds to
4.8 units across the eight captures of slot 1 and 4.3 of slot 2, where against
`shin a` it spreads 356.8 and 328.3: it is bolted to the b leg's shin, which is
what an ankle is (`LAG_CHAIN`).

The line this replaces also said the matrix was "the camera's to within a
small turn", and that was wrong twice over: this stop's rotation swings 4362
across those frames, tracking shin b's 4074, and the camera's is constant.
The piece that barely moves is the torso, at 185.
"""


def _camera_matrix(game):
    """The matrix the OTHER load hands the GTE, read until it repeats.

    `layout.POSE_MATRIX` is not a piece's: measured on 2026-09-18, it carries
    the SAME rotation at every stop of a pass while its translation walks the
    pieces, which is what a camera does and what a pose does not.  Reading it
    three times and demanding the three agree is what makes "constant" a
    measurement instead of a reading.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.POSE_MATRIX))
    path = os.path.join(game.out_dir, "camera-matrix.bin")
    found = []
    try:
        for _ in range(CAMERA_READS):
            client.call("continue")
            if not _wait_for_hit(game, WATCH_SECONDS):
                raise OracleError("%s never ran, so there is no camera matrix "
                                  "to compose against"
                                  % who_writes.hx(layout.POSE_MATRIX))
            registers = client.call("read_registers", group="gpr")
            base = who_writes.register_value(registers, layout.POSE_MATRIX_BASE)
            found.append(_matrix_struct(game, base, path))
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    rotations = {tuple(one[0]) for one in found}
    if len(rotations) != 1:
        raise OracleError("the camera load handed %d different rotations in "
                          "%d reads: %r" % (len(rotations), len(found),
                                            sorted(rotations)))
    return {"rotation": found[0][0], "translation": found[0][1]}


def capture_pose(game, slot, frame, maps, names):
    """The pose of one COUNTED frame: `load_state`, N steps, one draw pass.

    Every capture starts from the state again.  It has to: the pass is taken
    with the emulator running free between breakpoint hits, so a second
    capture in the same session is no longer N frames from anywhere.
    """
    restore_state(slot, verbose=False)
    game.load_looks(slot, label="pose-%d-%d" % (slot, frame))
    game.step(frame)
    drawn = _pose_cycle(game, maps, names)
    camera = _camera_matrix(game)
    # Said here rather than inferred from the absence of `pair`: on a pass
    # where the game never stopped at the unpack, the angles beside each piece
    # are what the scratchpad still held, and whoever reads this file has to
    # know that before counting anything (CORR-LOOKS-061).
    paired = sum(1 for piece in drawn if piece.get("pair") is not None)
    return {"slot": slot, "state": SLOTS[slot], "frame": frame,
            "camera": camera, "animation": _animation_now(game),
            "unpacked": paired, "pieces": drawn}


def _animation_now(game):
    """Which ANIME.BIN frame the state is playing, as the game holds it.

    Written beside the pose so the capture says WHERE in the file it came
    from: the list, the frame inside it, and the index that walks the list.
    """
    path = os.path.join(game.out_dir, "anime-now.bin")
    raw = game.read_ram(layout.ANIME_STATE + layout.ANIME_STATE_LIST, 8, path)
    frame_list, frame = struct.unpack("<2I", raw)
    index = game.read_ram(layout.ANIME_STATE + layout.ANIME_STATE_INDEX,
                          1, path)[0]
    return {"list": frame_list, "frame": frame, "index": index}


def write_pose(record):
    """One JSON per captured frame, in `work/looks-pose/`."""
    import json

    os.makedirs(POSE_DIR, exist_ok=True)
    path = os.path.join(POSE_DIR, "slot%d-frame%d.json"
                        % (record["slot"], record["frame"]))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


# --- reading the numbers ---------------------------------------------------

def _multiply(a, b):
    return [sum(a[row * 3 + k] * b[k * 3 + column] for k in range(3))
            for row in range(3) for column in range(3)]


def _transpose(m):
    return [m[column * 3 + row] for row in range(3) for column in range(3)]


def _determinant(m):
    return (m[0] * (m[4] * m[8] - m[5] * m[7])
            - m[1] * (m[3] * m[8] - m[5] * m[6])
            + m[2] * (m[3] * m[7] - m[4] * m[6]))


def _inverse(m):
    det = _determinant(m)
    if not det:
        return None
    cofactors = [
        (m[4] * m[8] - m[5] * m[7]), -(m[1] * m[8] - m[2] * m[7]),
        (m[1] * m[5] - m[2] * m[4]),
        -(m[3] * m[8] - m[5] * m[6]), (m[0] * m[8] - m[2] * m[6]),
        -(m[0] * m[5] - m[2] * m[3]),
        (m[3] * m[7] - m[4] * m[6]), -(m[0] * m[7] - m[1] * m[6]),
        (m[0] * m[4] - m[1] * m[3]),
    ]
    return [value / det for value in cofactors]


def matrix_deviation(rotation, camera):
    """How far `M x Mt` is from `C x Ct`, as a fraction of the largest entry.

    Near zero says the matrix is the camera composed with a true rotation --
    which is what makes the piece matrices ABSOLUTE, in the camera's space,
    rather than each piece's own turn waiting to be composed by whoever draws
    it.
    """
    want = _multiply(camera, _transpose(camera))
    got = _multiply(rotation, _transpose(rotation))
    scale = max(abs(value) for value in want) or 1
    return max(abs(a - b) for a, b in zip(want, got)) / scale


def joint_offset(parent, child):
    """Where the child's origin sits in the parent's own frame, in 4.12.

    `t_child - t_parent = M_parent x d`, so `d = inverse(M_parent) x (t_child
    - t_parent)`.  If the child hangs off the parent, `d` is the joint and does
    not move; if it does not, `d` swings with both poses.  This is where the
    hierarchy comes from, and it needs no anatomy.
    """
    inverse = _inverse(parent["rotation"])
    if inverse is None:
        return None
    delta = [child["translation"][k] - parent["translation"][k]
             for k in range(3)]
    return [sum(inverse[row * 3 + k] * delta[k] for k in range(3)) * FIXED_ONE
            for row in range(3)]


def hierarchy(frames):
    """Each piece's best parent, and how clearly it beat the runner-up.

    *frames* is a list of {piece name: record}.  A piece with no parent shows
    up as a poor best against a nearly as poor runner-up; the caller decides
    with `HIERARCHY_GAP`, and this function never decides for it.
    """
    names = sorted(frames[0])
    out = {}
    for child in names:
        scored = []
        for parent in names:
            if parent == child:
                continue
            offsets = [joint_offset(frame[parent], frame[child])
                       for frame in frames]
            if any(one is None for one in offsets):
                continue
            spread = max(max(one[k] for one in offsets)
                         - min(one[k] for one in offsets) for k in range(3))
            scored.append((spread, parent))
        scored.sort()
        if len(scored) < 2:
            continue
        (best, parent), (second, runner_up) = scored[0], scored[1]
        out[child] = {"parent": parent, "spread": best,
                      "runner_up": runner_up, "runner_up_spread": second,
                      "gap": second / best if best else float("inf")}
    return out



def _by_piece(record):
    return {one["id"]: one for one in record["pieces"]}


LAG_CHAIN = (("shin a", "foot a"), ("shin b", "foot a"),
             ("shin b", "foot b"), ("shin a", "foot b"))
"""The joint the lag is measured on, and why it is the boot's.

A limb that hangs off another keeps its origin STILL in the parent's own
frame, whatever the parent does -- that is `joint_offset`, and it needs no
anatomy.  The boot is the piece to ask because it is the one the wrong lag
moves furthest: one stop away it inherits the hip's matrix and lands at thigh
height.  Each boot comes with the OTHER shin as the control that has to LOSE:
a boot hangs off one shin and not off both, so a lag that makes it rigid
against either shin is not measuring a joint.

**Both boots since CORR-LOOKS-062**, and the second one is only nameable
since then: the twelfth stop of a pass was called `root` and read as drawing
nothing.  Measured over the captures of 2026-09-18, at the winning lag `shin b ->
foot b` holds to 4.8 on slot 1 and 4.3 on slot 2, against 356.8 and 328.3 for
the same boot against the other shin -- and `shin a -> foot a`, 5.0 and 6.4,
is the same joint on the same run.  A capture from before the rename carries no `foot b`,
and the two pairs that name it are skipped rather than failing the run.
"""

LAG_MARGIN = 5.0
"""How much better the winning lag must be than every other one."""


def _pointer_named(loads, lag):
    """{piece the matrix is for: load}, reading the pointers *lag* stops late.

    Old captures carry the raw observation in `piece`; new ones keep it in
    `pointer_piece` and put the corrected name in `piece`.  Reading the raw
    field of whichever is present is what keeps this measurement from
    inheriting the answer it is measuring.
    """
    count = len(loads)
    raw = [one.get("pointer_piece", one["piece"]) for one in loads]
    return {raw[(index + lag) % count]: one for index, one in enumerate(loads)}


def draw_lag(records, lags=(0, 1, 2)):
    """How many stops the model pointer trails the matrix, measured.

    *records* is several captures of ONE slot -- the spread matters, and a
    single frame names no joint at all (pitfall 48).  Each candidate lag is
    scored by how still the boot's origin sits in the shin's own frame across
    them, and the winner has to beat every other by `LAG_MARGIN`.

    This is the measurement LOOKS-TASK-27 was missing.  Nothing here looks at
    whether the assembled figure stands up: that is the thing being decided,
    and using it to decide would be the circle.
    """
    loads = [sorted(one["pieces"], key=lambda q: q["order"]) for one in records]
    scored = {}
    for lag in lags:
        named = [_pointer_named(one, lag) for one in loads]
        for parent, child in LAG_CHAIN:
            if any(parent not in one or child not in one for one in named):
                continue
            offsets = [joint_offset(one[parent], one[child]) for one in named]
            if any(one is None for one in offsets):
                continue
            scored[(lag, parent, child)] = max(
                max(one[k] for one in offsets) - min(one[k] for one in offsets)
                for k in range(3))
    if not scored:
        raise OracleError("no capture carries both ends of %r, so the draw "
                          "lag cannot be measured" % (LAG_CHAIN,))
    best = {lag: min(spread for (one, _p, _c), spread in scored.items()
                     if one == lag)
            for lag in {key[0] for key in scored}}
    winner = min(best, key=lambda lag: best[lag])
    others = [best[lag] for lag in best if lag != winner]
    if not others:
        margin = 0.0
    elif not best[winner]:
        # A joint that holds to the integer is not a weak win, and dividing by
        # it would say so.
        margin = float("inf")
    else:
        margin = min(others) / best[winner]
    return {"scored": scored, "best": best, "winner": winner,
            "margin": margin}


def _synthetic_pass(frames=5):
    """Captures of a skeleton whose one joint is known, with the lag in them.

    A boot bolted to `shin a` and a `shin b` that swings on its own, drawn in
    that order, with the model pointers written one stop LATE -- which is what
    the game does and what `_named_pass` undoes.  Nothing on a disc and no
    emulator: it exists so that the lag has a red case.
    """
    import math

    joint = (0, 60, 0)
    # Six pieces, not four: in a pass of four the cycle wraps so that a lag of
    # two hands back the SAME rigid pair the other way round, and scores 1.0
    # against the true lag's 1.0.  A tie is a synthetic too small to tell the
    # lags apart, not a finding about the game.
    drawn = ("torso", "head", "thigh a", "shin a", "foot a", "thigh b",
             "shin b")
    out = []
    for step in range(frames):
        turns = {"torso": 0.0, "head": 0.1 * step, "shin a": 0.3 * step,
                 "shin b": -0.5 * step, "thigh a": 0.7 * step,
                 "thigh b": 0.9 * step}
        turns["foot a"] = turns["shin a"]
        spun = {}
        for name, angle in turns.items():
            cos = int(round(math.cos(angle) * FIXED_ONE))
            sin = int(round(math.sin(angle) * FIXED_ONE))
            spun[name] = [cos, -sin, 0, sin, cos, 0, 0, 0, FIXED_ONE]
        places = {"torso": [0, 0, 0], "head": [0, -50 - step, 0],
                  "shin a": [10 * step, 100, 0],
                  "shin b": [-10 * step, 100, 40],
                  "thigh a": [5 * step, 50, -20],
                  "thigh b": [-5 * step, 50, 20]}
        places["foot a"] = [
            sum(spun["shin a"][axis * 3 + k] * joint[k] for k in range(3))
            // FIXED_ONE + places["shin a"][axis] for axis in range(3)]
        loads = []
        for order, name in enumerate(drawn):
            loads.append({
                # The pointer is the piece drawn one stop EARLIER.
                "piece": drawn[(order - DRAW_LAG) % len(drawn)],
                "file": None, "section": None,
                "rotation": spun[name], "translation": places[name],
            })
        out.append({"slot": 0, "frame": step,
                    "camera": {"rotation": [FIXED_ONE, 0, 0, 0, FIXED_ONE, 0,
                                            0, 0, FIXED_ONE],
                               "translation": [0, 0, 0]},
                    "pieces": _named_pass(loads)})
    return out


def load_poses(slot=None):
    """Every capture `--pose <SLOT> <N>` left in `POSE_DIR`, by slot."""
    import json

    out = {}
    if not os.path.isdir(POSE_DIR):
        return out
    for name in sorted(os.listdir(POSE_DIR)):
        if not name.endswith(".json"):
            continue
        with open(os.path.join(POSE_DIR, name), encoding="utf-8") as handle:
            record = json.load(handle)
        if slot is not None and record["slot"] != slot:
            continue
        out.setdefault(record["slot"], []).append(record)
    return out


def check_draw_lag(verbose=True):
    """`--pose-lag`: the pointer's lag, re-measured from the captures on disk.

    No emulator: it reads what `--poses` already wrote.  It is the witness
    that names which matrix belongs to which piece, and it fails if the lag
    the code assumes is not the one the numbers pick.
    """
    taken = load_poses()
    if not taken:
        print("oracle --pose-lag: no capture in %s -- run --poses first"
              % POSE_DIR)
        return SKIP
    problems = []
    for slot in sorted(taken):
        records = taken[slot]
        if len(records) < 2:
            problems.append("slot %d: %d capture(s), and one frame names no "
                            "joint" % (slot, len(records)))
            continue
        found = draw_lag(records)
        print("  -- slot %d, %d capture(s) --" % (slot, len(records)))
        for (lag, parent, child), spread in sorted(found["scored"].items()):
            print("     lag %d  %-13s -> %-13s spread %7.1f"
                  % (lag, parent, child, spread))
        print("     lag %d wins by %.1fx (needs %.1fx)"
              % (found["winner"], found["margin"], LAG_MARGIN))
        if found["winner"] != DRAW_LAG:
            problems.append(
                "slot %d: the numbers pick lag %d and the code reads lag %d -- "
                "every piece would be named one stop off"
                % (slot, found["winner"], DRAW_LAG))
        elif found["margin"] < LAG_MARGIN:
            problems.append(
                "slot %d: lag %d beats the next by only %.1fx, under the %.1fx "
                "that makes it a measurement"
                % (slot, found["winner"], found["margin"], LAG_MARGIN))
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --pose-lag: %d problem(s) over %d slot(s)"
          % (len(problems), len(taken)))
    return 1 if problems else 0


def _say_pose(record):
    """One captured frame, printed in the order the game drew it."""
    print("    frame %d, %d load(s) in draw order:" % (record["frame"],
                                                       len(record["pieces"])))
    camera = record["camera"]["rotation"]
    for one in record["pieces"]:
        deviation = matrix_deviation(one["rotation"], camera)
        sign = "mirrored" if _determinant(one["rotation"]) < 0 else "        "
        print("      %-2d %-16s %-9s t=%-22s dev=%.4f  %s"
              % (one["order"], one["id"],
                 "" if one["section"] is None
                 else "sec %d" % one["section"],
                 tuple(one["translation"]), deviation, sign))


SECTION_SAMPLE = 48
"""Addresses watched inside one section when asking whether it is read.

Spread over the whole section, never a handful from one end: four addresses
of a 400 KB file read as silence in LOOKS-TASK-24 and nearly became "the pose
does not come from there" (pitfall 42).  A sample of a section is a different
size of the same mistake, so the sample is even and the control is a section
the same pass is known to draw.
"""


def _section_addresses(maps, where, count=SECTION_SAMPLE):
    """*count* addresses spread evenly across one section's bytes."""
    for base, (name, _size, sections) in maps.items():
        if name != where[0]:
            continue
        one = sections[where[1]]
        step = max(4, (one.end - one.offset) // count)
        return [base + offset
                for offset in range(one.offset, one.end, step)][:count]
    raise OracleError("no section %r in the model maps" % (where,))


def _sections_read(game, maps, wanted):
    """Which of *wanted* the game reads, each one watched on a run of its own.

    **One section per run, and that is the whole correctness of it.**  Armed
    together, the emulator breaks on the FIRST hit and stays there, so a
    section the pass draws every frame takes every stop and the one being
    asked about never gets a turn -- silence that says nothing about the game.
    Measured on 2026-09-18, and it was not a nicety: all of them armed at once
    read `section 10: 0` beside the control's 4, which reads as *the screen
    never touches foot b*.  One run each, and section 10 reads **2**, exactly
    what the control reads.  The window had shown two boots all along.
    """
    found = {}
    for where in wanted:
        hits, _pcs = _watch_reads(game, _section_addresses(maps, where),
                                  stops=2)
        found[where] = sum(count for _address, count in hits)
    return found


# --- the camera the game projects with ------------------------------------

PROJECTION = ("H", "OFX", "OFY")
"""The three GTE control registers that turn camera space into screen pixels.

`RTPS` computes `SX = OFX + H * IR1 / SZ` in 16.16, so `H` is the focal length
in pixels and `OFX`/`OFY` are the principal point -- the middle of whatever
viewport the game is drawing into.  They are CONTROL registers, written by
`ctc2` like the matrix, so they are read the same way and at the same stop.
"""

CAMERA_STOPS = 12
"""Matrix loads read before the projection is called constant over a pass.

One stop would answer; the pass is twelve pieces and the question is whether
the game changes the viewport between them -- the panel is a window inside a
512x240 screen, and a projection measured on one piece and applied to twelve
would be a reading, not a measurement.
"""


HALFWORD = (1 << 16) - 1
"""Mask of one GTE control halfword.  Written as a shift and not as a hex
literal because rule 1's sweep reads hex as an address, and it is right to:
what makes this not one is that it is a field width."""


def _signed_word(value):
    """One 32-bit GTE control field, signed."""
    span = 1 << 32
    value &= span - 1
    return value - span if value >= span // 2 else value


def gte_projection(registers):
    """{H, OFX, OFY} out of a `get_gte_registers` answer, in pixels.

    `OFX` and `OFY` are 16.16 fixed point -- the hardware adds them to a 16.16
    product -- and `H` is a plain unsigned halfword.  Dividing here rather than
    at the point of use is what keeps the number that reaches a document in
    the unit the document says.
    """
    control = registers["control_registers"]
    return {
        "H": int(control["H"], 16) & HALFWORD,
        "OFX": _signed_word(int(control["OFX"], 16)) / 65536.0,
        "OFY": _signed_word(int(control["OFY"], 16)) / 65536.0,
    }


WALK_DIR = os.path.join(ROOT, "work", "looks-walk")
"""Where `--walk` writes one JSON per slot: the cycle, as the game played it."""

WALK_PASSES = 40
"""Draw passes taken in one run, which has to be more than one cycle.

The cycle measured is 34 passes, so 40 is the cycle plus enough of the next to
show the first pose coming back and nothing before it coming back.  A run that
took exactly 34 could not tell a period of 34 from a period of 34 the sequence
never repeats at.
"""

WALK_BLEND_MODE = 1  # not-an-address: the value of layout.ANIME_BLEND_MODE
"""What the selector byte holds when the game averages, of the three it takes.

0 draws the matrix just built and keeps it, 1 draws the average of it with the
kept one, 2 draws the kept one and drops the fresh one -- read off
`layout.ANIME_BLEND`'s three branches.  On this screen 0 and 1 happen and 2
never does, measured at every load of both cycles.
"""

WALK_CAMERA_GAP = 120
"""Frames between the two camera reads of a run, which is more than a cycle.

The cycle measured is 77 counted frames, so a camera that moved with the walk
would have moved by the second read.  It is the measurement behind "the swing
is the animation's": the pose's own matrices swing 4552 units of 4096 over the
cycle -- the widest of the nine entries of any piece's rotation in
`work/looks-walk/slotN.json`, both slots (CORR-LOOKS-092) -- while this comes
back the same nine halfwords and the same three translations.
"""

WALK_CONTROL_PASSES = 6
"""Passes taken a second time, from `load_state`, before anything is measured.

The capture runs the emulator free between breakpoint stops, so a second
capture in the same session is no longer a known number of passes from
anywhere: the control reloads the state and takes the first few again, and
they have to come back identical number by number.
"""


def _walk_stops(game, maps, names, passes, label, watch=None,
                pair_register=None, strict=True):
    """Every matrix load of *passes* consecutive draw passes, in one session.

    Two breakpoints and one stop each, and the pair is the point: **the watch
    is `layout.ANIME_BUILD` and not `layout.ANIME_UNPACK`** -- ten unpack
    variants share the dispatch and only one of them is the instruction the
    pose captures watched, so half of those passes came back with no pair on
    any piece (`anime.split_captures`).  Every variant reaches this one call.

    *watch* and *pair_register* swap the watched stop and its pair register,
    and are there for `--walk-watch` alone, which counts how many loads each
    watch names (CORR-LOOKS-092).  With *strict* false a load no hit of the watch
    named is kept with pair None instead of failing the run; the loads before
    the first hit are dropped either way.
    """
    if watch is None:
        watch, pair_register = layout.ANIME_BUILD, layout.ANIME_BUILD_BASE
    import anime
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    for address in (watch, layout.POSE_PIECE_MATRIX):
        client.call("breakpoint", action="add", type="execute",
                    address=who_writes.hx(address))
    path = os.path.join(game.out_dir, "walk-%s.bin" % label)
    out = []
    pair = None
    try:
        while len(out) < passes * (anime.PIECE_PAIRS + 1):
            client.call("continue")
            if not _wait_for_hit(game, WATCH_SECONDS):
                raise OracleError(
                    "the draw stopped after %d matrix load(s) -- the screen is "
                    "not drawing the figure any more" % len(out))
            registers = client.call("read_registers", group="gpr")
            if who_writes.register_value(registers, "pc") == watch:
                pair = who_writes.register_value(
                    registers, pair_register) - layout.ANIME_BASE
                continue
            if pair is None:
                # Every load is named by the build that preceded it; a load
                # without one would be a piece whose pose came from nowhere,
                # and guessing it is how a cycle gets read one visit off.
                # The run begins inside a pass whose builds are already past,
                # so those loads are dropped -- and only those: once a build
                # has been seen, a load without one is a failure.
                if not out:
                    continue
                if strict:
                    raise OracleError("a matrix load with no pair before it, "
                                      "%d stop(s) in" % len(out))
            where = _drawn_section(registers, maps)
            base = who_writes.register_value(registers,
                                             layout.POSE_PIECE_MATRIX_BASE)
            rotation, translation = _matrix_struct(game, base, path)
            out.append({
                "pointer_section": where[1] if where else None,
                "pointer_piece": names.get(where) if where else UNPOINTED_PIECE,
                "rotation": rotation, "translation": translation,
                "angles": list(struct.unpack(
                    "<3h", game.read_ram(layout.POSE_ANGLES, 6, path))),
                "pair": pair,
                "mode": game.read_ram(layout.ANIME_BLEND_MODE, 1, path)[0],
                "frame_number": client.call("get_status").get("frame_number"),
            })
            pair = None
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    return out


def _walk_align(stops):
    """Where the first whole pass begins, by the draw order repeating.

    The run starts in the middle of a pass -- the state was paused mid-frame
    -- and the frame number cannot say where the pass began, because the video
    frame ticks INSIDE a pass (`_pose_cycle`).  What says it is the order
    itself: twelve loads with the same model pointer in the same place, pass
    after pass.
    """
    import anime

    count = anime.PIECE_PAIRS
    for offset in range(count):
        columns = [{stops[at]["pointer_section"]
                    for at in range(offset + column, len(stops), count)}
                   for column in range(count)]
        if all(len(one) == 1 for one in columns):
            return offset
    raise OracleError("the %d matrix loads never settle into a repeating draw "
                      "order of %d, so no pass can be cut out of them"
                      % (len(stops), count))


def _walk_passes(stops, first_pair):
    """The run cut into whole passes, each load named and each pair placed.

    The piece is the model pointer of the stop after it (`DRAW_LAG`); the pair
    slot is read out of the pair's own offset in the frame.  **Keeping both is
    the control**: on the walk's first half the two have to be the same slot,
    and on the second the pair has to be the SIBLING's (`anime.WALK_SWAP`) --
    two independent readings of "whose pose is this", where one would only be
    a convention.
    """
    import anime

    count = anime.PIECE_PAIRS
    offset = _walk_align(stops)
    passes = []
    for start in range(offset, len(stops) - count + 1, count):
        taken = []
        for order in range(count):
            stop = dict(stops[start + order])
            stop["order"] = order
            named = stops[start + (order + DRAW_LAG) % count]["pointer_piece"]
            stop["piece"] = named
            stop["slot"] = anime.PIECE_ORDER.index(named)
            stop["read"] = ((stop["pair"] - first_pair) % anime.FRAME_BYTES
                            // anime.PAIR_BYTES)
            taken.append(stop)
        passes.append(taken)
    return passes


def _walk_first_slot(passes):
    """Which pair slot the pass opens on, read off the pieces it draws.

    The twelve loads of a pass are the twelve pieces in the file's own order,
    started somewhere: the cursor does not restart with the figure, so where
    it starts is whatever the save state caught (`anime.WALK_FIRST_SLOT`).
    Every pass of a run has to open on the same slot, or the pass is not being
    cut where the game cuts it.
    """
    import anime

    count = anime.PIECE_PAIRS
    found = set()
    for one in passes:
        slots = [stop["slot"] for stop in one]
        if sorted(slots) != list(range(count)):
            raise OracleError("a pass draws %r and not the twelve pieces once "
                              "each" % (slots,))
        if any((slots[0] + order) % count != slots[order]
               for order in range(count)):
            raise OracleError("a pass draws the pieces in the order %r, which "
                              "is not the file's order started somewhere"
                              % (slots,))
        found.add(slots[0])
    if len(found) != 1:
        raise OracleError("the passes of one run open on %d different pair "
                          "slots (%r)" % (len(found), sorted(found)))
    return found.pop()


def _walk_key(one):
    return tuple((stop["slot"], tuple(stop["rotation"]),
                  tuple(stop["translation"])) for stop in one)


def _walk_visit(data, passes, camera, animation, first_slot):
    """Where in the cycle the first pass sits, found by trying every place.

    One visit of the 34 has to reproduce the twelve matrices of the first pass
    exactly, and only one may: if two did, the cycle would have a repeated
    pose and "the period" would mean nothing.
    """
    import anime

    fits = []
    for visit in range(anime.walk_visits(data, animation)):
        model = {piece["slot"]: piece["matrix"]
                 for piece in anime.walk_pose(data, animation, visit, camera,
                                              first_slot)}
        if all(model[stop["slot"]] == stop["rotation"] for stop in passes[0]):
            fits.append(visit)
    if len(fits) != 1:
        raise OracleError(
            "%d of the %d places in the cycle reproduce the first pass (%r) -- "
            "the cycle cannot be counted from a pose that fits more than one "
            "place in it" % (len(fits), anime.walk_visits(data, animation),
                             fits))
    return fits[0]


def write_walk(plan):
    """One JSON per slot in `work/looks-walk/`, which is what `anime.py
    --frame N` reads: the cycle it must not invent."""
    import anime
    import json

    os.makedirs(WALK_DIR, exist_ok=True)
    path = anime.plan_path(plan["slot"])
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(plan, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def _walk_places(data, plan):
    """How far the model's places land from the translations the game loaded.

    Both ways round the negation the mirror variants do on x, because that is
    the measurement that says the negation is there: the same run with x left
    alone has to land further out, or the rule is decoration.
    """
    import anime

    camera = plan["camera"]
    worst = {"as measured": 0, "without the x negation": 0}
    for one in plan["cycle"]:
        model = {piece["slot"]: piece
                 for piece in anime.walk_pose(data, plan["animation"],
                                              plan["visit"] + one["pass"],
                                              camera["rotation"],
                                              plan["first_slot"])}
        for drawn in one["pieces"]:
            piece = model[drawn["slot"]]
            for name, place in (
                    ("as measured", piece["place"]),
                    ("without the x negation",
                     (abs(piece["place"][0]) if piece["rule"] != "plain"
                      else piece["place"][0],) + tuple(piece["place"][1:]))):
                turned = [sum(camera["rotation"][axis * 3 + k] * place[k]
                              for k in range(3)) // FIXED_ONE
                          + camera["translation"][axis] for axis in range(3)]
                apart = max(abs(a - b)
                            for a, b in zip(turned, drawn["translation"]))
                worst[name] = max(worst[name], apart)
    return worst


def pair_runs(stops):
    """The loads of a run as runs of named and unnamed, in order.

    `[("P", 152), (".", 204), ("P", 164)]` -- P a load a hit of the watch
    named, `.` one it did not.  The shape is what `--walk-watch` reports and
    not a ratio, because a ratio depends on where in the cycle the run began
    and the shape does not: what the unpack watch misses is one contiguous
    mirrored half at a time (CORR-LOOKS-092).
    """
    runs = []
    for stop in stops:
        mark = "." if stop["pair"] is None else "P"
        if runs and runs[-1][0] == mark:
            runs[-1] = (mark, runs[-1][1] + 1)
        else:
            runs.append((mark, 1))
    return runs


def check_walk_watch(slot=2, verbose=True):
    """`--walk-watch [SLOT]`: how many loads each watch names, over one run.

    The generator of the count behind `layout.ANIME_BUILD`'s "this is the
    stop to watch" (CORR-LOOKS-092): `WALK_PASSES` passes taken twice from
    the same state, once watching `layout.ANIME_BUILD` and once
    `layout.ANIME_UNPACK`, each load marked by whether a hit of the watch
    named its pair.  Reports the counts and the shape of what is missed.
    """
    import anime

    ready = preflight()
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        maps = model_maps(ready["image"])
        names, _orders = piece_names(ready["image"])
        print("  -- slot %d (%s): the %d matrix loads --walk takes for its %d "
              "passes, %d loads a pass --"
              % (slot, SLOTS[slot], WALK_PASSES * (anime.PIECE_PAIRS + 1),
                 WALK_PASSES, anime.PIECE_PAIRS))
        for label, watch, register in (
                ("ANIME_BUILD", layout.ANIME_BUILD, layout.ANIME_BUILD_BASE),
                ("ANIME_UNPACK", layout.ANIME_UNPACK,
                 layout.ANIME_UNPACK_BASE)):
            restore_state(slot, verbose=False)
            game.load_looks(slot, label="walk-watch-%s-%d" % (label, slot))
            stops = _walk_stops(game, maps, names, WALK_PASSES,
                                "watch-%s-%d" % (label, slot), watch=watch,
                                pair_register=register, strict=False)
            named = sum(1 for stop in stops if stop["pair"] is not None)
            print("    %-13s %d of %d matrix loads carry a pair"
                  % (label, named, len(stops)))
            print("      runs: %s" % " ".join(
                "%s%d" % run + ("" if run[0] == "P"
                                or run[1] % anime.PIECE_PAIRS
                                else " (%d passes)"
                                % (run[1] // anime.PIECE_PAIRS))
                for run in pair_runs(stops)))
            if label == "ANIME_BUILD" and named != len(stops):
                problems.append("ANIME_BUILD named %d of %d loads, and it is "
                                "the watch every variant reaches"
                                % (named, len(stops)))
    print("oracle --walk-watch: %d problem(s)" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    return 1 if problems else 0


def check_walk(slot=None, verbose=True):
    """`--walk [SLOT]`: the cycle of the walk, and the rule that draws it.

    The order of the run is the argument:

      **the control first** -- the state reloaded and the first passes taken
          again, identical number by number, or the sequence is measuring the
          emulator's mood rather than the animation;
      **the passes differ** -- without it a capture that reads one constant
          pose passes the control perfectly and reports a period of one;
      **the period** -- the first pass whose twelve matrices come back to the
          first pass's, in passes and in counted video frames;
      **the camera** -- read at its own load once per run, and the model
          judged against it: if the camera moved with the walk, no pose of a
          counted frame could be compared with anything;
      **the model** -- `anime.walk_pose` against every matrix of the cycle,
          integer for integer, with one visit along as the negative control.
    """
    import anime
    import iso_source

    ready = preflight()
    slots = (slot,) if slot else tuple(sorted(SLOTS))
    problems = []
    with iso_source.open_disc(ready["image"]) as disc:
        data = anime.read(disc)
    animation = layout.ANIME_SCREEN_ENTRY
    keyframes = anime.walk_visits(data, animation) // 2
    first_pair = anime.block(data, anime.header(data)[animation])["frames"][0]
    with Oracle(ready["cue"], verbose=verbose) as game:
        maps = model_maps(ready["image"])
        names, _orders = piece_names(ready["image"])
        for one in slots:
            print("  -- slot %d (%s) --" % (one, SLOTS[one]))

            restore_state(one, verbose=False)
            game.load_looks(one, label="walk-control-%d" % one)
            control = _walk_passes(_walk_stops(game, maps, names,
                                               WALK_CONTROL_PASSES + 1,
                                               "control-%d" % one), first_pair)
            restore_state(one, verbose=False)
            game.load_looks(one, label="walk-%d" % one)
            # The camera is read AFTER the passes, and the reason is the
            # control above: reading it first runs the game through three
            # stops of its own, so the sequence would start further along
            # than the control's and the two could not be compared.
            taken = _walk_passes(_walk_stops(game, maps, names, WALK_PASSES,
                                             "run-%d" % one), first_pair)
            camera = _camera_matrix(game)
            game.step(WALK_CAMERA_GAP)
            later = _camera_matrix(game)
            if later != camera:
                problems.append(
                    "slot %d: the camera read %d frame(s) later is not the "
                    "same (%r against %r) -- on this screen it has to be, and "
                    "if it moves with the walk then what swings is the camera "
                    "and not the animation"
                    % (one, WALK_CAMERA_GAP, later, camera))
                continue
            print("    control: the camera is the same matrix %d frame(s) "
                  "later, so what moves over the cycle is the pose and not "
                  "the view" % WALK_CAMERA_GAP)
            again = [_walk_key(each) for each in taken[:WALK_CONTROL_PASSES]]
            if [_walk_key(each) for each in control[:WALK_CONTROL_PASSES]] \
                    != again:
                problems.append(
                    "slot %d: the first %d pass(es) taken twice from "
                    "load_state differ, so the sequence is not repeatable and "
                    "no period under it means anything"
                    % (one, WALK_CONTROL_PASSES))
                continue
            print("    control: the first %d pass(es) taken twice from "
                  "load_state, %d load(s) each, identical number by number"
                  % (WALK_CONTROL_PASSES, anime.PIECE_PAIRS))

            first_slot = _walk_first_slot(taken)
            own = [stop for each in taken for stop in each
                   if stop["read"] == stop["slot"]]
            sibling = [stop for each in taken for stop in each
                       if stop["read"] == anime.WALK_SWAP[stop["slot"]]
                       and stop["read"] != stop["slot"]]
            loads = sum(len(each) for each in taken)
            strange = loads - len(own) - len(sibling)
            if strange:
                problems.append(
                    "slot %d: %d of %d load(s) read a pair that is neither the "
                    "piece's own nor its sibling's" % (one, strange, loads))
                continue
            print("    control: every one of the %d load(s) reads its own pair "
                  "(%d) or its sibling's (%d), and a pass opens on pair slot "
                  "%d" % (loads, len(own), len(sibling), first_slot))

            keys = [_walk_key(each) for each in taken]
            distinct = len(set(keys))
            if distinct < 2:
                problems.append(
                    "slot %d: all %d pass(es) carry the same numbers -- the "
                    "capture is reading a constant, not a walk"
                    % (one, len(keys)))
                continue
            back = [at for at in range(1, len(keys)) if keys[at] == keys[0]]
            if not back:
                problems.append(
                    "slot %d: the first pose does not come back in %d pass(es)"
                    % (one, len(keys)))
                continue
            period = back[0]
            frames = (taken[period][0]["frame_number"]
                      - taken[0][0]["frame_number"])
            print("    %d distinct pose(s) in %d pass(es); the first pose comes "
                  "back after %d pass(es) and %d counted frame(s), and at no "
                  "pass before it" % (distinct, len(keys), period, frames))
            if distinct != period:
                problems.append(
                    "slot %d: %d distinct pose(s) over a period of %d -- a "
                    "cycle repeats a pose inside itself, which no counting of "
                    "it can survive" % (one, distinct, period))
                continue
            if period != 2 * keyframes:
                problems.append(
                    "slot %d: %d pass(es) a cycle over %d frame(s) of the file "
                    "-- the walk is not the frames played twice, and the model "
                    "of it assumes it is" % (one, period, keyframes))
                continue

            visit = _walk_visit(data, taken, camera["rotation"], animation,
                                first_slot)
            plan = {"slot": one, "state": SLOTS[one], "animation": animation,
                    "visit": visit, "first_slot": first_slot,
                    "passes": period, "frames": frames,
                    "keyframes": keyframes, "camera": camera,
                    "cycle": [{"pass": at,
                               "frame_number": each[0]["frame_number"],
                               "pieces": [{"slot": stop["slot"],
                                           "piece": stop["piece"],
                                           "order": stop["order"],
                                           "pair": stop["pair"],
                                           "angles": stop["angles"],
                                           "mode": stop["mode"],
                                           "rotation": stop["rotation"],
                                           "translation": stop["translation"]}
                                          for stop in each]}
                              for at, each in enumerate(taken[:period])]}
            print("    the cycle starts at visit %d of %d: frame %d of %d, "
                  "side %d" % (visit, 2 * keyframes, visit % keyframes,
                               keyframes, visit // keyframes))

            found = anime.against_walk(data, plan)
            print("    %d of %d matrices of the cycle are the file's, integer "
                  "for integer (worst %d)"
                  % (found["exact"], found["pieces"], found["worst"]))
            if found["exact"] != found["pieces"]:
                problems.append(
                    "slot %d: %d of %d matrices are not what the file plus the "
                    "measured rule gives, worst %d: %r"
                    % (one, found["pieces"] - found["exact"], found["pieces"],
                       found["worst"], found["off"][:4]))
            wrong = anime.against_walk(data, plan, shift=1)
            if wrong["exact"] >= found["exact"]:
                problems.append(
                    "slot %d: modelling every pass with the NEXT visit is as "
                    "exact as modelling it with its own (%d of %d) -- the "
                    "comparison cannot tell one pose of the cycle from another"
                    % (one, wrong["exact"], wrong["pieces"]))
            else:
                print("    control: one visit along, %d of %d exact -- the "
                      "neighbour is not the pose"
                      % (wrong["exact"], wrong["pieces"]))

            # Whose matrix the game averaged, by its own selector byte,
            # against whose the model averages -- as SETS, because the two
            # counts agreeing while the pieces differ would be a coincidence
            # read as a rule.
            blended = {(each["pass"], piece["slot"])
                       for each in plan["cycle"] for piece in each["pieces"]
                       if piece["mode"] == WALK_BLEND_MODE}
            modelled = {(at, piece["slot"]) for at in range(period)
                        for piece in anime.walk_pose(data, animation,
                                                     visit + at, None,
                                                     first_slot)
                        if piece["blended"]}
            print("    the averaging byte says average at %d of the %d load(s) "
                  "of the cycle, and the model averages the same %d"
                  % (len(blended), found["pieces"],
                     len(blended & modelled)))
            if blended != modelled:
                problems.append(
                    "slot %d: the game averaged %d piece(s) and the model %d, "
                    "and %d of them are not the same piece of the same pass"
                    % (one, len(blended), len(modelled),
                       len(blended ^ modelled)))

            places = _walk_places(data, plan)
            print("    the places land %d unit(s) from the translations the "
                  "game loaded, against %d with the mirror's x left alone"
                  % (places["as measured"],
                     places["without the x negation"]))
            if places["as measured"] >= places["without the x negation"]:
                problems.append(
                    "slot %d: negating x on the mirrored pairs is no closer "
                    "than leaving it alone (%d against %d), so the negation is "
                    "not measured by this run"
                    % (one, places["as measured"],
                       places["without the x negation"]))

            print("    wrote %s" % write_walk(plan))
    print("oracle --walk: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    for line in problems:
        print("  FAIL  %s" % line)
    return 1 if problems else 0


CLOSE_UP_SETTLE = 300
"""Frames let run after the cursor lands on a row, before the camera is read.

The panel changes camera with the row under the cursor (pitfall 67), and the
change is not instant.  Three hundred is what the head took to settle in
CORR-LOOKS-049, and what the style photographs of LOOKS-TASK-28 needed.
"""


def capture_camera(game, slot, frame=0, row=None):
    """The projection and the camera of one counted frame.

    Read at the per-piece matrix load, which is inside the figure's own draw:
    a projection read anywhere else in the frame could be the panel's, the
    text's or the background's, and the three are not the same viewport.

    *row* moves the cursor there first.  The panel ZOOMS onto the head when a
    head row is selected (pitfall 67), so the camera of `NAT` -- where the
    state loads -- is not the camera of `HAIR`, and each is measured where it
    is used rather than assumed to be the other.
    """
    import who_writes

    restore_state(slot, verbose=False)
    game.load_looks(slot, label="camera-%d-%d-%s" % (slot, frame, row or ""))
    if row is not None:
        # Down all the way round, never a signed count: the cursor wraps
        # (section 10.3 (q)), and a row ABOVE the one the state loads on --
        # `DEFAUL` is the only one -- came out as no presses at all, which
        # measured the loading row's camera and called it that row's.
        for _ in range((ROWS.index(row) - ROWS.index(CURSOR_STARTS_ON))
                       % len(ROWS)):
            game.press("Down", box=FOOTER, least=ROW_MOVED)
        game.step(CLOSE_UP_SETTLE)
    game.step(frame)
    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.POSE_PIECE_MATRIX))
    seen = []
    try:
        for _ in range(CAMERA_STOPS):
            client.call("continue")
            if not _wait_for_hit(game, WATCH_SECONDS):
                raise OracleError("%s stopped %d time(s) and then stopped "
                                  "stopping"
                                  % (who_writes.hx(layout.POSE_PIECE_MATRIX),
                                     len(seen)))
            seen.append(gte_projection(client.call("get_gte_registers")))
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    camera = _camera_matrix(game)
    return {"slot": slot, "state": SLOTS[slot], "frame": frame, "row": row,
            "projection": seen, "camera": camera,
            "chain": _camera_chain(game)}


def _camera_chain(game):
    """What the camera is BUILT from, read where the game builds it.

    {"view": {rotation, translation}, "angles", "place", "scale"} -- the view
    matrix the `ctc2` at `layout.CAMERA_BUILD` loads through `s7`, and the
    figure's own turn, place and scale it is composed with (LOOKS-TASK-29).
    `stature.camera` composes them back into the load, and `scene.load_camera`
    refuses a chain that does not reproduce it: the chain is what lets the
    window draw a figure of another height with the camera the game would use.
    """
    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(layout.CAMERA_BUILD))
    path = os.path.join(game.out_dir, "camera-chain.bin")
    try:
        client.call("continue")
        if not _wait_for_hit(game, WATCH_SECONDS):
            raise OracleError("%s never ran, so the camera was not built"
                              % who_writes.hx(layout.CAMERA_BUILD))
        registers = client.call("read_registers", group="gpr")
        base = who_writes.register_value(registers, layout.CAMERA_VIEW_BASE)
        rotation, translation = _matrix_struct(game, base, path)
        figure = _figure_now(game)
    finally:
        try:
            client.call("breakpoint", action="clear")
            client.call("pause")
        except Exception:  # noqa: BLE001
            pass
    return dict(figure, view={"rotation": rotation,
                              "translation": translation})


def _figure_now(game):
    """The figure's angles, place and scale, as the game holds them now."""
    path = os.path.join(game.out_dir, "figure.bin")
    return {
        "angles": list(struct.unpack(
            "<3h", game.read_ram(layout.FIGURE_ANGLES, 6, path))),
        "place": list(struct.unpack(
            "<3h", game.read_ram(layout.FIGURE_PLACE, 6, path))),
        "scale": list(struct.unpack(
            "<3i", game.read_ram(layout.FIGURE_SCALE, 12, path))),
    }


def camera_from_pieces(pieces, anime_data, spread_limit=2.0):
    """The camera the game composed into THESE pieces, out of the pieces.

    `M = C . R_pose` and `T = C . place + T_cam` for every piece, with `R_pose`
    and `place` read out of ANIME.BIN at the pair the piece read.  So
    `C = M . R_pose^T` and `T_cam = T - C . place`, once per piece -- and the
    twelve answers have to AGREE, which is the check that the pose read off the
    file is the pose the game used.

    **Why not the camera load at `layout.POSE_MATRIX`.**  On the full figure
    the two are the same.  In the close-up the game shows with a head row under
    the cursor they are NOT: the figure turns, and the turn is composed into
    every piece and absent from that load -- measured 2026-09-18, an extra
    18.3, -16.9 and 16.9 degrees about y over three captures, the same to 0.05
    degrees across the twelve pieces of each, and 0.03 on the full figure.
    Composed with the load's camera, the translations spread 29 units; with
    the camera derived here, under one.
    """
    import anime

    rotations, turned = [], []
    for piece in pieces:
        at = piece.get("pair")
        if at is None:
            continue
        first, second = struct.unpack("<2I", anime_data[at:at + 8])
        pose = [value / float(FIXED_ONE)
                for value in anime.rotation(anime.angles(first))]
        # C = M . R^T, the rotation of a pose being its own inverse's transpose
        camera = [sum(piece["rotation"][row * 3 + k] * pose[column * 3 + k]
                      for k in range(3))
                  for row in range(3) for column in range(3)]
        rotations.append(camera)
        turned.append((piece["translation"], anime.position(first, second)))
    if len(rotations) < 2:
        raise OracleError("%d piece(s) carry a pair, and a camera derived from "
                          "fewer than two is not checked against anything"
                          % len(rotations))
    mean = [sum(one[index] for one in rotations) / len(rotations)
            for index in range(9)]
    worst = max(abs(one[index] - mean[index])
                for one in rotations for index in range(9))
    if worst > spread_limit * FIXED_ONE / 100.0:
        raise OracleError("the %d pieces imply cameras up to %.0f of %d apart "
                          "-- the pose read off the file is not the pose the "
                          "game composed" % (len(rotations), worst, FIXED_ONE))
    offsets = [[translation[axis]
                - sum(mean[axis * 3 + k] * place[k] for k in range(3))
                / float(FIXED_ONE) for axis in range(3)]
               for translation, place in turned]
    place = [sum(one[axis] for one in offsets) / len(offsets)
             for axis in range(3)]
    apart = max(abs(one[axis] - place[axis])
                for one in offsets for axis in range(3))
    return {"rotation": mean, "translation": place,
            "rotation_spread": worst, "translation_spread": apart}


CAMERA_DIR = os.path.join(ROOT, "work", "looks-camera")
"""Where `--camera` writes one JSON per slot, for the window to draw with."""


def write_camera(record):
    """One JSON per slot and row, in `work/looks-camera/`.

    `slotN.json` is the camera of the row the state loads on; a camera
    measured on another row is `slotN-ROW.json`, so the one the window draws
    the full figure with is never overwritten by a close-up.
    """
    import json

    os.makedirs(CAMERA_DIR, exist_ok=True)
    row = record.get("row")
    path = os.path.join(CAMERA_DIR, "slot%d%s.json"
                        % (record["slot"], "-" + row if row else ""))
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, sort_keys=True)
        handle.write("\n")
    return path


def check_camera(slot=None, verbose=True, row=None):
    """`--camera [SLOT]`: the projection and the camera, with the controls.

    Three, and the order is the point:

      **the same frame twice** -- captured from `load_state` both times, and
          identical number by number, or the capture is measuring the
          emulator's mood;
      **constant over the pass** -- the twelve pieces of one figure share one
          projection, or the panel is not one viewport and a single H would
          be an average;
      **a different frame agrees** -- the projection is screen setup and not
          animation, so it must NOT move with the walk.  If it did, every
          comparison against a counted frame would need it re-read, and this
          says so instead of assuming.
    """
    ready = preflight()
    slots = (slot,) if slot else tuple(sorted(SLOTS))
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in slots:
            print("  -- slot %d (%s) --" % (one, SLOTS[one]))
            first = capture_camera(game, one, 0, row)
            again = capture_camera(game, one, 0, row)
            if first != again:
                problems.append(
                    "slot %d: two captures of the same frame differ, so the "
                    "projection is not repeatable" % one)
                print("    %r" % (first,))
                print("    %r" % (again,))
                continue
            print("    control: frame 0 captured twice, %d stop(s) each, "
                  "identical number by number" % len(first["projection"]))

            distinct = {tuple(sorted(each.items()))
                        for each in first["projection"]}
            if len(distinct) != 1:
                problems.append(
                    "slot %d: the %d matrix loads of one pass carry %d "
                    "different projections, so the figure is not drawn into "
                    "one viewport: %r"
                    % (one, len(first["projection"]), len(distinct),
                       sorted(distinct)))
                continue
            found = first["projection"][0]
            print("    H %d px, principal point (%.2f, %.2f), the same at all "
                  "%d load(s)" % (found["H"], found["OFX"], found["OFY"],
                                  len(first["projection"])))

            later = capture_camera(game, one, POSE_CAPTURE_FRAMES[-1], row)
            if later["projection"][0] != found:
                problems.append(
                    "slot %d: frame %d projects with %r and frame 0 with %r -- "
                    "the projection moves with the walk, so it cannot be read "
                    "once" % (one, later["frame"], later["projection"][0],
                              found))
            else:
                print("    and frame %d projects with the same three, so the "
                      "projection is screen setup and not animation"
                      % later["frame"])

            print("    the camera matrix is %s, translation %s"
                  % (first["camera"]["rotation"],
                     first["camera"]["translation"]))
            print("    wrote %s" % write_camera(first))
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --camera: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def close_up_rows(slots=(2, 1), verbose=True):
    """`--closeups [SLOT]`: which rows zoom the panel, and the camera of each.

    The panel does not draw with one camera.  With a head row under the cursor
    the game moves the camera onto the head (pitfall 67), and this is what says
    WHICH rows do it -- every one of the twelve walked in the game, in both
    slots, rather than the ones whose name sounds like a head.

    The comparison is exact and the controls come first:

      **the loading row twice** -- the camera has to come back number for
          number, or no difference below is a difference;
      **a row that does not zoom equals the loading row EXACTLY** -- so
          "zooms" is a discrete answer and not a threshold;
      **a zooming row twice** -- the same walk has to give the same camera,
          which is what makes the file this writes worth drawing with.

    Each zooming row's camera is written to `work/looks-camera/slotN-ROW.json`,
    which is what `scene.load_camera` reads when the cursor is on that row.
    """
    ready = preflight()
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for slot in slots:
            print("  -- slot %d (%s) --" % (slot, SLOTS[slot]))
            base = capture_camera(game, slot, 0, None)
            again = capture_camera(game, slot, 0, None)
            if base["camera"] != again["camera"] or \
                    base["projection"] != again["projection"]:
                problems.append("slot %d: the loading row's camera read twice "
                                "differs, so nothing below is measured" % slot)
                continue
            print("    control: the loading row (%s) read twice, camera "
                  "identical: translation %s, H %d"
                  % (CURSOR_STARTS_ON, base["camera"]["translation"],
                     base["projection"][0]["H"]))
            zoomed, flat = {}, []
            for row in ROWS:
                record = capture_camera(game, slot, 0, row)
                same = (record["camera"] == base["camera"]
                        and record["projection"] == base["projection"])
                print("    %-9s translation %-22s H %4d  %s"
                      % (row, record["camera"]["translation"],
                         record["projection"][0]["H"],
                         "the loading row's camera" if same else "ZOOMS"))
                if same:
                    flat.append(row)
                else:
                    zoomed[row] = record
            if not zoomed:
                problems.append("slot %d: no row moved the camera, and the "
                                "close-up is measured (LOOKS-TASK-28)" % slot)
                continue
            if not flat:
                problems.append("slot %d: every row moved the camera, so "
                                "'zooms' says nothing about the row" % slot)
                continue
            print("    %d row(s) zoom (%s) and %d keep the loading row's "
                  "camera (%s)" % (len(zoomed), ", ".join(sorted(zoomed)),
                                   len(flat), ", ".join(flat)))
            witness = sorted(zoomed)[0]
            twice = capture_camera(game, slot, 0, witness)
            if twice["camera"] != zoomed[witness]["camera"]:
                problems.append("slot %d: %s read twice gives two cameras, so "
                                "the file would not be a measurement"
                                % (slot, witness))
                continue
            print("    control: %s read twice, camera identical" % witness)
            for row in sorted(zoomed):
                print("    wrote %s" % write_camera(zoomed[row]))
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --closeups: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


STATURE_DIR = os.path.join(ROOT, "work", "looks-stature")
"""Where `--stature` writes what it captured, one JSON per slot."""

STATURE_POSED = (
    ("state", ()),
    ("state again", ()),
    ("155 cm", (("HEIG", "155 cm"),)),
    ("210 cm", (("HEIG", "210 cm"),)),
    ("B TYPE", (("BODY", "B TYPE"),)),
    ("C TYPE", (("BODY", "C TYPE"),)),
    ("D TYPE", (("BODY", "D TYPE"),)),
    ("E TYPE", (("BODY", "E TYPE"),)),
    ("F TYPE", (("BODY", "F TYPE"),)),
    ("G TYPE", (("BODY", "G TYPE"),)),
    ("H TYPE", (("BODY", "H TYPE"),)),
    ("155 cm, H TYPE", (("HEIG", "155 cm"), ("BODY", "H TYPE"))),
)
"""The captures of `--stature` that carry a pose pass, in order.

The state's own values twice -- the control, which has to come back on the
same frames of the walk with the same camera, and identical number by number
on every piece that read the same pair -- then the two ends of `HEIG` (the state's 175 is the middle),
every other `BODY`, and one of each together: a rule that holds for the rows
one at a time could still be two rules that do not compose.
"""

STATURE_SETTLE = 60
"""Frames let run after the last press, before the first pass is read."""

STATURE_PASSES = 80
"""Draw passes a capture may read, one after another, to meet its frame.

**The same frame is the same frame of ANIME.BIN, named by the pairs -- not the
same counted frame.**  The first version padded every capture to one counted
frame from `load_state`, and it does not hold: measured 2026-09-18, the
captures walked to 155 and to 210 cm came back with no pair at all where the
state, padded to the same count, had twelve -- a change of value moves the
walk's phase.  So each capture reads passes until one carries the control's
own pairs, and a capture that never meets them in this many is a failure, not
a pose.  The walk cycle comes round long before: the pose captures on disk
repeat their frames within 80 counted frames.
"""


def _stature_presses(table, slot, row, text):
    """(button, count) that walks *row* from the state's value to *text*."""
    import screen

    state = screen.State(table, slot)
    target = screen.index_of(table, row, text)
    count = target - state.indices[row]
    return ("Right" if count > 0 else "Left", abs(count))


def _stature_walk(game, slot, steps, table):
    """Put *steps* on the game's screen; returns the presses it cost."""
    import confront

    here = CURSOR_STARTS_ON
    presses = 0
    for row, text in steps:
        way = "Down" if ROWS.index(row) > ROWS.index(here) else "Up"
        for _ in range(abs(ROWS.index(row) - ROWS.index(here))):
            game.press(way, box=FOOTER, least=ROW_MOVED)
            presses += 1
        here = row
        button, count = _stature_presses(table, slot, row, text)
        for _ in range(count):
            confront.press_value(game, button, row, oracle_module())
            presses += 1
    return presses


def oracle_module():
    """This module, for the helpers of `confront` that take it as an argument."""
    return sys.modules[__name__]


def _stature_capture(game, slot, steps, table, maps, names, reference,
                     anime_data):
    """One capture, on the control's frames of the walk.

    *reference* is the control's frames (`_stature_frames`), and passes are
    read one after another until one draws them (`STATURE_PASSES`); how many
    it took is kept beside the capture.  None makes this the CONTROL, which
    takes the first pass that is two things:

      **every piece carries a pair** -- a pass with eleven came back 0 of 11
          exact on 2026-09-18: the game was interpolating (the averaging at
          0x80011F90..0x800120D0, `(a+b)>>1` per term), so the pairs were read
          and the matrices are not the file's;
      **the pose reader reproduces it whole** at the state's own camera --
          on the goalkeeper the pieces of walk frame 0 come back off the file
          with the angles in scratchpad EQUAL to the file's, at the state's own
          stature as much as at any other -- the refused passes are printed,
          with how far their worst piece is off.  Frame 0 is where
          the cycle wraps and the game blends it (task 26's "mistura"): the
          pose reader's open question, not the stature's, and a control on it
          would charge it to the rule.
    """
    restore_state(slot, verbose=False)
    game.load_looks(slot, label="stature-%d" % slot)
    _stature_walk(game, slot, steps, table)
    game.step(STATURE_SETTLE)
    for passes in range(1, STATURE_PASSES + 1):
        figure = _figure_now(game)
        pieces = _pose_cycle(game, maps, names)
        frames = _stature_frames(pieces, anime_data)
        if frames is None or (reference is not None and frames != reference):
            continue
        record = {"steps": [list(one) for one in steps], "passes": passes,
                  "frames": list(frames), "figure": figure,
                  "camera": _camera_matrix(game), "pieces": pieces}
        if reference is None:
            exact, total, misses = _stature_pieces(record, anime_data)
            if exact != total:
                print("      control refuses pass %d, frames %s: %d of %d "
                      "exact, %s off by up to %d of 4096 with the scratchpad "
                      "angles the file's own"
                      % (passes, list(frames), exact, total, misses,
                         _stature_worst(record, anime_data)))
                continue
        return record
    raise OracleError("slot %d, %r: %d passes and none on the control's "
                      "frame of the walk" % (slot, steps, STATURE_PASSES))


def _stature_pairs(pieces):
    """{piece: pair} -- by NAME, never by position in the pass."""
    return {one["piece"]: one.get("pair") for one in pieces}


def _stature_frames(pieces, anime_data):
    """The frames of the walk a pass drew, as a sorted tuple, or None.

    None unless EVERY piece carries a pair.  **A pass is usually two frames,
    not one**: measured 2026-09-18, the walk advances in the middle of a draw
    pass, so a pass reads frames (1, 2) or (3, 4) -- split between them at a
    piece that moves with the phase.  Two captures of the same frames split
    them at different pieces, and a comparison of the pairs piece by piece
    spent eighty passes looking for a split it would not meet.  The frames are
    what names the pose; the split is where the draw happened to be.
    """
    import anime

    pairs = [one.get("pair") for one in pieces]
    if any(one is None for one in pairs):
        return None
    entry = anime.header(anime_data)[layout.ANIME_SCREEN_ENTRY]
    return tuple(sorted({anime.frame_of_pair(anime_data, entry, one)
                         for one in pairs}))


def _stature_worst(record, anime_data):
    """The largest term any piece of *record* is off the chain by."""
    import anime
    import stature

    worst = 0
    for piece in record["pieces"]:
        first, second = struct.unpack(
            "<2I", anime_data[piece["pair"]:piece["pair"] + 8])
        rotation, _place = stature.piece(record["camera"],
                                         anime.rotation(anime.angles(first)),
                                         anime.position(first, second))
        worst = max([worst] + [abs(one - two) for one, two
                               in zip(rotation, piece["rotation"])])
    return worst


def _stature_values(table, slot, steps):
    """{height, build} on screen after *steps*, off the measured table."""
    import screen

    state = screen.State(table, slot)
    for row, text in steps:
        state.indices[row] = screen.index_of(table, row, text)
    values = state.values()
    return values["height"], values["build"]


def _stature_pieces(record, anime_data):
    """(exact, total, misses) of the pieces that carry a pair."""
    import anime
    import stature

    exact, total, misses = 0, 0, []
    for piece in record["pieces"]:
        at = piece.get("pair")
        if at is None:
            continue
        first, second = struct.unpack("<2I", anime_data[at:at + 8])
        rotation, place = stature.piece(record["camera"],
                                        anime.rotation(anime.angles(first)),
                                        anime.position(first, second))
        total += 1
        if (rotation, place) == (piece["rotation"], piece["translation"]):
            exact += 1
        else:
            misses.append(piece["piece"])
    return exact, total, misses


def check_stature(slot=None, verbose=True):
    """`--stature [SLOT]`: what `HEIG` and `BODY` do, measured against the rule.

    Two halves, and the controls close first in each:

      **the pose** -- `STATURE_POSED`, every capture on the same frames of
          the walk: the state twice (the same, or nothing below means anything),
          then the ends of `HEIG`, every `BODY` and one of each together.  For
          each, the scale vector the game holds against `stature.scale`, the
          camera it loads against `stature.camera`, and every piece that
          carries a pair against `stature.piece` -- exact, integer for
          integer.  And the pairs of every capture have to be the control's:
          the same frame of the walk, so the only thing that moved is the
          stature;
      **the walk** -- every value of `HEIG` and of `BODY`, one press at a
          time from the state's own, the scale vector and the camera load
          read after each press and held against the rule.  Two different
          values have to give two different loads, or the capture is reading
          a constant.
    """
    import iso_source
    import screen
    import stature

    ready = preflight()
    table = screen.load()
    with iso_source.open_disc(ready["image"]) as disc:
        found = stature.rule(disc.read(layout.SELECT8))
        anime_data = disc.read(layout.ANIME)
    maps = model_maps(ready["image"])
    names, _orders = piece_names(ready["image"])
    slots = (slot,) if slot else tuple(sorted(SLOTS, reverse=True))
    problems = []
    written = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        for one in slots:
            print("  -- slot %d (%s) --" % (one, SLOTS[one]))
            first = _stature_capture(game, one, (), table, maps, names,
                                     None, anime_data)
            chain = _camera_chain(game)
            print("    the chain: view %s %s, figure turned %s at %s, scale %s"
                  % (chain["view"]["rotation"], chain["view"]["translation"],
                     chain["angles"], chain["place"], chain["scale"]))
            reference = tuple(first["frames"])
            own = _stature_pairs(first["pieces"])
            records = []
            for name, steps in STATURE_POSED:
                record = (first if name == "state" else
                          _stature_capture(game, one, steps, table, maps,
                                           names, reference, anime_data))
                height, build = _stature_values(table, one, steps)
                record.update(name=name, height=height, build=build)
                records.append(record)
                want = stature.scale(found, height, build)
                built = stature.camera(chain, want)
                exact, total, misses = _stature_pieces(record, anime_data)
                pairs = _stature_pairs(record["pieces"])
                shared = sum(1 for piece, pair in pairs.items()
                             if own.get(piece) == pair)
                marks = []
                if tuple(record["figure"]["scale"]) != want:
                    marks.append("scale %s, the rule says %s"
                                 % (record["figure"]["scale"], list(want)))
                if (record["camera"]["rotation"] != built["rotation"]
                        or record["camera"]["translation"]
                        != built["translation"]):
                    marks.append("camera %s, the chain says %s"
                                 % (record["camera"], built))
                if exact != total:
                    marks.append("pieces %s off the chain" % misses)
                if tuple(record["frames"]) != reference or total != len(pairs):
                    marks.append("not the control's frames of the walk: %s"
                                 % record["frames"])
                for mark in marks:
                    problems.append("slot %d, %s: %s" % (one, name, mark))
                print("    %-15s %3d cm %s  scale %-18s pieces %2d/%-2d exact"
                      ", frames %s, %2d with the control's own pair  %s"
                      % (name, height, "ABCDEFGH"[build],
                         tuple(record["figure"]["scale"]), exact, total,
                         record["frames"], shared,
                         "ok" if not marks else "PROBLEM"))
            # The control: the state twice.  The SAME frames of the walk, the
            # same camera and scale, and every piece that carries the same
            # pair carrying the same matrix.  Not the whole pass number for
            # number: under free running the fork does not repeat the pass at
            # which the walk's two frames split -- measured 2026-09-18 on the
            # goalkeeper, both captures on frames (3, 4) and 9 of 12 pieces on
            # the same pair -- and the split is where the draw happened to be,
            # not a property of the pose (pitfall 73).
            one_, two_ = records[0], records[1]
            same = [piece for piece in one_["pieces"]
                    if _stature_pairs(two_["pieces"]).get(piece["piece"])
                    == piece["pair"]]
            twin = {piece["piece"]: piece for piece in two_["pieces"]}
            agree = all((piece["rotation"], piece["translation"])
                        == (twin[piece["piece"]]["rotation"],
                            twin[piece["piece"]]["translation"])
                        for piece in same)
            if (one_["frames"] != two_["frames"]
                    or one_["camera"] != two_["camera"]
                    or one_["figure"] != two_["figure"] or not agree
                    or not same):
                problems.append("slot %d: the state captured twice differs, "
                                "so nothing else here is a measurement" % one)
            else:
                print("    control: the state captured twice -- the same "
                      "frames %s, camera and scale, and the %d piece(s) on "
                      "the same pair identical number by number"
                      % (one_["frames"], len(same)))
            loads = {tuple(r["camera"]["rotation"]) for r in records}
            print("    %d captures, %d different camera loads, translation "
                  "%s in all of them"
                  % (len(records), len(loads),
                     "the same" if len({tuple(r["camera"]["translation"])
                                        for r in records}) == 1
                     else "NOT the same"))
            walked = _stature_walk_all(game, one, table, found, chain,
                                       problems)
            os.makedirs(STATURE_DIR, exist_ok=True)
            path = os.path.join(STATURE_DIR, "slot%d.json" % one)
            import json

            with open(path, "w", encoding="utf-8") as handle:
                json.dump({"slot": one, "rule": found, "chain": chain,
                           "posed": records,
                           "walked": walked}, handle, indent=1)
                handle.write("\n")
            written.append(path)
    for path in written:
        print("  wrote %s" % path)
    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --stature: %d problem(s) over %d slot(s)"
          % (len(problems), len(slots)))
    return 1 if problems else 0


def _stature_walk_all(game, slot, table, found, chain, problems):
    """Every value of HEIG and BODY, a press at a time, against the rule."""
    import confront
    import screen
    import stature

    walked = []
    for row in ("HEIG", "BODY"):
        texts = table["rows"][row]["texts"]
        start = screen.State(table, slot).indices[row]
        for button, ends in (("Left", 0), ("Right", len(texts) - 1)):
            if start == ends:
                continue
            restore_state(slot, verbose=False)
            game.load_looks(slot, label="stature-walk-%d" % slot)
            for _ in range(ROWS.index(row) - ROWS.index(CURSOR_STARTS_ON)):
                game.press("Down", box=FOOTER, least=ROW_MOVED)
            for index in range(start, ends, 1 if button == "Right" else -1):
                confront.press_value(game, button, row, oracle_module())
                text = texts[index + (1 if button == "Right" else -1)]
                height, build = _stature_values(table, slot, ((row, text),))
                figure = _figure_now(game)
                load = _camera_matrix(game)
                want = stature.scale(found, height, build)
                built = stature.camera(chain, want)
                good = (tuple(figure["scale"]) == want
                        and load["rotation"] == built["rotation"]
                        and load["translation"] == built["translation"])
                if not good:
                    problems.append("slot %d, %s %s: scale %s camera %s, the "
                                    "rule says %s and %s"
                                    % (slot, row, text, figure["scale"],
                                       load, list(want), built))
                walked.append({"row": row, "text": text, "height": height,
                               "build": build, "scale": figure["scale"],
                               "camera": load, "ok": good})
    heights = sorted({one["height"] for one in walked if one["row"] == "HEIG"}
                     | {screen.State(table, slot).values()["height"]})
    builds = sorted({one["build"] for one in walked if one["row"] == "BODY"}
                    | {screen.State(table, slot).values()["build"]})
    loads = {tuple(one["camera"]["rotation"]) for one in walked}
    print("    walk: %d presses, %d heights (%d..%d cm) and %d builds, %d of "
          "them off the rule; %d different camera loads"
          % (len(walked), len(heights), heights[0], heights[-1], len(builds),
             sum(1 for one in walked if not one["ok"]), len(loads)))
    if len(loads) != len(walked):
        problems.append("slot %d: %d presses and only %d different loads -- "
                        "two values drew the same camera"
                        % (slot, len(walked), len(loads)))
    return walked


def check_pose_frames(slot=None, frames=None, verbose=True):
    """`--pose <SLOT> <N> [N ...]`: the pose of counted frames, per piece.

    The gabarito of Phase 9, and the shape of the run is the argument:

      **the control before the measurement** -- the first frame is captured
          TWICE and the two have to be identical number by number.  A capture
          that does not repeat measures the emulator's mood, and every number
          under it would be a reading;
      **two different N differ** -- without it a capture that reads a
          constant passes the control perfectly;
      **whose matrix is whose** -- the piece registers name the section at
          each stop, and `pieces.py` names the section;
      **absolute or composed** -- `M x Mt` against the camera's `C x Ct`,
          which is zero only when the matrix is the camera composed with a
          true rotation;
      **the hierarchy** -- the child's origin in the parent's own frame,
          across the frames: constant where there is a joint, swinging where
          there is not.
    """
    ready = preflight()
    slots = (slot,) if slot else tuple(sorted(SLOTS))
    wanted = tuple(frames) if frames else POSE_CAPTURE_FRAMES
    if len(wanted) < 2:
        raise OracleError("two frames at least, or nothing says the capture "
                          "is not reading a constant (got %r)" % (wanted,))
    problems = []
    with Oracle(ready["cue"], verbose=verbose) as game:
        maps = model_maps(ready["image"])
        names, orders = piece_names(ready["image"])
        for one in slots:
            print("  -- slot %d (%s) --" % (one, SLOTS[one]))

            # The control, before anything below is read as a measurement.
            first = capture_pose(game, one, wanted[0], maps, names)
            again = capture_pose(game, one, wanted[0], maps, names)
            if first != again:
                problems.append(
                    "slot %d: two captures of frame %d differ, so the capture "
                    "is not repeatable and no number under it means anything"
                    % (one, wanted[0]))
                _say_pose(first)
                _say_pose(again)
                continue
            print("    control: frame %d captured twice, %d load(s), "
                  "identical number by number"
                  % (wanted[0], len(first["pieces"])))

            taken = [first]
            for frame in wanted[1:]:
                taken.append(capture_pose(game, one, frame, maps, names))
            for record in taken:
                print("    wrote %s" % write_pose(record))
            if verbose:
                _say_pose(taken[0])

            # A pass whose loads are all the same numbers is not a pose,
            # however well it repeats.  Measured over 16 passes on both
            # slots: all twelve loads differ, every time.  Planting the
            # camera's own base register on the piece load -- so every piece
            # is read off the camera -- gives twelve identical loads, a
            # hierarchy of zero spreads and the head at the height of the
            # feet, and the run was GREEN until this check existed.
            for record in taken:
                distinct = {(tuple(piece["rotation"]),
                             tuple(piece["translation"]))
                            for piece in record["pieces"]}
                if len(distinct) != len(record["pieces"]):
                    problems.append(
                        "slot %d frame %d: %d of the %d loads carry the same "
                        "numbers as another -- a pass in which the pieces do "
                        "not differ is not a pose, whatever it repeats like"
                        % (one, record["frame"],
                           len(record["pieces"]) - len(distinct),
                           len(record["pieces"])))

            # A capture that reads a constant passes the control perfectly.
            moved = [record for record in taken[1:]
                     if _by_piece(record) != _by_piece(taken[0])]
            if not moved:
                problems.append(
                    "slot %d: frames %s all read the same numbers as frame "
                    "%d -- the capture is reading a constant"
                    % (one, list(wanted[1:]), wanted[0]))

            # Every pass draws the same pieces, or the draw order is not what
            # closes a pass and the captures are not comparable.
            sets = {tuple(sorted(_by_piece(record))) for record in taken}
            if len(sets) != 1:
                problems.append("slot %d: the passes drew %d different sets "
                                "of pieces: %r" % (one, len(sets),
                                                   sorted(sets)))
                continue
            drawn = set(sets.pop())
            print("    %d piece(s) every pass: %s"
                  % (len(drawn), ", ".join(sorted(drawn))))
            figure = {name for (where, name) in names.items()
                      if where[0] == layout.EDT_MOD}
            never = sorted(name for name in figure
                           if name not in drawn) if figure else []
            if never:
                print("    named by pieces.py and never loaded here: %s "
                      "-- the other figure's list, plus whatever this screen "
                      "does not draw" % ", ".join(never))
            # A piece of THIS figure's list that no load names is either not
            # drawn or drawn under somebody else's matrix, and the two call
            # for different readers.  A read watchpoint tells them apart, with
            # a section the same pass drew as the control for the instrument.
            drawn_here = {piece["section"] for piece in taken[0]["pieces"]
                          if piece["file"] == layout.EDT_MOD}
            # This slot's own list, picked by what it drew: the file holds two
            # figures and the goalkeeper's sections are 11..19, so asking
            # after list 0's sections on slot 1 watches the OTHER player and
            # reads his absence as a finding.
            mine = max(orders.values(),
                       key=lambda order: len(drawn_here & set(order)))
            missing = [index for index in sorted(mine)
                       if index not in drawn_here]
            if missing:
                control = sorted(drawn_here)[-1]
                wanted_sections = [(layout.EDT_MOD, control)]
                wanted_sections += [(layout.EDT_MOD, index)
                                    for index in missing]
                read = _sections_read(game, maps, wanted_sections)
                for where, count in sorted(read.items(),
                                           key=lambda pair: pair[0][1]):
                    print("      section %-2d (%-12s) read %d time(s)%s"
                          % (where[1], names.get(where, "?"), count,
                             "   <- control, drawn this pass"
                             if where[1] == control else ""))
                loads = sorted(set(
                    piece["section"] for piece in taken[0]["pieces"]
                    if piece["file"] == layout.EDT_MOD))
                for index in missing:
                    if read[(layout.EDT_MOD, index)]:
                        # NOT "drawn without a matrix".  The pass loads one
                        # matrix per drawn section; what this section has no
                        # share of is a NAME, because a load is named by the
                        # model pointer of the stop after it and the first
                        # stop of a pass carries none (CORR-LOOKS-062).  The
                        # nameless load is this one, and the ankle says so.
                        print("      section %d is READ and no load NAMES it: "
                              "a load is named by the pointer of the next "
                              "stop, and the first stop of a pass carries no "
                              "pointer, so the load of the piece drawn before "
                              "it goes unnamed.  %d load(s) name a section "
                              "this pass: %s -- and the unnamed one is %s "
                              "(`anime.PIECE_ORDER`, `LAG_CHAIN`)"
                              % (index, len(loads),
                                 ", ".join(str(one) for one in loads),
                                 UNPOINTED_PIECE))
                if not read[(layout.EDT_MOD, control)]:
                    problems.append(
                        "slot %d: section %d is drawn every pass and a read "
                        "watchpoint over it never fired, so silence over the "
                        "others means nothing" % (one, control))

            # Absolute, or each piece's own turn?  M x Mt against C x Ct.
            worst = 0.0
            for record in taken:
                camera = record["camera"]["rotation"]
                for piece in record["pieces"]:
                    deviation = matrix_deviation(piece["rotation"], camera)
                    worst = max(worst, deviation)
                    if deviation > MATRIX_TOLERANCE:
                        problems.append(
                            "slot %d frame %d: %s sits %.4f from the camera's "
                            "own product, over the %.4f a rounded rotation "
                            "takes -- this matrix is not the camera composed "
                            "with a rotation"
                            % (one, record["frame"], piece["id"],
                               deviation, MATRIX_TOLERANCE))
            print("    every matrix is the camera composed with a rotation: "
                  "worst |M x Mt - C x Ct| is %.4f of the largest entry "
                  "(threshold %.4f)" % (worst, MATRIX_TOLERANCE))

            mirrored = sorted(piece["id"] for piece in taken[0]["pieces"]
                              if _determinant(piece["rotation"]) < 0)
            print("    %d of %d carry a mirrored matrix (negative "
                  "determinant): %s"
                  % (len(mirrored), len(taken[0]["pieces"]),
                     ", ".join(mirrored) or "none"))

            # The hierarchy, from the frames themselves.
            tree = hierarchy([_by_piece(record) for record in taken])
            for child in sorted(tree):
                found = tree[child]
                verdict = ("child of %s" % found["parent"]
                           if found["gap"] >= HIERARCHY_GAP else "no parent")
                print("      %-13s %-22s spread %7.1f, next %s at %7.1f "
                      "(%.1fx)"
                      % (child, verdict, found["spread"], found["runner_up"],
                         found["runner_up_spread"], found["gap"]))
            joined = [child for child in tree
                      if tree[child]["gap"] >= HIERARCHY_GAP]
            if not joined:
                problems.append("slot %d: no piece hangs off another by more "
                                "than %.1fx, so these frames name no "
                                "hierarchy" % (one, HIERARCHY_GAP))

            # The sign of y, against the UP = -1 the v1 already draws with.
            head = _by_piece(taken[0]).get("head")
            feet = [piece for piece in taken[0]["pieces"]
                    if piece["piece"] and piece["piece"].startswith("foot")]
            if head and feet:
                low = max(piece["translation"][1] for piece in feet)
                print("    y grows %s: the head sits at y=%d and the lowest "
                      "foot at y=%d"
                      % ("DOWNWARD, as scene.UP = -1 already assumes"
                         if low > head["translation"][1] else "UPWARD",
                         head["translation"][1], low))

    for line in problems:
        print("  FAIL  %s" % line)
    print("oracle --pose: %d problem(s) over %d frame(s) and %d slot(s)"
          % (len(problems), len(wanted), len(slots)))
    return 1 if problems else 0


def check_default(slot=2, verbose=True):
    """`--default`: what `NAT` and `DEFAUL` do, measured in the game.

    The task this answers assumed the two rows were the halves of a default
    look per nationality, over `data/defaultlook.txt`.  They are not, and the
    shape of this run is what says so rather than asserting it:

      for each nation, the five look rows are read BEFORE and AFTER pressing
          Circle on `DEFAUL`, and so is the twelve-byte record.  A default
          being applied would move them;
      the file's line for that nation is printed beside them, so a reader sees
          what would have changed if it had been;
      the nationality byte is read at `layout.PLAYER_NATION`, which is where
          the choice DOES land, and checked against the row's own index;
      the control is the same nation reached twice, which has to read the
          same -- without it a difference between two nations says nothing.
    """
    import looks
    import screen

    table = screen.load()
    geometry = _screen_geometry(table)
    orders = table["orders"]
    texts = table["rows"]["NAT"]["texts"]
    lines = looks.nation_lines(texts)
    ready = preflight()
    problems, applied = [], []

    def rows(game):
        return ScreenReading(geometry, screen_objects(game)).rows(orders)

    def walk_to(game, nation):
        game.load_looks(slot)
        for _ in range(texts.index(nation)):
            tap(game, "Right")
        return rows(game)

    with Oracle(ready["cue"], verbose=verbose) as game:
        restore_state(slot, verbose=verbose)

        # The control first: one nation reached twice, from load_state both
        # times, has to read the same row, the same five looks and the same
        # nationality byte.
        first = walk_to(game, NATIONS[0])
        first_byte = _nation_byte(game)
        again = walk_to(game, NATIONS[0])
        again_byte = _nation_byte(game)
        if first != again or first_byte != again_byte:
            print("  FAIL  control: %s read %r/%r and then %r/%r"
                  % (NATIONS[0], first, first_byte, again, again_byte))
            print("oracle --default: the control failed, so no difference "
                  "below would mean anything")
            return 1
        print("  control: %s twice from load_state reads the same row, the "
              "same five looks and the same nationality byte %r"
              % (NATIONS[0], first_byte))

        # The whole row, one press at a time, reading the byte at each value.
        # Every value and not a sample: the code runs with the index for
        # fifty-four values and then jumps 41, and a sample of five would have
        # been taken for "the code is the index minus one" -- which is what
        # the first run of this command reported, until `Algeria` disagreed.
        game.load_looks(slot)
        codes = []
        for index in range(len(texts)):
            if index:
                tap(game, "Right")
            codes.append(_nation_byte(game))
        for index, byte in enumerate(codes):
            if index == looks.UNKNOWN_NATION:
                if byte[0] == byte[1]:
                    problems.append("the two copies agree on %r before a "
                                    "nation was chosen, and the measurement "
                                    "says they do not" % texts[index])
                continue
            if byte[0] != byte[1]:
                problems.append("%s: the two copies read %r"
                                % (texts[index], byte))
            want = looks.nation_code(index)
            if byte[0] != want:
                problems.append("%s is value %d of the row and stores %d; "
                                "looks.NATION_CODES says %d"
                                % (texts[index], index, byte[0], want))
        # Written over the runs the rule declares, not over two: a planted
        # rule with one run has to reach the comparison and report what it
        # got wrong, and an index error here would be a red that measured
        # nothing (trap 27 of the profile).
        jumps = ["%r (%d to %d)" % (texts[first], codes[first - 1][0],
                                    codes[first][0])
                 for first, _last, _add in looks.NATION_CODES[1:]]
        print("  the row's %d value(s) walked: codes %d..%d%s"
              % (len(texts), codes[1][0], codes[-1][0],
                 ", with the jump at %s" % ", ".join(jumps) if jumps
                 else ", in one run"))

        for nation in NATIONS:
            index = texts.index(nation)
            before = walk_to(game, nation)
            record_before = screen_record(game)
            nation_byte = _nation_byte(game)
            if before["NAT"] != nation:
                problems.append("walking to %s left the row on %r"
                                % (nation, before["NAT"]))
                continue
            tap(game, "Up")          # NAT is one below DEFAUL
            tap(game, "Circle")      # the confirm, which is what DEFAUL is
            game.step(CONFIRM_SETTLE)
            after_byte = _nation_byte(game)
            # The screen is gone by now, so the rows are read from the RAM the
            # print routine last wrote plus the record, which survives.
            record_after = screen_record(game)
            line = lines["paired"].get(index)
            moved = {name: (record_before[looks.BY_ROW[name].name],
                            record_after[looks.BY_ROW[name].name])
                     for name in LOOK_ROWS
                     if record_before[looks.BY_ROW[name].name]
                     != record_after[looks.BY_ROW[name].name]}
            if moved:
                applied.append((nation, moved))
            if verbose:
                shown = {name: before[name] for name in LOOK_ROWS}
                print("  %-9s value %2d, nationality byte %r -> %r after the "
                      "confirm" % (nation, index, nation_byte, after_byte))
                print("            the screen showed %r" % shown)
                print("            defaultlook.txt says %s"
                      % ("%r" % (line[1],) if line else "nothing -- no line "
                                                        "of its own"))
                print("            the record moved: %s"
                      % (moved if moved else "nothing"))

    for line in problems:
        print("  FAIL  %s" % line)
    if applied:
        print("  DEFAUL moved the record on %d nation(s): %r"
              % (len(applied), applied))
    print("oracle --default: %d problem(s); DEFAUL applied a default on %d of "
          "%d nation(s)" % (len(problems), len(applied), len(NATIONS)))
    return 1 if problems else 0


def _differences(want, got, path=""):
    if isinstance(want, dict) and isinstance(got, dict):
        out = []
        for key in sorted(set(want) | set(got)):
            out += _differences(want.get(key), got.get(key),
                                "%s.%s" % (path, key) if path else key)
        return out
    return [] if want == got else [(path, want, got)]


# --- self-check -----------------------------------------------------------

def self_check(verbose: bool = True) -> int:
    return harness.run("oracle.py", _checks, verbose)


FIXED_ONE = 4096  # not-an-address: 1.0 in the 4.12 fixed point the GTE uses
SPAN = 4096  # not-an-address: the size of the made-up file the check builds


def _jal(target):
    """A `jal <target>` word, for the self-check's synthetic code."""
    return JAL << 26 | (target & ~RAM_BASE) >> 2


def _addiu_word(register, immediate):
    """An `addiu <register>, zero, <immediate>` word, likewise."""
    return ADDIU << 26 | register << 16 | (immediate & IMMEDIATE_FIELD)


def _synthetic_boot():
    """(code, base) of a made-up text segment carrying the help box's chain.

    Everything else in it is zero, which is what makes each refusal below the
    word it names: there is nothing else in the segment for `help_chain` to
    take for the chain.
    """
    base = layout.BOOT_BASE
    end = max(layout.HELP_GLYPH_CALL, layout.HELP_GLYPH_LOOKUP,
              layout.KROM_STUB) + 0x100  # not-an-address: room past the last word
    code = bytearray(end - base)
    for address, word in (
            (layout.HELP_GLYPH_CALL, _jal(layout.HELP_GLYPH_LOOKUP)),
            (layout.HELP_GLYPH_LOOKUP, _jal(layout.KROM_STUB)),
            (layout.KROM_STUB, _addiu_word(T2, layout.KROM_TABLE)),
            (layout.KROM_STUB + INSTRUCTION_SIZE,
             T2 << 21 | JR_FUNCT),
            (layout.KROM_STUB + 2 * INSTRUCTION_SIZE,
             _addiu_word(T1, layout.KROM_FUNCTION))):
        struct.pack_into("<I", code, address - base, word)
    return bytes(code), base


def _boot_without(address, word):
    """The synthetic segment with one word of the chain replaced."""
    code, base = _synthetic_boot()
    broken = bytearray(code)
    struct.pack_into("<I", broken, address - base, word)
    return bytes(broken)


def _synthetic_glyph(rows):
    """One character of the ROM, as its fifteen big-endian rows."""
    return struct.pack(">%dH" % len(rows), *rows)


class _FakeSection:
    """A section span for the self-check, with only what `attribute()` reads."""

    def __init__(self, offset, end):
        self.offset = offset
        self.end = end
        self.primitives = ()


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

    # The scan that finds where a matrix reaches the GTE, on words made here.
    # `ctc2 t0, r0` is 0x48C80000: COP2, CT, rt=t0, rd=0.
    matrix = (0x48C80000).to_bytes(4, "little")  # not-an-address: ctc2 t0, r0
    other = (0x48C80800).to_bytes(4, "little")  # not-an-address: ctc2 t0, r1
    mfc = (0x48080000).to_bytes(4, "little")  # not-an-address: mfc2, a read
    ok("the scan finds a ctc2 into the matrix's first register",
       _ctc2_matrix_loads(matrix) == [RAM_BASE])
    ok("and passes over a ctc2 into another control register",
       _ctc2_matrix_loads(other) == [])
    ok("and over an instruction that reads the GTE instead of writing it",
       _ctc2_matrix_loads(mfc) == [])
    ok("it reports the address of each hit, not the count",
       _ctc2_matrix_loads(mfc + matrix + other + matrix)
       == [RAM_BASE + 4, RAM_BASE + 12])

    # -- the pose capture's arithmetic, on matrices made here ---------------
    #
    # 4.12 is the scale, so the identity is 4096 on the diagonal, and a
    # quarter turn about y is the permutation with one sign flipped.
    one = [FIXED_ONE, 0, 0, 0, FIXED_ONE, 0, 0, 0, FIXED_ONE]
    turn = [0, 0, FIXED_ONE, 0, FIXED_ONE, 0, -FIXED_ONE, 0, 0]
    # Nine 4.12 matrix entries read off the live camera, one per line so the
    # rule-1 sweep sees each of them annotated.
    camera = [3195, 0, 635,  # not-an-address: 4.12 matrix entries
              -27, 2488, 133,  # not-an-address: 4.12 matrix entries
              -635, -268, 3195]  # not-an-address: 4.12 matrix entries
    ok("the identity times anything is that thing",
       _multiply(one, turn) == [value * FIXED_ONE for value in turn])
    ok("a quarter turn has determinant 4096 cubed",
       _determinant(turn) == FIXED_ONE ** 3)
    ok("and the mirror of it has the negative of that -- which is how a "
       "mirrored piece is told from a turned one",
       _determinant([-value for value in turn]) == -(FIXED_ONE ** 3))

    # The composition test: C times a rotation keeps C's own product, and a
    # matrix that is NOT C times a rotation does not.
    ok("the camera composed with a turn sits at zero from the camera",
       matrix_deviation([value // FIXED_ONE
                         for value in _multiply(camera, turn)],
                        camera) < MATRIX_TOLERANCE)
    ok("the camera without its own scale does not",
       matrix_deviation([FIXED_ONE if i in (0, 4, 8) else 0
                         for i in range(9)],
                        camera) > MATRIX_TOLERANCE)

    # The joint: a child that sits at a fixed point of the parent's frame
    # reads the same offset whatever the parent is doing.
    joint = [1000, 0, 0]  # not-an-address: a length in model units

    def hung(rotation, at):
        """A child hung at *joint* off a parent turned by *rotation*."""
        moved = [sum(rotation[row * 3 + k] * joint[k]
                     for k in range(3)) // FIXED_ONE
                 for row in range(3)]
        return {"rotation": rotation,
                "translation": [at[k] + moved[k] for k in range(3)]}

    parents = [{"rotation": one, "translation": [10, 20, 30]},
               {"rotation": turn, "translation": [40, 50, 60]}]
    children = [hung(parent["rotation"], parent["translation"])
                for parent in parents]
    offsets = [joint_offset(parent, child)
               for parent, child in zip(parents, children)]
    ok("a child hung off a parent reads the same joint under any turn",
       all(abs(offsets[0][k] - offsets[1][k]) < 2.0 for k in range(3)),
       "%r vs %r" % (offsets[0], offsets[1]))
    ok("and the joint it reads is the one it was hung at",
       all(abs(offsets[0][k] - joint[k]) < 2.0 for k in range(3)),
       "%r" % (offsets[0],))
    loose = [{"rotation": one, "translation": [0, 0, 0]},
             {"rotation": one, "translation": [500, 0, 0]}]
    adrift = [joint_offset(parents[i], loose[i]) for i in range(2)]
    ok("a child that is NOT hung off it reads a different joint each frame",
       max(abs(adrift[0][k] - adrift[1][k]) for k in range(3)) > 100,
       "%r vs %r" % (adrift[0], adrift[1]))

    # And the search over those offsets picks the parent, with the runner-up
    # beside it so the caller can see how clear the win was.
    frames = [{"p": parents[i], "kid": children[i], "away": loose[i]}
              for i in range(2)]
    tree = hierarchy(frames)
    ok("the search names the parent a piece is hung off",
       tree["kid"]["parent"] == "p", "%r" % (tree["kid"],))
    ok("and reports the runner-up it beat",
       tree["kid"]["runner_up"] in ("away",) and tree["kid"]["gap"] > 1.0)

    # -- the pass closes on the sequence repeating, not on a piece returning -
    #
    # The boots are one section drawn twice, so the easy rule -- cut when a
    # piece comes round -- drops the last load of the pass.
    twice = ["r", "h", "t", "f", "l", "f"]
    ok("a pass with a piece drawn twice is found whole, not cut at the repeat",
       _repeating_period(twice + twice) == len(twice))
    ok("one turn is not enough to call it a period",
       _repeating_period(twice) is None)
    ok("and a tail that happens to look like the head is not a period of one",
       _repeating_period(["a", "b", "c", "a"]) is None)
    # The pointers trail the matrix by `DRAW_LAG`, so a pass that DRAWS
    # torso, foot a, foot a carries them one stop late.
    named = _named_pass([{"piece": "foot a"}, {"piece": "torso"},
                         {"piece": "foot a"}])
    ok("a section drawn twice is two pieces, numbered",
       [one["id"] for one in named] == ["torso", "foot a", "foot a #2"],
       "%r" % ([one["id"] for one in named],))
    ok("and what the registers actually said is kept beside it",
       [one["pointer_piece"] for one in named]
       == ["foot a", "torso", "foot a"])
    ok("and the draw order is kept as the number the caller reads",
       [one["order"] for one in named] == [0, 1, 2])

    # -- the lag itself, on a skeleton whose joint is known ------------------
    #
    # A boot bolted rigidly to one shin, a second shin swinging on its own,
    # and the pointers written one stop late -- which is what the game does.
    # `draw_lag` has to find the one lag that makes the joint hold, and the
    # WRONG shin has to stay loose under it, or the measurement is picking a
    # lag that makes everything look attached.
    synthetic = _synthetic_pass()
    found = draw_lag(synthetic)
    ok("the draw lag is measured back off a pass that carries it",
       found["winner"] == DRAW_LAG, "%r" % (found["best"],))
    ok("and it wins by more than the margin the check demands",
       found["margin"] >= LAG_MARGIN, "%.1f" % found["margin"])
    ok("the shin the boot does NOT hang off stays loose at the winning lag",
       found["scored"][(DRAW_LAG, "shin b", "foot a")]
       > found["scored"][(DRAW_LAG, "shin a", "foot a")] * LAG_MARGIN)

    # The pointer is the witness that names the piece, and two sections at
    # one stop would mean it is not.
    class Where:
        pass

    attempt("two sections pointed at by one matrix load are refused",
            OracleError,
            lambda: _drawn_section({"s6": "0x8011C788", "s7": "0x8011CC78"},
                                   {layout.BASE[layout.EDT_MOD]: (
                                       layout.EDT_MOD, SPAN,
                                       [_FakeSection(0, SPAN // 2),
                                        _FakeSection(SPAN // 2,
                                                     SPAN)])}))

    # The session taken by another client, on a fake server (CORR-LOOKS-051).
    import io
    import contextlib
    import mcp

    class Fake:
        def __init__(self, losses, other=False):
            self.losses, self.other = losses, other
            self.session, self.server, self.handshakes, self.calls = "s", {}, 0, 0

        def initialize(self):
            self.handshakes += 1
            self.server = {}

        def call(self, name, **arguments):
            self.calls += 1
            if self.other:
                raise mcp.ToolError("HTTP 500 from the server: something else")
            if self.losses:
                self.losses -= 1
                raise mcp.ToolError("HTTP 400 from the server: Bad Request: "
                                    "missing or invalid MCP-Session-Id")
            return "done"

    once = Fake(1)
    wrapped = OneSession(once)
    said = io.StringIO()
    with contextlib.redirect_stdout(said):
        answer = attempt("a call whose session was taken",
                         lambda: wrapped.call("pause"))
    ok("a lost session is handshaken again once, and the call goes through",
       answer == "done" and once.handshakes == 1 and wrapped.renewed == 1,
       "%r %d" % (answer, once.handshakes))
    ok("and it says so", "taken by another client" in said.getvalue())
    twice = OneSession(Fake(2))
    with contextlib.redirect_stdout(io.StringIO()):
        c.refusing(mcp.ToolError)("lost again right after the new handshake "
                                  "raises", lambda: twice.call("pause"),
                                  "MCP-Session-Id")
    other = Fake(0, other=True)
    c.refusing(mcp.ToolError)("any other refusal raises with no handshake",
                              lambda: OneSession(other).call("pause"),
                              "something else")
    ok("and handshakes nothing", other.handshakes == 0)
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

    # -- the help box's chain, and the console's glyph ----------------------
    #
    # The chain is three instructions of `/SLPM_870.56` and the check is that
    # each is what it is said to be, so the cases are built here rather than
    # read: a synthetic text segment with the chain in it, then one word of it
    # broken at a time.
    code, base = _synthetic_boot()
    found = attempt("the chain of a synthetic boot segment",
                    lambda: help_chain(code, base))
    ok("the chain reads the lookup and the BIOS call out of the code",
       found is not None and found["calls"] == [layout.HELP_GLYPH_LOOKUP]
       and found["table"] == layout.KROM_TABLE, "%s" % (found,))
    for label, address, word in (
            ("the call is not a jal", layout.HELP_GLYPH_CALL, 0),
            ("the call goes somewhere else", layout.HELP_GLYPH_CALL,
             _jal(layout.KROM_STUB)),
            ("the lookup never reaches the BIOS stub",
             layout.HELP_GLYPH_LOOKUP, 0),
            ("the stub does not load the kernel's vector", layout.KROM_STUB,
             _addiu_word(T2, layout.KROM_TABLE + 1)),
            ("the stub does not jump through it",
             layout.KROM_STUB + INSTRUCTION_SIZE, 0),
            ("the stub asks for another function",
             layout.KROM_STUB + 2 * INSTRUCTION_SIZE,
             _addiu_word(T1, layout.KROM_FUNCTION + 1))):
        broken = _boot_without(address, word)
        c.refuses("%s: refused" % label,
                  lambda one=broken: help_chain(one, base), "", OracleError)
    c.refuses("a header that loads somewhere else is refused",
              lambda: boot_word(code, base, layout.BOOT_BASE - 4), "outside",
              OracleError)

    # One character of the console's ROM: fifteen big-endian rows, and the
    # tile the game uploads is those bits plus a one-pixel ring.
    glyph = _synthetic_glyph([0] + [0b0000001111000000] * 4 + [0] * 10)
    ink = krom_ink(glyph)
    ok("a glyph's rows are read big-endian, one bit a pixel",
       ink == {(x, y) for y in range(1, 5) for x in range(6, 10)},
       "%s" % (sorted(ink),))
    c.refuses("a glyph shorter than the ROM's 30 bytes is refused",
              lambda: krom_ink(glyph[:8]), "30 bytes", OracleError)
    # Two halfwords a row, four texels each: the second nibble of the first
    # halfword is texel 1, and the fourth nibble of the second is texel 7.
    tile = [[0x00F0, 0x0000], [0x0000, 0x3000]]  # not-an-address: two rows of texels
    ok("a 4-bit tile's ink is every texel that is not index 0",
       tile_ink(tile) == {(1, 0), (7, 1)}, "%s" % (sorted(tile_ink(tile)),))
    ok("the glyph is in the tile when the tile is it plus the outline",
       glyph_in_tile(ink, _dilated(ink)) == ([], []))
    ok("and it is not when a row of it is missing",
       glyph_in_tile(ink, {one for one in ink if one[1] != 2})[0] != [])
    ok("nor when the tile has ink two pixels off the glyph",
       glyph_in_tile(ink, ink | {(20, 20)})[1] == [(20, 20)])

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

    # -- a node of the list is not a command --------------------------------
    #
    # The shape libgs leaves in the list for one glyph: an E1 naming the page
    # and a variable sprite, in ONE node.  Then a 16x16 sprite behind its own
    # E1, and a flat quad, each a node.  The words are the ones the frame of
    # LOOKS SET carries: page 27 is VRAM (704, 256) at 4 bits, and CLUT id
    # 0x7C40 is (0, 497).
    font_page = DRAW_MODE_SET << 24 | 27
    plate_page = DRAW_MODE_SET << 24 | 29
    corner = (-7 & 0xFFFF) << 16 | (-43 & 0xFFFF)  # not-an-address: y, x
    texel = 0x7C40 << 16 | 146 << 8 | 126  # not-an-address: clut, v, u
    sprite = int("64", 16) << 24 | 0x808080  # not-an-address: code and colour
    tile = int("7C", 16) << 24 | 0x808080  # not-an-address: idem, 16x16
    quad = int("28", 16) << 24 | 0x303030  # not-an-address: a flat quad
    nodes = [(0, [font_page, sprite, corner, texel, 12 << 16 | 5]),
             (1, [plate_page, tile, corner, texel]),
             (2, [quad, corner, corner, corner, corner])]
    commands = commands_of(nodes)
    ok("a node holding a draw mode and a sprite splits into both",
       [one[0] >> 24 for one in commands]
       == [DRAW_MODE_SET, int("64", 16), DRAW_MODE_SET, int("7C", 16),
           int("28", 16)],
       [hex(one[0]) for one in commands])
    found = sprites_of(commands)
    ok("both sprites are found, and nothing else",
       len(found) == 2, len(found))
    if len(found) == 2:
        glyph, plate = found
        ok("the glyph takes the page of the E1 in its own node",
           glyph["page"] == (704, 256) and glyph["bits"] == 4,
           (glyph["page"], glyph["bits"]))
        ok("the tile takes the page of the E1 in ITS node, not the first one",
           plate["page"] == (832, 256), plate["page"])
        ok("and its CLUT, corner and texel come off the packet",
           glyph["clut"] == (0, 497) and glyph["uv"] == (126, 146)
           and glyph["point"] == (256 - 43, 120 - 7),
           (glyph["clut"], glyph["uv"], glyph["point"]))
        ok("a variable sprite reads its size, a fixed one knows it",
           glyph["size"] == (5, 12) and plate["size"] == (16, 16),
           (glyph["size"], plate["size"]))
        ok("the texels a 4-bit sprite samples are counted in halfwords",
           len(sprite_texels(glyph)) == 2 * 12, len(sprite_texels(glyph)))
    ok("and the quad behind them is still furniture",
       len(furniture_of(nodes)) == 1, len(furniture_of(nodes)))

    # A width-0 code (CORR-LOOKS-074): the game hands the GPU a 0-wide sprite
    # for it, `Font.run` hands nothing, and `font_sprites` is what makes the
    # two lists count alike.  The toy table with `@` made 0 wide; the game's
    # list is what `Font.run` lays, the 0-wide sprite put in where the game
    # would, and a sprite off the font's page.
    import glyphs

    toy = bytearray(glyphs._toy_table())
    toy[2 * (ord("@") - glyphs.FIRST) + 1] = 0
    laid = glyphs.Font(bytes(toy)).run("A@B", (0, 0), 1, (128,) * 3)
    blank = {"point": (0, 0), "size": (0, layout.GLYPH_HEIGHT),
             "page": layout.GLYPH_PAGE}
    other = {"point": (0, 0), "size": (16, 16), "page": (832, 256)}
    game_list = [dict(laid[0], page=layout.GLYPH_PAGE), blank,
                 dict(laid[1], page=layout.GLYPH_PAGE), other]
    ok("Font.run lays no sprite for a 0-wide code",
       [one["code"] for one in laid] == [ord("A"), ord("B")],
       [one["code"] for one in laid])
    ok("the game's font sprites, the 0-wide one dropped, count as Font.run's",
       len(font_sprites(game_list)) == len(laid),
       (len(font_sprites(game_list)), len(laid)))
    ok("and without the drop they would not: the control",
       len([one for one in game_list
            if tuple(one["page"]) == layout.GLYPH_PAGE]) == len(laid) + 1)

    # The line that differs to the RIGHT of an unchanged label
    # (CORR-LOOKS-078).  The leftmost glyph of a row is the label's, and a
    # misplaced value moves nothing about it, so a sentence that named the
    # first glyph of the line named the label on both sides and said nothing.
    # What it has to name is the first glyph each side draws and the other
    # does not.
    label = (200, 41, 184, 146)  # not-an-address: a glyph, (x, y, u, v)
    in_game = (421, 41, 46, 158)  # not-an-address: idem, where the game put it
    in_window = (176, 41, 46, 158)  # not-an-address: idem, where we put it
    # Sorted on both sides, the way the two readers hand them over: our copy
    # of the value is LEFT of the label it belongs to, and the game's right
    # of it, so the leftmost glyph of the line is the label on one side only.
    sentences = _glyph_differences([label, in_game], [in_window, label])
    ok("a value moved beside an unchanged label names the moved glyph",
       len(sentences) == 1 and "%s" % (in_game,) in sentences[0]
       and "%s" % (in_window,) in sentences[0], "%s" % (sentences,))
    ok("and not the label, which the two sides draw alike",
       bool(sentences) and "%s" % (label,) not in sentences[0],
       "%s" % (sentences,))
    ok("a line drawn the same on both sides says nothing",
       _glyph_differences([label, in_game], [label, in_game]) == [],
       "%s" % (_glyph_differences([label, in_game], [label, in_game]),))
    ok("a glyph one side draws and the other does not is named on its own",
       _glyph_differences([label, in_game], [label])
       == ["the glyphs on line y 41: the game draws 2, the first the window "
           "lacks [(421, 41, 46, 158)]; our window 1, the first the game "
           "lacks []"],
       "%s" % (_glyph_differences([label, in_game], [label]),))

    # The window's cursor box off its picture (CORR-LOOKS-070): a picture at
    # scale 2 with DEFAUL's box drawn the way the window draws it -- a one-
    # pixel outline of the scaled rectangle -- comes back in native pixels.
    table = {"display": [512, 240],
             "regions": {"rows": {"native": [176, 37, 496, 185]}}}
    scale, drawn = 2, (396, 41, 476, 52)
    picture = [[(0, 32, 48)] * (512 * scale) for _ in range(240 * scale)]
    left, top = drawn[0] * scale, drawn[1] * scale
    right, bottom = (drawn[2] + 1) * scale - 1, (drawn[3] + 1) * scale - 1
    for x in range(left, right + 1):
        picture[top][x] = picture[bottom][x] = (181, 181, 57)
    for y in range(top, bottom + 1):
        picture[y][left] = picture[y][right] = (181, 181, 57)
    ok("the window's cursor box reads back off its picture in native pixels",
       window_cursor(picture, 512 * scale, table) == list(drawn),
       window_cursor(picture, 512 * scale, table))
    ok("and a picture with no yellow in the rows box has no cursor box",
       window_cursor([[(0, 32, 48)] * 512 for _ in range(240)], 512, table)
       is None)
    c.refusing(OracleError)(
        "a picture whose width is not a multiple of the display's is refused",
        lambda: window_cursor(picture, 512 * scale + 1, table),
        "whole multiple")

    # The shape --walk-watch reports (CORR-LOOKS-092): named and unnamed
    # loads as runs, in order, with a lone unnamed load its own run.
    marks = [{"pair": 1}] * 3 + [{"pair": None}] * 2 + [{"pair": 4}]
    ok("the loads of a run come back as runs of named and unnamed",
       pair_runs(marks) == [("P", 3), (".", 2), ("P", 1)],
       "%s" % (pair_runs(marks),))
    ok("and a run with no load is no run", pair_runs([]) == [])


# --- entry point ----------------------------------------------------------

def row_and_slot(args) -> tuple:
    """(row, slot) out of `[<ROW> [<SLOT>]]`: HAIR and 2 when left out.

    The slot is what makes the goalkeeper's walk a command and not a script
    (CORR-LOOKS-047): both measurements always took it, and the command line
    only ever passed the row.
    """
    row = args[0] if args else "HAIR"
    if len(args) > 2:
        raise OracleError("a row and a slot at most, and got %r" % (args,))
    if len(args) < 2:
        return (row, 2)
    if not args[1].isdigit() or int(args[1]) not in SLOTS:
        raise OracleError("slot %r, and the states are %s"
                          % (args[1], sorted(SLOTS)))
    return (row, int(args[1]))


def main(argv):
    import screen

    # Before anything prints: a row's help carries `■`, and so does the error
    # this walk raises when the cursor missed a row (CORR-LOOKS-055).
    screen.printable_output()
    try:
        if len(argv) == 2 and argv[1] == "--check":
            return self_check()
        if len(argv) == 2 and argv[1] == "--check-states":
            return check_states()
        if len(argv) == 2 and argv[1] == "--adopt-states":
            return adopt_states()
        if len(argv) == 2 and argv[1] == "--check-live":
            return check_live()
        if len(argv) in (2, 3) and argv[1] == "--screen":
            if len(argv) == 3 and argv[2] != "--write":
                raise OracleError("--screen takes --write and nothing else, "
                                  "and got %r" % argv[2])
            return check_screen(write=len(argv) == 3)
        if len(argv) >= 2 and argv[1] == "--pose":
            # `--pose [SLOT]` is where the pose comes FROM (LOOKS-TASK-24);
            # naming frames after the slot captures the pose itself
            # (LOOKS-TASK-25).  One flag, because they answer one question
            # from two ends and share every prerequisite.
            if len(argv) > 3:
                return check_pose_frames(int(argv[2]),
                                         [int(one) for one in argv[3:]])
            return check_pose(int(argv[2]) if len(argv) > 2 else None)
        if len(argv) >= 2 and argv[1] == "--camera":
            return check_camera(int(argv[2]) if len(argv) > 2 else None,
                                row=argv[3] if len(argv) > 3 else None)
        if len(argv) in (2, 3) and argv[1] == "--walk":
            return check_walk(int(argv[2]) if len(argv) == 3 else None)
        if len(argv) in (2, 3) and argv[1] == "--walk-watch":
            return check_walk_watch(int(argv[2]) if len(argv) == 3 else 2)
        if len(argv) == 2 and argv[1] == "--pose-lag":
            return check_draw_lag()
        if len(argv) in (2, 3) and argv[1] == "--stature":
            return check_stature(int(argv[2]) if len(argv) > 2 else None)
        if len(argv) >= 2 and argv[1] == "--poses":
            return check_pose_frames(int(argv[2]) if len(argv) > 2 else None,
                                     [int(one) for one in argv[3:]] or None)
        if len(argv) >= 2 and argv[1] == "--default":
            return check_default(int(argv[2]) if len(argv) > 2 else 2)
        if len(argv) >= 2 and argv[1] == "--keys":
            slot = int(argv[3]) if len(argv) > 3 else 2
            return check_keys(argv[2] if len(argv) > 2 else None, slot)
        if len(argv) >= 2 and argv[1] == "--writes":
            return check_writes(*row_and_slot(argv[2:]))
        if len(argv) >= 2 and argv[1] == "--colour":
            return check_colour(*row_and_slot(argv[2:4]),
                                starts=tuple(argv[4:]))
        if len(argv) >= 2 and argv[1] == "--patched":
            return check_patched(*row_and_slot(argv[2:4]),
                                 starts=tuple(argv[4:]))
        if len(argv) == 2 and argv[1] == "--hair":
            return check_hair()
        if len(argv) >= 2 and argv[1] == "--where":
            return check_where(row=argv[2] if len(argv) > 2 else "HAIR")
        if len(argv) >= 2 and argv[1] == "--assembly":
            return check_assembly(rows=tuple(argv[2:]) or None)
        if len(argv) in (2, 3) and argv[1] == "--glyphs":
            return check_glyphs((int(argv[2]),) if len(argv) > 2 else (2, 1))
        if len(argv) in (2, 3) and argv[1] == "--closeups":
            return close_up_rows((int(argv[2]),) if len(argv) > 2
                                 else (2, 1))
        if len(argv) in (2, 3) and argv[1] == "--help-box":
            return check_help_box((int(argv[2]),) if len(argv) > 2 else (2, 1))
        if len(argv) in (2, 3) and argv[1] == "--pages":
            return check_pages((int(argv[2]),) if len(argv) > 2 else (2, 1))
        if len(argv) in (2, 3) and argv[1] == "--repaint":
            return check_repaint((int(argv[2]),) if len(argv) > 2 else (2, 1))
        if len(argv) >= 2 and argv[1] == "--scenery":
            rest = [a for a in argv[2:] if a != "--write"]
            return check_scenery((int(rest[0]),) if rest else (2, 1),
                                 write="--write" in argv)
        if len(argv) in (2, 3) and argv[1] == "--kit":
            return check_kit((int(argv[2]),) if len(argv) > 2 else (2, 1))
        if len(argv) == 2 and argv[1] == "--palettes":
            return check_palettes()
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
    except Exception as exc:  # noqa: BLE001
        import screen

        if not isinstance(exc, screen.BadScreen):
            raise
        print("oracle FAILED: %s" % exc, file=sys.stderr)
        return 1
    print(__doc__.strip())
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))

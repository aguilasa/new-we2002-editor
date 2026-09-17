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
    python tools/looks/oracle.py --assembly [HAIR ...]  # every value of a field
    python tools/looks/oracle.py --where [HAIR]  # where a field goes when the file does not move
    python tools/looks/oracle.py --hair          # who writes the hair window, and from where
    python tools/looks/oracle.py --patched [HAIR [SLOT [TUPLE ...]]]  # which sections the game has edited, value by value
    python tools/looks/oracle.py --colour SKIN [SLOT [TUPLE ...]]  # which primitives of each head a colour row moves
    python tools/looks/oracle.py --writes [HAIR [SLOT]]  # every quad the game writes, value by value
    python tools/looks/oracle.py --screen [--write]  # LOOKS SET measured: every text, help, cursor and box; --write makes screen.json
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

OBJECT_SIZE = 16
"""The bytes of a text object that layout.SCREEN_PRINT documents."""

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

    The frame is closed by repetition, not by the clock: the first *repeat*
    stops coming round again in the same order.  The emulator is left paused.
    """
    import time

    import who_writes

    client = game.client
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="execute",
                address=who_writes.hx(address))
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
                    "lines": (screen.decode(text) if kind in ASCII_KINDS
                              else None)})
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
        """{title, shirt, plate: (text, [x, y])}: the kind-33 object, and the
        two left of the rows box, upper then lower."""
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
        def text(obj):
            return (" ".join(line.strip() for line in obj["lines"]).strip(),
                    [obj["x"], obj["y"]])

        return {"title": text(titles[0]), "shirt": text(left[0]),
                "plate": text(left[1])}


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
        outside = reading.outside()
        cursor_row, cursor_box = _cursor_row(frames, regions, geometry, origin)
        record = screen_record(game)
        plate = outside["plate"][0]
        anchors = {name: xy for name, (_, xy) in outside.items()}
        anchors["labels"] = [labels["x"], labels["y"]]
        table["initial"][str(slot)] = {
            "rows": reading.rows(orders), "title": outside["title"][0],
            "shirt": outside["shirt"][0], "plate": plate,
            "help": screen_help(game), "cursor": looks.SCREEN[cursor_row],
            "record": record, "anchors": anchors}
        say = print if verbose else (lambda *a: None)
        say("  slot %d on load: %s, plate %s, cursor on %s, help %r; %d "
            "glyph string(s) checked against %d object(s)"
            % (slot, SLOTS[slot], plate, looks.SCREEN[cursor_row],
               table["initial"][str(slot)]["help"], len(glyphs),
               len(objects)))
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
                      verbose))

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


def _walk_row(game, slot, name, table, geometry, orders, verbose):
    """Every value one row walks, both ends, and what moves beside it."""
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

    def read():
        reading = ScreenReading(geometry, screen_objects(game))
        rows = reading.rows(orders)
        value = screen_record(game)[field.name] if field else None
        return rows, value

    rows, value = read()
    initial = dict(rows)
    moved, dropped = set(), 0

    def go(direction, texts, values):
        nonlocal dropped
        for _ in range(SCREEN_WALK_LIMIT):
            tap(game, direction)
            rows, value = read()
            if rows[name] == texts[-1]:
                tap(game, direction)
                rows, value = read()
                if rows[name] == texts[-1]:
                    return "locks"
                dropped += 1
            moved.update(other for other in looks.SCREEN
                         if other != name and rows[other] != initial[other])
            if rows[name] in texts:
                return "wraps"
            texts.append(rows[name])
            values.append(value)
        raise OracleError("%s walked %s %d times without an end"
                          % (name, direction, SCREEN_WALK_LIMIT))

    left_texts, left_values = [rows[name]], [value]
    left = go("Left", left_texts, left_values)
    if left == "wraps":
        raise OracleError("%s wraps going Left; a wrapping row is not "
                          "modelled, and the walk says so rather than guess"
                          % name)
    texts, values = [left_texts[-1]], [left_values[-1]]
    right = go("Right", texts, values)
    if right == "wraps":
        raise OracleError("%s wraps going Right after locking going Left"
                          % name)
    if list(reversed(left_texts)) != texts[:len(left_texts)]:
        raise OracleError("%s: Left walked %r and Right came back %r"
                          % (name, left_texts, texts))
    glyphs = _control(game, ScreenReading(geometry, screen_objects(game)),
                      orders)
    out = {"texts": texts, "left": left, "right": right,
           "stored": field.name if field else None,
           "moves_beside": sorted(moved, key=looks.SCREEN.index)}
    if field:
        if values != list(range(values[0], values[0] + len(values))):
            raise OracleError("%s: the stored value did not step by one with "
                              "the text: %r" % (name, values))
        out["values"] = values
    if verbose:
        shown = texts if len(texts) <= 6 else texts[:3] + ["..."] + texts[-2:]
        print("  %-9s %3d value(s), Left %s, Right %s%s%s; end checked "
              "against %d drawn string(s)%s"
              % (name, len(texts), left, right,
                 ", stored %d..%d" % (values[0], values[-1]) if field else "",
                 ", moves %s" % out["moves_beside"] if moved else "",
                 glyphs, ", %d press(es) dropped" % dropped if dropped else ""))
        print("            %s" % " | ".join(shown))
    return out


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
    table = screen.load()
    differences = _differences(table, measured)
    for path, want, got in differences:
        print("  FAIL  %s: screen.json has %r, the game shows %r"
              % (path, want, got))
    print("oracle --screen: %d difference(s) from screen.json"
          % len(differences))
    return 1 if differences else 0


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


def _checks(c) -> None:
    ok, attempt = c.ok, c.attempt

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

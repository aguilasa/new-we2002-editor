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

ROW_VALUE = (0.600, 0.205, 0.960, 0.260)
"""The value cell of the row the cursor sits on when a state loads."""

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

    def press(self, button, box=None, expect_change=True):
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
            moved = before.difference(after, pixels(before, box))
            if moved <= MOVED:
                raise NotArrived(
                    "%s moved the screen by %.6f, which is no more than the "
                    "%.6f that counts as unchanged -- the press did not "
                    "register, or the region is the wrong one"
                    % (button, moved, MOVED)
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
    77, this repository's code across all five projects.
    """
    cue = drive_image()
    check_states(verbose=False)

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
        report = game.verify_load()
        ok("both model files are loaded where layout.py says",
           set(report) == set(layout.BASE))

        moved = game.press("Right", box=ROW_VALUE)
        ok("one press changes the field under the cursor",
           moved.difference(first, pixels(first, ROW_VALUE)) > MOVED)

    print("oracle --check-live: %d failure(s)" % len(failures))
    return 1 if failures else 0


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

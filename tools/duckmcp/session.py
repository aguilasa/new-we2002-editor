"""`Session`: a paused emulator and the calls every caller makes against it.

    with Session("/copy/of/disc.cue") as s:      # refuse pads, launch, pause
        s.load_state(1)
        s.press("Down")                          # 3 frames held, 17 after
        s.capture("/tmp/shot.png")               # -> the path, not an image
    # killed on the way out: this session launched it

    s = Session.attach()                         # a fork somebody else runs
    s.press("cross", pause_first=True)           # left running afterwards

Three ways in, and only one of them owns the emulator:

* `Session(image)` used as a context manager refuses a plugged game
  controller (`fork.refuse_joysticks`), boots `image` with `fork.launch`,
  pauses, and kills the fork on exit. If `launch` raises, the fork is killed
  only when a DuckStation pid appeared that was not there before -- a
  skipped launch never stops an emulator another session opened
  (CORR-DMCP-011). If the first `pause` fails, the fork it just launched is
  killed before the error leaves `__enter__`, which is the one place
  `__exit__` cannot reach.
* `Session(client)` -- or `Session(client=...)` -- wraps any object with
  `initialize`, `call`, `session` and `server`: a `Client`, or a fake that
  records calls. It handshakes and pauses on enter and never kills.
* `Session.attach(client=None)` talks to a fork that is already up, does
  not pause on enter and never kills: the user has the game in front of
  them and wants one action sent to it.

Everything a caller reads comes back as a **path or bytes, never as an
image**: decoding a PNG is the caller's business, and importing this module
must not import an imaging library (rule (a) of PLAN-DUCKMCP-PY.md section
3.3). Every path is made absolute before it is sent, because the server
resolves a relative one against the emulator's working directory, not the
caller's.

`call(name, **arguments)` is the documented escape hatch for a tool with no
method here; the tool names and argument names of every method are the ones
the fork's own input schemas declare (read out of its binary on 2026-10-22).
"""

# lineage: McpSession of tools/pes2/mcp_drive.py, Live of tools/pes2/pad.py,
# Oracle and vram_region of tools/looks/oracle.py, dump_slot of
# tools/kits/oracle.py, as of commit 791ca241.

import collections
import os
import shutil
import tempfile
import time

from . import buttons, env, fork
from .client import Client
from .errors import Fail, Skip, ToolError

PRESS_FRAMES = 3
"""Frames a button is held by default: `duration_frames` of `press_button`.

Three down and seventeen after moved exactly one menu row, every time, over
the walks measured on 2026-09-03. A caller that measured another pair (a
longer confirm, a longer settle) passes `frames=` and `after=`: which pair
each caller keeps is decided when it migrates (section 4.3 of the plan).
"""

AFTER_FRAMES = 17
"""Frames stepped after the hold by default, for the game to act on it."""

READ_LIMIT = 2 * 1024 * 1024
"""The most `read_memory` returns in one call (its schema's `size` maximum)."""

VRAM_SIZE = (1024, 512)
"""The PS1 frame buffer, in 16-bit pixels."""

CLIENT_ATTRIBUTES = ("initialize", "call", "session", "server")
"""What an object needs for `Session` to wrap it as its client."""

Game = collections.namedtuple("Game", "serial title")
Game.__doc__ = """What `get_status` says is loaded; None for an absent field.

`serial` is `game_serial` and `title` is `game_title`, the two fields the
fork's `get_status` schema promises at `detail='basic'`.
"""


def is_client(obj):
    """Does `obj` have what `Session` calls on its client?"""
    return all(hasattr(obj, name) for name in CLIENT_ATTRIBUTES)


def require_client(obj):
    """`obj`, or `TypeError` naming the attributes it lacks."""
    missing = [name for name in CLIENT_ATTRIBUTES if not hasattr(obj, name)]
    if missing:
        raise TypeError("%r cannot be a session's client: it has no %s"
                        % (obj, ", ".join(missing)))
    return obj


def _remove(path):
    """Delete a stale output, so that finding the file proves a fresh write."""
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


class Session:
    """A paused emulator, an MCP session against it, and who owns it.

    `image` is the `.cue` (or other image) to boot; a client-shaped object
    in its place is taken as `client`. `match`, `display`, `timeout` and
    `home` go to `fork.launch` unchanged; `display=None` is `env.display()`.
    """

    def __init__(self, image=None, *, client=None, match=None, display=None,
                 timeout=120, verbose=True, home=None):
        if client is None and image is not None and is_client(image):
            image, client = None, image
        self.image = image
        self.client = None if client is None else require_client(client)
        self.match = match
        self.display = display
        self.timeout = timeout
        self.verbose = verbose
        self.home = home
        self.pid = None
        self.window = None
        self.owned = False          # True only after this session launched
        self.pause_on_enter = True
        self.presses = 0
        self.steps = 0

    # -- lifecycle --

    @classmethod
    def attach(cls, client=None, verbose=True):
        """A fork already running, left running: no pause, no kill."""
        s = cls(client=client if client is not None else Client(),
                verbose=verbose)
        s.client.initialize()
        s.pause_on_enter = False
        return s

    def __enter__(self):
        if self.client is not None:
            self.client.initialize()
            if self.pause_on_enter:
                self.pause()
            return self
        if not self.image:
            raise Fail("Session needs an image to launch, a client to wrap, "
                       "or Session.attach() for a fork already up")
        fork.refuse_joysticks()
        running = set(fork.running_pids())
        try:
            self.pid, self.window, self.client = fork.launch(
                self.image, match=self.match, display=self.display,
                timeout=self.timeout, home=self.home, verbose=self.verbose)
        except BaseException:
            # A Fail can come after the Popen (no window in time): a new pid
            # is ours to stop; none new means nothing was launched.
            if set(fork.running_pids()) - running:
                fork.kill(verbose=False)
            raise
        self.owned = True
        try:
            self.pause()
        except BaseException:
            # __exit__ does not run for an exception raised in __enter__.
            fork.kill(verbose=False)
            self.owned = False
            raise
        return self

    def __exit__(self, *exc):
        if self.owned:
            self.owned = False
            fork.kill(verbose=False)
        return False

    def say(self, message):
        if self.verbose:
            print("  %s" % message, flush=True)

    def call(self, name, **arguments):
        """Any tool by name: the escape hatch for one with no method here."""
        return self.client.call(name, **arguments)

    # -- the emulator clock --

    def pause(self):
        self.call("pause")

    def resume(self):
        self.call("continue")

    def frame(self):
        """`get_status`'s `frame_number`; one `frame_step` moves it by one."""
        return self.call("get_status")["frame_number"]

    def step(self, n=1):
        """Advance exactly `n` frames and stay paused.

        About 57 ms a frame over the wire (pitfall 34), so it is for
        precision -- a button and its consequence -- and `run` is for
        distance.
        """
        if n < 0:
            raise ValueError("cannot step %d frames" % n)
        for _ in range(n):
            self.call("frame_step")
        self.steps += n

    def run(self, seconds, fast=False):
        """Run for `seconds` of wall clock, then pause again.

        Fast forward is a hold in DuckStation, not a toggle, so it is set
        before and cleared after, even when the run is interrupted.
        """
        if fast:
            self.call("set_speed", fast_forward=True)
        try:
            self.resume()
            time.sleep(seconds)
            self.pause()
        finally:
            if fast:
                self.call("set_speed", fast_forward=False)

    def game(self):
        """`Game(serial, title)` of what is loaded, from `get_status`.

        An empty or missing field is None: with no disc booted the server
        still answers `get_status`, and a caller comparing serials must not
        mistake `""` for one.
        """
        status = self.call("get_status")
        if not isinstance(status, dict):
            raise ToolError("get_status answered %r, not an object"
                            % (status,))
        return Game(status.get("game_serial") or None,
                    status.get("game_title") or None)

    # -- input --

    def press(self, button, frames=PRESS_FRAMES, after=AFTER_FRAMES,
              pause_first=False, slot=None):
        """Hold `button` for `frames` frames, then step `frames + after`.

        `duration_frames` is **always** sent: without it the server presses
        and never releases, and the button stays held (pitfall 36). The
        release happens on the emulator's own clock, so neither the hold
        nor the gap depends on how fast the caller talks to it.

        `pause_first` pauses before the press, for a session attached to a
        running game; a launched session is already paused. `slot` is the
        controller port, sent only when given (the server's default is 0).
        """
        name = buttons.canonical(button)
        if frames < 1:
            raise ValueError("a press holds at least one frame, not %d"
                             % frames)
        if after < 0:
            raise ValueError("cannot step %d frames after a press" % after)
        if pause_first:
            self.pause()
        extra = {} if slot is None else {"slot": slot}
        self.call("press_button", button=name, duration_frames=frames,
                  **extra)
        self.step(frames + after)
        self.presses += 1

    # -- output: paths and bytes, never images --

    def capture(self, path):
        """The emulator's own frame buffer as a PNG at `path`; returns it.

        Not a window grab: a modal on top of the game window cannot get into
        it. The file is removed first, so finding it proves this call wrote
        it.
        """
        path = os.path.abspath(path)
        _remove(path)
        self.call("take_screenshot", path=path)
        if not os.path.isfile(path):
            raise ToolError("take_screenshot reported a screenshot at %s and "
                            "there is no file there" % path)
        return path

    def read_ram(self, address, size, path=None):
        """`size` bytes of the live machine from `address`, as bytes.

        Through a file, which is what the server does with large reads; with
        `path=None` a temporary one, removed afterwards. A short file is an
        error, not a short answer.
        """
        if not 0 < size <= READ_LIMIT:
            raise ValueError("read_memory reads 1..%d bytes, not %d"
                             % (READ_LIMIT, size))
        scratch = None
        if path is None:
            scratch = tempfile.mkdtemp(prefix="duckmcp-ram-")
            path = os.path.join(scratch, "ram.bin")
        path = os.path.abspath(path)
        try:
            _remove(path)
            self.call("read_memory", address=address, size=size, path=path)
            try:
                with open(path, "rb") as handle:
                    data = handle.read()
            except FileNotFoundError:
                raise ToolError("read_memory wrote nothing at %s" % path) \
                    from None
        finally:
            if scratch:
                shutil.rmtree(scratch, ignore_errors=True)
        if len(data) != size:
            raise ToolError("asked for %d bytes at %#x and got %d"
                            % (size, address, len(data)))
        return data

    def read_vram_region(self, x, y, width, height, path=None, fmt="png"):
        """A rectangle of VRAM as a file; returns its path.

        The server picks the file (a temporary one) and answers its
        `output_path`; with `path` given the file is moved there. `fmt` is
        `png` (RGBA8) or `raw` (u16 1555, as the hardware stores it).
        """
        _check_rect(x, y, width, height)
        reply = self.call("read_vram_region", x=x, y=y, width=width,
                          height=height, format=fmt)
        out = reply.get("output_path") if isinstance(reply, dict) else None
        if not out or not os.path.isfile(out):
            raise ToolError("read_vram_region reported %r and there is no "
                            "file there" % (out,))
        if path is None:
            return out
        path = os.path.abspath(path)
        shutil.move(out, path)
        return path

    def dump_vram(self, path, fmt="png"):
        """All of VRAM at `path` (`png` or `bin`); returns the path."""
        path = os.path.abspath(path)
        _remove(path)
        self.call("dump_vram", path=path, format=fmt)
        if not os.path.isfile(path):
            raise ToolError("dump_vram wrote nothing at %s" % path)
        return path

    def write_vram_region(self, x, y, width, height, data=None,
                          input_path=None):
        """Raw u16 pixels into a VRAM rectangle, from bytes or a file.

        Exactly one of `data` and `input_path`; either way the size must be
        `width * height * 2`, checked here rather than by the server.
        Returns the server's answer.
        """
        _check_rect(x, y, width, height)
        if (data is None) == (input_path is None):
            raise ValueError("give exactly one of data and input_path")
        want = width * height * 2
        scratch = None
        try:
            if data is not None:
                if len(data) != want:
                    raise ValueError("%dx%d needs %d bytes, got %d"
                                     % (width, height, want, len(data)))
                scratch = tempfile.mkdtemp(prefix="duckmcp-vram-")
                input_path = os.path.join(scratch, "region.bin")
                with open(input_path, "wb") as handle:
                    handle.write(data)
            input_path = os.path.abspath(input_path)
            got = os.path.getsize(input_path)
            if got != want:
                raise ValueError("%s has %d bytes and %dx%d needs %d"
                                 % (input_path, got, width, height, want))
            return self.call("write_vram_region", x=x, y=y, width=width,
                             height=height, input_path=input_path,
                             format="raw")
        finally:
            if scratch:
                shutil.rmtree(scratch, ignore_errors=True)

    def gpu_state(self, aspect=None):
        """`get_gpu_state`; `aspect` as the server names them, None its
        default (`registers`)."""
        if aspect is None:
            return self.call("get_gpu_state")
        return self.call("get_gpu_state", aspect=aspect)

    def gte_registers(self):
        """`get_gte_registers`: the 32 data and 32 control registers."""
        return self.call("get_gte_registers")

    # -- save states --

    def load_state(self, slot, settle=0, path=None):
        """Restore save-state `slot`, then step `settle` frames.

        With `path`, a missing state file is refused before the call.
        """
        if path is not None and not os.path.isfile(path):
            raise Fail("no save state at %s" % path)
        self.call("load_state", slot=slot)
        self.step(settle)

    def save_state(self, slot, wait_for=None, serial=None, timeout=10.0,
                   poll=0.5):
        """Save to `slot` and wait until the state file really moved.

        The file is `wait_for`, or `env.state_path(serial, slot)` with the
        serial given or read from `game()`. Returns its path; `Fail` when
        its modification time has not passed the one before the call within
        `timeout` seconds -- a save that was asked for is not a save that
        happened.
        """
        if wait_for is None:
            serial = serial or self.game().serial
            if not serial:
                raise Fail("no serial to find the state file of slot %d: "
                           "no game loaded, and none given" % slot)
            wait_for = env.state_path(serial, slot)
        path = os.path.abspath(wait_for)
        before = os.path.getmtime(path) if os.path.exists(path) else 0
        self.call("save_state", slot=slot)
        deadline = time.time() + timeout
        while True:
            if os.path.exists(path) and os.path.getmtime(path) > before:
                return path
            if time.time() >= deadline:
                raise Fail("no save state appeared at %s within %ss"
                           % (path, timeout))
            time.sleep(poll)


def _check_rect(x, y, width, height):
    """Refuse a rectangle that is not inside the 1024x512 VRAM."""
    if (width < 1 or height < 1 or x < 0 or y < 0
            or x + width > VRAM_SIZE[0] or y + height > VRAM_SIZE[1]):
        raise ValueError("%dx%d at (%d, %d) is not inside the %dx%d VRAM"
                         % ((width, height, x, y) + VRAM_SIZE))


# --- self-check --------------------------------------------------------

class _FakeClient:
    """Records every call and answers like the fork, writing the files the
    real server would write."""

    def __init__(self, serial="TEST-00001", title="A Test Disc",
                 short_read=False):
        self.session = "fake-session"
        self.server = None
        self.calls = []
        self.handshakes = 0
        self.frame = 100
        self.serial = serial
        self.title = title
        self.short_read = short_read
        self.state_files = {}
        self.scratch = None          # made on the first read_vram_region

    def initialize(self):
        self.handshakes += 1
        self.server = {"name": "fake", "version": "0"}
        return self.server

    def _touch(self, path, data=b"\0"):
        with open(path, "wb") as handle:
            handle.write(data)

    def call(self, name, **arguments):
        self.calls.append((name, dict(arguments)))
        if name == "frame_step":
            self.frame += 1
            return {"status": "stepped", "frame_number": self.frame}
        if name == "get_status":
            return {"state": "paused", "game_serial": self.serial,
                    "game_title": self.title, "frame_number": self.frame}
        if name in ("take_screenshot", "dump_vram"):
            self._touch(arguments["path"])
            return {"path": arguments["path"]}
        if name == "read_memory":
            size = arguments["size"] - (1 if self.short_read else 0)
            self._touch(arguments["path"], bytes(range(256)) * (size // 256)
                        + bytes(size % 256))
            return {"output_path": arguments["path"]}
        if name == "read_vram_region":
            if self.scratch is None:
                self.scratch = tempfile.mkdtemp(prefix="duckmcp-fake-")
            out = os.path.join(self.scratch, "region.%s" % arguments["format"])
            self._touch(out)
            return {"output_path": out}
        if name == "save_state":
            path = self.state_files.get(arguments["slot"])
            if path:
                self._touch(path)
            return {"status": "saved", "slot": arguments["slot"]}
        return {"status": "ok"}

    def names(self):
        return [name for name, _ in self.calls]


def _raises(fn, cls):
    try:
        fn()
    except cls:
        return True
    except Exception:  # noqa: BLE001
        return False
    return False


def _check_press(check):
    fake = _FakeClient()
    s = Session(client=fake)
    s.press("down")
    s.press("CROSS", frames=5, after=0)
    s.press("Start", frames=1, after=40, pause_first=True)
    presses = [kw for name, kw in fake.calls if name == "press_button"]
    check("press always sends duration_frames (pitfall 36)",
          len(presses) == 3 and all("duration_frames" in kw for kw in presses)
          and [kw.get("duration_frames") for kw in presses] == [3, 5, 1],
          presses)
    check("press sends the canonical button name",
          [kw.get("button") for kw in presses] == ["Down", "Cross", "Start"],
          presses)
    check("press steps frames + after (3+17, 5+0, 1+40)",
          s.steps == 20 + 5 + 41 and fake.names().count("frame_step") == 66,
          "steps=%d" % s.steps)
    check("press pauses only with pause_first",
          fake.names() == ["press_button"] + ["frame_step"] * 20
          + ["press_button"] + ["frame_step"] * 5
          + ["pause", "press_button"] + ["frame_step"] * 41,
          fake.names()[:3])
    check("press refuses an unknown button before any call",
          _raises(lambda: s.press("Triangel"), buttons.UnknownButton)
          and fake.names().count("press_button") == 3)
    check("press refuses a hold of zero frames",
          _raises(lambda: s.press("Up", frames=0), ValueError))


def _check_client_shape(check):
    class Minimal:
        session = None
        server = None

        def initialize(self):
            self.server = {}

        def call(self, name, **arguments):
            return {"frame_number": 7}

    minimal = Minimal()
    s = Session(minimal)
    check("Session(fake) takes any object with initialize, call, session, "
          "server", s.client is minimal and s.image is None
          and s.frame() == 7)

    class NoServer:
        session = None

        def initialize(self):
            pass

        def call(self, name, **arguments):
            pass

    check("Session(client=...) refuses an object without server",
          _raises(lambda: Session(client=NoServer()), TypeError))
    check("Session('a.cue') keeps a string as the image",
          Session("a.cue").image == "a.cue")


def _check_outputs(check):
    fake = _FakeClient()
    s = Session(client=fake)
    out = tempfile.mkdtemp(prefix="duckmcp-session-")
    try:
        shot = os.path.join(out, "shot.png")
        got = s.capture(shot)
        check("capture returns the path, as a str",
              isinstance(got, str) and got == os.path.abspath(shot)
              and os.path.isfile(got), got)

        class Mute(_FakeClient):
            def call(self, name, **arguments):
                self.calls.append((name, arguments))
                return {}

        check("capture refuses a screenshot that wrote no file",
              _raises(lambda: Session(client=Mute()).capture(shot),
                      ToolError))
        check("read_ram returns exactly size bytes",
              s.read_ram(2048, 300) == (bytes(range(256)) + bytes(44)))
        check("read_ram refuses a short file",
              _raises(lambda: Session(client=_FakeClient(short_read=True))
                      .read_ram(2048, 300), ToolError))
        check("read_ram refuses more than read_memory's 2 MiB",
              _raises(lambda: s.read_ram(0, READ_LIMIT + 1), ValueError))
        region = s.read_vram_region(0, 0, 64, 32, os.path.join(out, "r.png"))
        check("read_vram_region moves the server's file to the path given",
              region == os.path.join(out, "r.png") and os.path.isfile(region))
        check("read_vram_region refuses a rectangle outside VRAM",
              _raises(lambda: s.read_vram_region(1000, 0, 64, 1), ValueError))
        check("dump_vram returns the path",
              s.dump_vram(os.path.join(out, "v.png"))
              == os.path.join(out, "v.png"))
        s.write_vram_region(0, 0, 2, 2, data=bytes(8))
        sent = [kw for name, kw in fake.calls if name == "write_vram_region"]
        check("write_vram_region sends raw from a file of w*h*2 bytes",
              len(sent) == 1 and sent[0]["format"] == "raw"
              and os.path.isabs(sent[0]["input_path"]), sent)
        check("write_vram_region refuses data of the wrong size",
              _raises(lambda: s.write_vram_region(0, 0, 2, 2, data=bytes(7)),
                      ValueError))
        check("game() reads game_serial and game_title",
              s.game() == ("TEST-00001", "A Test Disc"), s.game())
        check("game() answers None for an empty serial",
              Session(client=_FakeClient(serial="")).game().serial is None)
        state = os.path.join(out, "slot.sav")
        fake.state_files[2] = state
        check("save_state waits for the state file and returns it",
              s.save_state(2, wait_for=state, poll=0.01) == state)
        check("save_state fails when the file never moves",
              _raises(lambda: s.save_state(3, wait_for=os.path.join(
                  out, "never.sav"), timeout=0.05, poll=0.01), Fail))
        s.load_state(1, settle=2)
        check("load_state loads, then steps settle frames",
              fake.names()[-3:] == ["load_state", "frame_step", "frame_step"],
              fake.names()[-3:])
    finally:
        shutil.rmtree(out, ignore_errors=True)
        if fake.scratch:
            shutil.rmtree(fake.scratch, ignore_errors=True)


def _check_ownership(check):
    """`fork.launch`, `kill`, `running_pids` and `refuse_joysticks` stubbed."""
    saved = (fork.launch, fork.kill, fork.running_pids,
             fork.refuse_joysticks)
    log = []

    def stub(raised=None, pids=((), ()), client=None):
        answers = [list(p) for p in pids]
        fork.refuse_joysticks = lambda *a, **k: log.append("refuse")

        def launch(image, **kwargs):
            log.append("launch")
            if raised:
                raise raised
            return 4242, "window", client or _FakeClient()

        fork.launch = launch
        fork.kill = lambda verbose=True: log.append("kill") or 0
        fork.running_pids = lambda: answers.pop(0) if answers else []

    try:
        def kills():
            return log.count("kill")

        del log[:]
        stub()
        with Session(client=_FakeClient()):
            pass
        with Session.attach(_FakeClient()):
            pass
        check("exit does not kill a wrapped or attached client",
              kills() == 0 and "launch" not in log, log)

        del log[:]
        stub()
        with Session("/x/a.cue") as s:
            launched = s.owned and s.pid == 4242
        check("exit kills the fork this session launched, once",
              launched and kills() == 1 and log[:2] == ["refuse", "launch"],
              log)

        del log[:]
        stub(raised=Fail("no window"), pids=([], [5150]))
        _raises(lambda: Session("/x/a.cue").__enter__(), Fail)
        check("a launch that fails after its Popen stops the new pid",
              kills() == 1, log)

        del log[:]
        stub(raised=Skip("no X server"), pids=([4242], [4242]))
        _raises(lambda: Session("/x/a.cue").__enter__(), Skip)
        check("a skipped launch leaves another session's emulator alive",
              kills() == 0, log)

        class PauseFails(_FakeClient):
            def call(self, name, **arguments):
                if name == "pause":
                    raise ToolError("pause: session lost")
                return super().call(name, **arguments)

        del log[:]
        stub(client=PauseFails())
        _raises(lambda: Session("/x/a.cue").__enter__(), ToolError)
        check("a pause that fails in __enter__ kills what it launched",
              kills() == 1, log)

        del log[:]
        fake = _FakeClient()
        s = Session.attach(fake)
        s.__enter__()
        check("attach handshakes and does not pause",
              fake.handshakes >= 1 and "pause" not in fake.names(),
              fake.names())
    finally:
        (fork.launch, fork.kill, fork.running_pids,
         fork.refuse_joysticks) = saved


def self_check() -> list:
    """`press`, the client shape, the outputs and ownership, against fakes.

    Returns one `(name, passed, detail)` per assertion.
    """
    results = []

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    for part in (_check_press, _check_client_shape, _check_outputs,
                 _check_ownership):
        try:
            part(check)
        except Exception as exc:  # noqa: BLE001
            check("%s ran" % part.__name__, False,
                  "%s: %s" % (type(exc).__name__, exc))
    return results

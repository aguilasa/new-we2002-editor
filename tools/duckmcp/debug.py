"""The CPU debugger of the fork: one wait, breakpoints that always clear.

    from duckmcp import debug
    with Session(image) as s:
        hit = debug.who_writes(s, address, seconds=90)
        hit["pc"], hit["store"], hit["caller"]          # who wrote it

        with debug.breakpoints(s, [a, b], "execute"):   # cleared and paused
            s.resume()                                  # on the way out,
            debug.wait_for_pause(s, 10)                 # whatever happens

Every function takes a `Session` or anything client-shaped (`initialize`,
`call`): it talks to `session.client` when there is one, else to the object
itself, so a fake that records calls drives all of it.

**One wait, and it watches the process.** Waiting for a breakpoint is free
execution, and free execution is when the fork dies on its own, with no log
(pitfall 35 of PLAN-DUCKMCP-PY section 1.3). `wait_for_pause` asks the
client's liveness probe on every round, and a process gone mid-wait is a
`Fail` that says so -- not a timeout, and not the "is not running" sentence
that describes never having launched it. The two call for opposite actions.

**Silence is a failure.** A breakpoint that never fires and an emulator that
stopped stepping look the same in a quiet return, so `wait_for_pause` raises
on timeout unless the caller says, with `required=False`, that not firing is
an answer it wants (a control run).

**The poll interval is a parameter.** One copy slept a second between polls,
the other did not sleep at all; which one a caller keeps is measured when it
migrates (section 4.3 of the plan). `interval=0` is allowed.

**Breakpoints are a context manager.** `breakpoints` clears what was armed
and pauses in its `finally`, each attempted on its own, so an exception in
the middle -- a `Fail`, a `KeyboardInterrupt` -- never leaves a breakpoint
armed in an emulator the next run inherits, nor the machine running.
"""

# lineage: tools/pes2/who_writes.py as of commit 73e21f1d (parse_address, hx,
# split_store, register_value, is_paused, wait_for_hit and the cases of its
# self_check), and _wait_for_hit, catch_write, _stops, _watch_reads and the
# vram_watch calls of check_help_box in tools/looks/oracle.py at the same
# commit. catch_write left the machine running on the way out and who_writes
# did not pause either; here every armed wait ends paused.

import contextlib
import time

from . import buttons
from . import client as client_module
from .errors import Fail, ToolError

POLL_SECONDS = 1.0
"""The default sleep between two polls of `wait_for_pause`, in seconds."""

NUDGE_FRAMES = 6
"""Frames a nudge is held: long enough for a game to read it as a tap."""

NUDGE_EVERY = 6.0
"""Seconds between two nudges when a wait is asked to nudge."""

PRESS_FRAMES = 8
"""Frames `who_writes` holds the button it presses while waiting."""

WATCH_SECONDS = 90
"""How long `who_writes` waits for the write, in seconds."""

STOPS_SECONDS = 120
"""How long `stops` waits for the stops to come round, in seconds."""

READ_SECONDS = 8
"""How long `watch_reads` waits for each read, in seconds."""

INSTRUCTION_SIZE = 4
"""Bytes of one R3000A instruction."""

WINDOW_BEFORE = 8
WINDOW_AFTER = 4
"""Instructions disassembled before and after the pc of a hit.

A window, not one instruction: on this build the CPU stops on the
instruction *after* the store.
"""

CALLER_BEFORE = 12
"""Instructions disassembled before `ra`, the caller of the routine."""

WORD_MASK = (1 << 32) - 1
"""A 32-bit register."""

PLAN = client_module.PLAN
"""Where the pitfalls the messages cite are written down."""


def _client(session):
    """The object the calls go to: `session.client`, or `session` itself."""
    inner = getattr(session, "client", None)
    if inner is not None and hasattr(inner, "call"):
        return inner
    return session


def _quietly(client, name, **arguments):
    """One cleanup call; a failure here must not hide the one in flight."""
    try:
        client.call(name, **arguments)
    except Exception:                                        # noqa: BLE001
        pass


# --- address arithmetic ------------------------------------------------

def parse_address(text):
    """Accept `0x8001234A`, `8001234A`, or a decimal string; an int passes.

    Bare digits with no letter among them are decimal: `80012340` is not
    the address `0x80012340`.

    The MCP tools take "integer or hex string" and the fork is inconsistent
    about which it echoes back, so everything is an int here and formatted
    on the way out. A leading sign is kept: `sb zero, -0x4(v0)` is a real
    instruction, and `int()` will not take "-0x4" in any base.
    """
    if isinstance(text, int):
        return text
    t = str(text).strip()
    if not t:
        raise Fail("empty address")
    sign = 1
    if t[0] in "+-":
        sign = -1 if t[0] == "-" else 1
        t = t[1:].strip()
    if not t:
        raise Fail("%r is not an address" % (text,))
    try:
        if t.lower().startswith("0x"):
            return sign * int(t, 16)
        if any(c in "abcdefABCDEF" for c in t):
            return sign * int(t, 16)
        return sign * int(t, 10)
    except ValueError:
        raise Fail("%r is not an address" % (text,)) from None


def hx(value):
    """`0x%08X` of the low 32 bits: the spelling the fork's tools take."""
    return "0x%08X" % (value & WORD_MASK)


def split_store(instruction):
    """`(mnemonic, source, offset, base)` of a load/store, or None.

    `sb zero, 0x21a(v0)` -> `('sb', 'zero', 0x21a, 'v0')`. Anything not
    shaped like `op reg, off(base)` is None, because the pc after a hit is
    not always on the store itself.
    """
    text = " ".join(str(instruction).split())
    if "(" not in text or ")" not in text or "," not in text:
        return None
    head, _, rest = text.partition(" ")
    src, _, mem = rest.partition(",")
    mem = mem.strip()
    off_text, _, base = mem.partition("(")
    base = base.rstrip(")").strip()
    if not base:
        return None
    try:
        offset = parse_address(off_text.strip() or "0")
    except Fail:
        return None
    return (head.strip(), src.strip(), offset, base)


def register_value(registers, name):
    """A register out of `read_registers` as an int, whatever the shape."""
    if not isinstance(registers, dict):
        return None
    for key in (name, name.lower(), name.upper(), "$%s" % name):
        if key in registers:
            return parse_address(registers[key])
    for group in registers.values():
        if isinstance(group, dict):
            found = register_value(group, name)
            if found is not None:
                return found
    return None


def is_paused(reply):
    """Did `wait_for_pause` answer that the CPU stopped?

    **The key is `status`.** Measured against the live server on 2026-09-03:
    running is `{"status": "running", "poll_after_ms": 50, "message": ...}`,
    stopped is `{"status": "paused", "pc": ...}`. Reading another key reads
    every reply as "still running", and the breakpoint seems never to fire.
    `state` and a bare `paused: true` are accepted too.
    """
    if isinstance(reply, dict):
        for key in ("status", "state"):
            if str(reply.get(key, "")).lower() == "paused":
                return True
        return reply.get("paused") is True
    if isinstance(reply, str):
        low = reply.lower()
        return "paused" in low and "not paused" not in low
    return False


# --- the wait ----------------------------------------------------------

def _probe(client, alive):
    """The liveness probe: `alive`, the client's own, or the module's."""
    if alive is not None:
        return alive
    own = getattr(client, "_liveness", None)
    if callable(own):
        return own
    return client_module.process_alive


def _died():
    return Fail(
        "the emulator died while waiting for the CPU to stop (%s, pitfall "
        "35: the fork dies on its own during free execution, which is what "
        "waiting for a breakpoint is, and writes nothing when it goes). "
        "Relaunch it and repeat" % PLAN)


def wait_for_pause(session, seconds, interval=POLL_SECONDS, nudge=None,
                   every=NUDGE_EVERY, required=True, alive=None):
    """Wait for the CPU to stop; the seconds it took, as a float.

    Does not resume: the caller sends `continue` (or a press) first. Each
    round sleeps `interval` seconds (0 polls without sleeping), asks
    `wait_for_pause` of the server, nudges with the button `nudge` every
    `every` seconds when one is given, and asks the liveness probe.

    `alive` is a callable answering True, False or None (unknown); None
    here means the client's own probe. A False is a `Fail` naming pitfall
    35. On timeout it is a `Fail`, or None with `required=False` -- compare
    with `is None`, since a hit on the first poll can take 0.0 seconds.

    **Look before nudging.** `press_button` resumes the machine to deliver
    the press, so a blind nudge can start again the halt being waited for.
    """
    if interval < 0:
        raise ValueError("cannot poll every %r seconds" % (interval,))
    client = _client(session)
    probe = _probe(client, alive)
    button = buttons.canonical(nudge) if nudge else None
    start = time.time()
    deadline = start + seconds
    last_nudge = None
    while True:
        if interval:
            time.sleep(interval)
        if is_paused(client.call("wait_for_pause")):
            return time.time() - start
        if button and (last_nudge is None
                       or time.time() - last_nudge >= every):
            last_nudge = time.time()
            try:
                # duration_frames, or the pad stays held (pitfall 36)
                client.call("press_button", button=button,
                            duration_frames=NUDGE_FRAMES)
            except ToolError:
                pass
            if is_paused(client.call("wait_for_pause")):
                return time.time() - start
        if probe() is False:
            raise _died()
        if time.time() >= deadline:
            break
    if required:
        raise Fail(
            "the CPU did not stop within %ss. Either nothing triggers the "
            "breakpoint in what the game is doing now -- put it where that "
            "happens first -- or the emulator stopped stepping. Silence is "
            "not an answer here" % (seconds,))
    return None


# --- arming ------------------------------------------------------------

def _addresses(addresses):
    if isinstance(addresses, (int, str)):
        return [addresses]
    return list(addresses)


@contextlib.contextmanager
def breakpoints(session, addresses, type="execute"):
    """Clear, arm one breakpoint of `type` per address, and yield the client.

    `type` is the fork's `breakpoint` type: `execute`, `read` or `write`.
    On the way out -- normally or by any exception -- the breakpoints are
    cleared and the machine paused, each attempted even if the other fails.
    """
    client = _client(session)
    client.call("breakpoint", action="clear")
    try:
        for address in _addresses(addresses):
            client.call("breakpoint", action="add", type=type,
                        address=hx(parse_address(address)))
        yield client
    finally:
        _quietly(client, "breakpoint", action="clear")
        _quietly(client, "pause")


@contextlib.contextmanager
def vram_watch(session, x, y, width, height):
    """A VRAM write watch on a rectangle; yields the server's reply.

    Removed by its `id` on the way out, and the machine paused, whatever
    happens. Each hit is read with `last_vram_hit`.
    """
    client = _client(session)
    watch = client.call("vram_watch", action="add", x=x, y=y, width=width,
                        height=height)
    try:
        yield watch
    finally:
        ident = watch.get("id", 1) if isinstance(watch, dict) else 1
        _quietly(client, "vram_watch", action="remove", id=ident)
        _quietly(client, "pause")


def last_vram_hit(session):
    """`((x, y, width, height), pc)` of the last write the VRAM watch saw.

    The watch reports the last write of a batch, not every one, so what
    this says is the shape of a write and where it landed.
    """
    hit = _client(session).call("vram_watch", action="last_hit")
    hit = hit if isinstance(hit, dict) else {}
    return ((hit.get("x"), hit.get("y"), hit.get("width"),
             hit.get("height")), hit.get("pc"))


# --- the measurements --------------------------------------------------

def _disassemble(client, around, before, after):
    reply = client.call("disassemble",
                        address=hx(around - before * INSTRUCTION_SIZE),
                        count=before + after)
    return reply if isinstance(reply, list) else []


def find_store(rows, registers, address):
    """`(row, split_store parts, base value)` of the row that wrote `address`.

    The row whose base register plus offset is `address`; None when no row
    of the window is that store.
    """
    for row in rows:
        text = row.get("instruction") if isinstance(row, dict) else str(row)
        parts = split_store(text)
        if not parts:
            continue
        _mnemonic, _source, offset, base = parts
        value = register_value(registers, base)
        if value is not None and value + offset == address:
            return (row, parts, value)
    return None


def who_writes(session, address, seconds=WATCH_SECONDS, presses=0,
               button="Right", press_frames=PRESS_FRAMES, nudge=None,
               interval=POLL_SECONDS, before=WINDOW_BEFORE,
               after=WINDOW_AFTER, caller_before=CALLER_BEFORE, alive=None):
    """Arm a write breakpoint on `address`, run, and come back with the hit.

    `presses` is how many times `button` is pressed while waiting, the
    press first and `seconds // presses` of wait after each; zero means the
    game is expected to write it on its own. `nudge` is the other way to
    keep a game moving: a tap every `NUDGE_EVERY` seconds of the wait.

    Returns `{"pc", "registers", "rows", "store", "caller"}`: the pc of the
    stop, the `gpr` registers, the disassembly around the pc, the
    `find_store` triple or None, and the disassembly before `ra` (empty
    without one). Nothing writing it in time is a `Fail`; the emulator
    dying is a `Fail` naming pitfall 35. Left paused, breakpoints cleared.
    """
    address = parse_address(address)
    with breakpoints(session, [address], "write") as client:
        client.call("continue")
        hit = None
        for _ in range(max(1, presses)):
            if presses:
                client.call("press_button", button=buttons.canonical(button),
                            duration_frames=press_frames)
            hit = wait_for_pause(session, max(1, seconds // max(1, presses)),
                                 interval=interval, nudge=nudge,
                                 required=False, alive=alive)
            if hit is not None:
                break
        if hit is None:
            raise Fail(
                "nothing wrote %s in %ss%s: either the address is not what "
                "the caller thinks it is, or the emulator stopped stepping "
                "-- silence is not an answer here"
                % (hx(address), seconds,
                   " and %d press(es) of %s" % (presses, button)
                   if presses else ""))
        registers = client.call("read_registers", group="gpr")
        pc = register_value(registers, "pc")
        if pc is None:
            raise Fail("the register read gave no pc: %r"
                       % (str(registers)[:200],))
        rows = _disassemble(client, pc, before, after)
        caller = []
        ra = register_value(registers, "ra")
        if ra is not None:
            caller = _disassemble(client, ra, caller_before, after)
        return {"pc": pc, "registers": registers, "rows": rows,
                "store": find_store(rows, registers, address),
                "caller": caller}


def stops(session, addresses, read, repeat, limit, seconds=STOPS_SECONDS,
          interval=0, alive=None):
    """What `read(registers)` makes of each stop at execute breakpoints.

    With several addresses armed the stops come in the order the game runs
    them, and `read` tells them apart by the pc. The run is closed by
    repetition, not by the clock: the first `repeat` readings coming round
    again in the same order end it, and the repeat is dropped. More than
    `limit` stops without that, or `seconds` going by, is a `Fail`.
    """
    addresses = _addresses(addresses)
    first = hx(parse_address(addresses[0]))
    out = []
    deadline = time.time() + seconds
    with breakpoints(session, addresses, "execute") as client:
        client.call("continue")
        while True:
            left = deadline - time.time()
            if left <= 0 or wait_for_pause(session, left, interval=interval,
                                           required=False,
                                           alive=alive) is None:
                raise Fail("%s stopped %d time(s) in %ss and never came "
                           "round" % (first, len(out), seconds))
            out.append(read(client.call("read_registers", group="gpr")))
            if len(out) >= 2 * repeat and out[-repeat:] == out[:repeat]:
                del out[-repeat:]
                return out
            if len(out) > limit:
                raise Fail("%s stopped %d times without coming round"
                           % (first, limit))
            client.call("continue")


def watch_reads(session, addresses, seconds=READ_SECONDS, stops=1,
                interval=0, alive=None):
    """Arm a read breakpoint on every address at once, and run.

    Returns `(hits, pcs)`: `(address, hit_count)` of each breakpoint that
    fired, from `breakpoint list`, and `{pc: times}` of the stops. Up to
    `stops` stops are waited for, `seconds` each; a wait with no stop ends
    the run quietly -- silence is a result here, read from `hits`.
    """
    pcs = {}
    with breakpoints(session, addresses, "read") as client:
        for _ in range(stops):
            client.call("continue")
            if wait_for_pause(session, seconds, interval=interval,
                              required=False, alive=alive) is None:
                break
            pc = register_value(client.call("read_registers", group="all"),
                                "pc")
            pcs[pc] = pcs.get(pc, 0) + 1
        listed = client.call("breakpoint", action="list")
        hits = [(parse_address(w["address"]), w["hit_count"])
                for w in (listed if isinstance(listed, list) else [])
                if w.get("hit_count")]
    return hits, pcs


# --- self-check --------------------------------------------------------

class _Fake:
    """Records every call; answers `wait_for_pause` from a script.

    `paused_after` polls answer running before one answers paused (None:
    never). `pcs` are the pcs successive `read_registers` give.
    """

    def __init__(self, paused_after=None, pcs=(), base=None, fail_clear=False):
        self.session = "fake"
        self.server = None
        self.calls = []
        self.paused_after = paused_after
        self.polls = 0
        self.pcs = list(pcs)
        self.reads = 0
        self.base = base
        self.fail_clear = fail_clear

    def initialize(self):
        self.server = {}
        return self.server

    def call(self, name, **arguments):
        self.calls.append((name, dict(arguments)))
        if name == "wait_for_pause":
            self.polls += 1
            if (self.paused_after is not None
                    and self.polls > self.paused_after):
                return {"status": "paused"}
            return {"status": "running", "poll_after_ms": 50}
        if name == "continue":
            self.polls = 0
            return {"status": "ok"}
        if (name == "breakpoint" and arguments.get("action") == "clear"
                and self.fail_clear and "pause" not in self.names()
                and len(self.calls) > 1):
            raise ToolError("breakpoint: planted failure")
        if name == "breakpoint" and arguments.get("action") == "list":
            return [{"address": "0x80012340", "hit_count": 2},
                    {"address": "0x80012344", "hit_count": 0}]
        if name == "read_registers":
            pc = self.pcs[self.reads % len(self.pcs)] if self.pcs else None
            self.reads += 1
            regs = {"v0": hx(self.base or 0), "ra": "0x80015000"}
            if pc is not None:
                regs["pc"] = hx(pc)
            return {"gpr": regs}
        if name == "disassemble":
            start = parse_address(arguments["address"])
            return [{"address": hx(start + 4 * i),
                     "instruction": "sb zero, 0x21a(v0)" if i == 6 else "nop"}
                    for i in range(arguments["count"])]
        if name == "vram_watch" and arguments.get("action") == "add":
            return {"id": 3}
        if name == "vram_watch" and arguments.get("action") == "last_hit":
            return {"x": 832, "y": 256, "width": 16, "height": 15,
                    "pc": "0x80013000"}
        return {"status": "ok"}

    def names(self):
        return [name for name, _ in self.calls]

    def tail(self, n):
        return [(name, kw.get("action")) for name, kw in self.calls[-n:]]


def _raises(fn, cls):
    """`(raised cls, the exception or what happened instead)`."""
    try:
        got = fn()
    except cls as e:
        return True, e
    except Exception as e:                                   # noqa: BLE001
        return False, "%s: %s" % (type(e).__name__, e)
    return False, "returned %r" % (got,)


def _check_parsing(check):
    check("parse_address takes 0x, bare hex, decimal and an int",
          parse_address("0x8001234A") == parse_address("8001234A")
          == 0x8001234A and parse_address("42") == 42
          and parse_address(0x21A) == 0x21A)
    for bad in ("", "zzz", "0xnope", "-"):
        ok, e = _raises(lambda: parse_address(bad), Fail)
        check("parse_address refuses %r" % (bad,), ok, e)
    check("hx is eight upper-case digits of the low 32 bits",
          hx(0x21A) == "0x0000021A" and hx(-4) == "0x" + "F" * 7 + "C",
          hx(-4))
    check("a store is taken apart",
          split_store("sb zero, 0x21a(v0)") == ("sb", "zero", 0x21A, "v0"))
    check("sw is too", split_store("sw a0, 0x10(sp)") == ("sw", "a0", 0x10,
                                                          "sp"))
    check("a negative offset keeps its sign",
          split_store("sb zero, -0x4(v0)") == ("sb", "zero", -4, "v0"))
    for not_a_store in ("nop", "jr ra", "addiu v0, v0, 1"):
        check("%r is not a store" % not_a_store,
              split_store(not_a_store) is None)
    regs = {"pc": "0x80012348", "v0": "0x80012100", "ra": "0x80015000"}
    check("a register is read as an int",
          register_value(regs, "v0") == 0x80012100)
    check("nested register groups are searched",
          register_value({"gpr": regs}, "ra") == 0x80015000)
    check("a register that is not there is None",
          register_value(regs, "t7") is None)
    check("a running reply is not a pause",
          not is_paused({"status": "running", "poll_after_ms": 50,
                         "message": "System is still running."}))
    check("a paused reply is a pause",
          is_paused({"status": "paused", "pc": "0x80012348"}))
    check("the state spelling and the bare boolean are accepted",
          is_paused({"state": "paused"}) and is_paused({"paused": True}))
    check("an unknown shape is not a pause", not is_paused({"cpu": "stopped"}))


def _check_wait(check):
    ok, e = _raises(lambda: wait_for_pause(_Fake(), 0.2, interval=0,
                                           alive=lambda: True), Fail)
    check("a watchpoint that never fires is a Fail",
          ok and "did not stop" in str(e), e)
    got = wait_for_pause(_Fake(), 0.1, interval=0, required=False,
                         alive=lambda: True)
    check("with required=False, never firing is None", got is None, got)
    ok, e = _raises(lambda: wait_for_pause(_Fake(), 1.0, interval=0,
                                           alive=lambda: False), Fail)
    check("a death mid-wait is a Fail citing pitfall 35",
          ok and "pitfall 35" in str(e) and "died" in str(e)
          and PLAN in str(e), e)
    ok, e = _raises(lambda: wait_for_pause(_Fake(), 0.1, interval=0,
                                           alive=lambda: None), Fail)
    check("an unknown liveness keeps waiting to the timeout",
          ok and "did not stop" in str(e), e)
    fake = _Fake(paused_after=3)
    got = wait_for_pause(fake, 10.0, interval=0, alive=lambda: True)
    check("a pause is seen on the poll it comes, with interval=0",
          got is not None and fake.polls == 4, (got, fake.polls))
    started = time.time()
    wait_for_pause(_Fake(paused_after=2), 10.0, interval=0.05,
                   alive=lambda: True)
    took = time.time() - started
    check("the interval is slept between polls", took >= 0.14, took)
    ok, e = _raises(lambda: wait_for_pause(_Fake(), 1, interval=-1),
                    ValueError)
    check("a negative interval is refused", ok, e)

    fake = _Fake()
    wait_for_pause(fake, 0.3, interval=0.01, nudge="cross", every=0.05,
                   required=False, alive=lambda: True)
    presses = [kw for name, kw in fake.calls if name == "press_button"]
    check("the nudge is pressed while waiting", len(presses) >= 2,
          len(presses))
    check("and it carries a release (pitfall 36) and the canonical name",
          presses and all(kw.get("duration_frames") == NUDGE_FRAMES
                          and kw.get("button") == "Cross" for kw in presses),
          presses[:1])
    fake = _Fake()
    wait_for_pause(fake, 0.1, interval=0.01, required=False,
                   alive=lambda: True)
    check("and not pressed when none was asked for",
          "press_button" not in fake.names())

    class Probed(_Fake):
        def _liveness(self):
            return False
    ok, e = _raises(lambda: wait_for_pause(Probed(), 1.0, interval=0), Fail)
    check("the client's own liveness probe is the default",
          ok and "pitfall 35" in str(e), e)

    class Wrapper:
        def __init__(self, inner):
            self.client = inner
    fake = _Fake(paused_after=0)
    wait_for_pause(Wrapper(fake), 1.0, interval=0, alive=lambda: True)
    check("a session's client is the one called",
          fake.names() == ["wait_for_pause"], fake.names())


def _check_breakpoints(check):
    fake = _Fake()
    ok, e = _raises(lambda: _armed_then_raise(fake), KeyError)
    check("an exception inside breakpoints propagates", ok, e)
    check("an exception inside breakpoints still clears and pauses",
          fake.tail(2) == [("breakpoint", "clear"), ("pause", None)],
          fake.tail(2))
    added = [kw for name, kw in fake.calls
             if name == "breakpoint" and kw.get("action") == "add"]
    check("breakpoints clears first, then arms one per address",
          fake.calls[0] == ("breakpoint", {"action": "clear"})
          and [kw["address"] for kw in added] == ["0x80012340", "0x80012344"]
          and all(kw["type"] == "read" for kw in added), added)
    fake = _Fake(fail_clear=True)
    _raises(lambda: _armed_then_raise(fake), KeyError)
    check("a clear that fails on the way out does not skip the pause",
          fake.tail(1) == [("pause", None)], fake.tail(2))
    fake = _Fake()
    with breakpoints(fake, 0x80012340, "write"):
        pass
    check("a normal exit clears and pauses too",
          fake.tail(2) == [("breakpoint", "clear"), ("pause", None)],
          fake.tail(2))

    fake = _Fake()
    try:
        with vram_watch(fake, 832, 256, 64, 15) as watch:
            got = last_vram_hit(fake)
            raise KeyError("planted")
    except KeyError:
        pass
    removed = [kw for name, kw in fake.calls
               if name == "vram_watch" and kw.get("action") == "remove"]
    check("vram_watch removes its watch by id and pauses, even on exception",
          watch == {"id": 3} and removed == [{"action": "remove", "id": 3}]
          and fake.tail(1) == [("pause", None)], fake.calls[-2:])
    check("last_vram_hit gives the rectangle and the pc",
          got == ((832, 256, 16, 15), "0x80013000"), got)


def _armed_then_raise(fake):
    with breakpoints(fake, ["0x80012340", 0x80012344], "read"):
        fake.call("continue")
        raise KeyError("planted")


def _check_measurements(check):
    base = 0x80012100
    address = base + 0x21A
    fake = _Fake(paused_after=1, pcs=[0x80012348], base=base)
    hit = who_writes(fake, address, seconds=5, interval=0, alive=lambda: True)
    check("who_writes returns pc, registers, rows, store, caller",
          set(hit) == {"pc", "registers", "rows", "store", "caller"},
          sorted(hit))
    check("who_writes finds the store whose base + offset is the address",
          hit["store"] is not None and hit["store"][2] == base
          and hit["store"][1] == ("sb", "zero", 0x21A, "v0"), hit["store"])
    check("who_writes reads a window around the pc and one before ra",
          hit["pc"] == 0x80012348
          and len(hit["rows"]) == WINDOW_BEFORE + WINDOW_AFTER
          and len(hit["caller"]) == CALLER_BEFORE + WINDOW_AFTER,
          (len(hit["rows"]), len(hit["caller"])))
    check("who_writes arms a write breakpoint and ends cleared and paused",
          ("breakpoint", {"action": "add", "type": "write",
                          "address": hx(address)}) in fake.calls
          and fake.tail(2) == [("breakpoint", "clear"), ("pause", None)],
          fake.tail(2))
    fake = _Fake(base=base)
    ok, e = _raises(lambda: who_writes(fake, address, seconds=1, presses=2,
                                       interval=0, alive=lambda: True), Fail)
    check("who_writes with nothing writing is a Fail, left cleared and paused",
          ok and "nothing wrote" in str(e)
          and fake.tail(2) == [("breakpoint", "clear"), ("pause", None)], e)
    check("and the presses carry their duration",
          [kw for name, kw in fake.calls if name == "press_button"]
          == [{"button": "Right", "duration_frames": PRESS_FRAMES}] * 2)

    cycle = [0x80012000, 0x80012010, 0x80012020]
    fake = _Fake(paused_after=0, pcs=cycle * 3)
    got = stops(fake, tuple(cycle), lambda r: register_value(r, "pc"),
                repeat=2, limit=20, interval=0, alive=lambda: True)
    check("stops closes the run when the first stops come round",
          got == cycle, got)
    ok, e = _raises(lambda: stops(_Fake(paused_after=0, pcs=range(100)),
                                  [0x80012000], lambda r: r["gpr"]["pc"],
                                  repeat=2, limit=5, interval=0,
                                  alive=lambda: True), Fail)
    check("stops past its limit is a Fail", ok and "without coming" in str(e),
          e)
    ok, e = _raises(lambda: stops(_Fake(), [0x80012000], lambda r: r,
                                  repeat=1, limit=5, seconds=0.1, interval=0,
                                  alive=lambda: True), Fail)
    check("stops with no stop in time is a Fail", ok and "never came" in str(e),
          e)

    fake = _Fake(paused_after=0, pcs=[0x80012348])
    hits, pcs = watch_reads(fake, [0x80012340, 0x80012344], stops=2,
                            interval=0, alive=lambda: True)
    check("watch_reads lists the breakpoints that fired and the pcs",
          hits == [(0x80012340, 2)] and pcs == {0x80012348: 2}, (hits, pcs))
    fake = _Fake()
    hits, pcs = watch_reads(fake, [0x80012340], seconds=0.1, stops=3,
                            interval=0, alive=lambda: True)
    check("watch_reads ends quietly on a silent wait, cleared and paused",
          pcs == {} and fake.names().count("continue") == 1
          and fake.tail(2) == [("breakpoint", "clear"), ("pause", None)],
          fake.tail(2))


def self_check() -> list:
    """Parsing, the wait, the cleanup and the measurements, against fakes.

    Returns one `(name, passed, detail)` per assertion.
    """
    results = []

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    for part in (_check_parsing, _check_wait, _check_breakpoints,
                 _check_measurements):
        try:
            part(check)
        except Exception as exc:                             # noqa: BLE001
            check("%s ran" % part.__name__, False,
                  "%s: %s" % (type(exc).__name__, exc))
    return results

#!/usr/bin/env python3
"""Who writes this RAM address -- flow A, as a command instead of a Log.

USAGE
-----
    python3 tools/pes2/who_writes.py 0x8007151B --width 2
    python3 tools/pes2/who_writes.py 0x8007151B --timeout 180
    python3 tools/pes2/who_writes.py --self-check     # no emulator needed

WHY THIS EXISTS
---------------
Flow A -- *who writes this address* -- is the whole reason the DuckStation
fork was adopted, once PES2-TASK-32 delivered flows C and D in pure Python
(`savestate.py`). It closed on 2026-09-03 and produced a good answer:
`sb zero, 0x21a(v0)` at `0x80083574`, `v0 = 0x80071301`, cleanup routine at
`0x80083560`. But the *procedure* stayed in a Log, and nothing in
`tools/pes2/` knew how to arm a breakpoint -- so redoing it meant writing the
`mcp.py --call breakpoint action=add ...` sequence by hand every time.

Flow C got `savestate.py scan`, with a selftest, red cases and a place in
`pes2_selftest`. Flow A got a paragraph of prose. This is the missing half,
and it is not a convenience: phases 3 and 4 -- PES2-TASK-07 and the
disc-to-RAM loop of section 4.2 -- are flow A repeated over other addresses.

WHAT IT DOES
------------
Against an emulator that is already running (`fork.py launch`), it clears the
breakpoints, arms a write watchpoint on the address, resumes, and waits. On
the hit it reads the registers and disassembles around the PC, then prints
the reading already worked out: the storing instruction, its base register
and offset, the check that base + offset is the address you asked about, and
`ra`, which is who called the routine.

THE WAIT IS THE HARD PART
-------------------------
The fork dies on its own during free execution -- pitfall 35 of section 6.11,
four deaths in six runs when it was measured -- and free execution is exactly
what waiting for a watchpoint is. So the wait checks that the process is
still there on every poll and says *the emulator died* rather than *it is not
running*, which is the sentence that describes forgetting to launch it. The
two call for opposite actions and used to be the same sentence.

A watchpoint that never fires is a **failure**, not an empty result. An
address nothing writes and an emulator that stopped stepping look identical
in a silent return.
"""

import argparse
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import mcp                                                    # noqa: E402
from mcp import NotRunning, ToolError                         # noqa: E402

try:
    import fork                                               # noqa: E402
except Exception:                                             # noqa: BLE001
    fork = None

SKIP = 77
POLL_SECONDS = 1.0
# Long enough for the game to read it as a tap. `mcp_drive` holds 6 frames
# for menu work and this is the same order; the emulator releases it itself.
NUDGE_FRAMES = 6


class Fail(Exception):
    pass


class Skip(Exception):
    pass


# --- address arithmetic ------------------------------------------------

def parse_address(text):
    """Accept 0x8007151B, 8007151B, or a decimal string.

    The MCP tools take "integer or hex string" and the fork is inconsistent
    about which it echoes back, so everything is normalised to int here and
    formatted on the way out.
    """
    if isinstance(text, int):
        return text
    t = str(text).strip()
    if not t:
        raise Fail("empty address")
    # A leading sign is stripped first: `sb zero, -0x4(v0)` is a real
    # instruction, and int() will not take "-0x4" in any base.
    sign = 1
    if t[0] in "+-":
        sign = -1 if t[0] == "-" else 1
        t = t[1:].strip()
    if not t:
        raise Fail(f"{text!r} is not an address")
    try:
        if t.lower().startswith("0x"):
            return sign * int(t, 16)
        if any(c in "abcdefABCDEF" for c in t):
            return sign * int(t, 16)
        return sign * int(t, 10)
    except ValueError:
        raise Fail(f"{text!r} is not an address") from None


def hx(value):
    return f"0x{value & 0xFFFFFFFF:08X}"


def split_store(instruction):
    """Pull (mnemonic, source, offset, base) out of a MIPS store.

    `sb zero, 0x21a(v0)` -> ('sb', 'zero', 0x21a, 'v0'). Returns None for
    anything that is not a load/store shaped instruction, because the PC
    after a watchpoint hit is not always on the store itself -- the fork
    stops on the instruction *after* it on this build, which is why the
    caller disassembles a window and not one instruction.
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
    """A register out of `read_registers`, whatever shape it came in."""
    if not isinstance(registers, dict):
        return None
    for key in (name, name.lower(), name.upper(), f"${name}"):
        if key in registers:
            return parse_address(registers[key])
    for group in registers.values():
        if isinstance(group, dict):
            found = register_value(group, name)
            if found is not None:
                return found
    return None


# --- the run -----------------------------------------------------------

def is_paused(reply):
    """Did `wait_for_pause` say the CPU stopped?

    **The key is `status`.** Measured against the live server on 2026-09-03:
    running gives `{"status": "running", "poll_after_ms": 50, "message": …}`
    and stopped gives `{"status": "paused", "pc": "0x80019DE8"}`. Guessing
    `paused` or `state` -- the two obvious names -- reads every reply as
    "still running", so the watchpoint appears never to fire and the failure
    looks like the game, not the parser. That is how the first version of
    this file spent two runs blaming PES2.
    """
    if isinstance(reply, dict):
        for key in ("status", "state"):
            if str(reply.get(key, "")).lower() == "paused":
                return True
        if reply.get("paused") is True:
            return True
        return False
    if isinstance(reply, str):
        low = reply.lower()
        return "paused" in low and "not paused" not in low
    return False


def emulator_alive():
    if fork is None:
        return None
    try:
        return bool(fork.running_pids())
    except Exception:                                         # noqa: BLE001
        return None


def wait_for_hit(client, timeout, say=print, nudge=None, every=6.0,
                 alive=None):
    """Resume and wait for the watchpoint, watching the process too.

    Returns the number of seconds it took. Raises rather than returning
    quietly on either failure, because the two things that can go wrong here
    -- nothing writes the address, and the emulator died -- both look like
    "no answer".

    **`nudge` is not a convenience.** PES2 does not run freely: it stops at
    every kickoff waiting for a button, so `continue` on its own leaves the
    match frozen and nothing is written. Measured 2026-09-03: with the ball
    dead the score watchpoint sat at `hit_count: 0` for 150 s, and the same
    watchpoint reached 9 while `pad.py run` was giving the kickoffs. The
    press has to come from **this** client -- a second process talking to the
    server invalidates the session this one holds (`missing or invalid
    MCP-Session-Id`), so the obvious "run pad.py alongside" does not work.
    """
    # Injected, not looked up: `self_check` has to drive both the timeout
    # and the death path with no emulator anywhere, and a self-check whose
    # verdict depends on whether something outside is running is not a
    # self-check. This one already went red inside `pes2_selftest` for
    # exactly that reason while passing on its own.
    alive = emulator_alive if alive is None else alive
    client.call("continue")
    deadline = time.time() + timeout
    last_nudge = 0.0
    while time.time() < deadline:
        time.sleep(POLL_SECONDS)
        # Order matters. `press_button` resumes the machine to deliver the
        # press, so nudging blind can undo the very halt being waited for --
        # the watchpoint fires, the CPU stops, and the next nudge starts it
        # again before the poll sees it. Look first, and only nudge a machine
        # that is still going.
        if is_paused(client.call("wait_for_pause")):
            return round(time.time() - (deadline - timeout), 1)
        if nudge and time.time() - last_nudge >= every:
            last_nudge = time.time()
            try:
                # `duration_frames` or the button is never released. Without
                # it `press_button` answers `{"state": "pressed"}` and leaves
                # it held, so the first nudge pins the pad down and every one
                # after it is a no-op -- which looks exactly like a game that
                # will not advance. The release has to run on the emulator's
                # own clock, because during free execution there is nothing
                # here stepping frames to release it on.
                client.call("press_button", button=nudge.capitalize()
                            if nudge.islower() else nudge,
                            duration_frames=NUDGE_FRAMES)
            except ToolError:
                pass
            if is_paused(client.call("wait_for_pause")):
                return round(time.time() - (deadline - timeout), 1)
        if alive() is False:
            raise Fail(
                "the emulator died while the watchpoint was armed. This is "
                "pitfall 35 of section 6.11 -- the fork dies on its own "
                "during free execution, which is exactly what waiting for a "
                "watchpoint is -- and it writes nothing when it goes. "
                "Relaunch with fork.py launch and repeat")
        if is_paused(client.call("wait_for_pause")):
            return round(time.time() - (deadline - timeout), 1)
    raise Fail(
        f"the watchpoint did not fire within {timeout}s. Either nothing "
        f"writes that address in what the game is doing right now -- put it "
        f"in the state where the write happens first -- or the emulator "
        f"stopped stepping. Silence is not an answer here")


def who_writes(address, width=1, timeout=180, nudge=None, verbose=True):
    def say(msg):
        if verbose:
            print(f"  {msg}", flush=True)

    client = mcp.Client()
    client.initialize()

    say(f"clearing breakpoints, then a write watchpoint on {hx(address)}")
    client.call("breakpoint", action="clear")
    client.call("breakpoint", action="add", type="write", address=hx(address))
    try:
        if nudge:
            say(f"nudging with {nudge} while waiting -- this game stops at "
                f"every kickoff, and a stopped game writes nothing")
        took = wait_for_hit(client, timeout, say, nudge=nudge)  # noqa: E501
        say(f"the watchpoint fired after {took}s")

        registers = client.call("read_registers", group="gpr")
        pc = register_value(registers, "pc")
        if pc is None:
            raise Fail("the register read gave no pc -- cannot locate the "
                       f"store. Got: {str(registers)[:200]}")

        # A window, not one instruction: on this build the CPU stops on the
        # instruction *after* the store, and the routine's shape is worth
        # seeing anyway.
        window = client.call("disassemble", address=hx(pc - 16), count=8)
        rows = window if isinstance(window, list) else []

        store = None
        for row in rows:
            text = row.get("instruction") if isinstance(row, dict) else str(row)
            parts = split_store(text)
            if not parts:
                continue
            _, _, offset, base = parts
            base_value = register_value(registers, base)
            if base_value is None:
                continue
            if base_value + offset == address:
                store = (row, parts, base_value)
                break

        print()
        print(f"address      {hx(address)}  (width {width})")
        print(f"stopped at   {hx(pc)}")
        if store:
            row, (mnemonic, src, offset, base), base_value = store
            at = row.get("address") if isinstance(row, dict) else "?"
            print(f"written by   {at}  {mnemonic} {src}, {hx(offset)}({base})")
            print(f"             {base} = {hx(base_value)}, "
                  f"{hx(base_value)} + {hx(offset)} = {hx(address)}")
        else:
            print("written by   not identified in the 8 instructions before "
                  "the stop -- widen the window or read the disassembly")
        ra = register_value(registers, "ra")
        if ra is not None:
            print(f"called from  ra = {hx(ra)}")
        print()
        for row in rows:
            if isinstance(row, dict):
                mark = " <-" if store and row is store[0] else ""
                print(f"  {row.get('address')}  {row.get('instruction')}{mark}")
        return 0
    finally:
        try:
            client.call("breakpoint", action="clear")
        except Exception:                                     # noqa: BLE001
            pass


# --- self-check --------------------------------------------------------

def self_check(verbose=True):
    """What can be proved with no emulator: the parsing and the arithmetic."""
    bad = []

    def check(what, ok, detail=""):
        if verbose:
            print(f"  {'ok' if ok else 'FAIL'}   {what}"
                  + (f"  ({detail})" if detail and not ok else ""))
        if not ok:
            bad.append(f"{what}{': ' + detail if detail else ''}")

    check("0x prefix", parse_address("0x8007151B") == 0x8007151B)
    check("bare hex", parse_address("8007151B") == 0x8007151B)
    check("decimal", parse_address("42") == 42)
    check("an int passes through", parse_address(0x21A) == 0x21A)
    for bad_text in ("", "zzz", "0xnope"):
        try:
            parse_address(bad_text)
            check(f"{bad_text!r} is refused", False, "accepted it")
        except Fail:
            check(f"{bad_text!r} is refused", True)

    # The instruction the 2026-09-03 run found, taken apart.
    parts = split_store("sb zero, 0x21a(v0)")
    check("a store is taken apart", parts == ("sb", "zero", 0x21A, "v0"),
          str(parts))
    check("sw is too", split_store("sw a0, 0x10(sp)") == ("sw", "a0", 0x10, "sp"))
    check("a negative offset keeps its sign",
          split_store("sb zero, -0x4(v0)") == ("sb", "zero", -4, "v0"))
    for not_a_store in ("nop", "jr ra", "addiu v0, v0, 1"):
        check(f"{not_a_store!r} is not a store", split_store(not_a_store) is None)

    # The arithmetic that decides the answer, on the measured numbers.
    check("v0 + 0x21a lands on the score byte",
          0x80071301 + 0x21A == 0x8007151B,
          hx(0x80071301 + 0x21A))

    regs = {"pc": "0x80083578", "v0": "0x80071301", "ra": "0x800834C0"}
    check("a register is read as an int",
          register_value(regs, "v0") == 0x80071301)
    check("nested register groups are searched",
          register_value({"gpr": regs}, "ra") == 0x800834C0)
    check("a register that is not there is None",
          register_value(regs, "t7") is None)

    # The reply shapes, copied from the live server on 2026-09-03. These are
    # the assertion that stops the parser from silently reading every reply
    # as "still running" -- which is what the first version did, and it looks
    # exactly like a watchpoint nothing triggers.
    check("a running reply is not a hit",
          not is_paused({"status": "running", "poll_after_ms": 50,
                         "message": "System is still running."}))
    check("a paused reply is a hit",
          is_paused({"status": "paused", "pc": "0x80019DE8"}))
    check("the `state` spelling is accepted too",
          is_paused({"state": "paused"}))
    check("and the bare boolean", is_paused({"paused": True}))
    check("an unknown shape is not a hit", not is_paused({"cpu": "stopped"}))

    # **The red case**: a watchpoint that never fires must fail, not return
    # an empty answer. An address nothing writes and an emulator that stopped
    # stepping are indistinguishable in a quiet return.
    class _Never:
        def call(self, name, **kw):
            return {"status": "running", "poll_after_ms": 50}

    try:
        wait_for_hit(_Never(), timeout=2.0, say=lambda _m: None,
                     alive=lambda: True)
        check("a watchpoint that never fires is a failure", False,
              "it returned quietly")
    except Fail as e:
        check("a watchpoint that never fires is a failure",
              "did not fire" in str(e), str(e)[:60])

    # The nudge actually leaves the client, and only when asked for.
    class _Counting:
        def __init__(self):
            self.presses = 0
            self.held = None

        def call(self, name, **kw):
            if name == "press_button":
                self.presses += 1
                self.held = kw.get("duration_frames")
            return {"status": "running"}

    c = _Counting()
    try:
        wait_for_hit(c, timeout=3.0, say=lambda _m: None, nudge="Cross",
                     every=0.5, alive=lambda: True)
    except Fail:
        pass
    check("the nudge is pressed while waiting", c.presses >= 2, str(c.presses))
    # Without a duration the pad stays held and every later nudge is a no-op,
    # which reads as a game that refuses to advance.
    check("and it carries a release", c.held == NUDGE_FRAMES, str(c.held))
    c = _Counting()
    try:
        wait_for_hit(c, timeout=3.0, say=lambda _m: None, alive=lambda: True)
    except Fail:
        pass
    check("and not pressed when none was asked for", c.presses == 0,
          str(c.presses))

    # And the other silence: the process gone mid-wait is named as pitfall 35
    # and not as "not running", which is the sentence for never having
    # launched it.
    try:
        wait_for_hit(_Never(), timeout=10.0, say=lambda _m: None,
                     alive=lambda: False)
        check("a death mid-wait is a failure", False, "it returned quietly")
    except Fail as e:
        check("a death mid-wait says pitfall 35, not 'not running'",
              "pitfall 35" in str(e) and "died" in str(e), str(e)[:60])

    if verbose:
        print("SELF-CHECK " + ("FAILED" if bad else
                               "OK: addresses, stores, registers, both waits"))
    return bad


# --- entry point -------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("address", nargs="?",
                    help="RAM address, hex (0x8007151B) or decimal")
    ap.add_argument("--width", type=int, default=1,
                    help="bytes the write covers; reported, not enforced")
    ap.add_argument("--timeout", type=float, default=180.0,
                    help="seconds to wait for the watchpoint (default 180)")
    ap.add_argument("--nudge", metavar="BUTTON", default=None,
                    help="press this every few seconds while waiting. PES2 "
                         "stops at every kickoff, and a stopped game writes "
                         "nothing -- `--nudge Cross` keeps a match moving")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return 1 if self_check() else 0
    if not args.address:
        ap.error("give an address, or --self-check")

    try:
        return who_writes(parse_address(args.address), width=args.width,
                          timeout=args.timeout, nudge=args.nudge)
    except NotRunning as e:
        print(f"skipping: {e}")
        return SKIP
    except Skip as e:
        print(f"skipping: {e}")
        return SKIP
    except (Fail, ToolError) as e:
        print(f"WHO-WRITES FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

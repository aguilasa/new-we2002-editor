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
`0x80083560`. This command is that procedure, so redoing it is one line.

WHAT IT DOES
------------
Against an emulator that is already running (`duckmcp/cli.py launch`), it
attaches, arms a write watchpoint on the address, resumes, and waits. On the
hit it reads the registers and disassembles around the PC, then prints the
reading already worked out: the storing instruction, its base register and
offset, the check that base + offset is the address you asked about, and
`ra`, which is who called the routine.

**The measurement is the lib's** (`duckmcp.debug.who_writes`, DMCP-TASK-16):
the wait that watches the process -- a fork that dies mid-wait is pitfall 35,
not "not running" --, the watchpoint that never fires as a failure and not an
empty answer, the nudge with its release, and the breakpoints cleared in a
`finally`. What stays here is the command line and the report. Two things
changed with the move: the run now ends with the machine **paused** (every
armed wait of the lib does), and the parsing helpers below are the lib's,
re-exported for the callers that still import them from here
(`tools/kits/oracle.py`, `tools/looks/oracle.py`).
"""

import argparse
import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if os.path.dirname(HERE) not in sys.path:        # tools/, for duckmcp
    sys.path.insert(0, os.path.dirname(HERE))

from duckmcp import debug                                     # noqa: E402
from duckmcp.debug import (hx, is_paused, parse_address,      # noqa: E402,F401
                           register_value, split_store)
from duckmcp.errors import (SKIP, Fail, NotRunning, Skip,     # noqa: E402,F401
                            ToolError)
from duckmcp.session import Session                           # noqa: E402

# The disassembly window this command has always printed: 4 instructions
# before the pc and 4 from it (`pc - 16`, count 8). The lib's default is the
# wider 8 + 4 of the other copy; passing these keeps the report unchanged.
BEFORE = 4
AFTER = 4


def report(hit, address, width, out=print):
    """Print the reading of a `debug.who_writes` hit, as this CLI always did."""
    pc = hit["pc"]
    rows = hit["rows"]
    store = hit["store"]
    out("")
    out(f"address      {hx(address)}  (width {width})")
    out(f"stopped at   {hx(pc)}")
    if store:
        row, (mnemonic, src, offset, base), base_value = store
        at = row.get("address") if isinstance(row, dict) else "?"
        out(f"written by   {at}  {mnemonic} {src}, {hx(offset)}({base})")
        out(f"             {base} = {hx(base_value)}, "
            f"{hx(base_value)} + {hx(offset)} = {hx(address)}")
    else:
        out("written by   not identified in the 8 instructions before the "
            "stop -- widen the window or read the disassembly")
    ra = register_value(hit["registers"], "ra")
    if ra is not None:
        out(f"called from  ra = {hx(ra)}")
    out("")
    for row in rows:
        if isinstance(row, dict):
            mark = " <-" if store and row is store[0] else ""
            out(f"  {row.get('address')}  {row.get('instruction')}{mark}")


def who_writes(address, width=1, timeout=180, nudge=None, verbose=True,
               session=None, out=print):
    """Attach (or take `session`), measure, and print the report."""
    def say(msg):
        if verbose:
            out(f"  {msg}")

    session = Session.attach(verbose=verbose) if session is None else session
    say(f"clearing breakpoints, then a write watchpoint on {hx(address)}")
    if nudge:
        say(f"nudging with {nudge} while waiting -- this game stops at "
            f"every kickoff, and a stopped game writes nothing")
    hit = debug.who_writes(session, address, seconds=timeout, nudge=nudge,
                           before=BEFORE, after=AFTER)
    say(f"the watchpoint fired at {hx(hit['pc'])}")
    report(hit, address, width, out=out)
    return 0


# --- self-check --------------------------------------------------------
#
# The parsing, the arithmetic and both waits are checked where they live now,
# in `duckmcp/selftest.py` (the `debug:` lines). What is left to prove here is
# this file's own layer: the report reads the lib's hit right, and the exit
# codes are the ones ctest and the callers read.

class _Fake:
    """A client-shaped stand-in: one write at `0x80071301 + 0x21a`."""

    def __init__(self, fire=True):
        self.fire = fire
        self.names = []

    def initialize(self):
        return {}

    def _liveness(self):
        # Alive, so the verdict never depends on a fork outside running.
        return True

    def call(self, name, **arguments):
        self.names.append(name)
        if name == "wait_for_pause":
            return {"status": "paused" if self.fire else "running"}
        if name == "read_registers":
            return {"gpr": {"pc": "0x80083578", "v0": "0x80071301",
                            "ra": "0x800834C0"}}
        if name == "disassemble":
            start = parse_address(arguments["address"])
            return [{"address": hx(start + 4 * i),
                     "instruction": ("sb zero, 0x21a(v0)"
                                     if start + 4 * i == 0x80083574
                                     else "nop")}
                    for i in range(arguments["count"])]
        return {"status": "ok"}


def self_check(verbose=True):
    """The report and the exit codes, with no emulator. Failure strings."""
    bad = []

    def check(what, ok, detail=""):
        if verbose:
            print(f"  {'ok' if ok else 'FAIL'}   {what}"
                  + (f"  ({detail})" if detail and not ok else ""))
        if not ok:
            bad.append(f"{what}{': ' + detail if detail else ''}")

    lines = []
    fake = _Fake()
    who_writes(0x8007151B, width=1, timeout=2, verbose=False, session=fake,
               out=lines.append)
    text = "\n".join(lines)
    check("the store is named", "written by   0x80083574  sb zero, "
          "0x0000021A(v0)" in text, text[:200])
    check("and the arithmetic shown", "0x80071301 + 0x0000021A = 0x8007151B"
          in text, text[:200])
    check("ra is reported", "called from  ra = 0x800834C0" in text)
    rows = [line for line in lines if line.startswith("  0x")]
    # Literal numbers, not BEFORE + AFTER: the assertion is that the window
    # is still the one this command printed before the lib (pc - 16, 8 rows).
    check("the window is the 8 rows from pc - 16 this CLI always printed",
          len(rows) == 8 and rows[0].startswith("  0x80083568"),
          "%d rows, first %r" % (len(rows), rows[:1]))
    check("the run ends paused with the breakpoints cleared",
          fake.names[-2:] == ["breakpoint", "pause"], str(fake.names[-2:]))

    def quiet_main(argv, **kw):
        sink = io.StringIO()
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            return main(argv, **kw)

    # The red case of the command line: nothing fires within the timeout is
    # exit 1, not a quiet 0.
    code = quiet_main(["0x8007151B", "--timeout", "1"],
                      session=_Fake(fire=False))
    check("a watchpoint that never fires exits 1", code == 1, str(code))

    def _down():
        raise NotRunning("no fork on the port")

    code = quiet_main(["0x8007151B"], attach=_down)
    check("no emulator exits SKIP (77)", code == SKIP, str(code))
    code = quiet_main(["zzz"], session=_Fake())
    check("an address that is not one exits 1", code == 1, str(code))

    if verbose:
        print("SELF-CHECK " + ("FAILED" if bad else
                               "OK: report and exit codes over duckmcp.debug"))
    return bad


# --- entry point -------------------------------------------------------

def main(argv=None, session=None, attach=None):
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
        address = parse_address(args.address)
        if session is None:
            session = (attach or Session.attach)()
        return who_writes(address, width=args.width,
                          timeout=args.timeout, nudge=args.nudge,
                          session=session)
    except (NotRunning, Skip) as e:
        print(f"skipping: {e}")
        return SKIP
    except (Fail, ToolError) as e:
        print(f"WHO-WRITES FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

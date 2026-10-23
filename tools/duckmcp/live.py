#!/usr/bin/env python3
"""The live gate of duckmcp: boot a disc under the fork, step it, read it, kill it.

    python3 tools/duckmcp/live.py [--image COPY.cue] [--steps 5]

The image is any working copy's `.cue`; without `--image` it comes from
`DUCKSTATION_TEST_IMAGE` (read through `env.get`, rule (d)). Nothing here
knows which game it is: the gate asks only what every disc answers --
the tools the server declares, that `frame_step` moves `frame_number`,
that all of RAM and all of VRAM read back at the console's sizes, and
that `game()` names a serial.

What it does, in order: `fork.launch` (no title match), `pause`, count
`tools/list`, read `get_status` `frame_number`, call `frame_step` `--steps`
times, read `frame_number` again and demand it advanced by **exactly** the
number of steps -- measured on 2026-10-22, one `frame_step` is one frame of
`frame_number`, paused before and after. Then, through a `Session` wrapping
the same client (which does not own the process): all of main RAM by
`read_ram` must be `psx.RAM_SIZE` bytes, `dump_vram` must write a PNG of
`psx.VRAM_WIDTH` x `psx.VRAM_HEIGHT`, and `game()` must name a serial --
whatever disc it is, the gate only asks that one is loaded. The fork is killed once `launch`
returns, whatever happens after; when `launch` raises, only if a DuckStation
pid appeared that was not there before -- a skipped run (no X server, no
image) never stops an emulator it did not open (CORR-DMCP-011).

Exit codes: 0 ok; 77 (`errors.SKIP`, ctest's *skipped*) with no image, no
fork or no X server, the reason printed; 1 when the fork failed, a read
raised (a VRAM file that does not decode included), or any of the four
conditions -- frames, RAM, VRAM, serial -- does not hold, the FAIL line
naming which. The last line is always `duckmcp_live: <ok|FAIL|skipped> ...`.
"""

import argparse
import os
import shutil
import sys
import tempfile

if __package__ in (None, ""):
    _HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path
                   if os.path.abspath(p or os.curdir) != _HERE]
    sys.path.insert(0, os.path.dirname(_HERE))

from duckmcp import env, fork, png, psx  # noqa: E402
from duckmcp.session import Session  # noqa: E402
from duckmcp.errors import (SKIP, Fail, NotRunning, Skip,  # noqa: E402
                            ToolError)

IMAGE_VARIABLE = "DUCKSTATION_TEST_IMAGE"
"""The variable naming the `.cue` of a working copy, when `--image` is absent."""

DEFAULT_STEPS = 5
"""How many `frame_step`s the gate takes; ~57 ms each over the wire."""


def frame_number(client):
    """`get_status`'s `frame_number`, which `frame_step` must move."""
    return client.call("get_status")["frame_number"]


def run(image, steps, display=None):
    """Launch, pause, count tools, step, compare; kill in `finally`.

    Returns `(failed, tools, before, after, reads)`: `failed` the names of
    the conditions that did not hold (`failures`), empty when the gate
    passes; `reads` the RAM length, the VRAM PNG size and the `Game` that
    `game()` answered.
    """
    running = set(fork.running_pids())
    try:
        _pid, _window, client = fork.launch(image, display=display)
    except BaseException:
        # A Fail can come after the Popen (no window in time), so a new pid
        # is ours to stop; none new means nothing was launched.
        if set(fork.running_pids()) - running:
            fork.kill(verbose=False)
        raise
    try:
        client.call("pause")
        names = client.tools()
        print("  tools declared: %d" % len(names), flush=True)
        before = frame_number(client)
        for _ in range(steps):
            client.call("frame_step")
        after = frame_number(client)
        print("  frame_number %d -> %d after %d frame_step"
              % (before, after, steps), flush=True)
        reads = read_back(Session(client=client))
        return (failures(steps, before, after, reads), len(names), before,
                after, reads)
    finally:
        fork.kill(verbose=False)


def failures(steps, before, after, reads):
    """The names of the gate's conditions that do not hold, in order."""
    failed = []
    if after - before != steps:
        failed.append("frames")
    if reads["ram"] != psx.RAM_SIZE:
        failed.append("ram")
    if reads["vram"] != (psx.VRAM_WIDTH, psx.VRAM_HEIGHT):
        failed.append("vram")
    if reads["game"].serial is None:
        failed.append("serial")
    return failed


def read_back(session):
    """Main RAM, all of VRAM and `game()`, through `Session`.

    The VRAM goes to a temporary PNG, decoded with `png.read_png` for its
    size only; the folder is removed whatever happens.
    """
    ram = len(session.read_ram(psx.RAM_BASE, psx.RAM_SIZE))
    print("  read_ram: %d bytes from %#x" % (ram, psx.RAM_BASE), flush=True)
    scratch = tempfile.mkdtemp(prefix="duckmcp-live-")
    try:
        width, height, _rows = png.read_png(
            session.dump_vram(os.path.join(scratch, "vram.png")))
    finally:
        shutil.rmtree(scratch, ignore_errors=True)
    print("  dump_vram: %dx%d" % (width, height), flush=True)
    game = session.game()
    print("  game(): serial=%r title=%r" % (game.serial, game.title),
          flush=True)
    return {"ram": ram, "vram": (width, height), "game": game}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--image", help="the .cue of a working copy "
                        "(default: $%s)" % IMAGE_VARIABLE)
    parser.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    parser.add_argument("--display", help="default: env.display()")
    args = parser.parse_args(argv)

    image = args.image or env.get(IMAGE_VARIABLE)
    if not image:
        print("duckmcp_live: skipped -- no image: set %s to the .cue of a "
              "working copy, or pass --image" % IMAGE_VARIABLE)
        return SKIP
    print("duckmcp_live: %s, %d steps" % (image, args.steps), flush=True)
    try:
        failed, tools, before, after, reads = run(image, args.steps,
                                                  args.display)
    except Skip as exc:
        print("duckmcp_live: skipped -- %s" % exc)
        return SKIP
    except (Fail, NotRunning, ToolError, ValueError) as exc:
        # ValueError: png.PngError when the VRAM file does not decode, and
        # the size refusals of Session.read_ram -- a verdict, not a traceback.
        print("duckmcp_live: FAIL -- %s: %s" % (type(exc).__name__, exc))
        return 1
    verdict = "FAIL (%s)" % ", ".join(failed) if failed else "ok"
    print("duckmcp_live: %s -- frame_number moved %d for %d frame_step "
          "(want %d); tools=%d frames %d->%d; ram=%d vram=%dx%d serial=%s"
          % (verdict, after - before, args.steps, args.steps, tools,
             before, after, reads["ram"], reads["vram"][0], reads["vram"][1],
             reads["game"].serial))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())

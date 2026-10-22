#!/usr/bin/env python3
"""Shim: the save-state reader moved to `tools/duckmcp/savestate.py`.

DMCP-TASK-14 moved the module whole into the duckmcp library. This file
re-exports it so `import savestate` from `tools/pes2/` (and the callers in
`tools/looks/` and `tools/kits/` that put `tools/pes2/` on the path) keep
working while phases 5 to 7 migrate them; the cycle's close deletes it.

The names are the library's own objects, not copies: `SaveState`, `BadState`
and `Skip` here are `duckmcp.savestate`'s, so an `except savestate.BadState`
catches what the library raises.

`self_check` keeps its old contract -- a list of failed labels, `verbose`
printing as it runs -- over the library's `(name, passed, detail)` triples.

    python3 tools/pes2/savestate.py info <state.sav>     # same CLI as before
"""

import os
import sys

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from duckmcp import savestate as _lib  # noqa: E402
from duckmcp.savestate import (  # noqa: E402,F401
    BUS_RAM_TO_DMA, BUS_TAG_TO_RAM, KERNEL_MARK, KERNEL_MARK_AT,
    KERNEL_WINDOW, MAGIC, PSX_RAM, STORED, ZSTD, BadState, SaveState, Skip,
    _HDR, _synth, _tag, _unzstd, cmd_diff, cmd_info, cmd_ram, cmd_read,
    cmd_scan, cmd_selftest, cmd_shot, diff, main, mask_address, scan)


def self_check(tmpdir=None, verbose=True):
    """The library's self-check, as the list of labels that failed.

    May raise `Skip`, as the original could.
    """
    results = _lib.self_check(tmpdir, verbose=verbose)
    return [name for name, passed, _ in results if not passed]


if __name__ == "__main__":
    sys.exit(main())

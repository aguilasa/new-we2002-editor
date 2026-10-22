#!/usr/bin/env python3
"""Shim: the MCP client moved to `tools/duckmcp/` (PLAN-DUCKMCP-PY §2).

Every name the importers of this module use is the lib's own object, not a
copy -- `except mcp.ToolError` catches what `duckmcp.client` raises because
they are the same class. This file goes away when the cycle closes (§2,
decision 2); new code imports `duckmcp` with `tools/` on `sys.path`.

    python3 tools/duckmcp/cli.py list|status|call TOOL k=v   # the new CLI
    python3 tools/pes2/mcp.py --list|--status|--call TOOL k=v  # still works
    python3 tools/pes2/mcp.py --self-check                     # no emulator

One measured exception to "only re-exports" (CORR-DMCP-004): importing this
module rebinds `duckmcp.client.process_alive` to a probe over
`fork.running_pids()`, so a refused port still says whether duckstation-qt is
alive, as the old `mcp.py --list` did. The rebinding is process-wide -- it
also changes `duckmcp.client` for code that imports the lib directly -- and
`self_check` carries the two checks of that probe. The lib cannot hold the
probe yet: it would import `tools/pes2/fork.py`, against rules (b) and (c) of
PLAN-DUCKMCP-PY §3.3. DMCP-TASK-08 brings `running_pids` into
`duckmcp.fork`; the probe and its two checks move there, and this exception
goes away with it.
"""

import functools
import importlib
import os
import sys

_TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _TOOLS not in sys.path:
    sys.path.insert(0, _TOOLS)

from duckmcp import cli, client, env  # noqa: E402
from duckmcp.client import PROTOCOL, Client  # noqa: E402,F401
from duckmcp.errors import (SKIP, NotRunning, SessionLost,  # noqa: E402,F401
                            ToolError)

DEFAULT_HOST = env.mcp_host()
DEFAULT_PORT = env.mcp_port()

# The liveness seam of duckmcp.client, filled from fork.py so a refused port
# still says whether duckstation-qt is alive. Temporary: DMCP-TASK-08 fills
# the seam inside the lib. Lazy because fork.py imports this module; an
# exception in the probe reads as "unknown" (Client._liveness catches it).
_LIB_PROBE = client.process_alive
client.process_alive = lambda: bool(
    importlib.import_module("fork").running_pids())


def self_check(verbose=True):
    """duckmcp.client.self_check(), plus the fork-backed probe wired above.

    Returns failure strings, empty when green -- the shape selftest.py reads.
    The lib's checks run against its own default probe, as they assume.
    """
    fork = importlib.import_module("fork")
    wired, real = client.process_alive, fork.running_pids
    client.process_alive = _LIB_PROBE
    try:
        results = list(client.self_check())
    finally:
        client.process_alive = wired
    for pids, want in (([], "no DuckStation process either"),
                       ([4242], "duckstation-qt IS running")):
        fork.running_pids = lambda pids=pids: pids
        try:
            Client(port=1, timeout=2.0).call("get_status")
            got = "it connected"
        except NotRunning as e:
            got = str(e)
        except Exception as e:                               # noqa: BLE001
            got = "%s: %s" % (type(e).__name__, e)
        finally:
            fork.running_pids = real
        results.append(("the shim's probe reads fork.running_pids() == %r"
                        % (pids,), want in got, got))
    bad = ["%s: %s" % (name, detail) if detail else name
           for name, passed, detail in results if not passed]
    if verbose:
        for name, passed, detail in results:
            print("  %s   %s" % ("ok" if passed else "FAIL", name)
                  + ("  (%s)" % (detail,) if detail and not passed else ""))
        print("SELF-CHECK " + ("FAILED" if bad else "OK: %d checks"
                               % len(results)))
    return bad


main = functools.partial(cli.legacy_main, self_check=self_check)

if __name__ == "__main__":
    sys.exit(main())

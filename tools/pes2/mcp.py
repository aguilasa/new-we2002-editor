#!/usr/bin/env python3
"""Shim: the MCP client moved to `tools/duckmcp/` (PLAN-DUCKMCP-PY §2).

Every name the importers of this module use is the lib's own object, not a
copy -- `except mcp.ToolError` catches what `duckmcp.client` raises because
they are the same class. This file goes away when the cycle closes (§2,
decision 2); new code imports `duckmcp` with `tools/` on `sys.path`.

    python3 tools/duckmcp/cli.py list|status|call TOOL k=v   # the new CLI
    python3 tools/pes2/mcp.py --list|--status|--call TOOL k=v  # still works
    python3 tools/pes2/mcp.py --self-check                     # no emulator

The liveness probe a refused port reads -- is duckstation-qt alive? --
lives in the lib since DMCP-TASK-08, over `duckmcp.fork.running_pids()`,
with its two checks in the lib's selftest; this shim no longer rebinds
anything in `duckmcp.client` (CORR-DMCP-004).
"""

import functools
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


def self_check(verbose=True):
    """duckmcp.client.self_check() in the shape selftest.py reads.

    Returns failure strings, empty when green.
    """
    results = list(client.self_check())
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

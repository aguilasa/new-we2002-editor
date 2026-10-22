"""The exceptions every duckmcp module raises, and the skip exit code.

One place for them, so a caller catches `duckmcp.NotRunning` no matter which
module noticed the emulator was down. A command line maps them to exit codes:
`Skip` to `SKIP` (ctest reads 77 as skipped), the rest to 1.
"""

# lineage: tools/pes2/fork.py (SKIP, Fail, Skip) and tools/pes2/mcp.py
# (NotRunning, ToolError, SessionLost) as of commit f21182ea.

SKIP = 77
"""The exit code ctest reads as *skipped* (`SKIP_RETURN_CODE`)."""


class Fail(Exception):
    """The launcher could not get to a running, answering emulator."""


class Skip(Exception):
    """This machine cannot run it; ctest should read it as skipped."""


class NotRunning(Exception):
    """No server answered. The message says what to do about it.

    This exists so that the commonest failure of the whole MCP path -- the
    emulator simply is not up -- reads as one sentence instead of as a
    `urllib.error.URLError` wrapping a `ConnectionRefusedError` wrapping an
    errno.
    """


class ToolError(Exception):
    """The server took the call and refused it, or the tool itself failed."""


class SessionLost(ToolError):
    """The server no longer knows our session id.

    **The fork keeps one MCP session, and the newest `initialize` wins.**
    Measured on 2026-10-22: a second client's handshake turns every later
    call of the first into `400 Bad Request: missing or invalid
    MCP-Session-Id`. The second client is usually not ours -- an editor's MCP
    configuration pointing at the same port connects on its own whenever the
    port opens, at a moment no caller can predict. The client answers it by
    handshaking again and resending once; the refused request never reached
    a tool, so resending is safe.
    """


def self_check() -> list:
    """The exit code and the hierarchy the callers rely on.

    Returns one `(name, passed, detail)` per assertion.
    """
    distinct = (Fail, Skip, NotRunning, ToolError)
    results = [
        ("SKIP is 77", SKIP == 77, "got %r" % (SKIP,)),
        ("SessionLost is a ToolError", issubclass(SessionLost, ToolError), ""),
    ]
    for cls in distinct:
        results.append(("%s is an Exception" % cls.__name__,
                        issubclass(cls, Exception), ""))
    crossed = [(a.__name__, b.__name__) for a in distinct for b in distinct
               if a is not b and issubclass(a, b)]
    results.append(("Fail, Skip, NotRunning and ToolError are unrelated",
                    not crossed, crossed))
    return results

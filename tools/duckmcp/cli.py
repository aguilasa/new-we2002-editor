#!/usr/bin/env python3
"""The command line of duckmcp: ask the fork's MCP server one thing.

    python3 tools/duckmcp/cli.py list               # the tools the server declares
    python3 tools/duckmcp/cli.py status             # get_status, detail="full"
    python3 tools/duckmcp/cli.py call TOOL k=v ...  # one tool; values JSON when they parse
    python3 tools/duckmcp/cli.py ping               # the handshake alone

and the fork's process, which needs no server:

    python3 tools/duckmcp/cli.py launch COPY.cue [--display :98]
                                 [--timeout 120] [--match REGEX]
    python3 tools/duckmcp/cli.py kill               # every DuckStation
    python3 tools/duckmcp/cli.py procs              # `pids: [...]`, and which binary
    python3 tools/duckmcp/cli.py recipe             # how to get the fork
    python3 tools/duckmcp/cli.py which              # the binary; 77 when absent

`status` is the server's `get_status`; what is *running* is `procs`, a
different name so the two never mean each other. `launch` prints
`PID=`, `WINDOW=`, `DISPLAY=` (not on Windows) and `MCP=` and leaves the
fork running; `--match` is the caller's regex over the window title, and
without it the widest window the child owns that is not an emulator dialog
is taken (`fork.pick_window`).

`--host` and `--port` go before the subcommand and default to
`env.mcp_host()` and `env.mcp_port()`. Exit codes: 0 when the server
answered (or the process command did its work), 77 (`errors.SKIP`, ctest's
*skipped*) when no server answered -- the `NotRunning` sentence goes to
stderr -- or the machine cannot run the fork (`Skip`: no install, no
image, no X server), 1 when the server refused the call (`ToolError`) or
the fork failed (`Fail`), 2 for a bad command line.

Run it as a script or import it as `duckmcp.cli`. As a script it puts
`tools/` -- the parent of this folder -- on `sys.path` and takes this folder
off it, so this `cli.py` never shadows another project's.
"""

# lineage: the --list/--status/--call entry point of tools/pes2/mcp.py as of
# commit f21182ea; `legacy_argv` keeps its flags alive for the shim.

import argparse
import json
import os
import sys

if __package__ in (None, ""):
    _HERE = os.path.dirname(os.path.abspath(__file__))
    sys.path[:] = [p for p in sys.path
                   if os.path.abspath(p or os.curdir) != _HERE]
    sys.path.insert(0, os.path.dirname(_HERE))

from duckmcp import env, fork  # noqa: E402
from duckmcp.client import Client, self_check as client_self_check  # noqa: E402
from duckmcp.errors import SKIP, Fail, NotRunning, Skip, ToolError  # noqa: E402

SERVER_COMMANDS = ("ping", "list", "status", "call")
"""The subcommands that talk to the MCP server."""

PROCESS_COMMANDS = ("launch", "kill", "procs", "recipe", "which")
"""The subcommands that act on the fork's process and need no server."""

SUBCOMMANDS = SERVER_COMMANDS + PROCESS_COMMANDS
"""What the parser accepts."""


def parse_value(text):
    """A `key=value` value: the JSON it spells, or the string itself."""
    try:
        return json.loads(text)
    except ValueError:
        return text


def parse_pairs(pairs):
    """`["a=1", 'b="x"']` -> `{"a": 1, "b": "x"}`; a pair without `=` is
    refused, because silently sending `{"a": ""}` hides a typo."""
    out = {}
    for pair in pairs:
        key, sep, value = pair.partition("=")
        if not sep or not key:
            raise ValueError("argument %r is not KEY=VALUE" % (pair,))
        out[key] = parse_value(value)
    return out


def build_parser():
    ap = argparse.ArgumentParser(
        prog="cli.py", description=__doc__.splitlines()[0])
    ap.add_argument("--host", default=None,
                    help="server host (default: env.mcp_host())")
    ap.add_argument("--port", type=int, default=None,
                    help="server port (default: env.mcp_port())")
    ap.add_argument("--timeout", type=float, default=30.0)
    sub = ap.add_subparsers(dest="command", metavar="COMMAND")
    sub.required = True
    sub.add_parser("ping", help="handshake and print the server line")
    sub.add_parser("list", help="the tool names the server declares")
    sub.add_parser("status", help='get_status with detail="full"')
    call = sub.add_parser("call", help="call one tool")
    call.add_argument("tool")
    call.add_argument("pairs", nargs="*", metavar="KEY=VALUE")
    launch = sub.add_parser("launch", help="boot a .cue under the fork, "
                            "dismiss its dialogs, wait for MCP")
    launch.add_argument("image", help=".cue of a working copy")
    launch.add_argument("--display", default=None,
                        help="X display (default: env.display())")
    # Its own dest: the top-level --timeout is the client's, in seconds per
    # request, and a subparser default would overwrite it.
    launch.add_argument("--timeout", dest="launch_timeout", type=int,
                        default=120, help="seconds for the whole boot")
    launch.add_argument("--match", default=None, metavar="REGEX",
                        help="regex over the window title (default: the "
                             "widest non-dialog window; ANY means the same)")
    sub.add_parser("kill", help="stop every DuckStation process")
    sub.add_parser("procs", help="the DuckStation processes running, as "
                                 "`pids: [...]`, and which binary each is")
    sub.add_parser("recipe", help="how to get the fork")
    sub.add_parser("which", help="the fork's binary; exit 77 when absent")
    return ap


def parse(argv):
    """The parsed command line, with `call`'s pairs already decoded into
    `args.arguments`. Pure: talks to nothing. Raises `SystemExit(2)` on a
    bad line, like argparse."""
    ap = build_parser()
    args = ap.parse_args(argv)
    args.arguments = {}
    if args.command == "call":
        try:
            args.arguments = parse_pairs(args.pairs)
        except ValueError as exc:
            ap.error(str(exc))
    return args


def run_process(args, out=None):
    """Carry out one of `PROCESS_COMMANDS`. Returns the exit code."""
    out = out or sys.stdout
    try:
        if args.command == "recipe":
            print(fork.RECIPE, file=out)
            return 0
        if args.command == "which":
            print(fork.binary(), file=out)
            print("installed" if fork.installed() else "NOT INSTALLED",
                  file=out)
            return 0 if fork.installed() else SKIP
        if args.command == "kill":
            fork.kill()
            return 0
        if args.command == "procs":
            print("pids: %s" % (fork.running_pids(),), file=out)
            fork.status()
            return 0
        display = args.display or env.display()
        pid, window, client = fork.launch(
            args.image, match=args.match, display=display,
            timeout=args.launch_timeout)
        print("PID=%s" % pid, file=out)
        print("WINDOW=%s" % window, file=out)
        if not fork.WINDOWS:
            print("DISPLAY=%s" % display, file=out)
        print("MCP=%s" % client.url, file=out)
        return 0
    except Skip as exc:
        print("skipping: %s" % exc, file=out)
        return SKIP
    except Fail as exc:
        print("FORK FAILED: %s" % exc, file=sys.stderr)
        return 1


def run(args, out=None):
    """Carry out a parsed command. Returns the exit code."""
    if args.command in PROCESS_COMMANDS:
        return run_process(args, out)
    out = out or sys.stdout
    try:
        with Client(args.host, args.port, timeout=args.timeout) as c:
            print("%s %s on %s  session %s"
                  % (c.server.get("name"), c.server.get("version"), c.url,
                     c.session), file=out)
            if args.command == "list":
                names = c.tools()
                print("%d tools" % len(names), file=out)
                for name in names:
                    print("  %s" % name, file=out)
            elif args.command == "status":
                print(json.dumps(c.call("get_status", detail="full"),
                                 indent=2), file=out)
            elif args.command == "call":
                print(json.dumps(c.call(args.tool, **args.arguments),
                                 indent=2), file=out)
        return 0
    except NotRunning as exc:
        print("skipping: %s" % exc, file=sys.stderr)
        return SKIP
    except ToolError as exc:
        print("MCP FAILED: %s" % exc, file=sys.stderr)
        return 1


def main(argv=None):
    return run(parse(argv))


# --- the old flag interface, for the shim that keeps it alive -------------

def legacy_argv(argv):
    """The old `--list --status --call TOOL k=v` flags as subcommand lines.

    Returns `(lines, self_check)`: one argv per requested action, in the
    old order (list, status, call), each carrying `--host`/`--port`; and
    whether `--self-check` was asked. No action at all is a `ping`, which is
    what the old entry point did with no flag.
    """
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--host")
    ap.add_argument("--port")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--call", metavar="TOOL")
    ap.add_argument("--self-check", action="store_true")
    ap.add_argument("pairs", nargs="*")
    args = ap.parse_args(argv)
    common = []
    if args.host is not None:
        common += ["--host", args.host]
    if args.port is not None:
        common += ["--port", args.port]
    lines = []
    if args.list:
        lines.append(common + ["list"])
    if args.status:
        lines.append(common + ["status"])
    if args.call:
        lines.append(common + ["call", args.call] + args.pairs)
    if not lines:
        lines.append(common + ["ping"])
    return lines, args.self_check


def legacy_main(argv=None, self_check=None):
    """The old flags, run through `main`. `self_check` is the callable
    `--self-check` runs (failures out, empty when green); None runs the
    client's own. The first non-zero exit stops the run."""
    lines, check = legacy_argv(sys.argv[1:] if argv is None else argv)
    if check:
        if self_check is None:
            failed = [r for r in client_self_check() if not r[1]]
            for name, _, detail in failed:
                print("  FAIL  %s  %s" % (name, detail))
            print("SELF-CHECK " + ("FAILED" if failed else "OK"))
            return 1 if failed else 0
        return 1 if self_check() else 0
    for line in lines:
        code = main(line)
        if code:
            return code
    return 0


def self_check() -> list:
    """The parsing, with no server: what `call` sends and the old flags.

    Returns one `(name, passed, detail)` per assertion.
    """
    results = []

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    args = parse(["call", "frame_step", "a=1", 'b="x"', "c=word",
                  "d=[1, 2]", "e=true"])
    want = {"a": 1, "b": "x", "c": "word", "d": [1, 2], "e": True}
    check("call TOOL k=v decodes the values as JSON when they parse",
          (args.tool, args.arguments) == ("frame_step", want),
          (args.tool, args.arguments))
    args = parse(["--port", "1", "list"])
    check("--host/--port go before the subcommand",
          (args.command, args.port, args.host) == ("list", 1, None),
          (args.command, args.port, args.host))
    try:
        parse_pairs(["novalue"])
        check("a pair without '=' is refused", False, "it was accepted")
    except ValueError:
        check("a pair without '=' is refused", True)
    lines, chk = legacy_argv(["--port", "1", "--list", "--call", "pause",
                              "x=2"])
    check("the old flags become subcommand lines, in the old order",
          lines == [["--port", "1", "list"],
                    ["--port", "1", "call", "pause", "x=2"]] and not chk,
          lines)
    lines, chk = legacy_argv(["--self-check"])
    check("no old action is a ping, and --self-check is seen",
          lines == [["ping"]] and chk, (lines, chk))
    args = parse(["--timeout", "5", "launch", "x.cue", "--timeout", "9",
                  "--match", "^T$"])
    check("launch keeps its boot timeout apart from the client's",
          (args.timeout, args.launch_timeout, args.match, args.display)
          == (5.0, 9, "^T$", None),
          (args.timeout, args.launch_timeout, args.match, args.display))
    args = parse(["launch", "x.cue"])
    check("launch has no default title (--match None)", args.match is None,
          args.match)
    check("process commands and server commands do not share a name",
          not set(SERVER_COMMANDS) & set(PROCESS_COMMANDS))
    import io as _io
    buf = _io.StringIO()
    code = run(parse(["recipe"]), out=buf)
    check("recipe prints the fork's recipe and exits 0",
          code == 0 and buf.getvalue().strip() == fork.RECIPE.strip(), code)
    import contextlib
    buf = _io.StringIO()
    with contextlib.redirect_stderr(_io.StringIO()) as err:
        code = run(parse(["launch", "/x/roms/a.cue"]), out=buf)
    check("launch of a roms/ path exits 1 (Fail), before any boot",
          code == 1 and "roms/" in err.getvalue(), (code, err.getvalue()))
    check("the default host and port come from env.py",
          build_parser().parse_args(["list"]).port is None
          and Client().port == env.mcp_port())
    return results


if __name__ == "__main__":
    sys.exit(main())

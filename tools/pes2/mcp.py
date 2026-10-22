#!/usr/bin/env python3
"""A small MCP client for the DuckStation fork's server, in stdlib only.

The fork `sadnescity/duckstation`, branch `mcp`, runs an MCP server inside
the emulator on `127.0.0.1:2346`. What it buys this project is one thing the
`xdotool` driver could never have: **the emulator can be stopped between one
button and the next**. `pause` plus `frame_step` turns "five presses moved
five rows, probably" into an assertion.

This is the transport half. `fork.py` starts the emulator, `mcp_drive.py`
writes routes on top of both.

    from mcp import Client
    with Client() as c:
        c.call("pause")
        c.call("press_button", button="Down", duration_frames=2)
        for _ in range(12):
            c.call("frame_step")

Protocol, measured against `duckstation-mcp` 1.0.0 on 2026-09-03: Streamable
HTTP, protocol version `2025-11-25`, one POST per JSON-RPC message, and a
session id handed back in the `MCP-Session-Id` **response header** of
`initialize` that every later request must echo. A result arrives as
`result.content[0].text` holding a JSON *document* -- the tools answer in
text, not in structured content, so the payload is parsed a second time.

    python3 tools/pes2/mcp.py --list        # the tools the server declares
    python3 tools/pes2/mcp.py --self-check  # no emulator needed
"""

import argparse
import json
import os
import socket
import sys
import urllib.error
import urllib.request

SKIP = 77

DEFAULT_HOST = os.environ.get("PES2_MCP_HOST", "127.0.0.1")
DEFAULT_PORT = int(os.environ.get("PES2_MCP_PORT", "2346"))

# The version the fork answers with. Sending a different one is not an error
# -- the server replied with its own either way -- but pinning what was
# measured means a change shows up as a mismatch instead of as odd behaviour.
PROTOCOL = "2025-11-25"


class NotRunning(Exception):
    """No server answered. The message says what to do about it.

    This exists so that the commonest failure of the whole MCP path -- the
    emulator simply is not up -- reads as one sentence instead of as a
    `urllib.error.URLError` wrapping a `ConnectionRefusedError` wrapping an
    errno, which is what every draft of this printed.
    """


class ToolError(Exception):
    """The server took the call and refused it, or the tool itself failed."""


class SessionLost(ToolError):
    """The server no longer knows our session id.

    **The fork keeps one MCP session, and the newest `initialize` wins.**
    Measured on 2026-10-22: a second client's handshake turns every later
    call of the first into `400 Bad Request: missing or invalid
    MCP-Session-Id`. The second client is usually not ours -- the project's
    `.mcp.json` points Claude Code at the same port, and it connects on its
    own whenever the port opens, at a moment no route can predict. That is
    what made a route fail one run in three, mid-replay, with the emulator
    alive. `Client.call` answers it by handshaking again and resending once;
    the refused request never reached a tool, so resending is safe.
    """


class Client:
    """One MCP session against the emulator.

    Use it as a context manager. `initialize` is done lazily on the first
    call so that constructing a client cannot fail; that matters because a
    tool's `--self-check` builds one to look at its shape without an
    emulator anywhere.
    """

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, timeout=30.0,
                 name="pes2-tools", reclaim=True):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.name = name
        self.url = f"http://{host}:{port}/mcp"
        self.session = None
        self.server = None
        self._id = 0
        self.reclaim = reclaim       # handshake again when the session is taken
        self.reclaimed = 0

    # -- context manager --

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, *exc):
        return False

    # -- transport --

    def _post(self, payload, expect_reply=True):
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            # Both, and in this order: the server may answer either as a
            # plain JSON body or as a one-event SSE stream depending on the
            # call, and refusing one of them is a 406 that looks like a
            # protocol error.
            "Accept": "application/json, text/event-stream",
        }
        if self.session:
            headers["MCP-Session-Id"] = self.session
        request = urllib.request.Request(self.url, data=body, headers=headers,
                                         method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as r:
                raw = r.read().decode("utf-8", "replace")
                sid = r.headers.get("MCP-Session-Id")
                if sid and not self.session:
                    self.session = sid
        except urllib.error.HTTPError as e:                  # pragma: no cover
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code == 400 and "MCP-Session-Id" in detail and self.session:
                raise SessionLost(f"HTTP 400 from the server: {detail}") \
                    from None
            raise ToolError(f"HTTP {e.code} from the server: {detail}") from None
        except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
            # "The fork is not running" is true either way and useless in one
            # of the two cases. The fork dies on its own during free
            # execution (pitfall 35), and when it does every tool printed the
            # sentence that describes *forgetting to launch it* -- which cost
            # three wrong readings in one review before a `pgrep` showed the
            # process had simply gone. Ask, since `fork.py` already knows how.
            try:
                import fork
                alive = bool(fork.running_pids())
            except Exception:                            # noqa: BLE001
                alive = None
            if alive:
                raise NotRunning(
                    f"no MCP server at {self.url} -- but duckstation-qt IS "
                    f"running. The emulator is up and the server is not "
                    f"answering: it was started without EnableMCPServer, or "
                    f"it is on another port. [{type(e).__name__}]") from None
            if alive is False:
                raise NotRunning(
                    f"no MCP server at {self.url} -- and no DuckStation "
                    f"process either. It was never started, or it died "
                    f"mid-run (pitfall 35 of section 6.11: the fork dies "
                    f"silently during free execution). Start it with "
                    f"tools/pes2/fork.py launch (the official AppImage has "
                    f"no MCP server). [{type(e).__name__}]") from None
            raise NotRunning(
                f"no MCP server at {self.url} -- the DuckStation fork is not "
                f"running. Start it with tools/pes2/fork.py launch "
                f"(the official AppImage has no MCP server). "
                f"[{type(e).__name__}]") from None
        if not expect_reply:
            return None
        return _decode(raw)

    def _next_id(self):
        self._id += 1
        return self._id

    # -- protocol --

    def initialize(self):
        """Handshake, and remember the session id. Idempotent."""
        if self.server is not None:
            return self.server
        reply = self._post({
            "jsonrpc": "2.0", "id": self._next_id(), "method": "initialize",
            "params": {
                "protocolVersion": PROTOCOL,
                "capabilities": {},
                "clientInfo": {"name": self.name, "version": "1"},
            },
        })
        result = _result(reply)
        # Without this notification the server is within its rights to
        # refuse every later call; it costs one request and no reply.
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"},
                   expect_reply=False)
        self.server = result.get("serverInfo", {})
        return self.server

    def tools(self):
        """The tool names the server actually declares.

        **Count them here, not in the source.** The fork's static
        `TOOLS_JSON` lists 99 names and four of them -- `analyze_memory`,
        `debug_crash`, `inspect_gpu`, `trace_function` -- never reach
        `tools/list`. Measured 95 on 2026-09-03.
        """
        self.initialize()
        reply = self._post({"jsonrpc": "2.0", "id": self._next_id(),
                            "method": "tools/list"})
        return [t["name"] for t in _result(reply).get("tools", [])]

    def call(self, name, **arguments):
        """Call one tool and return its payload, already parsed.

        A tool answers with `content[0].text` holding a JSON document. When
        that text is not JSON -- some tools answer in prose -- the string is
        returned as-is rather than raising, because a caller that wanted a
        number will fail on the string and say so more usefully than a
        decoder would.
        """
        self.initialize()
        request = {"jsonrpc": "2.0", "method": "tools/call",
                   "params": {"name": name, "arguments": arguments}}
        try:
            reply = self._post(dict(request, id=self._next_id()))
        except SessionLost:
            if not self.reclaim:
                raise
            # Another client took the session -- see SessionLost. Take it
            # back and resend; a second loss in a row is a real failure.
            self.session = self.server = None
            self.initialize()
            self.reclaimed += 1
            reply = self._post(dict(request, id=self._next_id()))
        result = _result(reply, tool=name)
        if result.get("isError"):
            raise ToolError(f"{name}: {_text_of(result)}")
        text = _text_of(result)
        if text is None:
            return result
        try:
            return json.loads(text)
        except (ValueError, TypeError):
            return text


# --- decoding ----------------------------------------------------------

def _decode(raw):
    """One reply body, whether it arrived as JSON or as a single SSE event."""
    raw = raw.strip()
    if not raw:
        return {}
    if raw.startswith("{"):
        return json.loads(raw)
    # Streamable HTTP may answer as text/event-stream. Take the last data:
    # line that parses -- a stream can carry pings before the payload.
    payload = None
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("data:"):
            continue
        try:
            payload = json.loads(line[5:].strip())
        except ValueError:
            continue
    if payload is None:
        raise ToolError(f"could not decode a reply: {raw[:200]!r}")
    return payload


def _result(reply, tool=None):
    where = f"{tool}: " if tool else ""
    if "error" in reply:
        err = reply["error"]
        raise ToolError(f"{where}{err.get('message', err)} "
                        f"(code {err.get('code')})")
    if "result" not in reply:
        raise ToolError(f"{where}reply had no result: {str(reply)[:200]}")
    return reply["result"]


def _text_of(result):
    for item in result.get("content", []):
        if item.get("type") == "text":
            return item.get("text")
    return None


# --- self-check --------------------------------------------------------

class _OneSessionServer:
    """A loopback stand-in for the fork's session rule, for the self-check.

    Each `initialize` mints a new id and forgets the previous one; any
    other request carrying a stale id gets the fork's own 400. Everything
    else answers `{"ok": 1}`.
    """

    def __enter__(self):
        import http.server
        import threading
        state = {"sid": None, "n": 0}

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def do_POST(self):
                body = json.loads(self.rfile.read(
                    int(self.headers.get("Content-Length", 0))))
                if body.get("method") == "initialize":
                    state["n"] += 1
                    state["sid"] = f"s{state['n']}"
                    out = {"jsonrpc": "2.0", "id": body["id"],
                           "result": {"serverInfo": {"name": "stand-in"}}}
                    self.send_response(200)
                    self.send_header("MCP-Session-Id", state["sid"])
                elif self.headers.get("MCP-Session-Id") != state["sid"]:
                    self.send_response(400)
                    self.end_headers()
                    self.wfile.write(b'{"jsonrpc":"2.0","error":{"code":'
                                     b'-32600,"message":"Bad Request: missing'
                                     b' or invalid MCP-Session-Id"}}')
                    return
                elif "id" not in body:
                    self.send_response(202)
                    self.end_headers()
                    return
                else:
                    out = {"jsonrpc": "2.0", "id": body["id"], "result": {
                        "content": [{"type": "text", "text": '{"ok": 1}'}]}}
                    self.send_response(200)
                data = json.dumps(out).encode()
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

        self._httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()
        return self._httpd.server_address[1]

    def __exit__(self, *exc):
        self._httpd.shutdown()
        self._httpd.server_close()
        return False


def self_check(verbose=True):
    """Exercise the decoding and the red cases with no emulator in sight.

    Returns a list of failures, empty when all is well -- the shape
    `selftest.py` expects.
    """
    bad = []

    def check(what, ok, detail=""):
        if verbose:
            print(f"  {'ok' if ok else 'FAIL'}   {what}"
                  + (f"  ({detail})" if detail and not ok else ""))
        if not ok:
            bad.append(f"{what}{': ' + detail if detail else ''}")

    # Plain JSON and single-event SSE must decode to the same thing.
    doc = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    check("a plain JSON body decodes", _decode(json.dumps(doc)) == doc)
    sse = f"event: message\ndata: {json.dumps(doc)}\n\n"
    check("a one-event SSE body decodes the same", _decode(sse) == doc)
    check("an empty body is empty, not a crash", _decode("  ") == {})

    # An error reply must raise with the server's own message in it, not
    # return a half-result the caller then indexes into.
    err = {"jsonrpc": "2.0", "id": 1,
           "error": {"code": -32601, "message": "no such tool"}}
    try:
        _result(err, tool="nope")
        check("an error reply raises", False, "it returned instead")
    except ToolError as e:
        check("an error reply raises with the message", "no such tool" in str(e),
              str(e))

    try:
        _result({"jsonrpc": "2.0", "id": 1})
        check("a reply with no result raises", False, "it returned instead")
    except ToolError:
        check("a reply with no result raises", True)

    try:
        _decode("not json at all")
        check("an undecodable body raises", False, "it returned instead")
    except ToolError:
        check("an undecodable body raises", True)

    # The text payload is pulled out of content[], and non-JSON text comes
    # back as text rather than exploding.
    payload = {"content": [{"type": "text", "text": '{"a": 1}'}]}
    check("the text payload is found", _text_of(payload) == '{"a": 1}')
    check("no text content is None", _text_of({"content": []}) is None)

    # **The red case that matters**: a port nobody listens on must say the
    # fork is not running, not raise a URLError. Port 1 is reserved and
    # refuses instantly.
    #
    # And it must say *which* of the two silences it is, because they call
    # for opposite actions: launch the emulator, or work out why a live one
    # stopped answering. Both branches are driven here by standing in for
    # `fork.running_pids`, so neither is a promise -- and the branch that
    # matters most is the one nobody would think to test, since the fork
    # dying mid-run reads exactly like never having launched it.
    def _absent(pids, want, label):
        import fork as _fork
        real = _fork.running_pids
        _fork.running_pids = lambda: pids
        try:
            Client(port=1, timeout=2.0).call("get_status")
            check(label, False, "it connected")
        except NotRunning as e:
            msg = str(e)
            check(label, all(w in msg for w in want), msg)
        except Exception as e:                               # noqa: BLE001
            check(label, False, f"{type(e).__name__}: {e}")
        finally:
            _fork.running_pids = real

    _absent([], ["no DuckStation process either", "pitfall 35", "fork.py"],
            "an absent server with no process names the crash and the launcher")
    _absent([4242], ["duckstation-qt IS running", "not answering"],
            "an absent server with a live process says the server is the problem")

    # **One session, newest handshake wins** -- the fork's behaviour, played
    # by a local stand-in so it runs with no emulator. Client A is robbed by
    # client B mid-run; with `reclaim` it gets the session back and the call
    # goes through, and the red case is the same call with `reclaim` off,
    # which has to fail with SessionLost.
    with _OneSessionServer() as port:
        a = Client(port=port, timeout=5.0)
        check("the stand-in answers a call", a.call("get_status") == {"ok": 1})
        Client(port=port, timeout=5.0).initialize()
        try:
            check("a robbed session is taken back and the call goes through",
                  a.call("get_status") == {"ok": 1} and a.reclaimed == 1,
                  f"reclaimed {a.reclaimed}")
        except Exception as e:                           # noqa: BLE001
            check("a robbed session is taken back and the call goes through",
                  False, f"{type(e).__name__}: {e}")
        c = Client(port=port, timeout=5.0, reclaim=False)
        c.call("get_status")
        Client(port=port, timeout=5.0).initialize()
        try:
            c.call("get_status")
            check("without reclaim a robbed session fails", False,
                  "the call went through")
        except SessionLost:
            check("without reclaim a robbed session fails", True)

    # Constructing a client must not talk to anything -- tools build one to
    # look at its shape on machines with no emulator.
    check("constructing a client is inert",
          Client(port=1).session is None and Client(port=1).server is None)

    if verbose:
        print("SELF-CHECK " + ("FAILED" if bad else "OK: decoding, errors, "
                               "the absent-server message, the stolen session"))
    return bad


# --- entry point -------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default=DEFAULT_HOST)
    ap.add_argument("--port", type=int, default=DEFAULT_PORT)
    ap.add_argument("--list", action="store_true",
                    help="the tool names the server declares")
    ap.add_argument("--status", action="store_true",
                    help="get_status, as a sanity ping")
    ap.add_argument("--call", metavar="TOOL",
                    help="call one tool; arguments as KEY=VALUE after it")
    ap.add_argument("args", nargs="*", metavar="KEY=VALUE")
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return 1 if self_check() else 0

    try:
        with Client(args.host, args.port) as c:
            print(f"{c.server.get('name')} {c.server.get('version')} "
                  f"on {c.url}  session {c.session}")
            if args.list:
                names = c.tools()
                print(f"{len(names)} tools")
                for n in names:
                    print(f"  {n}")
            if args.status:
                print(json.dumps(c.call("get_status", detail="full"),
                                 indent=2))
            if args.call:
                kw = {}
                for pair in args.args:
                    k, _, v = pair.partition("=")
                    try:
                        kw[k] = json.loads(v)
                    except ValueError:
                        kw[k] = v
                print(json.dumps(c.call(args.call, **kw), indent=2))
        return 0
    except NotRunning as e:
        print(f"skipping: {e}", file=sys.stderr)
        return SKIP
    except ToolError as e:
        print(f"MCP FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

"""A small MCP client for the DuckStation fork's server, in stdlib only.

The fork `sadnescity/duckstation`, branch `mcp`, runs an MCP server inside
the emulator on `127.0.0.1:2346`. What it buys is one thing a keystroke
driver never had: **the emulator can be stopped between one button and the
next**. `pause` plus `frame_step` turns "five presses moved five rows,
probably" into an assertion.

This is the transport half: launching the emulator and the higher-level
session live in other modules of this package.

    from duckmcp.client import Client
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

Host and port default to `env.mcp_host()` and `env.mcp_port()`, read when a
client is built, never at import (rule (d) of PLAN-DUCKMCP-PY.md section 3.3).
"""

import json
import socket
import urllib.error
import urllib.request

from . import env
from .errors import NotRunning, SessionLost, ToolError

# lineage: tools/pes2/mcp.py as of commit f21182ea (Client, _decode,
# _result, _text_of, _OneSessionServer and the cases of mcp.self_check).

PROTOCOL = "2025-11-25"
"""The protocol version the fork answers with.

Sending a different one is not an error -- the server replies with its own
either way -- but pinning what was measured means a change shows up as a
mismatch instead of as odd behaviour.
"""

PLAN = "PLAN-DUCKMCP-PY §1.3"
"""Where the emulator pitfalls the messages cite are written down."""


def process_alive():
    """Whether a DuckStation process is running: True, False, or None.

    **The seam for the liveness probe**, filled by `duckmcp.fork`: True when
    `fork.running_pids()` lists a process, False when it lists none, and
    None -- *unknown*, the message that does not guess -- when the listing
    itself fails. The import is lazy because `fork` imports this module, and
    `fork.running_pids` is looked up at each call, so the client reads the
    process table at the moment the port is refused. A caller that knows
    better passes `Client(alive=...)`.
    """
    try:
        from . import fork
        return bool(fork.running_pids())
    except Exception:                                        # noqa: BLE001
        return None


class Client:
    """One MCP session against the emulator.

    Use it as a context manager. `initialize` is done lazily on the first
    call so that constructing a client cannot fail; that matters because a
    tool's self-check builds one to look at its shape without an emulator
    anywhere.

    `alive` is a callable answering like `process_alive`; None means the
    module-level `process_alive`. `reclaim` handshakes again, once, when
    another client took the session (pitfall 46).
    """

    def __init__(self, host=None, port=None, timeout=30.0, name="duckmcp",
                 reclaim=True, alive=None):
        self.host = env.mcp_host() if host is None else host
        self.port = env.mcp_port() if port is None else port
        self.timeout = timeout
        self.name = name
        self.url = "http://%s:%s/mcp" % (self.host, self.port)
        self.session = None
        self.server = None
        self._id = 0
        self.reclaim = reclaim       # handshake again when the session is taken
        self.reclaimed = 0
        self.alive = alive

    # -- context manager --

    def __enter__(self):
        self.initialize()
        return self

    def __exit__(self, *exc):
        return False

    # -- transport --

    def _liveness(self):
        """The probe's answer, or None when it cannot say."""
        probe = self.alive if self.alive is not None else process_alive
        try:
            answer = probe()
        except Exception:                                    # noqa: BLE001
            return None
        return None if answer is None else bool(answer)

    def _absent(self, exc):
        """The NotRunning for a refused port, saying which silence it is.

        "The fork is not running" is true either way and useless in one of
        the two cases. The fork dies on its own during free execution
        (pitfall 35), and when it did every tool printed the sentence that
        describes *forgetting to launch it*.
        """
        kind = type(exc).__name__
        alive = self._liveness()
        if alive:
            return NotRunning(
                "no MCP server at %s -- but duckstation-qt IS running. The "
                "emulator is up and the server is not answering: it was "
                "started without EnableMCPServer, or it is on another port. "
                "[%s]" % (self.url, kind))
        if alive is False:
            return NotRunning(
                "no MCP server at %s -- and no DuckStation process either. It "
                "was never started, or it died mid-run (%s, pitfall 35: the "
                "fork dies silently during free execution). Start the MCP "
                "fork (the official AppImage has no MCP server). [%s]"
                % (self.url, PLAN, kind))
        return NotRunning(
            "no MCP server at %s -- the DuckStation fork is not running, or "
            "it died mid-run (%s, pitfall 35). Start the MCP fork (the "
            "official AppImage has no MCP server). [%s]"
            % (self.url, PLAN, kind))

    def _post(self, payload, expect_reply=True):
        body = json.dumps(payload).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            # Both, and in this order: the server may answer either as a
            # plain JSON body or as a one-event SSE stream depending on the
            # call, and refusing one of them is a 406 that reads like a
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
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "replace")[:400]
            if e.code == 400 and "MCP-Session-Id" in detail and self.session:
                raise SessionLost(
                    "HTTP 400 from the server: %s (%s, pitfall 46: another "
                    "client's handshake took the session)" % (detail, PLAN)) \
                    from None
            raise ToolError("HTTP %d from the server: %s"
                            % (e.code, detail)) from None
        except (urllib.error.URLError, socket.timeout, ConnectionError) as e:
            raise self._absent(e) from None
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

        A stolen session (`SessionLost`, pitfall 46) is taken back once and
        the request resent; the refused request never reached a tool, so
        resending is safe. A second loss in a row raises.
        """
        self.initialize()
        request = {"jsonrpc": "2.0", "method": "tools/call",
                   "params": {"name": name, "arguments": arguments}}
        try:
            reply = self._post(dict(request, id=self._next_id()))
        except SessionLost:
            if not self.reclaim:
                raise
            self.session = self.server = None
            self.initialize()
            self.reclaimed += 1
            reply = self._post(dict(request, id=self._next_id()))
        result = _result(reply, tool=name)
        if result.get("isError"):
            raise ToolError("%s: %s" % (name, _text_of(result)))
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
        raise ToolError("could not decode a reply: %r" % (raw[:200],))
    return payload


def _result(reply, tool=None):
    where = "%s: " % tool if tool else ""
    if "error" in reply:
        err = reply["error"]
        raise ToolError("%s%s (code %s)" % (where, err.get("message", err),
                                            err.get("code")))
    if "result" not in reply:
        raise ToolError("%sreply had no result: %s" % (where, str(reply)[:200]))
    return reply["result"]


def _text_of(result):
    for item in result.get("content", []):
        if item.get("type") == "text":
            return item.get("text")
    return None


# --- self-check --------------------------------------------------------

class _OneSessionServer:
    """A loopback stand-in for the fork's session rule, for the self-check.

    Each `initialize` mints a new id and forgets the previous one; any other
    request carrying a stale id gets the fork's own 400. A `tools/call`
    answers `{"ok": 1}`, except: tool `sse` answers the same as a one-event
    SSE stream, tool `fail` answers a JSON-RPC error, tool `crash` an HTTP
    500. While `steal` is above zero, each `tools/call` first plays a rival
    client's handshake -- the session moves on -- and is refused.

    `handshakes` counts the `initialize` requests it answered.
    """

    def __init__(self):
        self.state = {"sid": None, "n": 0, "steal": 0}

    @property
    def handshakes(self):
        return self.state["n"]

    def steal(self, times):
        self.state["steal"] = times

    def __enter__(self):
        import http.server
        import threading
        state = self.state

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *a):
                pass

            def _send(self, code, data, ctype="application/json", sid=None):
                self.send_response(code)
                if sid:
                    self.send_header("MCP-Session-Id", sid)
                self.send_header("Content-Type", ctype)
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def do_POST(self):
                body = json.loads(self.rfile.read(
                    int(self.headers.get("Content-Length", 0))))
                if body.get("method") == "initialize":
                    state["n"] += 1
                    state["sid"] = "s%d" % state["n"]
                    out = {"jsonrpc": "2.0", "id": body["id"],
                           "result": {"serverInfo": {"name": "stand-in"}}}
                    self._send(200, json.dumps(out).encode(), sid=state["sid"])
                    return
                if (body.get("method") == "tools/call" and state["steal"] > 0
                        and self.headers.get("MCP-Session-Id")
                        == state["sid"]):
                    state["steal"] -= 1
                    state["sid"] = "rival-%d" % state["steal"]
                if self.headers.get("MCP-Session-Id") != state["sid"]:
                    self._send(400, b'{"jsonrpc":"2.0","error":{"code":'
                                    b'-32600,"message":"Bad Request: missing'
                                    b' or invalid MCP-Session-Id"}}')
                    return
                if "id" not in body:
                    self.send_response(202)
                    self.end_headers()
                    return
                tool = body.get("params", {}).get("name")
                if tool == "crash":
                    self._send(500, b"internal error")
                    return
                if tool == "fail":
                    out = {"jsonrpc": "2.0", "id": body["id"], "error": {
                        "code": -32601, "message": "no such tool"}}
                else:
                    out = {"jsonrpc": "2.0", "id": body["id"], "result": {
                        "content": [{"type": "text", "text": '{"ok": 1}'}]}}
                data = json.dumps(out)
                if tool == "sse":
                    self._send(200, ("event: message\ndata: %s\n\n"
                                     % data).encode(), "text/event-stream")
                else:
                    self._send(200, data.encode())

        self._httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=self._httpd.serve_forever, daemon=True).start()
        self.port = self._httpd.server_address[1]
        return self

    def __exit__(self, *exc):
        self._httpd.shutdown()
        self._httpd.server_close()
        return False


def _raises(fn, cls):
    """`(raised cls, the exception or what happened instead)`."""
    try:
        got = fn()
    except cls as e:
        return True, e
    except Exception as e:                                   # noqa: BLE001
        return False, "%s: %s" % (type(e).__name__, e)
    return False, "returned %r" % (got,)


def self_check() -> list:
    """Decoding, the error replies, the absent server and the stolen session.

    No emulator anywhere: the refused port is port 1, and the fork's session
    rule is played by `_OneSessionServer` on loopback. Returns one
    `(name, passed, detail)` per assertion.
    """
    results = []

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    # Plain JSON and single-event SSE must decode to the same thing.
    doc = {"jsonrpc": "2.0", "id": 1, "result": {"ok": True}}
    check("a plain JSON body decodes", _decode(json.dumps(doc)) == doc)
    sse = "event: message\ndata: %s\n\n" % json.dumps(doc)
    check("a one-event SSE body decodes the same as JSON",
          _decode(sse) == _decode(json.dumps(doc)))
    check("an SSE body with a ping before the payload takes the payload",
          _decode("data: not json\n" + sse) == doc)
    check("an empty body is empty, not a crash", _decode("  ") == {})

    # An error reply must raise with the server's own message in it, not
    # return a half-result the caller then indexes into.
    err = {"jsonrpc": "2.0", "id": 1,
           "error": {"code": -32601, "message": "no such tool"}}
    ok, e = _raises(lambda: _result(err, tool="nope"), ToolError)
    check("an error reply raises ToolError with the message",
          ok and "no such tool" in str(e), e)
    ok, e = _raises(lambda: _result({"jsonrpc": "2.0", "id": 1}), ToolError)
    check("a reply with no result raises ToolError", ok, e)
    ok, e = _raises(lambda: _decode("not json at all"), ToolError)
    check("an undecodable body raises ToolError", ok, e)

    # The text payload is pulled out of content[].
    payload = {"content": [{"type": "text", "text": '{"a": 1}'}]}
    check("the text payload is found", _text_of(payload) == '{"a": 1}')
    check("no text content is None", _text_of({"content": []}) is None)

    # Constructing a client must not talk to anything, and takes host and
    # port from env.py when not given.
    inert = Client(port=1)
    check("constructing a client is inert",
          inert.session is None and inert.server is None)
    built = Client()
    check("host and port default to env.mcp_host() and env.mcp_port()",
          (built.host, built.port) == (env.mcp_host(), env.mcp_port()),
          (built.host, built.port))
    check("the client does not introduce itself as a project",
          built.name == "duckmcp", built.name)

    # **The red case that matters**: a port nobody listens on must say the
    # fork is not running, not raise a URLError -- and say *which* of the
    # silences it is, because they call for opposite actions. Port 1 is
    # reserved and refuses instantly. Each branch is driven by an injected
    # probe, so none is a promise.
    def absent(alive, want, label):
        ok, e = _raises(lambda: Client(port=1, timeout=2.0, alive=alive)
                        .call("get_status"), NotRunning)
        check(label, ok and all(w in str(e) for w in want), e)

    absent(lambda: [], ["no DuckStation process either", "pitfall 35", PLAN],
           "a refused port with no process names the crash and the plan")
    absent(lambda: [4242], ["duckstation-qt IS running", "not answering"],
           "a refused port with a live process says the server is the problem")
    absent(lambda: None, ["not running", "pitfall 35", PLAN],
           "a refused port with an unknown process names both causes")

    def broken():
        raise OSError("probe failed")
    absent(broken, ["not running", "pitfall 35"],
           "a probe that raises reads as unknown, not as a crash")
    # The default probe lists processes through duckmcp.fork; the two
    # answers it gives a refused port are asserted there, with
    # running_pids() stubbed. Here: it answers in the probe's vocabulary.
    check("the default liveness probe answers True, False or None",
          process_alive() in (True, False, None), repr(process_alive()))

    # **One session, newest handshake wins** -- the fork's behaviour, played
    # by the stand-in. The red case is the same call with `reclaim` off.
    with _OneSessionServer() as srv:
        a = Client(port=srv.port, timeout=5.0)
        check("the stand-in answers a call", a.call("get_status") == {"ok": 1})
        check("the stand-in answers an SSE reply the same",
              a.call("sse") == {"ok": 1})

        b = Client(port=srv.port, timeout=5.0)
        b.call("get_status")
        Client(port=srv.port, timeout=5.0).initialize()
        try:
            answer = b.call("get_status")
            detail = "reclaimed %d" % b.reclaimed
        except Exception as e:                               # noqa: BLE001
            answer, detail = None, "%s: %s" % (type(e).__name__, e)
        check("a stolen session is recovered once and the call goes through",
              answer == {"ok": 1} and b.reclaimed == 1, detail)

        d = Client(port=srv.port, timeout=5.0)
        d.call("get_status")
        srv.steal(2)
        ok, e = _raises(lambda: d.call("get_status"), SessionLost)
        check("a second loss in a row is an error (SessionLost)",
              ok and d.reclaimed == 1 and "pitfall 46" in str(e),
              "%s; reclaimed %d" % (e, d.reclaimed))
        srv.steal(0)

        f = Client(port=srv.port, timeout=5.0)
        f.call("get_status")
        before = srv.handshakes
        ok, e = _raises(lambda: f.call("fail"), ToolError)
        check("another ToolError passes without a new handshake",
              ok and not isinstance(e, SessionLost) and f.reclaimed == 0
              and srv.handshakes == before and "no such tool" in str(e),
              "%s; handshakes %d -> %d" % (e, before, srv.handshakes))
        ok, e = _raises(lambda: f.call("crash"), ToolError)
        check("an HTTP 500 is a ToolError without a new handshake",
              ok and not isinstance(e, SessionLost) and f.reclaimed == 0
              and srv.handshakes == before and "HTTP 500" in str(e),
              "%s; handshakes %d -> %d" % (e, before, srv.handshakes))

        c = Client(port=srv.port, timeout=5.0, reclaim=False)
        c.call("get_status")
        Client(port=srv.port, timeout=5.0).initialize()
        ok, e = _raises(lambda: c.call("get_status"), SessionLost)
        check("without reclaim a stolen session fails with SessionLost", ok, e)

    return results

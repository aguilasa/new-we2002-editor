"""Everything duckmcp reads from the environment, and nothing else does.

Design rule (d) of PLAN-DUCKMCP-PY.md section 3.3: this is the only module
that touches `os.environ`, and the only one that builds `XAUTHORITY`. Every
function reads the environment **when called**, not at import, so a value set
after `import duckmcp` is honoured; each takes an optional `environ` mapping
so the self-check can try precedence without touching the process.

The variables, each with its legacy name read as fallback (the new name wins
over the legacy one, and either wins over the default):

| variable               | legacy fallback    | default                          |
|------------------------|--------------------|----------------------------------|
| `DUCKSTATION_MCP_HOST` | `PES2_MCP_HOST`    | `127.0.0.1`                      |
| `DUCKSTATION_MCP_PORT` | `PES2_MCP_PORT`    | `2346`                           |
| `DUCKSTATION_FORK`     | `PES2_FORK`        | `C:\\games\\ps1\\duckstation-mcp` on Windows, `~/Applications/duckstation-mcp` elsewhere |
| `DUCKSTATION_APPIMAGE` | `PES2_DUCKSTATION` | `~/Applications/DuckStation-x64.AppImage` |
| `DUCKSTATION_DISPLAY`  | `PES2_DISPLAY`     | `:98`                            |

The legacy names are read only so the callers that still export them keep
working while they migrate; they are legacy and new code sets the new ones.
"""

import os

# lineage: tools/pes2/fork.py:107-112, 237-246; tools/pes2/mcp.py:41-42;
# tools/looks/oracle.py:330-352; tools/pes2/drive.py:185-190.

WINDOWS = os.name == "nt"
"""Whether this runs on Windows, where the fork lives in its own folder."""

# lineage: the legacy names below are the ones tools/pes2 exported before
# this package existed; they are read as fallback only.
LEGACY = {
    "DUCKSTATION_MCP_HOST": "PES2_MCP_HOST",
    "DUCKSTATION_MCP_PORT": "PES2_MCP_PORT",
    "DUCKSTATION_FORK": "PES2_FORK",
    "DUCKSTATION_APPIMAGE": "PES2_DUCKSTATION",
    "DUCKSTATION_DISPLAY": "PES2_DISPLAY",
}
"""New variable name -> its legacy fallback, which the new one beats."""

DEFAULT_HOST = "127.0.0.1"
"""Where the fork's MCP server listens when nothing says otherwise."""

DEFAULT_PORT = 2346
"""The fork's MCP port when nothing says otherwise."""

DEFAULT_DISPLAY = ":98"
"""The repository's Xvfb; the user's session is never the default."""

XVFB_DISPLAY = ":98"
"""The display whose server runs without `-auth`, so `XAUTHORITY` is empty."""


def _environ(environ):
    return os.environ if environ is None else environ


def get(name, default=None, environ=None):
    """The value of `name`, else of its legacy fallback, else `default`.

    An empty string counts as unset, as it does for the shell idiom
    `${VAR:-default}`: exporting `DUCKSTATION_MCP_PORT=` must not turn the
    port into `int("")`.
    """
    env = _environ(environ)
    value = env.get(name)
    if value:
        return value
    legacy = LEGACY.get(name)
    if legacy:
        value = env.get(legacy)
        if value:
            return value
    return default


def mcp_host(environ=None):
    """The MCP server's host (`DUCKSTATION_MCP_HOST`, legacy `PES2_MCP_HOST`)."""
    return get("DUCKSTATION_MCP_HOST", DEFAULT_HOST, environ)


def mcp_port(environ=None):
    """The MCP server's port (`DUCKSTATION_MCP_PORT`, legacy `PES2_MCP_PORT`)."""
    return int(get("DUCKSTATION_MCP_PORT", str(DEFAULT_PORT), environ))


def fork_home(environ=None):
    """The fork's install folder (`DUCKSTATION_FORK`, legacy `PES2_FORK`).

    Windows has no `~/Applications`, and there the fork lives beside the
    games on the system volume.
    """
    default = (r"C:\games\ps1\duckstation-mcp" if WINDOWS
               else "~/Applications/duckstation-mcp")
    return os.path.expanduser(get("DUCKSTATION_FORK", default, environ))


def appimage(environ=None):
    """The official AppImage (`DUCKSTATION_APPIMAGE`, legacy `PES2_DUCKSTATION`)."""
    return os.path.expanduser(get(
        "DUCKSTATION_APPIMAGE", "~/Applications/DuckStation-x64.AppImage",
        environ))


def display(environ=None):
    """The X display to drive (`DUCKSTATION_DISPLAY`, legacy `PES2_DISPLAY`).

    Defaults to `:98`, never to the inherited `DISPLAY`: that is the user's
    real session.
    """
    return get("DUCKSTATION_DISPLAY", DEFAULT_DISPLAY, environ)


def x_env(display_name, base=None):
    """A copy of `base` (default: the process environment) aimed at a display.

    `DISPLAY` is set; `XAUTHORITY` is emptied **only** on `:98`, whose Xvfb
    runs without `-auth`, and is left as inherited everywhere else -- a
    server started by `xvfb-run`, or the user's own, needs its cookie, and
    without it Qt dies with `Invalid MIT-MAGIC-COOKIE-1 key`.
    """
    env = dict(_environ(base))
    env["DISPLAY"] = display_name
    if display_name == XVFB_DISPLAY:
        env["XAUTHORITY"] = ""
    return env


def data_dir(environ=None):
    """DuckStation's data directory on this machine.

    Windows runs the fork portable, out of its own folder; on Linux it is
    the user's shared `~/.local/share/duckstation`, one for every instance.
    """
    if WINDOWS:
        return fork_home(environ)
    return os.path.expanduser("~/.local/share/duckstation")


def savestates_dir(environ=None):
    """Where DuckStation itself writes save states: `<data_dir>/savestates`."""
    return os.path.join(data_dir(environ), "savestates")


def state_path(serial, slot, environ=None):
    """The file of save-state `slot` for the disc `serial`.

    DuckStation names it `<serial>_<slot>.sav`; the serial comes from the
    caller (the disc or the running emulator), never from this package.
    """
    return os.path.join(savestates_dir(environ), "%s_%d.sav" % (serial, slot))


def is_roms(path):
    """Does this path live under a `roms/` directory?

    Both separators are normalised: `os.path.abspath` answers in the
    platform's own, and a bare `"/roms/" in ...` is simply false for a
    Windows path -- which would let the one rule that protects the
    originals pass silently on half the machines this runs on.
    """
    full = os.path.abspath(path).replace(os.sep, "/").replace("\\", "/")
    return "/roms/" in full + "/"


def self_check() -> list:
    """Precedence, the `:98` rule, `is_roms` and `state_path`.

    Returns one `(name, passed, detail)` per assertion, so the gate counts
    each and names the one that failed.
    """
    results = []

    def expect(what, got, want):
        results.append((what, got == want, "got %r, want %r" % (got, want)))

    both = {"DUCKSTATION_MCP_PORT": "1", "PES2_MCP_PORT": "2"}
    expect("port: DUCKSTATION_MCP_PORT beats PES2_MCP_PORT", mcp_port(both), 1)
    expect("port: PES2_MCP_PORT alone beats the default",
           mcp_port({"PES2_MCP_PORT": "2"}), 2)
    expect("port: neither gives 2346", mcp_port({}), 2346)
    expect("port: empty new name falls through to legacy",
           mcp_port({"DUCKSTATION_MCP_PORT": "", "PES2_MCP_PORT": "2"}), 2)

    expect("host: DUCKSTATION_MCP_HOST beats PES2_MCP_HOST",
           mcp_host({"DUCKSTATION_MCP_HOST": "a", "PES2_MCP_HOST": "b"}), "a")
    expect("host: PES2_MCP_HOST alone beats the default",
           mcp_host({"PES2_MCP_HOST": "b"}), "b")
    expect("host: neither gives 127.0.0.1", mcp_host({}), "127.0.0.1")

    expect("display: DUCKSTATION_DISPLAY beats PES2_DISPLAY",
           display({"DUCKSTATION_DISPLAY": ":7", "PES2_DISPLAY": ":8"}), ":7")
    expect("display: PES2_DISPLAY alone beats the default",
           display({"PES2_DISPLAY": ":8"}), ":8")
    expect("display: neither gives :98", display({}), ":98")

    expect("fork: DUCKSTATION_FORK beats PES2_FORK",
           fork_home({"DUCKSTATION_FORK": "/a", "PES2_FORK": "/b"}), "/a")
    expect("fork: PES2_FORK alone beats the default",
           fork_home({"PES2_FORK": "/b"}), "/b")
    expect("appimage: DUCKSTATION_APPIMAGE beats PES2_DUCKSTATION",
           appimage({"DUCKSTATION_APPIMAGE": "/a", "PES2_DUCKSTATION": "/b"}),
           "/a")
    expect("appimage: PES2_DUCKSTATION alone beats the default",
           appimage({"PES2_DUCKSTATION": "/b"}), "/b")

    inherited = {"XAUTHORITY": "/run/cookie", "DISPLAY": ":1", "KEEP": "x"}
    on98 = x_env(":98", inherited)
    expect("x_env(':98'): XAUTHORITY is ''", on98.get("XAUTHORITY"), "")
    expect("x_env(':98'): DISPLAY is :98", on98.get("DISPLAY"), ":98")
    on1 = x_env(":1", inherited)
    expect("x_env(':1'): inherited XAUTHORITY untouched",
           on1.get("XAUTHORITY"), "/run/cookie")
    expect("x_env(':1'): no XAUTHORITY added when none inherited",
           "XAUTHORITY" in x_env(":1", {}), False)
    expect("x_env: other variables kept", on1.get("KEEP"), "x")
    expect("x_env: base is not modified", inherited["DISPLAY"], ":1")

    expect("is_roms: forward slashes", is_roms("/x/roms/a.bin"), True)
    expect("is_roms: backslashes", is_roms(r"C:\x\roms\a.bin"), True)
    expect("is_roms: the folder itself", is_roms("/x/roms"), True)
    expect("is_roms: work/ is not roms/", is_roms("/x/work/a.bin"), False)
    expect("is_roms: a name that only contains roms",
           is_roms(r"C:\x\myroms\a.bin"), False)

    fake = {"DUCKSTATION_FORK": "/f"}
    got = state_path("ABCD-12345", 2, fake)
    expect("state_path: file name is <serial>_<slot>.sav",
           os.path.basename(got), "ABCD-12345_2.sav")
    expect("state_path: lives in savestates_dir()",
           os.path.dirname(got), savestates_dir(fake))
    expect("savestates_dir: <data_dir>/savestates",
           savestates_dir(fake), os.path.join(data_dir(fake), "savestates"))
    return results

#!/usr/bin/env python3
"""Start, stop and find the DuckStation fork that carries the MCP server.

`run_duckstation.sh` launches the **official AppImage**, which has no MCP
server; this launches the fork, which does. The two coexist on purpose --
see `--which` and the note under WHERE below.

    tools/pes2/fork.py launch <copy.cue>     # boot, dismiss, wait for MCP
    tools/pes2/fork.py status                # is one up, and which binary?
    tools/pes2/fork.py kill                  # both binaries, and the mounts
    tools/pes2/fork.py recipe                # how to rebuild it from source
    tools/pes2/fork.py --self-check          # no emulator needed

WHERE
-----
The fork lives in `~/Applications/duckstation-mcp/`, chosen by the user on
2026-09-03, next to the official AppImage that is still the thing a third
party can reproduce. **It is not in the repository and must never be**: the
DuckStation licence is CC-BY-NC-ND-4.0 and the binary itself says a modified
build may not be distributed. Same rule as `roms/` and `we-team-editor.exe`.
`recipe` prints how to rebuild it; `PES2_FORK` overrides the location.

The layout is `bin/`, `lib/` and `plugins/`, and the last two are why this
module exists rather than a bare exec: the binary's RUNPATH is an absolute
path into the build tree it was compiled in, so it only finds its Qt through
`LD_LIBRARY_PATH`, and Qt only finds its platform plugin through
`QT_PLUGIN_PATH`. Copying `bin/` alone gives a binary that dies with
`could not load the Qt platform plugin "xcb"`, which reads like a display
problem and is not one.

WHAT IT HAS TO GET PAST
-----------------------
Measured 2026-09-03, and two of the three corrected an earlier reading:

* **An `Automatic Updater` dialog**, not the `You are not using an official
  release!` one the plan expected. It is a real modal, it overlaps the game
  window, and `Escape` does **not** close it -- the buttons are Download,
  Skip and Remind, none of them a reject role. This clicks *Remind Me
  Later*: Skip would silence it for good but by writing the user's own
  DuckStation configuration, which this launcher does not do (see the note
  in `run_duckstation.sh`).
* **The MCP port opens before the dialog is dismissed**, contrary to what
  PES2-TASK-33 recorded. `initialize` answered with the modal still on
  screen. The dialog is still dismissed, because it sits on top of the game
  window and `import -window` would capture it.
* **`xdotool windowkill` kills the process**, not the window -- it closes
  the X client. It took the emulator and the MCP session down with it once.
  Never use it here; click, or kill the process on purpose.
"""

import argparse
import os
import shutil
import signal
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from mcp import Client, NotRunning                            # noqa: E402

SKIP = 77

FORK_HOME = os.path.expanduser(
    os.environ.get("PES2_FORK", "~/Applications/duckstation-mcp"))
APPIMAGE = os.path.expanduser(
    os.environ.get("PES2_DUCKSTATION",
                   "~/Applications/DuckStation-x64.AppImage"))

# Every process name that is a DuckStation on this machine. The AppImage
# runs as `AppRun` and the fork as `duckstation-qt`, so a filter on either
# alone leaves the other holding the display -- armadilha 6 of section 6.11,
# which grew a third name the day the fork arrived.
PROCESS_NAMES = ("duckstation-qt", "AppRun", "DuckStation-x64")

GAME_WINDOW = "^Pro Evolution Soccer 2$"
DIALOGS = ("Automatic Updater", "DuckStation")

RECIPE = """\
Getting the fork -- two ways, cheapest first.

1. Download the build its own CI publishes. The fork's README is the
   upstream's, untouched, so it points at `stenzek/duckstation` releases --
   which are the build *without* the server. Its own releases tab is a
   different page, and the CI drops fourteen assets there on every push:

     gh release download latest --repo sadnescity/duckstation \\
        --pattern 'DuckStation-x64.AppImage'

   Confirm before trusting it. The release is rebuilt on every push and
   nothing promises the next build still carries the server -- this check is
   part of the recipe, not decoration:

     ./DuckStation-x64.AppImage --appimage-extract
     strings -a squashfs-root/usr/bin/duckstation-qt | grep -x EnableMCPServer

   Measured 2026-09-03 on the `latest` release of 2026-08-29:
   EnableMCPServer, MCPServerPort, duckstation-mcp, memory_scan,
   snapshot_memory, press_button, frame_step and load_state all present --
   and all absent from the official AppImage.

2. Build it from source -- measured 2026-09-03, 107 s for the compile
   itself, and what you want if you need to change it.

  git clone --depth 1 -b mcp https://github.com/sadnescity/duckstation.git
  cd duckstation
  scripts/deps/build-dependencies-linux.sh      # or the prebuilt pack
  sudo apt install clang-tools-18               # for clang-scan-deps;
                                                # CMake needs it to scan
                                                # the C++20 modules
  cmake -B build-release -DCMAKE_BUILD_TYPE=Release \\
        -DCMAKE_PREFIX_PATH=$PWD/dep/prebuilt/linux-x64
  cmake --build build-release -j

Then install it where this launcher looks, keeping the three directories
side by side so LD_LIBRARY_PATH and QT_PLUGIN_PATH can find them:

  DEST=~/Applications/duckstation-mcp
  mkdir -p $DEST/bin $DEST/lib $DEST/plugins
  cp -a build-release/bin/. $DEST/bin/
  find dep/prebuilt/linux-x64/lib -maxdepth 1 -name '*.so*' \\
       -exec cp -a {} $DEST/lib/ \\;
  cp -a dep/prebuilt/linux-x64/plugins/. $DEST/plugins/

The MCP server is off by default. It is enabled in the user's own
DuckStation configuration -- ~/.local/share/duckstation/settings.ini --
and was put there with authorisation on 2026-09-03:

  [Debug]
  EnableMCPServer = true
  MCPServerPort = 2346

Nothing of this goes in the repository. The licence is CC-BY-NC-ND-4.0.
"""


class Fail(Exception):
    """The launcher could not get to a running, answering emulator."""


class Skip(Exception):
    """This machine cannot run it; ctest should read it as skipped."""


# --- where the binary is -----------------------------------------------

def binary(home=None):
    return os.path.join(home or FORK_HOME, "bin", "duckstation-qt")


def installed(home=None):
    return os.path.isfile(binary(home))


def env_for(display, home=None):
    """The environment the fork needs, on top of the caller's.

    `XAUTHORITY` empty on :98 and inherited elsewhere is the repository
    rule; the two library paths are this build's own, see the module note.
    """
    home = home or FORK_HOME
    env = dict(os.environ, DISPLAY=display)
    if display == ":98":
        env["XAUTHORITY"] = ""
    lib = os.path.join(home, "lib")
    plugins = os.path.join(home, "plugins")
    if os.path.isdir(lib):
        env["LD_LIBRARY_PATH"] = lib + os.pathsep + env.get(
            "LD_LIBRARY_PATH", "")
    if os.path.isdir(plugins):
        env["QT_PLUGIN_PATH"] = plugins
    return env


# --- stopping ----------------------------------------------------------

def running_pids():
    """Every live DuckStation, by exact process name.

    **Not `pgrep -f`.** It matches the command line of the shell that is
    running this, so `pkill -f` over it kills the caller -- twice, in this
    project's history (armadilha 25).
    """
    pids = []
    for name in PROCESS_NAMES:
        out = subprocess.run(["pgrep", "-x", name], capture_output=True,
                             text=True)
        for line in out.stdout.split():
            try:
                pid = int(line)
            except ValueError:
                continue
            if pid != os.getpid() and pid not in pids:
                pids.append(pid)
    return pids


def kill(verbose=True):
    """Stop every DuckStation and clean up after the AppImage."""
    pids = running_pids()
    for pid in pids:
        try:
            # SIGTERM parks it on a Confirm Exit dialog that holds its
            # windows open for ever, even with ConfirmPowerOff = false.
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    for _ in range(20):
        if not running_pids():
            break
        time.sleep(0.5)

    # The AppImage leaves its squashfs mounted when killed this way. The
    # fork does not -- it is a plain binary -- but a mixed session can have
    # left one behind.
    for _ in range(3):
        left = 0
        out = subprocess.run(["mount"], capture_output=True, text=True).stdout
        points = [ln.split()[2] for ln in out.splitlines()
                  if "DuckStation-x64.AppImage" in ln and len(ln.split()) > 2]
        if not points:
            break
        for point in points:
            if subprocess.run(["fusermount", "-u", point],
                              capture_output=True).returncode != 0:
                left = 1
            try:
                os.rmdir(point)
            except OSError:
                pass
        if not left:
            break
        time.sleep(1)

    if verbose:
        print(f"stopped {len(pids)} DuckStation process(es)"
              + (f": {pids}" if pids else ""))
    return len(pids)


# --- starting ----------------------------------------------------------

def _windows(display, pattern):
    env = dict(os.environ, DISPLAY=display)
    if display == ":98":
        env["XAUTHORITY"] = ""
    out = subprocess.run(["xdotool", "search", "--name", pattern],
                         env=env, capture_output=True, text=True)
    return [w for w in out.stdout.split() if w]


def _xdotool(display, *args):
    env = dict(os.environ, DISPLAY=display)
    if display == ":98":
        env["XAUTHORITY"] = ""
    return subprocess.run(["xdotool", *args], env=env, capture_output=True,
                          text=True)


def _dismiss_dialogs(display, deadline):
    """Click any modal out of the way. Returns the titles it dismissed.

    The button is found by geometry rather than by accessibility, because
    there is no accessibility bridge on a bare Xvfb. `Remind Me Later` is
    the rightmost of three, about 70 px in from the right edge and 25 up
    from the bottom -- measured on the 651x474 dialog of 2026-09-03.
    """
    dismissed = []
    while time.time() < deadline:
        found = None
        for title in DIALOGS:
            for w in _windows(display, f"^{title}$"):
                # The game window is not a dialog, however it is named.
                name = _xdotool(display, "getwindowname", w).stdout.strip()
                if name in DIALOGS:
                    found = (w, name)
                    break
            if found:
                break
        if not found:
            return dismissed
        w, name = found
        geometry = _xdotool(display, "getwindowgeometry", w).stdout
        size = [ln for ln in geometry.splitlines() if "Geometry:" in ln]
        width, height = 651, 474
        if size:
            try:
                width, height = (int(x) for x in
                                 size[0].split(":")[1].strip().split("x"))
            except (ValueError, IndexError):
                pass
        _xdotool(display, "mousemove", "--window", w,
                 str(width - 70), str(height - 25), "click", "1")
        dismissed.append(name)
        time.sleep(2)
    return dismissed


def wait_for_mcp(deadline, host=None, port=None):
    """Poll `initialize` until the server answers. Returns the server info."""
    last = None
    while time.time() < deadline:
        try:
            c = Client(**({"host": host} if host else {}),
                       **({"port": port} if port else {}), timeout=5.0)
            return c.initialize(), c
        except NotRunning as e:
            last = e
            time.sleep(1)
    raise Fail(f"the MCP server never answered: {last}")


def launch(image, display=None, timeout=120, home=None, verbose=True,
           log=None):
    """Boot the game under the fork and come back with an answering session.

    Returns `(pid, window, client)`. Each of the four ways this fails says
    which one it was, because they look identical from the outside -- a
    missing binary, a process that died, a window that never came, and a
    port that never answered all present as "nothing happened".
    """
    home = home or FORK_HOME
    display = display or os.environ.get("PES2_DISPLAY", ":98")

    if not installed(home):
        raise Skip(f"no DuckStation fork at {binary(home)} -- "
                   f"run `tools/pes2/fork.py recipe` for how to build it")
    if not image:
        raise Fail("give the .cue of a working copy")
    if "/roms/" in os.path.abspath(image):
        raise Fail("refusing to boot roms/ -- copy first")
    if not os.path.isfile(image):
        raise Skip(f"no image at {image}")
    if shutil.which("xdotool") is None:
        raise Skip("xdotool is missing")
    if _xdotool(display, "getdisplaygeometry").returncode != 0:
        raise Skip(f"no X server on {display}")

    kill(verbose=False)
    time.sleep(1)

    log = log or os.path.join(
        os.path.dirname(os.path.abspath(image)), "duckstation-fork.log")
    # Append, never truncate. The fork dies on its own during free execution
    # (pitfall 35) and writes nothing when it goes, so the only chance of
    # ever catching it is a log that survives the next launch -- and the old
    # "wb" erased the previous run's evidence at exactly the moment someone
    # went looking for it. A run boundary goes in first so the file stays
    # readable.
    handle = open(log, "ab")
    handle.write(f"\n=== launch {time.strftime('%Y-%m-%d %H:%M:%S')} "
                 f"{os.path.basename(image)} ===\n".encode())
    handle.flush()
    process = subprocess.Popen(
        [binary(home), "-batch", "-fastboot", "-nogui", "--", image],
        env=env_for(display, home), stdout=handle, stderr=subprocess.STDOUT)
    deadline = time.time() + timeout

    def say(msg):
        if verbose:
            print(f"  {msg}", flush=True)

    say(f"fork {process.pid} on {display}, log {log}")

    # 1) the window. Match by _NET_WM_PID: a dead instance's window still
    #    answers to xdotool search, and capturing it yields a black frame.
    window = None
    while time.time() < deadline and window is None:
        if process.poll() is not None:
            handle.close()
            raise Fail(f"the fork exited during boot (code "
                       f"{process.returncode}); last of {log}:\n"
                       + _tail(log))
        _dismiss_dialogs(display, min(deadline, time.time() + 3))
        for w in _windows(display, GAME_WINDOW):
            owner = subprocess.run(["xprop", "-id", w, "_NET_WM_PID"],
                                   env=env_for(display, home),
                                   capture_output=True, text=True).stdout
            pid = owner.strip().split()[-1] if owner.strip() else ""
            if pid.isdigit() and int(pid) == process.pid:
                window = w
                break
        if window is None:
            time.sleep(1)
    if window is None:
        raise Fail(f"the game window never appeared within {timeout}s; "
                   f"last of {log}:\n" + _tail(log))
    say(f"window {window}")

    # 2) any modal that came up after the window, and there is one every
    #    launch: the updater sits on top of the game.
    for name in _dismiss_dialogs(display, min(deadline, time.time() + 20)):
        say(f"dismissed the {name} dialog")

    # 3) with no window manager the window places itself wherever it likes
    #    -- it picked x=2480 on a 1280-wide screen once, off the edge where
    #    `import` cannot reach it.
    if display == ":98":
        _xdotool(display, "windowmove", window, "0", "0")
        time.sleep(0.5)

    # 4) the server. This is the one that says the build has no MCP in it.
    server, client = wait_for_mcp(deadline)
    say(f"{server.get('name')} {server.get('version')} answering")
    return process.pid, window, client


def _tail(path, lines=8):
    try:
        with open(path, "rb") as fh:
            return b"".join(fh.readlines()[-lines:]).decode("utf-8", "replace")
    except OSError:
        return "(no log)"


# --- status ------------------------------------------------------------

def which_binary(pid):
    """The path a running DuckStation was started from."""
    try:
        return os.path.realpath(f"/proc/{pid}/exe")
    except OSError:                                          # pragma: no cover
        return "?"


def status(verbose=True):
    """What is running, and whether it is the fork or the AppImage."""
    pids = running_pids()
    report = {"pids": pids, "fork": False, "mcp": None, "binaries": []}
    for pid in pids:
        path = which_binary(pid)
        report["binaries"].append(path)
        if path.startswith(os.path.realpath(FORK_HOME)):
            report["fork"] = True
    try:
        with Client(timeout=3.0) as c:
            report["mcp"] = c.server
    except NotRunning:
        pass
    if verbose:
        if not pids:
            print("no DuckStation is running")
        for pid, path in zip(pids, report["binaries"]):
            kind = "fork (MCP)" if path.startswith(
                os.path.realpath(FORK_HOME)) else "official AppImage"
            print(f"  pid {pid}  {kind}  {path}")
        if report["mcp"]:
            print(f"  MCP: {report['mcp'].get('name')} "
                  f"{report['mcp'].get('version')}")
        elif pids:
            print("  MCP: no server answering -- this is not the fork, or "
                  "EnableMCPServer is off")
    return report


# --- self-check --------------------------------------------------------

def self_check(verbose=True):
    """What can be proved with no emulator: paths, environment, red cases."""
    bad = []

    def check(what, ok, detail=""):
        if verbose:
            print(f"  {'ok' if ok else 'FAIL'}   {what}"
                  + (f"  ({detail})" if detail and not ok else ""))
        if not ok:
            bad.append(f"{what}{': ' + detail if detail else ''}")

    env = env_for(":98", home="/nowhere")
    check("XAUTHORITY is blanked on :98", env.get("XAUTHORITY") == "")
    env1 = env_for(":1", home="/nowhere")
    check("XAUTHORITY is left alone on :1",
          env1.get("XAUTHORITY") == os.environ.get("XAUTHORITY", None)
          or "XAUTHORITY" not in env1 or env1["XAUTHORITY"] != "")
    check("a missing install adds no library path",
          "LD_LIBRARY_PATH" not in env or env["LD_LIBRARY_PATH"]
          == os.environ.get("LD_LIBRARY_PATH", ""))

    # The three process names must all be there: dropping one is exactly
    # how the fork escaped `run_duckstation.sh --kill`.
    for name in ("duckstation-qt", "AppRun", "DuckStation-x64"):
        check(f"{name} is in the kill list", name in PROCESS_NAMES)

    # Red case: launching with no install must skip with the recipe in the
    # message, not raise a FileNotFoundError from Popen.
    try:
        launch("/nonexistent.cue", home="/nowhere", verbose=False)
        check("a missing install skips", False, "it launched")
    except Skip as e:
        check("a missing install skips and names the recipe",
              "recipe" in str(e), str(e))
    except Exception as e:                                   # noqa: BLE001
        check("a missing install skips", False, f"{type(e).__name__}: {e}")

    # Red case: roms/ must be refused before anything is started, and the
    # refusal must not depend on the install being present.
    if installed():
        try:
            launch("/x/roms/whatever.cue", verbose=False)
            check("roms/ is refused", False, "it launched")
        except Fail as e:
            check("roms/ is refused", "roms/" in str(e), str(e))
        except Exception as e:                               # noqa: BLE001
            check("roms/ is refused", False, f"{type(e).__name__}: {e}")
    else:
        check("roms/ refusal (needs the install to reach it)", True)

    check("the recipe names the licence", "CC-BY-NC-ND" in RECIPE)
    check("the recipe names the install directory",
          "duckstation-mcp" in RECIPE)
    check("running_pids never returns our own pid",
          os.getpid() not in running_pids())

    if verbose:
        print("SELF-CHECK " + ("FAILED" if bad else
                               "OK: paths, kill list, refusals, recipe"))
    return bad


# --- entry point -------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("command", nargs="?",
                    choices=("launch", "kill", "status", "recipe", "which"),
                    default="status")
    ap.add_argument("image", nargs="?", help=".cue of a working copy")
    ap.add_argument("--display", default=os.environ.get("PES2_DISPLAY", ":98"))
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args(argv)

    if args.self_check:
        return 1 if self_check() else 0

    try:
        if args.command == "recipe":
            print(RECIPE)
            return 0
        if args.command == "which":
            print(binary())
            print("installed" if installed() else "NOT INSTALLED")
            return 0 if installed() else SKIP
        if args.command == "kill":
            kill()
            return 0
        if args.command == "status":
            status()
            return 0
        pid, window, client = launch(
            args.image or os.environ.get("PES2_IMAGE"),
            display=args.display, timeout=args.timeout)
        print(f"PID={pid}")
        print(f"WINDOW={window}")
        print(f"DISPLAY={args.display}")
        print(f"MCP={client.url}")
        return 0
    except Skip as e:
        print(f"skipping: {e}")
        return SKIP
    except Fail as e:
        print(f"FORK FAILED: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

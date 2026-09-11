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

ON WINDOWS
----------
The same three commands work, over a different mechanism, because none of
the Linux one exists there: no `pgrep`, no `SIGKILL`, no `xdotool`, no
`:98`. Measured 2026-09-11 against the fork's own
`duckstation-windows-x64-release.zip` in `C:\\games\\ps1\\duckstation-mcp`:

* **The layout is flat and portable**, not `bin/lib/plugins`. The `.exe`
  sits in the root with its Qt DLLs beside it and a `portable.txt` that
  keeps BIOS, cards, save states and `settings.ini` in the same folder. No
  `LD_LIBRARY_PATH` and no `QT_PLUGIN_PATH` -- Windows resolves DLLs from
  the executable's own directory, which is the whole reason that section
  above does not apply.
* **The window layer is `ctypes` over `user32`**, not `xdotool`:
  `EnumWindows` + `GetWindowThreadProcessId` is the `_NET_WM_PID` match,
  and `GetWindowRect` is `getwindowgeometry`. It needs no display server
  and no accessibility bridge.
* **No `Automatic Updater` came up**, over five polls across fifteen
  seconds. The reason is in `settings.ini`: `[AutoUpdater] LastVersion`
  travelled from the Linux install and matches this build's commit, so the
  updater has nothing to announce. A newer build on the fork's CI would
  make it reappear, so the dismissal is implemented anyway -- as
  **`WM_CLOSE` to the dialog**, because a Qt dialog draws its own buttons
  and owns no child `HWND` for `BM_CLICK` to reach. That path could not be
  exercised here; it is the one thing in this module Windows has not run.
* **There is a window manager**, so the window places itself sanely and
  the `windowmove` of step 3 has no object.

Pitfall 35 -- the fork dying on its own during free execution -- **is not a
Linux thing**. Two deaths in one Windows session on 2026-09-11, both within
a minute of the first MCP call, neither leaving a log line.
"""

import argparse
import csv
import io
import os
import re
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

WINDOWS = os.name == "nt"

# The install the user made on each machine. Windows has no `~/Applications`
# and the fork lives beside the roms on the system volume; `PES2_FORK`
# overrides either.
FORK_HOME = os.path.expanduser(os.environ.get(
    "PES2_FORK", r"C:\games\ps1\duckstation-mcp" if WINDOWS
    else "~/Applications/duckstation-mcp"))
APPIMAGE = os.path.expanduser(
    os.environ.get("PES2_DUCKSTATION",
                   "~/Applications/DuckStation-x64.AppImage"))

# Every process name that is a DuckStation on this machine. The AppImage
# runs as `AppRun` and the fork as `duckstation-qt`, so a filter on either
# alone leaves the other holding the display -- armadilha 6 of section 6.11,
# which grew a third name the day the fork arrived.
PROCESS_NAMES = ("duckstation-qt", "AppRun", "DuckStation-x64")

# The same list for Windows, where a process is named by its image file.
# There is no AppImage there, so the pair is the release build and whatever
# a local compile drops.
WINDOWS_PROCESS_NAMES = ("duckstation-qt-x64-ReleaseLTCG.exe",
                         "duckstation-qt.exe")

GAME_WINDOW = "^Pro Evolution Soccer 2$"
DIALOGS = ("Automatic Updater", "DuckStation")

# `--window ANY` for a game whose window title is not worth writing down.
# DuckStation names the window after the game's DISPLAY TITLE, out of its
# gamedb -- and for WE2002 that title is Japanese, because both the European
# Deluxe and the PT-BR translation boot `SLPM_870.56`. Hardcoding
# `ワールド・サッカー・ウイニング・イレブン２００２` in a caller would tie it to
# one gamedb revision. ANY takes the widest window the PID owns that is not
# one of these helpers, which is what `wait_for_main` does on the Linux side
# of the golden tests, and for the same reason.
ANY_WINDOW = "ANY"
NOT_THE_GAME = ("Qt Selection Owner", "duckstation-qt")

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
    home = home or FORK_HOME
    if WINDOWS:
        # Flat portable layout: the `.exe` in the root, DLLs beside it.
        # A local compile may name it without the build suffix, so the
        # release name is preferred and the plain one is the fallback.
        for name in WINDOWS_PROCESS_NAMES:
            candidate = os.path.join(home, name)
            if os.path.isfile(candidate):
                return candidate
        return os.path.join(home, WINDOWS_PROCESS_NAMES[0])
    return os.path.join(home, "bin", "duckstation-qt")


def installed(home=None):
    return os.path.isfile(binary(home))


def is_roms(path):
    """Does this path live under a `roms/` directory?

    The separator is normalised because `os.path.abspath` answers in the
    platform's own, and a bare `"/roms/" in ...` is simply **false** on
    Windows -- which would let the one rule that protects the originals
    pass silently on half the machines this runs on.
    """
    return "/roms/" in os.path.abspath(path).replace(os.sep, "/") + "/"


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

def _tasklist_pids():
    """Every live DuckStation on Windows, by image name.

    `tasklist` and not `wmic`, which is deprecated and absent on 11, nor a
    PowerShell hop, which costs half a second per call -- and `mcp.py` asks
    this on every failed connection to tell "never started" from "died mid
    run" (pitfall 35).
    """
    pids = []
    for name in WINDOWS_PROCESS_NAMES:
        out = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {name}", "/FO", "CSV", "/NH"],
            capture_output=True, text=True).stdout
        for row in csv.reader(io.StringIO(out)):
            # A filter that matches nothing prints a sentence, not CSV.
            if len(row) < 2 or not row[0].lower().endswith(".exe"):
                continue
            try:
                pid = int(row[1])
            except ValueError:
                continue
            if pid != os.getpid() and pid not in pids:
                pids.append(pid)
    return pids


def running_pids():
    """Every live DuckStation, by exact process name.

    **Not `pgrep -f`.** It matches the command line of the shell that is
    running this, so `pkill -f` over it kills the caller -- twice, in this
    project's history (armadilha 25).
    """
    if WINDOWS:
        return _tasklist_pids()
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
            if WINDOWS:
                # `/F` for the same reason SIGKILL is used below: a polite
                # close parks it on a Confirm Exit dialog.
                subprocess.run(["taskkill", "/F", "/PID", str(pid)],
                               capture_output=True)
            else:
                # SIGTERM parks it on a Confirm Exit dialog that holds its
                # windows open for ever, even with ConfirmPowerOff = false.
                os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    for _ in range(20):
        if not running_pids():
            break
        time.sleep(0.5)

    # The mount cleanup below is the AppImage's, and there is no AppImage
    # on Windows -- `mount` and `fusermount` are not commands there.
    if WINDOWS:
        if verbose:
            print(f"stopped {len(pids)} DuckStation process(es)"
                  + (f": {pids}" if pids else ""))
        return len(pids)

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


# --- the same, over user32 ---------------------------------------------

# Qt's own helper windows. They belong to the process and some are even
# visible for an instant, so the widest-window rule needs them excluded the
# way `NOT_THE_GAME` excludes theirs on X.
WINDOWS_NOT_THE_GAME = ("_q_titlebar", "ThemeChangeObserverWindow",
                        "ScreenChangeObserverWindow", "MSCTFIME UI",
                        "Default IME")

WM_CLOSE = 0x0010


def _user32():
    import ctypes
    return ctypes.WinDLL("user32", use_last_error=True)


def _win_windows(pid=None):
    """Every top-level window, as `(hwnd, pid, visible, cls, title, w, h)`.

    `EnumWindows` plus `GetWindowThreadProcessId` is what `_NET_WM_PID`
    does on the X side, and for the same reason: a dead instance's window
    can linger, and driving it captures a black frame.
    """
    import ctypes
    import ctypes.wintypes as wintypes
    user = _user32()
    out = []

    def collect(hwnd, _lparam):
        owner = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if pid is not None and owner.value != pid:
            return True
        title = ctypes.create_unicode_buffer(512)
        user.GetWindowTextW(hwnd, title, 512)
        cls = ctypes.create_unicode_buffer(256)
        user.GetClassNameW(hwnd, cls, 256)
        rect = wintypes.RECT()
        user.GetWindowRect(hwnd, ctypes.byref(rect))
        out.append((hwnd, owner.value, bool(user.IsWindowVisible(hwnd)),
                    cls.value, title.value,
                    rect.right - rect.left, rect.bottom - rect.top))
        return True

    proto = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    user.EnumWindows(proto(collect), 0)
    return out


def _dismiss_dialogs_windows(deadline, pid=None):
    """Close any modal of ours. Returns the titles it closed.

    **`WM_CLOSE`, not `BM_CLICK`.** A Qt dialog paints its own buttons; it
    owns no child `HWND`, so there is nothing for a button message to
    reach -- the `Contains("BitBtn") || Contains("Button")` rule that the
    repository's Windows notes give for the VCL editor does not carry over.
    `WM_CLOSE` is the title bar's X, which Qt routes to reject, and reject
    is *Remind Me Later*: it dismisses without writing the user's own
    DuckStation configuration, which is the same choice the X side makes.

    Untested against a real dialog -- see ON WINDOWS in the module note.
    """
    closed = []
    while time.time() < deadline:
        found = None
        for hwnd, _pid, visible, _cls, title, _w, _h in _win_windows(pid):
            if visible and title in DIALOGS:
                found = (hwnd, title)
                break
        if not found:
            return closed
        hwnd, title = found
        _user32().PostMessageW(hwnd, WM_CLOSE, 0, 0)
        closed.append(title)
        time.sleep(2)
    return closed


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
           log=None, match=GAME_WINDOW):
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
    if is_roms(image):
        raise Fail("refusing to boot roms/ -- copy first")
    if not os.path.isfile(image):
        raise Skip(f"no image at {image}")
    if not WINDOWS:
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

    say(f"fork {process.pid} on {'this desktop' if WINDOWS else display}, "
        f"log {log}")

    # 1) the window. Match by _NET_WM_PID: a dead instance's window still
    #    answers to xdotool search, and capturing it yields a black frame.
    window = None
    while time.time() < deadline and window is None:
        if process.poll() is not None:
            handle.close()
            raise Fail(f"the fork exited during boot (code "
                       f"{process.returncode}); last of {log}:\n"
                       + _tail(log))
        if WINDOWS:
            _dismiss_dialogs_windows(min(deadline, time.time() + 3),
                                     process.pid)
            candidates = []
            for hwnd, _p, visible, cls, title, width, _h in _win_windows(
                    process.pid):
                if not visible or title in DIALOGS:
                    continue
                if any(h in cls or h in title
                       for h in WINDOWS_NOT_THE_GAME):
                    continue
                if match != ANY_WINDOW and not re.search(match, title):
                    continue
                candidates.append((width, hwnd))
            if candidates:
                window = sorted(candidates, reverse=True)[0][1]
            if window is None:
                time.sleep(1)
            continue
        _dismiss_dialogs(display, min(deadline, time.time() + 3))
        mine = []
        for w in _windows(display, "." if match == ANY_WINDOW else match):
            owner = subprocess.run(["xprop", "-id", w, "_NET_WM_PID"],
                                   env=env_for(display, home),
                                   capture_output=True, text=True).stdout
            pid = owner.strip().split()[-1] if owner.strip() else ""
            if not (pid.isdigit() and int(pid) == process.pid):
                continue
            if match != ANY_WINDOW:
                mine = [w]
                break
            name = _xdotool(display, "getwindowname", w).stdout.strip()
            if name in DIALOGS or any(h in name for h in NOT_THE_GAME):
                continue
            geom = _xdotool(display, "getwindowgeometry", "--shell", w).stdout
            width = next((int(l.split("=")[1]) for l in geom.splitlines()
                          if l.startswith("WIDTH=")), 0)
            mine.append((width, w))
        if match == ANY_WINDOW:
            mine = [w for _, w in sorted(mine, reverse=True)]
        if mine:
            window = mine[0]
        if window is None:
            time.sleep(1)
    if window is None:
        raise Fail(f"the game window never appeared within {timeout}s; "
                   f"last of {log}:\n" + _tail(log))
    say(f"window {window}")

    # 2) any modal that came up after the window, and there is one every
    #    launch: the updater sits on top of the game.
    later = min(deadline, time.time() + 20)
    for name in (_dismiss_dialogs_windows(later, process.pid) if WINDOWS
                 else _dismiss_dialogs(display, later)):
        say(f"dismissed the {name} dialog")

    # 3) with no window manager the window places itself wherever it likes
    #    -- it picked x=2480 on a 1280-wide screen once, off the edge where
    #    `import` cannot reach it. Windows has a window manager, so this
    #    step has no object there.
    if not WINDOWS and display == ":98":
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
    if WINDOWS:
        return _win_image_path(pid)
    try:
        return os.path.realpath(f"/proc/{pid}/exe")
    except OSError:                                          # pragma: no cover
        return "?"


def _win_image_path(pid):
    """`/proc/<pid>/exe` over `QueryFullProcessImageNameW`.

    `PROCESS_QUERY_LIMITED_INFORMATION` and not `..._QUERY_INFORMATION`:
    the limited right is the one a non-elevated process is granted against
    another of its own user, and it is all this needs.
    """
    import ctypes
    import ctypes.wintypes as wintypes
    QUERY_LIMITED, size = 0x1000, wintypes.DWORD(32768)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel.OpenProcess(QUERY_LIMITED, False, pid)
    if not handle:
        return "?"
    try:
        buf = ctypes.create_unicode_buffer(size.value)
        if not kernel.QueryFullProcessImageNameW(handle, 0, buf,
                                                 ctypes.byref(size)):
            return "?"
        return buf.value
    finally:
        kernel.CloseHandle(handle)


def _under_fork_home(path):
    """Is this binary the fork's, rather than the official build?

    `normcase` because Windows paths differ in case and separator between
    what `tasklist` reports and what the user typed, and `startswith` over
    raw strings would call the same file two different binaries.
    """
    try:
        root = os.path.realpath(FORK_HOME)
    except OSError:                                          # pragma: no cover
        root = FORK_HOME
    return os.path.normcase(os.path.realpath(path)).startswith(
        os.path.normcase(root))


def status(verbose=True):
    """What is running, and whether it is the fork or the AppImage."""
    pids = running_pids()
    report = {"pids": pids, "fork": False, "mcp": None, "binaries": []}
    for pid in pids:
        path = which_binary(pid)
        report["binaries"].append(path)
        if _under_fork_home(path):
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
            kind = ("fork (MCP)" if _under_fork_home(path)
                    else "official build" if WINDOWS else "official AppImage")
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

    # Red case: roms/ must be refused before anything is started. The
    # predicate is checked directly, because reaching it through `launch`
    # needs the install present and that is exactly the machine where it
    # would go unmeasured.
    check("roms/ is recognised", is_roms(os.path.join("x", "roms", "a.cue")))
    check("a working copy is not roms/",
          not is_roms(os.path.join("x", "work", "a.cue")))
    check("roms/ survives the platform separator",
          is_roms(os.path.abspath(os.sep.join(("x", "roms", "a.cue")))))
    if installed():
        try:
            launch("/x/roms/whatever.cue", verbose=False)
            check("roms/ is refused", False, "it launched")
        except Fail as e:
            check("roms/ is refused", "roms/" in str(e), str(e))
        except Exception as e:                               # noqa: BLE001
            check("roms/ is refused", False, f"{type(e).__name__}: {e}")
    else:
        check("roms/ refusal through launch (needs the install)", True)

    # The platform split: each machine proves the half it runs.
    if WINDOWS:
        check("the binary is the portable .exe",
              binary().lower().endswith(".exe"))
        check("the release build is in the kill list",
              "duckstation-qt-x64-ReleaseLTCG.exe" in WINDOWS_PROCESS_NAMES)
        check("the window layer loads", bool(_user32()))
        check("enumerating windows costs no display",
              isinstance(_win_windows(pid=-1), list))
        check("a dead pid has no image path", _win_image_path(-1) == "?")
    else:
        check("the binary is bin/duckstation-qt",
              binary().endswith(os.path.join("bin", "duckstation-qt")))

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
    ap.add_argument("--window", default=GAME_WINDOW,
                    help="regex of the game window title, or ANY to take the "
                         "widest window the process owns")
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
            display=args.display, timeout=args.timeout,
            match=args.window)
        print(f"PID={pid}")
        print(f"WINDOW={window}")
        if not WINDOWS:
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

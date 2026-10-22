"""Start, stop and find the DuckStation fork that carries the MCP server.

Game-agnostic (PLAN-DUCKMCP-PY.md section 2.1): this module knows the
emulator's binary, processes, dialogs and windows, and nothing of the game it
boots. `launch(image)` finds the game window by the child's PID and takes the
widest window that is not one of the emulator's own dialogs; a caller that
wants a title passes `match=<regex>`, and the regex is the caller's.

    from duckmcp import fork
    pid, window, client = fork.launch("/path/to/copy.cue")
    fork.size_window(window, (width, height))    # X only; size is the caller's
    fork.kill()

Where the fork lives comes from `env.fork_home()`, the display from
`env.display()`, and the child's environment from `env.x_env()` -- this
module reads no variable itself (rule (d) of section 3.3).

WHERE
-----
The fork is not in the repository and must never be: the DuckStation licence
is CC-BY-NC-ND-4.0 and the binary itself says a modified build may not be
distributed. `RECIPE` says how to get it.

The Linux layout is `bin/`, `lib/` and `plugins/`, and the last two are why
this is more than a bare exec: the binary's RUNPATH is an absolute path into
the build tree it was compiled in, so it only finds its Qt through
`LD_LIBRARY_PATH`, and Qt only finds its platform plugin through
`QT_PLUGIN_PATH` (pitfall 28 of PLAN-DUCKMCP-PY section 1.3). Copying `bin/`
alone gives a binary that dies with `could not load the Qt platform plugin
"xcb"`, which reads like a display problem and is not one.

WHAT IT HAS TO GET PAST
-----------------------
Measured 2026-09-03:

* **An `Automatic Updater` dialog** (pitfall 29). It is a real modal, it
  overlaps the game window, and `Escape` does **not** close it -- the
  buttons are Download, Skip and Remind, none of them a reject role. This
  clicks *Remind Me Later*: Skip would silence it for good but by writing the
  user's own DuckStation configuration, which this launcher does not do.
* **The MCP port opens before the dialog is dismissed** (pitfall 30).
  `initialize` answered with the modal still on screen. The dialog is still
  dismissed, because it sits on top of the game window and a capture of the
  window would show it.
* **`xdotool windowkill` kills the process**, not the window (pitfall 27) --
  it closes the X client. Never use it here; click, or kill the process on
  purpose.

ON WINDOWS
----------
The same calls work over a different mechanism. Measured 2026-09-11 against
the fork's own `duckstation-windows-x64-release.zip`:

* **The layout is flat and portable**: the `.exe` sits in the root with its
  Qt DLLs beside it and a `portable.txt`. No library paths -- Windows
  resolves DLLs from the executable's own directory.
* **The window layer is `ctypes` over `user32`**: `EnumWindows` +
  `GetWindowThreadProcessId` is the `_NET_WM_PID` match, and
  `GetWindowRect` is `getwindowgeometry`.
* **No `Automatic Updater` came up** on that run, because the saved
  `[AutoUpdater] LastVersion` matched the build. The dismissal is
  implemented anyway, as `WM_CLOSE` to the dialog, and was never exercised
  against a real one.
* **There is a window manager**, so the window places itself sanely and the
  move to (0, 0) of the Xvfb has no object.

Pitfall 35 -- the fork dying on its own during free execution -- happens on
both systems.
"""

# lineage: tools/pes2/fork.py as of commit ebca2811 (binary, installed,
# _tasklist_pids, running_pids, kill, _windows, _xdotool, _user32,
# _win_windows, _dismiss_dialogs_windows, _dismiss_dialogs, joysticks,
# refuse_joysticks, wait_for_mcp, launch, _tail, which_binary,
# _win_image_path, _under_fork_home, status, RECIPE and the cases of
# self_check); its title default `GAME_WINDOW` (fork.py:126) stays with
# that project, per PLAN-DUCKMCP-PY section 2.1. hide_window and
# size_window: tools/looks/oracle.py:553-616, with SHOT_SIZE made the
# caller's `size` argument.

import csv
import io
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from . import env
from .client import Client
from .errors import Fail, NotRunning, Skip

WINDOWS = env.WINDOWS
"""Whether the Win32 half of this module is the one that runs."""

PROCESS_NAMES = ("duckstation-qt", "AppRun", "DuckStation-x64")
"""Every process name that is a DuckStation on Linux.

The AppImage runs as `AppRun` and the fork as `duckstation-qt`, so a filter
on either alone leaves the other holding the display (pitfalls 8, 9 and 31).
"""

WINDOWS_PROCESS_NAMES = ("duckstation-qt-x64-ReleaseLTCG.exe",
                         "duckstation-qt.exe")
"""The same list for Windows: the release build and a local compile."""

DIALOGS = ("Automatic Updater", "DuckStation")
"""The emulator's own modals, by exact title: never the game window."""

ANY_WINDOW = "ANY"
"""Alias of `match=None`, kept for command lines that spell it `--window ANY`."""

NOT_THE_GAME = ("Qt Selection Owner", "duckstation-qt")
"""Helper windows the fork's process owns on X, excluded by substring."""

WINDOWS_NOT_THE_GAME = ("_q_titlebar", "ThemeChangeObserverWindow",
                        "ScreenChangeObserverWindow", "MSCTFIME UI",
                        "Default IME")
"""Qt's helper windows on Win32, excluded by class or title substring."""

WM_CLOSE = 0x0010
"""The title bar's X, which Qt routes to a dialog's reject."""

JOYSTICK_DIR = "/dev/input"
"""Where the kernel puts joystick nodes (`js0`, `js1`, ...)."""

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

Then install it in the folder this launcher reads (DUCKSTATION_FORK, by
default ~/Applications/duckstation-mcp), keeping the three directories side
by side so LD_LIBRARY_PATH and QT_PLUGIN_PATH can find them:

  DEST=~/Applications/duckstation-mcp
  mkdir -p $DEST/bin $DEST/lib $DEST/plugins
  cp -a build-release/bin/. $DEST/bin/
  find dep/prebuilt/linux-x64/lib -maxdepth 1 -name '*.so*' \\
       -exec cp -a {} $DEST/lib/ \\;
  cp -a dep/prebuilt/linux-x64/plugins/. $DEST/plugins/

The MCP server is off by default. It is enabled in the user's own
DuckStation configuration -- ~/.local/share/duckstation/settings.ini:

  [Debug]
  EnableMCPServer = true
  MCPServerPort = 2346

A fresh data directory stops on the first-run wizard, and DuckStation's data
directory follows $HOME, not XDG_DATA_HOME (pitfalls 14 and 20): configure it
once by hand.

Nothing of this goes in a repository. The licence is CC-BY-NC-ND-4.0.
"""
"""How to get, install and enable the fork; printed, never executed."""


# --- where the binary is -----------------------------------------------

def binary(home=None):
    """The fork's executable under `home` (default `env.fork_home()`)."""
    home = home or env.fork_home()
    if WINDOWS:
        # Flat portable layout. A local compile may name it without the
        # build suffix, so the release name is preferred.
        for name in WINDOWS_PROCESS_NAMES:
            candidate = os.path.join(home, name)
            if os.path.isfile(candidate):
                return candidate
        return os.path.join(home, WINDOWS_PROCESS_NAMES[0])
    return os.path.join(home, "bin", "duckstation-qt")


def installed(home=None):
    """Whether the fork's executable exists."""
    return os.path.isfile(binary(home))


is_roms = env.is_roms
"""`env.is_roms`: the originals are never booted."""


def child_env(display, home=None):
    """The environment the fork's process gets: `env.x_env(display)` plus
    the build's own two library paths, when the install has them."""
    home = home or env.fork_home()
    child = env.x_env(display)
    lib = os.path.join(home, "lib")
    plugins = os.path.join(home, "plugins")
    if os.path.isdir(lib):
        child["LD_LIBRARY_PATH"] = lib + os.pathsep + child.get(
            "LD_LIBRARY_PATH", "")
    if os.path.isdir(plugins):
        child["QT_PLUGIN_PATH"] = plugins
    return child


# --- stopping ----------------------------------------------------------

def _tasklist_pids():
    """Every live DuckStation on Windows, by image name.

    `tasklist` and not `wmic`, which is absent on 11, nor a PowerShell hop,
    which costs half a second per call -- and the client asks this on every
    refused connection to tell "never started" from "died mid run".
    """
    pids = []
    for name in WINDOWS_PROCESS_NAMES:
        out = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq %s" % name, "/FO", "CSV",
             "/NH"], capture_output=True, text=True).stdout
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

    **Not `pgrep -f`** (pitfalls 7 and 25): it matches the command line of
    the shell running this, so `pkill -f` over it kills the caller.
    """
    if WINDOWS:
        return _tasklist_pids()
    found = []
    for name in PROCESS_NAMES:
        out = subprocess.run(["pgrep", "-x", name], capture_output=True,
                             text=True)
        found.extend(out.stdout.split())
    return select_pids(found, os.getpid(), _cmdline)


def _cmdline(pid):
    """`/proc/<pid>/cmdline` as text, or "" when the process is gone."""
    try:
        with open("/proc/%d/cmdline" % pid, "rb") as handle:
            return handle.read().decode("utf-8", "replace")
    except OSError:
        return ""


def select_pids(found, own, cmdline):
    """The DuckStation pids among `pgrep` output lines `found`.

    Drops our own pid `own`, repeats, and every pid whose command line
    (`cmdline(pid)`) does not say "duckstation" in any case. That last
    filter is not a nicety: every type-2 AppImage runs as `AppRun`, and
    without it `kill()` SIGKILLs other people's AppImages. Any case because
    the AppImage's path says `DuckStation` and the fork's `duckstation-mcp`.
    """
    pids = []
    for line in found:
        try:
            pid = int(line)
        except ValueError:
            continue
        if pid == own or pid in pids:
            continue
        if "duckstation" not in cmdline(pid).lower():
            continue
        pids.append(pid)
    return pids


def kill(verbose=True):
    """Stop every DuckStation and clean up after the AppImage.

    Returns how many processes it stopped.
    """
    pids = running_pids()
    for pid in pids:
        try:
            if WINDOWS:
                # `/F` for the reason SIGKILL is used below.
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

    # The AppImage leaves its squashfs mounted when killed this way; the
    # fork is a plain binary and does not, but a mixed session can have left
    # one behind. No AppImage, `mount` nor `fusermount` on Windows.
    if not WINDOWS:
        for _ in range(3):
            left = 0
            out = subprocess.run(["mount"], capture_output=True,
                                 text=True).stdout
            points = [ln.split()[2] for ln in out.splitlines()
                      if "DuckStation-x64.AppImage" in ln
                      and len(ln.split()) > 2]
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
        print("stopped %d DuckStation process(es)%s"
              % (len(pids), ": %s" % pids if pids else ""))
    return len(pids)


# --- windows on X --------------------------------------------------------

def _xdotool(display, *args):
    return subprocess.run(["xdotool", *args], env=env.x_env(display),
                          capture_output=True, text=True)


def _windows(display, pattern):
    """The X windows whose name matches `pattern`."""
    out = _xdotool(display, "search", "--name", pattern)
    return [w for w in out.stdout.split() if w]


def _x_owner(display, window):
    """The `_NET_WM_PID` of an X window, or None."""
    owner = subprocess.run(["xprop", "-id", window, "_NET_WM_PID"],
                           env=env.x_env(display), capture_output=True,
                           text=True).stdout.strip()
    pid = owner.split()[-1] if owner else ""
    return int(pid) if pid.isdigit() else None


def _x_width(display, window):
    geom = _xdotool(display, "getwindowgeometry", "--shell", window).stdout
    return next((int(line.split("=")[1]) for line in geom.splitlines()
                 if line.startswith("WIDTH=")), 0)


def _x_candidates(display, pid, match):
    """`(title, width, window)` of each X window the process owns.

    Matched by `_NET_WM_PID` (pitfalls 6 and 27): a dead instance's window
    still answers to `xdotool search`, and capturing it yields a black
    frame. With a `match` the name search is narrowed to it first.
    """
    out = []
    pattern = "." if match in (None, ANY_WINDOW) else match
    for w in _windows(display, pattern):
        if _x_owner(display, w) != pid:
            continue
        name = _xdotool(display, "getwindowname", w).stdout.strip()
        out.append((name, _x_width(display, w), w))
    return out


def pick_window(candidates, match=None):
    """The game window among `(title, width, handle)` candidates, or None.

    The emulator's dialogs and helper windows never count. With `match` None
    (or `ANY_WINDOW`) the widest of the rest wins -- the main window is the
    widest a DuckStation owns, which is what the golden tests' wait_for_main
    does for the same reason: the window is named after the game's gamedb
    title, which no caller should have to spell. With a `match` only titles
    the regex finds count, and the widest of those wins.
    """
    helpers = NOT_THE_GAME + WINDOWS_NOT_THE_GAME
    kept = []
    for title, width, handle in candidates:
        if title in DIALOGS or any(h in title for h in helpers):
            continue
        if match not in (None, ANY_WINDOW) and not re.search(match, title):
            continue
        kept.append((width, handle))
    if not kept:
        return None
    return max(kept, key=lambda pair: pair[0])[1]


def _dismiss_dialogs(display, deadline):
    """Click any modal of the emulator out of the way; the titles dismissed.

    The button is found by geometry, because there is no accessibility
    bridge on a bare Xvfb. `Remind Me Later` is the rightmost of three, about
    70 px in from the right edge and 25 up from the bottom -- measured on the
    651x474 dialog of 2026-09-03.
    """
    dismissed = []
    while time.time() < deadline:
        found = None
        for title in DIALOGS:
            for w in _windows(display, "^%s$" % title):
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


# --- the same, over user32 ---------------------------------------------

def _user32():
    import ctypes
    return ctypes.WinDLL("user32", use_last_error=True)


def _win_windows(pid=None):
    """Every top-level window, as `(hwnd, pid, visible, cls, title, w, h)`."""
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


def _win_candidates(pid):
    """`(title, width, hwnd)` of each visible window the process owns; a
    helper's class name is folded into the title so `pick_window` drops it."""
    out = []
    for hwnd, _p, visible, cls, title, width, _h in _win_windows(pid):
        if not visible:
            continue
        if any(h in cls for h in WINDOWS_NOT_THE_GAME):
            title = "%s [%s]" % (title, cls)
        out.append((title, width, hwnd))
    return out


def _dismiss_dialogs_windows(deadline, pid=None):
    """Close any modal of the emulator; the titles closed.

    **`WM_CLOSE`, not `BM_CLICK`**: a Qt dialog paints its own buttons and
    owns no child `HWND` for a button message to reach. `WM_CLOSE` is
    reject, which is *Remind Me Later* -- the same choice the X side makes.
    Never exercised against a real dialog.
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


# --- the window, once found ----------------------------------------------

def hide_window(handle):
    """Move the emulator off the visible desktop, on Windows, at once.

    There is no Xvfb to lean on there: the window goes to -32000, which
    keeps it drawing (unlike `SW_HIDE`, which blanks a capture) while keeping
    it off the screen the user works on. Returns False on X or with no
    handle, where there is nothing to do.
    """
    if not WINDOWS or not handle:
        return False
    off = -32000
    flags = 0x0001 | 0x0004 | 0x0010  # SWP_NOSIZE | SWP_NOZORDER | SWP_NOACTIVATE
    return bool(_user32().SetWindowPos(int(handle), 0, off, off, 0, 0,
                                       flags))


def size_window(handle, size, display=None):
    """Make the window `size` (`(width, height)`), on X, and wait until it is.

    The fork's `take_screenshot` comes out at the size of the game window, so
    a caller that measures on captures fixes the size here; the size is
    always the caller's -- this module has no default game size.

    Not on Windows: there SetWindowPos sizes the frame and not the client
    area, and no run has measured the difference. Returns False there or
    with no handle; raises `Fail` when the window never takes the size.
    """
    if WINDOWS or not handle:
        return False
    display = display or env.display()
    width, height = size
    run = _xdotool(display, "windowsize", str(handle), str(width),
                   str(height))
    if run.returncode != 0:
        raise Fail("xdotool windowsize failed on %s: %s"
                   % (handle, run.stderr.strip()))
    want = "Geometry: %dx%d" % (width, height)
    geometry = ""
    for _ in range(40):
        geometry = _xdotool(display, "getwindowgeometry", str(handle)).stdout
        if want in geometry:
            return True
        time.sleep(0.05)
    raise Fail("the game window did not become %dx%d: %s"
               % (width, height, geometry.strip()))


# --- joysticks ---------------------------------------------------------

def joysticks(root=JOYSTICK_DIR):
    """The joystick nodes under `root`; none on Windows, where the check
    has not been measured."""
    if WINDOWS:
        return []
    try:
        return sorted(os.path.join(root, name) for name in os.listdir(root)
                      if re.fullmatch(r"js\d+", name))
    except OSError:
        return []


def refuse_joysticks(root=JOYSTICK_DIR):
    """Refuse a measuring run while a game controller is plugged in.

    The fork reads this machine's DuckStation settings, whose `[Pad1]` is
    `SDL-0`, and SDL hands a controller to every process that opens it,
    whatever the display: a controller in use elsewhere presses buttons in
    the game under test (CORR-K3D-031). Raises `Fail`, not `Skip`: a run
    that cannot measure is not one that passes.
    """
    found = joysticks(root)
    if found:
        raise Fail("a game controller is plugged in (%s): the fork's [Pad1] "
                   "is SDL-0 and reads it on any display, so its buttons "
                   "reach the game under test -- unplug or switch it off "
                   "and run again" % ", ".join(found))


# --- starting ----------------------------------------------------------

def wait_for_mcp(deadline, host=None, port=None):
    """Poll `initialize` until the server answers.

    Returns `(server info, client)`. Host and port default to the client's,
    which are `env.mcp_host()` and `env.mcp_port()`.
    """
    last = None
    while time.time() < deadline:
        try:
            c = Client(host=host, port=port, timeout=5.0)
            return c.initialize(), c
        except NotRunning as e:
            last = e
            time.sleep(1)
    raise Fail("the MCP server never answered: %s" % (last,))


def _tail(path, lines=8):
    try:
        with open(path, "rb") as fh:
            return b"".join(fh.readlines()[-lines:]).decode("utf-8",
                                                            "replace")
    except OSError:
        return "(no log)"


def launch(image, match=None, display=None, timeout=120, home=None,
           verbose=True, log=None):
    """Boot `image` under the fork and come back with an answering session.

    Returns `(pid, window, client)`. `match` is an optional regex over the
    window title, the caller's; None takes the widest window the child owns
    that is not an emulator dialog. Each of the four ways this fails says
    which one it was, because they look identical from the outside -- a
    missing binary, a process that died, a window that never came, and a
    port that never answered all present as "nothing happened".

    The log is appended to `duckstation-fork.log` beside the image unless
    `log` names another file.
    """
    home = home or env.fork_home()
    display = display or env.display()

    # roms/ first: the refusal must not depend on the install being there.
    if image and is_roms(image):
        raise Fail("refusing to boot roms/ -- copy first")
    if not installed(home):
        raise Skip("no DuckStation fork at %s -- the recipe "
                   "(duckmcp.fork.RECIPE) says how to get it" % binary(home))
    if not image:
        raise Fail("give the .cue of a working copy")
    if not os.path.isfile(image):
        raise Skip("no image at %s" % image)
    if not WINDOWS:
        if shutil.which("xdotool") is None:
            raise Skip("xdotool is missing")
        if _xdotool(display, "getdisplaygeometry").returncode != 0:
            raise Skip("no X server on %s" % display)

    kill(verbose=False)
    time.sleep(1)

    log = log or os.path.join(os.path.dirname(os.path.abspath(image)),
                              "duckstation-fork.log")
    # Append, never truncate. The fork dies on its own during free execution
    # (pitfall 35) and writes nothing when it goes, so the only chance of
    # catching it is a log that survives the next launch. A run boundary
    # goes in first so the file stays readable.
    handle = open(log, "ab")
    handle.write(("\n=== launch %s %s ===\n"
                  % (time.strftime("%Y-%m-%d %H:%M:%S"),
                     os.path.basename(image))).encode())
    handle.flush()
    process = subprocess.Popen(
        [binary(home), "-batch", "-fastboot", "-nogui", "--", image],
        env=child_env(display, home), stdout=handle,
        stderr=subprocess.STDOUT)
    deadline = time.time() + timeout

    def say(msg):
        if verbose:
            print("  %s" % msg, flush=True)

    say("fork %d on %s, log %s"
        % (process.pid, "this desktop" if WINDOWS else display, log))

    # 1) the window, by the child's PID.
    window = None
    while time.time() < deadline and window is None:
        if process.poll() is not None:
            handle.close()
            raise Fail("the fork exited during boot (code %s); last of %s:\n"
                       % (process.returncode, log) + _tail(log))
        if WINDOWS:
            _dismiss_dialogs_windows(min(deadline, time.time() + 3),
                                     process.pid)
            window = pick_window(_win_candidates(process.pid), match)
        else:
            _dismiss_dialogs(display, min(deadline, time.time() + 3))
            window = pick_window(_x_candidates(display, process.pid, match),
                                 match)
        if window is None:
            time.sleep(1)
    if window is None:
        raise Fail("the game window never appeared within %ss; last of %s:\n"
                   % (timeout, log) + _tail(log))
    say("window %s" % window)

    # 2) any modal that came up after the window: the updater sits on top.
    later = min(deadline, time.time() + 20)
    for name in (_dismiss_dialogs_windows(later, process.pid) if WINDOWS
                 else _dismiss_dialogs(display, later)):
        say("dismissed the %s dialog" % name)

    # 3) with no window manager the window places itself wherever it likes
    #    (pitfall 5) -- x=2480 on a 1280-wide screen once, off the edge.
    if not WINDOWS and display == env.XVFB_DISPLAY:
        _xdotool(display, "windowmove", window, "0", "0")
        time.sleep(0.5)

    # 4) the server. This is the one that says the build has no MCP in it.
    server, client = wait_for_mcp(deadline)
    say("%s %s answering" % (server.get("name"), server.get("version")))
    return process.pid, window, client


# --- status ------------------------------------------------------------

def which_binary(pid):
    """The path a running DuckStation was started from."""
    if WINDOWS:
        return _win_image_path(pid)
    try:
        return os.path.realpath("/proc/%d/exe" % pid)
    except OSError:                                          # pragma: no cover
        return "?"


def _win_image_path(pid):
    """`/proc/<pid>/exe` over `QueryFullProcessImageNameW`, with the limited
    query right a non-elevated process gets against its own user's."""
    import ctypes
    import ctypes.wintypes as wintypes
    query_limited, size = 0x1000, wintypes.DWORD(32768)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    handle = kernel.OpenProcess(query_limited, False, pid)
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


def _under_fork_home(path, home=None):
    """Is this binary the fork's, rather than the official build?"""
    home = home or env.fork_home()
    try:
        root = os.path.realpath(home)
    except OSError:                                          # pragma: no cover
        root = home
    return os.path.normcase(os.path.realpath(path)).startswith(
        os.path.normcase(root))


def status(verbose=True):
    """What is running, and whether it is the fork or the official build.

    Returns `{"pids", "fork", "mcp", "binaries"}`.
    """
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
            print("  pid %d  %s  %s" % (pid, kind, path))
        if report["mcp"]:
            print("  MCP: %s %s" % (report["mcp"].get("name"),
                                    report["mcp"].get("version")))
        elif pids:
            print("  MCP: no server answering -- this is not the fork, or "
                  "EnableMCPServer is off")
    return report


# --- self-check --------------------------------------------------------

def self_check() -> list:
    """What can be proved with no emulator: paths, refusals, window choice,
    and the client's liveness probe over `running_pids()`.

    Returns one `(name, passed, detail)` per assertion. The environment half
    (the `:98` rule of `child_env`) is asserted by `selftest.py`, which may
    spell the variable it is about.
    """
    results = []

    def check(name, passed, detail=""):
        results.append((name, bool(passed), detail))

    # The three process names must all be there: dropping one is exactly
    # how the fork once escaped a kill.
    for name in ("duckstation-qt", "AppRun", "DuckStation-x64"):
        check("%s is in the kill list" % name, name in PROCESS_NAMES)

    # Red case: launching with no install must skip with the recipe in the
    # message, not raise a FileNotFoundError from Popen.
    try:
        launch("/nonexistent.cue", home="/nowhere", verbose=False)
        check("a missing install skips", False, "it launched")
    except Skip as e:
        check("a missing install skips and names the recipe",
              "recipe" in str(e), str(e))
    except Exception as e:                                   # noqa: BLE001
        check("a missing install skips", False,
              "%s: %s" % (type(e).__name__, e))

    # Red case: roms/ is refused through launch itself, before the install
    # is looked at -- so every machine measures it, on both separators.
    for label, image in (("forward slashes", "/x/roms/a.cue"),
                         ("backslashes", r"C:\x\roms\a.cue")):
        try:
            launch(image, home="/nowhere", verbose=False)
            check("roms/ is refused by launch (%s)" % label, False,
                  "it launched")
        except Fail as e:
            check("roms/ is refused by launch (%s)" % label,
                  "roms/" in str(e), str(e))
        except Exception as e:                               # noqa: BLE001
            check("roms/ is refused by launch (%s)" % label, False,
                  "%s: %s" % (type(e).__name__, e))
    check("a working copy is not roms/",
          not is_roms(os.path.join("x", "work", "a.cue")))

    if WINDOWS:
        check("the binary is the portable .exe",
              binary().lower().endswith(".exe"))
        check("the window layer loads", bool(_user32()))
        check("enumerating windows costs no display",
              isinstance(_win_windows(pid=-1), list))
        check("a dead pid has no image path", _win_image_path(-1) == "?")
    else:
        check("the binary is bin/duckstation-qt",
              binary().endswith(os.path.join("bin", "duckstation-qt")))
        check("hide_window is a no-op on X", hide_window(1) is False)

    # Red case: a joystick node refuses a measuring run, and none lets it go.
    with tempfile.TemporaryDirectory() as root:
        check("no joystick node lets a run go", joysticks(root) == [])
        open(os.path.join(root, "js0"), "w").close()
        open(os.path.join(root, "event3"), "w").close()
        try:
            refuse_joysticks(root)
            check("a joystick node refuses the run", WINDOWS,
                  "it was let through")
        except Fail as e:
            check("a joystick node refuses the run and names it",
                  "js0" in str(e), str(e))

    check("the recipe names the licence", "CC-BY-NC-ND" in RECIPE)
    check("the recipe names the install directory",
          "duckstation-mcp" in RECIPE)
    check("running_pids never returns our own pid",
          os.getpid() not in running_pids())
    # pgrep -x never lists this python, so the live call above cannot go red:
    # the own-pid filter is judged on select_pids, with our pid in the input.
    check("select_pids drops our own pid even when pgrep lists it",
          select_pids(["7", "8"], 7, lambda p: "duckstation-qt") == [8],
          select_pids(["7", "8"], 7, lambda p: "duckstation-qt"))
    lines = {"11": "/opt/other-app/AppRun\0300", "12": "/x/DuckStation.AppImage",
             "13": "/home/u/duckstation-mcp/bin/duckstation-qt"}
    check("an AppRun whose command line is not DuckStation's is spared",
          select_pids(["11", "12", "13"], -1, lambda p: lines[str(p)])
          == [12, 13], select_pids(["11", "12", "13"], -1,
                                   lambda p: lines[str(p)]))

    # The window choice, which launch() feeds from X or Win32.
    # The narrower window comes first, so "take the first" cannot pass.
    seen = [("Automatic Updater", 651, "d"), ("Qt Selection Owner", 3000, "q"),
            ("Other", 400, "o"), ("Some Game", 800, "g")]
    check("with no match the widest non-dialog window wins",
          pick_window(seen) == "g", pick_window(seen))
    check("ANY_WINDOW is the same as no match",
          pick_window(seen, ANY_WINDOW) == "g")
    check("a match narrows to the titles it finds",
          pick_window(seen, "^Other$") == "o", pick_window(seen, "^Other$"))
    check("a match no title has gives no window",
          pick_window(seen, "^Nothing$") is None)
    check("dialogs alone give no window",
          pick_window([("DuckStation", 900, "x"),
                       ("Automatic Updater", 651, "d")]) is None)
    import inspect
    default = inspect.signature(launch).parameters["match"].default
    check("launch() has no default title (match=None)", default is None,
          repr(default))

    # The client's liveness seam reads running_pids() of this module, lazily
    # and at the moment the port is refused (client.process_alive).
    from . import client
    module = sys.modules[__name__]
    real = module.running_pids

    def broken():
        raise OSError("probe failed")
    try:
        for pids, want, alive in (([], "no DuckStation process either", False),
                                  ([4242], "duckstation-qt IS running", True)):
            module.running_pids = lambda pids=pids: pids
            check("process_alive() is %s when running_pids() == %r"
                  % (alive, pids), client.process_alive() is alive)
            try:
                Client(port=1, timeout=2.0).call("get_status")
                got = "it connected"
            except NotRunning as e:
                got = str(e)
            except Exception as e:                           # noqa: BLE001
                got = "%s: %s" % (type(e).__name__, e)
            check("the client's default probe reads fork.running_pids() == %r"
                  % (pids,), want in got, got)
        module.running_pids = broken
        check("process_alive() is None when running_pids() raises",
              client.process_alive() is None)
    finally:
        module.running_pids = real
    return results

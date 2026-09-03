#!/usr/bin/env bash
# Launch PES2 under DuckStation on the headless display, ready to be driven.
#
# The recipe is short but almost none of it is guessable, so it lives here
# instead of in someone's shell history. Everything it does that is not
# obvious is a trap that cost time once; see docs/PLAN-PES2-PSX.md 6.11.
#
#   PES2_IMAGE     .cue of the working copy (required, except for --kill)
#   PES2_DISPLAY   X display, default :98 -- the one place the number lives.
#                  Set it to :1 to open on the user's own screen, which is
#                  for working *with* them and needs them to have asked;
#                  the cookie is kept in that case, and window placement is
#                  left to the window manager.
#   PES2_DATA      where the run's log goes; defaults to `ds-data` next to
#                  PES2_IMAGE. It is *not* a DuckStation data directory --
#                  see the note about configuration below.
#
# **This does not configure DuckStation, on purpose.** It used to write a
# whole settings.ini into an XDG_DATA_HOME of its own, and DuckStation never
# read a line of it: the AppImage resolves its data directory from $HOME.
# Twelve boots went into pressing keys bound to nothing before that was
# measured -- StartFullscreen = true in that file, and the window comes up
# 800x655. Overriding HOME does isolate it, but then the first boot stops on
# a nine-page setup wizard that SetupWizardIncomplete = false does not skip.
#
# The decision, taken by the user on 2026-09-02: **do not isolate.** This
# machine's DuckStation is for this project, so its own configuration is the
# one that runs, and writing a second one that nobody reads was worse than
# writing none -- it read as applied for a day. `drive.py` reads the [Pad1]
# bindings out of the file actually in force instead of declaring its own,
# so remapping a button in the DuckStation GUI is all it takes.
#
# Two consequences to know rather than to fix: save states and memory cards
# land in ~/.local/share/duckstation like any other session of it, and a
# leftover `SaveStateOnExit` writes a resume state after every run.
#
# Prints the PID and the window id, so a driver script can take it from here.
set -euo pipefail

DISPLAY_="${PES2_DISPLAY:-:98}"
APPIMAGE="${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage}"
IMAGE="${PES2_IMAGE:-}"


# A leftover instance is driven by mistake instead of the new one, and the
# result is a screenshot of the wrong game state.
#
# Matching this process is harder than it looks. `pkill -f DuckStation`
# matches the command line of the shell running it and kills the caller.
# And `pgrep -x DuckStation-x64` misses it: the AppImage runs as **AppRun**,
# so a name filter on the inner binary matches nothing while two live
# instances keep their windows on the display. Match every name, and never
# this script.
#
# **`duckstation-qt` is the third**, added 2026-09-03: the MCP fork is a
# plain binary rather than an AppImage, so it escaped both of the names
# above and an instance of it went on holding the display through a run of
# this launcher. `tools/pes2/fork.py kill` has the same list.
kill_leftovers() {
    local pid killed=""
    for pid in $(pgrep -x 'AppRun' 2>/dev/null || true) \
               $(pgrep -x 'DuckStation-x64' 2>/dev/null || true) \
               $(pgrep -x 'duckstation-qt' 2>/dev/null || true); do
        [ "$pid" = "$$" ] && continue
        # Case-insensitively, and that is not a nicety: the AppImage's path
        # says `DuckStation` and the fork's says `duckstation-mcp`, so the
        # exact-case version of this guard skipped every fork it had just
        # been taught to find.
        grep -qsi 'duckstation' "/proc/$pid/cmdline" || continue
        # SIGTERM leaves it parked on a "Confirm Exit" dialog forever,
        # holding its windows open, even with ConfirmPowerOff = false.
        kill -9 "$pid" 2>/dev/null || true
        killed="$killed $pid"
    done

    # Wait for them to actually go. Unmounting while a process still holds
    # the squashfs silently fails and leaves the mount behind -- which is
    # what happened the first time this ran.
    local waited=0
    while [ -n "${killed// /}" ] && [ "$waited" -lt 20 ]; do
        local alive=""
        for pid in $killed; do
            kill -0 "$pid" 2>/dev/null && alive="$alive $pid"
        done
        killed="$alive"
        [ -z "${killed// /}" ] && break
        sleep 0.5
        waited=$((waited + 1))
    done

    # The AppImage leaves its squashfs mounted when killed this way.
    local m attempt
    for attempt in 1 2 3; do
        local left=0
        for m in $(mount | awk '/DuckStation-x64.AppImage/{print $3}'); do
            fusermount -u "$m" 2>/dev/null || left=1
            rmdir "$m" 2>/dev/null || true
        done
        [ "$(mount | grep -c 'DuckStation-x64.AppImage')" -eq 0 ] && break
        sleep 1
    done
}
if [ "${1:-}" = "--kill" ]; then
    kill_leftovers
    echo "leftover DuckStation processes and mounts cleared"
    exit 0
fi

# Everything below this line needs an image, and everything below it also
# *writes*. `--kill` returned above without reaching any of it: it used to
# resolve DATA from an empty IMAGE -- `$(dirname "")/../ds-data` is
# `./../ds-data` -- and laid a directory in the parent of wherever it
# happened to be run from.
[ -n "$IMAGE" ] || { echo "set PES2_IMAGE to the .cue of a working copy" >&2; exit 1; }
[ -f "$IMAGE" ] || { echo "no image at $IMAGE" >&2; exit 1; }
[ -f "$APPIMAGE" ] || { echo "no DuckStation at $APPIMAGE" >&2; exit 1; }

# Absolute, and a sibling of the image rather than of its parent: the old
# default carried a `..` whose meaning changed with whether PES2_IMAGE was
# absolute or relative.
DATA="${PES2_DATA:-$(cd "$(dirname "$IMAGE")" && pwd)/ds-data}"

# The Xvfb of this project runs without -auth, so XAUTHORITY must be empty
# rather than inherited from the desktop session. Same rule as the rest of
# the repository -- see CLAUDE.md.
#
# **Except on the user's own display.** :1 is a real X server with a real
# cookie, and blanking XAUTHORITY there means the emulator cannot connect at
# all. Running there is the exception the repository rule asks to be asked
# about, and it exists for driving a session the user is watching -- see
# PES2_DISPLAY. The rule stands: nothing routine opens a window on :1.
export DISPLAY="$DISPLAY_"
if [ "$DISPLAY_" = ":98" ]; then
    export XAUTHORITY=""
fi

mkdir -p "$DATA"

kill_leftovers
sleep 1

"$APPIMAGE" -batch -fastboot -nogui -- "$IMAGE" >"$DATA/duckstation.log" 2>&1 &
PID=$!

# The AppImage asks to create a launcher shortcut the first time it sees a
# data directory it has not written before, and that dialog blocks the boot.
# With the machine's own DuckStation directory in use it should never show
# again; the handler stays because it costs nothing and its absence cost a
# boot once.
for _ in $(seq 1 30); do
    sleep 1
    dlg=$(xdotool search --name '^DuckStation$' 2>/dev/null | head -1 || true)
    if [ -n "$dlg" ]; then
        read -r dx dy <<<"$(xdotool getwindowgeometry "$dlg" |
            sed -n 's/.*Position: \([0-9]*\),\([0-9]*\).*/\1 \2/p')"
        xdotool mousemove $((dx + 82)) $((dy + 175)) click 1   # don't ask again
        xdotool mousemove $((dx + 380)) $((dy + 208)) click 1  # No
        break
    fi
    kill -0 "$PID" 2>/dev/null || { echo "DuckStation exited during boot" >&2; exit 1; }
done

# Match the window by _NET_WM_PID, not by name: a dead instance's window can
# still answer to xdotool search, and capturing it yields a black frame.
WIN=""
for _ in $(seq 1 60); do
    sleep 1
    for w in $(xdotool search --name '^Pro Evolution Soccer 2$' 2>/dev/null || true); do
        wp=$(xprop -id "$w" _NET_WM_PID 2>/dev/null | awk '{print $NF}')
        case "$wp" in ''|*[!0-9]*) continue ;; esac
        if kill -0 "$wp" 2>/dev/null; then WIN="$w"; break; fi
    done
    [ -n "$WIN" ] && break
done
[ -n "$WIN" ] || { echo "game window never appeared" >&2; exit 1; }

# With no window manager the window places itself wherever it likes, and it
# picked x=2480 on a 1280-wide screen -- off the edge, where `import` cannot
# reach it. Move it on screen before anyone tries to capture. On a display
# that has a window manager, leave placement to it.
if [ "$DISPLAY_" = ":98" ]; then
    xdotool windowmove "$WIN" 0 0
    sleep 1
fi

echo "PID=$PID"
echo "WINDOW=$WIN"
echo "DISPLAY=$DISPLAY_"
echo "LOG=$DATA/duckstation.log"
echo
echo "Drive it with the pointer inside the window -- there is no window"
echo "manager, so X focus is PointerRoot and keys go to whatever is under"
echo "the cursor:"
echo "    DISPLAY=$DISPLAY_ XAUTHORITY= xdotool mousemove 400 300"
echo "    DISPLAY=$DISPLAY_ XAUTHORITY= xdotool key Return"
echo "    DISPLAY=$DISPLAY_ XAUTHORITY= import -window $WIN shot.png"
echo
echo "Stop it with:  tools/pes2/run_duckstation.sh --kill"

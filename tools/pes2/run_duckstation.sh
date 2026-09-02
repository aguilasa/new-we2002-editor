#!/usr/bin/env bash
# Launch PES2 under DuckStation on the headless display, ready to be driven.
#
# The recipe is short but almost none of it is guessable, so it lives here
# instead of in someone's shell history. Everything it does that is not
# obvious is a trap that cost time once; see docs/PLAN-PES2-PSX.md 6.11.
#
#   PES2_IMAGE     .cue of the working copy (required, except for --kill)
#   PES2_DISPLAY   X display, default :98 -- the one place the number lives
#   PES2_DATA      isolated DuckStation data dir, absolute; defaults to
#                  `ds-data` next to PES2_IMAGE, so each working copy keeps
#                  its own memory cards and save states
#   PES2_BIOS      where to borrow the BIOS from, default
#                  ~/.local/share/duckstation/bios
#   PES2_PAD_TYPE  controller in port 1, default AnalogController. The other
#                  value worth passing is DigitalController -- see the note
#                  by [Pad1] below.
#
# Prints the PID and the window id, so a driver script can take it from here.
set -euo pipefail

DISPLAY_="${PES2_DISPLAY:-:98}"
APPIMAGE="${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage}"
IMAGE="${PES2_IMAGE:-}"
BIOS="${PES2_BIOS:-$HOME/.local/share/duckstation/bios}"
PAD_TYPE="${PES2_PAD_TYPE:-AnalogController}"

# A leftover instance is driven by mistake instead of the new one, and the
# result is a screenshot of the wrong game state.
#
# Matching this process is harder than it looks. `pkill -f DuckStation`
# matches the command line of the shell running it and kills the caller.
# And `pgrep -x DuckStation-x64` misses it: the AppImage runs as **AppRun**,
# so a name filter on the inner binary matches nothing while two live
# instances keep their windows on the display. Match both names, and never
# this script.
kill_leftovers() {
    local pid killed=""
    for pid in $(pgrep -x 'AppRun' 2>/dev/null || true) \
               $(pgrep -x 'DuckStation-x64' 2>/dev/null || true); do
        [ "$pid" = "$$" ] && continue
        grep -qs 'DuckStation' "/proc/$pid/cmdline" || continue
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
# `./../ds-data` -- and lay a whole DuckStation configuration in the parent
# of whatever directory it happened to be run from.
[ -n "$IMAGE" ] || { echo "set PES2_IMAGE to the .cue of a working copy" >&2; exit 1; }
[ -f "$IMAGE" ] || { echo "no image at $IMAGE" >&2; exit 1; }
[ -f "$APPIMAGE" ] || { echo "no DuckStation at $APPIMAGE" >&2; exit 1; }

# `ln -sfn` happily links to nothing. A dangling BIOS link shows up much
# later as DuckStation finding no BIOS at all and dying during the load,
# far from the cause -- exactly the shape of trap section 6.11 catalogues.
[ -d "$BIOS" ] || { echo "no BIOS directory at $BIOS" >&2; exit 1; }
ls "$BIOS"/* >/dev/null 2>&1 || { echo "no BIOS file in $BIOS" >&2; exit 1; }

# Absolute, and a sibling of the image rather than of its parent: the old
# default carried a `..` whose meaning changed with whether PES2_IMAGE was
# absolute or relative.
DATA="${PES2_DATA:-$(cd "$(dirname "$IMAGE")" && pwd)/ds-data}"

# The Xvfb of this project runs without -auth, so XAUTHORITY must be empty
# rather than inherited from the desktop session. Same rule as the rest of
# the repository -- see CLAUDE.md.
export DISPLAY="$DISPLAY_"
export XAUTHORITY=""

# **XDG_DATA_HOME does not isolate this AppImage, and believing it did cost
# a day.** It resolves its data directory from $HOME, so every run before
# 2026-09-02 used ~/.local/share/duckstation -- the user's own. Proved by
# setting StartFullscreen = true and getting an 800x655 window: the file
# below was never read, so DuckStation's *default* pad bindings were in
# force the whole time. Arrows and Enter worked because they are defaults;
# nothing this file said about the pad ever applied. It also wrote a resume
# save state into the user's directory.
#
# Overriding HOME does isolate it, and then the first boot stops on the
# nine-page setup wizard, which `SetupWizardIncomplete = false` does not
# skip -- measured with the flag present, with the resources seeded from a
# working install and with the BIOS as real files rather than a link. That
# is the open end; see PES2-TASK-03.
export XDG_DATA_HOME="$DATA"
DS="$XDG_DATA_HOME/duckstation"

mkdir -p "$DS"/{memcards,savestates,screenshots,cache}
# The BIOS stays where the user put it; we only borrow it.
ln -sfn "$BIOS" "$DS/bios"

# Written every run on purpose: this file is the whole configuration, and a
# half-written one fails in ways that look like emulator bugs. Two settings
# are load-bearing. Renderer=Software because Xvfb has no GPU and there is
# no -renderer on the command line. The [Pad1] keyboard bindings because
# DuckStation binds nothing by default here -- without them every keypress
# is silently dropped and the game sits in its attract loop forever.
#
# **And Tab working proved nothing.** Fast forward on Tab is DuckStation's
# *default* binding, so it kept working while this file was being ignored
# whole -- which is why the pad seemed dead for a dozen runs while the
# emulator plainly answered the keyboard. Three things were wrong with the
# file, all found by diffing it against the configuration the user drives
# by hand, which works:
#
#   - `SettingsVersion = 3` was stale. A version DuckStation does not
#     expect makes it reset the settings rather than read them.
#   - `DisableBackgroundInput` was unset, so its default applied. There is
#     no window manager on this display and the window never holds focus,
#     so the pad was being dropped as background input while hotkeys, which
#     do not go through that path, came through.
#   - `[InputSources] Keyboard = true` is not a key DuckStation writes.
#
# **And a letter is not a key name here.** `Keyboard/P` and `Keyboard/p`
# both failed to bind, tested against TogglePause -- which is the cheapest
# probe there is, since a pause is visible against the animated intro
# without reaching any particular screen. `Keyboard/F9` bound on the first
# try, and so did `UpArrow`, `DownArrow` and `Enter`. Special and function
# keys work; letters do not, whatever case they are written in. The
# configuration the user drives by hand does say `Cross = Keyboard/M`, but
# that file also has `SDL = true` and a full set of SDL-0 bindings, so its
# letters were very likely never exercised. Hence the face buttons on F5 to
# F8 -- which did not work either, because the function keys are where
# DuckStation keeps its own default hotkeys and they are consumed before
# the pad ever sees them. The names below were read out of the binary's own
# name table (`strings` over the extracted AppImage: UpArrow, Insert,
# Delete, Home, End, PageUp, PageDown, Backspace, Enter) rather than
# guessed. Only the names in that table bind: `X`, `P`, `Insert`, `Delete`
# and `Home` are not in it and never bound, which is what made the pad look
# dead for a dozen boots.
#
# **And a hotkey beats a pad binding.** `Keyboard/Space` is a valid name and
# is DuckStation's own pause key, so binding Cross to it paused the
# emulator instead of pressing a button -- visible as the pause glyph in
# the corner of the capture, and as every frame after it being identical.
# The letters below are all in the table and none of them is a hotkey.
#
# **The key names are DuckStation's, not X keysyms**, and the two disagree
# exactly where it hurts: the d-pad is `UpArrow`/`DownArrow`/`LeftArrow`/
# `RightArrow` here and `Up`/`Down`/`Left`/`Right` to xdotool, and Start is
# `Enter` here and `Return` there. A name DuckStation does not recognise
# does not become a binding and does not complain -- it logs nothing at all
# -- so every arrow press was dropped in silence, which is why no route
# past the title screen ever worked. Measured against the configuration the
# user drives by hand, which does work.
cat > "$DS/settings.ini" <<'INI'
[Main]
# Without these two the first run stops on the setup wizard and on the
# create-a-shortcut dialog, and no game window ever appears. They were
# invisible before 2026-09-02 because this file was not being read at all.
SetupWizardIncomplete = false
NoDesktopFile = true
ConfirmPowerOff = false
PauseOnFocusLoss = false
DisableBackgroundInput = false
SaveStateOnExit = false
StartFullscreen = false
InhibitScreensaver = false

[BIOS]
SearchDirectory = bios
PatchFastBoot = true

[GPU]
Renderer = Software

[Display]
VSync = false
SyncToHostRefreshRate = false

[Audio]
Backend = Null

[MemoryCards]
Card1Type = PerGame
Directory = memcards

[InputSources]
RawInput = false
SDL = false
XInput = false

[Pad1]
Type = AnalogController
Up = Keyboard/UpArrow
Down = Keyboard/DownArrow
Left = Keyboard/LeftArrow
Right = Keyboard/RightArrow
Cross = Keyboard/K
Circle = Keyboard/L
Square = Keyboard/J
Triangle = Keyboard/I
Start = Keyboard/Q
Select = Keyboard/Backspace
L1 = Keyboard/Q
R1 = Keyboard/E

[Hotkeys]
FastForward = Keyboard/Tab
LoadSelectedSaveState = Keyboard/F1
SaveSelectedSaveState = Keyboard/F2
SelectPreviousSaveStateSlot = Keyboard/F3
SelectNextSaveStateSlot = Keyboard/F4
TogglePause = Keyboard/F9
INI

# Substituted rather than interpolated: the heredoc is quoted so that no
# binding can be eaten by shell expansion, and one knob is not worth
# unquoting it for.
sed -i "s#^Type = AnalogController\$#Type = $PAD_TYPE#" "$DS/settings.ini"

kill_leftovers
sleep 1

"$APPIMAGE" -batch -fastboot -nogui -- "$IMAGE" >"$DATA/duckstation.log" 2>&1 &
PID=$!

# The AppImage asks to create a launcher shortcut the first time it sees a
# new XDG_DATA_HOME, and that dialog blocks the boot. Answer it if it shows.
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
# reach it. Move it on screen before anyone tries to capture.
xdotool windowmove "$WIN" 0 0
sleep 1

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

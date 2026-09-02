#!/usr/bin/env bash
# Drive PES2 under DuckStation to a named screen, and capture it.
#
# `run_duckstation.sh` boots the game and `boot_check.sh` proves it booted.
# This is the third step the plan's section 3.4 asks for: getting *to* a
# screen, because without an oracle the screen is the oracle (section 4.1)
# and a field is only mapped when a poke changes what it shows.
#
# The route is a list of steps, run in order:
#
#   wait:N     sleep N seconds
#   key:NAME   press NAME once -- an xdotool keysym, mapped by the
#              [Pad1] and [Hotkeys] bindings run_duckstation.sh writes
#   down:NAME  hold NAME down; up:NAME releases it. Fast forward is a
#              *hold* in DuckStation, not a toggle, so `key:Tab` does
#              nothing useful and `down:Tab … up:Tab` is what skips the
#              two minutes of intro
#   shot:LABEL capture the window into $OUTDIR/<label>.png
#   until:MEAN,SD,TOL,SECS
#              poll once a second until the frame's mean and standard
#              deviation are both within TOL of MEAN and SD, giving up
#              after SECS. This is how a route stops depending on the
#              clock: the intro is about two minutes of FMV whose length
#              varies with disc read speed and with fast forward, and a
#              fixed sleep either overshoots into the attract demo or
#              stops short. A screen has a signature; wait for it.
#
#   PES2_IMAGE     .cue of a working copy (required). Never roms/.
#   PES2_SCREEN    a named route, or use --route for one written inline
#   PES2_OUTDIR    where the PNGs go. They are frames of a commercial game,
#                  so they stay out of the repository like roms/ does.
#   PES2_DISPLAY   X display, default :98 -- run_duckstation.sh owns the
#                  number; this only passes it through
#
# Exits 77 -- ctest reads it as skipped -- when the machine cannot run it.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SKIP=77
skip() { echo "skipping: $*"; exit "$SKIP"; }
die() { echo "$*" >&2; exit 1; }

# The bindings run_duckstation.sh writes, kept here so a route reads as the
# pad button and not as the keyboard key underneath it.
#   Cross = X   Circle = C   Square = Z   Triangle = V
#   Start = Return   Select = BackSpace   L1 = Q   R1 = E
#   FastForward = Tab (held)   SaveState = F2   LoadState = F1
#
# **Cross is what skips the intro movie, not Start.** Three Returns during
# the opening FMV move nothing -- measured in PES2-TASK-29, and it reads
# like the emulator dropping input when it is really the game ignoring that
# particular button. MOVIE/WE2002.STR is 37 MB and runs about two minutes
# if nothing interrupts it.

ROUTE=""
SCREEN="${PES2_SCREEN:-}"
OUTDIR="${PES2_OUTDIR:-}"
IMAGE="${PES2_IMAGE:-}"

while [ $# -gt 0 ]; do
    case "$1" in
        --screen)  SCREEN="$2"; shift 2 ;;
        --route)   ROUTE="$2"; shift 2 ;;
        --out-dir) OUTDIR="$2"; shift 2 ;;
        --list)    sed -n 's/^route_\([a-z-]*\)() .*/  \1/p' "$0"; exit 0 ;;
        -*)        die "unknown option $1" ;;
        *)         IMAGE="$1"; shift ;;
    esac
done

# ---- the named routes ------------------------------------------------
#
# Times are seconds from launch and are deliberately generous: the disc is
# read through an emulated CD, and a route that only works on a warm page
# cache is not repeatable.

# The one route that is measured and repeatable: fast forward through the
# intro, then *wait for the title's signature* rather than for a clock.
# Five runs, five matches, means 0.5502..0.5528 and standard deviations
# 0.3397..0.3411 -- the spread is the sparkle animation, and it is an order
# of magnitude inside the 0.02 tolerance.
route_title() {
    echo "wait:6 down:Tab wait:25 up:Tab until:0.550,0.341,0.02,90 shot:title"
}

# NOT YET FOUND. Pressing Cross on the title does not reliably open the
# menu: across six runs it either left the title untouched or dropped back
# into the attract loop, and the one run that did reach a menu has not been
# reproduced. See the Log of PES2-TASK-03 for what was tried. Left here,
# failing loudly, rather than as a route that silently shoots the wrong
# screen.
route_main-menu() {
    die "the route into the menu is not established -- see PES2-TASK-03"
}

route_team-select() {
    die "the route into the menu is not established -- see PES2-TASK-03"
}

# ---- checks ----------------------------------------------------------

[ -n "$IMAGE" ] || die "usage: drive.sh <copy.cue> --screen NAME --out-dir DIR"
[ -f "$IMAGE" ] || skip "no image at $IMAGE"
case "$IMAGE" in */roms/*) die "refusing to boot roms/ -- copy first" ;; esac
[ -f "${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage}" ] ||
    skip "no DuckStation AppImage"
command -v import  >/dev/null || skip "ImageMagick import is missing"
command -v xdotool >/dev/null || skip "xdotool is missing"
DISPLAY="${PES2_DISPLAY:-:98}" XAUTHORITY= xdotool getdisplaygeometry >/dev/null 2>&1 ||
    skip "no X server on ${PES2_DISPLAY:-:98}"

if [ -z "$ROUTE" ]; then
    [ -n "$SCREEN" ] || die "give --screen NAME or --route \"steps\""
    declare -F "route_$SCREEN" >/dev/null || die "no route named $SCREEN"
    ROUTE="$(route_"$SCREEN")"
fi
OUTDIR="${OUTDIR:-$(mktemp -d -t pes2-drive-XXXXXX)}"
mkdir -p "$OUTDIR"

cleanup() { "$HERE/run_duckstation.sh" --kill >/dev/null 2>&1 || true; }
trap cleanup EXIT

export PES2_IMAGE="$IMAGE"
OUT="$("$HERE/run_duckstation.sh")"
WIN="$(sed -n 's/^WINDOW=//p' <<<"$OUT")"
export DISPLAY="$(sed -n 's/^DISPLAY=//p' <<<"$OUT")"
export XAUTHORITY=""
[ -n "$WIN" ] || die "no window id from the launcher"

geom() { xdotool getwindowgeometry "$WIN" | sed -n 's/.*Geometry: \([0-9]*x[0-9]*\).*/\1/p'; }
pos()  { xdotool getwindowgeometry "$WIN" |
         sed -n 's/.*Position: \([0-9]*\),\([0-9]*\).*/+\1+\2/p'; }

# Keyboard focus follows the pointer on a bare Xvfb -- there is no window
# manager to hand it over, and `xdotool key --window` goes through
# XSendEvent, which DuckStation ignores. Move the pointer in, then press
# without --window.
#
# **And the press has to be held.** `xdotool key X` is a press and release
# in the same instant, and the game never sees the button down: measured on
# the title screen, three taps -- plain, with windowfocus, with
# --clearmodifiers -- left the frame identical to six decimal places, and a
# keydown / 0.4 s / keyup went straight into the menu. A PSX game polls the
# pad once a frame; a tap can fall entirely between two polls. Nothing was
# wrong with the delivery, which is what three probes went looking for.
# One second, because that is what was measured. 0.4 s left the title
# screen unmoved; the probe that first got into the menu held for a full
# second. The game polls the pad once a frame and the title seems to want
# the button down across several of them.
PRESS_HOLD="${PES2_HOLD:-1.0}"
press() {
    # Both, and both matter. `windowfocus` calls XSetInputFocus, which is
    # what DuckStation reads the keyboard through; `windowactivate` is the
    # one that fails on a bare Xvfb, and the two are easy to confuse. The
    # pointer move is belt and braces for the PointerRoot case.
    xdotool windowfocus "$WIN" 2>/dev/null || true
    xdotool mousemove --window "$WIN" 20 20
    xdotool keydown "$1"
    sleep "$PRESS_HOLD"
    xdotool keyup "$1"
}

# The root window cropped to the game's geometry. `import -window <id>`
# fails with "Resource temporarily unavailable" whenever anything overlaps,
# which is trap 5 of section 6.11 and reads like a hung emulator.
shoot() { import -window root -crop "$(geom)$(pos)" +repage "$1"; }

echo "route: $ROUTE"
for step in $ROUTE; do
    case "$step" in
        wait:*) sleep "${step#wait:}" ;;
        key:*)  press "${step#key:}"; echo "  pressed ${step#key:}" ;;
        down:*) xdotool mousemove --window "$WIN" 20 20
                xdotool keydown "${step#down:}"; echo "  holding ${step#down:}" ;;
        up:*)   xdotool keyup "${step#up:}"; echo "  released ${step#up:}" ;;
        until:*)
                IFS=, read -r um usd utol usecs <<<"${step#until:}"
                echo "  waiting for mean=$um sd=$usd (+-$utol), up to ${usecs}s"
                hit=0
                for _ in $(seq 1 "$usecs"); do
                    shoot "$OUTDIR/.probe.png"
                    read -r m d <<<"$(identify -format '%[fx:mean] %[fx:standard_deviation]' "$OUTDIR/.probe.png")"
                    if awk -v m="$m" -v d="$d" -v um="$um" -v ud="$usd" -v t="$utol" \
                        'BEGIN{exit !((m-um<t&&um-m<t)&&(d-ud<t&&ud-d<t))}'; then
                        echo "    matched at mean=$m sd=$d"; hit=1; break
                    fi
                    sleep 1
                done
                [ "$hit" = 1 ] || die "never reached mean=$um sd=$usd in ${usecs}s" ;;
        shot:*) f="$OUTDIR/${step#shot:}.png"
                shoot "$f"
                echo "  shot ${step#shot:}  $f  $(identify -format '%[fx:mean] %[fx:standard_deviation]' "$f")" ;;
        *)      die "bad step: $step" ;;
    esac
done
echo "DRIVE OK: $OUTDIR"

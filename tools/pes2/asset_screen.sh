#!/usr/bin/env bash
# Shoot a series of frames from one image, so an asset edit can be seen.
#
# `boot_check.sh` proves the emulator is alive; this one is for looking at
# a *specific* screen. PES2-TASK-29 needs "the changed screen seen in the
# emulator" (section 4.1 -- the oracle is the game), and the screens an
# asset edit lands on are the early ones: the legal notice from LOGO.BIN
# and the title from TITLE.BIN, both before any menu. So no navigation is
# needed and PES2-TASK-03 is not on the path.
#
#   PES2_IMAGE     .cue of a working copy (required -- never roms/)
#   PES2_SHOTDIR   where the frames go. Frames of a commercial game, so
#                  they stay out of the repository like roms/ does.
#   PES2_AT        space-separated seconds to shoot at, default the first
#                  forty seconds of boot
#   PES2_SKIP      space-separated seconds at which to press Start, to get
#                  past the intro movie. The movie is MOVIE/WE2002.STR, 37
#                  MB of it, and without a press the title screen is still
#                  minutes away.
#
# Exits 77 -- ctest reads it as skipped -- when the machine cannot run it.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHOTDIR="${PES2_SHOTDIR:-$(mktemp -d -t pes2-screen-XXXXXX)}"
AT="${PES2_AT:-6 10 14 18 22 26 30 34 38}"

SKIP=77
skip() { echo "skipping: $*"; exit "$SKIP"; }

[ -n "${PES2_IMAGE:-}" ] || skip "PES2_IMAGE is not set"
[ -f "${PES2_IMAGE}" ]   || skip "no image at $PES2_IMAGE"
case "$PES2_IMAGE" in */roms/*) echo "refusing to boot roms/ -- copy first" >&2; exit 1 ;; esac
[ -f "${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage}" ] ||
    skip "no DuckStation AppImage"
command -v import >/dev/null || skip "ImageMagick import is missing"
command -v xdotool >/dev/null || skip "xdotool is missing"
DISPLAY="${PES2_DISPLAY:-:98}" XAUTHORITY= xdotool getdisplaygeometry >/dev/null 2>&1 ||
    skip "no X server on ${PES2_DISPLAY:-:98}"

mkdir -p "$SHOTDIR"
cleanup() { "$HERE/run_duckstation.sh" --kill >/dev/null 2>&1 || true; }
trap cleanup EXIT

OUT="$("$HERE/run_duckstation.sh")"
WIN="$(sed -n 's/^WINDOW=//p' <<<"$OUT")"
export DISPLAY="$(sed -n 's/^DISPLAY=//p' <<<"$OUT")"
export XAUTHORITY=""
[ -n "$WIN" ] || { echo "no window id from the launcher" >&2; exit 1; }

geom() { xdotool getwindowgeometry "$WIN" | sed -n 's/.*Geometry: \([0-9]*x[0-9]*\).*/\1/p'; }
pos() { xdotool getwindowgeometry "$WIN" |
        sed -n 's/.*Position: \([0-9]*\),\([0-9]*\).*/+\1+\2/p'; }

# The root window, cropped -- `import -window <id>` fails whenever anything
# overlaps, which is the trap CLAUDE.md records for the MFC editor too.
# The pointer carries keyboard focus on a bare Xvfb -- there is no window
# manager to hand it over, and `xdotool key --window` goes through
# XSendEvent, which DuckStation ignores. So: move the pointer into the
# window, then press without --window. CLAUDE.md records the same trap.
press() {
    xdotool mousemove --window "$WIN" 20 20
    xdotool key Return
}

SKIP_AT="${PES2_SKIP:-5 8 11}"
last=0
for t in $SKIP_AT; do
    sleep "$(( t - last ))"; last="$t"
    press
    echo "$t s  pressed Start"
done

for t in $AT; do
    [ "$t" -gt "$last" ] || continue
    sleep "$(( t - last ))"
    last="$t"
    f="$SHOTDIR/at-$(printf '%02d' "$t").png"
    import -window root -crop "$(geom)$(pos)" +repage "$f"
    echo "$t s  $f  $(identify -format '%[fx:mean] %[fx:standard_deviation]' "$f")"
done
echo "SHOTS OK: $SHOTDIR"

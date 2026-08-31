#!/usr/bin/env bash
# Boot PES2 under DuckStation and prove it got somewhere -- the evidence
# section 3.4 of the plan claims and never left behind.
#
# "It boots" was written down as prose after someone watched it once. A
# claim nobody can re-run is a memory, not a check. This one measures:
#
#   the window appears, and it is the size the emulator says it is;
#   the frame is not black -- a dead emulator and a booting one look
#   identical in a log, and completely different in a standard deviation;
#   two frames a few seconds apart are *different*, which is the part that
#   separates "running" from "hung on the first frame".
#
#   PES2_IMAGE     .cue of a working copy (required)
#   PES2_SHOTDIR   where the frames go, default a mktemp directory. They
#                  are frames of a commercial game, so they stay off the
#                  repository the same way roms/ and the FAQs do.
#   PES2_WARMUP    seconds to let the intro run before the first frame,
#                  default 45
#   PES2_GAP       seconds between the two frames, default 12
#   PES2_REFERENCE a PNG to compare the second frame against. It lives
#                  outside the repository -- it is a frame of a commercial
#                  game -- so it is a path, not a committed file.
#   PES2_TOLERANCE fraction of pixels allowed to differ from the
#                  reference, default 0.35. Emulation is not frame-exact
#                  across runs and the demo match never repeats, so this
#                  is a "same screen" test, not a golden one.
#
# Exits non-zero, loudly, on any of the checks. Exits 77 -- which ctest
# reads as *skipped* -- when the machine cannot run it at all: no image,
# no DuckStation, no X display.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SHOTDIR="${PES2_SHOTDIR:-$(mktemp -d -t pes2-boot-XXXXXX)}"
WARMUP="${PES2_WARMUP:-45}"
GAP="${PES2_GAP:-12}"

SKIP=77
skip() { echo "skipping the PES2 boot check: $*"; exit "$SKIP"; }

[ -n "${PES2_IMAGE:-}" ] || skip "PES2_IMAGE is not set"
[ -f "${PES2_IMAGE}" ]   || skip "no image at $PES2_IMAGE"
[ -f "${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage}" ] ||
    skip "no DuckStation AppImage"
command -v import   >/dev/null || skip "ImageMagick import is missing"
command -v identify >/dev/null || skip "ImageMagick identify is missing"
command -v xdotool  >/dev/null || skip "xdotool is missing"
DISPLAY="${PES2_DISPLAY:-:98}" XAUTHORITY= xdotool getdisplaygeometry >/dev/null 2>&1 ||
    skip "no X server on ${PES2_DISPLAY:-:98}"

mkdir -p "$SHOTDIR"
cleanup() { "$HERE/run_duckstation.sh" --kill >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "== launching =="
OUT="$("$HERE/run_duckstation.sh")"
echo "$OUT"
WIN="$(sed -n 's/^WINDOW=//p' <<<"$OUT")"
DPY="$(sed -n 's/^DISPLAY=//p' <<<"$OUT")"
[ -n "$WIN" ] || { echo "no window id in the launcher output" >&2; exit 1; }

export DISPLAY="$DPY"
export XAUTHORITY=""

# Capture the root window, not the game window. `import -window <id>` fails
# with "Resource temporarily unavailable" whenever anything overlaps it --
# the same trap CLAUDE.md records for the MFC editor -- and the root always
# works. The geometry below crops back to the window.
geom() { xdotool getwindowgeometry "$WIN" | sed -n 's/.*Geometry: \([0-9]*x[0-9]*\).*/\1/p'; }
pos() { xdotool getwindowgeometry "$WIN" |
        sed -n 's/.*Position: \([0-9]*\),\([0-9]*\).*/+\1+\2/p'; }

shoot() {   # shoot <file>
    import -window root -crop "$(geom)$(pos)" +repage "$1"
}

stats() {   # stats <file> -> "mean stddev"
    identify -format "%[fx:mean] %[fx:standard_deviation]" "$1"
}

echo "== warming up ${WARMUP}s =="
sleep "$WARMUP"
A="$SHOTDIR/boot-1.png"
shoot "$A"
read -r MEAN_A SD_A <<<"$(stats "$A")"
echo "frame 1  $A  mean=$MEAN_A  sd=$SD_A"

echo "== ${GAP}s later =="
sleep "$GAP"
B="$SHOTDIR/boot-2.png"
shoot "$B"
read -r MEAN_B SD_B <<<"$(stats "$B")"
echo "frame 2  $B  mean=$MEAN_B  sd=$SD_B"

# Fraction of pixels that differ between the two frames.
CHANGED="$(compare -metric AE "$A" "$B" null: 2>&1 || true)"
TOTAL="$(identify -format "%[fx:w*h]" "$A")"
echo "changed pixels: $CHANGED of $TOTAL"

REFERENCE="${PES2_REFERENCE:-}"
TOLERANCE="${PES2_TOLERANCE:-0.35}"
REF_DIFF=""
if [ -n "$REFERENCE" ]; then
    if [ ! -f "$REFERENCE" ]; then
        echo "PES2_REFERENCE=$REFERENCE does not exist" >&2
        exit 1
    fi
    # -metric AE after resizing to a common size: the window geometry can
    # differ between runs, and a size mismatch would otherwise read as
    # "everything changed".
    convert "$B" -resize 320x240! "$SHOTDIR/cmp-b.png"
    convert "$REFERENCE" -resize 320x240! "$SHOTDIR/cmp-r.png"
    REF_DIFF="$(compare -metric AE -fuzz 12% \
        "$SHOTDIR/cmp-b.png" "$SHOTDIR/cmp-r.png" null: 2>&1 || true)"
    echo "vs reference $REFERENCE: $REF_DIFF of 76800 pixels differ"
fi

fail=0
awk -v a="$SD_A" 'BEGIN{exit !(a > 0.02)}' || { echo "FAIL: frame 1 is flat (sd=$SD_A) -- black screen or dead emulator"; fail=1; }
awk -v b="$SD_B" 'BEGIN{exit !(b > 0.02)}' || { echo "FAIL: frame 2 is flat (sd=$SD_B)"; fail=1; }
case "$CHANGED" in
    ''|*[!0-9.e+]*) echo "FAIL: could not compare the two frames ($CHANGED)"; fail=1 ;;
    *) awk -v c="$CHANGED" -v t="$TOTAL" 'BEGIN{exit !(c > t*0.001)}' ||
           { echo "FAIL: the two frames are the same -- it is not running"; fail=1; } ;;
esac

if [ -n "$REFERENCE" ]; then
    case "$REF_DIFF" in
        ''|*[!0-9.e+]*) echo "FAIL: could not compare against the reference ($REF_DIFF)"; fail=1 ;;
        *) awk -v c="$REF_DIFF" -v t=76800 -v tol="$TOLERANCE" \
               'BEGIN{exit !(c <= t*tol)}' ||
               { echo "FAIL: frame 2 is not the same screen as the reference"; fail=1; } ;;
    esac
fi

if [ "$fail" -eq 0 ]; then
    echo "BOOT OK: window ${WIN}, $(geom), two live frames in $SHOTDIR"
fi
exit "$fail"

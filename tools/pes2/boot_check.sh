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
#   PES2_GAP       seconds the liveness sampling spans, default 12. One
#                  frame a second is taken across it and the largest
#                  difference from frame 1 decides -- see the note by the
#                  loop for why it is not two frames any more.
#   PES2_REFERENCE a PNG to compare the second frame against. It lives
#                  outside the repository -- it is a frame of a commercial
#                  game -- so it is a path, not a committed file.
#   PES2_TOLERANCE fraction of pixels allowed to differ from the
#                  reference, default 0.35. Emulation is not frame-exact
#                  across runs and the demo match never repeats, so this
#                  is a "same screen" test, not a golden one.
#   PES2_BINARY    `fork`, `appimage`, or unset. Unset prefers the fork and
#                  falls back to the AppImage -- see below.
#
# **Which emulator this judges, and why it is not one of them.** The fork
# `sadnescity/duckstation` is the working binary of this project since
# 2026-09-03 (section 6.14), and it is what this prefers. The official
# AppImage is what a third party can reproduce, and it stays as the
# fallback. Either way the run *says which one it was*: a boot check that
# does not name its binary cannot be compared with the one before it. The
# two binaries agree on every frame *mean* measured (section 6.14), and the
# title screen's standard deviation reproduces under neither -- it moved
# 0.019 on the untouched AppImage from one day to the next, which is why it
# was retired as a criterion. A number nobody judges by is a reason to
# record the binary, not to trust the frame.
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

# judge <sd_a> <sd_b> <changed> <total> <samples> <gap>
#
# The verdict, as a function, so `--self-check` can drive it with no emulator.
# It prints its FAILs and returns 1 if any fired. A gate whose red case has
# never been seen is decoration -- and this one's red case is the awkward
# sort, because producing it for real means a dead emulator.
judge() {
    local sd_a="$1" sd_b="$2" changed="$3" total="$4" samples="$5" gap="$6"
    local bad=0
    awk -v a="$sd_a" 'BEGIN{exit !(a > 0.02)}' ||
        { echo "FAIL: frame 1 is flat (sd=$sd_a) -- black screen or dead emulator"; bad=1; }
    awk -v b="$sd_b" 'BEGIN{exit !(b > 0.02)}' ||
        { echo "FAIL: frame 2 is flat (sd=$sd_b)"; bad=1; }
    case "$changed" in
        ''|*[!0-9.e+]*)
            echo "FAIL: could not compare the frames ($changed)"; bad=1 ;;
        # Say what was measured, not the conclusion. "It is not running" is
        # an inference; all this knows is that nothing moved across the
        # window it watched.
        *) awk -v c="$changed" -v t="$total" 'BEGIN{exit !(c > t*0.001)}' ||
               { echo "FAIL: no sample differed from frame 1 across ${gap}s ($samples samples, largest diff $changed of $total) -- a dead emulator looks like this, and so does a still screen that outlasted the window"; bad=1; } ;;
    esac
    return "$bad"
}

self_check() {
    local bad=0
    ok() { echo "  ok   $1"; }
    no() { echo "  FAIL $1"; bad=1; }

    # A live boot: something moved.
    judge 0.20 0.23 260000 524000 12 12 >/dev/null &&
        ok "a moving picture passes" || no "a moving picture passes"
    # The measured failure of 2026-09-03: content on screen, nothing moving.
    judge 0.13657 0.13657 0 524000 12 12 >/dev/null &&
        no "a frozen picture is refused" || ok "a frozen picture is refused"
    # A black screen, which is the dead-emulator case the flat test catches.
    judge 0.0 0.0 0 524000 12 12 >/dev/null &&
        no "a black screen is refused" || ok "a black screen is refused"
    # Movement just under the threshold: 0.1% of the frame is the line.
    judge 0.20 0.23 524 524000 12 12 >/dev/null &&
        no "movement at exactly the threshold is refused" ||
        ok "movement at exactly the threshold is refused"
    judge 0.20 0.23 525 524000 12 12 >/dev/null &&
        ok "movement just over it passes" || no "movement just over it passes"
    # A comparison that produced nothing usable.
    judge 0.20 0.23 "" 524000 12 12 >/dev/null &&
        no "an unusable comparison is refused" ||
        ok "an unusable comparison is refused"

    # And the measurement path itself, not just the arithmetic: two identical
    # images must compare to 0, two different ones must not.
    if command -v convert >/dev/null && command -v compare >/dev/null; then
        local t; t="$(mktemp -d -t pes2-boot-self-XXXXXX)"
        convert -size 64x64 gradient:black-white "$t/a.png"
        cp "$t/a.png" "$t/same.png"
        convert -size 64x64 gradient:white-black "$t/other.png"
        [ "$(compare -metric AE "$t/a.png" "$t/same.png" null: 2>&1)" = "0" ] &&
            ok "two copies of one frame compare to 0" ||
            no "two copies of one frame compare to 0"
        [ "$(compare -metric AE "$t/a.png" "$t/other.png" null: 2>&1)" != "0" ] &&
            ok "two different frames do not" || no "two different frames do not"
        rm -rf "$t"
    else
        echo "  ..   ImageMagick missing, skipping the comparison path"
    fi

    if [ "$bad" -eq 0 ]; then
        echo "SELF-CHECK OK: the verdict, its red cases and the comparison"
    else
        echo "SELF-CHECK FAILED"
    fi
    return "$bad"
}

if [ "${1:-}" = "--self-check" ]; then
    self_check
    exit $?
fi

# Two families of variable live side by side in this project -- WE2002_PES2_*
# for the disc tools, PES2_* for the emulator ones -- and the `ctest` recipe
# only carried the first for a while. The result was this gate reporting the
# same `Skipped` for "you set the other one" as for "this machine has no
# emulator", so a full run of the documented recipe printed 100% passed with
# the only gate that puts the game on screen never having run. Say which.
if [ -z "${PES2_IMAGE:-}" ]; then
    if [ -n "${WE2002_PES2_IMAGE:-}" ]; then
        skip "PES2_IMAGE is not set -- WE2002_PES2_IMAGE is, but this gate wants the .cue of a working copy, not the Track 1 .bin"
    fi
    skip "PES2_IMAGE is not set"
fi
[ -f "${PES2_IMAGE}" ]   || skip "no image at $PES2_IMAGE"
case "${PES2_IMAGE}" in
    *.cue) : ;;
    *) skip "PES2_IMAGE points at ${PES2_IMAGE##*/} -- this gate wants the .cue of a working copy, which is what the emulator opens, not a track .bin" ;;
esac

# Pick the binary before anything else: which one is available decides the
# launcher, the cleanup and the line this prints at the end.
BINARY="${PES2_BINARY:-}"
if [ -z "$BINARY" ]; then
    if python3 "$HERE/fork.py" which >/dev/null 2>&1; then
        BINARY=fork
    else
        BINARY=appimage
    fi
fi
case "$BINARY" in
    fork)
        python3 "$HERE/fork.py" which >/dev/null 2>&1 ||
            skip "no DuckStation fork -- see tools/pes2/fork.py recipe"
        LAUNCH=(python3 "$HERE/fork.py" launch "$PES2_IMAGE")
        KILL=(python3 "$HERE/fork.py" kill)
        WHICH="the fork ($(python3 "$HERE/fork.py" which | head -1))"
        ;;
    appimage)
        [ -f "${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage}" ] ||
            skip "no DuckStation AppImage"
        LAUNCH=("$HERE/run_duckstation.sh")
        KILL=("$HERE/run_duckstation.sh" --kill)
        WHICH="the official AppImage (${PES2_DUCKSTATION:-$HOME/Applications/DuckStation-x64.AppImage})"
        ;;
    *) echo "PES2_BINARY must be fork or appimage, not $BINARY" >&2; exit 1 ;;
esac

command -v import   >/dev/null || skip "ImageMagick import is missing"
command -v identify >/dev/null || skip "ImageMagick identify is missing"
command -v xdotool  >/dev/null || skip "xdotool is missing"
DISPLAY="${PES2_DISPLAY:-:98}" XAUTHORITY= xdotool getdisplaygeometry >/dev/null 2>&1 ||
    skip "no X server on ${PES2_DISPLAY:-:98}"

mkdir -p "$SHOTDIR"
cleanup() { "${KILL[@]}" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "== launching $WHICH =="
OUT="$("${LAUNCH[@]}")"
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

# Liveness, sampled rather than guessed at.
#
# This used to be one more frame `PES2_GAP` seconds later, and "they differ"
# was the proof of life. That assertion is only sound if the screen those two
# instants land on *animates*, and a PSX opening is mostly static screens
# whose timing shifts from run to run: when both samples fell inside one of
# them the gate declared "it is not running" about a perfectly live emulator.
# Measured 2026-09-03, one failure in three consecutive runs of the same
# command -- both frames byte-identical, 0 of 524000 pixels, at sd=0.13657,
# which is drawn content and not a black screen.
#
# It is pitfall 32 of section 6.11 inverted: there the risk is waiting for
# stillness on a screen that animates, here it is demanding movement from one
# that does not. Both come from treating the clock as if it said which screen
# you are on. So sample once a second across the gap and keep the largest
# difference any of them has from the first frame: a boot that is running
# crosses out of whatever still screen it is on, and one still screen no
# longer decides the verdict.
TOTAL="$(identify -format "%[fx:w*h]" "$A")"
CHANGED=0
SAMPLES=0
B="$SHOTDIR/boot-2.png"
echo "== sampling once a second for ${GAP}s =="
for _ in $(seq 1 "$GAP"); do
    sleep 1
    shoot "$B"
    SAMPLES=$((SAMPLES + 1))
    d="$(compare -metric AE "$A" "$B" null: 2>&1 || true)"
    case "$d" in
        ''|*[!0-9.e+]*) : ;;
        *) awk -v d="$d" -v c="$CHANGED" 'BEGIN{exit !(d > c)}' &&
               CHANGED="$d" ;;
    esac
done
read -r MEAN_B SD_B <<<"$(stats "$B")"
echo "frame 2  $B  mean=$MEAN_B  sd=$SD_B  (last of $SAMPLES samples)"
echo "changed pixels: $CHANGED of $TOTAL  (largest over $SAMPLES samples)"

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
judge "$SD_A" "$SD_B" "$CHANGED" "$TOTAL" "$SAMPLES" "$GAP" || fail=1

if [ -n "$REFERENCE" ]; then
    case "$REF_DIFF" in
        ''|*[!0-9.e+]*) echo "FAIL: could not compare against the reference ($REF_DIFF)"; fail=1 ;;
        *) awk -v c="$REF_DIFF" -v t=76800 -v tol="$TOLERANCE" \
               'BEGIN{exit !(c <= t*tol)}' ||
               { echo "FAIL: frame 2 is not the same screen as the reference"; fail=1; } ;;
    esac
fi

if [ "$fail" -eq 0 ]; then
    echo "BOOT OK: $WHICH, window ${WIN}, $(geom), $((SAMPLES + 1)) live frames in $SHOTDIR"
fi
exit "$fail"

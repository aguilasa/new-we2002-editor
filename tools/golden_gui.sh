#!/usr/bin/env bash
# Drive the Qt port through one open -> "Write into CD image" cycle, the same
# way tools/golden_run.sh drives ed.exe.
#
#   tools/golden_gui.sh /path/to/copy-of-image.bin [/path/to/newWe2002]
#
# The image is edited IN PLACE. Always pass a copy -- each one is ~474 MB.
#
# This is the phase 5 counterpart of golden_run.sh. Phase 3 proved the core
# writes what ed.exe writes; what this proves is that the widget layer in
# between does not change the answer -- that no signal fires during loading and
# writes a stale field back, and that the write button really does reach
# Database::Save. It is the reason the port takes an image path on the command
# line at all.
#
# Everything happens on DISPLAY=:98 (see CLAUDE.md). Never :1; that is the
# user's real session.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export DISPLAY="${GOLDEN_DISPLAY:-:98}"

if [ $# -lt 1 ]; then
    echo "uso: $0 <imagem.bin> [binario]   (copia! o arquivo e editado no lugar)" >&2
    exit 2
fi

IMAGE="$(readlink -f "$1")"
APP="${2:-$REPO/build/src/app/newWe2002}"
[ -f "$IMAGE" ] || { echo "$0: nao existe: $IMAGE" >&2; exit 1; }
[ -x "$APP" ] || { echo "$0: falta $APP (compile primeiro)" >&2; exit 1; }

# The dialog is 1077 px wide and the Xvfb screen is 960, so the right-hand
# edge is clipped. Every control this script touches is on the left, which is
# why that does not matter -- the same clipping applies to ed.exe.
#
# Coordinates are window-relative and come from ed.rc via the same DLU
# conversion tools/rc2ui.py uses: 6/4 px across, 13/8 px down.
dlu_x() { echo $(( $1 * 6 / 4 )); }
dlu_y() { echo $(( $1 * 13 / 8 )); }
# CMB_WRITE: "Write into CD image", at 145,312 and 130x18 DLU.
WRITE_X=$(( $(dlu_x 145) + $(dlu_x 130) / 2 ))
WRITE_Y=$(( $(dlu_y 312) + $(dlu_y 18) / 2 ))

APP_PID=""
cleanup() {
    if [ -n "$APP_PID" ]; then
        kill "$APP_PID" 2>/dev/null || true
        wait "$APP_PID" 2>/dev/null || true
    fi
}
trap cleanup EXIT

"$APP" "$IMAGE" >/dev/null 2>&1 &
APP_PID=$!

# Windows are matched by size, not by title: the main dialog and every message
# box share one. 1077x547 is the dialog's own geometry, transcribed from the
# .rc, so anything that big is the main window and anything smaller is a box.
#
# The candidates are restricted to windows this process owns, via the
# _NET_WM_PID Qt sets. Size alone is not enough: an editor left open on the
# display has a dialog of exactly the same size, and driving that one produces a
# byte diff that reads like a port bug. golden_check.sh also refuses to start in
# that situation; this is the second half of the same guard.
find_window() {   # find_window <min_w> <min_h> [max_w]
    local min_w="$1" min_h="$2" max_w="${3:-99999}" id geo w h
    for id in $(xdotool search --pid "$APP_PID" 2>/dev/null); do
        geo="$(xdotool getwindowgeometry "$id" 2>/dev/null | grep -o 'Geometry: [0-9]*x[0-9]*')"
        [[ "$geo" =~ ([0-9]+)x([0-9]+) ]] || continue
        w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
        if [ "$w" -ge "$min_w" ] && [ "$h" -ge "$min_h" ] && [ "$w" -le "$max_w" ]; then
            printf '0x%x' "$id"
            return 0
        fi
    done
    return 1
}

wait_for_window() {  # wait_for_window <min_w> <min_h> <max_w> <seconds>
    local i id
    for ((i = 0; i < $4 * 4; i++)); do
        if id="$(find_window "$1" "$2" "$3")" && [ -n "$id" ]; then
            printf '%s' "$id"
            return 0
        fi
        sleep 0.25
    done
    return 1
}

# The size warning. It only appears when the image is not exactly 474.431.328
# bytes -- which every dump on hand is not -- so a miss is not an error.
if wait_for_window 300 60 900 15 >/dev/null; then
    echo "gui: dispensando o aviso de tamanho"
    # QMessageBox puts its default button bottom-right; Return activates it
    # without having to know where that is.
    # Sent to whatever has focus rather than to $BOX by id: the box is modal
    # so it does have focus, and by the time the event lands the window may
    # already be gone, which makes an id-addressed XSendEvent a fatal BadWindow.
    xdotool key --clearmodifiers Return 2>/dev/null || true
    sleep 1
fi

MAIN="$(wait_for_window 1000 500 99999 30)" || {
    echo "gui: dialogo principal nao apareceu" >&2
    exit 1
}
echo "gui: dialogo principal $MAIN"

if [ -n "${GOLDEN_GUI_EDIT:-}" ]; then
    echo "gui: aplicando GOLDEN_GUI_EDIT"
    eval "$GOLDEN_GUI_EDIT"
fi

echo "gui: gravando"
xdotool mousemove --window "$MAIN" "$WRITE_X" "$WRITE_Y" click 1

# The write takes a few seconds on a 474 MB image; the confirmation box is the
# signal that it finished.
if ! wait_for_window 150 60 900 180 >/dev/null; then
    echo "gui: a confirmacao nao apareceu -- gravacao falhou?" >&2
    exit 1
fi
xdotool key --clearmodifiers Return 2>/dev/null || true
sleep 1
echo "gui: gravado"

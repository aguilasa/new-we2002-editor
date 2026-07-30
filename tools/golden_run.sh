#!/usr/bin/env bash
# Drive the original ed.exe through one open -> "Write into CD image" cycle,
# so its output can be diffed against this port's. ed.exe is the oracle for
# the phase 3 golden tests: where the two disagree, the port is wrong until
# proven otherwise.
#
#   tools/golden_run.sh /path/to/copy-of-image.bin
#
# The image is edited IN PLACE. Always pass a copy -- each one is ~474 MB.
#
# Everything happens on DISPLAY=:99 (see CLAUDE.md). Never :1; that is the
# user's real session.
#
# There is no scripting interface: ed.exe is an MFC dialog, so the sequence is
# driven with xdotool. It is stable because the layout is fixed at compile
# time -- the button coordinates below come straight out of the .rc.

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ED_DIR="$REPO/Debug"
WINE_BIN="${WINE_BIN:-/home/ingmar/.var/app/com.usebottles.bottles/data/bottles/runners/soda-9.0-1/bin}"
export DISPLAY="${GOLDEN_DISPLAY:-:99}"
export WINEDEBUG=-all

if [ $# -ne 1 ]; then
    echo "uso: $0 <imagem.bin>   (copia! o arquivo e editado no lugar)" >&2
    exit 2
fi

IMAGE="$(readlink -f "$1")"
[ -f "$IMAGE" ] || { echo "$0: nao existe: $IMAGE" >&2; exit 1; }
[ -x "$ED_DIR/ed.exe" ] || [ -f "$ED_DIR/ed.exe" ] || {
    echo "$0: $ED_DIR/ed.exe ausente -- e o oraculo, precisa ficar no disco" >&2
    exit 1
}

# A prefix of our own. Sharing one would be a bug waiting to happen: ed.cpp
# calls COleObjectFactory::UpdateRegistryAll(), which writes to the registry.
export WINEPREFIX="${WINEPREFIX:-$(mktemp -d)/prefix}"
OWN_PREFIX=0
if [ ! -d "$WINEPREFIX" ]; then
    mkdir -p "$WINEPREFIX"
    OWN_PREFIX=1
    "$WINE_BIN/wineboot" -i >/dev/null 2>&1 || true
fi

cleanup() {
    "$WINE_BIN/wineserver" -k >/dev/null 2>&1 || true
    if [ "$OWN_PREFIX" = 1 ] && [ "${GOLDEN_KEEP_PREFIX:-0}" != 1 ]; then
        rm -rf "$WINEPREFIX"
    fi
}
trap cleanup EXIT

# Wine maps the host root at Z:.
win_path() { printf 'Z:%s' "$(printf '%s' "$1" | tr '/' '\\')"; }

# ed.rc gives every control in dialog units. IDD_ED_DIALOG is FONT 8 "MS Sans
# Serif", whose base units are 6x13, so a DLU is 6/4 px across and 13/8 px
# down -- which is how the 718x337 DLU dialog comes out 1077x548 px.
dlu_x() { echo $(( $1 * 6 / 4 )); }
dlu_y() { echo $(( $1 * 13 / 8 )); }

# XSetInputFocus fails with BadMatch on a window that is not yet viewable, and
# xdotool turns that into a fatal X error. Wine maps its windows a beat after
# creating them, so wait for the map before touching focus.
focus() {
    local id="$1" i
    for ((i = 0; i < 40; i++)); do
        if xwininfo -id "$id" 2>/dev/null | grep -q "IsViewable"; then
            xdotool windowfocus "$id" 2>/dev/null && return 0
        fi
        sleep 0.25
    done
    echo "$0: nao consegui focar a janela $id" >&2
    return 1
}

# Wait until a window whose title matches $1 exists; echo its id.
wait_for_title() {
    local want="$1" tries="${2:-60}" i id name
    for ((i = 0; i < tries; i++)); do
        while read -r id; do
            name="$(xdotool getwindowname "$id" 2>/dev/null || true)"
            if [[ "$name" == "$want" ]]; then
                printf '%s' "$id"
                return 0
            fi
        done < <(xdotool search --name '.*' 2>/dev/null || true)
        sleep 1
    done
    return 1
}

# The main dialog carries no window title, so it cannot be found by name. It
# is the only large window Wine owns; match on size instead.
wait_for_main() {
    local tries="${1:-60}" i id
    for ((i = 0; i < tries; i++)); do
        id="$(xwininfo -root -children 2>/dev/null |
              awk '$0 ~ /[0-9]+x[0-9]+\+/ {
                       match($0, /([0-9]+)x([0-9]+)\+/, m)
                       if (m[1] > 500 && m[2] > 400) { print $1; exit }
                   }')"
        if [ -n "$id" ]; then
            printf '%s' "$id"
            return 0
        fi
        sleep 1
    done
    return 1
}

echo "oraculo: $IMAGE"
( cd "$ED_DIR" && "$WINE_BIN/wine64" ed.exe >/dev/null 2>&1 ) &

# 1. "IMAGE CD SELECTION" -- the CFileDialog that OnInitDialog opens before
#    the main window exists (edDlg.cpp: aprifilebin).
DLG="$(wait_for_title 'IMAGE CD SELECTION')" || {
    echo "$0: o dialogo de abertura nao apareceu" >&2; exit 1; }
focus "$DLG"
xdotool mousemove --window "$DLG" 378 445 click 1   # the "File name:" box
sleep 1
xdotool type --delay 15 "$(win_path "$IMAGE")"
sleep 1
xdotool key Return

# 2. ed.exe hardcodes one expected image length (474.431.328) and complains
#    about anything else. It is a warning, not a refusal -- it loads anyway.
if WARN="$(wait_for_title 'ed' 10)"; then
    focus "$WARN"
    xdotool key Return
fi

# 3. The main dialog, once carica_dabin() has finished reading.
MAIN="$(wait_for_main 90)" || {
    echo "$0: o dialogo principal nao apareceu" >&2; exit 1; }

# 4. Optional edits, so the golden test can cover more than a no-op write.
#    GOLDEN_EDIT is shell run with $MAIN in scope and DISPLAY already set;
#    dlu_x/dlu_y convert control coordinates straight out of ed.rc.
#
#      GOLDEN_EDIT='
#        xdotool mousemove --window $MAIN $(dlu_x 48) $(dlu_y 37) click 1
#        xdotool key --clearmodifiers ctrl+a; xdotool type GOLDEN
#      ' tools/golden_run.sh copy.bin
#
sleep 2
if [ -n "${GOLDEN_EDIT:-}" ]; then
    focus "$MAIN"
    eval "$GOLDEN_EDIT"
    sleep 1
fi

# 5. "Write into CD image". PUSHBUTTON CMB_WRITE,145,312,130,18 in DLU; with
#    the dialog's 8pt MS Sans Serif that is 6/4 and 13/8 pixels per DLU, so
#    the centre lands at (210*6/4, 321*13/8) = (315, 521).
focus "$MAIN"
xdotool mousemove --window "$MAIN" 315 521
sleep 1
xdotool click 1

# 6. "CD image edited !" is the only confirmation that the write finished.
DONE="$(wait_for_title 'ed' 180)" || {
    echo "$0: a gravacao nao confirmou" >&2; exit 1; }
focus "$DONE"
xdotool key Return
sleep 2

echo "oraculo: gravado"

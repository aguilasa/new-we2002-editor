# Prelúdio comum aos roteiros da §8.7 que este lote acrescenta.
#
# Concatenado ANTES de cada roteiro da seção; não roda sozinho. Os dois hooks
# (GOLDEN_EDIT e GOLDEN_GUI_EDIT) recebem o par prelúdio+roteiro sem alteração.
# Os roteiros do `Escape` de papel (8.7-escape-papel*.sh) são anteriores a este
# arquivo e trazem o próprio par_click -- não os concatene com este prelúdio.

par_click() {   # par_click <x> <y> <w> <h>  -- no MainDialog
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}
par_type() {    # par_type <texto>
    xdotool key --clearmodifiers End;        sleep 0.4
    xdotool key --clearmodifiers shift+Home; sleep 0.4
    xdotool key --clearmodifiers BackSpace;  sleep 0.4
    xdotool type --delay 40 "$1";            sleep 0.4
}

# O DefaultTacticsDialog é janela própria, de 481x297 px -- a quarta geometria
# desta série, depois do MainDialog, dos 493x323 do PlayerSkillsDialog (§8.4) e
# dos 390x404 do PlayerSelectDialog (§8.5).
tact_win() {
    local id geo w h
    for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        geo="$(xdotool getwindowgeometry "$id" 2>/dev/null)" || continue
        [[ "$geo" =~ Geometry:\ ([0-9]+)x([0-9]+) ]] || continue
        w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
        if [ "$w" -ge 460 ] && [ "$w" -le 500 ] && [ "$h" -ge 280 ] && [ "$h" -le 315 ]; then
            printf '%s' "$id"; return 0
        fi
    done
    return 1
}
tct_click() {   # tct_click <x> <y> <w> <h>  -- dentro do DefaultTacticsDialog
    xdotool mousemove --window "$TCT" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}

# Time: Nation 1 - Ireland.
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers Home;             sleep 1
xdotool key --clearmodifiers Down;             sleep 1
xdotool key --clearmodifiers Return;           sleep 2

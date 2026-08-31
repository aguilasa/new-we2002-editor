# Prelúdio comum aos roteiros da §8.8 -- bandeira e uniformes.
#
# Concatenado ANTES de cada roteiro da seção; não roda sozinho.

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

# O FlagKitDialog é janela própria, de 358x315 px -- a quinta geometria desta
# série. A faixa é estreita de propósito: o PlayerSelectDialog da §8.5 tem 390
# de largura, e um filtro largo pegaria o errado.
flag_win() {
    local id geo w h
    for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        geo="$(xdotool getwindowgeometry "$id" 2>/dev/null)" || continue
        [[ "$geo" =~ Geometry:\ ([0-9]+)x([0-9]+) ]] || continue
        w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
        if [ "$w" -ge 340 ] && [ "$w" -le 375 ] && [ "$h" -ge 300 ] && [ "$h" -le 330 ]; then
            printf '%s' "$id"; return 0
        fi
    done
    return 1
}
fk_click() {    # fk_click <x> <y> <w> <h>  -- dentro do FlagKitDialog
    xdotool mousemove --window "$FK" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}

# Time: PAR_TEAM Down a partir do "---" (1 = Nation 1 - Ireland, o padrão).
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers Home;             sleep 1
par_i=0
while [ "$par_i" -lt "${PAR_TEAM:-1}" ]; do
    xdotool key --clearmodifiers Down;         sleep 0.05
    par_i=$(( par_i + 1 ))
done
sleep 0.6
xdotool key --clearmodifiers Return;           sleep 2

# CMD_FLAG_KIT (190,173,100,18), rotulado "Flag - Shirt preview".
par_click 190 173 100 18;                      sleep 2
FK="$(flag_win)" || { echo "par: FlagKitDialog nao abriu" >&2; }

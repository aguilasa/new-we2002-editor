# Prelúdio comum aos roteiros da §8.4 -- os que editam no PlayerSkillsDialog.
#
# Este arquivo é concatenado ANTES de cada roteiro da seção, e não roda
# sozinho. Os dois hooks (GOLDEN_EDIT e GOLDEN_GUI_EDIT) recebem o par
# prelúdio+roteiro sem alteração; ambos exportam $MAIN e definem dlu_x/dlu_y.

par_click() {   # par_click <x> <y> <w> <h>  -- no MainDialog
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}
par_type() {    # par_type <texto>
    xdotool key --clearmodifiers End;        sleep 0.5
    xdotool key --clearmodifiers shift+Home; sleep 0.5
    xdotool key --clearmodifiers BackSpace;  sleep 0.5
    xdotool type --delay 40 "$1";            sleep 0.5
}

# O PlayerSkillsDialog é JANELA PRÓPRIA, de 493x323 px, e as coordenadas dos
# seus 21 campos no controls.json são relativas A ELE, não ao MainDialog.
# Por isso os cliques lá dentro precisam de --window "$SKILLS".
skills_win() {
    local id geo w h
    for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        geo="$(xdotool getwindowgeometry "$id" 2>/dev/null)" || continue
        [[ "$geo" =~ Geometry:\ ([0-9]+)x([0-9]+) ]] || continue
        w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
        if [ "$w" -ge 460 ] && [ "$w" -le 530 ] && [ "$h" -ge 300 ] && [ "$h" -le 350 ]; then
            printf '%s' "$id"; return 0
        fi
    done
    return 1
}
sk_click() {    # sk_click <x> <y> <w> <h>  -- dentro do PlayerSkillsDialog
    xdotool mousemove --window "$SKILLS" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}

# Time: Nation 1 - Ireland. Home antes do Down torna a escolha independente do
# estado inicial; o Return confirma e o formulário troca de time.
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers Home;             sleep 1
xdotool key --clearmodifiers Down;             sleep 1
xdotool key --clearmodifiers Return;           sleep 2

# CMD_SKILLS1 (382,32,20,9) abre o diálogo do 1º jogador.
par_click 382 32 20 9;                         sleep 2
SKILLS="$(skills_win)" || { echo "par: PlayerSkillsDialog nao abriu" >&2; }

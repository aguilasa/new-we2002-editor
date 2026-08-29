# Prelúdio comum aos roteiros da §8.5 -- os que trocam o jogador de um slot.
#
# Concatenado ANTES de cada roteiro da seção; não roda sozinho. Os dois hooks
# (GOLDEN_EDIT e GOLDEN_GUI_EDIT) recebem o par prelúdio+roteiro sem alteração.

par_click() {   # par_click <x> <y> <w> <h>  -- no MainDialog
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}

# O PlayerSelectDialog é JANELA PRÓPRIA, de 390x404 px, e as coordenadas dos
# seus controles no controls.json são relativas A ELE. Diferente do
# PlayerSkillsDialog da §8.4 (493x323), então o filtro de tamanho é outro.
select_win() {
    local id geo w h
    for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        geo="$(xdotool getwindowgeometry "$id" 2>/dev/null)" || continue
        [[ "$geo" =~ Geometry:\ ([0-9]+)x([0-9]+) ]] || continue
        w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
        if [ "$w" -ge 370 ] && [ "$w" -le 415 ] && [ "$h" -ge 380 ] && [ "$h" -le 425 ]; then
            printf '%s' "$id"; return 0
        fi
    done
    return 1
}
sel_click() {   # sel_click <x> <y> <w> <h>  -- dentro do PlayerSelectDialog
    xdotool mousemove --window "$SEL" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}
# Item de lista, POR TECLADO. As listas não têm coordenada por linha no
# manifesto, e calcular a altura da linha erraria: o Qt e o MFC não desenham a
# mesma. Clicar na lista para dar-lhe o foco, Home para ancorar no primeiro
# item -- sem ele "Down" significa "o próximo", que depende do que já estava
# selecionado -- e então N vezes Down. É a mesma lição do CMB_TEAM na §8.1.
sel_row() {     # sel_row <x> <y> <w> <h> <indice_zero_based>
    sel_click "$1" "$2" "$3" "$4";       sleep 0.8
    xdotool key --clearmodifiers Home;   sleep 0.5
    local i=0
    while [ "$i" -lt "$5" ]; do
        xdotool key --clearmodifiers Down; sleep 0.25
        i=$(( i + 1 ))
    done
    sleep 0.5
}

# Que time abrir, no CMB_TEAM (142,7,137,12):
#   PAR_TIME=nacional  (padrão) -> Nation 1 - Ireland, o 1º item depois do "---"
#   PAR_TIME=ml                 -> o último clube de Master League
#   PAR_TIME=allstar            -> "All Stars", o 1º slot de all-star
#
# Para o nacional, `Home` antes do `Down` ancora no primeiro; sem ele "Down"
# significa "o próximo", que depende do estado inicial. Para o ML, `End` cai em
# "Master League (default)", que é um item especial de campos desabilitados --
# um `Up` a partir dele dá o último clube real.
par_click 142 7 137 12;                        sleep 2
if [ "${PAR_TIME:-nacional}" = ml ]; then
    xdotool key --clearmodifiers End;          sleep 1
    xdotool key --clearmodifiers Up;           sleep 1
elif [ "${PAR_TIME:-nacional}" = allstar ]; then
    # 55 Down a partir do "---": os 54 nacionais e então "All Stars".
    # Medido em 2026-08-29 -- 58 dá "France" e 60 "Italy", que são os
    # all-star por região, não as seleções de mesmo nome já passadas.
    xdotool key --clearmodifiers Home;         sleep 1
    par_i=0
    while [ "$par_i" -lt 55 ]; do
        xdotool key --clearmodifiers Down;     sleep 0.05
        par_i=$(( par_i + 1 ))
    done
    sleep 0.6
else
    xdotool key --clearmodifiers Home;         sleep 1
    xdotool key --clearmodifiers Down;         sleep 1
fi
xdotool key --clearmodifiers Return;           sleep 2

# CMD_SWAP1 (405,32,20,9) abre a troca do 1º slot.
par_click 405 32 20 9;                         sleep 2
SEL="$(select_win)" || { echo "par: PlayerSelectDialog nao abriu" >&2; }

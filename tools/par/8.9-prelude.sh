# Prelúdio comum aos roteiros da §8.9 -- as operações em massa.
#
# Concatenado ANTES de cada roteiro da seção; não roda sozinho.
#
# Os três botões desta seção que dá para exercitar abrem a caixa
# "Operation done!" -- e **nem todos abrem**: o CMD_UPDATE_COSTS abre, o
# CMB_EDITALLLOOK e o CMB_EDITALLBARS não. Quem abre precisa da dispensa: sem isso ela fica na
# frente do CMB_WRITE, o clique de gravar não chega, e o `wait_for_window` do
# golden_gui.sh toma ESSA caixa pela confirmação de gravação -- imprime
# "gravado" e o arquivo sai intacto. Os dois lados se comportam assim, então o
# golden fica verde sem ter medido nada. Ver §8.2.
#
# Quem NÃO abre caixa **não deve chamar `dispensa_modal` de jeito nenhum**, nem
# com `|| true`. Duas razões, as duas medidas em 2026-09-01:
#
#  1. a função devolve 1 se não achar caixa, e os dois scripts do golden rodam
#     com `set -euo pipefail` -- sem `|| true` o roteiro aborta antes de gravar
#     e o golden falha sem imprimir motivo nenhum;
#  2. e com `|| true` é pior: sob Wine os controles do MFC são janelas X de
#     verdade, e vários caem na faixa que o `acha_modal` procura (206x80,
#     148x82). Ele acha um CONTROLE, clica nele, e a gravação do oráculo não
#     acontece -- a cópia sai IDENTICAL enquanto o port grava, e o golden acusa
#     o port por uma divergência que é do roteiro.

par_click() {   # par_click <x> <y> <w> <h>  -- no MainDialog
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}

acha_modal() {  # imprime "<id> <w> <h>", ou nada
    local id geo w h
    for id in $(xdotool search --onlyvisible --name '.*' 2>/dev/null); do
        geo="$(xdotool getwindowgeometry "$id" 2>/dev/null)" || continue
        [[ "$geo" =~ Geometry:\ ([0-9]+)x([0-9]+) ]] || continue
        w="${BASH_REMATCH[1]}"; h="${BASH_REMATCH[2]}"
        if [ "$w" -ge 100 ] && [ "$w" -le 900 ] &&
           [ "$h" -ge 60 ]  && [ "$h" -le 400 ]; then
            printf '%s %s %s' "$id" "$w" "$h"
            return 0
        fi
    done
    return 1
}

# `Return` não serve para fechar: fecha a QMessageBox do port e NÃO fecha a do
# MFC sob Wine. Clicar no botão funciona nos dois, mas a caixa do oráculo e a
# do Qt põem o OK em alturas diferentes -- daí a varredura de pontos.
dispensa_modal() {
    local i info id w h fx fy passe ponto
    for ((i = 0; i < 40; i++)); do
        info="$(acha_modal)" && break
        sleep 0.25
    done
    [ -n "${info:-}" ] || return 1
    for passe in 1 2 3; do
        for ponto in "50 40" "77 75" "50 75" "50 85"; do
            info="$(acha_modal)" || return 0      # já fechou
            set -- $info; id="$1"; w="$2"; h="$3"
            set -- $ponto; fx="$1"; fy="$2"
            xdotool mousemove --window "$id" \
                $(( w * fx / 100 )) $(( h * fy / 100 )) click 1
            sleep 1
        done
    done
    acha_modal >/dev/null && return 1
    return 0
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

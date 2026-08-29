# PARIDADE-FUNCIONAL §8.2, item 3 -- CMD_DEFAULT_NUMBERS.
#
# Estímulo: o botão "pl. n° = team n°" (CMD_NUMDEF no .rc), que percorre os
# times de seleção e copia o número de camisa de cada slot para o `number` do
# jogador que o ocupa. É GLOBAL: não depende de time selecionado, e por isso
# este roteiro não seleciona nenhum.
#
# Este arquivo é o trecho de shell que os DOIS hooks recebem sem alteração:
#   GOLDEN_EDIT     -> tools/golden_run.sh (o ed.exe sob Wine)
#   GOLDEN_GUI_EDIT -> tools/golden_gui.sh (o port Qt)
# Ambos exportam $MAIN e definem dlu_x/dlu_y com a mesma conversão do ed.rc.

par_click() {   # par_click <x> <y> <w> <h>
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}

# O botão abre "Operation done!", e a caixa precisa de dispensa EXPLÍCITA:
# deixada em pé ela cobre o CMB_WRITE, o clique de gravar não chega, e o
# wait_for_window do golden_gui.sh toma a caixa pela confirmação -- imprime
# "gravado" e o arquivo sai intacto, verde que não mediu nada.
#
# `Return` NÃO serve: fecha a QMessageBox do port e deixa a do MFC sob Wine em
# pé, e aí o port grava e o oráculo não. O que funciona nos dois é clicar no
# botão -- só que ele fica em lugares diferentes, medido em captura:
#
#   MFC sob Wine   148x82   OK no centro horizontal, a ~40% da altura
#   QMessageBox    188x100  OK a ~77% da largura e ~75% da altura
#
# Como o roteiro tem de ser o mesmo nos dois lados, os pontos são tentados em
# ordem e a caixa é reconferida entre eles: no oráculo o primeiro clique já a
# fecha, no port ele cai no texto (inócuo) e o segundo fecha. Os dois últimos
# pontos e os três passes são margem -- um clique que erra o botão não faz
# nada, e uma caixa que sobrevive ao roteiro engole o clique de gravar e deixa
# a corrida verde sem ter medido nada.

acha_modal() {  # imprime o id da caixa, ou nada
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

# CMD_DEFAULT_NUMBERS 639,178,62,15
par_click 639 178 62 15; sleep 2
dispensa_modal || echo "par: a caixa 'Operation done!' nao fechou" >&2
sleep 1

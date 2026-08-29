# PARIDADE-FUNCIONAL §8.7 -- Escape SEM ter navegado, num combo de papel.
#
# Time: Nation 1 - Ireland. Combo: CMB_SLOT_ROLE2 (CMB_TAT2 no .rc).
# Estímulo: abrir o combo e desistir com `Escape` na hora, sem tocar nas setas.
# Nenhum dos dois lados pode gravar papel nenhum.
#
# É a contraprova do 8.7-escape-papel.sh, irmã do 8.3-escape-sem-navegar.sh:
# aquele mostra que o item navegado sobrevive ao Escape nos dois lados, este
# mostra que sem navegação não há valor novo para sobreviver.
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

# CMB_TEAM 142,7,137,12 -- Home antes do Down torna a escolha independente do
# estado inicial, e o Return confirma o popup.
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers Home;             sleep 1
xdotool key --clearmodifiers Down;             sleep 1
xdotool key --clearmodifiers Return;           sleep 2

# CMB_SLOT_ROLE2 428,43,38,12 -- abre e desiste na hora
par_click 428 43 38 12; sleep 2
xdotool key --clearmodifiers Escape; sleep 2

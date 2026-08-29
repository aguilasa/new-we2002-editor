# PARIDADE-FUNCIONAL §8.7 -- Escape depois de navegar um combo de PAPEL.
#
# Time: Nation 1 - Ireland. Combo: CMB_SLOT_ROLE2 (CMB_TAT2 no .rc), o 1º dos
# dez papéis táticos.
# Estímulo: o mesmo do 8.3-escape-cobrador.sh, no outro combo -- três `Down`
# sem sair do controle, e desistir com `Escape`.
#
# Os dez combos de papel gravam pelo MESMO `FocusOut` que os seis de cobrador
# (o `currentIndexChanged` deles só repinta a legenda do marcador, não toca em
# dado). Por isso o `Escape` divergia aqui exatamente como divergia lá: o MFC
# mantém o item navegado e o QComboBox revertia.
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

# CMB_SLOT_ROLE2 428,43,38,12
par_click 428 43 38 12; sleep 2
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Escape; sleep 2

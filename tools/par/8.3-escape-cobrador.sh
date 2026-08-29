# PARIDADE-FUNCIONAL §8.3, item 1 -- Escape depois de navegar um combo de
# cobrador.
#
# Time: Nation 1 - Ireland.
# Estímulo: abrir o CMB_KICK_LONG_FK, três `Down` **sem sair do controle**, e
# desistir com `Escape`. O campo vale 3 na imagem, então três descidas dão 6.
#
# O que se mede é o que sobra no killfocus: os dois lados gravam em perda de
# foco (o clique em CMB_WRITE), mas o MFC mantém o item navegado depois do
# `Escape` e o QComboBox reverte para o de antes de abrir.
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

# CMB_KICK_LONG_FK 60,241,57,12
par_click 60 241 57 12; sleep 2
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Escape; sleep 2

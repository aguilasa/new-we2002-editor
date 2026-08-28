# PARIDADE-FUNCIONAL §8.1, item 4 (metade "clube de ML") --
# CMD_COPY_TEAM_NAMES num clube.
#
# Time: Master League 32 (o último clube real).
# Estímulo: o mesmo do 8.1-copy-selecao.sh, num time cujo registro tem os dois
# nomes extras (OFS_ML_TEAM_NAME_7/_8) -- por isso o copy toca mais regiões
# aqui do que na seleção.
#
# Este arquivo é o trecho de shell que os DOIS hooks recebem sem alteração:
#   GOLDEN_EDIT     -> tools/golden_run.sh (o ed.exe sob Wine)
#   GOLDEN_GUI_EDIT -> tools/golden_gui.sh (o port Qt)
# Ambos exportam $MAIN e definem dlu_x/dlu_y com a mesma conversão do ed.rc.

# clique no centro de um controle, com a geometria em DLU do ed.rc
par_click() {   # par_click <x> <y> <w> <h>
    xdotool mousemove --window "$MAIN" \
        $(( $(dlu_x "$1") + $(dlu_x "$3") / 2 )) \
        $(( $(dlu_y "$2") + $(dlu_y "$4") / 2 )) click 1
}
# limpa e digita. Ctrl+A NÃO seleciona tudo num CEdit do Win32 (CLAUDE.md):
# usar End, shift+Home, BackSpace, senão os dois lados recebem textos
# diferentes e o diff acusa divergência que não existe.
par_type() {    # par_type <texto>
    xdotool key --clearmodifiers End;        sleep 0.5
    xdotool key --clearmodifiers shift+Home; sleep 0.5
    xdotool key --clearmodifiers BackSpace;  sleep 0.5
    xdotool type --delay 40 "$1";            sleep 0.5
}

# CMB_TEAM 142,7,137,12. End cai em "Master League (default)", que é um item
# especial de campos desabilitados e não serve de clube; um Up a partir dele dá
# o último clube real, "Master League 32", sem depender de contar quantos são.
# O Return CONFIRMA -- sem ele o popup fica aberto e o formulário não troca.
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers End;              sleep 1
xdotool key --clearmodifiers Up;               sleep 1
xdotool key --clearmodifiers Return;           sleep 2

par_click 10 31 76 12; sleep 1      # TXT_TEAM_NAME1
par_type "GOLDEN"

par_click 75 17 34 10; sleep 3      # CMD_COPY_TEAM_NAMES

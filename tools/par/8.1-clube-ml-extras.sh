# PARIDADE-FUNCIONAL §8.1, item 5 -- clube de ML, com os dois nomes extras.
#
# Time: Master League 32.
# Estímulo: os 6 TXT_TEAM_NAME mais TXT_ML_EXTRA_NAME1 (12,189,89,12) e
# TXT_ML_EXTRA_NAME2 (12,205,89,12), que só existem para clube de ML. Os
# limites nesta tela são (11)(11)(11)(7)(7)(7) mais (8) e (11) -- quatro
# diferentes, que é o que faz este item medir o truncamento por rótulo.
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

i=1
for y in 31 44 57 70 83 96; do
    par_click 10 "$y" 76 12; sleep 1
    par_type "GOLDENML$i"
    i=$((i + 1))
done

par_click 12 189 89 12; sleep 1     # TXT_ML_EXTRA_NAME1
par_type "GOLDML7"
par_click 12 205 89 12; sleep 1     # TXT_ML_EXTRA_NAME2
par_type "GOLDENML8"

# tira o foco do último campo para o killfocus gravar
par_click 10 31 76 12; sleep 2      # TXT_TEAM_NAME1

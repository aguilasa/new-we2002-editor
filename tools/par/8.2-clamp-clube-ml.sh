# PARIDADE-FUNCIONAL §8.2, item 2 -- a ausência de clamp num clube de ML.
#
# Time: Master League 32. Slot: o 1º do elenco (TXT_NUM1).
# Estímulo: o mesmo 33 do 8.2-clamp-selecao.sh. Aqui não há teto: o disco
# guarda 32, contra os 31 da seleção. A assimetria é do original e tem de ser
# reproduzida, não corrigida.
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
# limpa e digita. Ctrl+A NÃO seleciona tudo num CEdit do Win32 (CLAUDE.md):
# usar End, shift+Home, BackSpace, senão os dois lados recebem textos
# diferentes e o diff acusa divergência que não existe.
par_type() {    # par_type <texto>
    xdotool key --clearmodifiers End;        sleep 0.5
    xdotool key --clearmodifiers shift+Home; sleep 0.5
    xdotool key --clearmodifiers BackSpace;  sleep 0.5
    xdotool type --delay 40 "$1";            sleep 0.5
}

# CMB_TEAM 142,7,137,12 -- End cai em "Master League (default)", que é item
# especial de campos desabilitados; um Up dá o último clube real,
# "Master League 32". O Return confirma o popup.
par_click 142 7 137 12;                        sleep 2
xdotool key --clearmodifiers End;              sleep 1
xdotool key --clearmodifiers Up;               sleep 1
xdotool key --clearmodifiers Return;           sleep 2

# TXT_NUM1 294,30,13,12 -- o número de camisa do 1º slot do elenco
par_click 294 30 13 12; sleep 1
par_type "33"

# tira o foco para o commit acontecer -- os dois gravam em perda de foco
# (EN_KILLFOCUS lá, editingFinished aqui), não a cada tecla.
# TXT_NUM2 294,43,13,12
par_click 294 43 13 12; sleep 2

# PARIDADE-FUNCIONAL §8.8, item 3 -- importar a bandeira (.b2002).
#
# Carrega tools/par/8.8-prelude.sh antes, com PAR_TEAM de um time COM bandeira
# própria.
#
#   CMD_IMPORT_FLAG 124,48,44,12
#   PAR_B = caminho de origem.
fk_click 124 48 44 12;               sleep 2.5
xdotool type --delay 40 "${PAR_B:?falta PAR_B}"
sleep 0.8
xdotool key --clearmodifiers Return; sleep 2.5
xdotool key --clearmodifiers Return; sleep 1.2
fk_click 196 26 36 14;               sleep 1.5

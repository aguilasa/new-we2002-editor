# PARIDADE-FUNCIONAL §8.8, item 3 -- exportar a bandeira (.b2002) e o
# uniforme 1 (.m2002).
#
# Carrega tools/par/8.8-prelude.sh antes, com um time que TENHA bandeira
# própria (PAR_TEAM=1). Num time sem, os dois lados recusam com
# `Choose a team (that has "indipendent" flag too) !` -- que é o item 2.
#
#   CMD_EXPORT_FLAG 124,65,44,12    CMD_EXPORT_KIT1 55,174,44,12
#   PAR_B / PAR_M = caminhos de destino.
fk_click 124 65 44 12;               sleep 2.5
xdotool type --delay 40 "${PAR_B:?falta PAR_B}"
sleep 0.8
xdotool key --clearmodifiers Return; sleep 2.5
xdotool key --clearmodifiers Return; sleep 1.2

fk_click 55 174 44 12;               sleep 2.5
xdotool type --delay 40 "${PAR_M:?falta PAR_M}"
sleep 0.8
xdotool key --clearmodifiers Return; sleep 2.5
xdotool key --clearmodifiers Return; sleep 1.2

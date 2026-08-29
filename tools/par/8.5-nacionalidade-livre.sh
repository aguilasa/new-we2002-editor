# PARIDADE-FUNCIONAL §8.5, item 3 -- agente livre com nacionalidade padrão ×
# escolhida no combo.
#
# Carrega tools/par/8.5-prelude.sh com PAR_TIME=ml antes.
#
# CHK_LK_DEF (29,224,44,10, "default") e CHK_LK_NDEF (87,224,54,10,
# "change nat.") são mutuamente exclusivos, e só aparecem quando o destino é o
# pool de agentes livres. O CMB_NATIONALITY (143,224,110,12) lista só os times
# cujo START_LINK alcança o jogador dentro de 255 (§4.2), então ele não é uma
# lista de todos os times -- escolher "o próximo" é o que dá determinismo aqui.
#
#   PAR_NAT=default (padrão) | change
sel_click 17 26 127 158;          sleep 0.8
xdotool key --clearmodifiers End; sleep 1          # o pool "- ML (non contacted) "
sel_row 154 26 89 158 4
if [ "${PAR_NAT:-default}" = change ]; then
    sel_click 87 224 54 10;       sleep 0.8        # CHK_LK_NDEF
    sel_click 143 224 110 12;     sleep 1          # abre o CMB_NATIONALITY
    xdotool key --clearmodifiers Home;   sleep 0.5
    xdotool key --clearmodifiers Down;   sleep 0.5
    xdotool key --clearmodifiers Return; sleep 1
else
    sel_click 29 224 44 10;       sleep 0.8        # CHK_LK_DEF
fi
sel_click 176 213 22 9;           sleep 2

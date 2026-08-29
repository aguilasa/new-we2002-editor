# PARIDADE-FUNCIONAL §8.5, item 2 -- slot de clube de ML, link para contratado
# e para agente livre.
#
# Carrega tools/par/8.5-prelude.sh com PAR_TIME=ml antes.
#
# CHK_ML (127,197,89,10), rotulado "link", só aparece para time por link -- é
# o que separa este item do anterior. Ele alterna "link" × "skill".
# O pool de agentes livres é a última entrada da LIST_TEAMS,
# "- ML (non contacted) ", com os 462 sem contrato (§4.2).
#
#   PAR_LIVRE=1 -> escolhe o pool de agentes livres em vez de um clube
if [ "${PAR_LIVRE:-0}" = 1 ]; then
    # o pool fica no fim da lista: End em vez de contar linhas
    sel_click 17 26 127 158;          sleep 0.8
    xdotool key --clearmodifiers End; sleep 1
else
    sel_row 17 26 127 158 2
fi
sel_row 154 26 89 158 4
sel_click 176 213 22 9;               sleep 2

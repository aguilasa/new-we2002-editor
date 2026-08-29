# PARIDADE-FUNCIONAL §8.5, item 1 -- slot de seleção nacional, nos dois modos.
#
# Carrega tools/par/8.5-prelude.sh antes, que já abriu o PlayerSelectDialog no
# 1º slot do Nation 1 - Ireland.
#
# CHK_COMPLETE_SWAP (19,197,93,10) tem o rótulo "incomplete substitution":
# DESMARCADO é a troca completa (os dois jogadores trocam de lugar) e MARCADO
# é a incompleta (o de origem é duplicado). PAR_INCOMPLETE=1 marca a caixa.
#
#   LIST_TEAMS 17,26,127,158   LIST_PLAYERS 154,26,89,158   IDC_BUTTON1 176,213,22,9
sel_row 17 26 127 158 3          # 4º time da lista
sel_row 154 26 89 158 5          # 6º jogador dele
if [ "${PAR_INCOMPLETE:-0}" = 1 ]; then
    sel_click 19 197 93 10;      sleep 0.8
fi
sel_click 176 213 22 9;          sleep 2

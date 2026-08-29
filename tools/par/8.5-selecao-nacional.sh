# PARIDADE-FUNCIONAL §8.5, item 1 -- slot de seleção nacional, nos dois modos.
#
# Carrega tools/par/8.5-prelude.sh antes, que já abriu o PlayerSelectDialog no
# 1º slot do Nation 1 - Ireland.
#
# CHK_COMPLETE_SWAP (19,197,93,10) nasce DESMARCADO e com o rótulo
# "incomplete substitution", que é o nome do estado em que ele ESTÁ, não do que
# a caixa faz quando marcada -- o rótulo é reescrito ao alternar. Então:
#
#   desmarcado  "incomplete"  duplica o escolhido no slot        1 registro
#   marcado     "complete"    os dois jogadores trocam de lugar  2 registros
#
# PAR_COMPLETA=1 marca a caixa e roda a completa.
#
#   LIST_TEAMS 17,26,127,158   LIST_PLAYERS 154,26,89,158   IDC_BUTTON1 176,213,22,9
sel_row 17 26 127 158 3          # 4º time da lista
sel_row 154 26 89 158 5          # 6º jogador dele
if [ "${PAR_COMPLETA:-0}" = 1 ]; then
    sel_click 19 197 93 10;      sleep 0.8
fi
sel_click 176 213 22 9;          sleep 2

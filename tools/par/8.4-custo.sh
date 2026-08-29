# PARIDADE-FUNCIONAL §8.4, item 3 -- custo com mais de 2 dígitos.
#
# Carrega tools/par/8.4-prelude.sh antes. O rótulo do campo é "ML price" e ele
# tem 16 DLU de largura; o item manda conferir que o ORIGINAL também trunca --
# ou seja, o que se mede é paridade de truncamento, não o truncamento em si.
#
#   TXT_COST 274,115,16,13
sk_click 274 115 16 13; sleep 1; par_type "12345"
sk_click 274 131 16 13; sleep 1
xdotool key --clearmodifiers Escape; sleep 2

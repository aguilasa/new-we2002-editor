# PARIDADE-FUNCIONAL §8.5, item 4 -- slot de all-star, e os nomes que se
# refazem depois.
#
# Carrega tools/par/8.5-prelude.sh com PAR_TIME=allstar antes.
#
# O item existe por causa de uma NÃO-IDEMPOTÊNCIA conhecida: o Save reconstrói
# as all-star a partir dos links (OFS_PLAYER_ATTR_8), então Load+Save sem
# editar nada já não devolve a imagem intacta. O oráculo faz o mesmo, e é por
# isso que este item se confere contra o ed.exe e NUNCA contra a imagem
# original -- comparar com o original aqui acusaria uma divergência que é o
# comportamento correto.
sel_row 17 26 127 158 3
sel_row 154 26 89 158 6
sel_click 176 213 22 9;           sleep 2

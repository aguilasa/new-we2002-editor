# PARIDADE-FUNCIONAL §8.7, item 2 -- trocar papel e conferir a legenda do
# marcador.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# CMB_SLOT_ROLE2 (428,43,38,12) é o 1º dos dez papéis. Diferente do
# 8.7-escape-papel.sh, aqui a escolha é CONFIRMADA (Return) e o foco sai (Tab):
# é o caminho que grava. O `currentIndexChanged` do combo só repinta a legenda
# do marcador no campinho; quem grava é o `FocusOut`.
par_click 428 43 38 12;              sleep 1.2
xdotool key --clearmodifiers Down;   sleep 0.5
xdotool key --clearmodifiers Down;   sleep 0.5
xdotool key --clearmodifiers Return; sleep 0.8
xdotool key --clearmodifiers Tab;    sleep 1.5

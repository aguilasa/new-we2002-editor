# PARIDADE-FUNCIONAL §8.7, item 1 -- clampar x em 0/48 e y em 0/112.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# TXT_SLOT_X2 (468,43,13,12) e TXT_SLOT_Y2 (483,43,17,12) são o 1º dos dez
# slots táticos -- não há slot 1 na tela, o goleiro é fixo. Os dois usam
# `textChanged` e não `textEdited`, porque no original o `EN_CHANGE` disparava
# também em `SetWindowText` e é o que move os marcadores do campinho ao trocar
# de time. Não "otimizar" isso.
#
#   PAR_X / PAR_Y: os valores a digitar. Fora da faixa, o original clampa.
par_click 468 43 13 12; sleep 1; par_type "${PAR_X:-99}"
par_click 483 43 17 12; sleep 1; par_type "${PAR_Y:-999}"
# tira o foco do último campo para o killfocus gravar
par_click 468 43 13 12; sleep 1.5

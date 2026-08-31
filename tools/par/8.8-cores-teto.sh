# PARIDADE-FUNCIONAL §8.8, item 1 -- cores no teto (65535) e acima.
#
# Carrega tools/par/8.8-prelude.sh antes.
#
# TXT_FLAG_COL1 (10,28,26,12) é a 1ª das 15 cores da bandeira, teto 65535 (uma
# word). TXT_KIT1_COL1 (11,101,26,12) e TXT_KIT2_COL1 (115,101,26,12) são a 1ª
# de cada uniforme -- 14 cores cada, porque as palavras 0 e 1 das 16 não são
# expostas (§4.4).
#
#   PAR_COR = o valor a digitar. 65535 é o teto; acima dele o original clampa.
fk_click 10 28 26 12;   sleep 0.8; par_type "${PAR_COR:-99999}"
fk_click 11 101 26 12;  sleep 0.8; par_type "${PAR_COR:-99999}"
fk_click 115 101 26 12; sleep 0.8; par_type "${PAR_COR:-99999}"
# tira o foco do último campo, depois fecha pelo IDOK "Close" (196,26,36,14),
# que neste diálogo É visível -- diferente do DefaultTacticsDialog da §8.7.
fk_click 10 28 26 12;   sleep 0.8
fk_click 196 26 36 14;  sleep 1.5

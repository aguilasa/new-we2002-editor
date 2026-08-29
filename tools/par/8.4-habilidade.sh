# PARIDADE-FUNCIONAL §8.4, item 1 -- o clamp de habilidade em 12..19.
#
# Carrega tools/par/8.4-prelude.sh antes (Nation 1 - Ireland, 1º jogador, com o
# PlayerSkillsDialog aberto). Estímulo: os dois extremos numa corrida só --
# 25 acima do teto no TXT_ATTACK, 3 abaixo do piso no TXT_DEFENCE. Os dois têm
# de sair 19 e 12.
#
# O clamp é `ClampBox(box, 12, 19)` em src/app/PlayerSkillsDialog.cpp contra
# `if(i<12)` / `if(i>19)` em legacy/mfc/carattDlg.cpp -- e vale para as 19
# caixas de habilidade, não só para estas duas.
#
#   TXT_ATTACK 175,13,21,13   TXT_DEFENCE 175,29,21,13
sk_click 175 13 21 13; sleep 1; par_type "${PAR_ATK:-25}"
sk_click 175 29 21 13; sleep 1; par_type "${PAR_DEF:-3}"
# tira o foco do último campo e fecha o diálogo
sk_click 175 13 21 13; sleep 1
xdotool key --clearmodifiers Escape; sleep 2

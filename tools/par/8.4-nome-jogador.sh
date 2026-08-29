# PARIDADE-FUNCIONAL §8.4, item 5 -- editar nome de jogador.
#
# Carrega tools/par/8.4-prelude.sh antes. O item registra onde se edita: é AQUI,
# no PlayerSkillsDialog, e não no diálogo principal -- lá a caixa ao lado do
# número é só leitura da lista.
#
#   TXT_NAME 55,13,62,13 -- setMaxLength(10) no MainWindow.cpp
sk_click 55 13 62 13; sleep 1; par_type "JOGADORxyz"
sk_click 55 129 24 13; sleep 1
xdotool key --clearmodifiers Escape; sleep 2

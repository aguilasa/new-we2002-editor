# PARIDADE-FUNCIONAL §8.7, item 5 -- exportar um .t2002.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# CMD_EXP (60,151,32,12) fica DENTRO do DefaultTacticsDialog e abre um diálogo
# de arquivo ("TACTIC FILE TO EXPORT"). O caminho é digitado curto de
# propósito: `xdotool type` embaralha string longa, e um caminho truncado vira
# "Path does not exist", que parece erro do app (CLAUDE.md).
#
#   PAR_T2002 = caminho de destino. No oráculo tem de ser um caminho Windows
#   (Z: é a raiz do Linux no prefix do Wine); no port, um caminho POSIX.
par_click 251 23 34 10;              sleep 2
TCT="$(tact_win)" || { echo "par: DefaultTacticsDialog nao abriu" >&2; }
tct_click 60 151 32 12;              sleep 2.5
xdotool type --delay 40 "${PAR_T2002:?falta PAR_T2002}"
sleep 0.8
xdotool key --clearmodifiers Return; sleep 2.5
# fecha o diálogo de táticas: Return é a única saída dele (o IDOK é
# NOT WS_VISIBLE) -- ver CORR-WTE-131.
xdotool key --clearmodifiers Return; sleep 1.5

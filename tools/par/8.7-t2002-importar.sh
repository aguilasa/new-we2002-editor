# PARIDADE-FUNCIONAL §8.7, item 5 -- importar um .t2002.
#
# >>> NO ORÁCULO ESTE ROTEIRO NÃO IMPORTA NADA, E ISSO É UM ACHADO. <<<
#
# O `ed.exe` recusa com `Not right file !` até o arquivo que ele mesmo
# exportou -- medido em 2026-08-31 com três variantes de conteúdo e dois
# caminhos (`Z:\tmp\x.t2002` e o nome curto no CWD dele). O port, no mesmo
# teste, aceita o próprio arquivo. Ver CORR-WTE-132.
#
# Ao usar este roteiro, SEMPRE conferir o controle positivo contra a imagem
# original: um import recusado grava só as não-idempotências conhecidas, e duas
# recusas produzem imagens idênticas -- o que se lê como "os dois lados
# concordam" quando na verdade os dois falharam.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# CMD_IMP (24,151,31,12) fica dentro do DefaultTacticsDialog e abre um diálogo
# de arquivo. O caminho é digitado curto de propósito -- `xdotool type`
# embaralha string longa, e um caminho truncado vira "Path does not exist",
# que parece erro do app (CLAUDE.md).
#
#   PAR_T2002 = caminho de origem. No oráculo é caminho Windows (Z: é a raiz
#   do Linux no prefix do Wine); no port, POSIX.
par_click 251 23 34 10;              sleep 2
TCT="$(tact_win)" || { echo "par: DefaultTacticsDialog nao abriu" >&2; }
tct_click 24 151 31 12;              sleep 2.5
xdotool type --delay 40 "${PAR_T2002:?falta PAR_T2002}"
sleep 0.8
xdotool key --clearmodifiers Return; sleep 2.5
# dispensa o aviso de "importado" e fecha o diálogo de táticas (Return é a
# única saída dele -- CORR-WTE-131).
xdotool key --clearmodifiers Return; sleep 1.2
xdotool key --clearmodifiers Return; sleep 1.5

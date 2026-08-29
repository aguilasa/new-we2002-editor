# PARIDADE-FUNCIONAL §8.7, item 5 -- editar e renomear um preset.
#
# >>> ESTE ROTEIRO NÃO FECHA, E POR ISSO NÃO MEDE NADA AINDA. <<<
#
# Ele está versionado como esqueleto: abre o diálogo, escolhe o preset, renomeia
# e edita a geometria -- tudo isso funciona. O que falta é CONFIRMAR, e o
# `tct_click 197 17 50 14` da última linha é a tentativa que falhou.
#
# O `IDOK` do DefaultTacticsDialog **não é desenhado em nenhum dos dois lados**
# (medido em 2026-08-29, captura do topo do diálogo no port e no ed.exe: ali só
# há "Selection" e "Name"). Sem confirmar, a gravação sai IDENTICAL à imagem
# original -- as edições do diálogo não chegam ao disco.
#
# Já descartados, não repetir: `Return` não fecha; clicar na posição do IDOK
# não fecha; deixar aberto não aplica. O próximo caminho é o `.rc` do IDOK ou o
# handler que o diálogo liga ao fechamento.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# CMD_EDIT_PRESETS (251,23,34,10, "modify") abre o diálogo, que mede 481x297 px.
# Dentro dele, e relativo a ELE:
#   CMB_FORMATION      21,31,42,12   escolhe qual dos presets editar
#   TXT_FORMATION_NAME 80,31,27,12   o nome, que é o que este item renomeia
#   TXT_SLOT_X2/Y2     273,47 / 289,47  a geometria do slot, para "editar"
#   IDOK               197,17,50,14  confirma
#
# Editar E renomear na mesma corrida é de propósito: são dois caminhos de
# gravação do mesmo diálogo, e um preset renomeado que perdesse a geometria
# (ou o contrário) passaria despercebido se medidos em corridas separadas.
par_click 251 23 34 10;              sleep 2
TCT="$(tact_win)" || { echo "par: DefaultTacticsDialog nao abriu" >&2; }

# o 2º preset da lista, para não medir sempre o primeiro
xdotool mousemove --window "$TCT" "$(dlu_x 42)" "$(dlu_y 37)" click 1; sleep 1.2
xdotool key --clearmodifiers Home;   sleep 0.5
xdotool key --clearmodifiers Down;   sleep 0.5
xdotool key --clearmodifiers Return; sleep 1.2

tct_click 80 31 27 12;  sleep 0.8; par_type "TAT9"
tct_click 273 47 13 12; sleep 0.8; par_type "40"
tct_click 289 47 17 12; sleep 0.8; par_type "90"
tct_click 197 17 50 14; sleep 2

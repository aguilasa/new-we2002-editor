# PARIDADE-FUNCIONAL §8.7 -- Escape num combo de papel DO DIÁLOGO DE PRESETS.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# Irmão do 8.7-escape-papel.sh, e NÃO é o mesmo controle. Aquele mede o
# CMB_SLOT_ROLE2 do MainDialog (428,43 no ed.rc), um dos dezesseis que a
# CORR-WTE-127 alcançou. Este mede o CMB_SLOT_ROLE2 do DefaultTacticsDialog
# (199,46, o TCMB_TAT2 do .rc) -- outros dez combos, que escrevem os mesmos
# `roles[]` só que nos PRESETS, e que a CORR-WTE-127 não alcançou.
#
# O caminho de commit também é outro, e é o que torna o conserto delicado: no
# MainDialog a escrita é no FocusOut; aqui é no `currentIndexChanged` guardado
# por `hasFocus()`. Repor o índice com o combo já sem foco não grava nada.
#
# Estímulo: três `Down` sem sair do controle, e desistir com `Escape`. No
# original as setas movem o CurSel do próprio combo e o `Escape` só fecha a
# lista, então o valor navegado é o que fica: `raw_formation[0]` do preset vai
# de 0x02 a 0x05. Ver CORR-WTE-134.
#
# O clique no TXT_FORMATION_NAME depois do Escape é o que tira o foco do combo
# -- sem ele o commit por perda de foco do oráculo não roda. O `Return` final
# fecha o diálogo (o IDOK é NOT WS_VISIBLE -- CORR-WTE-131).
par_click 251 23 34 10;              sleep 2
# O `exit 1` aqui não é zelo: sem o diálogo, o `Escape` abaixo chega ao
# MainWindow, que é um QDialog e REJEITA -- o port morre no meio do roteiro e o
# clique de gravação seguinte estoura `BadWindow`, que se lê como falha do
# harness. Melhor parar dizendo o que faltou. Medido em 2026-08-31, com um
# segundo port esquecido no `:98` roubando os cliques.
TCT="$(tact_win)" || { echo "par: DefaultTacticsDialog nao abriu" >&2; exit 1; }

# CMB_SLOT_ROLE2 199,46,38,12 -- dentro do diálogo
tct_click 199 46 38 12; sleep 2
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Down;   sleep 1
xdotool key --clearmodifiers Escape; sleep 2

# TXT_FORMATION_NAME 80,31,27,12 -- só para forçar a perda de foco
tct_click 80 31 27 12; sleep 1.5
xdotool key --clearmodifiers Return; sleep 1.5

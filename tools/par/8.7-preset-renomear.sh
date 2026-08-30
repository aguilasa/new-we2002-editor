# PARIDADE-FUNCIONAL §8.7, item 4 -- editar e renomear um preset.
#
# Carrega tools/par/8.7-prelude.sh antes.
#
# CMD_EDIT_PRESETS (251,23,34,10, "modify") abre o DefaultTacticsDialog, de
# 481x297 px. Dentro dele, e relativo a ELE:
#   CMB_FORMATION      21,31,42,12   qual preset editar
#   TXT_FORMATION_NAME 80,31,27,12   o nome, que é o que este item renomeia
#   TXT_SLOT_X2/Y2     273,47 / 289,47
#
# NÃO há clique de confirmação, e isso é deliberado: o `IDOK` do diálogo é
# `NOT WS_VISIBLE` no próprio ed.rc (linha 627), então não há botão para
# clicar, e `Return` não fecha o diálogo em NENHUM dos dois lados -- medido.
# O que o roteiro exercita é justamente o caminho que resta ao usuário: editar
# e mandar gravar com o diálogo aberto.
par_click 251 23 34 10;              sleep 2
TCT="$(tact_win)" || { echo "par: DefaultTacticsDialog nao abriu" >&2; }

# Edita o preset que o diálogo já abre selecionado. NÃO mexer no
# CMB_FORMATION: abrir aquele popup com o diálogo por cima deixa a gravação do
# oráculo sem confirmar ("a gravacao nao confirmou"), e a corrida morre antes
# de medir. Renomear e mexer na geometria do slot já exercitam os dois
# caminhos de escrita do diálogo, que é o que o item pede.
tct_click 80 31 27 12;  sleep 0.8; par_type "TAT9"
tct_click 273 47 13 12; sleep 0.8; par_type "40"
tct_click 289 47 17 12; sleep 0.8; par_type "90"
tct_click 80 31 27 12;  sleep 0.8
# O `Return` NÃO fecha o diálogo (o IDOK é NOT WS_VISIBLE), mas confirma o
# campo em edição. Sem ele o oráculo termina com a gravação sem confirmar e a
# corrida morre antes de medir -- medido em 2026-08-30.
xdotool key --clearmodifiers Return; sleep 1.5

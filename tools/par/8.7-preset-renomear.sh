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
# clicar. Quem confirma é o `Return` -- no MFC um DEFPUSHBUTTON invisível
# continua sendo o default do diálogo, e o EndDialog roda. O Qt não ativa por
# `Return` um botão invisível, e é aí que os dois lados divergem
# (CORR-WTE-131).
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
# O `Return` é o que FECHA o diálogo no oráculo, pelo IDOK default apesar do
# NOT WS_VISIBLE -- e só com ele fechado o clique em CMB_WRITE alcança o
# diálogo principal. Sem o `Return` o oráculo sai `a gravacao nao confirmou` e
# a cópia fica IDENTICAL: os dois lados são modais e os dois bloqueiam a
# gravação enquanto o diálogo está de pé. Medido em 2026-08-30, nas duas
# corridas -- com e sem esta linha.
#
# CUIDADO com a sonda de janela: depois do roteiro o "Modify default tactics"
# aparece mapeado nos DOIS lados. No oráculo é a janela X que o Wine deixa
# para o `tattDlg dlg_tatt` membro, reusado entre chamadas, e não quer dizer
# que o modal esteja de pé. Quem distingue é rodar sem o `Return`.
xdotool key --clearmodifiers Return; sleep 1.5

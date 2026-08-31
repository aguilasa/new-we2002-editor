# PARIDADE-FUNCIONAL §8.10, item 4 -- `Return` na janela principal.
#
# >>> ESTE ROTEIRO É HOOK DE UM LADO SÓ: `GOLDEN_GUI_EDIT`, o port. <<<
#
# Com `GOLDEN_EDIT` o oráculo RECEBE o `Return`, ENCERRA -- que é o achado do
# item -- e o `golden_run.sh` morre antes de gravar:
#
#     tools/golden_run.sh: nao consegui focar a janela 0xe00001
#
# Ou seja: `golden_check.sh` com este roteiro reprova SEMPRE, por construção, e
# isso é o resultado ESPERADO, não regressão (CORR-WTE-141). Não gaste uma
# corrida de golden para redescobrir isso.
#
# O veredito do item não é o `OK` do `golden_check.sh` -- é `cmp` entre a cópia
# gravada com o `Return` e a de uma corrida de CONTROLE sem tecla nenhuma. Os
# dois arquivos têm de sair iguais, e contra a imagem original acusam só as 5
# faixas / 41 bytes das não-idempotências conhecidas:
#
#     GOLDEN_GUI_EDIT="$(cat tools/par/8.10-return-nao-dispara.sh)" \
#         tools/golden_gui.sh "$SCRATCH/ret.bin"
#     tools/golden_gui.sh "$SCRATCH/ctl.bin"     # controle, sem estímulo
#     cmp "$SCRATCH/ret.bin" "$SCRATCH/ctl.bin"  # tem de sair silencioso
#
# NÃO carrega prelúdio: o item é sobre a janela principal recém-carregada, sem
# time selecionado nem campo em edição. Qualquer clique antes mudaria o foco e
# com ele o destino da tecla.
#
# O que se afirma: `Return` não pode DISPARAR AÇÃO DE EDIÇÃO. O risco tem nome
# e história -- dentro de um `QDialog` o Qt torna todo botão auto-default, e num
# diálogo com 86 botões e nenhum `DEFPUSHBUTTON` o `Return` clicaria o primeiro
# da ordem de tabulação; um dos candidatos aplica formação predefinida sobre o
# time selecionado. O `rc2ui.py` emite `autoDefault=false` por isso, e este
# roteiro é o que impede a emenda de apodrecer em silêncio.
#
# O ponteiro vai para o meio do diálogo ANTES da tecla: sem gerente de janelas
# o foco de teclado segue o ponteiro, e `Return` disparado com o ponteiro em
# outro lugar não mede o que se quer (CLAUDE.md, seção do `:98`).
xdotool mousemove --window "$MAIN" 300 300
sleep 0.5
xdotool key --clearmodifiers Return
sleep 2

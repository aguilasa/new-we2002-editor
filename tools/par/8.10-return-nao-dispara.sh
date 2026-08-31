# PARIDADE-FUNCIONAL §8.10, item 4 -- `Return` na janela principal.
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

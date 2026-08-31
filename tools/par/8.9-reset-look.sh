# PARIDADE-FUNCIONAL §8.9, item 4 -- CMB_EDITALLLOOK.
#
# Carrega tools/par/8.9-prelude.sh antes.
#
# CMB_EDITALLLOOK (639,212,62,15), rotulado "reset def. look": devolve a
# aparência padrão a todos os jogadores. Global, como o irmão acima.
par_click 639 212 62 15;  sleep 2
# Um `Return` seco, e NÃO o `dispensa_modal`. Os dois lados divergem aqui, e
# nenhuma das duas alternativas óbvias serve nos dois:
#
#   port     ABRE uma caixa (126x100) -- sem fechá-la, o clique de gravar não
#            chega e a cópia sai IDENTICAL
#   oráculo  NÃO abre caixa nenhuma -- e chamar `dispensa_modal` ali é pior que
#            inútil: sob Wine os controles do MFC são janelas X de verdade e
#            vários caem na faixa que o `acha_modal` procura (206x80, 148x82),
#            então ele acha um CONTROLE, clica nele, e a gravação não acontece
#
# `Return` fecha a QMessageBox do port e é inócuo no diálogo do ed.exe, que não
# tem DEFPUSHBUTTON nenhum (CLAUDE.md). Medido em 2026-09-01.
xdotool key --clearmodifiers Return; sleep 1.5

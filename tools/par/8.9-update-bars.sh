# PARIDADE-FUNCIONAL §8.9, item 5 -- CMB_EDITALLBARS.
#
# Carrega tools/par/8.9-prelude.sh antes.
#
# CMB_EDITALLBARS (190,195,100,18), rotulado "Update all team bars": recalcula
# as cinco barras de força de TODOS os times a partir dos jogadores.
#
# O item manda conferir que **57..63 ficaram intactos** -- são os all-star
# regionais, que não têm elenco próprio, e recalcular barras a partir de um
# elenco que não existe zeraria o que estava lá.
par_click 190 195 100 18; sleep 2.5
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
# `Return` fecha a QMessageBox do port. No `ed.exe` ele é inócuo AQUI, e a razão
# não é a que este comentário dizia até 2026-08-31 ("o diálogo não tem
# DEFPUSHBUTTON"): essa razão está errada e é perigosa.
#
# `Return` no FUNDO do diálogo do `ed.exe` **encerra o editor** -- sem
# `DEFPUSHBUTTON`, o Enter cai em `CDialog::OnOK` (§8.10 item 4,
# CORR-WTE-141). O que salva este roteiro é o ponteiro: ele acabou de clicar
# `CMB_EDITALLBARS` e continua sobre o botão, e no Win32 um pushbutton com foco
# vira o botão default temporário -- o `Return` re-clica ELE, que é idempotente,
# em vez de chegar ao `IDOK`.
#
# Ou seja: mexer no `par_click` acima sem mexer aqui pode fechar o oráculo antes
# de gravar. As duas medições que estabelecem isso são a corrida verde deste
# roteiro e a sonda da CORR-WTE-141, que diferem só em onde o ponteiro estava.
xdotool key --clearmodifiers Return; sleep 1.5

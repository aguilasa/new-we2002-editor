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
# ESPERAR a janela do diálogo de arquivo, não dormir um tempo fixo. O do port é
# o do portal GTK, em processo separado (1124x822), e demora mais que o
# `CFileDialog` do oráculo (660x488) -- com `sleep 2.5` o caminho era digitado
# antes de ele existir. Os dois lados usam o MESMO título (`lpstrTitle` em
# `legacy/mfc/tattDlg.cpp:728` e o `QStringLiteral` do port), então a
# espera serve aos dois.
for _ in $(seq 40); do
    xdotool search --onlyvisible --name 'TACTIC FILE TO EXPORT' >/dev/null 2>&1 && break
    sleep 0.25
done
sleep 0.5
xdotool type --delay 40 "${PAR_T2002:?falta PAR_T2002}"
sleep 0.8

# TRÊS `Return`, nesta ordem, e a contagem foi medida em 2026-08-31 nos dois
# lados (CORR-WTE-135). Ela NÃO se distribui igual:
#
#   port     #1 aceita o diálogo de arquivo E abre o aviso; #2 dispensa o
#            aviso; #3 fecha o diálogo de táticas
#   oráculo  #1 não fecha o diálogo de arquivo (fica de pé); #2 aceita e abre
#            o aviso; #3 dispensa o aviso
#
# O total é o mesmo e o efeito é o mesmo -- arquivo gravado, tela livre para o
# clique em CMB_WRITE --, que é o que o roteiro precisa. É a mesma classe de
# assimetria do `PAR_T2002` (caminho Windows de um lado, POSIX do outro): o
# gesto do usuário é o mesmo, o teclado é que não.
#
# NÃO transforme isto num laço guardado por `tact_win`. No oráculo o Wine deixa
# a janela do "Modify default tactics" MAPEADA depois de o modal fechar -- é a
# janela X do membro `tattDlg dlg_tatt`, reusado entre chamadas --, então
# `tact_win` continua achando 482x297 e o laço gasta `Return` a mais. E no
# diálogo principal do `ed.exe` um `Return` sobrando é fatal: `IDD_ED_DIALOG`
# não tem `DEFPUSHBUTTON`, e no MFC o Enter cai em `CDialog::OnOK`, que fecha o
# editor. O sintoma é `nao consegui focar a janela` na gravação, seguido de
# `IDENTICAL`.
xdotool key --clearmodifiers Return; sleep 1.5
xdotool key --clearmodifiers Return; sleep 1.5

# O CLIQUE NO CAMPO DE NOME: por que ele fica, agora que o defeito foi corrigido.
#
# Ele nasceu como contorno. O `CMD_IMP`/`CMD_EXP` fica com o foco depois de
# clicado, e no Qt um `QPushButton` focado consumia o `Return` e se auto-clicava
# -- reabrindo o diálogo de arquivo indefinidamente, com o port saindo
# `IDENTICAL` contra a imagem original sem nunca gravar. No MFC o `Return` vai
# para o botão DEFAULT do diálogo (o `IDOK`, invisível), e o foco do botão não
# atrapalha.
#
# A CORR-WTE-139 consertou isso no port: o `eventFilter` do
# `DefaultTacticsDialog` vê o `Return` antes dos botões. O clique CONTINUA aqui
# porque serve aos dois lados de qualquer modo -- é o mesmo alvo que o
# `8.7-preset-renomear.sh` usa antes do seu `Return` -- e tirá-lo exigiria duas
# corridas de golden só para provar que o veredito não muda. Se algum dia sair,
# é isso que tem de ser medido antes.
tct_click 80 31 27 12; sleep 1
xdotool key --clearmodifiers Return; sleep 1.5

WE2002 - Lazarus Editor -- os arquivos que faltam nesta pasta
=============================================================

Este diretorio esta vazio de proposito.

O editor precisa da arte do WE2002 Team Editor v0.99 do Obocaman: os bitmaps
de `image/` (bandeiras, uniformes 2D, cabelo, barba) e o `data/dat.bin`. Eles
NAO sao distribuidos com este programa -- sao obra de terceiro, sem licenca
concedida, do mesmo jeito que a imagem de CD do jogo nao acompanha nada disto.
Ver o NOTICE.md em share/doc/we2002Lazarus/.

Ponha aqui o conteudo da pasta do editor original, de modo que fiquem:

    <este diretorio>/image/...
    <este diretorio>/data/dat.bin

Alternativas, na ordem em que o programa procura:

  1. o diretorio que a variavel WTE_ASSETS_DIR apontar;
  2. ../assets, ao lado do executavel;
  3. este diretorio (o prefixo instalado).

Sem eles a janela abre, avisa, e as telas que desenham bandeira e uniforme
ficam vazias.

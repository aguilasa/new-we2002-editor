# `tests/roteiros/` — os roteiros de interação, fixos e versionados

Insumo da [WTE-TASK-13](../../../docs/tasks/13-trace-de-eventos.md) e, depois, do
harness golden da [WTE-TASK-22](../../../docs/tasks/22-harness-golden.md).

**Roteiro é fixo, nunca reativo.** Um driver que olha a tela e decide o próximo
passo muda o estímulo quando um lado diverge — e aí os dois param de receber a
mesma entrada, que é justamente a condição de qualquer comparação valer alguma
coisa. Aqui a sequência é escrita, versionada e idêntica nos dois lados.

## Formato

Arquivo de texto, uma diretiva por linha:

| Prefixo | Significado |
|---|---|
| `#` | comentário |
| `alvo:` | `port`, `original` ou `ambos` — de que lado o roteiro roda |
| `estado:` | `ok` ou `bloqueado: <razão>` |
| `!` | comando `xdotool`, literal, com as coordenadas **relativas à janela** |
| `~` | espera, em segundos |
| `espera:` | limite, em segundos, da **próxima** janela (`>` ou `>~`) |
| `@` | linha de trace esperada, sem o carimbo de tempo |

As coordenadas de `!` são relativas ao canto da janela alvo; quem replica soma
a origem, que muda a cada execução. O carimbo de tempo fica fora do `@` de
propósito: ele existe para ler intervalo, e a informação está na **ordem** das
linhas (ver o cabeçalho de [`../../src/retrace.pas`](../../src/retrace.pas)).

## Os roteiros 06 a 11 falam outro dialeto

Os seis são da WTE-TASK-19 e quem os executa é
[`../../tools/diff_dirigido.sh`](../../tools/diff_dirigido.sh), não a mão. Eles
acrescentam três diretivas e trocam a linha de `xdotool` crua por verbos:

| Prefixo | Significado |
|---|---|
| `>` | espera a janela com esse nome e passa a ser a origem das coordenadas |
| `>~` | idem, mas pelo **tamanho** (`529x498`) — ver abaixo |
| `=` | corta o log de I/O; tudo até a próxima marca é a conta daquela ação |
| `!` | `clique X Y`, `duplo X Y`, `tecla <k>`, `texto <t>` |

O `>~` existe porque **três formulários trocam o próprio `Caption` pelo nome do
time em tempo de execução** — `estrategia`, `jugador` e `ficha_dorsal`. Com a
ROM japonesa isso é Shift-JIS, e o que o `xdotool` vê é uma corrida de `?`: não
há regex estável. O tamanho há, e sai do `ClientWidth`/`ClientHeight` do próprio
DFM.

**Uma exceção medida:** o `ficha_dorsal` aparece como **135x153** e o DFM diz
129x121. Sem window manager o Wine desenha a moldura dentro da própria janela X,
e são 3 px de borda mais 29 de título. Só ele, entre os três — os outros dois
batem 1:1.

O motivo dos verbos é a coordenada: sem window manager no `:98` a origem da
janela muda a cada corrida, e escrever `xdotool` cru obrigaria cada linha a
saber somar. As coordenadas saem do
[`../../re/dfm/MainForm.dfm`](../../re/dfm/MainForm.dfm) — `Left`/`Top` do
controle mais o do `GroupBox` pai —, e o DFM bate **1:1** com o cliente da
janela: medido, `ClientWidth` 522 × `ClientHeight` 475 é exatamente o que o
`xdotool getwindowgeometry` devolve.

**Uma armadilha que custou dois diagnósticos:** a lista suspensa de um
`TComboBox` fica **mapeada** depois do clique no item e segura o ponteiro —
todo clique seguinte morre nela, inclusive num botão do outro lado da janela.
Trocar de item pelo teclado (`Down`) evita a lista. E o sintoma "o clique
parou de funcionar" tem um segundo culpado, que é pior: o `wte.exe` **cai** ao
carregar um time com as ROMs deste repositório, e a janela sobrevive ao
processo. Confira `ps -o stat` procurando `Z`, e não a tela.

### O 07 e o 08 são um par, e é isso que os torna medida

[`07-controle-sem-time.txt`](07-controle-sem-time.txt) e
[`08-so-troca-de-time.txt`](08-so-troca-de-time.txt) são **iguais linha a
linha até a marca `= ARRANQUE`**; o 08 tem duas linhas a mais, que trocam o
time pelo teclado. Medido com `WINEDEBUG=+seh,+loaddll`: **0 violações de
acesso no 07, 309 no 08** — uma variável de diferença.

O 06 também trava, e por isso **não** serve de par: ele clica as oito áreas
antes de trocar de time, o que são oito variáveis a mais.

Editar um dos dois sem o outro quebra a afirmação; o
[`../../tools/test_analisar_crash.py`](../../tools/test_analisar_crash.py)
compara os dois cabeçalhos e falha se divergirem. O veredito de onde a falha
cai está em [`../../re/crash.md`](../../re/crash.md).

### O 09 é o que o 06 deixou de poder ser

O [`09-areas-com-time.txt`](09-areas-com-time.txt) troca de time **primeiro** e
só então exercita cada área — que é a ordem natural, e era impossível enquanto
trocar de time matasse o app. A CORR-WTE-044 mediu a causa e o contorno: com
`roms/japanese-shift-jis.bin` o `wte.exe` passa da troca de time com **zero**
violação de acesso, contra 49.749 com a europeia.

**Ele só vale com a imagem japonesa.** Rodá-lo contra a europeia mede o
travamento, não as áreas. O `--imagem` não tem padrão que sirva aqui:

```sh
bash wte/tools/diff_dirigido.sh wte/tests/roteiros/09-areas-com-time.txt \
     --imagem roms/japanese-shift-jis.bin
```

Duas coisas que ele ensina sobre dirigir este app, e que custaram três
sessões exploratórias:

- **botão de área abre diálogo, e o diálogo é modal.** `boton_barras2iso` e
  `boton_nombres2iso` abrem a caixa `W11 TE PT!` (282×113, `Ok` em (142,80));
  `colorear` abre o `ficha_color` (`Cor`, 542×225, `OK` em (492,204));
  `mostrar_jugador_1` pergunta antes (`Calcular precos`, 285×124, `Sim` em
  (182,86)). Deixar qualquer um aberto **engole todos os cliques seguintes**, e
  o roteiro parece ter parado de funcionar;
- **`xdotool windowkill` num diálogo mata o processo inteiro.** Fechar é
  clicando no botão. Foi assim que uma sessão exploratória morreu no primeiro
  passo.

### O 10 e o 11 são a 5ª passagem, e dividem o trabalho por natureza

Depois do 09 sobravam 35 dos 50 `OFS_*` sem veredito dinâmico, e eles não
faltavam pelo mesmo motivo:

- [`10-telas-que-faltavam.txt`](10-telas-que-faltavam.txt) — o que faltava era
  **tela**: a estratégia, a ficha do jogador, o dorsal, o outro lado da janela,
  a extração do uniforme, o diálogo de textura;
- [`11-varredura-de-times.txt`](11-varredura-de-times.txt) — o que faltava era
  **índice**: `OFS_PLAYER_NAME_5..8`, `OFS_PLAYER_ATTR_1..9` e os `OFS_ML_*` são
  blocos com passo de setor, e o time do topo da lista endereça sempre o
  primeiro. Nenhuma tela nova resolve isso; descer na lista resolve.

Os dois só valem com a imagem japonesa, pela mesma razão do 09.

**Arquivo que o roteiro manda gravar tem de não existir antes.** O 10 extrai o
uniforme para `E:\u.bmp`; com o arquivo no lugar, o `TSaveDialog` abre a
confirmação de sobrescrita, que roteiro fixo nenhum espera — e a corrida morre
esperando a janela seguinte. Quem apaga é o `diff_dirigido.sh`, antes de copiar
a imagem.

### Os `golden-*` sao do gate, e falam o mesmo dialeto

[`golden-01-arranque.txt`](golden-01-arranque.txt) e o roteiro do gate da
[WTE-TASK-22](../../../docs/tasks/22-harness-golden.md), rodado pelo
[`../../tools/golden_check.sh`](../../tools/golden_check.sh). Duas diferencas
em relacao aos da WTE-TASK-19, e as duas existem porque o gate roda o **mesmo**
roteiro em **dois** lados:

- **`@IMAGEM@` no lugar do nome do arquivo.** Cada lado abre a sua copia, e
  copia tem nome proprio; nome fixo obrigaria dois roteiros, e dois roteiros
  deixam de ser a mesma entrada — que e a condicao de a comparacao valer;
- **`conhecida: <inicio>..<fim>` no cabecalho.** A faixa em que os dois lados
  podem divergir, declarada junto da operacao que a produz e nao numa lista
  central. Sao offsets **0-based e inclusivos**, como o `KNOWN_START`/`KNOWN_END`
  do `newWe2002` — e **nao** as posicoes 1-based do `cmp -l`, confusao que ja
  custou uma correcao (CORR-WTE-025).

**Declaracao que nao aparece reprova o gate** (codigo 3). Um gate que so
subtrai excecao passa verde quando o roteiro para de exercitar o que dizia
exercitar.

**Hoje nenhum roteiro declara faixa nenhuma, e isso e resultado, nao descuido.**
As unicas duas que existiam -- `1921862..1921862` e `2012984..2012985` -- eram
as faixas do arranque que o oraculo gravava e o port nao, e ficaram sem
explicacao da WTE-TASK-25 ate 2026-08-20. Os autores estavam escondidos a plena
vista: `0x00411616` no `FormShow` e `0x0040c19e` no `boton_dialogo_weClick`, os
dois com o endereco **imediato** no `.text`, o que e exatamente o motivo de
procurar por `OFS_LINK_ML` nunca os ter encontrado. A oitava passagem da
WTE-TASK-27 portou os dois remendos, os dois lados passaram a gravar, e as
declaracoes tiveram de sair -- pela propria regra do paragrafo acima.

## `espera:` e para o passo que vem depois de acao cara

O limite default de `>` e `>~` e 30s (`ROTEIRO_ESPERA_PADRAO` no
[`../../tools/roteiro.sh`](../../tools/roteiro.sh)), dimensionado para maquina
descarregada. Passo que vem logo depois da acao mais cara do roteiro estoura
esse limite quando a maquina esta ocupada: o `golden-14-uniforme` reprovou por
tempo em 3 de 4 corridas de controle, medido na
[CORR-WTE-080](../../../docs/tasks/CORR-WTE-080.md), sempre no dialogo que vem
logo apos a troca de time.

`espera: <seg>` sobe o limite **so da proxima janela**, e volta ao default
depois. Vale so para a proxima de proposito: espera longa em todo passo esconde
o caso em que o app nao subiu, que e o outro lado da mesma mensagem.

E as duas falhas dizem coisas diferentes desde a CORR-WTE-080 -- se a
**primeira** janela do roteiro nunca aparece, quem nao subiu foi o app, e o log
a olhar e o do Wine ou o da LCL; se ja havia janela achada, o app esta vivo e o
que nao veio foi o dialogo daquele passo.

## O `>` TROCA A ORIGEM das coordenadas, e nao so espera

Custou uma corrida em 2026-08-20. Depois de um `> Abre` para o dialogo do
cartao, todo `! clique` seguinte e relativo AO DIALOGO -- e um clique pensado
para a janela principal vai parar longe dela. Roteiro que abre um dialogo no
meio tem de **voltar** com um `>` para a janela principal antes do proximo
clique nela:

```text
> Abre
! clique 315 304
! texto E:\entrada.mcr
! tecla Return
~ 4

> W11 Team Editor PT by chagas_michel!    <- sem isto o clique abaixo erra
~ 2
! clique 52 292
```

O sintoma engana: o botao nunca e clicado, o trace nao acusa I/O nenhum na
marca, e parece **botao desabilitado** ou handler que nao faz nada.

## Janela orfa no `:98` quebra a espera por nome, e `pkill` nao a limpa

O README ja avisa que **o processo morre e a janela sobrevive**; o caso espelho
custou tres corridas em 2026-08-20. Uma sonda abortada deixou as janelas do
`wte.exe` mapeadas no `:98`, e a corrida seguinte parou em
`ERRO: janela 'Cuidado' nao apareceu em 30s` -- com a janela `Cuidado`
**visivel na tela**. A espera por nome filtra pelo `_NET_WM_PID` do processo
que o proprio script lancou, entao a janela velha nao serve, e a nova nunca
apareceu porque o `Abre` que o roteiro dirigiu foi o velho.

`pkill -9 -f we-team-editor.exe` **nao basta**: as janelas sao do wineserver,
nao do processo. O que limpa e

```sh
env WINEPREFIX="$PWD/work/wineprefix-wte" "$WINE_BIN/wineserver" -k
```

Confira antes de acusar o roteiro:

```sh
DISPLAY=:98 xdotool search --name '.' | while read i; do \
  echo "$i :: $(DISPLAY=:98 xdotool getwindowname $i)"; done
```

## As tres afordancias de arquivo do lado port

`WTE_TEXTURA`, `WTE_MCR_ENTRADA` (entradas) e `WTE_MCR` (saida) existem pela
mesma razao, e ela nao e conveniencia: **o `TOpenDialog`/`TSaveDialog` do gtk2
nao se dirige por coordenada fixa no `:98`**. O oraculo digita o caminho no
dialogo; o port o recebe por ambiente, e o `golden_run_laz.sh` as repassa
quando o chamador as define. O arquivo e o MESMO dos dois lados -- e o que faz
a comparacao valer.

O par [`golden-01-arranque.port.txt`](golden-01-arranque.port.txt) e a
assimetria temporaria: o port nao recebe teclado no `:98`, entao nao dirige o
dialogo de abrir -- ele carrega pela linha de comando desde a WTE-TASK-25.
Quando o teclado chegar (ou um window manager), o arquivo
some e o gate roda um roteiro so.

### Os `27-*` sao da gravacao, e o par de sondas mede o buffer

[`golden-02-gravacao.txt`](golden-02-gravacao.txt) e o roteiro do **diff de
controle** da [WTE-TASK-27](../../../docs/tasks/27-handlers-de-gravacao.md):
carrega um time e manda gravar sem tocar em campo nenhum.

Ele tem uma coisa que nenhum roteiro anterior precisava, e que nao e enfeite:
**cada bloco termina com uma troca de time, e so entao a marca de corte.** O
`wte.exe` grava pela saida bufferizada do runtime C, entao clicar o botao nao
produz syscall -- os bytes ficam no buffer e so vao ao arquivo quando algo
depois procura noutro ponto do mesmo arquivo (`fseek` esvazia a saida pendente
antes de mover).

O par [`27-descarga-sem.txt`](27-descarga-sem.txt) /
[`27-descarga-com.txt`](27-descarga-com.txt) mede exatamente isso, com **uma**
variavel de diferenca -- iguais linha a linha, e o `-com` troca de time depois
do clique. Medido: **zero** escrita no `-sem`, os 5 bytes em 2328184 no `-com`.
Editar um sem o outro quebra a afirmacao; o
[`../../tools/test_gravacao_controle.py`](../../tools/test_gravacao_controle.py)
compara os dois corpos e exige que o resultado medido continue oposto -- mesma
guarda que o par 07/08 tem.

Os `golden-03` e `golden-04` sao o gate de UMA gravacao, a das barras, e
existem em par porque so o segundo julga:

| roteiro | o que mede |
|---|---|
| [`golden-03-barras.txt`](golden-03-barras.txt) | gravar **sem editar** |
| [`golden-04-barras-editada.txt`](golden-04-barras-editada.txt) | editar pela tela e **entao** gravar |

Sem edicao os dois lados escrevem os bytes que ja estavam la, e **um port que
nao gravasse nada passaria igual**. O `golden-04` muda `bar_defence` do time 2
de 4 para 6 antes de mandar gravar, e ai o gate distingue as duas coisas. O
estimulo dele nao e novo: as tres coordenadas (3 `Down`, `sel_barra1` em
(30,112), trilha em (190,200)) sao as que o
[`../../tools/compara_tela.sh`](../../tools/compara_tela.sh) mediu nos dois
lados em 2026-08-12.

Cada um tem `.port.txt` proprio, e a assimetria e uma so: o `Ok` do
`ficha_info3` fica em (142,80) no oraculo e em (140,56) no port. Sob Wine sem
gerenciador de janela a moldura e desenhada DENTRO da janela X (3 px de borda,
29 de titulo); sob gtk2 a janela E o cliente.

O [`27-nomes-editados.txt`](27-nomes-editados.txt) e sonda de outra natureza:
ele nao mede o buffer, mede ONDE cada campo grava. O
`boton_nombres2iso` enche 18 registros (3 campos x 6 blocos) e manda gravar, e
o trace so mostra fronteira de DESCARGA -- duas gravacoes vizinhas caem na
mesma faixa. Digitar um texto distinto nos tres campos antes de gravar faz o
`cmp` atribuir cada bloco ao seu campo, e foi assim que os dez blocos da spec
do handler foram medidos. O texto e o time sao os do `compara_tela.sh --nomes`,
ja medidos nos dois lados.

O [`golden-05-nomes.txt`](golden-05-nomes.txt) e a mesma sequencia da sonda,
virada gate: ele grava os dez blocos de nome do time 2. Rodou nos DOIS modos --
`controle` byte-identico antes do `golden`, e isso nao e formalidade aqui:
roteiro que DIGITA tem uma fonte de nao-determinismo que roteiro de clique nao
tem, e o controle e o unico lugar onde ela apareceria.

O [`golden-06-textura.txt`](golden-06-textura.txt) e o unico roteiro do gate
que precisa de um arquivo EXTERNO, e ele nao esta versionado -- `work/` e
gitignored. O cabecalho traz o comando de uma linha que o recria, e os **5000
bytes** dele sao escolha, nao acaso: nao sendo multiplo de 2048, exercitam o
bloco parcial e o enchimento com zero. Com uma fonte de 40960 bytes um port que
gravasse so o que leu passaria, e falharia com qualquer outra.

E o unico tambem em que o lado port recebe algo por VARIAVEL DE AMBIENTE: o
`TOpenDialog` do gtk2 nao se dirige por coordenada fixa sem gerenciador de
janela, entao o oraculo escolhe pelo dialogo e o port recebe `WTE_TEXTURA`. Os
dois terminam com o MESMO arquivo, que e a condicao de a comparacao valer.

O par [`27-mcr.txt`](27-mcr.txt) / [`golden-07-mcr.txt`](golden-07-mcr.txt) e o
unico do grupo cuja gravacao NAO acontece na imagem: o `grabar_memory` emite um
`.mcr` de 128 KiB e a ROM sai intacta. Medido: o `cmp` da sonda acusa so os sete
setores do arranque e os dois bytes de arranque, e as seis faixas de `GRAVA_MCR`
no trace sao todas de LEITURA.

Isso obrigou uma regua nova no gate -- `golden_check.sh --artefato saida.mcr`.
Comparar so as duas imagens aprovaria um port que nao fizesse nada, porque as
duas sairiam iguais de qualquer jeito. O `--artefato` apaga `work/saida.mcr`
antes de cada lado, guarda o que aquele lado produziu e compara os dois; a
comparacao das imagens continua valendo pelo motivo inverso, que e provar que a
gravacao nao vazou para dentro da ROM.

O lado port recebe o destino por `WTE_MCR`, e aqui a variavel e mais necessaria
do que no `golden-06`: o `TSaveDialog` do gtk2 exige um nome DIGITADO, e sem
gerenciador de janela o `:98` nao entrega tecla a ele. O `golden_check.sh`
semeia a variavel com o mesmo `work/saida.mcr` que o oraculo digita.

O par [`27-dorsal-editado.txt`](27-dorsal-editado.txt) /
[`golden-08-dorsal-mcr.txt`](golden-08-dorsal-mcr.txt) fecha o criterio herdado
da WTE-TASK-26 -- o unico do projeto que julga edicao e gravacao juntas. Ele
exercita DUAS gravacoes numa corrida so: a escrita pontual do numero na imagem
(`dorsalClick`, `0x00404048`) e o `.mcr`, que le os 23 `dorsalN` DA TELA. Editar
o numero antes e o que tira os 16 bytes de `0x5404` do cartao da situacao de
serem conferidos contra um valor que ninguem tocou.

**O passo da barra foi medido nos dois widgetsets antes de o roteiro existir**,
como a trilha do `track_barra` exigiu na WTE-TASK-26: clique no meio da trilha
pagina por `LargeChange = 4`, os dois andam igual, e o time 2 vai de
`dorsal1 = 1` para 5 -- um byte, em 404748.

Aqui apareceu uma limitacao do proprio driver, e ela e do `>~`: o
`xdotool search --name '.'` **nao enxerga** janela cujo `WM_NAME` e Shift-JIS
cru, porque a regex casa contra o nome ja decodificado. Sob Wine o
`ficha_dorsal` aparece; sob gtk2 nao. Como os tres formularios que precisam de
busca por tamanho sao exatamente os que trocam o Caption por nome de jogador ou
de time, o `janela_geo` passou a enumerar por `--pid` quando ha filtro de
processo, caindo no nome so quando nao ha.

O par [`27-mover.txt`](27-mover.txt) / [`golden-09-mover.txt`](golden-09-mover.txt)
mede a metade de escrita que os OITO handlers de mover compartilham
(`0x00404820`). Os quatro botoes de mover um jogador so tem o mesmo corpo e a
mesma rotina de gravacao -- exercitar um exercita a rotina; o que muda entre eles
e qual lado e a origem.

Ele e o unico roteiro do gate que precisa de **quatro combos preenchidos**: o
`paderecha` nao faz nada sem time e jogador dos dois lados, e a guarda le o
`ItemIndex` do jogador de DESTINO antes de qualquer outra coisa -- por isso a
direita vem primeiro. Medido: o destino da sequencia e o time 1, slot 1, com 10
bytes de nome em 388336 e 12 de atributos em 2179780.

Duas consequencias que valem para todo roteiro de gravacao que vier depois:

- **roteiro que termina numa gravacao mede um oraculo truncado**, porque o
  harness encerra com `wineserver -k` e o buffer se perde;
- **marca de corte antes da descarga credita a faixa a acao seguinte.** Foi o
  que aconteceu na primeira medicao: os 5 bytes das barras apareceram como se
  fossem dos nomes, num TSV que parecia medido.

### O `golden-15` julga uma gravacao SEM editar campo nenhum

O par [`golden-15-ficha.txt`](golden-15-ficha.txt) /
[`.port.txt`](golden-15-ficha.port.txt) e o gate do
`jugador.BitBtn3Click` -- o `Comple.` da ficha --, aberto pela
[CORR-WTE-081](../../../docs/tasks/CORR-WTE-081.md). Ele parece violar a licao
do `golden-03`: nao toca em barrinha, nem em seta, nem em caixa de texto, e
mesmo assim distingue um port que grava de um que nao grava.

O que o torna medida e que **o `Comple.` e destrutivo por si so**. Os dez bytes
de nome saem do campo `casilla_nombre`, e o campo mostra o nome ja FILTRADO
pelo `0x0040b2d8` -- com a ROM japonesa, uma corrida de `?`. Clicar `Comple.`
sem editar nada grava `3f 3f 3f 3f` por cima de `ba b0 d7 dd`. Medido nos dois
lados, em `OFS_PLAYER_NAME+774`.

Duas coisas que ele ensina sobre dirigir a ficha:

- **a janela `jugador` mede os 707x273 do DFM sob Wine**, sem os 6x32 de
  moldura que o `ficha_dorsal` ganha. Os tres formularios que precisam de `>~`
  nao se comportam igual, e supor a moldura erra o clique;
- **a pergunta `Calcular precos` nao aparece nesta ordem.** Quem a provoca e o
  `base_team`, nao o `mostrar_jugador_1` -- ja estava medido no cabecalho do
  [`10-telas-que-faltavam.txt`](10-telas-que-faltavam.txt), e esperar por ela
  custou uma corrida de controle.

### O `golden-16` volta a precisar de edicao, e a razao e o oposto do `15`

O par [`golden-16-cor.txt`](golden-16-cor.txt) /
[`.port.txt`](golden-16-cor.port.txt) e o gate do `ficha_color.BitBtn3Click` --
o `OK` do editor de cor, a setima rota de escrita na imagem --, tambem da
[CORR-WTE-081](../../../docs/tasks/CORR-WTE-081.md).

Aqui a edicao e obrigatoria, e vale ver por que os dois gates vizinhos se
comportam ao contrario: as sete regioes do bloco de cor saem do que a carga leu
da imagem, entao clicar `OK` sem editar devolve os mesmos bytes e um port que
nao gravasse nada passaria. E a objecao que o `golden-03` teve de responder com
o `golden-04`; no `golden-15` ela nao existia porque o `Comple.` e destrutivo
sozinho.

**A edicao e um clique so.** O `aclarar` percorre a faixa do gradiente inteira
-- que nasce 1..16 --, entao nao depende de amostra selecionada nem de estado
do `recuadro2`. Medido: 30 bytes mudam em `OFS_FLAG_COLOURS+96` e mais nada
alem dos tres do arranque, embora a corrida grave 383.

A janela `Cor  ` mede os 542x225 do DFM sob Wine, sem moldura -- como a
`jugador` do `golden-15`, e ao contrario do `ficha_dorsal` do `golden-08`.

## Replicar

Lado port, com o trace num arquivo próprio:

```sh
WTE_TRACE_FILE=/tmp/t.log ./wte/build/wte &
# some a origem da janela em cada linha '!' e execute
```

Lado original: `make wte-98`, mesma sequência, **sem** trace — o `wte.exe` não
loga nada, e a leitura é por efeito de tela. Ver
[`../../re/eventos.md`](../../re/eventos.md).

## O teclado chega no app LCL, e a medição que dizia o contrário foi refeita

**Esta seção afirmava o oposto até 2026-08-21**, e vale manter o registro da
volta: a WTE-TASK-13 mediu que nenhuma tecla chegava ao GTK2 no `:98` — sem
window manager a janela nunca fica ativa —, o `golden_run_laz.sh` passou a
**reprovar** roteiro de port com `! tecla`, e o README escreveu "nenhum roteiro
do lado port usa tecla". Hoje **13 dos 14** `.port.txt` do gate usam, e passam.

O que faltava era um `xdotool windowfocus` antes. Ele é `XSetInputFocus`, não
precisa de gerenciador de janela, e com ele a tecla chega — remedido na
WTE-TASK-26 com 3 `Down` sobre a janela focada dando 3 disparos de
`lista_equiposChange` no trace do port. Quem faz isso é o `ROTEIRO_FOCO=1` do
[`../../tools/roteiro.sh`](../../tools/roteiro.sh), ligado **só do lado port**:
o oráculo não precisa, porque o Wine implementa o próprio foco, e mexer nele
invalidaria o controle sem ganho nenhum.

O que continua valendo é o resto do diagnóstico: `xdotool key --window` usa
`XSendEvent` e o GTK2 **descarta**; `xdotool windowactivate` precisa de
gerenciador e falha; e não há gerenciador instalado nesta máquina (`twm`,
`openbox`, `metacity`, `mutter`, `xfwm4`, `i3`, `fluxbox`, `icewm`, `jwm`,
`matchbox`, `marco`, `herbstluftwm`, `dwm`, `awesome` — nenhum encontrado).
**Instalar pacote continua sendo decisão do usuário**; o que mudou é que
deixou de ser necessário.

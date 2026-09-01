---
id: WTE-TASK-35
title: "Registro das divergências deliberadas"
type: verificação
category: verificação
phase: 6
depends_on: ["WTE-TASK-34"]
fonte_de_verdade: "/docs/PLAN-WTE-LAZARUS.md Fase 6 item 2 e §0"
status: concluído
---

# WTE-TASK-35: Divergências deliberadas

## Contexto

- **Referência:** `docs/PLAN-WTE-LAZARUS.md` Fase 6 item 2 e §0.

> **"100%" aqui significa: todo handler com veredito escrito e toda gravação
> byte-idêntica.** Não significa que nenhuma divergência é aceita — significa
> que nenhuma é *desconhecida*.

O precedente é o `newWe2002`, cujo escopo Linux fechou com **uma** divergência
aceita: a faixa de 16 bytes em `405724..405739`, o slot 64 de um array de 63 que
o `ed.exe` lê e grava a partir de memória vizinha. Documentada, explicada,
reproduzida no golden test como exceção nomeada.

**Diferença de política em relação ao `newWe2002`:** lá o objetivo era clonar o
`ed.exe` inclusive nos defeitos. Aqui o plano (§0) permite **não** reproduzir bug
do original — mas exige registro.

---

## Objetivo

Um documento no formato que o
[`PARIDADE-FUNCIONAL.md`](/docs/PARIDADE-FUNCIONAL.md) já usa: o que diverge, por
quê, e que evidência sustenta.

### Cada entrada precisa de

| Campo | Por quê |
|---|---|
| o que diverge | a operação e os bytes, ou o comportamento visível |
| natureza | bug do original, limitação de plataforma, ou escolha |
| decisão | reproduzir, corrigir, ou não implementar |
| razão | por que essa decisão e não outra |
| evidência | o diff, a captura, ou o teste que mostra |
| onde o teste sabe | se a bateria golden precisa de exceção nomeada |

O último campo é o que evita divergência documentada virar divergência
silenciosa: uma exceção no golden sem entrada aqui é buraco.

### Candidatas já conhecidas antes de a task rodar

- **Sufixo ` [Lazarus]` no `Caption` dos 18**
  ([WTE-TASK-11](/docs/tasks/concluidos/11-app-com-a-casca-completa.md)) — **já está no
  código**, diferente das outras quatro, que são hipóteses.
  *Natureza:* escolha. *Decisão:* manter.
  *Razão:* o `Caption` vem do DFM, e o do `MainForm` é literalmente
  `' W11 Team Editor PT by chagas_michel!'`; a partir da WTE-TASK-22 os dois
  editores rodam no mesmo `:99` e o harness acha janela por título e por
  tamanho — título igual faria ele dirigir o lado errado (armadilha 6 do
  [`progresso.md`](/docs/tasks/concluidos/progresso.md)).
  *Evidência:* posto em tempo de execução por `MarcaOsTitulos`, em
  `wte/src/wtemain.pas`, não no `.lfm`, que é gerado.
  *Onde o teste sabe:* no `:99` não há window manager, nenhuma barra de título
  é desenhada, e a captura da
  [WTE-TASK-12](/docs/tasks/concluidos/12-comparacao-visual.md) não enxerga o sufixo —
  num desktop de verdade enxerga, e deve.
- **Tolerância de cor do render 2D** (WTE-TASK-29), se a igualdade exata não
  sair.
- **Cinco glifos que não acinzentam** — medido pela
  [CORR-WTE-060](/docs/tasks/concluidos/CORR-WTE-060.md) em 2026-08-18, e **já está no
  código**, como o sufixo acima: não é hipótese, é comportamento em produção.
  *Natureza:* limitação de plataforma (widgetset), não bug do original nem do
  port. *Decisão:* não reproduzir.
  *Razão:* a LCL desenha o glifo de um botão desabilitado aplicando
  `gdeDisabled`, que é **conversão para tons de cinza**; pixel com `R = G = B`
  é ponto fixo dela. Glifo desenhado só com preto e branco puros sobre a cor
  transparente é portanto **invariante**, e o botão apaga logicamente sem mudar
  um pixel. O `comctl32` do Win32 não faz grayscale — monta o glifo
  desabilitado de uma máscara monocromática, em que preto vira sombra
  (`#A6A6A6`) e branco vira transparente. Igualar exigiria desenhar à mão um
  segundo glifo (`NumGlyphs = 2`) que **não existe no recurso do original**, ou
  reescrever o `TButtonGlyph` da LCL.
  *Evidência:* `iguala_nombres` muda **518 px** no oráculo sob Wine e **0** no
  port (`compara_tela.sh --habilitacao`, recorte `(344,184,73,25)`). As duas
  hipóteses anteriores — cor transparente e `ParentFont` — foram **refutadas**
  num harness LCL isolado: `ParentFont := True` continua dando 0 px, e recolorir
  o glifo do vizinho para a mesma cor de fundo dá 513 px, não 0. A regra é o
  grayscale, e o número fecha dos dois lados: `boton_nombres2iso` tem **280
  pixels não-cinza** no glifo e muda **280 px** no app rodando. Detalhe em
  [`MainForm.iguala_nombresClick`](../../../wte/re/spec/MainForm.iguala_nombresClick.md).
  *Onde o teste sabe:*
  [`check_glifos_disabled.py`](../../../wte/tools/check_glifos_disabled.py) varre
  os **59** botões com glifo dos 18 formulários e declara os **5** invariantes —
  `iguala_nombres`, `parriba`, `pabajo` (`MainForm`), `oscurecer` e `aclarar`
  (`color`). Glifo que entre ou saia desse conjunto derruba o
  `make -C wte check`. O `compara_tela.py` precisa da mesma exceção nomeada
  quando os cinco forem exercitados — hoje só o `iguala_nombres` cai na faixa
  medida, e ele aparece lá como `DIVERGE`.
- **Cara, cabelo e barba da ficha não redesenham** — decidido pela
  [CORR-WTE-063](/docs/tasks/concluidos/CORR-WTE-063.md) em 2026-08-18, e, como as duas
  entradas acima, **não é hipótese**: é o que o port faz hoje.
  *O que diverge:* cinco das doze setas de aparência do formulário `jugador` —
  `flechasapa2` (tom de pele), `3` e `4` (forma e cor do cabelo), `5` e `6`
  (forma e cor da barba) — mudam o rótulo e **não** mudam o desenho. No
  original elas repintam `imagen_base`, `imagen_pelo` e `imagen_barba` por três
  carregadoras de bitmap — `0x00406fe0` (`image/careto_base.bmp`, 301 B),
  `0x00407110` (`image/pelo/pelo_<n>.bmp`, 552 B) e `0x00407338`
  (`image/barba/barba_<n>.bmp`, 561 B), **1.414 B somados** —, chamadas pelo
  segundo despachante do `jugador.flechasapaClick`. Nenhum byte da imagem de CD
  entra na conta: o handler não alcança nenhuma das duas escritoras.
  *Natureza:* escolha de escopo. Não é bug do original nem limitação de
  widgetset — as três rotinas estão lidas e medidas, e a LCL desenharia o
  resultado sem novidade.
  *Decisão:* não implementar.
  *Razão:* as três abrem o `.bmp` em `"r+b"` (a cadeia de modo em
  `0x004249cd`), dão `fseek` para a entrada 10 da paleta (`0x5e` = 54 + 10 × 4)
  e **regravam a paleta dentro do próprio arquivo de asset** antes de
  recarregá-lo por `LoadFromFile`. Como `pelo_<n>.bmp` e `barba_<n>.bmp` são
  compartilhados por todos os jogadores e o `make -C wte assets` liga a pasta
  de assets em `we-team-editor/`, do usuário, mexer numa seta de cabelo
  reescreveria o arquivo que todos usam, na pasta do Obocaman. As saídas seriam
  duas — reproduzir a gravação in-place, tornando o porte read-write sobre dado
  do usuário, ou escrever um segundo caminho de recolorir em memória, que é
  trabalho que nenhuma task pediu — e **nenhuma das duas tem dono**: a
  [WTE-TASK-26](/docs/tasks/concluidos/26-handlers-de-edicao.md) é dona de handler e
  excluiu as três; a [WTE-TASK-29](/docs/tasks/concluidos/29-camisa-e-bandeira-2d.md) é
  dona de asset, mas dos dois do `MainForm` — uniforme e bandeira —, e não cita
  cara, cabelo nem barba. Caíam entre as duas definições, e é a própria 26 que
  escreve a regra: *"Exclusão sem dono nomeado é buraco, e este projeto já
  pagou por isso na 25."* Esta entrada é o dono.
  *Evidência:* o efeito visível está escrito na spec do handler
  ([`jugador.flechasapaClick`](../../../wte/re/spec/jugador.flechasapaClick.md)) —
  rótulo muda, desenho não. As medições vêm da §5, da §5.1 e da §6 do
  [`assets.md`](../../../wte/re/assets.md): as três tabelas de cor em `.data` —
  pele `0x00423998` (0x40 bytes, 16 entradas a partir da 10, passo 64, 4 tons),
  cabelo `0x00423a98` (0x14 bytes, 5 entradas, passo 20, 8 cores) e barba
  `0x00423b38` (0x0c bytes, 3 entradas, passo 12) —, o `careto_base.bmp` único
  (não há `careto_<n>`: o rosto é um só e o tom de pele é troca de 16 entradas
  de paleta), e as contagens de arquivo que fecham com o `Max` do DFM — 32
  `pelo_` contra `Max` 31 do `flechasapa3`, 7 `barba_` contra `Max` 6 do
  `flechasapa5`. Que a gravação acontece de verdade não precisou de teste
  destrutivo: a §6.1 lê o `mtime` dos 198 `.bmp` — 176 de 2002, 19 de 2006 — e
  acha **três** reescritos no mesmo segundo de 2026-08-05, a primeira sessão de
  `make wte` nesta máquina, com o tamanho intacto. Os três são os do `MainForm`
  (`bandera37`, `camiseta2`, `pantalon0`), porque a ficha do jogador não foi
  aberta naquela sessão; o mecanismo é o mesmo nas seis rotinas.
  **O que esta exclusão não cobre:** a saturação em `7` do `beard_style`. O
  disco guarda 3 bits (0..7), o `Max` do controle é 6 e só existem `barba_0..6`;
  o `TUpDown` do original satura em `Max`, então um 7 vindo do disco vira 6 na
  tela e **vira 6 no disco** ao gravar (§5.1). Isso é comportamento de gravação,
  é da [WTE-TASK-27](/docs/tasks/concluidos/27-handlers-de-gravacao.md), e não deixa de
  valer por o desenho não sair.
  *Onde o teste sabe:* **nenhuma régua alcança o formulário `jugador`**, e por
  isso esta entrada não pede exceção nomeada em lugar nenhum. A bateria de bytes
  não passa por aqui — o handler não grava na imagem. A de pixel também não: o
  [`compara_tela.py`](../../../wte/tools/compara_tela.py) mede a janela do
  `MainForm` (as cinco barras de força, e a mudança de aparência no
  `--habilitacao`), e os três modos do
  [`compara_tela.sh`](../../../wte/tools/compara_tela.sh) — `--edicao`, `--nomes`,
  `--habilitacao` — partem todos dali; o
  [`check_edicao.py`](../../../wte/tools/check_edicao.py) já registra, para os
  handlers da ficha, *"sub-dialogo que nenhuma regua de tela alcanca"*. O
  instrumento nomeado do `flechasapaClick` naquela tabela é o
  [`check_bitfields.py`](../../../wte/tools/check_bitfields.py), que prende a
  **identidade** dos campos de aparência — os 12 registros de `0x00423708`
  contra o `Player.Decode` do `we2002_core` — e não diz nada sobre desenho.
  Se alguma passagem futura criar régua para o `jugador`, ela nasce com as três
  imagens divergindo, e é esta entrada que explica por quê.
- **O limite do `edit_nombre1` na European Deluxe** — medido pela
  [CORR-WTE-064](/docs/tasks/concluidos/CORR-WTE-064.md) em 2026-08-18, e **já está no
  código**.
  *O que diverge:* o `MaxLength` do primeiro campo de nome, em **49 dos 95**
  times, e **só na imagem European Deluxe**. Na japonesa os dois lados
  concordam nos 95.
  *Natureza:* consequência de uma decisão já registrada, não bug.
  *Decisão:* manter.
  *Razão:* o original **anda pelo arquivo** a cada troca de time, medindo a
  largura do registro como "bytes não-zero até o próximo não-zero". O port não
  reabre a imagem — decisão medida, escrita no cabeçalho do
  [`lista_equiposChange.inc`](../../../wte/src/impl/ep2002_mainform.lista_equiposChange.inc)
  — e tira o número de `TEAM_NAME_KANJI_LEN`, do `we2002_core`. Os dois
  caminhos dão o mesmo resultado quando o slot de kanji contém kanji. Na
  European Deluxe nomes latinos foram escritos em slot de kanji e deixaram
  lixo depois do terminador, então a distância ao próximo registro encurta e a
  medição em tempo de execução não bate mais com a tabela. Reproduzir exigiria
  o port reabrir a imagem a cada troca de time, que é a decisão contrária.
  *Evidência:* emulada a travessia do original sobre as duas imagens,
  `(largura − 1) div 2 == TEAM_NAME_KANJI_LEN − 1` em **95/95** times na
  japonesa e **46/95** na European Deluxe. O lote `OFS_TEAM_NAME_3`, que o
  `edit_nombre2` usa, bate **95/95 nas duas** — o problema é do slot de kanji,
  não do método.
  *Onde o teste sabe:* o `compara_tela.sh --nomes` roda sobre a imagem
  japonesa (`WTE_TELA_IMAGEM` tem esse padrão), onde não há divergência. Rodar
  o mesmo modo apontando para a European Deluxe acusaria — e **acusaria
  corretamente**, então não há exceção a nomear, e sim uma imagem a escolher de
  propósito.
- **O preço do 23º jogador nunca é gravado** — medido pela
  [CORR-WTE-095](/docs/tasks/concluidos/CORR-WTE-095.md) em 2026-08-24, e, como as três
  entradas acima, **não é hipótese**: é o que o port faz hoje, por
  `ULTIMO_SLOT_PRECADO = 21` no
  [`base_teamClick.inc`](../../../wte/src/impl/ep2002_mainform.base_teamClick.inc).
  *O que diverge:* o `MainForm.base_teamClick` do original percorre os 23 slots
  de um time e grava **22** bytes de preço, de `OFS_COST_NATIONAL + 23·t` até
  `+ 21`. O do slot 22 fica com o valor de fábrica. O port reproduz.
  *Natureza:* **bug do original**, e não do formato: o slot 22 é endereçável e o
  próprio editor o grava por outro caminho — o
  [`io-medido.tsv`](../../../wte/re/io-medido.tsv), sessão `27-mcr2iso`, traz
  `W 3067473 3067495 23`, o import de `.mcr` escrevendo os 23 bytes
  condicionais do time 3.
  *Decisão:* reproduzir.
  *Razão:* o gate da feature é byte a byte contra o oráculo
  ([`golden-22-precos`](../../../wte/tests/roteiros/golden-22-precos.txt)), e §0
  permite não reproduzir bug do original mas exige registro — aqui reproduzir é
  o que mantém o gate honesto. Gravar o 23º byte faria o port divergir do
  oráculo num byte por time em toda a operação, e a "correção" seria uma escolha
  nossa sobre dado do usuário sem nada que a valide.
  *Evidência:* três réguas independentes, todas de 2026-08-24.
  **(1) Plantio** — `0xFF` posto nos slots 20, 21 e 22 do time 2; depois da
  corrida os dois primeiros voltam **26** e **21**, o `previsto` do
  [`preco.tsv`](../../../wte/re/preco.tsv), e o terceiro continua **255**. Separa
  "não grava" de "grava o valor que já estava lá".
  **(2) `strace`** (`diff_dirigido.sh`) — o oráculo **lê** o byte condicional do
  slot 22 em 3067472, com o mesmo número de seeks dos outros 22, e a
  `0x004046e8` só faz essa leitura quando a terceira coluna **não** é zero
  (`0x00404748` desvia para `0x0040477e` no caso zero, e lá não há I/O). Logo
  não é o `je` de `0x004110ad` que pula o slot — que era a explicação corrente
  até esta correção. Contadas as syscalls, são **22** `write` de 1 byte para
  **23** voltas.
  **(3) Depurador** (`winedbg` anexado ao PID Wine) — o `call 0x00403400` do
  laço (`0x00411170`) para **23** vezes, o `fputc` dentro dela (`0x0040342a`)
  para **23** vezes, e os 23 retornam **sucesso**: o retorno é o caractere
  gravado, e o da 23ª volta é **20**, exatamente o preço que a fórmula prevê
  para o slot 22 do time 2. O byte é calculado certo, aceito pelo runtime C e
  **não vira `write`** — perde-se na saída bufferizada da Borland, abaixo do
  `fputc`. Não é pendência descarregável: o próprio roteiro faz descarga (troca
  de time, com I/O de sobra) depois do clique, e o byte continua não chegando.
  *Onde o teste sabe:* em dois lugares, e nenhum precisa de exceção nomeada,
  porque o port **reproduz**. O `golden-22-precos` compara imagem inteira e
  fecha byte-idêntico com 22 bytes dos dois lados; e o
  [`check_preco.py`](../../../wte/tools/check_preco.py) **recusa** qualquer linha
  de slot 22 marcada como medida no `preco.tsv` — se a regra cair, o
  `ULTIMO_SLOT_PRECADO` está errado e o `make -C wte check` diz isso.
- **O vaivém dos cobradores na segunda gravação — não existe no `wte.exe`** —
  encaminhado pela
  [WTE-TASK-34](/docs/tasks/concluidos/34-bateria-golden-completa.md) e medido pela
  [CORR-WTE-104](/docs/tasks/concluidos/CORR-WTE-104.md) em 2026-08-25. É **resultado
  negativo**, e entra aqui por isso: o que precisa de decisão não é uma
  divergência a reproduzir, é o **enunciado da fase 6**, que atribui ao editor
  um comportamento herdado de outro binário.
  *O que se afirmava:* que `Load`+`Save` troca os dois primeiros cobradores de
  cada clube de ML (`OFS_KICKER`) e que gravar duas vezes volta ao início. Isso
  é do **`ed.exe`**, medido pelo `newWe2002`; o `wte.exe` do Obocaman é outro
  binário e outro caminho de código, e nunca foi medido.
  *Natureza:* nenhuma — não há divergência. O port não tem o que reproduzir, e
  **não deve inventar** o vaivém para "ficar parecido" com o `ed.exe`.
  *Decisão:* **nada a corrigir no plano** — conferido em 2026-08-25, o
  `PLAN-WTE-LAZARUS.md` tem **zero** ocorrências de
  `idempot`/`cobrador`/`OFS_KICKER`/`vaivém`, e a fase 6 dele não fala em
  gravar duas vezes. A afirmação morava em dois sítios e os dois já dizem
  `ed.exe`: o enunciado da
  [WTE-TASK-34](/docs/tasks/concluidos/34-bateria-golden-completa.md), reconciliado, e a
  prosa gerada do [`golden.md`](../../../wte/re/golden.md). Resultado negativo
  escrito de propósito: quem reler daqui a um mês não refaz a busca.
  *Fora daqui, e maior:* quatro sítios do lado WTE atribuem a
  não-idempotência ao *"editor original"* — que neste projeto lê-se `wte.exe`,
  não `ed.exe` — e a medição acima cobre **um** caminho de gravação, o da
  tática. Está aberto na [CORR-WTE-109](/docs/tasks/concluidos/CORR-WTE-109.md).
  *Evidência:* o terceiro ponto, medido num time em que a troca **seria**
  visível — uma gravação de tática contra duas, pelo
  [`golden-24-gravacao-dupla`](../../../wte/tests/roteiros/golden-24-gravacao-dupla.txt)
  e por ele mesmo truncado depois da descarga. As duas imagens são **iguais**
  (0 bytes), e os seis cobradores do time 5 saem intactos dos três estados:
  `[9, 5, 5, 5, 7, 5]` na ROM virgem, depois de uma gravação e depois de duas.
  E as duas gravações **aconteceram** — 11.962 bytes diferem da ROM virgem —,
  o que impede o zero de ser dois lados parados. Está publicado em
  [`golden.md`](../../../wte/re/golden.md), pelo `check_golden.py`.
  *Por que o time importa:* até a CORR-WTE-104 o roteiro gravava no time 2,
  cujos dois primeiros cobradores são iguais (`[7, 7, …]`). Ali a troca é a
  identidade e a medição **não podia** responder em nenhum dos dois sentidos —
  a pendência que a 34 encaminhou era, sem que ela soubesse, indecidível como
  estava escrita.
  *Onde o teste sabe:* o `test_check_golden.py` lê o time do próprio roteiro e
  **reprova** se os dois primeiros cobradores dele forem iguais. Se alguém
  mover o `golden-24` de volta para um time cego, o `make -C wte check` diz
  isso antes de o número virar doc.
- **`TStaticText` no GTK2** (§8.9), se o fundo não puder ficar idêntico.
- **Rótulos cortados por fonte substituta** — acontece nos dois lados, e talvez
  não conte como divergência; decidir.
- **Comportamento de truncamento de campo** (WTE-TASK-36), se o Pascal não
  reproduzir o do buffer fixo.

### O que não entra aqui

Divergência **não** deliberada. Se algo diverge e ninguém sabe por quê, isso é
bug aberto, não entrada neste documento. Confundir os dois é como uma lista de
problemas conhecidos vira desculpa.

---

## Arquivos a criar ou modificar

| Arquivo | Ação |
|---|---|
| `wte/re/divergencias.md` | criar — o registro, escrito à mão |
| `wte/tools/check_divergencias.py` | criar — a conferência cruzada, com `--check` |
| `wte/tools/compara_tela.py` | modificar — **remover** o grupo `pendente_32` |
| `wte/tools/test_compara_tela.py` | modificar — o teste que travava a isenção |
| `wte/tools/golden_suite.sh` | modificar — o ponteiro para a regra |

*Adaptado na execução (2026-08-25).* Duas correções ao enunciado, e as duas são
achado:

**O `divergencias.md` não é gerado, e não deve ser.** As entradas são *decisão*
— por que reproduzir um bug e não outro. Prosa não se gera; um gerador que a
produzisse estaria inventando razão a partir de número. O que dá para mecanizar
é a outra metade, a que o próprio enunciado nomeia numa frase — *"uma exceção no
golden sem entrada aqui é buraco"* —, e é o `check_divergencias.py`.

**O `golden_suite.sh` não tinha exceção nomeada para receber.** Nenhum dos 23
roteiros declara `conhecida:`; a bateria de bytes fechou com zero. Ele ganhou o
ponteiro para a regra, não dado — quem acrescentar uma faixa encontra ali a
obrigação de abrir a entrada, e o `check_divergencias.py` aborta se não abrir.

---

## Critério de conclusão

- [x] Toda divergência da bateria com entrada completa — **a bateria não tem
      divergência nenhuma**: 92 corridas, zero `REPROVOU`, e **zero roteiro
      declarando `conhecida:`**. Está escrito como afirmação medida na §8 do
      registro, e o `check_divergencias.py` aborta se uma faixa nova aparecer
      sem entrada
- [x] Toda exceção do golden com entrada correspondente — **3 exceções
      nomeadas, as 3 com entrada**: `glifo_cinza` e `INVARIANTES` (§2) e
      `ULTIMO_SLOT_PRECADO` (§5). Mecanizado nos **dois** sentidos, e as
      recusas ficaram **versionadas** em
      [`test_check_divergencias.py`](../../../wte/tools/test_check_divergencias.py)
      pela [CORR-WTE-106](/docs/tasks/concluidos/CORR-WTE-106.md) — 20 casos, com os
      quatro sentidos plantados. Este critério dizia *"com as três recusas
      vistas"*, e ver não é deixar visto: as recusas da execução não
      sobreviveram a ela, e o gate era o único de recusa sem par de teste
- [x] Divergência sem causa conhecida classificada como bug aberto, não como
      deliberada — nenhuma apareceu. As seis entradas têm causa medida e
      citada; a única linha ainda aberta é o truncamento, e ela **tem dono
      nomeado** ([WTE-TASK-36](/docs/tasks/concluidos/36-buffers-e-truncamento.md)), que é
      a diferença entre pendência e buraco
- [x] As quatro candidatas conhecidas decididas — **nenhuma virou entrada**, e
      cada veredito é medido: tolerância do render 2D é **zero**; nenhum dos 37
      `TStaticText` usa `Transparent`; rótulo cortado acontece **nos dois
      lados**, pela mesma fonte substituta; truncamento é da WTE-TASK-36.
      Estão na §7 do registro
- [x] Commit no formato conventional, em inglês

## Log de Execução

- **Executado em:** 2026-08-25

- **Resumo do que foi feito:**

  Escrito o [`wte/re/divergencias.md`](../../../wte/re/divergencias.md) — **seis
  entradas** com os seis campos que o enunciado pede, mais três seções que o
  enunciado não previa e a execução exigiu. E mecanizada a metade que dá para
  mecanizar, no [`check_divergencias.py`](../../../wte/tools/check_divergencias.py).

  **O achado é uma exceção que sobreviveu à própria causa.** O grupo
  `pendente_32` do `compara_tela.py` isentava `bandera`, `home1` e `home2` de
  reprovar, com a justificativa *"quem DESENHA é a WTE-TASK-29"*. A 29 fechou em
  2026-08-21 e as CORR-WTE-083/-084 ainda consertaram a bandeira preta de dez
  times. Medido em 2026-08-25 pelo `compara_tela.sh --habilitacao`, os três
  **batem**, com números idênticos dos dois lados — 3840/3840, 2328/2328 e
  1012/1012.

  Por isso eles **não viraram entrada, viraram remoção**. Escrever entrada de
  divergência deliberada para algo que não diverge seria o defeito desta task
  pelo avesso: o documento existe para que nenhuma divergência seja
  desconhecida, e uma entrada falsa manda alguém procurar um problema que não
  existe. Os três voltaram para `segue_nacional` e agora **reprovam** se
  voltarem a divergir.

  **E as quatro candidatas que o enunciado deixou em aberto: nenhuma virou
  entrada.** Todas as quatro já tinham resposta medida em task anterior —
  hipótese que não se confirma não vira divergência deliberada, vira linha
  dizendo que foi conferida.

- **Problemas encontrados:**

  **Remover a isenção quebrou dois testes, e os dois modos de falha valem
  registro.**

  O primeiro era o teste que **travava a isenção**, com a premissa escrita no
  próprio docstring: *"desenhar a bandeira é da WTE-TASK-29, e ela ainda não
  chegou"*. Ela chegou. O teste não estava errado quando foi escrito — envelheceu
  junto com a isenção que guardava, que é a mesma **prosa vencida** que a
  terceira passagem da [WTE-TASK-31](/docs/tasks/concluidos/31-fechamento-fase-4.md)
  batizou. Foi virado ao contrário: agora bandeira que diverge de um lado só
  **reprova**.

  O segundo é mais sutil e é o que vale levar adiante. A lista `P32` do teste se
  **derivava da própria tabela sob teste** (`[n for n in CONTROLES if grupo ==
  "pendente_32"]`). Removido o grupo, ela virou **lista vazia em silêncio**, e o
  teste da bandeira passou a plantar nada e a conferir nada — passaria verde
  para sempre sem medir coisa alguma. É exatamente a armadilha que a
  CORR-WTE-020 achou no `dfm2lfm.py` e que o `check_glifos_disabled.py`
  documenta: **lista derivada da tabela que ela deveria guardar não guarda
  nada.** Agora os nomes vêm do `RENDER` do módulo.

  E há um sinal de que a remoção de fato aconteceu, em vez de ter sido só
  renomeada: a contagem de controles que contrariam a spec quando nada muda
  subiu de **9 para 12** sozinha — os três entraram na conta ao deixar de ser
  isentos.

- **Arquivos criados/modificados:** ver `git show --stat`. Criados:
  `wte/re/divergencias.md`, `wte/tools/check_divergencias.py`. Modificados:
  `wte/tools/compara_tela.py` e `wte/tools/test_compara_tela.py` (a remoção da
  isenção e os dois testes), `wte/tools/golden_suite.sh` (o ponteiro para a
  regra), `docs/PLAN-WTE-LAZARUS.md`, `docs/tasks/concluidos/progresso.md`;
  [`docs/tasks/concluidos/36-buffers-e-truncamento.md`](/docs/tasks/concluidos/36-buffers-e-truncamento.md)
  — **o repasse**: a 36 passa a ser a dona declarada da única linha em aberto
  da §7 do registro, com a forma de devolução escrita (os seis campos) e a
  obrigação de passar pelo `check_divergencias.py` se a régua ganhar isenção;
  este arquivo.

---

## Candidatas posteriores — WTE-TASK-37 (2026-08-25)

Três medidas da reconferência de UI com a lógica ligada que pediam decisão de
registro. Todas em [`wte/re/visual.md`](../../../wte/re/visual.md), segunda
passada, com captura em
[`wte/re/visual/carregado/`](../../../wte/re/visual/carregado).

> **As três foram destinadas em 2026-08-25 pela
> [CORR-WTE-114](/docs/tasks/concluidos/CORR-WTE-114.md), e esta seção virou índice.**
> Ela existia porque o repasse foi escrito na task que criou o formato — e
> esta task já estava `concluído`, então ninguém a executaria de novo. O
> registro que o formato produz é o
> [`divergencias.md`](../../../wte/re/divergencias.md), e é lá que as entradas
> moram agora.

1. **`ficha_warning` não é levantado pelo port** (achado 8). O aviso de tamanho
   do original pergunta antes de aplicar os dois remendos de arranque; o port
   os aplica **sem perguntar**, e é por isso que a gravação bate byte a byte.
   → **§10 do registro**, divergência deliberada, decisão *não reproduzir*.
2. **`ficha_enlaza` não tem chamador nenhum no port** (achado 8). Não é escolha
   de tela: a rota que o alcança é o `MainForm.mostrar_jugadorClick` para
   jogador de clube de Master League, que a
   [WTE-TASK-30](/docs/tasks/concluidos/30-handlers-auxiliares.md) deixou escrito por
   medir. **Rota não portada**, não divergência escolhida — o vocabulário
   importa aqui. → **não vira entrada**: está na seção *"O que NÃO entra
   aqui"* do registro, com o dono nomeado.
3. **`TStaticText` desabilitado pinta fundo próprio no GTK2** (achado 11). Um
   dos 37: `help_team` sai `#76B6FF` (a cor do formulário) no oráculo e
   `#DCDAD5` (o cinza do tema) no port. `base_team`, também `Enabled = False`
   no DFM, **bate** — porque o app o reabilita em runtime. O que diverge é a
   pintura do estado desabilitado, que nenhuma propriedade do DFM controla: é a
   mesma família da divergência 2 (os cinco glifos que não acinzentam).
   → **§11 do registro**, decisão *não reproduzir*.

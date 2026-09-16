---
id: LOOKS-TASK-14
title: "`assembly.py` — campo de LOOKS → peça + paleta"
type: engenharia-reversa
category: núcleo
phase: 4
depends_on: ["LOOKS-TASK-12", "LOOKS-TASK-13"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §6"
status: pendente
---

# LOOKS-TASK-14: A tabela de montagem

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §6,
  incógnita (c).
- **É o coração do projeto e a fase mais cara.** O que liga `HAIR = B3` à peça
  e à paleta certas.
- **Não pode vir antes da Fase 2.** Tabela de índice escrita contra peça não
  identificada produz mapeamento plausível e errado — é a armadilha das oito
  listas de nome de time do PES2 (§6.1 do
  [PLAN-PES2-PSX.md](/docs/PLAN-PES2-PSX.md)), onde casar por índice gravava no
  time errado e a tela parecia certa.

---

- **Quatro linhas da tabela já estão medidas, e com o mecanismo junto.**
  Das tasks [`08`](/docs/tasks/looks/08-de-onde-vem-o-boneco.md) e
  [`09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md), por
  `python tools/looks/oracle.py --fields`:

  | campo | peça | o que ele muda na primitiva |
  |---|---|---|
  | `SKIN` | tronco (pescoço), antebraço, coxa, perna | o **CLUT**, `+0x40` por passo |
  | `HAIR` | cabeça (`MODEL.BIN` seção 24) | o **`v`** das quatro quinas, `+0x20` |
  | `H.COL` | cabeça | o **CLUT** |
  | `BOOTS` | pé | o **CLUT** |

  O padrão é o que importa para esta task: **a peça nunca é trocada — o que
  muda é a paleta ou a faixa do atlas.** Uma tabela de montagem que mapeie
  campo → *peça diferente* estaria descrevendo um jogo que não é este.

  **Isso vale dentro de um boneco, e a escolha do boneco vem antes.** Os dois
  não compartilham as peças de braço: medido em 2026-09-15
  ([`CORR-LOOKS-021`](/docs/tasks/looks/CORR-LOOKS-021.md)), braço e antebraço
  têm **malha diferente** entre as duas listas — 30/24 contra 40/34 e 80/78
  contra 88/86 — e só a perna e o pé são de fato a mesma malha. Quem monta
  escolhe **a lista primeiro** (A é o jogador de linha, B é o goleiro) e só
  depois aplica campo; carregar uma malha e trocar só paleta desenha o goleiro
  de manga curta.
- **E as peças têm nome medido**, com o mapa em `tools/looks/pieces.py`: tronco,
  braço, antebraço, coxa, perna, pé (espelhados em `z`) e a cabeça, que mora no
  outro arquivo.

---

- **A metade "paleta" da tabela já tem leitor e regra**, desde 2026-09-15
  ([`LOOKS-TASK-10`](/docs/tasks/looks/10-lista-de-cluts-do-dat2d.md)): o
  `tools/looks/texture.py` acha as 267 paletas do `DAT2D.BIN` e resolve um CLUT
  id pelo registro que o **cobre**, não pelo que lhe é igual. A distinção é da
  tabela de montagem: as chuteiras são (0, 484), a pele nua (0, 480), e a cabeça
  (16, 480) e (144, 480) — as três últimas **dentro da mesma paleta larga**, de
  modo que "campo → paleta" não é um par de offsets e sim `(x, y, largura)`.
- **E o campo que move a peça move a linha de VRAM inteira:** um passo de `SKIN`
  soma `0x40` ao id, que é uma linha, e leva pele, cabeça e tudo que amostra
  daquela paleta junto. Uma linha de tabela que mande `SKIN` trocar só a pele
  estaria descrevendo outro jogo.

---

- **Mais duas linhas da tabela medidas, e agora com a imagem junto.** Em
  2026-09-15 ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)):

  | campo | peça | primitivas | o que muda | imagem |
  |---|---|---|---|---|
  | `HAIR` | cabeça | 1 e 14 | `v` `+0x20` | `DAT2D.BIN` **3.568** |
  | `FACE` | cabeça | 8 e 13 | `v` `+0x10` | `DAT2D.BIN` **3.568** |

- **Uma linha da tabela precisa de três coisas, não duas:** peça, paleta **e
  imagem** — e a imagem não se deduz da página, porque uma página de 4 bits
  cobre 256 texels e as imagens deste arquivo têm 128. `u` acima de 127 amostra
  a imagem seguinte, e foi exatamente isso que decidiu a §1.8. O
  `tools/looks/atlas.py` resolve `(página, u, v)` para o registro certo; usá-lo
  é mais barato do que repetir a conta.
- **O uniforme não está no arquivo comum.** As 1.039 primitivas de kit amostram
  páginas e paletas que moram em **105 `TEX_*.BIN`**, um por time. Uma tabela de
  montagem que procure o uniforme no `DAT2D.BIN` não acha nada e não diz por
  quê.
- **E é aqui que a escolha da paleta do uniforme fica ambígua.** Cada
  `TEX_*.BIN` tem **cinco** paletas de 256 — duas em (0, 486), duas em (0, 488)
  e uma em (256, 480) que a geometria não nomeia. **"Casa e fora" é hipótese**,
  não medição: ninguém trocou o uniforme do time na tela para ver qual das duas
  de uma id se move ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)).
  O uniforme é o único campo com **duas candidatas por id**, e é desta task
  decidir por medição — escolher "a primeira" desenha perfeitamente, nas cores
  erradas.

---

- **Paleta larga não é uma linha da tabela: é dezesseis.** Medido em
  2026-09-15 pela
  [`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md): um registro
  de 256 entradas é uma fileira de **dezesseis CLUTs de 4 bits**, e os três
  campos de cor são **duas coordenadas** dessa grade — `SKIN` anda a linha
  (a raça, quatro), `H.COL` e `H.F.COL.` andam a coluna (oito cabelos a partir
  da 1, sete barbas a partir da 9). Os três **alcançam** as dezesseis colunas:
  1 + 8 + 7 = 16.

  **E alcance não é identidade — é aqui que esta task erra em silêncio.** A
  coluna 1 não é "cabelo 0": é onde repousam **948 primitivas de 50 seções do
  `MODEL.BIN`**, das quais só **16** são a cabeça, e as colunas 2..8 e 10..15
  não têm primitiva nenhuma no disco
  ([`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md)). Escrever
  `coluna 1 → cor de cabelo 0` na tabela dá a 932 primitivas uma cor de cabelo
  que elas não têm, e o boneco **desenha perfeitamente**. Quem preenche uma
  linha desta tabela a partir de campo de tela tem de dizer **a peça também**,
  nunca só a coordenada.

  | campo | peça | primitivas | coordenada | alcance |
  |---|---|---|---|---|
  | `SKIN` | toda pele nua, mais a cabeça | 196 e 326 bytes, por slot | linha | 4 |
  | `H.COL` | cabeça | 0, 1, 4, 9, 14, 16, 17 | coluna | 8 (1..8) |
  | `H.F.COL.` | cabeça | 8 e 13 | coluna | 7 (9..15) |

- **`H.COL` move sete primitivas, não as duas do cabelo.** As duas que o `HAIR`
  reformata estão entre elas; as outras cinco são partes da cabeça pintadas com
  a cor do cabelo. Uma linha de montagem que ligue `H.COL` só ao cabelo deixa
  cinco primitivas com a cor errada.
- **O desempate "registro mais estreito ganha" é o que o console faz**, e agora
  está medido contra a VRAM: as 21 linhas de CLUT do `DAT2D.BIN` batem entrada
  por entrada quando resolvidas pelo `texture.covering`, e a linha 484 — onde
  seis paletas de 16 entradas ficam por cima de uma de 256 — dá **71** entradas
  diferentes se resolvida pelo registro largo. A tabela de montagem pode usar o
  `covering` sem ressalva.

---

- **São dez campos guardados, não doze**, e o `tools/looks/looks.py` os entrega
  decodificados desde 2026-09-15
  ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)).
  `DEFAUL` e `NAT` não guardam nada: são as duas metades do *default look por
  nacionalidade*, cuja tabela é o `data/defaultlook.txt` deste repositório — 95
  nações × as **mesmas cinco colunas** da tupla do corpus. Uma tabela de
  montagem com doze linhas tem duas que não têm de onde vir.
- **E o rótulo da tela não é o nome do campo:** `FACE` é o `beard_style`,
  `H.F.COL.` é o `beard_colour`, `HEIG` é `height` e `BODY` é `build`. O
  `looks.BY_ROW` e o `looks.BY_NAME` dão os dois sentidos.
- **Três campos têm menos rótulo do que valor** — barba e cor de barba guardam
  oito e têm sete nomes, o pé guarda quatro e tem três. Nos 1.449 registros do
  disco nenhum passa do último rótulo, mas a montagem tem de **suportar** o
  índice sem nome em vez de recusar: `looks.label()` devolve `?`.

---

## Objetivo

`tools/looks/assembly.py`: dada uma tupla de LOOKS, dizer quais peças desenhar
e com que paleta.

---

## Critério de conclusão

- [x] **RESOLVIDO COM RESÍDUO NOMEADO, 2026-09-16 (terceira passagem).** O
      `HAIR` **não edita uma seção: escolhe uma.** Medido pelo
      `oracle.py --patched HAIR`, que lê o arquivo inteiro depois de cada tecla:
      a **letra** do rótulo é uma seção **par** do primeiro bloco (A→24, B→26,
      C→30, D→48, F→52, G→28, I→34, J→36, K→32, L→46, O→44, P→50) e o **dígito**
      é a faixa de dezesseis linhas da folha 3.568 escrita nos quads daquela
      seção. A seção 24 é a família **A sozinha**, que é de onde vinham os
      "três estados". A tabela é o `assembly.HAIR_MAP`.
      **O resíduo, que não se preenche por dedução:** três valores — `H1`, `M1`
      e `N1` — não escreveram nada, e três seções pares — 38, 40 e 42 — nunca
      foram nomeadas; o `head_of` **recusa** esses três. O `E1` reescreveu a
      seção do `D`. E **quais primitivas das outras doze cabeças recebem a
      faixa** não está medido.
- [x] As **4 peles** resolvidas, pelo mecanismo que a LOOKS-TASK-12 decidiu:
      `SKIN` anda a **linha** do CLUT id, `+0x40` por passo, e alcança as quatro
      — andado de ponta a ponta, não deduzido.
- [x] `FACE`, `H.F.COL.`, `BOOTS` e `BODY`, cada um com veredito:
      **`BOOTS` resolvido** (8 colunas do registro de chuteira, 42 das 56
      primitivas de cada pé); **`H.F.COL.` resolvido** (7 colunas, 9 a 15);
      **`FACE` alcança 5** das sete que os rótulos nomeiam e das oito que os bits
      guardam — buraco nomeado; **`BODY` não toca geometria nenhuma**, medido
      pela LOOKS-TASK-08, e está no `assembly.UNTOUCHED` com a razão, junto com
      `HEIG`, `AGE`, `NAT`, `DEFAUL` e `FOOT`.
- [x] A tabela é **derivada de medição**, e cada linha diz de onde veio: o
      `assembly.EFFECTS` guarda, por campo, o que ele anda, o passo, **quantos
      valores a tela alcança** e quais primitivas ele move — tudo saído do
      `oracle.py --assembly`, que anda o campo do fundo ao topo e lê a seção
      depois de cada tecla.
- [x] Controle negativo: `assembly-table-off-by-one` desloca a tabela em um
      índice e fica vermelho — o fundo de cada campo é o estado que o disco já
      guarda, então tabela deslocada pede edição onde o jogo não pede. Mais um:
      `assembly-effects-do-not-compose`.
- [ ] **NÃO FEITO, e agora está destravado.** Cross-check contra o corpus: ao
      menos três das 50 tuplas do Superpack produzem a mesma escolha de peças
      que o JPG mostra. O que faltava era o mapa, e o mapa existe desde
      2026-09-16: `assembly --tuple A-I3-A-A-A` já responde com a cabeça 34 e
      `A-B4-...` com a 26. O que falta é **comparar com o JPG**, e comparar
      escolha de peças com uma imagem exige o desenho — que nasce na
      [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md). Este
      critério é o que mantém esta task pendente.

---

## Log de Execução

**Executado em:** 2026-09-15 e 2026-09-16 (três passagens) — **PARCIAL**.
Cinco dos seis critérios fechados; **a âncora do cabelo fechou na terceira
passagem**, com resíduo nomeado, e só o cross-check contra o corpus ficou — ele
depende de desenhar, que é a LOOKS-TASK-15. A task **continua pendente**.

### O que se aprendeu, e é mais forte do que a tabela

**A geometria nunca muda.** Nenhum vértice se mexeu em nenhum dos seis campos
andados, e campo nenhum troca uma seção por outra. O que um campo de LOOKS
reescreve é o **CLUT id** de algumas primitivas ou o **`v`** de algumas
primitivas, e nada mais. Então a lista de desenho é **as seções do disco com
uma edição pequena e medida aplicada** — não uma escolha entre malhas. Isso
simplifica a Fase 5 inteira.

**E o fundo de cada campo é o estado que o disco guarda.** Descendo a linha até
o fim (32 `Left` no `HAIR`, 8 nos outros), o que se lê na RAM é byte a byte o
que o arquivo tem. É a âncora que faz a tabela ser absoluta em vez de relativa,
e é a asserção que o controle de deslocamento derruba.

### A tabela, medida

```text
python tools/looks/oracle.py --assembly HAIR FACE BOOTS SKIN H.COL H.F.COL.
  BOOTS     8 press(es): clut 0x7900..0x7907   42 de 56 primitivas de cada pé
  SKIN      4 press(es): linha 480..483        8 primitivas da cabeça
  H.COL     8 press(es): coluna 1..8           7 primitivas da cabeça
  H.F.COL.  7 press(es): coluna 9..15          2 primitivas (a barba)
  FACE      5 de 8:      v 0,16,32,48,64       2 primitivas (a barba)
  HAIR      3 de 32:     v 1, 33, 17           2 primitivas (o cabelo)
```

**Todos os seis travam nas pontas; nenhum dá a volta.** A LOOKS-TASK-12 tinha
medido isso em três campos; agora são seis.

### Os dois buracos, nomeados

**`HAIR` não tem mapa.** O campo guarda 32 valores e a tela, andada do fundo ao
topo, alcança **três** estados na seção 24 — faixas 0, 2 e 1, nessa ordem — e
as trinta teclas seguintes não mudam **nada**. Malha nenhuma se mexe, então os
32 estilos não são 32 malhas; e a imagem 3.568 tem 128 linhas, que dão oito
faixas de 16, que ainda não são 32. Escrever `faixa = estilo` produziria um mapa
que desenha perfeitamente e está errado — que é exatamente o que esta task
existe para não fazer.

**`FACE` alcança 5**, das sete que os rótulos de terceiro nomeiam e das oito que
os três bits guardam. É um terceiro número na mesma família do `beard_colour`
da LOOKS-TASK-13 (oito bits, sete nomes) — mas ali a tela alcançava os sete, e
aqui não alcança.

### Três defeitos de método que a corrida expôs

1. **O jogo reescreve o bloco de primitivas ao longo de mais de um quadro.** Na
   primeira corrida do `BOOTS`, uma leitura logo depois da tecla trouxe 34 das
   42 primitivas no CLUT novo e 8 ainda no velho — um estado que nunca existiu.
   Pior: uma amostra tirada **antes** de a escrita começar é igual à anterior, e
   a varredura lia isso como fim do alcance. Foi o que transformou 32 valores de
   `HAIR` em três e 8 de `BOOTS` em nove. Conserto: o `steady()` lê até duas
   leituras seguidas concordarem, e **recusa** se nunca concordarem.
2. **Parar na repetição exige uma observação que mude a cada passo**, e a
   seção 24 não é isso para o `HAIR`. O comando passou a **contar teclas**
   contra o domínio que a LOOKS-TASK-13 mediu, em vez de esperar a repetição.
3. **Dois campos podem ser donos da mesma primitiva.** Seis das primitivas da
   cabeça são movidas por `SKIN` e por `H.COL`, e a primeira versão do
   `draw_list` aplicava cada campo ao valor **do disco** em vez de ao valor
   corrente — de modo que o segundo desfazia o primeiro e `SKIN` de A a D saía
   movendo **zero** primitivas. Verde no `self_check`, vazio contra o disco. O
   `combine()` existe por isso, e tem controle próprio.

### Segunda passagem, 2026-09-16: onde moram os 32

A pendência de cima começava pela pista errada, e a corrida mostrou isso em
dois minutos: **as duas faixas de buffer se reescrevem a cada quadro** — o
boneco anima —, então o `oracle.py --where`, que anda o campo lendo as duas
faixas, morre no `steady()` com *"never settled in 8 x 20 frame(s)"*. Está
certo que morra: display list de cena animada não é observação estável. O
comando fica, porque a recusa é a medição.

A pista boa estava no disco, de graça. Varrendo as 106 seções do `MODEL.BIN`
atrás de quem amostra a folha de cabelo:

```text
python tools/looks/assembly.py --check-image
  MODEL.BIN sections 24..55:  32 distinct body(ies), 32 of them sampling the hair sheet
  MODEL.BIN sections 74..105: 32 distinct body(ies), 16 of them sampling the hair sheet
```

**Dois blocos de 32 cabeças.** Trinta e dois é o domínio do `hair_style`; dois
blocos são as duas figuras. Cada uma das 32 do primeiro bloco tem janela própria
na folha — da 24 (`v` 1..14 no par do cabelo) à 52 (`v` 8..126) — e os pares
vizinhos compartilham **o mesmo array de vértices** com UV diferente: as 24 e 25
têm vértices idênticos, corpo diferente.

**E a metade que falta continua faltando, agora com um "não" medido no lugar de
uma dúvida:** as três faixas que a tela alcança **não batem com a janela de
seção nenhuma** das 32, e **nenhum vértice se mexe em nenhum dos 33 estados** —
o que descarta a leitura óbvia, a de que a linha troca o corpo da seção. Onde o
valor do campo vira uma daquelas 32 seções segue sem medição.

### Terceira passagem, 2026-09-16: a âncora

**A pergunta estava mal posta, e a primeira medição da passagem mostrou isso.**
A pendência dizia "por que a tela alcança três faixas". O `oracle.py --hair`
anda a linha inteira capturando a **célula de valor da linha** junto com a
seção, e o que ele mede é:

```text
python tools/looks/oracle.py --hair
  HAIR on slot 2: the value cell moved on 32 of 32 press(es) of Right,
  and /BIN/MODEL.BIN section 24 reached 3 distinct state(s) in 33 value(s)
```

A tela **anda os 32**. O que assentava em três era a seção que a varredura
olhava. Duas corridas, o mesmo número.

**O escritor, por breakpoint — o primeiro deste ciclo.** Um watchpoint de
escrita no `v` do quad de cabelo da seção 24 (`0x80172351`, derivado do disco
mais o `layout.BASE`) para em `0x80011594`, e a rotina é:

```text
0x80011580  andi  v0, a2, 0x00ff      a banda, como o chamador a passou
0x80011584  sll   v0, v0, 4           dezesseis linhas por banda
0x80011588  addiu v1, v0, 15
0x8001158C  addiu v0, v0, 1
0x80011590  sb v1, 0x1(a0)            o `v` das quatro quinas do quad
0x80011594  sb v0, 0x5(a0)
0x80011598  sb v1, 0x9(a0)
0x8001159C  sb v0, 0xd(a0)
      a0 = 0x80172350 -> /BIN/MODEL.BIN section 24, primitive 1
      chamado de ra = 0x80012694, que carrega a banda de `0x80(sp)`
```

As dezesseis linhas por faixa deixam de ser observação e viram aritmética do
jogo. **E o byte só é escrito em alguns valores**: 90 s de execução livre no
valor seguinte sem um único toque.

**A âncora veio de ler o arquivo inteiro, não um byte.** O `oracle.py --patched`
anda a linha e compara os 64.800 bytes do `MODEL.BIN` vivo contra o disco depois
de cada tecla:

```text
python tools/looks/oracle.py --patched HAIR
   0  changed: section 24 (4 byte(s), band(s) [0]), section 32 (16 byte(s), ...)
   1  changed: section 24 (8 byte(s), band(s) [2])
   2  changed: section 24 (8 byte(s), band(s) [1])
   3  changed: section 26 (8 byte(s), band(s) [0, 1])
   ...
  25  changed: section 46 (12 byte(s), band(s) [5])
  30  changed: section 44 (4 byte(s), band(s) [0, 1])
  31  changed: section 50 (4 byte(s), band(s) [0, 1])
```

**A letra do rótulo é a seção; o dígito é a faixa.** A→24, B→26, C→30, D→48,
F→52, G→28, I→34, J→36, K→32, L→46, O→44, P→50 — treze seções, todas **pares**,
todas do primeiro bloco. A seção 24 é a família **A sozinha**, três valores de
32: é daí que vinham os "três estados". O mapa é o `assembly.HAIR_MAP`, e o
`assembly.head_of` é quem responde por uma tupla.

**E o bloco 24..55 é dezesseis PARES.** Medido no disco pelo
`assembly.head_pairs`: 91 primitivas diferem dentro de um par, e o que as separa
é a barba — 32 saem da coluna 1 do CLUT para a 9, 41 já estavam na 9, nenhuma
volta. Ler "32 seções, e o `hair_style` guarda 32" como identidade teria sido a
coincidência mais cara desta task.

### O que ficou pendente

- **O resíduo do mapa, que não se preenche por dedução.** Três valores — `H1`,
  `M1` e `N1` — não escreveram nada, e três seções pares — 38, 40 e 42 — nunca
  foram nomeadas; o par de treses é sugestivo e não é medição. O `head_of`
  **recusa** esses três, com controle negativo (`assembly-hair-map-defaults`).
  O `E1` reescreveu a seção do `D`. O caminho que fecha isso é o watchpoint em
  cada uma das três seções candidatas, andando a linha até ele disparar.
- **Quais primitivas das outras doze cabeças recebem a faixa.** Só o par da
  seção 24 tem índice nomeado (LOOKS-TASK-08); nas outras, a contagem de bytes
  medida não bate com o conjunto óbvio (a seção 30 tem doze primitivas na folha
  de cabelo com a cor do cabelo e o jogo reescreve **duas**). Por isso o
  `draw_list` aplica a faixa só na 24.
- **O cross-check contra o corpus**, que agora depende de **desenhar**: a
  escolha de peças já sai por comando, mas compará-la com um JPG exige o
  visualizador da [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md).

### Gates medidos

```text
python tools/looks/selftest.py --quiet
  modules:  0 failure(s)
  rules:    0 failure(s)      ..... rule 1 swept 14 file(s), 8916 line(s)
  controls: 0 failure(s)      ..... 29 of 29 controls red
  looks_selftest: 0 failure(s)
```

```text
python tools/looks/assembly.py --check        ->  assembly.py: 0 failure(s)
python tools/looks/assembly.py --check-image  ->  assembly --check-image: ok
python tools/looks/looks.py --check-image     ->  looks --check-image: ok
python tools/looks/skin.py --check-image      ->  skin --check-image: ok
python tools/looks/texture.py --check-image   ->  texture --check-image: ok
python tools/looks/atlas.py --check-image     ->  atlas --check-image: ok
python tools/looks/pieces.py --check-image    ->  pieces --check-image: ok
python tools/looks/modelfile.py --check-image ->  ok
python tools/looks/oracle.py --check          ->  oracle.py: 0 failure(s)
python tools/check_tasks.py                   ->  123 task(s), ok
```

E a lista de desenho sai por comando:

```text
python tools/looks/assembly.py --tuple A-A1-A-A-A
A-A1-A-A-A, figure 0: 593 primitive(s)
    /BIN/EDT_MOD.BIN   section 3   image 8      palette (0, 480, 16)   band +0  x78
    /BIN/EDT_MOD.BIN   section 9   image 8      palette (0, 484, 16)   band +0  x56
    /BIN/MODEL.BIN     section 24  image 3568   palette (144, 480, 16) band +0  x2
    ...
```

Toda leitura de disco saiu do **japonês**; o emulador bootou o `.cue` **inglês**
e a janela dele foi para −32000 na abertura. `roms/` só foi lida.

### Arquivos criados/modificados

- `tools/looks/assembly.py` — **novo**. `Effect` e a tabela `EFFECTS`,
  `UNTOUCHED` com os seis buracos nomeados, `edits()`, `apply_to()`,
  `combine()`, `sections_of()`, `draw_list()`, o `self_check()` com os casos
  vermelhos, e `--check`, `--check-image`, `--tuple`
- `tools/looks/oracle.py` — o comando `--assembly`: `section_address()` (agora
  o corpo inteiro da seção, vértices incluídos), `walk()` generalizado,
  `steady()`, `check_assembly()` e `_say_primitives()`; e o `--where`, que anda
  um campo lendo as duas faixas de buffer — e **recusa**, porque elas não
  assentam
- `tools/looks/layout.py` — `ATLAS_BAND`, `BOOT_SECTIONS` e `HEAD_RUNS` (esta
  com a âncora medida no lugar do buraco, na terceira passagem)
- `tools/looks/controls.py` — `assembly-table-off-by-one` e
  `assembly-effects-do-not-compose`
- `tools/looks/selftest.py` — `assembly` no `MODULES`
- `docs/PLAN-LOOKS-PY.md` — §6(c) com o que está medido e o que ficou aberto,
  e §3.2 com o que o `assembly.py` entrega
- `docs/prompts/perfil-looks.md` — duas armadilhas novas (o bloco se escreve em
  mais de um quadro; alcance de tela não é domínio de campo) e o gate novo
- `docs/tasks/looks/14-tabela-de-montagem.md` — os critérios e este Log

Na terceira passagem, 2026-09-16:

- `tools/looks/assembly.py` — o `HAIR_MAP` e o `head_of()`, o `HEAD_BAND`, o
  `CHOOSES` (a linha que escolhe seção em vez de editar uma), o `head_pairs()`
  com o `HEAD_PAIR_COLUMNS`, o `sections_of()` que passa a receber a tupla e a
  asserção nova do `--check-image`
- `tools/looks/oracle.py` — os comandos `--hair` e `--patched`, o
  `catch_write()` com o controle de execução livre, o `texcoord_address()`, o
  `model_maps()`/`pointers_into_models()`, o `band_of()` e o `_say_writer()`
- `tools/looks/section.py` — `TEXCOORD_STRIDE` e `V_IN_TEXCOORD`, para o
  watchpoint ter um endereço que a varredura da regra 1 enxerga
- `tools/looks/controls.py` — `assembly-hair-map-defaults` e
  `assembly-hair-map-is-one-section` (29 → 31)
- `tools/looks/layout.py` — o `HEAD_RUNS` com a âncora medida no lugar do buraco
- `docs/PLAN-LOOKS-PY.md` — §6(c) com a âncora, a rotina do jogo e o resíduo
- `docs/prompts/perfil-looks.md` — a armadilha 19 **corrigida** (a tela andava
  os 32; quem mostrava três era a seção), a 20 nova sobre byte escrito com o
  mesmo valor, e as duas linhas novas da tabela de gates

### Problemas encontrados

Os três de método acima, e mais um de arquivo: a
[`CORR-LOOKS-026`](/docs/tasks/looks/CORR-LOOKS-026.md) tinha acabado de
acrescentar `SKIN_COLOUR_PRIMITIVES` ao `layout.py`, e esta execução escreveu
**um segundo** com o mesmo nome e outro conteúdo — treze primitivas em vez de
oito. Python fica com o último e não reclama. Removido; vale o oito da CORR, que
saiu do `--fields` com o filtro de churn. As treze do passeio incluem primitivas
que só diferem em estados intermediários, e **a diferença entre as duas medições
não está resolvida**.

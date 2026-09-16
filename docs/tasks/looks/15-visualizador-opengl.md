---
id: LOOKS-TASK-15
title: "`ui/viewer.py` e `ui/app.py` — `QOpenGLWidget`, câmera orbital e uma tupla na tela"
type: implementação
category: ui
phase: 5
depends_on: ["LOOKS-TASK-14"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §3.2"
status: concluído
---

# LOOKS-TASK-15: O visualizador

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §3.2, §3.3
  (regra 3) e §4.3.
- **`QOpenGLWidget`, não Qt3D nem rasterizador em Python.** O Qt3D é módulo
  grande e meio abandonado no Qt6 (§4b do
  [PLAN-STADIUMS.md](/docs/PLAN-STADIUMS.md)); rasterizar em Python puro é
  inviável sem `numpy`, que **não está instalado** e cuja instalação é decisão
  do dono da máquina.
- A UI **não conhece endereço** e o núcleo **não conhece Qt**.

---

- **Existe um gabarito da geometria já desenhada, e ele é alcançável.** Medido
  em 2026-09-15 pela
  [`LOOKS-TASK-09`](/docs/tasks/looks/09-nomear-as-onze-pecas.md) com
  `python tools/looks/oracle.py --buffers`: as duas faixas de RAM em que todo
  campo de LOOKS escreve são **listas de display do PSX**, dobradas —
  `0x80153000` e `0x80162000`, a `0xF000` uma da outra, com 365 e 440 nós, a
  maioria esmagadora deles **quad texturizado**. Cada nó é `[link][pacote]`, e o
  pacote traz os `(u, v)`, o CLUT e a página de textura **já resolvidos**, mais
  as coordenadas de tela. Se o render sair diferente do jogo, é ali que se
  compara vértice a vértice, em vez de só comparar quadros.

---

- **O atlas já é exportável, colorido, por comando.** Desde 2026-09-15
  ([`LOOKS-TASK-11`](/docs/tasks/looks/11-qual-imagem-e-o-cabelo.md)):
  `python tools/looks/atlas.py --export <dir>` grava as 23 imagens do
  `DAT2D.BIN` como PNG de paleta, cada uma na profundidade e com a paleta que a
  própria geometria nomeia. O `atlas.texel()` e o `atlas.image_at()` são o que o
  renderizador precisa para ir de `(página, u, v)` ao texel certo.
- **E o uniforme vem de outro arquivo, por time.** As páginas e as paletas de
  kit estão em **105 `TEX_*.BIN`**, com **cinco** paletas de 256 entradas em
  cada — duas em (0, 486), duas em (0, 488) e uma em (256, 480) que a geometria
  não nomeia ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)). Um
  visualizador que carregue só o `DAT2D.BIN` desenha o boneco pelado — não por
  bug, por arquivo faltando.

  **Esta linha dizia que a escolha da paleta de kit "chega aqui decidida" pela
  LOOKS-TASK-14, e não chegou** — corrigido em 2026-09-16, ao executar esta
  task: a 14 mediu a cabeça e não o uniforme, e nenhum `TEX_*.BIN` tem digest
  no `layout.py` para ser lido pela guarda. Medido aqui: **237 das 593**
  primitivas da figura amostram páginas que não estão no `DAT2D.BIN`, e saem em
  cinza de espaço reservado, contadas em `Scene.notes`. Qual contêiner e qual
  das cinco paletas o jogo usa é pergunta para o emulador, e a linha está
  escrita na
  [`LOOKS-TASK-17`](/docs/tasks/looks/17-confronto-com-o-emulador.md).
- **Duas paletas que a geometria nomeia não estão em contêiner nenhum do
  disco:** (0, 485) e (336, 510). Se o render sair com uma peça cinza, é uma
  delas, e não um erro de leitura.

---

- **A cabeça vem do `assembly.head_of()`, não da seção 24.** Medido em
  2026-09-16 pela
  [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md): a linha `HAIR`
  **escolhe** uma das treze seções pares do primeiro bloco de cabeças (a letra
  do rótulo) e uma faixa de dezesseis linhas da folha 3.568 (o dígito).
  Desenhar sempre a 24 desenha sempre a família `A`, e desenha perfeitamente.
- **Três estilos — `H1`, `M1` e `N1` — o `head_of` RECUSA**, porque o mapa não
  os alcançou. Quem desenhar tem de tratar a recusa: uma tupla do corpus com um
  deles não é erro do visualizador.
- **A faixa só é aplicada em quatro cabeças de treze** (`layout.HAIR_QUADS`);
  nas outras nove a janela é a do disco. Se uma tupla dessas sair com o cabelo
  "errado mas plausível", é isto, e é medição que falta, não bug de render.
- **E o mapa é do jogador de linha.** O segundo bloco de cabeças (74..105) é o
  do goleiro e ninguém andou a linha nele; o `sections_of()` deixa a cabeça do
  disco para a figura 1 de propósito.

---

- **O que o renderizador tem de implementar está medido, e é uma frase.**
  [`LOOKS-TASK-12`](/docs/tasks/looks/12-pele-paleta-ou-vertice.md),
  2026-09-15: **textura com CLUT e nenhuma cor de vértice** — o índice sai do
  texel da imagem que a página e o `u` resolvem (`atlas.image_at`), e a cor sai
  da **janela de dezesseis entradas** que o CLUT id da primitiva nomeia dentro
  do registro de 256 (`texture.palette_for`, `skin.grid`), nunca do registro
  inteiro. Uma primitiva deste formato não tem campo de cor nenhum.
- **E o que ele NÃO precisa fazer:** as paletas na VRAM são as do arquivo e
  ficam paradas. Medido: as 21 linhas de CLUT do `DAT2D.BIN` batem com a VRAM
  entrada por entrada, e um passo de `H.COL` reescreve **zero** das 256
  entradas. Trocar de cor é trocar o **id**, então não há upload de paleta para
  emular — carregue as 267 uma vez e indexe.

---

- **O `--looks TUPLA` já tem parser, e ele recusa alto.** Desde 2026-09-15
  ([`LOOKS-TASK-13`](/docs/tasks/looks/13-campos-e-dominios-de-looks.md)):
  `looks.parse_tuple("A-I3-A-F-A")` devolve os cinco campos, `looks.format_tuple`
  faz a volta, e um rótulo que o campo não tem sai como `BadLooks` com a lista
  dos válidos — não como índice zero em silêncio.
- **A UI mostra rótulo, e rótulo pode faltar.** Três campos guardam mais valores
  do que alguém nomeou; `looks.label()` devolve `?` nesses, e a janela tem de
  saber desenhar isso.

---

## Objetivo

Uma janela que desenha o boneco de uma tupla de LOOKS, e que se deixa dirigir
de fora.

---

## Critério de conclusão

- [x] `ui/viewer.py` desenha as peças com `QOpenGLWidget`, câmera orbital
      (yaw, pitch e distância, por mouse ou por chamada) e os modos sólido e
      wireframe. Sem luz e sem descarte de face: as duas seriam opinião sobre
      coisa não medida — a primitiva não tem cor de vértice, e para que lado um
      quad enrola é a diagonal que o `scene.TRIANGLES` deixa em aberto.
- [x] A cor chega pelo caminho da LOOKS-TASK-12 e por nenhum outro: o índice sai
      do texel, e a cor sai da **janela** de dezesseis entradas que o CLUT id
      nomeia. O `texture.window_for` nasceu aqui porque o `palette_for` lia do
      começo do registro — janela zero, dezesseis cores de outro, desenhando
      perfeitamente (controle `texture-window-at-record-start`).
- [x] **Desenha a tupla, e a do enunciado é uma RECUSA medida.** O
      `A-I3-A-F-A` deste critério é de antes da LOOKS-TASK-14: o `assembly`
      mediu a tela da barba chegando a cinco valores e recusa o `F`, então a
      janela imprime a recusa e sai **2**, em vez de desenhar um `E` calado. O
      que se desenhou e se olhou foi `A-I3-A-E-A`, mais quatro tuplas — a
      recusa e o desenho estão os dois no Log.
- [x] `--smoke` abre a janela, pinta um quadro, imprime o que desenhou e sai
      com 0.
- [x] `--screenshot out.png` grava a imagem **fora da tela**: janela em −32000
      no Windows, `:98` no Linux (§4.3). Nenhuma janela apareceu para o usuário
      em corrida nenhuma desta task.
- [x] Varredura: o `selftest` passou a varrer `ui/` de verdade (a regra 3 não
      tinha o que varrer até hoje) — nenhum import proibido, e `PySide6` fora
      de `sys.modules` depois de importar o núcleo inteiro. A regra 1 alcança
      `ui/`: 17 arquivos, **11.831** linhas — medido na árvore que fecha a
      task, o commit `f2df3fc`
      ([`CORR-LOOKS-036`](/docs/tasks/looks/CORR-LOOKS-036.md)).

---

## Log de Execução

**Executado em:** 2026-09-16 — **CONCLUÍDA**.

### O que se aprendeu, e é o achado da task

**Nenhum dos dois arquivos de modelo diz onde uma peça fica.** Cada seção é
modelada em torno da própria origem — a cabeça de y -15 a 48, a chuteira de -15
a 18 —, então desenhar as doze nas coordenadas do arquivo empilha a figura num
ponto só, e cada peça isolada parece perfeita. Quem posiciona é o jogo, em tempo
de desenho, na display list que a LOOKS-TASK-09 mediu. O plano previa "pose
neutra" (§5.6); o disco não dá nem isso, e a §5.6 foi corrigida no lugar.

A v1 desenha então uma **prateleira**, e diz que é uma (`scene.shelf`): peças em
fila, cada uma inteira, nenhuma sobre a outra. Inventar articulação plausível
desenharia uma figura que parece certa e é de ninguém — a mesma recusa que o
`head_of` faz com os três estilos de cabelo não medidos.

### O que foi construído

- **`tools/looks/scene.py`** — o núcleo do render, sem Qt: a lista de desenho do
  `assembly` virando quatro pontos, quatro `(u, v)` normalizados e uma textura
  RGBA por `(imagem, profundidade, CLUT)`. `--check`, `--check-image`,
  `--tuple` e `--corpus`.
- **`tools/looks/ui/viewer.py`** — `QOpenGLWidget`, shader de textura sem luz,
  câmera orbital, sólido e wireframe.
- **`tools/looks/ui/app.py`** — `--looks`, `--figure`, `--piece head`,
  `--smoke`, `--screenshot`, `--compare`, `--wireframe`, `--no-shelf` e
  `--visible`. A janela nasce fora da tela.
- **`texture.window_for` e o `first` do `read_palette`** — a janela de dezesseis
  entradas dentro de um registro de 256, que faltava.

### As corridas, e o que elas mediram

```text
$ python tools/looks/selftest.py          # na arvore de f2df3fc
  ..... rule 1 swept 17 file(s), 11831 line(s)
  ..... 37 of 37 controls red
looks_selftest: 0 failure(s)

$ WE2002_LOOKS_IMAGE=<japonesa> python tools/looks/scene.py --check-image
  A-A1-A-A-A, figure 0: 593 primitive(s), 356 textured, 5 surface(s)
      sections 12, triangles 1186, notes {'no image': 237, 'no palette': 0,
      'off the record': 0, 'band unmeasured': 0}
      the head sits at y 17 and the boots at y -3, with UP = -1
      A-A1-A-A-A has 5 surface(s), A-A1-C-A-A has 6, 4 shared
      A-I3-A-A-A draws [('/BIN/MODEL.BIN', 34)] where A-A1-A-A-A draws [24]
scene --check-image: ok

$ WE2002_LOOKS_IMAGE=<japonesa> python tools/looks/scene.py --corpus <pasta>
      31 drawn, 19 refused
      13 x FACE=F is value 5        3 x FACE=G is value 6
       2 x hair style H1 wrote nothing to either model file ...
       1 x the name that is not a tuple

$ <venv>/python tools/looks/ui/app.py --looks A-A1-A-A-A --piece head \
      --screenshot work/looks-shots/t15-A-A1-A-A-A.png
  A-A1-A-A-A, figure 0: 18 primitive(s), 18 textured, 3 surface(s), 36 triangle(s)
  window up, off the desktop at -32000,-32000

$ <venv>/python tools/looks/ui/app.py --compare <A-A1-A-A-A> <B-A1-A-A-A>
  193050 of 409600 pixel(s) differ (47.13%)
$ ... --compare <A-A1-A-A-A> <A-A1-C-A-A>    70336 of 409600 (17.17%)
$ ... --compare <A-A1-A-A-A> <A-I3-A-A-A>   149776 of 409600 (36.57%)
```

**As imagens foram OLHADAS, não só contadas.** A cabeça `A-A1-A-A-A` desenha um
rosto; a `B-A1-A-A-A` é o mesmo rosto mais escuro; a `A-I3-A-A-A` é outra malha,
com outro cabelo. É o que o critério de "duas tuplas diferentes produzem imagens
diferentes" pede, e o percentual sozinho não prova — um render quebrado de dois
jeitos diferentes também dá 47%.

### Problemas encontrados

- **`setUniformValue` com um `int` chega como zero no shader**, sem erro nenhum:
  o primeiro render saiu com a figura inteira na cor de espaço reservado, o que
  parece textura que não carregou. É `setUniformValue1i`, e o mesmo vale para o
  sampler. Virou armadilha 25 do perfil.
- **O modelo olha para -z**, então a câmera em yaw 0 fotografa a nuca — um
  crânio preto, que também parece falha de textura. O default da janela passou a
  ser `FRONT = 180`.
- **`palette_for` lia do começo do registro.** Um id de 4 bits dentro de um
  registro de 256 nomeia uma das dezesseis janelas, e ler do começo devolve a
  janela zero: dezesseis cores de outro, que desenham perfeitamente. Consertado
  em `texture.py`, com controle negativo.
- **A tupla do enunciado desta task é recusada pela tabela** (`FACE=F`), e no
  corpus há dezesseis renders com `F` ou `G`. Não se mexeu na tabela: alcance de
  campo se mede andando a tela, e isso está encaminhado para a LOOKS-TASK-17.

### O que foi encaminhado, e para onde

- **LOOKS-TASK-16** — os três comandos que o gate dirige, os percentuais de
  referência, a recusa que sai 2 e as peças cinza que são esperadas.
- **LOOKS-TASK-17** — o deslocamento de cada peça (a pose), a diagonal do quad,
  o uniforme dos `TEX_*.BIN` e o alcance real da barba.
- **LOOKS-TASK-18** — 31 das 50 desenháveis hoje, e por quê.

### Arquivos criados/modificados

- `tools/looks/scene.py` — novo
- `tools/looks/ui/viewer.py` e `tools/looks/ui/app.py` — novos
- `tools/looks/texture.py` — `window_for`, o `first` do `read_palette`, o
  `_rgba` que os dois compartilham, `build_container` aceitando uma cor por
  entrada, e os casos novos do `self_check`
- `tools/looks/controls.py` — quatro controles novos (33 → 37)
- `tools/looks/selftest.py` — `scene` na lista de módulos
- `docs/PLAN-LOOKS-PY.md` — §3.2, §3.4 e a §5.6 corrigida no lugar
- `docs/prompts/perfil-looks.md` — as armadilhas 24 e 25, e seis linhas de gate
- `docs/tasks/looks/16-contratos-da-ui.md`,
  `docs/tasks/looks/17-confronto-com-o-emulador.md` e
  `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` — as pendências
  encaminhadas, escritas **nas tasks de destino**
- `docs/tasks/looks/progresso.md` — a linha da tabela e os itens da Fase 5

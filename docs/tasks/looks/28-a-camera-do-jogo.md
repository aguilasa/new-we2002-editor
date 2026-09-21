---
id: LOOKS-TASK-28
title: "A câmera do jogo — projeção medida, e a silhueta como testemunha de forma"
type: implementação
category: oráculo
phase: 9
depends_on: [LOOKS-TASK-27]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: 2026-09-18
review_commit: null
done_on: 2026-09-18
done_commit: b85b6c5
---

# LOOKS-TASK-28: A câmera do jogo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (m), §10.4 (3) e §6 (h).
- **Sem a câmera do jogo, comparar desenho mede a câmera.**
- **Esta task fecha a §6 (h).** Figura montada na pose do jogo e mesma
  projeção: a silhueta passa a ser comparável, e forma ganha testemunha.
- **A [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) deixou uma
  armadilha que alcança toda leitura de registrador numa parada:** o ponteiro
  de modelo que o jogo carrega quando a matriz é carregada nomeia a peça que
  ele **acabou de desenhar**, uma parada atrás (`oracle.DRAW_LAG`). Quem
  acrescentar uma captura por breakpoint confere o atraso com
  `oracle.py --pose-lag` em vez de supor que o registrador fala da peça da vez.
- **O controle já existe:** a captura do emulador se repete em zero pixel a
  partir do `load_state` (§5.3). O limiar sai do controle, escrito depois de
  medido e dito que foi.

---

## Objetivo

Medir a projeção e a câmera da tela `LOOKS SET`, aplicá-las no painel, e
comparar a silhueta do nosso quadro com a do emulador no mesmo quadro N.

---

## Critério de conclusão

- [x] `H`, o deslocamento de tela e a matriz de câmera lidos do GTE por
      breakpoint, com o comando que os lê — `oracle.py --camera`. **E o
      deslocamento de tela do GTE é ZERO**, que é achado: quem põe o boneco
      dentro do painel é o deslocamento de desenho da GPU.
- [x] O painel desenha com eles, no tamanho do painel do jogo — a janela recebe
      do núcleo a 4x4 do jogo (`scene.panel_camera`), construída no tamanho
      **nativo** do painel e conferida contra o `project()` ao pixel.
- [x] `confront.py --silhouette [SLOT]`: máscara nos dois quadros e a
      diferença impressa.
- [x] **Controles antes do teste:** o mesmo quadro contado duas vezes dá **0**
      pixel de diferença, e quadros diferentes dão 603 a 1.483 no slot 2 e 670 a
      1.452 no slot 1. Os limiares
      saem daí e estão escritos como medidos.
- [x] Três estilos de cabelo diferentes, dois slots: a silhueta concorda, e um
      estilo trocado de propósito discorda — **no close-up**, onde o estilo é
      grande: cada foto do jogo escolhe o próprio estilo entre os três, 6 de 6,
      por 1,36x a 4,10x contra o estilo errado mais próximo, que é o que o
      `--silhouette-styles` imprime por foto. No corpo inteiro o estilo não se
      separa, e está dito (quarta sessão). Desde a
      [`CORR-LOOKS-063`](/docs/tasks/looks/CORR-LOOKS-063.md) o gate pergunta
      isso como o `--silhouette` pergunta o seu: **controle antes** (o mesmo
      close-up duas vezes, 0 pixel e câmera idêntica nos dois slots), razão
      contra o estilo errado **mais próximo** impressa por foto e conferida
      (`CLOSEUP_MARGIN = 1.2`), e teto para o escore certo
      (`CLOSEUP_SHARE = 0.25`, medido 6% a 8% da tinta da faixa).
- [x] §6 (h) e §10.3 (m) com o veredito e a data — as duas **fechadas** em
      2026-09-18: a (h) pela pose no corpo inteiro e pelo cabelo no close-up.

---

## Log de Execução

**Executado em:** 2026-09-18, em cinco sessões — a primeira **parcial**, fechada
na quinta ("Quinta sessão", abaixo)

**O que ficou medido**

**A câmera da tela, do GTE, com três controles.** `oracle.py --camera` para na
carga da matriz por peça — dentro do desenho da própria figura, e não em
qualquer ponto do quadro — e lê os registradores de controle do GTE:

- **`H` = 1376 px**, a distância focal com que o `RTPS` projeta;
- **`OFX` = `OFY` = 0,00**, e isso é o achado do dia: o ponto principal do GTE
  é a origem, então **o painel não é posicionado pelo GTE**. Quem o posiciona é
  o deslocamento de desenho da GPU, e o critério que dizia "o deslocamento de
  tela lido do GTE" recebe, medido, a resposta *é zero*;
- a matriz da câmera `[3195, 0, 635, -27, 2488, 133, -635, -268, 3195]` com
  translação `[-480, 192, 4125]` — **a mesma nos dois slots**.

Os três controles, nesta ordem: o mesmo quadro capturado **duas vezes** dá
números idênticos; as **doze** cargas de uma passada carregam a mesma projeção,
que é o que autoriza falar de "a" projeção do painel; e o quadro contado 140
projeta com os mesmos três, o que diz que a projeção é montagem de tela e não
animação.

**E a projeção está certa na largura.** Projetada com esses números, a nossa
figura mede **50,5 px** de largura contra **50** da figura do jogo no painel —
1% de diferença, sobre uma medida que nenhuma constante nossa escolheu.

**A silhueta, com os dois controles verdes.** `confront.py --silhouette` tira a
máscara do painel do **quadro nativo** (512x240, do `dump_vram`), pelo fundo de
cada **linha** — o painel é um degradê de 339 cores, e um fundo único para a
caixa inteira não separa nada. Os controles fecham antes de qualquer
comparação: o mesmo quadro contado duas vezes dá **0** pixel de diferença sobre
2.532 de tinta, e o quadro contado 80 difere do 20 em **1.300**.

**O que NÃO fecha, e é o bloqueio**

**A ponte entre o quadro contado do emulador e o quadro do `ANIME.BIN` que a
foto mostra.** O `anime.frame_of_pair` já diz qual quadro do arquivo o par que
o jogo estava lendo pertence, e a captura da foto e a captura do par são
corridas separadas — a foto custa alguns `frame_step` a mais, e a animação anda
no meio. Varrendo o **ciclo inteiro** (17 quadros, com a volta):

```text
frame 20: o par nomeia o quadro 13; melhor casamento no 7, 1.156 px de 2.532
frame 80: o par nomeia o quadro  6; melhor casamento no 5,   411 px de 2.454
```

O mínimo do quadro 80 é nítido e cai **um quadro antes** do que o par nomeia —
o que uma tela que mostra o buffer anterior explicaria. O do quadro 20 é raso
(1.156 contra 1.173 do vizinho) e cai seis quadros fora. Dois deslocamentos
diferentes não são uma ponte, e o comando **reprova** em vez de escolher o que
convém. Enquanto isso não fechar, comparar silhueta em três estilos mediria a
diferença de pose, não a de malha — que é justamente a §6 (h).

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/oracle.py` — `gte_projection()`, `capture_camera()`,
  `write_camera()`, `check_camera()` e a rota `--camera`
- `tools/looks/scene.py` — `load_camera()`, `to_camera()`, `project()`,
  `silhouette()`, `projected_box()`, `mask_box()`, `masks_differ()`
- `tools/looks/anime.py` — `frame_of_pair()`, a ponte entre o par lido e o
  quadro do arquivo
- `tools/looks/confront.py` — `panel_mask()`, `playing_frame()`,
  `game_silhouette()`, `our_silhouette()`, `fit_centre()`,
  `check_silhouette()` e a rota `--silhouette`
- `docs/tasks/looks/27-o-boneco-montado.md` — a contagem de controles
  corrigida de 86 para 87 (ver os problemas)
- `docs/prompts/perfil-looks.md`, `docs/PLAN-LOOKS-PY.md`,
  `docs/tasks/looks/28-a-camera-do-jogo.md`

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 87 of 87 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --camera
    H 1376 px, principal point (0.00, 0.00), the same at all 12 load(s)
oracle --camera: 0 problem(s) over 2 slot(s)

$ python tools/looks/oracle.py --pose-lag
oracle --pose-lag: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette 2
    control: frame 20 captured twice, 2532 pixel(s) of ink, identical
    control: frame(s) [80] differ from it by [1300] pixel(s)
confront --silhouette: 1 problem(s) over 1 slot(s)   <- o bloqueio acima

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**Problemas encontrados**

1. **A ponte de quadro não fecha** — o bloqueio, descrito acima e escrito no
   critério.
2. **Número de gate transcrito de uma corrida anterior à última edição.** O Log
   da [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) dizia
   `86 of 86` controles; rodando a ferramenta **sobre o commit** dá **87**. A
   corrida de onde o número saiu foi feita antes de o último controle entrar.
   Corrigido lá, e é armadilha de perfil agora.
3. **Janela de varredura que o resultado encosta não é janela.** A primeira
   corrida procurou o casamento a dois quadros de distância e achou o melhor
   **na borda**, nas duas comparações e em direções opostas — o que não diz
   onde está o mínimo. Alargada para o ciclo inteiro, com a volta, os mínimos
   ficam no interior e a resposta passa a ser legível.
4. **Máscara por cor única não separa figura de painel.** O fundo do painel é
   um degradê; o fundo tomado por **linha** entrega a silhueta limpa, e a borda
   do painel precisa de três pixels de recuo ou a caixa da figura vira o painel
   inteiro.

---

### Segunda sessão — a silhueta fecha

**A ponte de quadro era um bug de recorte, não um mistério.** O segundo buffer
de quadro desta tela começa na linha **240** da VRAM, não na 256; lido com 256,
o conteúdo chega **dezesseis linhas deslocado** e a caixa de ajuda entra no
retângulo do painel — a máscara então conta o branco de `Visual` como figura,
2.618 pixels de tinta contra 2.376, e nenhum quadro da caminhada casa. Duas das
seis comparações estavam assim, e a assinatura é sempre a mesma: **tinta acima
do normal e varredura chata**.

**E a comparação tinha de ser livre de translação.** A primeira versão media
uma translação única e a mantinha fixa — o que soa mais rigoroso e é pior:
ajustada numa pose e aplicada à foto de outra, ela desloca a figura inteira e
**todo** candidato pontua mal (medido: o melhor casamento foi de 13% da tinta
para 72%). Alinhada por comparação, a medida passa a julgar **forma e
tamanho**, que é o que a §6 (h) pede; onde a figura cai dentro do painel é o
deslocamento de desenho da GPU, e isto não o mede.

**O resultado, nos dois slots e em três quadros contados cada:**

```text
slot 2   quadro 60  -> caminhada 0,  0 atrás, 399 de 2383 (17%)
         quadro 80  -> caminhada 6,  2 atrás, 300 de 2454 (12%)
         quadro 100 -> caminhada 14, 1 atrás, 198 de 2532 ( 8%)
slot 1   quadro 60  -> caminhada 0,  0 atrás, 426 de 2376 (18%)
         quadro 80  -> caminhada 7,  2 atrás, 331 de 2460 (13%)
         quadro 100 -> caminhada 16, 2 atrás, 179 de 2426 ( 7%)
```

Cada varredura tem **mínimo interior e nítido**, e o quadro que o par do
próprio jogo nomeia está sempre **0 a 2 quadros à frente** do que a foto
mostra — que é o buffer anterior, com um quadro da caminhada durando ~3,5
quadros do emulador. O atraso é um **limite**, não uma constante, e exigir uma
constante foi o que fez a primeira leitura parecer ausência de ponte.

**A §6 (h) fecha: a forma tem testemunha.** O controle é um estilo de cabelo
que o state não veste — `A-I3` pontua **696 a 834** onde o certo pontua 179 a
426. E o que dá direito de chamar isso de testemunha de **forma** é o par que
não mexe: trocar a **cor de pele** (`B-A1` contra `A-A1`) muda **0** pixel da
silhueta, porque pele é paleta e não geometria.

**Por que a tomada começa no quadro 60:** antes disso a tela ainda assenta. No
quadro contado 20 o painel traz 2.726 pixels de tinta contra os 2.376 a 2.532
de todos os outros, e **nenhum** quadro da caminhada casa melhor que 3.570 —
pior que a própria tinta.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/confront.py` — `BUFFERS`, `still_frame()`, `game_at()`,
  `swapped_style()`, os limiares medidos (`WALK_LAG`, `MATCH_SHARE`,
  `MATCH_MARGIN`, `STYLE_MARGIN`) e as asserções do `check_silhouette`
- `docs/PLAN-LOOKS-PY.md` — o veredito da §10.3 (m) e o fechamento da §6 (h)
- `docs/prompts/perfil-looks.md` — as armadilhas novas
- `docs/tasks/looks/28-a-camera-do-jogo.md` — este Log

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 87 of 87 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/confront.py --silhouette
    control: frame 60 captured twice, 2383 pixel(s) of ink, identical
    control: frame(s) [80, 100] differ from it by [603, 1483] pixel(s)
    (slot 1) control: frame(s) [80, 100] differ from it by [670, 1452]
  the picture trails the draw by [0, 1, 2] frame(s) of the walk over 6
  comparison(s), and the bound is 2
confront --silhouette: 0 problem(s) over 2 slot(s)

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**O que continua aberto**

1. **A janela não desenha com a câmera do jogo.** A silhueta vive no núcleo; o
   painel da tela ainda usa a órbita da v1. É o critério 2, e é o que falta
   para a task fechar.
2. **Os três estilos não foram andados no jogo.** O controle troca o **nosso**
   lado sobre a mesma foto, que é o que prova que a silhueta vê a malha; andar
   o `HAIR` no emulador e refotografar é o resto.

**Problemas encontrados**

1. **Buffer de quadro lido na linha errada desloca a foto sem parecer erro.**
   240 e não 256 — e o sintoma é uma máscara com tinta demais que não casa com
   nada, não uma imagem visivelmente torta.
2. **Translação única mantida fixa é pior que alinhamento por comparação.**
   Ela parece mais rigorosa e mede outra coisa: 13% viraram 72%.
3. **Limite não é constante.** Exigir um deslocamento único entre o quadro que
   o par nomeia e o que a foto mostra produziu quatro respostas diferentes e a
   leitura "não há ponte"; o que há é um atraso com teto, e o teto se mede.
4. **Janela de varredura que o resultado encosta não é janela** — a de dois
   quadros devolveu o melhor na borda nas duas direções.

---

### Terceira sessão — a janela, e os estilos no jogo

**O painel desenha com a câmera do jogo.** O núcleo constrói a 4x4
(`scene.camera_matrix`) a partir do que o `--camera` mediu, e a janela só a
envia ao shader — a regra 3 no ponto da câmera. Ela é construída no tamanho
**nativo** do painel (146x120), não no do widget: `H` é contado em pixels do
jogo, e uma projeção feita para o widget desenharia a figura em tamanho nativo
dentro de uma área duas vezes maior. O self-check roda a matriz contra o
`project()` em pontos inventados e exige o **mesmo pixel** — pior caso
**0,000000 px**. Olhado nos dois slots: o jogador em pé, as duas chuteiras,
enchendo o painel como no jogo. Onde a **raiz** cai dentro do painel é escolha
de enquadramento (`scene.ROOT_AT`) e está dito que é: o deslocamento de desenho
da GPU continua sem medida.

**Dois achados andando o `HAIR` no jogo**, e o segundo mantém a task aberta:

1. **Com uma linha de CABEÇA sob o cursor, o jogo aproxima a câmera na cabeça.**
   A foto tirada logo depois das teclas é um close-up, com `Kind of Hair` na
   caixa de ajuda, **o dobro** da tinta da figura inteira (4.374 a 5.154 contra
   2.376 a 2.532) e a caminhada parada num quadro só. Não é assentamento —
   trezentos quadros depois continua igual. A foto passou a ser tirada com o
   cursor de volta em `NAT`, onde a câmera é a de corpo inteiro que o
   `--camera` mediu. **E a janela não faz esse close-up** — encaminhado para a
   [`LOOKS-TASK-31`](/docs/tasks/looks/31-o-painel-e-o-cenario.md), com a linha
   escrita lá.
2. **No corpo inteiro, a foto do jogo com `C1` ou `I3` casa com o NOSSO `A1`.**
   A tela lê `I3 TYPE` — a troca ficou —, e mesmo assim:

   ```text
   slot 2  A-C1: o nosso A1 dá 430, o nosso C1 dá  903
           A-I3: o nosso A1 dá 412, o nosso I3 dá  769
   slot 1  A-C1: o nosso A1 dá 446, o nosso C1 dá 1052
           A-I3: o nosso A1 dá 433, o nosso I3 dá  825
   ```

   Duas leituras cabem e nenhuma foi medida: **o corpo inteiro desenha uma
   cabeça que não depende do estilo** (um nível de detalhe menor), ou **a tabela
   `HAIR` → cabeça do `assembly` discorda do jogo nesse tamanho**. O que separa
   as duas é o close-up: medir a câmera com o cursor em `HAIR` e comparar os
   estilos **lá**, onde o estilo aparece. É o próximo passo desta task.

**E isto não reabre a §6 (h).** A (h) pedia uma testemunha de forma, e ela
existe e **funciona** — foi ela que achou a discordância. O que ficou aberto é
uma pergunta nova sobre o cabelo, e é critério desta task.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/scene.py` — `camera_matrix()`, `clip_to_pixel()`,
  `apply_matrix()`, `ROOT_AT`, `panel_camera()` e o self-check contra o
  `project()`
- `tools/looks/ui/viewer.py` — `game_camera`, e o `_camera()` que a envia
- `tools/looks/ui/looks_set.py` — `panel_native()`
- `tools/looks/ui/app.py` — o painel da tela desenha com a câmera do jogo
- `tools/looks/confront.py` — `_judged()`, `route_row()`, `game_at_tuple()`,
  `STYLE_TUPLES`, `STYLE_SETTLE` e o `--silhouette-styles`
- `docs/PLAN-LOOKS-PY.md`, `docs/prompts/perfil-looks.md`,
  `docs/tasks/looks/31-o-painel-e-o-cenario.md`,
  `docs/tasks/looks/28-a-camera-do-jogo.md`

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 87 of 87 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/confront.py --silhouette
  the picture trails the draw by [0, 1, 2] frame(s) of the walk over 6
  comparison(s), and the bound is 2
confront --silhouette: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette-styles
confront --silhouette: 12 problem(s) over 2 slot(s)   <- o critério aberto

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

O `looks_ui` e as duas silhuetas correram na árvore que difere da commitada só
por **comentários** no `scene.py` — as anotações `not-an-address` que a
varredura da regra 1 pediu depois. O `selftest`, o `cli check` e o
`check_tasks` correram na árvore commitada.

**Problemas encontrados**

1. **A câmera muda por linha**, e uma foto tirada com o cursor numa linha de
   cabeça é outro desenho — o dobro da tinta, com cara de tela ainda assentando.
2. **Os estilos andados no jogo discordam do nosso lado** — o critério aberto.

---

### Quarta sessão — o defeito que fabricou a evidência

**A §6 (h) foi fechada na segunda sessão com um número que era defeito, e fica
reaberta aqui.** O controle de estilo trocado pontuava 696–834 contra 179–426,
e isso foi lido como *"a silhueta vê a malha"*. Não era: o `scene.pose()` só
sabia posar a cabeça de referência, a seção **24**. O `HAIR` escolhe outra seção
do `MODEL.BIN` para cada estilo — **30** para `C1`, **34** para `I3` —, e essas
cabeças ficavam na origem do arquivo, **fora do pescoço**, 25 e 23 primitivas
sem pose, com todos os gates verdes, porque todos desenhavam a tupla de
referência. O controle estava pontuando uma cabeça flutuando.

Como apareceu, na ordem:

1. **As fotos do próprio jogo, umas contra as outras:** `A1` e `I3` diferem
   **15 px**, `A1` e `C1` **29 px**, todos na faixa da cabeça. O jogo desenha
   cabeças diferentes — mas quase iguais nesse tamanho.
2. **As nossas, com a mesma translação:** 206 e 235 px — oito a catorze vezes
   mais que as do jogo. Parte do "656/783" antigo era o alinhamento por caixa
   deslocando o corpo inteiro quando a cabeça muda de altura.
3. **A câmera do close-up**, medida com o cursor em `HAIR`
   (`oracle.py --camera <SLOT> HAIR`): o mesmo `H = 1376`, a translação em z de
   **999** contra 4125, e girada — igual nos dois slots.
4. **Uma conferência independente da câmera de corpo inteiro:** `T_peça − R·lugar`
   dá **exatamente** `[-480, 192, 4125]` nas doze peças, nos dois slots — o que
   o `--camera` leu. Câmera e lugares se confirmam um pelo outro.
5. **No close-up os nossos `C1` e `I3` saíram idênticos e 2.150 px menores** —
   e foi aí que o defeito apareceu: sem pose, a cabeça deles caía fora do
   painel. `scene.place_for` dá a qualquer cabeça do `MODEL.BIN` a pose da
   cabeça.

**O que vale depois do conserto:**

- **no corpo inteiro, estilo não se separa.** A foto `A1` do jogo casa com o
  nosso `I3` (378) melhor que com o nosso `A1` (399); `C1` e `I3` ganham os
  próprios por 7%. A silhueta testemunha **a pose e o corpo** — as seis
  comparações por quadro continuam a 7–18% — e **não** o cabelo. O controle de
  estilo trocado passa a ser impresso, não afirmado, no `--silhouette`;
- **no close-up**, com a câmera do close-up, lugares absolutos e o eixo no
  centro da tela (as caixas das duas máscaras ficam a 3 px), a faixa da cabeça
  escolhe o estilo certo em **2 de 3** nos dois slots e em qualquer largura de
  faixa — 30, 40 ou 50 linhas —, e erra o `A1`, que casa melhor com o nosso
  `C1`. Por que o `A1` erra não está medido.

**E a guarda que teria pegado o defeito:** o `scene.py --check-image` desenha
agora `A1`, `C1` e `I3` e exige **zero** primitiva sem pose — as três
desenham as seções 24, 30 e 34, todas posadas —, e o controle plantado
`scene-pose-knows-one-head` tira a regra e fica vermelho.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/scene.py` — `place_for()`, `POSED_STYLES`, a guarda no
  `--check-image` e o self-check da regra
- `tools/looks/oracle.py` — `CLOSE_UP_SETTLE`, a linha no `capture_camera`, o
  `write_camera` por linha e o `--camera <SLOT> <LINHA>`
- `tools/looks/confront.py` — o controle de estilo só afirmado no
  `--silhouette-styles`, e as docstrings de `STYLE_SWAP` e `STYLE_TUPLES`
  corrigidas
- `tools/looks/controls.py` — `scene-pose-knows-one-head`
- `docs/PLAN-LOOKS-PY.md` — a §6 (h) reaberta e a (m) corrigida
- `docs/prompts/perfil-looks.md` — a armadilha 68 corrigida e a 69
- `docs/tasks/looks/28-a-camera-do-jogo.md` — este Log

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 88 of 88 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/scene.py --check-image
      A-A1-A-A-A draws head section(s) [24], 0 primitive(s) not posed
      A-C1-A-A-A draws head section(s) [30], 0 primitive(s) not posed
      A-I3-A-A-A draws head section(s) [34], 0 primitive(s) not posed
scene --check-image: ok

$ python tools/looks/ui_check.py
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/oracle.py --camera 2 HAIR   (e o slot 1)
    H 1376 px, principal point (0.00, 0.00), the same at all 12 load(s)
    the camera matrix is [3067, 0, -1097, 45, 2488, 128, 1097, -268, 3067],
    translation [-120, 266, 999]
oracle --camera: 0 problem(s) over 1 slot(s)

$ python tools/looks/confront.py --silhouette
  the picture trails the draw by [0, 1, 2] frame(s) of the walk over 6
  comparison(s), and the bound is 2
confront --silhouette: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette-styles
confront --silhouette: 12 problem(s) over 2 slot(s)   <- o critério aberto

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

O `--silhouette` correu antes da última edição do `confront.py`, que mexeu só
em docstring; o `--silhouette-styles`, antes de o controle de estilo deixar de
ser afirmado no corpo inteiro — os doze problemas dele eram, àquela altura, o
controle de estilo nas seis comparações por quadro e nas seis por estilo.

**Problemas encontrados**

1. **Um defeito da LOOKS-TASK-27 fabricou a evidência que fechou a §6 (h).**
   Gate que só desenha a tupla de referência mede a tupla de referência.
2. **Alinhamento por caixa amplifica mudança de cabeça.** Uma cabeça mais alta
   desloca o centro da caixa e o corpo inteiro com ele.

---

### Quinta sessão — o close-up gira, e os três estilos fecham

**Qual cabeça o jogo desenha no close-up.** A captura de pose, rodada com o
cursor em `HAIR` depois de andar o estilo, nomeia a seção de cada carga: **24
para `A1`, 30 para `C1`, 34 para `I3`** — exatamente as da nossa tabela. O
mapeamento `HAIR` → cabeça está certo.

**E no close-up o modelo gira.** Todas as doze peças erravam a nossa matriz por
700 a 1.000 de 4.096 — não só a cabeça. Resolvendo `C⁻¹·M·R_poseᵀ` peça a peça,
sai a **mesma** rotação extra em `y` para as doze: **+18,3°** numa captura,
**−16,9°** e **+16,9°** nas outras duas, igual a 0,05° entre as peças de cada
uma, e **±0,03°** no corpo inteiro, que é o controle. O giro está composto em
cada peça e **ausente** da carga de câmera que o `--camera` lê: com ela, a
translação `T_peça − R·lugar` espalha **29** unidades; com a câmera derivada das
próprias peças, menos de uma.

**Uma correção da quarta invocação.** Eu escrevi, na saída dela, que no close-up
`T_peça − R·lugar` ficava "a ±1" da câmera lida. Estava errado: imprimi os quatro
primeiros valores de uma lista ordenada, não o intervalo — que era de 29
unidades. Nada disso entrou em documento, e a armadilha 71 registra a forma do
erro.

**`oracle.camera_from_pieces`** deriva a câmera das peças que ela compôs —
`C = M·R_poseᵀ` e `T = T_peça − C·lugar`, uma vez por peça — e **recusa** se as
doze não concordarem. Conferida contra o corpo inteiro, bate com a lida a uma
unidade.

**Os três estilos, com foto e câmera da mesma parada** (`--silhouette-styles`),
comparados na faixa da cabeça (40 linhas a partir do topo da tinta do jogo):

```text
slot 2  jogo A1:  nosso A1 202*  C1 357  I3 274
        jogo C1:  nosso A1 488   C1 119* I3 563
        jogo I3:  nosso A1 385   C1 559  I3 155*
slot 1  jogo A1:  nosso A1 178*  C1 323  I3 284
        jogo C1:  nosso A1 469   C1 127* I3 561
        jogo I3:  nosso A1 373   C1 542  I3 176*
```

**6 de 6**: cada foto escolhe o próprio estilo, e os outros dois — os estilos
trocados — discordam, por 1,36x a 4,10x contra o mais próximo (esta linha
dava uma faixa arredondada, de conta à mão sobre a tabela, até a
[`CORR-LOOKS-064`](/docs/tasks/looks/CORR-LOOKS-064.md); o gate não imprimia
razão). Uma captura (slot 1, `C1`) derivou a
câmera com espalhamento de 74 em 4.096 contra 3,7 das outras — dentro do limite,
e provavelmente uma das matrizes que o jogo mistura (a
[`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md) mediu seis).

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/oracle.py` — `camera_from_pieces()`
- `tools/looks/confront.py` — `HEAD_BAND`, `CLOSE_UP_ROW`,
  `closeup_at_tuple()`, `check_closeup_styles()`, o `--silhouette-styles`
  ligado a ele, e o caminho morto do corpo inteiro removido (`game_at_tuple`,
  `STYLE_SETTLE`, o laço de estilos do `check_silhouette`)
- `docs/PLAN-LOOKS-PY.md` — a §6 (h) e a §10.3 (m) fechadas
- `docs/prompts/perfil-looks.md` — as armadilhas 70 e 71 e a linha do gate
- `CLAUDE.md` — os comandos novos e a armadilha das duas câmeras
- `docs/tasks/looks/28-a-camera-do-jogo.md` — este Log

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 88 of 88 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/confront.py --silhouette
    control: frame 60 captured twice, 2383 pixel(s) of ink, identical
    control: frame(s) [80, 100] differ from it by [603, 1483] pixel(s)
  the picture trails the draw by [0, 1, 2] frame(s) of the walk over 6
  comparison(s), and the bound is 2
confront --silhouette: 0 problem(s) over 2 slot(s)

$ python tools/looks/confront.py --silhouette-styles
confront --silhouette-styles: 0 problem(s) over 2 slot(s)

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

O `looks_ui` não foi rodado de novo: esta sessão mudou só o `oracle.py` e o
`confront.py`, que o `ui_check.py` não importa, e a última corrida dele —
**7 de 7**, na quarta sessão — foi na árvore que já tinha o `scene.py` de hoje.

**Problemas encontrados**

1. **O close-up gira o modelo, e a câmera lida não traz o giro** — armadilha 70.
2. **Um intervalo lido pela cabeça de uma lista ordenada** — armadilha 71.

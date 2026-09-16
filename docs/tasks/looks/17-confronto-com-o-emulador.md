---
id: LOOKS-TASK-17
title: "Confronto — nosso quadro contra o quadro do emulador, na mesma tupla"
type: verificação
category: oráculo
phase: 6
depends_on: ["LOOKS-TASK-16"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §5.3"
status: concluído
---

# LOOKS-TASK-17: O confronto com o gabarito vivo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §5.3 e
  §5.6.
- **A diferença não precisa ser zero, e não vai ser.** A §5.6 já diz por quê: a
  pose vem do `ANIME.BIN`, que está fora de escopo, e a câmera do jogo muda por
  campo. Nosso render é pose neutra e câmera livre.
- *Um número que ninguém olhou não é verificação.* A diferença tem de ser
  **medida, registrada e explicada**.
- **`load_state` é o que torna o confronto repetível.** Sem baseline fixo, o
  quadro capturado depende de quanto tempo a animação correu, e o número muda
  entre corridas sem que nada tenha mudado. Slot 1 é goleiro, slot 2 é jogador
  de linha.

---

- **Três resíduos da tabela de montagem chegam aqui, e o confronto é o que os
  fecha.** Medidos em 2026-09-16 pela
  [`LOOKS-TASK-14`](/docs/tasks/looks/14-tabela-de-montagem.md):
  **(1)** os estilos de cabelo `H1`, `M1` e `N1` não foram alcançados pelo mapa
  e o `assembly.head_of` os recusa — as seções pares 38, 40 e 42 nunca foram
  nomeadas, e casar três com três por contagem é o mapeamento plausível que
  este ciclo não escreve; **(2)** a faixa da folha de cabelo só é aplicada em
  **quatro** das treze cabeças (`layout.HAIR_QUADS`), porque o breakpoint da
  instrução que escreve o quad só parou nessas quatro; **(3)** o mapa inteiro é
  do **jogador de linha**, e o bloco de cabeças do goleiro não foi andado.
  Confrontar as tuplas nos **dois slots** é o que mede as três coisas de uma
  vez — e uma tupla com `H1` tem de aparecer no confronto como recusa, não
  como diferença de pixel.
- **O corpus já foi confrontado uma vez, e no nível de textura.** O
  `assembly.py --corpus` compara onde os renders de terceiro mudam com a altura
  que a malha dá às primitivas de cada campo, e fecha em `rho = 0,80`. O que
  ele **não** faz é comparar o desenho: isso é daqui.

---

- **A POSE NÃO ESTÁ EM ARQUIVO NENHUM QUE ESTE CICLO LÊ, e isso chega aqui.**
  Medido em 2026-09-16 pela
  [`LOOKS-TASK-15`](/docs/tasks/looks/15-visualizador-opengl.md): cada seção é
  modelada em torno da **própria origem** — a cabeça vai de y -15 a 48 e a
  chuteira de -15 a 18 —, então nem "pose neutra" o disco dá. O visualizador
  desenha uma **prateleira** (`scene.shelf`), peças em fila. Quem posiciona é o
  jogo, na display list da §6(a) do plano, que é justamente o que se lê com o
  emulador de pé.

  **Esta linha dizia que medir o deslocamento de cada peça era trabalho desta
  task, "e sem ele o confronto compara uma fila com um jogador e a métrica não
  quer dizer nada".** Valia para uma métrica de pixel. A métrica escolhida é de
  **cor**, e cor não depende de onde a peça fica — corrigido em 2026-09-16, ao
  executar; a pose segue não medida e está escrita na
  [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md).
- **Qual das duas diagonais um quad é continua sem veredito.** O
  `scene.TRIANGLES` usa a ordem **como o arquivo guarda** — (0, 1, 2) e
  (1, 2, 3) — e o `section.Primitive.corners` oferece a leitura do `we3d`, que
  escolhe a outra. As duas desenham; só o confronto contra o quadro do jogo
  diz qual. Escolher aqui em silêncio é o que esta linha existe para impedir.
  **Respondido ao executar:** a ordem guardada, 7 a 0 contra a do `we3d`, pela
  display list do jogo (`confront.py --score`, Log abaixo).
- **O uniforme não é desenhado, e não é bug:** 237 das 593 primitivas da figura
  amostram páginas que o `DAT2D.BIN` não tem — elas vivem nos 105
  `TEX_*.BIN`, um por time, cada um com cinco paletas de 256 entradas
  ([`CORR-LOOKS-025`](/docs/tasks/looks/CORR-LOOKS-025.md)). Saem em cinza de
  espaço reservado. Qual contêiner e qual das cinco paletas o jogo usa é
  pergunta que só o emulador responde, e o `layout.DIGEST` ainda não tem esses
  arquivos.
- **A tela da barba pode alcançar mais do que a varredura mediu.** O
  `assembly` mede `FACE` chegando a **cinco** valores (A..E) e **recusa** `F` e
  `G`; o corpus de terceiro traz dezesseis renders com eles
  (`scene.py --corpus`: 31 dos 50 desenhados, 16 recusados por isso). É a
  armadilha 19 outra vez, do outro lado: andar o campo até a ponta nos **dois**
  slots é o que separa "a tela trava em E" de "a varredura parou em E".
  **Respondido ao executar:** a varredura parou — a tela vai a `G` nos dois
  slots (`confront.py --reach FACE`), e isso é a
  [`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md).

---

## Objetivo

Fechar o laço: mesma tupla dos dois lados, e um número que se possa acompanhar
ao longo do projeto.

---

## Critério de conclusão

- [x] O ciclo roda: `confront.py --run` faz `load_state`, escolhe a tupla na
      tela por `press_button` (cada tecla afirmada sobre a própria célula),
      captura por `take_screenshot`, desenha a mesma tupla pelo `ui/app.py` e
      compara.
- [x] Captura no **mesmo quadro**: tudo é `frame_step` contado a partir do
      state — o quadro de cada tupla sai impresso (90 a 706) — e a rota da
      referência repetida dá **0 pixel** de diferença no quadro inteiro, nos
      dois slots, e as duas corridas completas deram a mesma matriz.
- [x] **Dois slots**, seis tuplas cada.
- [x] **Cinco tuplas pontuadas e uma recusa** por slot — e não uma.
- [x] Métrica nomeada e justificada: interseção de histogramas de cor de 15
      bits, cada quadro contra todos os renders do slot, com o teto de
      liderança ao lado. Número por tupla no Log.
- [x] Fontes de diferença atribuídas: pose e câmera (fora da métrica por
      construção), resolução (a cor de 15 bits sai exata), filtro (nenhum:
      as cores do quadro são as da paleta). O que sobrou virou **três CORRs**
      e três incógnitas escritas na LOOKS-TASK-20.
- [x] Repetível e versionado: `confront.TUPLES`, `confront.plan()` e os três
      comandos, com `--score` rejulgando as capturas sem emulador.

---

## Log de Execução

**Executado em:** 2026-09-16 — **CONCLUÍDA**.

### O que se aprendeu

**Quadro do jogo e render nosso não se comparam por pixel, e não precisam.** A
pose e a câmera mudam quase todo pixel sem mudar a tupla; o que a tupla muda é
**quais cores aparecem**. Medido antes de escrever a métrica: as catorze cores
de 15 bits da nossa cabeça `A-A1-A-A-A` aparecem **exatas** no quadro do
emulador — os quads são desenhados sem modulação. Daí a métrica: interseção de
histogramas de cor, e nunca um número sozinho.

**Vitória por pouco tem teto, e o teto se calcula.** Para histogramas
normalizados, `I(g, a) − I(g, b) ≤ 1 − I(a, b)`: nenhum quadro do jogo lidera
por mais do que os **nossos** dois renders distam. A referência e a barba
`B`/`E` distam 0,039, então a margem de 0,02 pedia metade do teto. **O nível
`ranked` foi acrescentado depois da primeira corrida lida** — está dito no
código e aqui, porque regra escrita depois do dado é o tipo que se ajusta a
ele; a razão é o limite, não o número.

**A display list é juiz de ordem de vértice.** A GPU desenha um pacote como
(0, 1, 2) e (1, 2, 3); casar os `(u, v)` de cada primitiva com os pacotes diz
em que ordem o jogo as manda. A ordem **guardada** ganhou por 7 a 0, e isso
mostrou de graça que o anel do wireframe (0-1-2-3) desenhava as duas diagonais
— eram os cruzamentos da captura da LOOKS-TASK-15, lidos como malha densa.

**A célula de valor não conta valores** — o cursor pisca e a seta de fim de
curso mora dentro da caixa. A contagem crua deu 8 numa linha de sete rótulos. A
máscara de glifo não pisca (armadilha 28 do perfil).

### As corridas

As **capturas** saem da segunda corrida completa do `--run`, feita com o
`confront.py` antes do veredito de três níveis — a captura não depende do
veredito, e a primeira corrida, com outro código de pontuação, deu a mesma
matriz número a número. O **veredito** abaixo é o `--score` rodado na árvore de
`6b6b671` sobre essas capturas. O `--reach` rodou com a máscara de glifo que
está no commit.

```text
$ python tools/looks/confront.py --run      # e --score sobre as capturas
  slot 2 A-A1-A-A-A: captured on frame 90 after load_state
  slot 2 B-A1-A-A-A: captured on frame 118 after load_state
  slot 2 A-A1-C-A-A: captured on frame 202 after load_state
  slot 2 A-I3-A-A-A: captured on frame 706 after load_state
  slot 2 A-A1-A-B-E: captured on frame 398 after load_state
  slot 2 A-H1-A-A-A: captured on frame 622 after load_state
  slot 2: the reference route repeated differs in 0 pixel(s) of the whole frame -- repeatable
  slot 2 A-H1-A-A-A: our side refuses -- app: A-H1-A-A-A refuses -- hair style H1 ...
  slot 2, figure 0: histogram intersection over the 34 colour(s) our side draws
                   A-A1-A-A-A  A-A1-A-B-E  A-A1-C-A-A  A-I3-A-A-A  B-A1-A-A-A
      A-A1-A-A-A   0.766       0.750       0.597       0.723       0.137
      B-A1-A-A-A   0.124       0.124       0.001       0.053       0.660
      A-A1-C-A-A   0.647       0.635       0.911       0.659       0.010
      A-I3-A-A-A   0.749       0.730       0.630       0.777       0.103
      A-A1-A-B-E   0.750       0.759       0.580       0.705       0.137
      A-H1-A-A-A   0.775       0.758       0.657       0.760       0.130    (refused)
      A-A1-A-A-A   RANKED      first by 0.016 over A-A1-A-B-E, whose render ours is 0.039 apart from
      B-A1-A-A-A   WIN         by 0.536 over A-A1-A-A-A
      A-A1-C-A-A   WIN         by 0.253 over A-I3-A-A-A
      A-I3-A-A-A   WIN         by 0.028 over A-A1-A-A-A
      A-A1-A-B-E   RANKED      first by 0.010 over A-A1-A-A-A, whose render ours is 0.039 apart from
  slot 2: 3 win, 2 ranked, 0 expected, 0 unexplained
  slot 1: the reference route repeated differs in 0 pixel(s) of the whole frame -- repeatable
      A-A1-A-A-A   RANKED      first by 0.016 over A-A1-A-B-E ...
      B-A1-A-A-A   WIN         by 0.536 over A-A1-A-A-A
      A-A1-C-A-A   WIN         by 0.265 over A-A1-A-A-A
      A-I3-A-A-A   EXPECTED    the goalkeeper's head ... (CORR-LOOKS-043)
      A-A1-A-B-E   RANKED      first by 0.010 over A-A1-A-A-A ...
      A-H1-A-A-A   EXPECTED    the goalkeeper's head ... (CORR-LOOKS-043)
  slot 1: 2 win, 2 ranked, 2 expected, 0 unexplained
  the diagonal: 539 textured quad packet(s) in the two bands, and the head's 18 primitive(s):
      stored 5, untangled 0, stored one row off 2, untangled one row off 0,
      twin 4, ambiguous 0, absent 7
      verdict: the game draws the STORED order
confront: ok

$ python tools/looks/confront.py --reach FACE
  FACE on slot 2: 530 glyph pixel(s) at rest, still with nothing pressed; 6 Right(s)
      changed the label, so the screen reaches 7 of the 8 value(s) the field holds
  FACE on slot 1: (idem) ... reaches 7 of the 8 value(s) the field holds
```

Os quadros foram **olhados**: a tela `LOOKS SET` fecha no rosto na linha `HAIR`
nos dois slots; a tira `reach-{1,2}-FACE-*` mostra `BTYPE`..`GTYPE` e depois
`GTYPE` parado; o wireframe novo da cabeça desenha contornos e nenhum X.

### Gates medidos

```text
$ python tools/looks/selftest.py --quiet        # na arvore de 6b6b671
  ..... rule 1 swept 19 file(s), 13930 line(s)
  ..... 47 of 47 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/<modelfile|texture|atlas|skin|looks|assembly|pieces|scene>.py --check-image
  8 de 8: ok
$ python tools/looks/oracle.py --check           oracle.py: 0 failure(s)
$ python tools/looks/ui_check.py                 looks_ui: 3 of 3 negative control(s) red,
                                                 and the window drew every tuple it was asked for
$ python tools/check_tasks.py                    check_tasks: 123 task(s), ok
```

Controles de 41 para 47: `confront-margin-ignored`, `confront-tie-passes`,
`confront-background-counted`, `confront-diagonal-any-clut`,
`confront-twins-vote` e `confront-mask-sees-blink`. O `EDGES` do wireframe não
ganhou controle: o `viewer.py` é Qt e não tem `self_check`, e nenhum gate lê o
wireframe — dito aqui para não parecer coberto.

### Problemas encontrados, e para onde foram

- **Os quads de cabelo saem uma linha curtos** — o jogo desenha `v` 15 onde o
  disco guarda 14 ([`CORR-LOOKS-042`](/docs/tasks/looks/CORR-LOOKS-042.md)).
  **Consertado em 2026-09-16:** as mesmas capturas dão agora `stored 7` e
  `stored, one row off 0`; a transcrição acima é da corrida desta task.
- **O goleiro desenha qualquer estilo como `A`, sem recusar**
  ([`CORR-LOOKS-043`](/docs/tasks/looks/CORR-LOOKS-043.md)).
- **A tela da barba alcança sete valores, e a tabela diz cinco e recusa `F` e
  `G`** ([`CORR-LOOKS-044`](/docs/tasks/looks/CORR-LOOKS-044.md)). A hipótese
  "editor gravando direto" da LOOKS-TASK-18 caiu, e a linha está lá.
- **A pose, o uniforme e sete quads fora da display list lida** ficam abertos,
  com a razão escrita na
  [`LOOKS-TASK-20`](/docs/tasks/looks/20-reconciliacao-e-entregaveis.md).
- **A métrica para os JPGs não é a mesma coisa**: compressão com perda não
  guarda cor exata — escrito na
  [`LOOKS-TASK-18`](/docs/tasks/looks/18-corpus-dos-cinquenta-renders.md).
- O primeiro nome de arquivo das faixas de RAM saía do tamanho da lista de
  pacotes (`band-270.bin`); virou `BANDS`, fixo.

### Arquivos criados/modificados

Commit `6b6b671`:

- `tools/looks/confront.py` — novo
- `tools/looks/controls.py` — seis controles
- `tools/looks/selftest.py` — `confront` na lista de módulos
- `tools/looks/scene.py` — a docstring do `TRIANGLES` com o veredito
- `tools/looks/ui/viewer.py` — o `EDGES` do contorno, e a docstring do
  descarte de face
- `docs/PLAN-LOOKS-PY.md` — §3.2, §5.3 com a matriz, §5.6 item 1
- `docs/prompts/perfil-looks.md` — armadilhas 28 e 29, três linhas de gate
- `docs/tasks/looks/18-corpus-dos-cinquenta-renders.md` e
  `docs/tasks/looks/20-reconciliacao-e-entregaveis.md` — o encaminhado, escrito
  nas tasks de destino
- `docs/tasks/looks/CORR-LOOKS-042.md`, `-043.md`, `-044.md` e
  `docs/tasks/looks/correcoes-progresso.md` — as três correções abertas

Commit seguinte: este Log, o frontmatter e `docs/tasks/looks/progresso.md`.

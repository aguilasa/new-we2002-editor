---
id: LOOKS-TASK-32
title: "Incógnita (p) — o ciclo da caminhada: quadros por passada, interpolação e balanço"
type: investigação
category: oráculo
phase: 11
depends_on: [LOOKS-TASK-26]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.3"
reviewed_on: 2026-09-24
review_commit: 42c23a32
done_on: 2026-09-23
done_commit: 6a2c16fb
---

# LOOKS-TASK-32: O ciclo da caminhada

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.3 (p) e §10.4.
- **Nenhum número da gravação do usuário vale aqui.** Vídeo de tela tem a
  cadência do gravador; quem conta é o `frame_step`.
- **Animar num ritmo inventado produz caminhada bonita e errada.**
- **Duas perguntas que parecem uma:** quantos quadros o jogo leva para repetir
  a pose, e quantos quadros-chave o `ANIME.BIN` guarda. Se forem diferentes, o
  jogo interpola, e a regra se mede.
- **O tronco balança na gravação.** Raiz da animação ou câmera muda onde o
  balanço mora.

- **O jogo MISTURA matrizes, e medir isso é desta task.** Medido em 2026-09-18
  pela [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md), sobre
  96 peças julgadas (de 192 capturadas — oito capturas não param no
  desempacotamento) nos dois slots:
  - **os ângulos vêm sempre do arquivo** — 96 de 96, inteiro por inteiro, no
    par que o jogo está lendo. Uma versão anterior desta linha dizia que
    metade dos quadros era construída, e aquilo era artefato da ponte errada
    (o quadro que o estado nomeia, que erra no goleiro);
  - **mas 6 das 96 matrizes não são a volta de par nenhum do arquivo** —
    varredura de todos os pares, `anime.no_pair_explains()`. O caminho que as
    produz é `0x80011F90`: ele **soma a matriz recém-construída com a que o
    jogo guardou e desloca um bit** (`sra 1`), meia-palavra a meia-palavra, e
    quem escolhe esse caminho é o byte em `0x0(s3)`;
  - as seis eram todas de **um passe só**, e as peças que vieram do quadro
    anterior da animação — o passe atravessou a troca de quadro. **De onde vem
    a segunda matriz da soma é o que falta**, e é o que decide o ritmo.
  - As ferramentas já entregam o que essa medição precisa:
    `oracle.py --pose <SLOT> <N>` grava, por peça, o ângulo e **o par que o
    jogo leu**; `anime.py --against-pose` separa exatas, misturadas e
    inexplicadas a cada corrida.

- **Três medições da [`LOOKS-TASK-29`](/docs/tasks/looks/29-altura-e-corpo.md),
  de 2026-09-19, que são do ritmo e não da estatura.** Ela as achou enquanto
  controlava `HEIG` e `BODY`, recusou-as do controle com razão, e elas se medem
  **aqui** (armadilhas 73 e 74 do perfil). Quem as reproduz é
  `python tools/looks/oracle.py --stature`, em toda corrida:
  - **uma passada de desenho atravessa DOIS quadros do `ANIME.BIN`**, cortados
    numa peça que muda com a fase — `frames [1, 2]` no slot 2 e `[3, 4]` no
    slot 1, remedido em 2026-09-20. Comparar pares peça a peça gastou 80
    passadas procurando um corte que não voltava; o que nomeia a pose é o
    **conjunto** de quadros (`oracle._stature_frames`). Isto é o período visto
    de outro ângulo: se uma passada desenha dois quadros-chave, "quadros por
    passada" e "quadros do `ANIME.BIN`" não são a mesma contagem;
  - **uma passada inteira pode vir interpolada** — 11 pares lidos e **0 de 11**
    matrizes exatas, medido pela 29 —, pela mesma média `(a+b)>>1` de
    `0x80011F90` que explica as 6 misturas de peça avulsa acima. A diferença
    importa para o critério: lá é peça avulsa na troca de quadro, aqui é a
    passada toda;
  - **no goleiro, o quadro 0 é mistura** na estatura do próprio estado: a
    `foot b` sai **até 92 de 4096** fora da matriz do arquivo **com os ângulos
    do scratchpad iguais aos do par** — ângulo certo, matriz outra. O
    `--stature` imprime isso como passada recusada, e a linha é literal na
    corrida de 2026-09-20:

    ```text
    control refuses pass 2, frames [0, 1]: 11 of 12 exact, ['foot b'] off by
    up to 92 of 4096 with the scratchpad angles the file's own
    ```

  É onde o critério "quadros-chave contra quadros desenhados: iguais, ou a
  interpolação medida" encosta: os três casos são a interpolação aparecendo, e
  o goleiro dá o exemplo mais barato de medir, porque acontece no quadro 0.

- **A [`LOOKS-TASK-27`](/docs/tasks/looks/27-o-boneco-montado.md) deixou uma
  armadilha que alcança toda leitura de registrador numa parada:** o ponteiro
  de modelo que o jogo carrega quando a matriz é carregada nomeia a peça que
  ele **acabou de desenhar**, uma parada atrás (`oracle.DRAW_LAG`). Quem
  acrescentar uma captura por breakpoint confere o atraso com
  `oracle.py --pose-lag` em vez de supor que o registrador fala da peça da vez.

---

## Objetivo

Medir o ciclo da caminhada em quadros do jogo, e fazer o `anime.py` devolver a
pose de **qualquer** quadro do ciclo igual à do jogo.

---

## Critério de conclusão

- [x] O período: a primeira volta de todas as matrizes ao quadro 0, contada
      por `frame_step`, nos dois slots — e o comando que conta.
- [x] Quadros-chave contra quadros desenhados: iguais, ou a interpolação
      medida, com o arredondamento do ponto fixo.
- [x] `anime.py --frame N` reproduz o jogo **exatamente** em pelo menos oito N
      espalhados pelo ciclo, fora os quadros-chave.
- [x] O balanço atribuído: raiz da animação, ou câmera.
- [x] Controle negativo: interpolar pelo quadro-chave vizinho errado fica
      vermelho.
- [x] §10.3 (p) com o veredito e a data.

---

## Log de Execução

**Executado em:** 2026-09-23

### O que foi feito

- **A unidade da caminhada é a passada de desenho, e o período é 34 delas.**
  O `oracle.py --walk` toma passadas consecutivas numa sessão só, com o
  `frame_number` do emulador lido em cada parada: a tela desenha a figura
  **uma vez a cada dois ou três quadros**, o ciclo fecha em **34 passadas e 77
  quadros contados**, igual nos dois slots, e a pose não volta em passada
  nenhuma antes.
- **Em quadros de vídeo não existe período, e isso é medição.** O índice da
  animação avança 219 vezes em 500 quadros (0,438 por quadro), o intervalo
  alterna 2 e 3, e a varredura de período não acha nenhum até 250 quadros nem
  no padrão de intervalos. Por isso o critério — "a primeira volta de todas as
  matrizes ao quadro 0, contada por `frame_step`" — se responde em passadas,
  com o número de quadros ao lado como medição daquela corrida (armadilha 98).
- **São 34 poses desenhadas a partir de 17 guardadas: o jogo espelha o segundo
  lado.** Cada membro lê o par do membro do outro lado (`anime.WALK_SWAP`) e os
  ângulos vêm virados (`anime.WALK_RULES`): cabeça e tronco negam o segundo e o
  terceiro; os dez membros negam o primeiro e o terceiro e somam meia volta; e
  os dois casos negam o `x` do lugar. As regras saem das **dez variantes** de
  desempacotamento do dispatch `0x80011DA0`, lidas no código e conferidas
  contra os ângulos que o jogo deixou no scratchpad em 516 paradas por slot.
- **Interpolação entre quadros-chave: não. Uma média, sim, e estreita.** Na
  visita que **abre cada lado** o jogo soma a matriz nova com a guardada e
  desloca um bit — `(a + b) >> 1`, aritmético (`layout.ANIME_BLEND`) —, 24 das
  408 peças de um ciclo, as mesmas que o byte seletor marca. Fora delas toda
  matriz é a volta de um par, exata.
- **O instrumento mudou de instrução, e é o que fecha um mistério antigo.** A
  vigia agora é `layout.ANIME_BUILD` (o `jal` da `RotMatrix`), não
  `ANIME_UNPACK`: dez variantes dividem o dispatch, e a passada que toma outra
  não para na instrução antiga — é a razão das oito capturas sem par da
  [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md), não
  oscilação do emulador. 480 de 480 paradas trazem par na nova, contra 132 de
  480 na antiga.
- **A vaga de par em que uma passada abre é propriedade do save state:** 7 no
  slot 2 e 0 no slot 1, constante em toda passada de uma corrida. É o "uma
  passada atravessa dois quadros do `ANIME.BIN`" da
  [`LOOKS-TASK-29`](/docs/tasks/looks/29-altura-e-corpo.md), com o corte
  nomeado — e por isso `anime.walk_pose` recebe a vaga medida em vez de
  assumir 7.
- **O reprodutor:** `anime.py --frame N [SLOT]` monta a pose de uma passada do
  arquivo mais o ciclo medido, e `--against-walk` julga as 34 passadas **sem
  emulador**.

### Evidência

```text
$ python tools/looks/oracle.py --walk            # ~1 min 20 s por slot
  -- slot 2 (outfield player) --
    control: the camera is the same matrix 120 frame(s) later, so what moves over the cycle is the pose and not the view
    control: the first 6 pass(es) taken twice from load_state, 12 load(s) each, identical number by number
    control: every one of the 516 load(s) reads its own pair (346) or its sibling's (170), and a pass opens on pair slot 7
    34 distinct pose(s) in 43 pass(es); the first pose comes back after 34 pass(es) and 77 counted frame(s), and at no pass before it
    the cycle starts at visit 4 of 34: frame 4 of 17, side 0
    408 of 408 matrices of the cycle are the file's, integer for integer (worst 0)
    control: one visit along, 34 of 408 exact -- the neighbour is not the pose
    the averaging byte says average at 24 of the 408 load(s) of the cycle, and the model averages the same 24
    the places land 0 unit(s) from the translations the game loaded, against 111 with the mirror's x left alone
oracle --walk: 0 problem(s) over 2 slot(s)
       (o slot 1 dá os mesmos números, com a passada abrindo na vaga 0 e o
        ciclo começando na visita 6)

$ python tools/looks/anime.py --against-walk     # sem emulador, ~2 s
  slot 1 (goalkeeper): 34 pass(es) of the cycle, 408 matrix(es), 17 frame(s) in the file, 77 counted frame(s) a cycle
  408 of 408 exact, integer for integer (worst 0)
  the 8 pass(es) asked for, spread over the 18 that no frame of the file holds (11, 13, 15, 17, 20, 22, 24, 26): worst 0 of 4096
  control: one visit along, 34 of 408 exact
  slot 2 (outfield player): ... 408 of 408 exact ... spread over the 19 (12, 14, 16, 19, 21, 23, 26, 28): worst 0 of 4096

$ python tools/looks/anime.py --frame 12 1
  slot 1, drawn pass 12 of 34: visit 18, frame 1 of 17, side 1
    head         frame  1 mirror          angles (32, -16, 0)           place (3, -400, -6)
    torso        frame  1 mirror          angles (48, -16, -4096)       place (2, -319, -2)
    upper arm a  frame  1 flip            angles (-1840, 208, -1792)    place (-56, -332, -7)
```

**O balanço é da animação, e não é do tronco.** A câmera lida na própria carga
volta com as mesmas nove meias-palavras e a mesma translação 120 quadros depois
— mais de um ciclo —, e o modelo acerta as 408 matrizes de cada slot com **uma**
câmera só. Dentro da animação, sobre o ciclo do slot 2:

```text
foot b       rotation spread  4552   translation spread [31, 31, 179]
foot a       rotation spread  4268   translation spread [42, 31, 178]
shin b       rotation spread  4140   translation spread [21, 19, 120]
...
head         rotation spread   333   translation spread [13, 8, 4]
torso        rotation spread   185   translation spread [ 8,  8,   2]
```

O tronco é a peça **mais parada** da figura, e não há raiz que translade o
conjunto: o balanço que a gravação mostra são os membros. É resultado
negativo para a pergunta como ela foi escrita ("raiz da animação, ou câmera") —
nenhuma das duas.

**Os controles plantados**, todos vermelhos (`python tools/looks/controls.py`,
`108 of 108 red`):

```text
RED    anime-walk-never-mirrors         anime.py :: _visit_turn
RED    anime-walk-averages-every-visit  anime.py :: walk_pose
RED    anime-walk-pass-is-one-frame     anime.py :: walk_pose
```

E o controle que o critério pede — interpolar pelo quadro-chave vizinho errado
— é o `shift=1` do `anime.against_walk`, que roda em **toda** corrida dos dois
comandos: 34 de 408 exatas contra 408 de 408.

### Problemas encontrados

- **Três controles do `anime.py` não podiam ficar vermelhos.** Estavam escritos
  `attempt("... é recusado", BadAnime, lambda: ...)`, e o `attempt` do
  `harness` **roda** o segundo argumento: ele construía a exceção, devolvia e
  afirmava nada. Passaram a `refuses(..., trecho, BadAnime)`, com o trecho da
  mensagem, e os sete do módulo agora afirmam (armadilha 100). Foi copiando
  esse padrão para os controles novos que ele apareceu.
- **A primeira leitura do período foi trivial e errada.** Contando por
  `frame_step` e capturando a pose a cada quadro, a pose "volta" no quadro
  seguinte — o quadro-chave fica 2 ou 3 quadros na tela. O que a pergunta quer
  é a volta do **desenho**, e o desenho é a passada.
- **O `pc` da parada não é a variante.** A explicação em pé até hoje era que o
  jogo *misturava* matrizes na segunda metade do ciclo (§10.3 (j)); o que ele
  faz é espelhar, e a mistura existe em 24 peças de 408. A varredura de todos
  os pares sob as três regras continua não explicando as seis matrizes da
  LOOKS-TASK-26 — elas são médias —, o que separa os dois casos.
- **O `capture_pose` não serve para contar o ciclo.** Ele volta ao estado e
  anda N quadros, mas depois roda livre até a parada e o `_pose_cycle` precisa
  de duas passadas para achar o período: a passada capturada fica duas ou três
  à frente do N pedido. A captura sequencial numa sessão só, com o
  `frame_number` lido em cada parada, é o que casa passada e quadro.
- **A câmera tinha de ser lida depois das passadas.** Lida antes, os três
  stops dela adiantam o jogo e a sequência não bate com a do controle — o
  primeiro controle ficou vermelho por isso, e a ordem agora está escrita no
  código com o motivo.

### Gates

Quatro gates re-rodados em 2026-09-25 na HEAD `a3e6809b`, cujo `tools/looks/`
é o do commit entregue (`git diff --stat 6a2c16fb HEAD -- tools/looks` sai
vazio), com `WE2002_LOOKS_IMAGE` na imagem japonesa; todos verdes. A
transcrição anterior era de uma corrida no meio da task, 150 linhas de código
antes da entrega ([CORR-LOOKS-093](/docs/tasks/looks/CORR-LOOKS-093.md)).

```text
$ python tools/looks/selftest.py --quiet | grep -E "rule 1 swept|controls red|^looks_selftest"
  ..... rule 1 swept 27 file(s), 32555 line(s)
  ..... 108 of 108 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check | tail -1
cli check: 12 module(s), 12 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/anime.py --against-walk
  slot 1 (goalkeeper): 34 pass(es) of the cycle, 408 matrix(es), 17 frame(s) in the file, 77 counted frame(s) a cycle
  408 of 408 exact, integer for integer (worst 0)
  the 8 pass(es) asked for, spread over the 18 that no frame of the file holds (11, 13, 15, 17, 20, 22, 24, 26): worst 0 of 4096
  control: one visit along, 34 of 408 exact
anime --against-walk: 0 failure(s)
  slot 2 (outfield player): 34 pass(es) of the cycle, 408 matrix(es), 17 frame(s) in the file, 77 counted frame(s) a cycle
  408 of 408 exact, integer for integer (worst 0)
  the 8 pass(es) asked for, spread over the 19 that no frame of the file holds (12, 14, 16, 19, 21, 23, 26, 28): worst 0 of 4096
  control: one visit along, 34 of 408 exact
anime --against-walk: 0 failure(s)

$ python tools/check_tasks.py | tail -1
check: 0 error(s), 13 warning(s) in 4 cycle(s)
```

Os dois abaixo **não** foram re-rodados: são a transcrição da corrida da
própria task, na forma em que ela a colou. O `oracle.py --walk` precisa do
emulador e o `ui_check.py` abre janela, e a re-corrida de 2026-09-25 não tinha
nenhum dos dois à disposição. Como o `tools/looks/` não mudou desde o
`6a2c16fb`, o que eles mediriam é o mesmo código, mas a saída é a de antes.

```text
$ python tools/looks/oracle.py --walk
oracle --walk: 0 problem(s) over 2 slot(s)

$ python tools/looks/ui_check.py
looks_ui: 18 of 18 negative control(s) red
```
- **Closed** — commit `6a2c16fb` (2026-09-23): feat(looks): measure the walk cycle and reproduce it from the file
  - Files (`git show --name-status 6a2c16fb`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/32-o-ciclo-da-caminhada.md`
    - `M docs/tasks/looks/33-a-janela-animada.md`
    - `M docs/tasks/looks/progresso.md`
    - `M tools/looks/anime.py`
    - `M tools/looks/controls.py`
    - `M tools/looks/layout.py`
    - `M tools/looks/oracle.py`
- **Reviewed** (2026-09-24) at `42c23a32`: CORR-LOOKS-092, CORR-LOOKS-093

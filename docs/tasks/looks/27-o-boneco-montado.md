---
id: LOOKS-TASK-27
title: "As peças no lugar — `scene.py` aplica a pose, e o painel da tela mostra o boneco montado"
type: implementação
category: render
phase: 9
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-26"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.4"
status: concluído
---

# LOOKS-TASK-27: O boneco montado

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1, §10.4 e §6 (e).
- **É o primeiro pedido do usuário:** o jogador **montado**, no painel da tela
  `LOOKS SET` da [`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md), não em prateleira.
- **A regra 3 continua:** a pose sai do núcleo (`anime.py` → `scene.py`); a
  `ui/` só desenha.
- **A prateleira não some.** É o jeito de olhar uma peça isolada, e o `S` a
  alterna; o que muda é o default.
- **O que a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md)
  mediu em 2026-09-18 e esta task tem de honrar:**
  - **a transformação por peça é absoluta** — a câmera composta com a volta da
    peça —, então montar não é compor hierarquia: é aplicar doze
    transformações prontas. O esqueleto do jogo **não é rígido** (cinco juntas
    se separam, o resto não), e supor uma cadeia anatômica é inventar;
  - **a tela desenha DUAS chuteiras, e as duas carregam matriz.** As seções 9 e
    10 são lidas as duas (watchpoint de leitura, uma corrida por seção, 2 e 2,
    com seção desenhada de controle). Este item dizia que só a 9 carregava
    matriz e que a segunda chuteira seria desenhada *"reaproveitando a rotação
    que já está no GTE"*; corrigido em 2026-09-18
    ([`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)). São doze cargas
    para doze seções desenhadas, e a carga da seção 10 é a única **sem quem a
    nomeie**: cada carga é nomeada pelo ponteiro da parada seguinte, e a
    primeira parada de uma passada não carrega ponteiro. Ela foi lida como uma
    raiz que não desenha nada, e quem a nomeia é o tornozelo — a junta rígida
    que já decidiu o atraso de desenho;
  - **`y` cresce para baixo** (cabeça em `y = −8`, pé mais baixo em `y = 60`),
    de acordo com o `UP = -1` que o `scene.py` já usa, e **nenhuma matriz tem
    determinante negativo** — o espelho das peças `b` está na geometria.

---

## Objetivo

O `scene.py` monta a figura aplicando a pose do quadro pedido a cada peça, e o
painel da tela `LOOKS SET` abre com o boneco montado.

---

## Critério de conclusão

- [x] `scene.from_image(..., frame=N)` devolve os pontos transformados pela
      pose do quadro N; `scene.shelf` continua disponível.
- [x] `ui/app.py --frame N`; sem ele, a prateleira de sempre — e o **painel da
      tela** abre montado, no quadro 0.
- [x] **Conferido contra o jogo, peça a peça:** a ordem relativa dos centros é
      asserção do `scene.py --check-image` (`scene.standing`), mais a simetria
      dos pares `a`/`b`.
- [x] Captura olhada no Log, nos dois slots.
- [x] `ui_check.py` julga a figura montada.
- [x] Controle negativo: quatro, e todos vermelhos.

---

## Log de Execução

**Executado em:** 2026-09-18, em duas sessões. A primeira parou num
bloqueio; a segunda o mediu e o desfez, e está registrada abaixo dela.

### Primeira sessão — PARCIAL

**Resumo do que foi aprendido**

**O `ANIME.BIN` guarda a pose inteira: ângulo E lugar.** A segunda palavra de
cada par, que a [`LOOKS-TASK-26`](/docs/tasks/looks/26-o-formato-do-anime-bin.md)
tinha deixado sem leitura, é a **posição** da peça: `x` nos bits 10:0 com
sinal, `z` nos 31:21 com sinal, e `y` em dez bits que o jogo remonta
**trocados** — os bits 11..15 viram os cinco altos e os 16..20 os cinco baixos
—, com o sinal nos dois bits de cima da **primeira** palavra. É o código em
`0x80011F0C..0x80011F50` lido de volta, e a conferência é contra as translações
que o próprio jogo entregou ao GTE: com o lugar do décimo segundo par
subtraído (a segunda chuteira, [`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md)) e a câmera
aplicada, **96 peças batem com erro máximo de 4 unidades** (79 delas com 1).

**E com esses lugares a figura não fica em pé.** Montada, a chuteira cai na
altura da coxa. Isso **não é erro de decodificação**, e é o que esta task deixa
medido: nas translações que o jogo carregou — não nas nossas —, a origem da
chuteira está a **192** unidades da raiz e a da canela a **394**. O jogo põe a
origem da chuteira acima da canela, e as duas seções de chuteira medem
`y −18..15` em torno da própria origem, então não é geometria pendurada. Falta
uma peça do quadro: o que reposiciona a chuteira não está no par dela.

**O que fica pronto** é a máquina inteira: `anime.position()`, `scene.pose()`,
`scene.from_image(..., frame=N)` aplicando matriz e lugar no núcleo (a `ui/`
não importa `anime`), `ui/app.py --frame N`, e a captura fora da tela.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/anime.py` — `position()`, o lugar em cada peça de `frame_angles`,
  e os self-checks do campo
- `tools/looks/scene.py` — `pose()`, `piece_names()`, `mirror_of()`,
  `place_points()`, `_posed()`, e o `frame` em `build`/`from_image`/`Builder`
- `tools/looks/ui/app.py` — `--frame N`, e a prateleira desligada quando há pose
- `tools/looks/ui_check.py` — a linha plantada seguiu a linha que mudou de forma
- `docs/tasks/looks/27-o-boneco-montado.md` — este Log

**Gates, na árvore de `d8ce2ee`**

```text
$ python tools/looks/selftest.py
  ..... 81 of 81 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/ui_check.py
looks_ui: 6 of 6 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/looks/anime.py --against-pose
  96 of 96 carry the angles the file holds at the pair the game read
  90 matrices of 96 are EXACT, 6 are blends the game made, and 0 are neither
anime --against-pose: 0 failure(s)

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**A captura da figura montada** (`ui/app.py --looks A-A1-A-A-A --frame 0
--screenshot`, fora da tela, 640x640): as doze peças aparecem **cada uma no seu
lugar e nenhuma no lugar certo** — cabeça embaixo, chuteira no ar à altura da
coxa. É a imagem do bloqueio, e é por ela que o critério da ordem dos centros
segue aberto.

**Problemas encontrados**

1. **A figura montada com o que o arquivo diz não fica em pé**, e a medição do
   jogo concorda com o arquivo — então o que falta é outra coisa, não a
   leitura. É o bloqueio da task, e está escrito no critério.
2. **A prateleira e a pose se somam se as duas ficarem ligadas.** O
   `ui/app.py` desliga a prateleira quando há `--frame`; sem isso cada peça é
   movida duas vezes e o resultado parece pose errada.
3. **Controle plantado do `ui_check` casava com uma linha que mudou de forma.**
   Quebrar a chamada do `from_image` em duas linhas para caber o `frame` fez o
   literal parar de casar: `matched 0 time(s)`, nem verde nem vermelho. É a
   mesma armadilha 53, noutro arquivo.

---

### Segunda sessão — o bloqueio desfeito

**O bloqueio não era o arquivo: era de quem é cada matriz.** A primeira sessão
mediu que a chuteira cai na altura da coxa **nas translações que o próprio jogo
carregou**, e concluiu que faltava alguma coisa fora do par. Faltava, e estava
na captura: o ponteiro de modelo que os registradores carregam na parada da
carga da matriz nomeia a peça que o jogo **acabou de desenhar** — a matriz
entra no GTE primeiro e os ponteiros da peça são armados depois. Com isso cada
peça ficava com a matriz da seguinte, e a chuteira herdava a do quadril. É
`oracle.DRAW_LAG`, e vale para qualquer instrumento que leia registrador numa
parada.

**O que desempata é medido, e de propósito não é o desenho** — decidir pelo
desenho seria usar o critério que se quer afirmar. Três medições, nenhuma
delas olhando a figura:

- **o tornozelo.** A origem da chuteira no referencial da própria canela tem
  dispersão **5,0** unidades no atraso 1 e **158,8** no atraso 0, sobre oito
  quadros espalhados, nos dois slots — e a **outra** canela, de controle, fica
  solta em 357,3 no mesmo atraso, que é o que impede "achei um atraso que
  gruda tudo". É o `oracle.py --pose-lag`, sem emulador, sobre as capturas em
  disco;
- **a simetria.** Corrigido o atraso, os pares `a`/`b` ficam à mesma altura —
  quadris a −224 e −217, ombros a −341 e −342 —, onde o outro atraso põe um
  cotovelo **acima do próprio ombro**;
- **a captura viva, refeita.** A hierarquia que o `--pose <SLOT> <N>` mede
  passa a nomear as juntas certas: `foot a` filha de `shin a` (dispersão 6,4,
  ganho 9,2x), `head` filha de `torso` (3,0, 14,6x), `forearm a` de
  `upper arm a` (16,4, 4,9x) e `forearm b` de `upper arm b` (17,1, 4,6x).
  Com o atraso lido na hora, o tornozelo não era junta nenhuma.

**E os lugares do próprio arquivo então empilham a figura**: cabeça em −420,
torso, braços, coxas, canelas e a chuteira em **0**, que é a chuteira contra a
qual todos os outros lugares são medidos — dizia "o chão em que a raiz se
apoia" até a [`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md). O
`scene.py --check-image` afirma essa ordem (`scene.standing`) e a simetria dos
pares; `SIDES_APART` saiu daqui como **45** e a mesma correção o levou a **55**,
porque o par mais aberto dos dezessete quadros é o das **chuteiras**, a 36,7, e
ele aparecia como 0 enquanto a segunda chuteira era posta por espelho.

**Um segundo defeito apareceu só no desenho, e é de referencial.** O
`part_for` já guarda `y * UP`, então os pontos de uma `Part` estão no
referencial **desenhado** e a pose está no do **arquivo**. Aplicada uma no
referencial da outra, a figura sai de cabeça para baixo com **cada peça
individualmente em pé** — cabeça embaixo, chuteira no ar. O `drawn_points`
desfaz o espelho na entrada e refaz na saída; `place_points` continua puro, no
referencial do arquivo, que é o que o `--check-image` usa.

**Arquivos criados/modificados** *(conferidos contra o commit)*

- `tools/looks/anime.py` — `PIECE_ORDER` girado uma casa, com as três medições
  que o decidem
- `tools/looks/oracle.py` — `DRAW_LAG`, o `_named_pass` que o aplica guardando
  `pointer_*`, `draw_lag()`, `_synthetic_pass()`, `load_poses()` e o
  `--pose-lag`
- `tools/looks/scene.py` — `standing()`, `CHAINS`, `SIDES_APART`,
  `drawn_points()`, o `frame` do `Builder`, a asserção no `--check-image` e os
  self-checks do juiz
- `tools/looks/ui_check.py` — `ink_box()`, `judge_posed()`, `measure_posed()`,
  `POSED_FRAME` e o quarto controle plantado
- `tools/looks/controls.py` — quatro controles novos
- `tools/looks/ui/app.py` — o painel da tela abre montado
- `docs/PLAN-LOOKS-PY.md` — o veredito da §10.4
- `docs/prompts/perfil-looks.md` — armadilha 59 e a linha do `--pose-lag`
- `CLAUDE.md` — a armadilha e o comando novo
- `docs/tasks/looks/progresso.md` e `docs/tasks/looks/27-o-boneco-montado.md`

**Gates, na árvore commitada**

```text
$ python tools/looks/selftest.py
  ..... 87 of 87 controls red
looks_selftest: 0 failure(s)

$ python tools/looks/cli.py check
cli check: 9 module(s), 9 ok, 0 skipped, 0 failed -- ok

$ python tools/looks/scene.py --check-image
      the figure, top down: head -386, torso -298, thigh a -162, shin a -53, foot a 13
      the figure, top down: upper arm a -301, forearm a -224
scene --check-image: ok

$ python tools/looks/oracle.py --pose-lag
     lag 1 wins by 11.2x (needs 5.0x)        [slot 1]
     lag 1 wins by 6.8x (needs 5.0x)         [slot 2]
oracle --pose-lag: 0 problem(s) over 2 slot(s)

$ python tools/looks/oracle.py --poses
oracle --pose: 0 problem(s) over 8 frame(s) and 2 slot(s)

$ python tools/looks/anime.py --against-pose
  96 of 96 carry the angles the file holds at the pair the game read
  90 matrices of 96 are EXACT, 6 are blends the game made, and 0 are neither
anime --against-pose: 0 failure(s)

$ python tools/looks/ui_check.py
  the figure posed on frame 0: ink 187x521 (2.79 tall for one wide, floor 1.8)
  against the shelf's 520x136 (0.26, ceiling 0.6)
looks_ui: 7 of 7 negative control(s) red, and the window drew every tuple it
was asked for and answered every key with what the game shows

$ python tools/check_tasks.py
check_tasks: 138 task(s), ok
```

**As capturas, olhadas** (fora da tela, sem janela na sessão do usuário)

- `ui/app.py --looks A-A1-A-A-A --frame 0 --screenshot`, 640x640: um jogador
  **em pé, a meio passo** — cabeça, tronco, os dois braços, as duas pernas e a
  chuteira no chão. É a figura que a primeira sessão não conseguiu montar.
- `ui/app.py --state 1 --screenshot` e `--state 2`, 1024x480: o painel da tela
  `LOOKS SET` abre com o boneco montado nos dois slots — o goleiro (`GK`) e o
  jogador de linha (`CB`), cada um com as duas chuteiras. O uniforme continua
  cinza, que é a task 30.

**Problemas encontrados**

1. **O ponteiro vivo nomeia a peça anterior** — a armadilha 59, e o bloqueio
   inteiro da primeira sessão. O sintoma é o pior possível: todo número dentro
   da faixa, cada peça isolada perfeita, e a figura não fica em pé.
2. **Pose e desenho em referenciais diferentes.** O `part_for` já espelha `y`;
   aplicar a pose do arquivo sobre esses pontos vira a figura de cabeça para
   baixo sem virar nenhuma peça, que não se parece com erro de sinal.
3. **Proporção de tinta é juiz fraco para ordem de peça.** A figura montada dá
   2,79 de altura por largura, a pilha 1,75 e a prateleira 0,26 — mas uma pose
   lida uma casa fora **também** desenha algo alto. O `looks_ui` diz isso na
   própria constante e desenha a **pilha** de propósito para ter um vermelho
   que não dependa da proporção; quem julga a ordem é o `scene --check-image`.
4. **A transcrição do gate saiu de uma corrida anterior à última edição.**
   Esta seção dizia `86 of 86` porque a corrida foi feita antes de o último
   controle entrar; a árvore commitada mede **87**, e quem conferiu foi a
   LOOKS-TASK-28 rodando a ferramenta sobre o commit. Número de gate se
   transcreve da corrida feita **na árvore que se commita**.
5. **Um sintético de quatro peças empata os atrasos.** No `_synthetic_pass`, com
   quatro peças o ciclo dá a volta e o atraso 2 devolve o mesmo par rígido ao
   contrário, com a mesma pontuação do atraso certo. Sete peças, na ordem em
   que o jogo desenha, separam.

---

### Depois da task — a segunda chuteira, medida

A revisão desta task abriu a
[`CORR-LOOKS-062`](/docs/tasks/looks/CORR-LOOKS-062.md) porque **o pé que o
Contexto mandava medir não tinha sido medido**: o `scene.pose()` o punha
espelhando o outro em `z`, e as duas pernas de uma passada não são reflexo uma
da outra — a chuteira `b` caía a 258 unidades da própria canela contra 18 da
outra, e a perna no ar terminava sem pé. Fechada em 2026-09-18, e o resultado
muda o que esta task afirma no Contexto: o par 12 de cada quadro do
`ANIME.BIN`, lido até então como uma **raiz** que não desenha nada, é a
**chuteira `b`** — a seção 10, cuja carga de matriz existe e é a única que
ponteiro nenhum nomeia. As duas asserções que deviam ter pego isso eram vazias:
o `standing()` só percorria a cadeia do lado `a`, e o par `a`/`b` era conferido
em `y`, que o espelho preserva.

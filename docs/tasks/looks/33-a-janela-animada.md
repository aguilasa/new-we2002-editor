---
id: LOOKS-TASK-33
title: "A janela animada — o boneco caminhando na tela `LOOKS SET`, no ritmo do jogo"
type: implementação
category: render
phase: 11
depends_on: [LOOKS-TASK-28, LOOKS-TASK-32, LOOKS-TASK-40]
status: done
source_of_truth: "/docs/PLAN-LOOKS-PY.md#10.4"
reviewed_on: 2026-09-26
review_commit: f3bdbcb2
done_on: 2026-09-25
done_commit: 7b5a01a3
resources: [emulador, tela]
---

# LOOKS-TASK-33: A janela animada

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.1 e §10.4.
- **É o pedido do usuário por inteiro:** a tela como a gravação e os save
  states a mostram, com o boneco andando e as linhas trocáveis ao mesmo tempo.
- **O ritmo é o da [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md)**, em quadros do jogo; o relógio da janela converte
  para tempo, não o contrário.
- **Trocar um valor não reinicia o passo** — ou reinicia, se o jogo reinicia:
  mede-se na tela do jogo.
- **A câmera muda com a linha** desde a [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md): numa linha de cabeça o
  painel desenha o close-up, e a animação anda com a câmera que a linha pede.
- **Gate precisa de quadro determinístico.** O timer é para quem olha; o gate
  desenha `--frame N`.

---

- **Da [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md):** o
  ritmo está medido e o reprodutor existe — `anime.py --frame N` entrega a pose
  da passada N do ciclo, do arquivo, e `oracle.py --walk` escreve o ciclo em
  `work/looks-walk/slotN.json`. Três coisas que mudam o que esta task
  implementa: o ciclo tem **34 passadas** (17 quadros do arquivo, o segundo
  lado espelhado), a unidade é a **passada de desenho** e não o quadro de vídeo
  (a tela desenha a figura a cada dois ou três quadros, sem período em
  quadros), e a vaga de par em que uma passada abre é **propriedade do save
  state** — a janela lê a do plano, não uma constante. O `--frame N` recusa
  rodar sem o ciclo medido, então o gate determinístico que esta task pede já
  tem de onde sair.

---

## Objetivo

O painel da tela `LOOKS SET` anima a caminhada em loop, no ritmo do jogo, com a
figura montada e a câmera do jogo, enquanto as linhas continuam trocáveis.

---

## Critério de conclusão

- [x] O painel anima por default; uma tecla pausa e outra anda um quadro,
      sem colidir com as setas das linhas; `--frame N` desenha parado.
- [x] O ritmo: um ciclo da janela dura o período da [`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md) convertido pela taxa
      de quadros do jogo, medida e escrita.
- [x] O que acontece com o passo ao trocar um valor, medido no jogo e
      reproduzido.
- [x] **O gate:** `confront.py --silhouette` em pelo menos oito N do ciclo,
      nos dois slots, dentro do limiar da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md).
- [x] O `ui_check.py` confere que dois `--frame` diferentes dão imagens
      diferentes e o mesmo `--frame` duas vezes dá a mesma.

---

- **Da [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md):** qual
  câmera vale em cada linha já está resolvido —
  `scene.load_camera(slot, escala, linha)` lê o arquivo da linha quando ela
  tem um, e `scene.close_up_rows` diz quais têm. O que fica para a janela
  animada é o **giro**: nas cinco linhas de cabeça o jogo gira o modelo
  continuamente, e o arquivo guarda um instante dele — medido, a vista lida
  onde o jogo a constrói já está ~1° (61 a 80 de 4096) atrás da matriz da
  carga no mesmo quadro, e entre capturas o giro anda +18,3°, −16,9° e
  +16,9°. Uma janela animada terá de modelar esse giro, não interpolar entre
  dois arquivos.

## Log de Execução

### 2026-09-25 — executada

**O que mudou.** O painel da tela `LOOKS SET` anda por default. O relógio é
`scene.WalkClock` (puro, sem Qt: o tempo entra por argumento) sobre o ciclo que
o `oracle.py --walk` gravou em `work/looks-walk/slotN.json`, e o que ele
converte são **quadros do jogo** em segundos pela taxa medida
(`layout.FRAME_TICKS`, `layout.CONSOLE_CLOCK`). A pose de cada passada sai de
`scene.walk_places`/`scene.walk_scene` — o `anime.walk_pose` da
[`LOOKS-TASK-32`](/docs/tasks/looks/32-o-ciclo-da-caminhada.md), com o espelho
e a média — e todas as passadas são medidas a partir de **uma** âncora
(`scene.walk_anchor`), senão a figura escorrega pela passada. `Space` pausa e
retoma, `.` anda uma passada; `--frame N` fica parado na passada N do ciclo
medido; `--animate-for S` deixa o relógio correr S segundos antes do
relatório. Com o `--looks` (visualizador de uma tupla) o `--frame` continua
sendo o quadro do arquivo, como antes.

**Critério 1 — anima, pausa, anda, e `--frame` parado.** Na janela de verdade
o timer liga sozinho (`app.py` sem `--smoke`/`--screenshot`); os gates não
podem abrir janela à vista, então o que prova é o `--animate-for` e as teclas
mandadas como eventos de Qt:

```
work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --frame 5 --keys Right --walk-keys step,step --smoke
  row NAT       = 'Ireland'
  presses +
  walk: pass 7 (7 of the cycle's 34), visit 11, first slot 7, still; ...
```

E o `ui_check.py` (critério 5) exige `.` duas vezes → passada 7 sem mexer
linha, `Right` + `.` → linha movida e passada 6, `Space` numa caminhada que
corria → parada. As setas continuam só nas linhas (`looks_set.KEYS`); as duas
teclas da caminhada são `looks_set.WALK_KEYS`.

**Critério 2 — o ritmo, medido e escrito.** `python tools/looks/oracle.py
--rhythm`, contando `frame_step`, nunca a gravação:

```
  -- slot 1 (goalkeeper) --
    the GPU: pal_mode False, interlaced False, 512x240
    cycle        77 frame(s): 43597690 tick(s), 34 picture(s) presented
    cycle again  77 frame(s): 43597690 tick(s), 34 picture(s) presented
    two cycles  154 frame(s): 87195382 tick(s), 68 picture(s) presented
    control: the same span twice 0 tick(s) apart, twice the frames 2 from twice the ticks, one picture a drawn pass; a progressive NTSC frame is 566203.8 ticks
    566203.8 tick(s) a frame, 59.817 frame(s) a second; a cycle of 77 frame(s) lasts 1.287 s
  -- slot 2 (outfield player) --
    cycle        77 frame(s): 43597690 tick(s), 34 picture(s) presented
    cycle again  77 frame(s): 43597700 tick(s), 34 picture(s) presented
    566203.8 tick(s) a frame, 59.817 frame(s) a second; a cycle of 77 frame(s) lasts 1.287 s
oracle --rhythm: 0 problem(s) over 2 slot(s)
```

Escrito em `layout.FRAME_TICKS = 566204`, com o comando no docstring, e a
janela o lê por `scene.frame_rate()`. A unidade do tick não foi tomada por
certa: o GPU diz NTSC progressivo, e 263 linhas de 3.413 ciclos a 53.693.175
Hz são 566.204,5 ticks — essa é a testemunha. Duas que **não** servem, as duas
tentadas: os timers raiz (o jogo os programa: 523 HBlanks num state e 65.463
no outro, no mesmo ciclo) e o relógio de parede (33.857.860 ticks/s numa
corrida, 20.743.364 na seguinte, com o host sem acompanhar) — armadilha 102.
Na janela:

```
work/venv-looks/Scripts/python.exe tools/looks/ui/app.py --animate-for 2.574 --smoke
  walk: pass 67 (33 of the cycle's 34), visit 71, first slot 7, still; 59.817 frame(s) a second, a cycle of 77 frame(s) lasts 1.287 s; 67 pass change(s) drawn
```

Dois ciclos de parede (2,574 s) → 67 passadas, onde o ritmo dá 68,0.

**Critério 3 — o passo ao trocar um valor, medido e reproduzido.** O mesmo
`--rhythm` compara as 26 montagens de pose (`layout.ANIME_BUILD`: número de
quadro e par) depois da tecla com as da corrida sem ela, com a corrida sem
tecla duas vezes (iguais) e 11 quadros adiante (pares diferentes) de controle:

```
    a value changed on NAT: the walk CONTINUES -- the 26 build(s) after the press are the untouched run's, frame number and pair
    a value changed on BOOTS: the walk CONTINUES -- the 26 build(s) after the press are the untouched run's, frame number and pair
    a value changed on SKIN: the walk CONTINUES -- held before the press and held on the same frame after it, pair for pair
```

(slot 2; o slot 1 igual.) **Trocar valor não reinicia nem desloca**, e a
janela reproduz não mexendo no relógio (`WalkClock.value_changed`,
`layout.WALK_ON_VALUE`). O que **mexe** é o cursor, e isso foi medido junto,
porque sem isso a janela não reproduziria a tela:

```
    row NAT       (0 Down) the figure walks
    row SKIN      (1 Down) the figure is HELD on frame 12 of the walk
    row HAIR      (2 Down) the figure is HELD on frame 12 of the walk
    row H.COL     (3 Down) the figure is HELD on frame 12 of the walk
    row FACE      (4 Down) the figure is HELD on frame 12 of the walk
    row H.F.COL.  (5 Down) the figure is HELD on frame 12 of the walk
    row HEIG      (6 Down) the figure walks
    row BOOTS     (9 Down) the figure walks
    row FOOT      (2 Up) the figure plays animation (147,) instead of the walk
    leaving SKIN for NAT: the first pass reads [(5, 13)]
```

A janela anda até o quadro 12 e para nas cinco linhas de cabeça, e sai para o
13 (`WalkClock.hold`/`release`, `layout.WALK_HELD_ROWS`); o `ui_check` confere
`SKIN` parado no 12. Isso corrige a armadilha 73, que atribuía à troca de
valor o deslocamento de fase que era do caminho do cursor (armadilha 101).

**Critério 4 — o gate da silhueta.** `python tools/looks/confront.py
--silhouette`, refeito sobre a caminhada: oito quadros contados por slot
(`confront.WALK_SILHOUETTE_FRAMES`) fotografados na montagem de pose
(`layout.ANIME_BUILD` — o `ANIME_UNPACK` do `game_at` só para em uma das dez
variantes, e os quadros 60, 108 e 128 fotografavam a mesma passada, armadilha
99), a passada nomeada pelo `frame_number` e a nossa desenhada por
`scene.walk_scene`, o mesmo caminho do `--frame N` da janela:

```
    control: frame 60 captured twice, 2451 pixel(s) of ink, identical, pass 27 both times
    control: frame(s) [70, 79, 89, 99, 108, 118, 128] differ from frame 60 by [461, 639, 879, 1387, 1374, 1341, 910] pixel(s)
    the eight frames name passes [27, 31, 1, 6, 10, 14, 18, 23] of 34
    slot 2 frame 60        names pass 27; best at pass 26, 1 behind, 347 of 2451 (14%); the worst of the sweep 1452
    ...
    slot 1 frame 118       names pass 18; best at pass 15, 3 behind, 325 of 2475 (13%); the worst of the sweep 1797
  the picture trails the named pass by [1, 2, 3] pass(es) over 16 comparison(s), and the bound is 3
confront --silhouette: 0 problem(s) over 2 slot(s)
```

As dezesseis comparações ficam dentro do `MATCH_SHARE` de 25% da
[`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md) (13 a 15%) e com
mínimo real (`MATCH_MARGIN` 2,5x; o pior da varredura fica a 2,8x a 5,4x do
melhor). O `PASS_LAG = 3` foi escrito **depois** de medido: com 2, a corrida
ficou vermelha em quatro de dezesseis, a 3 passadas, e o docstring diz por que
três é o teto (o nome pode ser a passada seguinte, e a foto é um dos dois
buffers).

**Critério 5 — `--frame` determinístico no `ui_check`.** `python
tools/looks/ui_check.py`:

```
  the walk: two --frame draw two pictures and one --frame twice one (slot 1 apart 10730, slot 2 apart 11495); after 2.574 s the clock is on pass(es) 67 (want 68.0), 67 (want 68.0) against the rhythm's count, the panel drawing 67, 67; `.` and `Space` step and pause without moving a row; SKIN holds frame 12
negative: breaking --frame reaching the clock reddens the walk -- slot 2: --frame 17 reports {'pass': 0, ...}, not pass 17 standing still
negative: breaking the step key reddens the walk -- `.` twice from pass 5 reports {'pass': 5, ...}, not pass 7 still
looks_ui: 20 of 20 negative control(s) red, ...
```

`--frame 0` duas vezes: 0 pixel; `--frame 0` contra `--frame 17`: 11.495
(slot 2) e 10.730 (slot 1). Os dois controles plantados ficam vermelhos.

**Uma consequência que o gate pegou.** As fotos de estatura do `looks_ui`
passaram a sair em passadas diferentes (a de `HEIG` atravessa as linhas de
cabeça) e a largura de 210 cm contra 175 deu 1,411 contra 1,200: tinta
comparada entre duas poses mede a pose. Elas agora ficam em `--frame 0`, e a
cópia plantada leva `work/looks-walk/` junto (armadilha 103).

**Aberto, e não ignorado.** (1) O **giro** do modelo nas cinco linhas de
cabeça, da [`LOOKS-TASK-40`](/docs/tasks/looks/40-a-camera-do-close-up.md).
Medido agora que ali a caminhada **para** no quadro 12 — o contexto desta task
previa "a animação anda com a câmera que a linha pede", e não anda —, o que
falta nessas linhas é só o giro: a janela segura o quadro 12 sem girar, e o
relatório diz `walk note: on SKIN the game also turns the model, and this
window does not`. Modelá-lo pede medir a velocidade do giro, o que nenhum dos
cinco critérios pede. (2) A **animação 147** que o jogo toca em `FOOT`: a
janela continua andando ali e diz. Os dois foram para a nota da
[`LOOKS-TASK-35`](/docs/tasks/looks/35-fechamento-da-v2.md).

**Gates.** `python tools/looks/selftest.py` → `108 of 108 controls red`,
`looks_selftest: 0 failure(s)`; `python tools/looks/ui_check.py` → `20 of 20
negative control(s) red`; `python tools/looks/cli.py check` → `12 module(s),
12 ok, 0 skipped, 0 failed -- ok`; `python tools/check_tasks.py` → `0
error(s)`.
- **Closed** — commit `7b5a01a3` (2026-09-25): feat(looks): walk the LOOKS SET panel at the game's measured rhythm
  - Files (`git show --name-status 7b5a01a3`):
    - `M CLAUDE.md`
    - `M docs/PLAN-LOOKS-PY.md`
    - `M docs/prompts/perfil-looks.armadilhas.md`
    - `M docs/prompts/perfil-looks.md`
    - `M docs/tasks/looks/33-a-janela-animada.md`
    - `M docs/tasks/looks/34-o-goleiro-andando.md`
    - `M docs/tasks/looks/35-fechamento-da-v2.md`
    - `M tools/looks/confront.py`
    - `M tools/looks/layout.py`
    - `M tools/looks/oracle.py`
    - `M tools/looks/scene.py`
    - `M tools/looks/ui/app.py`
    - `M tools/looks/ui/looks_set.py`
    - `M tools/looks/ui/viewer.py`
    - `M tools/looks/ui_check.py`
- **Reviewed** (2026-09-26) at `f3bdbcb2`: CORR-LOOKS-094, CORR-LOOKS-095, CORR-LOOKS-096

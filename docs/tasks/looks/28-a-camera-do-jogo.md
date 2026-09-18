---
id: LOOKS-TASK-28
title: "A câmera do jogo — projeção medida, e a silhueta como testemunha de forma"
type: implementação
category: oráculo
phase: 9
depends_on: ["LOOKS-TASK-27"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (m)"
status: pendente
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
      dentro do painel é o deslocamento de desenho da GPU, não o `OFX`/`OFY`.
- [ ] O painel desenha com eles, no tamanho do painel do jogo. **NÃO FEITO** —
      a silhueta se calcula no núcleo (`scene.silhouette`), e a janela ainda
      desenha com a câmera orbital da v1.
- [x] `confront.py --silhouette <SLOT>`: máscara nos dois quadros e a
      diferença impressa.
- [x] **Controles antes do teste:** o mesmo quadro contado duas vezes dá **0**
      pixel de diferença e um quadro diferente dá **1.300**.
- [ ] Três estilos de cabelo diferentes, dois slots. **NÃO FEITO, e a razão
      está no Log:** a ponte entre o quadro contado do emulador e o quadro do
      `ANIME.BIN` que a tela mostra ainda não fecha, e sem ela a silhueta se
      compara com uma pose que o jogo não estava desenhando.
- [ ] §6 (h) e §10.3 (m) com o veredito e a data — a (m) fica com o veredito
      **parcial**; a (h) segue aberta.

---

## Log de Execução

**Executado em:** 2026-09-18 — **PARCIAL**

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

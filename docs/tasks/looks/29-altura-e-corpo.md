---
id: LOOKS-TASK-29
title: "Incógnita (s) — `HEIG` e `BODY`: o que mudam no desenho, medido pela pose"
type: investigação
category: montagem
phase: 9
depends_on: ["LOOKS-TASK-22", "LOOKS-TASK-28"]
fonte_de_verdade: "/docs/PLAN-LOOKS-PY.md §10.3 (s)"
status: concluído
---

# LOOKS-TASK-29: Altura e corpo

## Contexto

- **Referência:** [`/docs/PLAN-LOOKS-PY.md`](/docs/PLAN-LOOKS-PY.md) §10.2 e §10.3 (s).
- **`BODY` não escreve em nenhum dos dois arquivos de modelo** (§6 (a)); se
  muda o desenho, muda na transformação — e a [`LOOKS-TASK-25`](/docs/tasks/looks/25-a-pose-de-referencia.md) já lê a transformação.
- **`HEIG` vai de 148 a 211** (`looks.py`), e a tela dos dois states mostra
  `175 cm`. Escala linear em altura é o palpite óbvio, e palpite óbvio já foi
  medido errado neste ciclo mais de uma vez.
- **As linhas já existem na tela** ([`LOOKS-TASK-22`](/docs/tasks/looks/22-a-tela-na-janela.md)); hoje elas trocam o texto e não o
  desenho.

---

## Objetivo

Medir o que `HEIG` e `BODY` fazem com as matrizes de cada peça, e aplicar no
desenho.

---

## Critério de conclusão

- [x] A pose do mesmo quadro capturada em pelo menos três alturas (as duas
      pontas e uma do meio) e em todos os valores de `BODY`, nos dois slots.
- [x] A regra medida — escala por eixo, por peça, ou outra coisa — com a
      diferença de inteiro para inteiro, e o que não muda dito.
- [x] O `scene.py` aplica a regra, e as matrizes reproduzem as capturadas
      exatamente.
- [x] Silhueta contra o emulador nas pontas de `HEIG` e em dois `BODY`,
      dentro do limiar da [`LOOKS-TASK-28`](/docs/tasks/looks/28-a-camera-do-jogo.md).
- [x] Controle negativo: altura aplicada no eixo errado fica vermelha.
- [x] §10.3 (s) com o veredito e a data.

---

## Log de Execução

- **Executado em:** 2026-09-18
- **Resumo do que foi feito:** `HEIG` e `BODY` não mexem em peça nem em pose:
  moram na **câmera**. O jogo escala as **colunas** da rotação da figura por
  um vetor `(x, y, z)` antes de multiplicar a vista — `y = (h<<12)/180` e
  `x = z = (h<<12)/(tabela[BODY]+10)`, `h = HEIG+148` —, então a altura mexe
  nos três eixos e o corpo só em largura e profundidade. Achado pelo código,
  não por ajuste: um watchpoint no vetor com `Right` em `BODY` parou no
  overlay `/SELECT8.BIN`, e o `stature.py` decodifica a regra das próprias
  instruções (o `/180` é a multiplicação mágica `0xB60B60B7`). Medido pelo
  `oracle.py --stature` nos dois slots: 56 alturas e 8 corpos, 0 fora da
  regra; 12 capturas de pose por slot, 12 de 12 peças exatas em todas. A
  janela recompõe a câmera quando uma das duas linhas muda, e o `looks_ui`
  julga isso pela tinta do painel.
- **Arquivos criados/modificados:** `tools/looks/stature.py` (novo: a regra
  lida do overlay, a cadeia inteira, self-check e `--check-image`);
  `tools/looks/layout.py` (`/SELECT8.BIN` com digest japonês, LBA, tamanho e
  família `CODE_FILES`; `SELECT8_BASE`, `STATURE_*`, `FIGURE_*`,
  `CAMERA_BUILD`); `tools/looks/oracle.py` (`capture_camera` lê a cadeia —
  `_camera_chain`, `_figure_now` —, e o `--stature`); `tools/looks/scene.py`
  (`load_camera` e `panel_camera` com escala, `figure_scale`,
  `Builder.scale`, o `Builder` lê o `/SELECT8.BIN`);
  `tools/looks/confront.py` (`--silhouette-stature`, `game_at` com
  `steps`, e as três silhuetas no uso); `tools/looks/ui/looks_set.py`
  (`camera_for`, `aim`, e o `press` que reaponta a câmera);
  `tools/looks/ui/app.py` (liga o `camera_for`); `tools/looks/ui_check.py`
  (`measure_stature`, `STATURE_BREAKS`, `plant_stature`);
  `tools/looks/controls.py` (`stature-height-on-the-wrong-axis`, e o
  `cli-check-forgets-a-module` reapontado para o fim novo da lista);
  `tools/looks/cli.py` e `tools/looks/selftest.py` (o `stature` nas duas
  listas); `docs/PLAN-LOOKS-PY.md` (§10.2 e §10.3 (s) com o veredito);
  `docs/prompts/perfil-looks.md` (armadilhas 72 a 76, três linhas de gate e
  duas atualizadas); `CLAUDE.md` (duas linhas de comando, o item de
  estatura, o estado do ciclo e "os dez `--check-image`").
- **Problemas encontrados:**
  1. **Esta task dizia "`HEIG` vai de 148 a 211".** O campo guarda isso; a
     tela anda de **155 a 210** (56 valores, `screen.json`). Medido nas 56
     que a tela alcança.
  2. **O palpite que a task temia teria errado dois eixos de três**: a altura
     escala também largura e profundidade.
  3. **Quadro contado igual não é quadro da caminhada igual depois de uma
     troca de valor** — capturas acolchoadas ao mesmo quadro vieram sem par —,
     e uma passada desenha dois quadros do `ANIME.BIN` cortados numa peça que
     muda com a fase: comparar pares peça a peça gastou 80 passadas. O
     critério certo é o conjunto de quadros (armadilha 73).
  4. **Passada com pares pode ser interpolação** (11 pares, 0 de 11 exatas),
     e **o quadro 0 do goleiro é mistura** mesmo na estatura do estado. O
     controle exige uma passada que o leitor de pose reproduz inteira e
     imprime as que recusa (armadilha 74) — o que fica para o leitor de pose,
     não para esta task.
  5. **Um controle plantado ficou verde, e saiu**: escalar linhas em vez de
     colunas dá os mesmos inteiros com `sx = sz` e giro só em `y`
     (armadilha 75).
  6. **`D TYPE` fica abaixo da resolução da silhueta**: a foto do jogo muda
     menos do que a nossa comparação já erra, e a figura na estatura do
     estado pontuou melhor. Os limiares da task 28 passam; a ordem só se
     afirma quando o jogo muda mais que o resíduo (armadilha 76).

**Gates, na árvore commitada:** `selftest` 0 falhas, 90 de 90 controles
vermelhos; `cli check` 10 de 10; `oracle.py --stature` 0 problemas (34 min 6 s);
`confront.py --silhouette-stature` 0 problemas (6 min 15 s); `looks_ui`
9 de 9 controles vermelhos, os dois de estatura inclusos; `check_tasks` 138 ok.

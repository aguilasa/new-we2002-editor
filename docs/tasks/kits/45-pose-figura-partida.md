---
id: KITS-TASK-45
---

# KITS-TASK-45 — Capturar a pose da figura de partida do MODEL.BIN

## Goal

Tirar do jogo, no slot 5, a pose de duas figuras de partida: um jogador de linha comum e um capitão. A pose é a matriz e a translação de cada peça do `MODEL.BIN`, na ordem de desenho que a KITS-TASK-44 mediu. Ela vira um arquivo que a aba 3D lê, com o confronto que prova que está certa: os vértices do disco, passados pelas matrizes capturadas, caem nos pontos de tela que o mesmo quadro entrega ao GPU.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`: uma opção nova, `--match-pose SLOT`. Ela captura, no mesmo quadro, as paradas de matriz (`--attach-matrix`) e a lista do GPU (`--attach`), e escolhe uma figura de cada ordem medida. A saída é `work/kits-pose/slotN-<cabeça>.json`, com a câmera do GTE (`H` e os deslocamentos de tela, como o `looks --camera`) e, por peça, seção, rotação e translação
  - `tools/kits/selftest.py`, para a parte pura
  - `docs/PLAN-KITS-PY.md`: §4.3
- Out: desenhar na janela (KITS-TASK-47); a manga curta (KITS-TASK-46)

## Done criteria

- [ ] `oracle.py --match-pose 5` colado no Log. Para cada figura escolhida, por peça: a seção, e o erro médio em pixels entre os vértices projetados pela matriz capturada e os pontos de tela das primitivas da mesma peça no mesmo quadro
- [ ] O erro máximo de peça e o limite que o afirma, os dois saídos da corrida; o limite fica abaixo do que a planta produz
- [ ] Um vermelho visto: a matriz dada à peça vizinha (sem o atraso de ponteiro) e a ferramenta acusando
- [ ] A §4.3 diz onde a pose mora e o comando que a refaz

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 por decisão do usuário: abrir o trabalho de figura de partida, para a braçadeira e a manga longa entrarem na aba 3D (KITS-TASK-40).

O que já se sabe: a partida carrega a matriz por peça em `layout.POSE_PIECE_MATRIX` (0x8001229C) e a matriz de uma parada é da peça que a parada seguinte nomeia (KITS-TASK-44). A ordem de um jogador de linha é `cabeça 2 95 96 97 98 7 9 11 8 10 12`, e a do capitão troca a 97 pela 93. A transformação por peça é absoluta, com a câmera já composta (o `looks`). Para separar a câmera da pose, o `looks` lê a carga `layout.POSE_MATRIX`.

Recursos: emulador e o slot 5 (`work/kits-states/`).

## Log de Execução

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

- [x] `oracle.py --match-pose 5` colado no Log. Para cada figura escolhida, por peça: a seção, e o erro médio em pixels entre os vértices projetados pela matriz capturada e os pontos de tela das primitivas da mesma peça no mesmo quadro
- [x] O erro máximo de peça e o limite que o afirma, os dois saídos da corrida; o limite fica abaixo do que a planta produz
- [x] Um vermelho visto: a matriz dada à peça vizinha (sem o atraso de ponteiro) e a ferramenta acusando
- [x] A §4.3 diz onde a pose mora e o comando que a refaz

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3).

Aberta em 2026-10-06 por decisão do usuário: abrir o trabalho de figura de partida, para a braçadeira e a manga longa entrarem na aba 3D (KITS-TASK-40).

O que já se sabe: a partida carrega a matriz por peça em `layout.POSE_PIECE_MATRIX` (0x8001229C) e a matriz de uma parada é da peça que a parada seguinte nomeia (KITS-TASK-44). A ordem de um jogador de linha é `cabeça 2 95 96 97 98 7 9 11 8 10 12`, e a do capitão troca a 97 pela 93. A transformação por peça é absoluta, com a câmera já composta (o `looks`). Para separar a câmera da pose, o `looks` lê a carga `layout.POSE_MATRIX`.

Recursos: emulador e o slot 5 (`work/kits-states/`).

## Log de Execução

### 2026-10-06 — execução

`--match-pose 5` captura, numa corrida só, as paradas de matriz por peça e os envios de lista ao GPU. As matrizes desde o envio anterior são provadas na lista do envio: vértice do disco pela matriz e pela projeção do GTE, canto a canto pelo texel. A pose de duas figuras vai para `work/kits-pose/`. Duas corridas ao vivo deram os mesmos números.

```
$ python tools/kits/oracle.py --match-pose 5        # exit 0
  capture kept at work/kits-oracle/pose-5.json (--frame-json reads it back)
  147 event(s): 140 matrix stop(s), 7 submit(s), 3 list(s) walked
  frame of list 0x80069134: 70 matrix stop(s) since the previous one, 6 player group(s); projection (H, OFX, OFY) (1376, 0.0, 0.0)
  captain, head 30, order 30 2 95 96 93 98 7 9 11 8 10 12:
    on player group 2; per piece, the mean distance in pixels between its projected corners and the frame's:
      section 30     0.96 px over 8 primitive(s)
      section 2      0.84 px over 12 primitive(s)
      section 95     0.91 px over 5 primitive(s)
      section 96     0.77 px over 7 primitive(s)
      section 93     0.73 px over 5 primitive(s)
      section 98     0.83 px over 7 primitive(s)
      section 7      0.85 px over 7 primitive(s)
      section 9      0.91 px over 5 primitive(s)
      section 11     0.97 px over 2 primitive(s)
      section 8      0.78 px over 6 primitive(s)
      section 10     0.62 px over 5 primitive(s)
      section 12     0.84 px over 2 primitive(s)
  outfield, head 24, order 24 2 95 96 97 98 7 9 11 8 10 12:
    on player group 1; per piece, the mean distance in pixels between its projected corners and the frame's:
      section 24     0.86 px over 9 primitive(s)
      section 2      0.96 px over 10 primitive(s)
      section 95     0.88 px over 4 primitive(s)
      section 96     1.01 px over 7 primitive(s)
      section 97     0.68 px over 4 primitive(s)
      section 98     0.91 px over 7 primitive(s)
      section 7      0.83 px over 7 primitive(s)
      section 9      0.78 px over 4 primitive(s)
      section 11     0.86 px over 3 primitive(s)
      section 8      0.78 px over 6 primitive(s)
      section 10     0.98 px over 5 primitive(s)
      section 12     0.83 px over 3 primitive(s)
  worst piece 1.01 px, limit 2.00
  wrote work/kits-pose/slot5-30.json
  wrote work/kits-pose/slot5-24.json
  ok    every piece of both figures lands within 2.00 px of its frame
```

Erro máximo de peça 1,01 px. O limite é 2,0 px (`oracle.POSE_LIMIT`), abaixo do melhor caso da planta:

```
$ python tools/kits/oracle.py --match-pose 5 --frame-json work/kits-oracle/pose-5.json --plant-pose   # exit 1
  PLANT  each matrix given to the piece named at its own stop (no lag)
  worst piece 264.70 px, limit 2.00
  FAIL  captain: section 10 is 4.72 px from the frame, over 2.00
  (e as outras 23 peças, de 5,82 a 264,70 px)
```

O texel de cada canto segue `Primitive.indices`, a ordem gravada, e não `corners`. Pareado por `corners`, o erro vai a 2 a 4 px por peça (primeira corrida, worst 3.96 px).

Selftest: cinco checagens novas. O vermelho plantado foi o pareamento por `corners` em `piece_error`, com `FAIL  oracle --match-pose: a piece's own matrix lands within the limit, paired by texel  14.015451651872144 over 1`. O código foi restaurado: `kits_selftest: 0 failure(s)`.
- **Closed** — commit `d1c64a3` (2026-10-06): feat(kits): capture the match figure's pose and prove it on its own frame
  - Files (`git show --name-status d1c64a3`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/45-pose-figura-partida.md`
    - `M docs/tasks/kits/47-figura-partida-aba-3d.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`

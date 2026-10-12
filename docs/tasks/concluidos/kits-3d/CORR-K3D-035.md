---
id: CORR-K3D-035
---

# CORR-K3D-035 — Deslocamento e ordem do vizinho no G8 saem de sonda, e a ordem está errada

Origin: [K3D-TASK-19](/docs/tasks/concluidos/kits-3d/19-medir-capitao-linha-replay.md)

## Problem

Os itens 4 e 7 do G8, da [K3D-TASK-19](/docs/tasks/concluidos/kits-3d/19-medir-capitao-linha-replay.md), usam números que nenhuma opção do `oracle.py` imprime: "slot
9: a 4,0 px do eixo" para o vizinho brasileiro, e "a de um jogador sem faixa
`46 2 3 5 4 6 …`". Essa ordem também está errada: a única figura de linha sem braçadeira do
slot 9 nas capturas abre com a cabeça 34 (`34 2 3 5 4 6 …`). O `--replay --focus` só imprime
deslocamento e ordem da figura acompanhada. A regra da fase 7 diz que todo número do G8 sai
de opção do oráculo, não de sonda; os valores só se reproduziram com um script avulso que lê
a captura fora do git.

## Evidência

```text
$ grep -n '4,0 px\|46 2 3 5 4 6' docs/KITS-AJUSTES-3D.md
1371:   seção **4** (a ordem do Bokšić é `46 2 3 5 90 6 …`, a de um jogador sem faixa `46 2 3 5 4 6 …`), dois
1389:   9: a 4,0 px do eixo, 6802 de profundidade; slot 10: a 3907, à frente dele), e os quads do vizinho
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --focus 3 --frame-json work/kits-oracle/replay-9-3.json | grep -c '4.0 px'
0
```

A sonda do revisor sobre `work/kits-oracle/replay-9-3.json` dá, para o mesmo quadro,
`(6802, 4.0, [34, 2, 3, 5, 4, 6, 7, 9, 11, 8, 10, 12])` no vizinho e
`(4694, 0.6, [46, 2, 3, 5, 90, 6, ...])` no Bokšić.

## Root cause

Hipótese: o vizinho foi inspecionado com uma sonda descartável, e a cabeça dele foi escrita
como a 46 do jogador acompanhado.

## Fix

No `run_replay` de `tools/kits/oracle.py`, quando houver `focus_k`, imprimir toda figura do
quadro com profundidade, deslocamento do eixo e ordem (a sonda de cima feita linha de
opção). Colar essa linha no G8 e corrigir a ordem para `34 2 3 5 4 6 …`.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --focus 3 --frame-json work/kits-oracle/replay-9-3.json | grep -q '4.0 px' && ! grep -q '46 2 3 5 4 6' docs/KITS-AJUSTES-3D.md
```

Hoje falha nas duas metades; depois, passa.

## Log de Execução

### 2026-10-12 — toda figura do quadro impressa pelo `--replay --focus`

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED** na HEAD `d348951`. O `grep`
achou as linhas 1371 (`46 2 3 5 4 6`) e 1389 (`4,0 px`), e o `--replay 9 --focus 3` contou `0` linhas
com `4.0 px`.

Conserto: com `--focus`, o `run_replay` de `tools/kits/oracle.py` imprime `every figure of the last
frame, nearest the axis first:`, uma linha por figura com profundidade, px fora do eixo e seções a
partir da cabeça, e marca a seguida. É a sonda do revisor, agora como saída da opção.

Medido, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin` e `--frame-json work/kits-oracle/replay-<slot>-<K>.json`:
- `--replay 9 --focus 3`: `depth  6802,   4.0 px off the axis: 34 2 3 5 4 6 7 9 11 8 10 12`;
- `--replay 10 --focus 3`: `depth  3907,  63.9 px off the axis: 34 2 95 96 97 98 7 9 11 8 10 12`;
- `--replay 10 --focus 2`: `depth  3886, 119.9 px off the axis: 34 2 95 96 97 98 …`.

O vizinho sem faixa do slot 9 tem cabeça **34**, não 46.

G8:
- as três saídas foram recoladas;
- o bloco da planta continua só com as linhas `PLANT` e `FAIL`, como era;
- o item 4 diz `34 2 3 5 4 6 …` do vizinho brasileiro e remete à linha impressa;
- o item 7 cita as linhas `every figure of the last frame` para os 4,0 px e os 3907.

Verificação: o comando da CORR (`… | grep -q '4.0 px' && ! grep -q '46 2 3 5 4 6' docs/KITS-AJUSTES-3D.md`)
sai 0.

Gates:
- `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits`:
  `100% tests passed, 0 tests failed out of 4`, nenhum *skipped*.
- `python3 tools/kits/controls.py`: `controls: 53 of 53 red`.
- **Closed** — commit `3bfae0c7` (2026-10-12): fix(kits): print every figure of the frame in --replay --focus and correct the neighbour's order
  - Files (`git show --name-status 3bfae0c7`):
    - `M docs/KITS-AJUSTES-3D.md`
    - `M docs/tasks/kits-3d/CORR-K3D-035.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M tools/kits/oracle.py`

---
id: CORR-K3D-023
---

# CORR-K3D-023 — --replay não imprime o limite de inatividade contra o qual compara

Origin: [K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md)

## Problem

O critério da [K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md) pede que cada captura rode menos quadros que o limite medido por
`--replay-idle`, "e a saída diz os dois números". O `--replay` imprime os quadros gastos
(9 de frente; 599 e 45 no giro), mas nunca o 390 contra o qual eles são comparados. Esse
limite vem calado do dicionário fixo `REPLAY_IDLE` dentro do `replay_judge`, então quem lê
a saída do `--replay` não vê a comparação; o 390 só aparece no G8 pela corrida separada do
`--replay-idle`.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json | grep -c "390\|idle"
0
$ grep -n "REPLAY_IDLE = " tools/kits/oracle.py
3023:REPLAY_IDLE = {9: 390, 10: 390}
```

## Root cause

Hipótese: o `run_replay` passa `REPLAY_IDLE.get(slot)` ao relatório para o juiz, mas as
linhas impressas o deixam de fora — esquecido quando a linha do giro foi escrita.

## Fix

No `run_replay` de `tools/kits/oracle.py`, imprimir o limite de inatividade ao lado de
`front_frames` e `back_frames` nas linhas "front:" e "turn:", e recolar as duas saídas no
bloco do G8 em `docs/KITS-AJUSTES-3D.md`.

## Arquivos a criar ou modificar

- tools/kits/oracle.py
- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json | grep -E "idle 390"
```

Hoje não casa; depois, casa nas linhas de frente e de giro.

## Log de Execução

- 2026-10-10 — triagem inline: **REPRODUCED**. `--replay 9 --frame-json …` não trazia nem "390"
  nem "idle" (`grep -c` → 0).
- `oracle.py`: o `run_replay` imprime `idle N` na linha `front:` e na linha `turn:`, o mesmo valor
  que o juiz recebe. Os dois blocos do G8 recolados da HEAD: só essas quatro linhas mudaram.
- Verificação: `grep -E "idle 390"` casa nas linhas `front:` e `turn:` dos slots 9 e 10.

---
id: CORR-KITS-051
---

# CORR-KITS-051 — Colar a vantagem da Escócia da ferramenta, não de notas arredondadas

Origin: [KITS-TASK-28](/docs/tasks/kits/28-confronto-3.md)

## Problem

O Log da KITS-TASK-28 diz que as vantagens medidas são "0,341 e 0,410", e a mensagem do commit 165495d diz "0.341 and 0.410". O 0,341 é 0,770 − 0,429 feito à mão sobre as notas arredondadas; a própria ferramenta dá 0,342 para essa diferença, e a corrida positiva não imprime vantagem nenhuma — então 0,341 nunca saiu da ferramenta.

## Evidência

```text
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score --negative
red   the TEX_01 players score our TEX_13 0.429, TEX_01 0.770: a lead of -0.342, under 0.05
red   the TEX_13 players score our TEX_01 0.349, TEX_13 0.759: a lead of -0.410, under 0.05
$ grep -n "0,341" docs/tasks/kits/28-confronto-3.md
69:0,341 e 0,410.
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score | grep -c "lead"
0
```

## Root cause

Hipótese: a vantagem foi subtraída à mão das notas impressas com três casas, porque o `--score` positivo não imprime a vantagem de cada time.

## Fix

Em `score()` de `tools/kits/confront.py`, imprimir a vantagem de cada time também na corrida positiva, e colar esse valor no Log da KITS-TASK-28 (0,342, se for o que ela imprimir).

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `docs/tasks/kits/28-confronto-3.md`

## Verificação

`WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score | grep -c "lead"` dá 0 hoje; 2 depois do conserto, e o valor no Log é igual ao impresso (`grep -c "0,341" docs/tasks/kits/28-confronto-3.md` dá 0).

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `e8e7a3f`:

```
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score | grep -c lead
0
$ grep -n "0,341" docs/tasks/kits/28-confronto-3.md
69:0,341 e 0,410.
```

Conserto: `leads()` em `tools/kits/confront.py` calcula a vantagem de cada time, e o `score_verdict` passa a usá-la; a corrida positiva imprime as duas. O Log da KITS-TASK-28 troca o "0,341 e 0,410" pelo comando e a saída dele. A mensagem do commit 165495d continua dizendo 0.341 — commit não se reescreve.

```
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score
  frame: work/kits-oracle/match-3/screen.png
  players on the pitch         ours TEX_01 set 1  ours TEX_13 set 2
  TEX_01 Scotland, first kit  0.770 (33.0 % kept)  0.429 (10.8 % kept)
  TEX_13 Denmark, second kit  0.349 (14.9 % kept)  0.759 (29.8 % kept)
  TEX_01 players: our TEX_01 leads our TEX_13 by 0.342
  TEX_13 players: our TEX_13 leads our TEX_01 by 0.410
confront 3: 2 of 2 team(s) score their own kit 0.05 over the other's
$ WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin python3 tools/kits/confront.py --score --negative | tail -1
confront 3 --negative: the swapped renders give 2 failure(s) of 2 -- the control holds
$ grep -c "0,341" docs/tasks/kits/28-confronto-3.md
0
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```
- **Closed** — commit `122b921` (2026-10-04): feat(kits): confront.py --score prints each team's lead
  - Files (`git show --name-status 122b921`):
    - `M docs/tasks/kits/28-confronto-3.md`
    - `M docs/tasks/kits/CORR-KITS-051.md`
    - `M tools/kits/confront.py`

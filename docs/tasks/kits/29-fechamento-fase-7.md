---
id: KITS-TASK-29
---

# KITS-TASK-29 — Fechamento da fase 7 — o emulador julga o 3D

## Goal

A fase 7 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [x] Comandos das tasks 27 e 28 refeitos na HEAD, saídas coladas
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### 2026-10-04

Na HEAD `4b47eaf`, com `WE2002_LOOKS_IMAGE=roms/japanese-shift-jis.bin`.

**Task 27** — `python3 tools/kits/oracle.py --slot 3 --cue $PWD/work/we2002-english.cue --out <scratchpad>/f7 --lines --flags --expect 01=1 --expect 13=2`, exit 0:

```
  control: two dumps a frame apart give the same 8 match(es)
  TEX_01 uniform  at (576,256): set 1 differs in 4746 of 8192 halfwords, set 2 in 5050 -- set 1 nearer
  TEX_01 sleeves  at (576,384): set 1 differs in 2995 of 8192 halfwords, set 2 in 4211 -- set 1 nearer
  TEX_13 uniform  at (640,256): set 1 differs in 7198 of 8192 halfwords, set 2 in 2640 -- set 2 nearer
  TEX_13 sleeves  at (640,384): set 1 differs in 7693 of 8192 halfwords, set 2 in 4093 -- set 2 nearer
  TEX_01 uniform  set 1 at (576,256):  80 of 128 lines not flat,  12 of them exact
  TEX_13 uniform  set 2 at (640,256):  80 of 128 lines not flat,  80 of them exact
  ok    TEX_01 in set 1, TEX_13 in set 2
```

O `screen.png` dessa corrida tem o sha256 que o confronto 3 fixou
(`ee1bfba6e7dc…`). Controle com os conjuntos trocados, sobre o dump desta
corrida (`--png <scratchpad>/f7/vram-0.png --expect 01=2 --expect 13=1`), exit 1:

```
  FAIL  TEX_13: exact player palette of set 2, expected set 1
  FAIL  TEX_13: the uniform page is nearer to set 2, expected set 1
  FAIL  TEX_13: the sleeves page is nearer to set 2, expected set 1
```

**Task 28** — `python3 tools/kits/confront.py --score --game <scratchpad>/f7/screen.png`, exit 0:

```
  TEX_01 players: our TEX_01 leads our TEX_13 by 0.342
  TEX_13 players: our TEX_13 leads our TEX_01 by 0.410
confront 3: 2 of 2 team(s) score their own kit 0.05 over the other's
```

`--score --negative`, exit 0 (o controle reprova os dois times):

```
confront 3 --negative: the swapped renders give 2 failure(s) of 2 -- the control holds
```

**`rite check --cycle kits`**: `check: 0 error(s), 0 warning(s) in 1 cycle(s)`.
- **Closed** — commit `6ed380b` (2026-10-04): docs(kits): phase 7 re-measured at HEAD
  - Files (`git show --name-status 6ed380b`):
    - `M docs/tasks/kits/29-fechamento-fase-7.md`

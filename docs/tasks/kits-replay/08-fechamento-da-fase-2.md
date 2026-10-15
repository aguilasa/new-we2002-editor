---
id: KRP-TASK-08
---

# KRP-TASK-08 — Fechamento da fase 2

## Goal

A fase 2 (a linha de comando, a captura e o confronto) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 2 do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - nenhum: só reroda e corrige escrituração
- Out:
  - código novo

## Done criteria

- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo
- [ ] `replay.py figure --json` reproduz a linha `ok` do oracle nas cinco capturas de perto, de novo na HEAD
- [ ] `kits_replay` visto 77 sem captura
- [ ] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

- **pending** (2026-10-15): phase 2 still has open fixes CORR-KRP-010..014 from the KRP-TASK-06 review; the closing task runs after /rite:fix-all, by the user's choice

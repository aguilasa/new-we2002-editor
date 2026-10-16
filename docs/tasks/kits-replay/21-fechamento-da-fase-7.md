---
id: KRP-TASK-21
---

# KRP-TASK-21 — Fechamento da fase 7

## Goal

A fase 7 (a câmera replay) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 7 do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md`: o que a fase mudou, escrito no plano (o resto só reroda e corrige escrituração)
- Out:
  - código novo

## Done criteria

- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo
- [ ] o `confront --tab` das cinco capturas com a câmera nova está no plano ou no Log da 20
- [ ] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

---
id: KRP-TASK-23
---

# KRP-TASK-23 — Fechamento da fase 3a

## Goal

A fase 3a (os controles da cabeça na aba) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 3a do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - `docs/PLAN-KITS-REPLAY.md`: o que a fase mudou, escrito no §3.3 (o resto só reroda e corrige escrituração)
- Out:
  - código novo

## Done criteria

- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`
- [ ] uma captura da aba com o painel à vista, nas duas línguas, citada no Log
- [ ] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

---
id: K3D-TASK-03
---

# K3D-TASK-03 — Fechamento da fase 1

## Goal

A fase 1 conferida na HEAD.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [ ] as verificações da Fase 1 do perfil, cada uma com o comando e a saída colados no Log
- [ ] `rite check --cycle kits-3d`: 0 erros
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

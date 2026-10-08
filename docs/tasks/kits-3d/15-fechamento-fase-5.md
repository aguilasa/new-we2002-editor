---
id: K3D-TASK-15
---

# K3D-TASK-15 — Fechamento da fase 5

## Goal

A fase 5 (G6) conferida na HEAD, com capturas para o usuário conferir de olho o que motivou a fase.

## Arquivos a criar ou modificar

- In:
  - nenhum de código — só conferência
- Out: —

## Done criteria

- [ ] as verificações da Fase 5 do perfil, cada uma com o comando e a saída colados no Log
- [ ] capturas do TEX_00 de costas (yaw 0) e de lado (yaw 90 e 270), jogador e goleiro, enviadas ao usuário, com os caminhos no Log
- [ ] `rite check --cycle kits-3d`: 0 erros
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin`: `100% tests passed, 0 tests failed out of 4`, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`

## Notes

## Log de Execução

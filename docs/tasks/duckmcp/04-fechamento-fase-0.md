---
id: DMCP-TASK-04
---

# DMCP-TASK-04 — Fechamento da Fase 0 — o esqueleto

## Goal

A Fase 0 (o esqueleto) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 0 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 0 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/duckmcp/controls.py` sai 0
- [ ] `ctest --test-dir build -R duckmcp_selftest` passa
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

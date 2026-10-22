---
id: DMCP-TASK-24
---

# DMCP-TASK-24 — Fechamento da Fase 6 — a migração do looks

## Goal

A Fase 6 (a migração do looks) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 6 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 6 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/looks/selftest.py` sai 0
- [ ] `python3 tools/duckmcp/audit.py` sem sítio do `looks`
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

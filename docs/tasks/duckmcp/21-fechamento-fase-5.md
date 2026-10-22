---
id: DMCP-TASK-21
---

# DMCP-TASK-21 — Fechamento da Fase 5 — a migração do pes2

## Goal

A Fase 5 (a migração do pes2) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 5 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 5 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/pes2/selftest.py` sai 0
- [ ] `python3 tools/duckmcp/audit.py` sem sítio do `pes2`
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

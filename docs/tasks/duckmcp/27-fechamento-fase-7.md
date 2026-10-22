---
id: DMCP-TASK-27
---

# DMCP-TASK-27 — Fechamento da Fase 7 — a migração do kits

## Goal

A Fase 7 (a migração do kits) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 7 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 7 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/kits/selftest.py` sai 0
- [ ] `python3 tools/duckmcp/audit.py` sem sítio do `kits`
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

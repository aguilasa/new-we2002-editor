---
id: DMCP-TASK-18
---

# DMCP-TASK-18 — Fechamento da Fase 4 — a depuração

## Goal

A Fase 4 (a depuração) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 4 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 4 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/duckmcp/controls.py` sai 0
- [ ] `python3 tools/duckmcp/audit.py` colado
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

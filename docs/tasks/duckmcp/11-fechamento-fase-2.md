---
id: DMCP-TASK-11
---

# DMCP-TASK-11 — Fechamento da Fase 2 — o lançador

## Goal

A Fase 2 (o lançador) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 2 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 2 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `ctest --test-dir build -R duckmcp_live` com `DUCKSTATION_TEST_IMAGE` e `DISPLAY=:98 XAUTHORITY=` no comando: `Passed`
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

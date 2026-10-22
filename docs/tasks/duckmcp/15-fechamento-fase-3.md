---
id: DMCP-TASK-15
---

# DMCP-TASK-15 — Fechamento da Fase 3 — as primitivas

## Goal

A Fase 3 (as primitivas) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 3 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 3 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `duckmcp_live` estendido com `read_ram` (2 MiB), `dump_vram` (1024×512) e `game()` passa, saída colada no Log
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

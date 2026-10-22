---
id: DMCP-TASK-07
---

# DMCP-TASK-07 — Fechamento da Fase 1 — o transporte

## Goal

A Fase 1 (o transporte) está fechada: todas as tasks dela concluídas e revistas, os gates refeitos na HEAD de fechamento e as verificações da Fase 1 do perfil rodadas uma a uma.

## Arquivos a criar ou modificar

- In:
  - só o Log desta task
- Out:
  - código novo

## Done criteria

- [ ] `rite status --cycle duckmcp` mostra as tasks da Fase 1 `done` e revistas, com nenhuma CORR aberta delas
- [ ] `python3 tools/duckmcp/selftest.py` sai 0, e a última linha diz quantos checks rodaram
- [ ] `python3 tools/pes2/selftest.py` sai 0
- [ ] `ctest --test-dir build -R tasks` passa

## Notes

## Log de Execução

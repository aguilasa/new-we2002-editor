---
id: KITS-TASK-31
---

# KITS-TASK-31 — O combobox passa a listar times, na ordem do jogo

## Goal

`TeamEntry.tag` preenchido; com a tabela, o combobox lista times; tag sem time continua acessível.

## Arquivos a criar ou modificar

- `tools/kits/core/teams.py`
- `tools/kits/ui/*.py`

## Done criteria

- [ ] `cli.py teams` mostra `tag` preenchida em N linhas (N da task 30)
- [ ] Captura da janela com o combobox de times
- [ ] `kits_ui` verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.2).

Da KITS-TASK-30: a tabela é `tools/kits/core/generated/team_kits.py` (`TEAM_KIT`, um tag por índice de time 0 a 94; `ML_DEFAULT_KIT` = `A4`; `UNREACHED_KITS` = `95`..`A3`, que nenhum time veste e continuam acessíveis por tag). O N é **95**, dito por `python tools/kits/gen_tables.py --report`. `core/teams.py` a lê de `generated/`, como já lê `team_names.py`.

## Log de Execução

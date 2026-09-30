---
id: KITS-TASK-31
title: "O combobox passa a listar times, na ordem do jogo"
type: "implementação"
phase: 8
depends_on: [KITS-TASK-30, KITS-TASK-20]
source_of_truth: "/docs/PLAN-KITS-PY.md#4.2"
files: ["tools/kits/core/teams.py", "tools/kits/ui/*.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: ["tela"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
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

## Log de Execução

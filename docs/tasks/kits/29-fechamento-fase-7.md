---
id: KITS-TASK-29
title: "Fechamento da fase 7 — o emulador julga o 3D"
type: closing
phase: 7
depends_on: [KITS-TASK-27, KITS-TASK-28]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: ["emulador", "save-states"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-29 — Fechamento da fase 7 — o emulador julga o 3D

## Goal

A fase 7 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] Comandos das tasks 27 e 28 refeitos na HEAD, saídas coladas
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

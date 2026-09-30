---
id: KITS-TASK-23
title: "Fechamento da fase 5 — as duas mudanças no `looks`"
type: closing
phase: 5
depends_on: [KITS-TASK-21, KITS-TASK-22]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: ["emulador", "save-states"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-23 — Fechamento da fase 5 — as duas mudanças no `looks`

## Goal

A fase 5 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `ctest -R looks` na HEAD, os quatro pelo nome
- [ ] `ctest -R kits` na HEAD
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

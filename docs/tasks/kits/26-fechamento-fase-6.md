---
id: KITS-TASK-26
title: "Fechamento da fase 6 — o 3D"
type: closing
phase: 6
depends_on: [KITS-TASK-24, KITS-TASK-25]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: ["tela"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-26 — Fechamento da fase 6 — o 3D

## Goal

A fase 6 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `ctest -R kits` na HEAD
- [ ] `controls.py` na HEAD
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

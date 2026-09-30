---
id: KITS-TASK-17
title: "Fechamento da fase 3 — plano e zonas, sem janela"
type: closing
phase: 3
depends_on: [KITS-TASK-15, KITS-TASK-16]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-17 — Fechamento da fase 3 — plano e zonas, sem janela

## Goal

A fase 3 conferida na HEAD, e ainda sem arquivo em `tools/kits/ui/`.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `ctest -R kits` e `controls.py` na HEAD, saídas coladas
- [ ] `git ls-files tools/kits/ui` vazio
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

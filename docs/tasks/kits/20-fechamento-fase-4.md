---
id: KITS-TASK-20
title: "Fechamento da fase 4 — a janela mínima"
type: closing
phase: 4
depends_on: [KITS-TASK-18, KITS-TASK-19]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: ["tela"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-20 — Fechamento da fase 4 — a janela mínima

## Goal

A fase 4 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `ctest -R kits` na HEAD com os nomes dos alvos
- [ ] Captura refeita na HEAD
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

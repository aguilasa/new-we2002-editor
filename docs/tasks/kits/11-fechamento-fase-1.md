---
id: KITS-TASK-11
title: "Fechamento da fase 1 — núcleo, lado TEX"
type: closing
phase: 1
depends_on: [KITS-TASK-06, KITS-TASK-07, KITS-TASK-08, KITS-TASK-09, KITS-TASK-10]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-11 — Fechamento da fase 1 — núcleo, lado TEX

## Goal

A fase 1 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `ctest -R kits` na HEAD, saída colada com os nomes dos alvos
- [ ] `python tools/kits/controls.py` na HEAD, todos vermelhos
- [ ] Confrontos 1 e 2 refeitos, números colados
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

---
id: KITS-TASK-14
title: "Fechamento da fase 2 — núcleo, lado ROM"
type: closing
phase: 2
depends_on: [KITS-TASK-12, KITS-TASK-13]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-14 — Fechamento da fase 2 — núcleo, lado ROM

## Goal

A fase 2 conferida na HEAD.

## Arquivos a criar ou modificar

- nenhum de código — só conferência

## Done criteria

- [ ] `gen_tables.py --check` e `ctest -R kits` na HEAD, saídas coladas
- [ ] `cli.py teams` nas duas imagens de `roms/`, contagens coladas
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

---
id: KITS-TASK-05
title: "Fechamento da fase 0 — medições no disco"
type: closing
phase: 0
depends_on: [KITS-TASK-01, KITS-TASK-02, KITS-TASK-03, KITS-TASK-04]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: ["docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-05 — Fechamento da fase 0 — medições no disco

## Goal

A fase 0 conferida de ponta a ponta na HEAD: as três medições e o levantamento reproduzem os números que o plano cita.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Os subcomandos das tasks 01–04 rodados de novo na HEAD, saídas coladas; nenhum número do plano diverge
- [ ] As §4.3, §4.4 e §4.6 têm veredito ou o que ficou aberto dito, com o comando
- [ ] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

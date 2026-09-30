---
id: KITS-TASK-04
title: "Levantar as UV que o boneco amostra no bitmap de 256×128"
type: "investigação"
phase: 0
depends_on: [KITS-TASK-03]
source_of_truth: "/docs/PLAN-KITS-PY.md#4.6"
files: ["tools/kits/core/survey.py", "tools/kits/cli.py", "docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-04 — Levantar as UV que o boneco amostra no bitmap de 256×128

## Goal

A entrada da §4.6: o conjunto de retângulos do bitmap de trabalho 256×128 que as primitivas das duas figuras amostram, por comando versionado, pronto para a fase 3 cruzar com o mapa de zonas.

## Arquivos a criar ou modificar

- `tools/kits/core/survey.py`
- `tools/kits/cli.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Subcomando versionado imprime, por figura, os retângulos UV amostrados no espaço 256×128; a saída (ou o digest dela, se longa) está no Log
- [ ] A §4.6 do plano diz onde a saída mora e quantas primitivas caem fora do 256×128 (número da ferramenta)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.6).

## Log de Execução

---
id: KITS-TASK-28
title: "Confronto 3: `confront.py --score` com um uniforme que não é o `A4`"
type: "verificação"
phase: 7
depends_on: [KITS-TASK-27]
source_of_truth: "/docs/PLAN-KITS-PY.md#5"
files: ["tools/kits/confront.py", "docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: ["emulador", "save-states"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-28 — Confronto 3: `confront.py --score` com um uniforme que não é o `A4`

## Goal

O confronto por histograma de cor do `looks` refeito com o time da §4.1, titular e suplente, contra o quadro do emulador.

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Os escores de titular e suplente colados, com o limiar que o `looks` usa
- [ ] Controle: nosso titular contra o quadro do suplente do jogo reprova

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

## Log de Execução

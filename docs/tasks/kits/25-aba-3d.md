---
id: KITS-TASK-25
title: "Aba 3D: titular/suplente, jogador/goleiro, giro livre"
type: "implementação"
phase: 6
depends_on: [KITS-TASK-24]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.2"
files: ["tools/kits/ui/*.py", "tools/kits/ui_check.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: ["tela"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-25 — Aba 3D: titular/suplente, jogador/goleiro, giro livre

## Goal

A aba 3D desenha a figura pela fachada; sem geometria fica desligada com a frase do motivo, e o 2D funciona igual.

## Arquivos a criar ou modificar

- `tools/kits/ui/*.py`
- `tools/kits/ui_check.py`

## Done criteria

- [ ] Captura das quatro combinações de uma tag do §1.1 que difere: titular ≠ suplente (digests no Log)
- [ ] Sem `WE2002_LOOKS_IMAGE`, a aba aparece desligada com a frase (captura)
- [ ] `kits_ui` estendido às quatro combinações, verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.2).

## Log de Execução

---
id: KITS-TASK-33
title: "Aba Diagnóstico: a lista de `kit.problems`"
type: "implementação"
phase: 9
depends_on: [KITS-TASK-20]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.4"
files: ["tools/kits/ui/*.py", "tools/kits/ui_check.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: ["tela"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-33 — Aba Diagnóstico: a lista de `kit.problems`

## Goal

A aba lista os problemas da guarda de forma registro a registro; TEX recusado aparece com o motivo, não desenhado torto.

## Arquivos a criar ou modificar

- `tools/kits/ui/*.py`
- `tools/kits/ui_check.py`

## Done criteria

- [ ] Captura com o `TEX_13` e o `TEX_48` da European Deluxe mostrando cada um o seu motivo
- [ ] Captura com um TEX sadio: lista vazia
- [ ] `kits_ui` estendido, verde

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.4). O plano liga a fase 9 à fase 1; a aba precisa da janela, então depende da 20. Decisão de 2026-09-30.

## Log de Execução

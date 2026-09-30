---
id: KITS-TASK-21
title: "`scene.Builder(kit=...)` no `looks`, com `TEX_A4` de default"
type: "implementação"
phase: 5
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#2"
files: ["tools/looks/scene.py", "tools/looks/selftest.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-21 — `scene.Builder(kit=...)` no `looks`, com `TEX_A4` de default

## Goal

O `scene.Builder` aceita qualquer das 105 tags; sem o argumento desenha como hoje.

## Arquivos a criar ou modificar

- `tools/looks/scene.py`
- `tools/looks/selftest.py`

## Done criteria

- [ ] `ctest -R looks` com as quatro (`looks_selftest`, `looks_image`, `looks_ui`, `looks_live`) verdes, ou *skipped* só pela falta declarada, **antes e depois** — as duas transcrições no Log
- [ ] Um self-check do `looks` constrói com uma tag que não é a `A4` e confere que o banco de textura usado é o dela
- [ ] Controle: o default trocado numa cópia derruba o self-check que garante `TEX_A4`

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#2). Toca `tools/looks/`, projeto arquivado (§6). Mudança aditiva.

## Log de Execução

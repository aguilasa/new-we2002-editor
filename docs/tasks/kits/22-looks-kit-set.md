---
id: KITS-TASK-22
title: "Parâmetro `kit_set`: o banco do TEX entrega o 2º par de registros"
type: "implementação"
phase: 5
depends_on: [KITS-TASK-21]
source_of_truth: "/docs/PLAN-KITS-PY.md#2"
files: ["tools/looks/scene.py", "tools/looks/assembly.py", "tools/looks/atlas.py", "tools/looks/texture.py", "tools/looks/selftest.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-22 — Parâmetro `kit_set`: o banco do TEX entrega o 2º par de registros

## Goal

`kit_set=1` (titular, default) e `kit_set=2` (suplente) no `Builder` e no caminho de tupla; a escolha é de ordem de busca no banco e o resto do `looks` não muda.

## Arquivos a criar ou modificar

- `tools/looks/scene.py`
- `tools/looks/assembly.py`
- `tools/looks/atlas.py`
- `tools/looks/texture.py`
- `tools/looks/selftest.py`

## Done criteria

- [ ] `ctest -R looks` com as quatro (`looks_selftest`, `looks_image`, `looks_ui`, `looks_live`) verdes, ou *skipped* só pela falta declarada, **antes e depois** — as duas transcrições no Log
- [ ] Controle do §5: o suplente do `TEX_A4` dá o mesmo quadro que o titular; de uma tag do §1.1 que difere, um quadro diferente — digests no Log
- [ ] Controle: forçar `kit_set` ignorado numa cópia derruba o self-check

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#2). Depende da 21 porque as duas tocam `scene.py`.

## Log de Execução

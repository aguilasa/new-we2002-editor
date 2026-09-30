---
id: KITS-TASK-08
title: "Criar selftest, controles negativos e os alvos `kits_selftest` e `kits_image`"
type: infra
phase: 1
depends_on: [KITS-TASK-07]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.5"
files: ["tools/kits/selftest.py", "tools/kits/controls.py", "tests/CMakeLists.txt"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-08 — Criar selftest, controles negativos e os alvos `kits_selftest` e `kits_image`

## Goal

O gate do ciclo existe: `kits_selftest` roda sem nada e nunca pula; `kits_image` precisa de uma ROM e sai 77 sem ela; os controles negativos são plantados por comando e cada um tem o vermelho visto.

## Arquivos a criar ou modificar

- `tools/kits/selftest.py`
- `tools/kits/controls.py`
- `tests/CMakeLists.txt`

## Done criteria

- [ ] `ctest -R kits` lista `kits_selftest` e `kits_image` pelo nome (saída colada — `No tests were found` não conta)
- [ ] `kits_selftest` roda os self-checks do `looks` que o `kits` importa (§6, Acoplamento)
- [ ] `python tools/kits/controls.py` planta cada controle numa cópia e exige o vermelho; a última linha diz quantos são
- [ ] Sem `WE2002_LOOKS_IMAGE`, `kits_image` sai *skipped* (77); com ela, passa

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.5).

## Log de Execução

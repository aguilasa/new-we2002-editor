---
id: KITS-TASK-03
title: "Contar primitivas de cada figura por retângulo do TEX"
type: "investigação"
phase: 0
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#4.3"
files: ["tools/kits/core/survey.py", "tools/kits/cli.py", "docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-03 — Contar primitivas de cada figura por retângulo do TEX

## Goal

A primeira metade da §4.3 medida no disco: para a figura 0 (linha) e a 1 (goleiro), quantas primitivas amostram cada um dos retângulos do TEX (uniforme, mangas, bandeira, árbitro), lido pela geometria do `looks`.

## Arquivos a criar ou modificar

- `tools/kits/core/survey.py`
- `tools/kits/cli.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] Subcomando versionado imprime a contagem por figura e por retângulo; colada no Log
- [ ] A §4.3 do plano registra se a imagem de mangas (576,384) é amostrada por alguma primitiva do `EDT_MOD.BIN` — sim ou não, com o número
- [ ] Controle: a contagem total por figura bate com o número de primitivas que o `tools/looks` já desenha (comando e número no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.3). Nada de remapear UV à mão (§4.3). Se a manga longa for outra geometria, esta task só registra isso.

## Log de Execução

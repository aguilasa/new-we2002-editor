---
id: KITS-TASK-30
title: "§4.2: qual TEX cada time veste"
type: "investigação"
phase: 8
depends_on: [KITS-TASK-14]
source_of_truth: "/docs/PLAN-KITS-PY.md#4.2"
files: ["tools/kits/core/generated/", "tools/kits/gen_tables.py", "docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: ["emulador"]        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-30 — §4.2: qual TEX cada time veste

## Goal

A tabela índice de time → tag, medida (editor do Obocaman em `we-team-editor/`, e/ou o emulador pelo `--kit`), versionada como dado com proveniência.

## Arquivos a criar ou modificar

- `tools/kits/core/generated/`
- `tools/kits/gen_tables.py`
- `docs/PLAN-KITS-PY.md`

## Done criteria

- [ ] A tabela cobre N times, número da ferramenta, e cada linha diz de onde veio
- [ ] Pelo menos três linhas conferidas no emulador, comando e saída no Log
- [ ] A §4.2 do plano tem veredito

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.2). Nada do `we-team-editor.exe` entra no git; só o dado medido.

## Log de Execução

---
id: KITS-TASK-02
title: "Medir o que são os retângulos (608,256) e (704,256)"
type: "investigação"
phase: 0
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#4.4"
files: ["tools/kits/cli.py", "tools/kits/core/survey.py", "docs/PLAN-KITS-PY.md", "docs/PLAN-LOOKS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-02 — Medir o que são os retângulos (608,256) e (704,256)

## Goal

A §4.4 fechada: qual arquivo do disco declara registro em (608,256) e em (704,256), lido por comando versionado, e a linha do PLAN-LOOKS §1.7 corrigida se estiver velha.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/core/survey.py`
- `docs/PLAN-KITS-PY.md`
- `docs/PLAN-LOOKS-PY.md`

## Done criteria

- [ ] Um subcomando da CLI lista, para os dois retângulos, todo arquivo do disco japonês que declara registro ali; a saída está colada no Log
- [ ] A §4.4 do plano tem veredito e o comando que o sustenta
- [ ] Se o PLAN-LOOKS §1.7 estava errado, a linha foi corrigida no mesmo commit; se estava certo, o Log diz por quê

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#4.4).

## Log de Execução

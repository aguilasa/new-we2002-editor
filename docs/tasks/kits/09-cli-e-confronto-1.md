---
id: KITS-TASK-09
title: "`cli.py info/export` e o confronto 1: `tex.py` contra `bin_archive.py export`"
type: "verificação"
phase: 1
depends_on: [KITS-TASK-08]
source_of_truth: "/docs/PLAN-KITS-PY.md#5"
files: ["tools/kits/cli.py", "tools/kits/selftest.py", "tools/kits/core/api.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-09 — `cli.py info/export` e o confronto 1: `tex.py` contra `bin_archive.py export`

## Goal

A CLI faz `info` e `export` só pela fachada, e os dois decodificadores concordam imagem por imagem e paleta por paleta nas 105 tags.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/selftest.py`
- `tools/kits/core/api.py`

## Done criteria

- [ ] `grep -nE '^(from|import) ' tools/kits/cli.py` só mostra `core.api` e a biblioteca padrão
- [ ] Confronto 1 roda como opção versionada e imprime 105 de 105 tags iguais (6 imagens e 5 paletas cada); colado no Log
- [ ] Controle: um pixel alterado no lado do `tex.py` derruba o confronto (vermelho no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

## Log de Execução

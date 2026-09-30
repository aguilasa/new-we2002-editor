---
id: KITS-TASK-01
title: "Promover o levantamento do §1.1 a ferramenta versionada"
type: ferramenta
phase: 0
depends_on: []
source_of_truth: "/docs/PLAN-KITS-PY.md#1.1"
files: ["tools/kits/core/__init__.py", "tools/kits/core/survey.py", "tools/kits/cli.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-01 — Promover o levantamento do §1.1 a ferramenta versionada

## Goal

O levantamento dos 105 TEX que produziu a tabela do §1.1 passa a ser uma função do núcleo (`core/survey.py`, que devolve dados) e um subcomando `cli.py survey` que os imprime. A tabela do §1.1 deixa de depender de um script descartável.

## Arquivos a criar ou modificar

- `tools/kits/core/__init__.py`
- `tools/kits/core/survey.py`
- `tools/kits/cli.py`

## Done criteria

- [ ] `python tools/kits/cli.py survey <trilha japonesa>` imprime, colado no Log: forma única nos 105 (6 imagens + 5 CLUTs), titular = suplente só no `TEX_A4`, 103 com imagens diferentes, 1 só com paletas diferentes, 1 com paleta de jogador = goleiro, árbitro idêntico nos 105, tamanho de 25.948 a 34.200 bytes
- [ ] Número do Log que divergir do §1.1 corrige o §1.1 no mesmo commit, com a saída da ferramenta como prova
- [ ] `core/survey.py` não tem `print`, `sys.exit` nem import de Qt: `grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py` vazio

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#1.1). O plano diz `tex.py --survey`; o §3.1 proíbe `print` no núcleo. Decisão de 2026-09-30 no `/rite:plan-to-tasks`: a medição fica no núcleo, a impressão na CLI.

## Log de Execução

---
id: KITS-TASK-15
title: "`flat.py`: imagem + paleta em RGBA, o bitmap de trabalho e a grade 16×16"
type: "implementação"
phase: 3
depends_on: [KITS-TASK-11]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.1"
files: ["tools/kits/core/flat.py", "tools/kits/core/api.py", "tools/kits/cli.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-15 — `flat.py`: imagem + paleta em RGBA, o bitmap de trabalho e a grade 16×16

## Goal

`kit.flat`, `kit.work_bitmap(kit_set, figure)` e `kit.palette_grid` existem; índice 0 é transparente; `cli.py export` grava PNG.

## Arquivos a criar ou modificar

- `tools/kits/core/flat.py`
- `tools/kits/core/api.py`
- `tools/kits/cli.py`

## Done criteria

- [ ] Os 105 TEX × as combinações de imagem e paleta que o jogo usa saem sem índice fora da paleta e sem imagem de uma cor só (contagem da ferramenta)
- [ ] `kit.work_bitmap` tem 256×128 e o `export` do titular e do suplente de uma tag do §1.1 que difere dá PNGs diferentes; do `TEX_A4`, iguais (digests no Log)
- [ ] Sem Qt e sem Pillow no núcleo: `grep -rn 'PySide\|PIL' tools/kits/core/` vazio

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.1). PNG escrito sem Pillow no núcleo (`zlib` da stdlib) ou pela CLI; a escolha fica no Log.

## Log de Execução

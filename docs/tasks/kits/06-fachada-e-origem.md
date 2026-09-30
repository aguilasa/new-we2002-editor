---
id: KITS-TASK-06
title: "Criar a fachada `api.py` e o `source.py` que reconhece ROM ou TEX pelo conteúdo"
type: "implementação"
phase: 1
depends_on: [KITS-TASK-05]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.1"
files: ["tools/kits/core/api.py", "tools/kits/core/source.py", "tools/kits/core/errors.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-06 — Criar a fachada `api.py` e o `source.py` que reconhece ROM ou TEX pelo conteúdo

## Goal

`api.open_source(path)` devolve uma origem com `kind` `"rom"` ou `"tex"`, decidido pelo conteúdo; erros são exceções tipadas cuja mensagem é a frase que a interface mostra.

## Arquivos a criar ou modificar

- `tools/kits/core/api.py`
- `tools/kits/core/source.py`
- `tools/kits/core/errors.py`

## Done criteria

- [ ] Um `.bin` do disco japonês renomeado para `.tex` abre como `rom`, e um TEX extraído renomeado para `.bin` abre como `tex` — comando e saída no Log
- [ ] Arquivo que não é nenhum dos dois é recusado com exceção tipada e frase — comando e saída no Log
- [ ] `grep -rnE 'print\(|sys\.exit|PySide|^[A-Z_]+ *= *\[\]' tools/kits/core/` vazio (sem saída, sem Qt, sem estado global mutável)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.1).

## Log de Execução

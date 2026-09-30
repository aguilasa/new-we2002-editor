---
id: KITS-TASK-24
title: "`figure.py` e `api.figure`: a única ponte com o `looks`"
type: "implementação"
phase: 6
depends_on: [KITS-TASK-20, KITS-TASK-23]
source_of_truth: "/docs/PLAN-KITS-PY.md#3.1"
files: ["tools/kits/core/figure.py", "tools/kits/core/api.py"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-24 — `figure.py` e `api.figure`: a única ponte com o `looks`

## Goal

`api.figure(kit, kit_set, figure, geometry_path, frame=None)` pede a cena ao `scene` do `looks`; com um TEX avulso, a geometria vem de `WE2002_LOOKS_IMAGE`, e sem ela a exceção tem a frase do motivo.

## Arquivos a criar ou modificar

- `tools/kits/core/figure.py`
- `tools/kits/core/api.py`

## Done criteria

- [ ] `grep -rn 'looks' tools/kits/core/ --include=*.py -l` só lista `figure.py`
- [ ] Sem `WE2002_LOOKS_IMAGE`, `api.figure` levanta a exceção tipada com a frase (saída colada)
- [ ] Controle do §5: trocar as paletas 486 e 488 troca jogador e goleiro na cena (vermelho no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#3.1).

## Log de Execução

---
id: KITS-TASK-10
title: "Confronto 2: os pares `_BND.bin`/`_BND.tim` do Superpack"
type: "verificação"
phase: 1
depends_on: [KITS-TASK-08]
source_of_truth: "/docs/PLAN-KITS-PY.md#5"
files: ["tools/kits/confront.py", "tools/kits/selftest.py", "NOTICE.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
done_on: null
done_commit: null
reviewed_on: null
review_commit: null
---

# KITS-TASK-10 — Confronto 2: os pares `_BND.bin`/`_BND.tim` do Superpack

## Goal

A descompressão do `.bin` de cada par do `Banderas 3D/` devolve os pixels do `.tim` byte a byte — oráculo que não passou pelo nosso código. Lê de `WE2002_KITS_CORPUS`; nada do Superpack entra no git.

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `tools/kits/selftest.py`

## Done criteria

- [ ] Com `WE2002_KITS_CORPUS`, o confronto imprime quantos pares foram lidos e quantos batem; a contagem é a da ferramenta, colada no Log
- [ ] Sem a variável, sai 77 com a frase do que faltou
- [ ] Controle: um `.tim` com um pixel trocado (cópia no scratchpad) reprova
- [ ] `git status` não mostra arquivo do Superpack
- [ ] A seção do `kits` no `NOTICE.md` credita, no mesmo commit, os autores que aparecem **dentro** do `Banderas 3D/`: quem produziu os `.bin` (WEZip — Lagarto, com a descompressão de WarlockDC e Jordinator) e o autor de cada bandeira onde o arquivo o nomear; quem não for nomeado fica dito como não identificado. O Superpack não é citado

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

## Log de Execução

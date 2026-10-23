---
id: CORR-DMCP-023
---

# CORR-DMCP-023 — Declarar duckmcp/selftest.py nas tasks de migração que a PENDING amarra

Origin: [DMCP-TASK-17](/docs/tasks/duckmcp/17-regra-b.md)

## Problem

Por causa do check de entrada velha, toda task que remove um sítio listado tem de encolher a `PENDING`
do `tools/duckmcp/selftest.py` no mesmo commit. As DMCP-TASK-23, 25 e 26 têm entradas na `PENDING` mas
não declaram `tools/duckmcp/selftest.py`; as 19, 20, 22 e 30 declaram. Cada uma das três ficará
vermelha no próprio gate até editar um arquivo não declarado — o padrão "escopo não declarado" que o
`CLAUDE.md` registra.

## Evidência

```text
$ for t in 23 25 26; do sh "$RITE_HOME/bin/rite" context DMCP-TASK-$t --json | python3 -c "import json,sys;d=json.load(sys.stdin)['item'];print(d['id'],'tools/duckmcp/selftest.py' in d['files'])"; done
DMCP-TASK-23 False
DMCP-TASK-25 False
DMCP-TASK-26 False
$ cd tools/duckmcp && python3 -c "import selftest;print(sorted({e[0] for e in selftest.PENDING}))"
['DMCP-TASK-19', 'DMCP-TASK-20', 'DMCP-TASK-22', 'DMCP-TASK-23', 'DMCP-TASK-25', 'DMCP-TASK-26', 'DMCP-TASK-30']
```

## Root cause

Esta task fez toda migração editar o `selftest.py`, mas não atualizou as declarações das tasks a
jusante; o único rastro é uma nota no próprio Log.

## Fix

`rite set DMCP-TASK-23 --files …`, e o mesmo para 25 e 26 (depois da CORR-DMCP-021 a 26 pode sair),
acrescentando `tools/duckmcp/selftest.py`, com uma linha em "Arquivos a criar ou modificar" de cada
task.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/23-looks-breakpoints.md`
- `docs/tasks/duckmcp/25-kits-oracle.md`
- `docs/tasks/duckmcp/26-kits-controles.md`

## Verificação

O laço da Evidência hoje imprime `False` três vezes; depois tem de imprimir `True` para toda task que
tenha entrada na `PENDING`.

## Log de Execução

2026-10-23 — reproduzido: o laço da Evidência imprimia `False` para as DMCP-TASK-23, 25 e 26.

Conserto: `rite set … --files` acrescentou `tools/duckmcp/selftest.py` aos arquivos das três,
preservando os que já estavam. Cada uma ganhou uma linha em "Arquivos a criar ou modificar" dizendo
por quê. Com a CORR-DMCP-021 a 26 continua dona de uma entrada (`kits/selftest.py`) e por isso fica.

Verificação, sobre toda task com entrada no `PENDING`:

```text
$ for t in 19 20 22 23 25 26 30; do sh "$RITE_HOME/bin/rite" context DMCP-TASK-$t --json | python3 -c "…print(d['id'],'tools/duckmcp/selftest.py' in d['files'])"; done
DMCP-TASK-23 True
DMCP-TASK-25 True
DMCP-TASK-26 True
DMCP-TASK-19 True
DMCP-TASK-20 True
DMCP-TASK-22 True
DMCP-TASK-30 True
```
- **Closed** — commit `c39e4c74` (2026-10-23): docs(duckmcp): declare duckmcp/selftest.py in the migrations PENDING binds
  - Files (`git show --name-status c39e4c74`):
    - `M docs/tasks/duckmcp/23-looks-breakpoints.md`
    - `M docs/tasks/duckmcp/25-kits-oracle.md`
    - `M docs/tasks/duckmcp/26-kits-controles.md`
    - `M docs/tasks/duckmcp/CORR-DMCP-023.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M docs/tasks/duckmcp/progress.json`

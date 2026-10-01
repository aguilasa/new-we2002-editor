---
id: CORR-KITS-012
title: "Declare cli.py and the open subcommand in the task's scope"
origin: KITS-TASK-06
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-012 — Declare cli.py and the open subcommand in the task's scope

Origin: [KITS-TASK-06](/docs/tasks/kits/06-fachada-e-origem.md)

## Problem

O commit da KITS-TASK-06 muda `tools/kits/cli.py`, acrescentando o subcomando `open`, mas o `cli.py` não está na lista `files:` da task. O §3.1 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) lista os subcomandos do CLI como `info`, `teams`, `export` e `check`, sem `open`. O Log explica o porquê (evidência por comando versionado em vez de sonda descartável), mas nem o frontmatter — que os lotes usam para a matriz de conflito, e a KITS-TASK-09 também edita o `cli.py` — nem o plano registram isso.

## Evidência

```text
$ git show --stat 51c8a6a0
tools/kits/cli.py | 28 ++++
$ grep -n 'tools/kits/cli.py' docs/tasks/kits/06-fachada-e-origem.md | grep files:
(vazio, saída 1)
$ grep -n 'info.*teams.*export.*check' docs/PLAN-KITS-PY.md
(`tools/kits/cli.py`: `info`, `teams`, `export`, `check`)
```

## Root cause

O subcomando entrou durante a task para manter a evidência num comando versionado, e o escopo e o plano não foram atualizados junto.

## Fix

Acrescentar `tools/kits/cli.py` ao `files:` da task e listar `open` entre os subcomandos do CLI no §3.1 do plano — ou deixar o registro para a KITS-TASK-09, que é dona do `cli.py`.

## Arquivos a criar ou modificar

- `docs/tasks/kits/06-fachada-e-origem.md`
- `docs/PLAN-KITS-PY.md`

## Verificação

```text
$ grep -n 'tools/kits/cli.py' docs/tasks/kits/06-fachada-e-origem.md | grep files:
```

Hoje não sai nada; depois tem de imprimir uma linha.

## Log de Execução

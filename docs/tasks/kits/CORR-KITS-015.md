---
id: CORR-KITS-015
title: Update NOTICE.md kits rows to name tex.py as the CARP importer
origin: KITS-TASK-07
severity: low
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-015 — Update NOTICE.md kits rows to name tex.py as the CARP importer

Origin: [KITS-TASK-07](/docs/tasks/kits/07-tex-e-guarda-de-forma.md)

## Problem

A linha de linhagem do kits no `NOTICE.md` diz que `lzss`/`bin_archive` chegam pelo `tools/kits/core/survey.py`, "which ... imports to read every kit container". Desde a KITS-TASK-07 quem lê todo contêiner de kit é o `tex.py`: ele importa `bin_archive` e `lzss` e põe `tools/pes2` no `sys.path`, e o `survey.py` passou a depender dele para isso. O crédito existe, mas a rota descrita está velha. A regra do repositório é que a linha do NOTICE muda no mesmo commit que traz o código.

## Evidência

```text
$ grep -n "tools/kits/core/survey.py\` imports to read every kit" NOTICE.md
220:| **Maximiliano Ducoli (CARP)** | ... Through `tools/pes2/lzss.py` and `tools/pes2/bin_archive.py`, which `tools/kits/core/survey.py` imports to read every kit container. ...
$ grep -n "^import bin_archive\|^import lzss" tools/kits/core/tex.py
38:import bin_archive  # noqa: E402  (tools/pes2, after the path insert)
39:import lzss  # noqa: E402
$ grep -c "tools/kits/core/tex.py" NOTICE.md
0
```

## Root cause

O `NOTICE.md` não estava na lista `files:` da task, então o commit não o tocou.

## Fix

Na linha 220 do `NOTICE.md`, nomear `tools/kits/core/tex.py` (a guarda de forma) como quem importa, ao lado do `survey.py`.

## Arquivos a criar ou modificar

- `NOTICE.md`

## Verificação

```text
$ grep -c "tools/kits/core/tex.py" NOTICE.md
```

Hoje dá 0; depois, pelo menos 1.

## Log de Execução

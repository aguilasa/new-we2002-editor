---
id: CORR-KITS-075
---

# CORR-KITS-075 — Declarar a task 40 nos arquivos, ou tirar a nota do commit

Origin: [KITS-TASK-43](/docs/tasks/kits/43-medir-encaixe-mangas.md)

## Problem

O commit da80383 altera `docs/tasks/kits/40-checkboxes-numero-bracadeira.md`, que não está entre os arquivos declarados da KITS-TASK-43 (`oracle.py`, `selftest.py`, `PLAN-KITS-PY.md`). O Log o menciona ("A nota foi para a KITS-TASK-40"), então é rastreável, mas fica fora do escopo declarado.

## Evidência

```text
$ git show --stat da80383 | grep 40-
 docs/tasks/kits/40-checkboxes-numero-bracadeira.md |   2 +
$ sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/43-medir-encaixe-mangas.md | grep -c 40-checkboxes
0
```

## Root cause

A nota de passagem do critério 4 foi escrita direto na task bloqueada sem atualizar o escopo.

## Fix

Acrescentar o caminho à seção "Arquivos a criar ou modificar" de `docs/tasks/kits/43-medir-encaixe-mangas.md` (e, se for o caso, aos arquivos da task pelo `rite set`).

## Arquivos a criar ou modificar

- `docs/tasks/kits/43-medir-encaixe-mangas.md`

## Verificação

```sh
sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/43-medir-encaixe-mangas.md | grep -c 40-checkboxes
```

Dá 0 hoje; 1 depois. (A grep sobre o arquivo inteiro já casa a linha 109, do Log, e não serve de verificação.)

## Log de Execução

Reproduzido em 2026-10-06 sobre `c88cd00`: `git show --stat da80383` lista
`40-checkboxes-numero-bracadeira.md`, mas a seção "Arquivos" da task 43 não cita esse arquivo (a
contagem dá 0).

Conserto: a seção "Arquivos a criar ou modificar" da task 43 declara a nota da task 40. O
estado da task também, por `rite set KITS-TASK-43 --files …`.

```text
$ sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/43-medir-encaixe-mangas.md | grep -c 40-checkboxes
1
```

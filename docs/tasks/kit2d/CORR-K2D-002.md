---
id: CORR-K2D-002
---

# CORR-K2D-002 — Varrer também literais de string na regra de endereço do layout.py

Origin: [K2D-TASK-01](/docs/tasks/kit2d/01-esqueleto.md)

## Problem

`address_breaks()` em `tools/kit2d/selftest.py` olha só tokens `tokenize.NUMBER`. Um endereço da §1.1 escrito como texto e convertido — `int("0x3F534", 16)`, ou constante guardada em `str` — escapa da regra "nenhum outro arquivo soletra esses números" que a docstring do `layout.py` declara.

## Evidência

Rode da raiz do repositório:

```text
$ S=$(mktemp -d); git archive HEAD tools src | tar -x -C $S; echo 'X = int("0x3F534", 16)' > $S/tools/kit2d/p.py; python3 $S/tools/kit2d/selftest.py --quiet; echo exit=$?
kit2d_selftest: 12 check(s) ran, 0 failure(s)
exit=0
```

## Root cause

Hipótese: a varredura foi limitada a `NUMBER` de propósito, para não acusar prosa. Mas um `STRING` cujo conteúdo é só um número não é prosa.

## Fix

Em `address_breaks()`, também interpretar tokens `STRING` cujo conteúdo, sem aspas e espaços, seja um literal inteiro inteiro (decimal ou `0x`) e acusá-los se o valor estiver em `layout.ADDRESSES`. Somar o controle correspondente em `PLANTS`.

## Arquivos a criar ou modificar

- `tools/kit2d/selftest.py`

## Verificação

O comando da Evidência passa a sair `exit=1`, listando `('p.py', 1, …)`; `python3 tools/kit2d/selftest.py` continua verde na árvore real.

## Log de Execução

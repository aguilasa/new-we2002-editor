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

- 2026-10-22 — reproduzido na HEAD `88f9e194` (`rite reproduce`, antes da CORR-K2D-001): `kit2d_selftest: 12 check(s) ran, 0 failure(s)` / `exit=0` com `int("0x3F534", 16)` em `p.py`.
- Correção: `_literal_int()` devolve o inteiro de um token `NUMBER` ou de um `STRING` cujo valor (`ast.literal_eval`, sem espaços) é só um literal inteiro decimal ou `0x`; `address_breaks()` usa os dois. Controle novo em `PLANTS`: `planted.py` com `OFFSET = int("0x3F534", 16)`.
- **Closed** — commit `dcfe2b79` (2026-10-22): fix(kit2d): catch section 1.1 addresses spelled as strings
  - Files (`git show --name-status dcfe2b79`):
    - `M docs/tasks/kit2d/CORR-K2D-002.md`
    - `M tools/kit2d/selftest.py`

## Verificação feita

```text
$ S=$(mktemp -d); git ls-files tools src | tar -c -T - | tar -x -C $S; echo 'X = int("0x3F534", 16)' > $S/tools/kit2d/p.py; python3 $S/tools/kit2d/selftest.py --quiet; echo exit=$?
  FAIL  no address of section 1.1 is spelled outside layout.py  [('p.py', 1, '"0x3F534"')]
kit2d_selftest: 14 check(s) ran, 1 failure(s)
exit=1
$ python3 tools/kit2d/selftest.py --quiet; echo exit=$?
kit2d_selftest: 14 check(s) ran, 0 failure(s)
exit=0
```

Controle do controle — o ramo de `STRING` desligado numa cópia derruba o plantio novo:

```text
  FAIL  planted an address spelled as a string turns its rule red
kit2d_selftest: 14 check(s) ran, 1 failure(s)
exit=1
```

Gates: `kit2d_selftest` e `ctest -R kit2d_selftest` verdes; o terceiro (`tools/kit2d/controls.py`) sai 2, esperado até a K2D-TASK-16.

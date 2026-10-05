---
id: CORR-KITS-050
---

# CORR-KITS-050 — Corrigir a docstring do report() que promete filtro de conjunto compartilhado

Origin: [KITS-TASK-27](/docs/tasks/kits/27-titular-e-suplente-no-jogo.md)

## Problem

A docstring de `report()` em `tools/kits/oracle.py` diz que conta um registro "not shared byte for byte with the other set of the same kit", mas o código não tem esse filtro: todo registro não plano de índice 0-7 é contado. É por isso que o `TEX_A4` (conjuntos idênticos) sai como "exact records of set 1 and 2", como o Log anota.

## Evidência

```text
$ sed -n '/^def report(hits/,/^    return/p' tools/kits/oracle.py
  """... not flat, and
  not shared byte for byte with the other set of the same kit."""
  ...
      if not flat and index in SETS:
          worn.setdefault(tag, set()).add(SETS[index])
$ grep -n "shared byte for byte" tools/kits/oracle.py
187:    shared byte for byte with the other set of the same kit."""
```

## Root cause

A docstring foi escrita antes do código, ou o filtro caiu.

## Fix

Em `tools/kits/oracle.py`, implementar o filtro (pular o índice i quando `payload(i) == payload(i±4)`) ou tirar a cláusula da docstring.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`

## Verificação

`grep -n "shared byte for byte" tools/kits/oracle.py` não acha nada; ou, com o filtro, `--png` sobre o dump do LOOKS SET (`work/kits-oracle/looks-2`) deixa de imprimir "TEX_A4: exact records of set 1 and 2".

## Log de Execução

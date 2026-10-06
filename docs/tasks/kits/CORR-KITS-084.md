---
id: CORR-KITS-084
---

# CORR-KITS-084 — Catalogar um controle para a ordem de texel do --match-pose

Origin: [KITS-TASK-45](/docs/tasks/kits/45-pose-figura-partida.md)

## Problem

A KITS-TASK-45 acrescenta cinco verificações de selftest para `piece_error` e `pose_judge`, mas nenhuma entrada em `tools/kits/controls.py`. O vermelho do Log saiu de uma edição à mão, não versionada. A KITS-TASK-44 precisou da CORR-KITS-076 para o mesmo tipo de controle.

## Evidência

```text
$ grep -c "match-pose\|pose-texel" tools/kits/controls.py
0
$ python tools/kits/controls.py --list | tail -1
controls: 27 catalogued
```

Plantado à mão numa cópia da HEAD (`zip(prim.indices` → `zip(prim.corners` em `piece_error`), o `selftest.py` fica vermelho:

```text
FAIL  oracle --match-pose: a piece's own matrix lands within the limit, paired by texel  14.015451651872144 over 1
```

## Root cause

O controle foi plantado à mão para o vermelho do Log e nunca entrou no catálogo.

## Fix

Em `tools/kits/controls.py`, um `Control("oracle-pose-texel-order", "kits/oracle.py", "piece_error", "        for vi, texel in zip(prim.indices, prim.texcoords):\n", "        for vi, texel in zip(prim.corners, prim.texcoords):\n", "FAIL  oracle --match-pose: a piece's own matrix lands within the limit, paired by texel", ...)`.

## Arquivos a criar ou modificar

- `tools/kits/controls.py`

## Verificação

`python tools/kits/controls.py --only oracle-pose-texel-order` sai 0 e mostra o controle vermelho. Hoje o controle não existe.

## Log de Execução

Reproduzido em 2026-10-06 sobre `8910f8d`: `grep -c "match-pose\|pose-texel" tools/kits/controls.py`
dá `0`.

Conserto: o controle `oracle-pose-texel-order` em `tools/kits/controls.py`, com a planta e o FAIL
esperado que a Correção dá.

```text
$ python3 tools/kits/controls.py --only oracle-pose-texel-order
  RED    oracle-pose-texel-order      kits/oracle.py :: piece_error
controls: 1 of 1 red
```

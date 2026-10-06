---
id: CORR-KITS-070
---

# CORR-KITS-070 — Devolver a docstring de UNIFORM_RECORD para baixo da constante

Origin: [KITS-TASK-42](/docs/tasks/kits/42-medir-numero-partida.md)

## Problem

O commit e1d38dc inseriu `UNIFORM_SET2 = 4` e a docstring dela entre `UNIFORM_RECORD = 0` e a docstring dessa constante. Resultado: `UNIFORM_RECORD` fica sem docstring, e o texto do conjunto 1 ("The set-1 uniform page, (576,256) ...") fica solto depois da docstring de `UNIFORM_SET2`.

## Evidência

```text
$ sed -n 745,748p tools/kits/oracle.py
UNIFORM_RECORD = 0
UNIFORM_SET2 = 4
"""The set-2 uniform page; records 0 and 4 share the rectangle (section 1.1)."""
"""The set-1 uniform page, (576,256) 64x128 halfwords = 128x128 pixels."""
$ python3 -c "import ast;b=ast.parse(open('tools/kits/oracle.py').read()).body;[print(n.targets[0].id,'->',repr(b[i+1].value.value)[:40] if isinstance(b[i+1],ast.Expr) else 'no docstring') for i,n in enumerate(b) if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id in('UNIFORM_RECORD','UNIFORM_SET2')]"
UNIFORM_RECORD -> no docstring
UNIFORM_SET2 -> 'The set-2 uniform page; records 0 and 4
```

## Root cause

A constante nova foi inserida uma linha cedo demais.

## Fix

Em `tools/kits/oracle.py`, mover `UNIFORM_SET2 = 4` e a docstring dela para baixo da docstring do conjunto 1.

## Arquivos a criar ou modificar

- `tools/kits/oracle.py`

## Verificação

A mesma linha `python3 -c` acima imprime `UNIFORM_RECORD -> 'The set-1 uniform page` (hoje imprime `no docstring`).

## Log de Execução

Reproduzido em 2026-10-06 sobre `72effec`: a linha `python3 -c` da Evidência imprime
`UNIFORM_RECORD -> no docstring`.

Conserto: `UNIFORM_SET2 = 4` e a docstring dela desceram para baixo da docstring do conjunto 1.
Só muda a ordem das declarações.

```text
$ python3 -c "<a linha da Evidência>"
UNIFORM_RECORD -> 'The set-1 uniform page, (576,256) 64x12
UNIFORM_SET2 -> 'The set-2 uniform page; records 0 and 4
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin ctest --test-dir build -R kits
100% tests passed, 0 tests failed out of 4
```

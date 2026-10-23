---
id: CORR-DMCP-028
---

# CORR-DMCP-028 — Nomear tools/looks/confront.py entre os chamadores das reexportações do who_writes

Origin: [DMCP-TASK-20](/docs/tasks/duckmcp/20-pes2-who-writes-e-drive.md)

## Problem

O docstring do `who_writes.py` e o Log dizem que as funções reexportadas (`hx`, `register_value`, ...)
ficam para `tools/kits/oracle.py` e `tools/looks/oracle.py`. O `tools/looks/confront.py` também importa
`who_writes` e usa `hx` e `register_value`. O `audit.py` não acusa `import who_writes`, então quem
remover as reexportações depois não recebe aviso sobre o `confront.py`, e ele quebra.

## Evidência

```text
$ grep -rn --include='*.py' -E "import who_writes" tools | grep -v "^tools/pes2/who_writes.py" | cut -d: -f1 | sort | uniq -c
      2 tools/kits/oracle.py
      2 tools/looks/confront.py
     32 tools/looks/oracle.py
$ grep -n "tools/kits/oracle.py" tools/pes2/who_writes.py
re-exported for the callers that still import them from here
(`tools/kits/oracle.py`, `tools/looks/oracle.py`).
```

## Root cause

Hipótese: os chamadores foram contados à mão, e só os dois `oracle.py` foram conferidos.

## Fix

Acrescentar `tools/looks/confront.py` à lista de chamadores no docstring do `tools/pes2/who_writes.py`.

## Arquivos a criar ou modificar

- `tools/pes2/who_writes.py`

## Verificação

`grep -c "tools/looks/confront.py" tools/pes2/who_writes.py` imprime 0 hoje e ao menos 1 depois.

## Log de Execução

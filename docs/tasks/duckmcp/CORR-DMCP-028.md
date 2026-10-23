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

**Reprodução (2026-10-23, HEAD `b0c0cc77`, `rite reproduce --all --cycle duckmcp`):** REPRODUCED.

```text
$ grep -rn --include='*.py' -E "import who_writes" tools | grep -v "^tools/pes2/who_writes.py" | cut -d: -f1 | sort | uniq -c
      2 tools/kits/oracle.py
      2 tools/looks/confront.py
     30 tools/looks/oracle.py
$ grep -n "tools/kits/oracle.py" tools/pes2/who_writes.py
35:(`tools/kits/oracle.py`, `tools/looks/oracle.py`).
```

O `tools/looks/oracle.py` tem hoje 30 linhas de `import who_writes`, não 32 como a Evidência registrou;
o que decide — o `confront.py` importa e o docstring não o nomeia — continua igual. A causa confere:
`tools/looks/confront.py:1335` e `:1343` usam `who_writes.hx` e `who_writes.register_value`.

**Conserto:** a lista de chamadores no docstring do `tools/pes2/who_writes.py` ganhou
`tools/looks/confront.py`.

**Verificação:**

```text
$ git show HEAD:tools/pes2/who_writes.py | grep -c "tools/looks/confront.py"
0
$ grep -c "tools/looks/confront.py" tools/pes2/who_writes.py
1
$ python3 tools/pes2/selftest.py 2>&1 | tail -1
OK
$ python3 tools/duckmcp/selftest.py 2>&1 | tail -1
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
```
- **Closed** — commit `e3bb6449` (2026-10-23): docs(pes2): name tools/looks/confront.py among who_writes re-export callers
  - Files (`git show --name-status e3bb6449`):
    - `M docs/tasks/duckmcp/CORR-DMCP-028.md`
    - `M tools/pes2/who_writes.py`

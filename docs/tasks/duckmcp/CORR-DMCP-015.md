---
id: CORR-DMCP-015
---

# CORR-DMCP-015 — Listar 81-9F e C1-DF entre os opcodes que a cópia do looks perdia

Origin: [DMCP-TASK-13](/docs/tasks/duckmcp/13-hardware-e-pixels.md)

## Problem

A Nota (1) lista os opcodes que o `command_words` do looks não conhecia como `01, 1F, 03..1E, E0,
E7..FF` (mais CPU→VRAM A0..BF). Essa cópia também entregava o resto do nó para 81..9F e C1..DF, porque
o `COMMAND_WORDS` só tinha 00/02/80/C0; o `gpu.py` dá 4 e 3 palavras para eles. A Nota é o checklist
que a migração da Fase 5 tem de confirmar contra capturas, então falta esse caso.

## Evidência

```text
$ D=$(mktemp -d); git archive 87987d9d tools | tar -x -C "$D"; cd "$D" && python3 - <<'PY'
import ast, sys
sys.path.insert(0, "tools")
from duckmcp import gpu
tree = ast.parse(open("tools/looks/oracle.py").read())
want = {"command_words", "_COMMAND_WORDS", "COMMAND_WORDS", "_DRAW_MODE", "DRAW_MODE_CODES", "POLYLINE_MASK", "POLYLINE_MARK"}
ns = {}
for n in tree.body:
    names = [n.name] if isinstance(n, ast.FunctionDef) else [t.id for t in getattr(n, "targets", []) if isinstance(t, ast.Name)]
    if set(names) & want:
        exec(compile(ast.Module([n], []), "x", "exec"), ns)
for c in (0x81, 0x9F, 0xC1, 0xDF):
    w = [c << 24, 0, 1 | 1 << 16, 0, 0, 0, 0, 0]
    print(hex(c), "looks", ns["command_words"](w, 0), "gpu", gpu.command_size(w))
PY
0x81 looks 8 gpu 4
0x9f looks 8 gpu 4
0xc1 looks 8 gpu 3
0xdf looks 8 gpu 3
$ grep -n '81..9F' docs/tasks/duckmcp/13-hardware-e-pixels.md tools/duckmcp/gpu.py
(vazio)
```

## Root cause

A Nota listou os opcodes desconhecidos por família e esqueceu os não-base das famílias de cópia de VRAM
e de leitura de VRAM.

## Fix

Acrescentar `81..9F` e `C1..DF` à diferença (1) nas Notas da
`docs/tasks/duckmcp/13-hardware-e-pixels.md` e no comentário de linhagem do `tools/duckmcp/gpu.py`.

## Arquivos a criar ou modificar

- `docs/tasks/duckmcp/13-hardware-e-pixels.md`
- `tools/duckmcp/gpu.py`

## Verificação

`grep -n '81..9F' docs/tasks/duckmcp/13-hardware-e-pixels.md tools/duckmcp/gpu.py` — vazio hoje; depois
casa nos dois arquivos (e `C1..DF` também).

## Log de Execução

2026-10-22 — reproduzido com o comando da Evidência (`git archive 87987d9d`):
`0x81 looks 8 gpu 4`, `0x9f looks 8 gpu 4`, `0xc1 looks 8 gpu 3`, `0xdf looks 8 gpu 3`. O
`grep '81..9F'` vinha vazio.

Conserto: a diferença (1) das Notas da `13-hardware-e-pixels.md` e o comentário de linhagem do
`gpu.py` passaram a dizer que o `COMMAND_WORDS` do `looks` só tinha `00`/`02`/`80`/`C0`. Por isso
`81..9F` e `C1..DF` levavam o resto do nó, e aqui levam 4 e 3 palavras.

Verificação:

```text
$ grep -n '81..9F' docs/tasks/duckmcp/13-hardware-e-pixels.md tools/duckmcp/gpu.py | cut -c1-60
tools/duckmcp/gpu.py:27:# and the copy knew only 00/02/80/C0, so the VRAM co
docs/tasks/duckmcp/13-hardware-e-pixels.md:28:- **`gpu.py` segue o hardware o
$ grep -c 'C1..DF' docs/tasks/duckmcp/13-hardware-e-pixels.md tools/duckmcp/gpu.py
docs/tasks/duckmcp/13-hardware-e-pixels.md:1
tools/duckmcp/gpu.py:1
$ python3 tools/duckmcp/selftest.py --quiet
duckmcp_selftest: 361 check(s) ran, 0 failure(s)
```
- **Closed** — commit `6e3a4beb` (2026-10-22): docs(duckmcp): list 81..9F and C1..DF among the opcodes the looks copy lost
  - Files (`git show --name-status 6e3a4beb`):
    - `M docs/tasks/duckmcp/13-hardware-e-pixels.md`
    - `M docs/tasks/duckmcp/CORR-DMCP-015.md`
    - `M docs/tasks/duckmcp/correcoes-progresso.md`
    - `M docs/tasks/duckmcp/fixes.json`
    - `M tools/duckmcp/gpu.py`

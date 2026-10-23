---
id: CORR-DMCP-027
---

# CORR-DMCP-027 — Tirar o default do --display do mcp_drive.py de duckmcp.env.display()

Origin: [DMCP-TASK-19](/docs/tasks/duckmcp/19-pes2-mcp-drive-e-pad.md)

## Problem

A migração tirou do `McpSession.__init__` o `os.environ.get("PES2_DISPLAY", ":98")`, mas a mesma
leitura ficou no argparse do `main()`. Como o `--display` sempre tem valor de string, o
`display=None → env.display()` da lib nunca é usado, e `DUCKSTATION_DISPLAY` é ignorado pelo
`mcp_drive.py` — contra a decisão 3 da §2 do plano, confirmada no perfil: "a nova ganha da velha". O
`drive.py`, migrado logo depois na DMCP-TASK-20, já usa `default=env.display()`, então os dois
lançadores do `pes2` escolhem o display de jeitos diferentes. Hoje não há defeito visível, porque os
dois defaults são `:98`.

## Evidência

```text
$ grep -n 'add_argument("--display"' tools/pes2/mcp_drive.py tools/pes2/drive.py
tools/pes2/drive.py:795:    ap.add_argument("--display", default=env.display())
tools/pes2/mcp_drive.py:1276:    ap.add_argument("--display", default=os.environ.get("PES2_DISPLAY", ":98"))
$ DUCKSTATION_DISPLAY=:97 PES2_DISPLAY= python3 -B -c "import sys; sys.path.insert(0,'tools'); from duckmcp import env; print('env.display ->', env.display())"
env.display -> :97
```

Com esse ambiente o `mcp_drive.py` usaria o valor de `PES2_DISPLAY` (vazio) ou `:98`, não `:97`.

## Root cause

Hipótese: a task olhou só os duplicados que o Objetivo lista (`PRESS_FRAMES`/`AFTER_FRAMES`,
`STATE_DIR`, `capitalize`, captura) e não viu o default do argparse.

## Fix

No `main()` do `tools/pes2/mcp_drive.py`: `ap.add_argument("--display", default=None)`, para o
`Session` resolver por `env.display()`, ou `default=env.display()` como no `drive.py`. Somar ao
`self_check()` um check que afirme que o default sai de `env.display()`.

## Arquivos a criar ou modificar

- `tools/pes2/mcp_drive.py`

## Verificação

`grep -nE 'add_argument\("--display", default=(None|env\.display\(\))\)' tools/pes2/mcp_drive.py` sai 1
hoje e 0 depois do conserto; `python3 tools/pes2/selftest.py` continua `OK`.

## Log de Execução

**Reprodução (2026-10-23, HEAD `b0c0cc77`, `rite reproduce --all --cycle duckmcp`):** REPRODUCED.

```text
$ grep -n 'add_argument("--display"' tools/pes2/mcp_drive.py tools/pes2/drive.py
tools/pes2/mcp_drive.py:1276:    ap.add_argument("--display", default=os.environ.get("PES2_DISPLAY", ":98"))
tools/pes2/drive.py:795:    ap.add_argument("--display", default=env.display())
$ DUCKSTATION_DISPLAY=:97 PES2_DISPLAY= python3 -B -c "import sys; sys.path.insert(0,'tools'); from duckmcp import env; print('env.display ->', env.display())"
env.display -> :97
```

A causa confere: o default do argparse sempre tem valor, então o `display=None → env.display()` do
`Session` nunca é alcançado pelo `main()`.

**Conserto:** o parser do `main()` virou `_parser()`, e o `--display` passou a
`default=env.display()`, como no `drive.py`. O `self_check()` ganhou um check que põe
`DUCKSTATION_DISPLAY=:97` e `PES2_DISPLAY=:96` no ambiente, lê o default de `_parser()` e exige
`:97` (o ambiente é restaurado num `finally`).

**Controle** — a linha velha plantada numa cópia de `tools/pes2` + `tools/duckmcp` no scratchpad:

```text
$ grep -n 'add_argument("--display"' tools/pes2/mcp_drive.py      # na cópia
1293:    ap.add_argument("--display", default=os.environ.get("PES2_DISPLAY", ":98"))
$ python3 tools/pes2/mcp_drive.py --self-check | grep -E "FAIL|SELF"   # na cópia
  FAIL   --display defaults to env.display(), the new name first  (':96')
SELF-CHECK FAILED
exit 1
```

**Verificação** na árvore entregue:

```text
$ grep -nE 'add_argument\("--display", default=(None|env\.display\(\))\)' tools/pes2/mcp_drive.py; echo "exit $?"
1293:    ap.add_argument("--display", default=env.display())
exit 0
$ python3 tools/pes2/mcp_drive.py --self-check | grep -E "display|SELF"
  ok   --display defaults to env.display(), the new name first
SELF-CHECK OK: routes, thresholds, regions, signatures
$ python3 tools/pes2/selftest.py 2>&1 | tail -1
OK
$ python3 tools/duckmcp/selftest.py 2>&1 | tail -1
duckmcp_selftest: 435 check(s) ran, 0 failure(s)
```
- **Closed** — commit `256200da` (2026-10-23): fix(pes2): mcp_drive --display defaults through duckmcp.env.display()
  - Files (`git show --name-status 256200da`):
    - `M docs/tasks/duckmcp/CORR-DMCP-027.md`
    - `M tools/pes2/mcp_drive.py`

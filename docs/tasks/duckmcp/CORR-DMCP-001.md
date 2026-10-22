---
id: CORR-DMCP-001
---

# CORR-DMCP-001 — Cobrir o fallback por regex do audit.py com caso no selftest

Origin: [DMCP-TASK-02](/docs/tasks/duckmcp/02-audit.md)

## Problem

Quando um arquivo não parseia, `_sites_regex` ([audit.py:210](/tools/duckmcp/audit.py)) conta os sítios
no lugar do AST, e o Log da DMCP-TASK-02 anuncia esse fallback. Nenhuma checagem o exercita: trocar o
corpo dele por um `return sites` imediato deixa o selftest verde. O código funciona na HEAD (árvore
sintética com arquivo que não parseia dá 2 sítios; com o fallback desligado, 0) — mas nada notaria se
quebrasse. "Verificador sem vermelho visto não é gate."

## Evidência

```text
$ S=$(mktemp -d); git archive HEAD tools | tar -x -C $S && python3 - "$S/tools/duckmcp/audit.py" <<'PY'
import sys
p=sys.argv[1]; s=open(p).read()
s=s.replace('def _sites_regex(lines, project, targets, own_module, is_module):\n    sites = []','def _sites_regex(lines, project, targets, own_module, is_module):\n    sites = []\n    return sites',1)
open(p,'w').write(s)
PY
$ (cd $S && python3 tools/duckmcp/selftest.py --quiet; echo exit=$?)
duckmcp_selftest: 86 check(s) ran, 0 failure(s)
exit=0
$ T=$(mktemp -d); mkdir -p $T/emu $T/proj; touch $T/emu/mcp.py $T/emu/fork.py $T/emu/savestate.py; printf 'import fork\nclient.call("x")\ndef (:\n' > $T/proj/a.py
$ python3 tools/duckmcp/audit.py --root $T | tail -1        # HEAD
audit: 2 raw site(s) in 1 file(s)
$ (cd $S && python3 tools/duckmcp/audit.py --root $T | tail -1)   # fallback desligado
audit: 0 raw site(s) in 0 file(s)
```

## Root cause

Provável, não provada: `audit.self_check()` só monta árvores que parseiam, então o ramo
`except (SyntaxError, ValueError)` (audit.py:237) nunca roda sob teste.

## Fix

Em `self_check` do `tools/duckmcp/audit.py`, acrescentar uma árvore sintética com um arquivo que não
parseia e contém um sítio de cada categoria; afirmar que ele aparece em `doc["unparsed"]` e que as
contagens por categoria batem.

## Arquivos a criar ou modificar

- `tools/duckmcp/audit.py`

## Verificação

Aplicar a planta `return sites` acima numa cópia e rodar `python3 tools/duckmcp/selftest.py --quiet`:
hoje sai 0; depois do conserto tem de sair 1. Na árvore real, `python3 tools/duckmcp/selftest.py` sai 0.

## Log de Execução

2026-10-22 — reproduzido (planta `return sites` numa cópia: selftest 86 checks, exit 0; árvore
sintética 2 sítios na HEAD, 0 com o fallback desligado). Causa confirmada: nenhuma árvore do
`self_check` tinha arquivo que não parseia.

Conserto: `self_check` ganhou a árvore `broken`, com `other/c.py` que não parseia e traz um sítio de
cada categoria; afirma `doc["unparsed"] == ["broken/other/c.py"]` e
`by_category == {"import": 1, "client": 1, "sys.path": 1}`.

Verificação:

```text
$ python3 tools/duckmcp/selftest.py --quiet; echo exit=$?
duckmcp_selftest: 88 check(s) ran, 0 failure(s)
exit=0
$ (cd $S && python3 tools/duckmcp/selftest.py --quiet; echo exit=$?)   # cópia com a planta
  FAIL  audit: the regex fallback counts one site of every category  got {'import': 0, 'client': 0, 'sys.path': 0}, want {'import': 1, 'client': 1, 'sys.path': 1}
duckmcp_selftest: 88 check(s) ran, 1 failure(s)
exit=1
```

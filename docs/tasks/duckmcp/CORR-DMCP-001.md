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

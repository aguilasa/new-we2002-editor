---
id: CORR-KITS-088
---

# CORR-KITS-088 — Devolver a docstring de TAB_NAMES para baixo da constante em ui/app.py

Origin: [KITS-TASK-47](/docs/tasks/concluidos/kits/47-figura-partida-aba-3d.md)

## Problem

O commit f060945 inseriu `MATCH_FIGURE = 2` e a docstring dela entre `TAB_NAMES` e a docstring de `TAB_NAMES`. O texto "--tab names of the three tabs" agora vem depois de `MATCH_FIGURE` e não documenta nada, e `TAB_NAMES` fica sem docstring.

## Evidência

```text
$ sed -n 66,69p tools/kits/ui/app.py
TAB_NAMES = ("plan", "3d", "diag")
MATCH_FIGURE = 2
"""The 3D figure selector's third item: the match player of section 4.3."""
"""--tab names of the three tabs, in tab order."""
```

## Root cause

A constante nova foi inserida uma linha cedo demais.

## Fix

Em `tools/kits/ui/app.py`, mover `MATCH_FIGURE` e a docstring dela para baixo da linha `"""--tab names ..."""`.

## Arquivos a criar ou modificar

- `tools/kits/ui/app.py`

## Verificação

`sed -n 66,68p tools/kits/ui/app.py | sed -n 2p | grep -q '^"""--tab names'` falha hoje; passa depois.

## Log de Execução

Reproduzido em 2026-10-06 sobre `4d99303`: `sed -n 66,69p tools/kits/ui/app.py` mostra
`MATCH_FIGURE` entre `TAB_NAMES` e a docstring dela, e a Verificação sai 1.

Conserto: `MATCH_FIGURE` e a docstring dela desceram para baixo da docstring de `TAB_NAMES`. Só
muda a ordem.

```text
$ sed -n 66,68p tools/kits/ui/app.py | sed -n 2p | grep -q '^"""--tab names'; echo $?
0
$ python3 tools/kits/selftest.py | tail -1
kits_selftest: 0 failure(s)
```
- **Closed** — commit `3cc1902` (2026-10-06): refactor(kits): TAB_NAMES gets its docstring back
  - Files (`git show --name-status 3cc1902`):
    - `M docs/tasks/kits/CORR-KITS-088.md`
    - `M tools/kits/ui/app.py`

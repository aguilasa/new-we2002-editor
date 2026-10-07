---
id: CORR-KITS-056
---

# CORR-KITS-056 — Registrar pelo rite set os quatro arquivos fora do escopo da task 31

Origin: [KITS-TASK-31](/docs/tasks/concluidos/kits/31-combobox-de-times.md)

## Problem

O commit 6484655 altera `tools/kits/core/api.py`, `tools/kits/cli.py`, `tools/kits/selftest.py` e `docs/PLAN-KITS-PY.md`, mas os arquivos da KITS-TASK-31 no estado do Rite (os que o `rite context` reporta) são só `tools/kits/core/teams.py` e `tools/kits/ui/*.py`. O mesmo commit acrescentou os quatro à lista "Arquivos" do corpo da task, mas não ao estado. A CORR-KITS-055 fechou exatamente essa lacuna para a KITS-TASK-30.

## Evidência

```text
$ git show --stat 6484655
 docs/PLAN-KITS-PY.md, tools/kits/cli.py, tools/kits/core/api.py, tools/kits/core/teams.py, tools/kits/selftest.py, tools/kits/ui/app.py, tools/kits/ui/i18n.py, ...
$ sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-31 --json | python3 -c "import json,sys;print(json.load(sys.stdin)['item']['files'])"
['tools/kits/core/teams.py', 'tools/kits/ui/*.py']
```

## Root cause

Hipótese: o escopo foi alargado só no corpo em markdown, e o estado escrito pelo CLI ficou para trás.

## Fix

`rite set KITS-TASK-31 --files tools/kits/core/teams.py,tools/kits/ui/*.py,tools/kits/core/api.py,tools/kits/cli.py,tools/kits/selftest.py,docs/PLAN-KITS-PY.md` — pelo CLI, nunca editando o `progress.json` à mão.

## Arquivos a criar ou modificar

- estado da KITS-TASK-31, via `rite set`

## Verificação

```sh
sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-31 --json | python3 -c "import json,sys;f=json.load(sys.stdin)['item']['files'];assert all(p in f for p in ['tools/kits/core/api.py','tools/kits/cli.py','tools/kits/selftest.py','docs/PLAN-KITS-PY.md']),f"
```

Falha hoje; passa depois do conserto.

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `45d9fef`: `rite context KITS-TASK-31 --json` dava `item.files` = `['tools/kits/core/teams.py', 'tools/kits/ui/*.py']`, e a verificação da CORR falhava; `git show --stat 6484655` lista os quatro arquivos (`docs/PLAN-KITS-PY.md`, `tools/kits/cli.py`, `tools/kits/core/api.py`, `tools/kits/selftest.py`). A lista "Arquivos" do corpo da task já os tinha.

Conserto, pelo CLI:

```
$ rite set KITS-TASK-31 --files 'tools/kits/core/teams.py,tools/kits/ui/*.py,tools/kits/core/api.py,tools/kits/cli.py,tools/kits/selftest.py,docs/PLAN-KITS-PY.md'
$ rite context KITS-TASK-31 --json | python3 -c "import json,sys;f=json.load(sys.stdin)['item']['files'];assert all(p in f for p in ['tools/kits/core/api.py','tools/kits/cli.py','tools/kits/selftest.py','docs/PLAN-KITS-PY.md']),f;print('ok',f)"
ok ['tools/kits/core/teams.py', 'tools/kits/ui/*.py', 'tools/kits/core/api.py', 'tools/kits/cli.py', 'tools/kits/selftest.py', 'docs/PLAN-KITS-PY.md']
```
- **Closed** — commit `11e78cb` (2026-10-04): chore(kits): record the four out-of-scope KITS-TASK-31 files in its state
  - Files (`git show --name-status 11e78cb`):
    - `M docs/tasks/kits/CORR-KITS-056.md`
    - `M docs/tasks/kits/progress.json`

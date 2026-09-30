---
id: CORR-KITS-001
title: "Route cli.py survey through core/api.py, or record the exception"
origin: KITS-TASK-01
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-001 — Route cli.py survey through core/api.py, or record the exception

Origin: [KITS-TASK-01](/docs/tasks/kits/01-levantamento-do-tex.md)

## Problem

`tools/kits/cli.py` importa o módulo do núcleo direto (`from core import survey as survey_mod`) e lê `survey_mod.EXPECTED_SHAPE` e `survey_mod.KIND_IMAGE`. O §3.1 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) e a decisão do perfil dizem que UI e CLI só importam `core/api.py`. Nem o Log da KITS-TASK-01 nem as tasks da fachada (06) e do CLI (09) registram que o subcomando `survey` precisa passar para trás da fachada.

## Evidência

```text
$ grep -n "^from core\|survey_mod\.\(EXPECTED\|KIND\)" tools/kits/cli.py
16:from core import survey as survey_mod  # noqa: E402
41:    images = sum(1 for r in survey_mod.EXPECTED_SHAPE if r[0] == survey_mod.KIND_IMAGE)
42:    cluts = len(survey_mod.EXPECTED_SHAPE) - images
$ sed -n 194p docs/PLAN-KITS-PY.md
O contrato é **uma fachada**, `core/api.py`, e a interface só importa ela:
$ grep -n "survey" docs/tasks/kits/06-fachada-e-origem.md docs/tasks/kits/09-cli-e-confronto-1.md | grep -i api
(vazio)
```

## Root cause

Hipótese: `api.py` é da fase 1 (KITS-TASK-06), então um CLI da fase 0 não tinha o que importar; o desvio não foi registrado como passagem para a task seguinte.

## Fix

Registrar a exceção temporária em "Problemas encontrados" da KITS-TASK-01 e acrescentar à KITS-TASK-09 (ou 06) que `cli.py survey` passa a ir por `api.py`, com as constantes de forma vindo de lá.

## Arquivos a criar ou modificar

- `docs/tasks/kits/01-levantamento-do-tex.md`
- `docs/tasks/kits/09-cli-e-confronto-1.md` (ou `06-fachada-e-origem.md`)
- `tools/kits/cli.py` (quando a task 09 rodar)

## Verificação

```text
$ grep -n "survey" docs/tasks/kits/09-cli-e-confronto-1.md docs/tasks/kits/06-fachada-e-origem.md | grep -i "api"
```

Vazio antes; depois lista a passagem. Depois da task 09, `grep -nP "^from core import (?!api)" tools/kits/cli.py` sai vazio.

## Log de Execução

---
id: CORR-DMCP-009
---

# CORR-DMCP-009 — Varrer o plano pela troca de status para procs no cli.py

Origin: [DMCP-TASK-09](/docs/tasks/duckmcp/09-cli-fork-e-lancadores.md)

## Problem

A task reescreveu o próprio critério 3 de "`status` sem fork imprime `pids: []`" para "`procs` …",
porque `status` já era o `get_status` do servidor MCP. A fonte de verdade continua prometendo
`cli.py … launch, kill, recipe, which` mais um `status` de processo, e nada em lugar nenhum nomeia
`procs`. O Objetivo da própria task ainda diz `cli.py launch|kill|status|recipe|which`.

## Evidência

```text
$ git diff 1238f761 c2630fad -- docs/tasks/duckmcp/09-cli-fork-e-lancadores.md | grep 'pids: \[\]'
-- [ ] `python3 tools/duckmcp/cli.py recipe` imprime a receita, e `status` sem fork imprime `pids: []`
+- [x] `python3 tools/duckmcp/cli.py recipe` imprime a receita, e `procs` sem fork imprime `pids: []` (o `status` da lib já é o `get_status` do servidor; ver o Log)
$ grep -n 'procs\|launch/kill/status' docs/PLAN-DUCKMCP-PY.md
366:| 2 | **lançador**: … `cli.py launch/kill/status/recipe/which`; …
```

## Root cause

Uma decisão mudou dentro da task (o status de processo virou `procs`) e os documentos que a enunciam
não foram atualizados — "fechar um veredito é varrer quem dizia o anterior".

## Fix

Registrar `procs` no `docs/PLAN-DUCKMCP-PY.md`, §2 (linha do `cli.py`) e §5 (linha da Fase 2), e no
Objetivo da `docs/tasks/duckmcp/09-cli-fork-e-lancadores.md`.

## Arquivos a criar ou modificar

- `docs/PLAN-DUCKMCP-PY.md`
- `docs/tasks/duckmcp/09-cli-fork-e-lancadores.md`

## Verificação

`grep -n 'procs' docs/PLAN-DUCKMCP-PY.md` hoje não imprime nada; depois tem de nomear o comando, e
`grep -n 'launch/kill/status' docs/PLAN-DUCKMCP-PY.md` não pode mais achar a forma antiga.

## Log de Execução

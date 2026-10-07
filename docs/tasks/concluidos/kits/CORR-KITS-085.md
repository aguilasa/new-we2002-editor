---
id: CORR-KITS-085
---

# CORR-KITS-085 — Tirar a nota da KITS-TASK-47 do commit da KITS-TASK-45, ou declará-la

Origin: [KITS-TASK-45](/docs/tasks/concluidos/kits/45-pose-figura-partida.md)

## Problem

O commit de trabalho d1c64a3 altera `docs/tasks/kits/47-figura-partida-aba-3d.md` (2 linhas), que não está entre os arquivos declarados da KITS-TASK-45 (`oracle.py`, `selftest.py`, `PLAN-KITS-PY.md`). A nota também leva para uma task posterior a afirmação errada "2 a 4 px" da CORR-KITS-083.

## Evidência

```text
$ git show --stat d1c64a3 | grep 47-
 docs/tasks/kits/47-figura-partida-aba-3d.md |   2 +
$ sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-45 --json | grep -c 47-figura
0
```

## Root cause

Seguir a regra de varrer quem repete um veredito é razoável, mas o arquivo não foi declarado no escopo da task.

## Fix

Declarar o arquivo nos arquivos da KITS-TASK-45 pelo `rite set` (ou no Escopo), ou mover a nota para a §4.3 e deixar a task 47 remeter a ela. Corrigir o número lá junto com a CORR-KITS-083.

## Arquivos a criar ou modificar

- `docs/tasks/kits/45-pose-figura-partida.md` (ou os arquivos da task, via `rite set`)
- `docs/tasks/kits/47-figura-partida-aba-3d.md`

## Verificação

`rite context KITS-TASK-45 --json | grep -c 47-figura` é pelo menos 1, ou a nota sai da task 47 e passa a viver na §4.3.

## Log de Execução

Reproduzido em 2026-10-06 sobre `01f8aca`. O campo `files` da KITS-TASK-45 era `oracle.py`,
`selftest.py` e `PLAN-KITS-PY.md`, e `git show --stat d1c64a3` mostra também
`47-figura-partida-aba-3d.md`.

Conserto: o arquivo entra nos arquivos da task, por `rite set KITS-TASK-45 --files …`. O número
errado da nota ("2 a 4 px") é corrigido junto com a CORR-KITS-083.

```text
$ python3 -c "…print(files da KITS-TASK-45)…"
['tools/kits/oracle.py', 'tools/kits/selftest.py', 'docs/PLAN-KITS-PY.md', 'docs/tasks/kits/47-figura-partida-aba-3d.md']
```
- **Closed** — commit `1b26d74` (2026-10-06): chore(kits): task 45 declares the task 47 note it wrote
  - Files (`git show --name-status 1b26d74`):
    - `M docs/tasks/kits/CORR-KITS-085.md`
    - `M docs/tasks/kits/progress.json`

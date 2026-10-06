---
id: CORR-KITS-086
---

# CORR-KITS-086 — Declarar os quatro arquivos a mais no escopo da KITS-TASK-47

Origin: [KITS-TASK-47](/docs/tasks/kits/47-figura-partida-aba-3d.md)

## Problem

O escopo da KITS-TASK-47 lista 7 arquivos. O commit f060945 também altera `tools/kits/oracle.py` (`--match-silhouette`, `--plant-silhouette`, `--match-pose --write/--check`), `tools/kits/selftest.py`, `docs/prompts/perfil-kits.md` (uma entrada nova de artefato gerado) e acrescenta `tools/kits/core/match_pose.json`. O critério 1 ("com o comando") precisava do trabalho no oracle, e o Log descreve tudo, mas o escopo nunca o lista. O commit ainda move `SLEEVE_LENGTHS` do `oracle.py` para o core.

## Evidência

```text
$ git show --stat f060945
 tools/kits/core/match_pose.json             | 477 ++++
 tools/kits/oracle.py                        | 220 ++++-
 tools/kits/selftest.py                      |  27 ++
 docs/prompts/perfil-kits.md                 |   1 +
$ LC_ALL=C comm -13 <(sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-47 --json | python3 -c 'import json,sys;print("\n".join(json.load(sys.stdin)["item"]["files"]))' | LC_ALL=C sort) <(git show --name-only --format= f060945 | grep -v '^docs/tasks/' | LC_ALL=C sort)
docs/prompts/perfil-kits.md
tools/kits/core/match_pose.json
tools/kits/oracle.py
tools/kits/selftest.py
```

## Root cause

Hipótese: a task foi aberta antes de ficar claro que seriam precisos uma pose versionada e um confronto pelo oracle, e o escopo não foi emendado quando isso mudou.

## Fix

Acrescentar os quatro arquivos aos arquivos da KITS-TASK-47 pelo `rite set KITS-TASK-47 --files …` (nunca à mão), com uma linha para cada um no escopo do corpo da task.

## Arquivos a criar ou modificar

- arquivos da KITS-TASK-47, via `rite set`
- `docs/tasks/kits/47-figura-partida-aba-3d.md` (escopo no corpo)

## Verificação

O `comm` acima imprime 4 caminhos hoje; nada depois do conserto. (O `LC_ALL=C` nos dois `sort` é necessário: sem ele o `comm` reclama de ordem e acusa um quinto caminho falso.)

## Log de Execução

Reproduzido em 2026-10-06 sobre `4d99303`: o `comm` da Evidência imprime os quatro caminhos
(`docs/prompts/perfil-kits.md`, `tools/kits/core/match_pose.json`, `tools/kits/oracle.py`,
`tools/kits/selftest.py`).

Conserto:

- `rite set KITS-TASK-47 --files …` acrescenta os quatro arquivos ao estado.
- O escopo no corpo da task ganhou uma linha para cada um, e a do `oracle.py` registra a descida
  do `SLEEVE_LENGTHS` para o core.

```text
$ LC_ALL=C comm -13 <(rite context KITS-TASK-47 … | sort) <(git show --name-only --format= f060945 | grep -v '^docs/tasks/' | sort)
(sem saída)
```
- **Closed** — commit `b2c4f77` (2026-10-06): chore(kits): task 47 declares the four files it also changed
  - Files (`git show --name-status b2c4f77`):
    - `M docs/tasks/kits/47-figura-partida-aba-3d.md`
    - `M docs/tasks/kits/CORR-KITS-086.md`
    - `M docs/tasks/kits/progress.json`

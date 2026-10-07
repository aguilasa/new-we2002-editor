---
id: CORR-KITS-089
---

# CORR-KITS-089 — Declarar os cinco arquivos que a task 40 mudou fora do escopo

Origin: [KITS-TASK-40](/docs/tasks/concluidos/kits/40-checkboxes-numero-bracadeira.md)

## Problem

O commit `05d54ec` da KITS-TASK-40 muda cinco arquivos que o `files` da task não declara: `tools/kits/core/api.py`, `tools/kits/core/figure.py`, `tools/kits/oracle.py`, `tools/kits/selftest.py` e `tools/kits/ui/figure_view.py`. Três deles também ficam fora do "Dentro" da task: `oracle.py`, `selftest.py` e `figure_view.py`. A mudança do `figure_view.py` desenha `cx - x` e desfaz o espelho de toda figura da aba 3D, o que vai além das três caixas. É a mesma lacuna que a [CORR-KITS-086](/docs/tasks/concluidos/kits/CORR-KITS-086.md) apontou na task 47.

## Evidência

```text
$ R=/home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite
LC_ALL=C comm -13 \
  <(sh $R context KITS-TASK-40 --json | python3 -c "import json,sys;[print(f) for f in json.load(sys.stdin)['item']['files']]" | LC_ALL=C sort) \
  <(git show --name-only --format= 05d54ec | grep -v '^docs/tasks/' | LC_ALL=C sort)
tools/kits/core/api.py
tools/kits/core/figure.py
tools/kits/oracle.py
tools/kits/selftest.py
tools/kits/ui/figure_view.py
```

## Root cause

Hipótese do revisor: o defeito de espelho foi achado durante a execução e corrigido ali mesmo, e o `files` não acompanhou.

## Fix

Declarar os cinco caminhos pelo CLI, nunca editando o frontmatter nem o `progress.json`:

```sh
sh $R set KITS-TASK-40 --files tools/kits/ui/app.py,tools/kits/ui/i18n.py,tools/kits/ui_check.py,docs/PLAN-KITS-PY.md,tools/kits/core/api.py,tools/kits/core/figure.py,tools/kits/oracle.py,tools/kits/selftest.py,tools/kits/ui/figure_view.py
```

Na seção "Dentro" da task, acrescentar uma linha dizendo que a correção do espelho da vista entrou como defeito achado no caminho. O Log já a explica.

## Arquivos a criar ou modificar

- `docs/tasks/kits/40-checkboxes-numero-bracadeira.md` (prosa do "Dentro")
- `files` da KITS-TASK-40, via `rite set`

## Verificação

```sh
R=/home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite
LC_ALL=C comm -13 \
  <(sh $R context KITS-TASK-40 --json | python3 -c "import json,sys;[print(f) for f in json.load(sys.stdin)['item']['files']]" | LC_ALL=C sort) \
  <(git show --name-only --format= 05d54ec | grep -v '^docs/tasks/' | LC_ALL=C sort)
```

Hoje imprime as cinco linhas da Evidência. Depois da correção não imprime nada.

## Log de Execução

- **Closed** — commit `c70ad8b` (2026-10-07): docs(kits): declare the five files KITS-TASK-40 changed out of scope
  - Files (`git show --name-status c70ad8b`):
    - `M docs/tasks/kits/40-checkboxes-numero-bracadeira.md`

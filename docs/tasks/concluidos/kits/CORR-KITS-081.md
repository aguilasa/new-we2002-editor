---
id: CORR-KITS-081
---

# CORR-KITS-081 — Declarar selftest.py e a nota da task 47 nos arquivos da task

Origin: [KITS-TASK-46](/docs/tasks/concluidos/kits/46-manga-curta-partida.md)

## Problem

A KITS-TASK-46 declara `tools/kits/oracle.py` e `docs/PLAN-KITS-PY.md`, mas o commit c1adc98 também altera `tools/kits/selftest.py` (duas verificações de manga curta) e `docs/tasks/kits/47-figura-partida-aba-3d.md` (uma nota). A edição da task 47 fica fora do escopo declarado.

## Evidência

```text
$ git show --stat c1adc98
  docs/tasks/kits/47-figura-partida-aba-3d.md |  2 ++
  tools/kits/selftest.py                      |  7 ++++
$ sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-46 --json | grep -c selftest.py
0
```

## Root cause

As verificações do selftest são o gate que os critérios pedem, e a nota da task 47 é passagem; nenhuma das duas entrou nos arquivos da task.

## Fix

Acrescentar os dois caminhos aos arquivos da KITS-TASK-46 pelo `rite set KITS-TASK-46 --files …` (nunca editando o frontmatter nem o `progress.json` à mão), ou deixar no Log uma linha justificando a nota de passagem.

## Arquivos a criar ou modificar

- arquivos da KITS-TASK-46, via `rite set`

## Verificação

`sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-46 --json | grep -c selftest.py` é pelo menos 1 (hoje 0).

## Log de Execução

Reproduzido em 2026-10-06 sobre `01f8aca`. O campo `files` da KITS-TASK-46 no estado era
`['tools/kits/oracle.py', 'docs/PLAN-KITS-PY.md']`, e `git show --stat c1adc98` mostra também
`tools/kits/selftest.py` e `docs/tasks/kits/47-figura-partida-aba-3d.md`. O `grep -c selftest.py`
da Verificação já casava 1, mas por texto do Log no `rite context`, não pelo campo.

Conserto: `rite set KITS-TASK-46 --files
tools/kits/oracle.py,tools/kits/selftest.py,docs/PLAN-KITS-PY.md,docs/tasks/kits/47-figura-partida-aba-3d.md`.

```text
$ python3 -c "…print(files da KITS-TASK-46)…"
['tools/kits/oracle.py', 'tools/kits/selftest.py', 'docs/PLAN-KITS-PY.md', 'docs/tasks/kits/47-figura-partida-aba-3d.md']
```
- **Closed** — commit `a28da61` (2026-10-06): chore(kits): task 46 declares selftest.py and its task 47 note
  - Files (`git show --name-status a28da61`):
    - `M docs/tasks/kits/CORR-KITS-081.md`
    - `M docs/tasks/kits/progress.json`

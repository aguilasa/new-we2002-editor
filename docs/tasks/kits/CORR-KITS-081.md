---
id: CORR-KITS-081
---

# CORR-KITS-081 — Declarar selftest.py e a nota da task 47 nos arquivos da task

Origin: [KITS-TASK-46](/docs/tasks/kits/46-manga-curta-partida.md)

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

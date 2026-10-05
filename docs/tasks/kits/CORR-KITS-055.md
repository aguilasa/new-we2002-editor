---
id: CORR-KITS-055
---

# CORR-KITS-055 — Declarar no escopo da task as edições do perfil e da task 31

Origin: [KITS-TASK-30](/docs/tasks/kits/30-tabela-time-tag.md)

## Problem

O commit aefc8ae muda dois arquivos fora da lista declarada da KITS-TASK-30 (`tools/kits/core/generated/`, `gen_tables.py`, `PLAN-KITS-PY.md`, `NOTICE.md`): a entrada de artefatos gerados em `docs/prompts/perfil-kits.md` e uma nota de passagem em `docs/tasks/kits/31-combobox-de-times.md`. As duas edições são razoáveis — a do perfil é a que a regra "fechar um veredito é varrer quem dizia o anterior" pede —, mas estão além do escopo declarado.

## Evidência

```text
$ git show --stat aefc8ae
 docs/prompts/perfil-kits.md             |   1 +
 docs/tasks/kits/31-combobox-de-times.md |   2 +
$ sh /home/ingmar/.claude/plugins/cache/rite/rite/0.15.0/bin/rite context KITS-TASK-30 --json | python3 -c "import json,sys;print(json.load(sys.stdin)['item']['files'])"
['tools/kits/core/generated/', 'tools/kits/gen_tables.py', 'docs/PLAN-KITS-PY.md', 'NOTICE.md']
```

## Root cause

A lista de arquivos foi escrita antes de se saber que a convenção de gerador pede uma entrada no perfil.

## Fix

Acrescentar `docs/prompts/perfil-kits.md` (e, se a passagem for mantida, `docs/tasks/kits/31-combobox-de-times.md`) aos arquivos da task 30 por `rite set KITS-TASK-30 --files …` — nunca editando o frontmatter à mão —, ou registrá-los no Log dela.

## Arquivos a criar ou modificar

- `docs/tasks/kits/30-tabela-time-tag.md` (Log), ou os arquivos da task pelo `rite set`

## Verificação

`rite context KITS-TASK-30 --json` lista `docs/prompts/perfil-kits.md` em `item.files` (hoje não lista), ou o Log da task nomeia as duas edições.

## Log de Execução

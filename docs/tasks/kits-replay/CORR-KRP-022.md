---
id: CORR-KRP-022
---

# CORR-KRP-022 — KRP-TASK-22 declara docs/PLAN-KITS-REPLAY.md no files mas não em Arquivos a criar ou modificar

Origin: [KRP-TASK-22](/docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md)

## Problem

O commit de trabalho c74ba1cb edita o `docs/PLAN-KITS-REPLAY.md` (parágrafo da §3.3). O
`rite set --files` o pôs no frontmatter e no `progress.json`, mas a seção "Arquivos a criar ou
modificar" da task não tem linha para ele. O `CLAUDE.md` exige as duas coisas no mesmo commit; sem
isso conta como escopo não declarado.

## Evidência

```text
$ git show --stat c74ba1cb | grep PLAN
 docs/PLAN-KITS-REPLAY.md                           |   6 +-
$ awk '/^## Arquivos a criar/,/^## Done/' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md | grep -c PLAN-KITS-REPLAY
0
```

## Root cause

Só a metade da regra que vai no frontmatter foi aplicada. A lista em prosa foi escrita antes de a
edição do plano se mostrar necessária.

## Fix

Acrescentar, em "In:", no `docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md`, a
linha "- `docs/PLAN-KITS-REPLAY.md` (§3.3: o 940×409 → 786×409 medido e os números de confronto
inalterados)".

## Arquivos a criar ou modificar

- `docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md`

## Verificação

```sh
awk '/^## Arquivos a criar/,/^## Done/' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md | grep -c PLAN-KITS-REPLAY
```

Hoje imprime 0. Depois do conserto tem de imprimir pelo menos 1.

## Log de Execução

### 2026-10-16

Reprodução (`rite reproduce`, HEAD `804d7280`): `git show --stat c74ba1cb | grep PLAN` dá
`docs/PLAN-KITS-REPLAY.md | 6 +-`, e o `awk … | grep -c PLAN-KITS-REPLAY` dá 0.

Conserto: em "In:", a linha `docs/PLAN-KITS-REPLAY.md` (§3.3), com o texto do Fix e o link desta
correção.

Verificação:

```text
$ awk '/^## Arquivos a criar/,/^## Done/' docs/tasks/kits-replay/22-painel-de-controles-da-cabeca-na-aba-3d.md | grep -c PLAN-KITS-REPLAY
1
```

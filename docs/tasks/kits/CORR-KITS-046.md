---
id: CORR-KITS-046
---

# CORR-KITS-046 — Declarar a edição do PLAN-KITS-PY.md na lista de arquivos da task

Origin: [KITS-TASK-25](/docs/tasks/kits/25-aba-3d.md)

## Problem

O commit a47275a altera `docs/PLAN-KITS-PY.md` (§3.4: a aba 3D é desenhada por `QPainter`, não por OpenGL). Esse arquivo não está na lista "Arquivos a criar ou modificar" da KITS-TASK-25; aparece só no bloco de fechamento do Log, não no escopo declarado.

## Evidência

```text
$ git show --stat a47275a | grep PLAN
 docs/PLAN-KITS-PY.md         |   4 +-
$ sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/25-aba-3d.md | grep -c PLAN-KITS
0
```

## Root cause

Uma decisão de desenho (renderização por software em vez de OpenGL) foi escrita de volta no plano sem alargar a lista de arquivos declarada da task.

## Fix

Acrescentar `docs/PLAN-KITS-PY.md` (§3.4, decisão de renderização) à lista de arquivos de `docs/tasks/kits/25-aba-3d.md`, com uma linha dizendo o motivo.

## Arquivos a criar ou modificar

- `docs/tasks/kits/25-aba-3d.md`

## Verificação

```sh
sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/25-aba-3d.md | grep -c PLAN-KITS
```

Dá 0 hoje; 1 depois do conserto. (A grep sobre o arquivo inteiro já casa a linha 102, do Log, e por isso não serve de verificação.)

## Log de Execução

### 2026-10-04

Reproduzido na HEAD `2cf47a5`:

```
$ git show --stat a47275a | grep PLAN
 docs/PLAN-KITS-PY.md         |   4 +-
$ sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/25-aba-3d.md | grep -c PLAN-KITS
0
```

Conserto: `docs/PLAN-KITS-PY.md` entra na lista de arquivos da KITS-TASK-25, com o motivo da decisão de renderização (§3.4). O plano não muda.

```
$ sed -n '/^## Arquivos/,/^## /p' docs/tasks/kits/25-aba-3d.md | grep -c PLAN-KITS
1
```
- **Closed** — commit `ae68e02` (2026-10-04): docs(kits): list the PLAN-KITS-PY.md edit in the KITS-TASK-25 files
  - Files (`git show --name-status ae68e02`):
    - `M docs/tasks/kits/25-aba-3d.md`
    - `M docs/tasks/kits/CORR-KITS-046.md`

---
id: CORR-KITS-043
---

# CORR-KITS-043 — Registrar no Escopo a reescrita da verificação da fase 6 no perfil

Origin: [KITS-TASK-24](/docs/tasks/kits/24-figura.md)

## Problem

O commit da KITS-TASK-24 reescreveu a verificação da fase 6 no perfil do ciclo (`docs/prompts/perfil-kits.md`), de "Só `core/figure.py` importa o `looks`" para o mais estreito "importa o `scene`". Esse arquivo não está no Escopo da task nem em `files`, e o executor reescreveu no mesmo commit o próprio critério 1. A reescrita concorda com a §3.1 (que mantém endereços no `layout` do `looks`), mas o estreitamento da verificação do ciclo não ficou registrado como item de Escopo nem como decisão.

## Evidência

```text
$ git show --stat 3747272 | grep perfil
 docs/prompts/perfil-kits.md  |   2 +-
$ sed -n '/^## Arquivos/,/^## Done/p' docs/tasks/kits/24-figura.md | grep -c perfil-kits
0
```

## Root cause

A mudança de critério foi levada ao perfil sem ser declarada como parte do escopo da task.

## Fix

Acrescentar `docs/prompts/perfil-kits.md` (a reescrita da verificação da fase 6) à lista de Escopo de `docs/tasks/kits/24-figura.md`, com uma linha dizendo por que a verificação foi estreitada.

## Arquivos a criar ou modificar

- `docs/tasks/kits/24-figura.md`

## Verificação

```sh
sed -n '/^## Arquivos/,/^## Done/p' docs/tasks/kits/24-figura.md | grep -c perfil-kits
```

Dá 0 hoje; 1 depois do conserto.

## Log de Execução

### 2026-10-03

Reproduzido na HEAD `c9ca511`:

```
$ git show --stat 3747272 | grep perfil
 docs/prompts/perfil-kits.md  |   2 +-
$ sed -n '/^## Arquivos/,/^## Done/p' docs/tasks/kits/24-figura.md | grep -c perfil-kits
0
```

Conserto: `docs/prompts/perfil-kits.md` entra na lista de Escopo da KITS-TASK-24, com a razão do estreitamento (a §3.1 põe endereço no `layout` do `looks` e lista as sondas do `survey.py`; o que ela reserva ao `figure.py` é pedir a cena). O perfil não muda.

```
$ sed -n '/^## Arquivos/,/^## Done/p' docs/tasks/kits/24-figura.md | grep -c perfil-kits
1
```

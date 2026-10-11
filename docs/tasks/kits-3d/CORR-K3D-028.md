---
id: CORR-K3D-028
---

# CORR-K3D-028 — Nota de passagem na K3D-TASK-19 fora do escopo da K3D-TASK-18

Origin: [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md)

## Problem

O commit de trabalho da [K3D-TASK-18](/docs/tasks/kits-3d/18-medir-os-22-replay.md) acrescenta 8 linhas de nota ao arquivo da K3D-TASK-19. Esse
arquivo não está na lista "In" do escopo da 18, e o fechamento do Rite já o acusa em
"Outside declared files". É a terceira vez no ciclo (ver CORR-K3D-006 e CORR-K3D-025).

## Evidência

```text
$ git show --stat 27f2565 | grep 19-medir
 .../tasks/kits-3d/19-medir-capitao-linha-replay.md |   8 +
$ grep -n 'Outside declared files' -A1 docs/tasks/kits-3d/18-medir-os-22-replay.md
  - `docs/tasks/kits-3d/19-medir-capitao-linha-replay.md`
```

## Root cause

A passagem para a task seguinte foi escrita no mesmo commit sem declarar o arquivo.

## Fix

Declarar `docs/tasks/kits-3d/19-medir-capitao-linha-replay.md` no escopo "In" da
K3D-TASK-18 (pelo `rite set` e no arquivo da task). Ou, já que o padrão se repete,
registrar em `docs/prompts/perfil-kits-3d.md` ("Pull-ahead precedents") que nota entre
tasks é precedente permitido.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/18-medir-os-22-replay.md (ou docs/prompts/perfil-kits-3d.md)

## Verificação

O fechamento do Rite para a K3D-TASK-18 não traz entrada "Outside declared files" — ou o
perfil registra o precedente.

## Log de Execução

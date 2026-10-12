---
id: CORR-K3D-028
---

# CORR-K3D-028 — Nota de passagem na K3D-TASK-19 fora do escopo da K3D-TASK-18

Origin: [K3D-TASK-18](/docs/tasks/concluidos/kits-3d/18-medir-os-22-replay.md)

## Problem

O commit de trabalho da [K3D-TASK-18](/docs/tasks/concluidos/kits-3d/18-medir-os-22-replay.md) acrescenta 8 linhas de nota ao arquivo da K3D-TASK-19. Esse
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

### 2026-10-11 — arquivo da K3D-TASK-19 declarado no escopo da 18

Triagem inline (`rite reproduce --all --cycle kits-3d`): **REPRODUCED**. As duas linhas da Evidência saem
iguais na HEAD `75ae037`: ` .../tasks/kits-3d/19-medir-capitao-linha-replay.md |   8 +` e a entrada
`Outside declared files` na linha 100 da task.

O remédio é o da [CORR-K3D-025](/docs/tasks/concluidos/kits-3d/CORR-K3D-025.md) para a K3D-TASK-17: declarar o
arquivo. O "In" da K3D-TASK-18 ganhou `docs/tasks/kits-3d/19-medir-capitao-linha-replay.md`, e
`rite set K3D-TASK-18 --files tools/kits/oracle.py,tools/kits/selftest.py,tools/kits/controls.py,docs/KITS-AJUSTES-3D.md,docs/tasks/kits-3d/19-medir-capitao-linha-replay.md`
gravou o mesmo no estado. A entrada `Outside declared files` do fechamento de `27f2565` fica como está: é
registro do que aquele commit tocou contra o escopo de então.

O precedente no perfil (`Pull-ahead precedents`) não entrou: a seção registra o que o usuário autorizou,
e não há autorização dele para nota entre tasks.
- **Closed** — commit `43c2129` (2026-10-11): docs(kits): declare the K3D-TASK-19 note in K3D-TASK-18's scope
  - Files (`git show --name-status 43c2129`):
    - `M docs/tasks/kits-3d/18-medir-os-22-replay.md`
    - `M docs/tasks/kits-3d/CORR-K3D-028.md`
    - `M docs/tasks/kits-3d/correcoes-progresso.md`
    - `M docs/tasks/kits-3d/fixes.json`
    - `M docs/tasks/kits-3d/progress.json`

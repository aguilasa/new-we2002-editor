---
id: CORR-K3D-002
---

# CORR-K3D-002 — files da K3D-TASK-04 omite api.py e a nota na K3D-TASK-05

Origin: [K3D-TASK-04](/docs/tasks/kits-3d/04-buracos-por-angulo.md)

## Problem

O commit de trabalho da [K3D-TASK-04](/docs/tasks/kits-3d/04-buracos-por-angulo.md),
`b90d7e7`, muda sete arquivos, e dois estão fora do `files` declarado da task:
`tools/kits/core/api.py` (os invólucros `count_holes`, `planted_gap` e `HoleCount`) e
`docs/tasks/kits-3d/05-costas-sempre.md` (uma nota de cinco linhas escrita no corpo de
outra task). O próprio fechamento acusou os dois em "Outside declared files", e a task
foi fechada assim mesmo. O `api.py` está coberto pelo escopo em prosa ("`tools/kits/core/`
se a contagem pedir apoio"), mas não pela lista `files`; a edição na 05 é mudança no
arquivo de outra task que o escopo desta não nomeia.

## Evidência

```text
$ git show --stat b90d7e7 | grep -E 'api.py|05-costas'
 docs/tasks/kits-3d/05-costas-sempre.md      |   5 +
 tools/kits/core/api.py                      |  19 +++
$ sh "$RITE_HOME/bin/rite" context K3D-TASK-04 --json | python3 -c 'import json,sys; print("tools/kits/core/api.py" in json.load(sys.stdin)["item"]["files"])'
False
```

## Root cause

Hipótese: o `files` foi escrito antes do trabalho; o invólucro da API entrou quando foi
preciso, e a nota de passagem para a 05 foi para o arquivo daquela task em vez do Log
desta. Ninguém atualizou a declaração no fechamento.

## Fix

Pelo CLI, nunca à mão: `rite set K3D-TASK-04 --files <lista atual>,tools/kits/core/api.py`.
Quanto à nota na 05: ou declará-la no Log da 04 como passagem deliberada, ou movê-la para
dentro do trabalho da própria K3D-TASK-05.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/04-buracos-por-angulo.md (o `files`, via `rite set`, e o Log)
- docs/tasks/kits-3d/05-costas-sempre.md

## Verificação

```sh
sh "$RITE_HOME/bin/rite" context K3D-TASK-04 --json | python3 -c 'import json,sys; print("tools/kits/core/api.py" in json.load(sys.stdin)["item"]["files"])'
```

Imprime `False` hoje; tem de imprimir `True` depois da correção.

## Log de Execução

---
id: CORR-K3D-025
---

# CORR-K3D-025 — Nota de passagem na K3D-TASK-18 fora do escopo e com afirmação sem saída

Origin: [K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md)

## Problem

O commit `f020577` da [K3D-TASK-17](/docs/tasks/kits-3d/17-medir-goleiro-capitao-replay.md) edita `docs/tasks/kits-3d/18-medir-os-22-replay.md`, que não
está na lista "In" da task; o Log já a acusa em "Outside declared files". A nota traz
ainda uma afirmação com cara de medida ("de frente o torso do goleiro não manda à GPU
nenhum quad do painel") que nenhuma saída do `--replay` imprime.

## Evidência

```text
$ git show --stat f020577 | grep 18-medir
 docs/tasks/kits-3d/18-medir-os-22-replay.md        |   9 +
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json | grep -ic "front.*panel"
0
```

## Root cause

A passagem foi escrita na task seguinte em vez de no G8 ou no Log.

## Fix

Levar a parte medida para o G8, com um comando que a imprima (quads do painel de frente
por seção), ou pôr o arquivo no escopo da task pelo `rite set`.

## Arquivos a criar ou modificar

- docs/tasks/kits-3d/18-medir-os-22-replay.md
- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json | grep -i "front.*panel"
```

Hoje vazio; depois tem de imprimir a contagem de quads do painel de frente — ou a frase
sai da nota da 18.

## Log de Execução

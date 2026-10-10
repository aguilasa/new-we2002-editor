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

### 2026-10-10 — a medida sai do `--replay`, e a nota remete a ela

O `--replay` passou a imprimir quantas primitivas da figura amostram um painel de frente
(`panel_samples` sobre o grupo de frente). Com
`WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json`
(e `10`), saída 0 nos dois:

- `front: 0 primitive(s) of the figure sample a panel (the back is read after the turn)`;
- `back: 4 primitive(s) of the figure sample panel (100,104) of page (576,256); 4 of them are torso 13's own texels on the disc`.

Antes da mudança o mesmo `grep -ic "front.*panel"` dava 0 (a Evidência); agora casa uma linha. As duas
linhas estão coladas no G8, e a nota da K3D-TASK-18 remete a elas e a esta CORR.

- Triagem inline: **REPRODUCED** (`git show --stat f020577` lista `18-medir-os-22-replay.md | 9 +`;
  `grep -ic "front.*panel"` dava 0). O arquivo da 18 entrou no `files` da K3D-TASK-17 por `rite set`,
  e o G8 ganhou o parágrafo "O painel do goleiro só se vê de costas". `selftest.py`:
  `kits_selftest: 0 failure(s)`; `controls.py`: `controls: 43 of 43 red`.

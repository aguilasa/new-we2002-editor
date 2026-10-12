---
id: CORR-K3D-032
---

# CORR-K3D-032 — G8 diz que Bokšić e Balaban pintam a cabeça pela mesma CLUT, e a saída mostra CLUTs diferentes

Origin: [K3D-TASK-19](/docs/tasks/kits-3d/19-medir-capitao-linha-replay.md)

## Problem

A lista de diferenças que o G8 deixa para a task de conserto, escrita pela [K3D-TASK-19](/docs/tasks/kits-3d/19-medir-capitao-linha-replay.md), diz que
Bokšić e Balaban "usam a mesma seção 46 … pela mesma CLUT (128,480) — o que pinta o cabelo
de cada um não está medido aqui". A saída colada poucas linhas antes mostra a 46 do Bokšić
na CLUT (128,480) nos dois slots e a 46 do Balaban em (32,480) (160,480). A CLUT difere e
é a provável fonte da cor do cabelo, então a task de conserto fica apontada para o lado
errado.

## Evidência

```text
$ grep -n 'CLUT (128,480)\|CLUT (32,480)\|mesma CLUT' docs/KITS-AJUSTES-3D.md
1178:     46: 14 prim(s), ... CLUT (128,480); page (512,256) ...        (Bokšić, slot 9)
1234:     46: 15 prim(s), ... CLUT (128,480); page (512,256) ...        (Bokšić, slot 10)
1290:     46: 18 prim(s), ... CLUT (32,480) (160,480); page (512,256) ... (Balaban, slot 10)
1411:  e o Balaban usam a mesma seção 46, mas um de cabelo loiro e outro castanho, pela mesma CLUT
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/oracle.py --replay 10 --focus 2 --frame-json work/kits-oracle/replay-10-2.json | grep ' 46: '
     46: 18 prim(s), ... CLUT (32,480) (160,480); page (512,256) ...
```

## Root cause

Hipótese: a prosa foi escrita de memória do bloco do Bokšić, não do bloco do Balaban.

## Fix

No G8 de `docs/KITS-AJUSTES-3D.md`, em "As diferenças do capitão de linha": a cabeça é a
mesma seção 46 em linhas de CLUT diferentes — (128,480) no Bokšić, (32,480)/(160,480) no
Balaban —, e a cor do cabelo de cada jogador passa por essa CLUT.

## Arquivos a criar ou modificar

- docs/KITS-AJUSTES-3D.md

## Verificação

```sh
grep -n 'pela mesma CLUT' docs/KITS-AJUSTES-3D.md
```

Hoje imprime a linha 1411; depois, nada.

## Log de Execução

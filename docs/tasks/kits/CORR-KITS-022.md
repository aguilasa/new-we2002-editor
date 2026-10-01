---
id: CORR-KITS-022
---

# CORR-KITS-022 — Correct the corpus description in the task notes and NOTICE

Origin: [KITS-TASK-10](/docs/tasks/kits/10-confronto-2-superpack.md)

## Problem

As Notas da KITS-TASK-10 dizem que "os .tim que sobram são os de `Banderas 3D Nacionales`". Dos 113 `.tim` sem par, 109 estão em `Nacionales` e 4 em `Banderas 3D - Mixto` (`BILB_BAND`, `BTS_BND`, `LEVK_BND`, `RNG_BND`). As Notas também dizem que a imagem é "128×128 em (960,0), 128×64 em (704,256)", mas os 160 pares têm 7 retângulos, entre eles (896,0) 128×128 ×28 e (0,0) 128×64 ×11. O `NOTICE.md` e as mensagens do `confront.py` falam em "160 pares `*_BND.bin` / `*_BND.tim`", mas 8 dos 160 não se chamam `_BND` (`BAND_ARG`, `BAND_AUS`, `BAND_BRA`, `BAND_CMR`, `BAND_ING`, `BAND_IRA`, `BAND_URU`, `WBRE_BAND`).

## Evidência

```text
$ python tools/kits/confront.py --report
confront.py: error: unrecognized arguments: --report
$ cd "$WE2002_KITS_CORPUS"; for d in */; do echo "$d bin=$(find "$d" -type f -iname '*.bin'|wc -l) tim=$(find "$d" -type f -iname '*.tim'|wc -l)"; done
Banderas 3D - Mixto/ bin=161 tim=164
Banderas 3D Nacionales/ bin=0 tim=109
```

Sonda do revisor, sem versão (`confront.find_pairs` e `confront.tim_pixels` sobre o corpus, contando nome, flags/CLUT e retângulo de cada par):

```text
pairs 160 named *_BND 152
flags,clutlen Counter({(9, 524): 160})
rect (x,y,width_px,h) Counter({(704, 256, 128, 64): 76, (960, 0, 128, 128): 41, (896, 0, 128, 128): 28, (0, 0, 128, 64): 11, (0, 0, 128, 128): 2, (704, 256, 128, 128): 1, (960, 0, 128, 64): 1})
['BAND_ARG', 'BAND_AUS', 'BAND_BRA', 'BAND_CMR', 'BAND_ING', 'BAND_IRA', 'BAND_URU', 'WBRE_BAND']
```

## Root cause

Hipótese: a descrição do corpus foi escrita a partir de uma amostra de pares, sem contagem por ferramenta; o `confront.py` imprime só pares lidos e pares iguais.

## Fix

Acrescentar ao `tools/kits/confront.py` um modo `--report` que imprima os arquivos sem par por pasta e a distribuição de retângulo e de CLUT. Colar a saída nas Notas da KITS-TASK-10, corrigir a frase dos `.tim` que sobram e a dos retângulos, e tirar o "`*_BND`" (ou dizer "152 `_BND` e 8 `BAND_*`") no `NOTICE.md` e na docstring e nas mensagens do `confront.py`.

## Arquivos a criar ou modificar

- `tools/kits/confront.py`
- `docs/tasks/kits/10-confronto-2-superpack.md`
- `NOTICE.md`

## Verificação

```text
$ WE2002_KITS_CORPUS=<…/Banderas 3D> python tools/kits/confront.py --report
```

Hoje dá erro de argumento; depois tem de listar os 4 `.tim` sem par em `Mixto` e os 7 retângulos, batendo com as Notas.

## Log de Execução

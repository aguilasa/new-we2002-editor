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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `f66559ad`)

O shell do `rite reproduce` não tinha `WE2002_KITS_CORPUS` (o `cd ""` ficou na raiz do repositório); refeita com a variável apontando a pasta do corpus:

```text
$ python tools/kits/confront.py --report
usage: confront.py [-h] [--negative] [--scratch SCRATCH]
confront.py: error: unrecognized arguments: --report
$ cd "$WE2002_KITS_CORPUS"; for d in */; do echo "$d bin=$(find "$d" -type f -iname '*.bin'|wc -l) tim=$(find "$d" -type f -iname '*.tim'|wc -l)"; done
Banderas 3D - Mixto/ bin=161 tim=164
Banderas 3D Nacionales/ bin=0 tim=109
Base bandera 3D - Neo2k3/ bin=0 tim=0
Remover as bandeiras 3D grandes e pequenas dos estádios - Fabio FJA/ bin=0 tim=0
```

REPRODUCED: 164 `.tim` e 160 pares no `Mixto`, então 4 `.tim` sem par ali, contra as Notas que punham todos os que sobram em `Nacionales`.

### O que foi feito

- `tools/kits/confront.py --report`: por pasta, `.bin`/`.tim`/pares e os sem par (nomeados até 10); os pares por nome (`*_BND` ou não); e, de cada par, flags e CLUT do TIM e o retângulo da imagem em pixels (`tim_shape`). Docstring, uso e mensagem de pulo sem o "`*_BND`" geral.
- KITS-TASK-10, Notas: a frase dos retângulos (eram dois; são sete) e a dos `.tim` que sobram (109 + 4), com a saída do `--report` colada.
- `NOTICE.md`: "160 `.bin` / `.tim` pairs (152 named `*_BND`, 8 otherwise)".

### Verificação

```text
$ WE2002_KITS_CORPUS=".../Superpackv6/We2002/TEX/Banderas 3D" python tools/kits/confront.py --report; echo "exit $?"
Banderas 3D - Mixto/: 161 .bin, 164 .tim, 160 pair(s)
  1 .bin without a partner: LENS_BND
  4 .tim without a partner: BILB_BAND, BTS_BND, LEVK_BND, RNG_BND
Banderas 3D Nacionales/: 0 .bin, 109 .tim, 0 pair(s)
  109 .tim without a partner: (109, not listed)
pairs: 160, 152 named *_BND, 8 otherwise: BAND_ARG, BAND_AUS, BAND_BRA, BAND_CMR, BAND_ING, BAND_IRA, BAND_URU, WBRE_BAND
  TIM flags 9, CLUT block 524 bytes: 160
  image at (704,256) 128x64 px: 76
  image at (960,0) 128x128 px: 41
  image at (896,0) 128x128 px: 28
  image at (0,0) 128x64 px: 11
  image at (0,0) 128x128 px: 2
  image at (704,256) 128x128 px: 1
  image at (960,0) 128x64 px: 1
exit 0
$ python tools/kits/confront.py | tail -1
confront 2: 160 pairs read, 160 match byte for byte (no mismatch)
$ python tools/kits/confront.py --negative | tail -1
control held: the changed copy is refused
$ env -u WE2002_KITS_CORPUS python tools/kits/confront.py; echo "exit $?"
confront 2: skipped -- WE2002_KITS_CORPUS is not set (a folder with the community's .bin / .tim flag pairs)
exit 77
```

Os 4 `.tim` sem par no `Mixto` e os 7 retângulos batem com a sonda da revisão e agora com as Notas.
- **Closed** — commit `38231a25` (2026-10-01): fix(kits): count the flag corpus with confront.py --report
  - Files (`git show --name-status 38231a25`):
    - `M NOTICE.md`
    - `M docs/tasks/kits/10-confronto-2-superpack.md`
    - `M docs/tasks/kits/CORR-KITS-022.md`
    - `M tools/kits/confront.py`

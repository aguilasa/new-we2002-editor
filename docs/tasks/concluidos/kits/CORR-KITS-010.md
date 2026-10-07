---
id: CORR-KITS-010
---

# CORR-KITS-010 — Re-run the plan's secondary subcommands in the closing Log

Origin: [KITS-TASK-05](/docs/tasks/concluidos/kits/05-fechamento-fase-0.md)

## Problem

O critério 1 da KITS-TASK-05 diz que "nenhum número do plano diverge", mas o [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) cita números de variantes de subcomando que o Log de fechamento não reexecutou: no §4.3, `prims --all-kits` (105 kits, 1 resultado), `prims --all-kits --negative` (104 e 1) e as contagens por `--tuple` (603/639 e 598/634); no §4.4, `rects --all … 704,256` (os onze arquivos); no §4.6, que o digest "não muda com o TEX". O revisor reexecutou todos e eles se sustentam — a afirmação da task é verdadeira —, mas o Log não traz evidência delas.

## Evidência

```text
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --tuple A-A1-A-A-A --tuple A-P1-A-A-A --tuple A-I3-A-G-A
  A-P1-A-A-A     figure 0: 603 total, kit role uniform 237; figure 1: 639 total, kit role uniform 429
  A-I3-A-G-A     figure 0: 598 total, kit role uniform 237; figure 1: 634 total, kit role uniform 429
$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --all-kits --negative
  planted  105 kits, 2 distinct result(s): 104, 1  [TEX_A4]
$ python tools/kits/cli.py rects --all roms/japanese-shift-jis.bin 704,256 | tail -1
  ... 11 file(s): /BIN/DATSEL3.BIN, /BIN/EDT_2D.BIN, /BIN/LC_AF.BIN, ... /BIN/LC_OL.BIN
$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --kit 98 | tail -1
  sha256 of the canonical JSON: 2360a921f7cee6f69dcbc1bb3ad2633c306a720c86399a04b918fbdf9448fb84
$ grep -cE 'all-kits|--tuple|rects --all|--kit 98' docs/tasks/kits/05-fechamento-fase-0.md
0
```

## Root cause

Hipótese: o fechamento reexecutou só a forma padrão e a `--negative` do subcomando de cada task, tomando "os subcomandos das tasks" como se cobrissem também as variantes que o plano cita.

## Fix

No bloco de evidência de `docs/tasks/kits/05-fechamento-fase-0.md`, acrescentar essas cinco corridas, coladas da ferramenta na HEAD. Não precisa mudar código nem plano.

## Arquivos a criar ou modificar

- `docs/tasks/kits/05-fechamento-fase-0.md`

## Verificação

```text
$ grep -cE 'all-kits|--tuple|rects --all|--kit 98' docs/tasks/kits/05-fechamento-fase-0.md
```

Hoje dá 0; depois, pelo menos 4.

## Log de Execução

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `226b1582`)

```text
$ grep -cE 'all-kits|--tuple|rects --all|--kit 98' docs/tasks/kits/05-fechamento-fase-0.md
0
```

REPRODUCED. As quatro corridas da Evidência dão hoje os mesmos números que a revisão viu (603/639, 598/634, 104 e 1, os onze arquivos, o digest `2360a921…48fb84` com `--kit 98`). Causa raiz confirmada: o Log do fechamento reexecutou só a forma padrão e a `--negative` de cada subcomando.

### O que foi feito

Cinco corridas acrescentadas ao bloco de evidência da KITS-TASK-05, geradas por script a partir da ferramenta na HEAD e não digitadas: `prims --all-kits`, `prims --all-kits --negative`, `prims` com as oito tuplas da CORR-KITS-005, `rects --all … 704,256 | tail -1` e `uv --kit 98 | tail -1`, todas com saída 0. Uma frase fora do bloco diz de onde vieram. Código e plano não mudaram.

### Verificação

```text
$ grep -cE 'all-kits|--tuple|rects --all|--kit 98' docs/tasks/kits/05-fechamento-fase-0.md
5
```
- **Closed** — commit `22555288` (2026-09-30): docs(kits): re-run in the phase 0 closing Log the subcommand variants the plan cites
  - Files (`git show --name-status 22555288`):
    - `M docs/tasks/kits/05-fechamento-fase-0.md`
    - `M docs/tasks/kits/CORR-KITS-010.md`

---
id: CORR-KITS-003
title: "Version the rects probes: full owner list and negative control"
origin: KITS-TASK-02
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: pending
depends_on: []
done_on: null
done_commit: null
---

# CORR-KITS-003 — Version the rects probes: full owner list and negative control

Origin: [KITS-TASK-02](/docs/tasks/kits/02-retangulos-608-e-704.md)

## Problem

Duas afirmações da KITS-TASK-02 se apoiam em corridas que não estão no repositório. (a) `cli.py rects` imprime só três nomes por grupo (`NAMES_SHOWN = 3`, depois `...`), mas o §4.4 do [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md) e o Log nomeiam os onze donos 32×128 de (704,256) — `DATSEL3`, `EDT_2D` e nove `LC_*` —, e nenhum comando versionado imprime essa lista. (b) O controle negativo do Log rodou "em memória": as duas origens do `TEX_A4` passaram de 576 para 640 e deram 106→105 arquivos e 211→209 registros. Nenhum subcomando nem opção o reproduz. É a mesma classe de defeito que a CORR-KITS-002 corrigiu no `survey --negative`.

## Evidência

```text
$ python tools/kits/cli.py rects roms/japanese-shift-jis.bin 608,256 704,256
(704,256): 116 record(s) in 116 file(s) cover it, 116 start there
  image origin ( 704, 256)  32x128 hw  STARTS here   11 file(s): /BIN/DATSEL3.BIN, /BIN/EDT_2D.BIN, /BIN/LC_AF.BIN ...
$ grep -n 'NAMES_SHOWN = ' tools/kits/cli.py
94:NAMES_SHOWN = 3
$ python tools/kits/cli.py rects --negative roms/japanese-shift-jis.bin 608,256
cli.py: error: unrecognized arguments: --negative
```

O revisor reproduziu os 105/209 só por sonda descartável (monkeypatch de `survey.bin_archive.entries` com x=640 nas entradas do `TEX_A4` em (576,256), e depois `survey.owners_of`).

## Root cause

Hipótese: a lista completa e o defeito plantado foram calculados em sessões descartáveis do interpretador, e só as conclusões foram para o Log e para o plano.

## Fix

Em `tools/kits/cli.py`, adicionar `rects --all` (ou `--names N`) para imprimir todos os caminhos donos, e `rects --negative`, apoiado numa função pura em `tools/kits/core/survey.py` que planta o deslocamento de origem do `TEX_A4` e devolve as contagens que se movem. Citar os dois comandos no §4.4 do plano e no Log da task.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/core/survey.py`
- `docs/PLAN-KITS-PY.md`
- `docs/tasks/kits/02-retangulos-608-e-704.md`

## Verificação

```text
$ python tools/kits/cli.py rects --negative roms/japanese-shift-jis.bin 608,256
$ python tools/kits/cli.py rects --all roms/japanese-shift-jis.bin 704,256
```

Hoje o primeiro sai 2 (argumento não reconhecido). Depois, ele imprime 106→105 arquivos, 211→209 registros e o `TEX_A4` fora; o segundo lista os onze donos 32×128.

## Log de Execução

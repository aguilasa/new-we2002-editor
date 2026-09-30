---
id: CORR-KITS-003
title: "Version the rects probes: full owner list and negative control"
origin: KITS-TASK-02
severity: medium
files: []            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
depends_on: []
done_on: 2026-09-30
done_commit: 921ed149
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

### Reprodução (`rite reproduce --all --cycle kits`, HEAD `10bd0e3a`)

```text
$ grep -n 'NAMES_SHOWN = ' tools/kits/cli.py
94:NAMES_SHOWN = 3
$ python tools/kits/cli.py rects --negative roms/japanese-shift-jis.bin 608,256
usage: cli.py [-h] {survey,rects} ...
cli.py: error: unrecognized arguments: --negative
```

REPRODUCED (exit 2); e `rects ... 704,256` corta os onze em `/BIN/LC_AF.BIN ...`. Causa raiz confirmada: nenhum código versionado planta o deslocamento nem imprime a lista inteira.

### O que foi feito

- `tools/kits/core/survey.py`: `rects_negative(files, points)` puro — desloca para x=640 toda imagem do `TEX_A4` com origem em (576,256) e devolve, por ponto, arquivos, registros e se o `TEX_A4` é dono, antes e depois (`RectsControl`); `rects_negative_image(path, points)` lê o disco.
- `tools/kits/cli.py rects --all` (todos os nomes) e `rects --negative` (sai 1 se algum ponto não se mover).
- §4.4 do plano cita os dois comandos; o Log da KITS-TASK-02 troca a lista escrita à mão e a sonda pelas saídas.

### Verificação

```text
$ python tools/kits/cli.py rects --negative roms/japanese-shift-jis.bin 608,256; echo "exit $?"
Planted: 2 image record(s) of /BIN/TEX_A4.BIN moved from (576,256) to x=640
  (608,256): files 106 -> 105, records 211 -> 209, /BIN/TEX_A4.BIN owns it: yes -> NO  red
1 of 1 points red
exit 0
$ python tools/kits/cli.py rects --all roms/japanese-shift-jis.bin 704,256 | tail -1
  image origin ( 704, 256)  32x128 hw  STARTS here   11 file(s): /BIN/DATSEL3.BIN, /BIN/EDT_2D.BIN, /BIN/LC_AF.BIN, /BIN/LC_AM.BIN, /BIN/LC_AS.BIN, /BIN/LC_EU.BIN, /BIN/LC_IC.BIN, /BIN/LC_KO.BIN, /BIN/LC_LG.BIN, /BIN/LC_MS.BIN, /BIN/LC_OL.BIN
```

O verificador visto falhando — um ponto que o deslocamento não alcança:

```text
$ python tools/kits/cli.py rects --negative roms/japanese-shift-jis.bin 608,256 704,256; echo "exit $?"
Planted: 2 image record(s) of /BIN/TEX_A4.BIN moved from (576,256) to x=640
  (608,256): files 106 -> 105, records 211 -> 209, /BIN/TEX_A4.BIN owns it: yes -> NO  red
  (704,256): files 116 -> 116, records 116 -> 116, /BIN/TEX_A4.BIN owns it: yes -> yes  GREEN (control failed)
1 of 2 points red
exit 1
$ grep -nE 'print\(|sys\.exit|PySide' tools/kits/core/survey.py
(sem saída, exit 1)
```
- **Closed** — commit `921ed149` (2026-09-30): fix(kits): version the rects owner list and negative control
  - Files (`git show --name-status 921ed149`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/02-retangulos-608-e-704.md`
    - `M docs/tasks/kits/CORR-KITS-003.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/survey.py`

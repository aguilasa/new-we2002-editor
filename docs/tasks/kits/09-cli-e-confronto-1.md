---
id: KITS-TASK-09
---

# KITS-TASK-09 — `cli.py info/export` e o confronto 1: `tex.py` contra `bin_archive.py export`

## Goal

A CLI faz `info` e `export` só pela fachada, e os dois decodificadores concordam imagem por imagem e paleta por paleta nas 105 tags.

## Arquivos a criar ou modificar

- `tools/kits/cli.py`
- `tools/kits/selftest.py`
- `tools/kits/core/api.py`

## Done criteria

- [x] `grep -nE '^(from|import) ' tools/kits/cli.py` só mostra `core.api` e a biblioteca padrão
- [x] `cli.py survey` passa pela fachada: `api.py` expõe o levantamento (`survey_image`) e a forma esperada (quantas imagens e quantas CLUTs), e `grep -nP "^from core import (?!api)" tools/kits/cli.py` sai vazio
- [x] Confronto 1 roda como opção versionada e imprime 105 de 105 tags iguais (6 imagens e 5 paletas cada); colado no Log
- [x] Controle: um pixel alterado no lado do `tex.py` derruba o confronto (vermelho no Log)

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#5).

Da [CORR-KITS-001](/docs/tasks/kits/CORR-KITS-001.md): o subcomando `survey`, entregue na KITS-TASK-01 antes de a fachada existir, importa `core.survey` direto e lê `survey_mod.EXPECTED_SHAPE`/`KIND_IMAGE`. Esta task o passa para trás de `core/api.py`, com as constantes de forma vindo de lá.

Da [CORR-KITS-018](/docs/tasks/kits/CORR-KITS-018.md): o `cli.py` já não importa `core.survey` — as sondas chegam como `api.measure` —, e o `kits_selftest` confere a regra (`facade_breaks`, com o controle `cli-imports-survey`). O critério acima continua desta task: conferir na HEAD, e decidir se `api.measure` basta ou se o levantamento ganha entrada própria na fachada.

Da KITS-TASK-02: `texture.tables` (do `looks`) e `bin_archive.entries` (de `tools/pes2`) discordam sobre `/BIN/DATSEL2.BIN` — o primeiro acha nele registro sobre (576,256)/(608,256), o segundo não (`atlas.py --elsewhere` contra `cli.py rects ... 576,256 608,256`). Não é TEX, mas é o mesmo tipo de pergunta: vale saber qual leitor está certo antes de declarar os dois decodificadores concordes.

O que ficou decidido:

- **`api.measure` continua**, para as sondas da fase 0 (`rects`, `prims`, `uv`), e o levantamento ganhou entrada própria na fachada: `api.survey_image`, `api.Survey`, `api.SurveyError`, e a forma como contagem, `api.IMAGE_COUNT` (6) e `api.PALETTE_COUNT` (5), tiradas do `EXPECTED_SHAPE`. O `cli.py survey` usa essas.
- **O confronto 1 é `cli.py export --confront`.** Para cada uma das 5 paletas, o nosso `export` e o `tools/pes2/bin_archive.py export --clut k` (como processo à parte — a CLI só importa a fachada) escrevem os PNGs indexados, com o mesmo nome, `TEX_<tag>_<i>.png`; o confronto lê os dois e compara índices, `PLTE` e `tRNS` decodificados, não bytes de PNG. São 6 imagens × 5 paletas por tag.
- **O que o confronto de paleta não vê:** o bit STP de cada cor não passa pelo PNG — só a regra de transparência que ele decide (preto com STP limpo). A conversão BGR555 → RGB dos dois lados é a mesma fórmula escrita duas vezes; o que se confronta de independente é a descompressão e a escolha do registro.
- **`kits_image` roda o confronto e o controle** (`_confront_checks`): `N of N` com `N` = kits lidos, e o `--negative` tem de dar `N-1 of N` e `red, held`.
- A discordância `texture.tables` × `bin_archive.entries` sobre `/BIN/DATSEL2.BIN` (nota da KITS-TASK-02) não é TEX e o confronto não a toca; ficou como nota na KITS-TASK-11.

## Log de Execução

### 2026-10-01

```
$ grep -nE '^(from|import) ' tools/kits/cli.py
21:from __future__ import annotations
23:import argparse
24:import json
25:import os
26:import struct
27:import subprocess
28:import sys
29:import tempfile
30:import zlib
34:from core import api  # noqa: E402
$ LC_ALL=C.UTF-8 grep -nP "^from core import (?!api)" tools/kits/cli.py; echo "grep exit=$?"
grep exit=1
```

(O `grep -P` sem locale UTF-8 sai 2 no Git Bash — `-P supports only unibyte and UTF-8 locales` —, o que pareceria vazio sem ser.)

Confronto 1, no disco japonês:

```
$ python tools/kits/cli.py export --confront roms/japanese-shift-jis.bin      # exit 0, ~31 s
confront 1: 105 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
```

O controle — um pixel do nosso lado:

```
$ python tools/kits/cli.py export --confront --negative roms/japanese-shift-jis.bin   # exit 0
  DIFFER TEX_00_00.png palette 0: 1 pixel(s) differ, first at 4096 (0,32)
  DIFFER TEX_00_00.png palette 1: 1 pixel(s) differ, first at 4096 (0,32)
  DIFFER TEX_00_00.png palette 2: 1 pixel(s) differ, first at 4096 (0,32)
  DIFFER TEX_00_00.png palette 3: 1 pixel(s) differ, first at 4096 (0,32)
  DIFFER TEX_00_00.png palette 4: 1 pixel(s) differ, first at 4096 (0,32)
confront 1: 104 of 105 tags equal (6 images x 5 palettes each), tex.py against bin_archive.py export
control: TEX_00 image 0 pixel 4096 +1 on our side -- red, held
```

`info` e `export` sozinhos:

```
$ python tools/kits/cli.py info --tag A4 roms/japanese-shift-jis.bin | sed -n '6,8p;17p'
TEX_A4  31584 bytes  passes the guard
  image   record  0  uniform, first set             128x128
  image   record  1  sleeves, first set             128x128
  palette record  9  flag palette                   256 colours
$ python tools/kits/cli.py export --tag 00 --out <tmp>/exp00 roms/japanese-shift-jis.bin
wrote 6 PNG(s) to <tmp>/exp00 with palette 0 (player palette, first set); 0 kit(s) refused
```

Os gates, no build fora da árvore (`%TEMP%/build-kits08`):

```
$ WE2002_LOOKS_IMAGE=.../roms/japanese-shift-jis.bin ctest -R kits -V
14:   ..... 11 of 11 controls red
14: kits_selftest: 0 failure(s)
1/2 Test #14: kits_selftest ....................   Passed   41.88 sec
15:   ..... 105 of 105 kits pass the guard
15:   ..... confront 1: 105 of 105 tags equal
15: kits_image: 0 failure(s)
2/2 Test #15: kits_image .......................   Passed   49.45 sec
```
- **Closed** — commit `7b1143ef` (2026-10-01): feat(kits): add cli.py info/export and confront 1 against bin_archive.py export
  - Files (`git show --name-status 7b1143ef`):
    - `M docs/PLAN-KITS-PY.md`
    - `M docs/tasks/kits/09-cli-e-confronto-1.md`
    - `M docs/tasks/kits/11-fechamento-fase-1.md`
    - `M docs/tasks/kits/15-flat.md`
    - `M docs/tasks/kits/progress.json`
    - `M docs/tasks/kits/progresso.md`
    - `M tools/kits/cli.py`
    - `M tools/kits/core/api.py`
    - `M tools/kits/selftest.py`

---
id: KITS-TASK-05
title: "Fechamento da fase 0 — medições no disco"
type: closing
phase: 0
depends_on: [KITS-TASK-01, KITS-TASK-02, KITS-TASK-03, KITS-TASK-04]
source_of_truth: "/docs/PLAN-KITS-PY.md#7"
files: ["docs/PLAN-KITS-PY.md"]            # predicted paths/globs; batches build their conflict matrix from them
resources: []        # serialized resources this item needs (rite.toml [resources] / profile)
status: done
done_on: 2026-09-30
done_commit: b040bd96
reviewed_on: pending
review_commit: null
---

# KITS-TASK-05 — Fechamento da fase 0 — medições no disco

## Goal

A fase 0 conferida de ponta a ponta na HEAD: as três medições e o levantamento reproduzem os números que o plano cita.

## Arquivos a criar ou modificar

- `docs/PLAN-KITS-PY.md`

## Done criteria

- [x] Os subcomandos das tasks 01–04 rodados de novo na HEAD, saídas coladas; nenhum número do plano diverge
- [x] As §4.3, §4.4 e §4.6 têm veredito ou o que ficou aberto dito, com o comando
- [x] `rite check --cycle kits` limpo

## Notes

Fonte de verdade: [PLAN-KITS-PY.md](/docs/PLAN-KITS-PY.md#7).

## Log de Execução

### O que foi feito

Fechamento da fase 0 na HEAD `68e94745`, depois das revisões das KITS-TASK-01 a 04 e das nove correções (CORR-KITS-001 a 009), todas fechadas. Nenhum código mudou nesta task.

- **§1.1:** as oito linhas da tabela batem com o `survey` (105 de 105 numa forma, `TEX_A4`, 103, `TEX_98`, `TEX_A4`, 16.384 B com `0xFF` em 93 e `0x00` em 12, árbitro em 1 variante, 25.948 a 34.200 bytes).
- **§4.3:** a tabela (593/356/237/0 e 629/200/429/0, caixas (576,256)..(607,359) e (600,256)..(639,383)) bate com o `prims`. Veredito da primeira metade dado (mangas não amostradas); **aberto e dito**: se manga longa e braçadeira são outra geometria.
- **§4.4:** fechada; "0 start there" em (608,256), 116 arquivos em (704,256), 106→105 e 211→209 no controle — batem com o `rects`.
- **§4.6:** entrada medida (237 e 429 primitivas, caixas (0,0)..(63,103) e (48,0)..(127,127), 4.117 e 3.825 px, 0 fora, digest `2360a921…48fb84`) — bate com o `uv`. **Aberto e dito**: o cruzamento com o mapa de zonas, que é a KITS-TASK-16.

### Evidência

```
$ python tools/kits/cli.py survey roms/japanese-shift-jis.bin      # exit 0
Kit container survey: roms/japanese-shift-jis.bin
  TEX_<tag>.BIN containers                       105
  shape 6 images + 5 CLUTs, same rects/order     105 of 105
  distinct shapes                                  1
  first set == second set (images and palettes)    1 of 105  [TEX_A4]
  images differ between the two sets             103 of 105
  only the palettes differ                         1 of 105  [TEX_98]
  player palette == keeper palette (first set)     1 of 105  [TEX_A4]
  flag, decompressed size                        16,384 B (record declares 8,192 B)
  flag, 2nd half is one byte value               105 of 105
  flag, 2nd-half byte value per container        0x00 in 12, 0xff in 93
  referee identical in all                       yes (1 variant(s))
  file size                                      25,948 .. 34,200 bytes

$ python tools/kits/cli.py survey --negative roms/japanese-shift-jis.bin      # exit 0
  A4 player CLUT, second set       TEX_A4   first set == second set: ('A4',) -> ()  red
  A4 goalkeeper CLUT, first set    TEX_A4   player palette == keeper palette: ('A4',) -> ()  red
  00 referee LZSS stream, +3       TEX_00   referee variants / problems: (1, ()) -> (2, ())  red
  00 referee rect x + 1            TEX_00   shape ok: 105 -> 104  red
4 of 4 controls red

$ python tools/kits/cli.py rects roms/japanese-shift-jis.bin 608,256 704,256      # exit 0
VRAM point owners: roms/japanese-shift-jis.bin
  236 files read, 131 hold records; 9 skipped
    skipped /MOVIE/WE2002.STR (Form 2)
    skipped /SD/DA/01GOALDM.DA (outside the track)
    skipped /SD/DA/02GMOVER.DA (outside the track)
    skipped /SD/DA/03SELE01.DA (outside the track)
    skipped /SD/DA/04SELE02.DA (outside the track)
    skipped /SD/DA/05RSLT01.DA (outside the track)
    skipped /SD/DA/06TITLEV.DA (outside the track)
    skipped /SD/DA/07STAFF1.DA (outside the track)
    skipped /SD/DA/08STAFF2.DA (outside the track)
(608,256): 211 record(s) in 106 file(s) cover it, 0 start there
  image origin ( 576, 256)  64x128 hw  covers only  105 file(s): /BIN/TEX_00.BIN, /BIN/TEX_01.BIN, /BIN/TEX_02.BIN ...
  image origin ( 592, 256)  32x128 hw  covers only    1 file(s): /SELECT2.BIN
(704,256): 116 record(s) in 116 file(s) cover it, 116 start there
  image origin ( 704, 256)  64x 64 hw  STARTS here  105 file(s): /BIN/TEX_00.BIN, /BIN/TEX_01.BIN, /BIN/TEX_02.BIN ...
  image origin ( 704, 256)  32x128 hw  STARTS here   11 file(s): /BIN/DATSEL3.BIN, /BIN/EDT_2D.BIN, /BIN/LC_AF.BIN ...

$ python tools/kits/cli.py rects roms/japanese-shift-jis.bin 608,256 --negative      # exit 0
Planted: 2 image record(s) of /BIN/TEX_A4.BIN moved from (576,256) to x=640
  (608,256): files 106 -> 105, records 211 -> 209, /BIN/TEX_A4.BIN owns it: yes -> NO  red
1 of 1 points red

$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin      # exit 0
Primitives per kit record: roms/japanese-shift-jis.bin
  kit TEX_A4, tuple A-A1-A-A-A, geometry and resolution by tools/looks draw_list
figure 0 (outfield): 593 primitive(s) over 12 section(s)
  container (draw list, first corner)      DAT2D 356, kit 237
  kit role (draw list, first corner)       uniform 237
  kit role (any of four corners)           uniform 237
  a corner in a DAT2D image record         356
  a corner in no record of either file     0
  corners touch a kit role first missed    0
  VRAM box of the corners in kit records   (576,256)..(607,359)
  sleeves (576,384): 0 primitive(s)
figure 1 (goalkeeper): 629 primitive(s) over 12 section(s)
  container (draw list, first corner)      DAT2D 200, kit 429
  kit role (draw list, first corner)       uniform 429
  kit role (any of four corners)           uniform 429
  a corner in a DAT2D image record         200
  a corner in no record of either file     0
  corners touch a kit role first missed    0
  VRAM box of the corners in kit records   (600,256)..(639,383)
  sleeves (576,384): 0 primitive(s)

$ python tools/kits/cli.py prims roms/japanese-shift-jis.bin --negative      # exit 0
  sleeves moved to (0,0)       moved 2  figure 0  sleeves first              0 ->   0  stays zero        held
  sleeves moved to (0,0)       moved 2  figure 0  sleeves touch              0 ->   0  stays zero        held
  sleeves moved to (0,0)       moved 2  figure 1  sleeves first              0 ->   0  stays zero        held
  sleeves moved to (0,0)       moved 2  figure 1  sleeves touch              0 ->   0  stays zero        held
  uniform moved to (0,0)       moved 2  figure 0  uniform first            237 ->   0  drops to zero     held
  uniform moved to (0,0)       moved 2  figure 0  uniform touch            237 ->   0  drops to zero     held
  uniform moved to (0,0)       moved 2  figure 1  uniform first            429 ->   0  drops to zero     held
  uniform moved to (0,0)       moved 2  figure 1  uniform touch            429 ->   0  drops to zero     held
  sleeves moved to (560,256)   moved 2  figure 0  other (560,256) touch      0 -> 238  rises above zero  held
  sleeves moved to (560,256)   moved 2  figure 0  other (560,256) first      0 ->   0  stays zero        held
  sleeves moved to (560,256)   moved 2  figure 0  disagree                   0 -> 238  rises above zero  held
  sleeves moved to (560,256)   moved 2  figure 1  other (560,256) touch      0 -> 194  rises above zero  held
  sleeves moved to (560,256)   moved 2  figure 1  other (560,256) first      0 ->   0  stays zero        held
  sleeves moved to (560,256)   moved 2  figure 1  disagree                   0 -> 194  rises above zero  held
14 of 14 expectations held

$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin      # exit 0
UV rects in the 256x128 work bitmap: roms/japanese-shift-jis.bin
  kit TEX_A4, tuple A-A1-A-A-A; uniform at x 0..127, sleeves at x 128..255; pixels from page and u,v
figure 0 (outfield): 237 kit primitive(s), 237 mapped
  mapped per image                             uniform 237
  union box, bitmap px (inclusive)             (0,0)..(63,103)
  distinct px in the rects (bounding-rect)     4117
  outside 256x128: 0
figure 1 (goalkeeper): 429 kit primitive(s), 429 mapped
  mapped per image                             uniform 429
  union box, bitmap px (inclusive)             (48,0)..(127,127)
  distinct px in the rects (bounding-rect)     3825
  outside 256x128: 0
sha256 of the canonical JSON: 2360a921f7cee6f69dcbc1bb3ad2633c306a720c86399a04b918fbdf9448fb84

$ python tools/kits/cli.py uv roms/japanese-shift-jis.bin --negative      # exit 0
  uniform moved to (577,256) moved 2  both      digest changes           2360a921f7cee6f6 -> 39883f850ca73f5d  held
  uniform moved to (577,256) moved 2  figure 0  rects move -2 px in x    237 mapped -> 215 of 215 still mapped moved  held
  uniform moved to (577,256) moved 2  figure 0  union x1 moves -2 px     (0, 0, 63, 103) -> (0, 0, 61, 103)  held
  uniform moved to (577,256) moved 2  figure 1  rects move -2 px in x    429 mapped -> 429 of 429 still mapped moved  held
  uniform moved to (577,256) moved 2  figure 1  union x1 moves -2 px     (48, 0, 127, 127) -> (46, 0, 125, 127)  held
  uniform moved to (577,256) moved 2  figure 0  outside: split rises     0 outside -> 18 corners in two images  held
  uniform named banner       moved 0  figure 0  outside: role = mapped   0 outside -> 237 not uniform or sleeves  held
  uniform named banner       moved 0  figure 1  outside: role = mapped   0 outside -> 429 not uniform or sleeves  held
  uniform at (560,256) w 96  moved 2  figure 1  outside: edge rises      0 outside -> 236 rect leaves 256x128  held
  uniform moved to (0,0)     moved 2  figure 0  mapped count drops to 0  237 -> 0  held
  uniform moved to (0,0)     moved 2  figure 1  mapped count drops to 0  429 -> 0  held
11 of 11 expectations held

$ grep -rnE 'print\(|sys\.exit|PySide' tools/kits/core/      # exit 1, sem saída (corrida no Git Bash)
```

(As nove linhas `skipped` do `rects` — 1 Form 2 e 8 fora da trilha — ficam na saída acima.)

```
$ rite check --cycle kits
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```
- **Closed** — commit `b040bd96` (2026-09-30): docs(kits): close phase 0 — the four measurements re-run at HEAD match the plan
  - Files (`git show --name-status b040bd96`):
    - `M docs/tasks/kits/05-fechamento-fase-0.md`

### Problemas encontrados

- A primeira versão deste Log dizia `# exit 2, sem saída` no `grep` do núcleo. O `exit 2` era erro do próprio `grep` chamado pelo `subprocess` do Python (`grep: Unmatched ( or \(` — o padrão chegou sem o escape que o shell daria), não um veredito. Refeito no Git Bash: `exit 1`, sem saída — o núcleo continua sem `print`, `sys.exit` e `PySide`.


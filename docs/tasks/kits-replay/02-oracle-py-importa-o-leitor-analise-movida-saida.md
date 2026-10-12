---
id: KRP-TASK-02
---

# KRP-TASK-02 — oracle.py importa o leitor: análise movida, saída de --frame-json idêntica nas capturas existentes

## Goal

As dezenove funções de análise do bloco G8 listadas no [§2.2](/docs/PLAN-KITS-REPLAY.md#2.2) moram só em `tools/kits/core/replay.py`; o `oracle.py` as importa e fica com `REPLAY_EXPECT`, `REPLAY_FIELD_EXPECT`, os gates, as plantas e a captura, sem mudar uma linha de saída.

## Arquivos a criar ou modificar

- In:
  - `tools/kits/oracle.py`
  - `tools/kits/core/replay.py`
  - `tools/kits/selftest.py`
  - `tools/kits/controls.py`
- Out:
  - captura nova (KRP-TASK-07)
  - `tools/kits/core/figure.py`
  - `tools/kits/ui/*`

## Done criteria

- [x] `grep -cE '^def (replay_figures|figure_depth|figure_off_axis|replay_focus|field_focus|pose_change|figure_group|piece_box|section_samples|shading_of|colour_confront|panel_samples|panel_cell|field_panels|field_number|sleeves_of|armband_of|figure_tag|_restore_samples)\b' tools/kits/oracle.py`: `0`
- [x] a saída de `oracle.py --replay 9|10 --frame-json`, `--replay 9|10 --focus 3 --frame-json`, `--replay 10 --focus 2 --frame-json`, `--replay-field 9|10 --frame-json` e `--replay-confront 9|10 --frame-json` (sem subir a aba) é byte-idêntica antes e depois do move: `diff` vazio das sete, com as linhas `$` completas no Log
- [x] `--plant-replay` e `--plant-replay-field` continuam saindo 1 com a mesma contagem de `FAIL` que o [relatório](/docs/KITS-REPLAYS-9-10.md#como-foi-medido) registra
- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Capture a saída de antes **antes** de mover (arquivos em `work/`), e compare depois. Se o `--replay-confront` sem emulador exigir a aba, registre só a parte que roda sem ela e diga isso no Log.

Da KRP-TASK-01: além das dezenove, o `core/replay.py` já traz cópias dos auxiliares que elas usam — `is_figure`, `kit_image_of`, `sample_zones`, `matrix_pieces`, `pose_frames`, `pose_project`, `piece_error` (sem o `pair`), `triangle_pixels`, `sample_pixels`, `texel_colour`, `panel_cells`, `pixel_index`, `back_indices`, `glyphs`, `read_panel`, `read_panels`, `field_row`, as constantes `KIT_PAGES`, `KIT_CLUTS`, `POSE_MARGIN`, `TORSO_MARGIN`, `PANEL_W/H`, `PLAYER_PALETTE`, `REPLAY_STILL`, `REPLAY_FOLLOW_*`, `REPLAY_FOCUS_MARGIN`, `REPLAY_ARMBANDS`, `*_SLEEVES`, `REPLAY_SHARED_CELL` — e os juízes `judge`/`judge_walk`. Para não sobrar cópia, o oracle passa a importá-los também. Duas assinaturas mudaram: `field_number(pages, panel, width, shift)` recebe a largura do registro do uniforme, e `judge(report, expect, plant_root=None)` troca o `plant=True` pela raiz plantada.

## Log de Execução

### 2026-10-12

Saem do `oracle.py` as dezenove do [§2.2](/docs/PLAN-KITS-REPLAY.md#2.2) e, para não sobrar
cópia, os auxiliares que a KRP-TASK-01 levou para o leitor (`is_figure`, `kit_image_of`,
`work_point`, `sample_zones`, `matrix_pieces`, `pose_frames`, `pose_project`, `piece_error`,
`triangle_pixels`, `sample_pixels`, `texel_colour`, `panel_cells`, `pixel_index`, `back_indices`,
`glyphs`, `read_panel`, `read_panels`, `field_row`), os juízes `replay_judge`/`replay_field_judge`
e as constantes deles; o oracle importa tudo de `core.replay` num bloco só, no topo. O `judge` do
leitor entra como `replay_judge`, porque o oracle já tem um `judge` (o do `--expect`, VRAM) — a
primeira corrida "depois" saiu com `TypeError: judge() missing 1 required positional argument`
por isso. O `piece_error` do leitor ganhou de volta o `pair` (o `--pair-by corners` do
`--match-pose` o usa). `field_number` recebe a largura do registro do uniforme, que o
`run_replay_field` lê do disco como antes. 749 linhas removidas, 22 inseridas (`git diff --stat`).

```
$ grep -cE '^def (replay_figures|figure_depth|figure_off_axis|replay_focus|field_focus|pose_change|figure_group|piece_box|section_samples|shading_of|colour_confront|panel_samples|panel_cell|field_panels|field_number|sleeves_of|armband_of|figure_tag|_restore_samples)\b' tools/kits/oracle.py
0
```

Saída antes e depois: cada linha abaixo rodada com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin DISPLAY=:98 XAUTHORITY=`,
na HEAD `fffa211a` (antes, em `work/krp02/before/`) e depois do move (`work/krp02/after/`):

```
$ python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json
$ python3 tools/kits/oracle.py --replay 10 --frame-json work/kits-oracle/replay-10.json
$ python3 tools/kits/oracle.py --replay 9 --focus 3 --frame-json work/kits-oracle/replay-9-3.json
$ python3 tools/kits/oracle.py --replay 10 --focus 3 --frame-json work/kits-oracle/replay-10-3.json
$ python3 tools/kits/oracle.py --replay 10 --focus 2 --frame-json work/kits-oracle/replay-10-2.json
$ python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json
$ python3 tools/kits/oracle.py --replay-field 10 --frame-json work/kits-oracle/replay-field-10-capture.json
$ python3 tools/kits/oracle.py --replay-confront 9 --frame-json work/kits-oracle/replay-9.json
$ python3 tools/kits/oracle.py --replay-confront 10 --frame-json work/kits-oracle/replay-10.json
$ python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json --plant-replay
$ python3 tools/kits/oracle.py --replay 9 --focus 3 --frame-json work/kits-oracle/replay-9-3.json --plant-replay
$ python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json --plant-replay-field
$ python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json --plant-replay-field focus
$ python3 tools/kits/oracle.py --replay-field 9 --frame-json work/kits-oracle/replay-field-9-capture.json --plant-replay-field panel
$ for f in work/krp02/before/*.txt; do n=$(basename $f); diff -q $f work/krp02/after/$n >/dev/null && echo "same $n" || echo "DIFF $n"; done
same confront-10.txt
same confront-9.txt
same field-10.txt
same field-9.txt
same plant-9-3.txt
same plant-9.txt
same plant-field-9-focus.txt
same plant-field-9-panel.txt
same plant-field-9.txt
same replay-10-2.txt
same replay-10-3.txt
same replay-10.txt
same replay-9-3.txt
same replay-9.txt
```

O `--replay-confront` sobe a aba (`app.py --export-3d` no `:98`) e roda; entrou inteiro na
comparação, histogramas inclusive. As sete leituras saem 0 com a linha `ok` do relatório; as
plantas saem 1 com `--plant-replay` 4 `FAIL` (goleiro) e 6 (Bokšić), `--plant-replay-field` 49,
`focus` 47 e `panel` 1 (`grep -c FAIL` de cada arquivo) — 4, 6 e 49 são os do
[relatório](/docs/KITS-REPLAYS-9-10.md#como-foi-medido), idênticos antes e depois.

Análise estática dos nomes (`ast`: todo `Name` lido contra o definido ou importado no módulo) não
acusa nenhum nome indefinido em `oracle.py` nem em `core/replay.py` — os outros modos do oracle
(`--match-pose`, `--back`, `--edit-number`…) usavam auxiliares que saíram.

Controles: dois quebraram por plantar em funções que saíram do oracle (`oracle-back-byte-order`
em `pixel_index`, `oracle-pose-texel-order` em `piece_error`, `matched 0x`); apontados para
`kits/core/replay.py`, os dois `RED` em `--only`. Controle novo `replay-copy-in-oracle`, contra a
regra nova do selftest (`REPLAY_MOVED`, `replay_copies`): planta uma `def figure_depth` no oracle.

```
$ python3 tools/kits/controls.py --only replay-copy-in-oracle
  RED    replay-copy-in-oracle        kits/oracle.py :: module constant
(selftest --no-plant da cópia plantada, sai 1)
  FAIL  oracle.py defines none of the analysis core/replay.py holds (section 2.2)  ['figure_depth']
```

Gates:

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
1/4 Test #18: kits_selftest ....................   Passed  235.06 sec
2/4 Test #19: kits_image .......................   Passed   49.66 sec
3/4 Test #20: kits_gen .........................   Passed    0.11 sec
4/4 Test #21: kits_ui ..........................   Passed  258.01 sec
100% tests passed, 0 tests failed out of 4
$ python3 tools/kits/controls.py
controls: 56 of 56 red
```
- **Closed** — commit `09203255` (2026-10-12): refactor(kits): oracle.py imports the replay reader, analysis moved
  - Files (`git show --name-status 09203255`):
    - `M docs/tasks/kits-replay/02-oracle-py-importa-o-leitor-analise-movida-saida.md`
    - `M docs/tasks/kits-replay/progress.json`
    - `M docs/tasks/kits-replay/progresso.md`
    - `M tools/kits/controls.py`
    - `M tools/kits/core/replay.py`
    - `M tools/kits/oracle.py`
    - `M tools/kits/selftest.py`
  - **Outside declared files** (`tools/kits/oracle.py`, `tools/kits/core/replay.py`, `tools/kits/selftest.py`, `tools/kits/controls.py`):
    - `docs/tasks/kits-replay/progress.json`
    - `docs/tasks/kits-replay/progresso.md`

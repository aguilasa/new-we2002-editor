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

- [ ] `grep -cE '^def (replay_figures|figure_depth|figure_off_axis|replay_focus|field_focus|pose_change|figure_group|piece_box|section_samples|shading_of|colour_confront|panel_samples|panel_cell|field_panels|field_number|sleeves_of|armband_of|figure_tag|_restore_samples)\b' tools/kits/oracle.py`: `0`
- [ ] a saída de `oracle.py --replay 9|10 --frame-json`, `--replay 9|10 --focus 3 --frame-json`, `--replay 10 --focus 2 --frame-json`, `--replay-field 9|10 --frame-json` e `--replay-confront 9|10 --frame-json` (sem subir a aba) é byte-idêntica antes e depois do move: `diff` vazio das sete, com as linhas `$` completas no Log
- [ ] `--plant-replay` e `--plant-replay-field` continuam saindo 1 com a mesma contagem de `FAIL` que o [relatório](/docs/KITS-REPLAYS-9-10.md#como-foi-medido) registra
- [ ] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [ ] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo

## Notes

Capture a saída de antes **antes** de mover (arquivos em `work/`), e compare depois. Se o `--replay-confront` sem emulador exigir a aba, registre só a parte que roda sem ela e diga isso no Log.

## Log de Execução

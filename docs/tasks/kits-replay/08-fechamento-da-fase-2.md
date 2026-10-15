---
id: KRP-TASK-08
---

# KRP-TASK-08 — Fechamento da fase 2

## Goal

A fase 2 (a linha de comando, a captura e o confronto) fica fechada: os gates do [§9](/docs/PLAN-KITS-REPLAY.md#9) e as verificações da fase 2 do perfil rodam de novo na HEAD, e o que a fase mudou está escrito no plano.

## Arquivos a criar ou modificar

- In:
  - nenhum: só reroda e corrige escrituração
- Out:
  - código novo

## Done criteria

- [x] `ctest --test-dir build -R kits` com `DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle`: todos os alvos do [§9](/docs/PLAN-KITS-REPLAY.md#9) passam, sem *skipped*
- [x] `python3 tools/kits/controls.py`: última linha `controls: N of N red`, com os controles novos desta task no catálogo
- [x] `replay.py figure --json` reproduz a linha `ok` do oracle nas cinco capturas de perto, de novo na HEAD
- [x] `kits_replay` visto 77 sem captura
- [x] `rite check --cycle kits-replay`: `0 error(s), 0 warning(s)`

## Notes

Task de fechamento: não implementa; reroda e corrige escrituração. Toda saída colada da HEAD (armadilha K3).

## Log de Execução

- **pending** (2026-10-15): phase 2 still has open fixes CORR-KRP-010..014 from the KRP-TASK-06 review; the closing task runs after /rite:fix-all, by the user's choice

- **done** (2026-10-15): fixes CORR-KRP-010..015 fechadas antes (`rite status --cycle kits-replay`: `open fixes: critical 0, high 0, medium 0, low 0`). Gates e verificações da fase 2 rerodados na HEAD `d1d6f596`; o plano ganhou o parágrafo "Feito na fase 2" no fim do [§2.6](/docs/PLAN-KITS-REPLAY.md#2.6). Esta task não acrescenta controle: o catálogo tem os da fase, 70.

```
$ DISPLAY=:98 XAUTHORITY= WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin WE2002_KITS_REPLAY_DIR=$PWD/work/kits-oracle ctest --test-dir build -R kits
2/5 Test #19: kits_image .......................   Passed   28.06 sec
3/5 Test #20: kits_gen .........................   Passed    0.03 sec
4/5 Test #21: kits_ui ..........................   Passed  210.98 sec
5/5 Test #22: kits_replay ......................   Passed    7.92 sec
100% tests passed, 0 tests failed out of 5
$ python3 tools/kits/controls.py
controls: 70 of 70 red
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py check; echo "exit=$?"
kits_replay: skipped -- WE2002_KITS_REPLAY_DIR is not set (the folder of the kept captures, work/kits-oracle)
exit=77
$ sh rite check --cycle kits-replay
check: 0 error(s), 0 warning(s) in 1 cycle(s)
```

A linha `ok` do oracle contra o `figure` nas cinco capturas de perto, com `WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin DISPLAY=:98 XAUTHORITY=`. A saída humana do `figure` é impressa do mesmo documento que o `--json` emite, e o `--json` das cinco traz `"schema": "kits-replay/1"` (5 de 5, `replay.py figure <captura> --json | grep '"schema"'`).

```
$ python3 tools/kits/oracle.py --replay 9 --frame-json work/kits-oracle/replay-9.json
  ok    the followed figure opens at section 13 with head 34, draws 92 in place of 15, holds still, and its back shows panel (576, 100, 104) with number 1
$ python3 tools/kits/oracle.py --replay 10 --frame-json work/kits-oracle/replay-10.json
  ok    the followed figure opens at section 13 with head 34, draws 92 in place of 15, holds still, and its back shows panel (576, 100, 104) with number 1
$ python3 tools/kits/oracle.py --replay 9 --focus 3 --frame-json work/kits-oracle/replay-9-3.json
  ok    the followed figure opens at section 2 with head 46, draws 90 in place of 4, holds still, and its back shows panel (640, 60, 104) with number 11
$ python3 tools/kits/oracle.py --replay 10 --focus 3 --frame-json work/kits-oracle/replay-10-3.json
  ok    the followed figure opens at section 2 with head 46, draws 93 in place of 97, holds still, and its back shows panel (640, 60, 104) with number 11
$ python3 tools/kits/oracle.py --replay 10 --focus 2 --frame-json work/kits-oracle/replay-10-2.json
  ok    the followed figure opens at section 2 with head 46, draws no armband, holds still, and its back shows panel (640, 80, 104) with number 20
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9.json
work/kits-oracle/replay-9.json, nearest: goalkeeper 13, head 34, sleeves None, armband 92 for 15; still 0; depth 4681
  order 34 13 14 16 92 17 18 20 11 19 21
  panel [576, 100, 104] from the back capture, number 1
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10.json
work/kits-oracle/replay-10.json, nearest: goalkeeper 13, head 34, sleeves None, armband 92 for 15; still 0; depth 4682
  order 34 13 14 16 92 17 18 20 11 19 21
  panel [576, 100, 104] from the back capture, number 1
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-9-3.json
work/kits-oracle/replay-9-3.json, on_axis: outfield 2, head 46, sleeves short, armband 90 for 4; still 0; depth 4694
  order 46 2 3 5 90 6 7 9 11 8 10
  panel [640, 60, 104] from the front capture, number 11
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-3.json
work/kits-oracle/replay-10-3.json, on_axis: outfield 2, head 46, sleeves long, armband 93 for 97; still 0; depth 4699
  order 46 2 95 96 93 98 7 9 11 8 10
  panel [640, 60, 104] from the front capture, number 11
$ WE2002_LOOKS_IMAGE=$PWD/roms/japanese-shift-jis.bin python3 tools/kits/replay.py figure work/kits-oracle/replay-10-2.json
work/kits-oracle/replay-10-2.json, on_axis: outfield 2, head 46, sleeves long, armband None; still 0; depth 4699
  order 46 2 95 96 97 98 7 9 11 8 10
  panel [640, 80, 104] from the front capture, number 20
```

Campo a campo iguais. O "its back shows" do oracle é texto fixo; o `from the … capture` do `figure` diz de qual captura o painel saiu (atrás de um jogador a primeira captura é as costas, que o `replay.py` chama `front` por ser a primeira — `game_side`).
- **Closed** — commit `9998ece1` (2026-10-15): docs(kits): close phase 2 of kits-replay with the gates rerun at HEAD
  - Files (`git show --name-status 9998ece1`):
    - `M docs/PLAN-KITS-REPLAY.md`
    - `M docs/tasks/kits-replay/08-fechamento-da-fase-2.md`
- **Reviewed** (2026-10-15) at `3689ca9e`: no finding
